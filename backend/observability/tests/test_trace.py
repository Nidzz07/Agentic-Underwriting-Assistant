"""TRACE-1 (LOAD-BEARING — full-highest): 100%-step trace coverage over U4's REAL node list,
via the single ``record_span`` sink with TWO callers, across BOTH real graph paths.

Grounded in ``memo_agent_core/orchestrator.py`` (draft/validate/finalize/flag + the CAP retry)
and ``MEMO_CITATION_RETRY_CAP`` — referenced by value, NOT invented. The system-wide 100% is
AC-7's deploy-time audit; this asserts the recording-fake coverage at tier-U only.
"""
from __future__ import annotations

import pytest

# Grounding the retry-path length against the frozen cap (a test-only import of a frozen
# CONSTANT — not U4's test file, not a production edge). If CAP changes, this fails loudly.
from backend.memo_agent_core.constants import MEMO_CITATION_RETRY_CAP
from backend.observability.trace import _SPAN_ALLOWED, TraceRecorder
from backend.observability.tests.fixtures import (
    FINALIZE_SEQUENCE,
    RETRY_THEN_FLAG_SEQUENCE,
    RecordingTraceSink,
)


def test_grounded_sequences_match_the_frozen_graph_structure():
    # finalize path = 3 node executions; retry-then-flag at CAP = 2*CAP + 1 executions.
    assert len(FINALIZE_SEQUENCE) == 3
    assert len(RETRY_THEN_FLAG_SEQUENCE) == 2 * MEMO_CITATION_RETRY_CAP + 1
    assert FINALIZE_SEQUENCE == ("draft", "validate", "finalize")
    assert RETRY_THEN_FLAG_SEQUENCE == ("draft", "validate", "draft", "validate", "flag")


@pytest.mark.parametrize(
    "sequence,expected_count",
    [(FINALIZE_SEQUENCE, 3), (RETRY_THEN_FLAG_SEQUENCE, 5)],
)
def test_one_span_per_node_execution_across_both_real_paths(sequence, expected_count):
    """The checkpointer-callback caller yields EXACTLY one span per node execution — none
    missed, none double-counted (draft/validate legitimately appear twice on the retry path)."""
    sink = RecordingTraceSink()
    recorder = TraceRecorder(sink)
    for step in sequence:
        recorder.on_step(step, {"duration_ms": 5})
    assert len(sink.spans) == expected_count
    assert sink.step_names == list(sequence)


def test_span_api_caller_wraps_a_non_graph_tool_step():
    """The span-API caller records a span for a non-graph tool step (U18 scoring / U19 routing
    at composition), through the SAME single ``record_span`` sink."""
    sink = RecordingTraceSink()
    recorder = TraceRecorder(sink)
    with recorder.span("outlier_scoring", {"is_outlier": True}):
        pass
    assert sink.step_names == ["outlier_scoring"]
    assert sink.spans[0][1] == {"is_outlier": True}


def test_union_coverage_graph_nodes_plus_tool_steps_one_stream():
    """100% = graph nodes UNION tool steps over ONE span stream (Q3-A) — both callers feed the
    same sink; ``step_name`` distinguishes graph names from tool names (latent attribution)."""
    sink = RecordingTraceSink()
    recorder = TraceRecorder(sink)
    for step in FINALIZE_SEQUENCE:
        recorder.on_step(step, {})
    with recorder.span("mcp_retrieval", {}):
        pass
    assert sink.step_names == ["draft", "validate", "finalize", "mcp_retrieval"]


def test_span_attributes_are_projected_through_the_allowlist():
    """A demographic attribute handed to a caller is DROPPED before it reaches the span."""
    sink = RecordingTraceSink()
    recorder = TraceRecorder(sink)
    recorder.on_step("draft", {"recommendation": "APPROVE", "full_name": "Jane Doe"})
    step_name, attributes = sink.spans[0]
    assert attributes == {"recommendation": "APPROVE"}
    assert "full_name" not in attributes
    # every emitted attribute name is in the named allowlist constant (parameterized off it)
    assert set(attributes).issubset(_SPAN_ALLOWED)
