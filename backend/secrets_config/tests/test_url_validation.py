"""Unit tests — C2 is_postgres_url / NFR-SEC-SCHEME-1 (Step 1).

The 3 URL fields accept `postgresql://` (+ driver variants) and reject sqlite / other
scheme / malformed — via secrets-config's OWN validator (no `DbUrlGuard` import).
"""
from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from backend.secrets_config.url_validation import is_postgres_url


@pytest.mark.parametrize("url", [
    "postgresql://u:p@localhost:5432/db",
    "postgresql+psycopg2://u:p@host/db",
    "postgresql+psycopg://u@host/db",
    "postgresql+asyncpg://u:p@host:5432/db",
])
def test_postgres_accepted(url):
    assert is_postgres_url(url) is True


@pytest.mark.parametrize("url", ["sqlite://", "sqlite:///./local.db", "sqlite:///:memory:"])
def test_sqlite_rejected(url):
    assert is_postgres_url(url) is False


@pytest.mark.parametrize("url", [
    "mysql://u@h/db", "oracle://x/y", "redis://h:6379", "mongodb://h/db",
])
def test_other_scheme_rejected(url):
    assert is_postgres_url(url) is False


@pytest.mark.parametrize("url", ["", "   ", "not a url at all", "://missing-scheme", "\t\n"])
def test_malformed_rejected(url):
    assert is_postgres_url(url) is False


@given(st.text(max_size=40).filter(lambda s: not s.strip().lower().startswith("postgresql")))
def test_fuzz_non_postgresql_always_rejected(value):
    # any string that is not a postgresql URL -> False (never raises)
    assert is_postgres_url(value) is False
