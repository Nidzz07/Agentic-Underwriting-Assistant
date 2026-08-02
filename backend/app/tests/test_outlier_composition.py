"""The fitted outlier model as a composition concern (WIRE1-Fold-6 stage 3, Q4(a)).

⚑ **WHY THIS IS A COMPOSITION PROBLEM AT ALL.** Fitting the model costs **~2.6 s**. That is fine
once per script run and unacceptable per HTTP request, so something must hold a fitted model for
the process lifetime — a concern ``backend/app/`` has never had. Q4(a) chose the same lazy
``lru_cache`` idiom the three engines already use, making this the **fourth** provider of
identical shape rather than a new pattern.

⛔ **THE LAZINESS IS LOAD-BEARING, NOT INCIDENTAL** (ambiguity-check Fold C). Because the fit
happens on FIRST USE rather than at import or app construction, ``create_app()`` still costs
nothing — and the composition root is constructed four times in ``conftest.py`` alone. Q4(b)'s
eager alternative would turn that into ~2.6 s x every ``create_app()``. ``test_create_app_does_
not_fit_the_model`` exists so that cannot regress silently.

⚑ **COST DISCIPLINE IN THIS FILE**: exactly ONE real fit is paid, by ``test_the_fitted_model_is_
cached``, and every later test reuses the cached instance. The two tests that must NOT fit
(laziness, missing corpus) are written so they never trigger one.
"""
from __future__ import annotations

import pytest

from backend.app import dependencies as deps
from backend.app import outlier_composition as oc
from backend.app.main import create_app
from backend.app.outlier_canonical import OUTLIER_QUANT_DECIMAL_PLACES, QuantizedOutlierResult
from backend.app.tests.conftest import UNDERWRITER
from backend.app.tests.test_submission_routes import submit
from backend.case_lifecycle.pipeline import CasePipeline
from backend.common.canon_ser import canon_deserialize


class TestTheModelIsFittedOncePerProcess:
    """G1/G2 — the two halves of Q4(a): cached, and lazily so."""

    def test_the_fitted_model_is_cached(self):
        """G1. ⚑ Pins the property that keeps a ~2.6 s fit OFF the per-request path. Without the
        cache every submission that reaches drafting would refit the whole corpus."""
        assert deps.outlier_model() is deps.outlier_model()

    def test_create_app_does_not_fit_the_model(self, monkeypatch):
        """G2. ⛔ **PINS THE LAZINESS**, which Fold C found load-bearing.

        ⚑ Asserted by COUNTING FITS rather than by timing: a timing assertion would be flaky and
        would not say *why* it was slow. The counter also costs nothing — it never fits, so this
        test cannot itself become the thing it is guarding against.
        """
        fits = []
        monkeypatch.setattr(
            oc, "build_outlier_model", lambda *a, **k: fits.append(1) or object()
        )
        monkeypatch.setattr(deps, "outlier_model", deps.outlier_model.__wrapped__)

        create_app()

        assert fits == [], "create_app() must construct nothing and fit nothing"


class TestAMissingCorpusFailsLoudly:
    """G3 — Q6(a) as answered, Q6(b) as rejected."""

    def test_a_missing_corpus_fails_loudly_and_by_name(self, tmp_path):
        """⚑ **A silent ``outlier=None`` fallback was considered and REFUSED.** It would
        reproduce, invisibly, the exact defect the outlier pass existed to fix — and a null is
        indistinguishable from the legitimate Phase-1 behaviour, so nobody would notice. A named
        failure cannot be missed.

        ⛔ This is also the assertion that makes ``corpus/profiles.json`` a **hard runtime
        dependency of the deployed backend**, not a nice-to-have. See
        ``outlier_composition.CORPUS_ON_RENDER``.
        """
        with pytest.raises(FileNotFoundError) as excinfo:
            oc.build_outlier_model(tmp_path / "no-such-corpus")

        message = str(excinfo.value)
        assert "profiles.json" in message, f"the missing file must be named: {message!r}"
        assert "no-such-corpus" in message, f"the searched path must be named: {message!r}"

    def test_the_deployment_dependency_is_declared_in_code_not_only_in_prose(self):
        """⚑ NOT in the plan's step list. Q4's forced follow-up said the corpus question *"stops
        being carried"* here — but a carried note that moves from one markdown file to another is
        still a carried note. This asserts the declaration exists as a NAMED, GREPPABLE symbol in
        the production tree, so the deployment pass finds it by searching the code rather than by
        remembering a plan.
        """
        assert "corpus/profiles.json" in oc.CORPUS_ON_RENDER
        assert "render" in oc.CORPUS_ON_RENDER.lower()
        assert oc.CORPUS_DIR.name == "corpus"


