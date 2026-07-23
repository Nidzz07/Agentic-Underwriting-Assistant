"""Test substrate for the `database` integration tier (Step 0).

A testcontainers ``postgres:16`` fixture that applies **this unit's production
migration sequence** (not audit-store's interim TEST DDL) to a fresh container, plus
reflection + clean-slate helpers. Integration tests are ``@pytest.mark.integration``
and **auto-skipped** when Docker is unavailable (local dev) — they MUST run in CI so
the DB-role / atomicity / append-only / byte-fidelity halves are exercised (DATA-5,
no SQLite).
"""
from __future__ import annotations

import os

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("testcontainers.postgres")

import sqlalchemy as sa
from testcontainers.postgres import PostgresContainer

from backend.database.migration_runner import MigrationRunner
from backend.database.tests.factories import READER_PASSWORD, WRITER_PASSWORD


def _docker_available() -> bool:
    try:
        import docker  # a testcontainers dependency

        docker.from_env().ping()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def migrated_engine():
    """One ``postgres:16`` container for the session, with the production migration
    sequence applied (schema + grants). Grant passwords come from a throwaway env
    (the placeholder-substitution mechanism, SEC-3)."""
    if not _docker_available():
        pytest.skip("Docker unavailable — database integration tests run in CI")
    with PostgresContainer("postgres:16") as pg:
        engine = sa.create_engine(pg.get_connection_url())
        env = dict(os.environ)
        env["AUDIT_WRITER_PASSWORD"] = WRITER_PASSWORD   # throwaway, fixture-scoped
        env["AUDIT_READER_PASSWORD"] = READER_PASSWORD
        MigrationRunner(engine, env=env).apply_all()
        yield engine
        engine.dispose()


@pytest.fixture(scope="session")
def reflected_tables(migrated_engine):
    """The two audit tables reflected from the live migration-produced schema.

    Inserts are driven off THIS reflection — not off ``pg_repository``'s Table objects
    (that import is reserved for the FIDELITY-1 test), keeping ATOMIC-1/BYTEA-1
    independent of the consuming unit.
    """
    md = sa.MetaData()
    md.reflect(bind=migrated_engine, only=["audit_record", "applicant_profile_snapshot"])
    return md


@pytest.fixture()
def clean_tables(migrated_engine):
    """Empty both audit tables before a test needing a clean slate. Uses the
    owner/admin connection — the OWNER may delete for test setup; the append-only
    guarantee is a ROLE-level property, proven separately in test_grants_roles.py."""
    with migrated_engine.begin() as conn:
        conn.exec_driver_sql("DELETE FROM applicant_profile_snapshot")
        conn.exec_driver_sql("DELETE FROM audit_record")
    return migrated_engine
