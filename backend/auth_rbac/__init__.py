"""`auth-rbac` (U11) — the canonical role/permission model + backend enforcement.

The single authorization policy (`AuthRBAC.authorize`), the canonical `Role` enum
(closed at the app layer; the DB `role` column stays open, BR-DB-12), the immutable
`PERMISSION_MATRIX`, the `to_role` canonicalization helper, the `UserRoleRepository`
read model (Protocol + in-memory fake + real Postgres adapter), and the `ApiAuthGuard`
delegation guard.

Boundaries held (FD / NFR Design):
- **Reference-not-own** — this package's production code NEVER imports
  ``backend.audit_store`` or ``backend.database``. Conformance to audit-store's
  ``Authorizer`` Protocol is duck-typed; the Protocol import lives only in the
  PROTOCOL-1 test. The real adapter consumes ``database``'s ``app_user`` via its own
  query, asserting nothing about its schema. (Structurally verified —
  ``tests/test_no_forbidden_imports.py``.)
- **SEC-4** fail-closed (deny-by-default); **CON-BR1** — no demographics in the authz
  path; **advisory-only** — "decision" is not used for an authz result; **SEC-3** — no
  credentials (the real adapter takes an injected ``Engine``). **No LLM.**
"""
from __future__ import annotations
