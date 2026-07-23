"""Tests for the checked-in representative rulebook data (Step 13).

Asserts the runtime rulebook under ``rules_engine/rulebook/`` loads and exercises
every engine path, folding in the Code-Gen sharpenings:
  * (2) ALL 7 operators appear across the rulebook;
  * (3) >=2 versions (1.0.0, 1.1.0) — both loadable, distinct content_hash,
        1.0.0 unchanged (NFR-RULES-AUDIT-2 append-only immutability);
  * (4) ALL 3 recommendation tiers reachable end-to-end (APPROVE / REFER /
        DECLINE-RECOMMEND);
  * (5) >=1 set-threshold (``in``) rule (NFR-RULES-CANON-1 set-order path).
All rulebook data is synthetic (no real PII).
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import backend.rules_engine as re_pkg
from backend.intake import schema as isch
from backend.rules_engine.engine import RulesEngine
from backend.rules_engine.loader import RulebookLoader
from backend.rules_engine.report_schema import OutcomeTier, Operator, Recommendation, RuleCategory

RULEBOOK_DIR = Path(re_pkg.__file__).parent / "rulebook"


def _engine():
    return RulesEngine(RulebookLoader(RULEBOOK_DIR), engine_version="engine-test-1")


def _profile(**over):
    kw = dict(
        application_id="APP-1", date_of_birth=date(1986, 1, 1), as_of_date=date(2026, 1, 1),
        age_years_derived=40, bmi_derived=Decimal("22.00"),
        verifiable_income_annual=Decimal("1000000"), requested_cover_amount=Decimal("5000000"),
        existing_debt_obligations_annual=Decimal("300000"),  # dti 0.30
        employment_type=isch.EmploymentType.SALARIED, smoking_status=isch.SmokingStatus.NON_SMOKER,
        occupation="engineer", health_flags=[], incomplete=False,
        demographics=isch.Demographics(full_name="A B", gender=isch.Gender.FEMALE, city="Metro"),
        documents=isch.DocumentManifest(expected_count=3, satisfied_count=3, entries=[]),
    )
    kw.update(over)
    return isch.ApplicantProfile(**kw)


# --------------------------------------------------------------------------
# Loadability + versioning (sharpening 3 / AUDIT-1 / AUDIT-2)
# --------------------------------------------------------------------------
def test_both_versions_load_with_distinct_hash():
    loader = RulebookLoader(RULEBOOK_DIR)
    v1 = loader.load_rulebook("1.0.0")
    v11 = loader.load_rulebook("1.1.0")
    assert len(v1.content_hash) == 64 and len(v11.content_hash) == 64
    assert v1.content_hash != v11.content_hash
    # 1.0.0 unchanged after loading the successor (append-only immutability)
    assert loader.load_rulebook("1.0.0").content_hash == v1.content_hash


# --------------------------------------------------------------------------
# Operator / tier / set-threshold / category coverage
# --------------------------------------------------------------------------
def test_all_seven_operators_present():
    rules = RulebookLoader(RULEBOOK_DIR).load_rulebook("1.0.0").rules
    assert {r.operator for r in rules} == set(Operator)         # sharpening 2


def test_both_non_pass_outcome_tiers_authored():
    rules = RulebookLoader(RULEBOOK_DIR).load_rulebook("1.0.0").rules
    assert {r.outcome for r in rules} == {OutcomeTier.REFER_TRIGGER, OutcomeTier.DECLINE_FAIL}


def test_has_a_set_threshold_rule():
    rules = RulebookLoader(RULEBOOK_DIR).load_rulebook("1.0.0").rules
    set_rules = [r for r in rules if r.operator is Operator.IN and isinstance(r.threshold, list)]
    assert set_rules and any(len(r.threshold) >= 2 for r in set_rules)   # sharpening 5


def test_all_nine_categories_present():
    # Gap resolved (FD §4.2 back-annotation): medical_health + document_completeness
    # now authored via derived scalar operands -> ALL nine categories exercised.
    rules = RulebookLoader(RULEBOOK_DIR).load_rulebook("1.0.0").rules
    assert {r.category for r in rules} == set(RuleCategory)   # all 9, no orphan slot


# --------------------------------------------------------------------------
# All 3 recommendation tiers reachable end-to-end (sharpening 4)
# --------------------------------------------------------------------------
def test_clean_profile_approves():
    assert _engine().evaluate(_profile(), "1.0.0").recommendation is Recommendation.APPROVE


def test_borderline_profile_refers():
    # occupation outside the sanctioned set -> refer_trigger, no decline -> REFER
    rep = _engine().evaluate(_profile(occupation="trapeze-artist"), "1.0.0")
    assert rep.recommendation is Recommendation.REFER


def test_health_flag_refers_via_derived_count():
    rep = _engine().evaluate(_profile(health_flags=["diabetes"]), "1.0.0")
    med = next(r for r in rep.rule_results if r.rule_id == "MED-HEALTH-1")
    assert med.status.value == "fail" and med.actual_value == Decimal("1")
    assert rep.recommendation is Recommendation.REFER   # health flag -> refer, not decline


def test_missing_document_refers_via_derived_count():
    thin = _profile(documents=isch.DocumentManifest(expected_count=3, satisfied_count=2, entries=[]))
    rep = _engine().evaluate(thin, "1.0.0")
    docs = next(r for r in rep.rule_results if r.rule_id == "DOCS-COMPLETE-1")
    assert docs.status.value == "fail" and docs.actual_value == Decimal("1")
    assert rep.recommendation is Recommendation.REFER   # thin-file -> REFER, never DECLINE


def test_bad_profile_declines():
    rep = _engine().evaluate(_profile(age_years_derived=70), "1.0.0")
    assert rep.recommendation is Recommendation.DECLINE_RECOMMEND
    assert rep.recommendation.value == "DECLINE-RECOMMEND"


# --------------------------------------------------------------------------
# Immutable versioning changes the outcome (replay handle is real)
# --------------------------------------------------------------------------
def test_tightened_version_flips_borderline_dti():
    # dti = 0.38 : passes 1.0.0 (<= 0.40) but declines under 1.1.0 (<= 0.35).
    engine = _engine()
    borderline = _profile(existing_debt_obligations_annual=Decimal("380000"))
    assert engine.evaluate(borderline, "1.0.0").recommendation is Recommendation.APPROVE
    assert engine.evaluate(borderline, "1.1.0").recommendation is Recommendation.DECLINE_RECOMMEND
