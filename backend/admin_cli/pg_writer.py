"""C4 (omitted shim) PgWriter — the thin injected-Engine SQL round-trip.

The **only** DB-touching code in admin-cli: ``engine.begin()`` + ``conn.execute``.
Mirrors auth-rbac's ``pg_repository.py`` posture (injected ``sqlalchemy.Engine``,
parameterized SQL, no secret VALUE) and is likewise **omitted from unit coverage**
(exercised via the testcontainers integration tier, not unit-import-covered).

SQLAlchemy 2.0: the ``Engine``'s only DB entry points are ``connect()``/``begin()``
(there is no ``.execute`` on ``Engine``) — the ``RoleGate`` runs before this shim is
ever called (ADMIN-NFR-Fold-2), so a spy engine observing ``begin()`` proves the
gate-before-connection ordering. No LLM.
"""
from __future__ import annotations

import sqlalchemy as sa


class PgWriter:
    """Execute a parameterized write statement over an injected ``Engine``."""

    def __init__(self, engine: sa.Engine) -> None:
        self._engine = engine

    def execute_write(self, statement: sa.TextClause, params: dict) -> sa.CursorResult:
        with self._engine.begin() as conn:
            return conn.execute(statement, params)
