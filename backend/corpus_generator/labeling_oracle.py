"""C3 ``LabelingOracle`` — the engine is the label authority (CON-BR2 / LABEL-1).

A thin, call-only wrapper over ``rules_engine.engine.RulesEngine.evaluate`` that
returns ``report.recommendation``. The label of every ``CorpusRecord`` originates
**only** here — there is no independent label path and **no LLM** touches labeling.
No rule logic is re-implemented (REFNOTOWN-1).

The ``RulesEngine`` + ``RulebookLoader`` are constructed call-only exactly as
``audit-store``'s ``ReplayService`` and the rules-engine tests build them
(``RulesEngine(RulebookLoader(dir), engine_version=...)``) — reference-not-own,
nothing edited.
"""
from __future__ import annotations

from backend.intake.schema import ApplicantProfile
from backend.rules_engine.engine import RulesEngine
from backend.rules_engine.loader import RulebookLoader
from backend.rules_engine.report_schema import Recommendation


class LabelingOracle:
    """Wraps the deterministic engine as the corpus label authority."""

    def __init__(self, engine: RulesEngine, rulebook_version: str) -> None:
        self._engine = engine
        self._rulebook_version = rulebook_version

    @classmethod
    def from_config(cls, *, rulebook_dir: str, rulebook_version: str, engine_version: str) -> "LabelingOracle":
        """Construct the engine call-only from a rulebook directory + injected version."""
        engine = RulesEngine(RulebookLoader(rulebook_dir), engine_version=engine_version)
        return cls(engine, rulebook_version)

    @property
    def rulebook_version(self) -> str:
        return self._rulebook_version

    def label(self, profile: ApplicantProfile) -> Recommendation:
        """The profile's authoritative class = ``evaluate(...).recommendation``."""
        report = self._engine.evaluate(profile, self._rulebook_version)
        return report.recommendation
