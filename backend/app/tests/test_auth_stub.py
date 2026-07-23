"""INT-AUTH-1 — the X-User-Id stub handshake (Decision 2 / Q4-A), fail-closed.

The stub stands in for WIRE-1 §6/A6's "abstract seam, deferred". What it must guarantee:
the ROLE is never trusted from the request — only the user id is, and the role is read from
``app_user`` through auth-rbac's own repository. Anything unresolvable fails CLOSED to 401.
"""
from __future__ import annotations

import pytest

from backend.app.tests.conftest import ADMIN, AUDITOR, UNDERWRITER


class TestHappyPath:
    @pytest.mark.parametrize(
        "headers,user_id,role",
        [(UNDERWRITER, "UW-1", "underwriter"), (AUDITOR, "AUD-1", "auditor"), (ADMIN, "ADM-1", "admin")],
    )
    def test_a_known_user_resolves_to_its_app_user_role(self, client, headers, user_id, role):
        assert client.get("/session", headers=headers).json() == {"user_id": user_id, "role": role}


class TestFailClosed:
    def test_a_missing_header_is_401(self, client):
        assert client.get("/session").status_code == 401

    @pytest.mark.parametrize("value", ["", "   ", "\t"])
    def test_a_blank_header_is_401(self, client, value):
        assert client.get("/session", headers={"X-User-Id": value}).status_code == 401

    def test_an_unknown_user_is_401_not_403(self, client):
        # get_role -> None (no row). This is a failure to AUTHENTICATE, not to authorize:
        # we cannot know who the caller is, so 401 is the honest status (§4).
        assert client.get("/session", headers={"X-User-Id": "NOBODY"}).status_code == 401

    def test_a_user_whose_role_is_blank_is_401(self, client):
        # to_role is the frozen TOTAL canonicalizer and fail-closes on blank/non-canonical.
        assert client.get("/session", headers={"X-User-Id": "GHOST-1"}).status_code == 401

    def test_every_wired_route_requires_authentication(self, client):
        for path in ("/session", "/decisions", "/decisions/DEC-1"):
            assert client.get(path).status_code == 401, path


class TestRoleIsNeverTrustedFromTheRequest:
    def test_a_role_header_cannot_elevate_the_caller(self, client):
        # Even if a caller asserts a role, the role comes from app_user. ADM-1 is admin there,
        # so it stays admin (and READ_AUDIT still denies it) regardless of what it claims.
        response = client.get("/session", headers={**ADMIN, "X-Role": "underwriter", "Role": "underwriter"})
        assert response.json()["role"] == "admin"
        assert client.get("/decisions", headers={**ADMIN, "X-Role": "underwriter"}).status_code == 403

    def test_an_unknown_user_cannot_authenticate_by_claiming_a_role(self, client):
        assert client.get("/session", headers={"X-User-Id": "NOBODY", "X-Role": "admin"}).status_code == 401
