"""PromptBuilder — GROUND-1 (scoped to MemoAgentInput, no MCP) + ADVISORY-1."""
from __future__ import annotations

import ast
import inspect

from backend.memo_agent_core import prompt_builder as pb_module


def _top_level_imports(module) -> set[str]:
    """Actual top-level import roots of a module (ignores docstring/comment prose)."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(inspect.getsource(module))):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names
from backend.memo_agent_core.prompt_builder import PromptBuilder
from backend.memo_agent_core.tests.fixtures.factories import make_input, make_profile, make_report


BUILDER = PromptBuilder()


def test_prompt_is_scoped_to_the_agent_input_signature():
    # GROUND-1: build takes ONLY the MemoAgentInput.
    assert list(inspect.signature(PromptBuilder.build).parameters) == ["self", "agent_input"]


def test_prompt_grounds_only_in_the_handed_report_rule_ids():
    agent_input = make_input(report=make_report(rule_ids=("R-AGE-1", "R-DTI-1")))
    prompt = BUILDER.build(agent_input)
    assert "R-AGE-1" in prompt and "R-DTI-1" in prompt
    assert "RULE REPORT" in prompt


def test_no_mcp_client_is_constructed_in_p1():
    # GROUND-1: no MCP / tool fetch in Phase 1 (checks actual imports, not prose).
    assert "mcp" not in _top_level_imports(pb_module)


def test_prompt_enforces_advisory_language():
    prompt = BUILDER.build(make_input())
    assert "recommendation" in prompt.lower()
    assert "never call it a 'decision'" in prompt
    assert "MUST NOT change" in prompt


def test_prompt_excludes_demographics_bias_free():
    profile = make_profile()
    prompt = BUILDER.build(make_input(profile=profile))
    assert profile.demographics.full_name not in prompt
    assert profile.demographics.city not in prompt
    assert profile.demographics.gender.value not in prompt


def test_prompt_is_deterministic():
    agent_input = make_input()
    assert BUILDER.build(agent_input) == BUILDER.build(agent_input)


def test_prompt_includes_bmi_when_present():
    from decimal import Decimal

    profile = make_profile().model_copy(update={"bmi_derived": Decimal("27.5")})
    prompt = BUILDER.build(make_input(profile=profile))
    assert "bmi: 27.5" in prompt


# --------------------------------------------------------------------------
# ⛔ Register #33 X1 — changes (j), (k), (l).
#
# ⚠️ THE HONEST LIMIT OF THESE TESTS (plan §1.1): X1 changes what is ASKED of a
# model, and NO unit test can verify that a model COMPLIES. These assert the
# instruction is PRESENT and well-formed. #33 is NOT closed by them going green —
# only §7's live verification can show a real memo.
# --------------------------------------------------------------------------
def test_the_prompt_asks_for_xml_and_nothing_else():
    """⛔ **(j)** — the defect was that the model was never asked for XML *at all*, so it answered
    in Markdown and `_parse_xml` raised on the first live call."""
    prompt = BUILDER.build(make_input())

    assert "REQUIRED OUTPUT FORMAT:" in prompt
    assert "no Markdown, and no code fence" in prompt


def test_the_four_original_constraints_are_NOT_weakened_by_the_added_sentence():
    """⚠️ **(j) was appended, not substituted.** The advisory-language, read-only-recommendation
    and cite-only-listed-rules constraints predate #33 and must survive it intact."""
    prompt = BUILDER.build(make_input())

    assert "never call it a 'decision'" in prompt
    assert "MUST NOT change, override, or state a different recommendation" in prompt
    assert "it is fixed and read-only" in prompt
    assert "never invent or infer a rule that is not listed" in prompt


def test_the_format_block_names_the_EXACT_elements_the_parser_reads():
    """⛔ **(k)** — `GeminiAdapter._parse_xml` reads `narrative_prose` and
    `./cited_rule_ids/rule_id` **by exact path**. ⚠️ A well-formed document with any other names
    parses to SILENCE: empty prose, no citations, no exception. These four names are the
    contract, so the test names them literally rather than trusting a substring of the block."""
    prompt = BUILDER.build(make_input())

    assert "<memo>" in prompt
    assert "<narrative_prose>" in prompt
    assert "<cited_rule_ids>" in prompt
    assert "<rule_id>" in prompt


def test_the_worked_examples_placeholder_carries_the_underscore_that_defends_it():
    """⛔ **(l)** — the second, independent defense against register #35: the placeholder must not
    be shaped like a rule id, and rule ids in this build are HYPHENATED.

    ⚠️ **The cross-unit half of this assertion deliberately lives elsewhere.** Checking it against
    the offline double's real `_RULE_ID_PATTERN` would mean a file inside the FROZEN
    `memo_agent_core` tree importing `backend.app` — ⛔ **the composition root importing its units
    is the only legal direction**, and `test_frozen_untouched.py` enforces it. That assertion is
    therefore made on the app side, in `test_offline_double_citation_invariant.py`, where importing
    both is legitimate. ⚑ Here we pin only what is local to this unit."""
    from backend.memo_agent_core.prompt_builder import EXAMPLE_RULE_ID

    assert "_" in EXAMPLE_RULE_ID, "the underscore IS the defense"
    assert "-" not in EXAMPLE_RULE_ID, "a hyphen would make it match the rule-id shape"


def test_the_format_block_is_appended_LAST_after_the_applicant_facts():
    """⛔ The POSITION is load-bearing for register #35, not cosmetic. `APPLICANT FACTS
    (non-demographic):` is the closing bound of the offline double's extraction region; the
    worked example must fall OUTSIDE it. ⚑ This test is what fails if someone later moves the
    block 'somewhere tidier' — and the failure would otherwise be a silently mis-cited memo."""
    prompt = BUILDER.build(make_input())

    assert prompt.index("APPLICANT FACTS (non-demographic):") < prompt.index(
        "REQUIRED OUTPUT FORMAT:"
    )
    assert prompt.rstrip().endswith("must never appear in your reply.")
