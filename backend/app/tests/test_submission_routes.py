"""R10 / R11 — the application-submission surface (WIRE1-Fold-6, register #2).

⚑ **AUTHORIZATION IS TESTED FIRST, DELIBERATELY.** Q10 makes ``underwriter``-only part of each
route's *definition* rather than later hardening: R10 creates a case and R11 spends compute on an
LLM-bearing draft, and R5 already establishes that a write gets its own role gate. Testing auth
after the happy path would let a spend-capable trigger ship reachable-by-anyone for one commit.

⚑ **The three failure modes are three distinct codes, all pre-existing in WIRE-1 §4** — 401
``unauthenticated``, 403 ``forbidden``, 400 ``invalid_request``. Fold-6 invented none of them.
"""
from __future__ import annotations

import pytest

from backend.app.dependencies import (
    case_seams,
    get_case_pipeline,
    get_case_store,
    get_intake_pipeline,
)
from backend.app.offline_memo_double import (
    OFFLINE_MODEL_VERSION,
    OfflineMemoLLMClient,
    first_cited_rule_id,
)
from backend.app.tests.conftest import ADMIN, AUDITOR, UNDERWRITER
from backend.case_lifecycle.pipeline import DraftOutcome
from backend.case_lifecycle.states import CaseState
from backend.intake.pipeline import PipelineResult
from backend.intake.schema import ReasonCategory, RejectedIntake

#: A structurally complete application — every value the frozen ``IntakeGate`` requires.
#: ⛔ Money is a DECIMAL STRING, never a JSON float: intake's BR-TYP-1 refuses float outright.
VALID_FORM_FIELDS = {
    "date_of_birth": "1986-03-14",
    "as_of_date": "2026-01-01",
    "verifiable_income_annual": "1200000",
    "requested_cover_amount": "4000000",
    "full_name": "Ada Byron",
    "gender": "female",
    "city": "Metropolis",
}


def submit(client, form_fields=None, documents=None, headers=UNDERWRITER):
    body = {"form_fields": VALID_FORM_FIELDS if form_fields is None else form_fields}
    if documents is not None:
        body["documents"] = documents
    return client.post("/applications", json=body, headers=headers)


class TestR10Authorization:
    """A1/A2 — R10 is ``underwriter`` only (WIRE-1 §3, Q10(a))."""

    def test_r10_rejects_an_auditor_with_403(self, submission_client):
        # ⚑ SEC-4 treats the auditor's read-only-ness as a security property, not a convention.
        response = submission_client.post("/applications", json={"form_fields": {}}, headers=AUDITOR)
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "forbidden"

    def test_r10_rejects_an_unauthenticated_caller_with_401(self, submission_client):
        response = submission_client.post("/applications", json={"form_fields": {}})
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "unauthenticated"


class TestR11Authorization:
    """A3/A4 — R11 is ``underwriter`` only. The spend-capable trigger, so this is the load-bearing
    half: an auditor able to trigger drafting would quietly break SEC-4's read-only property."""

    def test_r11_rejects_an_auditor_with_403(self, submission_client):
        response = submission_client.post("/applications/APP-2/draft", headers=AUDITOR)
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "forbidden"

    def test_r11_rejects_an_unauthenticated_caller_with_401(self, submission_client):
        response = submission_client.post("/applications/APP-2/draft")
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "unauthenticated"

    def test_r11_rejects_an_admin_with_403(self, submission_client):
        """⚑ NOT in the plan's step list — added because Q10(c) (`underwriter` OR `admin`) was a
        REAL option that was considered and rejected. Without this, nothing would catch a later
        widening to admin, and the rejection of (c) would be a comment rather than a guarantee."""
        response = submission_client.post("/applications/APP-2/draft", headers=ADMIN)
        assert response.status_code == 403


