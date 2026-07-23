"""Tests for the RulesEngine ``evaluate()`` orchestration (Step 11).

Maps: NFR-RULES-DET-1 (same-order ×N≥10 byte-identical whole report end-to-end),
NFR-RULES-DET-2 (permuted-authoring → identical), FD ``business-logic-model.md §2``
(happy APPROVE / boundary / incomplete→REFER / multi-fail→DECLINE-RECOMMEND).

Sharpening 1: ``engine_version`` is **INJECTED** via the constructor seam — the
engine NEVER shells out to git / reads a file for it inside ``evaluate()`` (keeps
``evaluate`` a pure function of ``(profile, rulebook_version)`` for DET-1).
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import yaml

from backend.common.canon_ser import canon_ser
from backend.intake import schema as isch
from backend.rules_engine.engine import RulesEngine
from backend.rules_engine.loader import RulebookLoader
from backend.rules_engine.report_schema import Confidence, Recommendation, RuleStatus

_ENGINE_VERSION = "engine-sha-deadbeef"


# --------------------------------------------------------------------------
# A small representative rulebook (all authored thresholds are strings — no float)
# --------------------------------------------------------------------------
def _rulebook_dict(version="1.0.0", rules_order="normal"):
    rules = [
        dict(rule_id="AGE-1", category="age_eligibility", input_fields=["age_years_derived"],
             operator="between",
             threshold=dict(low="18", low_inclusive=True, high="65", high_inclusive=True),
             outcome="decline_fail", rationale_message="age {actual_value} outside 18-65"),
        # acceptable = NOT obese (bmi < 30); obese fails -> refer_trigger
        dict(rule_id="BMI-1", category="medical_bmi", input_fields=["bmi_derived"],
             operator="lt", threshold="30", outcome="refer_trigger",
             rationale_message="bmi {actual_value} at or above 30"),
        dict(rule_id="DTI-1", category="financial_dti", input_fields=["dti_ratio"],
             operator="lte", threshold="0.40", outcome="decline_fail",
             rationale_message="dti {actual_value} over 0.40"),
        # acceptable = non_smoker; smoker/unknown fails -> refer_trigger
        dict(rule_id="SMOKE-1", category="lifestyle_smoking", input_fields=["smoking_status"],
             operator="in", threshold=["non_smoker"], outcome="refer_trigger",
             rationale_message="smoker status {actual_value}"),
    ]
    if rules_order == "reversed":
        rules = list(reversed(rules))
    return dict(rulebook_version=version, content_hash="", rules=rules,
                confidence_bands=dict(high_margin="0.15", low_margin="0.03"))


def _engine(tmp_path, version="1.0.0", rules_order="normal"):
    (tmp_path / f"{version}.yaml").write_text(
        yaml.safe_dump(_rulebook_dict(version, rules_order)), encoding="utf-8"
    )
    return RulesEngine(RulebookLoader(tmp_path), engine_version=_ENGINE_VERSION)


def _profile(**over):
    kw = dict(
        application_id="APP-1", date_of_birth=date(1986, 1, 1), as_of_date=date(2026, 1, 1),
        age_years_derived=40, height_cm=Decimal("180"), weight_kg=Decimal("71"),
        bmi_derived=Decimal("22.00"), verifiable_income_annual=Decimal("1000000"),
        requested_cover_amount=Decimal("5000000"),
        existing_debt_obligations_annual=Decimal("300000"),
        employment_type=isch.EmploymentType.SALARIED, smoking_status=isch.SmokingStatus.NON_SMOKER,
        occupation="engineer", health_flags=[], incomplete=False,
        demographics=isch.Demographics(full_name="A B", gender=isch.Gender.FEMALE, city="Metro"),
        documents=isch.DocumentManifest(expected_count=3, satisfied_count=3, entries=[]),
    )
    kw.update(over)
    return isch.ApplicantProfile(**kw)


# --------------------------------------------------------------------------
# Flows (FD §6)
# --------------------------------------------------------------------------
def test_happy_path_is_approve(tmp_path):
    report = _engine(tmp_path).evaluate(_profile(), "1.0.0")
    assert report.recommendation is Recommendation.APPROVE
    assert all(r.status is RuleStatus.PASS for r in report.rule_results)
    assert report.decline_reasons == [] and report.refer_reasons == []


def test_boundary_values_approve_and_recorded_exactly(tmp_path):
    # age 65 (inclusive), bmi 25 (< 30 -> not obese), dti exactly 0.40 (<= 0.40).
    report = _engine(tmp_path).evaluate(
        _profile(age_years_derived=65, bmi_derived=Decimal("25.00"),
                 existing_debt_obligations_annual=Decimal("400000")),  # dti = 0.40
        "1.0.0",
    )
    assert report.recommendation is Recommendation.APPROVE
    by_id = {r.rule_id: r for r in report.rule_results}
    assert by_id["AGE-1"].actual_value == Decimal("65")
    assert by_id["DTI-1"].actual_value == Decimal("0.4000") and by_id["DTI-1"].status is RuleStatus.PASS


def test_incomplete_flag_is_refer_not_decline(tmp_path):
    report = _engine(tmp_path).evaluate(_profile(incomplete=True), "1.0.0")
    assert report.recommendation is Recommendation.REFER
    assert report.refer_reasons  # carries the insufficient-info trigger


def test_missing_operand_is_refer(tmp_path):
    # No debt figure -> dti_ratio uncomputable -> DTI not_evaluated -> REFER.
    report = _engine(tmp_path).evaluate(
        _profile(existing_debt_obligations_annual=None), "1.0.0"
    )
    dti = next(r for r in report.rule_results if r.rule_id == "DTI-1")
    assert dti.status is RuleStatus.NOT_EVALUATED and dti.actual_value is None
    assert report.recommendation is Recommendation.REFER


def test_multi_fail_is_decline_recommend(tmp_path):
    report = _engine(tmp_path).evaluate(
        _profile(age_years_derived=70, existing_debt_obligations_annual=Decimal("500000")),  # dti 0.50
        "1.0.0",
    )
    assert report.recommendation is Recommendation.DECLINE_RECOMMEND
    assert report.recommendation.value == "DECLINE-RECOMMEND"
    driving = " ".join(report.decline_reasons)
    assert "AGE-1" in driving and "DTI-1" in driving


def test_decline_dominates_even_if_incomplete(tmp_path):
    report = _engine(tmp_path).evaluate(_profile(age_years_derived=70, incomplete=True), "1.0.0")
    assert report.recommendation is Recommendation.DECLINE_RECOMMEND


# --------------------------------------------------------------------------
# Provenance + injected engine_version (sharpening 1)
# --------------------------------------------------------------------------
def test_report_stamps_version_hash_and_injected_engine_version(tmp_path):
    engine = _engine(tmp_path)
    report = engine.evaluate(_profile(), "1.0.0")
    assert report.rulebook_version == "1.0.0"
    assert len(report.content_hash) == 64
    assert report.engine_version == _ENGINE_VERSION   # injected, not git-derived


def test_load_rulebook_delegates(tmp_path):
    engine = _engine(tmp_path)
    rb = engine.load_rulebook("1.0.0")
    assert rb.rulebook_version == "1.0.0"


# --------------------------------------------------------------------------
# DET-1 (×N same-order byte-identity) + DET-2 (permuted authoring -> identical)
# --------------------------------------------------------------------------
def test_det1_same_order_byte_identical_across_ten_runs(tmp_path):
    engine = _engine(tmp_path)
    profile = _profile()
    baseline = canon_ser(engine.evaluate(profile, "1.0.0").model_dump())
    for _ in range(10):
        assert canon_ser(engine.evaluate(profile, "1.0.0").model_dump()) == baseline


def test_det2_reversed_rule_authoring_yields_identical_report(tmp_path, tmp_path_factory):
    normal = _engine(tmp_path).evaluate(_profile(), "1.0.0")
    other_dir = tmp_path_factory.mktemp("rev")
    rev_engine = _engine(other_dir, rules_order="reversed")
    reversed_report = rev_engine.evaluate(_profile(), "1.0.0")
    assert canon_ser(normal.model_dump()) == canon_ser(reversed_report.model_dump())
