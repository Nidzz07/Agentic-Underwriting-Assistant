"""TelemetryEmitter — allowlist, demographic-free telemetry (Step 12).

NFR Design §8. An **allowlist Pydantic schema** whose fields are **structurally
incapable** of carrying applicant / demographic / free-text content: the only
``str`` leaves are **rulebook metadata** (``rulebook_version`` / ``rule_id``);
everything else is an ``int`` count/timing or an ``Enum``. There is **no
applicant-profile-derived field and no free-text field** — CON-BR1 extends to
telemetry **by construction** (NFR-RULES-OBS-1), not by an omit-convention.
``extra="forbid"`` rejects any sneaked-in field.

Performance is **observed-only** (NFR-RULES-PERF-1): ``evaluate_micros`` is
emitted for the soft-budget dashboard — it is measured by the caller **around**
the pure ``evaluate`` (never inside it, which would break DET-1) and is **never
gated** (no latency-failing check). **Emit-only**: the emitter pushes to a sink;
the ``observability`` unit wires Langfuse/Prometheus (reference-not-own).
"""
from __future__ import annotations

from typing import Callable, Optional

from pydantic import BaseModel, ConfigDict

from backend.rules_engine.report_schema import (
    Confidence,
    Recommendation,
    RuleResultReport,
    RuleStatus,
)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class RuleStatusEntry(_Frozen):
    """Per-rule outcome — ``rule_id`` (rulebook metadata) + a status ``Enum`` only."""
    rule_id: str
    status: RuleStatus


class EvaluationTelemetry(_Frozen):
    """The allowlist telemetry record — counts / enums / timing / rulebook metadata."""
    rulebook_version: str            # rulebook metadata (semver)
    recommendation: Recommendation   # enum
    confidence: Confidence           # enum
    rule_count: int
    pass_count: int
    not_evaluated_count: int
    decline_count: int
    refer_count: int
    evaluate_micros: int             # observed-only timing (PERF-1)
    per_rule: list[RuleStatusEntry]


def build_telemetry(report: RuleResultReport, evaluate_micros: int) -> EvaluationTelemetry:
    """Project a report to telemetry — counts / enums / metadata ONLY.

    Derives nothing from ``actual_value`` / ``message`` / the applicant profile,
    so no demographic or free-text value can be represented.
    """
    results = report.rule_results
    return EvaluationTelemetry(
        rulebook_version=report.rulebook_version,
        recommendation=report.recommendation,
        confidence=report.confidence,
        rule_count=len(results),
        pass_count=sum(1 for r in results if r.status is RuleStatus.PASS),
        not_evaluated_count=sum(1 for r in results if r.status is RuleStatus.NOT_EVALUATED),
        decline_count=len(report.decline_reasons),
        refer_count=len(report.refer_reasons),
        evaluate_micros=evaluate_micros,
        per_rule=[RuleStatusEntry(rule_id=r.rule_id, status=r.status) for r in results],
    )


class TelemetryEmitter:
    """Emit-only seam. The ``observability`` unit supplies the ``sink`` that wires
    the metrics/trace stack; this unit only emits (reference-not-own)."""

    def __init__(self, sink: Optional[Callable[[EvaluationTelemetry], None]] = None) -> None:
        self._sink = sink
        self.last: Optional[EvaluationTelemetry] = None

    def emit(self, report: RuleResultReport, evaluate_micros: int) -> EvaluationTelemetry:
        telemetry = build_telemetry(report, evaluate_micros)
        if self._sink is not None:
            self._sink(telemetry)
        self.last = telemetry
        return telemetry
