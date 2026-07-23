"""The evaluation lifecycle (C-JUDGE-2) — assemble, scope-filter, score, aggregate, report.

**Header comment — DOCUMENTATION ONLY, never enforcement** (each property is scan-enforced
in C-JUDGE-5): holds no LLM; edits no frozen unit; declares no verdict; no network at tier-U.

STRICTLY DOWNSTREAM of memo generation: memos arrive already drafted and NOTHING here feeds
back into generation, alters a recommendation, or reaches the deterministic rules path.

Patterns realized here:
  * **P-JUDGE-9 ScopePartition** — ``partition_by_scope`` is a PARTITION, so "scored" and
    "retained" can never silently diverge.
  * **P-JUDGE-1 PositiveWitness** — ``run_eval`` RETAINS exempt samples in ``sample_scores``
    and counts them in ``exempt_count``. Exempt is never dropped.
  * **P-JUDGE-2 DegenerateSetGuard** — ``is_nonvacuous_exemption_set`` (see its docstring;
    it is deliberately a SIBLING of the pipeline, never a step in it).
  * **P-JUDGE-8 PureBoundaryArithmetic** — ``meets_threshold`` single-sources the ``>=``
    comparison for both the per-sample and the run-level gate. No RNG, no wall-clock.
"""
from __future__ import annotations

from typing import Optional, Sequence

from backend.llm_judge.engine import RubricEngine
from backend.llm_judge.schemas import (
    EXEMPT_REASON_MEMO_QUALITY,
    DimensionScore,
    EvalRunResult,
    EvalTier,
    GroundednessRubric,
    JudgedSample,
    ProviderScopeTag,
    SampleScore,
)

#: The FR-PROV-GATE-2 in-gate set. Ollama is deliberately absent (memo-quality gates only).
IN_GATE_PROVIDERS: frozenset[ProviderScopeTag] = frozenset(
    {ProviderScopeTag.GEMINI, ProviderScopeTag.CLAUDE}
)


def partition_by_scope(
    samples: Sequence[JudgedSample],
) -> tuple[list[JudgedSample], list[JudgedSample]]:
    """``(in_gate, exempt)`` — a PARTITION: every sample lands in exactly one side."""
    in_gate = [s for s in samples if s.provider in IN_GATE_PROVIDERS]
    exempt = [s for s in samples if s.provider not in IN_GATE_PROVIDERS]
    return in_gate, exempt


def is_nonvacuous_exemption_set(samples: Sequence[JudgedSample]) -> bool:
    """True iff at least one sample is exempt-tagged — i.e. there IS something to exclude.

    ⚑ A SET property, not a test-configuration opinion. It FLAGS NOTHING and RAISES NOTHING
    on its own, and **nothing in production calls it as a gate** — so it can never wrongly
    reject a legitimate run over a corpus that genuinely contains no Ollama memos. The TEST
    applies it: ``False`` over ``degenerate_all_in_gate_set()``, ``True`` over the
    three-sample composition.

    ⚑ ANTI-COLLAPSE (ND-Fold-2): takes samples, returns ``bool``. It NEVER constructs, runs
    or reads an ``EvalRunResult`` — doing so would collapse it into P-JUDGE-1's positive
    teeth, which assert on the OUTPUT report. This guards THEIR precondition: over an
    all-in-gate set a pipeline that never implemented exemption at all would still report
    ``scored_count == 2``, so those teeth would pass VACUOUSLY without this.
    """
    return any(s.provider not in IN_GATE_PROVIDERS for s in samples)


def meets_threshold(aggregate: float, threshold: int) -> bool:
    """The SINGLE source of the gate comparison — ``>=``, stated explicitly.

    Boundary discipline (THRESH-1): ``meets_threshold(4.0, 4)`` is True and
    ``meets_threshold(3.99, 4)`` is False.
    """
    return aggregate >= threshold


def aggregate_sample(
    scores: Sequence[DimensionScore], threshold: int
) -> tuple[float, bool]:
    """``(aggregate, passed)`` — PURE. Mean of the dimension scores; ``passed`` via
    ``meets_threshold``. An empty score set aggregates to ``0.0`` and does not pass."""
    if not scores:
        return 0.0, False
    aggregate = sum(s.score for s in scores) / len(scores)
    return aggregate, meets_threshold(aggregate, threshold)


def run_eval(
    samples: Sequence[JudgedSample],
    rubric: GroundednessRubric,
    engine: RubricEngine,
    tier: EvalTier = EvalTier.UNIT,
) -> EvalRunResult:
    """Assemble -> partition -> score in-gate through the injected seam -> aggregate ->
    assemble the report.

    Exempt samples are RETAINED in ``sample_scores`` and counted in ``exempt_count``; their
    ``aggregate``/``passed`` are ``None`` (not scored — deliberately not "failed"), and they
    carry ``EXEMPT_REASON_MEMO_QUALITY`` naming the exemption's scope.

    ``sample_scores`` preserves INPUT order, so the report is deterministic.
    """
    in_gate, _exempt = partition_by_scope(samples)
    in_gate_ids = {s.sample_id for s in in_gate}

    sample_scores: list[SampleScore] = []
    in_gate_aggregates: list[float] = []

    for sample in samples:
        if sample.sample_id in in_gate_ids and sample.provider in IN_GATE_PROVIDERS:
            dimension_scores = tuple(engine.score(sample, rubric))
            aggregate, passed = aggregate_sample(dimension_scores, rubric.threshold)
            in_gate_aggregates.append(aggregate)
            sample_scores.append(
                SampleScore(
                    sample_id=sample.sample_id,
                    provider=sample.provider,
                    dimension_scores=dimension_scores,
                    aggregate=aggregate,
                    passed=passed,
                    in_gate=True,
                )
            )
        else:
            sample_scores.append(
                SampleScore(
                    sample_id=sample.sample_id,
                    provider=sample.provider,
                    dimension_scores=(),
                    aggregate=None,
                    passed=None,
                    in_gate=False,
                    exempt_reason=EXEMPT_REASON_MEMO_QUALITY,
                )
            )

    aggregate_score = (
        sum(in_gate_aggregates) / len(in_gate_aggregates) if in_gate_aggregates else 0.0
    )
    return EvalRunResult(
        rubric_id=rubric.rubric_id,
        sample_scores=tuple(sample_scores),
        scored_count=len(in_gate_aggregates),
        exempt_count=len(sample_scores) - len(in_gate_aggregates),
        aggregate_score=aggregate_score,
        gate_passed=meets_threshold(aggregate_score, rubric.threshold),
        tier=tier,
        dimension_ids=tuple(d.dimension_id for d in rubric.dimensions),
    )


def score_for(result: EvalRunResult, sample_id: str) -> Optional[SampleScore]:
    """The named sample's record, or ``None`` — used to assert an exempt sample is PRESENT."""
    for score in result.sample_scores:
        if score.sample_id == sample_id:
            return score
    return None
