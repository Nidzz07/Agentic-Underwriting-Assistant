"""C5 UserRoleRepository — the role read model (Protocol + in-memory fake).

The **read contract** (FD §2.5): `get_role(user_id) -> str | None` returns the **raw**
`app_user.role` value — `None` when there is no matching row; otherwise the stored
string **exactly as persisted** (canonical or not, possibly blank). The lookup does
**not** canonicalize — that (and the fail-close) is `authorize`'s job.

Both this in-memory fake and the real Postgres adapter (`pg_repository.py`) implement
the **one** Protocol, so they cannot drift. No LLM. No credentials.
"""
from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class UserRoleRepository(Protocol):
    def get_role(self, user_id: str) -> Optional[str]:
        """Return the raw stored role for ``user_id``, or ``None`` if no such user."""
        ...


class InMemoryUserRoleRepository:
    """Deterministic in-memory fake — a preset ``user_id -> raw role string`` map.
    Returns ``None`` for an unknown ``user_id`` (the no-row case)."""

    def __init__(self, roles: Optional[dict[str, str]] = None) -> None:
        self._roles: dict[str, str] = dict(roles or {})

    def get_role(self, user_id: str) -> Optional[str]:
        return self._roles.get(user_id)
