"""Tests for DerivationFunctions (Step 4) — DR-DTI / DR-INCM.

Maps: NFR-RULES-DEC-1. Pure `Decimal` derivations via the shared context, 4dp
`ROUND_HALF_UP`, boundary-exact; **guard-before-divide** — a missing operand or
zero income returns ``None`` (→ the caller emits `not_evaluated` +
`refer_trigger`) and **no division is attempted**.
"""
from __future__ import annotations

from decimal import Decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from backend.intake.schema import DocStatus, DocType, DocumentEntry, DocumentManifest
from backend.rules_engine.derivations import (
    compute_documents_missing_count,
    compute_dti,
    compute_health_flag_count,
    compute_income_multiple,
)


# --------------------------------------------------------------------------
# DR-DTI
# --------------------------------------------------------------------------
def test_dti_boundary_exact_0_40():
    assert compute_dti(Decimal("40000"), Decimal("100000")) == Decimal("0.4000")


def test_dti_just_over_boundary():
    assert compute_dti(Decimal("40010"), Decimal("100000")) == Decimal("0.4001")


def test_dti_half_up_rounding():
    # 1 / 3 = 0.33333... -> 0.3333 (HALF_UP at 4dp)
    assert compute_dti(Decimal("1"), Decimal("3")) == Decimal("0.3333")
    # 2 / 3 = 0.66666... -> 0.6667
    assert compute_dti(Decimal("2"), Decimal("3")) == Decimal("0.6667")


def test_dti_quantized_to_four_places():
    assert compute_dti(Decimal("40000"), Decimal("100000")).as_tuple().exponent == -4


@pytest.mark.parametrize("debt,income", [
    (None, Decimal("100000")),   # debt missing
    (Decimal("40000"), None),    # income missing
    (Decimal("40000"), Decimal("0")),  # zero income -> no divide
])
def test_dti_guard_before_divide_returns_none(debt, income):
    assert compute_dti(debt, income) is None


# --------------------------------------------------------------------------
# DR-INCM
# --------------------------------------------------------------------------
def test_income_multiple_exact():
    assert compute_income_multiple(Decimal("500000"), Decimal("100000")) == Decimal("5.0000")


def test_income_multiple_guard_before_divide():
    assert compute_income_multiple(Decimal("500000"), Decimal("0")) is None
    assert compute_income_multiple(None, Decimal("100000")) is None
    assert compute_income_multiple(Decimal("500000"), None) is None


# --------------------------------------------------------------------------
# Derived scalar operands for the non-scalar categories (FD §4.2 back-annotation)
# --------------------------------------------------------------------------
def test_health_flag_count_is_list_length():
    assert compute_health_flag_count([]) == 0
    assert compute_health_flag_count(["diabetes"]) == 1
    assert compute_health_flag_count(["diabetes", "cardiac", "hypertension"]) == 3


def test_health_flag_count_is_plain_int_deterministic():
    flags = ["a", "b"]
    assert compute_health_flag_count(flags) == 2
    assert isinstance(compute_health_flag_count(flags), int)
    assert not isinstance(compute_health_flag_count(flags), bool)


def _manifest(expected, satisfied):
    return DocumentManifest(expected_count=expected, satisfied_count=satisfied, entries=[])


def test_documents_missing_count_expected_minus_satisfied():
    assert compute_documents_missing_count(_manifest(3, 3)) == 0   # complete
    assert compute_documents_missing_count(_manifest(3, 2)) == 1   # one missing
    assert compute_documents_missing_count(_manifest(3, 0)) == 3


def test_documents_missing_count_floored_at_zero():
    # Defensive: satisfied > expected never yields a negative shortfall.
    assert compute_documents_missing_count(_manifest(2, 5)) == 0


def test_documents_missing_count_is_deterministic_int():
    m = _manifest(4, 1)
    assert compute_documents_missing_count(m) == compute_documents_missing_count(m) == 3
    assert isinstance(compute_documents_missing_count(m), int)


# --------------------------------------------------------------------------
# Determinism
# --------------------------------------------------------------------------
def test_dti_byte_identical_across_runs():
    runs = {compute_dti(Decimal("33333"), Decimal("99999")) for _ in range(10)}
    assert len(runs) == 1


@pytest.mark.property
@settings(max_examples=150)
@given(
    debt=st.decimals(min_value=Decimal("0"), max_value=Decimal("5000000"),
                     allow_nan=False, allow_infinity=False, places=2),
    income=st.decimals(min_value=Decimal("1"), max_value=Decimal("5000000"),
                       allow_nan=False, allow_infinity=False, places=2),
)
def test_dti_deterministic_and_4dp_property(debt, income):
    first = compute_dti(debt, income)
    assert first == compute_dti(debt, income)      # pure / repeatable
    assert first.as_tuple().exponent == -4         # always 4dp
    assert isinstance(first, Decimal)              # never float
