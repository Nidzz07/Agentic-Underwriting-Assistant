"""R10 / R11 — the application-submission surface (WIRE1-Fold-6, register #2).

    R10  POST /applications                        -> SubmissionAccepted   (200, bare body)
    R11  POST /applications/{id}/draft             -> DraftTriggerResult   (200, bare body)

⚑ **THIS MODULE IS THE ONLY ROUTE MODULE PERMITTED TO REACH THE PIPELINE**, and that permission
is mechanical, not conventional: ``test_no_write_route.py``'s ``_PIPELINE_MODULES`` is an
**exact set** naming this file and ``dependencies.py``, so a third module reaching for
``CasePipeline`` fails the suite, and this module quietly dropping it fails too.

⚑ **THIS MODULE SERVES NO GET ROUTE, AND THAT IS LOAD-BEARING.** The narrowed BR-CASE-4 /
TRIGGER-1 guard asserts *"no module that serves a GET route may reference the pipeline"* at
FILE level — following the sibling ``_DOMAIN_SEAMS`` assertion's deliberate choice, *"so a
helper-function indirection inside a route module cannot evade it"*. Adding a GET handler here
would therefore fail the suite. **Do not add one.** R2/R3/R4 live in ``not_wired.py`` and must
stay there.

**TWO PHASES, DELIBERATELY (Q3(a)).** R10 is LLM-free: intake -> rules -> persist at
``evaluated``, returning fast. R11 is the separate, explicit, LLM-bearing drafting trigger. The
system was already shaped for this — R4's ``status: pending | ready`` discriminator exists
precisely because a case can exist before its memo does — so the two-phase flow renders
correctly with no change to any existing view.

**COMPOSITION ONLY — no domain logic lives here.** Intake, the rules engine, the orchestrator
and the pipeline all arrive via ``Depends``; the rejection body is built by a PURE projection.
"""
from __future__ import annotations

from typing import Any

import json

from fastapi import APIRouter, Depends, Request
from starlette.concurrency import run_in_threadpool

from backend.app.dependencies import (
    Identity,
    get_case_pipeline,
    get_intake_pipeline,
    require_underwriter,
)
from backend.app.errors import (
    INTERNAL_ERROR,
    INVALID_REQUEST,
    NOT_FOUND,
    PAYLOAD_TOO_LARGE,
    WireError,
)
from backend.app.multipart_reader import (
    MultipartInvalid,
    MultipartTooLarge,
    read_submission_multipart,
)
from backend.app.parse_concurrency import run_bounded_parse
from backend.app.projections import rejected_intake_detail
from backend.app.upload_storage import upload_temp_dir
from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.states import case_to_memo_view_state
from backend.intake.pipeline import DocumentInput, IntakePipeline
from backend.intake.schema import RejectedIntake

router = APIRouter()

_NO_SUCH_APPLICATION = "No such application."
_REJECTED = "The application did not pass intake validation."
_MALFORMED_BODY = "The request body was not a valid submission."
_MALFORMED_UPLOAD = "The uploaded documents could not be read."
_TOO_LARGE = "The uploaded documents exceed the size limit."
_DOCUMENTS_NEED_MULTIPART = "Attach documents with multipart/form-data, not JSON."
_MULTIPART = "multipart/form-data"


async def _json_form_fields(request: Request) -> dict[str, Any]:
    """R10's ORIGINAL JSON body, validated by hand.

    ⛔ **SUPERSEDES ``SubmissionRequest``, and the reason is structural, not stylistic.** Fold-6
    declared a Pydantic body model. A body PARAMETER makes FastAPI read the request body at
    ``routing.py:422`` — **before** ``solve_dependencies`` at ``:473`` — so an unauthorized
    caller's upload would be fully received before ``require_underwriter`` refused it. Fold-7
    removes the parameter entirely so the framework never touches the body, which means this
    function must do the validation the model used to do and produce the **identical** WIRE-1 §4
    envelope for a malformed body.

    The Fold-6 model is preserved here as the record of what this replaces::

        class SubmissionRequest(BaseModel):
            form_fields: dict[str, Any]
            documents: list[Any] = Field(default_factory=list)
    """
    try:
        body = json.loads(await request.body())
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise WireError(INVALID_REQUEST, _MALFORMED_BODY) from None
    if not isinstance(body, dict) or not isinstance(body.get("form_fields"), dict):
        raise WireError(INVALID_REQUEST, _MALFORMED_BODY)
    if body.get("documents"):
        # ⚑ The JSON encoding still carries no documents — that is what multipart is for.
        raise WireError(INVALID_REQUEST, _DOCUMENTS_NEED_MULTIPART)
    return body["form_fields"]


def _intake_and_submit(intake, pipeline, form_fields, documents):
    """The blocking half — intake (parsing included) then ``submit()``. Runs in a WORKER THREAD.

    ⛔ Rejection is raised from here and propagates out of the threadpool unchanged, so
    ``RejectedIntake`` still never enters the pipeline (Q8(a)) and no half-created row exists —
    whether the submission arrived as JSON or as multipart.
    """
    outcome = intake.process(form_fields, documents=documents).outcome
    if isinstance(outcome, RejectedIntake):
        raise WireError(INVALID_REQUEST, _REJECTED, detail=rejected_intake_detail(outcome))
    return pipeline.submit(outcome.application_id, outcome)


