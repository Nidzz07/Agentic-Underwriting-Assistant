"""DEPLOY-TIME migration entrypoint — register #8 ``DEPLOY-MIGRATE-DEFERRED``.

Applies BOTH forward-only migration sequences — ``database`` (U15) then ``case_lifecycle`` (U24) —
to the database named by ``DATABASE_URL``, in order, BEFORE the app serves traffic. This is the
runnable CLI entrypoint ``render.yaml``'s ``preDeployCommand`` invokes.

⚑ **A CROSS-UNIT ORCHESTRATOR, deliberately in ``backend/scripts/`` (register #8 / Q1-B).** It must
drive BOTH U15's ``MigrationRunner`` AND U24's ``apply_case_migrations`` — homing it inside
``backend/database/`` would make a frozen unit's package import a later one. Built from
``get_settings()`` directly (no ``dependencies.py`` FastAPI ``Depends`` graph) and route-free — the
same out-of-band shape as ``seed_demo_cases.py`` / ``reconcile_committing_cases.py``.

⚑ **U24 is applied ONLY through ``apply_case_migrations()`` (C-C)** — the sole sanctioned path, which
runs the PRODUCTION collision guard (``assert_no_collision_with_database``) FIRST. A bare
``MigrationRunner`` pointed at U24's ``CASE_MIGRATIONS_DIR`` would bypass P-CASE-11 and let a shared
filename be silently skipped. U15 is applied through a plain ``MigrationRunner(engine)`` against its
own default sequence.

⚑ **IDEMPOTENT by construction.** Each runner records applied files in ``applied_migrations`` (keyed
by bare filename) and skips them on re-run, so a redeploy applies nothing new — this entrypoint adds
NO re-runnability logic of its own; it inherits the frozen runners' behaviour.

⚑ **FAIL-LOUD (Q4-a).** Any error — a missing grant-password env var (``MissingEnvVarError``), a real
SQL failure, a filename collision — propagates to a non-zero exit so Render's release step FAILS
VISIBLY before traffic is served. Nothing is swallowed; the ``finally`` disposes the engine but never
suppresses. **The rendered SQL is NEVER logged** (the grants file substitutes a secret — SEC-3); only
filenames/counts are printed.

⚑ **This file frozen-CALLS, never frozen-EDITS.** It constructs and invokes ``MigrationRunner`` and
``apply_case_migrations`` exactly as the seed script already does; it touches no ``.sql`` file and no
frozen machinery. It lives outside every ``--cov`` target, so it is coverage-invisible — its logic is
proven by the tier-U orchestration test + the tier-I integration test, not by the coverage gate.

Run (deploy / out of band)::

    python -m backend.scripts.run_migrations
"""
from __future__ import annotations

import argparse

import sqlalchemy as sa

from backend.case_lifecycle.migrate import apply_case_migrations
from backend.database.migration_runner import MigrationRunner
from backend.secrets_config import get_settings


def apply_all_migrations(engine: sa.Engine) -> tuple[list[str], list[str]]:
    """Apply ``database`` (U15) then ``case_lifecycle`` (U24, guard-first).

    Returns ``(u15_newly_applied, u24_newly_applied)`` — the filenames applied THIS call (empty on a
    re-run, since both runners skip already-applied files). U24 goes through
    :func:`apply_case_migrations` — the ONLY sanctioned path — never a bare ``MigrationRunner`` on
    U24's dir (C-C). Fail-loud: any error propagates.
    """
    applied_db = MigrationRunner(engine).apply_all()   # U15: plain runner, its own default dir
    applied_case = apply_case_migrations(engine)        # U24: collision-guard first, its own dir
    return applied_db, applied_case


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args(argv)
    engine = sa.create_engine(get_settings().DATABASE_URL)   # owner connection (register #20-ratified)
    try:
        applied_db, applied_case = apply_all_migrations(engine)
    finally:
        engine.dispose()
    # NEVER log rendered SQL (SEC-3) — only filenames/counts.
    print(f"migrations applied: database={applied_db} case_lifecycle={applied_case}")
    return 0


if __name__ == "__main__":  # pragma: no cover - deploy-time entrypoint
    raise SystemExit(main())
