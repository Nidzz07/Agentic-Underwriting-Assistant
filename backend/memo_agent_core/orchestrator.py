"""LangGraphOrchestrator — the C4 memo sub-flow (CON-BR2-STATE / CITE-FAILURE / CON-BR2-COMMIT).

Scoped to the memo sub-flow ONLY: ``draft -> validate -> retry/finalize`` (+ ``flag``).
Checkpointer **NO** (register **#34**, candidate C2); in-graph interrupt **NO** — the
human approval gate is EXTERNAL (``DecisionCommitService`` in audit-store). This unit
constructs **no** commit path (CON-BR2-COMMIT): it produces a pending advisory
``DecisionMemo`` and never commits.

⛔ **This previously read "Checkpointer YES (``MemorySaver``, in-process — retry loop +
durability + 100%-step tracing)", and all three justifications were false.** Stated
rather than silently dropped, because the checkpointer did active harm: drafting one
application **twice** raised ``RuntimeError`` from :func:`_reject_channel_write`
(register #34).

* *retry loop* — the ``add_conditional_edges`` cycle is plain graph state. ⚑ **Reproduced
  working with no checkpointer at all**: bad-then-good provider → 2 calls, memo finalized.
* *durability* — ``MemorySaver`` is in-process, and ⛔ **nothing anywhere ever read a
  checkpoint back**: no ``get_state``, ``update_state``, ``get_state_history``,
  ``.stream``, ``astream`` or ``interrupt`` exists in this repository.
* *100%-step tracing* — ⛔ tracing was **never** wired through the checkpointer, and
  ``observability.TraceRecorder.on_step`` has **no production caller at all**. ⚠️ That
  claim was false **before** C2, not because of it (owned by OBS-SINK-DEFERRED).

**CON-BR2-STATE**: ``recommendation`` + ``confidence`` are **read-only channels** —
their reducer (:func:`_reject_channel_write`) raises on any node write. ⚑ **No node
returns those keys, so they can never change inside the graph** — that half is
unchanged, and it is what CON-BR2-STATE actually rests on.

⚠️ **The seeding claim was narrower than it read.** *"LangGraph does not run the reducer
on the initial input"* holds **only for a thread whose channels are ``MISSING``** — i.e.
one with no existing checkpoint. ⚑ It was affirmatively tested at build time
(``audit.md:760``, *"verified LangGraph doesn't call the reducer on seed"*), but that
test compiled its graph **without** a checkpointer, so **the no-checkpoint case was the
only one ever exercised**. With a checkpointer, invoke #2 of the same ``thread_id``
**restored** the channels, seeding took the reducer branch, and the reducer fired on a
**seed**. C2 removes the checkpointer, so the precondition now always holds.

**Bounded retry (CITE-FAILURE)**: on ``citation_failure`` with attempts left the
graph re-drafts; at ``MEMO_CITATION_RETRY_CAP`` attempts it flags (memo blocked,
the deterministic recommendation stands). The cap is imported from
``constants`` — the single source of truth.
"""
from __future__ import annotations

import time
from typing import Annotated, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from backend.rules_engine.report_schema import Confidence, Recommendation
from backend.rules_engine.rulebook_schema import Rulebook
from backend.memo_agent_core.assembler import MemoAssembler
from backend.memo_agent_core.citation_validator import CitationValidator
from backend.memo_agent_core.constants import MEMO_CITATION_RETRY_CAP
from backend.memo_agent_core.memo_hash_adapter import MemoHashAdapter
from backend.memo_agent_core.missing_info import MissingInfoDeriver
from backend.memo_agent_core.prompt_builder import PromptBuilder
from backend.memo_agent_core.provider import ProviderAbstraction
from backend.memo_agent_core.schemas import (
    CitationValidationResult,
    DecisionMemo,
    MemoAgentInput,
    MemoDraftOutput,
)
from backend.memo_agent_core.telemetry import MemoTelemetryEvent, TelemetryEmitter


def _reject_channel_write(current, update):
    """Reducer for the read-only ``recommendation``/``confidence`` channels.

    ⛔ **If you are reading this because this error just fired**: reaching here means a
    node returned ``recommendation`` or ``confidence``, which is a real CON-BR2-STATE
    violation. **The behaviour is unchanged and deliberate** — it still raises on any
    node write.

    ⚠️ **It has, however, fired once for a reason that was NOT a node write** (register
    **#34**). LangGraph skips this reducer on seeded input only while the channel is
    ``MISSING``. This graph was compiled with a ``MemorySaver`` and ``run()`` keys the
    thread by ``application_id``, so the **second** draft of one application restored the
    channels, seeding took the reducer branch, and this raised with ``current == update``
    — the seed's own value, with no node involved. ⚑ **C2 removed the checkpointer**, so
    that precondition now always holds.

    ⚑ **The diagnostic**: if ``current == update`` and no node returns these keys, suspect
    a **reintroduced checkpointer**, not a CON-BR2-STATE breach.
    """
    raise RuntimeError(
        "recommendation/confidence are read-only channels (CON-BR2-STATE); no node may write them"
    )


