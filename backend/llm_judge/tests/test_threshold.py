"""NFR-JUDGE-THRESH-1 (P-JUDGE-8) — the >= 4/5 gate, with the boundary asserted EXPLICITLY.

BR-JUDGE-1 / AC-6 / QA-4. Aggregation and the gate are a PURE function of the dimension
scores: no RNG, no wall-clock, byte-reproducible given fixed scores.
"""
from __future__ import annotations

from backend.llm_judge.pipeline import (
    aggregate_sample,
    meets_threshold,
    run_eval,
)
from backend.llm_judge.rubric import GROUNDEDNESS_RUBRIC
from backend.llm_judge.schemas import DimensionScore
from backend.llm_judge.tests import fixtures as fx


def test_boundary_aggregate_exactly_four_passes():
    # The `>=` comparison asserted explicitly, on the intended side of the boundary.
    assert meets_threshold(4.0, 4) is True


def test_boundary_aggregate_three_point_nine_nine_fails():
    assert meets_threshold(3.99, 4) is False


def test_threshold_comparison_is_gte_not_gt():
    # A `>` implementation would fail the first assertion; a `>` on 4.0 would read False.
    assert meets_threshold(4.0, 4) is True
    assert meets_threshold(4.5, 4) is True
    assert meets_threshold(3.5, 4) is False


def test_aggregate_sample_is_the_mean_and_applies_the_threshold():
    scores = (
        DimensionScore(dimension_id="groundedness", score=5, justification="j"),
        DimensionScore(dimension_id="anchoring_consistency", score=3, justification="j"),
    )
    aggregate, passed = aggregate_sample(scores, GROUNDEDNESS_RUBRIC.threshold)
    assert aggregate == 4.0
    assert passed is True


def test_aggregate_sample_below_threshold_does_not_pass():
    scores = (
        DimensionScore(dimension_id="groundedness", score=3, justification="j"),
        DimensionScore(dimension_id="anchoring_consistency", score=4, justification="j"),
    )
    aggregate, passed = aggregate_sample(scores, GROUNDEDNESS_RUBRIC.threshold)
    assert aggregate == 3.5
    assert passed is False


def test_aggregate_sample_empty_score_set_does_not_pass():
    assert aggregate_sample((), GROUNDEDNESS_RUBRIC.threshold) == (0.0, False)


def test_gate_passed_computed_over_the_in_gate_mean():
    engine = fx.DeclaredScoreEngine(default=(4, 4))
    result = run_eval(fx.in_gate_samples(), GROUNDEDNESS_RUBRIC, engine)
    assert result.aggregate_score == 4.0
    assert result.gate_passed is True


def test_gate_fails_when_the_in_gate_mean_is_below_four():
    engine = fx.DeclaredScoreEngine(
        {fx.INGATE_IDS[0]: (3, 3), fx.INGATE_IDS[1]: (4, 4)}
    )
    result = run_eval(fx.in_gate_samples(), GROUNDEDNESS_RUBRIC, engine)
    assert result.aggregate_score == 3.5
    assert result.gate_passed is False


def test_exempt_sample_provably_does_not_contribute_to_the_gate():
    # The Ollama sample is present, but a wildly-low declared score for it must not move
    # the aggregate: the in-gate mean is identical with and without it.
    engine = fx.DeclaredScoreEngine({fx.EXEMPT_ID: (1, 1)}, default=(4, 4))
    with_exempt = run_eval(fx.exemption_composition(), GROUNDEDNESS_RUBRIC, engine)
    in_gate_only = run_eval(fx.in_gate_samples(), GROUNDEDNESS_RUBRIC, engine)
    assert with_exempt.aggregate_score == in_gate_only.aggregate_score == 4.0
    assert with_exempt.gate_passed is True


def test_scoring_is_deterministic_and_follows_declared_dimension_order():
    engine = fx.DeclaredScoreEngine(default=(5, 3))
    first = run_eval(fx.in_gate_samples(), GROUNDEDNESS_RUBRIC, engine)
    second = run_eval(fx.in_gate_samples(), GROUNDEDNESS_RUBRIC, engine)
    assert first == second  # byte-reproducible given fixed scores
    assert first.dimension_ids == tuple(
        d.dimension_id for d in GROUNDEDNESS_RUBRIC.dimensions
    )
    assert first.sample_scores[0].dimension_scores[0].dimension_id == "groundedness"
    assert (
        first.sample_scores[0].dimension_scores[1].dimension_id
        == "anchoring_consistency"
    )
