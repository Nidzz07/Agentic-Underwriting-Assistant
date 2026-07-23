"""C1 AuthRBAC — the single authorization policy entry point.

`authorize(user_id, rbac_action) -> bool` is **one** linear, fail-closed flow
(FailClosedMatrixLookup): read the raw role via the injected `UserRoleRepository` →
canonicalize with `to_role` (fail-close to `None` for no-row / blank / non-canonical) →
`rbac_action ∈ PERMISSION_MATRIX[role]`. The four DENY-1 cases + the exhaustive matrix +
the commit slice are all satisfied by this one implementation (inputs vary, not code).

**Conformance (reference-not-own):** `authorize`'s signature matches audit-store's
`@runtime_checkable Authorizer` Protocol by **duck typing** — this module does **NOT**
import `audit_store`. The Protocol import + `isinstance` live only in the PROTOCOL-1
test. Structurally verified by `tests/test_no_forbidden_imports.py`.

**Pure + deterministic (DET-1):** a function of (the injected role read, the immutable
`PERMISSION_MATRIX`) — no wall-clock, no randomness, no global mutable state.
**Advisory-only:** this gates *who may act*; it never finalizes an underwriting outcome.
No LLM. No credentials.
"""
from __future__ import annotations

from backend.auth_rbac.repository import UserRoleRepository
from backend.auth_rbac.roles import PERMISSION_MATRIX, to_role


class AuthRBAC:
    """The one policy. `authorize` is injected with a `UserRoleRepository` (the fake in
    tests; the real Postgres adapter in production)."""

    def __init__(self, repository: UserRoleRepository) -> None:
        self._repository = repository

    def authorize(self, user_id: str, rbac_action: str) -> bool:
        raw = self._repository.get_role(user_id)   # raw str | None (no row -> None)
        role = to_role(raw)                        # canonicalize + fail-close
        if role is None:                           # unknown user / non-canonical / blank
            return False
        return rbac_action in PERMISSION_MATRIX[role]
