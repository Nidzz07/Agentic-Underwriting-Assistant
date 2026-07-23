"""NFR-MEXT-THINK-1 — the thinking mode is supplied at CONSTRUCTION; no frozen signature
changes (BR-MEXT-4 / Fold-1). (a) the frozen 3-param ``complete`` signature on EACH new
adapter + ``isinstance`` the frozen ``ProviderAbstraction``; (b) offline capturing-double
proof that EXTENDED produces a thinking-configured request and STANDARD does not (R2:
``thinking`` is a real request parameter on the U19-local seam); (c) the mode is
construction-time only.
"""
from __future__ import annotations

import inspect

import pytest

from backend.memo_agent_core.provider import ProviderAbstraction
from backend.memo_agent_core.schemas import MemoDraftOutput, ThinkingMode
from backend.memo_extensions.provider_secondary import ClaudeAdapter
from backend.memo_extensions.provider_showcase import OllamaAdapter
from backend.memo_extensions.tests import fixtures as fx

ADAPTERS = [ClaudeAdapter, OllamaAdapter]


@pytest.mark.parametrize("cls", ADAPTERS)
def test_complete_signature_is_exactly_self_prompt_schema(cls):
    assert list(inspect.signature(cls.complete).parameters) == ["self", "prompt", "schema"]


@pytest.mark.parametrize("cls", ADAPTERS)
def test_adapter_satisfies_frozen_provider_abstraction(cls):
    adapter = cls(fx.CapturingThinkingClient(), model="m")
    assert isinstance(adapter, ProviderAbstraction)


@pytest.mark.parametrize("cls", ADAPTERS)
def test_extended_produces_a_thinking_configured_request(cls):
    client = fx.CapturingThinkingClient()
    cls(client, model="m", thinking_mode=ThinkingMode.EXTENDED).complete("prompt", MemoDraftOutput)
    assert client.calls[-1]["thinking"] is True


@pytest.mark.parametrize("cls", ADAPTERS)
def test_standard_produces_no_thinking_request(cls):
    client = fx.CapturingThinkingClient()
    cls(client, model="m", thinking_mode=ThinkingMode.STANDARD).complete("prompt", MemoDraftOutput)
    assert client.calls[-1]["thinking"] is False


@pytest.mark.parametrize("cls", ADAPTERS)
def test_model_version_returns_the_constructed_model(cls):
    adapter = cls(fx.CapturingThinkingClient(), model="prov-model-x")
    assert adapter.model_version == "prov-model-x"


@pytest.mark.parametrize("cls", ADAPTERS)
def test_thinking_mode_is_construction_time_only(cls):
    assert "thinking_mode" not in inspect.signature(cls.complete).parameters
    assert "thinking_mode" in inspect.signature(cls.__init__).parameters
