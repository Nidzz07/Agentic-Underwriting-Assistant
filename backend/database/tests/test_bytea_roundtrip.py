"""Integration test — NFR-DB-BYTEA-1 opaque byte-fidelity round-trip (Step 8).

Writes adversarial byte sequences (bytes a JSONB column would re-order/re-encode) plus
real shared-CANON-SER output into the BYTEA columns, reads back byte-identical, and
confirms a recomputed content_hash matches — proving the DB performs NO normalization
(BR-DB-10; REPLAY-1 / DET-2). Uses the shared ``backend.common.canon_ser`` (not
``audit_store``) for the realistic case, keeping this test independent of the consumer.
"""
from __future__ import annotations

import hashlib
from decimal import Decimal

import pytest
import sqlalchemy as sa

from backend.common.canon_ser import canon_ser, content_hash
from backend.database.tests import factories as f

pytestmark = pytest.mark.integration


def test_adversarial_bytes_roundtrip_byte_identical(migrated_engine, reflected_tables, clean_tables):
    audit = reflected_tables.tables["audit_record"]
    snap = reflected_tables.tables["applicant_profile_snapshot"]

    for i, probe in enumerate(f.ADVERSARIAL_BYTES):
        did = f"B{i}"
        with migrated_engine.begin() as conn:
            conn.execute(audit.insert().values(**f.sample_audit_row(decision_id=did, rule_results=probe)))
            conn.execute(snap.insert().values(**f.sample_snapshot_row(decision_id=did, profile_canonical=probe)))
        with migrated_engine.connect() as conn:
            rr = conn.execute(sa.select(audit.c.rule_results).where(audit.c.decision_id == did)).scalar_one()
            pc = conn.execute(sa.select(snap.c.profile_canonical).where(snap.c.decision_id == did)).scalar_one()
        assert bytes(rr) == probe, f"rule_results not byte-identical for probe {i}"
        assert bytes(pc) == probe, f"profile_canonical not byte-identical for probe {i}"


def test_real_canon_ser_roundtrip_and_content_hash(migrated_engine, reflected_tables, clean_tables):
    audit = reflected_tables.tables["audit_record"]
    snap = reflected_tables.tables["applicant_profile_snapshot"]

    # Real CANON-SER output — Decimal-as-string, sorted keys (P1/P2); bytes a JSONB
    # column would re-order. content_hash == sha256 over exactly these bytes.
    payload = {"rule_id": "DTI-1", "actual": Decimal("0.30"), "threshold": Decimal("0.40"),
               "status": "pass", "nested": {"b": 2, "a": 1}}
    blob = canon_ser(payload)
    expected_hash = content_hash(payload)

    with migrated_engine.begin() as conn:
        conn.execute(audit.insert().values(**f.sample_audit_row(decision_id="BR", rule_results=blob)))
        conn.execute(snap.insert().values(
            **f.sample_snapshot_row(decision_id="BR", profile_canonical=blob, content_hash=expected_hash)))
    with migrated_engine.connect() as conn:
        got = bytes(conn.execute(
            sa.select(snap.c.profile_canonical).where(snap.c.decision_id == "BR")).scalar_one())

    assert got == blob                                           # byte-identical
    assert hashlib.sha256(got).hexdigest() == expected_hash      # no DB normalization