@router.post("/applications")
async def submit_application(
    request: Request,
    _identity: Identity = Depends(require_underwriter),
    intake: IntakePipeline = Depends(get_intake_pipeline),
    pipeline: CasePipeline = Depends(get_case_pipeline),
) -> dict[str, Any]:
    """R10. ⚑ **The first path in this build by which an application the system did not invent
    can enter it** — and the first exercise of U1 ``intake`` anywhere reachable.

    Error mapping (WIRE-1 §4, every code pre-existing):
      * wrong role / no session            -> **403** / **401**, before the body below runs
      * a non-empty ``documents`` list     -> **400** ``invalid_request`` (Q2(a): not this fold)
      * ``RejectedIntake``                 -> **400** ``invalid_request`` + per-field ``detail``

    ⚑ **REJECTION IS HANDLED HERE, BEFORE ``submit()`` IS EVER CALLED (Q8(a)).** ``submit()``
    returns ``PendingApplication`` and has **no failure channel** — the asymmetry register #27
    turned on. Rather than reopen U24 to give it one, the composition root decides: a rejected
    application never enters the pipeline, so **no half-created row exists** and ``submit()``'s
    contract stays intact.
    """
    content_type = request.headers.get("content-type", "")

    # ⛔ NOTHING HAS BEEN READ YET. The handler declares no body parameter, so FastAPI never
    # touched the body, and `require_underwriter` has already run. A refused caller costs
    # literally zero bytes of I/O — the property Fold A found degraded and Q13(b) restored.
    if content_type.lower().startswith(_MULTIPART):
        with upload_temp_dir() as directory:
            try:
                upload = await read_submission_multipart(
                    content_type, request.stream(), directory
                )
            except MultipartTooLarge:
                raise WireError(PAYLOAD_TOO_LARGE, _TOO_LARGE) from None
            except MultipartInvalid:
                raise WireError(INVALID_REQUEST, _MALFORMED_UPLOAD) from None

            documents = [
                DocumentInput(doc_type=doc_type, source_path=str(path))
                for doc_type, path in upload.documents.items()
            ]
            # ⛔ BOUNDED **and** OFF THE EVENT LOOP, in ONE call. `SubprocessParseWorker` runs
            # `subprocess.run`, which is fully blocking; on the loop it would freeze the whole
            # process for up to ~15 s, health checks included. The limiter caps concurrent
            # parses so N submissions cannot multiply 256 MB by N.
            application = await run_bounded_parse(
                _intake_and_submit, intake, pipeline, upload.form_fields, documents
            )
    else:
        form_fields = await _json_form_fields(request)
        # ⚑ OFFLOADED but deliberately NOT BOUNDED: the JSON encoding carries no documents, so it
        # spawns no subprocess. Bounding it would queue document-free submissions behind
        # document-bearing ones for nothing. It is still offloaded, because `submit()` writes to
        # the database synchronously and would otherwise block the loop.
        application = await run_in_threadpool(
            _intake_and_submit, intake, pipeline, form_fields, []
        )

    return {
        "application_id": application.application_id,
        "status": case_to_memo_view_state(application),
    }


@router.post("/applications/{application_id}/draft")
def trigger_drafting(
    application_id: str,
    _identity: Identity = Depends(require_underwriter),
    pipeline: CasePipeline = Depends(get_case_pipeline),
) -> dict[str, Any]:
    """R11. The explicit drafting trigger — the second half of Q3(a)'s two-phase flow.

    ⚑ **A SEPARATE ROUTE RATHER THAN A BACKGROUND TASK, DELIBERATELY.** Q3(c) was rejected
    because fire-and-forget work has *"no retry, no visibility, and no failure surface"*, and
    this project already treats crash-in-the-middle as a real condition (register #19's
    ``committing`` state exists for exactly that reason). An explicit POST keeps the transition
    visible and attributable, mirroring how the rest of the system exposes state changes.

    Error mapping (WIRE-1 §4, every code pre-existing):
      * unknown application                -> **404** ``not_found``
      * drafting produced no memo          -> **500** ``internal_error`` — see below
      * already drafted / already committed -> **200** ``outcome: "skipped"``, NOT an error

    ⚑ **RE-TRIGGERING IS IDEMPOTENT, NOT A FAILURE.** ``DraftOutcome.skipped`` is a FIELD, not a
    parsed string (register #27's change (c)): without that discriminator a repeat click would
    report a failure on every already-drafted case, *"which trains an operator to ignore FAILED
    lines — precisely how #18 stayed invisible"*.

    ⛔ **A GENUINE drafting failure maps to 500, and the case's ``failed`` state is NOT on the
    wire.** ``case_to_memo_view_state`` maps ``failed -> "pending"`` — **register #14**, open.
    WIRE1-Fold-6 declined to widen R4's ``ready | pending`` discriminator on #14's behalf, so
    this route declares only the two outcomes the contract can honestly express. The limitation
    is #14's to resolve; it is recorded here, not papered over.
    """
    if pipeline.read(application_id) is None:
        raise WireError(NOT_FOUND, _NO_SUCH_APPLICATION)

    outcome = pipeline.draft(application_id)
    if not outcome.succeeded and not outcome.skipped:
        raise WireError(INTERNAL_ERROR, "Drafting did not produce a memo.")

    case = pipeline.read(application_id)
    return {
        "application_id": application_id,
        "status": case_to_memo_view_state(case),
        "outcome": "drafted" if outcome.succeeded else "skipped",
    }
