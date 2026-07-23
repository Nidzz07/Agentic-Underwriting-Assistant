"""LangGraphOrchestrator — CON-BR2-STATE, CON-BR2-COMMIT, CITE-FAILURE (both directions).

All against the injected FakeProvider — no live LLM anywhere, including the retry loop.
"""
from __future__ import annotations

import ast
import inspect
from typing import Annotated, Optional, TypedDict

import pytest
from langgraph.graph import END, START, StateGraph

from backend.rules_engine.report_schema import Confidence, Recommendation
from backend.memo_agent_core import orchestrator as orch_module
from backend.memo_agent_core.constants import MEMO_CITATION_RETRY_CAP
from backend.memo_agent_core.memo_hash_adapter import MemoHashAdapter
from backend.memo_agent_core.orchestrator import LangGraphOrchestrator, _reject_channel_write
from backend.memo_agent_core.telemetry import TelemetryEmitter
from backend.memo_agent_core.tests.fixtures.factories import make_input, make_report, make_rulebook
from backend.memo_agent_core.tests.fixtures.fake_provider import (
    FakeProvider,
    always_hallucinate_script,
    recover_within_cap_script,
    valid_output,
)

_RULE_IDS = ("R-AGE-1", "R-DTI-1")


def _build(script, *, recommendation=Recommendation.APPROVE, confidence=Confidence.HIGH, telemetry=None):
    report = make_report(rule_ids=_RULE_IDS, recommendation=recommendation, confidence=confidence)
    agent_input = make_input(report=report)
    orch = LangGraphOrchestrator(
        FakeProvider(script),
        rulebook=make_rulebook(rule_ids=_RULE_IDS),
        model_version="fake-provider",
        telemetry=telemetry,
    )
    return orch, agent_input


# --------------------------------------------------------------------------
# Happy path
# --------------------------------------------------------------------------
def test_happy_path_finalizes_a_verifiable_memo():
    orch, agent_input = _build([valid_output(["R-AGE-1"])])
    memo = orch.run(agent_input)
    assert memo is not None
    assert orch._provider.call_count == 1
    assert MemoHashAdapter().verify(memo) is True
    assert memo.recommendation is Recommendation.APPROVE


# --------------------------------------------------------------------------
# CITE-FAILURE — both directions, both importing MEMO_CITATION_RETRY_CAP
# --------------------------------------------------------------------------
def test_retry_recovers_within_cap():
    script = recover_within_cap_script(MEMO_CITATION_RETRY_CAP, valid_cited=["R-AGE-1"])
    orch, agent_input = _build(script, recommendation=Recommendation.REFER)
    memo = orch.run(agent_input)
    assert memo is not None                                   # recovered → finalized
    assert orch._provider.call_count == MEMO_CITATION_RETRY_CAP
    assert memo.recommendation is Recommendation.REFER        # injected, unchanged
    assert MemoHashAdapter().verify(memo) is True


def test_retry_exhausts_cap_then_flags_recommendation_stands():
    telemetry = TelemetryEmitter()
    orch, agent_input = _build(
        always_hallucinate_script(), recommendation=Recommendation.DECLINE_RECOMMEND, telemetry=telemetry
    )
    memo = orch.run(agent_input)
    assert memo is None                                       # blocked — no memo surfaced
    assert orch._provider.call_count == MEMO_CITATION_RETRY_CAP
    # No hallucinated rule reached the underwriter; the deterministic recommendation stands.
    assert telemetry.events[-1].outcome == "blocked"
    assert telemetry.events[-1].recommendation == Recommendation.DECLINE_RECOMMEND.value


# --------------------------------------------------------------------------
# CON-BR2-STATE — the recommendation cannot change inside the graph
# --------------------------------------------------------------------------
def test_contradictory_prose_does_not_change_the_recommendation():
    contradictory = valid_output(["R-AGE-1"])  # valid citation, but...
    contradictory = contradictory.model_copy(update={"narrative_prose": "I recommend APPROVE instead."})
    orch, agent_input = _build([contradictory], recommendation=Recommendation.DECLINE_RECOMMEND)
    memo = orch.run(agent_input)
    assert memo is not None
    assert memo.recommendation is Recommendation.DECLINE_RECOMMEND  # injected value stands


def test_read_only_channel_reducer_raises_on_write():
    with pytest.raises(RuntimeError):
        _reject_channel_write(Recommendation.APPROVE, Recommendation.REFER)


def test_a_node_writing_the_recommendation_channel_is_rejected():
    # Directly prove the reducer blocks a node write (seeding is allowed).
    class _S(TypedDict):
        recommendation: Annotated[Optional[str], _reject_channel_write]
        work: Optional[str]

    def _bad(state):
        return {"recommendation": "HACKED"}

    graph = StateGraph(_S)
    graph.add_node("n", _bad)
    graph.add_edge(START, "n")
    graph.add_edge("n", END)
    app = graph.compile()
    with pytest.raises(RuntimeError):
        app.invoke({"recommendation": "APPROVE", "work": None})


# --------------------------------------------------------------------------
# CON-BR2-COMMIT — the unit constructs no commit path
# --------------------------------------------------------------------------
def test_orchestrator_constructs_no_commit_path():
    # AST-based (code references, not docstring prose): no commit module imported
    # and no DecisionCommitService symbol referenced anywhere in the code.
    tree = ast.parse(inspect.getsource(orch_module))
    imported: set[str] = set()
    referenced: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.Name):
            referenced.add(node.id)
        elif isinstance(node, ast.Attribute):
            referenced.add(node.attr)
    assert not any("commit" in m.lower() for m in imported)
    assert "DecisionCommitService" not in referenced
    assert "commit" not in {r.lower() for r in referenced}


# --------------------------------------------------------------------------
# TEMP0-1 (call site) — the draft node calls complete(prompt, schema), no temperature
# --------------------------------------------------------------------------
def test_draft_node_calls_provider_without_a_temperature_argument():
    from backend.memo_agent_core.schemas import MemoDraftOutput

    orch, agent_input = _build([valid_output(["R-AGE-1"])])
    orch.run(agent_input)
    fake = orch._provider
    assert fake.call_count == 1
    assert fake.calls[0].schema is MemoDraftOutput  # only (prompt, schema) recorded — no temperature
