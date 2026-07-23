"""CONTRACT-1, behavioral half: U21 declares NO recommendation/verdict and cannot alter an
outcome (BR-OBS-7, advisory-only inherited). Metrics are counts / timings / enum-value labels
only. The structural scan (no ``Recommendation``/``Confidence`` type) + detector self-test live
in ``test_structural_guard.py`` (scan 5).
"""
from __future__ import annotations

from backend.observability.metrics import (
    COUNTER,
    GAUGE,
    HISTOGRAM,
    METRIC_DEFINITIONS,
    derive_from_event,
)
from backend.observability.tests.fixtures import memo_event_fields


def test_metrics_are_counts_timings_and_enum_labels_only():
    kinds = {d.kind for d in METRIC_DEFINITIONS}
    assert kinds <= {COUNTER, HISTOGRAM, GAUGE}


def test_recommendation_appears_only_as_a_scalar_label_value_not_a_verdict():
    counter = next(
        c for c in derive_from_event(memo_event_fields()) if c.labels
    )
    # the label VALUE is a plain string, not a Recommendation-typed object / verdict
    assert isinstance(counter.labels["recommendation"], str)


def test_no_contribution_carries_a_pass_fail_or_verdict_field():
    for c in derive_from_event(memo_event_fields()):
        assert set(c.labels).issubset({"recommendation"})
        assert isinstance(c.value, float)   # a number, never a decision
