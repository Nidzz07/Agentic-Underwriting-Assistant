"""tier-U orchestration-contract test for the deploy migration entrypoint (register #8).

No Docker, no real DB. Monkeypatches the frozen runners + the engine factory so the
ORCHESTRATION contract is asserted in isolation:

* the engine is built from ``get_settings().DATABASE_URL`` (the owner connection);
* U15's sequence is applied BEFORE U24's;
* U24 is applied via ``apply_case_migrations()`` EXACTLY ONCE — never a bare ``MigrationRunner``
  pointed at U24's ``CASE_MIGRATIONS_DIR`` (C-C: that path would bypass the production collision
  guard). This is proved by SPYING ON MigrationRunner's CONSTRUCTOR ARGUMENTS, not merely its
  call count — so the test genuinely fails if someone later hands ``CASE_MIGRATIONS_DIR`` to the
  wrong runner;
* any error propagates (FAIL-LOUD, Q4-a) AND the engine is still disposed via the ``finally``;
* on success ``main`` returns 0, disposes, and logs only filenames/counts — never rendered SQL
  (the grants file carries a substituted secret, SEC-3).

This module lives in ``backend/scripts/`` — outside every ``--cov`` target — so it EXERCISES the
entrypoint's logic without that logic entering the coverage denominator (Q6 / the coverage
subtlety), exactly as the entrypoint itself is coverage-invisible.
"""
from __future__ import annotations

import types

import pytest

from backend.case_lifecycle.migrate import CASE_MIGRATIONS_DIR
from backend.database.migration_runner import MIGRATIONS_DIR as DB_MIGRATIONS_DIR
from backend.scripts import run_migrations as rm

#: Sentinel for "no migrations_dir argument was passed to MigrationRunner" — distinct from any
#: real Path, so the C-C proof can tell "used its own U15 default" from "was handed a dir".
_UNSET = object()

DATABASE_URL = "postgresql://owner:pw@host:5432/appdb"


class _EntrypointError(RuntimeError):
    """A synthetic failure injected to prove fail-loud propagation."""


class _FakeEngine:
    def __init__(self) -> None:
        self.disposed = False
        self.url: str | None = None

    def dispose(self) -> None:
        self.disposed = True


@pytest.fixture()
def spies(monkeypatch):
    """Install happy-path spies for the frozen runners + engine factory.

    Exposes the shared call log, the constructor-arg record, the fake engine, and two helpers to
    make either half raise (for the fail-loud tests)."""
    calls: list = []
    runner_ctor_args: list[dict] = []
    engine = _FakeEngine()

    class _SpyRunner:
        def __init__(self, engine_arg, migrations_dir=_UNSET, env=None) -> None:
            # ⚑ Record the ARGS, not just the fact of construction — this is the C-C proof.
            runner_ctor_args.append(
                {"engine": engine_arg, "migrations_dir": migrations_dir, "env": env}
            )

        def apply_all(self):
            calls.append("u15")
            return ["0001_initial_schema.sql", "0002_grants.sql"]

    def _fake_apply_case(engine_arg):
        calls.append("u24")
        return ["0001_case_lifecycle.sql"]

    def _fake_create_engine(url):
        calls.append(("create_engine", url))
        engine.url = url
        return engine

    monkeypatch.setattr(rm, "MigrationRunner", _SpyRunner)
    monkeypatch.setattr(rm, "apply_case_migrations", _fake_apply_case)
    monkeypatch.setattr(rm.sa, "create_engine", _fake_create_engine)
    monkeypatch.setattr(rm, "get_settings", lambda: types.SimpleNamespace(DATABASE_URL=DATABASE_URL))

    def make_u15_raise(exc: Exception) -> None:
        class _RaisingRunner(_SpyRunner):
            def apply_all(self):
                raise exc

        monkeypatch.setattr(rm, "MigrationRunner", _RaisingRunner)

    def make_u24_raise(exc: Exception) -> None:
        def _raise(engine_arg):
            raise exc

        monkeypatch.setattr(rm, "apply_case_migrations", _raise)

    return types.SimpleNamespace(
        calls=calls,
        runner_ctor_args=runner_ctor_args,
        engine=engine,
        database_url=DATABASE_URL,
        make_u15_raise=make_u15_raise,
        make_u24_raise=make_u24_raise,
    )


def test_builds_engine_from_settings_database_url(spies):
    rm.main([])
    assert ("create_engine", spies.database_url) in spies.calls


def test_applies_u15_before_u24(spies):
    rm.main([])
    assert spies.calls.index("u15") < spies.calls.index("u24")


def test_u24_is_applied_via_apply_case_migrations_exactly_once(spies):
    rm.main([])
    # apply_case_migrations() is the ONLY sanctioned U24 path (runs the guard first).
    assert spies.calls.count("u24") == 1


def test_u15_runner_is_constructed_with_the_default_dir_never_the_case_dir(spies):
    rm.main([])
    # Exactly one MigrationRunner is constructed (U15's); U24 does NOT go through a bare runner.
    assert len(spies.runner_ctor_args) == 1
    dirs = [c["migrations_dir"] for c in spies.runner_ctor_args]
    # The U15 runner was handed NO migrations_dir → it operates on its own default (U15's dir).
    assert dirs == [_UNSET]
    # ⚑ C-C, structurally: CASE_MIGRATIONS_DIR is never passed to ANY MigrationRunner.
    assert CASE_MIGRATIONS_DIR not in dirs
    # And nothing sneaks U15's own dir in explicitly either (it's the implicit default).
    assert DB_MIGRATIONS_DIR not in dirs


def test_error_in_u15_apply_propagates_and_still_disposes(spies):
    spies.make_u15_raise(_EntrypointError("u15 boom"))
    with pytest.raises(_EntrypointError):
        rm.main([])
    # fail-loud AND cleanup: the finally disposed the engine even as the error propagated.
    assert spies.engine.disposed is True


def test_error_in_u24_apply_propagates_and_still_disposes(spies):
    spies.make_u24_raise(_EntrypointError("u24 boom"))
    with pytest.raises(_EntrypointError):
        rm.main([])
    assert spies.engine.disposed is True


def test_main_returns_zero_disposes_and_logs_no_rendered_sql(spies, capsys):
    rc = rm.main([])
    assert rc == 0
    assert spies.engine.disposed is True
    out = capsys.readouterr().out
    # The summary names filenames/counts …
    assert "0001_initial_schema.sql" in out
    assert "0001_case_lifecycle.sql" in out
    # … and NEVER the rendered SQL (SEC-3 — the grants file substitutes a secret).
    assert "CREATE ROLE" not in out
    assert "CREATE TABLE" not in out
    assert "PASSWORD" not in out
