"""C4 ``ReproducibilityGate`` — CON-BR2/AC-1 (P2 / NFR-QG-REPRO-1).

Running the **same** input through ``evaluate()`` **×10** must yield an **identical
``evaluation_output()`` projection** each run (identical decision + rule results +
reasons) — asserted on the **deterministic engine output**, not LLM wording;
**100%** or the gate fails. Uses the **imported** ``evaluation_output()`` projection
(reference-not-own — the same one ``audit-store``'s ReplayService uses; QG-Fold-4).
The seeded-outlier determinism clause is **deferred to ``outlier-model`` (P2)**.

The engine is **injected** (P7); a duck-typed non-deterministic fake drives the
teeth test, so the real ``evaluate()`` is never routed through (NFR-QG-Fold-1).
"""
from __future__ import annotations

from backend.intake.schema import ApplicantProfile
from backend.rules_engine.report import evaluation_output
from backend.quality_gates.reports import ReproducibilityReport

#: The project calibration convention (US-PLAT-4): identical input × 10.
DEFAULT_RUNS = 10


class ReproducibilityGate:
    """Asserts ×N identical ``evaluation_output()`` projection per profile (100%)."""

    def __init__(self, engine, runs: int = DEFAULT_RUNS) -> None:
        self._engine = engine
        self._runs = runs

    def run(self, profiles: list[ApplicantProfile], rulebook_version: str) -> ReproducibilityReport:
        mismatches: list[dict] = []
        reproducible = 0
        for profile in profiles:
            baseline = evaluation_output(self._engine.evaluate(profile, rulebook_version))
            profile_ok = True
            for run_index in range(1, self._runs):
                projection = evaluation_output(self._engine.evaluate(profile, rulebook_version))
                if projection != baseline:
                    profile_ok = False
                    mismatches.append(
                        {"application_id": profile.application_id, "run_index": run_index}
                    )
            if profile_ok:
                reproducible += 1
        pct = 100.0 * reproducible / len(profiles) if profiles else 100.0
        return ReproducibilityReport(
            passed=pct == 100.0,
            profiles_tested=len(profiles),
            runs=self._runs,
            mismatches=mismatches,
            reproducibility_pct=pct,
        )
