"""C-CASE-8 fixtures — FIVE deliberately-separate NAMED FAMILIES (Q2-A) + the tier-U store fake.

One module per unit with purpose-built families that are NOT reused across targets whose failure
modes differ — the U18/U19/U22 convention.

  * ``clean_case()``               -> STATE-1 · EAGER-1   (the baseline that advances)
  * ``illegal_transition_cases()`` -> STATE-2             (⚑ ONE collection — UNSPLITTABLE)
  * ``drafting_success_double()``  -> STATE-1 · TRIGGER-1 · ROUTE-1
  * ``drafting_failure_double()``  -> FAILED-1 · COMMITBOUND-1(c)  (⚑ its OWN family)
  * ``borderline_refer_case()``    -> ROUTE-1             (a REFER report must route EXTENDED)

⚑ ``illegal_transition_cases()`` returns **one collection** (mirroring ``anchoring_pair()``'s
unsplittability) so STATE-2's rejection set **cannot be trimmed one case at a time**.
⚑ ``drafting_failure_double()`` is **its own family** (mirroring ``exempt_witness_sample()``) so
**FAILED-1 can never be weakened by a success-path edit**.

**The in-memory ``CaseStore`` fake lives HERE, not in production** — the sibling convention (no
unit in this build has a ``tests/fakes.py``). It **buffers-and-discards** exactly like the frozen
``InMemoryAuditRepository``, which is what makes EAGER-1's *"no partial row"* **non-vacuous**
(CASE-ND-Fold-1).

**Demographic-free**: no applicant identifier appears in any prose below. **No RNG, no
wall-clock** — every value is fixed.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import date
from decimal import Decimal
from typing import Iterator, Optional

from backend.case_lifecycle.schemas import PendingApplication, PendingRecommendation
from backend.case_lifecycle.states import CaseState, CommitClaimResult
from backend.intake.schema import (
    ApplicantProfile,
    Demographics,
    DocumentEntry,
    DocumentManifest,
    DocStatus,
    DocType,
    Gender,
)
from backend.memo_agent_core.schemas import DecisionMemo
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

APPLICATION_ID = "case-0001"
RECOMMENDATION_ID = "rec-0001"
_RULE_ID = "DTI-001"


# --- frozen-shape builders (imported read-only; instantiating is USING, not modifying) -----

def make_profile(application_id: str = APPLICATION_ID) -> ApplicantProfile:
    return ApplicantProfile(
        application_id=application_id,
        date_of_birth=date(1988, 5, 4),
        as_of_date=date(2026, 1, 1),
        age_years_derived=40,
        bmi_derived=Decimal("24.0"),
        verifiable_income_annual=Decimal("600000"),
        requested_cover_amount=Decimal("3000000"),
        existing_debt_obligations_annual=Decimal("276000"),
        health_flags=[],
        demographics=Demographics(full_name="Applicant Zero", gender=Gender.FEMALE, city="Pune"),
        documents=DocumentManifest(
            expected_count=1,
            satisfied_count=1,
            entries=[
                DocumentEntry(
                    doc_type=DocType.SALARY_SLIP,
                    status=DocStatus.PARSED,
                    content_hash="hash-0",
                )
            ],
        ),
    )


def make_report(recommendation: Recommendation = Recommendation.APPROVE) -> RuleResultReport:
    return RuleResultReport(
        rule_results=[
            RuleResult(
                rule_id=_RULE_ID,
                category=RuleCategory.FINANCIAL_DTI,
                status=(
                    RuleStatus.PASS
                    if recommendation is Recommendation.APPROVE
                    else RuleStatus.FAIL
                ),
                actual_value=Decimal("46"),
                operator=Operator.LTE,
                threshold=Decimal("40"),
                outcome_tier=(
                    OutcomeTier.PASS_ONLY
                    if recommendation is Recommendation.APPROVE
                    else OutcomeTier.REFER_TRIGGER
                ),
                message="debt-to-income ratio evaluated",
            )
        ],
        recommendation=recommendation,
        confidence=Confidence.MEDIUM,
        rulebook_version="rb-test-v1",
        content_hash="deadbeef",
        engine_version="engine-test-v1",
    )


def make_memo() -> DecisionMemo:
    return DecisionMemo(
        narrative_prose=(
            "The debt-to-income ratio was evaluated against the permitted band and rule "
            "DTI-001 was applied. On that evidence the recommendation is recorded for "
            "underwriter review."
        ),
        cited_rule_ids=[_RULE_ID],
        missing_information=[],
        recommendation=Recommendation.APPROVE,
        confidence=Confidence.MEDIUM,
        memo_hash="memo-hash-1",
        model_version="model-test-v1",
    )


# --- the tier-U store fake — buffers-and-discards (CASE-ND-Fold-1) -------------------------

class InMemoryCaseStore:
    """tier-U ``CaseStore``. ``atomic()`` buffers writes and flushes only on a clean exit —
    the frozen ``InMemoryAuditRepository`` pattern, so *"no partial row"* is NOT vacuous."""

    def __init__(self, fail_on_put: bool = False) -> None:
        self._applications: dict[str, PendingApplication] = {}
        self._recommendations: dict[str, PendingRecommendation] = {}
        self._pending: Optional[list] = None
        self._fail_on_put = fail_on_put
        self.atomic_entries = 0

    @contextmanager
    def atomic(self) -> Iterator[None]:
        self._pending = []
        self.atomic_entries += 1
        try:
            yield
        except BaseException:
            self._pending = None            # rollback — discard everything buffered
            raise
        else:
            for kind, obj in self._pending:  # commit — flush atomically
                if kind == "application":
                    self._applications[obj.application_id] = obj
                else:
                    self._recommendations[obj.recommendation_id] = obj
            self._pending = None

    def _buffer(self, kind: str, obj) -> None:
        if self._pending is None:
            raise RuntimeError("store writes must run inside atomic()")
        self._pending.append((kind, obj))
        if self._fail_on_put:
            raise FaultInjected("injected persist fault")

    def put_application(self, application: PendingApplication) -> None:
        self._buffer("application", application)

    def get_application(self, application_id: str) -> Optional[PendingApplication]:
        return self._applications.get(application_id)

    def put_recommendation(self, recommendation: PendingRecommendation) -> None:
        self._buffer("recommendation", recommendation)

    def get_recommendation(self, recommendation_id: str) -> Optional[PendingRecommendation]:
        return self._recommendations.get(recommendation_id)

    def recommendation_for_application(
        self, application_id: str
    ) -> Optional[PendingRecommendation]:
        for rec in self._recommendations.values():
            if rec.application_id == application_id:
                return rec
        return None

    def list_application_ids(self) -> list[str]:
        """⚑ AUTHORIZED U24 REOPENING (Q1-A). Sorted, mirroring the shim's ``ORDER BY``.

        PERSIST-1 is what keeps this fake and ``PostgresCaseStore`` honest about agreeing.
        """
        return sorted(self._applications)

    # --- register #19: the two-step commit claim ------------------------------------------
    #
    # ⚑ Mirrors the SQL shim's SEMANTICS, not its mechanism. The shim's guarantee comes from a
    # row-level write lock; this fake is single-threaded and has no such lock, so it reproduces
    # the OUTCOMES only. **CLAIM-CONCURRENT-1 (tier-I) is what proves the real guarantee** —
    # and PERSIST-1's lineage is what keeps the two implementations honest about agreeing.

    def _application_for(self, recommendation_id: str) -> Optional[PendingApplication]:
        """The join U24 performs internally: recommendation -> its owning application."""
        recommendation = self._recommendations.get(recommendation_id)
        if recommendation is None:
            return None
        return self._applications.get(recommendation.application_id)

    def _swap_state(
        self, recommendation_id: str, expected: CaseState, new: CaseState
    ) -> bool:
        """Conditional state write — the fake's stand-in for the shim's CAS ``UPDATE``."""
        application = self._application_for(recommendation_id)
        if application is None or application.state is not expected:
            return False
        with self.atomic():
            self.put_application(
                PendingApplication(
                    application_id=application.application_id,
                    state=new,
                    profile_canonical=application.profile_canonical,
                    profile_content_hash=application.profile_content_hash,
                    rule_results_canonical=application.rule_results_canonical,
                    rule_results_content_hash=application.rule_results_content_hash,
                    rulebook_version=application.rulebook_version,
                    engine_version=application.engine_version,
                )
            )
        return True

    def claim_for_commit(self, recommendation_id: str) -> CommitClaimResult:
        if self._recommendations.get(recommendation_id) is None:
            return CommitClaimResult.NOT_FOUND
        won = self._swap_state(recommendation_id, CaseState.DRAFTED, CaseState.COMMITTING)
        return CommitClaimResult.WON if won else CommitClaimResult.LOST

    def finalize_commit(self, recommendation_id: str) -> None:
        self._swap_state(recommendation_id, CaseState.COMMITTING, CaseState.COMMITTED)

    def release_claim(self, recommendation_id: str) -> None:
        self._swap_state(recommendation_id, CaseState.COMMITTING, CaseState.DRAFTED)


class FaultInjected(RuntimeError):
    """Injected mid-transaction fault — drives EAGER-1's no-partial-row assertion."""


