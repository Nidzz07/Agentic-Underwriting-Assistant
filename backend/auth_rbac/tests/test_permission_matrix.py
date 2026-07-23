"""Unit tests — C3 PERMISSION_MATRIX / NFR-AUTH-MATRIX-1 + NFR-AUTH-COMMIT-1 (Step 1).

The role->permission policy as a data-driven total-coverage property: every
(Role x rbac_action) combination has a defined, deterministic bool outcome, no
unhandled combination. Plus the SEC-4 core slice: commit only for underwriter.
"""
from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from backend.auth_rbac.roles import (
    ALL_RBAC_ACTIONS,
    PERMISSION_MATRIX,
    RBAC_COMMIT,
    Role,
)


def _allows(role: Role, action: str) -> bool:
    return action in PERMISSION_MATRIX[role]


# --------------------------------------------------------------------------
# MATRIX-1 — every (Role x rbac_action) has a defined bool; no unhandled combo
# --------------------------------------------------------------------------
@pytest.mark.parametrize("role", list(Role))
@pytest.mark.parametrize("action", sorted(ALL_RBAC_ACTIONS))
def test_full_cross_product_defined_bool(role, action):
    result = _allows(role, action)
    assert isinstance(result, bool)  # defined, no exception, no None


def test_every_role_has_a_matrix_entry():
    assert set(PERMISSION_MATRIX) == set(Role)  # no unhandled role


def test_matrix_values_are_frozensets_of_known_actions():
    for role, allowed in PERMISSION_MATRIX.items():
        assert isinstance(allowed, frozenset)
        assert allowed <= ALL_RBAC_ACTIONS  # no unknown action leaks in


@given(st.sampled_from(list(Role)), st.sampled_from(sorted(ALL_RBAC_ACTIONS)))
def test_matrix_membership_is_total_hypothesis(role, action):
    assert isinstance(action in PERMISSION_MATRIX[role], bool)


# --------------------------------------------------------------------------
# COMMIT-1 — commit is granted ONLY to underwriter (satisfies UnauthorizedCommit)
# --------------------------------------------------------------------------
def test_commit_only_underwriter():
    assert _allows(Role.UNDERWRITER, RBAC_COMMIT) is True
    assert _allows(Role.AUDITOR, RBAC_COMMIT) is False
    assert _allows(Role.ADMIN, RBAC_COMMIT) is False


def test_auditor_is_read_only():
    # no write-ish action; specifically no commit
    assert RBAC_COMMIT not in PERMISSION_MATRIX[Role.AUDITOR]
    assert PERMISSION_MATRIX[Role.AUDITOR] == frozenset({"view_queue", "view_memo", "read_audit"})
