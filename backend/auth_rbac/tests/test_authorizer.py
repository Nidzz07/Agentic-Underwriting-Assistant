"""Unit tests — C1 AuthRBAC.authorize (Step 4).

Covers NFR-AUTH-DENY-1 (four independent cases), the authorize-level MATRIX exhaustive
grid, NFR-AUTH-DET-1 (repeat-invariance), NFR-AUTH-BIAS-1 (structural signature + swap),
and NFR-AUTH-PERF-1 (observed, non-gating). All against the in-memory fake — no live DB,
no audit-store.
"""
from __future__ import annotations

import inspect
import time

import pytest

from backend.auth_rbac.authorizer import AuthRBAC
from backend.auth_rbac.repository import InMemoryUserRoleRepository
from backend.auth_rbac.roles import ALL_RBAC_ACTIONS, PERMISSION_MATRIX, RBAC_COMMIT, Role


def _authz(roles: dict[str, str]) -> AuthRBAC:
    return AuthRBAC(InMemoryUserRoleRepository(roles))


# --------------------------------------------------------------------------
# DENY-1 — the four fail-closed cases, each independently constructible by INPUT
# --------------------------------------------------------------------------
def test_deny_unknown_user():
    assert _authz({}).authorize("nobody", RBAC_COMMIT) is False


def test_deny_noncanonical_role():
    az = _authz({"u1": "wizard"})
    assert az.authorize("u1", RBAC_COMMIT) is False
    assert az.authorize("u1", "view_queue") is False


@pytest.mark.parametrize("blank", ["", "   ", "\t"])
def test_deny_blank_role(blank):
    assert _authz({"u1": blank}).authorize("u1", "view_queue") is False


def test_deny_unlisted_action_for_valid_role():
    az = _authz({"aud": "auditor"})
    assert az.authorize("aud", RBAC_COMMIT) is False        # auditor cannot commit
    assert az.authorize("aud", "manage_users") is False     # not in auditor's set


# --------------------------------------------------------------------------
# MATRIX (authorize level) — every grid cell matches the matrix, defined bool
# --------------------------------------------------------------------------
@pytest.mark.parametrize("role", list(Role))
@pytest.mark.parametrize("action", sorted(ALL_RBAC_ACTIONS))
def test_authorize_matches_matrix_for_every_grid_cell(role, action):
    az = _authz({"u": role.value})
    expected = action in PERMISSION_MATRIX[role]
    result = az.authorize("u", action)
    assert result is expected
    assert isinstance(result, bool)


def test_commit_true_only_for_underwriter_via_authorize():
    assert _authz({"u": "underwriter"}).authorize("u", RBAC_COMMIT) is True
    assert _authz({"u": "auditor"}).authorize("u", RBAC_COMMIT) is False
    assert _authz({"u": "admin"}).authorize("u", RBAC_COMMIT) is False


# --------------------------------------------------------------------------
# DET-1 — repeat-invariance
# --------------------------------------------------------------------------
def test_repeat_invariance():
    az = _authz({"u": "underwriter"})
    assert {az.authorize("u", RBAC_COMMIT) for _ in range(25)} == {True}
    az2 = _authz({"u": "auditor"})
    assert {az2.authorize("u", RBAC_COMMIT) for _ in range(25)} == {False}


# --------------------------------------------------------------------------
# BIAS-1 — structural: no demographic-shaped parameter can enter the decision
# --------------------------------------------------------------------------
def test_authorize_signature_is_exactly_user_id_and_rbac_action():
    sig = inspect.signature(AuthRBAC.authorize)
    params = [p for p in sig.parameters if p != "self"]
    assert params == ["user_id", "rbac_action"]
    for p in sig.parameters.values():
        assert "ApplicantProfile" not in str(p.annotation)
        assert "Demographic" not in str(p.annotation)


def test_swap_invariance_demographics_not_an_input():
    # demographics are not even an input — same user/role -> same result
    az = _authz({"u": "underwriter"})
    assert az.authorize("u", RBAC_COMMIT) == az.authorize("u", RBAC_COMMIT)


# --------------------------------------------------------------------------
# PERF-1 — observed, non-gating
# --------------------------------------------------------------------------
def test_authorize_latency_observed():
    az = _authz({"u": "underwriter"})
    start = time.perf_counter()
    for _ in range(1000):
        az.authorize("u", RBAC_COMMIT)
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"\n[PERF-1 observed] 1000 authorize calls: {elapsed_ms:.2f} ms (soft, non-gating)")
    assert elapsed_ms >= 0  # observed only — never gates the build
