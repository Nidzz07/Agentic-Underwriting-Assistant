"""NFR-CASE-EAGER-1 (P-CASE-5) — eager, all-or-nothing advance. BR-CASE-3.

The `submitted -> profiled -> evaluated` advance runs inside ONE `store.atomic()`, and all three
steps are LLM-FREE. A mid-way fault leaves NO partial row.

⚑ This assertion is NON-VACUOUS only because the tier-U fake BUFFERS-AND-DISCARDS
(CASE-ND-Fold-1). With a single composite store method it would have been trivially true.
"""
from __future__ import annotations

import pytest

from backend.case_lifecycle.pipeline import CasePipeline
from backend.case_lifecycle.states import CaseState
from backend.case_lifecycle.tests import fixtures as fx


def test_submission_reaches_evaluated_in_one_transaction():
    store = fx.InMemoryCaseStore()
    pipeline = CasePipeline(store, fx.drafting_success_double(), fx.recommendation_id_factory)
    application_id, raw = fx.clean_case()

    application = pipeline.submit(application_id, raw)

    assert application.state is CaseState.EVALUATED
    assert store.atomic_entries == 1
    assert store.get_application(application_id).state is CaseState.EVALUATED


def test_both_canonical_payloads_and_hashes_are_persisted():
    store = fx.InMemoryCaseStore()
    pipeline = CasePipeline(store, fx.drafting_success_double(), fx.recommendation_id_factory)
    application_id, raw = fx.clean_case()
    pipeline.submit(application_id, raw)

    stored = store.get_application(application_id)
    assert stored.profile_canonical and stored.profile_content_hash
    assert stored.rule_results_canonical and stored.rule_results_content_hash
    assert stored.rulebook_version == "rb-test-v1"
    assert stored.engine_version == "engine-test-v1"


def test_a_fault_injected_mid_transaction_leaves_no_partial_row():
    """⚑ The all-or-nothing teeth — non-vacuous because the fake buffers and discards."""
    store = fx.InMemoryCaseStore(fail_on_put=True)
    pipeline = CasePipeline(store, fx.drafting_success_double(), fx.recommendation_id_factory)
    application_id, raw = fx.clean_case()

    with pytest.raises(fx.FaultInjected):
        pipeline.submit(application_id, raw)

    assert store.get_application(application_id) is None


def test_writes_outside_an_atomic_block_are_rejected():
    """The fake enforces the discipline, exactly as InMemoryAuditRepository does."""
    store = fx.InMemoryCaseStore()
    with pytest.raises(RuntimeError):
        store.put_application(fx.PendingApplication(
            application_id="x", state=CaseState.SUBMITTED,
            profile_canonical=b"", profile_content_hash="",
        ))


def test_the_eager_advance_is_llm_free():
    store = fx.InMemoryCaseStore()
    seams = fx.drafting_success_double()
    pipeline = CasePipeline(store, seams, fx.recommendation_id_factory)
    application_id, raw = fx.clean_case()
    pipeline.submit(application_id, raw)

    assert seams.calls == ["profile", "evaluate"]
    assert "draft_memo" not in seams.calls
