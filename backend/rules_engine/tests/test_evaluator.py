"""Tests for RuleEvaluator (Step 7).

Maps: NFR-RULES-DET-1 (same-order ×N≥10 → byte-identical results), NFR-RULES-BND-1
(boundary exactness — age 18/65 inclusive, BMI 25→overweight / 30→obese, DTI 0.40
pass / 0.4001 fail; exact ``actual_value`` + ``operator`` recorded), FD
``business-rules.md §1`` + ``business-logic-model.md §2`` (tri-state RuleResult;
operands resolved ONLY from ``input_fields``; ``not_evaluated`` → ``refer_trigger``).

Sharpening 2: the ALL-SEVEN-operators coverage (gt/eq included, not just the
category rules) is exercised here.
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from backend.common.canon_ser import canon_ser
from backend.intake.schema import DocumentManifest, EmploymentType, SmokingStatus
from backend.rules_engine import report_schema as rs
from backend.rules_engine import rulebook_schema as ks
from backend.rules_engine.evaluator import evaluate_rules


# --------------------------------------------------------------------------
# Builders
# --------------------------------------------------------------------------
def _ns(**over):
    ns = dict(
        age_years_derived=40,
        bmi_derived=Decimal("22.00"),
        verifiable_income_annual=Decimal("1000000"),
        existing_debt_obligations_annual=Decimal("300000"),
        requested_cover_amount=Decimal("5000000"),
        employment_type=EmploymentType.SALARIED,
        smoking_status=SmokingStatus.NON_SMOKER,
        occupation="engineer",
        health_flags=["none"],
        documents=DocumentManifest(expected_count=3, satisfied_count=3, entries=[]),
        dti_ratio=Decimal("0.3000"),
        income_multiple=Decimal("5.0000"),
    )
    ns.update(over)
    return ns


def _rule(rule_id, operator, threshold, input_fields, *, category=rs.RuleCategory.FINANCIAL_DTI,
          outcome=rs.OutcomeTier.DECLINE_FAIL, msg="{actual_value} vs {threshold}"):
    return ks.Rule(rule_id=rule_id, category=category, input_fields=input_fields,
                   operator=operator, threshold=threshold, outcome=outcome,
                   rationale_message=msg)


def _rulebook(rules):
    return ks.Rulebook(rulebook_version="1.0.0", content_hash="", rules=rules,
                       confidence_bands=ks.ConfidenceBands(high_margin=Decimal("0.15"),
                                                           low_margin=Decimal("0.03")))


_AGE_RULE = _rule("AGE-1", ks.Operator.BETWEEN,
                  rs.DecimalRange(low=Decimal("18"), low_inclusive=True,
                                  high=Decimal("65"), high_inclusive=True),
                  ["age_years_derived"], category=rs.RuleCategory.AGE_ELIGIBILITY)


def _one(rule, ns):
    results = evaluate_rules(_rulebook([rule]), ns)
    assert len(results) == 1
    return results[0]


# --------------------------------------------------------------------------
# BND-1 — age boundaries (between, both inclusive)
# --------------------------------------------------------------------------
@pytest.mark.parametrize("age,passes", [(18, True), (65, True), (17, False), (66, False), (40, True)])
def test_age_boundary_inclusive(age, passes):
    r = _one(_AGE_RULE, _ns(age_years_derived=age))
    assert (r.status is rs.RuleStatus.PASS) == passes
    assert r.actual_value == Decimal(age)          # exact value recorded
    assert r.operator is ks.Operator.BETWEEN
    assert r.outcome_tier == (rs.OutcomeTier.PASS_ONLY if passes else rs.OutcomeTier.DECLINE_FAIL)


# --------------------------------------------------------------------------
# BND-1 — BMI bands: 25.00 -> overweight (not normal); 30.00 -> obese
# --------------------------------------------------------------------------
def _bmi_normal():   # normal iff bmi < 25
    return _rule("BMI-N", ks.Operator.LT, Decimal("25"), ["bmi_derived"],
                 category=rs.RuleCategory.MEDICAL_BMI, outcome=rs.OutcomeTier.REFER_TRIGGER)


def _bmi_overweight():  # 25 <= bmi < 30
    return _rule("BMI-O", ks.Operator.BETWEEN,
                 rs.DecimalRange(low=Decimal("25"), low_inclusive=True,
                                 high=Decimal("30"), high_inclusive=False),
                 ["bmi_derived"], category=rs.RuleCategory.MEDICAL_BMI,
                 outcome=rs.OutcomeTier.REFER_TRIGGER)


def _bmi_obese():   # bmi >= 30
    return _rule("BMI-B", ks.Operator.GTE, Decimal("30"), ["bmi_derived"],
                 category=rs.RuleCategory.MEDICAL_BMI, outcome=rs.OutcomeTier.DECLINE_FAIL)


def test_bmi_25_is_overweight_not_normal():
    ns = _ns(bmi_derived=Decimal("25.00"))
    assert _one(_bmi_normal(), ns).status is rs.RuleStatus.FAIL       # not < 25
    assert _one(_bmi_overweight(), ns).status is rs.RuleStatus.PASS   # 25 <= 25 < 30
    assert _one(_bmi_obese(), ns).status is rs.RuleStatus.FAIL        # not >= 30


def test_bmi_30_is_obese():
    ns = _ns(bmi_derived=Decimal("30.00"))
    assert _one(_bmi_obese(), ns).status is rs.RuleStatus.PASS        # >= 30
    assert _one(_bmi_overweight(), ns).status is rs.RuleStatus.FAIL   # high-exclusive at 30


# --------------------------------------------------------------------------
# BND-1 — DTI 0.40 passes, 0.4001 fails
# --------------------------------------------------------------------------
def _dti_rule():
    return _rule("DTI-1", ks.Operator.LTE, Decimal("0.40"), ["dti_ratio"])


@pytest.mark.parametrize("dti,passes", [("0.4000", True), ("0.4001", False), ("0.3999", True)])
def test_dti_ceiling_exact(dti, passes):
    r = _one(_dti_rule(), _ns(dti_ratio=Decimal(dti)))
    assert (r.status is rs.RuleStatus.PASS) == passes
    assert r.actual_value == Decimal(dti)
    assert r.threshold == Decimal("0.40")


# --------------------------------------------------------------------------
# Tri-state — missing operand -> not_evaluated + refer_trigger + null value
# --------------------------------------------------------------------------
def test_missing_operand_is_not_evaluated_refer_trigger():
    r = _one(_dti_rule(), _ns(dti_ratio=None))
    assert r.status is rs.RuleStatus.NOT_EVALUATED
    assert r.outcome_tier is rs.OutcomeTier.REFER_TRIGGER   # never decline on missing
    assert r.actual_value is None


def test_message_renders_actual_and_threshold():
    r = _one(_dti_rule(), _ns(dti_ratio=Decimal("0.4001")))
    assert "0.4001" in r.message and "0.40" in r.message


def test_message_with_unknown_placeholder_returned_verbatim():
    # A template referencing an unknown key must not crash — returned as-is.
    rule = _rule("BADMSG", ks.Operator.LTE, Decimal("0.40"), ["dti_ratio"],
                 msg="dti check {not_a_real_key}")
    r = _one(rule, _ns(dti_ratio=Decimal("0.30")))
    assert r.message == "dti check {not_a_real_key}"


# --------------------------------------------------------------------------
# All SEVEN operators exercised (sharpening 2)
# --------------------------------------------------------------------------
def test_all_seven_operators_exercised():
    rules = [
        _rule("OP-lte", ks.Operator.LTE, Decimal("0.40"), ["dti_ratio"]),
        _rule("OP-lt", ks.Operator.LT, Decimal("25"), ["bmi_derived"],
              category=rs.RuleCategory.MEDICAL_BMI),
        _rule("OP-gte", ks.Operator.GTE, Decimal("30"), ["bmi_derived"],
              category=rs.RuleCategory.MEDICAL_BMI),
        _rule("OP-gt", ks.Operator.GT, Decimal("65"), ["age_years_derived"],
              category=rs.RuleCategory.AGE_ELIGIBILITY),
        _rule("OP-eq", ks.Operator.EQ, Decimal("40"), ["age_years_derived"],
              category=rs.RuleCategory.AGE_ELIGIBILITY),
        _rule("OP-in", ks.Operator.IN, ["self_employed", "contract"], ["employment_type"],
              category=rs.RuleCategory.FINANCIAL_INCOME_MULTIPLE, outcome=rs.OutcomeTier.REFER_TRIGGER),
        _AGE_RULE,  # between
    ]
    results = evaluate_rules(_rulebook(rules), _ns())
    seen = {r.operator for r in results}
    assert seen == set(ks.Operator)          # all 7 operators present
    assert len(results) == 7
    assert all(r.status is not rs.RuleStatus.NOT_EVALUATED for r in results)


def test_in_operator_enum_membership():
    rule = _rule("SMOKE", ks.Operator.IN, ["smoker"], ["smoking_status"],
                 category=rs.RuleCategory.LIFESTYLE_SMOKING, outcome=rs.OutcomeTier.REFER_TRIGGER)
    assert _one(rule, _ns(smoking_status=SmokingStatus.SMOKER)).status is rs.RuleStatus.PASS
    r = _one(rule, _ns(smoking_status=SmokingStatus.NON_SMOKER))
    assert r.status is rs.RuleStatus.FAIL
    assert r.actual_value == "non_smoker"    # enum recorded by its .value


def test_eq_categorical_threshold_recorded_as_singleton_list():
    # eq x on a categorical ≡ in {x}; the recorded threshold is a singleton list
    # so it fits the report ThresholdRepr (no bare str).
    rule = _rule("EQC", ks.Operator.EQ, "smoker", ["smoking_status"],
                 category=rs.RuleCategory.LIFESTYLE_SMOKING, outcome=rs.OutcomeTier.REFER_TRIGGER)
    r = _one(rule, _ns(smoking_status=SmokingStatus.SMOKER))
    assert r.status is rs.RuleStatus.PASS
    assert r.threshold == ["smoker"]


# --------------------------------------------------------------------------
# pass -> pass_only tier; fail -> the rule's outcome tier
# --------------------------------------------------------------------------
def test_pass_gives_pass_only_fail_gives_rule_outcome():
    passing = _one(_dti_rule(), _ns(dti_ratio=Decimal("0.30")))
    assert passing.outcome_tier is rs.OutcomeTier.PASS_ONLY
    failing = _one(_dti_rule(), _ns(dti_ratio=Decimal("0.50")))
    assert failing.outcome_tier is rs.OutcomeTier.DECLINE_FAIL   # == rule.outcome


# --------------------------------------------------------------------------
# Determinism + canonical order
# --------------------------------------------------------------------------
def test_results_sorted_by_rule_id_regardless_of_authoring_order():
    rules = [_dti_rule(), _AGE_RULE, _bmi_obese()]  # ids: DTI-1, AGE-1, BMI-B
    results = evaluate_rules(_rulebook(rules), _ns())
    assert [r.rule_id for r in results] == sorted(r.rule_id for r in rules)


def test_det1_byte_identical_across_ten_runs():
    rules = [_dti_rule(), _AGE_RULE, _bmi_overweight()]
    rb, ns = _rulebook(rules), _ns(bmi_derived=Decimal("25.00"))
    baseline = evaluate_rules(rb, ns)
    baseline_bytes = canon_ser([r.model_dump() for r in baseline])
    for _ in range(10):
        again = evaluate_rules(rb, ns)
        assert again == baseline
        assert canon_ser([r.model_dump() for r in again]) == baseline_bytes


def test_only_named_input_fields_are_read():
    # A rule naming ONLY dti_ratio is unaffected by a change to a non-named field.
    rule = _dti_rule()
    r1 = _one(rule, _ns(age_years_derived=40))
    r2 = _one(rule, _ns(age_years_derived=99))
    assert r1 == r2
