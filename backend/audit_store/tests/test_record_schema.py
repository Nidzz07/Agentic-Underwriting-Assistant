"""Tests for record_schema (Step 1) — the frozen AuditRecord superset.

Maps: NFR-AUDIT-TUPLE-1 at the TYPE level (6-tuple + snapshot + linkage + seam,
all non-null; closed `status`/`action` enums); FD ``domain-entities.md §2–§5``.
Frozen value objects (`frozen=True`, `extra=forbid`).
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.audit_store import record_schema as rs
from backend.audit_store.tests import factories as f


def test_audit_record_all_fields_present_and_non_null():
    rec = f.make_record()
    assert rec.decision_id and rec.application_id and rec.recommendation_id
    assert rec.audit_tuple is not None
    assert rec.applicant_profile_snapshot is not None
    assert rec.committed_decision is not None
    assert rec.status is rs.DecisionStatus.ACTIVE
    assert rec.supersedes_decision_id is None


def test_six_tuple_fields_all_present():
    t = f.make_tuple()
    for field in ("rulebook_version", "rule_results", "timestamp", "model_version",
                  "memo_hash", "engine_version"):
        assert getattr(t, field) is not None


@pytest.mark.parametrize("missing", ["rulebook_version", "timestamp", "model_version",
                                     "memo_hash", "engine_version", "rule_results"])
def test_audit_tuple_rejects_missing_required_field(missing):
    kw = dict(
        rulebook_version="1.0.0", rule_results=f.make_report(),
        timestamp=f.make_tuple().timestamp, model_version="m", memo_hash="h", engine_version="e",
    )
    kw.pop(missing)
    with pytest.raises(ValidationError):
        rs.AuditTuple(**kw)


def test_record_is_frozen_and_forbids_extra():
    rec = f.make_record()
    with pytest.raises(ValidationError):
        rec.decision_id = "OTHER"
    with pytest.raises(ValidationError):
        rs.CommittedDecision(recommendation_id="R", underwriter_id="U",
                             action=rs.CommitAction.APPROVE, reason=None, sneaky="x")


def test_status_is_a_closed_enum():
    assert {s.value for s in rs.DecisionStatus} == {"active", "superseded"}
    with pytest.raises(ValidationError):
        f.make_record(status="deleted")


def test_action_is_a_closed_enum():
    assert {a.value for a in rs.CommitAction} == {"approve", "override"}
    with pytest.raises(ValidationError):
        f.make_committed(action="reject")


def test_reason_optional_defaults_none():
    assert f.make_committed().reason is None
    assert f.make_committed(action=rs.CommitAction.OVERRIDE, reason="too risky").reason == "too risky"


def test_seam_defaults_active_and_null_supersedes():
    # OOS-7 seam: Phase-1/2 defaults are status=active + supersedes_decision_id=null.
    rec = rs.AuditRecord(
        decision_id="D", application_id="A", recommendation_id="R",
        audit_tuple=f.make_tuple(), applicant_profile_snapshot=f.make_snapshot(),
        committed_decision=f.make_committed(),
    )
    assert rec.status is rs.DecisionStatus.ACTIVE
    assert rec.supersedes_decision_id is None


def test_snapshot_carries_profile_and_hash():
    snap = f.make_snapshot()
    assert snap.application_id == "APP-1"
    assert snap.profile.application_id == "APP-1"   # the exact intake ApplicantProfile
    assert snap.content_hash


def test_commit_context_carries_tuple_inputs_plus_profile():
    ctx = f.make_context()
    for field in ("rule_results", "memo_hash", "model_version", "engine_version",
                  "rulebook_version", "applicant_profile"):
        assert getattr(ctx, field) is not None
