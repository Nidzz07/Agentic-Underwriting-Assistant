"""Tests for NamespaceBuilder (Step 5).

Maps: NFR-RULES-BR1-2 — the INDEPENDENT (belt-and-suspenders) structural guard.
The operand-resolution namespace is built from ONLY the demographic-excluded
allowlist + the derived operands; the ``demographics`` sub-object is NEVER in it.
So a demographic name resolves as *missing* even if a bad rule were loaded — the
value is never read.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.intake import schema as isch
from backend.rules_engine.namespace import build_namespace
from backend.rules_engine.rulebook_schema import ALLOWED_INPUT_FIELDS


def _profile(**over):
    kw = dict(
        application_id="APP-1", date_of_birth=date(1990, 5, 20), as_of_date=date(2026, 5, 20),
        age_years_derived=36, height_cm=Decimal("180"), weight_kg=Decimal("81"),
        bmi_derived=Decimal("25.00"), verifiable_income_annual=Decimal("1000000"),
        requested_cover_amount=Decimal("5000000"),
        existing_debt_obligations_annual=Decimal("300000"),
        employment_type=isch.EmploymentType.SALARIED, smoking_status=isch.SmokingStatus.NON_SMOKER,
        occupation="engineer", health_flags=["none"], incomplete=False,
        demographics=isch.Demographics(full_name="Test Person", gender=isch.Gender.FEMALE, city="Metropolis"),
        documents=isch.DocumentManifest(expected_count=3, satisfied_count=3, entries=[]),
    )
    kw.update(over)
    return isch.ApplicantProfile(**kw)


def test_namespace_keys_equal_the_single_sourced_allowlist():
    ns = build_namespace(_profile())
    assert set(ns.keys()) == set(ALLOWED_INPUT_FIELDS)


def test_demographics_never_in_namespace():
    ns = build_namespace(_profile())
    for demographic in ("demographics", "full_name", "gender", "city", "name"):
        assert demographic not in ns


def test_derived_operands_present_and_computed():
    ns = build_namespace(_profile())
    assert ns["dti_ratio"] == Decimal("0.3000")        # 300000 / 1000000
    assert ns["income_multiple"] == Decimal("5.0000")  # 5000000 / 1000000


def test_derived_scalar_operands_for_non_scalar_categories_present():
    # FD §4.2 back-annotation: health_flag_count + documents_missing_count are
    # exposed as scalars (still demographic-excluded; BR1-2 holds).
    ns = build_namespace(_profile(health_flags=["diabetes", "cardiac"]))
    assert ns["health_flag_count"] == 2
    assert ns["documents_missing_count"] == 0          # expected 3, satisfied 3
    # the new operands are in-allowlist and demographics remain absent
    assert {"health_flag_count", "documents_missing_count"} <= set(ns)
    for demographic in ("demographics", "full_name", "gender", "city"):
        assert demographic not in ns


def test_documents_missing_count_reflects_shortfall():
    ns = build_namespace(_profile(
        documents=isch.DocumentManifest(expected_count=3, satisfied_count=1, entries=[])))
    assert ns["documents_missing_count"] == 2


def test_derived_operands_none_when_income_missing_or_zero():
    ns = build_namespace(_profile(verifiable_income_annual=Decimal("0")))
    assert ns["dti_ratio"] is None
    assert ns["income_multiple"] is None


def test_namespace_values_match_profile_facts():
    p = _profile()
    ns = build_namespace(p)
    assert ns["age_years_derived"] == 36
    assert ns["bmi_derived"] == Decimal("25.00")
    assert ns["smoking_status"] is isch.SmokingStatus.NON_SMOKER
    assert ns["occupation"] == "engineer"


def test_missing_optional_operand_is_none_not_demographic_leak():
    ns = build_namespace(_profile(existing_debt_obligations_annual=None))
    assert ns["existing_debt_obligations_annual"] is None
    assert ns["dti_ratio"] is None  # guard-before-divide via missing operand
    assert "gender" not in ns
