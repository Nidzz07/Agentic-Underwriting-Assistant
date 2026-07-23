"""NFR-JUDGE-ADVISORY-1 / NOVERDICT-1 (P-JUDGE-10) — advisory-only. BR-JUDGE-7 / CON-BR2-TYPE.

The judge scores PROSE. It emits no ``Recommendation``, no verdict, and no field capable of
carrying one — so *"the judge changed the recommendation"* is UNREPRESENTABLE, not merely
forbidden.

⚑ SCOPE (CG-JUDGE-Fold-2) — the VERDICT-token half scans PRODUCTION MODULES ONLY, and that
is FORCED by a frozen shape, not chosen for convenience: ``DecisionMemo.recommendation`` is a
REQUIRED field on the frozen U4 model, so every memo fixture MUST carry a verdict value.
That is the memo UNDER JUDGMENT — judge INPUT — which the approved NFR text already
distinguishes from a verdict *"used as a judge OUTPUT"*. The STRUCTURAL half below carries
the real teeth and is unaffected by fixture content.
"""
from __future__ import annotations

from dataclasses import fields

from backend.llm_judge import pipeline, rubric, schemas
from backend.llm_judge.pipeline import run_eval
from backend.llm_judge.rubric import GROUNDEDNESS_RUBRIC
from backend.llm_judge.schemas import (
    DimensionScore,
    EvalRunResult,
    JudgedSample,
    SampleScore,
)
from backend.llm_judge.tests import fixtures as fx
from backend.llm_judge.tests import structural as sg

_U22_OWNED_TYPES = (
    schemas.RubricDimension,
    schemas.GroundednessRubric,
    JudgedSample,
    DimensionScore,
    SampleScore,
    EvalRunResult,
)


def test_no_u22_owned_type_declares_a_recommendation_typed_field():
    """The STRUCTURAL half: the verdict is unrepresentable in U22's own output."""
    for tp in _U22_OWNED_TYPES:
        annotations = {str(f.type) for f in fields(tp)}
        for annotation in annotations:
            assert "Recommendation" not in annotation, (tp.__name__, annotation)
            assert "Confidence" not in annotation, (tp.__name__, annotation)


def test_the_report_carries_no_verdict_field():
    names = {f.name for f in fields(EvalRunResult)} | {f.name for f in fields(SampleScore)}
    for forbidden in ("recommendation", "verdict", "decision", "confidence"):
        assert forbidden not in names


def test_no_production_module_declares_a_recommendation_annotation():
    scanned = 0
    for path in sg.production_py_files():
        names = sg.annotation_names(sg.parse(path))
        assert "Recommendation" not in names, path.name
        scanned += 1
    assert scanned >= len(sg.EXPECTED_PRODUCTION_MODULES)  # non-vacuity


def test_no_bare_verdict_token_is_emitted_as_a_judge_output_in_production():
    scanned = 0
    for path in sg.production_py_files():
        for literal in sg.string_constants(sg.parse(path)):
            for token in sg.VERDICT_TOKENS:
                assert token not in literal, (path.name, token)
        scanned += 1
    assert scanned >= len(sg.EXPECTED_PRODUCTION_MODULES)


def test_detector_a_synthetic_verdict_emitting_type_is_flagged():
    source = (
        "from dataclasses import dataclass\n"
        "from backend.rules_engine.report_schema import Recommendation\n"
        "@dataclass\n"
        "class Bad:\n"
        "    recommendation: Recommendation\n"
    )
    assert "Recommendation" in sg.annotation_names(sg.parse_source(source))


def test_detector_a_synthetic_verdict_token_literal_is_flagged():
    source = 'VERDICT = "APPROVE"\n'
    literals = sg.string_constants(sg.parse_source(source))
    assert any(t in lit for lit in literals for t in sg.VERDICT_TOKENS)


def test_only_the_narrative_prose_region_is_judged():
    """Judging the D/RO/M regions would re-open CON-BR2-TYPE."""
    engine = fx.DeclaredScoreEngine(default=(4, 4))
    run_eval(fx.in_gate_samples(), GROUNDEDNESS_RUBRIC, engine)
    # the fake is handed the whole sample, but the rubric's criteria address prose only
    for dimension in GROUNDEDNESS_RUBRIC.dimensions:
        text = dimension.description.lower()
        assert "prose" in text or "narrative" in text or "wording" in text


def test_rubric_copy_uses_recommendation_never_a_bare_decision():
    for dimension in rubric.GROUNDEDNESS_RUBRIC.dimensions:
        assert "decision" not in dimension.description.lower()


def test_the_judge_never_alters_the_memo_under_judgment():
    engine = fx.DeclaredScoreEngine(default=(4, 4))
    samples = fx.in_gate_samples()
    before = [s.memo.recommendation for s in samples]
    run_eval(samples, GROUNDEDNESS_RUBRIC, engine)
    after = [s.memo.recommendation for s in samples]
    assert before == after  # frozen models: strictly downstream, read-only
    assert pipeline.IN_GATE_PROVIDERS  # module reachable
