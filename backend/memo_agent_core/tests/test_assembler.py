"""MemoAssembler — CON-BR2-TYPE injection + memo_hash compute (finalize)."""
from __future__ import annotations

from backend.rules_engine.report_schema import Confidence, Recommendation
from backend.memo_agent_core.assembler import MemoAssembler
from backend.memo_agent_core.memo_hash_adapter import MemoHashAdapter
from backend.memo_agent_core.schemas import (
    MemoDraftOutput,
    MissingInfoSource,
    MissingInformationItem,
)
from backend.memo_agent_core.tests.fixtures.factories import make_input


ASSEMBLER = MemoAssembler(MemoHashAdapter())


def test_recommendation_and_confidence_come_only_from_the_injected_input():
    # The draft prose contradicts the recommendation; the memo must still carry
    # the injected read-only value (CON-BR2-TYPE) — the draft cannot influence it.
    agent_input = make_input(
        recommendation=Recommendation.DECLINE_RECOMMEND, confidence=Confidence.LOW
    )
    draft = MemoDraftOutput(narrative_prose="I recommend APPROVE.", cited_rule_ids=["R-AGE-1"])
    memo = ASSEMBLER.finalize(
        agent_input=agent_input, draft=draft, missing_information=[], model_version="fake-1"
    )
    assert memo.recommendation is Recommendation.DECLINE_RECOMMEND
    assert memo.confidence is Confidence.LOW
    assert memo.narrative_prose == "I recommend APPROVE."  # prose preserved, but powerless


def test_memo_hash_is_computed_and_verifies():
    agent_input = make_input()
    draft = MemoDraftOutput(narrative_prose="Advisory prose.", cited_rule_ids=["R-AGE-1"])
    missing = [MissingInformationItem(source=MissingInfoSource.INCOMPLETE_FLAG, detail="profile_incomplete")]
    memo = ASSEMBLER.finalize(
        agent_input=agent_input, draft=draft, missing_information=missing, model_version="fake-1"
    )
    assert memo.memo_hash != ""
    assert MemoHashAdapter().verify(memo) is True


def test_model_version_recorded_and_missing_info_passed_through():
    agent_input = make_input()
    draft = MemoDraftOutput(narrative_prose="p", cited_rule_ids=[])
    missing = [MissingInformationItem(source=MissingInfoSource.NOT_EVALUATED_RULE, detail="R-DTI-1")]
    memo = ASSEMBLER.finalize(
        agent_input=agent_input, draft=draft, missing_information=missing, model_version="gemini-x"
    )
    assert memo.model_version == "gemini-x"
    assert memo.missing_information == missing
