"""INT-ERR-1 — the WIRE-1 §4 envelope on EVERY non-2xx + the frozen status->code table.

§4 binds: one error body shape for every non-2xx, and "no secret VALUE ever appears in
message/detail".
"""
from __future__ import annotations

import pytest

from backend.app.errors import STATUS_TABLE
from backend.app.tests.conftest import ADMIN, AUDITOR, UNDERWRITER


def assert_is_wire1_envelope(body):
    """The §4 shape, exactly: {error:{code,message,detail}} — detail always an object."""
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message", "detail"}
    assert isinstance(body["error"]["code"], str) and body["error"]["code"]
    assert isinstance(body["error"]["message"], str) and body["error"]["message"]
    assert isinstance(body["error"]["detail"], dict)


class TestEnvelopeOnEveryNonTwoXX:
    @pytest.mark.parametrize(
        "method,path,headers,status,code",
        [
            ("get", "/session", {}, 401, "unauthenticated"),                 # missing header
            ("get", "/decisions", {}, 401, "unauthenticated"),
            ("get", "/decisions/DEC-1", {}, 401, "unauthenticated"),
            ("get", "/decisions", ADMIN, 403, "forbidden"),                  # Q1-B: admin denied
            ("get", "/decisions/NOPE", UNDERWRITER, 404, "not_found"),       # R7 miss
            # ⚑ REVISED BY THE SCOPE B WIRING PASS. These two rows previously asserted the R2/R5
            # `501 not_implemented` markers. R2-R5 are now WIRED, so the markers are gone and the
            # rows are replaced by the REAL frozen statuses those routes can now emit — which is
            # strictly more coverage: 501 exercised one additive extension, whereas these
            # exercise three of the seven FROZEN §4 statuses on live routes.
            ("get", "/applications/NOPE", UNDERWRITER, 404, "not_found"),           # R3 miss
            ("post", "/recommendations/NOPE/commit", UNDERWRITER, 404, "not_found"),  # R5 miss
            ("post", "/recommendations/REC-1/commit", AUDITOR, 403, "forbidden"),   # R5 RBAC_COMMIT
        ],
    )
    def test_status_and_code_match_the_frozen_table(self, wired_client, method, path, headers, status, code):
        kwargs = {"json": {"action": "approve"}} if method == "post" else {}
        response = getattr(wired_client, method)(path, headers=headers, **kwargs)
        assert response.status_code == status
        assert_is_wire1_envelope(response.json())
        assert response.json()["error"]["code"] == code
        # the code emitted is the one the frozen table binds to that status
        assert STATUS_TABLE[status] == code

    def test_an_unknown_path_still_returns_the_envelope_never_a_framework_body(self, client):
        response = client.get("/no-such-route", headers=UNDERWRITER)
        assert response.status_code == 404
        assert_is_wire1_envelope(response.json())
        assert response.json()["error"]["code"] == "not_found"

    def test_a_malformed_query_is_400_invalid_request_not_the_frameworks_422(self, client):
        # §4 reserves 422 for "well-formed but unprocessable"; a non-integer page is malformed.
        response = client.get("/decisions?page=abc", headers=UNDERWRITER)
        assert response.status_code == 400
        assert_is_wire1_envelope(response.json())
        assert response.json()["error"]["code"] == "invalid_request"

    def test_an_out_of_range_page_is_rejected_as_malformed_not_500(self, client):
        response = client.get("/decisions?page=0", headers=UNDERWRITER)
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "invalid_request"


class TestNoSecretValueLeaks:
    def test_error_bodies_never_echo_the_callers_input(self, client):
        # §4: no secret VALUE in message/detail. Messages here are static and caller-independent —
        # a requested id is never reflected back into the body.
        body = client.get("/decisions/SUPER-SECRET-ID", headers=UNDERWRITER).json()
        assert "SUPER-SECRET-ID" not in str(body)

    def test_a_malformed_query_value_is_not_echoed(self, client):
        body = client.get("/decisions?page=SECRET-VALUE", headers=UNDERWRITER).json()
        assert "SECRET-VALUE" not in str(body)

    def test_a_wired_read_route_leaks_no_application_id(self, wired_client):
        """⚑ REVISED BY THE SCOPE B WIRING PASS.

        Previously this asserted the 501 marker's ``detail`` carried only a route id
        (``{"route": "R3"}``). R3 is now WIRED, so there is no marker — and the §4 concern the
        assertion existed to protect is now **more** load-bearing, not less: a live route that
        actually looks an id up must still never reflect it back.
        """
        body = wired_client.get("/applications/APP-SECRET", headers=UNDERWRITER).json()
        assert body["error"]["detail"] == {}
        assert "APP-SECRET" not in str(body)

    def test_a_wired_commit_route_leaks_no_recommendation_id(self, wired_client):
        body = wired_client.post(
            "/recommendations/REC-SECRET/commit",
            json={"action": "approve"},
            headers=UNDERWRITER,
        ).json()
        assert "REC-SECRET" not in str(body)


class TestStatusTableIntegrity:
    def test_the_table_holds_every_frozen_status_plus_the_one_additive_extension(self):
        # The seven FROZEN §4 statuses keep their exact meanings...
        for status, code in {
            400: "invalid_request", 401: "unauthenticated", 403: "forbidden",
            404: "not_found", 409: "commit_conflict", 422: "unprocessable",
            500: "internal_error",
        }.items():
            assert STATUS_TABLE[status] == code
        # ...and 501 is the ONE additive extension (Q2-A) — it replaces nothing.
        # ⚑ SCOPE B: the extension is now DECLARED BUT UNUSED — R2-R5 are wired, so no route
        # emits it any more (asserted in test_not_wired.py). The constant is deliberately KEPT
        # rather than deleted: it is the historical record of an additive extension that was
        # made, used, and retired, and removing it would erase that. Its disuse is the
        # assertion elsewhere; its existence is the record here.
        assert STATUS_TABLE[501] == "not_implemented"
        assert len(STATUS_TABLE) == 8
