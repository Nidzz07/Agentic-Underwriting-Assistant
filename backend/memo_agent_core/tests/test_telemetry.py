"""TelemetryEmitter — OBS-1 (allowlist, no prose/demographic) + PERF-1 (observed-not-gated)."""
from __future__ import annotations

from backend.memo_agent_core.telemetry import MemoTelemetryEvent, TelemetryEmitter


_ALLOWED_FIELDS = {
    "application_id",
    "recommendation",
    "confidence",
    "outcome",
    "cited_rule_count",
    "missing_info_count",
    "draft_attempts",
    "duration_ms",
}

_FORBIDDEN_SUBSTRINGS = ("prose", "narrative", "text", "name", "city", "gender", "span", "detail")


def test_event_carries_only_allowlist_fields():
    fields = set(MemoTelemetryEvent.__dataclass_fields__)
    assert fields == _ALLOWED_FIELDS
    for name in fields:
        assert not any(bad in name.lower() for bad in _FORBIDDEN_SUBSTRINGS)


def test_event_field_types_are_ids_enums_counts_or_timing():
    types = {f.name: f.type for f in MemoTelemetryEvent.__dataclass_fields__.values()}
    assert types["application_id"] == "str"
    assert types["recommendation"] == "str" and types["confidence"] == "str"
    assert types["cited_rule_count"] == "int"
    assert types["duration_ms"] == "int"


def test_emit_appends_and_is_not_latency_gated():
    emitter = TelemetryEmitter()
    event = MemoTelemetryEvent(
        application_id="APP-1",
        recommendation="APPROVE",
        confidence="High",
        outcome="finalized",
        cited_rule_count=2,
        missing_info_count=0,
        draft_attempts=1,
        duration_ms=10_000_000,  # absurdly slow — still emitted, never rejected (PERF-1)
    )
    emitter.emit(event)
    assert emitter.events == [event]


def test_emitter_uses_shared_sink_when_supplied():
    sink: list = []
    emitter = TelemetryEmitter(sink)
    emitter.emit(
        MemoTelemetryEvent("APP-2", "REFER", "Medium", "blocked", 0, 1, 2, 5)
    )
    assert len(sink) == 1
