"""AuditService — the auditor read-only surface (Step 7).

FD ``business-rules.md §4``; NFR Design §6. **Read-only** queries — ``get`` +
``browse_history`` return the full 6-tuple; there is **no write method** (READ-1
structural; the DB-level read-only ``audit_reader`` role enforces it at the DB, and
the backend authz for the write path). The persisted history **is** the SEC-5 audit
trail (LOG-1). ``effective_status`` / ``is_superseded`` is the **derived-superseded
READ** over the reserved ``supersedes_decision_id`` — never an in-place status write
(STATUS-1); Phase-1/2 always resolves ``active``.
"""
from __future__ import annotations

from typing import Optional

from backend.audit_store.record_schema import AuditRecord, DecisionStatus
from backend.audit_store.repository import AuditRepository


class AuditNotFound(KeyError):
    """No ``AuditRecord`` exists for the requested ``decision_id``."""


class AuditService:
    def __init__(self, repository: AuditRepository) -> None:
        self._repository = repository

    def get(self, decision_id: str) -> Optional[AuditRecord]:
        return self._repository.get(decision_id)

    def browse_history(self, application_id: Optional[str] = None) -> list[AuditRecord]:
        return self._repository.browse(application_id)

    def is_superseded(self, decision_id: str) -> bool:
        """Derived-superseded READ — a record is superseded iff a newer record
        references it via ``supersedes_decision_id`` (Phase-1/2 → always False)."""
        return self._repository.exists_superseding(decision_id)

    def effective_status(self, decision_id: str) -> DecisionStatus:
        record = self._repository.get(decision_id)
        if record is None:
            raise AuditNotFound(decision_id)
        if self._repository.exists_superseding(decision_id):
            return DecisionStatus.SUPERSEDED
        return record.status
