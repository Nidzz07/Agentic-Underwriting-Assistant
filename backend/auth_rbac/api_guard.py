"""C6 ApiAuthGuard — the API-layer enforcement POINT (pure delegation).

`check(user_id, rbac_action) -> bool` returns **exactly** `AuthRBAC.authorize(...)`'s
result. The guard is a second enforcement **point**, NOT a second policy: it holds a
single injected `AuthRBAC`, no `Role`/matrix data, and makes **no** allow/deny decision
of its own (NFR-AUTH-SSOT-1 / fold #2). It MAY route an endpoint to its required
`rbac_action` (a mapping concern, done by the caller/app-assembly unit) but MUST NOT
decide allow/deny itself.

> **If a raising `require(...)` convenience is ever added** (for FastAPI, e.g. raise 403
> on deny), it **MUST delegate to `check`/`authorize` internally** — no independent
> decision — so SSOT-1 continues to hold for it too. `require()` is deliberately **not
> built or tested in this unit**; the concrete FastAPI dependency + route wiring are the
> app-assembly unit's Code-Gen.

Imports **no** `audit_store`/`database` module (references only `AuthRBAC`). No LLM.
"""
from __future__ import annotations

from backend.auth_rbac.authorizer import AuthRBAC


class ApiAuthGuard:
    """Constructor-injected single `AuthRBAC`; `check` delegates only."""

    def __init__(self, authz: AuthRBAC) -> None:
        self._authz = authz

    def check(self, user_id: str, rbac_action: str) -> bool:
        """Return exactly the one policy's decision for ``(user_id, rbac_action)``."""
        return self._authz.authorize(user_id, rbac_action)
