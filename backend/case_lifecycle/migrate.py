"""C-CASE-7 — U24's own migration sequence + the PRODUCTION collision guard.

**Header comment — DOCUMENTATION ONLY, never enforcement** (each property is scan-enforced in
C-CASE-8): holds no LLM; edits no frozen unit; declares no verdict; **never re-implements the
commit gate, the authz check, or a write to ``audit_record``**.

⚑ **Deliberately a SEPARATE module from ``repository.py`` (Q1-A).** ``repository.py`` is omitted
from coverage; this module must stay **counted**, because the collision guard below is pure logic
that a coverage carve-out must not swallow.

**P-CASE-11 (Q3-A) — the guard runs IN PRODUCTION, on the apply path.** The hazard it defends
against is a **production** hazard: the shared ``applied_migrations`` table is keyed by the **bare
filename**, so a name shared with U15's sequence would be seen as **already applied and SILENTLY
SKIPPED — a no-op, not an error**. A test-only guard would not protect a deployment.

**⚑ U15's filenames are read LIVE** through the frozen, parameterized ``migration_files()`` helper
rather than copied into a constant, so the guard is **always current**: if ``database`` ever gains
``0003_*.sql``, this sees it immediately with **no U24 edit**, and it **cannot drift because there
is no copy**. ``import-to-read != edit`` — ``database`` (U15) is **not** modified.

**MIGSCOPE-1**: U24 applies **only its own** sequence and **authors no CLI entrypoint** — register
item **#8 ``DEPLOY-MIGRATE-DEFERRED`` is NOT adopted and NOT made worse**.
"""
from __future__ import annotations

from pathlib import Path

import sqlalchemy as sa

from backend.database.migration_runner import (
    MIGRATIONS_DIR as DB_MIGRATIONS_DIR,
    MigrationRunner,
    migration_files,
)

#: U24's OWN forward-only sequence — never `database`'s default.
CASE_MIGRATIONS_DIR: Path = Path(__file__).resolve().parent / "migrations"

#: U24's OWN immutability manifest.
CASE_MANIFEST_PATH: Path = CASE_MIGRATIONS_DIR / "checksums.json"


class MigrationNameCollision(RuntimeError):
    """A U24 migration filename collides with `database`'s sequence.

    Raised LOUDLY instead of letting the shared ``applied_migrations`` primary key silently
    skip the colliding file as "already applied" — a no-op, not an error.
    """


def case_migration_names() -> set[str]:
    """U24's migration filenames, via the frozen parameterized helper."""
    return {path.name for path in migration_files(CASE_MIGRATIONS_DIR)}


def database_migration_names() -> set[str]:
    """`database`'s filenames, read LIVE (never copied) so the guard cannot go stale."""
    return {path.name for path in migration_files(DB_MIGRATIONS_DIR)}


def assert_no_collision_with_database() -> None:
    """The production guard. Raises :class:`MigrationNameCollision` on any shared filename."""
    shared = case_migration_names() & database_migration_names()
    if shared:
        raise MigrationNameCollision(
            "U24 migration filename(s) collide with database's sequence and would be "
            f"silently skipped: {sorted(shared)}"
        )


def apply_case_migrations(engine: sa.Engine) -> list[str]:
    """Apply U24's OWN sequence, guard first.

    ⚑ This is the production entry point, and the ONLY sanctioned way to apply U24's
    migrations — including from the tier-I test (CG-CASE-Fold-3), so the guard is exercised
    **on the path PERSIST-1 verifies** rather than bypassed.
    """
    assert_no_collision_with_database()
    return MigrationRunner(engine, migrations_dir=CASE_MIGRATIONS_DIR).apply_all()
