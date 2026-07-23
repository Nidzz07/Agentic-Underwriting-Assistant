"""Register #19 — R5's two-step commit claim, at the route. `COMMITTED-TRANSITION-NEVER-PERFORMED`.

⚑ **What this file proves**: R5 takes the claim **before** calling the frozen service, maps the
three claim outcomes to the three WIRE-1 statuses, finalizes **after** a successful commit, and
**releases the claim on every rejection** so an ordinary failure never strands a case.

⛔ **What it does NOT prove**: the concurrency guarantee. The store fake here is single-threaded.
The compare-and-swap that actually eliminates duplicate ``AuditRecord``s is proven against real
Postgres in ``case_lifecycle/tests/test_claim_integration.py`` (CLAIM-CONCURRENT-1).

⚑ The frozen ``DecisionCommitService`` is REAL in every test below — the CON-BR4 gate and the
independent AUTHZ-1 re-check genuinely run, unmodified. R5 re-implements neither.
"""
from __future__ import annotations

from backend.case_lifecycle.states import CaseState

UNDERWRITER = {"X-User-Id": "UW-1"}
AUDITOR = {"X-User-Id": "AUD-1"}


def _state(case_store, application_id: str = "APP-1") -> CaseState:
    return case_store.get_application(application_id).state


class TestTheClaimIsTakenAndFinalized:
    def test_a_successful_commit_leaves_the_case_committed(self, wired_client, case_store):
        """⚑ The defect register #19 named: nothing performed ``drafted -> committed``."""
        assert _state(case_store) is CaseState.DRAFTED
        response = wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "approve"}, headers=UNDERWRITER
        )
        assert response.status_code == 200
        assert _state(case_store) is CaseState.COMMITTED

    def test_a_second_commit_of_the_same_recommendation_is_409(self, wired_client, case_store):
        """⚑ WIRE-1 §4's already-committed 409 — UNENFORCED before this fix."""
        first = wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "approve"}, headers=UNDERWRITER
        )
        assert first.status_code == 200

        second = wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "approve"}, headers=UNDERWRITER
        )
        assert second.status_code == 409
        assert second.json()["error"]["code"] == "commit_conflict"

    def test_a_second_commit_writes_no_duplicate_audit_record(
        self, wired_client, commit_repository
    ):
        """⚑ **THE DEFECT ITSELF.** Before this fix, the second call wrote a SECOND record."""
        for _ in range(3):
            wired_client.post(
                "/recommendations/REC-1/commit", json={"action": "approve"}, headers=UNDERWRITER
            )
        assert len(commit_repository.browse()) == 1

    def test_an_unknown_recommendation_is_still_404_not_409(self, wired_client):
        """⚑ The 3-valued result exists precisely so this does NOT regress to a 409."""
        response = wired_client.post(
            "/recommendations/NO-SUCH-REC/commit", json={"action": "approve"}, headers=UNDERWRITER
        )
        assert response.status_code == 404

    def test_a_case_that_is_not_drafted_cannot_be_committed(self, wired_client, case_store):
        """APP-2 is ``evaluated`` — it has no recommendation, so the claim reports NOT_FOUND."""
        response = wired_client.post(
            "/recommendations/REC-2/commit", json={"action": "approve"}, headers=UNDERWRITER
        )
        assert response.status_code == 404
        assert _state(case_store, "APP-2") is CaseState.EVALUATED


class TestTheClaimIsReleasedOnEveryRejection:
    """⚑ **A4 — the four tests that keep this fix from being worse than the defect.**

    The claim is taken BEFORE ``commit()``. Every way ``commit()`` can reject must therefore
    put the case back to ``drafted``, or a routine user error would strand it in ``committing``.
    """

    def test_a_blank_reason_override_releases_the_claim(self, wired_client, case_store):
        """⚑ Branch 1 — a routine user error the whole `ui-override-form` unit is built around."""
        response = wired_client.post(
            "/recommendations/REC-1/commit",
            json={"action": "override", "reason": "   "},
            headers=UNDERWRITER,
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "commit_conflict"
        assert _state(case_store) is CaseState.DRAFTED

    def test_a_released_case_can_be_committed_on_the_next_attempt(
        self, wired_client, case_store, commit_repository
    ):
        """⚑ The point of releasing: the underwriter fixes the reason and succeeds."""
        wired_client.post(
            "/recommendations/REC-1/commit",
            json={"action": "override", "reason": ""},
            headers=UNDERWRITER,
        )
        assert _state(case_store) is CaseState.DRAFTED

        retry = wired_client.post(
            "/recommendations/REC-1/commit",
            json={"action": "override", "reason": "Verified a second income source by phone."},
            headers=UNDERWRITER,
        )
        assert retry.status_code == 200
        assert _state(case_store) is CaseState.COMMITTED
        assert len(commit_repository.browse()) == 1

    def test_an_action_rejected_by_the_frozen_gate_releases_the_claim(
        self, wired_client, case_store, monkeypatch
    ):
        """⚑ Branch 2 — an action passing R5's wire-check but rejected by the frozen ``_gate``.

        The two checks are INDEPENDENT by design (defence in depth), so this branch must not be
        assumed unreachable. Forced here by widening the wire-check's accepted set only.
        """
        import backend.app.routes.not_wired as module

        monkeypatch.setattr(
            module, "_PERMITTED_COMMIT_ACTIONS", {"approve", "override", "abstain"}
        )
        response = wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "abstain"}, headers=UNDERWRITER
        )
        assert response.status_code == 409
        assert _state(case_store) is CaseState.DRAFTED

    def test_an_unauthorized_committer_releases_the_claim(self, wired_client, case_store):
        """⚑ Branch 3 — rejected by the frozen service's own AUTHZ-1 re-check."""
        response = wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "approve"}, headers=AUDITOR
        )
        assert response.status_code == 403
        assert _state(case_store) is CaseState.DRAFTED

    def test_a_failing_release_does_not_mask_the_original_rejection(
        self, wired_client, case_store
    ):
        """⚑ **The failure-tolerant-recovery test.**

        If recovery itself throws, the caller must still see the ORIGINAL 409 — not a 500. A
        stranded case is a reconciliation problem; a 500 in place of a 409 is a lie about what
        happened.
        """
        case_store.release_raises = True
        response = wired_client.post(
            "/recommendations/REC-1/commit",
            json={"action": "override", "reason": "  "},
            headers=UNDERWRITER,
        )
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "commit_conflict"
        # the claim could not be released, so the case is legitimately left mid-commit
        assert _state(case_store) is CaseState.COMMITTING


