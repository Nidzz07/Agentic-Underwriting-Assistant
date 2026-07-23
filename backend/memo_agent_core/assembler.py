"""MemoAssembler — finalize the DecisionMemo (CON-BR2-TYPE injection + memo_hash).

Assembles the three-region ``DecisionMemo``: the LLM-authored ``narrative_prose``
+ ``cited_rule_ids`` (from the validated draft), the deterministic
``missing_information`` (from the deriver), and the **injected read-only**
``recommendation`` + ``confidence`` — sourced from ``agent_input`` (the
deterministic core's values), **never** from the model draft (``MemoDraftOutput``
has no such field). The ``memo_hash`` is computed here via the ``MemoHashAdapter``.
"""
from __future__ import annotations

from typing import Sequence

from backend.memo_agent_core.memo_hash_adapter import MemoHashAdapter
from backend.memo_agent_core.schemas import (
    DecisionMemo,
    MemoAgentInput,
    MemoDraftOutput,
    MissingInformationItem,
)


class MemoAssembler:
    def __init__(self, hash_adapter: MemoHashAdapter) -> None:
        self._hash_adapter = hash_adapter

    def finalize(
        self,
        *,
        agent_input: MemoAgentInput,
        draft: MemoDraftOutput,
        missing_information: Sequence[MissingInformationItem],
        model_version: str,
    ) -> DecisionMemo:
        missing = list(missing_information)
        # RO: recommendation/confidence come ONLY from the injected input, never
        # from the draft — the model cannot influence them (CON-BR2-TYPE).
        recommendation = agent_input.recommendation
        confidence = agent_input.confidence
        memo_hash = self._hash_adapter.compute(
            narrative_prose=draft.narrative_prose,
            cited_rule_ids=draft.cited_rule_ids,
            missing_information=missing,
            recommendation=recommendation,
            confidence=confidence,
        )
        return DecisionMemo(
            narrative_prose=draft.narrative_prose,
            cited_rule_ids=list(draft.cited_rule_ids),
            missing_information=missing,
            recommendation=recommendation,
            confidence=confidence,
            memo_hash=memo_hash,
            model_version=model_version,
        )
