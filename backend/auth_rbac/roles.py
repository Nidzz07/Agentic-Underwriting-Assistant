"""C2 Role + C3 PERMISSION_MATRIX + C4 to_role — the policy data + canonicalization.

- **Role** — the canonical role set, **closed at the app layer** (auth-rbac owns it).
  The `database` `app_user.role` column stays an open `VARCHAR` (BR-DB-12); auth-rbac
  never adds a DB CHECK.
- **rbac_action vocabulary** — the RBAC OPERATIONS (distinct from
  `CommittedDecision.action` approve/override, BR-AUTH-11). `RBAC_COMMIT`'s VALUE
  (`"commit"`) equals audit-store's `RBAC_COMMIT` **by contract** — matched by value,
  NOT imported (duck-typed; no production `audit_store` import).
- **PERMISSION_MATRIX** — the immutable single policy datum (`dict[Role, frozenset]`).
- **to_role** — the TOTAL canonicalization helper (raw `str | None` -> `Role | None`),
  fail-closing on None / blank / non-canonical with no exception as control flow.

No LLM. No credentials.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional


class Role(str, Enum):
    """The canonical Phase-1 role set (closed at the app layer). Extending it is a
    forward-only app-layer change — no DB migration (BR-DB-12)."""
    UNDERWRITER = "underwriter"   # acts: may reach the commit boundary; may read
    AUDITOR = "auditor"           # read-only (SEC-4); may NOT commit
    ADMIN = "admin"               # user/config management via admin-cli; not an underwriting actor


# --- rbac_action vocabulary (the RBAC operations) -------------------------------
#: The commit operation. VALUE equals audit-store's ``RBAC_COMMIT`` by contract
#: (duck-typed; audit_store is NOT imported in production).
RBAC_COMMIT = "commit"
VIEW_QUEUE = "view_queue"
VIEW_MEMO = "view_memo"
READ_AUDIT = "read_audit"
MANAGE_USERS = "manage_users"
MANAGE_CONFIG = "manage_config"

#: Every known rbac_action — for exhaustive MATRIX-1 coverage.
ALL_RBAC_ACTIONS: frozenset[str] = frozenset({
    RBAC_COMMIT, VIEW_QUEUE, VIEW_MEMO, READ_AUDIT, MANAGE_USERS, MANAGE_CONFIG,
})

#: The single authorization policy datum (immutable). underwriter: commit + read ops;
#: auditor: read ops only (no commit); admin: manage_users + config ops.
PERMISSION_MATRIX: dict[Role, frozenset[str]] = {
    Role.UNDERWRITER: frozenset({RBAC_COMMIT, VIEW_QUEUE, VIEW_MEMO, READ_AUDIT}),
    Role.AUDITOR: frozenset({VIEW_QUEUE, VIEW_MEMO, READ_AUDIT}),
    Role.ADMIN: frozenset({MANAGE_USERS, MANAGE_CONFIG}),
}

#: Exact canonical string -> Role member (built once).
_CANONICAL: dict[str, Role] = {role.value: role for role in Role}


def to_role(raw: Optional[str]) -> Optional[Role]:
    """Map a raw ``app_user.role`` value to a canonical ``Role``, or ``None`` to
    fail-close.

    Total + deterministic: ``None`` (no row), blank/whitespace, and any string that is
    not an **exact** canonical value all return ``None`` (fail-close). A wrong-case or
    whitespace-padded value is treated as non-canonical → ``None`` (deny-safe). No
    ``try/except`` as control flow.
    """
    if raw is None:
        return None
    if raw.strip() == "":            # blank / whitespace-only
        return None
    return _CANONICAL.get(raw)       # exact canonical match, else None
