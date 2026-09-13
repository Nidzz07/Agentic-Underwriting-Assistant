"""TelemetryEmitter — emit-only allowlist telemetry (OBS-1 / PERF-1).

The event schema **structurally carries only** ids / enum values / int counts /
timing — **no** prose, demographic, free-text, or ``original_span`` field can be
emitted (OBS-1). Latency is **observed, not gated** (``duration_ms`` is emitted;
there is no latency-failing check — PERF-1). Langfuse tracing is owned by
``observability`` (reference-not-own).

⚠️ This line previously ended *"via the graph checkpointer"*. ⛔ **That was already false
before C2 removed the checkpointer — not a consequence of it**: tracing was never wired
through a checkpointer, and ``observability.TraceRecorder.on_step`` has no production
caller at all (owned by OBS-SINK-DEFERRED, not by this unit). Corrected here only so
this unit does not name a mechanism it no longer has — register #34, change (m).
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
