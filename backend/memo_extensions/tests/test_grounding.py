"""NFR-MEXT-GROUND-1 — the retrieval-miss guard is STRUCTURAL, via the frozen validator
(BR-MEXT-6 / Q7-A / FM1-FM2). Direct retrieval-miss test against the REAL frozen
``CitationValidator``; append-only composition proven via ``str`` immutability; the
non-citable marker present. The no-append-to-``cited_rule_ids`` scan lives in
``test_structural_guard.py``.
"""
from __future__ import annotations

from backend.memo_agent_core.citation_validator import CitationValidator
from backend.memo_agent_core.schemas import CitationOutcome, MemoDraftOutput
from backend.memo_extensions.mcp_tools import SUPPLEMENT_MARKER
from backend.memo_extensions.tests import fixtures as fx


def test_retrieval_miss_rule_in_rulebook_but_absent_from_report_fails_citation():
    # GHOST-1 exists in the rulebook (exactly what MCP could describe) but was NOT evaluated
    # for this applicant → report-membership fails → citation_failure (frozen validator, unchanged).
    report = fx.make_report(rule_results=[fx.make_rule_result(rule_id="DTI-1")])
    rulebook = fx.make_rulebook(("DTI-1", "GHOST-1"))
    draft = MemoDraftOutput(narrative_prose="cites a described-but-unevaluated rule", cited_rule_ids=["GHOST-1"])
    result = CitationValidator(report).validate_citations(draft, rulebook)
    assert result.outcome is CitationOutcome.CITATION_FAILURE
    assert "GHOST-1" in result.offending_cited_ids


def test_report_member_citation_passes_frozen_gate():
    report = fx.make_report(rule_results=[fx.make_rule_result(rule_id="DTI-1")])
    rulebook = fx.make_rulebook(("DTI-1",))
    draft = MemoDraftOutput(narrative_prose="cites an evaluated rule", cited_rule_ids=["DTI-1"])
    result = CitationValidator(report).validate_citations(draft, rulebook)
    assert result.all_valid is True


def test_compose_prompt_is_append_only_and_str_immutable():
    service = fx.make_service()
    context = service.supplementary_context(fx.make_report())
    assert context.retrieval_ok is True
    base = "U4 PROMPT BUILDER OUTPUT"
    composed = service.compose_prompt(base, context)
    assert composed.startswith(base)      # U4 output only appended to
    assert composed is not base           # a new object
    assert base == "U4 PROMPT BUILDER OUTPUT"  # str immutable — base unmodified
    assert SUPPLEMENT_MARKER in composed  # supplement explicitly marked NON-CITABLE


def test_supplement_is_marked_non_citable():
    assert "NON-CITABLE" in SUPPLEMENT_MARKER
