"""C5 ``RuleCoverageGate`` — QA-3 / AC-4 (P3 / NFR-QG-RULECOV-1).

Every ``rule_id`` in the loaded rulebook (via ``RulebookLoader.load_rulebook(
manifest.rulebook_version)`` — QG-Fold-2, the exact version the corpus was labeled
against) must reach a **definite PASS or FAIL** (status not ``NOT_EVALUATED``) in
**≥1** corpus record; any never-definitively-evaluated rule is a **blocking**
failure. Reference-not-own: the real ``RulesEngine`` + ``RulebookLoader`` are used
call-only; no rule evaluation is re-implemented here.
"""
from __future__ import annotations

from backend.intake.schema import ApplicantProfile
from backend.rules_engine.report_schema import RuleStatus
from backend.quality_gates.reports import RuleCoverageReport

#: The two definite statuses (NOT_EVALUATED does not count as coverage — Q2-A).
_DEFINITE = {RuleStatus.PASS, RuleStatus.FAIL}


class RuleCoverageGate:
    """Accumulates definite PASS/FAIL per rule over the corpus (100% or blocking)."""

    def __init__(self, engine, loader) -> None:
        #: Both injected call-only: ``engine`` supplies ``evaluate()``, ``loader``
        #: supplies the rule-ID set at the corpus's rulebook version.
        self._engine = engine
        self._loader = loader

    def run(self, profiles: list[ApplicantProfile], rulebook_version: str) -> RuleCoverageReport:
        rulebook = self._loader.load_rulebook(rulebook_version)
        all_rule_ids = [rule.rule_id for rule in rulebook.rules]
        covered: set[str] = set()
        for profile in profiles:
            report = self._engine.evaluate(profile, rulebook_version)
            for result in report.rule_results:
                if result.status in _DEFINITE:
                    covered.add(result.rule_id)
        covered_ids = [rid for rid in all_rule_ids if rid in covered]
        uncovered_ids = [rid for rid in all_rule_ids if rid not in covered]
        total = len(all_rule_ids)
        pct = 100.0 * len(covered_ids) / total if total else 100.0
        return RuleCoverageReport(
            passed=not uncovered_ids,
            rulebook_version=rulebook.rulebook_version,
            total_rules=total,
            covered_rule_ids=covered_ids,
            uncovered_rule_ids=uncovered_ids,
            coverage_pct=pct,
        )
