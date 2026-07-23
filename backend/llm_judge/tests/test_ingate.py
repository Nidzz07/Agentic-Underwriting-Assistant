"""NFR-JUDGE-INGATE-1 (P-JUDGE-9) — Gemini + Claude are in-gate. BR-JUDGE-2 / FR-PROV-GATE-2.

⚑ Explicitly NOT re-derived: FR-PROV-GATE-1's DECISION-LEVEL gates (reproducibility 100%,
bias-swap delta 0) apply to all three providers and remain ``quality-gates``' to own. U22
single-sources GATE-2 only.
"""
from __future__ import annotations

from backend.llm_judge.pipeline import IN_GATE_PROVIDERS, partition_by_scope, run_eval
from backend.llm_judge.rubric import GROUNDEDNESS_RUBRIC
from backend.llm_judge.schemas import ProviderScopeTag
from backend.llm_judge.tests import fixtures as fx


def test_gemini_and_claude_are_the_in_gate_set():
    assert IN_GATE_PROVIDERS == {ProviderScopeTag.GEMINI, ProviderScopeTag.CLAUDE}
    assert ProviderScopeTag.OLLAMA not in IN_GATE_PROVIDERS


def test_both_in_gate_samples_are_scored_and_counted():
    engine = fx.DeclaredScoreEngine(default=(4, 4))
    result = run_eval(fx.in_gate_samples(), GROUNDEDNESS_RUBRIC, engine)

    assert result.scored_count == 2
    assert all(s.in_gate is True for s in result.sample_scores)
    assert {s.sample_id for s in result.sample_scores} == set(fx.INGATE_IDS)


def test_detector_a_sample_wrongly_filtered_out_drops_the_count():
    engine = fx.DeclaredScoreEngine(default=(4, 4))
    full = run_eval(fx.in_gate_samples(), GROUNDEDNESS_RUBRIC, engine)
    dropped = run_eval(fx.in_gate_samples()[:1], GROUNDEDNESS_RUBRIC, engine)
    assert full.scored_count == 2
    assert dropped.scored_count == 1  # <- what a wrongly-filtered sample would produce


def test_partition_is_exhaustive_and_disjoint():
    samples = fx.exemption_composition()
    in_gate, exempt = partition_by_scope(samples)
    assert len(in_gate) + len(exempt) == len(samples)
    assert {s.sample_id for s in in_gate}.isdisjoint({s.sample_id for s in exempt})


def test_every_sample_appears_in_the_report_in_input_order():
    engine = fx.DeclaredScoreEngine(default=(4, 4))
    samples = fx.exemption_composition()
    result = run_eval(samples, GROUNDEDNESS_RUBRIC, engine)
    assert [s.sample_id for s in result.sample_scores] == [s.sample_id for s in samples]