class _MemoState(TypedDict):
    agent_input: MemoAgentInput
    rulebook: Rulebook
    model_version: str
    recommendation: Annotated[Recommendation, _reject_channel_write]  # read-only
    confidence: Annotated[Confidence, _reject_channel_write]          # read-only
    draft: Optional[MemoDraftOutput]
    validation: Optional[CitationValidationResult]
    attempts: int
    memo: Optional[DecisionMemo]
    blocked: bool


class LangGraphOrchestrator:
    """Runs the memo sub-flow against an injected ``ProviderAbstraction``."""

    def __init__(
        self,
        provider: ProviderAbstraction,
        *,
        rulebook: Rulebook,
        model_version: str,
        telemetry: Optional[TelemetryEmitter] = None,
    ) -> None:
        self._provider = provider
        self._rulebook = rulebook
        self._model_version = model_version
        self._telemetry = telemetry
        self._prompt_builder = PromptBuilder()
        self._deriver = MissingInfoDeriver()
        self._assembler = MemoAssembler(MemoHashAdapter())
        self._graph = self._build_graph()

    # -- nodes -------------------------------------------------------------
    def _draft_node(self, state: _MemoState) -> dict:
        prompt = self._prompt_builder.build(state["agent_input"])
        output = self._provider.complete(prompt, MemoDraftOutput)  # no temperature arg
        return {"draft": output, "attempts": state["attempts"] + 1}

    def _validate_node(self, state: _MemoState) -> dict:
        validator = CitationValidator(state["agent_input"].rule_report)
        result = validator.validate_citations(state["draft"], state["rulebook"])
        return {"validation": result}

    def _finalize_node(self, state: _MemoState) -> dict:
        agent_input = state["agent_input"]
        missing = self._deriver.derive(agent_input)
        memo = self._assembler.finalize(
            agent_input=agent_input,
            draft=state["draft"],
            missing_information=missing,
            model_version=state["model_version"],
        )
        return {"memo": memo}

    def _flag_node(self, state: _MemoState) -> dict:
        return {"blocked": True}

    def _route_after_validate(self, state: _MemoState) -> str:
        if state["validation"].all_valid:
            return "finalize"
        if state["attempts"] < MEMO_CITATION_RETRY_CAP:
            return "draft"
        return "flag"

    def _build_graph(self):
        graph = StateGraph(_MemoState)
        graph.add_node("draft", self._draft_node)
        graph.add_node("validate", self._validate_node)
        graph.add_node("finalize", self._finalize_node)
        graph.add_node("flag", self._flag_node)
        graph.add_edge(START, "draft")
        graph.add_edge("draft", "validate")
        graph.add_conditional_edges(
            "validate",
            self._route_after_validate,
            {"finalize": "finalize", "draft": "draft", "flag": "flag"},
        )
        graph.add_edge("finalize", END)
        graph.add_edge("flag", END)
        return graph.compile()

    # -- entry -------------------------------------------------------------
    def run(self, agent_input: MemoAgentInput) -> Optional[DecisionMemo]:
        """Run the sub-flow; return the pending ``DecisionMemo`` or ``None`` if blocked."""
        started = time.perf_counter()
        initial: _MemoState = {
            "agent_input": agent_input,
            "rulebook": self._rulebook,
            "model_version": self._model_version,
            "recommendation": agent_input.recommendation,
            "confidence": agent_input.confidence,
            "draft": None,
            "validation": None,
            "attempts": 0,
            "memo": None,
            "blocked": False,
        }
        config = {"configurable": {"thread_id": agent_input.applicant_profile.application_id}}
        final = self._graph.invoke(initial, config=config)
        memo = final["memo"]
        self._emit(agent_input, final, started)
        return memo

    def _emit(self, agent_input: MemoAgentInput, final: _MemoState, started: float) -> None:
        if self._telemetry is None:
            return
        memo = final["memo"]
        self._telemetry.emit(
            MemoTelemetryEvent(
                application_id=agent_input.applicant_profile.application_id,
                recommendation=agent_input.recommendation.value,
                confidence=agent_input.confidence.value,
                outcome="finalized" if memo is not None else "blocked",
                cited_rule_count=len(memo.cited_rule_ids) if memo else 0,
                missing_info_count=len(memo.missing_information) if memo else 0,
                draft_attempts=final["attempts"],
                duration_ms=int((time.perf_counter() - started) * 1000),
            )
        )