# --- the injected seams (offline doubles — no key, no network, no live LLM) ----------------

class RecordingSeams:
    """Records every call so TRIGGER-1 and ROUTE-1 can assert on real arguments."""

    def __init__(
        self,
        report: Optional[RuleResultReport] = None,
        memo: Optional[DecisionMemo] = None,
        outlier: object = None,
    ) -> None:
        self._report = report if report is not None else make_report()
        self._memo = memo
        self._outlier = outlier
        self.calls: list[str] = []
        self.route_args: list[tuple] = []
        self.thinking_modes: list[object] = []

    def profile(self, raw: object) -> ApplicantProfile:
        self.calls.append("profile")
        return make_profile()

    def evaluate(self, profile: object) -> RuleResultReport:
        self.calls.append("evaluate")
        return self._report

    def score_outlier(self, profile: object):
        self.calls.append("score_outlier")
        return self._outlier

    def draft_memo(self, profile, report, thinking_mode):
        self.calls.append("draft_memo")
        self.route_args.append((report, self._outlier))
        self.thinking_modes.append(thinking_mode)
        return self._memo


# --- the FIVE named families ---------------------------------------------------------------

def clean_case() -> tuple[str, object]:
    """The baseline case that advances cleanly to ``evaluated``."""
    return APPLICATION_ID, {"raw": "application-payload"}