class TestTheUnderwriterIsNotRejected:
    """⚑ NON-VACUITY for the four assertions above. Without this, deleting both routes entirely
    would leave A1-A4 passing on 405s — the guard must reject the auditor *and admit the
    underwriter*, or it is not testing authorization at all."""

    def test_an_underwriter_is_not_refused_by_the_role_gate(self, submission_client):
        response = submission_client.post(
            "/applications", json={"form_fields": {}}, headers=UNDERWRITER
        )
        assert response.status_code not in (401, 403, 405), response.status_code


class TestR10AcceptsAStructuredApplication:
    """B1-B3 — the happy path. ⚑ This is the FIRST time U1 ``intake`` runs in a reachable path:
    the sanitizer, the PII guard and the validation gate all execute here, and the
    ``application_id`` in the response was assigned by the frozen ``IntakeGate``, not chosen by
    the caller."""

    def test_r10_returns_the_created_application_id(self, submission_client):
        response = submit(submission_client)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["application_id"], body
        # ⚑ System-assigned on gate pass — the caller never supplied one (WIRE-1 §5, Fold-6).
        assert "application_id" not in VALID_FORM_FIELDS
        assert body["status"] == "pending"

    def test_the_persisted_case_is_at_state_evaluated(self, submission_client, case_store):
        application_id = submit(submission_client).json()["application_id"]
        case = case_store.get_application(application_id)
        assert case is not None, "R10 must persist the case"
        # ⚑ Q3(a): submission is LLM-free and stops at `evaluated`. Drafting is R11's job.
        assert case.state is CaseState.EVALUATED

    def test_r10_accepts_an_explicitly_empty_documents_list(self, submission_client):
        """Q2's follow-up, asserted rather than assumed: the seam's shape is already correct for
        when documents land, so an explicit ``[]`` must be accepted, not merely tolerated."""
        assert submit(submission_client, documents=[]).status_code == 200


class TestR10RejectsAnInvalidApplication:
    """C1-C3 — Q8(a): rejection is handled in the ROUTE, before ``submit()`` is ever called."""

    def test_a_rejected_intake_returns_400_invalid_request(self, submission_client):
        response = submit(submission_client, form_fields={"full_name": "Ada Byron"})
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "invalid_request"

    def test_the_error_detail_carries_the_rejected_intake_fields(self, submission_client):
        """⚑ THE REASON Q8(a) WAS WORTH CHOOSING — a form can render per-field errors from this.
        WIRE-1 §4 has documented ``detail`` as *"optional (e.g. per-field validation errors)"*
        since the 2026-07-08 pin, so this invents no contract surface."""
        detail = submit(
            submission_client, form_fields={"full_name": "Ada Byron"}
        ).json()["error"]["detail"]
        assert detail["reason_category"] == "missing_required"
        assert "verifiable_income_annual" in detail["missing_items"]
        offending = {error["field"] for error in detail["field_errors"]}
        assert "verifiable_income_annual" in offending and "date_of_birth" in offending

    def test_a_rejected_intake_creates_no_row(self, submission_client, case_store):
        """⚑ The property that keeps ``submit()``'s contract intact: ``RejectedIntake`` NEVER
        enters the pipeline, so no half-created case exists to reconcile later."""
        before = set(case_store.list_application_ids())
        submit(submission_client, form_fields={"full_name": "Ada Byron"})
        assert set(case_store.list_application_ids()) == before

    def test_a_float_money_value_is_rejected_not_coerced(self, submission_client):
        """⚑ NOT in the plan's step list. BR-TYP-1 (*"float not permitted; use a decimal
        string"*) is the one intake rule a JSON client can trip by accident, and WIRE-1 §5's
        decimal-string requirement would be an unenforced comment without this."""
        response = submit(
            submission_client,
            form_fields={**VALID_FORM_FIELDS, "verifiable_income_annual": 1200000.50},
        )
        assert response.status_code == 400
        assert response.json()["error"]["detail"]["reason_category"] == "malformed"


