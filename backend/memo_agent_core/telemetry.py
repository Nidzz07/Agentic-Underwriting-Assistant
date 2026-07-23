"""TelemetryEmitter — emit-only allowlist telemetry (OBS-1 / PERF-1).

The event schema **structurally carries only** ids / enum values / int counts /
timing — **no** prose, demographic, free-text, or ``original_span`` field can be
emitted (OBS-1). Latency is **observed, not gated** (``duration_ms`` is emitted;
there is no latency-failing check — PERF-1). Langfuse 100%-step tracing is wired
by ``observability`` (reference-not-own) via the graph checkpointer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MemoTelemetryEvent:
    """Allowlist fields only — ids, enum values, int counts, timing."""
    application_id: str        # id
    recommendation: str        # enum value (not free text)
    confidence: str            # enum value
    outcome: str               # "finalized" | "blocked" (enum-like)
    cited_rule_count: int      # count
    missing_info_count: int    # count
    draft_attempts: int        # count
    duration_ms: int           # timing (observed, not gated)


class TelemetryEmitter:
    def __init__(self, sink: Optional[list] = None) -> None:
        self.events: list[MemoTelemetryEvent] = [] if sink is None else sink

    def emit(self, event: MemoTelemetryEvent) -> None:
        self.events.append(event)
