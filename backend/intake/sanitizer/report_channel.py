"""SanitizationReportChannel — the audit channel (SEC-1-FORENSIC surface 1).

The SanitizationReport (which preserves ``original_span`` verbatim) travels a
SEPARATE audit channel to ``audit-store``. This channel is the SOLE carrier of
span text; it is DISJOINT by construction from the telemetry seam and any log
sink. Only ``SanitizedText.clean_text`` (the neutralized text) flows toward
``memo-agent-core`` (surface 2), and telemetry carries counts/enums only
(surface 3) — so the raw injection can never re-enter an LLM-bound context.
"""
from __future__ import annotations

from typing import Callable, Optional

from backend.intake.schema import SanitizationReportEntry


class SanitizationReportChannel:
    """Carries the full SanitizationReport (span text) to the audit sink only."""

    def __init__(
        self,
        audit_sink: Optional[Callable[[str, list[SanitizationReportEntry]], None]] = None,
    ) -> None:
        self._sink = audit_sink or (lambda source_ref, report: None)
        self.published: list[tuple[str, list[SanitizationReportEntry]]] = []

    def publish(self, source_ref: str, report: list[SanitizationReportEntry]) -> None:
        self.published.append((source_ref, report))
        self._sink(source_ref, report)