class _SpyIntake:
    """Records every ``process`` call, then returns a rejection so the request terminates.

    ⚑ It returns a ``RejectedIntake`` rather than raising, deliberately: an exception would make
    the two tests below indistinguishable from a crash, and the non-vacuity test needs an
    AUTHORIZED call to complete so it can observe that the seam is genuinely consulted.
    """

    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def process(self, form_fields, documents):
        self.calls.append((form_fields, documents))
        return PipelineResult(outcome=RejectedIntake(reason_category=ReasonCategory.MALFORMED))


class TestTheForbiddenPathNeverReachesIntake:
    """C4 — ⚑ STRUCTURAL, NOT TIMING-BASED.

    FastAPI resolves ``Depends(...)`` before the handler body runs, so ``require_underwriter``
    fires before any intake code executes. The spy records **zero** calls — which is a statement
    about *whether the body ran*, not about *how fast* anything was. This is what stops the route
    regressing into "validate first, authorize later", a shape that would leak rejection detail
    (field names, missing items) to a caller with no right to it.
    """

    def test_a_403_records_zero_intake_calls(self, submission_client):
        spy = _SpyIntake()
        submission_client.app.dependency_overrides[get_intake_pipeline] = lambda: spy

        response = submission_client.post(
            "/applications", json={"form_fields": VALID_FORM_FIELDS}, headers=AUDITOR
        )

        assert response.status_code == 403
        assert spy.calls == [], "intake ran for a caller the role gate should have stopped"

    def test_the_spy_would_have_recorded_an_authorized_call(self, submission_client):
        """⚑ NON-VACUITY for the spy. A spy wired to a dependency the route never asks for would
        record zero calls no matter what, and the assertion above would be worthless."""
        spy = _SpyIntake()
        submission_client.app.dependency_overrides[get_intake_pipeline] = lambda: spy

        submission_client.post(
            "/applications", json={"form_fields": VALID_FORM_FIELDS}, headers=UNDERWRITER
        )

        assert len(spy.calls) == 1, "the route must actually consult the injected intake seam"


class TestR11TriggersDrafting:
    """D1-D3.

    ⚠️ **THE DRAFTABLE CASE IS CREATED THROUGH R10, NOT TAKEN FROM THE FIXTURE — and the
    reason is a real finding, recorded rather than worked around.** The ``case_store`` fixture's
    ``APP-2`` carries a report built by ``factories.make_report()``, whose rule id is ``DTI-1``
    — **a value that does not exist in the rulebook** (the real DTI rule is ``DTI-CEIL-1``).
    U4's ``CitationValidator`` requires every cited id to be in the report **and** in the
    rulebook, so drafting that case fails citation validation, retries, and produces no memo.

    ⚑ Submitting through R10 first is not a workaround for that — it is the more faithful
    test: every case R11 will ever see in production came from R10 and therefore carries REAL
    rule ids from the real ``RulesEngine``. The factory report was only ever built to be READ
    back by R2/R3/R4, which never validate citations.
    """

    def test_r11_drafts_a_pending_case_and_it_becomes_ready(self, submission_client, case_store):
        application_id = submit(submission_client).json()["application_id"]
        response = submission_client.post(
            f"/applications/{application_id}/draft", headers=UNDERWRITER
        )
        assert response.status_code == 200, response.text
        assert response.json() == {
            "application_id": application_id, "status": "ready", "outcome": "drafted",
        }
        assert case_store.get_application(application_id).state is CaseState.DRAFTED
        assert case_store.recommendation_for_application(application_id) is not None

    def test_r11_on_an_already_drafted_case_returns_the_skip_outcome(self, submission_client):
        """⚑ INHERITS register #27's ``DraftOutcome.skipped``. A repeat click is idempotent, not
        a failure — without the discriminator this would report an error on every re-trigger,
        which is what trains an operator to ignore FAILED lines."""
        response = submission_client.post("/applications/APP-1/draft", headers=UNDERWRITER)
        assert response.status_code == 200
        assert response.json()["outcome"] == "skipped"

    def test_a_second_trigger_creates_no_second_recommendation(self, submission_client, case_store):
        """⚑ NOT in the plan's step list. Register #27 was *unbounded accumulation* of
        ``pending_recommendation`` rows, and R11 is a new caller of exactly the path that
        accumulated. The skip STATUS could be right while a row was still written; only counting
        rows proves it is not."""
        application_id = submit(submission_client).json()["application_id"]
        submission_client.post(f"/applications/{application_id}/draft", headers=UNDERWRITER)
        first = case_store.recommendation_for_application(application_id).recommendation_id
        submission_client.post(f"/applications/{application_id}/draft", headers=UNDERWRITER)
        assert case_store.recommendation_for_application(application_id).recommendation_id == first
        assert len([r for r in case_store._recommendations.values()
                    if r.application_id == application_id]) == 1

    def test_r11_on_an_unknown_application_is_404(self, submission_client):
        response = submission_client.post("/applications/APP-NOPE/draft", headers=UNDERWRITER)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    def test_the_drafted_memo_is_stamped_as_an_offline_double(self, submission_client, case_store):
        """⛔ NOT in the plan's step list, and the most important thing in this file to keep
        honest. Q5(a) closes Q11-A's gaps (i) and (ii) — **NOT (iii)**. The memo prose stays
        SYNTHETIC and register #18 stays open, so the stamp that says so must be asserted, not
        trusted. If this ever passes without the stamp, the system is presenting placeholder
        prose as a real recommendation."""
        application_id = submit(submission_client).json()["application_id"]
        submission_client.post(f"/applications/{application_id}/draft", headers=UNDERWRITER)
        recommendation = case_store.recommendation_for_application(application_id)
        assert recommendation.model_version == OFFLINE_MODEL_VERSION


