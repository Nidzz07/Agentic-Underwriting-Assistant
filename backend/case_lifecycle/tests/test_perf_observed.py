"""NFR-CASE-PERF-1 (P-CASE-15) — observed, NEVER gated.

U24 owns NO runtime SLO: drafting is an out-of-band step behind its own trigger, not a
request-path read. Nothing is timed at tier-U (the LLM is an offline double), and NO U24 test
asserts a timing failure.
"""
from __future__ import annotations

from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.tests import fixtures as fx
from backend.case_lifecycle.tests import structural as sg


def test_the_lifecycle_runs_without_any_timing_assertion():
    store = fx.InMemoryCaseStore()
    pipeline = CasePipeline(store, fx.drafting_success_double(), fx.recommendation_id_factory)
    application_id, raw = fx.clean_case()
    pipeline.submit(application_id, raw)
    assert pipeline.draft(application_id).succeeded is True   # correctness only


def test_no_u24_test_gates_on_a_duration():
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
