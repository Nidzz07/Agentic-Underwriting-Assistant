"""C-CASE-6 — the REAL ``CommitContextProvider``. **Context only.**

**Header comment — DOCUMENTATION ONLY, never enforcement** (each property is scan-enforced in
C-CASE-8): holds no LLM; edits no frozen unit; declares no verdict; **never re-implements the
commit gate, the authz check, or a write to ``audit_record``**; no network at tier-U.

**P-CASE-3 / BR-CASE-13.** Until now the only implementation of the frozen
``audit_store.seams.CommitContextProvider`` Protocol was ``DictCommitContextProvider`` — labelled
by audit-store itself a *"Test/fake provider."* This is the real one.

⚑ **The human-in-the-loop enforcement is NOT here and must never be.** The CON-BR4 gate and the
independent authz re-check run **INSIDE the frozen ``DecisionCommitService.commit()``**, before any
assembly. This class supplies **assembly inputs only** — its return type is ``CommitContext``, so
*"the provider committed something"* is **unrepresentable**.

⚑ **A ``failed`` case can never reach this provider** (COMMITBOUND-1(c)). R5 is keyed by
``recommendation_id`` — the PK of ``PendingRecommendation`` — which is created **only** at the
``drafted`` transition. A failed case never reaches ``drafted``, so **the object R5 is keyed by
never exists for it**; ``get()`` raises and R5 returns 404. The failed path and the commit path
**structurally do not intersect**.
"""
from __future__ import annotations

from backend.audit_store.canon_adapter import CanonSerAdapter
from backend.audit_store.record_schema import CommitContext
from backend.case_lifecycle.store import CaseStore


class UnknownPendingRecommendation(KeyError):
    """No pending recommendation for that id — R5 maps this to 404."""


class PendingCommitContextProvider:
    """Satisfies the FROZEN ``CommitContextProvider`` Protocol. Performs no authz, no write."""

    def __init__(self, store: CaseStore) -> None:
        self._store = store

    def get(self, recommendation_id: str) -> CommitContext:
        """Assemble the frozen ``CommitContext``. **Context only — nothing else.**"""
        recommendation = self._store.get_recommendation(recommendation_id)
        if recommendation is None:
            raise UnknownPendingRecommendation(
                f"no pending recommendation for {recommendation_id!r}"
            )
        application = self._store.get_application(recommendation.application_id)
        if application is None:  # pragma: no cover - unreachable via the FK'd write path
            raise UnknownPendingRecommendation(
                f"no pending application for {recommendation.application_id!r}"
            )
        return CommitContext(
            rule_results=CanonSerAdapter.report_from_canonical(
                application.rule_results_canonical
            ),
            memo_hash=recommendation.memo_hash,
            model_version=recommendation.model_version,
            engine_version=recommendation.engine_version,
            rulebook_version=recommendation.rulebook_version,
            applicant_profile=CanonSerAdapter.profile_from_canonical(
                application.profile_canonical
            ),
        )
