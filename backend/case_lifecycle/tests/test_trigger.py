"""NFR-CASE-TRIGGER-1 (P-CASE-6) — R4 is a pure, side-effect-free read. BR-CASE-4.

⚑ A SPY proves it, not an absence of failure: the read path must invoke the pipeline ZERO times.
"""
from __future__ import annotations

from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.states import CaseState
from backend.case_lifecycle.tests import fixtures as fx


def test_the_read_path_invokes_the_pipeline_zero_times():
    store = fx.InMemoryCaseStore()
    seams = fx.drafting_success_double()
    pipeline = CasePipeline(store, seams, fx.recommendation_id_factory)
    application_id, raw = fx.clean_case()
    pipeline.submit(application_id, raw)

    calls_before = list(seams.calls)
    atomics_before = store.atomic_entries

    pipeline.read(application_id)
    pipeline.read(application_id)

    assert seams.calls == calls_before          # ZERO new pipeline calls
    assert store.atomic_entries == atomics_before  # and no write


def test_the_read_path_does_not_change_state():
    store = fx.InMemoryCaseStore()
    pipeline = CasePipeline(store, fx.drafting_success_double(), fx.recommendation_id_factory)
    application_id, raw = fx.clean_case()
    pipeline.submit(application_id, raw)

    before = store.get_application(application_id).state
    pipeline.read(application_id)
    assert store.get_application(application_id).state is before is CaseState.EVALUATED


def test_after_the_explicit_trigger_the_state_is_drafted():
    store = fx.InMemoryCaseStore()
    pipeline = CasePipeline(store, fx.drafting_success_double(), fx.recommendation_id_factory)
    application_id, raw = fx.clean_case()
    pipeline.submit(application_id, raw)

    assert pipeline.draft(application_id).succeeded is True
    assert store.get_application(application_id).state is CaseState.DRAFTED


def test_reading_an_unknown_application_returns_none_without_side_effects():
    store = fx.InMemoryCaseStore()
    seams = fx.drafting_success_double()
    pipeline = CasePipeline(store, seams, fx.recommendation_id_factory)
    assert pipeline.read("no-such-case") is None
    assert seams.calls == []


def test_drafting_an_unknown_application_returns_a_failure_outcome():
    """No exception for a domain miss — an ordinary DraftOutcome (Q4-A)."""
    store = fx.InMemoryCaseStore()
    seams = fx.drafting_success_double()
    pipeline = CasePipeline(store, seams, fx.recommendation_id_factory)

    outcome = pipeline.draft("no-such-case")

    assert outcome.succeeded is False
    assert outcome.failure_reason == "unknown application"
    assert seams.calls == []          # nothing in the pipeline ran
