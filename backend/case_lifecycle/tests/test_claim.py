"""NFR-CASE-CLAIM-1 — the two-step commit claim, at tier-U. **Register #19.**

⚑ **WHAT THIS FILE PROVES, AND WHAT IT DELIBERATELY DOES NOT.**

It proves the **claim LOGIC**: which states may be claimed, which may not, that a claim is
one-shot, that finalize and release move the case where they say, and that a released claim is
re-claimable. Every one of those is a real, falsifiable property.

⛔ **It does NOT prove the CONCURRENCY guarantee.** ``InMemoryCaseStore`` is single-threaded, so
a tier-U test cannot interleave two transactions — the same vacuity trap ``store.py``'s header
already warns about for ``atomic()``. **A test here asserting "the second caller loses" proves
the STATE CHECK, not the compare-and-swap.** The database-level serialization that actually
eliminates duplicate ``AuditRecord``s is proven at tier-I, in
``test_claim_integration.py::CLAIM-CONCURRENT-1``, against real Postgres with two real
connections. This narrowing is stated here rather than left for a reader to assume.
"""
from __future__ import annotations

import pytest

from backend.case_lifecycle.states import CaseState, CommitClaimResult
from backend.case_lifecycle.tests import fixtures as fx


def _store_with(state: CaseState) -> tuple[fx.InMemoryCaseStore, str]:
    """A store holding one application in ``state`` plus its pending recommendation."""
    store = fx.InMemoryCaseStore()
    application_id = fx.APPLICATION_ID
    recommendation_id = fx.recommendation_id_factory(application_id)
    with store.atomic():
        store.put_application(fx.make_application(application_id, state))
        store.put_recommendation(fx.make_recommendation(recommendation_id, application_id))
    return store, recommendation_id


# --- claiming ------------------------------------------------------------------------------


def test_a_drafted_case_can_be_claimed():
    store, recommendation_id = _store_with(CaseState.DRAFTED)
    assert store.claim_for_commit(recommendation_id) is CommitClaimResult.WON
    assert store.get_application(fx.APPLICATION_ID).state is CaseState.COMMITTING


def test_a_claim_is_one_shot():
    """⚑ The second attempt LOSES — the duplicate-commit guard, at the logic level."""
    store, recommendation_id = _store_with(CaseState.DRAFTED)
    assert store.claim_for_commit(recommendation_id) is CommitClaimResult.WON
    assert store.claim_for_commit(recommendation_id) is CommitClaimResult.LOST
    assert store.get_application(fx.APPLICATION_ID).state is CaseState.COMMITTING


@pytest.mark.parametrize(
    "state",
    [CaseState.SUBMITTED, CaseState.PROFILED, CaseState.EVALUATED,
     CaseState.COMMITTING, CaseState.COMMITTED, CaseState.FAILED],
)
def test_only_a_drafted_case_can_be_claimed(state):
    """⚑ Every non-``drafted`` state LOSES — including ``failed``, which must never commit."""
    store, recommendation_id = _store_with(state)
    assert store.claim_for_commit(recommendation_id) is CommitClaimResult.LOST
    assert store.get_application(fx.APPLICATION_ID).state is state


def test_an_unknown_recommendation_id_is_not_found_not_lost():
    """⚑ The distinction that keeps R5's 404 correct instead of regressing it to a 409."""
    store, _recommendation_id = _store_with(CaseState.DRAFTED)
    assert store.claim_for_commit("no-such-recommendation") is CommitClaimResult.NOT_FOUND


def test_a_lost_claim_leaves_the_case_untouched():
    store, recommendation_id = _store_with(CaseState.COMMITTED)
    before = store.get_application(fx.APPLICATION_ID)
    assert store.claim_for_commit(recommendation_id) is CommitClaimResult.LOST
    assert store.get_application(fx.APPLICATION_ID) == before


# --- finalizing ----------------------------------------------------------------------------


def test_finalize_moves_a_claimed_case_to_committed():
    store, recommendation_id = _store_with(CaseState.DRAFTED)
    store.claim_for_commit(recommendation_id)
    store.finalize_commit(recommendation_id)
    assert store.get_application(fx.APPLICATION_ID).state is CaseState.COMMITTED


def test_a_committed_case_can_never_be_claimed_again():
    """⚑ ``COMMITTED`` is terminal — the end state of the whole guard."""
    store, recommendation_id = _store_with(CaseState.DRAFTED)
    store.claim_for_commit(recommendation_id)
    store.finalize_commit(recommendation_id)
    assert store.claim_for_commit(recommendation_id) is CommitClaimResult.LOST


# --- releasing (recovery) ------------------------------------------------------------------


def test_release_returns_a_claimed_case_to_drafted():
    store, recommendation_id = _store_with(CaseState.DRAFTED)
    store.claim_for_commit(recommendation_id)
    store.release_claim(recommendation_id)
    assert store.get_application(fx.APPLICATION_ID).state is CaseState.DRAFTED


def test_a_released_case_is_claimable_again():
    """⚑ THE POINT OF THE RECOVERY PATH — an ordinary rejection must not strand the case."""
    store, recommendation_id = _store_with(CaseState.DRAFTED)
    store.claim_for_commit(recommendation_id)
    store.release_claim(recommendation_id)
    assert store.claim_for_commit(recommendation_id) is CommitClaimResult.WON


def test_release_is_a_no_op_on_a_case_that_is_not_committing():
    """⚑ Recovery must be SAFE to call defensively — it must never corrupt a good state."""
    for state in (CaseState.DRAFTED, CaseState.COMMITTED, CaseState.FAILED):
        store, recommendation_id = _store_with(state)
        store.release_claim(recommendation_id)
        assert store.get_application(fx.APPLICATION_ID).state is state


def test_finalize_is_a_no_op_on_a_case_that_is_not_committing():
    for state in (CaseState.DRAFTED, CaseState.FAILED):
        store, recommendation_id = _store_with(state)
        store.finalize_commit(recommendation_id)
        assert store.get_application(fx.APPLICATION_ID).state is state


def test_finalize_and_release_on_an_unknown_id_do_not_raise():
    store, _recommendation_id = _store_with(CaseState.DRAFTED)
    store.finalize_commit("no-such-recommendation")
    store.release_claim("no-such-recommendation")


# --- the transaction discipline ------------------------------------------------------------


def test_each_claim_method_opens_its_own_transaction():
    """⚑ INT-FAITHFUL-1 depends on this: the CALLER never wraps these in ``atomic()``.

    ``backend/app/`` must open no transaction of its own, so each method must own one.
    """
    store, recommendation_id = _store_with(CaseState.DRAFTED)
    before = store.atomic_entries
    store.claim_for_commit(recommendation_id)
    store.finalize_commit(recommendation_id)
    assert store.atomic_entries == before + 2
