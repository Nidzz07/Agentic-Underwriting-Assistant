"""AuditRepository — the persistence boundary (Step 4).

NFR Design §2/§4. A **Protocol** with an **in-memory fake** (unit tier) and a
Postgres impl (``pg_repository.py``, integration tier). The surface is **insert +
read ONLY — no ``update``, no ``delete`` method** (structural APPEND-1). The
``atomic()`` unit-of-work is the single boundary the whole write happens inside;
on any exception it **rolls back** (both-or-neither — ATOMIC-1). ``exists_superseding``
is the STATUS-1 derived-superseded **read** (never a write path).
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional, Protocol, runtime_checkable

from backend.audit_store.record_schema import AuditRecord


class FaultInjected(Exception):
    """A test-injected persist fault (drives the ATOMIC-1 both-or-neither assertion)."""


@runtime_checkable
class AuditRepository(Protocol):
    """Insert + read only. NO update/delete — append-only by construction."""

    def atomic(self) -> Iterator[None]: ...
    def insert(self, record: AuditRecord) -> None: ...
    def get(self, decision_id: str) -> Optional[AuditRecord]: ...
    def browse(self, application_id: Optional[str] = None) -> list[AuditRecord]: ...
    def exists_superseding(self, decision_id: str) -> bool: ...


class InMemoryAuditRepository:
    """In-memory fake for the unit tier. ``atomic()`` buffers inserts and flushes
    only on a clean exit — simulating a transaction's both-or-neither rollback."""

    def __init__(self, fail_on_insert: bool = False) -> None:
        self._store: dict[str, AuditRecord] = {}
        self._pending: Optional[list[AuditRecord]] = None
        self._fail_on_insert = fail_on_insert

    @contextmanager
    def atomic(self) -> Iterator[None]:
        self._pending = []
        try:
            yield
        except BaseException:
            self._pending = None            # rollback — discard buffered inserts
            raise
        else:
            for record in self._pending:    # commit — flush buffered inserts atomically
                self._store[record.decision_id] = record
            self._pending = None

    def insert(self, record: AuditRecord) -> None:
        if self._pending is None:
            raise RuntimeError("insert() must run inside atomic()")
        self._pending.append(record)
        if self._fail_on_insert:            # injected fault -> the atomic block rolls back
            raise FaultInjected("injected persist fault")

    def get(self, decision_id: str) -> Optional[AuditRecord]:
        return self._store.get(decision_id)

    def browse(self, application_id: Optional[str] = None) -> list[AuditRecord]:
        records = list(self._store.values())
        if application_id is not None:
            records = [r for r in records if r.application_id == application_id]
        return sorted(records, key=lambda r: r.decision_id)

    def exists_superseding(self, decision_id: str) -> bool:
        """Derived-superseded read (STATUS-1): a record is superseded iff a newer
        record references it via ``supersedes_decision_id`` — a pure read."""
        return any(r.supersedes_decision_id == decision_id for r in self._store.values())
