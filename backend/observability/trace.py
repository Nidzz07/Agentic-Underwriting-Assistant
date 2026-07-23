"""trace-side (C-OBS-1, P-OBS-1/2/4) — the demographic-free span schema + the ONE injected
span sink driven by TWO callers (TRACE-1, Q3-A).

``TraceSink`` is an INJECTED Protocol (an offline recording fake at tier-U; the real
``langfuse`` handler binds at composition — ``OBS-SINK-DEFERRED``). ``TraceRecorder`` has the
two callers NFR Design named: ``on_step`` (the graph-checkpointer callback adapter) and
``span`` (the context-manager the composition wraps around non-graph tool steps). Both project
every attribute through ``project_allowlisted`` (P-OBS-4), so a demographic attribute is
dropped before it can reach a span.

Header note (documentation only, NEVER enforcement): holds no LLM; edits no frozen unit
(the sink is injected — nothing to gain by editing frozen code, NOEDIT-1); every attribute is
routed through the allowlist.

DEFERRED (``OBS-SINK-DEFERRED`` / INFRA-OBS-Fold-1c — named here, NOT taken, NOT a U4 edit):
emitting each INTERNAL graph node (``draft``/``validate``/``finalize``/``flag``) as its own span
needs LangGraph's per-node callback, which the frozen ``memo_agent_core`` orchestrator's
``run()`` (which builds its invoke ``config`` internally, with no ``callbacks`` key) does not
forward. The future minimal additive seam is a ``callbacks``/``config`` passthrough on ``run()``
that merges a handler driving ``on_step`` below — the injected seam already exists here. The
run-level + tool-step spans (via ``span``) and the metric plane (via U4's existing ``telemetry``
seam) need NO such change.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Mapping, Protocol

from backend.observability.allowlist import ScalarValue, project_allowlisted

# Permitted span-attribute names — ids / enum values / int counts / timings only. No prose,
# demographic, free-text, or ``original_span`` name appears; every entry is an allowlist scalar
# field. Tests parameterize OFF this constant (Q4-A) — never a hardcoded duplicate literal.
_SPAN_ALLOWED: frozenset[str] = frozenset(
    {
        "recommendation",       # enum value
        "confidence",           # enum value
        "outcome",              # enum-like value
        "draft_attempts",       # count
        "cited_rule_count",     # count
        "missing_info_count",   # count
        "duration_ms",          # timing (observed, not gated)
        "is_outlier",           # bool
        "outlier_score",        # numeric score
    }
)


class TraceSink(Protocol):
    """The injected span sink — one method, driven by BOTH callers. Recording fake at tier-U;
    the real ``langfuse`` handler binds at composition (``OBS-SINK-DEFERRED``)."""

    def record_span(self, step_name: str, attributes: Mapping[str, ScalarValue]) -> None: ...


class TraceRecorder:
    """ONE ``record_span`` sink, TWO callers (Q3-A): ``on_step`` (checkpointer callback) and
    ``span`` (tool-step context-manager). Both project through the shared allowlist."""

    def __init__(self, sink: TraceSink) -> None:
        self._sink = sink

    def on_step(self, step_name: str, raw_attributes: Mapping[str, object]) -> None:
        """Graph-checkpointer callback caller — one span per node execution."""
        self._sink.record_span(step_name, project_allowlisted(raw_attributes, _SPAN_ALLOWED))

    @contextmanager
    def span(self, step_name: str, raw_attributes: Mapping[str, object]) -> Iterator[None]:
        """Span-API caller — the context-manager composition wraps around a non-graph tool step."""
        self._sink.record_span(step_name, project_allowlisted(raw_attributes, _SPAN_ALLOWED))
        yield
