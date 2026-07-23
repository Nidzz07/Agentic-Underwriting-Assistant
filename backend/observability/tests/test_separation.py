"""SEP-1: TRACES and METRICS are two separate planes (BR-OBS-3 / P-OBS-3). From the SAME input
value, two INDEPENDENT assertions (one span + one counter contribution) hold with NO shared
mechanism — the deliberately-separated planes are not coupled. The structural no-cross-import
half lives in ``test_structural_guard.py`` (scan 2).
"""
from __future__ import annotations

from backend.observability.metrics import DECISIONS_BY_RECOMMENDATION, derive_from_event
from backend.observability.trace import TraceRecorder
from backend.observability.tests.fixtures import RecordingTraceSink, memo_event_fields


def test_same_value_feeds_both_planes_via_independent_paths():
    """One memo completion value produces ONE span (trace plane) AND ONE decisions-by-
    recommendation contribution (metric plane), each derived independently."""
    value = memo_event_fields()

    # trace plane — independent path
    sink = RecordingTraceSink()
    TraceRecorder(sink).on_step("finalize", value)
    assert len(sink.spans) == 1
    assert sink.spans[0][1]["recommendation"] == "APPROVE"

    # metric plane — independent path, SAME input value, no shared mechanism
    contributions = derive_from_event(value)
    counter = next(c for c in contributions if c.metric == DECISIONS_BY_RECOMMENDATION.name)
    assert counter.labels == {"recommendation": "APPROVE"}


def test_the_two_planes_do_not_share_a_bus_or_mechanism():
    # Independent module surfaces: the trace recorder and the metric derivation are reached
    # through different callables; neither routes through the other (import-level check is scan 2).
    import backend.observability.metrics as metrics
    import backend.observability.trace as trace

    assert not hasattr(trace, "derive_from_event")
    assert not hasattr(metrics, "TraceRecorder")
