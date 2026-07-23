"""INT-WIRE-1 (pending half) — R2/R3/R4/R5 against the CONTRACT'S TEXT.

The sibling of ``test_wire1_shapes.py``, which does this for R1/R6/R7. Every assertion here is
read off WIRE-1 §3/§4/§5 rather than off the implementation: exact field sets, the enum wire
values BY VALUE and never re-cased, the ``status`` discriminator's two branches, and the frozen
error mapping.
"""
from __future__ import annotations

import pytest

from backend.app.tests.conftest import ADMIN, AUDITOR, UNDERWRITER


class TestR2ApplicationSummary:
    def test_the_list_wrapper_shape_is_exactly_the_contract(self, wired_client):
        body = wired_client.get("/applications", headers=UNDERWRITER).json()
        assert set(body) == {"items", "page"}
        assert set(body["page"]) == {"page", "size", "total"}

    def test_each_item_has_exactly_the_four_contract_fields(self, wired_client):
        for item in wired_client.get("/applications", headers=UNDERWRITER).json()["items"]:
            assert set(item) == {
                "application_id", "recommendation_id", "recommendation", "confidence"
            }

    def test_a_drafted_case_carries_its_recommendation_by_value_never_recased(self, wired_client):
        items = {i["application_id"]: i for i in
                 wired_client.get("/applications", headers=UNDERWRITER).json()["items"]}
        drafted = items["APP-1"]
        assert drafted["recommendation_id"] == "REC-1"
        # WIRE-1 §1: UPPERCASE Recommendation, Title-case Confidence — emitted verbatim.
        assert drafted["recommendation"] == "APPROVE"
        assert drafted["confidence"] == "High"

    def test_an_undrafted_case_nulls_all_three_recommendation_fields(self, wired_client):
        """§5: *null until a recommendation is drafted*."""
        items = {i["application_id"]: i for i in
                 wired_client.get("/applications", headers=UNDERWRITER).json()["items"]}
        undrafted = items["APP-2"]
        assert undrafted["recommendation_id"] is None
        assert undrafted["recommendation"] is None
        assert undrafted["confidence"] is None

    def test_total_is_the_full_count_not_the_page_length(self, wired_client):
        body = wired_client.get("/applications?page=1&size=1", headers=UNDERWRITER).json()
        assert len(body["items"]) == 1
        assert body["page"]["total"] == 2

    def test_a_page_past_the_end_is_empty_not_an_error(self, wired_client):
        body = wired_client.get("/applications?page=99&size=20", headers=UNDERWRITER).json()
        assert body["items"] == []
        assert body["page"]["total"] == 2

    def test_an_empty_store_yields_an_empty_page_not_a_404(self, empty_case_client):
        response = empty_case_client.get("/applications", headers=UNDERWRITER)
        assert response.status_code == 200
        assert response.json() == {"items": [], "page": {"page": 1, "size": 20, "total": 0}}

    def test_pagination_is_1_based_and_rejects_page_zero(self, wired_client):
        assert wired_client.get("/applications?page=0", headers=UNDERWRITER).status_code == 400

    def test_a_malformed_page_is_400_not_the_frameworks_422(self, wired_client):
        response = wired_client.get("/applications?page=abc", headers=UNDERWRITER)
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "invalid_request"

    def test_the_order_is_the_stores_own_asserted_honestly(self, wired_client):
        """⚑ NOT a designed guarantee — the observed store order (the Q3-A precedent for R6).

        No frozen artifact pins R2's order. This records what the store actually returns
        (``ORDER BY application_id``) so the behaviour is documented rather than assumed, and a
        change to it shows up as a visible test failure instead of a silent client surprise.
        """
        ids = [i["application_id"] for i in
               wired_client.get("/applications", headers=UNDERWRITER).json()["items"]]
        assert ids == ["APP-1", "APP-2"]
        assert ids == sorted(ids), "application_id order — not chronological, not priority"


