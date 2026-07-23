"""Unit tests — C1 Settings / FAILCLOSED-1 + DET-1 + PERF-1 (Step 2).

Hermetic: the `clean_env` fixture clears all six keys; each case sets only the fields
it needs and constructs `Settings(_env_file=None)` **directly** (never via the cached
accessor — there is no cache anyway) so no stale instance leaks across the ~19 cases.
Dummy values are throwaway literals (SEC-3).
"""
from __future__ import annotations

import ast
import pathlib
import time

import pytest
from pydantic import ValidationError

from backend.secrets_config import settings as settings_module
from backend.secrets_config import url_validation as url_module
from backend.secrets_config.settings import Settings, get_settings
from backend.secrets_config.tests.conftest import SETTINGS_ENV_KEYS, VALID_ENV


def _build(monkeypatch, env: dict) -> Settings:
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return Settings(_env_file=None)  # ignore any real .env — hermetic


# --------------------------------------------------------------------------
# FAILCLOSED-1 — success + each field's missing/invalid case, all hermetic
# --------------------------------------------------------------------------
def test_complete_valid_env_constructs(clean_env):
    s = _build(clean_env, VALID_ENV)
    assert s.DATABASE_URL == VALID_ENV["DATABASE_URL"]
    assert s.GEMINI_API_KEY == VALID_ENV["GEMINI_API_KEY"]


@pytest.mark.parametrize("missing", SETTINGS_ENV_KEYS)
def test_missing_field_raises(clean_env, missing):
    env = {k: v for k, v in VALID_ENV.items() if k != missing}
    with pytest.raises(ValidationError):
        _build(clean_env, env)


_INVALID = {
    "DATABASE_URL": ["sqlite:///x.db", "not a url at all"],
    "AUDIT_WRITER_URL": ["sqlite://", "mysql://h/db"],
    "AUDIT_READER_URL": ["", "redis://h:6379"],
    "AUDIT_WRITER_PASSWORD": ["", "   "],
    "AUDIT_READER_PASSWORD": ["", "\t"],
    "GEMINI_API_KEY": ["", "  "],
}


@pytest.mark.parametrize(
    "field,bad", [(f, b) for f, bads in _INVALID.items() for b in bads]
)
def test_invalid_field_raises(clean_env, field, bad):
    env = dict(VALID_ENV)
    env[field] = bad
    with pytest.raises(ValidationError):
        _build(clean_env, env)


def test_get_settings_reads_env(clean_env):
    for key, value in VALID_ENV.items():
        clean_env.setenv(key, value)
    s = get_settings()
    assert s.AUDIT_WRITER_URL == VALID_ENV["AUDIT_WRITER_URL"]


# --------------------------------------------------------------------------
# DET-1 — same env -> identical result; module imports nothing nondeterministic
# --------------------------------------------------------------------------
def test_same_env_identical_result(clean_env):
    s1 = _build(clean_env, VALID_ENV)
    s2 = Settings(_env_file=None)  # same env still set
    assert s1.model_dump() == s2.model_dump()


def test_modules_import_no_network_or_clock():
    forbidden = {"requests", "httpx", "aiohttp", "socket", "time", "random", "secrets"}
    for module in (settings_module, url_module):
        src = pathlib.Path(module.__file__).read_text(encoding="utf-8")
        imported: set[str] = set()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported.add(node.module.split(".")[0])
        assert not (imported & forbidden), f"{module.__name__} imports {imported & forbidden}"


# --------------------------------------------------------------------------
# PERF-1 — observed, non-gating
# --------------------------------------------------------------------------
def test_construction_latency_observed(clean_env):
    for key, value in VALID_ENV.items():
        clean_env.setenv(key, value)
    start = time.perf_counter()
    for _ in range(100):
        Settings(_env_file=None)
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"\n[PERF-1 observed] 100 Settings constructions: {elapsed_ms:.2f} ms (soft, non-gating)")
    assert elapsed_ms >= 0
