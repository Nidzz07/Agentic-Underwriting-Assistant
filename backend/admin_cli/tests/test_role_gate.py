"""C3 RoleGate — the canonical-role SOLE gate, pure (NFR-ADMIN-ROLEGATE-1, tier U)."""
from __future__ import annotations

import pytest

from backend.admin_cli.exceptions import RoleValidationError
from backend.admin_cli.role_gate import RoleGate
from backend.auth_rbac.roles import Role


@pytest.mark.parametrize("role", [r.value for r in Role])
def test_canonical_roles_pass(role):
    RoleGate().check(role)  # no raise


@pytest.mark.parametrize("role", ["superuser", "Admin", "UNDERWRITER", "", "   ", None])
def test_non_canonical_roles_are_rejected(role):
    with pytest.raises(RoleValidationError) as ei:
        RoleGate().check(role)
    assert repr(role) in str(ei.value)  # "invalid role {role!r}"


def test_gate_is_single_sourced_from_auth_rbac_role():
    # The gate accepts exactly auth-rbac's canonical value set (auto-agrees if it extends).
    for role in Role:
        RoleGate().check(role.value)
