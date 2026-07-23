"""tier-I integration test for the deploy migration entrypoint (register #8).

Proves the entrypoint's ``apply_all_migrations`` materializes BOTH sequences on a REAL Postgres —
the thing tier-U (which monkeypatches the runners) cannot show — and that a second run applies
nothing new (end-to-end idempotency).

⚑ **Uses ``database``'s / ``case_lifecycle``'s KNOWN-GOOD clean-skip guard VERBATIM**:
``_docker_available()`` pings the daemon INSIDE the fixture body, BEFORE any container is
constructed. That is precisely why this SKIPS CLEANLY where ``audit_store``'s importorskip-only
pattern reaches container construction and ERRORS (the 5 pre-existing errors). **This test adds ZERO
errors** — Docker-absence is a skip, never a sixth error.

⚑ Grant passwords for U15's ``0002_grants.sql`` (``${AUDIT_WRITER_PASSWORD}`` /
``${AUDIT_READER_PASSWORD}``) come from a throwaway, fixture-scoped env — the placeholder-substitution
mechanism (SEC-3), exactly as ``database``'s own conftest injects them.

⚑ This is the FIRST test in the build to apply BOTH U15's and U24's sequences to ONE container via
the production deploy entrypoint — the combination ``render.yaml``'s ``preDeployCommand`` will run.
"""
from __future__ import annotations

import os

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("testcontainers.postgres")

import sqlalchemy as sa
from testcontainers.postgres import PostgresContainer

from backend.database.tests.factories import READER_PASSWORD, WRITER_PASSWORD
from backend.scripts.run_migrations import apply_all_migrations

pytestmark = pytest.mark.integration


def _docker_available() -> bool:
    try:
        import docker  # a testcontainers dependency

        docker.from_env().ping()
        return True
    except Exception:
        return False


@pytest.fixture(scope="module")
def migrated(fresh_engine):
    """The entrypoint's ``apply_all_migrations`` run ONCE against the empty container.

    Yields ``(engine, applied_db, applied_case)`` so every test depends only on this fixture — not on
    another test's side effects. The second-run idempotency test does its own extra call."""
    applied_db, applied_case = apply_all_migrations(fresh_engine)
    return fresh_engine, applied_db, applied_case


@pytest.fixture(scope="module")
def fresh_engine():
    """One ``postgres:16`` container, EMPTY — no migrations pre-applied (the entrypoint applies them).

    Ping-guard FIRST (clean skip when Docker is absent), then construct. Grant passwords injected
    into the process env for U15's grants file (throwaway, SEC-3)."""
    if not _docker_available():
        pytest.skip("Docker unavailable — run-migrations integration test runs in CI")
    prior = {k: os.environ.get(k) for k in ("AUDIT_WRITER_PASSWORD", "AUDIT_READER_PASSWORD")}
    os.environ["AUDIT_WRITER_PASSWORD"] = WRITER_PASSWORD   # throwaway, fixture-scoped
    os.environ["AUDIT_READER_PASSWORD"] = READER_PASSWORD
    try:
        with PostgresContainer("postgres:16") as pg:
            engine = sa.create_engine(pg.get_connection_url())
            yield engine
            engine.dispose()
    finally:
        for k, v in prior.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_applies_both_sequences_to_a_fresh_container(migrated):
    engine, applied_db, applied_case = migrated
    # Both sequences report the files they applied, in one invocation.
    assert applied_db == ["0001_initial_schema.sql", "0002_grants.sql"]
    assert applied_case == ["0001_case_lifecycle.sql"]
    tables = set(sa.inspect(engine).get_table_names())
    # U15's schema AND U24's pending store, both present on the one database.
    assert {
        "audit_record",
        "applicant_profile_snapshot",
        "app_user",
        "pending_application",
        "pending_recommendation",
    } <= tables


def test_applied_migrations_records_both_sequences(migrated):
    engine, _, _ = migrated
    # The shared tracking table names every applied file across BOTH sequences.
    with engine.connect() as conn:
        applied = {r[0] for r in conn.execute(sa.text("SELECT filename FROM applied_migrations"))}
    assert applied == {
        "0001_initial_schema.sql",
        "0002_grants.sql",
        "0001_case_lifecycle.sql",
    }


def test_second_run_applies_nothing_new(migrated):
    engine, _, _ = migrated
    # End-to-end idempotency: a redeploy re-runs the entrypoint and applies nothing.
    applied_db, applied_case = apply_all_migrations(engine)
    assert applied_db == []
    assert applied_case == []
