"""C-CASE-1 — the case state machine + the pure wire projection.

**Header comment — DOCUMENTATION ONLY, never enforcement.** Every property below is
independently enforced by a C-CASE-8 scan carrying a detector self-test:
  * holds no LLM, builds no prompt, opens no socket;
  * edits no frozen unit (frozen shapes are imported READ-ONLY);
  * declares NO verdict;
  * **never re-implements the commit gate, the authz check, or a write to ``audit_record``**;
  * reaches no network at tier-U.

**P-CASE-4 (Q1-A).** ``LEGAL_TRANSITIONS`` is the **SINGLE SOURCE OF TRUTH**. The illegal set is
its **COMPLEMENT** over ``product(CaseState, CaseState)`` — never a second hand-maintained table.
Exhaustiveness is therefore **automatic**: a newly added state instantly appears in the derived
illegal set with **no test edit**, and two tables cannot drift because there is only one.

**P-CASE-8 (Q5-A).** ``case_to_memo_view_state`` is a **PURE** function (no I/O, no state) that the
composition root CALLS at wiring time rather than re-deriving. The ``failed -> "pending"``
projection is domain knowledge only this unit possesses.

⛔ **Register #14 MEMOVIEW-FAILED-STATE-UNMODELLED** — owner: **a future authorized WIRE-1 contract
amendment**. WIRE-1's ``MemoView.status`` admits only ``ready | pending``, so U24's internal
``failed`` state has **no wire representation** and projects to ``"pending"``. Rationale: adding a
third status value would amend WIRE-1's frozen contract text, which Scope B's holds forbid.
**U24 claims NO discharge of this item.** Non-blocking: the shape stays valid and the client still
renders; the loss is diagnostic precision at the wire, not correctness.

⚑ **REGISTER #14 WIDENED BY REGISTER #19's FIX.** ``COMMITTING`` is a **second** internal state
with no wire representation — it also projects to ``"pending"``. So a case that is *mid-commit*
is, at the wire, indistinguishable from one that has not been drafted yet. The widening is
**disclosed, not silently absorbed**: the same closed two-value discriminator now hides **two**
internal states rather than one, and both await the same future authorized WIRE-1 amendment.
**This fix claims NO discharge of register #14 either.**

⚑ **REGISTER #19 — THE COMMIT IS TWO-STEP.** ``drafted -> committed`` is no longer a legal single
transition. A commit takes the claim (``drafted -> committing``, a compare-and-swap) **before**
the frozen ``DecisionCommitService.commit()`` runs, and finalizes (``committing -> committed``)
**after** it returns; a commit that fails releases the claim (``committing -> drafted``). This
eliminates duplicate ``AuditRecord`` writes. ⚠️ It does **NOT** achieve cross-store atomicity —
a crash between the audit write and the finalize leaves the case in ``committing``, which is
explicit, non-terminal and reconcilable, but real.
"""
from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:  # pragma: no cover - typing only
    from backend.case_lifecycle.schemas import PendingApplication


class CaseState(str, Enum):
    """The lifecycle states plus TWO INTERNAL states.

    ``FAILED`` and ``COMMITTING`` are both internal to U24: neither ever appears as a wire
    value (see ``case_to_memo_view_state`` and register #14).

    ⚑ ``COMMITTING`` is the **claim state** added by register #19's fix. It is **NOT terminal**:
    it is either finalized to ``COMMITTED`` or released back to ``DRAFTED``.
    """

    SUBMITTED = "submitted"
    PROFILED = "profiled"
    EVALUATED = "evaluated"
    DRAFTED = "drafted"
    COMMITTING = "committing"
    COMMITTED = "committed"
    FAILED = "failed"


