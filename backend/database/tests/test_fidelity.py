"""Tests — C5 FidelityComparator / NFR-DB-FIDELITY-1.

Reference-not-own (in reverse): **this TEST** imports ``pg_repository``'s Table
metadata read-only and hands it to the comparator. The comparator's PRODUCTION code
never imports ``audit_store`` (no production cross-import, no circular dependency).

Two tiers:
- **unit** (always run): ``spec_from_table`` normalization of the consumer's metadata
  (no container — reading ``sa.Table`` objects needs no DB).
- **integration** (Docker): the live migration-produced schema matches ``pg_repository``
  column-for-column; a simulated drift fails.
"""
from __future__ import annotations

import pytest
import sqlalchemy as sa

# Read-only import of the CONSUMER's declaration — TEST-ONLY (never in production code).
from backend.audit_store.pg_repository import (
    applicant_profile_snapshot as pg_snapshot,
    audit_record as pg_audit_record,
)
from backend.database.fidelity_comparator import (
    FidelityError,
    assert_fidelity,
    spec_from_table,
)


def _consumer_tables():
    return {
        "audit_record": pg_audit_record,
        "applicant_profile_snapshot": pg_snapshot,
    }


# --------------------------------------------------------------------------
# unit — normalize the consumer's own Table metadata (no container)
# --------------------------------------------------------------------------
def test_spec_from_pg_audit_record():
    spec = spec_from_table(pg_audit_record)
    assert spec["decision_id"] == {
        "type": "string", "nullable": False, "pk": True, "fk_target": None, "indexed": False,
    }
    assert spec["application_id"]["indexed"] is True
    assert spec["rule_results"]["type"] == "bytea"
    assert spec["timestamp"]["type"] == "timestamptz"
    assert spec["reason"]["nullable"] is True


def test_spec_from_pg_snapshot_fk():
    spec = spec_from_table(pg_snapshot)
    assert spec["decision_id"]["fk_target"] == "audit_record.decision_id"
    assert spec["profile_canonical"]["type"] == "bytea"


# --------------------------------------------------------------------------
# integration — the migration-produced schema matches the consumer column-for-column
# --------------------------------------------------------------------------
@pytest.mark.integration
def test_migration_matches_pg_repository(migrated_engine):
    # No raise == the 18/18 column-for-column consistency holds.
    assert_fidelity(migrated_engine, _consumer_tables())


@pytest.mark.integration
def test_consumer_expecting_missing_column_fails(migrated_engine):
    drifted = sa.Table(
        "audit_record", sa.MetaData(),
        sa.Column("decision_id", sa.String, primary_key=True),
        sa.Column("a_column_the_schema_lacks", sa.String, nullable=False),
    )
    consumer = _consumer_tables()
    consumer["audit_record"] = drifted
    with pytest.raises(FidelityError):
        assert_fidelity(migrated_engine, consumer)


@pytest.mark.integration
def test_consumer_type_drift_fails(migrated_engine):
    # rule_results declared as string instead of bytea -> a type drift the guard catches.
    drifted = sa.Table(
        "audit_record", sa.MetaData(),
        *[sa.Column(c.name, sa.String, primary_key=c.primary_key) for c in pg_audit_record.columns],
    )
    consumer = _consumer_tables()
    consumer["audit_record"] = drifted
    with pytest.raises(FidelityError):
        assert_fidelity(migrated_engine, consumer)
