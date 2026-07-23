"""C1 MigrationSequence runner — forward-only apply + placeholder substitution.

The minimal raw-SQL versioned runner (Q1 = A; no new dependency). Ordered
``NNNN_*.sql`` files under ``migrations/`` are applied in filename order; a tiny
``applied_migrations`` tracking table records what ran (idempotent, forward-only).
The tracking table is a TOOL ARTIFACT of the runner — it is expected to be present
alongside the schema tables, so schema-scope assertions (MIGRATE-1 / SCOPE-1) use
targeted presence/absence checks, never a closed-world "only these tables exist".

Placeholder substitution (the pinned Infra mechanism, in code): the committed grants
file carries ``${AUDIT_WRITER_PASSWORD}`` / ``${AUDIT_READER_PASSWORD}`` tokens ONLY;
this runner reads ``os.environ`` and substitutes at execution time — a **missing env
var is a hard error, never a silent empty password** (SEC-3). Token-free migrations
pass through unchanged (only the grants file carries tokens). The **rendered SQL is
NEVER logged** — only the placeholder-bearing form is ever on disk or in logs.

DATA-5 / no LLM. This module executes against a real Postgres only (dev / CI
testcontainers / Render); it is exercised in the integration tier.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Mapping, Optional

import sqlalchemy as sa

#: The forward-only sequence lives beside this module.
MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"

#: ``${NAME}`` placeholder tokens (upper-snake env-var names).
_PLACEHOLDER_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")

#: Tool-tracking table — records which migration files have been applied.
TRACKING_TABLE = "applied_migrations"


class MissingEnvVarError(RuntimeError):
    """A ``${VAR}`` placeholder in a migration has no corresponding env value.

    Raised instead of substituting an empty string — a silent empty password would
    be a SEC-3 defect, so a missing var fails loudly.
    """


def substitute_placeholders(sql: str, env: Mapping[str, str]) -> str:
    """Replace every ``${VAR}`` token in ``sql`` with ``env[VAR]``.

    Hard-errors (``MissingEnvVarError``) on any absent variable — never a silent
    empty value. Token-free SQL is returned unchanged. **The caller must never log
    the returned string** — for the grants file it contains a rendered secret.
    """
    def _repl(match: "re.Match[str]") -> str:
        name = match.group(1)
        try:
            return env[name]
        except KeyError:
            raise MissingEnvVarError(
                f"migration requires environment variable {name!r} but it is not set"
            ) from None

    return _PLACEHOLDER_RE.sub(_repl, sql)


def migration_files(migrations_dir: Path = MIGRATIONS_DIR) -> list[Path]:
    """The forward-only sequence: ``NNNN_*.sql`` sorted by filename (never edited
    in place — a change is a new higher-numbered file, BR-DB-4)."""
    return sorted(migrations_dir.glob("[0-9][0-9][0-9][0-9]_*.sql"))


class MigrationRunner:
    """Apply the forward-only migration sequence to a Postgres engine.

    Idempotent: already-applied files (recorded in ``applied_migrations``) are
    skipped. Each file is applied + recorded inside one transaction, so a partial
    failure rolls back that step.
    """

    def __init__(
        self,
        engine: sa.Engine,
        migrations_dir: Path = MIGRATIONS_DIR,
        env: Optional[Mapping[str, str]] = None,
    ) -> None:
        self._engine = engine
        self._migrations_dir = migrations_dir
        #: default to the real process env; tests inject a throwaway mapping.
        self._env = env if env is not None else os.environ

    def apply_all(self) -> list[str]:
        """Apply every not-yet-applied migration in order. Returns the filenames
        newly applied this call."""
        self._ensure_tracking_table()
        already = self._applied_set()
        newly: list[str] = []
        for path in migration_files(self._migrations_dir):
            if path.name in already:
                continue
            rendered = substitute_placeholders(
                path.read_text(encoding="utf-8"), self._env
            )  # NOTE: never log `rendered` (SEC-3 — may contain a secret).
            with self._engine.begin() as conn:
                conn.exec_driver_sql(rendered)
                conn.execute(
                    sa.text(f"INSERT INTO {TRACKING_TABLE} (filename) VALUES (:f)"),
                    {"f": path.name},
                )
            newly.append(path.name)
        return newly

    def _ensure_tracking_table(self) -> None:
        with self._engine.begin() as conn:
            conn.exec_driver_sql(
                f"CREATE TABLE IF NOT EXISTS {TRACKING_TABLE} ("
                "filename VARCHAR PRIMARY KEY, "
                "applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"
            )

    def _applied_set(self) -> set[str]:
        with self._engine.connect() as conn:
            rows = conn.execute(sa.text(f"SELECT filename FROM {TRACKING_TABLE}"))
            return {row[0] for row in rows}
