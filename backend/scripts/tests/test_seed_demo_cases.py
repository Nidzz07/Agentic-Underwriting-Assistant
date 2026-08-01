"""tier-U guard for the demo seed script — the test that would have caught BOTH defects.

⚑ **This test IS the fix.** The two defects it pins (`RulebookLoader()` called with no argument;
the offline double citing a rule id `DTI-001` that does not exist in this build) were both
one-token errors in a module that was **untested, uncollected, coverage-invisible and had never
been run to completion**. Neither is subtle — either would have been caught by a single
execution. The absence of *any* test that constructs `_SeedSeams` and asserts a memo comes out
was the actual gap; the one-line fixes are incidental to it.

**Scope — stated honestly.** These are **tier-U** assertions over the in-memory chain, using
U24's own `InMemoryCaseStore` (the cross-unit test-fixture import convention already used by
`test_run_migrations_integration.py` and `app/tests/test_llm_client.py`). They prove the demo
path is **constructible and reaches `drafted`/`ready` offline**. They do **NOT** prove the script
runs end-to-end against a real Postgres — that needs Docker or a live DB, is **not** exercised
here, and is tracked as an outstanding residual (the #8 precedent), never folded into a "fixed"
claim.

No network, no key, no SDK, no DB.
"""
from __future__ import annotations

import sys
from decimal import Decimal
from types import SimpleNamespace
from xml.etree import ElementTree

import pytest

from backend.app.outlier_canonical import QuantizedOutlierResult, dequantize_outlier
from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.states import CaseState, case_to_memo_view_state
from backend.case_lifecycle.tests.fixtures import InMemoryCaseStore
from backend.common.canon_ser import canon_deserialize
from backend.memo_agent_core.input_builder import MemoAgentInputBuilder
from backend.memo_agent_core.prompt_builder import PromptBuilder
from backend.outlier_model.model import OutlierModel
from backend.outlier_model.schemas import OutlierResult
from backend.outlier_model.shap_explainer import ShapExplainer
from backend.outlier_model.tests.fixtures import (
    make_manifest,
    normal_corpus_profiles,
    typical_profile,
)
from backend.rules_engine.loader import RulebookLoader
from backend.scripts import seed_demo_cases as sd


# ---------------------------------------------------------------------------
# DEFECT 1 — _SeedSeams must be constructible at all
# ---------------------------------------------------------------------------
def test_seed_seams_constructs_without_raising():
    """The defect-1 guard. `RulebookLoader.__init__` takes a REQUIRED `rulebook_dir`; the
    script called it with none, so `_SeedSeams.__init__` raised `TypeError` on its FIRST
    statement and `main()` could not complete under any invocation."""
    seams = sd._SeedSeams()

    assert seams is not None
    # the rulebook really was loaded, not merely constructed
    assert seams._rulebook.rulebook_version == sd.RULEBOOK_VERSION


# ---------------------------------------------------------------------------
# DEFECT 2 — the offline double must cite a rule that EXISTS
# ---------------------------------------------------------------------------
def _real_report_and_prompt():
    loader = RulebookLoader(sd.rulebook_dir())
    from backend.rules_engine.engine import RulesEngine

    engine = RulesEngine(loader, engine_version=sd.ENGINE_VERSION)
    profile = sd._demo_profile(1)
    report = engine.evaluate(profile, sd.RULEBOOK_VERSION)
    agent_input = MemoAgentInputBuilder().build(
        applicant_profile=profile, rule_report=report
    )
    return report, PromptBuilder().build(agent_input)


