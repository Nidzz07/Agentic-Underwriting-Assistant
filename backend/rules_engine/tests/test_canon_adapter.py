"""Tests for RulebookCanonAdapter (Step 3).

Maps: NFR-RULES-CANON-1. The adapter normalizes the Rulebook into
``backend.common.canon_ser``'s EXISTING value space (set→declared-sorted-list,
DecimalRange→dict, enum→.value) then calls the UNCHANGED shared util. Byte-stable
+ set-order-invariant + rule-order-invariant; change a rule → different hash.
"""
from __future__ import annotations

from decimal import Decimal

from backend.common import canon_ser as cs
from backend.rules_engine import report_schema as rs
from backend.rules_engine import rulebook_schema as ks
from backend.rules_engine.canon_adapter import RulebookCanonAdapter


def _rule(rule_id, **over):
    kw = dict(
        rule_id=rule_id, category=rs.RuleCategory.FINANCIAL_DTI,
        input_fields=["dti_ratio"], operator=rs.Operator.LTE,
        threshold=Decimal("0.40"), outcome=rs.OutcomeTier.DECLINE_FAIL,
        rationale_message="m", irdai_ref="",
    )
    kw.update(over)
    return ks.Rule(**kw)


def _in_rule(rule_id, values):
    return ks.Rule(rule_id=rule_id, category=rs.RuleCategory.LIFESTYLE_SMOKING,
                   input_fields=["smoking_status"], operator=rs.Operator.IN,
                   threshold=list(values), outcome=rs.OutcomeTier.REFER_TRIGGER,
                   rationale_message="m")


def _rulebook(rules, version="1.0.0"):
    return ks.Rulebook(rulebook_version=version, content_hash="",
                       rules=rules,
                       confidence_bands=ks.ConfidenceBands(
                           high_margin=Decimal("0.15"), low_margin=Decimal("0.03")))


def test_content_hash_deterministic_and_hex():
    rb = _rulebook([_rule("A"), _rule("B")])
    h1 = RulebookCanonAdapter.content_hash(rb)
    h2 = RulebookCanonAdapter.content_hash(rb)
    assert h1 == h2
    assert len(h1) == 64  # sha256 hex


def test_set_threshold_order_invariant():
    # Same set, different authoring order -> identical canonical bytes / hash.
    rb1 = _rulebook([_in_rule("S1", ["smoker", "non_smoker"])])
    rb2 = _rulebook([_in_rule("S1", ["non_smoker", "smoker"])])
    assert RulebookCanonAdapter.canonical_bytes(rb1) == RulebookCanonAdapter.canonical_bytes(rb2)
    assert RulebookCanonAdapter.content_hash(rb1) == RulebookCanonAdapter.content_hash(rb2)


def test_rule_order_invariant():
    rb1 = _rulebook([_rule("A"), _rule("B")])
    rb2 = _rulebook([_rule("B"), _rule("A")])
    assert RulebookCanonAdapter.content_hash(rb1) == RulebookCanonAdapter.content_hash(rb2)


def test_rule_change_changes_hash():
    base = _rulebook([_rule("A", threshold=Decimal("0.40"))])
    changed = _rulebook([_rule("A", threshold=Decimal("0.41"))])
    assert RulebookCanonAdapter.content_hash(base) != RulebookCanonAdapter.content_hash(changed)


def test_confidence_bands_change_changes_hash():
    base = _rulebook([_rule("A")])
    other = ks.Rulebook(rulebook_version="1.0.0", content_hash="", rules=[_rule("A")],
                        confidence_bands=ks.ConfidenceBands(high_margin=Decimal("0.20"),
                                                            low_margin=Decimal("0.03")))
    assert RulebookCanonAdapter.content_hash(base) != RulebookCanonAdapter.content_hash(other)


def test_version_label_not_in_hash():
    # content_hash is over the RULE SET (+ bands), not the version label.
    rb1 = _rulebook([_rule("A")], version="1.0.0")
    rb2 = _rulebook([_rule("A")], version="9.9.9")
    assert RulebookCanonAdapter.content_hash(rb1) == RulebookCanonAdapter.content_hash(rb2)


def test_delegates_to_shared_canon_ser_unchanged():
    # The adapter's bytes equal common.canon_ser applied to its canonical form —
    # it delegates to the single shared util (no fork).
    rb = _rulebook([_rule("A"), _in_rule("S1", ["smoker"])])
    form = RulebookCanonAdapter.canonical_form(rb)
    assert RulebookCanonAdapter.canonical_bytes(rb) == cs.canon_ser(form)
    # a raw set would make canon_ser raise; the adapter never passes one.
    assert isinstance(form["rules"], list)


def test_decimal_range_normalized_to_dict():
    r = _rule("AGE", category=rs.RuleCategory.AGE_ELIGIBILITY,
              input_fields=["age_years_derived"], operator=rs.Operator.BETWEEN,
              threshold=rs.DecimalRange(low=Decimal("18"), low_inclusive=True,
                                        high=Decimal("65"), high_inclusive=True))
    form = RulebookCanonAdapter.canonical_form(_rulebook([r]))
    th = form["rules"][0]["threshold"]
    assert th == {"low": Decimal("18"), "low_inclusive": True,
                  "high": Decimal("65"), "high_inclusive": True}