class TestADraftedCaseCarriesRealOutlierData:
    """G4/G5 — the model reaches the wire through R11, not through a script.

    ⚑ **This is the first time an outlier score is produced for an application the system did not
    invent.** The outlier pass computed real scores, but only for ``_demo_profile()`` cases the
    seed script hardcoded. Here the profile came through U1 ``intake`` over HTTP.
    """

    def test_a_drafted_case_persists_a_real_quantized_outlier_result(
        self, submission_client, case_store
    ):
        """G4. ⛔ **QUANTIZED, and that is barrier #5, not a detail.**
        ``CanonSerAdapter.canonical_bytes`` refuses IEEE float (CON-DET-1) and every numeric
        field of ``OutlierResult`` is a float — so if the seam returned the raw result,
        ``draft()`` would RAISE before writing a row. This asserts the persisted bytes exist AND
        that what round-trips is the Decimal projection."""
        application_id = submit(submission_client).json()["application_id"]
        submission_client.post(f"/applications/{application_id}/draft", headers=UNDERWRITER)

        recommendation = case_store.recommendation_for_application(application_id)
        assert recommendation.outlier_canonical is not None, "no outlier bytes were persisted"

        # ⚑ The read path is ``bytes -> canon_deserialize -> QuantizedOutlierResult`` — the
        # same two steps ``projections.py`` uses. Deserializing to the QUANTIZED shape (rather
        # than straight to ``OutlierResult``) is the point: it proves Decimals were what got
        # written, which is the only reason CANON-SER accepted them at all.
        stored = canon_deserialize(recommendation.outlier_canonical)
        quantized = QuantizedOutlierResult.model_validate(stored)
        exponent = -quantized.outlier_score.as_tuple().exponent
        assert exponent <= OUTLIER_QUANT_DECIMAL_PLACES, (
            f"score carries {exponent} decimals, beyond the named quantization precision"
        )

    def test_r4_serves_the_outlier_for_a_user_submitted_case(self, submission_client):
        """G5. EXPLAIN-1 on the wire: every flag carries its own explanation, and the provenance
        triple is what makes a score replayable rather than merely reported."""
        application_id = submit(submission_client).json()["application_id"]
        submission_client.post(f"/applications/{application_id}/draft", headers=UNDERWRITER)

        outlier = submission_client.get(
            f"/applications/{application_id}/memo", headers=UNDERWRITER
        ).json()["outlier"]

        assert outlier is not None
        assert isinstance(outlier["outlier_score"], float)
        assert isinstance(outlier["is_outlier"], bool)
        for flag in outlier["flagged_features"]:
            assert flag["feature"] and flag["direction"] in ("high", "low")
            assert "z_score" in flag and "shap_value" in flag
        provenance = outlier["provenance"]
        assert provenance["corpus_version"] and provenance["outlier_model_version"]
        assert isinstance(provenance["seed"], int)

    def test_the_same_profile_scores_identically_twice(self, submission_client):
        """⚑ NOT in the plan's step list. Acceptance criterion §5.1 is *"identical input ->
        identical output, 100% of the time"*, and this pass puts scoring on a **per-request**
        path for the first time — where a refit per request, or a model rebuilt between calls,
        would break reproducibility invisibly. Two identical submissions must score identically.

        ⚠️ Scoped precisely: this asserts determinism **within one process against one fitted
        model**. It is NOT a claim of cross-version floating-point reproducibility, which
        nothing in this stack promises — see ``outlier_canonical``.
        """
        scores = []
        for _ in range(2):
            application_id = submit(submission_client).json()["application_id"]
            submission_client.post(f"/applications/{application_id}/draft", headers=UNDERWRITER)
            scores.append(submission_client.get(
                f"/applications/{application_id}/memo", headers=UNDERWRITER
            ).json()["outlier"]["outlier_score"])
        assert scores[0] == scores[1], scores


class _UnscoredSeams:
    """The seams as they stood for the whole of stage 2 — everything real except the score."""

    def __init__(self, inner) -> None:
        self._inner = inner

    def profile(self, raw):
        return self._inner.profile(raw)

    def evaluate(self, profile):
        return self._inner.evaluate(profile)

    def score_outlier(self, profile):
        return None

    def draft_memo(self, profile, report, thinking_mode):
        return self._inner.draft_memo(profile, report, thinking_mode)


class TestTheNullOutlierPathSurvives:
    """G6 — ⚑ **the path that must NOT break, and the one most likely to.**

    Every case seeded or drafted before this stage carries ``outlier_canonical = NULL``, and R4
    must keep serving them ``outlier: null`` rather than erroring. WIRE1-Fold-4 binds the field
    nullable precisely so a case without a score is representable; making scoring reachable must
    not quietly make it mandatory.
    """

    def test_a_case_drafted_with_no_model_still_emits_outlier_null(
        self, submission_client, case_store
    ):
        application_id = submit(submission_client).json()["application_id"]
        submission_client.app.dependency_overrides[deps.get_case_pipeline] = (
            lambda: CasePipeline(
                case_store, _UnscoredSeams(deps.case_seams()), deps._recommendation_id_factory
            )
        )

        assert submission_client.post(
            f"/applications/{application_id}/draft", headers=UNDERWRITER
        ).json()["outcome"] == "drafted"

        view = submission_client.get(
            f"/applications/{application_id}/memo", headers=UNDERWRITER
        ).json()
        assert view["status"] == "ready", "an unscored case must still draft to ready"
        assert view["outlier"] is None
        assert case_store.recommendation_for_application(application_id).outlier_canonical is None
