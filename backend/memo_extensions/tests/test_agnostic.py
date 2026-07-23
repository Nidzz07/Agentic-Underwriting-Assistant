"""NFR-MEXT-AGNOSTIC-1 — the routing outcome is provider-agnostic; capability degrades at
the adapter, never at the trigger (BR-MEXT-3 / FR-PROV-5). The router's signature carries
no provider; an Ollama adapter built with EXTENDED still completes. The
router-references-no-provider AST scan is part of ROUTE-1's allow-list in
``test_structural_guard.py``.
"""
from __future__ import annotations

import inspect
from decimal import Decimal

from backend.memo_agent_core.schemas import MemoDraftOutput, ThinkingMode
from backend.rules_engine.report_schema import Recommendation
from backend.memo_extensions.borderline_router import route_borderline
from backend.memo_extensions.provider_secondary import ClaudeAdapter
from backend.memo_extensions.provider_showcase import OllamaAdapter
from backend.memo_extensions.tests import fixtures as fx


def test_router_signature_carries_no_provider_parameter():
    params = list(inspect.signature(route_borderline).parameters)
    assert params == ["rule_report", "outlier_signal"]


def test_routing_outcome_unchanged_by_provider_construction():
    report = fx.make_report(
        rule_results=[fx.make_rule_result(actual_value=Decimal("0.20"), threshold=Decimal("0.40"))],
        recommendation=Recommendation.REFER,
    )
    before = route_borderline(report)
    # constructing any/every provider adapter cannot change the routing outcome
    client = fx.CapturingThinkingClient()
    ClaudeAdapter(client, model="claude-opus-4-8", thinking_mode=ThinkingMode.EXTENDED)
    OllamaAdapter(client, model="llama3.1", thinking_mode=ThinkingMode.STANDARD)
    after = route_borderline(report)
    assert before is after is ThinkingMode.EXTENDED


def test_ollama_adapter_with_extended_still_completes():
    client = fx.CapturingThinkingClient()
    adapter = OllamaAdapter(client, model="llama3.1", thinking_mode=ThinkingMode.EXTENDED)
    result = adapter.complete("prompt", MemoDraftOutput)  # degrades, does not raise
    assert isinstance(result, MemoDraftOutput)
