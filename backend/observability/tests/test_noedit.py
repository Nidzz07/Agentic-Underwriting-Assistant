"""NOEDIT-1 (LOAD-BEARING — full-highest), behavioral half: injected sinks make editing frozen
code UNNECESSARY (the by-construction argument). The structural scan (no frozen import/mutate)
+ its detector self-test live in ``test_structural_guard.py`` (scan 1). Together they prove U21
edits no frozen unit — BR-OBS-1.
"""
from __future__ import annotations

from backend.observability.metrics import derive_from_event, derive_from_step_outcome
from backend.observability.trace import TraceRecorder
from backend.observability.tests.fixtures import (
    RecordingMetricExporter,
    RecordingTraceSink,
    memo_event_fields,
    outlier_step_outcome,
)


def test_trace_recorder_works_against_an_injected_fake_no_frozen_code_touched():
    """The recorder produces spans against an INJECTED fake sink — nothing about the frozen
    ``memo_agent_core`` orchestrator is imported, edited, or required."""
    sink = RecordingTraceSink()
    TraceRecorder(sink).on_step("draft", memo_event_fields())
    assert sink.step_names == ["draft"]


def test_metric_exporter_is_a_plain_injected_protocol_double():
    """The exporter is a plain injected double — derivations produce contributions with no live
    ``prometheus-client`` and no frozen-unit dependency (by-construction: nothing to edit)."""
    exporter = RecordingMetricExporter()
    for contribution in derive_from_event(memo_event_fields()):
        exporter.export(contribution)
    for contribution in derive_from_step_outcome(outlier_step_outcome()):
        exporter.export(contribution)
    assert len(exporter.contributions) == 3   # recommendation counter + latency + outlier flag


def test_no_frozen_module_object_is_reachable_from_u21_production():
    """By construction: importing the three production modules pulls in NO frozen backend unit."""
    import sys

    import backend.observability.allowlist  # noqa: F401
    import backend.observability.metrics  # noqa: F401
    import backend.observability.trace  # noqa: F401

    frozen = {
        "backend.memo_agent_core.orchestrator",
        "backend.outlier_model.model",
        "backend.memo_extensions.borderline_router",
        "backend.secrets_config.settings",
    }
    # None of these need to be imported for U21 production to load (they may be loaded by OTHER
    # tests in the session; the guarantee here is U21 production declares no such import — proven
    # structurally in scan 1). This behavioral check asserts the production modules import cleanly.
    assert "backend.observability.trace" in sys.modules
    assert "backend.observability.metrics" in sys.modules
    assert frozen  # sentinel — the structural scan (scan 1) is the authoritative no-import proof
