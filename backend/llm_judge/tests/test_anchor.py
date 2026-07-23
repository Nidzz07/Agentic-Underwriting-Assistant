"""NFR-JUDGE-ANCHOR-1 (P-JUDGE-6) — the paired-fixture teeth. BR-JUDGE-5 / QA-4 / Q7-A.

⚑ HONEST SCOPE (Q2-A / ND-Fold-1) — stated here as a first-class part of the target, not a
caveat. The tier-U ``RubricEngine`` fake is FROZEN BY THE FD as returning FIXTURE-DECLARED
scores. So what these teeth prove is:

  * the PAIRED-FIXTURE PLUMBING — two distinguishable samples flow through the seam and land
    as distinguishable ``SampleScore``s, in declared dimension order, aggregated correctly,
    with the close one higher; and
  * the UNSPLITTABLE-PAIR SAFEGUARD — the pair cannot be taken apart at the call site.

They do **NOT** prove that a real judge scores divergence lower. That is ENGINE behaviour,
and it is the fifth named discharge criterion of ``PROMPTFOO-CLI-DEFERRED``
(*"real-shape interop verified against the seeded fixtures"*).

⚑ The fake is deliberately NOT given a similarity heuristic: U22 would then own a scoring
heuristic that is not what the real engine does, and a green test here would attest to
U22's own heuristic rather than to the rubric — the same false-confidence failure mode
already rejected for the by-value interop replica.
"""
from __future__ import annotations

import inspect

from backend.llm_judge.pipeline import run_eval, score_for
from backend.llm_judge.rubric import (
    DIMENSION_ANCHORING_CONSISTENCY,
    GROUNDEDNESS_RUBRIC,
)
from backend.llm_judge.tests import fixtures as fx


def test_close_fixture_outscores_the_divergent_fixture():
    close, divergent = fx.anchoring_pair()          # the pair, taken TOGETHER
    result = run_eval([close, divergent], GROUNDEDNESS_RUBRIC, fx.anchoring_engine())

    close_score = score_for(result, fx.ANCHOR_CLOSE_ID)
    divergent_score = score_for(result, fx.ANCHOR_DIVERGENT_ID)

    assert close_score.aggregate > divergent_score.aggregate
    assert close_score.passed is True
    assert divergent_score.passed is False


def test_the_anchoring_dimension_is_scored_for_both_members_of_the_pair():
    close, divergent = fx.anchoring_pair()
    result = run_eval([close, divergent], GROUNDEDNESS_RUBRIC, fx.anchoring_engine())
    for sample_id in (fx.ANCHOR_CLOSE_ID, fx.ANCHOR_DIVERGENT_ID):
        dims = {d.dimension_id for d in score_for(result, sample_id).dimension_scores}
        assert DIMENSION_ANCHORING_CONSISTENCY in dims


def test_the_pair_is_unsplittable_at_the_type_level():
    """``anchoring_pair()`` returns ONE value, so a test cannot take one without the other."""
    pair = fx.anchoring_pair()
    assert isinstance(pair, tuple)
    assert len(pair) == 2
    signature = inspect.signature(fx.anchoring_pair)
    assert "tuple" in str(signature.return_annotation).lower()


def test_detector_a_single_fixture_only_configuration_is_insufficient():
    """A lone close fixture passes VACUOUSLY - it proves no discrimination whatsoever.

    We demonstrate the vacuity directly: over a single fixture the run is 'green' while
    saying nothing about the divergent case, which is exactly why the pair is mandatory.
    """
    close, divergent = fx.anchoring_pair()

    single = run_eval([close], GROUNDEDNESS_RUBRIC, fx.anchoring_engine())
    assert single.gate_passed is True          # green...
    assert single.scored_count == 1            # ...on ONE fixture - vacuous
    assert score_for(single, fx.ANCHOR_DIVERGENT_ID) is None  # nothing to compare against

    paired = run_eval([close, divergent], GROUNDEDNESS_RUBRIC, fx.anchoring_engine())
    assert paired.scored_count == 2            # the pair is what makes it discriminating


def test_the_anchoring_pair_is_not_overlapped_onto_the_provider_tagged_samples():
    """Q1-A: its own family, so a provider-scope edit cannot move the anchoring baseline."""
    anchor_ids = {s.sample_id for s in fx.anchoring_pair()}
    provider_ids = {s.sample_id for s in fx.in_gate_samples()} | {fx.EXEMPT_ID}
    assert anchor_ids.isdisjoint(provider_ids)


def test_one_canonical_reference_memo_serves_the_whole_set():
    """QA-4's 'not claimed bit-identical': a STYLE exemplar, not a per-applicant twin."""
    first = fx.reference_memo()
    second = fx.reference_memo()
    assert first == second
    assert first.narrative_prose  # non-empty


def test_honest_scope_is_documented_on_the_fake_itself():
    """The narrowing is part of the pattern's definition, not tribal knowledge."""
    doc = fx.DeclaredScoreEngine.__doc__ or ""
    assert "does NOT compute similarity" in doc
