"""provider — PROV-1 (injected abstraction, Gemini-only P1, Phase-2 not wired)
and TEMP0-1 (two-part: central temperature=0 offline + no per-call temperature).

No test constructs a real Gemini client, reads a key, or touches the network.
"""
from __future__ import annotations

import ast
import inspect

import pytest

from backend.memo_agent_core import provider as provider_module


def _top_level_imports(module) -> set[str]:
    """Actual top-level import roots of a module (ignores docstring/comment prose)."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(inspect.getsource(module))):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names
from backend.memo_agent_core.provider import (
    GeminiAdapter,
    ProviderAbstraction,
    route_borderline,
)
from backend.memo_agent_core.schemas import MemoDraftOutput
from backend.memo_agent_core.tests.fixtures.fake_provider import FakeProvider, valid_output


class _CapturingClient:
    """Offline test double for the injected LLMClient — records the request,
    returns canned XML. No network, no key."""

    def __init__(self, response_xml: str) -> None:
        self.response_xml = response_xml
        self.calls: list[dict] = []

    def generate(self, *, model: str, prompt: str, temperature: float) -> str:
        self.calls.append({"model": model, "prompt": prompt, "temperature": temperature})
        return self.response_xml


_CANNED_XML = (
    "<memo>"
    "<narrative_prose>Advisory recommendation prose.</narrative_prose>"
    "<cited_rule_ids><rule_id>R-AGE-1</rule_id><rule_id>R-DTI-1</rule_id></cited_rule_ids>"
    "</memo>"
)


# --------------------------------------------------------------------------
# TEMP0-1 part ii — structural: complete() carries no per-call temperature
# --------------------------------------------------------------------------
def test_complete_has_no_temperature_parameter():
    for target in (ProviderAbstraction.complete, GeminiAdapter.complete):
        params = list(inspect.signature(target).parameters)
        assert params == ["self", "prompt", "schema"]
        assert "temperature" not in params


# --------------------------------------------------------------------------
# TEMP0-1 part i — GeminiAdapter builds a temperature=0 request, offline
# --------------------------------------------------------------------------
def test_gemini_adapter_builds_a_temperature_zero_request_offline():
    client = _CapturingClient(_CANNED_XML)
    adapter = GeminiAdapter(client, model="gemini-2.5-flash")
    adapter.complete("prompt text", MemoDraftOutput)
    assert len(client.calls) == 1
    assert client.calls[0]["temperature"] == 0
    assert client.calls[0]["model"] == "gemini-2.5-flash"


def test_gemini_adapter_parses_xml_to_pydantic_offline():
    adapter = GeminiAdapter(_CapturingClient(_CANNED_XML))
    out = adapter.complete("prompt", MemoDraftOutput)
    assert isinstance(out, MemoDraftOutput)
    assert out.narrative_prose == "Advisory recommendation prose."
    assert out.cited_rule_ids == ["R-AGE-1", "R-DTI-1"]


def test_gemini_adapter_reports_its_model_version():
    assert GeminiAdapter(_CapturingClient(_CANNED_XML), model="gemini-x").model_version == "gemini-x"


# --------------------------------------------------------------------------
# PROV-1 — injectable abstraction; Gemini-only P1; Phase-2 seams not wired
# --------------------------------------------------------------------------
def test_route_borderline_is_a_not_wired_stub():
    with pytest.raises(NotImplementedError):
        route_borderline()


def test_only_gemini_adapter_is_present_no_claude_ollama_mcp():
    names = dir(provider_module)
    assert "GeminiAdapter" in names
    assert not any(("Claude" in n or "Ollama" in n or "Mcp" in n or "MCP" in n) for n in names)
    assert "mcp" not in _top_level_imports(provider_module)  # no MCP client imported in P1


def test_fake_provider_is_a_valid_provider_abstraction():
    fake = FakeProvider([valid_output(["R-AGE-1"])])
    assert isinstance(fake, ProviderAbstraction)  # runtime_checkable Protocol


# --------------------------------------------------------------------------
# FakeProvider scripting mechanism (call-count-aware, records params)
# --------------------------------------------------------------------------
def test_fake_provider_returns_ith_output_last_repeats_and_records_calls():
    a, b = valid_output(["R-AGE-1"]), valid_output(["R-DTI-1"])
    fake = FakeProvider([a, b])
    assert fake.complete("p0", MemoDraftOutput) is a
    assert fake.complete("p1", MemoDraftOutput) is b
    assert fake.complete("p2", MemoDraftOutput) is b  # last repeats
    assert fake.call_count == 3
    assert [c.prompt for c in fake.calls] == ["p0", "p1", "p2"]
    assert all(c.schema is MemoDraftOutput for c in fake.calls)


def test_fake_provider_rejects_empty_script():
    with pytest.raises(ValueError):
        FakeProvider([])
