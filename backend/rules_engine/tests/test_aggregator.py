"""Tests for Aggregator (Step 8).

Maps: NFR-RULES-AGG-1 — order-independent fixed precedence
(DECLINE > REFER > APPROVE) proved via a Hypothesis permutation of the tier set;
``incomplete`` / ``not_evaluated`` contribute only ``refer_trigger`` (thin-file →
REFER, never DECLINE); ``decline_reasons`` / ``refer_reasons`` collected in the
one canonical order (feeds DET-2). The ``-RECOMMEND`` suffix is mandatory.
"""
from __future__ import annotations

from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from backend.rules_engine import report_schema as rs
from backend.rules_engine.aggregator import INCOMPLETE_REASON, aggregate


def _res(rule_id, tier, msg="m"):
    status = rs.RuleStatus.PASS if tier is rs.OutcomeTier.PASS_ONLY else rs.RuleStatus.FAIL
    if tier is rs.OutcomeTier.REFER_TRIGGER:
        status = rs.RuleStatus.NOT_EVALUATED  # a common refer source
    return rs.RuleResult(
        rule_id=rule_id, category=rs.RuleCategory.FINANCIAL_DTI, status=status,
        actual_value=None, operator=rs.Operator.LTE, threshold=Decimal("0"),
        outcome_tier=tier, message=msg,
    )


_PASS = lambda i: _res(f"P{i}", rs.OutcomeTier.PASS_ONLY)
_REFER = lambda i: _res(f"R{i}", rs.OutcomeTier.REFER_TRIGGER)
_DECLINE = lambda i: _res(f"D{i}", rs.OutcomeTier.DECLINE_FAIL)


# --------------------------------------------------------------------------
# Fixed precedence
# --------------------------------------------------------------------------
def test_all_pass_is_approve():
    out = aggregate([_PASS(1), _PASS(2)], incomplete=False)
    assert out.recommendation is rs.Recommendation.APPROVE
    assert out.decline_reasons == [] and out.refer_reasons == []


def test_any_refer_is_refer():
    out = aggregate([_PASS(1), _REFER(1)], incomplete=False)
    assert out.recommendation is rs.Recommendation.REFER


def test_any_decline_is_decline_recommend():
    out = aggregate([_PASS(1), _DECLINE(1)], incomplete=False)
    assert out.recommendation is rs.Recommendation.DECLINE_RECOMMEND
    assert out.recommendation.value == "DECLINE-RECOMMEND"   # -RECOMMEND suffix


def test_decline_dominates_refer():
    out = aggregate([_REFER(1), _DECLINE(1), _PASS(1)], incomplete=False)
    assert out.recommendation is rs.Recommendation.DECLINE_RECOMMEND


# --------------------------------------------------------------------------
# incomplete / thin-file -> REFER, never DECLINE
# --------------------------------------------------------------------------
def test_incomplete_alone_is_refer_not_decline():
    out = aggregate([_PASS(1), _PASS(2)], incomplete=True)
    assert out.recommendation is rs.Recommendation.REFER
    assert INCOMPLETE_REASON in out.refer_reasons


def test_thin_file_not_evaluated_plus_incomplete_is_refer():
    out = aggregate([_REFER(1), _PASS(1)], incomplete=True)
    assert out.recommendation is rs.Recommendation.REFER


def test_decline_dominates_even_when_incomplete():
    out = aggregate([_DECLINE(1)], incomplete=True)
    assert out.recommendation is rs.Recommendation.DECLINE_RECOMMEND


# --------------------------------------------------------------------------
# Reasons — collected, canonical order
# --------------------------------------------------------------------------
def test_reasons_collected_by_tier():
    out = aggregate([_DECLINE(1), _REFER(1), _PASS(1)], incomplete=True)
    assert any(r.startswith("D1:") for r in out.decline_reasons)
    assert any(r.startswith("R1:") for r in out.refer_reasons)
    assert INCOMPLETE_REASON in out.refer_reasons
    # pass rules never become a reason
    assert not any("P1" in r for r in out.decline_reasons + out.refer_reasons)


def test_reasons_in_canonical_sorted_order():
    results = [_DECLINE(3), _DECLINE(1), _DECLINE(2)]
    out = aggregate(results, incomplete=False)
    assert out.decline_reasons == sorted(out.decline_reasons)


# --------------------------------------------------------------------------
# AGG-1 — order-independence under permutation (Hypothesis)
# --------------------------------------------------------------------------
_FIXED = [_DECLINE(2), _REFER(3), _PASS(1), _REFER(1), _DECLINE(1), _PASS(2)]


@given(order=st.permutations(_FIXED), incomplete=st.booleans())
def test_recommendation_and_reasons_are_permutation_invariant(order, incomplete):
    baseline = aggregate(_FIXED, incomplete=incomplete)
    permuted = aggregate(list(order), incomplete=incomplete)
    assert permuted.recommendation is baseline.recommendation
    assert permuted.decline_reasons == baseline.decline_reasons
    assert permuted.refer_reasons == baseline.refer_reasons


@given(order=st.permutations([_REFER(1), _REFER(2), _PASS(1)]))
def test_incomplete_only_refers_never_declines_any_order(order):
    out = aggregate(list(order), incomplete=True)
    assert out.recommendation is rs.Recommendation.REFER  # never DECLINE on refer+incomplete
