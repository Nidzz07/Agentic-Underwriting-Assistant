"""AuthenticationService — uniform failure, lockout, and revocable sessions.

Every test runs over the in-memory fakes with an injected clock, so the whole layer is
tier-U testable with **no database, no environment and no wall-clock dependence**.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from backend.authn.constants import LOCKOUT_DURATION, MAX_FAILED_ATTEMPTS, SESSION_TTL
from backend.authn.hashing import hash_password
from backend.authn.service import AuthenticationService
from backend.authn.store import InMemoryCredentialStore, InMemorySessionStore

_PASSWORD = "correct horse battery staple"
_T0 = datetime(2026, 7, 25, 9, 0, 0, tzinfo=timezone.utc)


class _Clock:
    """A movable clock — lockout and expiry must be provable without sleeping."""

    def __init__(self, now: datetime = _T0) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> None:
        self._now += delta


def _service(*, with_user: bool = True, with_credential: bool = True):
    clock = _Clock()
    credentials = InMemoryCredentialStore()
    if with_user and with_credential:
        credentials.set_password("u1", hash_password(_PASSWORD), clock.now())
    sessions = InMemorySessionStore()
    counter = iter(f"raw-token-{n}" for n in range(1000))
    service = AuthenticationService(
        credentials=credentials,
        sessions=sessions,
        clock=clock,
        token_factory=lambda: next(counter),
    )
    return service, clock, credentials, sessions


# --- (1)-(4) UNIFORM FAILURE: four distinct causes, one indistinguishable outcome ------

def test_an_unknown_user_returns_none():
    service, _, _, _ = _service(with_user=False, with_credential=False)
    assert service.authenticate("nobody", _PASSWORD) is None


def test_a_user_with_no_credential_row_returns_none():
    # A legitimate state: provisioned via admin, password never set.
    service, _, _, _ = _service(with_credential=False)
    assert service.authenticate("u1", _PASSWORD) is None


def test_a_wrong_password_returns_none():
    service, _, _, _ = _service()
    assert service.authenticate("u1", "wrong") is None


def test_a_locked_account_returns_none_even_with_the_correct_password():
    service, _, _, _ = _service()
    for _ in range(MAX_FAILED_ATTEMPTS):
        service.authenticate("u1", "wrong")
    # ⚑ The password is now CORRECT and still refused — and refused IDENTICALLY, because
    # "you are locked out" is itself an enumeration oracle (WIRE-1 §3, uniform 401).
    assert service.authenticate("u1", _PASSWORD) is None


# --- (5)-(7) LOCKOUT: trip, reset, expiry ---------------------------------------------

def test_consecutive_failures_trip_the_lock_at_the_declared_threshold():
    service, _, credentials, _ = _service()
    for _ in range(MAX_FAILED_ATTEMPTS - 1):
        service.authenticate("u1", "wrong")
    assert credentials.get("u1").locked_until is None, "locked one attempt too early"
    service.authenticate("u1", "wrong")
    assert credentials.get("u1").locked_until is not None, "did not lock at the threshold"


def test_a_successful_login_resets_the_failure_counter():
    service, _, credentials, _ = _service()
    for _ in range(MAX_FAILED_ATTEMPTS - 1):
        service.authenticate("u1", "wrong")
    assert service.authenticate("u1", _PASSWORD) is not None
    assert credentials.get("u1").failed_attempts == 0


def test_the_lock_releases_after_the_lockout_window():
    service, clock, _, _ = _service()
    for _ in range(MAX_FAILED_ATTEMPTS):
        service.authenticate("u1", "wrong")
    assert service.authenticate("u1", _PASSWORD) is None
    clock.advance(LOCKOUT_DURATION + timedelta(seconds=1))
    assert service.authenticate("u1", _PASSWORD) is not None, "lock never released"


# --- (8)-(11) SESSIONS: issue, resolve, expire, revoke ---------------------------------

def test_authentication_issues_a_session_that_resolves_to_its_user():
    service, _, _, _ = _service()
    token = service.authenticate("u1", _PASSWORD)
    assert token is not None
    assert service.resolve(token) == "u1"


def test_an_unknown_token_resolves_to_none():
    service, _, _, _ = _service()
    assert service.resolve("never-issued") is None


def test_a_session_stops_resolving_once_its_absolute_ttl_passes():
    service, clock, _, _ = _service()
    token = service.authenticate("u1", _PASSWORD)
    clock.advance(SESSION_TTL - timedelta(seconds=1))
    assert service.resolve(token) == "u1"
    clock.advance(timedelta(seconds=2))
    assert service.resolve(token) is None, "expiry is not enforced server-side"


def test_logout_revokes_the_session_immediately_not_at_expiry():
    # ⚑ The property that justifies an 8h TTL (Q5a): revocation is server-side, so a
    # logout or role change takes effect on the NEXT request, not when the token expires.
    service, _, _, _ = _service()
    token = service.authenticate("u1", _PASSWORD)
    service.logout(token)
    assert service.resolve(token) is None


# --- (12) THE RAW TOKEN IS NEVER PERSISTED --------------------------------------------

def test_the_raw_token_is_never_stored_only_its_hash():
    # ⚑ A database read must yield NO usable session credential.
    service, _, _, sessions = _service()
    token = service.authenticate("u1", _PASSWORD)
    stored_keys = list(sessions.all_ids())
    assert stored_keys, "no session was persisted at all"
    assert token not in stored_keys, "the RAW token was persisted — a DB read would yield a live credential"
    assert all(len(k) == 64 and all(c in "0123456789abcdef" for c in k) for k in stored_keys), (
        "session ids must be sha256 hex digests of the raw token"
    )
