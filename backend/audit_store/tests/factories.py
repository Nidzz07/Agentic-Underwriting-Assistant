"""Shared test factories for audit-store — synthetic only (DATA-4).

Builders for the frozen record shapes + the imported intake/rules-engine objects,
reused across the unit + integration suites. Not a test module.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from backend.intake import schema as isch
from backend.rules_engine import report_schema as rrs
from backend.audit_store import record_schema as rs


def make_profile(**over) -> isch.ApplicantProfile:
    kw = dict(
        application_id="APP-1", date_of_birth=date(1986, 1, 1), as_of_date=date(2026, 1, 1),
        age_years_derived=40, height_cm=Decimal("180"), weight_kg=Decimal("71"),
        bmi_derived=Decimal("22.00"), verifiable_income_annual=Decimal("1000000"),
        requested_cover_amount=Decimal("5000000"), existing_debt_obligations_annual=Decimal("300000"),
        employment_type=isch.EmploymentType.SALARIED, smoking_status=isch.SmokingStatus.NON_SMOKER,
        occupation="engineer", health_flags=[], incomplete=False,
        demographics=isch.Demographics(full_name="Ada Byron", gender=isch.Gender.FEMALE, city="Metropolis"),
        documents=isch.DocumentManifest(expected_count=3, satisfied_count=3, entries=[]),
    )
    kw.update(over)
    return isch.ApplicantProfile(**kw)


def make_report(**over) -> rrs.RuleResultReport:
    kw = dict(
        rule_results=[rrs.RuleResult(
            rule_id="DTI-1", category=rrs.RuleCategory.FINANCIAL_DTI, status=rrs.RuleStatus.PASS,
            actual_value=Decimal("0.30"), operator=rrs.Operator.LTE, threshold=Decimal("0.40"),
            outcome_tier=rrs.OutcomeTier.PASS_ONLY, message="dti 0.30 within 0.40")],
        recommendation=rrs.Recommendation.APPROVE, confidence=rrs.Confidence.HIGH,
        rulebook_version="1.0.0", content_hash="rulebook-hash", engine_version="eng-sha-1",
        decline_reasons=[], refer_reasons=[],
    )
    kw.update(over)
    return rrs.RuleResultReport(**kw)


def make_tuple(**over) -> rs.AuditTuple:
    kw = dict(
        rulebook_version="1.0.0", rule_results=make_report(),
        timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        model_version="gemini-1.5", memo_hash="memo-hash-1", engine_version="eng-sha-1",
    )
    kw.update(over)
    return rs.AuditTuple(**kw)


def make_snapshot(**over) -> rs.ApplicantProfileSnapshot:
    kw = dict(application_id="APP-1", profile=make_profile(), content_hash="profile-hash-1")
    kw.update(over)
    return rs.ApplicantProfileSnapshot(**kw)


def make_committed(**over) -> rs.CommittedDecision:
    kw = dict(recommendation_id="REC-1", underwriter_id="UW-1",
              action=rs.CommitAction.APPROVE, reason=None)
    kw.update(over)
    return rs.CommittedDecision(**kw)


def make_record(**over) -> rs.AuditRecord:
    kw = dict(
        decision_id="DEC-1", application_id="APP-1", recommendation_id="REC-1",
        audit_tuple=make_tuple(), applicant_profile_snapshot=make_snapshot(),
        committed_decision=make_committed(),
        status=rs.DecisionStatus.ACTIVE, supersedes_decision_id=None,
    )
    kw.update(over)
    return rs.AuditRecord(**kw)


def make_context(**over) -> rs.CommitContext:
    kw = dict(
        rule_results=make_report(), memo_hash="memo-hash-1", model_version="gemini-1.5",
        engine_version="eng-sha-1", rulebook_version="1.0.0", applicant_profile=make_profile(),
    )
    kw.update(over)
    return rs.CommitContext(**kw)
