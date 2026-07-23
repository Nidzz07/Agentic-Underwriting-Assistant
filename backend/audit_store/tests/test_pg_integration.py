"""Integration tests — real Postgres via testcontainers (Step 10).

Maps the DB-touching halves: NFR-AUDIT-ATOMIC-1 (multi-row both-or-neither under a
fault), NFR-AUDIT-APPEND-1 (DB-role: UPDATE/DELETE raise for audit_writer/audit_reader),
NFR-AUDIT-READ-1 / -LOG-1 (auditor read surface), NFR-AUDIT-TUPLE-1-persisted (full
record round-trips, CANON-SER fidelity). DATA-5: real PostgreSQL, no SQLite.

Auto-skipped when SQLAlchemy / testcontainers / Docker are unavailable (local dev);
MUST run in CI.

============================================================================
TEST-ONLY DDL — **NOT** the production schema.
The 2-table normalized shape (audit_record + applicant_profile_snapshot child) and
the audit_writer/audit_reader roles below are a **TEST-HARNESS choice** to exercise
multi-row atomicity (ATOMIC-1) + the DB-role enforcement (APPEND-1). The **production
schema (single-table vs normalized) + role-grant DDL are owned by the `database`
unit**, bound only by the co-location constraint. Do NOT treat this fixture as the
`database` unit's deliverable.
============================================================================
"""
from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("testcontainers.postgres")

import sqlalchemy as sa
from testcontainers.postgres import PostgresContainer

from backend.audit_store import record_schema as rs
from backend.audit_store.pg_repository import (
    PostgresAuditRepository,
    applicant_profile_snapshot,
    audit_record,
    metadata,
)
from backend.audit_store.tests import factories as f

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def admin_engine():
    with PostgresContainer("postgres:16") as pg:
        engine = sa.create_engine(pg.get_connection_url())
        metadata.create_all(engine)                       # TEST-only: materialize the tables
        with engine.begin() as conn:                      # TEST-only roles + grants
            conn.execute(sa.text("CREATE ROLE audit_writer LOGIN PASSWORD 'wpw'"))
            conn.execute(sa.text("GRANT INSERT, SELECT ON audit_record, applicant_profile_snapshot TO audit_writer"))
            conn.execute(sa.text("CREATE ROLE audit_reader LOGIN PASSWORD 'rpw'"))
            conn.execute(sa.text("GRANT SELECT ON audit_record, applicant_profile_snapshot TO audit_reader"))
        engine._au_url = engine.url                       # stash for role engines
        yield engine
        engine.dispose()


def _role_engine(admin_engine, user, password):
    return sa.create_engine(admin_engine.url.set(username=user, password=password))


@pytest.fixture()
def repo(admin_engine):
    # clean slate per test
    with admin_engine.begin() as conn:
        conn.execute(sa.delete(applicant_profile_snapshot))
        conn.execute(sa.delete(audit_record))
    return PostgresAuditRepository(admin_engine)


# --------------------------------------------------------------------------
# TUPLE-1 persisted — full record round-trips (CANON-SER fidelity)
# --------------------------------------------------------------------------
def test_full_record_round_trips(repo):
    original = f.make_record(decision_id="D1")
    with repo.atomic():
        repo.insert(original)
    loaded = repo.get("D1")
    assert loaded is not None
    assert loaded.applicant_profile_snapshot.profile == original.applicant_profile_snapshot.profile
    assert loaded.audit_tuple.rule_results == original.audit_tuple.rule_results
    assert loaded.committed_decision == original.committed_decision
    assert loaded.status is rs.DecisionStatus.ACTIVE


# --------------------------------------------------------------------------
# ATOMIC-1 — multi-row both-or-neither
# --------------------------------------------------------------------------
def test_fault_mid_transaction_rolls_back_both_rows(repo, admin_engine):
    with pytest.raises(Exception):
        with repo.atomic():
            repo.insert(f.make_record(decision_id="D1"))
            repo.insert(f.make_record(decision_id="D1"))   # duplicate PK -> IntegrityError
    with admin_engine.connect() as conn:
        assert conn.execute(sa.select(sa.func.count()).select_from(audit_record)).scalar_one() == 0
        assert conn.execute(sa.select(sa.func.count()).select_from(applicant_profile_snapshot)).scalar_one() == 0


# --------------------------------------------------------------------------
# APPEND-1 — DB-role enforcement (UPDATE/DELETE raise)
# --------------------------------------------------------------------------
def test_writer_role_cannot_update_or_delete(repo, admin_engine):
    with repo.atomic():
        repo.insert(f.make_record(decision_id="D1"))
    writer = _role_engine(admin_engine, "audit_writer", "wpw")
    with writer.connect() as conn:
        with pytest.raises(Exception):
            conn.execute(sa.update(audit_record).values(status="superseded"))
        with pytest.raises(Exception):
            conn.execute(sa.delete(audit_record))
    writer.dispose()


def test_reader_role_is_select_only(repo, admin_engine):
    with repo.atomic():
        repo.insert(f.make_record(decision_id="D1"))
    reader = _role_engine(admin_engine, "audit_reader", "rpw")
    with reader.connect() as conn:
        assert conn.execute(sa.select(sa.func.count()).select_from(audit_record)).scalar_one() == 1
        with pytest.raises(Exception):
            conn.execute(sa.update(audit_record).values(status="superseded"))
        with pytest.raises(Exception):
            conn.execute(sa.delete(audit_record))
    reader.dispose()


# --------------------------------------------------------------------------
# READ-1 / LOG-1 — auditor read surface
# --------------------------------------------------------------------------
def test_browse_and_get_over_real_postgres(repo):
    with repo.atomic():
        repo.insert(f.make_record(decision_id="D1", application_id="APP-1"))
    with repo.atomic():
        repo.insert(f.make_record(decision_id="D2", application_id="APP-1"))
    assert {r.decision_id for r in repo.browse(application_id="APP-1")} == {"D1", "D2"}
    assert repo.get("D1").application_id == "APP-1"
    assert repo.exists_superseding("D1") is False
