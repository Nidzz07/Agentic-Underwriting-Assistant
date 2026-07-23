"""The single declared ``Decimal`` context for the deterministic core.

CON-DET-1 / NFR-INT-DET-1: every monetary and threshold-compared value uses
``Decimal`` (never IEEE float), and every derivation rounds under ONE declared
context so the result is byte-identical on every run and on replay. Set once,
imported everywhere — no per-call context drift.

Rounding mode ``ROUND_HALF_UP`` and 2-decimal quantization back the exact
boundary values (BMI 25.00 / 30.00, DTI 0.40) the rulebook compares against.
"""
from __future__ import annotations

from decimal import Context, Decimal, ROUND_HALF_UP

#: The one context for the unit. 28 significant digits is ample headroom for
#: currency and ratio arithmetic; the rounding mode is fixed and declared.
CANON_DECIMAL_CONTEXT: Context = Context(prec=28, rounding=ROUND_HALF_UP)

#: Two-decimal-place quantum used for stored derived values (e.g. bmi_derived)
#: and money. A single declared quantum keeps 25.00 / 30.00 exact.
TWO_PLACES: Decimal = Decimal("0.01")


def quantize_2dp(value: Decimal) -> Decimal:
    """Quantize ``value`` to 2 dp under the single declared context/rounding.

    Deterministic: same input -> same output, ``ROUND_HALF_UP`` every time.
    """
    return value.quantize(TWO_PLACES, context=CANON_DECIMAL_CONTEXT)
