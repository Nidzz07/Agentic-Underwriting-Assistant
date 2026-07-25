"""Credential + session store Protocols, and deterministic in-memory fakes.

⚑ **Authored OUTSIDE ``backend/app/`` deliberately (Q12a).** This is the constraint that
**preserves A-4** — the composition root's guarantee that *"every write goes through the
frozen ``DecisionCommitService``"*. If these stores lived under ``backend/app/``, ``.insert(``
would appear there and ``test_no_write_route.py``'s assertion would have had to be relaxed.
Authoring them here means that guarantee survives this work **completely intact**.

Follows U24 ``case_lifecycle``'s pattern exactly: Protocols + in-memory fakes here, the real
Postgres adapters in ``repository.py``, both injected at the composition root.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Iterable, Optional, Protocol


@dataclass(frozen=True)
class CredentialRecord:
    """A user's stored credential. ``password_hash`` is an Argon2id ENCODED string."""
    user_id: str
    password_hash: str
    failed_attempts: int
    locked_until: Optional[datetime]
    updated_at: datetime


@dataclass(frozen=True)
class SessionRecord:
    """An issued session. ``session_id`` is the SHA-256 of the raw token, never the token."""
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    revoked_at: Optional[datetime]


class CredentialStore(Protocol):
    def get(self, user_id: str) -> Optional[CredentialRecord]: ...
    def set_password(self, user_id: str, password_hash: str, now: datetime) -> None: ...
    def record_failure(self, user_id: str, now: datetime, locked_until: Optional[datetime]) -> None: ...
    def reset_failures(self, user_id: str) -> None: ...


class SessionStore(Protocol):
    def create(self, record: SessionRecord) -> None: ...
    def get(self, session_id: str) -> Optional[SessionRecord]: ...
    def revoke(self, session_id: str, now: datetime) -> None: ...


class InMemoryCredentialStore:
    """Deterministic fake — the tier-U counterpart of the Postgres adapter."""

    def __init__(self) -> None:
        self._rows: dict[str, CredentialRecord] = {}

    def get(self, user_id: str) -> Optional[CredentialRecord]:
        return self._rows.get(user_id)

    def set_password(self, user_id: str, password_hash: str, now: datetime) -> None:
        self._rows[user_id] = CredentialRecord(
            user_id=user_id, password_hash=password_hash,
            failed_attempts=0, locked_until=None, updated_at=now,
        )

    def record_failure(self, user_id: str, now: datetime, locked_until: Optional[datetime]) -> None:
        row = self._rows.get(user_id)
        if row is None:
            return
        self._rows[user_id] = replace(
            row, failed_attempts=row.failed_attempts + 1, locked_until=locked_until, updated_at=now,
        )

    def reset_failures(self, user_id: str) -> None:
        row = self._rows.get(user_id)
        if row is not None:
            self._rows[user_id] = replace(row, failed_attempts=0, locked_until=None)


class InMemorySessionStore:
    """Deterministic fake. ``all_ids`` exists so a test can prove the RAW token is absent."""

    def __init__(self) -> None:
        self._rows: dict[str, SessionRecord] = {}

    def create(self, record: SessionRecord) -> None:
        self._rows[record.session_id] = record

    def get(self, session_id: str) -> Optional[SessionRecord]:
        return self._rows.get(session_id)

    def revoke(self, session_id: str, now: datetime) -> None:
        row = self._rows.get(session_id)
        if row is not None:
            self._rows[session_id] = replace(row, revoked_at=now)

    def all_ids(self) -> Iterable[str]:
        return list(self._rows)
