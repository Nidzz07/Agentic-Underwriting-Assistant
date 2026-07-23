"""NFR-JUDGE-PERF-1 (P-JUDGE-14) — observed, NEVER gated.

U22 owns NO runtime SLO: memo-quality evaluation is an OUT-OF-BAND quality activity, never
on the request path and never deployed. (This is also part of why the Infrastructure Design
stage was assessed as a logged SKIP.) Nothing is timed at tier-U — the engine is an offline
fake — and NO test in this unit asserts a timing failure.
"""
from __future__ import annotations

from backend.llm_judge.pipeline import run_eval
from backend.llm_judge.rubric import GROUNDEDNESS_RUBRIC
from backend.llm_judge.tests import fixtures as fx
from backend.llm_judge.tests import structural as sg


def test_the_run_completes_without_any_timing_assertion():
    engine = fx.DeclaredScoreEngine(default=(4, 4))
    result = run_eval(fx.exemption_composition(), GROUNDEDNESS_RUBRIC, engine)
    assert result.scored_count == 2  # correctness only - no duration asserted


def test_no_u22_test_gates_on_a_duration():
    """The observed-never-gated discipline, enforced by a scan over U22's own tests."""
    forbidden = ("time.time(", "perf_counter(", "timeout=", "duration_ms", "elapsed")
    scanned = 0
    for path in sg.authored_py_files():
        if path.name == "test_perf_observed.py":
            continue  # holds the token list itself
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, (path.name, token)
        scanned += 1
    assert scanned >= len(sg.EXPECTED_PRODUCTION_MODULES)


def test_no_production_module_declares_a_latency_field_or_slo():
    for path in sg.production_py_files():
        text = path.read_text(encoding="utf-8").lower()
        assert "slo" not in text, path.name
        assert "latency" not in text, path.name