# --- register #19: direct row builders for the CLAIM-1 family -------------------------------
#
# ⚑ These build a case IN A GIVEN STATE directly, rather than driving the pipeline to reach it.
# CLAIM-1 must exercise states the pipeline cannot produce on demand (``committing``,
# ``committed``), and driving the pipeline would couple the claim tests to drafting behaviour
# they are not testing. No RNG, no wall-clock — every value fixed.


def make_application(
    application_id: str = APPLICATION_ID, state: CaseState = CaseState.DRAFTED
) -> PendingApplication:
    return PendingApplication(
        application_id=application_id,
        state=state,
        profile_canonical=b"{}",
        profile_content_hash="profile-hash-1",
        rule_results_canonical=b"{}",
        rule_results_content_hash="report-hash-1",
        rulebook_version="rb-test-v1",
        engine_version="engine-test-v1",
    )


def make_recommendation(
    recommendation_id: str = RECOMMENDATION_ID, application_id: str = APPLICATION_ID
) -> PendingRecommendation:
    return PendingRecommendation(
        recommendation_id=recommendation_id,
        application_id=application_id,
        memo_canonical=b"{}",
        memo_hash="memo-hash-1",
        model_version="model-test-v1",
        engine_version="engine-test-v1",
        rulebook_version="rb-test-v1",
    )


def illegal_transition_cases() -> tuple[tuple[CaseState, CaseState], ...]:
    """⚑ STATE-2's landmark rejections, returned as ONE collection — UNSPLITTABLE.

    Skip-evaluation · a backward move · a terminal exit. Returned together so the set cannot
    be trimmed one case at a time.
    """
    return (
        (CaseState.SUBMITTED, CaseState.DRAFTED),     # skips evaluation
        (CaseState.SUBMITTED, CaseState.COMMITTED),   # skips everything
        (CaseState.DRAFTED, CaseState.EVALUATED),     # backward
        (CaseState.EVALUATED, CaseState.PROFILED),    # backward
        (CaseState.COMMITTED, CaseState.DRAFTED),     # out of a terminal state
        (CaseState.FAILED, CaseState.DRAFTED),        # out of a terminal state
    )


def drafting_success_double() -> RecordingSeams:
    """Seams whose ``draft_memo`` returns a real ``DecisionMemo``."""
    return RecordingSeams(memo=make_memo())


def drafting_failure_double() -> RecordingSeams:
    """⚑ ITS OWN FAMILY — seams whose ``draft_memo`` returns ``None``.

    Kept separate so FAILED-1 and COMMITBOUND-1(c) can never be weakened by an edit made for
    the success path.
    """
    return RecordingSeams(memo=None)


def borderline_refer_case() -> RecordingSeams:
    """A ``REFER`` report — the frozen router MUST return ``EXTENDED`` for it."""
    return RecordingSeams(report=make_report(Recommendation.REFER), memo=make_memo())


def recommendation_id_factory(application_id: str) -> str:
    """Deterministic id — no RNG, no wall-clock."""
    return f"rec-{application_id}"
