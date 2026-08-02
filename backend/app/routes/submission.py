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

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.app.dependencies import (
    Identity,
    get_case_pipeline,
    get_intake_pipeline,
    require_underwriter,
)
from backend.app.errors import INTERNAL_ERROR, INVALID_REQUEST, NOT_FOUND, WireError
from backend.app.projections import rejected_intake_detail
from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.states import case_to_memo_view_state
from backend.intake.pipeline import IntakePipeline
from backend.intake.schema import RejectedIntake

router = APIRouter()

_NO_SUCH_APPLICATION = "No such application."
_REJECTED = "The application did not pass intake validation."
_DOCUMENTS_NOT_WIRED = "Document upload is not supported; submit structured fields only."


class SubmissionRequest(BaseModel):
    """R10's body (WIRE-1 §5, WIRE1-Fold-6).

    ⚑ ``form_fields`` is typed ``dict``, NOT a re-declared applicant schema, deliberately. Its
    key vocabulary belongs to **intake**, whose ``IntakeGate`` is the SEC-2 total-function
    validation boundary — *"every input, including arbitrary garbage, maps to exactly one of
    ``ApplicantProfile | RejectedIntake`` and NO input can cause an unhandled raise"*. Mirroring
    those fields in a Pydantic model here would fork a frozen unit's contract into the
    composition root and give two places to keep in step, while converting intake's rich
    ``RejectedIntake`` (per-field errors, missing items, a reason category) into FastAPI's flat
    422 — the same reasoning that types R5's ``action`` as ``str`` rather than a ``Literal``.

    ⚑ ``application_id`` is deliberately ABSENT: it is assigned by ``IntakeGate`` on gate pass,
    so a client cannot choose its own — the same shape as R5's server-derived ``underwriter_id``.
    """

    form_fields: dict[str, Any]
    documents: list[Any] = Field(default_factory=list)


@router.post("/applications")
def submit_application(
    body: SubmissionRequest,
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
    if body.documents:
        raise WireError(INVALID_REQUEST, _DOCUMENTS_NOT_WIRED)

    outcome = intake.process(body.form_fields, documents=[]).outcome
    if isinstance(outcome, RejectedIntake):
        raise WireError(INVALID_REQUEST, _REJECTED, detail=rejected_intake_detail(outcome))

    application = pipeline.submit(outcome.application_id, outcome)
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
