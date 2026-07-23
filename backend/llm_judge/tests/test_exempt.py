"""NFR-JUDGE-EXEMPT-1 — LOAD-BEARING (full-highest). BR-JUDGE-3.

⚑ Why load-bearing: a FROZEN U19 artifact (``memo_extensions/tests/test_provgate.py``)
assigns this duty to ``llm-judge`` (U22) BY NAME and deliberately declines to assert it —
*"a tooling-config fact owned by llm-judge (U22), recorded as an explicit, documented
exemption — never implicit, and not asserted here."* **If U22 does not assert it, NOTHING
IN THE BUILD DOES.**

⚑ TWO DISTINCT MECHANISMS, kept in one file so their complementarity is visible (Q4-A):
  * **P-JUDGE-1 PositiveWitness** — teeth on the OUTPUT ``EvalRunResult``: the exemption is
    proven BY PRESENCE (``exempt_count``), never by absence.
  * **P-JUDGE-2 DegenerateSetGuard** — a set predicate on the INPUT sample sequence.

They are NOT the same assertion renamed (ND-Fold-2): different subject (OUTPUT report vs
INPUT set), different field (``exempt_count`` vs ``sample.provider``), different stage
(post-run vs pre-run), different failure mode. **One guards the other's PRECONDITION**: over
an all-in-gate set, a pipeline that never implemented exemption AT ALL would still report
``scored_count == 2``, so the positive teeth would pass VACUOUSLY without the guard.
"""
from __future__ import annotations

from backend.llm_judge.pipeline import (
    is_nonvacuous_exemption_set,
    run_eval,
    score_for,
)
from backend.llm_judge.rubric import GROUNDEDNESS_RUBRIC
from backend.llm_judge.schemas import ProviderScopeTag
from backend.llm_judge.tests import fixtures as fx

# --- P-JUDGE-1: the POSITIVE WITNESS teeth (on the OUTPUT report) ------------------------


def test_exemption_positive_witness_over_the_three_sample_composition():
    engine = fx.DeclaredScoreEngine(default=(4, 4))
    result = run_eval(fx.exemption_composition(), GROUNDEDNESS_RUBRIC, engine)

    assert result.scored_count == 2       # only the two in-gate samples were scored
    assert result.exempt_count == 1       # THE POSITIVE WITNESS - present and counted
    assert score_for(result, fx.EXEMPT_ID) is not None  # RETAINED, never dropped


def test_exempt_sample_is_retained_but_not_scored():
    engine = fx.DeclaredScoreEngine(default=(4, 4))
    result = run_eval(fx.exemption_composition(), GROUNDEDNESS_RUBRIC, engine)
    exempt = score_for(result, fx.EXEMPT_ID)

    assert exempt.in_gate is False
    assert exempt.dimension_scores == ()
    # `None`, deliberately NOT 0.0/False - "not scored", never "failed".
    assert exempt.aggregate is None
    assert exempt.passed is None


def test_detector_a_wrongly_scored_ollama_sample_makes_scored_count_read_three():
    """The detector self-test: the teeth cannot pass on a broken partition.

    Were the Ollama sample wrongly SCORED, ``scored_count`` would read 3. We prove the
    assertion is discriminating by constructing exactly that counterfactual - three
    in-gate-tagged samples - and observing the count the broken behaviour would produce.
    """
    engine = fx.DeclaredScoreEngine(default=(4, 4))
    all_in_gate = [
        *fx.in_gate_samples(),
        fx._sample(fx.EXEMPT_ID, ProviderScopeTag.GEMINI, "prose"),
    ]
    broken = run_eval(all_in_gate, GROUNDEDNESS_RUBRIC, engine)
    assert broken.scored_count == 3       # <- what a mis-partition would produce
    assert broken.exempt_count == 0

    correct = run_eval(fx.exemption_composition(), GROUNDEDNESS_RUBRIC, engine)
    assert correct.scored_count == 2      # <- what the real partition produces
    assert correct.exempt_count == 1


def test_the_engine_is_never_asked_to_score_the_exempt_sample():
    engine = fx.DeclaredScoreEngine(default=(4, 4))
    run_eval(fx.exemption_composition(), GROUNDEDNESS_RUBRIC, engine)
    assert fx.EXEMPT_ID not in engine.calls
    assert sorted(engine.calls) == sorted(fx.INGATE_IDS)


# --- P-JUDGE-2: the DEGENERATE-SET GUARD (on the INPUT set) -----------------------------


def test_degenerate_all_in_gate_set_is_flagged_as_a_vacuous_configuration():
    assert is_nonvacuous_exemption_set(fx.degenerate_all_in_gate_set()) is False


def test_the_three_sample_composition_is_a_nonvacuous_configuration():
    assert is_nonvacuous_exemption_set(fx.exemption_composition()) is True


def test_a_degenerate_set_would_report_exempt_count_zero():
    """Why the guard exists: the degenerate set produces exactly the vacuous outcome
    BR-JUDGE-3 forbids - and the positive teeth alone would NOT catch it."""
    engine = fx.DeclaredScoreEngine(default=(4, 4))
    result = run_eval(fx.degenerate_all_in_gate_set(), GROUNDEDNESS_RUBRIC, engine)
    assert result.exempt_count == 0
    assert result.scored_count == 2  # <- indistinguishable from a correct in-gate run
    assert is_nonvacuous_exemption_set(fx.degenerate_all_in_gate_set()) is False


def test_the_predicate_never_touches_an_eval_run_result():
    """ANTI-COLLAPSE (ND-Fold-2): the predicate is a pure set property over INPUT samples.
    Its signature takes samples and returns bool - it constructs no report."""
    result = is_nonvacuous_exemption_set(fx.exemption_composition())
    assert isinstance(result, bool)


# --- Req-Fold-1: the two families are provably never identity-equal (Q2-A) ---------------


def test_degenerate_and_in_gate_fixture_id_sets_are_disjoint():
    """The separation is ASSERTED, not merely intended."""
    in_gate_ids = {s.sample_id for s in fx.in_gate_samples()}
    degenerate_ids = {s.sample_id for s in fx.degenerate_all_in_gate_set()}
    assert in_gate_ids.isdisjoint(degenerate_ids)


def test_every_fixture_family_uses_a_distinct_id_prefix():
    families = {
        "ingate-": {s.sample_id for s in fx.in_gate_samples()},
        "exempt-": {fx.exempt_witness_sample().sample_id},
        "degen-": {s.sample_id for s in fx.degenerate_all_in_gate_set()},
        "anchor-": {s.sample_id for s in fx.anchoring_pair()},
    }
    for prefix, ids in families.items():
        assert all(i.startswith(prefix) for i in ids), prefix
    # pairwise disjoint across all four families
    all_ids = [i for ids in families.values() for i in ids]
    assert len(all_ids) == len(set(all_ids))


def test_degenerate_builder_does_not_reuse_the_in_gate_builder():
    """It must be a genuinely separate builder, not an alias."""
    in_gate = fx.in_gate_samples()
    degenerate = fx.degenerate_all_in_gate_set()
    assert in_gate != degenerate
    assert all(d.sample_id not in {s.sample_id for s in in_gate} for d in degenerate)
