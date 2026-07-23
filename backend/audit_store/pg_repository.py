"""PostgresAuditRepository — the real persistence impl (Step 9).

NFR Design §2; DATA-5 (PostgreSQL, no SQLite). SQLAlchemy 2.x Core behind the same
``AuditRepository`` Protocol as the in-memory fake. ``atomic()`` is a single
``engine.begin()`` transaction (BEGIN … COMMIT; rollback on any exception) — the
both-or-neither boundary (ATOMIC-1). Both writes (the ``audit_record`` row + the
``applicant_profile_snapshot`` child row) happen inside it. The load path
**deserializes** the CANON-SER columns back to the exact intake ``ApplicantProfile``
+ rules-engine ``RuleResultReport`` via the ``CanonSerAdapter`` (REPLAY-2 fidelity).

The Table **metadata** below is the shape audit-store reads/writes; the
**production DDL / migrations / role-grants are owned by the ``database`` unit**
(reference-not-own). Only the integration TEST fixture materializes these tables.

Exercised via testcontainers integration in CI (no SQLite locally); omitted from
unit-tier coverage (``pyproject`` ``omit``).
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

import sqlalchemy as sa

from backend.audit_store.canon_adapter import CanonSerAdapter
from backend.audit_store.record_schema import (
    ApplicantProfileSnapshot,
    AuditRecord,
    AuditTuple,
    CommitAction,
    CommittedDecision,
    DecisionStatus,
)

metadata = sa.MetaData()

#: The committed-decision row (the 6-tuple + linkage + seam; rule_results as CANON-SER bytes).
audit_record = sa.Table(
    "audit_record", metadata,
    sa.Column("decision_id", sa.String, primary_key=True),
    sa.Column("application_id", sa.String, nullable=False, index=True),
    sa.Column("recommendation_id", sa.String, nullable=False),
    sa.Column("rulebook_version", sa.String, nullable=False),
    sa.Column("rule_results", sa.LargeBinary, nullable=False),        # CANON-SER bytes
    sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    sa.Column("model_version", sa.String, nullable=False),
    sa.Column("memo_hash", sa.String, nullable=False),
    sa.Column("engine_version", sa.String, nullable=False),
    sa.Column("underwriter_id", sa.String, nullable=False),
    sa.Column("action", sa.String, nullable=False),
    sa.Column("reason", sa.String, nullable=True),
    sa.Column("status", sa.String, nullable=False),
    sa.Column("supersedes_decision_id", sa.String, nullable=True),
)

#: The persisted original input — a separate co-located child row (FK), so ATOMIC-1
#: is a genuine multi-row both-or-neither write.
applicant_profile_snapshot = sa.Table(
    "applicant_profile_snapshot", metadata,
    sa.Column("decision_id", sa.String, sa.ForeignKey("audit_record.decision_id"), primary_key=True),
    sa.Column("application_id", sa.String, nullable=False),
    sa.Column("profile_canonical", sa.LargeBinary, nullable=False),  # CANON-SER bytes
    sa.Column("content_hash", sa.String, nullable=False),
)


class PostgresAuditRepository:
    """Insert + read only (no update/delete) over Postgres — APPEND-1 at the service
    layer; the DB ``audit_writer``/``audit_reader`` roles enforce it at the DB."""

    def __init__(self, engine: sa.Engine) -> None:
        self._engine = engine
        self._conn: Optional[sa.Connection] = None

    @contextmanager
    def atomic(self) -> Iterator[None]:
        with self._engine.begin() as conn:      # BEGIN … COMMIT; rollback on exception
            self._conn = conn
            try:
                yield
            finally:
                self._conn = None

    def insert(self, record: AuditRecord) -> None:
        if self._conn is None:
            raise RuntimeError("insert() must run inside atomic()")
        t, cd, snap = record.audit_tuple, record.committed_decision, record.applicant_profile_snapshot
        self._conn.execute(audit_record.insert().values(
            decision_id=record.decision_id,
            application_id=record.application_id,
            recommendation_id=record.recommendation_id,
            rulebook_version=t.rulebook_version,
            rule_results=CanonSerAdapter.canonical_bytes(t.rule_results),
            timestamp=t.timestamp,
            model_version=t.model_version,
            memo_hash=t.memo_hash,
            engine_version=t.engine_version,
            underwriter_id=cd.underwriter_id,
            action=cd.action.value,
            reason=cd.reason,
            status=record.status.value,
            supersedes_decision_id=record.supersedes_decision_id,
        ))
        self._conn.execute(applicant_profile_snapshot.insert().values(
            decision_id=record.decision_id,
            application_id=snap.application_id,
            profile_canonical=CanonSerAdapter.canonical_bytes(snap.profile),
            content_hash=snap.content_hash,
        ))

    def get(self, decision_id: str) -> Optional[AuditRecord]:
        with self._engine.connect() as conn:
            return self._load_one(conn, decision_id)

    def browse(self, application_id: Optional[str] = None) -> list[AuditRecord]:
        with self._engine.connect() as conn:
            query = sa.select(audit_record.c.decision_id)
            if application_id is not None:
                query = query.where(audit_record.c.application_id == application_id)
            ids = [row[0] for row in conn.execute(query.order_by(audit_record.c.decision_id))]
            return [self._load_one(conn, decision_id) for decision_id in ids]

    def exists_superseding(self, decision_id: str) -> bool:
        with self._engine.connect() as conn:
            query = sa.select(sa.func.count()).select_from(audit_record).where(
                audit_record.c.supersedes_decision_id == decision_id)
            return conn.execute(query).scalar_one() > 0

    @staticmethod
    def _load_one(conn: sa.Connection, decision_id: str) -> Optional[AuditRecord]:
        rec = conn.execute(sa.select(audit_record).where(
            audit_record.c.decision_id == decision_id)).mappings().first()
        if rec is None:
            return None
        snap = conn.execute(sa.select(applicant_profile_snapshot).where(
            applicant_profile_snapshot.c.decision_id == decision_id)).mappings().first()
        return AuditRecord(
            decision_id=rec["decision_id"],
            application_id=rec["application_id"],
            recommendation_id=rec["recommendation_id"],
            audit_tuple=AuditTuple(
                rulebook_version=rec["rulebook_version"],
                rule_results=CanonSerAdapter.report_from_canonical(rec["rule_results"]),
                timestamp=rec["timestamp"],
                model_version=rec["model_version"],
                memo_hash=rec["memo_hash"],
                engine_version=rec["engine_version"],
            ),
            applicant_profile_snapshot=ApplicantProfileSnapshot(
                application_id=snap["application_id"],
                profile=CanonSerAdapter.profile_from_canonical(snap["profile_canonical"]),
                content_hash=snap["content_hash"],
            ),
            committed_decision=CommittedDecision(
                recommendation_id=rec["recommendation_id"],
                underwriter_id=rec["underwriter_id"],
                action=CommitAction(rec["action"]),
                reason=rec["reason"],
            ),
            status=DecisionStatus(rec["status"]),
            supersedes_decision_id=rec["supersedes_decision_id"],
        )
