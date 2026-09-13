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
from xml.etree import ElementTree

from backend.memo_agent_core.provider import (
    GeminiAdapter,
    ProviderAbstraction,
    MemoDocumentShapeError,
    route_borderline,
    strip_to_memo_element,
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


# ===========================================================================
# ⛔ Register #33 — X3: SUBTRACTIVE parse tolerance (changes (f) + (g)).
#
# ⚑ These are the FIRST direct exercise of parse behaviour anywhere in this
# build — verified: before this pass no test referenced `_parse_xml` at all,
# which is why #33 reached a live call undetected.
#
# ⚠️ SUBTRACTIVE ONLY (Q4-A): the helper removes what surrounds the document
# and hands the remainder to the SAME `ElementTree.fromstring`. ⛔ It never
# regex-extracts VALUES — that was explicitly rejected, because a parser that
# reconstructs fields from prose can silently invent them.
# ===========================================================================
_CLEAN_XML = (
    "<memo>"
    "<narrative_prose>Advisory prose.</narrative_prose>"
    "<cited_rule_ids><rule_id>R-AGE-1</rule_id></cited_rule_ids>"
    "</memo>"
)


def _parsed(raw: str) -> MemoDraftOutput:
    return GeminiAdapter._parse_xml(raw, MemoDraftOutput)


def test_already_clean_xml_is_unchanged_the_no_op_path():
    """⚑ The no-op case pinned FIRST: tolerance must not alter what already worked, or every
    existing green result becomes untrustworthy."""
    out = _parsed(_CLEAN_XML)

    assert out.narrative_prose == "Advisory prose."
    assert out.cited_rule_ids == ["R-AGE-1"]


def test_an_xml_fenced_code_block_is_tolerated():
    """⛔ The single most likely real-model response shape, and the one that produced #33."""
    out = _parsed(f"```xml\n{_CLEAN_XML}\n```")

    assert out.narrative_prose == "Advisory prose."
    assert out.cited_rule_ids == ["R-AGE-1"]


def test_a_bare_fenced_code_block_is_tolerated():
    out = _parsed(f"```\n{_CLEAN_XML}\n```")

    assert out.cited_rule_ids == ["R-AGE-1"]


def test_a_conversational_preamble_before_the_document_is_tolerated():
    out = _parsed(f"Certainly! Here is the memo you requested:\n\n{_CLEAN_XML}")

    assert out.cited_rule_ids == ["R-AGE-1"]


def test_trailing_commentary_after_the_document_is_tolerated():
    out = _parsed(f"{_CLEAN_XML}\n\nLet me know if you would like it rephrased.")

    assert out.cited_rule_ids == ["R-AGE-1"]


def test_preamble_AND_fence_AND_trailing_text_together_are_tolerated():
    """⚑ The combination, not just each in isolation — a real model emits them together."""
    out = _parsed(
        f"Sure — here you go:\n\n```xml\n{_CLEAN_XML}\n```\n\nHope that helps!"
    )

    assert out.narrative_prose == "Advisory prose."
    assert out.cited_rule_ids == ["R-AGE-1"]


def test_genuine_prose_with_NO_xml_at_all_STILL_RAISES():
    """⛔ **The non-vacuity guard, and the most important test in this block.** Tolerance must not
    become 'never fails'. A model that ignored the format instruction entirely has produced no
    memo, and that must stay a LOUD failure — ⚠️ silently returning an empty `MemoDraftOutput`
    would surface downstream as 'drafting produced no memo' with no cause attached."""
    with pytest.raises(ElementTree.ParseError):
        _parsed("I'm sorry, I can't help with underwriting decisions.")


def test_the_helper_is_SUBTRACTIVE_it_never_invents_a_value():
    """⛔ Q4-A's boundary, asserted directly on the helper: whatever it returns must be a literal
    SUBSTRING of what it was handed. ⚑ This is what forbids a future 'improvement' that
    regex-reconstructs fields out of prose."""
    raw = f"Here:\n```xml\n{_CLEAN_XML}\n```\ndone"

    assert strip_to_memo_element(raw) in raw


def test_the_helper_returns_input_unchanged_when_there_is_no_document():
    """⚑ The pass-through branch: with nothing to subtract, `fromstring` must receive the ORIGINAL
    text so its error message still describes what the model actually said."""
    prose = "no xml here at all"

    assert strip_to_memo_element(prose) == prose


# ===========================================================================
# ⛔ Register #33 change (h) — the SILENT-EMPTY path.
#
# ⚑ X1 is what makes this reachable, and that is the whole argument for landing
# it here: asking the model for XML converts a LOUD failure (not XML at all,
# ParseError) into a QUIET one (well-formed XML, wrong element names). The
# parser reads `narrative_prose` and `./cited_rule_ids/rule_id` BY EXACT PATH,
# so <memo_text> parses to prose="" / cited=[] with NO exception — surfacing
# downstream only as "drafting produced no memo", cause discarded.
#
# ⚠️ Q13-A's boundary: this must stay DISTINGUISHABLE from a model that
# genuinely cited nothing. That is a real, legitimate outcome — CitationValidator
# is supposed to block it — and it must NOT be turned into a format error.
# ===========================================================================
_WRONG_NAMES = (
    "<memo>"
    "<memo_text>Advisory prose under the wrong element name.</memo_text>"
    "<rules><rule>R-AGE-1</rule></rules>"
    "</memo>"
)


def test_a_wellformed_document_with_WRONG_element_names_raises_a_NAMED_error():
    """⛔ The defect: this used to return an empty `MemoDraftOutput` and no exception."""
    with pytest.raises(MemoDocumentShapeError):
        _parsed(_WRONG_NAMES)


def test_the_shape_error_NAMES_what_it_actually_found():
    """⚑ 'Diagnosable' means the message identifies the document it rejected — otherwise the
    operator is no better off than with the silent empty memo."""
    with pytest.raises(MemoDocumentShapeError) as excinfo:
        _parsed(_WRONG_NAMES)

    message = str(excinfo.value)
    assert "memo_text" in message, "the error must name the elements it actually saw"
    assert "narrative_prose" in message, "the error must name what it expected"


def test_a_model_that_GENUINELY_CITED_NOTHING_is_NOT_a_shape_error():
    """⛔ **Q13-A's boundary, and the test that keeps (h) honest.** An empty `<cited_rule_ids/>`
    alongside real prose is a legitimate draft — the model declined to cite. ⚠️ It must reach
    `CitationValidator` and be blocked THERE, on the merits, not be rewritten into a format
    failure here. Collapsing these two cases would destroy exactly the distinction (h) exists
    to draw."""
    genuinely_empty = (
        "<memo>"
        "<narrative_prose>No rule in the handed report applies to this applicant.</narrative_prose>"
        "<cited_rule_ids></cited_rule_ids>"
        "</memo>"
    )

    out = _parsed(genuinely_empty)

    assert out.cited_rule_ids == []
    assert "No rule in the handed report applies" in out.narrative_prose


def test_prose_present_but_citations_element_absent_is_NOT_a_shape_error():
    """⚠️ 'NEITHER element' is the trigger, not 'either element'. A partial document still
    carries recoverable content, and over-raising here would reject drafts that parse fine."""
    out = _parsed(
        "<memo><narrative_prose>Prose only, no citations element.</narrative_prose></memo>"
    )

    assert out.cited_rule_ids == []
    assert "Prose only" in out.narrative_prose


def test_the_shape_error_is_distinct_from_a_parse_error():
    """⚑ Two different failures, two different types: 'not XML' (ParseError) and 'XML of the
    wrong shape' (MemoDocumentShapeError). ⛔ Collapsing them would re-lose the distinction X1
    created."""
    assert not issubclass(MemoDocumentShapeError, ElementTree.ParseError)

    with pytest.raises(ElementTree.ParseError):
        _parsed("not xml at all")
