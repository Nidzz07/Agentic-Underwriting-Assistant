"""DerivationFunctions — DR-DTI / DR-INCM (FD ``business-rules.md §2``).

NFR-RULES-DEC-1 / NFR Design §2. Pure ``Decimal`` derivations using the **single
shared** ``backend.common.decimal_context`` (``ROUND_HALF_UP``), quantized to 4
decimal places so the ``0.40`` / ceiling boundaries are exact and replayable.

**Guard-before-divide (structural)**: a missing operand or zero income returns
``None`` **before any division** — the caller emits ``not_evaluated`` +
``refer_trigger`` (`actual_value == null`). There is no divide-by-zero path.
"""
from __future__ import annotations

from decimal import Decimal, localcontext
from typing import Optional

from backend.common.decimal_context import CANON_DECIMAL_CONTEXT
from backend.intake.schema import DocumentManifest

_FOUR_PLACES = Decimal("0.0001")


def _ratio(numerator: Optional[Decimal], denominator: Optional[Decimal]) -> Optional[Decimal]:
    # Guard runs BEFORE any division — no divide-by-zero path is ever reached.
    if numerator is None or denominator is None or denominator == 0:
        return None
    with localcontext(CANON_DECIMAL_CONTEXT):
        value = numerator / denominator
        return value.quantize(_FOUR_PLACES)


def compute_dti(
    existing_debt_obligations_annual: Optional[Decimal],
    verifiable_income_annual: Optional[Decimal],
) -> Optional[Decimal]:
    """DTI = debt / income (4dp). ``None`` when un-computable (guard-before-divide)."""
    return _ratio(existing_debt_obligations_annual, verifiable_income_annual)


def compute_income_multiple(
    requested_cover_amount: Optional[Decimal],
    verifiable_income_annual: Optional[Decimal],
) -> Optional[Decimal]:
    """income multiple = cover / income (4dp). ``None`` when un-computable."""
    return _ratio(requested_cover_amount, verifiable_income_annual)


# --------------------------------------------------------------------------
# Derived SCALAR operands for the non-scalar categories (FD §4.2 back-annotation
# 2026-07-05). Pure, deterministic ``int`` derivations — no divide path — so the
# `medical_health` / `document_completeness` categories author under the frozen
# scalar/enum evaluator without extending it. Non-demographic (CON-BR1 clean).
# --------------------------------------------------------------------------
def compute_health_flag_count(health_flags: list[str]) -> int:
    """Number of reported health flags (list → scalar count). ``0`` when clean."""
    return len(health_flags)


def compute_documents_missing_count(documents: DocumentManifest) -> int:
    """Required documents not yet satisfied = ``max(expected - satisfied, 0)``.

    Self-normalized to a fixed ``0`` threshold (robust across applicants with
    different ``expected_count``); floored at 0 so ``satisfied > expected`` never
    yields a negative shortfall.
    """
    return max(documents.expected_count - documents.satisfied_count, 0)
