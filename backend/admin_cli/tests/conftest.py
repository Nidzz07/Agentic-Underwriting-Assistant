"""Test substrate for admin-cli's integration tier (ADMIN-NFR-Fold-1/3).

A disposable ``postgres:16`` testcontainers fixture seeding a **test-only minimal**
``app_user`` (``@pytest.mark.integration``, auto-skipped without Docker; runs in CI).

============================================================================
TEST-ONLY DDL — **NOT** ``database``'s production schema/migration. It seeds its own
minimal ``app_user`` purely to exercise admin-cli's write + the fault-injection; it is a
harness (SCOPE-1 / ADMIN-NFR-Fold-3) and **asserts nothing** about ``database``'s schema
correctness (that is ``database``'s FIDELITY-1). ``role`` is an open ``VARCHAR`` with
**no CHECK** (faithful to the real column so the fault-injection is valid); ``subject``
carries ``NOT NULL UNIQUE`` so admin-cli's duplicate-``subject`` teeth (CREATE-1 b) fire.
============================================================================
"""
from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")

import sqlalchemy as sa

_CREATE_TEST_APP_USER = (
    "CREATE TABLE app_user ("
    "user_id VARCHAR PRIMARY KEY, "
    "subject VARCHAR NOT NULL UNIQUE, "
    "role VARCHAR NOT NULL)"  # open VARCHAR, NO CHECK — the fault-injection depends on it
)


def _docker_available() -> bool:
    try:
        import docker

        docker.from_env().ping()
        return True
    except Exception:
        return False


@pytest.fixture
def app_user_engine():
    """A fresh disposable ``postgres:16`` container seeding the test-only ``app_user``."""
    pytest.importorskip("testcontainers.postgres")
    from testcontainers.postgres import PostgresContainer

    if not _docker_available():
        pytest.skip("Docker unavailable — admin-cli integration tests run in CI")
    with PostgresContainer("postgres:16") as pg:
        engine = sa.create_engine(pg.get_connection_url())
        with engine.begin() as conn:
            conn.exec_driver_sql(_CREATE_TEST_APP_USER)
        try:
            yield engine
        finally:
            engine.dispose()
