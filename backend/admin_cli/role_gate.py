"""C3 RoleGate — the pre-connection canonical-role SOLE gate (P2 / SEC-4).

Validates ``role in Role`` (auth-rbac's canonical set, imported **call-only**) BEFORE
any DB connection is acquired. ``AppUserWriter`` composes this and invokes ``check`` as
the **first line** of each write method, so a non-canonical role is rejected before
``connect()``/``begin()`` — and because ``app_user.role`` is an open ``VARCHAR`` with
**no CHECK** (BR-DB-12), this pre-write check is the **SOLE** structural enforcement
(ADMIN-Fold-1). Pure: no DB, no I/O. No LLM.
"""
from __future__ import annotations

from typing import Optional

from backend.auth_rbac.roles import Role
from backend.admin_cli.exceptions import RoleValidationError

#: The canonical value set, single-sourced from auth-rbac's ``Role`` (auto-agrees if
#: the enum extends). Non-canonical, blank, wrong-case, and ``None`` all fall outside.
_CANONICAL: frozenset[str] = frozenset(r.value for r in Role)


class RoleGate:
    """Reject any role not in auth-rbac's canonical ``Role`` value set."""

    def check(self, role: Optional[str]) -> None:
        """Raise :class:`RoleValidationError` unless ``role`` is an exact canonical
        value. ``None``, blank/whitespace, wrong-case, and unknown values are all
        rejected (fail-closed) BEFORE any SQL; a canonical role returns ``None``."""
        if role not in _CANONICAL:
            raise RoleValidationError(f"invalid role {role!r}")
