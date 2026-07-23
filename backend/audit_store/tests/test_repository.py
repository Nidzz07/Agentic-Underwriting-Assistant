"""Tests for the AuditRepository Protocol + in-memory fake (Step 4).

Maps: NFR-AUDIT-APPEND-1 (service-layer structural — insert + read ONLY, no
update/delete method) + the ATOMIC-1 boundary seam (unit-of-work ``atomic()``
rolls back on any exception) + the STATUS-1 derived-superseded read query.
"""
from __future__ import annotations

import pytest

from backend.audit_store.repository import (
    AuditRepository,
    FaultInjected,
    InMemoryAuditRepository,
)
from backend.audit_store.tests import factories as f


def test_insert_then_get_within_atomic():
    repo = InMemoryAuditRepository()
    rec = f.make_record()
    with repo.atomic():
        repo.insert(rec)
    assert repo.get(rec.decision_id) == rec


def test_atomic_rolls_back_on_exception():
    repo = InMemoryAuditRepository()
    rec = f.make_record()
    with pytest.raises(RuntimeError):
        with repo.atomic():
            repo.insert(rec)
            raise RuntimeError("fault after insert, before commit")
    assert repo.get(rec.decision_id) is None            # both-or-neither: rolled back


def test_insert_outside_atomic_is_rejected():
    repo = InMemoryAuditRepository()
    with pytest.raises(RuntimeError):
        repo.insert(f.make_record())


def test_fail_on_insert_rolls_back_the_transaction():
    repo = InMemoryAuditRepository(fail_on_insert=True)
    rec = f.make_record()
    with pytest.raises(FaultInjected):
        with repo.atomic():
            repo.insert(rec)
    assert repo.get(rec.decision_id) is None


def test_repository_has_no_mutation_methods():
    # APPEND-1 structural: no update / delete anywhere on the surface.
    repo = InMemoryAuditRepository()
    for banned in ("update", "delete", "remove", "set_status", "mutate"):
        assert not hasattr(repo, banned)
    assert not hasattr(AuditRepository, "update") and not hasattr(AuditRepository, "delete")


def test_browse_by_application_id_and_across_cases():
    repo = InMemoryAuditRepository()
    with repo.atomic():
        repo.insert(f.make_record(decision_id="D1", application_id="APP-1"))
        repo.insert(f.make_record(decision_id="D2", application_id="APP-2"))
    assert [r.decision_id for r in repo.browse(application_id="APP-1")] == ["D1"]
    assert {r.decision_id for r in repo.browse()} == {"D1", "D2"}


def test_exists_superseding_is_a_read_query():
    repo = InMemoryAuditRepository()
    with repo.atomic():
        repo.insert(f.make_record(decision_id="D1"))
    assert repo.exists_superseding("D1") is False               # lone record -> not superseded
    with repo.atomic():
        repo.insert(f.make_record(decision_id="D2", supersedes_decision_id="D1"))
    assert repo.exists_superseding("D1") is True                # D2 supersedes D1 (derived)
