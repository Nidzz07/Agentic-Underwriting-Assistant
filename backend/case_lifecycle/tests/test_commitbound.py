"""NFR-CASE-COMMITBOUND-1 (P-CASE-3) — LOAD-BEARING (full-highest). BR-CASE-13.

⚑ **ONE target with TWO halves, kept in ONE file** — the measured ``test_exempt.py`` precedent,
so the halves' complementarity is visible in one place while remaining distinct mechanisms.

**This is the assertion that U24 never finalizes a decision** — the single most consequential
invariant in the build. The CON-BR4 gate and the independent authz re-check run **inside the
frozen ``DecisionCommitService.commit()``**; U24 supplies **context only**.
"""
from __future__ import annotations

import pytest

from backend.audit_store.record_schema import CommitContext
from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.provider import (
    PendingCommitContextProvider,
    UnknownPendingRecommendation,
)
from backend.case_lifecycle.states import CaseState
from backend.case_lifecycle.tests import fixtures as fx
from backend.case_lifecycle.tests import structural as sg


def _drafted_case(seams=None):
    store = fx.InMemoryCaseStore()
    pipeline = CasePipeline(
        store, seams or fx.drafting_success_double(), fx.recommendation_id_factory
    )
    application_id, raw = fx.clean_case()
    pipeline.submit(application_id, raw)
    outcome = pipeline.draft(application_id)
    return store, pipeline, application_id, outcome


# --- (a) STRUCTURAL half -------------------------------------------------------------------


def test_no_u24_module_implements_a_gate_an_authz_check_or_an_audit_write():
    scanned = 0
    for path in sg.production_py_files():
        # ⚑ EXECUTABLE text only — a docstring that DOCUMENTS the prohibition must not be
        # mistaken for the prohibited thing itself (otherwise the scan flags its own disclosure).
        code = sg.executable_text(sg.parse(path))
        for forbidden in sg.FORBIDDEN_COMMIT_TOKENS:
            assert forbidden not in code, (path.name, forbidden)
        scanned += 1
    assert scanned >= len(sg.EXPECTED_PRODUCTION_MODULES)


def test_no_u24_module_imports_the_commit_service():
    for path in sg.production_py_files():
        code = sg.executable_text(sg.parse(path))
        assert "DecisionCommitService" not in code, path.name
        assert "commit_service" not in code, path.name


def test_detector_a_synthetic_gate_predicate_is_flagged():
    source = "def _gate(underwriter_id, action, reason):\n    return authorize(underwriter_id)\n"
    assert "authorize" in sg.called_names(sg.parse_source(source))


def test_detector_a_synthetic_audit_record_write_is_flagged():
    source = 'conn.execute("INSERT INTO audit_record VALUES (1)")\n'
    assert any("audit_record" in lit for lit in sg.string_constants(sg.parse_source(source)))


def test_detector_a_synthetic_rbac_commit_reference_is_flagged():
    assert "RBAC_COMMIT" in sg.FORBIDDEN_COMMIT_TOKENS
    source = 'PERMISSION = "RBAC_COMMIT"\n'
    assert any("RBAC_COMMIT" in lit for lit in sg.string_constants(sg.parse_source(source)))


# --- (b) BEHAVIOURAL half ------------------------------------------------------------------


def test_the_provider_returns_a_commit_context_and_nothing_more():
    store, _pipeline, application_id, _outcome = _drafted_case()
    provider = PendingCommitContextProvider(store)
    context = provider.get(fx.recommendation_id_factory(application_id))

    assert isinstance(context, CommitContext)
    assert context.memo_hash == "memo-hash-1"
    assert context.model_version == "model-test-v1"
    assert context.rulebook_version == "rb-test-v1"
    assert context.engine_version == "engine-test-v1"


def test_the_provider_rehydrates_the_two_rich_shapes_through_the_frozen_adapter():
    store, _pipeline, application_id, _outcome = _drafted_case()
    context = PendingCommitContextProvider(store).get(
        fx.recommendation_id_factory(application_id)
    )
    assert context.applicant_profile.application_id == application_id
    assert context.rule_results.rulebook_version == "rb-test-v1"


def test_the_provider_raises_for_an_unknown_recommendation_id():
    """R5 maps this to 404."""
    store, _pipeline, _application_id, _outcome = _drafted_case()
    with pytest.raises(UnknownPendingRecommendation):
        PendingCommitContextProvider(store).get("no-such-recommendation")


# --- (c) ⚑ POSITIVE: a failed case can NEVER reach the boundary ----------------------------


def test_a_failed_case_has_no_pending_recommendation():
    """⚑ The object R5 is keyed by never exists for a failed case."""
    store = fx.InMemoryCaseStore()
    pipeline = CasePipeline(
        store, fx.drafting_failure_double(), fx.recommendation_id_factory
    )
    application_id, raw = fx.clean_case()
    pipeline.submit(application_id, raw)
    outcome = pipeline.draft(application_id)

    assert outcome.succeeded is False
    assert store.get_application(application_id).state is CaseState.FAILED
    assert store.recommendation_for_application(application_id) is None


def test_the_provider_raises_for_a_failed_case():
    """The failed path and the commit path structurally do not intersect."""
    store = fx.InMemoryCaseStore()
    pipeline = CasePipeline(
        store, fx.drafting_failure_double(), fx.recommendation_id_factory
    )
    application_id, raw = fx.clean_case()
    pipeline.submit(application_id, raw)
    pipeline.draft(application_id)

    with pytest.raises(UnknownPendingRecommendation):
        PendingCommitContextProvider(store).get(
            fx.recommendation_id_factory(application_id)
        )


# --- (d) atomicity: the ONLY route by which (c) could open ---------------------------------


def test_the_drafted_transition_and_the_recommendation_share_one_atomic_block():
    store, _pipeline, application_id, outcome = _drafted_case()
    assert outcome.succeeded is True
    # submit() used one atomic block; draft()'s success path used exactly one more.
    assert store.atomic_entries == 2
    assert store.get_application(application_id).state is CaseState.DRAFTED
    assert store.get_recommendation(fx.recommendation_id_factory(application_id)) is not None