class _WriteRecordingStore:
    """Wraps a real ``InMemoryCaseStore``, recording every state-writing call it receives."""

    def __init__(self, inner) -> None:
        self._inner = inner
        self.writes: list[str] = []

    def __getattr__(self, name):
        attribute = getattr(self._inner, name)
        if name in ("put_application", "put_recommendation"):
            def recording(*args, **kwargs):
                self.writes.append(name)
                return attribute(*args, **kwargs)
            return recording
        return attribute


class TestR4RemainsSideEffectFree:
    """E1 — ⚑ **BEHAVIOURAL, and deliberately NOT a pipeline spy.**

    A spy on ``get_case_pipeline`` would be VACUOUS here: R4 does not depend on that provider at
    all, so it would record zero calls even if R4 were rewritten to draft by some other means.
    This records writes at the **store** instead — the one boundary every drafting path must
    cross, whatever object it travels through — so it catches a write reaching domain state by
    ANY means, including a module-level helper.

    ⚑ **This is a DIFFERENT claim from the one G3's structural guard makes.** G3 asserts that no
    GET-serving MODULE references the pipeline; this asserts that exercising R4 CHANGES NOTHING.
    A structural guard could hold while behaviour drifted (a shared helper in a non-route
    module); a behavioural one could hold while the guard rotted. The invariant needs both.
    """

    def _recording_store(self, submission_client, case_store):
        recording = _WriteRecordingStore(case_store)
        submission_client.app.dependency_overrides[get_case_store] = lambda: recording
        return recording

    def test_reading_r4_triggers_no_pipeline_write(self, submission_client, case_store):
        recording = self._recording_store(submission_client, case_store)

        for application_id in ("APP-1", "APP-2"):
            for _ in range(3):
                assert submission_client.get(
                    f"/applications/{application_id}/memo", headers=UNDERWRITER
                ).status_code == 200

        assert recording.writes == [], recording.writes
        # ⚑ ...and the pending case is STILL pending: reading it did not draft it.
        assert case_store.get_application("APP-2").state is CaseState.EVALUATED

    def test_the_recorder_does_catch_a_real_write(self, submission_client, case_store):
        """⚑ NON-VACUITY for the recorder. If it recorded nothing under any circumstances the
        assertion above would be worthless — so R11 must move its needle."""
        recording = self._recording_store(submission_client, case_store)
        application_id = submit(submission_client).json()["application_id"]
        submission_client.post(f"/applications/{application_id}/draft", headers=UNDERWRITER)
        assert "put_application" in recording.writes
        assert "put_recommendation" in recording.writes


