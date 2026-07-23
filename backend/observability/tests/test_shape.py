"""SHAPE-1, behavioral half: U21 consumes events/outcomes BY SHAPE — plain mappings drive every
derivation, no frozen event type is imported or constructed. The structural no-import scan +
detector self-test live in ``test_structural_guard.py`` (scan 4).
"""
from __future__ import annotations

from backend.observability.metrics import derive_from_event, derive_from_step_outcome
from backend.observability.trace import TraceRecorder
from backend.observability.tests.fixtures import (
    RecordingTraceSink,
    memo_event_fields,
    outlier_step_outcome,
    rules_event_fields,
)


def test_plain_mappings_drive_the_metric_derivations_no_type_needed():
    assert derive_from_event(dict(memo_event_fields()))          # by-shape mapping
    assert derive_from_event(dict(rules_event_fields()))
    assert derive_from_step_outcome(dict(outlier_step_outcome()))


def test_plain_mapping_drives_the_trace_recorder():
    sink = RecordingTraceSink()
    TraceRecorder(sink).on_step("validate", dict(memo_event_fields()))
    assert sink.step_names == ["validate"]


def test_is_outlier_is_read_by_value_not_by_type():
    # A bare mapping with just the field name drives the outlier metric — no OutlierResult import.
    from backend.observability.metrics import OUTLIER_FLAG

    contributions = derive_from_step_outcome({"is_outlier": True})
    assert any(c.metric == OUTLIER_FLAG.name for c in contributions)
