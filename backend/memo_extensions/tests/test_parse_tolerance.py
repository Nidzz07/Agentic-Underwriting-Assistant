"""⛔ Register #33 — X3 SUBTRACTIVE parse tolerance, the U19 half (change (g), step 8.5).

⚑ **The tolerance helper is SHARED, not re-implemented.** ``provider_secondary._parse_xml``
imports :func:`~backend.memo_agent_core.provider.strip_to_memo_element` from U4, because ⚠️ **two
hand-rolled implementations would drift** — and this parser exists precisely to *mirror* U4's.
⛔ **These tests pin the sharing itself**, not just the behaviour: a future copy-paste of the
logic into U19 would keep every behavioural test green while re-creating the drift risk.

⚑ **``OllamaAdapter`` inherits this for free** — ``provider_showcase`` imports the same
``_parse_xml`` — so all THREE adapters (Gemini, Claude, Ollama) tolerate the same shapes. ⚠️ That
is a consequence worth asserting rather than assuming, so the showcase adapter is parametrized in.

⚠️ **The frozen edge is legitimate**: Scan 7 allows the ``memo_agent_core`` root, and Scan 1's
tighter allow-list is scoped to ``borderline_router.py`` only (§6.2). ⛔ `test_structural_guard.py`
is the enforcement; this module does not duplicate it.
"""
from __future__ import annotations

import pytest
from xml.etree import ElementTree

from backend.memo_agent_core.provider import strip_to_memo_element
from backend.memo_agent_core.schemas import MemoDraftOutput
from backend.memo_extensions.provider_secondary import ClaudeAdapter, _parse_xml
from backend.memo_extensions.provider_showcase import OllamaAdapter
from backend.memo_extensions.tests import fixtures as fx

ADAPTERS = [ClaudeAdapter, OllamaAdapter]

_CLEAN_XML = fx.VALID_MEMO_XML


def _through_adapter(cls, raw: str) -> MemoDraftOutput:
    """Drive the REAL adapter end-to-end, not just the module function — the adapter is what
    production calls, and a helper wired into the wrong place would pass a direct-call test."""
    return cls(fx.CapturingThinkingClient(raw), model="m").complete("prompt", MemoDraftOutput)


# --------------------------------------------------------------------------
# The tolerated shapes — driven through BOTH adapters
# --------------------------------------------------------------------------
@pytest.mark.parametrize("cls", ADAPTERS)
def test_already_clean_xml_is_unchanged_the_no_op_path(cls):
    """⚑ Pinned FIRST: tolerance must not alter what already worked."""
    out = _through_adapter(cls, _CLEAN_XML)

    assert out.cited_rule_ids == ["DTI-1"]
    assert "underwriter review required" in out.narrative_prose


@pytest.mark.parametrize("cls", ADAPTERS)
@pytest.mark.parametrize(
    "wrapper",
    [
        pytest.param("```xml\n{doc}\n```", id="xml-fenced"),
        pytest.param("```\n{doc}\n```", id="bare-fenced"),
        pytest.param("Certainly! Here is the memo:\n\n{doc}", id="preamble"),
        pytest.param("{doc}\n\nLet me know if you want it rephrased.", id="trailing-text"),
        pytest.param("Sure:\n```xml\n{doc}\n```\nHope that helps!", id="all-three-together"),
    ],
)
def test_a_wrapped_document_is_tolerated(cls, wrapper):
    out = _through_adapter(cls, wrapper.format(doc=_CLEAN_XML))

    assert out.cited_rule_ids == ["DTI-1"]


# --------------------------------------------------------------------------
# ⛔ The non-vacuity guard — tolerance must NOT become "never fails"
# --------------------------------------------------------------------------
@pytest.mark.parametrize("cls", ADAPTERS)
def test_genuine_prose_with_NO_xml_at_all_STILL_RAISES(cls):
    """⛔ **The most important test in this module.** A model that ignored the format instruction
    produced no memo, and that must stay LOUD. ⚠️ Silently returning an empty ``MemoDraftOutput``
    would surface downstream only as *"drafting produced no memo"*, with the cause thrown away."""
    with pytest.raises(ElementTree.ParseError):
        _through_adapter(cls, "I'm sorry, I can't help with underwriting decisions.")


# --------------------------------------------------------------------------
# ⛔ The SHARING itself — what a re-implementation would silently break
# --------------------------------------------------------------------------
def test_u19_uses_u4s_helper_rather_than_its_own_copy():
    """⚑ Behavioural tests alone cannot tell 'imported' from 'copy-pasted'. This can: it asserts
    the U19 parser's module resolves the helper to the **same function object** U4 exports."""
    import backend.memo_extensions.provider_secondary as ps

    assert ps.strip_to_memo_element is strip_to_memo_element


def test_the_two_parsers_agree_on_every_wrapped_shape():
    """⚠️ The anti-drift assertion stated as an equivalence rather than as two copies of the same
    expectations — if either parser is changed alone, this fails."""
    from backend.memo_agent_core.provider import GeminiAdapter

    for wrapper in ("```xml\n{doc}\n```", "Here:\n{doc}", "{doc}\ntrailing"):
        raw = wrapper.format(doc=_CLEAN_XML)
        u4 = GeminiAdapter._parse_xml(raw, MemoDraftOutput)
        u19 = _parse_xml(raw, MemoDraftOutput)

        assert u4.narrative_prose == u19.narrative_prose
        assert u4.cited_rule_ids == u19.cited_rule_ids


# --------------------------------------------------------------------------
# ⛔ Change (h) — the silent-empty path, mirrored in U19
# --------------------------------------------------------------------------
@pytest.mark.parametrize("cls", ADAPTERS)
def test_wrong_element_names_raise_the_SHARED_named_error(cls):
    """⛔ Well-formed XML of the wrong shape used to yield an empty draft and no exception here
    too. ⚑ The error type is **imported from U4**, not redefined — a U19-local copy would make
    `except MemoDocumentShapeError` at a shared caller silently miss the U19 case."""
    from backend.memo_agent_core.provider import MemoDocumentShapeError

    with pytest.raises(MemoDocumentShapeError):
        _through_adapter(cls, "<memo><memo_text>wrong name</memo_text></memo>")


@pytest.mark.parametrize("cls", ADAPTERS)
def test_a_model_that_GENUINELY_CITED_NOTHING_is_NOT_a_shape_error(cls):
    """⚠️ Q13-A's boundary holds in U19 as well: an empty `<cited_rule_ids/>` with real prose is a
    legitimate draft for `CitationValidator` to block on the merits, not a format failure."""
    out = _through_adapter(
        cls,
        "<memo><narrative_prose>No listed rule applies.</narrative_prose>"
        "<cited_rule_ids></cited_rule_ids></memo>",
    )

    assert out.cited_rule_ids == []
    assert "No listed rule applies" in out.narrative_prose
