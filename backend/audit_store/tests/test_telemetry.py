"""Tests for TelemetryEmitter (Step 8).

Maps: NFR-AUDIT-OBS-1 (allowlist schema — the only str leaves are metadata ids;
no applicant-profile / demographic / free-text field; distinct from the SEC-5
trail), NFR-AUDIT-PERF-1 (commit/replay timing emitted, never gated).
"""
from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import get_args, get_origin

from pydantic import BaseModel

from backend.common.canon_ser import canon_ser
from backend.audit_store import record_schema as rs
from backend.audit_store.replay_service import ReplayVerdict
from backend.audit_store.telemetry import (
    CommitTelemetry,
    ReplayOutcome,
    ReplayTelemetry,
    TelemetryEmitter,
)
from backend.audit_store.tests import factories as f

_META_STR = {"decision_id", "rulebook_version"}


def _leaf_types(model, str_fields, other):
    for name, field in model.model_fields.items():
        ann = field.annotation
        inner = get_args(ann)[0] if get_origin(ann) in (list, tuple) and get_args(ann) else ann
        if isinstance(inner, type) and issubclass(inner, BaseModel):
            _leaf_types(inner, str_fields, other)
        elif inner is str:
            str_fields.add(name)
        elif inner in (int, bool) or (isinstance(inner, type) and issubclass(inner, Enum)):
            continue
        else:
            other.add((name, inner))


def test_only_str_leaves_are_metadata_ids():
    for model in (CommitTelemetry, ReplayTelemetry):
        str_fields, other = set(), set()
        _leaf_types(model, str_fields, other)
        assert str_fields <= _META_STR      # only metadata ids are str
        assert other == set()               # everything else int | bool | Enum


def test_no_demographic_or_free_text_field_names():
    names = set(CommitTelemetry.model_fields) | set(ReplayTelemetry.model_fields)
    forbidden = {
        "message", "actual_value", "reason", "memo", "memo_hash", "full_name", "name",
        "gender", "city", "occupation", "health_flags", "profile", "applicant",
        "underwriter_id", "model_version", "rule_results",
    }
    assert names & forbidden == set()


def test_commit_telemetry_carries_no_applicant_free_text():
    rec = f.make_record(
        committed_decision=f.make_committed(action=rs.CommitAction.OVERRIDE,
                                            reason="SECRET underwriter rationale"),
        applicant_profile_snapshot=f.make_snapshot(
            profile=f.make_profile(occupation="spy-in-gotham")),
    )
    tel = TelemetryEmitter().emit_commit(rec, commit_micros=42)
    blob = canon_ser(tel.model_dump()).decode("utf-8")
    assert "SECRET" not in blob and "spy-in-gotham" not in blob
    assert "Ada Byron" not in blob and "Metropolis" not in blob   # demographics excluded


def test_extra_fields_are_forbidden():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        CommitTelemetry(decision_id="D", rulebook_version="1.0.0",
                        action=rs.CommitAction.APPROVE, commit_micros=1, leak="x")


def _verdict(match=True):
    return ReplayVerdict(decision_id="DEC-1", match=match, fresh_projection={},
                         recorded_projection={}, delta=None if match else {"x": 1},
                         engine_drift=False, rulebook_drift=False)


def test_emit_commit_and_replay_push_to_sink_and_record_last():
    captured = []
    emitter = TelemetryEmitter(sink=captured.append)
    c = emitter.emit_commit(f.make_record(), commit_micros=7)
    r = emitter.emit_replay(_verdict(), rulebook_version="1.0.0", replay_micros=9)
    assert captured == [c, r]
    assert emitter.last is r
    assert r.outcome is ReplayOutcome.MATCH


def test_replay_outcome_mismatch_enum():
    tel = TelemetryEmitter().emit_replay(_verdict(match=False), rulebook_version="1.0.0",
                                         replay_micros=5)
    assert tel.outcome is ReplayOutcome.MISMATCH


def test_perf_timing_observed_not_gated():
    # An enormous duration is emitted, never raises / fails a latency check (PERF-1).
    tel = TelemetryEmitter().emit_commit(f.make_record(), commit_micros=10**12)
    assert tel.commit_micros == 10**12
