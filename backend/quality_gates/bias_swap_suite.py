"""C3 ``BiasSwapGate`` — CON-BR1 single verification authority (P1 / NFR-QG-BIAS-1 + PROXY-1).

Swapping the segregated demographic identifiers ``{full_name, gender, city}`` on an
otherwise-identical profile must leave the engine ``recommendation`` **unchanged**
(**delta = 0, any delta blocking**). The ``AttributionCheck`` sub-pattern (PROXY-1)
attributes any recommendation change under ``occupation``/``income`` variation to a
**sanctioned rule** via the imported ``evaluation_output()`` ``rule_results``, never
a demographic proxy; ``pincode`` is documented **N/A** (no such field exists).

**Reference-not-own (P7 / NFR-QG-Fold-1)** — the engine is **injected** (the
``ReplayService(__init__(self, repository, engine))`` pattern); a duck-typed fake
replaces it in the teeth test, so the real ``evaluate()`` is never routed through.
This gate re-defines / enforces nothing — it only asserts the invariant holds.
"""
from __future__ import annotations

from backend.intake.schema import ApplicantProfile, Demographics, Gender
from backend.rules_engine.report import evaluation_output
from backend.quality_gates.reports import BiasSwapReport, SwapRecord

#: The three segregated demographic identifiers the suite swaps (QG-Fold-5).
SWAPPED_FIELDS = ["full_name", "gender", "city"]


def swapped_demographics(demographics: Demographics) -> Demographics:
    """Return a demographics differing in all three identifiers (frozen-safe).

    Gender is flipped MALE<->FEMALE (else -> MALE) so the swap always changes the
    identifier set; a bias-sensitive engine would therefore reveal itself.
    """
    new_gender = Gender.FEMALE if demographics.gender == Gender.MALE else Gender.MALE
    return Demographics(
        full_name=f"{demographics.full_name} (swapped)",
        gender=new_gender,
        city=f"{demographics.city} Alt",
    )


class BiasSwapGate:
    """Asserts demographic-swap invariance over the corpus (delta=0, blocking)."""

    def __init__(self, engine) -> None:
        #: Injected engine (real ``RulesEngine`` in prod; duck-typed fake in tests) —
        #: reference-not-own, never re-implemented (ReplayService pattern).
        self._engine = engine

    def run(self, profiles: list[ApplicantProfile], rulebook_version: str) -> BiasSwapReport:
        """For every profile: swap demographics, re-evaluate, assert recommendation unchanged."""
        swaps: list[SwapRecord] = []
        delta_count = 0
        for profile in profiles:
            baseline = self._engine.evaluate(profile, rulebook_version).recommendation
            swapped_profile = profile.model_copy(
                update={"demographics": swapped_demographics(profile.demographics)}
            )
            swapped = self._engine.evaluate(swapped_profile, rulebook_version).recommendation
            if baseline != swapped:
                delta_count += 1
            swaps.append(
                SwapRecord(
                    application_id=profile.application_id,
                    swapped_fields=list(SWAPPED_FIELDS),
                    baseline_recommendation=baseline.value,
                    swapped_recommendation=swapped.value,
                )
            )
        return BiasSwapReport(
            passed=delta_count == 0,
            profiles_tested=len(profiles),
            swaps=swaps,
            delta_count=delta_count,
        )

    def changed_rules(
        self,
        profile_a: ApplicantProfile,
        profile_b: ApplicantProfile,
        rulebook_version: str,
    ) -> list[str]:
        """AttributionCheck (PROXY-1) — rule_ids whose status differs between two
        profiles, via the imported ``evaluation_output()`` projection. The caller
        asserts any change is attributable to a **sanctioned** rule, never a proxy."""
        out_a = {r["rule_id"]: r["status"] for r in evaluation_output(
            self._engine.evaluate(profile_a, rulebook_version))["rule_results"]}
        out_b = {r["rule_id"]: r["status"] for r in evaluation_output(
            self._engine.evaluate(profile_b, rulebook_version))["rule_results"]}
        return sorted(rid for rid in out_a if out_a[rid] != out_b.get(rid))
