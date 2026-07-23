"""DerivationFunctions — pure DR-AGE / DR-BMI (FD ``business-rules.md §3``).

NFR-INT-DET-1 / CON-DET-1: derivations are PURE functions of their stored
inputs. No system clock is ever read; all arithmetic is ``Decimal`` under the
single declared context (:mod:`backend.common.decimal_context`). Same input ->
byte-identical output on every run and on replay. Values are computed once here
and stored on the profile so no consumer re-derives divergently.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal, localcontext

from backend.common.decimal_context import CANON_DECIMAL_CONTEXT, quantize_2dp


def compute_age(date_of_birth: date, as_of_date: date) -> int:
    """Completed whole years from ``date_of_birth`` to ``as_of_date`` (floor).

    Birthday-not-yet-reached rule (explicit comparison): if the ``as_of``
    (month, day) is strictly less than the birth (month, day), subtract one from
    the raw year difference; equality means the birthday HAS occurred (age
    increments on the birthday).

    Leap-day convention: a Feb-29 birth in a non-leap ``as_of`` year is treated
    as having its birthday on Mar 1. This falls out naturally from the
    (month, day) tuple comparison — on Feb 28 the birthday is not yet reached;
    on Mar 1 it is — so no special-casing is required.
    """
    years = as_of_date.year - date_of_birth.year
    birth_md = (date_of_birth.month, date_of_birth.day)
    asof_md = (as_of_date.month, as_of_date.day)
    if asof_md < birth_md:
        years -= 1
    return years


def compute_bmi(height_cm: Decimal, weight_kg: Decimal) -> Decimal:
    """BMI from height/weight, quantized to 2 dp under the single context.

    ``height_m = height_cm / 100``; ``bmi = weight_kg / height_m**2``; quantize
    to 2 dp ``ROUND_HALF_UP`` so 25.00 / 30.00 boundaries are exact and the
    value is reproducible on replay. All ``Decimal``, never float.
    """
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("height_cm and weight_kg must be strictly positive")
    with localcontext(CANON_DECIMAL_CONTEXT):
        height_m = height_cm / Decimal(100)
        bmi = weight_kg / (height_m * height_m)
    return quantize_2dp(bmi)