class TestR3ApplicantProfile:
    def test_it_returns_intakes_profile_shape_verbatim(self, wired_client):
        body = wired_client.get("/applications/APP-1", headers=UNDERWRITER).json()
        # §5: "intake.schema.ApplicantProfile (verbatim; intake's contract governs)"
        for field in ("application_id", "date_of_birth", "verifiable_income_annual",
                      "requested_cover_amount", "demographics", "documents"):
            assert field in body

    def test_it_is_a_bare_resource_body_with_no_envelope(self, wired_client):
        body = wired_client.get("/applications/APP-1", headers=UNDERWRITER).json()
        assert "error" not in body

    def test_an_unknown_application_is_404_not_found(self, wired_client):
        response = wired_client.get("/applications/NOPE", headers=UNDERWRITER)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    def test_the_profile_survives_the_canon_ser_round_trip(self, wired_client):
        """The stored bytes rehydrate to the same values the case was built with."""
        body = wired_client.get("/applications/APP-1", headers=UNDERWRITER).json()
        assert body["application_id"] == "APP-1"


class TestR4MemoView:
    def test_the_shape_is_exactly_the_seven_contract_fields(self, wired_client):
        body = wired_client.get("/applications/APP-1/memo", headers=UNDERWRITER).json()
        assert set(body) == {
            "application_id", "recommendation_id", "status", "profile", "report", "memo", "outlier"
        }

    def test_a_drafted_case_is_ready_with_every_payload_present(self, wired_client):
        body = wired_client.get("/applications/APP-1/memo", headers=UNDERWRITER).json()
        assert body["status"] == "ready"
        assert body["recommendation_id"] == "REC-1"
        assert body["profile"] is not None
        assert body["report"] is not None
        assert body["memo"] is not None

    def test_the_ready_memo_rehydrates_with_its_hash_and_citations_intact(self, wired_client):
        """⚑ Exercises U24's third-reopening ``MemoCanonAdapter`` end-to-end over the wire."""
        memo = wired_client.get("/applications/APP-1/memo", headers=UNDERWRITER).json()["memo"]
        assert memo["memo_hash"] == "memo-hash-1"
        assert memo["cited_rule_ids"] == ["DTI-1"]
        assert memo["recommendation"] == "APPROVE"      # by value, never re-cased
        assert memo["confidence"] == "High"

    def test_an_undrafted_case_is_pending_with_report_and_memo_null(self, wired_client):
        body = wired_client.get("/applications/APP-2/memo", headers=UNDERWRITER).json()
        assert body["status"] == "pending"
        assert body["recommendation_id"] is None
        assert body["report"] is None
        assert body["memo"] is None

    def test_a_pending_view_still_carries_the_profile(self, wired_client):
        """§5 explicitly permits it, and U24's eager transaction always populates it (Q5a)."""
        body = wired_client.get("/applications/APP-2/memo", headers=UNDERWRITER).json()
        assert body["profile"] is not None

    def test_outlier_is_null_even_on_a_ready_view(self, wired_client):
        """⚑ WIRE1-Fold-4 binds ``outlier: null`` in PHASE 1 even when ``ready``.

        U24 DOES persist real outlier data (``PendingRecommendation.outlier_canonical``), so this
        is the contract, not the data, deciding. Register #17 records the mismatch; emitting the
        data would amend WIRE-1, which this pass may not do.
        """
        for application_id in ("APP-1", "APP-2"):
            body = wired_client.get(f"/applications/{application_id}/memo", headers=UNDERWRITER).json()
            assert body["outlier"] is None

    def test_the_status_discriminator_only_ever_emits_two_values(self, wired_client):
        for application_id in ("APP-1", "APP-2"):
            body = wired_client.get(f"/applications/{application_id}/memo", headers=UNDERWRITER).json()
            assert body["status"] in {"ready", "pending"}

    def test_an_unknown_application_is_404(self, wired_client):
        assert wired_client.get("/applications/NOPE/memo", headers=UNDERWRITER).status_code == 404

    def test_repeated_reads_are_identical_and_mutate_nothing(self, wired_client):
        """⚑ BR-CASE-4 / TRIGGER-1 — R4 is a PURE GET. A drafting side effect would show here."""
        first = wired_client.get("/applications/APP-2/memo", headers=UNDERWRITER).json()
        second = wired_client.get("/applications/APP-2/memo", headers=UNDERWRITER).json()
        assert first == second
        assert second["status"] == "pending", "a read must never advance the case to drafted"


