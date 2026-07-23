"""CitationValidator — the hallucination guard (CITE-1).

``validate_citations`` keeps its **frozen 2-arg C4 signature**
``(memo_draft, rulebook) -> CitationValidationResult``. The authoritative
grounding source — the handed ``RuleResultReport`` — is supplied at
**construction** (the orchestrator builds the validator from the graph state's
report, per invocation), so the frozen signature is preserved unchanged.

Authoritative check (BR-CITE-VALIDATE): every ``cited_rule_id`` must be a
**member of the handed report** (the rules actually evaluated for this
applicant). Belt-and-suspenders: it must also exist in the active ``Rulebook``.
Either miss → ``citation_failure`` with the offending ids. Pure — no provider.
"""
from __future__ import annotations

from backend.rules_engine.report_schema import RuleResultReport
from backend.rules_engine.rulebook_schema import Rulebook
from backend.memo_agent_core.schemas import (
    CitationOutcome,
    CitationValidationResult,
    MemoDraftOutput,
)


class CitationValidator:
    """Constructed with the handed report (authoritative grounding); the frozen
    ``validate_citations(memo_draft, rulebook)`` uses it plus the rulebook."""

    def __init__(self, report: RuleResultReport) -> None:
        # The authoritative membership set — the rules actually evaluated here.
        self._report_ids: frozenset[str] = frozenset(r.rule_id for r in report.rule_results)

    def validate_citations(
        self, memo_draft: MemoDraftOutput, rulebook: Rulebook
    ) -> CitationValidationResult:
        rulebook_ids = frozenset(r.rule_id for r in rulebook.rules)
        offending = [
            cid
            for cid in memo_draft.cited_rule_ids
            if cid not in self._report_ids or cid not in rulebook_ids
        ]
        if offending:
            return CitationValidationResult(
                all_valid=False,
                offending_cited_ids=offending,
                outcome=CitationOutcome.CITATION_FAILURE,
            )
        return CitationValidationResult(
            all_valid=True,
            offending_cited_ids=[],
            outcome=CitationOutcome.VALID,
        )
