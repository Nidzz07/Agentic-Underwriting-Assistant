"""AuthenticationService — the one place a credential is checked and a session is issued.

**Uniform failure is the design, not a detail (Q4).** ``authenticate`` returns ``None`` for
**every** rejection — unknown user, no credential row, wrong password, locked account — so
the caller structurally *cannot* distinguish them and map them to different responses. The
route turns that single ``None`` into the single WIRE-1 ``401``. Anything finer-grained is a
**user-enumeration oracle**, which is why even "you are locked out" is withheld.

⚑ **The unknown-user path runs a dummy verify.** Without it, a missing user would return
noticeably faster than a wrong password, and the response *timing* would leak exactly what
the uniform envelope is hiding. The dummy hash is a module constant computed once.

**Everything time-dependent is injected** (``clock``, ``token_factory``), so lockout windows
and session expiry are provable at tier-U without sleeping and without a real CSPRNG.

**No logging anywhere in this module** — a password or token in a log line would defeat the
whole layer, so the safest construction is one that never has a logger to misuse.
**No LLM. No environment reads.**
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from typing import Callable, Optional, Protocol

from backend.authn.constants import LOCKOUT_DURATION, MAX_FAILED_ATTEMPTS, SESSION_TTL
from backend.authn.hashing import hash_password, verify_password
from backend.authn.store import CredentialStore, SessionRecord, SessionStore


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    """Production clock — timezone-aware UTC, matching the schema's TIMESTAMPTZ columns."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


def new_token() -> str:
    """A high-entropy opaque session token. Never a JWT, never signed — see WIRE-1 §6."""
    return secrets.token_urlsafe(32)


def session_id_for(raw_token: str) -> str:
    """The SHA-256 hex of a raw token — what is PERSISTED, so a DB read yields nothing usable."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


#: Computed once, at import, so the unknown-user path costs the same as a real verify.
_DUMMY_HASH = hash_password("dummy-password-for-constant-time-unknown-user-path")


class AuthenticationService:
    def __init__(
        self,
        credentials: CredentialStore,
        sessions: SessionStore,
        clock: Optional[Clock] = None,
        token_factory: Callable[[], str] = new_token,
    ) -> None:
        self._credentials = credentials
        self._sessions = sessions
        self._clock = clock if clock is not None else SystemClock()
        self._new_token = token_factory

    def authenticate(self, user_id: str, password: str) -> Optional[str]:
        """Return a RAW session token on success, or ``None`` — uniformly — on any failure."""
        now = self._clock.now()
        record = self._credentials.get(user_id)

        if record is None:
            verify_password(_DUMMY_HASH, password)   # timing parity; result deliberately unused
            return None

        if record.locked_until is not None and record.locked_until > now:
            return None

        if not verify_password(record.password_hash, password):
            attempts = record.failed_attempts + 1
            locked_until = now + LOCKOUT_DURATION if attempts >= MAX_FAILED_ATTEMPTS else None
            self._credentials.record_failure(user_id, now, locked_until)
            return None

        self._credentials.reset_failures(user_id)
        raw_token = self._new_token()
        self._sessions.create(SessionRecord(
            session_id=session_id_for(raw_token),
            user_id=user_id,
            created_at=now,
            expires_at=now + SESSION_TTL,
            revoked_at=None,
        ))
        return raw_token

    def resolve(self, raw_token: str) -> Optional[str]:
        """Return the session's ``user_id``, or ``None`` if absent, expired or revoked.

        ⚑ Expiry and revocation are checked **server-side on every call** — that is what
        makes an 8-hour TTL acceptable and what makes logout take effect immediately.
        """
        now = self._clock.now()
        record = self._sessions.get(session_id_for(raw_token))
        if record is None or record.revoked_at is not None or record.expires_at <= now:
            return None
        return record.user_id

    def logout(self, raw_token: str) -> None:
        """Revoke the session. Idempotent, and silent about whether it existed."""
        self._sessions.revoke(session_id_for(raw_token), self._clock.now())
