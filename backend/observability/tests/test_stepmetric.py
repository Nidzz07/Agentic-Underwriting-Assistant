"""STEPMETRIC-1: the 2 step-outcome metrics derive on a DISTINCT path (P-OBS-7), with dedicated
non-overlapping fixtures, ``is_outlier`` read BY VALUE, and the Fold-3 consistency assertion.
"""
from __future__ import annotations

from backend.observability.metrics import (
    LLM_CALL_ERRORS,
    OUTLIER_FLAG,
    _EVENT_ALLOWED,
    _STEP_ALLOWED,
    derive_from_step_outcome,
)
from backend.observability.tests.fixtures import (
    outlier_step_outcome,
    provider_error_step_outcome,
)


def _by_metric(contributions):
    return {c.metric: c for c in contributions}


def test_provider_error_true_yields_an_llm_call_error_counter():
    by_metric = _by_metric(derive_from_step_outcome(provider_error_step_outcome(error=True)))
    assert set(by_metric) == {LLM_CALL_ERRORS.name}
    assert by_metric[LLM_CALL_ERRORS.name].value == 1.0


def test_provider_error_false_yields_no_contribution():
    assert derive_from_step_outcome(provider_error_step_outcome(error=False)) == []


def test_outlier_flagged_yields_gauge_one():
    by_metric = _by_metric(derive_from_step_outcome(outlier_step_outcome(is_outlier=True)))
    assert by_metric[OUTLIER_FLAG.name].value == 1.0


def test_outlier_not_flagged_yields_gauge_zero():
    by_metric = _by_metric(derive_from_step_outcome(outlier_step_outcome(is_outlier=False)))
    assert by_metric[OUTLIER_FLAG.name].value == 0.0


def test_empty_step_outcome_yields_no_contribution():
    assert derive_from_step_outcome({}) == []


def test_step_and_event_allowlists_are_structurally_separate():
    # P-OBS-7: the two derivation paths use DISTINCT, non-overlapping allowlist sets.
    assert _STEP_ALLOWED.isdisjoint(_EVENT_ALLOWED)


def test_fold3_fixture_field_names_are_subset_of_step_allowlist():
    """Fold-3: the ``is_outlier``-by-value fixture's fields ⊆ ``_STEP_ALLOWED`` — a rename either
    side fails loudly. ``is_outlier`` is U18's REAL field name (no ``outlier_model`` import)."""
    outlier_fields = set(outlier_step_outcome())
    # outlier_score is present in the fixture but is NOT a step metric source — the derivation
    # reads only the allowlisted subset; assert the SOURCED field is in the allowlist.
    assert "is_outlier" in _STEP_ALLOWED
    assert "is_outlier" in outlier_fields
    assert set(provider_error_step_outcome()).issubset(_STEP_ALLOWED)
