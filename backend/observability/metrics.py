"""metric-side (C-OBS-2, P-OBS-6/7/4) — the ~5 metric definitions + the TWO structurally
separate derivation paths + the injected exporter (METRIC-1 / STEPMETRIC-1).

``MetricExporter`` is an INJECTED Protocol (an offline fake at tier-U; ``prometheus-client``
binds at composition — ``OBS-SINK-DEFERRED``). ``derive_from_event`` (emitter-sourced, 3 metrics)
and ``derive_from_step_outcome`` (step-outcome, 2 metrics) read their inputs BY SHAPE through
``project_allowlisted`` over DISTINCT allowlist sets — no overlap (P-OBS-7). Every label is an
allowlist scalar (P-OBS-4).

Header note (documentation only, NEVER enforcement): does NOT import ``trace`` (SEP-1); every
label routed through the allowlist; step outcomes read by shape; ``is_outlier`` read BY VALUE
with no ``outlier_model`` import (Req-Fold-2); no ``Recommendation``/verdict type is declared or
produced (CONTRACT-1) — ``recommendation`` appears only as a scalar label VALUE.

CG-OBS-Fold-2: ``recommendation`` is a str-enum value carried by BOTH the memo event and the
rules-engine event. ``decisions_by_recommendation_type`` counts DECISIONS, so its source is the
MEMO event stream (one memo run == one decision, ``domain-entities §4``); which emitter stream
feeds this derivation is composition wiring (``OBS-SINK-DEFERRED``). The field->metric map below
is 1:1 and pure — it maps whatever allowlisted fields it is given.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol

from backend.observability.allowlist import ScalarValue, project_allowlisted

# --- metric kinds ----------------------------------------------------------
COUNTER = "counter"
HISTOGRAM = "histogram"
GAUGE = "gauge"


@dataclass(frozen=True)
class MetricDefinition:
    """A metric's name + kind + the allowlist label keys it may carry (demographic-free)."""

    name: str
    kind: str
    labels: tuple[str, ...] = ()


@dataclass(frozen=True)
class MetricContribution:
    """One derived contribution to a metric — a value + allowlist scalar labels only."""

    metric: str
    value: float
    labels: Mapping[str, ScalarValue] = field(default_factory=dict)


class MetricExporter(Protocol):
    """The injected exporter — a recording fake at tier-U; ``prometheus-client`` at composition."""

    def export(self, contribution: MetricContribution) -> None: ...


# --- the five frozen metric definitions (domain-entities §4) ---------------
DECISIONS_BY_RECOMMENDATION = MetricDefinition(
    "decisions_by_recommendation_type", COUNTER, ("recommendation",)
)
DECISION_LATENCY = MetricDefinition("decision_latency_ms", HISTOGRAM)
RULE_EVALUATION_DURATION = MetricDefinition("rule_evaluation_duration_micros", HISTOGRAM)
LLM_CALL_ERRORS = MetricDefinition("llm_call_errors", COUNTER)
OUTLIER_FLAG = MetricDefinition("outlier_flag", GAUGE)

METRIC_DEFINITIONS: tuple[MetricDefinition, ...] = (
    DECISIONS_BY_RECOMMENDATION,
    DECISION_LATENCY,
    RULE_EVALUATION_DURATION,
    LLM_CALL_ERRORS,
    OUTLIER_FLAG,
)

# emitter-sourced fields (3 metrics). recommendation (memo) / duration_ms (memo) /
# evaluate_micros (rules-engine). Tests parameterize OFF these constants (Q4-A).
_EVENT_ALLOWED: frozenset[str] = frozenset({"recommendation", "duration_ms", "evaluate_micros"})

# step-outcome fields (2 metrics). is_outlier is U18's REAL field (read by value, no import);
# provider_call_error is a Code-Gen realization (no frozen emitter field — LLM-call-error path).
_STEP_ALLOWED: frozenset[str] = frozenset({"is_outlier", "provider_call_error"})


def derive_from_event(fields: Mapping[str, object]) -> list[MetricContribution]:
    """Emitter-sourced derivations (P-OBS-6, 3 metrics), read BY SHAPE over ``_EVENT_ALLOWED``."""
    safe = project_allowlisted(fields, _EVENT_ALLOWED)
    out: list[MetricContribution] = []
    if "recommendation" in safe:
        out.append(
            MetricContribution(
                DECISIONS_BY_RECOMMENDATION.name, 1.0, {"recommendation": safe["recommendation"]}
            )
        )
    if "duration_ms" in safe:
        out.append(MetricContribution(DECISION_LATENCY.name, float(safe["duration_ms"])))
    if "evaluate_micros" in safe:
        out.append(MetricContribution(RULE_EVALUATION_DURATION.name, float(safe["evaluate_micros"])))
    return out


def derive_from_step_outcome(outcome: Mapping[str, object]) -> list[MetricContribution]:
    """Step-outcome derivations (P-OBS-7, 2 metrics), a DISTINCT path over ``_STEP_ALLOWED``.

    Reads ``is_outlier`` BY VALUE (Req-Fold-2) — no ``outlier_model`` import, no Protocol proof.
    """
    safe = project_allowlisted(outcome, _STEP_ALLOWED)
    out: list[MetricContribution] = []
    if "provider_call_error" in safe and bool(safe["provider_call_error"]):
        out.append(MetricContribution(LLM_CALL_ERRORS.name, 1.0))
    if "is_outlier" in safe:
        out.append(MetricContribution(OUTLIER_FLAG.name, 1.0 if bool(safe["is_outlier"]) else 0.0))
    return out