def test_the_offline_double_cites_a_rule_id_that_exists_in_the_report():
    """The defect-2 guard.

    The double previously hardcoded ``DTI-001``, which **is not a rule in this build** — the DTI
    rule is ``DTI-CEIL-1``. The condition was therefore always False, the double emitted an
    EMPTY ``<rule_id>``, and U4's `CitationValidator` rejected every draft.
    """
    report, prompt = _real_report_and_prompt()
    raw = sd._OfflineLLMClient().generate(model="m", prompt=prompt, temperature=0)

    cited = [el.text or "" for el in ElementTree.fromstring(raw).findall("./cited_rule_ids/rule_id")]
    report_ids = {r.rule_id for r in report.rule_results}

    assert cited, "the double must cite something"
    assert all(c for c in cited), f"empty citation emitted: {cited!r}"
    for rule_id in cited:
        assert rule_id in report_ids, (
            f"{rule_id!r} is not in the rule report - citation validation will reject it. "
            f"Report ids: {sorted(report_ids)}"
        )


def test_no_hardcoded_rule_id_is_absent_from_the_rulebook():
    """Detector: whatever id the double names must be a real one. Guards the *class* of defect,
    not just the specific string, so re-introducing another bogus id is caught."""
    loader = RulebookLoader(sd.rulebook_dir())
    rulebook_ids = {rule.rule_id for rule in loader.load_rulebook(sd.RULEBOOK_VERSION).rules}

    assert "DTI-001" not in rulebook_ids, "sanity: the old hardcoded id really is bogus"
    assert "DTI-CEIL-1" in rulebook_ids


# ---------------------------------------------------------------------------
# THE LOAD-BEARING ONE — a memo actually comes out
# ---------------------------------------------------------------------------
def test_drafting_a_demo_case_produces_a_memo_rather_than_blocking():
    """⚑ The single assertion that would have caught BOTH defects.

    Defect 1 makes this raise; defect 2 makes `draft_memo` return `None` (blocked after the
    citation-retry cap). Only with both fixed does a memo come out.
    """
    seams = sd._SeedSeams()
    profile = sd._demo_profile(1)
    report = seams.evaluate(profile)

    memo = seams.draft_memo(profile, report, None)

    assert memo is not None, "drafting was BLOCKED - the citation did not validate"
    assert memo.recommendation == report.recommendation, "CON-BR2-TYPE: the LLM never changes it"
    assert memo.cited_rule_ids, "a memo with no citations is not audit-ready"


def test_the_seeded_memo_is_stamped_as_an_offline_placeholder():
    """The placeholder must stay unmistakable wherever it travels (register #18's discipline)."""
    seams = sd._SeedSeams()
    profile = sd._demo_profile(2)
    memo = seams.draft_memo(profile, seams.evaluate(profile), None)

    assert memo.model_version == sd.OFFLINE_MODEL_VERSION
    assert "NOT-A-REAL-LLM" in memo.model_version
    assert "PLACEHOLDER" in memo.narrative_prose.upper()


# ---------------------------------------------------------------------------
# The demo path reaches `drafted` / R4 `ready` — what #2's claim actually needs
# ---------------------------------------------------------------------------
def test_the_demo_path_reaches_drafted_and_r4_reports_ready():
    """tier-U proof of the property register #2's claim depends on: a seeded case is
    exercisable. Uses U24's in-memory store; **a real Postgres run is NOT covered here.**"""
    store = InMemoryCaseStore()
    pipeline = CasePipeline(store, sd._SeedSeams(), sd._recommendation_id_factory)

    profile = sd._demo_profile(1)
    application = pipeline.submit(profile.application_id, profile)
    assert application.state is CaseState.EVALUATED

    outcome = pipeline.draft(profile.application_id)
    assert outcome.succeeded, f"draft failed: {outcome.failure_reason}"

    persisted = store.get_application(profile.application_id)
    assert persisted.state is CaseState.DRAFTED
    # R4's `ready` branch - the one the script exists to make reachable
    assert case_to_memo_view_state(persisted) == "ready"
    assert store.recommendation_for_application(profile.application_id) is not None


def test_the_offline_default_path_needs_no_sdk_no_key_and_no_network():
    """The offline double is the DEFAULT; nothing on this path imports the provider SDK."""
    sd._SeedSeams()
    assert "google.genai" not in sys.modules


