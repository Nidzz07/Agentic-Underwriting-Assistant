"""Integration tests — NFR-DB-APPEND-1 role write matrix (Step 2).

Applies the production grants (via the migration sequence in the fixture), connects as
each real DB role, and asserts the write matrix (BR-DB-4/5, SEC-4/SEC-5):
  audit_writer -> INSERT + SELECT ok; UPDATE / DELETE raise.
  audit_reader -> SELECT ok; INSERT / UPDATE / DELETE raise.
Each raising operation runs on its own connection (a prior error aborts a txn).
"""
from __future__ import annotations

import pytest
import sqlalchemy as sa

from backend.database.tests import factories as f

pytestmark = pytest.mark.integration


# --------------------------------------------------------------------------
# audit_writer — INSERT + SELECT ok; UPDATE / DELETE raise
# --------------------------------------------------------------------------
def test_writer_can_insert_and_select(migrated_engine, reflected_tables, clean_tables):
    audit = reflected_tables.tables["audit_record"]
    writer = f.role_engine(migrated_engine, "audit_writer", f.WRITER_PASSWORD)
    try:
        with writer.begin() as conn:
            conn.execute(audit.insert().values(**f.sample_audit_row(decision_id="W1")))
        with writer.connect() as conn:
            assert conn.execute(sa.select(sa.func.count()).select_from(audit)).scalar_one() == 1
    finally:
        writer.dispose()


def test_writer_cannot_update(migrated_engine, reflected_tables, clean_tables):
    audit = reflected_tables.tables["audit_record"]
    with migrated_engine.begin() as conn:  # owner seeds a row
        conn.execute(audit.insert().values(**f.sample_audit_row(decision_id="W2")))
    writer = f.role_engine(migrated_engine, "audit_writer", f.WRITER_PASSWORD)
    try:
        with writer.connect() as conn:
            with pytest.raises(Exception):
                conn.execute(sa.update(audit).values(status="superseded"))
    finally:
        writer.dispose()


def test_writer_cannot_delete(migrated_engine, reflected_tables, clean_tables):
    audit = reflected_tables.tables["audit_record"]
    with migrated_engine.begin() as conn:
        conn.execute(audit.insert().values(**f.sample_audit_row(decision_id="W3")))
    writer = f.role_engine(migrated_engine, "audit_writer", f.WRITER_PASSWORD)
    try:
        with writer.connect() as conn:
            with pytest.raises(Exception):
                conn.execute(sa.delete(audit))
    finally:
        writer.dispose()


# --------------------------------------------------------------------------
# audit_reader — SELECT ok; INSERT / UPDATE / DELETE raise
# --------------------------------------------------------------------------
def test_reader_can_select(migrated_engine, reflected_tables, clean_tables):
    audit = reflected_tables.tables["audit_record"]
    with migrated_engine.begin() as conn:
        conn.execute(audit.insert().values(**f.sample_audit_row(decision_id="R1")))
    reader = f.role_engine(migrated_engine, "audit_reader", f.READER_PASSWORD)
    try:
        with reader.connect() as conn:
            assert conn.execute(sa.select(sa.func.count()).select_from(audit)).scalar_one() == 1
    finally:
        reader.dispose()


def test_reader_cannot_insert(migrated_engine, reflected_tables, clean_tables):
    audit = reflected_tables.tables["audit_record"]
    reader = f.role_engine(migrated_engine, "audit_reader", f.READER_PASSWORD)
    try:
        with reader.connect() as conn:
            with pytest.raises(Exception):
                conn.execute(audit.insert().values(**f.sample_audit_row(decision_id="R2")))
    finally:
        reader.dispose()


def test_reader_cannot_update_or_delete(migrated_engine, reflected_tables, clean_tables):
    audit = reflected_tables.tables["audit_record"]
    with migrated_engine.begin() as conn:
        conn.execute(audit.insert().values(**f.sample_audit_row(decision_id="R3")))
    reader = f.role_engine(migrated_engine, "audit_reader", f.READER_PASSWORD)
    try:
        with reader.connect() as conn:
            with pytest.raises(Exception):
                conn.execute(sa.update(audit).values(status="superseded"))
        with reader.connect() as conn:
            with pytest.raises(Exception):
                conn.execute(sa.delete(audit))
    finally:
        reader.dispose()
