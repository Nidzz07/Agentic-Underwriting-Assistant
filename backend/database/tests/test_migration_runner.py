"""Unit tests — the migration runner's PURE substitution logic (Step 3).

No container, no Docker. Covers the ${VAR} placeholder mechanism (the pinned Infra
mechanism, in code): substitute from an explicit env, HARD-ERROR on a missing var
(never a silent empty password), token-free migrations pass through unchanged, and
the committed grants file carries ONLY placeholder tokens (SEC-3 — no value on disk).

The DB-apply half of the runner (apply_all against a real container) is exercised in
the integration tier (test_migration_apply.py); this module proves the substitution
in isolation.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from backend.database.migration_runner import (
    MIGRATIONS_DIR,
    MissingEnvVarError,
    migration_files,
    substitute_placeholders,
)

WRITER_TOKEN = "${AUDIT_WRITER_PASSWORD}"
READER_TOKEN = "${AUDIT_READER_PASSWORD}"


# --------------------------------------------------------------------------
# substitution — happy path
# --------------------------------------------------------------------------
def test_substitutes_tokens_from_env():
    sql = "CREATE ROLE audit_writer LOGIN PASSWORD '${AUDIT_WRITER_PASSWORD}';"
    out = substitute_placeholders(sql, {"AUDIT_WRITER_PASSWORD": "s3cret"})
    assert out == "CREATE ROLE audit_writer LOGIN PASSWORD 's3cret';"
    assert "${" not in out


def test_substitutes_multiple_distinct_tokens():
    sql = f"a '{WRITER_TOKEN}' b '{READER_TOKEN}'"
    out = substitute_placeholders(sql, {
        "AUDIT_WRITER_PASSWORD": "wpw", "AUDIT_READER_PASSWORD": "rpw",
    })
    assert out == "a 'wpw' b 'rpw'"


def test_token_free_sql_passes_through_unchanged():
    sql = "CREATE TABLE audit_record (decision_id VARCHAR NOT NULL);"
    assert substitute_placeholders(sql, {}) == sql


# --------------------------------------------------------------------------
# substitution — hard error on a missing var (never a silent empty password)
# --------------------------------------------------------------------------
def test_missing_env_var_hard_errors():
    with pytest.raises(MissingEnvVarError) as exc:
        substitute_placeholders("PASSWORD '${AUDIT_WRITER_PASSWORD}'", {})
    assert "AUDIT_WRITER_PASSWORD" in str(exc.value)


def test_missing_env_var_is_not_silently_emptied():
    # A partially-populated env must still fail for the absent token — no ''.
    with pytest.raises(MissingEnvVarError):
        substitute_placeholders(
            f"'{WRITER_TOKEN}' '{READER_TOKEN}'",
            {"AUDIT_WRITER_PASSWORD": "wpw"},  # reader missing
        )


# --------------------------------------------------------------------------
# the forward-only sequence + SEC-3 (no value on disk)
# --------------------------------------------------------------------------
def test_migration_files_are_ordered():
    names = [p.name for p in migration_files()]
    assert names == ["0001_initial_schema.sql", "0002_grants.sql", "0003_auth.sql"]
    assert names == sorted(names)  # forward-only, filename order


def test_committed_grants_file_holds_only_placeholder_tokens():
    grants = (MIGRATIONS_DIR / "0002_grants.sql").read_text(encoding="utf-8")
    # SEC-3: the placeholder tokens are present; no literal password value is.
    assert WRITER_TOKEN in grants
    assert READER_TOKEN in grants
    # No stray LOGIN PASSWORD '<literal>' (every PASSWORD literal is a ${...} token).
    for line in grants.splitlines():
        if "PASSWORD" in line:
            assert "${" in line, f"grants line has a non-placeholder password: {line!r}"


def test_initial_schema_migration_has_no_placeholders():
    schema = (MIGRATIONS_DIR / "0001_initial_schema.sql").read_text(encoding="utf-8")
    assert "${" not in schema  # only the grants file carries tokens


def test_migrations_dir_is_the_package_dir():
    assert MIGRATIONS_DIR == Path(__file__).resolve().parent.parent / "migrations"
