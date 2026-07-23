"""Tests for ConfidenceBander (Step 9).

Maps: NFR-RULES-CONF-1 — deterministic ``confidence ∈ {High, Medium, Low}`` as a
pure function of numeric-value proximity + completeness over the FIXED versioned
``ConfidenceBands`` constants; identical inputs → identical band ×N;
order-independent; never LLM. FD ``business-rules.md §4`` / ``domain-entities.md §5``.
"""
from __future__ import annotations

from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from backend.rules_engine import report_schema as rs
from backend.rules_engine import rulebook_schema as ks
from backend.rules_engine.confidence import band_confidence

_BANDS = ks.ConfidenceBands(high_margin=Decimal("0.15"), low_margin=Decimal("0.03"))


def _num(rule_id, actual, threshold, status=rs.RuleStatus.PASS):
    return rs.RuleResult(
        rule_id=rule_id, category=rs.RuleCategory.FINANCIAL_DTI, status=status,
        actual_value=None if status is rs.RuleStatus.NOT_EVALUATED else Decimal(actual),
        operator=rs.Operator.LTE, threshold=Decimal(threshold),
        outcome_tier=rs.OutcomeTier.PASS_ONLY if status is rs.RuleStatus.PASS
        else rs.OutcomeTier.REFER_TRIGGER,
        message="m",
    )


def _cat(rule_id):  # categorical pass — no proximity, ignored for banding
    return rs.RuleResult(
        rule_id=rule_id, category=rs.RuleCategory.LIFESTYLE_SMOKING, status=rs.RuleStatus.PASS,
        actual_value="non_smoker", operator=rs.Operator.IN, threshold=["non_smoker"],
        outcome_tier=rs.OutcomeTier.PASS_ONLY, message="m",
    )


_CLEAR = _num("C", "0.10", "0.40")     # dist 0.30 -> clear of high_margin
_NEAR = _num("N", "0.35", "0.40")      # dist 0.05 -> within high_margin, not low
_VERY_NEAR = _num("V", "0.39", "0.40")  # dist 0.01 -> within low_margin


def test_all_clear_and_complete_is_high():
    assert band_confidence([_CLEAR, _cat("S")], incomplete=False, bands=_BANDS) is rs.Confidence.HIGH


def test_single_near_boundary_is_medium():
    assert band_confidence([_CLEAR, _NEAR], incomplete=False, bands=_BANDS) is rs.Confidence.MEDIUM


def test_multiple_near_boundary_is_low():
    near2 = _num("N2", "0.36", "0.40")
    assert band_confidence([_NEAR, near2], incomplete=False, bands=_BANDS) is rs.Confidence.LOW


def test_at_or_under_low_margin_is_low():
    assert band_confidence([_CLEAR, _VERY_NEAR], incomplete=False, bands=_BANDS) is rs.Confidence.LOW


def test_not_evaluated_material_incompleteness_is_low():
    ne = _num("NE", "0", "0.40", status=rs.RuleStatus.NOT_EVALUATED)
    assert band_confidence([_CLEAR, ne], incomplete=False, bands=_BANDS) is rs.Confidence.LOW


def test_incomplete_flag_single_incompleteness_is_medium():
    assert band_confidence([_CLEAR], incomplete=True, bands=_BANDS) is rs.Confidence.MEDIUM


def test_between_range_proximity_uses_nearest_bound():
    rng = rs.DecimalRange(low=Decimal("18"), low_inclusive=True,
                          high=Decimal("65"), high_inclusive=True)
    near_low = rs.RuleResult(
        rule_id="AGE", category=rs.RuleCategory.AGE_ELIGIBILITY, status=rs.RuleStatus.PASS,
        actual_value=Decimal("19"), operator=rs.Operator.BETWEEN, threshold=rng,
        outcome_tier=rs.OutcomeTier.PASS_ONLY, message="m",
    )  # dist to 18 = 1, /18 ≈ 0.055 -> near (medium), not low
    assert band_confidence([near_low], incomplete=False, bands=_BANDS) is rs.Confidence.MEDIUM


def test_categorical_results_do_not_create_near_hits():
    assert band_confidence([_cat("S1"), _cat("S2")], incomplete=False, bands=_BANDS) is rs.Confidence.HIGH


def test_numeric_actual_with_list_threshold_has_no_proximity():
    # Defensive branch: a Decimal actual paired with a list threshold yields no
    # numeric proximity (returns None) -> contributes no near hit -> High.
    odd = rs.RuleResult(
        rule_id="ODD", category=rs.RuleCategory.FINANCIAL_DTI, status=rs.RuleStatus.PASS,
        actual_value=Decimal("5"), operator=rs.Operator.IN, threshold=["a", "b"],
        outcome_tier=rs.OutcomeTier.PASS_ONLY, message="m",
    )
    assert band_confidence([odd], incomplete=False, bands=_BANDS) is rs.Confidence.HIGH


# --------------------------------------------------------------------------
# Determinism + order-independence
# --------------------------------------------------------------------------
def test_deterministic_across_ten_runs():
    results = [_CLEAR, _NEAR, _cat("S")]
    first = band_confidence(results, incomplete=False, bands=_BANDS)
    for _ in range(10):
        assert band_confidence(results, incomplete=False, bands=_BANDS) is first


@given(order=st.permutations([_CLEAR, _NEAR, _VERY_NEAR, _cat("S")]), incomplete=st.booleans())
def test_confidence_is_permutation_invariant(order, incomplete):
    baseline = band_confidence([_CLEAR, _NEAR, _VERY_NEAR, _cat("S")], incomplete=incomplete, bands=_BANDS)
    assert band_confidence(list(order), incomplete=incomplete, bands=_BANDS) is baseline
