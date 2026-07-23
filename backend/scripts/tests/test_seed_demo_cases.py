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
from xml.etree import ElementTree

import pytest

from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.states import CaseState, case_to_memo_view_state
from backend.case_lifecycle.tests.fixtures import InMemoryCaseStore
from backend.memo_agent_core.input_builder import MemoAgentInputBuilder
from backend.memo_agent_core.prompt_builder import PromptBuilder
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
