"""Tests for ReportBuilder (Step 10).

Maps: NFR-RULES-DET-2 (ALL order-derived list fields — ``rule_results`` /
``decline_reasons`` / ``refer_reasons`` — in the one canonical order by
``rule_id`` → a PERMUTED evaluation yields a byte-identical WHOLE report),
NFR-RULES-AUDIT-3 (output-vs-provenance separation — a report differing ONLY in
``engine_version`` / ``content_hash`` is equal under the evaluation-output
projection; provenance is forensic/verification, not equality).
"""
from __future__ import annotations

from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from backend.common.canon_ser import canon_ser
from backend.rules_engine import report_schema as rs
from backend.rules_engine import rulebook_schema as ks
from backend.rules_engine.aggregator import aggregate
from backend.rules_engine.confidence import band_confidence
from backend.rules_engine.report import build_report, evaluation_output

_BANDS = ks.ConfidenceBands(high_margin=Decimal("0.15"), low_margin=Decimal("0.03"))


def _res(rule_id, tier, actual="0.30", msg="m"):
    status = rs.RuleStatus.PASS if tier is rs.OutcomeTier.PASS_ONLY else rs.RuleStatus.FAIL
    return rs.RuleResult(
        rule_id=rule_id, category=rs.RuleCategory.FINANCIAL_DTI, status=status,
        actual_value=Decimal(actual), operator=rs.Operator.LTE, threshold=Decimal("0.40"),
        outcome_tier=tier, message=msg,
    )


_RESULTS = [
    _res("D-2", rs.OutcomeTier.DECLINE_FAIL, "0.90"),
    _res("A-1", rs.OutcomeTier.PASS_ONLY),
    _res("R-3", rs.OutcomeTier.REFER_TRIGGER, "0.41"),
    _res("A-2", rs.OutcomeTier.PASS_ONLY),
]


def _report(results, *, incomplete=False, engine_version="eng-abc", content_hash="hash-1"):
    agg = aggregate(results, incomplete=incomplete)
    conf = band_confidence(results, incomplete=incomplete, bands=_BANDS)
    return build_report(
        results=results, aggregation=agg, confidence=conf,
        rulebook_version="1.0.0", content_hash=content_hash, engine_version=engine_version,
    )


# --------------------------------------------------------------------------
# Canonical order of ALL list fields
# --------------------------------------------------------------------------
def test_rule_results_sorted_by_rule_id():
    rep = _report(_RESULTS)
    ids = [r.rule_id for r in rep.rule_results]
    assert ids == sorted(ids) == ["A-1", "A-2", "D-2", "R-3"]


def test_reason_lists_are_sorted():
    rep = _report(_RESULTS, incomplete=True)
    assert rep.decline_reasons == sorted(rep.decline_reasons)
    assert rep.refer_reasons == sorted(rep.refer_reasons)
    assert rep.recommendation is rs.Recommendation.DECLINE_RECOMMEND  # decline present


def test_report_carries_all_provenance_fields():
    rep = _report(_RESULTS)
    assert rep.rulebook_version == "1.0.0"
    assert rep.content_hash == "hash-1"
    assert rep.engine_version == "eng-abc"


# --------------------------------------------------------------------------
# DET-2 — permuted evaluation order -> byte-identical WHOLE report
# --------------------------------------------------------------------------
def test_det2_permuted_results_yield_byte_identical_report():
    baseline = canon_ser(_report(_RESULTS).model_dump())
    reversed_bytes = canon_ser(_report(list(reversed(_RESULTS))).model_dump())
    assert baseline == reversed_bytes


@given(order=st.permutations(_RESULTS))
def test_det2_whole_report_byte_identity_under_any_permutation(order):
    baseline = canon_ser(_report(_RESULTS).model_dump())
    assert canon_ser(_report(list(order)).model_dump()) == baseline


# --------------------------------------------------------------------------
# AUDIT-3 — output-vs-provenance separation (forensic, not equality)
# --------------------------------------------------------------------------
def test_engine_version_difference_is_equal_under_output_projection():
    a = _report(_RESULTS, engine_version="eng-OLD")
    b = _report(_RESULTS, engine_version="eng-NEW")
    # Whole report differs (provenance included)...
    assert canon_ser(a.model_dump()) != canon_ser(b.model_dump())
    # ...but the evaluation-output projection is equal (engine drift != regression).
    assert evaluation_output(a) == evaluation_output(b)


def test_content_hash_difference_is_equal_under_output_projection():
    a = _report(_RESULTS, content_hash="hash-A")
    b = _report(_RESULTS, content_hash="hash-B")
    assert evaluation_output(a) == evaluation_output(b)


def test_output_projection_excludes_all_three_provenance_fields():
    proj = evaluation_output(_report(_RESULTS))
    for provenance in ("rulebook_version", "content_hash", "engine_version"):
        assert provenance not in proj
    for output in ("rule_results", "recommendation", "confidence", "decline_reasons", "refer_reasons"):
        assert output in proj


def test_real_output_difference_is_caught_by_projection():
    # A genuine evaluation difference (a rule flips) DOES change the projection.
    flipped = [r for r in _RESULTS if r.rule_id != "R-3"] + [
        _res("R-3", rs.OutcomeTier.PASS_ONLY, "0.10")
    ]
    assert evaluation_output(_report(_RESULTS)) != evaluation_output(_report(flipped))