class TestTheFullJourney:
    """E2 — submission to a drafted memo, over HTTP, through the routes only."""

    def test_r10_then_r4_pending_then_r11_then_r4_ready(self, submission_client):
        application_id = submit(submission_client).json()["application_id"]

        pending = submission_client.get(
            f"/applications/{application_id}/memo", headers=UNDERWRITER
        ).json()
        assert pending["status"] == "pending" and pending["memo"] is None

        assert submission_client.post(
            f"/applications/{application_id}/draft", headers=UNDERWRITER
        ).json()["outcome"] == "drafted"

        ready = submission_client.get(
            f"/applications/{application_id}/memo", headers=UNDERWRITER
        ).json()
        assert ready["status"] == "ready"
        assert ready["memo"]["narrative_prose"]
        assert ready["recommendation_id"]
        # ⚑ SUPERSEDED BY STAGE 3, exactly as this assertion was written to be. The stage-2 text
        # is preserved verbatim: *"Stage 3's territory: no model is composed yet, so a real
        # submission still carries `outlier: null` — the honest current state, asserted so stage
        # 3 has a baseline to move."* `assert ready["outlier"] is None` was TRUE for the whole of
        # stage 2 and is FALSE now, which is the point: the fourth `lru_cache` provider landed and
        # a user-submitted case is scored against the committed corpus like any other.
        assert ready["outlier"] is not None
        assert ready["outlier"]["provenance"]["corpus_version"]

    def test_the_submitted_case_appears_in_the_r2_queue(self, submission_client):
        """⚑ NOT in the plan's step list. Q11-A's gap (ii) is a CLICKABLE path, and the queue is
        where a submitted case has to appear for stage 4's frontend unit to have anything to
        show. Cheap to assert now; expensive to discover in stage 4."""
        application_id = submit(submission_client).json()["application_id"]
        queue = submission_client.get("/applications", headers=UNDERWRITER).json()
        assert application_id in {item["application_id"] for item in queue["items"]}


