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
