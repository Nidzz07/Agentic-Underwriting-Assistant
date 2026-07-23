"""Unit test — NFR-AUTH-PROTOCOL-1 (Step 7).

Proven by TWO assertions together, since `@runtime_checkable` `isinstance` verifies
METHOD PRESENCE only (not the signature):
  1. structural presence — `isinstance(AuthRBAC(...), Authorizer)` is True;
  2. call-shape / return-type — `authorize(user_id, rbac_action)` returns a `bool`.

This is the ONLY file in `auth-rbac` that imports `audit_store` — a READ-ONLY import of
the Protocol, in a TEST (never in production; see test_no_forbidden_imports.py).
"""
from __future__ import annotations

# TEST-ONLY read-only import of the consumer's Protocol (never in production code).
from backend.audit_store.seams import RBAC_COMMIT, Authorizer
from backend.auth_rbac.authorizer import AuthRBAC
from backend.auth_rbac.repository import InMemoryUserRoleRepository
from backend.auth_rbac.roles import RBAC_COMMIT as AUTH_RBAC_COMMIT


def _authz() -> AuthRBAC:
    return AuthRBAC(InMemoryUserRoleRepository({"u": "underwriter"}))


def test_isinstance_authorizer_structural_presence():
    # @runtime_checkable verifies the `authorize` method is present (not its signature).
    assert isinstance(_authz(), Authorizer) is True


def test_call_shape_returns_bool():
    # pins the signature + return type the Protocol declares (isinstance does not).
    result = _authz().authorize("u", "commit")
    assert isinstance(result, bool)


def test_rbac_commit_value_matches_audit_store_by_contract():
    # auth-rbac defines its own RBAC_COMMIT by VALUE (duck-typed) — it must equal
    # audit-store's so authorize(user, RBAC_COMMIT) drives the built commit re-check.
    assert AUTH_RBAC_COMMIT == RBAC_COMMIT == "commit"