class TestTheSubmissionCompositionIsReal:
    """⚑ NOT in the plan's step list — and its absence was a gap, not a simplification.

    Every test above reaches the providers through ``TestClient``, which means a provider could
    be subtly wrong (a stale rulebook path, an uncached seam rebuilt per request, a parse worker
    that silently accepts documents) and still pass, because the failure would surface only as a
    slow or wrong response somewhere else. These call the real providers **directly**.
    """

    def test_the_seams_are_built_once_per_process(self):
        """⚑ Pins the ``lru_cache``, and the property it buys: the rulebook is read from disk and
        the LangGraph orchestrator is constructed ONCE, not on every submission. This is the same
        laziness Fold C found load-bearing for the outlier model — recorded here for the seams
        because the cost has the same shape."""
        assert case_seams() is case_seams()

    def test_the_intake_pipeline_is_the_real_frozen_unit(self):
        """⚑ The gate, sanitizer and PII guard are U1's own — not re-implemented here. A garbage
        input must come back as a ``RejectedIntake``, which is intake's SEC-2 total-function
        guarantee, exercised through the composition root's own provider."""
        result = get_intake_pipeline().process({"nonsense": True}, documents=[])
        assert isinstance(result.outcome, RejectedIntake)

    def test_the_case_pipeline_is_built_over_the_injected_store(self):
        from backend.app.tests.factories import InMemoryCaseStore

        store = InMemoryCaseStore()
        pipeline = get_case_pipeline(store=store)
        # ⚑ Reading through the pipeline reaches the store it was handed, not a global.
        assert pipeline.read("APP-NOPE") is None

    def test_the_parse_worker_is_the_REAL_sandboxed_one(self):
        """⚑ SUPERSEDED 2026-08-03 (WIRE1-Fold-7). The Fold-6 assertion is preserved verbatim:

            it('the parse worker refuses rather than exists')
            with pytest.raises(NotImplementedError, match="structured fields only"):
                _NoDocumentParseWorker().parse("salary_slip", "/tmp/whatever.pdf")

        ⛔ **Its subject no longer exists, and that is the point.** Under Fold-6 the composition
        root injected a worker that REFUSED, so structured-only was mechanical rather than
        documentary. Fold-7 is the named follow-on that lands documents, so the refusing stub is
        replaced by the real sandboxed worker — fresh subprocess per document, 5 s wall clock,
        POSIX RLIMIT_CPU/RLIMIT_AS, data-only IPC.

        What this still pins is the half that matters: the worker is the **real** one, not a
        permissive double that would let an unsandboxed parse into the request path.
        """
        from backend.intake.parser import SubprocessParseWorker

        worker = get_intake_pipeline()._parse
        assert isinstance(worker, SubprocessParseWorker)
        assert worker.DEFAULT_MEM_BYTES == 256 * 1024 * 1024
        assert worker.DEFAULT_TIMEOUT_S == 5.0

    def test_documents_in_a_JSON_body_are_still_refused(self, submission_client):
        """⚑ Fold-7 did NOT make the JSON encoding document-bearing. Documents travel as
        `multipart/form-data`; a `documents` array in a JSON body is still a 400, because it
        would otherwise look like it worked while carrying nothing but metadata."""
        response = submit(
            submission_client, documents=[{"doc_type": "salary_slip", "source_path": None}]
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "invalid_request"


def _prompt_shaped_like_the_real_one(*, rules: str, recommendation: str = "APPROVE") -> str:
    """A prompt carrying the two section markers ``PromptBuilder.build()`` actually emits.

    ⚠️ **These fixtures changed at the register #35 fix (step 6.3), and the reason matters.**
    ``first_cited_rule_id`` used to search the WHOLE prompt, so a bare string like
    ``"... rule DTI-CEIL-1 evaluated ..."`` exercised it fine. ⛔ **That unbounded search WAS #35** —
    it matched ``RECOMMENDATION (read-only): DECLINE-RECOMMEND`` above the report and cited the
    recommendation itself. Extraction is now bounded between the two markers, so a prompt without
    them is no longer valid input and correctly yields ``""``. ⚑ **The tests' intent is unchanged
    and their assertions are not weakened** — only the fixture is now shaped like what the single
    production caller (`orchestrator._draft_node` → `PromptBuilder.build`) really hands over.
    """
    return (
        f"RECOMMENDATION (read-only): {recommendation}\n"
        "CONFIDENCE (read-only): High\n"
        "\n"
        "RULE REPORT (the only citable rules):\n"
        f"{rules}"
        "\n"
        "APPLICANT FACTS (non-demographic):\n"
        "- age_years: 41\n"
    )


class TestTheOfflineDoubleAnnouncesItself:
    """⛔ Register #18's gap (iii) stays OPEN. These pin the two properties that keep that honest."""

    def test_it_discovers_the_cited_rule_id_rather_than_hardcoding_one(self):
        """⚑ The defect this replaced cited a hardcoded ``DTI-001`` that does not exist in this
        build, so every draft failed citation validation and every seeded case landed in
        ``FAILED`` — invisibly. Discovery is what stops that recurring."""
        found = _prompt_shaped_like_the_real_one(rules="- DTI-CEIL-1 [PASS] within ceiling\n")
        assert first_cited_rule_id(found) == "DTI-CEIL-1"

        none_listed = _prompt_shaped_like_the_real_one(rules="")
        assert first_cited_rule_id(none_listed) == ""

    def test_it_does_not_cite_the_RECOMMENDATION_itself(self):
        """⛔ **Register #35** ``OFFLINE-DOUBLE-CITES-THE-RECOMMENDATION``, pinned at the caller
        this class covers. ``Recommendation.DECLINE_RECOMMEND.value`` is ``"DECLINE-RECOMMEND"``,
        which the rule-id regex matches — and it sits ABOVE the rule report. ⚑ Bounding the search
        between the two markers is what keeps it out; ⚠️ ``APPROVE``/``REFER`` never exposed this
        because their values contain no hyphen."""
        prompt = _prompt_shaped_like_the_real_one(
            rules="- DTI-CEIL-1 [FAIL] ratio above ceiling\n", recommendation="DECLINE-RECOMMEND"
        )

        assert first_cited_rule_id(prompt) == "DTI-CEIL-1"

    def test_the_generated_memo_announces_itself_as_a_placeholder(self):
        xml = OfflineMemoLLMClient().generate(
            model="ignored",
            prompt=_prompt_shaped_like_the_real_one(rules="- AGE-BAND-1 [PASS] within band\n"),
            temperature=0.0,
        )
        assert "NOT BY A LANGUAGE MODEL" in xml
        assert "<rule_id>AGE-BAND-1</rule_id>" in xml

    def test_the_stamp_matches_the_seed_scripts_stamp_by_value(self):
        """⚑ The two doubles are separate implementations (disclosed in the module docstring).
        An operator reading a database row must not have to know which path wrote it to know the
        memo is synthetic, so the STAMP must not drift even though the code may."""
        import backend.scripts.seed_demo_cases as seed

        assert OFFLINE_MODEL_VERSION == seed.OFFLINE_MODEL_VERSION


class _FailingDraftPipeline:
    """A pipeline whose ``draft()`` runs and comes back with no memo — a GENUINE failure, which
    ``DraftOutcome`` distinguishes from a benign skip by ``skipped=False``."""

    def __init__(self, inner) -> None:
        self._inner = inner

    def read(self, application_id):
        return self._inner.read(application_id)

    def draft(self, application_id):
        return DraftOutcome(failure_reason="drafting produced no memo")


class TestAGenuineDraftingFailureIsNotASkip:
    """⛔ NOT in the plan's step list. This pins **the boundary decision WIRE1-Fold-6 made about
    register #14**, which would otherwise be prose in a contract and nothing else.

    ``DraftOutcome`` has THREE outcomes; the wire has TWO. A real failure moves the case to
    ``failed``, and ``failed`` has **no wire representation** — ``case_to_memo_view_state`` maps
    it to ``"pending"`` (register #14, open). Fold-6 declined to widen R4's ``ready | pending``
    discriminator on #14's behalf, so R11 maps a genuine failure to the existing **500** and
    declares only the two outcomes it can honestly express.

    ⚑ Without this test the distinction is untested and the 500 branch unreachable in the suite —
    so a later change collapsing "failed" into ``outcome: "skipped"`` would pass silently. That
    would be the worst possible outcome of the three: it would tell an operator that nothing
    needed doing, about a case that had just failed.
    """

    def test_a_failed_draft_is_a_500_not_a_skip(self, submission_client, case_store):
        application_id = submit(submission_client).json()["application_id"]
        submission_client.app.dependency_overrides[get_case_pipeline] = (
            lambda: _FailingDraftPipeline(get_case_pipeline(store=case_store))
        )

        response = submission_client.post(
            f"/applications/{application_id}/draft", headers=UNDERWRITER
        )

        assert response.status_code == 500
        assert response.json()["error"]["code"] == "internal_error"
        # ⛔ and emphatically NOT reported as a benign skip
        assert "outcome" not in response.json()
