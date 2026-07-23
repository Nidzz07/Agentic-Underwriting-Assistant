"""C1 ``GenerationConfig`` — the seeded generation parameters (FD ``domain-entities.md §6``).

A frozen Pydantic value object: the fixed ``seed`` + the band parameters
(``target_split`` / ``tolerance_pp``) are the **single source** both the
``RejectionSampler`` pre-flight (band lower edge, ND-Fold-1) and the ``SkewAudit``
band check read — one band definition, two uses, cannot independently disagree.

DET-1 discipline: every field is a fixed input; there is no wall-clock and no
unseeded randomness anywhere in this object or the generation path it parameterizes.

Realization notes (faithful to the frozen FD §6 + the answered Q3 / Fold NFR-1;
no semantic re-opening):
  * ``required_edge_cases`` defaults to the fixed 8-item DATA-2 enumeration
    (the "fixed enumerated set" of NFR-CORP-SKEW-EDGE-1 for the real corpus). A
    **test-scoped** config may pass a satisfiable subset (Q3-A / Fold NFR-1); the
    real tier-B corpus uses the default.
  * ``rulebook_dir`` + ``engine_version`` are the call-only construction seams for
    ``rules_engine.RulesEngine`` (exactly how ``audit-store``'s ``ReplayService``
    and the rules-engine tests build the engine — reference-not-own, nothing edited).
"""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from backend.rules_engine.report_schema import Recommendation

#: Target class split (~40/35/25), keyed by the canonical ``Recommendation`` VALUE
#: strings (``"DECLINE-RECOMMEND"`` — hyphenated, the -RECOMMEND suffix mandatory).
DEFAULT_TARGET_SPLIT: dict[str, Decimal] = {
    Recommendation.APPROVE.value: Decimal("0.40"),
    Recommendation.REFER.value: Decimal("0.35"),
    Recommendation.DECLINE_RECOMMEND.value: Decimal("0.25"),
}

#: The fixed DATA-2 mandatory edge-case enumeration (NFR-CORP-SKEW-EDGE-1). This is
#: the "fixed enumerated set" for the real corpus; it is never averaged into the band.
DATA2_EDGE_CASES: tuple[str, ...] = (
    "thin_file",
    "self_employed_irregular",
    "age_18",
    "age_65",
    "bmi_25",
    "bmi_30",
    "dti_40",
    "single_missing_document",
)


class GenerationConfig(BaseModel):
    """The fixed, seeded generation parameters (frozen value object; DET-1)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: int
    rulebook_version: str
    rulebook_dir: str
    engine_version: str
    model_id: str
    attempt_budget: int = Field(gt=0)
    target_split: dict[str, Decimal] = Field(default_factory=lambda: dict(DEFAULT_TARGET_SPLIT))
    tolerance_pp: Decimal = Decimal("3")
    min_profiles: int = Field(default=300, gt=0)
    required_edge_cases: tuple[str, ...] = DATA2_EDGE_CASES

    @property
    def tolerance(self) -> Decimal:
        """The band half-width as a proportion (``tolerance_pp / 100``)."""
        return self.tolerance_pp / Decimal(100)