class TestTheProviderStillGuardsTheCommitPath:
    """⚑ The claim makes ``UnknownPendingRecommendation`` UNREACHABLE on the normal path.

    Once the claim answers ``NOT_FOUND`` for an unknown id, the frozen provider can no longer
    raise for one — the request never gets that far. The ``except`` branch is therefore
    **defence in depth**, kept because the provider is the frozen unit's own guarantee and the
    route must not assume its own pre-check is the only thing standing there (the same reasoning
    that keeps ``require_commit`` alongside AUTHZ-1).

    Forced here by pointing the commit service's provider at a DIFFERENT, empty store — the
    claim wins against the real store, then the provider finds nothing.
    """

    def test_a_provider_that_cannot_find_the_recommendation_is_404_and_releases(
        self, audit_repository, case_store, commit_repository
    ):
        from datetime import datetime, timezone

        from fastapi.testclient import TestClient

        from backend.app.dependencies import (
            get_audit_service,
            get_case_store,
            get_commit_service,
            get_user_role_repository,
        )
        from backend.app.main import create_app
        from backend.audit_store.audit_service import AuditService
        from backend.audit_store.commit_service import DecisionCommitService
        from backend.audit_store.seams import FixedClock, SequenceIdGenerator
        from backend.auth_rbac.authorizer import AuthRBAC
        from backend.auth_rbac.repository import InMemoryUserRoleRepository
        from backend.case_lifecycle.provider import PendingCommitContextProvider

        from .conftest import USERS
        from .factories import InMemoryCaseStore

        role_repository = InMemoryUserRoleRepository(dict(USERS))
        app = create_app()
        app.dependency_overrides[get_user_role_repository] = lambda: role_repository
        app.dependency_overrides[get_audit_service] = lambda: AuditService(audit_repository)
        app.dependency_overrides[get_case_store] = lambda: case_store
        app.dependency_overrides[get_commit_service] = lambda: DecisionCommitService(
            repository=commit_repository,
            context_provider=PendingCommitContextProvider(InMemoryCaseStore()),  # empty
            authorizer=AuthRBAC(role_repository),
            id_generator=SequenceIdGenerator(),
            clock=FixedClock(datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)),
        )
        with TestClient(app) as client:
            response = client.post(
                "/recommendations/REC-1/commit",
                json={"action": "approve"},
                headers=UNDERWRITER,
            )

        assert response.status_code == 404
        assert _state(case_store) is CaseState.DRAFTED     # the claim was released
        assert commit_repository.browse() == []


class TestTheFrozenServiceIsStillTheGate:
    def test_the_claim_runs_before_commit_and_a_lost_claim_never_calls_it(
        self, wired_client, commit_repository, case_store
    ):
        """⚑ A lost claim must short-circuit — the frozen service is never even reached."""
        wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "approve"}, headers=UNDERWRITER
        )
        assert _state(case_store) is CaseState.COMMITTED
        before = len(commit_repository.browse())

        response = wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "approve"}, headers=UNDERWRITER
        )
        assert response.status_code == 409
        assert len(commit_repository.browse()) == before

    def test_a_malformed_action_is_still_422_and_takes_no_claim(self, wired_client, case_store):
        """⚑ The wire-shape check still runs FIRST — no claim is taken for a bad action."""
        response = wired_client.post(
            "/recommendations/REC-1/commit", json={"action": "reject"}, headers=UNDERWRITER
        )
        assert response.status_code == 422
        assert _state(case_store) is CaseState.DRAFTED
