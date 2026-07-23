"""RulesEngine — the ``evaluate()`` orchestration (Step 11).

The frozen C2 contract (``component-methods.md``): ``load_rulebook(version) ->
Rulebook`` and ``evaluate(profile, rulebook_version) -> RuleResultReport``. Wires
the frozen pipeline (FD ``business-logic-model.md §1/§2``):

    load_rulebook → build_namespace → evaluate_rules → aggregate → band_confidence
    → build_report

**Pure, zero LLM** (CON-BR2). ``evaluate`` has **no wall-clock, no unseeded
randomness, no git subprocess**: the ``engine_version`` (git SHA / build id) is
**INJECTED once at construction** by the composition root — it is NEVER read via
git or file I/O inside ``evaluate()`` (sharpening 1; mirrors intake's injectable
``application_id`` generator seam). Rulebook loading reads immutable, hash-frozen
versioned data (deterministic + cached), so ``evaluate`` is a pure function of
``(profile, rulebook_version)`` — DET-1 holds.
"""
from __future__ import annotations

from backend.intake.schema import ApplicantProfile
from backend.rules_engine.aggregator import aggregate
from backend.rules_engine.confidence import band_confidence
from backend.rules_engine.evaluator import evaluate_rules
from backend.rules_engine.loader import RulebookLoader
from backend.rules_engine.namespace import build_namespace
from backend.rules_engine.report import build_report
from backend.rules_engine.report_schema import RuleResultReport
from backend.rules_engine.rulebook_schema import Rulebook


class RulesEngine:
    """Pure deterministic evaluation over a versioned rulebook (no LLM, no I/O in
    ``evaluate`` beyond the deterministic, cached rulebook load)."""

    def __init__(self, loader: RulebookLoader, engine_version: str) -> None:
        #: Reference-not-own: the loader + the injected engine_version are supplied
        #: by the composition root — the engine derives neither itself.
        self._loader = loader
        self._engine_version = engine_version

    def load_rulebook(self, version: str) -> Rulebook:
        """Resolve a semver to its immutable, hash-verified :class:`Rulebook`."""
        return self._loader.load_rulebook(version)

    def evaluate(self, profile: ApplicantProfile, rulebook_version: str) -> RuleResultReport:
        """Evaluate ``profile`` against ``rulebook_version`` → a RuleResultReport.

        Pure function of ``(profile, rulebook_version)`` — the recommendation and
        confidence originate here (CON-BR2), never from an LLM.
        """
        rulebook = self._loader.load_rulebook(rulebook_version)
        namespace = build_namespace(profile)
        results = evaluate_rules(rulebook, namespace)
        aggregation = aggregate(results, incomplete=profile.incomplete)
        confidence = band_confidence(
            results, incomplete=profile.incomplete, bands=rulebook.confidence_bands
        )
        return build_report(
            results=results,
            aggregation=aggregation,
            confidence=confidence,
            rulebook_version=rulebook.rulebook_version,
            content_hash=rulebook.content_hash,
            engine_version=self._engine_version,
        )
