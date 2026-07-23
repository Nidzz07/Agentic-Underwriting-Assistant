"""Shared test fixtures/factories for memo-extensions (U19) — synthetic, offline only.

One factory module reused across the teeth (Q2-A). Builds: the capturing
``ThinkingLLMClient`` double (records the outgoing request), the fake
``DecisionRecordSource`` (seeded incl. a demographic swap pair) + a failing variant, the
frozen rules-engine / audit-store shapes by value, a U19-local ``OutlierSignal`` fake, and
a BY-VALUE U18 ``OutlierResult`` stand-in (never importing ``outlier_model``). No network,
no key, no live DB, no live MCP server.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from backend.intake import schema as isch
from backend.rules_engine import report_schema as rrs
from backend.rules_engine import rulebook_schema as rbs
from backend.audit_store import record_schema as ars

from backend.memo_extensions import mcp_tools as mt

# --------------------------------------------------------------------------
# A canned valid LLM XML output (narrative_prose + one cited rule id).
# --------------------------------------------------------------------------
VALID_MEMO_XML = (
    "<memo>"
    "<narrative_prose>Advisory recommendation prose; underwriter review required.</narrative_prose>"
    "<cited_rule_ids><rule_id>DTI-1</rule_id></cited_rule_ids>"
    "</memo>"
)


class CapturingThinkingClient:
    """A capturing double implementing the U19-local ``ThinkingLLMClient`` seam. Records
    every outgoing request; returns a fixed valid XML. No network, no key."""

    def __init__(self, raw_xml: str = VALID_MEMO_XML) -> None:
        self._raw_xml = raw_xml
        self.calls: list[dict] = []

    def generate(self, *, model: str, prompt: str, temperature: float, thinking: bool) -> str:
        self.calls.append(
            {"model": model, "prompt": prompt, "temperature": temperature, "thinking": thinking}
        )
        return self._raw_xml


# --------------------------------------------------------------------------
# rules-engine shapes (mirroring the audit-store factory conventions).
# --------------------------------------------------------------------------
def make_rule_result(
    *,
    rule_id: str = "DTI-1",
    category: rrs.RuleCategory = rrs.RuleCategory.FINANCIAL_DTI,
    status: rrs.RuleStatus = rrs.RuleStatus.PASS,
    actual_value=Decimal("0.30"),
    operator: rrs.Operator = rrs.Operator.LTE,
    threshold=Decimal("0.40"),
    outcome_tier: rrs.OutcomeTier = rrs.OutcomeTier.PASS_ONLY,
    message: str = "dti within band",
) -> rrs.RuleResult:
    return rrs.RuleResult(
        rule_id=rule_id, category=category, status=status, actual_value=actual_value,
        operator=operator, threshold=threshold, outcome_tier=outcome_tier, message=message,
    )


def make_report(
    *,
    rule_results: list[rrs.RuleResult] | None = None,
    recommendation: rrs.Recommendation = rrs.Recommendation.APPROVE,
    confidence: rrs.Confidence = rrs.Confidence.HIGH,
    rulebook_version: str = "1.0.0",
) -> rrs.RuleResultReport:
    return rrs.RuleResultReport(
        rule_results=rule_results if rule_results is not None else [make_rule_result()],
        recommendation=recommendation, confidence=confidence,
        rulebook_version=rulebook_version, content_hash="rulebook-hash",
        engine_version="eng-sha-1", decline_reasons=[], refer_reasons=[],
    )


def make_rulebook(rule_ids: tuple[str, ...] = ("DTI-1",)) -> rbs.Rulebook:
    rules = [
        rbs.Rule(
            rule_id=rid, category=rrs.RuleCategory.FINANCIAL_DTI, input_fields=["dti_ratio"],
            operator=rrs.Operator.LTE, threshold=Decimal("0.40"),
            outcome=rrs.OutcomeTier.REFER_TRIGGER,
            rationale_message=f"Debt-to-income ceiling rule {rid}.", irdai_ref="IRDAI-2024-DTI",
        )
        for rid in rule_ids
    ]
    return rbs.Rulebook(
        rulebook_version="1.0.0", content_hash="rulebook-hash", rules=rules,
        confidence_bands=rbs.ConfidenceBands(high_margin=Decimal("0.10"), low_margin=Decimal("0.05")),
    )


# --------------------------------------------------------------------------
# audit-store committed-decision records (carry demographics via the profile).
# --------------------------------------------------------------------------
def make_profile(
    *, full_name: str = "Ada Byron", gender: isch.Gender = isch.Gender.FEMALE, city: str = "Metropolis"
) -> isch.ApplicantProfile:
    return isch.ApplicantProfile(
        application_id="APP-1", date_of_birth=date(1986, 1, 1), as_of_date=date(2026, 1, 1),
        age_years_derived=40, height_cm=Decimal("180"), weight_kg=Decimal("71"),
        bmi_derived=Decimal("22.00"), verifiable_income_annual=Decimal("1000000"),
        requested_cover_amount=Decimal("5000000"), existing_debt_obligations_annual=Decimal("300000"),
        employment_type=isch.EmploymentType.SALARIED, smoking_status=isch.SmokingStatus.NON_SMOKER,
        occupation="engineer", health_flags=[], incomplete=False,
        demographics=isch.Demographics(full_name=full_name, gender=gender, city=city),
        documents=isch.DocumentManifest(expected_count=3, satisfied_count=3, entries=[]),
    )


def make_record(
    *,
    decision_id: str = "DEC-1",
    recommendation: rrs.Recommendation = rrs.Recommendation.REFER,
    confidence: rrs.Confidence = rrs.Confidence.MEDIUM,
    profile: isch.ApplicantProfile | None = None,
) -> ars.AuditRecord:
    report = make_report(recommendation=recommendation, confidence=confidence)
    tuple_ = ars.AuditTuple(
        rulebook_version="1.0.0", rule_results=report,
        timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        model_version="gemini-2.5-flash", memo_hash="memo-hash-1", engine_version="eng-sha-1",
    )
    snapshot = ars.ApplicantProfileSnapshot(
        application_id="APP-1", profile=profile if profile is not None else make_profile(),
        content_hash="profile-hash-1",
    )
    committed = ars.CommittedDecision(
        recommendation_id="REC-1", underwriter_id="UW-1", action=ars.CommitAction.APPROVE, reason=None,
    )
    return ars.AuditRecord(
        decision_id=decision_id, application_id="APP-1", recommendation_id="REC-1",
        audit_tuple=tuple_, applicant_profile_snapshot=snapshot, committed_decision=committed,
        status=ars.DecisionStatus.ACTIVE, supersedes_decision_id=None,
    )


def demographic_swap_pair() -> tuple[ars.AuditRecord, ars.AuditRecord]:
    """Two committed records with IDENTICAL financials/recommendation, differing ONLY in
    full_name/gender/city — the BIAS-1 swap teeth."""
    a = make_record(profile=make_profile(full_name="Ada Byron", gender=isch.Gender.FEMALE, city="Metropolis"))
    b = make_record(profile=make_profile(full_name="Bob Stone", gender=isch.Gender.MALE, city="Gotham"))
    return a, b


class FakeDecisionRecordSource:
    """A fake ``DecisionRecordSource`` seeded with records (no live DB)."""

    def __init__(self, records: list[ars.AuditRecord]) -> None:
        self._records = records

    def recent_records(self, query: mt.PrecedentQuery):
        return list(self._records[: query.limit])


class FailingDecisionRecordSource:
    """A ``DecisionRecordSource`` that always fails — the MISS-1 unavailable handler."""

    def recent_records(self, query: mt.PrecedentQuery):
        raise RuntimeError("decisions-tools transport unavailable (simulated miss)")


def make_service(
    *, rule_ids: tuple[str, ...] = ("DTI-1",), records: list[ars.AuditRecord] | None = None
) -> mt.McpToolService:
    rulebook_tools = mt.RulebookTools(make_rulebook(rule_ids))
    source = FakeDecisionRecordSource(records if records is not None else [make_record()])
    return mt.McpToolService(rulebook_tools, mt.DecisionsTools(source))


def make_failing_service(rule_ids: tuple[str, ...] = ("DTI-1",)) -> mt.McpToolService:
    rulebook_tools = mt.RulebookTools(make_rulebook(rule_ids))
    return mt.McpToolService(rulebook_tools, mt.DecisionsTools(FailingDecisionRecordSource()))


# --------------------------------------------------------------------------
# The outlier read-surface: a U19-local fake + a BY-VALUE U18 OutlierResult stand-in.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class FakeOutlierSignal:
    """A U19-local fake satisfying ``OutlierSignal`` by shape — drives every routing test
    with NO outlier_model import."""

    is_outlier: bool
    outlier_score: float


class ByValueOutlierResult(BaseModel):
    """A frozen model in the U18 ``OutlierResult`` SHAPE, constructed BY VALUE — never
    imported from ``outlier_model``. Carries the extra prose/trace fields the router must
    NOT read, proving the narrow ``OutlierSignal`` Protocol is still satisfied structurally."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    is_outlier: bool
    outlier_score: float
    flagged_features: list[str] = []
    provenance: dict = {}
