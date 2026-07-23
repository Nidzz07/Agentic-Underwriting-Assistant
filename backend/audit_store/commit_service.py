"""DecisionCommitService — the CON-BR4 write-gate (Step 5).

FD ``business-rules.md §1/§2`` + NFR Design §1/§2/§3. A **single fail-closed
boundary**: the CON-BR4 total-function predicate (GATE-1) **and** the independent
backend authz re-check (AUTHZ-1) both gate the boundary **before** any assembly.
The pending-recommendation context is fetched via the injected
``CommitContextProvider`` (§1.5). The complete ``AuditRecord`` is **assembled +
Pydantic-validated BEFORE the transaction opens** (TUPLE-1) — a validation failure
opens no transaction — then the transaction wraps **only** the atomic write
(ATOMIC-1). ``decision_id`` / ``timestamp`` come from injected seams (audit
metadata, not in the replay equality set).

No LLM. Advisory-only: the persisted ``action`` is the human's committed choice —
the one correct use of "decision".
"""
from __future__ import annotations

from typing import Optional, Union

from backend.audit_store.canon_adapter import CanonSerAdapter
from backend.audit_store.record_schema import (
    ApplicantProfileSnapshot,
    AuditRecord,
    AuditTuple,
    CommitAction,
    CommittedDecision,
    DecisionStatus,
)
from backend.audit_store.repository import AuditRepository
from backend.audit_store.seams import (
    RBAC_COMMIT,
    Authorizer,
    Clock,
    CommitContextProvider,
    IdGenerator,
)


class CommitRejected(Exception):
    """The CON-BR4 gate rejected the commit (no ``AuditRecord`` written)."""


class UnauthorizedCommit(CommitRejected):
    """The backend authz re-check rejected a non-underwriter committer (SEC-4)."""


def _coerce_action(action: object) -> Optional[CommitAction]:
    """Return the ``CommitAction`` for a member/valid value, else ``None`` (→ reject).
    ``action`` is a CLOSED enum — anything outside it cannot commit."""
    if isinstance(action, CommitAction):
        return action
    try:
        return CommitAction(action)
    except (ValueError, KeyError):
        return None


class DecisionCommitService:
    def __init__(
        self,
        *,
        repository: AuditRepository,
        context_provider: CommitContextProvider,
        authorizer: Authorizer,
        id_generator: IdGenerator,
        clock: Clock,
    ) -> None:
        self._repository = repository
        self._context_provider = context_provider
        self._authorizer = authorizer
        self._id_generator = id_generator
        self._clock = clock

    def commit(
        self,
        recommendation_id: str,
        underwriter_id: str,
        action: Union[CommitAction, str],
        reason: Optional[str] = None,
    ) -> CommittedDecision:
        # 1. CON-BR4 gate predicate (GATE-1) — total function, BEFORE any assembly.
        checked_action = self._gate(underwriter_id, action, reason)
        # 2. Backend authz re-check (AUTHZ-1) — independent of the API layer.
        if not self._authorizer.authorize(underwriter_id, RBAC_COMMIT):
            raise UnauthorizedCommit(
                f"user {underwriter_id!r} is not authorized for {RBAC_COMMIT!r}"
            )
        # 3. Fetch the pending-recommendation context (§1.5 seam).
        context = self._context_provider.get(recommendation_id)
        # 4. Assemble + validate the COMPLETE record in memory — BEFORE BEGIN.
        record = self._assemble(recommendation_id, underwriter_id, checked_action, reason, context)
        # 5. Atomic write — the transaction wraps ONLY the write (both-or-neither).
        with self._repository.atomic():
            self._repository.insert(record)
        return record.committed_decision

    @staticmethod
    def _gate(underwriter_id: str, action: object, reason: Optional[str]) -> CommitAction:
        """BR-COMMIT-GATE: reject iff missing underwriter_id / action, action outside
        the closed enum, or an override with a trim-then-empty reason."""
        if underwriter_id is None or underwriter_id.strip() == "":
            raise CommitRejected("underwriter_id is required")
        checked_action = _coerce_action(action)
        if checked_action is None:
            raise CommitRejected("action must be one of {approve, override}")
        if checked_action is CommitAction.OVERRIDE and (reason is None or reason.strip() == ""):
            raise CommitRejected("an override requires a non-blank reason")
        return checked_action

    def _assemble(
        self,
        recommendation_id: str,
        underwriter_id: str,
        action: CommitAction,
        reason: Optional[str],
        context,
    ) -> AuditRecord:
        profile = context.applicant_profile
        snapshot = ApplicantProfileSnapshot(
            application_id=profile.application_id,
            profile=profile,
            content_hash=CanonSerAdapter.content_hash(profile),
        )
        audit_tuple = AuditTuple(
            rulebook_version=context.rulebook_version,
            rule_results=context.rule_results,
            timestamp=self._clock.now(),               # commit wall-clock — audit metadata
            model_version=context.model_version,
            memo_hash=context.memo_hash,
            engine_version=context.engine_version,
        )
        committed = CommittedDecision(
            recommendation_id=recommendation_id,
            underwriter_id=underwriter_id,
            action=action,
            reason=reason,
        )
        return AuditRecord(
            decision_id=self._id_generator.new_id(),   # system-generated PK (injected seam)
            application_id=profile.application_id,
            recommendation_id=recommendation_id,
            audit_tuple=audit_tuple,
            applicant_profile_snapshot=snapshot,
            committed_decision=committed,
            status=DecisionStatus.ACTIVE,
            supersedes_decision_id=None,
        )
