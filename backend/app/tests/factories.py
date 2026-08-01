"""Synthetic record factories for the composition-root tests (DATA-4: synthetic only).

MIRRORED, NOT IMPORTED: audit-store has its own test factories, but they live in a FROZEN unit's
test tree — not its public API. Per the project's reference-not-own discipline, this module
builds the same shapes from each unit's PUBLIC schema instead of importing a sibling's test
internals. The frozen schemas themselves (intake / rules_engine / audit_store) are imported and
used verbatim — never re-declared.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from backend.audit_store import record_schema as rs
from backend.intake import schema as isch
from backend.rules_engine import report_schema as rrs


def make_profile(**over) -> isch.ApplicantProfile:
    kw = dict(
        application_id="APP-1",
        date_of_birth=date(1986, 1, 1),
        as_of_date=date(2026, 1, 1),
        age_years_derived=40,
        verifiable_income_annual=Decimal("1000000"),
        requested_cover_amount=Decimal("5000000"),
        incomplete=False,
        demographics=isch.Demographics(
            full_name="Ada Byron", gender=isch.Gender.FEMALE, city="Metropolis"
        ),
        documents=isch.DocumentManifest(expected_count=3, satisfied_count=3, entries=[]),
    )
    kw.update(over)
    return isch.ApplicantProfile(**kw)


def make_report(**over) -> rrs.RuleResultReport:
    kw = dict(
        rule_results=[
            rrs.RuleResult(
                rule_id="DTI-1",
                category=rrs.RuleCategory.FINANCIAL_DTI,
                status=rrs.RuleStatus.PASS,
                actual_value=Decimal("0.30"),
                operator=rrs.Operator.LTE,
                threshold=Decimal("0.40"),
                outcome_tier=rrs.OutcomeTier.PASS_ONLY,
                message="dti 0.30 within 0.40",
            )
        ],
        recommendation=rrs.Recommendation.APPROVE,
        confidence=rrs.Confidence.HIGH,
        rulebook_version="1.0.0",
        content_hash="rulebook-hash",
        engine_version="eng-sha-1",
        decline_reasons=[],
        refer_reasons=[],
    )
    kw.update(over)
    return rrs.RuleResultReport(**kw)


def make_record(index: int = 1, **over) -> rs.AuditRecord:
    """One synthetic AuditRecord. ``index`` yields stable, distinguishable ids + timestamps."""
    kw = dict(
        decision_id=f"DEC-{index}",
        application_id=f"APP-{index}",
        recommendation_id=f"REC-{index}",
        audit_tuple=rs.AuditTuple(
            rulebook_version="1.0.0",
            rule_results=make_report(),
            timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc) + timedelta(hours=index),
            model_version="gemini-1.5",
            memo_hash=f"memo-hash-{index}",
            engine_version="eng-sha-1",
        ),
        applicant_profile_snapshot=rs.ApplicantProfileSnapshot(
            application_id=f"APP-{index}",
            profile=make_profile(application_id=f"APP-{index}"),
            content_hash=f"profile-hash-{index}",
        ),
        committed_decision=rs.CommittedDecision(
            recommendation_id=f"REC-{index}",
            underwriter_id="UW-1",
            action=rs.CommitAction.APPROVE,
            reason=None,
        ),
        status=rs.DecisionStatus.ACTIVE,
        supersedes_decision_id=None,
    )
    kw.update(over)
    return rs.AuditRecord(**kw)


def make_override_record(index: int = 2) -> rs.AuditRecord:
    """An `override` record — the human namespace's conditional-reason case."""
    return make_record(
        index=index,
        committed_decision=rs.CommittedDecision(
            recommendation_id=f"REC-{index}",
            underwriter_id="UW-1",
            action=rs.CommitAction.OVERRIDE,
            reason="Verified a second income source by phone.",
        ),
    )


# --- pending-state factories + an app-local CaseStore fake (Scope B wiring pass) ----------
# MIRRORED, NOT IMPORTED (the same discipline as the audit factories above): U24 has its own
# InMemoryCaseStore, but it lives in that unit's TEST tree, which is not its public API. This
# builds the same Protocol shape from U24's PUBLIC schemas instead of importing a sibling's
# test internals. The SCHEMAS themselves are imported and used verbatim, never re-declared.

from contextlib import contextmanager
from dataclasses import replace
from typing import Iterator, Optional

from backend.audit_store.canon_adapter import CanonSerAdapter
from backend.case_lifecycle.schemas import PendingApplication, PendingRecommendation
from backend.case_lifecycle.states import CaseState, CommitClaimResult
from backend.memo_agent_core.schemas import DecisionMemo


def make_memo(**over) -> DecisionMemo:
    kw = dict(
        narrative_prose="The applicant meets the debt-to-income band. Advisory only.",
        cited_rule_ids=["DTI-1"],
        missing_information=[],
        recommendation=rrs.Recommendation.APPROVE,
        confidence=rrs.Confidence.HIGH,
        memo_hash="memo-hash-1",
        model_version="gemini-2.5-flash",
    )
    kw.update(over)
    return DecisionMemo(**kw)


