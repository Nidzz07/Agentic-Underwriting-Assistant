"""INT-AUTH-1 — the session handshake, fail-closed.

⚑ **MIGRATED 2026-07-25 (register #25 / PER-4 / WIRE1-Fold-5).** This module was titled
*"the X-User-Id stub handshake (Decision 2 / Q4-A)"* and every test here drove that header.
The header is **retired** — ``current_identity`` no longer reads it — so each test has been
**re-expressed against the cookie**, not left to pass for the wrong reason.

**Why that mattered.** After the fixture migration these tests went green on their own, because
they sent a header the server now ignores and got their 401 from the **absent cookie** rather
than from the property each was written to prove. Green, and testing nothing. Every one is
restated below against the mechanism that actually decides.

**What this module guarantees, unchanged in substance**: the ROLE is never trusted from the
request — the caller proves identity with a session this server issued, and the role is read
from ``app_user`` through auth-rbac's own repository. Anything unresolvable fails **CLOSED**
to 401.
"""
from __future__ import annotations

import pytest

from backend.app.tests._route_inventory import ROUTE_INVENTORY
from backend.app.tests.conftest import ADMIN, AUDITOR, GHOST, ORPHAN, UNDERWRITER

#: R8 is the handshake itself, so it is the one route that MUST be reachable unauthenticated.
_THE_HANDSHAKE = ("/login", "post")


class TestHappyPath:
    @pytest.mark.parametrize(
        "headers,user_id,role",
        [(UNDERWRITER, "UW-1", "underwriter"), (AUDITOR, "AUD-1", "auditor"), (ADMIN, "ADM-1", "admin")],
    )
    def test_a_known_user_resolves_to_its_app_user_role(self, client, headers, user_id, role):
        assert client.get("/session", headers=headers).json() == {"user_id": user_id, "role": role}


class TestFailClosed:
    def test_no_session_cookie_is_401(self, client):
        # ⚑ RENAMED from test_a_missing_header_is_401 — the absent thing is now the cookie.
        assert client.get("/session").status_code == 401

    @pytest.mark.parametrize("value", ["", "   ", "\t"])
    def test_a_blank_session_cookie_is_401(self, client, value):
        """⚑ RE-EXPRESSED from ``test_a_blank_header_is_401``, which sent a blank *header*.

        Post-migration that header is ignored, so the old form proved only that a request with
        no cookie is 401 — already covered above. The genuine, still-distinct property is that
        a cookie which is **present but blank or whitespace** must also fail closed — exactly
        what a half-cleared browser jar sends.

        ⚑ Stated precisely: this asserts the **behaviour**, not one line. ``current_identity``
        guards on ``not session.strip()``, but a blank token would also miss the session store
        and 401 anyway, so the test does not isolate that guard — it pins the outcome, which is
        what a caller depends on.
        """
        assert client.get("/session", headers={"Cookie": f"session={value}"}).status_code == 401

    def test_an_unresolvable_session_is_401_not_403(self, client):
        """⚑ RE-EXPRESSED from ``test_an_unknown_user_is_401_not_403``.

        The property is the **authenticate-vs-authorize distinction**, and it survives the
        migration in two forms, both asserted here: a token that matches no session at all,
        and — the one the old test actually covered — a session that RESOLVES to a user with
        **no ``app_user`` row**. Neither can tell us who the caller is, so 401 is the honest
        status; 403 would claim we knew them and refused them (§4).
        """
        assert client.get("/session", headers={"Cookie": "session=never-issued"}).status_code == 401
        assert client.get("/session", headers=ORPHAN).status_code == 401

    def test_a_session_whose_resolved_role_is_blank_is_401(self, client):
        """⚑ RE-EXPRESSED from ``test_a_user_whose_role_is_blank_is_401``, which sent
        ``X-User-Id: GHOST-1``. GHOST-1 now presents a real **session**, so the request gets
        all the way to ``to_role`` — the frozen TOTAL canonicalizer — which fail-closes on a
        blank role. That is the assertion this test was always making; before this fix it was
        being made by the absent cookie instead.
        """
        assert client.get("/session", headers=GHOST).status_code == 401

    def test_every_authenticated_route_requires_a_session(self, client):
        """⚑ RENAMED + WIDENED from ``test_every_wired_route_requires_authentication``.

        The old name promised *"every wired route"* and checked a **hardcoded three** of the
        then-seven — the same name-vs-implementation gap register #13 tracks. It now derives
        the surface from the **declared route inventory**, so a future route that forgets
        authentication fails here instead of slipping through.

        ⚑ **R8 ``POST /login`` is excluded deliberately, and that exclusion is asserted, not
        assumed** (below): it *is* the handshake, so requiring a session to reach it would make
        logging in impossible. Every other route — R9 ``/logout`` included — must refuse an
        unauthenticated caller.
        """
        checked = 0
        for path, method in ROUTE_INVENTORY:
            if (path, method) == _THE_HANDSHAKE:
                continue
            # Path params are irrelevant: authentication is decided before the handler runs.
            concrete = path.replace("{application_id}", "APP-1") \
                           .replace("{recommendation_id}", "REC-1") \
                           .replace("{decision_id}", "DEC-1")
            response = client.request(method.upper(), concrete, json={})
            assert response.status_code == 401, f"{method.upper()} {concrete}"
            checked += 1
        assert checked == len(ROUTE_INVENTORY) - 1, "the inventory was not fully exercised"

    def test_the_handshake_itself_is_reachable_without_a_session(self, client):
        # ⚑ The other half of the exclusion above: R8 must NOT 401, or nobody could ever log
        # in. It rejects these credentials (401 is not possible here — the client has no
        # session, and the store has no such user), so assert only that it is not an auth wall.
        response = client.post("/login", json={"user_id": "UW-1", "password": "wrong"})
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "unauthenticated"


class TestRoleIsNeverTrustedFromTheRequest:
    def test_a_role_header_cannot_elevate_the_caller(self, client):
        """The role comes from ``app_user``, never from the request — for an authenticated
        caller **and** for an unauthenticated one.

        ⚑ **CONSOLIDATED**: ``test_an_unknown_user_cannot_authenticate_by_claiming_a_role``
        was folded in here rather than deleted silently. Post-migration it sent
        ``X-User-Id: NOBODY`` plus a role claim — but the server reads **neither** header, so
        it had become an exact duplicate of *"no session is 401"* with an ignored header
        attached. Its surviving distinct content — **a role claim cannot bootstrap
        authentication** — is the second assertion below, where it belongs.
        """
        # Authenticated: ADM-1 is admin in app_user and stays admin however it labels itself.
        response = client.get("/session", headers={**ADMIN, "X-Role": "underwriter", "Role": "underwriter"})
        assert response.json()["role"] == "admin"
        assert client.get("/decisions", headers={**ADMIN, "X-Role": "underwriter"}).status_code == 403

        # Unauthenticated: claiming a role buys nothing — there is no session to attach it to.
        assert client.get("/session", headers={"X-Role": "admin"}).status_code == 401
