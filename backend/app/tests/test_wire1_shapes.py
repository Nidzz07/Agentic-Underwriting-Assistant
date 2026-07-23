"""INT-WIRE-1 (load-bearing) — every wired route matches the FROZEN WIRE-1 §5 shape EXACTLY.

The contract is the authority: these assertions are written against WIRE-1's text, not against
whatever the code happens to emit. Enum values are checked BY VALUE and for NO re-casing (§1).
"""
from __future__ import annotations

from backend.app.tests.conftest import ADMIN, AUDITOR, UNDERWRITER


class TestR1Session:
    def test_returns_exactly_user_id_and_role(self, client):
        response = client.get("/session", headers=UNDERWRITER)
        assert response.status_code == 200
        assert response.json() == {"user_id": "UW-1", "role": "underwriter"}

    def test_role_is_the_exact_lowercase_wire_value_never_re_cased(self, client):
        # WIRE-1 §6: "the exact lowercase enum value — no re-case".
        assert client.get("/session", headers=AUDITOR).json()["role"] == "auditor"
        assert client.get("/session", headers=ADMIN).json()["role"] == "admin"

    def test_r1_is_authenticated_any_role_no_authorization(self, client):
        # §3 marks R1 "authenticated": admin must reach it even though PERMISSION_MATRIX
        # excludes admin from READ_AUDIT. R1 delivers identity; it gates nothing.
        assert client.get("/session", headers=ADMIN).status_code == 200


class TestR6ListDecisions:
    def test_body_is_the_list_wrapper_with_items_and_page(self, client):
        body = client.get("/decisions", headers=UNDERWRITER).json()
        assert set(body) == {"items", "page"}
        assert set(body["page"]) == {"page", "size", "total"}

    def test_decision_summary_has_exactly_the_five_frozen_fields(self, client):
        item = client.get("/decisions", headers=UNDERWRITER).json()["items"][0]
        # WIRE-1 §5 DecisionSummary — exactly these five, no more, no fewer.
        assert set(item) == {
            "decision_id", "application_id", "recommendation_id", "action", "timestamp",
        }

    def test_summary_carries_the_human_action_by_value_and_the_timestamp(self, client):
        items = client.get("/decisions", headers=UNDERWRITER).json()["items"]
        by_id = {i["decision_id"]: i for i in items}
        assert by_id["DEC-1"]["action"] == "approve"     # frozen lowercase CommitAction value
        assert by_id["DEC-2"]["action"] == "override"
        assert by_id["DEC-1"]["timestamp"].startswith("2026-01-01T13:00:00")

    def test_summary_omits_the_system_recommendation(self, client):
        # §5: the R6 list item does NOT carry recommendation/confidence — R7 is their only
        # source. This is exactly why ui-history's rows show no recommendation (no N+1).
        item = client.get("/decisions", headers=UNDERWRITER).json()["items"][0]
        assert "recommendation" not in item
        assert "confidence" not in item

    def test_page_is_one_based_and_total_is_the_full_count(self, client):
        body = client.get("/decisions", headers=UNDERWRITER).json()
        assert body["page"] == {"page": 1, "size": 20, "total": 3}


class TestR7GetDecision:
    def test_body_is_the_full_audit_record_with_the_frozen_top_level_keys(self, client):
        body = client.get("/decisions/DEC-1", headers=UNDERWRITER).json()
        # §5: R7 == audit_store.record_schema.AuditRecord, verbatim.
        assert set(body) == {
            "decision_id", "application_id", "recommendation_id", "audit_tuple",
            "applicant_profile_snapshot", "committed_decision", "status",
            "supersedes_decision_id",
        }

    def test_audit_tuple_carries_the_full_forensic_six_tuple(self, client):
        tuple_ = client.get("/decisions/DEC-1", headers=UNDERWRITER).json()["audit_tuple"]
        assert set(tuple_) == {
            "rulebook_version", "rule_results", "timestamp", "model_version",
            "memo_hash", "engine_version",
        }

    def test_rule_results_is_the_full_report_the_system_recommendation_lives_in(self, client):
        report = client.get("/decisions/DEC-1", headers=UNDERWRITER).json()["audit_tuple"]["rule_results"]
        assert report["recommendation"] == "APPROVE"   # UPPERCASE, never re-cased (§1)
        assert report["confidence"] == "High"          # Title-case, never re-cased (§1)
        assert len(report["rule_results"]) == 1        # every entry preserved

    def test_committed_decision_carries_the_human_linkage(self, client):
        body = client.get("/decisions/DEC-2", headers=UNDERWRITER).json()
        assert body["committed_decision"] == {
            "recommendation_id": "REC-2",
            "underwriter_id": "UW-1",
            "action": "override",
            "reason": "Verified a second income source by phone.",
        }

    def test_status_is_active_and_supersedes_is_null_in_phase_one(self, client):
        body = client.get("/decisions/DEC-1", headers=UNDERWRITER).json()
        assert body["status"] == "active"
        assert body["supersedes_decision_id"] is None

    def test_profile_snapshot_is_the_persisted_original_input(self, client):
        snapshot = client.get("/decisions/DEC-1", headers=UNDERWRITER).json()["applicant_profile_snapshot"]
        assert set(snapshot) == {"application_id", "profile", "content_hash"}
        assert snapshot["profile"]["demographics"]["full_name"] == "Ada Byron"