# ---------------------------------------------------------------------------
# OUTLIER WIRING (register #17 / Q5(a) / Q6(a)) — the injection seam
#
# ⚑ Fold B's whole design is that the FIVE existing `_SeedSeams()` constructions above keep
# byte-identical behaviour: no corpus needed, no ~2.6s fit paid, no new failure mode in a
# constructor that already had a defect of exactly that shape (`test_seed_seams_constructs_
# without_raising`). T1 is the standing proof of that, so a later refactor that moves fitting
# INTO the constructor fails here rather than silently slowing/breaking the five.
# ---------------------------------------------------------------------------
def test_seed_seams_with_no_injected_model_scores_none():
    """T1 — TODAY's behaviour, PINNED (Fold B's safety net).

    ⚑ Non-vacuity was demonstrated by EXECUTION, not asserted: with the `outlier_model is None`
    guard temporarily removed from `_SeedSeams.score_outlier`, this test FAILS. It is green here
    because the guard is present, which is the property being pinned.

    This is what lets the five constructions above stay untouched: the default seam is still the
    Phase-1 `None`, so none of them needs a corpus or pays a fit.
    """
    seams = sd._SeedSeams()

    assert seams.score_outlier(sd._demo_profile(1)) is None


def _tier_u_fitted_model():
    """A SMALL fitted model for tier-U — 12 in-memory profiles, NOT the 615KB committed corpus.

    ⚑ Deliberate: `CorpusSource` was built to impose no hard `corpus/` dependency (BR-OUT-8 /
    NFR-OUT-CORPUS-1), and a tier-U test must not acquire one. The committed-corpus path is
    Q6(a)'s concern and is exercised at T4/T3 against `main()`, where it belongs. Cross-unit
    test-fixture import is this file's existing convention (`case_lifecycle.tests.fixtures`).
    """
    return OutlierModel.fit(normal_corpus_profiles(), make_manifest(), ShapExplainer())


def test_an_injected_fitted_model_makes_score_outlier_return_a_scored_projection():
    """T2 — the injection seam actually scores.

    Mirrors the ESTABLISHED `llm_client` injection shape on this same class: an optional
    constructor argument with an offline-safe default. Nothing is fitted in `__init__`.

    ⚑ SUPERSEDED NAME, recorded: `..._return_a_real_outlier_result`. Written before barrier #5
    was found, when the seam was expected to return `OutlierResult` directly. It returns the
    Decimal `QuantizedOutlierResult` projection instead — CANON-SER refuses float, so the raw
    result cannot cross the persistence boundary. The test's SUBJECT is unchanged (the injection
    seam scores); only the type it pins moved, by the design decision recorded in plan §4.1.
    """
    seams = sd._SeedSeams(outlier_model=_tier_u_fitted_model())

    result = seams.score_outlier(typical_profile())

    assert isinstance(result, QuantizedOutlierResult)
    # ⛔ Decimal, NOT float — this is the property that makes the score persistable at all.
    assert isinstance(result.outlier_score, Decimal)
    assert isinstance(result.is_outlier, bool)
    # PROV-1: the reproducibility triple travels with the score or it cannot be replayed.
    assert result.provenance.corpus_version == "corpus-test-v1"
    assert result.provenance.seed == 4242
    assert result.provenance.outlier_model_version
    # BR-OUT-9 / advisory-only: a score carries NO verdict field, projection or not.
    assert not hasattr(result, "recommendation")

    # and it dequantizes back to the real advisory shape the wire expects
    assert isinstance(dequantize_outlier(result), OutlierResult)


def test_main_fails_loudly_and_by_name_when_the_corpus_is_absent(tmp_path, monkeypatch):
    """T3 — Q6(a)'s loud failure, and it must name the PATH.

    ⚑ The rejected alternative was Q6(b): fall back to `outlier=None` when the corpus is missing.
    That silently reproduces the exact defect this pass exists to fix, in a script whose entire
    job is producing COMPLETE demo data — so a missing corpus is an error, not a degrade.

    ⚑ This must raise BEFORE any database work, so the test needs no Postgres: `get_settings()`
    and `create_engine` are never reached. That ordering is the property under test as much as
    the message is.
    """
    monkeypatch.setattr(sd, "CORPUS_DIR", tmp_path / "no-such-corpus")

    with pytest.raises(FileNotFoundError) as excinfo:
        sd.main(["--cases", "1"])

    message = str(excinfo.value)
    assert "profiles.json" in message, f"the missing file must be named: {message!r}"
    assert "no-such-corpus" in message, f"the searched path must be named: {message!r}"


