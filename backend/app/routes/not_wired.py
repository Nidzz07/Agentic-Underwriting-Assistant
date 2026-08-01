"""R2-R5 — the pending-application surface, WIRED IN PLACE (Scope B wiring pass).

⚑ **THE FILENAME IS STALE AND KNOWINGLY SO — register item #13 ``NOTWIRED-FILENAME-STALE``.**
This module no longer holds "not wired" markers: R2-R5 are REAL here. The name is kept
deliberately, because U23's frozen ``NFR-DEP-ROUTES-1`` asserts EXACT-SET equality over the
filenames in this directory, and renaming would break a LOAD-BEARING test in a frozen unit.
**Renaming this file and relaxing that assertion are a MATCHED PAIR** belonging to their own
authorized change (Q9-A/Q9-B). Scope B lives with the stale name and DISCLOSES it rather than
silently reconciling it.

    R2  GET  /applications?page=&size=        -> list wrapper of ApplicationSummary
    R3  GET  /applications/{id}               -> ApplicantProfile (intake's shape, verbatim)
    R4  GET  /applications/{id}/memo          -> MemoView (status: ready | pending)
    R5  POST /recommendations/{id}/commit     -> CommittedDecision

**COMPOSITION ONLY — no domain logic lives here.** Every handler is the established two-layer
thin adapter the composition root already used for R1/R6/R7: ``Depends(...)`` an injected frozen
object, call it, hand the result to a PURE projection in ``projections.py``. The lifecycle state
model, the pending stores, the drafting trigger and the real ``CommitContextProvider`` all live
in U24; the commit gate lives in the frozen ``DecisionCommitService``.

⚑ **R2/R3/R4 ARE PURE READS.** They call ``CaseStore.get_application`` /
``list_application_ids`` and U24's PURE ``case_to_memo_view_state``. **They never invoke a
pipeline step**, so no read path can trigger drafting (BR-CASE-4 / TRIGGER-1). ``CasePipeline``
is not even constructed in this package (Q3-D) — R4 is side-effect-free BY CONSTRUCTION, not by
discipline.

⚑ **R5 IS THE ONLY WRITE PATH IN THE APPLICATION, AND IT DELEGATES.** The CON-BR4 gate and the
independent ``RBAC_COMMIT`` re-check run INSIDE the frozen ``DecisionCommitService.commit()``,
before any assembly. This module re-implements NEITHER. The API-layer ``require_commit`` guard is
DEFENCE IN DEPTH only (Q6a) — the service remains the sole authority.
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from backend.app.dependencies import (
    Identity,
    current_identity,
    get_case_store,
    get_commit_service,
    require_commit,
)
from backend.app.errors import (
    COMMIT_CONFLICT,
    FORBIDDEN,
    NOT_FOUND,
    UNPROCESSABLE,
    WireError,
)
from backend.app.projections import (
    DEFAULT_PAGE_SIZE,
    application_list_wrapper,
    application_summary,
    memo_view,
)
from backend.audit_store.canon_adapter import CanonSerAdapter
from backend.audit_store.commit_service import (
    CommitRejected,
    DecisionCommitService,
    UnauthorizedCommit,
)
from backend.audit_store.record_schema import CommitAction
from backend.case_lifecycle.memo_adapter import MemoCanonAdapter
from backend.case_lifecycle.provider import UnknownPendingRecommendation
from backend.case_lifecycle.repository import PostgresCaseStore
from backend.case_lifecycle.states import CommitClaimResult, case_to_memo_view_state

router = APIRouter()

#: The static 404 for an unknown application/recommendation. WIRE-1 §4: the caller's own id is
#: never echoed back in message/detail.
_NO_SUCH_APPLICATION = "No such application."
_NO_SUCH_RECOMMENDATION = "No such recommendation."

#: The closed wire-shape set for R5's ``action`` (WIRE-1 §4 -> 422). ⚑ A WIRE-SHAPE check only —
#: the frozen ``_gate`` still validates the action independently and still rejects on its own.
_PERMITTED_COMMIT_ACTIONS = frozenset(member.value for member in CommitAction)


def _release(store, recommendation_id: str) -> None:
    """Release a claim taken by R5, **never masking the rejection that caused the release**.

    ⚑ Register #19. If recovery itself fails, the caller must still receive the ORIGINAL status
    (a 409/403/404) rather than a 500: a case stranded in ``committing`` is a reconciliation
    problem the reconciliation script exists for, but a 500 in place of a 409 would be a lie
    about what actually happened to the commit. Swallowing here is therefore deliberate — the
    stranded row remains detectable, and the honest status still reaches the client.
    """
    try:
        store.release_claim(recommendation_id)
    except Exception:                       # noqa: BLE001 - see the docstring: never mask
        pass


def _load_report(case) -> Optional[object]:
    """Rehydrate the rule report through the FROZEN adapter. ``None`` before ``evaluated``."""
    if case.rule_results_canonical is None:
        return None
    return CanonSerAdapter.report_from_canonical(case.rule_results_canonical)


@router.get("/applications")
def list_applications(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=100),
    _identity: Identity = Depends(current_identity),
    store: PostgresCaseStore = Depends(get_case_store),
) -> dict[str, Any]:
    """R2. Authenticated, ANY role (WIRE-1 §3) — no named permission applies.

    ⚑ Deliberately uses ``current_identity``, NOT ``require_read_audit``: R6/R7's READ_AUDIT
    carries the recorded, still-unresolved Q1-B divergence, and propagating it onto a route the
    contract marks "any role" would spread a known defect rather than contain it.

    ⚑ N+1 BY CONSTRUCTION, amplified beyond R6's (register #15): enumerate all ids, then per row
    a ``get_application`` + a CANON-SER rehydration + a ``recommendation_for_application``. The
    accepted cost of keeping pagination in-app; pushing limit/offset into U24 is a separate
    change. Harmless at Phase-1 volumes; one bounded page still crosses the wire.
    """
    summaries = []
    for application_id in store.list_application_ids():
        case = store.get_application(application_id)
        if case is None:  # pragma: no cover - a row cannot vanish between the two reads here
            continue
        recommendation = store.recommendation_for_application(application_id)
        summaries.append(
            application_summary(application_id, _load_report(case), recommendation)
        )
    return application_list_wrapper(summaries, page=page, size=size)


@router.get("/applications/{application_id}")
def get_application(
    application_id: str,
    _identity: Identity = Depends(current_identity),
    store: PostgresCaseStore = Depends(get_case_store),
) -> dict[str, Any]:
    """R3. The applicant profile — ``intake.schema.ApplicantProfile``, intake's contract governs.

    Serialized by the frozen Pydantic model itself, so this route neither re-declares nor
    re-cases the shape (the ``audit_record_wire`` precedent).
    """
    case = store.get_application(application_id)
    if case is None:
        raise WireError(NOT_FOUND, _NO_SUCH_APPLICATION)
    profile = CanonSerAdapter.profile_from_canonical(case.profile_canonical)
    return profile.model_dump(mode="json")


@router.get("/applications/{application_id}/memo")
def get_application_memo(
    application_id: str,
    _identity: Identity = Depends(current_identity),
    store: PostgresCaseStore = Depends(get_case_store),
) -> dict[str, Any]:
    """R4. The combined memo view. ⚑ A PURE, SIDE-EFFECT-FREE GET — it never triggers drafting.

    ``status`` comes from U24's PURE ``case_to_memo_view_state``: ``drafted -> "ready"``,
    everything else INCLUDING ``failed`` -> ``"pending"`` (register #14 — ``failed`` has no wire
    representation, so a failed case reports as pending; disclosed, not resolved here).
    """
    case = store.get_application(application_id)
    if case is None:
        raise WireError(NOT_FOUND, _NO_SUCH_APPLICATION)

    status = case_to_memo_view_state(case)
    profile = CanonSerAdapter.profile_from_canonical(case.profile_canonical)
    recommendation = store.recommendation_for_application(application_id)

    report = _load_report(case) if status == "ready" else None
    memo = (
        # U24's OWN thin adapter (its SECOND authorized reopening, Q14-A) — the frozen
        # CanonSerAdapter rehydrates only ApplicantProfile/RuleResultReport, and putting a
        # canon_deserialize call here would move U24's domain knowledge into the composition root.
        #
        # ⚑ SUPERSEDED, preserved: this read "its THIRD authorized reopening". Off by one.
        # BUILD-COMPLETION-REPORT.md:198 and :303 are the authoritative record — the Scope B
        # wiring pass required TWO reopenings (`list_application_ids()` and this adapter,
        # `memo_from_canonical()`), making register #19's two-step commit claim the THIRD.
        # (Register #27/#28's fix is the fourth.) Corrected as an ordinary non-frozen edit:
        # this file is the composition root, NOT part of `case_lifecycle`, so it needed no
        # reopening authority. Numbering only — no behaviour, and no other claim, changes.
        MemoCanonAdapter.memo_from_canonical(recommendation.memo_canonical)
        if (status == "ready" and recommendation is not None)
        else None
    )
    return memo_view(case, status, profile, report, memo, recommendation)


class CommitRequest(BaseModel):
    """R5's body (WIRE-1 §5 / WIRE1-Fold-1).

    ⚑ ``action`` is typed ``str``, NOT ``Literal["approve","override"]``, DELIBERATELY. A
    ``Literal`` mismatch raises ``RequestValidationError``, which this app's GLOBAL handler maps
    to **400** — but WIRE-1 §4 assigns an action outside the enum to **422**. Typing it ``str``
    and checking membership in the handler yields the contract's 422 while leaving the global
    envelope handler (and its frozen test) completely untouched (Q13-A).

    ⚑ ``underwriter_id`` is deliberately ABSENT: it comes from the authenticated session, so a
    client cannot commit AS ANOTHER USER. ``recommendation_id`` comes from the path.
    """

    action: str
    reason: Optional[str] = None


@router.post("/recommendations/{recommendation_id}/commit")
def commit_recommendation(
    recommendation_id: str,
    body: CommitRequest,
    identity: Identity = Depends(require_commit),
    service: DecisionCommitService = Depends(get_commit_service),
    store: PostgresCaseStore = Depends(get_case_store),
) -> dict[str, Any]:
    """R5. The ONLY write path in the application — and it DELEGATES, it does not enforce.

    ⚑ The human-in-the-loop invariant is satisfied by the FROZEN service, not by this route: the
    CON-BR4 gate and the independent authz re-check run INSIDE ``commit()``, before any assembly.
    This handler cannot bypass them and re-implements neither.

    Error mapping (WIRE-1 §4):
      * action outside ``{approve, override}``      -> **422** (checked below, see ``CommitRequest``)
      * ``UnauthorizedCommit``                      -> **403**
      * ``UnknownPendingRecommendation``            -> **404**
      * any other ``CommitRejected`` (the gate)     -> **409**  — e.g. a blank-reason override

    ⚑ The membership check below is a CLOSED-ENUM WIRE-SHAPE check ("is this string one of two
    literal values"), NOT a re-implementation of the gate: it inspects no authorization and no
    business rule, and the frozen ``_gate`` still runs and still rejects independently. Because
    a malformed action is rejected here, every ``CommitRejected`` reaching the ``except`` below
    is unambiguously a GATE rejection, which is what makes the 409 mapping honest.

    ⚑ **REGISTER #19 — THE TWO-STEP COMMIT CLAIM. This is what fixes the double-commit defect.**

    The handler takes a **compare-and-swap claim** (``drafted -> committing``) on U24's case
    store **before** calling the frozen service, and **finalizes** it (``committing ->
    committed``) after ``commit()`` returns. Because the CAS is a single conditional ``UPDATE``,
    **concurrent callers serialize on the row's write lock and exactly one wins** — so the same
    ``recommendation_id`` can no longer write a duplicate ``AuditRecord``. WIRE-1 §4's
    *"already-committed recommendation -> 409"* is now **genuinely enforced, including under
    concurrent access**, and a committed case no longer reports ``ready`` on R4 forever.

    ⚑ **The claim is NOT an authorization decision and NOT a second gate.** It is a state
    check on a row U24 owns. The CON-BR4 gate and the independent AUTHZ-1 re-check still run
    **inside the frozen ``commit()``**, unmodified, and this handler re-implements neither.

    ⚑ **Every rejection RELEASES the claim** (``committing -> drafted``), so an ordinary user
    error — a blank-reason override, say — leaves the case exactly as it was and immediately
    re-committable. A release that itself fails must **not** mask the original rejection.

    ⚠️ **What this does NOT achieve: cross-store atomicity.** ``audit_record`` and the pending
    store are two transactional boundaries on two engines, and merging them would require
    editing a frozen unit. **A crash between the audit write and the finalize leaves the case in
    ``committing``** — explicit, non-terminal, detectable and reconcilable
    (``backend/scripts/reconcile_committing_cases.py``), but real. A narrow, disclosed window
    replacing an unbounded, always-reachable defect — **not** perfect atomicity.
    """
    if body.action not in _PERMITTED_COMMIT_ACTIONS:
        raise WireError(UNPROCESSABLE, "The action is not a permitted commit action.")

    # ⚑ THE CLAIM — before the frozen service is reached. A lost claim short-circuits, so
    # commit() is never invoked for an already-claimed or already-committed recommendation.
    claim = store.claim_for_commit(recommendation_id)
    if claim is CommitClaimResult.NOT_FOUND:
        raise WireError(NOT_FOUND, _NO_SUCH_RECOMMENDATION)
    if claim is CommitClaimResult.LOST:
        raise WireError(COMMIT_CONFLICT, "This recommendation has already been committed.")

    try:
        committed = service.commit(
            recommendation_id=recommendation_id,
            underwriter_id=identity.user_id,
            action=body.action,
            reason=body.reason,
        )
    except UnauthorizedCommit:
        # The frozen service's OWN re-check refused — the authoritative denial (require_commit
        # is only defence in depth and may already have caught this).
        _release(store, recommendation_id)
        raise WireError(FORBIDDEN, "You do not have permission to commit a decision.")
    except UnknownPendingRecommendation:
        _release(store, recommendation_id)
        raise WireError(NOT_FOUND, _NO_SUCH_RECOMMENDATION)
    except CommitRejected:
        # The CON-BR4 gate rejected it — e.g. an override with a blank reason (WIRE-1 §4: 409).
        _release(store, recommendation_id)
        raise WireError(COMMIT_CONFLICT, "The commit was rejected by the approval gate.")

    store.finalize_commit(recommendation_id)
    return committed.model_dump(mode="json")
