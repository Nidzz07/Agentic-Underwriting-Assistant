"""C4 AppUserWriter — tier-U spy-engine tests (NFR-ADMIN-ROLEGATE-1 a + P3 branches).

The spy stands in for a real ``Engine`` and records ``connect()``/``begin()``. For a
non-canonical role the gate raises FIRST, so **neither** ``connect()`` nor ``begin()``
is ever called (ADMIN-NFRD-Fold-1 reorder-guard); a canonical role proceeds through the
real ``PgWriter`` -> ``engine.begin()``. The spy also drives the result-interpretation
branches (IntegrityError -> "already exists"; rowcount 0 -> "no such user") without Docker.
"""
from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from backend.admin_cli.app_user_writer import AppUserWriter
from backend.admin_cli.exceptions import RoleValidationError, UserWriteError
from backend.admin_cli.pg_writer import PgWriter


class _FakeResult:
    def __init__(self, rowcount: int) -> None:
        self.rowcount = rowcount


class _FakeConn:
    def __init__(self, spy: "SpyEngine") -> None:
        self._spy = spy

    def __enter__(self) -> "_FakeConn":
        return self

    def __exit__(self, *exc) -> bool:
        return False

    def execute(self, statement, params):
        self._spy.executed.append((statement, params))
        if self._spy.raise_integrity:
            raise IntegrityError("stmt", params, Exception("duplicate key"))
        return _FakeResult(self._spy.rowcount)


class SpyEngine:
    """Records the only Engine->DB entry points (connect/begin) in SQLAlchemy 2.0."""

    def __init__(self, rowcount: int = 1, raise_integrity: bool = False) -> None:
        self.connect_calls = 0
        self.begin_calls = 0
        self.executed: list = []
        self.rowcount = rowcount
        self.raise_integrity = raise_integrity

    def begin(self) -> _FakeConn:
        self.begin_calls += 1
        return _FakeConn(self)

    def connect(self) -> _FakeConn:
        self.connect_calls += 1
        return _FakeConn(self)


@pytest.mark.parametrize("bad_role", ["superuser", "Admin", "", "   ", None])
@pytest.mark.parametrize("op", ["create", "set"])
def test_non_canonical_role_rejected_before_any_connection(bad_role, op):
    spy = SpyEngine()
    writer = AppUserWriter(PgWriter(spy))
    with pytest.raises(RoleValidationError):
        if op == "create":
            writer.create_user("u1", "s1", bad_role)
        else:
            writer.set_role("u1", bad_role)
    # the SOLE-gate guarantee: no connection was ever acquired -> no SQL possible
    assert spy.begin_calls == 0
    assert spy.connect_calls == 0


def test_canonical_role_reaches_the_connection():
    spy = SpyEngine(rowcount=1)
    AppUserWriter(PgWriter(spy)).create_user("u1", "s1", "underwriter")
    assert spy.begin_calls == 1  # gate passed -> begin() acquired


def test_create_user_maps_integrity_violation_to_already_exists():
    spy = SpyEngine(raise_integrity=True)
    with pytest.raises(UserWriteError, match="already exists"):
        AppUserWriter(PgWriter(spy)).create_user("u1", "s1", "admin")


def test_set_role_maps_zero_rowcount_to_no_such_user():
    spy = SpyEngine(rowcount=0)
    with pytest.raises(UserWriteError, match="no such user"):
        AppUserWriter(PgWriter(spy)).set_role("ghost", "auditor")


def test_set_role_success_when_a_row_is_updated():
    spy = SpyEngine(rowcount=1)
    AppUserWriter(PgWriter(spy)).set_role("u1", "auditor")  # no raise
    assert spy.begin_calls == 1