#: ⚑ THE SINGLE SOURCE OF TRUTH (Q1-A). The illegal set is derived as its COMPLEMENT.
#:
#: ⚑ **REGISTER #19 — THE COMMIT IS TWO-STEP.** ``DRAFTED -> COMMITTED`` is **deliberately
#: ABSENT**: committing goes ``DRAFTED -> COMMITTING -> COMMITTED``, so ``COMMITTED`` is
#: reachable **only** through the claim. Re-adding the direct edge would make the compare-and-swap
#: that eliminates duplicate ``AuditRecord``s **bypassable**, which is why its absence is asserted
#: by its own test rather than left to convention.
LEGAL_TRANSITIONS: frozenset[tuple[CaseState, CaseState]] = frozenset(
    {
        (CaseState.SUBMITTED, CaseState.PROFILED),
        (CaseState.PROFILED, CaseState.EVALUATED),
        (CaseState.EVALUATED, CaseState.DRAFTED),
        (CaseState.EVALUATED, CaseState.FAILED),
        (CaseState.DRAFTED, CaseState.COMMITTING),      # the CAS claim (register #19)
        (CaseState.COMMITTING, CaseState.COMMITTED),    # finalize, after the audit write
        (CaseState.COMMITTING, CaseState.DRAFTED),      # recovery — release a claim that failed
    }
)

#: Terminal states — no transition leaves them.
#:
#: ⚑ **UNCHANGED by register #19's fix.** ``COMMITTING`` is deliberately NOT here (it has two
#: out-edges), and ``FAILED``'s terminal status is untouched — FAILED-1 and COMMITBOUND-1(c)
#: are unaffected by this change.
TERMINAL_STATES: frozenset[CaseState] = frozenset({CaseState.COMMITTED, CaseState.FAILED})


class CommitClaimResult(str, Enum):
    """The outcome of a ``claim_for_commit`` compare-and-swap. **Register #19.**

    ⚑ **THREE values, not a bool.** A bare boolean would collapse ``LOST`` and ``NOT_FOUND``
    into one, silently turning R5's correct **404** for an unknown ``recommendation_id`` into a
    **409** — a WIRE-1 §4 regression introduced by the fix itself.

    ⚑ **None of these is an authorization decision.** ``NOT_FOUND`` is a plain row-existence
    answer, exactly like the ``UnknownPendingRecommendation`` that ``provider.py`` already
    raises for the same condition (COMMITBOUND-1 asserts that behaviour). The CON-BR4 gate and
    the independent authz re-check remain **inside the frozen ``DecisionCommitService``**, and
    this unit re-implements neither.
    """

    WON = "won"              # the CAS took the claim: drafted -> committing
    LOST = "lost"            # already committing or committed — R5 maps this to 409
    NOT_FOUND = "not_found"  # no such recommendation_id at all — R5 maps this to 404


class IllegalTransition(ValueError):
    """Raised when a transition is not in ``LEGAL_TRANSITIONS``."""

    def __init__(self, src: CaseState, dst: CaseState) -> None:
        super().__init__(f"illegal transition {src.value!r} -> {dst.value!r}")
        self.src = src
        self.dst = dst


def is_legal(src: CaseState, dst: CaseState) -> bool:
    """Membership in the ONE table. Pure."""
    return (src, dst) in LEGAL_TRANSITIONS


def assert_legal(src: CaseState, dst: CaseState) -> None:
    """Raise :class:`IllegalTransition` unless ``(src, dst)`` is legal."""
    if not is_legal(src, dst):
        raise IllegalTransition(src, dst)


def case_to_memo_view_state(case: "PendingApplication") -> Literal["ready", "pending"]:
    """The R4 wire state for a case. **PURE** — no I/O, no state (Q5-A).

    ``drafted`` -> ``"ready"``; **everything else, including ``failed`` AND ``committing``,
    -> ``"pending"``**.

    ⚑ The return annotation is a two-value ``Literal``, so emitting a third status is
    **structurally unrepresentable** — WIRE-1's discriminator has no third value (register #14).

    ⚑ **``COMMITTING`` needs no branch of its own** — it falls into the ``else`` and yields
    ``"pending"``, which is exactly right: a case mid-commit must **never** present as ``ready``.
    Register #19's fix therefore changed **this function's documentation, not its logic**.
    """
    return "ready" if case.state is CaseState.DRAFTED else "pending"
