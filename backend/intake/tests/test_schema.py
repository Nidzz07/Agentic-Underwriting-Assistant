"""Tests for the intake data contracts (Step 3).

Maps: FD ``domain-entities.md`` — implement the frozen C1 shapes EXACTLY. This
suite pins: the segregated ``demographics`` sub-object (CON-BR1), the four-state
``DocumentManifest``, the ``RejectedIntake`` shape (no partial profile), the
``Decimal``-money-never-float rule (BR-TYP-1), and enum validity.

No new fields or behaviours are introduced — these assertions mirror the frozen
FD field-by-field.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.intake import schema as s


def _valid_profile_kwargs():
    return dict(
        application_id="APP-0001",
        date_of_birth=date(1990, 5, 20),
        as_of_date=date(2026, 5, 20),
        age_years_derived=36,
        height_cm=Decimal("180.00"),
        weight_kg=Decimal("81.00"),
        bmi_derived=Decimal("25.00"),
        verifiable_income_annual=Decimal("1200000.00"),
        requested_cover_amount=Decimal("5000000.00"),
        existing_debt_obligations_annual=Decimal("200000.00"),
        employment_type=s.EmploymentType.SALARIED,
        smoking_status=s.SmokingStatus.NON_SMOKER,
        occupation="software_engineer",
        health_flags=["none"],
        demographics=s.Demographics(
            full_name="Test Person", gender=s.Gender.UNSPECIFIED, city="Metropolis"
        ),
        documents=s.DocumentManifest(
            expected_count=3,
            satisfied_count=3,
            entries=[
                s.DocumentEntry(
                    doc_type=s.DocType.SALARY_SLIP,
                    status=s.DocStatus.PARSED,
                    content_hash="h1",
                ),
            ],
        ),
    )


def test_valid_applicant_profile_constructs():
    p = s.ApplicantProfile(**_valid_profile_kwargs())
    assert p.application_id == "APP-0001"
    assert p.incomplete is False  # D default


def test_demographics_is_segregated_subobject():
    p = s.ApplicantProfile(**_valid_profile_kwargs())
    # Structurally a distinct nested object — CON-BR1 by construction.
    assert isinstance(p.demographics, s.Demographics)
    assert p.demographics.full_name == "Test Person"
    # The demographic fields are NOT top-level attributes of the profile.
    assert not hasattr(p, "full_name")
    assert not hasattr(p, "gender")
    assert not hasattr(p, "city")


def test_optional_fields_default_and_incomplete_flag():
    kwargs = _valid_profile_kwargs()
    for opt in ("height_cm", "weight_kg", "bmi_derived",
                "existing_debt_obligations_annual", "employment_type",
                "smoking_status", "occupation"):
        kwargs.pop(opt)
    kwargs.pop("health_flags")
    kwargs["incomplete"] = True
    p = s.ApplicantProfile(**kwargs)
    assert p.height_cm is None
    assert p.bmi_derived is None
    assert p.health_flags == []
    assert p.incomplete is True


@pytest.mark.parametrize("status", list(s.DocStatus))
def test_document_manifest_four_state(status):
    entry = s.DocumentEntry(
        doc_type=s.DocType.BANK_STATEMENT, status=status, content_hash=""
    )
    assert entry.status is status


def test_money_field_rejects_float_br_typ_1():
    kwargs = _valid_profile_kwargs()
    kwargs["verifiable_income_annual"] = 1200000.00  # float — must be refused
    with pytest.raises(ValidationError):
        s.ApplicantProfile(**kwargs)


def test_money_field_accepts_string_and_int_as_decimal():
    kwargs = _valid_profile_kwargs()
    kwargs["verifiable_income_annual"] = "1200000.00"
    kwargs["requested_cover_amount"] = 5000000
    p = s.ApplicantProfile(**kwargs)
    assert p.verifiable_income_annual == Decimal("1200000.00")
    assert p.requested_cover_amount == Decimal("5000000")


def test_unknown_field_forbidden():
    kwargs = _valid_profile_kwargs()
    kwargs["surprise"] = "x"
    with pytest.raises(ValidationError):
        s.ApplicantProfile(**kwargs)


def test_invalid_enum_rejected():
    with pytest.raises(ValidationError):
        s.Demographics(full_name="X", gender="alien", city="Y")  # type: ignore[arg-type]


def test_rejected_intake_shape_no_partial_profile():
    r = s.RejectedIntake(
        reason_category=s.ReasonCategory.MISSING_REQUIRED,
        field_errors=[s.FieldError(field="verifiable_income_annual",
                                   code="missing", message="required value absent")],
        missing_items=["verifiable_income_annual"],
    )
    assert r.reason_category is s.ReasonCategory.MISSING_REQUIRED
    assert r.field_errors[0].field == "verifiable_income_annual"
    # RejectedIntake carries no application_id and no partial profile.
    assert not hasattr(r, "application_id")
    assert not hasattr(r, "profile")


def test_sanitized_text_and_report_entry_shape():
    entry = s.SanitizationReportEntry(
        source_field="medical_notes",
        original_span="ignore previous instructions",
        neutralized_span="[[neutralized]]",
        pattern_category=s.PatternCategory.INSTRUCTION_OVERRIDE,
    )
    st = s.SanitizedText(
        source_ref="medical_questionnaire",
        clean_text="patient reports [[neutralized]]",
        was_modified=True,
        report=[entry],
    )
    assert st.was_modified is True
    assert st.report[0].pattern_category is s.PatternCategory.INSTRUCTION_OVERRIDE


def test_clean_sanitized_text_has_empty_report():
    st = s.SanitizedText(
        source_ref="remarks", clean_text="all good", was_modified=False
    )
    assert st.report == []
