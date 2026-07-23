"""C-OUT-1 ``FeatureVectorBuilder`` — numeric, demographic-excluded projection + imputer (U18).

P-OUT-1 (bias, load-bearing) + P-OUT-3 (impute/threshold composition).

BY CONSTRUCTION — demographic exclusion + imputed-mask (documentation only; the enforcement
is the typed ``FeatureInputs`` + the ``_ACCESSORS`` allow-list + the module-load invariant
+ the StructuralGuard AST scan):

  ``project`` reads an ``ApplicantProfile`` **only** through the ``_ACCESSORS`` map, whose keys
  are asserted equal to ``OUTLIER_FEATURE_FIELDS`` at import. It emits a ``FeatureInputs`` that
  has **no** ``demographics`` field — a demographic value has no resolvable target in the
  feature flow (BR-OUT-1 / CON-BR1). The ``.demographics`` / ``full_name`` / ``gender`` / ``city``
  attributes are NEVER referenced in this module.

  A missing optional is filled with the fitted **corpus median** (the IsolationForest score
  input) AND its ``imputed[i]`` mask is set ``True`` (CG-ND-OUT-Fold-1) — the median feeds the
  score; the mask drives z=0-at-flagging downstream, so a missing value can never manufacture
  an anomaly flag (BR-OUT-3).

  The ``dti_ratio`` / ``income_multiple`` derivations MIRROR the frozen ``rules_engine``
  semantics (debt/income, cover/income; guard-before-divide → ``None`` when un-computable) —
  computed here from the profile, **not imported** (SCOPE-1: the only backend imports are
  ``corpus_generator.records`` call-only + ``intake.schema`` by shape).
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from statistics import median
from typing import Callable, Optional

from backend.intake.schema import ApplicantProfile
from backend.outlier_model.feature_fields import OUTLIER_FEATURE_FIELDS, FeatureInputs


@dataclass(frozen=True)
class CorpusImputer:
    """Fitted once, stored — deterministic (no RNG). Medians in ``field_order()``."""

    medians: tuple[float, ...]   # per-feature corpus median over the PRESENT values


def _ratio(numerator: Optional[Decimal], denominator: Optional[Decimal]) -> Optional[float]:
    """Mirror of the frozen rules-engine ratio: guard-before-divide → ``None`` if un-computable."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return float(numerator) / float(denominator)


# ---------------------------------------------------------------------------
# Accessor map — reads ONLY allow-listed numeric fields. NEVER references
# ``.demographics`` / ``full_name`` / ``gender`` / ``city``. Each returns a float,
# or ``None`` for a missing optional (→ imputed to the corpus median + mask set).
# ---------------------------------------------------------------------------
def _age(p: ApplicantProfile) -> Optional[float]:
    return float(p.age_years_derived)


def _bmi(p: ApplicantProfile) -> Optional[float]:
    return None if p.bmi_derived is None else float(p.bmi_derived)


def _income(p: ApplicantProfile) -> Optional[float]:
    return float(p.verifiable_income_annual)


def _debt(p: ApplicantProfile) -> Optional[float]:
    return None if p.existing_debt_obligations_annual is None else float(p.existing_debt_obligations_annual)


def _cover(p: ApplicantProfile) -> Optional[float]:
    return float(p.requested_cover_amount)


def _dti(p: ApplicantProfile) -> Optional[float]:
    return _ratio(p.existing_debt_obligations_annual, p.verifiable_income_annual)


def _income_multiple(p: ApplicantProfile) -> Optional[float]:
    return _ratio(p.requested_cover_amount, p.verifiable_income_annual)


def _health_flag_count(p: ApplicantProfile) -> Optional[float]:
    return float(len(p.health_flags))


def _documents_missing_count(p: ApplicantProfile) -> Optional[float]:
    return float(max(p.documents.expected_count - p.documents.satisfied_count, 0))


_ACCESSORS: dict[str, Callable[[ApplicantProfile], Optional[float]]] = {
    "age_years_derived": _age,
    "bmi_derived": _bmi,
    "verifiable_income_annual": _income,
    "existing_debt_obligations_annual": _debt,
    "requested_cover_amount": _cover,
    "dti_ratio": _dti,
    "income_multiple": _income_multiple,
    "health_flag_count": _health_flag_count,
    "documents_missing_count": _documents_missing_count,
}

# Construction invariant (mirrors rules_engine NamespaceBuilder's assert): the accessor
# map is EXACTLY the allow-list — never a demographic field, never a categorical.
assert set(_ACCESSORS) == OUTLIER_FEATURE_FIELDS


def _median(values: list[float]) -> float:
    """Deterministic median over present values; ``0.0`` if the feature is wholly absent."""
    return float(median(values)) if values else 0.0


class FeatureVectorBuilder:
    """Projects an ``ApplicantProfile`` onto the numeric, demographic-excluded vector."""

    @staticmethod
    def field_order() -> tuple[str, ...]:
        """The stable, sorted field order (determinism — BR-OUT-4)."""
        return tuple(sorted(OUTLIER_FEATURE_FIELDS))

    @classmethod
    def _raw(cls, profile: ApplicantProfile) -> tuple[Optional[float], ...]:
        return tuple(_ACCESSORS[name](profile) for name in cls.field_order())

    @classmethod
    def fit_imputer(cls, corpus_profiles: list[ApplicantProfile]) -> CorpusImputer:
        """Corpus median per feature over PRESENT values — computed once, stored (BR-OUT-3)."""
        order = cls.field_order()
        columns: list[list[float]] = [[] for _ in order]
        for profile in corpus_profiles:
            for i, value in enumerate(cls._raw(profile)):
                if value is not None:
                    columns[i].append(value)
        return CorpusImputer(medians=tuple(_median(col) for col in columns))

    @classmethod
    def project(cls, profile: ApplicantProfile, imputer: CorpusImputer) -> FeatureInputs:
        """Raw profile → ``FeatureInputs`` (imputed value + mask for each missing optional)."""
        values: list[float] = []
        imputed: list[bool] = []
        for i, value in enumerate(cls._raw(profile)):
            if value is None:
                values.append(imputer.medians[i])
                imputed.append(True)
            else:
                values.append(value)
                imputed.append(False)
        return FeatureInputs(values=tuple(values), imputed=tuple(imputed))

    @classmethod
    def build_matrix(
        cls, corpus_profiles: list[ApplicantProfile], imputer: CorpusImputer
    ) -> list[FeatureInputs]:
        """The corpus fit matrix — one ``FeatureInputs`` per corpus profile."""
        return [cls.project(profile, imputer) for profile in corpus_profiles]
