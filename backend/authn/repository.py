"""Real Postgres adapters for the credential + session stores.

Shares the one Protocol pair with the in-memory fakes in ``store.py``, so the two cannot
drift. **SEC-3**: takes an **injected** ``sqlalchemy.Engine`` — no connection string and no
credential VALUE appears here.

⚑ **Owner engine only.** Both tables are owner-only by construction (``0003_auth.sql`` grants
nothing, applying after ``0002_grants.sql``), so this binds to the ``DATABASE_URL`` engine —
the same posture ``app_user`` already has, ratified as CORE-RATIONALE-20 (register #20).

Coverage-omitted like every other live-DB adapter in this build (the ``pg_repository.py`` /
``case_lifecycle/repository.py`` precedent); exercised via the in-memory fakes at tier-U and
against a real database in CI. **No LLM.**
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import sqlalchemy as sa

from backend.authn.store import CredentialRecord, SessionRecord

_GET_CREDENTIAL = sa.text(
    "SELECT user_id, password_hash, failed_attempts, locked_until, updated_at "
    "FROM user_credential WHERE user_id = :user_id"
)
_UPSERT_CREDENTIAL = sa.text(
    "INSERT INTO user_credential (user_id, password_hash, failed_attempts, locked_until, updated_at) "
    "VALUES (:user_id, :password_hash, 0, NULL, :now) "
    "ON CONFLICT (user_id) DO UPDATE SET password_hash = :password_hash, "
    "failed_attempts = 0, locked_until = NULL, updated_at = :now"
)
_RECORD_FAILURE = sa.text(
    "UPDATE user_credential SET failed_attempts = failed_attempts + 1, "
    "locked_until = :locked_until, updated_at = :now WHERE user_id = :user_id"
)
_RESET_FAILURES = sa.text(
    "UPDATE user_credential SET failed_attempts = 0, locked_until = NULL WHERE user_id = :user_id"
)
_CREATE_SESSION = sa.text(
    "INSERT INTO user_session (session_id, user_id, created_at, expires_at, revoked_at) "
    "VALUES (:session_id, :user_id, :created_at, :expires_at, NULL)"
)
_GET_SESSION = sa.text(
    "SELECT session_id, user_id, created_at, expires_at, revoked_at "
    "FROM user_session WHERE session_id = :session_id"
)
_REVOKE_SESSION = sa.text(
    "UPDATE user_session SET revoked_at = :now WHERE session_id = :session_id AND revoked_at IS NULL"
)


class PostgresCredentialStore:
    """Real credential adapter. Injected engine; parameterized statements only."""

    def __init__(self, engine: sa.Engine) -> None:
        self._engine = engine

    def get(self, user_id: str) -> Optional[CredentialRecord]:
        with self._engine.connect() as conn:
            row = conn.execute(_GET_CREDENTIAL, {"user_id": user_id}).mappings().one_or_none()
        return None if row is None else CredentialRecord(**dict(row))

    def set_password(self, user_id: str, password_hash: str, now: datetime) -> None:
        with self._engine.begin() as conn:
            conn.execute(_UPSERT_CREDENTIAL,
                         {"user_id": user_id, "password_hash": password_hash, "now": now})

    def record_failure(self, user_id: str, now: datetime, locked_until: Optional[datetime]) -> None:
        with self._engine.begin() as conn:
            conn.execute(_RECORD_FAILURE,
                         {"user_id": user_id, "now": now, "locked_until": locked_until})

    def reset_failures(self, user_id: str) -> None:
        with self._engine.begin() as conn:
            conn.execute(_RESET_FAILURES, {"user_id": user_id})


class PostgresSessionStore:
    """Real session adapter. ``session_id`` is always the SHA-256 of the raw token."""

    def __init__(self, engine: sa.Engine) -> None:
        self._engine = engine

    def create(self, record: SessionRecord) -> None:
        with self._engine.begin() as conn:
            conn.execute(_CREATE_SESSION, {
                "session_id": record.session_id, "user_id": record.user_id,
                "created_at": record.created_at, "expires_at": record.expires_at,
            })

    def get(self, session_id: str) -> Optional[SessionRecord]:
        with self._engine.connect() as conn:
            row = conn.execute(_GET_SESSION, {"session_id": session_id}).mappings().one_or_none()
        return None if row is None else SessionRecord(**dict(row))

    def revoke(self, session_id: str, now: datetime) -> None:
        with self._engine.begin() as conn:
            conn.execute(_REVOKE_SESSION, {"session_id": session_id, "now": now})


_USER_EXISTS = sa.text("SELECT 1 FROM app_user WHERE user_id = :user_id")


class PostgresUserDirectory:
    """The ``UserDirectory`` existence check, read-only against ``app_user``.

    ⚑ Writes its OWN parameterized query rather than importing ``auth_rbac``, following the
    pattern that unit already set for the same table (*"consumes database's app_user via
    auth-rbac's own parameterized query… imports no database/audit_store module"*). Keeps
    ``authn`` self-contained: it shares a TABLE with other units, never a module.

    Existence, not role: a user whose ``role`` is blank still **exists**, and it is
    ``to_role``'s job — not this one's — to fail-close on the role at authentication time.
    """

    def __init__(self, engine: sa.Engine) -> None:
        self._engine = engine

    def exists(self, user_id: str) -> bool:
        with self._engine.connect() as conn:
            return conn.execute(_USER_EXISTS, {"user_id": user_id}).scalar_one_or_none() is not None
