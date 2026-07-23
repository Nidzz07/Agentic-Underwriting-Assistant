"""Tests for AuditService (Step 7).

Maps: NFR-AUDIT-READ-1 (read-only surface — no write method), NFR-AUDIT-LOG-1
(every committed decision retrievable in the trail), NFR-AUDIT-STATUS-1
(``effective_status`` / ``is_superseded`` is a pure derived READ over the reserved
``supersedes_decision_id`` — Phase-1/2 always ``active``).
"""
from __future__ import annotations

import pytest

from backend.audit_store import record_schema as rs
from backend.audit_store.audit_service import AuditNotFound, AuditService
from backend.audit_store.repository import InMemoryAuditRepository
from backend.audit_store.tests import factories as f


def _seeded(*records):
    repo = InMemoryAuditRepository()
    with repo.atomic():
        for rec in records:
            repo.insert(rec)
    return AuditService(repo), repo


def test_get_returns_the_record_or_none():
    svc, _ = _seeded(f.make_record(decision_id="D1"))
    assert svc.get("D1").decision_id == "D1"
    assert svc.get("missing") is None


def test_browse_history_by_application_and_across_cases():
    svc, _ = _seeded(
        f.make_record(decision_id="D1", application_id="APP-1"),
        f.make_record(decision_id="D2", application_id="APP-2"),
    )
    assert [r.decision_id for r in svc.browse_history(application_id="APP-1")] == ["D1"]
    assert {r.decision_id for r in svc.browse_history()} == {"D1", "D2"}


def test_every_committed_decision_is_retrievable():
    recs = [f.make_record(decision_id=f"D{i}", application_id="APP-1") for i in range(5)]
    svc, _ = _seeded(*recs)
    for rec in recs:
        got = svc.get(rec.decision_id)
        assert got is not None and got.audit_tuple is not None   # full tuple present (LOG-1)
    assert len(svc.browse_history(application_id="APP-1")) == 5


def test_audit_service_has_no_write_method():
    svc, _ = _seeded()
    for banned in ("commit", "insert", "update", "delete", "persist", "write"):
        assert not hasattr(svc, banned)


def test_effective_status_is_active_when_not_superseded():
    svc, _ = _seeded(f.make_record(decision_id="D1"))
    assert svc.is_superseded("D1") is False
    assert svc.effective_status("D1") is rs.DecisionStatus.ACTIVE


def test_effective_status_is_derived_superseded_from_a_newer_record():
    # Phase-3 shape (a newer record references D1) — the READ derives superseded,
    # with no in-place status write (STATUS-1).
    svc, _ = _seeded(
        f.make_record(decision_id="D1"),
        f.make_record(decision_id="D2", supersedes_decision_id="D1"),
    )
    assert svc.is_superseded("D1") is True
    assert svc.effective_status("D1") is rs.DecisionStatus.SUPERSEDED
    assert svc.effective_status("D2") is rs.DecisionStatus.ACTIVE


def test_effective_status_missing_raises():
    svc, _ = _seeded()
    with pytest.raises(AuditNotFound):
        svc.effective_status("nope")
