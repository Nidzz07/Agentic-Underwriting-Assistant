"""Feature-field allow-list + the numeric-only projection type (U18 / P-OUT-1, BR-OUT-1/2).

BY CONSTRUCTION — demographic exclusion (documentation only; NOT enforcement — Q1-A of
NFR-Design: a comment carries no load-bearing weight in Python; the typed structure + the
StructuralGuard AST scans are the enforcement):

  ``OUTLIER_FEATURE_FIELDS`` is a U18-local allow-list of NINE NUMERIC facts. The
  ``FeatureInputs`` projection type below carries ``values`` + ``imputed`` ONLY — it has
  NO ``demographics`` field, no ``full_name`` / ``gender`` / ``city``, and no categorical
  field. A demographic value is therefore *structurally unnameable* in the feature flow:
  there is no attribute on ``FeatureInputs`` it could occupy without first adding a
  demographic field here — an obvious, reviewable change the AST scan + swap-invariance
  teeth regress. This mirrors the frozen ``rules_engine`` ``ALLOWED_INPUT_FIELDS`` +
  ``assert set(...) == ...`` mechanism — **mirrored, NOT imported**.

  Numeric-only (v1): ``employment_type`` / ``smoking_status`` / ``occupation`` are excluded,
  each for a documented reason (FD ``domain-entities.md §2.2``): ``occupation`` is a CON-BR1
  proxy-checked variable unfit for an unconstrained anomaly detector; the two categoricals
  are an arbitrary-encoding determinism hazard for low marginal signal.
"""
from __future__ import annotations

from dataclasses import dataclass

# The nine numeric feature names (single-sourced, U18-local, not imported). Order is
# irrelevant here — ``FeatureVectorBuilder.field_order()`` imposes the stable sort.
OUTLIER_FEATURE_FIELDS: frozenset[str] = frozenset(
    {
        "age_years_derived",
        "bmi_derived",
        "verifiable_income_annual",
        "existing_debt_obligations_annual",
        "requested_cover_amount",
        "dti_ratio",
        "income_multiple",
        "health_flag_count",
        "documents_missing_count",
    }
)


@dataclass(frozen=True)
class FeatureInputs:
    """The builder's WORKING TYPE — numeric-only, demographic-excluded (P-OUT-1 / Q2-A).

    NOTE: there is NO ``demographics``, no name/gender/city, no categorical field on this
    type — a demographic value has nowhere to live in the feature flow.
    """

    values: tuple[float, ...]   # resolved numeric vector, in ``field_order()``
    imputed: tuple[bool, ...]   # per-feature imputed mask — CG-ND-OUT-Fold-1
