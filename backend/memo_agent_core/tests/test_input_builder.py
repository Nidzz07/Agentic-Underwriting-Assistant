"""MemoAgentInputBuilder — GROUND-1 (clean artifacts only) + SEC1-1 (no forensic span)."""
from __future__ import annotations

import inspect

from backend.rules_engine.report_schema import Confidence, Recommendation
from backend.memo_agent_core.input_builder import MemoAgentInputBuilder
from backend.memo_agent_core.schemas import MemoAgentInput
from backend.memo_agent_core.tests.fixtures.factories import make_profile, make_report


BUILDER = MemoAgentInputBuilder()


def test_builds_from_clean_artifacts_and_defaults_readonly_from_report():
    report = make_report(recommendation=Recommendation.REFER, confidence=Confidence.MEDIUM)
    result = BUILDER.build(applicant_profile=make_profile(), rule_report=report)
    assert isinstance(result, MemoAgentInput)
    assert result.recommendation is Recommendation.REFER   # injected from the report
    assert result.confidence is Confidence.MEDIUM


def test_readonly_values_can_be_supplied_explicitly():
    report = make_report(recommendation=Recommendation.APPROVE, confidence=Confidence.HIGH)
    result = BUILDER.build(
        applicant_profile=make_profile(),
        rule_report=report,
        recommendation=Recommendation.REFER,
        confidence=Confidence.LOW,
    )
    assert result.recommendation is Recommendation.REFER
    assert result.confidence is Confidence.LOW


def test_builder_has_no_forensic_span_parameter():
    # SEC1-1: no original_span / SanitizationReport parameter can enter the memo path.
    params = list(inspect.signature(MemoAgentInputBuilder.build).parameters)
    assert params == ["self", "applicant_profile", "rule_report", "recommendation", "confidence"]
    assert "original_span" not in params
    assert "sanitization_report" not in params
    assert "report" not in params  # (the rules report is 'rule_report', not a sanitization 'report')


def test_built_input_carries_no_forensic_field():
    result = BUILDER.build(applicant_profile=make_profile(), rule_report=make_report())
    assert "original_span" not in type(result).model_fields