def test_main_builds_and_injects_a_fitted_model_from_the_committed_corpus(monkeypatch):
    """T4 — the entrypoint really fits the COMMITTED corpus and hands it to the seams.

    ⚑ This is the ONE test that pays the real ~2.6s fit against `corpus/profiles.json` (300
    profiles), deliberately and exactly once. Fold B's finding was that paying it per
    `_SeedSeams()` construction would cost ~5x that across the tier-U suite for tests whose
    subject is not outlier scoring — hence injection, and hence this single entrypoint test.

    No database: `seed` is intercepted, so nothing downstream of the model build runs.
    """
    captured = {}

    def _capture_seed(engine, case_count, seams, draft=True):
        captured["seams"] = seams
        return []

    monkeypatch.setattr(sd, "get_settings", lambda: SimpleNamespace(DATABASE_URL="postgresql://x/y"))
    monkeypatch.setattr(sd.sa, "create_engine", lambda url: object())
    monkeypatch.setattr(sd, "apply_all_migrations", lambda engine: None)
    monkeypatch.setattr(sd, "seed", _capture_seed)

    assert sd.main(["--cases", "1"]) == 0

    seams = captured["seams"]
    assert seams._outlier_model is not None, "main() must INJECT a fitted model, not leave None"

    # The injected model scores for real, and its provenance is the COMMITTED corpus's own.
    result = seams.score_outlier(sd._demo_profile(1))
    assert isinstance(result, QuantizedOutlierResult)
    assert result.provenance.corpus_version == "1.0.0"
    assert result.provenance.seed == 42


def test_a_scored_case_drafts_and_persists_its_outlier_end_to_end():
    """T10 — ⛔ THE BARRIER #5 REGRESSION TEST.

    Before the Decimal projection this raised `CanonSerError: float is not permitted; use Decimal
    (CON-DET-1)` at `pipeline.py:134` — a real score could not be persisted AT ALL, so the case
    never reached `drafted`. This is the end-to-end proof that the whole path now works, at the
    only tier available without a database.

    ⚑ It also exercises `route_borderline`, which U24 calls with the seam's return and which
    compares `outlier_score >= OUTLIER_SCORE_CUTOFF` (a float). Decimal-vs-float COMPARISON is
    supported in Python 3 (only arithmetic raises), but that is a fact worth pinning rather than
    assuming, since it sits between two frozen units.
    """
    model = OutlierModel.fit(normal_corpus_profiles(), make_manifest(), ShapExplainer())
    store = InMemoryCaseStore()
    pipeline = CasePipeline(store, sd._SeedSeams(outlier_model=model), sd._recommendation_id_factory)
    profile = sd._demo_profile(1)

    pipeline.submit(profile.application_id, profile)
    outcome = pipeline.draft(profile.application_id)

    assert outcome.succeeded, f"draft failed: {outcome.failure_reason}"
    assert store.get_application(profile.application_id).state is CaseState.DRAFTED

    recommendation = store.recommendation_for_application(profile.application_id)
    assert recommendation.outlier_canonical is not None, (
        "the whole point of this pass: outlier data must actually be PERSISTED"
    )

    # and it reads back as a real OutlierResult, not as an opaque blob
    restored = dequantize_outlier(canon_deserialize(recommendation.outlier_canonical))
    assert isinstance(restored, OutlierResult)
    assert isinstance(restored.outlier_score, float)
    # the tier-U fixture manifest's seed, single-sourced — NOT the committed corpus's 42
    assert restored.provenance.seed == 4242
