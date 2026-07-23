"""Synthetic factories for memo-agent-core tests (DATA-4 — synthetic only).

Builds valid intake ``ApplicantProfile``, rules-engine ``RuleResultReport`` /
``Rulebook``, and ``MemoAgentInput`` instances. Demographics are present but
carry no outcome influence (CON-BR1). Nothing here calls an LLM.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.intake.schema import (
    ApplicantProfile,
    Demographics,
    DocStatus,
    DocType,
    DocumentEntry,
    DocumentManifest,
    Gender,
)
from backend.rules_engine.report_schema import (
    Confidence,
    Operator,
    OutcomeTier,
    Recommendation,
    RuleCategory,
    RuleResult,
    RuleResultReport,
    RuleStatus,
)
from backend.rules_engine.rulebook_schema import ConfidenceBands, Rule, Rulebook

from backend.memo_agent_core.schemas import MemoAgentInput


def make_profile(*, incomplete: bool = False, entries=None, health_flags=None) -> ApplicantProfile:
    default_entries = [
        DocumentEntry(doc_type=DocType.SALARY_SLIP, status=DocStatus.PARSED, content_hash="h1"),
        DocumentEntry(doc_type=DocType.BANK_STATEMENT, status=DocStatus.PARSED, content_hash="h2"),
        DocumentEntry(doc_type=DocType.MEDICAL_QUESTIONNAIRE, status=DocStatus.PARSED, content_hash="h3"),
    ]
    ents = default_entries if entries is None else entries
    docs = DocumentManifest(
        expected_count=len(ents),
        satisfied_count=sum(1 for e in ents if e.status is DocStatus.PARSED),
        entries=ents,
    )
    return ApplicantProfile(
        application_id="APP-0001",
        date_of_birth=date(1990, 1, 1),
        as_of_date=date(2026, 1, 1),
        age_years_derived=36,
        verifiable_income_annual=Decimal("1200000"),
        requested_cover_amount=Decimal("5000000"),
        health_flags=health_flags or [],
        incomplete=incomplete,
        demographics=Demographics(full_name="Test Person", gender=Gender.UNSPECIFIED, city="Testville"),
        documents=docs,
    )


def make_rule_result(
    rule_id: str,
    *,
    status: RuleStatus = RuleStatus.PASS,
    category: RuleCategory = RuleCategory.AGE_ELIGIBILITY,
    outcome_tier: OutcomeTier = OutcomeTier.PASS_ONLY,
) -> RuleResult:
    return RuleResult(
        rule_id=rule_id,
        category=category,
        status=status,
        actual_value=None if status is RuleStatus.NOT_EVALUATED else Decimal("36"),
        operator=Operator.LTE,
        threshold=Decimal("65"),
        outcome_tier=outcome_tier,
        message=f"{rule_id} {status.value}",
    )


def make_report(
    *,
    rule_ids=("R-AGE-1", "R-DTI-1"),
    recommendation: Recommendation = Recommendation.APPROVE,
    confidence: Confidence = Confidence.HIGH,
    not_evaluated=(),
) -> RuleResultReport:
    results = [
        make_rule_result(rid, status=(RuleStatus.NOT_EVALUATED if rid in not_evaluated else RuleStatus.PASS))
        for rid in rule_ids
    ]
    return RuleResultReport(
        rule_results=results,
        recommendation=recommendation,
        confidence=confidence,
        rulebook_version="1.0.0",
        content_hash="rb-hash",
        engine_version="eng-sha",
        decline_reasons=[],
        refer_reasons=[],
    )


def make_rulebook(*, rule_ids=("R-AGE-1", "R-DTI-1")) -> Rulebook:
    rules = [
        Rule(
            rule_id=rid,
            category=RuleCategory.AGE_ELIGIBILITY,
            input_fields=["age_years_derived"],
            operator=Operator.LTE,
            threshold=Decimal("65"),
            outcome=OutcomeTier.DECLINE_FAIL,
            rationale_message=f"{rid} rationale",
        )
        for rid in rule_ids
    ]
    return Rulebook(
        rulebook_version="1.0.0",
        content_hash="rb-hash",
        rules=rules,
        confidence_bands=ConfidenceBands(high_margin=Decimal("0.2"), low_margin=Decimal("0.05")),
    )


def make_input(*, profile=None, report=None, recommendation=None, confidence=None) -> MemoAgentInput:
    rep = report or make_report()
    return MemoAgentInput(
        applicant_profile=profile or make_profile(),
        rule_report=rep,
        recommendation=recommendation or rep.recommendation,
        confidence=confidence or rep.confidence,
    )
