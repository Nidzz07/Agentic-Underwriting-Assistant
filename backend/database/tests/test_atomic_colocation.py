"""Integration test — NFR-DB-ATOMIC-1 / COLOC-1 (Step 8).

The co-location both-or-neither guarantee: a two-row insert (audit_record +
applicant_profile_snapshot) with a fault on a later insert leaves BOTH tables empty
after rollback. The fault is a deterministic duplicate primary key -> IntegrityError
(fold #3; the same proven mechanism audit-store uses). Inserts are driven off the
reflected migration-produced schema (NOT pg_repository).
"""
from __future__ import annotations

import pytest
import sqlalchemy as sa

from backend.database.tests import factories as f

pytestmark = pytest.mark.integration


def test_duplicate_pk_rolls_back_both_rows(migrated_engine, reflected_tables, clean_tables):
    audit = reflected_tables.tables["audit_record"]
    snap = reflected_tables.tables["applicant_profile_snapshot"]

    with pytest.raises(sa.exc.IntegrityError):
        with migrated_engine.begin() as conn:
            conn.execute(audit.insert().values(**f.sample_audit_row(decision_id="A1")))
            conn.execute(snap.insert().values(**f.sample_snapshot_row(decision_id="A1")))
            conn.execute(audit.insert().values(**f.sample_audit_row(decision_id="A1")))  # dup PK

    # both-or-neither: after rollback, BOTH tables are empty
    with migrated_engine.connect() as conn:
        assert conn.execute(sa.select(sa.func.count()).select_from(audit)).scalar_one() == 0
        assert conn.execute(sa.select(sa.func.count()).select_from(snap)).scalar_one() == 0
