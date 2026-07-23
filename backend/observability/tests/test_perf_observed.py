"""PERF-1 (soft / observed, CONTRACT-1 companion): latency is RECORDED, never gated. The
``duration_ms`` / ``evaluate_micros`` timings become metric VALUES with no pass/fail threshold
and no latency-failing assertion (observed-never-gated, OBS-D8).
"""
from __future__ import annotations

from backend.observability.metrics import (
    DECISION_LATENCY,
    RULE_EVALUATION_DURATION,
    derive_from_event,
)
from backend.observability.tests.fixtures import memo_event_fields, rules_event_fields


def test_latency_is_recorded_as_a_metric_value():
    latency = next(
        c for c in derive_from_event(memo_event_fields()) if c.metric == DECISION_LATENCY.name
    )
    assert latency.value == 1234.0   # observed, not compared against any SLO


def test_rule_evaluation_duration_is_recorded_not_gated():
    duration = next(
        c
        for c in derive_from_event(rules_event_fields())
        if c.metric == RULE_EVALUATION_DURATION.name
    )
    assert duration.value == 4200.0   # recorded; no threshold, no failure path


def test_a_large_latency_still_only_produces_a_value_never_a_failure():
    # An extreme value produces a metric value, NOT an assertion error — nothing gates on it.
    contributions = derive_from_event({"duration_ms": 10_000_000})
    assert contributions[0].value == 10_000_000.0
