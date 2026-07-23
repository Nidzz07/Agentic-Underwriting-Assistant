"""Unit tests — C6 ApiAuthGuard / NFR-AUTH-SSOT-1 (Step 5).

The single-source-of-truth guarantee, as a delegation-via-injected-stub test: swap in a
stub AuthRBAC with a controlled `authorize` output and confirm the guard's `check`
output tracks the stub in BOTH directions (stub-True and stub-False). If the guard held
any independent/inlined role logic, its output would not track the swapped stub.
"""
from __future__ import annotations

from backend.auth_rbac.api_guard import ApiAuthGuard


class _StubAuthz:
    """A stub AuthRBAC — its authorize returns a controlled value and records calls."""

    def __init__(self, result: bool) -> None:
        self._result = result
        self.calls: list[tuple[str, str]] = []

    def authorize(self, user_id: str, rbac_action: str) -> bool:
        self.calls.append((user_id, rbac_action))
        return self._result


_GRID = [("u1", "commit"), ("aud", "view_queue"), ("adm", "manage_users"), ("x", "read_audit")]


def test_guard_tracks_stub_true():
    stub = _StubAuthz(True)
    guard = ApiAuthGuard(stub)
    for uid, action in _GRID:
        assert guard.check(uid, action) is True
    assert stub.calls == _GRID  # the guard delegated every decision to the stub


def test_guard_tracks_stub_false():
    stub = _StubAuthz(False)
    guard = ApiAuthGuard(stub)
    for uid, action in _GRID:
        assert guard.check(uid, action) is False
    assert stub.calls == _GRID


def test_guard_output_equals_authorize_exactly_both_directions():
    for result in (True, False):
        stub = _StubAuthz(result)
        guard = ApiAuthGuard(stub)
        for uid, action in _GRID:
            assert guard.check(uid, action) is result


def test_guard_holds_no_role_or_matrix_data_of_its_own():
    # structural "no inlined role logic": the guard's ONLY state is the injected policy
    guard = ApiAuthGuard(_StubAuthz(True))
    assert set(vars(guard)) == {"_authz"}
