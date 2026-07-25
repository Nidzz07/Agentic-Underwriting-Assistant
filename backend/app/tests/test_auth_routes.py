"""R8/R9 — the real handshake replacing the `X-User-Id` stub (register #25, WIRE1-Fold-5).

What these must guarantee: the session arrives in a **hardened cookie**, identity is resolved
**from that cookie** rather than a forgeable header, **R1's shape is unchanged**, and the old
stub header is **no longer trusted at all**.

⚑ `SESSION_COOKIE_SECURE` is set explicitly in every test that depends on it — these live in
`backend/app/tests`, so the `authn` package's hermetic conftest does not apply here. Same
discipline `ALLOW_REAL_LLM_CALLS` uses.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.dependencies import (
    SESSION_COOKIE_NAME,
    get_auth_service,
    get_user_role_repository,
)
from backend.app.main import create_app
from backend.app.tests.conftest import USERS
from backend.authn.hashing import hash_password
from backend.authn.service import AuthenticationService
from backend.authn.store import InMemoryCredentialStore, InMemorySessionStore
from backend.auth_rbac.repository import InMemoryUserRoleRepository

_PASSWORD = "correct horse battery staple"


@pytest.fixture
def auth_client(monkeypatch):
    """The REAL app with in-memory credential/session stores and a real AuthenticationService."""
    monkeypatch.delenv("SESSION_COOKIE_SECURE", raising=False)
    credentials = InMemoryCredentialStore()
    from datetime import datetime, timezone
    credentials.set_password("UW-1", hash_password(_PASSWORD), datetime.now(timezone.utc))
    service = AuthenticationService(credentials=credentials, sessions=InMemorySessionStore())

    app = create_app()
    app.dependency_overrides[get_user_role_repository] = lambda: InMemoryUserRoleRepository(dict(USERS))
    app.dependency_overrides[get_auth_service] = lambda: service
    with TestClient(app) as client:
        yield client


def _login(client, user_id="UW-1", password=_PASSWORD):
    return client.post("/login", json={"user_id": user_id, "password": password})


class TestTheCookieIsHardened:
    def test_a_session_cookie_is_httponly_on_success_and_absent_on_failure(self, auth_client):
        # ⚑ HttpOnly is what keeps a session token out of reach of any XSS on the page.
        assert "httponly" in _login(auth_client).headers["set-cookie"].lower()
        # ⚑ ...and a REJECTED login must emit no cookie at all — not an empty or invalid one.
        rejected = _login(auth_client, password="wrong")
        assert rejected.status_code == 401
        assert "set-cookie" not in {k.lower() for k in rejected.headers}

    def test_the_cookie_is_secure_by_default_and_opts_out_only_on_an_exact_false(
        self, auth_client, monkeypatch
    ):
        # ⚑ FAIL-SAFE DEFAULT (Q4a): absent, misspelt, or any value other than the exact
        # literal "false" must yield Secure. A forgotten env var must never silently
        # downgrade a production cookie. Mirrors ALLOW_REAL_LLM_CALLS's exact-match rule.
        assert "secure" in _login(auth_client).headers["set-cookie"].lower()
        for not_false in ("FALSE", "False", "0", "no", "", " false"):
            monkeypatch.setenv("SESSION_COOKIE_SECURE", not_false)
            assert "secure" in _login(auth_client).headers["set-cookie"].lower(), not_false
        monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
        assert "secure" not in _login(auth_client).headers["set-cookie"].lower()

    def test_the_cookie_is_samesite_lax(self, auth_client):
        assert "samesite=lax" in _login(auth_client).headers["set-cookie"].lower()


class TestIdentityComesFromTheSession:
    """⚑ These set ``SESSION_COOKIE_SECURE=false`` deliberately.

    The fail-safe default issues a **Secure** cookie, and a Secure cookie is correctly NOT
    retained by any client over plain http — including ``TestClient``, which speaks
    ``http://testserver``. That is the flag doing its job, and it is exactly why local dev
    must opt out. Setting it here is the same explicit opt-in a developer makes, not a
    weakening of the test.
    """

    def test_a_valid_session_authenticates_the_caller(self, auth_client, monkeypatch):
        monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
        assert _login(auth_client).status_code == 204
        assert auth_client.get("/session").status_code == 200

    def test_an_unknown_session_and_a_logged_out_session_are_both_401(self, auth_client, monkeypatch):
        monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
        auth_client.cookies.set(SESSION_COOKIE_NAME, "never-issued")
        assert auth_client.get("/session").status_code == 401
        auth_client.cookies.clear()

        assert _login(auth_client).status_code == 204
        assert auth_client.get("/session").status_code == 200
        # ⚑ Revocation is server-side, so logout takes effect on the NEXT request — not at
        # token expiry. That property is what makes the 8h TTL acceptable (Q5a).
        assert auth_client.post("/logout").status_code == 204
        assert auth_client.get("/session").status_code == 401


class TestTheContractAndTheOldStub:
    def test_r1_response_shape_is_byte_unchanged(self, auth_client, monkeypatch):
        # ⚑ Q6(a) / WIRE-1 §6: R1 still returns exactly {user_id, role}, lowercase, no
        # re-case and no new field — so no frozen UI unit needs any change.
        monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
        _login(auth_client)
        assert auth_client.get("/session").json() == {"user_id": "UW-1", "role": "underwriter"}

    def test_the_x_user_id_header_is_no_longer_trusted(self, auth_client):
        # ⚑ THE POINT OF REGISTER #25. Before this pass, this header WAS authentication:
        # any caller who knew a user_id was that user. It must now be inert.
        assert auth_client.get("/session", headers={"X-User-Id": "UW-1"}).status_code == 401
        assert auth_client.get("/decisions", headers={"X-User-Id": "AUD-1"}).status_code == 401
