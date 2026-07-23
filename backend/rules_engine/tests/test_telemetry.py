"""Tests for TelemetryEmitter (Step 12).

Maps: NFR-RULES-OBS-1 — an allowlist schema that **structurally cannot carry**
demographic / applicant-profile / free-text content (a schema-level assertion:
the only ``str`` leaves are rulebook metadata — ``rulebook_version`` / ``rule_id``
— everything else is an ``int`` count/timing or an ``Enum``); NFR-RULES-PERF-1 —
``evaluate`` timing is **observed-only** (emitted, never gated: no latency-failing
check). Emit-only seam; the ``observability`` unit wires the stack (reference-not-own).
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import get_args, get_origin

import yaml
from pydantic import BaseModel

from backend.common.canon_ser import canon_ser
from backend.intake import schema as isch
from backend.rules_engine.engine import RulesEngine
from backend.rules_engine.loader import RulebookLoader
from backend.rules_engine import report_schema as rs
from backend.rules_engine.telemetry import (
    EvaluationTelemetry,
    RuleStatusEntry,
    TelemetryEmitter,
    build_telemetry,
)


# --------------------------------------------------------------------------
# A report to build telemetry from (via the real engine)
# --------------------------------------------------------------------------
def _report(tmp_path, **profile_over):
    rules = [
        dict(rule_id="DTI-1", category="financial_dti", input_fields=["dti_ratio"],
             operator="lte", threshold="0.40", outcome="decline_fail",
             rationale_message="dti {actual_value} over 0.40"),
        dict(rule_id="OCC-1", category="lifestyle_occupation", input_fields=["occupation"],
             operator="in", threshold=["engineer", "teacher"], outcome="refer_trigger",
             rationale_message="occupation {actual_value}"),
    ]
    (tmp_path / "1.0.0.yaml").write_text(
        yaml.safe_dump(dict(rulebook_version="1.0.0", content_hash="", rules=rules,
                            confidence_bands=dict(high_margin="0.15", low_margin="0.03"))),
        encoding="utf-8",
    )
    kw = dict(
        application_id="APP-1", date_of_birth=date(1986, 1, 1), as_of_date=date(2026, 1, 1),
        age_years_derived=40, bmi_derived=Decimal("22.00"),
        verifiable_income_annual=Decimal("1000000"), requested_cover_amount=Decimal("5000000"),
        existing_debt_obligations_annual=Decimal("500000"),  # dti 0.50 -> decline
        employment_type=isch.EmploymentType.SALARIED, smoking_status=isch.SmokingStatus.NON_SMOKER,
        occupation="spy-in-gotham", health_flags=[], incomplete=False,
        demographics=isch.Demographics(full_name="Bruce Wayne", gender=isch.Gender.MALE, city="Gotham"),
        documents=isch.DocumentManifest(expected_count=3, satisfied_count=3, entries=[]),
    )
    kw.update(profile_over)
    engine = RulesEngine(RulebookLoader(tmp_path), engine_version="eng-1")
    return engine.evaluate(isch.ApplicantProfile(**kw), "1.0.0")


# --------------------------------------------------------------------------
# OBS-1 — structural: the ONLY str leaves are rulebook metadata
# --------------------------------------------------------------------------
def _leaf_types(model, str_fields, other_non_enum):
    for name, field in model.model_fields.items():
        ann = field.annotation
        inner = get_args(ann)[0] if get_origin(ann) in (list, tuple) and get_args(ann) else ann
        if isinstance(inner, type) and issubclass(inner, BaseModel):
            _leaf_types(inner, str_fields, other_non_enum)
        elif inner is str:
            str_fields.add(name)
        elif inner is int or (isinstance(inner, type) and issubclass(inner, Enum)):
            continue
        else:
            other_non_enum.add((name, inner))


def test_only_str_leaves_are_rulebook_metadata():
    str_fields, other = set(), set()
    _leaf_types(EvaluationTelemetry, str_fields, other)
    assert str_fields == {"rulebook_version", "rule_id"}   # rulebook metadata only
    assert other == set()                                  # everything else is int | Enum


def test_no_demographic_or_free_text_field_names():
    names = set(EvaluationTelemetry.model_fields) | set(RuleStatusEntry.model_fields)
    forbidden = {
        "message", "actual_value", "full_name", "name", "gender", "city", "occupation",
        "health_flags", "clean_text", "original_span", "demographics", "income", "bmi",
        "age_years_derived", "threshold",
    }
    assert names & forbidden == set()


def test_schema_forbids_extra_fields():
    # extra="forbid" -> a sneaked-in free-text field is structurally rejected.
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        EvaluationTelemetry(
            rulebook_version="1.0.0", recommendation=rs.Recommendation.APPROVE,
            confidence=rs.Confidence.HIGH, rule_count=0, pass_count=0,
            not_evaluated_count=0, decline_count=0, refer_count=0,
            evaluate_micros=1, per_rule=[], applicant_name="leak",  # noqa
        )


# --------------------------------------------------------------------------
# OBS-1 — no applicant free-text (message / actual_value / demographic) leaks
# --------------------------------------------------------------------------
def test_telemetry_bytes_carry_no_applicant_free_text(tmp_path):
    report = _report(tmp_path)
    tel = build_telemetry(report, evaluate_micros=42)
    blob = canon_ser(tel.model_dump()).decode("utf-8")
    # message text, the exact actual_value, occupation, and demographics never appear
    assert "0.50" not in blob and "0.5000" not in blob    # actual_value / message excluded
    assert "spy-in-gotham" not in blob                    # occupation excluded
    assert "Bruce" not in blob and "Gotham" not in blob   # demographics excluded
    assert "dti" not in blob                              # rationale message excluded


def test_telemetry_carries_counts_enums_and_metadata(tmp_path):
    report = _report(tmp_path)
    tel = build_telemetry(report, evaluate_micros=99)
    assert tel.rulebook_version == "1.0.0"
    assert tel.recommendation is rs.Recommendation.DECLINE_RECOMMEND
    assert tel.rule_count == 2
    assert tel.decline_count == len(report.decline_reasons)
    assert tel.refer_count == len(report.refer_reasons)
    assert {e.rule_id for e in tel.per_rule} == {"DTI-1", "OCC-1"}
    assert all(isinstance(e.status, rs.RuleStatus) for e in tel.per_rule)


# --------------------------------------------------------------------------
# Emit-only seam + PERF-1 observed-not-gated
# --------------------------------------------------------------------------
def test_emit_pushes_to_sink_and_records_last(tmp_path):
    captured = []
    emitter = TelemetryEmitter(sink=captured.append)
    tel = emitter.emit(_report(tmp_path), evaluate_micros=7)
    assert captured == [tel]
    assert emitter.last is tel


def test_emit_without_sink_is_noop_but_records(tmp_path):
    emitter = TelemetryEmitter()          # reference-not-own: no stack configured here
    tel = emitter.emit(_report(tmp_path), evaluate_micros=7)
    assert emitter.last is tel


def test_perf_timing_observed_not_gated(tmp_path):
    # An enormous duration is emitted, never raises / fails a latency check (PERF-1).
    tel = build_telemetry(_report(tmp_path), evaluate_micros=10**12)
    assert tel.evaluate_micros == 10**12
