"""Integration smoke — C5 real PostgresUserRoleRepository (Step 6).

A THIN consumption check: the real adapter reads a seeded `app_user` row via the read
contract. It **asserts nothing about `database`'s schema correctness** (that is
`database`'s FIDELITY-1 / MIGRATE-1) — SCOPE-1. Auto-skipped without Docker; runs in CI.

============================================================================
TEST-ONLY DDL — **NOT** `database`'s production schema. This fixture seeds its own
minimal `app_user` table purely to exercise the adapter's read; it is a test harness,
not `auth-rbac`'s deliverable and not an assertion about `database`'s migrations.
============================================================================
"""
from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("testcontainers.postgres")

import sqlalchemy as sa
from testcontainers.postgres import PostgresContainer

from backend.auth_rbac.pg_repository import PostgresUserRoleRepository

pytestmark = pytest.mark.integration


def _docker_available() -> bool:
    try:
        import docker

        docker.from_env().ping()
        return True
    except Exception:
        return False


@pytest.fixture(scope="module")
def engine():
    if not _docker_available():
        pytest.skip("Docker unavailable — auth-rbac integration smoke runs in CI")
    with PostgresContainer("postgres:16") as pg:
        eng = sa.create_engine(pg.get_connection_url())
        with eng.begin() as conn:  # TEST-only minimal app_user (NOT database's migration)
            conn.exec_driver_sql(
                "CREATE TABLE app_user (user_id VARCHAR PRIMARY KEY, subject VARCHAR, role VARCHAR NOT NULL)"
            )
            conn.exec_driver_sql(
                "INSERT INTO app_user (user_id, subject, role) VALUES ('u1', 's1', 'underwriter')"
            )
        yield eng
        eng.dispose()


def test_reads_seeded_app_user_role(engine):
    repo = PostgresUserRoleRepository(engine)
    assert repo.get_role("u1") == "underwriter"   # raw value read via the contract
    assert repo.get_role("nobody") is None          # no row -> None
