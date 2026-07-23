"""End-to-end memo sub-flow against the FakeProvider (no live LLM anywhere).

Wires MemoAgentInputBuilder -> LangGraphOrchestrator and exercises the whole
flow: happy path, retry-recover, retry-exhaust->flag, CON-BR2 across the flow,
deterministic memo_hash, and deterministic missing_information.
"""
from __future__ import annotations

from backend.intake.schema import DocStatus, DocType, DocumentEntry
from backend.rules_engine.report_schema import Confidence, Recommendation
from backend.memo_agent_core.constants import MEMO_CITATION_RETRY_CAP
from backend.memo_agent_core.input_builder import MemoAgentInputBuilder
from backend.memo_agent_core.memo_hash_adapter import MemoHashAdapter
from backend.memo_agent_core.orchestrator import LangGraphOrchestrator
from backend.memo_agent_core.schemas import MissingInfoSource
from backend.memo_agent_core.telemetry import TelemetryEmitter
from backend.memo_agent_core.tests.fixtures.factories import make_profile, make_report, make_rulebook
from backend.memo_agent_core.tests.fixtures.fake_provider import (
    FakeProvider,
    always_hallucinate_script,
    recover_within_cap_script,
    valid_output,
)

_RULE_IDS = ("R-AGE-1", "R-DTI-1")
_BUILDER = MemoAgentInputBuilder()


def _run(script, *, profile=None, recommendation=Recommendation.APPROVE, confidence=Confidence.HIGH,
         not_evaluated=(), telemetry=None):
    report = make_report(
        rule_ids=_RULE_IDS, recommendation=recommendation, confidence=confidence, not_evaluated=not_evaluated
    )
    agent_input = _BUILDER.build(applicant_profile=profile or make_profile(), rule_report=report)
    orch = LangGraphOrchestrator(
        FakeProvider(script), rulebook=make_rulebook(rule_ids=_RULE_IDS),
        model_version="fake-1", telemetry=telemetry,
    )
    return orch.run(agent_input)


def test_e2e_happy_path_produces_a_pending_verifiable_memo():
    emitter = TelemetryEmitter()
    memo = _run([valid_output(["R-AGE-1"])], telemetry=emitter)
    assert memo is not None
    assert memo.narrative_prose
    assert memo.cited_rule_ids == ["R-AGE-1"]
    assert memo.recommendation is Recommendation.APPROVE
    assert MemoHashAdapter().verify(memo) is True
    assert emitter.events[-1].outcome == "finalized"


def test_e2e_retry_recovers_within_cap():
    script = recover_within_cap_script(MEMO_CITATION_RETRY_CAP, valid_cited=["R-AGE-1"])
    memo = _run(script, recommendation=Recommendation.REFER)
    assert memo is not None
    assert memo.recommendation is Recommendation.REFER


def test_e2e_retry_exhausts_and_blocks_no_memo_surfaces():
    memo = _run(always_hallucinate_script(), recommendation=Recommendation.DECLINE_RECOMMEND)
    assert memo is None  # blocked — no hallucinated rule reaches the underwriter


def test_e2e_conbr2_contradictory_prose_keeps_injected_recommendation():
    draft = valid_output(["R-AGE-1"]).model_copy(update={"narrative_prose": "I recommend APPROVE."})
    memo = _run([draft], recommendation=Recommendation.DECLINE_RECOMMEND)
    assert memo is not None
    assert memo.recommendation is Recommendation.DECLINE_RECOMMEND


def test_e2e_memo_hash_is_deterministic_across_runs():
    hashes = {
        _run([valid_output(["R-AGE-1"])]).memo_hash
        for _ in range(3)
    }
    assert len(hashes) == 1


def test_e2e_missing_information_is_deterministic_and_ordered():
    profile = make_profile(
        incomplete=True,
        entries=[
            DocumentEntry(doc_type=DocType.SALARY_SLIP, status=DocStatus.MISSING, content_hash=""),
            DocumentEntry(doc_type=DocType.BANK_STATEMENT, status=DocStatus.PARSED, content_hash="h"),
            DocumentEntry(doc_type=DocType.MEDICAL_QUESTIONNAIRE, status=DocStatus.PARSED, content_hash="h"),
        ],
    )
    memo = _run([valid_output(["R-AGE-1"])], profile=profile, not_evaluated=("R-DTI-1",))
    got = [(i.source, i.detail) for i in memo.missing_information]
    assert got == [
        (MissingInfoSource.MISSING_DOCUMENT, "salary_slip"),
        (MissingInfoSource.NOT_EVALUATED_RULE, "R-DTI-1"),
        (MissingInfoSource.INCOMPLETE_FLAG, "profile_incomplete"),
    ]
    assert MemoHashAdapter().verify(memo) is True