class TestR5Commit:
    def test_an_underwriter_can_approve_and_gets_the_committed_decision(self, wired_client):
        response = wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "approve"}, headers=UNDERWRITER
        )
        assert response.status_code == 200
        body = response.json()
        assert set(body) == {"recommendation_id", "underwriter_id", "action", "reason"}
        assert body["recommendation_id"] == "REC-1"
        assert body["underwriter_id"] == "UW-1"
        assert body["action"] == "approve"      # lowercase CommitAction, never the UPPERCASE
        assert body["reason"] is None

    def test_an_override_requires_a_reason_and_returns_it(self, wired_client):
        response = wired_client.post(
            "/recommendations/REC-1/commit",
            json={"action": "override", "reason": "Compensating assets verified."},
            headers=UNDERWRITER,
        )
        assert response.status_code == 200
        assert response.json()["action"] == "override"
        assert response.json()["reason"] == "Compensating assets verified."

    def test_a_blank_reason_override_is_409_commit_conflict(self, wired_client):
        """WIRE-1 §4 + the frozen BR-COMMIT-GATE. The GATE rejects this, not the route."""
        response = wired_client.post(
            "/recommendations/REC-1/commit",
            json={"action": "override", "reason": "   "},
            headers=UNDERWRITER,
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "commit_conflict"

    def test_a_missing_reason_override_is_409(self, wired_client):
        response = wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "override"}, headers=UNDERWRITER
        )
        assert response.status_code == 409

    def test_an_action_outside_the_enum_is_422_not_400(self, wired_client):
        """⚑ Q13-A: the explicit membership check yields the CONTRACT'S 422.

        A Pydantic ``Literal`` would have produced the global handler's 400 instead — the
        400-vs-422 fold this pass surfaced and resolved deliberately.
        """
        response = wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "reject"}, headers=UNDERWRITER
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "unprocessable"

    @pytest.mark.parametrize("headers", [AUDITOR, ADMIN])
    def test_a_non_underwriter_is_403(self, wired_client, headers):
        response = wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "approve"}, headers=headers
        )
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "forbidden"

    def test_an_unauthenticated_caller_is_401(self, wired_client):
        response = wired_client.post("/recommendations/REC-1/commit", json={"action": "approve"})
        assert response.status_code == 401

    def test_an_unknown_recommendation_is_404(self, wired_client):
        response = wired_client.post(
            "/recommendations/NOPE/commit", json={"action": "approve"}, headers=UNDERWRITER
        )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    def test_the_underwriter_id_comes_from_the_session_not_the_body(self, wired_client):
        """⚑ AUTHZ-1 — a client cannot commit AS ANOTHER USER."""
        response = wired_client.post(
            "/recommendations/REC-1/commit",
            json={"action": "approve", "underwriter_id": "SOMEONE-ELSE"},
            headers=UNDERWRITER,
        )
        assert response.status_code == 200
        assert response.json()["underwriter_id"] == "UW-1"

    def test_a_successful_commit_writes_exactly_one_audit_record(self, wired_client, commit_repository):
        wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "approve"}, headers=UNDERWRITER
        )
        assert len(commit_repository.browse()) == 1

    def test_a_rejected_commit_writes_nothing(self, wired_client, commit_repository):
        """The gate runs BEFORE any assembly — a rejection leaves no partial record."""
        wired_client.post(
            "/recommendations/REC-1/commit",
            json={"action": "override", "reason": ""},
            headers=UNDERWRITER,
        )
        wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "approve"}, headers=AUDITOR
        )
        assert commit_repository.browse() == []

    def test_no_error_response_echoes_a_caller_supplied_value(self, wired_client):
        """WIRE-1 §4: no secret VALUE in message/detail."""
        body = wired_client.post(
            "/recommendations/SECRET-REC-9/commit", json={"action": "approve"}, headers=UNDERWRITER
        ).json()
        assert "SECRET-REC-9" not in str(body)


