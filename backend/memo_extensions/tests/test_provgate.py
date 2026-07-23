"""NFR-MEXT-PROVGATE-1 — Ollama is exempt from MEMO-QUALITY gates only, never from
DECISION-LEVEL gates (BR-MEXT-10 / FR-PROV-GATE-1/2). *"Wired-only" != untested code*: the
Ollama adapter IS unit-tested offline (constructed, temperature=0, structured output
parsed), and the decision-level gates (temperature=0, CON-BR2-TYPE) hold for it identically.

Governance note (NOT a code test): Ollama's ABSENCE from the groundedness/promptfoo target
set (AC-6 / QA-4 / FR-PROV-GATE-2) is a tooling-config fact owned by ``llm-judge`` (U22),
recorded as an explicit, documented exemption — never implicit, and not asserted here.
"""
from __future__ import annotations

from backend.memo_agent_core.schemas import MemoDraftOutput, ThinkingMode
from backend.memo_extensions.provider_showcase import OllamaAdapter
from backend.memo_extensions.tests import fixtures as fx


def test_ollama_adapter_is_unit_tested_offline():
    client = fx.CapturingThinkingClient()
    adapter = OllamaAdapter(client, model="llama3.1", thinking_mode=ThinkingMode.EXTENDED)
    draft = adapter.complete("prompt", MemoDraftOutput)
    assert isinstance(draft, MemoDraftOutput)
    assert draft.narrative_prose  # structured XML output parsed


def test_ollama_holds_the_decision_level_gates():
    client = fx.CapturingThinkingClient()
    OllamaAdapter(client, model="llama3.1", thinking_mode=ThinkingMode.STANDARD).complete(
        "prompt", MemoDraftOutput
    )
    assert client.calls[-1]["temperature"] == 0                # TEMP0-1 holds for Ollama
    assert "recommendation" not in MemoDraftOutput.model_fields  # CON-BR2-TYPE holds for Ollama
