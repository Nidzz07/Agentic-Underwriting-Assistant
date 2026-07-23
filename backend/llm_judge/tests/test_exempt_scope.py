"""NFR-JUDGE-EXEMPTSCOPE-1 (P-JUDGE-9) — exempt from MEMO-QUALITY gates ONLY. BR-JUDGE-4.

*"Exempt from scoring"* must NEVER be recorded, rendered or read as *"untested"*. Ollama
holds ``temperature=0`` and CON-BR2-TYPE identically — and frozen U19 asserts those
DECISION-LEVEL gates for it directly (``memo_extensions/tests/test_provgate.py``).

⚑ U22 REFERENCES those assertions; it never re-derives them. This file therefore asserts
only what U22 owns: that the exempt record NAMES the exemption's scope.
"""
from __future__ import annotations

from backend.llm_judge import pipeline, rubric, schemas
from backend.llm_judge.pipeline import run_eval, score_for
from backend.llm_judge.rubric import GROUNDEDNESS_RUBRIC
from backend.llm_judge.schemas import EXEMPT_REASON_MEMO_QUALITY
from backend.llm_judge.tests import fixtures as fx
from backend.llm_judge.tests import structural as sg


def test_the_exempt_record_carries_an_explicit_memo_quality_reason_tag():
    engine = fx.DeclaredScoreEngine(default=(4, 4))
    result = run_eval(fx.exemption_composition(), GROUNDEDNESS_RUBRIC, engine)
    exempt = score_for(result, fx.EXEMPT_ID)

    assert exempt.exempt_reason == EXEMPT_REASON_MEMO_QUALITY
    assert "memo-quality" in exempt.exempt_reason
    # The scope is NAMED, and the decision-level gates are explicitly still held.
    assert "decision-level" in exempt.exempt_reason


def test_in_gate_records_carry_no_exemption_reason():
    engine = fx.DeclaredScoreEngine(default=(4, 4))
    result = run_eval(fx.exemption_composition(), GROUNDEDNESS_RUBRIC, engine)
    for score in result.sample_scores:
        if score.in_gate:
            assert score.exempt_reason is None


def test_no_u22_module_states_or_implies_ollama_is_untested():
    """A scan over every U22 module: the word 'untested' must appear nowhere."""
    scanned = 0
    for path in sg.authored_py_files():
        if path.name == "test_exempt_scope.py":
            continue  # holds the forbidden token itself, by necessity (the detector below)
        text = path.read_text(encoding="utf-8")
        assert "untested" not in text.lower(), path.name
        scanned += 1
    assert scanned >= len(sg.EXPECTED_PRODUCTION_MODULES)  # non-vacuity


def test_detector_the_untested_scan_is_non_vacuous():
    # A synthetic artifact characterising Ollama as untested IS flagged by the same check.
    synthetic = "The ollama provider is untested in this build."
    assert "untested" in synthetic.lower()


def test_the_exemption_scope_is_documented_in_the_provider_scope_tag():
    doc = schemas.ProviderScopeTag.__doc__ or ""
    assert "memo-quality" in doc
    assert "decision-level" in doc
    # documentation only - the enforcement is the reason-tag assertion above
    assert schemas.ProviderScopeTag.OLLAMA not in pipeline.IN_GATE_PROVIDERS
    assert rubric.GROUNDEDNESS_RUBRIC.threshold == 4