class TestTheFrozenServiceIsTheRealGateNotTheLayerGuard:
    """⚑ The load-bearing claim of the whole wiring pass, tested directly.

    ``require_commit`` is DEFENCE IN DEPTH (Q6a). If it were the only thing standing between a
    non-underwriter and a write, removing it would open a hole. These tests remove it and prove
    the FROZEN ``DecisionCommitService`` refuses anyway — which is what makes the layer guard
    genuinely optional rather than load-bearing.
    """

    @pytest.fixture
    def guard_disabled_client(self, audit_repository, case_store, commit_repository):
        """A client with the API-layer RBAC guard DELIBERATELY bypassed."""
        from datetime import datetime, timezone

        from fastapi.testclient import TestClient

        from backend.app.dependencies import (
            Identity,
            get_audit_service,
            get_case_store,
            get_commit_service,
            get_user_role_repository,
            require_commit,
        )
        from backend.app.main import create_app
        from backend.app.tests.conftest import USERS
        from backend.audit_store.audit_service import AuditService
        from backend.audit_store.commit_service import DecisionCommitService
        from backend.audit_store.seams import FixedClock, SequenceIdGenerator
        from backend.auth_rbac.authorizer import AuthRBAC
        from backend.auth_rbac.repository import InMemoryUserRoleRepository
        from backend.auth_rbac.roles import Role
        from backend.case_lifecycle.provider import PendingCommitContextProvider

        role_repository = InMemoryUserRoleRepository(dict(USERS))
        app = create_app()
        app.dependency_overrides[get_user_role_repository] = lambda: role_repository
        app.dependency_overrides[get_audit_service] = lambda: AuditService(audit_repository)
        app.dependency_overrides[get_case_store] = lambda: case_store
        # ⚑ the guard is neutered — an AUDITOR is waved through the API layer
        app.dependency_overrides[require_commit] = lambda: Identity(
            user_id="AUD-1", role=Role.AUDITOR
        )
        app.dependency_overrides[get_commit_service] = lambda: DecisionCommitService(
            repository=commit_repository,
            context_provider=PendingCommitContextProvider(case_store),
            authorizer=AuthRBAC(role_repository),
            id_generator=SequenceIdGenerator(),
            clock=FixedClock(datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)),
        )
        with TestClient(app) as test_client:
            yield test_client

    def test_the_service_still_refuses_when_the_layer_guard_is_bypassed(self, guard_disabled_client):
        """⚑ AUTHZ-1 — the frozen service's OWN re-check is the authority."""
        response = guard_disabled_client.post(
            "/recommendations/REC-1/commit", json={"action": "approve"}
        )
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "forbidden"

    def test_nothing_is_written_when_the_service_refuses(self, guard_disabled_client, commit_repository):
        guard_disabled_client.post("/recommendations/REC-1/commit", json={"action": "approve"})
        assert commit_repository.browse() == []


class TestAnUnevaluatedCaseDegradesGracefully:
    def test_a_case_without_rule_results_reports_pending_with_a_null_report(self, audit_repository):
        """⚑ ``rule_results_canonical`` is ``Optional`` on the frozen schema, so a row CAN exist
        without it (U24's eager transaction makes this rare, not impossible). R4 must not blow up.
        """
        from fastapi.testclient import TestClient

        from backend.app.dependencies import (
            get_audit_service,
            get_case_store,
            get_user_role_repository,
        )
        from backend.app.main import create_app
        from backend.app.tests.conftest import USERS
        from backend.app.tests.factories import InMemoryCaseStore, make_profile
        from backend.audit_store.audit_service import AuditService
        from backend.audit_store.canon_adapter import CanonSerAdapter
        from backend.auth_rbac.repository import InMemoryUserRoleRepository
        from backend.case_lifecycle.schemas import PendingApplication
        from backend.case_lifecycle.states import CaseState

        profile = make_profile(application_id="APP-BARE")
        bare = PendingApplication(
            application_id="APP-BARE",
            state=CaseState.SUBMITTED,
            profile_canonical=CanonSerAdapter.canonical_bytes(profile),
            profile_content_hash=CanonSerAdapter.content_hash(profile),
        )
        store = InMemoryCaseStore().seed(bare)

        app = create_app()
        app.dependency_overrides[get_user_role_repository] = lambda: InMemoryUserRoleRepository(dict(USERS))
        app.dependency_overrides[get_audit_service] = lambda: AuditService(audit_repository)
        app.dependency_overrides[get_case_store] = lambda: store
        with TestClient(app) as client:
            memo = client.get("/applications/APP-BARE/memo", headers=UNDERWRITER).json()
            listed = client.get("/applications", headers=UNDERWRITER).json()

        assert memo["status"] == "pending"
        assert memo["report"] is None
        assert memo["profile"] is not None
        # R2 must also survive a row with no report — all three fields null, no crash
        summary = listed["items"][0]
        assert summary["recommendation"] is None
        assert summary["confidence"] is None
