"""C5 real UserRoleRepository — reads the raw `app_user.role` from Postgres.

Consumes `database`'s `app_user` via auth-rbac's **own** parameterized query — reads
exactly `user_id` -> `role`, returns the raw string or `None` (no row). It **imports no
`database`/`audit_store` module** and adds **no schema/FIDELITY assertion** of its own
(SCOPE-1): `app_user` drift protection, if ever wanted, is `database`'s concern. Shares
the one `UserRoleRepository` Protocol with the in-memory fake (no drift).

**SEC-3:** takes an **injected** ``sqlalchemy.Engine`` — no connection string / credential
VALUE appears here (the URL is `secrets-config`'s). Exercised via the optional
testcontainers smoke; omitted from unit-tier coverage (like every unit's `pg_repository.py`).
No LLM.
"""
from __future__ import annotations

from typing import Optional

import sqlalchemy as sa

#: Read exactly the raw role for one user (user_id is app_user's PK -> 0 or 1 row).
_GET_ROLE = sa.text("SELECT role FROM app_user WHERE user_id = :user_id")


class PostgresUserRoleRepository:
    """Real adapter over the shared Postgres. Injected engine; parameterized read."""

    def __init__(self, engine: sa.Engine) -> None:
        self._engine = engine

    def get_role(self, user_id: str) -> Optional[str]:
        with self._engine.connect() as conn:
            return conn.execute(_GET_ROLE, {"user_id": user_id}).scalar_one_or_none()
