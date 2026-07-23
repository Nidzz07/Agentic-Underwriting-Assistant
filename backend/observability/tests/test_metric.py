"""METRIC-1: the 3 emitter-sourced metrics derive correctly BY SHAPE (P-OBS-6).

decisions by recommendation type (counter, memo ``recommendation``) · decision latency
(histogram, memo ``duration_ms``) · rule-evaluation duration (histogram, rules ``evaluate_micros``).
"""
from __future__ import annotations

from backend.observability.metrics import (
    DECISION_LATENCY,
    DECISIONS_BY_RECOMMENDATION,
    METRIC_DEFINITIONS,
    RULE_EVALUATION_DURATION,
    _EVENT_ALLOWED,
    derive_from_event,
)
from backend.observability.tests.fixtures import memo_event_fields, rules_event_fields


def _by_metric(contributions):
    return {c.metric: c for c in contributions}


def test_memo_event_yields_recommendation_counter_and_latency_histogram():
    contributions = derive_from_event(memo_event_fields())
    by_metric = _by_metric(contributions)
    assert set(by_metric) == {DECISIONS_BY_RECOMMENDATION.name, DECISION_LATENCY.name}
    counter = by_metric[DECISIONS_BY_RECOMMENDATION.name]
    assert counter.value == 1.0
    assert counter.labels == {"recommendation": "APPROVE"}   # enum VALUE label, demographic-free
    assert by_metric[DECISION_LATENCY.name].value == 1234.0


def test_rules_event_yields_rule_evaluation_duration_histogram():
    contributions = derive_from_event(rules_event_fields())
    by_metric = _by_metric(contributions)
    assert set(by_metric) == {RULE_EVALUATION_DURATION.name}
    assert by_metric[RULE_EVALUATION_DURATION.name].value == 4200.0


def test_all_three_emitter_metrics_reachable_across_the_two_event_shapes():
    produced = {c.metric for c in derive_from_event(memo_event_fields())}
    produced |= {c.metric for c in derive_from_event(rules_event_fields())}
    assert produced == {
        DECISIONS_BY_RECOMMENDATION.name,
        DECISION_LATENCY.name,
        RULE_EVALUATION_DURATION.name,
    }


def test_empty_event_yields_no_contribution():
    assert derive_from_event({}) == []


def test_derivation_reads_only_allowlisted_fields_off_the_named_constant():
    # parameterized OFF _EVENT_ALLOWED (Q4-A) — a field outside the constant is never sourced.
    fields = {"unlisted_field": 99, **memo_event_fields()}
    for c in derive_from_event(fields):
        assert set(c.labels).issubset(_EVENT_ALLOWED)
    assert "unlisted_field" not in _EVENT_ALLOWED


def test_five_metric_definitions_are_declared():
    assert len(METRIC_DEFINITIONS) == 5
    assert DECISIONS_BY_RECOMMENDATION.labels == ("recommendation",)
