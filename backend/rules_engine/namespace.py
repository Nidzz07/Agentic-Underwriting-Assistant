"""NamespaceBuilder — the demographic-excluded operand namespace (NFR Design §4).

NFR-RULES-BR1-2 — the INDEPENDENT structural guard (belt-and-suspenders with the
load-time reject). The resolution namespace is built from ONLY the
demographic-excluded profile fields (the single-sourced ``ALLOWED_INPUT_FIELDS``)
plus the engine-derived ``dti_ratio`` / ``income_multiple``. The ``demographics``
sub-object is NEVER placed in it — so a demographic name has no resolvable target
even if a bad rule were somehow loaded; it resolves as *missing* and the value is
never read.
"""
from __future__ import annotations

from typing import Any

from backend.intake.schema import ApplicantProfile
from backend.rules_engine.derivations import (
    compute_documents_missing_count,
    compute_dti,
    compute_health_flag_count,
    compute_income_multiple,
)
from backend.rules_engine.rulebook_schema import ALLOWED_INPUT_FIELDS


def build_namespace(profile: ApplicantProfile) -> dict[str, Any]:
    """Build the operand-resolution namespace (demographic-excluded)."""
    namespace: dict[str, Any] = {
        "age_years_derived": profile.age_years_derived,
        "bmi_derived": profile.bmi_derived,
        "verifiable_income_annual": profile.verifiable_income_annual,
        "existing_debt_obligations_annual": profile.existing_debt_obligations_annual,
        "requested_cover_amount": profile.requested_cover_amount,
        "employment_type": profile.employment_type,
        "smoking_status": profile.smoking_status,
        "occupation": profile.occupation,
        "health_flags": profile.health_flags,
        "documents": profile.documents,
        # engine-derived operands (rules-engine-owned)
        "dti_ratio": compute_dti(
            profile.existing_debt_obligations_annual, profile.verifiable_income_annual
        ),
        "income_multiple": compute_income_multiple(
            profile.requested_cover_amount, profile.verifiable_income_annual
        ),
        # derived scalar operands for the non-scalar categories (FD §4.2)
        "health_flag_count": compute_health_flag_count(profile.health_flags),
        "documents_missing_count": compute_documents_missing_count(profile.documents),
    }
    # Invariant (defensive, by construction): the namespace is exactly the
    # allowlist — never a demographic field.
    assert set(namespace) == set(ALLOWED_INPUT_FIELDS)  # pragma: no cover - construction invariant
    return namespace