def make_case(application_id: str = "APP-1", state: CaseState = CaseState.EVALUATED,
              profile=None, report=None) -> PendingApplication:
    """A pending application carrying CANON-SER bytes, exactly as U24 persists it."""
    profile = profile if profile is not None else make_profile(application_id=application_id)
    report = report if report is not None else make_report()
    return PendingApplication(
        application_id=application_id,
        state=state,
        profile_canonical=CanonSerAdapter.canonical_bytes(profile),
        profile_content_hash=CanonSerAdapter.content_hash(profile),
        rule_results_canonical=CanonSerAdapter.canonical_bytes(report),
        rule_results_content_hash=CanonSerAdapter.content_hash(report),
        rulebook_version=report.rulebook_version,
        engine_version=report.engine_version,
    )


def make_pending_recommendation(recommendation_id: str = "REC-1",
                                application_id: str = "APP-1",
                                memo=None) -> PendingRecommendation:
    memo = memo if memo is not None else make_memo()
    return PendingRecommendation(
        recommendation_id=recommendation_id,
        application_id=application_id,
        memo_canonical=CanonSerAdapter.canonical_bytes(memo),
        memo_hash=memo.memo_hash,
        model_version=memo.model_version,
        engine_version="eng-sha-1",
        rulebook_version="1.0.0",
    )


class InMemoryCaseStore:
    """An app-local ``CaseStore`` satisfying U24's Protocol. Buffers inside ``atomic()``."""

    def __init__(self) -> None:
        self._applications: dict[str, PendingApplication] = {}
        self._recommendations: dict[str, PendingRecommendation] = {}
        self._pending: Optional[list] = None
        #: register #19 — set by the failure-tolerant-recovery test only.
        self.release_raises = False

    @contextmanager
    def atomic(self) -> Iterator[None]:
        self._pending = []
        try:
            yield
        except BaseException:
            self._pending = None
            raise
        else:
            for kind, obj in self._pending:
                if kind == "application":
                    self._applications[obj.application_id] = obj
                else:
                    self._recommendations[obj.recommendation_id] = obj
            self._pending = None

    def _buffer(self, kind: str, obj) -> None:
        if self._pending is None:
            raise RuntimeError("store writes must run inside atomic()")
        self._pending.append((kind, obj))

    def put_application(self, application: PendingApplication) -> None:
        self._buffer("application", application)

    def get_application(self, application_id: str) -> Optional[PendingApplication]:
        return self._applications.get(application_id)

    def put_recommendation(self, recommendation: PendingRecommendation) -> None:
        self._buffer("recommendation", recommendation)

    def get_recommendation(self, recommendation_id: str) -> Optional[PendingRecommendation]:
        return self._recommendations.get(recommendation_id)

    def recommendation_for_application(self, application_id: str) -> Optional[PendingRecommendation]:
        """⚑ Mirrors the shim's ``ORDER BY recommendation_id LIMIT 1`` (register #27, change (e)).

        Same correction as U24's own fake: returning the **first inserted** match made this double
        deterministic where Postgres is not, so it masked the defect rather than exposing it.
        """
        matches = [
            rec for rec in self._recommendations.values()
            if rec.application_id == application_id
        ]
        if not matches:
            return None
        return min(matches, key=lambda rec: rec.recommendation_id)

    def list_application_ids(self) -> list[str]:
        return sorted(self._applications)

    # -- register #19: the two-step commit claim (mirrors U24's semantics) --
    #
    # ⚑ Reproduces the SQL shim's OUTCOMES, not its mechanism: the real guarantee is a Postgres
    # row-level write lock, proven at tier-I in ``case_lifecycle/tests/test_claim_integration.py``.
    # ``release_raises`` exists for the failure-tolerant-recovery test — a recovery that itself
    # throws must not mask the original rejection.

    def _swap_state(self, recommendation_id: str, expected, new) -> bool:
        recommendation = self._recommendations.get(recommendation_id)
        if recommendation is None:
            return False
        application = self._applications.get(recommendation.application_id)
        if application is None or application.state is not expected:
            return False
        with self.atomic():
            self.put_application(replace(application, state=new))
        return True

    def claim_for_commit(self, recommendation_id: str) -> CommitClaimResult:
        if self._recommendations.get(recommendation_id) is None:
            return CommitClaimResult.NOT_FOUND
        won = self._swap_state(recommendation_id, CaseState.DRAFTED, CaseState.COMMITTING)
        return CommitClaimResult.WON if won else CommitClaimResult.LOST

    def finalize_commit(self, recommendation_id: str) -> None:
        self._swap_state(recommendation_id, CaseState.COMMITTING, CaseState.COMMITTED)

    def release_claim(self, recommendation_id: str) -> None:
        if self.release_raises:
            raise RuntimeError("injected recovery failure")
        self._swap_state(recommendation_id, CaseState.COMMITTING, CaseState.DRAFTED)

    # -- test-only seeding helper (not part of the Protocol) --
    def seed(self, *objects) -> "InMemoryCaseStore":
        with self.atomic():
            for obj in objects:
                if isinstance(obj, PendingApplication):
                    self.put_application(obj)
                else:
                    self.put_recommendation(obj)
        return self
