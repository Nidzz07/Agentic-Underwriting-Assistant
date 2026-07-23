"""C4 ``RejectionSampler`` — bounded rejection-sampling toward per-class quotas (BOUND-1).

Two guards, both raising the SAME typed ``BudgetExhaustedError`` (Q1 / NFR-Design §10):

  1. **Pre-flight feasibility guard (seed-independent)** — before ANY sampling, if a
     class's band LOWER-edge count (``skew_audit.band_lower_edge_count``, the SAME
     band arithmetic ``SkewAudit`` uses — ND-Fold-1) exceeds ``attempt_budget``
     (``quota > budget``, pigeonhole), raise immediately. No seed can attain a count
     exceeding the attempt budget, so the guarantee is structurally checkable.
  2. **Runtime exhaustion guard** — for a config feasible on paper that the seeded
     factory cannot satisfy within budget, the bounded loop runs to ``attempt_budget``
     then raises.

Each attempt either fills a still-needed class (keep) or is discarded; the loop is
bounded by ``attempt_budget`` → no unbounded regeneration, never a hang. The engine
(the injected ``oracle``) is the label authority — a kept record's stored class is
always the engine label, never the generation target (Fold 1/3).
"""
from __future__ import annotations

from typing import Callable, NamedTuple, Protocol

from backend.corpus_generator.config import GenerationConfig
from backend.corpus_generator.exceptions import BudgetExhaustedError
from backend.corpus_generator.profile_factory import INTENDED_CLASS_FOR_EDGE, ProfileFactory
from backend.corpus_generator.skew_audit import band_lower_edge_count
from backend.intake.schema import ApplicantProfile
from backend.rules_engine.report_schema import Recommendation


class SampledProfile(NamedTuple):
    """One kept sample: the profile + engine label + provenance."""

    profile: ApplicantProfile
    label: Recommendation                 # the engine's authoritative class
    intended_class: Recommendation        # generation target only
    edge_case_tags: list[str]


class _Oracle(Protocol):
    def label(self, profile: ApplicantProfile) -> Recommendation: ...


#: deterministic class order (APPROVE, REFER, DECLINE-RECOMMEND).
_CLASS_ORDER: tuple[Recommendation, ...] = (
    Recommendation.APPROVE,
    Recommendation.REFER,
    Recommendation.DECLINE_RECOMMEND,
)


def _target_counts(config: GenerationConfig) -> dict[str, int]:
    """Integer per-class targets summing to ``min_profiles`` (largest-remainder).

    Exact ``Decimal`` arithmetic (no float) — deterministic across platforms.
    """
    raw = {cls: config.min_profiles * prop for cls, prop in config.target_split.items()}
    floors = {cls: int(value) for cls, value in raw.items()}
    remainder = config.min_profiles - sum(floors.values())
    # distribute the remainder to the largest fractional parts (deterministic order)
    order = sorted(raw, key=lambda c: (raw[c] - floors[c], c), reverse=True)
    for cls in order[:max(remainder, 0)]:
        floors[cls] += 1
    return floors


class RejectionSampler:
    """Bounded rejection-sampling with the pre-flight + runtime guards."""

    def preflight(self, config: GenerationConfig) -> None:
        """Seed-independent feasibility guard (pigeonhole ``quota > budget``)."""
        for cls, target in config.target_split.items():
            lower_edge = band_lower_edge_count(target, config)
            if lower_edge > config.attempt_budget:
                raise BudgetExhaustedError(
                    f"infeasible: class {cls!r} band lower-edge count {lower_edge} "
                    f"exceeds attempt_budget {config.attempt_budget} (pigeonhole)"
                )

    def sample(
        self,
        config: GenerationConfig,
        factory: ProfileFactory,
        oracle: _Oracle,
    ) -> list[SampledProfile]:
        """Return the kept corpus (edge records + band-filling records)."""
        self.preflight(config)

        kept: list[SampledProfile] = []
        counts: dict[str, int] = {cls.value: 0 for cls in _CLASS_ORDER}
        attempts = 0

        # -- phase A: the required DATA-2 edge records (deterministic, always kept) --
        for edge in config.required_edge_cases:
            index = len(kept)
            profile, tags = factory.build_edge(index, edge)
            label = oracle.label(profile)
            intended = INTENDED_CLASS_FOR_EDGE.get(edge, label)
            kept.append(SampledProfile(profile, label, intended, tags))
            counts[label.value] = counts.get(label.value, 0) + 1

        # -- phase B: bounded rejection-sampling to fill each class to its target --
        targets = _target_counts(config)
        class_builders: dict[Recommendation, Callable[[int], tuple[ApplicantProfile, list[str]]]] = {
            Recommendation.APPROVE: factory.build_approve,
            Recommendation.REFER: factory.build_refer,
            Recommendation.DECLINE_RECOMMEND: factory.build_decline,
        }

        while any(counts[cls.value] < targets.get(cls.value, 0) for cls in _CLASS_ORDER):
            if attempts >= config.attempt_budget:
                raise BudgetExhaustedError(
                    f"attempt_budget {config.attempt_budget} exhausted before quotas met; "
                    f"counts={counts}, targets={targets}"
                )
            attempts += 1
            # bias toward the first still-needed class (deterministic order)
            needed = next(
                cls for cls in _CLASS_ORDER if counts[cls.value] < targets.get(cls.value, 0)
            )
            profile, tags = class_builders[needed](len(kept))
            label = oracle.label(profile)                        # engine is the authority
            if counts[label.value] < targets.get(label.value, 0):
                kept.append(SampledProfile(profile, label, needed, tags))
                counts[label.value] += 1
            # else: discard (its class is already filled) — bounded by attempt_budget

        return kept
