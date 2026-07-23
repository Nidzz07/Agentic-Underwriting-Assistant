"""C-CASE-4 — the injected persistence seam: ONE Protocol, two implementations.

**Header comment — DOCUMENTATION ONLY, never enforcement** (each property is scan-enforced in
C-CASE-8): holds no LLM; edits no frozen unit; declares no verdict; **never re-implements the
commit gate, the authz check, or a write to ``audit_record``**; no network at tier-U.

**P-CASE-5 / CASE-ND-Fold-1 — why ``atomic()`` is EXPOSED on the Protocol.**
The frozen ``audit_store.repository.AuditRepository`` exposes ``atomic()``, and its
``InMemoryAuditRepository`` *"buffers inserts and flushes only on a clean exit — simulating a
transaction's both-or-neither rollback."* U24 mirrors that **verbatim**, deliberately:

  * with a single **composite method**, the tier-U fake would satisfy atomicity **TRIVIALLY** — a
    single method body cannot half-execute in a single-threaded test — so **EAGER-1's "no partial
    row" assertion and COMMITBOUND-1(d) would be VACUOUS**;
  * with ``atomic()`` **plus a buffering fake**, "no partial row" **actually tests something**:
    inject a fault mid-transaction and assert **nothing was flushed**.

Both implementations honour atomicity through the **same Protocol shape** — the tier-U fake
(``tests/fixtures.InMemoryCaseStore``) and the tier-I SQL shim (``repository.py``). **PERSIST-1
(tier-I) is what checks the two agree.**
"""
from __future__ import annotations

from typing import Iterator, Optional, Protocol

from backend.case_lifecycle.schemas import PendingApplication, PendingRecommendation
from backend.case_lifecycle.states import CommitClaimResult


class CaseStore(Protocol):
    """Pending-state persistence. **No commit path, no audit_record access.**"""

    def atomic(self) -> Iterator[None]:
        """Both-or-neither. Writes inside a failed block MUST NOT be visible afterwards."""
        ...

    def put_application(self, application: PendingApplication) -> None: ...

    def get_application(self, application_id: str) -> Optional[PendingApplication]: ...

    def put_recommendation(self, recommendation: PendingRecommendation) -> None: ...

    def get_recommendation(
        self, recommendation_id: str
    ) -> Optional[PendingRecommendation]: ...

    def recommendation_for_application(
        self, application_id: str
    ) -> Optional[PendingRecommendation]: ...

    def list_application_ids(self) -> list[str]:
        """⚑ Added by the AUTHORIZED U24 REOPENING (Scope B wiring pass, Q1-A).

        R2 (``GET /applications?page=&size=``) is a **paginated list**, and this Protocol
        previously exposed **no enumeration primitive at all** — every method was keyed by a
        single id. R2 was therefore not implementable against U24's public surface, which is
        what the reopening exists to fix.

        ⚑ Returns **IDS ONLY, never rehydrated aggregates.** Two reasons, both deliberate:

          * **ADAPTER-1 stays intact.** ``repository.py`` must contain **no canonicalization
            call at all** (a POSITIVE assertion). Returning ids keeps the shim free of any
            CANON-SER rehydration; the composition root re-reads each case through the
            existing ``get_application`` and rehydrates via the **frozen** ``CanonSerAdapter``,
            exactly as R3/R4 do.
          * **No new projection duty enters the store.** The store stays a persistence seam;
            the wire shape stays ``projections.py``'s job.

        Order is the store's own and is **NOT a designed guarantee** — the composition root
        asserts whatever it actually observes rather than inventing a contract (the Q3-A
        precedent set for R6).
        """
        ...

    # --- register #19: the two-step commit claim (U24's THIRD authorized reopening) --------
    #
    # ⚑ ALL THREE ARE KEYED BY ``recommendation_id``, NOT ``application_id`` (A2). R5 is keyed
    # by the recommendation, while the state lives on ``PendingApplication`` — so U24 performs
    # the join INTERNALLY. Keying by ``application_id`` would force the composition root to
    # resolve the mapping first, which (a) reintroduces a read-then-act window at the call site
    # — the exact defect class this fix removes — and (b) puts the application<->recommendation
    # relationship inside ``backend/app/``, breaking its "no domain logic" invariant.
    #
    # ⚑ EACH OPENS ITS OWN ``atomic()`` INTERNALLY. The caller never wraps them. This is what
    # keeps ``backend/app/`` free of any transaction (INT-FAITHFUL-1) and is required anyway for
    # the compare-and-swap to be a single serialized operation.

    def claim_for_commit(self, recommendation_id: str) -> CommitClaimResult:
        """**COMPARE-AND-SWAP** ``drafted -> committing``. The duplicate-commit guard.

        ⚑ **The guarantee is the DATABASE's, not the application's.** The SQL implementation is
        one conditional ``UPDATE ... WHERE state = 'drafted'``; concurrent callers serialize on
        the row's write lock, so **exactly one wins** no matter how the requests interleave.
        This is why it eliminates duplicate ``AuditRecord``s rather than merely narrowing the
        window.

        Returns :class:`CommitClaimResult` — ``WON`` (proceed to commit), ``LOST`` (already
        claimed or already committed), or ``NOT_FOUND`` (no such recommendation).

        ⚑ Performs **no authorization and no gate check**. Whether the caller *may* commit is
        decided **inside the frozen ``DecisionCommitService.commit()``**, which still runs
        afterwards, unmodified and independently.
        """
        ...

    def finalize_commit(self, recommendation_id: str) -> None:
        """``committing -> committed``, after the frozen service's audit write RETURNED.

        ⚑ Runs **outside** the frozen service's transaction — it cannot be inside one, because
        ``commit()`` exposes no post-write hook and ``audit_record`` lives on a different engine.
        A crash between the audit write and this call leaves the case in ``committing``: the
        explicit, reconcilable residual window this design accepts and discloses.
        """
        ...

    def release_claim(self, recommendation_id: str) -> None:
        """``committing -> drafted`` — RECOVERY. Makes a failed attempt retryable.

        ⚑ Called when ``commit()`` **rejects** (a blank-reason override, an unauthorized
        caller, an unknown recommendation). Without it an ordinary, expected rejection would
        strand the case in ``committing`` forever — trading one defect for a worse one.
        """
        ...
