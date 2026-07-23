"""Tests for the rulebook input schema + load validators (Step 2).

Maps: NFR-RULES-BR1-1 (input_fields allowlist — demographic/unknown field
rejected, as a Hypothesis universal-quantifier) + NFR-RULES-SCHEMA-1
(operator↔threshold-shape mismatch rejected). FD ``domain-entities.md §2/§2.1``
(frozen — implement exactly).
"""
from __future__ import annotations

from decimal import Decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from backend.rules_engine import report_schema as rs
from backend.rules_engine import rulebook_schema as ks


def _rule(**over):
    kw = dict(
        rule_id="DTI-1", category=rs.RuleCategory.FINANCIAL_DTI,
        input_fields=["dti_ratio"], operator=rs.Operator.LTE,
        threshold=Decimal("0.40"), outcome=rs.OutcomeTier.DECLINE_FAIL,
        rationale_message="DTI over ceiling", irdai_ref="",
    )
    kw.update(over)
    return ks.Rule(**kw)


# --------------------------------------------------------------------------
# Valid rules across the operator/threshold shapes
# --------------------------------------------------------------------------
def test_valid_numeric_rule():
    r = _rule()
    assert r.operator is rs.Operator.LTE and r.threshold == Decimal("0.40")


def test_valid_between_rule():
    r = _rule(rule_id="AGE-1", category=rs.RuleCategory.AGE_ELIGIBILITY,
              input_fields=["age_years_derived"], operator=rs.Operator.BETWEEN,
              threshold=rs.DecimalRange(low=Decimal("18"), low_inclusive=True,
                                        high=Decimal("65"), high_inclusive=True))
    assert isinstance(r.threshold, rs.DecimalRange)


def test_valid_in_rule():
    r = _rule(rule_id="SMK-1", category=rs.RuleCategory.LIFESTYLE_SMOKING,
              input_fields=["smoking_status"], operator=rs.Operator.IN,
              threshold=["smoker"])
    assert r.threshold == ["smoker"]


def test_valid_eq_rule_scalar_literal():
    r = _rule(rule_id="SMK-EQ", category=rs.RuleCategory.LIFESTYLE_SMOKING,
              input_fields=["smoking_status"], operator=rs.Operator.EQ,
              threshold="smoker")
    assert r.operator is rs.Operator.EQ and r.threshold == "smoker"


def test_eq_rejects_list_threshold():
    with pytest.raises(ValidationError):
        _rule(operator=rs.Operator.EQ, threshold=["a", "b"])


# --------------------------------------------------------------------------
# NFR-RULES-SCHEMA-1 — operator↔threshold-shape mismatch rejected
# --------------------------------------------------------------------------
def test_between_requires_range():
    with pytest.raises(ValidationError):
        _rule(operator=rs.Operator.BETWEEN, threshold=Decimal("0.40"))


def test_numeric_operator_rejects_range():
    with pytest.raises(ValidationError):
        _rule(operator=rs.Operator.LTE,
              threshold=rs.DecimalRange(low=Decimal("1"), low_inclusive=True,
                                        high=Decimal("2"), high_inclusive=True))


def test_in_requires_set_list():
    with pytest.raises(ValidationError):
        _rule(operator=rs.Operator.IN, threshold=Decimal("1"))


def test_numeric_operator_rejects_list():
    with pytest.raises(ValidationError):
        _rule(operator=rs.Operator.GTE, threshold=["a", "b"])


def test_float_threshold_rejected():
    with pytest.raises(ValidationError):
        _rule(operator=rs.Operator.LTE, threshold=0.40)  # float


# --------------------------------------------------------------------------
# NFR-RULES-BR1-1 — input_fields allowlist (demographic/unknown -> reject)
# --------------------------------------------------------------------------
def test_valid_allowlist_fields_accepted():
    for field in ks.ALLOWED_INPUT_FIELDS:
        _rule(input_fields=[field], operator=rs.Operator.LTE, threshold=Decimal("1"))


def test_empty_input_fields_rejected():
    with pytest.raises(ValidationError):
        _rule(input_fields=[])


@pytest.mark.parametrize("bad", [
    "demographics", "demographics.gender", "full_name", "gender", "city",
    "name", "unknown_field", "age", "SSN",
])
def test_demographic_or_unknown_field_rejected(bad):
    with pytest.raises(ValidationError):
        _rule(input_fields=[bad])


_bad_field = st.one_of(
    st.sampled_from(["demographics", "demographics.gender", "full_name", "gender", "city", "name"]),
    st.text(min_size=1, max_size=20).filter(lambda s: s not in ks.ALLOWED_INPUT_FIELDS),
)


@pytest.mark.property
@settings(max_examples=200)
@given(bad=_bad_field)
def test_universal_quantifier_any_out_of_allowlist_field_rejected(bad):
    # ∀ field not in the allowlist (demographic OR unknown) -> load-time reject.
    with pytest.raises(ValidationError):
        _rule(input_fields=[bad])


@pytest.mark.property
@settings(max_examples=100)
@given(good=st.sampled_from(sorted(ks.ALLOWED_INPUT_FIELDS)),
       bad=st.sampled_from(["demographics.city", "gender", "zzz_unknown"]))
def test_any_bad_field_mixed_with_good_still_rejected(good, bad):
    # even one bad field among valid ones fails the whole rule.
    with pytest.raises(ValidationError):
        _rule(input_fields=[good, bad], operator=rs.Operator.LTE, threshold=Decimal("1"))


# --------------------------------------------------------------------------
# Rulebook + ConfidenceBands
# --------------------------------------------------------------------------
def test_rulebook_and_confidence_bands():
    rb = ks.Rulebook(
        rulebook_version="1.0.0", content_hash="h",
        rules=[_rule()],
        confidence_bands=ks.ConfidenceBands(high_margin=Decimal("0.15"), low_margin=Decimal("0.03")),
    )
    assert rb.rulebook_version == "1.0.0"
    assert rb.confidence_bands.high_margin == Decimal("0.15")


def test_rule_is_frozen():
    r = _rule()
    with pytest.raises((ValidationError, TypeError)):
        r.operator = rs.Operator.GT
