"""C4 AppUserWriter — the two ``app_user`` mutations, gated + interpreted (P3).

``create_user`` / ``set_role`` each invoke ``RoleGate.check`` **FIRST** (before any
connection is acquired — the SOLE gate is on the sole path, structurally
un-bypassable, P2 / ADMIN-NFRD-Fold-1), then build a parameterized statement, delegate
the real round-trip to the injected :class:`~backend.admin_cli.pg_writer.PgWriter`, and
**interpret** the result into explicit typed errors:

- an ``IntegrityError`` (PK ``user_id`` / UNIQUE ``subject``) -> :class:`UserWriteError`
  ``"already exists"`` (generic-but-accurate for either constraint, ADMIN-NFRD-Fold-2);
- ``rowcount == 0`` (no matching row) -> :class:`UserWriteError` ``"no such user"``.

No upsert, no pre-SELECT (atomic, race-free). Reference-not-own: parameterized SQL over
an injected ``Engine`` (via ``PgWriter``); no ``database``/``auth_rbac`` production
import; no schema/CHECK added (BR-DB-12). No LLM.
"""
from __future__ import annotations

from typing import Optional, Protocol

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from backend.admin_cli.exceptions import UserWriteError
from backend.admin_cli.role_gate import RoleGate

_INSERT_USER = sa.text(
    "INSERT INTO app_user (user_id, subject, role) VALUES (:user_id, :subject, :role)"
)
_UPDATE_ROLE = sa.text("UPDATE app_user SET role = :role WHERE user_id = :user_id")


class _Writer(Protocol):
    """The write shim contract (real :class:`PgWriter`; a spy/fake in tier-U tests)."""

    def execute_write(self, statement: sa.TextClause, params: dict) -> sa.CursorResult:
        ...


class AppUserWriter:
    """The two ``app_user`` operations — gate-first, parameterized, explicitly
    conflict/absence-detecting."""

    def __init__(self, writer: _Writer, gate: Optional[RoleGate] = None) -> None:
        self._writer = writer
        self._gate = gate if gate is not None else RoleGate()

    def create_user(self, user_id: str, subject: str, role: Optional[str]) -> None:
        """INSERT a new ``app_user``; a duplicate ``user_id``/``subject`` raises
        :class:`UserWriteError` ``"already exists"``."""
        self._gate.check(role)  # FIRST — before any connection is acquired
        try:
            self._writer.execute_write(
                _INSERT_USER,
                {"user_id": user_id, "subject": subject, "role": role},
            )
        except IntegrityError as exc:
            raise UserWriteError(f"user {user_id} already exists") from exc

    def set_role(self, user_id: str, role: Optional[str]) -> None:
        """UPDATE an existing user's role; ``rowcount == 0`` raises
        :class:`UserWriteError` ``"no such user"``."""
        self._gate.check(role)  # FIRST — before any connection is acquired
        result = self._writer.execute_write(
            _UPDATE_ROLE, {"user_id": user_id, "role": role}
        )
        if result.rowcount == 0:
            raise UserWriteError(f"no such user {user_id}")
