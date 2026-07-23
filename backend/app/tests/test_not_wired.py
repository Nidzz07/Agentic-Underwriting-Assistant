"""INT-WIRED-1 — R2-R5 are LIVE, and the ``501`` marker is GONE.

⚑ **THIS FILE'S GUARANTEE INVERTED IN THE SCOPE B WIRING PASS. Surfaced, not silently patched.**

Scope A asserted the opposite of what is asserted here: *"all four return the explicit ``501``
marker, uniformly"*. R2-R5 are now real, so **every one of those assertions is false by design**.
Deleting the file would have silently dropped a target; leaving it would have asserted a
deployment state that no longer exists. It is therefore **REFRAMED** — and the reframing is a
genuine strengthening, not a formality:

  * **``not_implemented`` must no longer be emitted by ANY route.** Scope A's 501 was an ADDITIVE
    extension to WIRE-1 §4's frozen status table for a state that no longer exists. Asserting its
    ABSENCE is what stops a half-wired route from quietly regressing to a marker.
  * **404-vs-501 distinguishability becomes 404-vs-200**: an unknown application is now a REAL
    ``not_found``, not an unwired route. The original concern (a client's generic error path
    misreading "unwired" as "no such record") is retired by the wiring itself.
  * **⚑ Role-independence becomes MEANINGFUL rather than trivial.** Scope A asserted all roles
    got the same 501 — true of any unwired route, and therefore nearly vacuous. It now asserts
    that R2/R3/R4 are genuinely **any-authenticated** per WIRE-1 §3, which is a real
    authorization claim: it proves the **Q1-B divergence was NOT propagated** onto the new routes
    (they use ``current_identity``, not R6/R7's ``READ_AUDIT`` guard, so ``admin`` is NOT
    excluded here).
"""
from __future__ import annotations

import pytest

from backend.app.tests.conftest import ADMIN, AUDITOR, UNDERWRITER

WIRED_READS = [
    ("get", "/applications", "R2"),
    ("get", "/applications/APP-1", "R3"),
    ("get", "/applications/APP-1/memo", "R4"),
]


class TestTheMarkerIsGone:
    @pytest.mark.parametrize("method,path,route", WIRED_READS)
    def test_no_read_route_returns_the_not_implemented_marker(self, wired_client, method, path, route):
        response = getattr(wired_client, method)(path, headers=UNDERWRITER)
        assert response.status_code == 200, route

    def test_r5_no_longer_returns_the_marker(self, wired_client):
        response = wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "approve"}, headers=UNDERWRITER
        )
        assert response.status_code != 501

    def test_not_implemented_is_emitted_by_no_route_at_all(self, wired_client):
        """⚑ The load-bearing inversion: the additive 501 extension is now unused.

        Checked across every contract route AND an unknown path, so a single half-wired handler
        cannot quietly reintroduce the marker.
        """
        probes = [
            ("get", "/session"), ("get", "/applications"), ("get", "/applications/APP-1"),
            ("get", "/applications/APP-1/memo"), ("get", "/decisions"),
            ("get", "/decisions/DEC-1"), ("get", "/no-such-route"),
        ]
        for method, path in probes:
            response = getattr(wired_client, method)(path, headers=UNDERWRITER)
            assert response.status_code != 501, path
            if response.status_code >= 400:
                assert response.json()["error"]["code"] != "not_implemented", path


class TestMissingRecordsAreRealNotFounds:
    def test_an_unknown_application_is_a_genuine_404(self, wired_client):
        """Previously unreachable: R3 returned 501 for every id. Now it discriminates."""
        response = wired_client.get("/applications/NOPE", headers=UNDERWRITER)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    def test_a_known_application_and_an_unknown_one_differ(self, wired_client):
        known = wired_client.get("/applications/APP-1", headers=UNDERWRITER)
        unknown = wired_client.get("/applications/NOPE", headers=UNDERWRITER)
        assert known.status_code == 200
        assert unknown.status_code == 404

    def test_the_404_echoes_no_caller_supplied_id(self, wired_client):
        """WIRE-1 §4: no caller value appears in message/detail."""
        body = wired_client.get("/applications/SECRET-ID-42", headers=UNDERWRITER).json()
        assert "SECRET-ID-42" not in str(body)


class TestTheReadRoutesAreAnyAuthenticated:
    """⚑ A REAL authorization claim now — see this module's docstring."""

    @pytest.mark.parametrize("headers", [UNDERWRITER, AUDITOR, ADMIN])
    @pytest.mark.parametrize("method,path,route", WIRED_READS)
    def test_every_authenticated_role_including_admin_succeeds(
        self, wired_client, headers, method, path, route
    ):
        response = getattr(wired_client, method)(path, headers=headers)
        assert response.status_code == 200, (route, headers)

    def test_admin_is_not_excluded_from_r2_unlike_r6(self, wired_client):
        """⚑ The Q1-B divergence is CONTAINED, not spread.

        R6/R7 enforce ``READ_AUDIT``, which excludes ``admin`` — the recorded, still-unresolved
        divergence with WIRE-1 §3. R2 is marked "any role" and uses ``current_identity``, so
        ``admin`` passes. This asserts the two behave DIFFERENTLY, on purpose: the new routes did
        not inherit a known defect.
        """
        assert wired_client.get("/applications", headers=ADMIN).status_code == 200
        assert wired_client.get("/decisions", headers=ADMIN).status_code == 403

    @pytest.mark.parametrize("method,path,route", WIRED_READS)
    def test_an_unauthenticated_caller_is_still_401(self, wired_client, method, path, route):
        assert getattr(wired_client, method)(path).status_code == 401
