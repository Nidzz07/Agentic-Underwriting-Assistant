"""NFR-MEXT-CONTRACT-1 — no new output contract; a recommendation-change stays
unrepresentable (BR-MEXT-12 / CON-BR2-TYPE / QA-5 / skill #1). ``MemoDraftOutput`` still
declares no recommendation/confidence field, so QA-5 holds for Claude and Ollama exactly as
for Gemini. The no-LLM-output-model / no-``Recommendation``-path AST scan (scoped per Q5-A)
lives in ``test_structural_guard.py``.
"""
from __future__ import annotations

import pytest

from backend.memo_agent_core.schemas import MemoDraftOutput
from backend.memo_extensions.provider_secondary import ClaudeAdapter
from backend.memo_extensions.provider_showcase import OllamaAdapter
from backend.memo_extensions.tests import fixtures as fx

ADAPTERS = [ClaudeAdapter, OllamaAdapter]


def test_memo_draft_output_declares_no_recommendation_or_confidence_field():
    assert "recommendation" not in MemoDraftOutput.model_fields
    assert "confidence" not in MemoDraftOutput.model_fields
    assert set(MemoDraftOutput.model_fields) == {"narrative_prose", "cited_rule_ids"}


@pytest.mark.parametrize("cls", ADAPTERS)
def test_adapter_output_cannot_carry_a_recommendation(cls):
    draft = cls(fx.CapturingThinkingClient(), model="m").complete("prompt", MemoDraftOutput)
    assert isinstance(draft, MemoDraftOutput)
    assert not hasattr(draft, "recommendation")  # QA-5 — unrepresentable through every provider
