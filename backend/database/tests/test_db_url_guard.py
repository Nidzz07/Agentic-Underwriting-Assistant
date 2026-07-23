"""Unit tests — DbUrlGuard / NFR-DB-DATA5-1 config guard (Step 4).

Pure function, no container. The config-load guard half of DATA-5: a
``postgresql://`` URL is accepted; a ``sqlite://`` URL is rejected; any other
scheme is rejected. (The structural half — BYTEA/TIMESTAMPTZ can't apply on
SQLite — is proven by the migration DDL itself in the integration tier.)
"""
from __future__ import annotations

import pytest

from backend.database.db_url_guard import NonPostgresUrlError, require_postgres_url


@pytest.mark.parametrize("url", [
    "postgresql://user:pw@localhost:5432/underwriting",
    "postgresql+psycopg2://user:pw@localhost/db",
    "postgresql+psycopg://user:pw@host/db",
])
def test_postgres_urls_accepted_and_returned(url):
    assert require_postgres_url(url) == url


@pytest.mark.parametrize("url", [
    "sqlite://",
    "sqlite:///./local.db",
    "sqlite:///:memory:",
])
def test_sqlite_urls_rejected(url):
    with pytest.raises(NonPostgresUrlError):
        require_postgres_url(url)


@pytest.mark.parametrize("url", [
    "mysql://user:pw@localhost/db",
    "oracle://x/y",
    "duckdb:///:memory:",
])
def test_other_schemes_rejected(url):
    with pytest.raises(NonPostgresUrlError):
        require_postgres_url(url)


def test_rejection_message_names_the_backend():
    with pytest.raises(NonPostgresUrlError) as exc:
        require_postgres_url("sqlite:///x.db")
    assert "sqlite" in str(exc.value).lower()


def test_unparseable_url_rejected():
    with pytest.raises(NonPostgresUrlError):
        require_postgres_url("not a url at all")
