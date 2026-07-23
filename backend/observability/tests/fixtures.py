"""Shared tier-U fixtures (Q2-A) — capturing offline doubles + by-value event/step-outcome
fixtures. NO live SDK, NO network, NO key, NO Docker (TIERU-1). Nothing here imports a frozen
event type (SHAPE-1) — every fixture is a plain mapping shaped BY VALUE.

The grounded graph-path node sequences (Q3-A) are U4's ACTUAL node names, referenced not invented:
``orchestrator.py`` = ``draft -> validate -> {finalize | draft (retry) | flag}``.
"""
from __future__ import annotations

from typing import Mapping

from backend.observability.metrics import MetricContribution
from backend.observability.trace import ScalarValue


# --- capturing trace sink (offline recording fake) -------------------------
class RecordingTraceSink:
    """Implements the ``TraceSink`` Protocol by capturing every ``record_span`` call."""

    def __init__(self) -> None:
        self.spans: list[tuple[str, Mapping[str, ScalarValue]]] = []

    def record_span(self, step_name: str, attributes: Mapping[str, ScalarValue]) -> None:
        self.spans.append((step_name, dict(attributes)))

    @property
    def step_names(self) -> list[str]:
        return [name for name, _ in self.spans]


# --- capturing metric exporter (offline recording fake) --------------------
class RecordingMetricExporter:
    """Implements the ``MetricExporter`` Protocol by collecting every exported contribution."""

    def __init__(self) -> None:
        self.contributions: list[MetricContribution] = []

    def export(self, contribution: MetricContribution) -> None:
        self.contributions.append(contribution)


# --- grounded graph-path node sequences (Q3-A, by value from orchestrator.py) ---
# finalize path: draft -> validate -> finalize (3 node executions)
FINALIZE_SEQUENCE: tuple[str, ...] = ("draft", "validate", "finalize")
# retry-then-flag path at CAP=2: draft -> validate -> draft -> validate -> flag (5 executions)
RETRY_THEN_FLAG_SEQUENCE: tuple[str, ...] = ("draft", "validate", "draft", "validate", "flag")


# --- by-value emitter-event fixtures (distinct families, Q2-A) -------------
def memo_event_fields() -> dict[str, object]:
    """A ``MemoTelemetryEvent``-shaped mapping BY VALUE (recommendation + duration_ms + siblings)."""
    return {
        "application_id": "APP-001",       # id — NOT in _EVENT_ALLOWED (not a metric source)
        "recommendation": "APPROVE",       # str-enum VALUE
        "confidence": "High",
        "outcome": "finalized",
        "cited_rule_count": 4,
        "missing_info_count": 0,
        "draft_attempts": 1,
        "duration_ms": 1234,               # timing
    }


def rules_event_fields() -> dict[str, object]:
    """An ``EvaluationTelemetry``-shaped mapping BY VALUE exposing ``evaluate_micros``."""
    return {
        "rulebook_version": "1.4.0",
        "rule_count": 30,
        "pass_count": 28,
        "evaluate_micros": 4200,           # timing (rule-evaluation duration source)
    }


# --- by-value step-outcome fixtures (distinct family, Q2-A / Req-Fold-2) ----
def outlier_step_outcome(*, is_outlier: bool = True) -> dict[str, object]:
    """A step outcome exposing ``is_outlier`` BY VALUE (U18's real field; no ``outlier_model`` import)."""
    return {"is_outlier": is_outlier, "outlier_score": 0.73}


def provider_error_step_outcome(*, error: bool = True) -> dict[str, object]:
    """A provider-call step outcome exposing the LLM-call-error marker (Code-Gen realization)."""
    return {"provider_call_error": error}


# --- a forbidden-attribute event (for the DEMOFREE / detector self-tests) ---
def event_with_forbidden_attribute() -> dict[str, object]:
    """A memo-shaped event that ALSO carries a demographic / free-text / object field which the
    allowlist MUST drop (never reaching a span or a label)."""
    fields = memo_event_fields()
    fields.update(
        {
            "full_name": "Jane Doe",           # demographic — must be dropped
            "city": "Mumbai",                  # demographic — must be dropped
            "original_span": object(),         # non-scalar object — must be dropped
            "memo_prose": "free text summary", # free-text — dropped (not in any allowlist)
        }
    )
    return fields
