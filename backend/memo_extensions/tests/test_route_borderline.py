"""NFR-MEXT-ROUTE-1 (LOAD-BEARING, full-highest) — deterministic, LLM-free, provider-free
borderline routing (BR-MEXT-1). Purity teeth + trigger teeth + boundary teeth + the
constants-parameterized-off-the-named-constant discipline. The AST import-allow-list scan
lives in ``test_structural_guard.py``.
"""
from __future__ import annotations

from decimal import Decimal

from backend.memo_agent_core.schemas import ThinkingMode
from backend.rules_engine.report_schema import Recommendation
from backend.memo_extensions.borderline_router import (
    OUTLIER_SCORE_CUTOFF,
    RULE_PROXIMITY_MARGIN,
    route_borderline,
)
from backend.memo_extensions.tests import fixtures as fx


def _report_with_actual(actual: Decimal, *, recommendation=Recommendation.APPROVE):
    return fx.make_report(
        rule_results=[fx.make_rule_result(actual_value=actual, threshold=Decimal("0.40"))],
        recommendation=recommendation,
    )


# -- constants ---------------------------------------------------------------
def test_constants_are_single_named_floats():
    assert isinstance(RULE_PROXIMITY_MARGIN, float)
    assert isinstance(OUTLIER_SCORE_CUTOFF, float)


# -- purity ------------------------------------------------------------------
def test_purity_same_inputs_same_mode_across_calls():
    report = _report_with_actual(Decimal("0.20"))
    signal = fx.FakeOutlierSignal(is_outlier=False, outlier_score=0.1)
    first = route_borderline(report, signal)
    second = route_borderline(report, signal)
    assert first is second  # identical ThinkingMode, no retained state
    assert first is ThinkingMode.STANDARD


def test_purity_no_state_retained_between_differing_calls():
    far = _report_with_actual(Decimal("0.20"))
    refer = _report_with_actual(Decimal("0.20"), recommendation=Recommendation.REFER)
    assert route_borderline(refer) is ThinkingMode.EXTENDED
    # a prior EXTENDED call must not leak into the next STANDARD one
    assert route_borderline(far) is ThinkingMode.STANDARD


# -- trigger teeth -----------------------------------------------------------
def test_refer_routes_extended():
    report = _report_with_actual(Decimal("0.20"), recommendation=Recommendation.REFER)
    assert route_borderline(report) is ThinkingMode.EXTENDED


def test_rule_proximity_within_margin_routes_extended():
    # relative distance strictly INSIDE the margin (half of it)
    inside = Decimal("0.40") * (Decimal("1") - Decimal(str(RULE_PROXIMITY_MARGIN / 2)))
    assert route_borderline(_report_with_actual(inside)) is ThinkingMode.EXTENDED


def test_rule_proximity_outside_margin_routes_standard():
    # relative distance clearly OUTSIDE the margin (double it)
    outside = Decimal("0.40") * (Decimal("1") - Decimal(str(RULE_PROXIMITY_MARGIN * 2)))
    assert route_borderline(_report_with_actual(outside)) is ThinkingMode.STANDARD


def test_outlier_score_above_cutoff_routes_extended():
    report = _report_with_actual(Decimal("0.20"))
    signal = fx.FakeOutlierSignal(is_outlier=True, outlier_score=OUTLIER_SCORE_CUTOFF + 0.1)
    assert route_borderline(report, signal) is ThinkingMode.EXTENDED


def test_outlier_score_below_cutoff_routes_standard():
    report = _report_with_actual(Decimal("0.20"))
    signal = fx.FakeOutlierSignal(is_outlier=False, outlier_score=OUTLIER_SCORE_CUTOFF - 0.1)
    assert route_borderline(report, signal) is ThinkingMode.STANDARD


# -- boundary teeth (<= / >= explicit, parameterized OFF the named constant) --
def test_rule_proximity_exactly_at_margin_is_inclusive_extended():
    at_boundary = Decimal("0.40") * (Decimal("1") - Decimal(str(RULE_PROXIMITY_MARGIN)))
    assert route_borderline(_report_with_actual(at_boundary)) is ThinkingMode.EXTENDED


def test_outlier_score_exactly_at_cutoff_is_inclusive_extended():
    report = _report_with_actual(Decimal("0.20"))
    signal = fx.FakeOutlierSignal(is_outlier=True, outlier_score=OUTLIER_SCORE_CUTOFF)
    assert route_borderline(report, signal) is ThinkingMode.EXTENDED


def test_range_threshold_proximity_uses_both_bounds():
    bounds = fx.rrs.DecimalRange(
        low=Decimal("18"), low_inclusive=True, high=Decimal("65"), high_inclusive=True
    )
    near_high = Decimal("65") * (Decimal("1") - Decimal(str(RULE_PROXIMITY_MARGIN / 2)))
    report = fx.make_report(
        rule_results=[
            fx.make_rule_result(actual_value=near_high, operator=fx.rrs.Operator.BETWEEN, threshold=bounds)
        ],
        recommendation=Recommendation.APPROVE,
    )
    assert route_borderline(report) is ThinkingMode.EXTENDED


def test_list_threshold_contributes_no_numeric_proximity():
    report = fx.make_report(
        rule_results=[
            fx.make_rule_result(
                actual_value=Decimal("1"), operator=fx.rrs.Operator.IN, threshold=[Decimal("1"), Decimal("2")]
            )
        ],
        recommendation=Recommendation.APPROVE,
    )
    assert route_borderline(report) is ThinkingMode.STANDARD


def test_zero_bound_threshold_uses_absolute_proximity():
    report = fx.make_report(
        rule_results=[
            fx.make_rule_result(actual_value=Decimal("0"), operator=fx.rrs.Operator.GTE, threshold=Decimal("0"))
        ],
        recommendation=Recommendation.APPROVE,
    )
    assert route_borderline(report) is ThinkingMode.EXTENDED


def test_non_numeric_actual_value_carries_no_proximity():
    # a categorical (str) actual value against a set threshold is skipped by proximity
    report = fx.make_report(
        rule_results=[
            fx.make_rule_result(
                actual_value="smoker", operator=fx.rrs.Operator.IN, threshold=["smoker", "non_smoker"]
            )
        ],
        recommendation=Recommendation.APPROVE,
    )
    assert route_borderline(report) is ThinkingMode.STANDARD
