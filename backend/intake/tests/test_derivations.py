"""Tests for DerivationFunctions (Step 4) — DR-AGE / DR-BMI.

Maps: NFR-INT-DET-1 (byte-identical deterministic derivations). Pure functions
of their stored inputs — NO wall-clock, no unseeded randomness. Explicit
boundary cases (age 18/65, BMI 25.00/30.00, leap-day, as_of==dob) plus the
same-input ×N≥10 discipline.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from backend.intake.derivations import compute_age, compute_bmi


# --------------------------------------------------------------------------
# DR-AGE
# --------------------------------------------------------------------------
def test_age_same_day_is_zero():
    assert compute_age(date(2026, 5, 20), date(2026, 5, 20)) == 0


def test_age_on_birthday_increments():
    # Exactly 18 ON the birthday -> 18 (equality means birthday has occurred).
    assert compute_age(date(2008, 6, 14), date(2026, 6, 14)) == 18


def test_age_day_before_birthday_not_yet_reached():
    assert compute_age(date(2008, 6, 14), date(2026, 6, 13)) == 17


def test_age_boundary_exactly_65():
    assert compute_age(date(1961, 6, 14), date(2026, 6, 14)) == 65


def test_age_leap_day_birth_reached_on_mar_1_in_non_leap_year():
    dob = date(2000, 2, 29)  # leap-day birth
    # 2026 is NOT a leap year. On Feb 28 the birthday is not yet reached...
    assert compute_age(dob, date(2026, 2, 28)) == 25
    # ...and on Mar 1 it is (documented leap-day convention).
    assert compute_age(dob, date(2026, 3, 1)) == 26


def test_age_leap_day_birth_on_leap_year_birthday():
    dob = date(2000, 2, 29)
    assert compute_age(dob, date(2024, 2, 29)) == 24  # 2024 is a leap year


def test_age_is_byte_identical_across_10_runs():
    dob, as_of = date(1985, 3, 3), date(2026, 3, 2)
    runs = {compute_age(dob, as_of) for _ in range(10)}
    assert len(runs) == 1
    assert runs.pop() == 40  # birthday (Mar 3) not yet reached on Mar 2


# --------------------------------------------------------------------------
# DR-BMI
# --------------------------------------------------------------------------
def test_bmi_boundary_exactly_25():
    # 100 kg at 2.00 m -> 25.00 exactly.
    assert compute_bmi(Decimal("200"), Decimal("100")) == Decimal("25.00")


def test_bmi_boundary_exactly_30():
    # 30 kg at 1.00 m -> 30.00 exactly.
    assert compute_bmi(Decimal("100"), Decimal("30")) == Decimal("30.00")


def test_bmi_is_quantized_to_two_places_half_up():
    bmi = compute_bmi(Decimal("180"), Decimal("81"))
    assert bmi == Decimal("25.00")
    assert bmi.as_tuple().exponent == -2  # exactly 2 dp, scale preserved


def test_bmi_half_up_rounding_is_deterministic():
    # A value whose 3rd decimal forces HALF_UP rounding.
    bmi = compute_bmi(Decimal("170"), Decimal("72.5"))
    # 72.5 / (1.70^2) = 72.5 / 2.89 = 25.0865... -> 25.09 (HALF_UP)
    assert bmi == Decimal("25.09")


def test_bmi_is_byte_identical_across_10_runs():
    runs = {compute_bmi(Decimal("175"), Decimal("77")) for _ in range(10)}
    assert len(runs) == 1


@pytest.mark.property
@settings(max_examples=100)
@given(
    height=st.decimals(min_value=Decimal("120"), max_value=Decimal("220"),
                       allow_nan=False, allow_infinity=False, places=1),
    weight=st.decimals(min_value=Decimal("30"), max_value=Decimal("200"),
                       allow_nan=False, allow_infinity=False, places=1),
)
def test_bmi_deterministic_property(height, weight):
    # ∀ valid (height, weight): the derivation is a pure function (repeatable)
    # and always quantized to 2 dp.
    first = compute_bmi(height, weight)
    second = compute_bmi(height, weight)
    assert first == second
    assert first.as_tuple().exponent == -2


def test_bmi_rejects_non_positive_dimensions():
    with pytest.raises(ValueError):
        compute_bmi(Decimal("0"), Decimal("70"))
    with pytest.raises(ValueError):
        compute_bmi(Decimal("180"), Decimal("0"))
