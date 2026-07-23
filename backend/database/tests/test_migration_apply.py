"""Integration tests — apply-from-empty, co-location, scope, perf (Steps 1, 8, 9).

Targets: NFR-DB-MIGRATE-1, NFR-DB-COLOC-1, NFR-DB-SCOPE-1, NFR-DB-PERF-1.

The ``migrated_engine`` fixture already applied the production migration sequence
from empty. Exact column-for-column parity of the two audit tables is FIDELITY-1's
job (test_fidelity.py — the ONE file that imports pg_repository read-only); here we
use **targeted presence/absence assertions** (never a closed-world "only exactly
these tables exist" check — the ``applied_migrations`` tool table is legitimately
present too).
"""
from __future__ import annotations

import time

import pytest
import sqlalchemy as sa

from backend.database.migration_runner import MigrationRunner, TRACKING_TABLE
from backend.database.schema_introspector import normalized_table_spec, table_names
from backend.database.tests import factories as f

pytestmark = pytest.mark.integration

AUDIT_RECORD_COLUMNS = {
    "decision_id", "application_id", "recommendation_id", "rulebook_version",
    "rule_results", "timestamp", "model_version", "memo_hash", "engine_version",
    "underwriter_id", "action", "reason", "status", "supersedes_decision_id",
}
SNAPSHOT_COLUMNS = {"decision_id", "application_id", "profile_canonical", "content_hash"}
APP_USER_COLUMNS = {"user_id", "subject", "role"}


# --------------------------------------------------------------------------
# MIGRATE-1 — apply-from-empty produced the expected tables; forward-only
# --------------------------------------------------------------------------
def test_apply_from_empty_created_the_three_tables(migrated_engine):
    present = table_names(migrated_engine)
    assert {"audit_record", "applicant_profile_snapshot", "app_user"} <= present


def test_audit_tables_have_their_expected_columns(migrated_engine):
    assert set(normalized_table_spec(migrated_engine, "audit_record")) == AUDIT_RECORD_COLUMNS
    assert set(normalized_table_spec(migrated_engine, "applicant_profile_snapshot")) == SNAPSHOT_COLUMNS
    assert set(normalized_table_spec(migrated_engine, "app_user")) == APP_USER_COLUMNS


def test_migration_sequence_is_forward_only_and_idempotent(migrated_engine):
    # Re-applying the full sequence applies nothing new (already recorded) — a fresh
    # apply is the source of truth; no down-migration is relied upon.
    env = {"AUDIT_WRITER_PASSWORD": f.WRITER_PASSWORD, "AUDIT_READER_PASSWORD": f.READER_PASSWORD}
    newly = MigrationRunner(migrated_engine, env=env).apply_all()
    assert newly == []
    with migrated_engine.connect() as conn:
        applied = {r[0] for r in conn.execute(sa.text(f"SELECT filename FROM {TRACKING_TABLE}"))}
    assert applied == {"0001_initial_schema.sql", "0002_grants.sql"}


# --------------------------------------------------------------------------
# COLOC-1 — both audit tables in one database + one schema, one connection
# --------------------------------------------------------------------------
def test_both_audit_tables_in_one_schema(migrated_engine):
    insp = sa.inspect(migrated_engine)
    public_tables = set(insp.get_table_names(schema="public"))
    # reachable together on one connection in one schema namespace (ATOMIC-1 basis)
    assert {"audit_record", "applicant_profile_snapshot"} <= public_tables
    with migrated_engine.connect() as conn:
        for t in ("audit_record", "applicant_profile_snapshot"):
            conn.execute(sa.select(sa.func.count()).select_from(sa.text(t)))


# --------------------------------------------------------------------------
# SCOPE-1 — app_user role is open (novel value inserts); rulebook table absent
# --------------------------------------------------------------------------
def test_app_user_role_is_open_novel_value_inserts(migrated_engine):
    # The NEGATIVE property: a novel role value succeeds -> role carries no closing CHECK.
    with migrated_engine.begin() as conn:
        conn.execute(
            sa.text("INSERT INTO app_user (user_id, subject, role) VALUES (:u, :s, :r)"),
            {"u": "U-admin-1", "s": "subject-admin-1", "r": "admin"},
        )
    with migrated_engine.connect() as conn:
        role = conn.execute(
            sa.text("SELECT role FROM app_user WHERE user_id = :u"), {"u": "U-admin-1"}
        ).scalar_one()
    assert role == "admin"


def test_rulebook_registry_table_is_absent(migrated_engine):
    # Targeted absence (NOT a closed-world check): no rulebook-registry table exists.
    present = table_names(migrated_engine)
    assert not any("rulebook" in name for name in present)


# --------------------------------------------------------------------------
# PERF-1 — observed, non-gating (never fails the build)
# --------------------------------------------------------------------------
def test_insert_latency_observed(migrated_engine, reflected_tables, clean_tables):
    audit = reflected_tables.tables["audit_record"]
    start = time.perf_counter()
    with migrated_engine.begin() as conn:
        conn.execute(audit.insert().values(**f.sample_audit_row(decision_id="PERF-1")))
        conn.execute(sa.select(sa.func.count()).select_from(audit))
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"\n[PERF-1 observed] audit_record insert+count latency: {elapsed_ms:.1f} ms (soft budget, non-gating)")
    assert elapsed_ms >= 0  # observed only — never gates the build
