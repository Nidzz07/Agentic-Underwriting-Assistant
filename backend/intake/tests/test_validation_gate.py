"""Tests for IntakeGate (Step 8) — the SEC-2 total-function gate.

Maps: NFR-INT-SEC2-TOTAL (never raises; every input -> ApplicantProfile |
RejectedIntake) + NFR-INT-SEC2-COVERAGE (exhaustive reject-vs-REFER over the
four-state DocumentManifest x required-value presence). FD ``business-rules.md``
§1/§2 + ``business-logic-model.md`` §2.3.

Design realization notes (faithful to the frozen FD markers):
  * ``application_id`` is system-assigned ONLY on gate pass (injected generator
    seam for deterministic tests); a RejectedIntake never carries one.
  * Reason precedence: structural-invalid -> ``malformed``; else required value
    absent with an unparseable expected doc -> ``unparseable``; else plain
    absence -> ``missing_required``.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from backend.intake import schema as s
from backend.intake.validation_gate import IntakeGate

GATE = IntakeGate(id_generator=lambda: "APP-TEST")


def make_draft(**overrides):
    """A complete, valid extracted draft (all required values present, all docs
    parsed). Tests mutate/remove keys to exercise the gate."""
    draft = {
        "date_of_birth": "1990-05-20",
        "as_of_date": "2026-05-20",
        "verifiable_income_annual": "1200000.00",
        "requested_cover_amount": "5000000.00",
        "height_cm": "180.00",
        "weight_kg": "81.00",
        "existing_debt_obligations_annual": "200000.00",
        "employment_type": "salaried",
        "smoking_status": "non_smoker",
        "occupation": "software_engineer",
        "health_flags": ["none"],
        "full_name": "Test Person",
        "gender": "unspecified",
        "city": "Metropolis",
        "documents": [
            {"doc_type": "salary_slip", "status": "parsed", "content_hash": "h1"},
            {"doc_type": "bank_statement", "status": "parsed", "content_hash": "h2"},
            {"doc_type": "medical_questionnaire", "status": "parsed", "content_hash": "h3"},
        ],
    }
    draft.update(overrides)
    return draft


# --------------------------------------------------------------------------
# Happy path
# --------------------------------------------------------------------------
def test_valid_complete_profile():
    result = GATE.validate_gate(make_draft())
    assert isinstance(result, s.ApplicantProfile)
    assert result.application_id == "APP-TEST"
    assert result.incomplete is False
    assert result.age_years_derived == 36
    assert result.bmi_derived == Decimal("25.00")


def test_valid_profile_derives_and_stores_age_and_bmi():
    result = GATE.validate_gate(make_draft(date_of_birth="2008-06-14", as_of_date="2026-06-14"))
    assert isinstance(result, s.ApplicantProfile)
    assert result.age_years_derived == 18  # boundary derivation stored


# --------------------------------------------------------------------------
# Reject-vs-REFER boundary (the four-state x value-presence coverage)
# --------------------------------------------------------------------------
def test_thin_file_value_present_doc_missing_is_valid_incomplete():
    # Income present on the form, salary slip NOT uploaded -> valid + incomplete.
    draft = make_draft(documents=[
        {"doc_type": "salary_slip", "status": "missing"},
        {"doc_type": "bank_statement", "status": "parsed", "content_hash": "h"},
        {"doc_type": "medical_questionnaire", "status": "parsed", "content_hash": "h"},
    ])
    result = GATE.validate_gate(draft)
    assert isinstance(result, s.ApplicantProfile)
    assert result.incomplete is True  # -> rules-engine routes REFER


def test_single_missing_optional_operand_is_valid_incomplete():
    draft = make_draft()
    del draft["existing_debt_obligations_annual"]
    result = GATE.validate_gate(draft)
    assert isinstance(result, s.ApplicantProfile)
    assert result.incomplete is True
    assert result.existing_debt_obligations_annual is None


def test_missing_bmi_operands_valid_incomplete():
    draft = make_draft()
    del draft["height_cm"]
    result = GATE.validate_gate(draft)
    assert isinstance(result, s.ApplicantProfile)
    assert result.bmi_derived is None
    assert result.incomplete is True


def test_required_value_absent_all_sources_doc_missing_rejects_missing_required():
    draft = make_draft()
    del draft["verifiable_income_annual"]
    draft["documents"] = [
        {"doc_type": "salary_slip", "status": "missing"},
        {"doc_type": "bank_statement", "status": "parsed", "content_hash": "h"},
        {"doc_type": "medical_questionnaire", "status": "parsed", "content_hash": "h"},
    ]
    result = GATE.validate_gate(draft)
    assert isinstance(result, s.RejectedIntake)
    assert result.reason_category is s.ReasonCategory.MISSING_REQUIRED
    assert "verifiable_income_annual" in result.missing_items


def test_required_value_absent_doc_unparseable_rejects_unparseable():
    draft = make_draft()
    del draft["verifiable_income_annual"]
    draft["documents"] = [
        {"doc_type": "salary_slip", "status": "unparseable"},
        {"doc_type": "bank_statement", "status": "parsed", "content_hash": "h"},
        {"doc_type": "medical_questionnaire", "status": "parsed", "content_hash": "h"},
    ]
    result = GATE.validate_gate(draft)
    assert isinstance(result, s.RejectedIntake)
    assert result.reason_category is s.ReasonCategory.UNPARSEABLE


def test_transient_present_status_treated_as_unparseable_at_gate():
    # A residual `present` at gate time is never silently admitted.
    draft = make_draft()
    del draft["verifiable_income_annual"]
    draft["documents"] = [
        {"doc_type": "salary_slip", "status": "present"},
        {"doc_type": "bank_statement", "status": "parsed", "content_hash": "h"},
        {"doc_type": "medical_questionnaire", "status": "parsed", "content_hash": "h"},
    ]
    result = GATE.validate_gate(draft)
    assert isinstance(result, s.RejectedIntake)
    assert result.reason_category is s.ReasonCategory.UNPARSEABLE


# --------------------------------------------------------------------------
# Malformed / structural rejects
# --------------------------------------------------------------------------
def test_unparseable_date_is_malformed():
    result = GATE.validate_gate(make_draft(date_of_birth="not-a-date"))
    assert isinstance(result, s.RejectedIntake)
    assert result.reason_category is s.ReasonCategory.MALFORMED


def test_dob_after_as_of_is_malformed():
    result = GATE.validate_gate(make_draft(date_of_birth="2027-01-01"))
    assert isinstance(result, s.RejectedIntake)
    assert result.reason_category is s.ReasonCategory.MALFORMED


def test_negative_income_is_malformed():
    result = GATE.validate_gate(make_draft(verifiable_income_annual="-1"))
    assert isinstance(result, s.RejectedIntake)
    assert result.reason_category is s.ReasonCategory.MALFORMED


def test_non_positive_cover_is_malformed():
    result = GATE.validate_gate(make_draft(requested_cover_amount="0"))
    assert isinstance(result, s.RejectedIntake)
    assert result.reason_category is s.ReasonCategory.MALFORMED


def test_non_numeric_money_is_malformed():
    result = GATE.validate_gate(make_draft(verifiable_income_annual="abc"))
    assert isinstance(result, s.RejectedIntake)
    assert result.reason_category is s.ReasonCategory.MALFORMED


def test_float_money_value_is_malformed():
    # A float value in the draft violates BR-TYP-1 (never coerce through float).
    result = GATE.validate_gate(make_draft(verifiable_income_annual=1200000.0))
    assert isinstance(result, s.RejectedIntake)
    assert result.reason_category is s.ReasonCategory.MALFORMED


def test_invalid_optional_enum_is_malformed():
    result = GATE.validate_gate(make_draft(employment_type="astronaut"))
    assert isinstance(result, s.RejectedIntake)
    assert result.reason_category is s.ReasonCategory.MALFORMED


def test_age_out_of_sanity_range_is_malformed():
    result = GATE.validate_gate(make_draft(date_of_birth="1800-01-01"))
    assert isinstance(result, s.RejectedIntake)
    assert result.reason_category is s.ReasonCategory.MALFORMED


def test_rejected_intake_has_no_application_id():
    result = GATE.validate_gate(make_draft(date_of_birth="bad"))
    assert isinstance(result, s.RejectedIntake)
    assert not hasattr(result, "application_id")


# --------------------------------------------------------------------------
# Total function — never raises (NFR-INT-SEC2-TOTAL negative matrix)
# --------------------------------------------------------------------------
@pytest.mark.parametrize("garbage", [
    None,
    123,
    "a string",
    b"raw bytes",
    [],
    ["list", "of", "things"],
    {},
    {"date_of_birth": object()},
    {"date_of_birth": {"nested": "dict"}},
    {"verifiable_income_annual": ["not", "scalar"]},
    {"documents": "not-a-list"},
    {"documents": [{"doc_type": "unknown_type", "status": "parsed"}]},
    {"x" * 10000: "y" * 10000},
    make_draft(gender="not-a-gender"),
    make_draft(full_name=""),
])
def test_gate_is_total_never_raises(garbage):
    result = GATE.validate_gate(garbage)
    assert isinstance(result, (s.ApplicantProfile, s.RejectedIntake))


def test_each_reason_category_is_reachable():
    reasons = set()
    reasons.add(GATE.validate_gate(make_draft(date_of_birth="bad")).reason_category)  # malformed
    d1 = make_draft(); del d1["verifiable_income_annual"]
    d1["documents"] = [{"doc_type": "salary_slip", "status": "missing"}]
    reasons.add(GATE.validate_gate(d1).reason_category)  # missing_required
    d2 = make_draft(); del d2["requested_cover_amount"]
    d2["documents"] = [{"doc_type": "salary_slip", "status": "unparseable"}]
    reasons.add(GATE.validate_gate(d2).reason_category)  # unparseable
    assert reasons == {
        s.ReasonCategory.MALFORMED,
        s.ReasonCategory.MISSING_REQUIRED,
        s.ReasonCategory.UNPARSEABLE,
    }


def test_non_positive_height_is_malformed():
    result = GATE.validate_gate(make_draft(height_cm="0"))
    assert isinstance(result, s.RejectedIntake)
    assert result.reason_category is s.ReasonCategory.MALFORMED


def test_non_positive_weight_is_malformed():
    result = GATE.validate_gate(make_draft(weight_kg="-5"))
    assert isinstance(result, s.RejectedIntake)
    assert result.reason_category is s.ReasonCategory.MALFORMED


def test_negative_debt_is_malformed():
    result = GATE.validate_gate(make_draft(existing_debt_obligations_annual="-1"))
    assert isinstance(result, s.RejectedIntake)
    assert result.reason_category is s.ReasonCategory.MALFORMED


def test_absent_optional_enums_yield_none_and_incomplete():
    draft = make_draft()
    del draft["employment_type"]
    del draft["smoking_status"]
    result = GATE.validate_gate(draft)
    assert isinstance(result, s.ApplicantProfile)
    assert result.employment_type is None
    assert result.smoking_status is None
    assert result.incomplete is True


def test_gate_accepts_typed_date_and_decimal_values():
    # The gate is defensive about input types: native date / Decimal pass through.
    result = GATE.validate_gate(make_draft(
        date_of_birth=date(1990, 5, 20),
        as_of_date=date(2026, 5, 20),
        verifiable_income_annual=Decimal("1200000.00"),
    ))
    assert isinstance(result, s.ApplicantProfile)


def test_gate_accepts_prebuilt_manifest_and_entry_instances():
    manifest = s.DocumentManifest(
        expected_count=3, satisfied_count=3,
        entries=[
            s.DocumentEntry(doc_type=s.DocType.SALARY_SLIP, status=s.DocStatus.PARSED, content_hash="h"),
            s.DocumentEntry(doc_type=s.DocType.BANK_STATEMENT, status=s.DocStatus.PARSED, content_hash="h"),
            s.DocumentEntry(doc_type=s.DocType.MEDICAL_QUESTIONNAIRE, status=s.DocStatus.PARSED, content_hash="h"),
        ],
    )
    result = GATE.validate_gate(make_draft(documents=manifest))
    assert isinstance(result, s.ApplicantProfile)
    assert result.incomplete is False


@pytest.mark.property
@settings(max_examples=200)
@given(
    draft=st.dictionaries(
        keys=st.text(max_size=25),
        values=st.one_of(st.none(), st.text(max_size=25), st.integers(),
                         st.lists(st.text(max_size=5), max_size=3)),
        max_size=8,
    )
)
def test_arbitrary_dict_never_raises(draft):
    result = GATE.validate_gate(draft)
    assert isinstance(result, (s.ApplicantProfile, s.RejectedIntake))
