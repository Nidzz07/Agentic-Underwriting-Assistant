"""NFR-CASE-ROUTE-1 (P-CASE-10) — routing is invoked, and the mode is re-derivable. BR-CASE-10.

⚑ `route_borderline` is NOT internal to the frozen orchestrator (measured: zero routing
references there). U24 calls the REAL frozen function explicitly and threads the resulting
`ThinkingMode` into the adapter.

⚑ `ThinkingMode` is deliberately NOT persisted: it is a pure deterministic function of
`(rule_report, outlier_signal)`, both of which ARE persisted — so it is EXACTLY re-derivable from
stored state. This file proves that re-derivation, which is what makes the non-persistence safe.
"""
from __future__ import annotations

from dataclasses import fields

from backend.audit_store.canon_adapter import CanonSerAdapter
from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.schemas import PendingRecommendation
from backend.case_lifecycle.tests import fixtures as fx
from backend.memo_agent_core.schemas import ThinkingMode
from backend.memo_extensions.borderline_router import route_borderline


def _run(seams):
    store = fx.InMemoryCaseStore()
    pipeline = CasePipeline(store, seams, fx.recommendation_id_factory)
    application_id, raw = fx.clean_case()
    pipeline.submit(application_id, raw)
    outcome = pipeline.draft(application_id)
    return store, application_id, outcome


def test_the_router_is_actually_invoked_with_the_real_arguments():
    """A spy records the real (rule_report, outlier) pair — not merely that a mode appeared."""
    seams = fx.drafting_success_double()
    _store, _application_id, _outcome = _run(seams)

    assert len(seams.route_args) == 1
    report, outlier = seams.route_args[0]
    assert report.rulebook_version == "rb-test-v1"
    assert outlier is None                      # this fixture supplies no outlier


def test_a_refer_report_routes_extended_and_the_adapter_receives_it():
    seams = fx.borderline_refer_case()
    _store, _application_id, outcome = _run(seams)

    assert outcome.thinking_mode is ThinkingMode.EXTENDED
    assert seams.thinking_modes == [ThinkingMode.EXTENDED]   # the adapter actually got it


def test_the_mode_is_re_derivable_from_stored_state_alone():
    """⚑ This is what makes NOT persisting ThinkingMode safe for reproducibility."""
    seams = fx.borderline_refer_case()
    store, application_id, outcome = _run(seams)

    stored = store.get_application(application_id)
    report = CanonSerAdapter.report_from_canonical(stored.rule_results_canonical)
    re_derived = route_borderline(report, None)

    assert re_derived is outcome.thinking_mode


def test_thinking_mode_is_not_a_persisted_column():
    names = {f.name for f in fields(PendingRecommendation)}
    assert "thinking_mode" not in names
    assert "thinking" not in " ".join(names)
