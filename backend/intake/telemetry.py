"""TelemetryEmitter — the single, forensic-free telemetry choke point (NFR §5/§7).

SEC-1-FORENSIC surface 3. The emitter accepts ONLY an allowlisted schema of
typed NON-TEXT fields — int counts, enum categories, durations, booleans /
statuses — and has NO free-text / ``str`` field. Span text (``original_span``
AND ``neutralized_span`` content) is therefore STRUCTURALLY UNREPRESENTABLE in
telemetry: there is no field that could hold it.

Emit-only (NFR-INT-OBS): this unit exposes signals through a thin, stack-agnostic
seam; the ``observability`` unit wires it to Langfuse/Prometheus/Grafana. The
emitted signal set is ``{counts, enums, durations, statuses}`` — nothing else.
"""
from __future__ import annotations

from enum import Enum
from typing import Callable, Optional

from pydantic import BaseModel, ConfigDict

from backend.intake.schema import ReasonCategory


class TelemetryEventType(str, Enum):
    PARSE = "parse"
    SANITIZE = "sanitize"
    VALIDATE_GATE = "validate_gate"


class TelemetryEvent(BaseModel):
    """A forensic-free telemetry event. Allowlist schema: enums / ints / bools
    only — NO free-text field (span text cannot be represented)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    event: TelemetryEventType
    neutralization_count: int = 0
    unparseable_doc_count: int = 0
    reject_reason: Optional[ReasonCategory] = None
    incomplete: Optional[bool] = None
    duration_ms: int = 0


class TelemetryEmitter:
    """Emit-only seam. The ``observability`` unit injects the real sink."""

    def __init__(self, sink: Optional[Callable[[TelemetryEvent], None]] = None) -> None:
        self._sink: Callable[[TelemetryEvent], None] = sink or (lambda event: None)
        self.emitted: list[TelemetryEvent] = []

    def emit(self, event: TelemetryEvent) -> None:
        self.emitted.append(event)
        self._sink(event)
