"""Tests — C4 SchemaIntrospector.

Two tiers in one module:
- **unit** (always run): the pure ``base_type_token`` normalization.
- **integration** (``@pytest.mark.integration``, needs Docker): the live
  reflection of the migration-produced ``audit_record`` schema into the normalized
  column-spec dict.
"""
from __future__ import annotations

import pytest
import sqlalchemy as sa

from backend.database.schema_introspector import (
    UnmappedTypeError,
    base_type_token,
    normalized_table_spec,
)


# --------------------------------------------------------------------------
# unit — base-type token normalization (length/precision ignored)
# --------------------------------------------------------------------------
def test_token_for_string_variants():
    assert base_type_token(sa.String()) == "string"
    assert base_type_token(sa.String(50)) == "string"       # length ignored
    assert base_type_token(sa.VARCHAR(255)) == "string"


def test_token_for_bytea():
    assert base_type_token(sa.LargeBinary()) == "bytea"


def test_token_for_timestamptz():
    assert base_type_token(sa.DateTime(timezone=True)) == "timestamptz"
    assert base_type_token(sa.TIMESTAMP(timezone=True)) == "timestamptz"


def test_unmapped_type_raises():
    with pytest.raises(UnmappedTypeError):
        base_type_token(sa.Integer())


# --------------------------------------------------------------------------
# integration — reflect the live migration-produced audit_record
# --------------------------------------------------------------------------
@pytest.mark.integration
def test_reflects_audit_record_shape(migrated_engine):
    spec = normalized_table_spec(migrated_engine, "audit_record")
    # a representative slice of the normalized dict (full parity is FIDELITY-1's job)
    assert spec["decision_id"] == {
        "type": "string", "nullable": False, "pk": True, "fk_target": None, "indexed": False,
    }
    assert spec["application_id"]["indexed"] is True          # explicit CREATE INDEX
    assert spec["rule_results"]["type"] == "bytea"            # opaque CANON-SER
    assert spec["timestamp"]["type"] == "timestamptz"
    assert spec["reason"]["nullable"] is True                 # WHY nullable
    assert spec["supersedes_decision_id"]["nullable"] is True


@pytest.mark.integration
def test_reflects_snapshot_fk_target(migrated_engine):
    spec = normalized_table_spec(migrated_engine, "applicant_profile_snapshot")
    assert spec["decision_id"]["pk"] is True
    assert spec["decision_id"]["fk_target"] == "audit_record.decision_id"
