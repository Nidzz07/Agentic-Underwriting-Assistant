"""Hermetic test substrate for `secrets-config` (Step 0).

The `clean_env` fixture makes every Settings test hermetic: it `monkeypatch.delenv`s
all six required keys **first**, so a real shell-set variable can never leak into or
mask a case (pydantic-settings reads `os.environ` regardless of `_env_file`). Tests
then set only the fields a case needs and construct `Settings(_env_file=None)`
directly. `VALID_ENV` holds **throwaway dummy literals** — never real values (SEC-3).
"""
from __future__ import annotations

import pytest

#: The six Phase-1 required env-var names (== the Settings field names).
SETTINGS_ENV_KEYS = [
    "DATABASE_URL",
    "AUDIT_WRITER_URL",
    "AUDIT_READER_URL",
    "AUDIT_WRITER_PASSWORD",
    "AUDIT_READER_PASSWORD",
    "GEMINI_API_KEY",
]

#: A complete, valid env — THROWAWAY dummy literals only (SEC-3: never real secrets).
VALID_ENV = {
    "DATABASE_URL": "postgresql://u:p@localhost:5432/underwriting",
    "AUDIT_WRITER_URL": "postgresql://audit_writer:p@localhost:5432/underwriting",
    "AUDIT_READER_URL": "postgresql://audit_reader:p@localhost:5432/underwriting",
    "AUDIT_WRITER_PASSWORD": "wpw_dummy",
    "AUDIT_READER_PASSWORD": "rpw_dummy",
    "GEMINI_API_KEY": "gemini_dummy_key",
}


@pytest.fixture()
def clean_env(monkeypatch):
    """Clear all six keys so no real shell var leaks/masks a case; return the
    monkeypatch so a test can set only the fields it needs."""
    for key in SETTINGS_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    return monkeypatch
