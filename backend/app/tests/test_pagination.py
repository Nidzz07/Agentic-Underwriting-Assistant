"""INT-PAGE-1 + INT-PROJ-1 — in-app pagination (Decision 4) + the §5 projections. Pure, no I/O."""
from __future__ import annotations

import pytest

from backend.app.projections import (
    DEFAULT_PAGE_SIZE,
    audit_record_wire,
    decision_list_wrapper,
    decision_summary,
    paginate,
)
from backend.app.tests.conftest import UNDERWRITER
from backend.app.tests.factories import make_override_record, make_record


@pytest.fixture
def many():
    """25 records, ids DEC-1..DEC-25 in browse()'s decision_id order."""
    return sorted([make_record(i) for i in range(1, 26)], key=lambda r: r.decision_id)


class TestPaginateIsOneBased:
    def test_page_one_returns_the_first_slice(self, many):
        items, total = paginate(many, page=1, size=10)
        assert total == 25
        assert [r.decision_id for r in items] == [r.decision_id for r in many[:10]]

    def test_page_k_returns_the_kth_slice(self, many):
        items, _ = paginate(many, page=3, size=10)
        assert [r.decision_id for r in items] == [r.decision_id for r in many[20:25]]

    def test_total_is_the_full_count_not_the_page_length(self, many):
        items, total = paginate(many, page=1, size=10)
        assert len(items) == 10
        assert total == 25

    def test_a_page_past_the_end_is_empty_not_an_error(self, many):
        items, total = paginate(many, page=99, size=10)
        assert items == []
        assert total == 25   # total still truthful

    def test_a_size_larger_than_the_corpus_returns_everything_once(self, many):
        items, total = paginate(many, page=1, size=1000)
        assert len(items) == 25 == total

    def test_an_empty_store_paginates_to_an_empty_page(self):
        assert paginate([], page=1, size=20) == ([], 0)


class TestDecisionSummaryProjection:
    def test_exactly_the_five_frozen_fields(self):
        assert set(decision_summary(make_record(1))) == {
            "decision_id", "application_id", "recommendation_id", "action", "timestamp",
        }

    def test_action_is_the_wire_value_never_the_enum_repr(self):
        assert decision_summary(make_record(1))["action"] == "approve"
        assert decision_summary(make_override_record(2))["action"] == "override"

    def test_timestamp_is_iso_8601_from_the_audit_tuple(self):
        record = make_record(1)
        assert decision_summary(record)["timestamp"] == record.audit_tuple.timestamp.isoformat()

    def test_the_projection_drops_no_id(self):
        summary = decision_summary(make_record(7))
        assert summary["decision_id"] == "DEC-7"
        assert summary["application_id"] == "APP-7"
        assert summary["recommendation_id"] == "REC-7"


class TestListWrapper:
    def test_shape_is_items_plus_page(self, many):
        body = decision_list_wrapper(many, page=2, size=10)
        assert set(body) == {"items", "page"}
        assert body["page"] == {"page": 2, "size": 10, "total": 25}
        assert len(body["items"]) == 10

    def test_delivered_order_is_preserved_by_the_projection(self, many):
        body = decision_list_wrapper(many, page=1, size=5)
        # the projection re-sorts nothing — it emits the order it was handed (Q3-A).
        assert [i["decision_id"] for i in body["items"]] == [r.decision_id for r in many[:5]]


class TestAuditRecordWire:
    def test_serialization_is_the_frozen_models_own(self):
        record = make_record(1)
        assert audit_record_wire(record) == record.model_dump(mode="json")

    def test_the_report_enums_are_not_re_cased(self):
        report = audit_record_wire(make_record(1))["audit_tuple"]["rule_results"]
        assert report["recommendation"] == "APPROVE"
        assert report["confidence"] == "High"


class TestPaginationThroughTheRealRoute:
    def test_r6_honours_page_and_size(self, client):
        body = client.get("/decisions?page=2&size=2", headers=UNDERWRITER).json()
        assert body["page"] == {"page": 2, "size": 2, "total": 3}
        assert [i["decision_id"] for i in body["items"]] == ["DEC-3"]

    def test_r6_defaults_to_page_one_and_the_default_size(self, client):
        body = client.get("/decisions", headers=UNDERWRITER).json()
        assert body["page"]["page"] == 1
        assert body["page"]["size"] == DEFAULT_PAGE_SIZE

    def test_a_page_past_the_end_returns_an_empty_page_not_a_404(self, client):
        response = client.get("/decisions?page=9&size=2", headers=UNDERWRITER)
        assert response.status_code == 200
        assert response.json() == {"items": [], "page": {"page": 9, "size": 2, "total": 3}}

    def test_an_empty_store_returns_an_empty_page(self, empty_client):
        body = empty_client.get("/decisions", headers=UNDERWRITER).json()
        assert body["items"] == []
        assert body["page"]["total"] == 0


class TestOrderingIsBrowsesDecisionIdOrder:
    def test_r6_emits_decision_id_order_the_honest_current_behaviour(self, client):
        # Q3-A, recorded: no frozen artifact pins R6's order. This asserts the order the app
        # ACTUALLY emits (browse()'s ORDER BY decision_id) — it is not a designed guarantee,
        # and ui-history re-sorts nothing, so this is what an auditor sees.
        items = client.get("/decisions", headers=UNDERWRITER).json()["items"]
        ids = [i["decision_id"] for i in items]
        assert ids == sorted(ids)
        assert ids == ["DEC-1", "DEC-2", "DEC-3"]

    def test_it_is_NOT_newest_first_by_timestamp(self, client):
        # Documents the consequence honestly: DEC-1 is the OLDEST (timestamp +1h) yet sorts
        # first. A history view conventionally reads newest-first; this one does not, because
        # inventing a timestamp sort would have required touching frozen audit-store.
        items = client.get("/decisions", headers=UNDERWRITER).json()["items"]
        timestamps = [i["timestamp"] for i in items]
        assert timestamps == sorted(timestamps)          # ascending == oldest first
        assert timestamps != sorted(timestamps, reverse=True)
