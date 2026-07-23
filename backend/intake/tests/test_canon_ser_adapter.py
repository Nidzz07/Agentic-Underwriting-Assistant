"""Tests for CanonSerAdapter (Step 10).

Maps: NFR-INT-DET-2 (ApplicantProfile CANON-SER round-trip byte-identity — the
replay dependency). The adapter DELEGATES to the single shared CANON-SER spec
(``backend.common.canon_ser``, audit-store §2.1) — no parallel convention.

Sharpening 3 (folded in): assert the §2.1 properties on the *profile*
serialization explicitly (Decimal-as-string, null-explicit, segregated
demographics + nested manifest preserved, keys sorted), not merely round-trip.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.common import canon_ser as cs
from backend.intake import schema as s
from backend.intake.canon_ser_adapter import CanonSerAdapter


def _complete_profile() -> s.ApplicantProfile:
    return s.ApplicantProfile(
        application_id="APP-XYZ",
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
        incomplete=False,
        demographics=s.Demographics(full_name="Test Person", gender=s.Gender.FEMALE, city="Metropolis"),
        documents=s.DocumentManifest(
            expected_count=3, satisfied_count=1,
            entries=[s.DocumentEntry(doc_type=s.DocType.SALARY_SLIP,
                                     status=s.DocStatus.PARSED, content_hash="h1")],
        ),
    )


def _thin_profile() -> s.ApplicantProfile:
    """A profile with the optional fields absent (null-explicit stress)."""
    return s.ApplicantProfile(
        application_id="APP-THIN",
        date_of_birth=date(2000, 1, 1),
        as_of_date=date(2026, 1, 1),
        age_years_derived=26,
        verifiable_income_annual=Decimal("500000.00"),
        requested_cover_amount=Decimal("1000000.00"),
        incomplete=True,
        demographics=s.Demographics(full_name="Thin File", gender=s.Gender.UNSPECIFIED, city="Townsville"),
        documents=s.DocumentManifest(expected_count=3, satisfied_count=0, entries=[]),
    )


def test_round_trip_byte_identity_complete():
    p = _complete_profile()
    once = CanonSerAdapter.serialize(p)
    twice = CanonSerAdapter.serialize(CanonSerAdapter.deserialize(once))
    assert once == twice


def test_round_trip_byte_identity_thin():
    p = _thin_profile()
    once = CanonSerAdapter.serialize(p)
    twice = CanonSerAdapter.serialize(CanonSerAdapter.deserialize(once))
    assert once == twice


def test_deserialize_reconstructs_equal_profile():
    p = _complete_profile()
    restored = CanonSerAdapter.deserialize(CanonSerAdapter.serialize(p))
    assert restored == p
    # types preserved (the replay dependency): Decimal stays Decimal, enums/date restored.
    assert isinstance(restored.bmi_derived, Decimal)
    assert restored.employment_type is s.EmploymentType.SALARIED
    assert restored.date_of_birth == date(1990, 5, 20)


def test_delegates_to_shared_canon_ser_spec():
    # The adapter uses the SINGLE shared implementation — its bytes/hash match
    # common.canon_ser applied to the profile's dump (no parallel convention).
    p = _complete_profile()
    assert CanonSerAdapter.serialize(p) == cs.canon_ser(p.model_dump(mode="python"))
    assert CanonSerAdapter.content_hash(p) == cs.content_hash(p.model_dump(mode="python"))


# --- Sharpening 3: §2.1 properties asserted on the profile serialization ----
def test_p2_decimal_serialized_as_string():
    text = CanonSerAdapter.serialize(_complete_profile()).decode("utf-8")
    assert '"1200000.00"' in text  # income Decimal-as-string, scale preserved
    assert '"25.00"' in text        # bmi Decimal-as-string


def test_p3_null_explicit_for_absent_optionals():
    text = CanonSerAdapter.serialize(_thin_profile()).decode("utf-8")
    # absent optional operands are explicit null, not omitted
    assert '"bmi_derived":null' in text
    assert '"existing_debt_obligations_annual":null' in text


def test_segregated_demographics_and_nested_manifest_preserved():
    text = CanonSerAdapter.serialize(_complete_profile()).decode("utf-8")
    assert '"demographics":' in text
    assert '"full_name":"Test Person"' in text
    assert '"documents":' in text
    assert '"content_hash":"h1"' in text


def test_p1_keys_sorted_lexicographically():
    text = CanonSerAdapter.serialize(_complete_profile()).decode("utf-8")
    # top-level keys appear in sorted order: age_years_derived < application_id < as_of_date
    assert text.index("age_years_derived") < text.index("application_id") < text.index("as_of_date")


def test_content_hash_is_deterministic():
    p = _complete_profile()
    assert CanonSerAdapter.content_hash(p) == CanonSerAdapter.content_hash(_complete_profile())
    assert len(CanonSerAdapter.content_hash(p)) == 64
