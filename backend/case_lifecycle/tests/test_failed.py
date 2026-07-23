"""NFR-CASE-FAILED-1 (P-CASE-7) — the failed terminal state is real. BR-CASE-5.

Driven by `drafting_failure_double()` — ⚑ ITS OWN FIXTURE FAMILY, so this target can never be
weakened by an edit made for the success path.
"""
from __future__ import annotations

from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.states import TERMINAL_STATES, CaseState
from backend.case_lifecycle.tests import fixtures as fx


def _failed_case():
    store = fx.InMemoryCaseStore()
    pipeline = CasePipeline(store, fx.drafting_failure_double(), fx.recommendation_id_factory)
    application_id, raw = fx.clean_case()
    pipeline.submit(application_id, raw)
    outcome = pipeline.draft(application_id)
    return store, application_id, outcome


def test_a_failing_double_drives_the_case_to_failed():
    store, application_id, outcome = _failed_case()
    assert outcome.succeeded is False
    assert outcome.failure_reason == "drafting produced no memo"
    assert store.get_application(application_id).state is CaseState.FAILED


def test_failed_is_distinguishable_from_evaluated():
    """A never-triggered case is NOT the same as a broken one."""
    failed_store, failed_id, _ = _failed_case()

    untriggered_store = fx.InMemoryCaseStore()
    pipeline = CasePipeline(
        untriggered_store, fx.drafting_success_double(), fx.recommendation_id_factory
    )
    application_id, raw = fx.clean_case()
    pipeline.submit(application_id, raw)

    assert failed_store.get_application(failed_id).state is CaseState.FAILED
    assert untriggered_store.get_application(application_id).state is CaseState.EVALUATED


def test_failed_is_terminal():
    assert CaseState.FAILED in TERMINAL_STATES


def test_the_failure_outcome_still_carries_the_routing_decision():
    """The outcome is informative even on failure — the mode was computed before drafting."""
    _store, _application_id, outcome = _failed_case()
    assert outcome.thinking_mode is not None
    assert outcome.memo is None
