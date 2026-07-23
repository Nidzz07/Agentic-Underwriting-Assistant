"""NFR-MEXT-MISS-1 — a retrieval miss is NON-FATAL (BR-MEXT-8 / brief §10 FM2). With the
handlers unavailable, drafting still yields a valid ``MemoDraftOutput`` whose citations pass
the frozen gate; the failure path adds NO content; the miss is OBSERVABLE (retrieval_ok=False),
never silent, and never relaxes GROUND-1.
"""
from __future__ import annotations

from backend.memo_agent_core.citation_validator import CitationValidator
from backend.memo_agent_core.schemas import MemoDraftOutput
from backend.memo_extensions.provider_secondary import ClaudeAdapter
from backend.memo_extensions.tests import fixtures as fx


def test_miss_degrades_observably_not_silently():
    service = fx.make_failing_service()
    context = service.supplementary_context(fx.make_report())
    assert context.retrieval_ok is False           # observable
    assert context.rule_descriptions == []
    assert context.precedents == []


def test_miss_adds_no_content_to_the_prompt():
    service = fx.make_failing_service()
    context = service.supplementary_context(fx.make_report())
    base = "U4 PROMPT BUILDER OUTPUT"
    assert service.compose_prompt(base, context) == base   # no content added on a miss


def test_miss_still_yields_valid_draft_passing_the_frozen_gate():
    report = fx.make_report(rule_results=[fx.make_rule_result(rule_id="DTI-1")])
    service = fx.make_failing_service()
    context = service.supplementary_context(report)
    prompt = service.compose_prompt("U4 PROMPT BUILDER OUTPUT", context)
    adapter = ClaudeAdapter(fx.CapturingThinkingClient(), model="claude-opus-4-8")
    draft = adapter.complete(prompt, MemoDraftOutput)
    result = CitationValidator(report).validate_citations(draft, fx.make_rulebook(("DTI-1",)))
    assert result.all_valid is True   # the citable set never depended on MCP
