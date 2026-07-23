"""Tests for the rules-engine output contract (Step 1).

Maps: FD ``domain-entities.md §6`` — implement the frozen shapes EXACTLY
(tri-state ``RuleResult``, the ``RuleResultReport`` with rulebook_version +
content_hash + engine_version + decline/refer reasons, the exact enums incl. the
mandatory ``-RECOMMEND`` suffix). No new field/behaviour beyond the FD.

The shared value types (``Operator`` / ``RuleCategory`` / ``OutcomeTier`` /
``DecimalRange``) live here (the schema leaf) and are imported by
``rulebook_schema`` — a module-placement choice to avoid a circular import.
"""
from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.rules_engine import report_schema as rs


def test_recommendation_enum_values_incl_decline_recommend():
    assert {r.value for r in rs.Recommendation} == {"APPROVE", "REFER", "DECLINE-RECOMMEND"}
    assert rs.Recommendation.DECLINE_RECOMMEND.value == "DECLINE-RECOMMEND"  # suffix mandatory


def test_confidence_enum():
    assert {c.value for c in rs.Confidence} == {"High", "Medium", "Low"}


def test_operator_enum_has_seven():
    assert {o.value for o in rs.Operator} == {"lte", "lt", "gte", "gt", "eq", "in", "between"}


def test_category_enum_has_nine():
    assert {c.value for c in rs.RuleCategory} == {
        "age_eligibility", "medical_bmi", "medical_health", "financial_dti",
        "financial_income_multiple", "document_completeness", "lifestyle_smoking",
        "lifestyle_occupation", "compliance_irdai",
    }


def test_status_and_tier_enums():
    assert {s.value for s in rs.RuleStatus} == {"pass", "fail", "not_evaluated"}
    assert {t.value for t in rs.OutcomeTier} == {"pass_only", "refer_trigger", "decline_fail"}


def test_decimal_range_model():
    dr = rs.DecimalRange(low=Decimal("18"), low_inclusive=True,
                         high=Decimal("65"), high_inclusive=True)
    assert dr.low == Decimal("18") and dr.high_inclusive is True


def test_rule_result_pass_with_decimal_value():
    r = rs.RuleResult(
        rule_id="DTI-001", category=rs.RuleCategory.FINANCIAL_DTI,
        status=rs.RuleStatus.PASS, actual_value=Decimal("0.40"),
        operator=rs.Operator.LTE, threshold=Decimal("0.40"),
        outcome_tier=rs.OutcomeTier.PASS_ONLY, message="DTI within ceiling",
    )
    assert r.status is rs.RuleStatus.PASS
    assert r.actual_value == Decimal("0.40")


def test_rule_result_not_evaluated_has_null_actual_value():
    r = rs.RuleResult(
        rule_id="DTI-001", category=rs.RuleCategory.FINANCIAL_DTI,
        status=rs.RuleStatus.NOT_EVALUATED, actual_value=None,
        operator=rs.Operator.LTE, threshold=Decimal("0.40"),
        outcome_tier=rs.OutcomeTier.REFER_TRIGGER, message="income missing",
    )
    assert r.status is rs.RuleStatus.NOT_EVALUATED
    assert r.actual_value is None


def test_rule_result_threshold_accepts_range_and_set():
    dr = rs.DecimalRange(low=Decimal("18"), low_inclusive=True, high=Decimal("65"), high_inclusive=True)
    r = rs.RuleResult(rule_id="AGE-1", category=rs.RuleCategory.AGE_ELIGIBILITY,
                      status=rs.RuleStatus.PASS, actual_value=Decimal("40"),
                      operator=rs.Operator.BETWEEN, threshold=dr,
                      outcome_tier=rs.OutcomeTier.PASS_ONLY, message="eligible")
    assert isinstance(r.threshold, rs.DecimalRange)
    r2 = rs.RuleResult(rule_id="SMK-1", category=rs.RuleCategory.LIFESTYLE_SMOKING,
                       status=rs.RuleStatus.FAIL, actual_value="smoker",
                       operator=rs.Operator.IN, threshold=["smoker"],
                       outcome_tier=rs.OutcomeTier.REFER_TRIGGER, message="smoker")
    assert r2.threshold == ["smoker"]


def test_rule_result_rejects_float_actual_value():
    with pytest.raises(ValidationError):
        rs.RuleResult(rule_id="X", category=rs.RuleCategory.FINANCIAL_DTI,
                      status=rs.RuleStatus.PASS, actual_value=0.40,  # float -> reject
                      operator=rs.Operator.LTE, threshold=Decimal("0.40"),
                      outcome_tier=rs.OutcomeTier.PASS_ONLY, message="x")


def _sample_report():
    r = rs.RuleResult(rule_id="AGE-1", category=rs.RuleCategory.AGE_ELIGIBILITY,
                      status=rs.RuleStatus.PASS, actual_value=Decimal("40"),
                      operator=rs.Operator.BETWEEN,
                      threshold=rs.DecimalRange(low=Decimal("18"), low_inclusive=True,
                                                high=Decimal("65"), high_inclusive=True),
                      outcome_tier=rs.OutcomeTier.PASS_ONLY, message="eligible")
    return rs.RuleResultReport(
        rule_results=[r], recommendation=rs.Recommendation.APPROVE,
        confidence=rs.Confidence.HIGH, rulebook_version="1.0.0",
        content_hash="abc", engine_version="deadbeef",
        decline_reasons=[], refer_reasons=[],
    )


def test_rule_result_report_shape():
    rep = _sample_report()
    assert rep.recommendation is rs.Recommendation.APPROVE
    assert rep.rulebook_version == "1.0.0"
    assert rep.content_hash == "abc"
    assert rep.engine_version == "deadbeef"
    assert rep.decline_reasons == [] and rep.refer_reasons == []


def test_report_is_frozen_and_forbids_extra():
    rep = _sample_report()
    with pytest.raises(ValidationError):
        rs.RuleResultReport(rule_results=[], recommendation=rs.Recommendation.APPROVE,
                            confidence=rs.Confidence.HIGH, rulebook_version="1",
                            content_hash="h", engine_version="e", surprise="x")
    with pytest.raises((ValidationError, TypeError)):
        rep.recommendation = rs.Recommendation.REFER  # frozen
