"""NFR-CASE-STATE-1 + NFR-CASE-STATE-2 (P-CASE-4) — the five-state model. BR-CASE-1/2.

⚑ STATE-2's exhaustiveness is **derived, never hand-listed**: the illegal set is
``product(CaseState, CaseState) - LEGAL_TRANSITIONS``, so a newly added state appears in it
**with no test edit**. Named landmarks are asserted **in addition**, via the UNSPLITTABLE
``illegal_transition_cases()`` collection.
"""
from __future__ import annotations

import itertools

import pytest

from backend.case_lifecycle.states import (
    LEGAL_TRANSITIONS,
    TERMINAL_STATES,
    CaseState,
    IllegalTransition,
    assert_legal,
    is_legal,
)
from backend.case_lifecycle.tests import fixtures as fx


def test_the_lifecycle_states_plus_the_two_internal_states_exist():
    """⚑ RENAMED by register #19's fix — the old name said "the five states", which stopped
    being true when ``COMMITTING`` was added. ``FAILED`` and ``COMMITTING`` are both INTERNAL:
    neither has a wire representation (register #14)."""
    assert {s.value for s in CaseState} == {
        "submitted", "profiled", "evaluated", "drafted", "committing", "committed", "failed",
    }


def test_every_legal_transition_is_accepted():
    for src, dst in LEGAL_TRANSITIONS:
        assert_legal(src, dst)          # must not raise
        assert is_legal(src, dst) is True


def test_the_legal_table_is_the_expected_happy_path_plus_failure():
    """⚑ UPDATED by register #19's fix: the commit is now TWO-STEP.

    ``DRAFTED -> COMMITTED`` is **GONE** — it is replaced by the claim pair
    ``DRAFTED -> COMMITTING -> COMMITTED`` plus the recovery edge
    ``COMMITTING -> DRAFTED``.
    """
    assert LEGAL_TRANSITIONS == frozenset({
        (CaseState.SUBMITTED, CaseState.PROFILED),
        (CaseState.PROFILED, CaseState.EVALUATED),
        (CaseState.EVALUATED, CaseState.DRAFTED),
        (CaseState.EVALUATED, CaseState.FAILED),
        (CaseState.DRAFTED, CaseState.COMMITTING),      # the CAS claim
        (CaseState.COMMITTING, CaseState.COMMITTED),    # finalize
        (CaseState.COMMITTING, CaseState.DRAFTED),      # recovery (release the claim)
    })


# --- register #19: the two-step commit, asserted STRUCTURALLY ------------------------------


def test_the_direct_drafted_to_committed_edge_is_gone():
    """⚑ THE LOAD-BEARING ASSERTION of register #19's fix.

    The one-step transition the fix REPLACES must be **structurally unexpressible**. If this
    edge came back, a caller could commit without ever taking the claim — and the CAS that
    eliminates duplicate ``AuditRecord``s would be bypassable.
    """
    assert (CaseState.DRAFTED, CaseState.COMMITTED) not in LEGAL_TRANSITIONS
    assert is_legal(CaseState.DRAFTED, CaseState.COMMITTED) is False
    with pytest.raises(IllegalTransition):
        assert_legal(CaseState.DRAFTED, CaseState.COMMITTED)


def test_committing_is_not_terminal():
    assert CaseState.COMMITTING not in TERMINAL_STATES
    assert any(src is CaseState.COMMITTING for src, _dst in LEGAL_TRANSITIONS)


def test_committed_is_reachable_only_from_committing():
    """⚑ Derived from the ONE table — the guarantee is structural, not conventional."""
    predecessors = {src for src, dst in LEGAL_TRANSITIONS if dst is CaseState.COMMITTED}
    assert predecessors == {CaseState.COMMITTING}


def test_committing_is_reachable_only_from_drafted():
    predecessors = {src for src, dst in LEGAL_TRANSITIONS if dst is CaseState.COMMITTING}
    assert predecessors == {CaseState.DRAFTED}


def test_the_only_exits_from_committing_are_committed_and_drafted():
    successors = {dst for src, dst in LEGAL_TRANSITIONS if src is CaseState.COMMITTING}
    assert successors == {CaseState.COMMITTED, CaseState.DRAFTED}


def test_terminal_states_is_unchanged():
    """⚑ A1(i), PINNED AS A TEST RATHER THAN A MEMORY.

    Register #19's fix adds ``COMMITTING`` but changes ``TERMINAL_STATES`` **not at all**.
    ``FAILED`` remains terminal — FAILED-1 and COMMITBOUND-1(c) are untouched by this fix.
    """
    assert TERMINAL_STATES == frozenset({CaseState.COMMITTED, CaseState.FAILED})


# --- STATE-2: the DERIVED exhaustiveness sweep ------------------------------------------


def test_every_illegal_transition_in_the_full_cross_product_is_rejected():
    """⚑ The illegal set is the COMPLEMENT — nothing to forget, nothing to drift."""
    illegal = set(itertools.product(CaseState, CaseState)) - LEGAL_TRANSITIONS
    assert illegal, "the cross-product complement must be non-empty (non-vacuity)"
    for src, dst in illegal:
        assert is_legal(src, dst) is False
        with pytest.raises(IllegalTransition):
            assert_legal(src, dst)


def test_the_derived_illegal_set_covers_the_whole_cross_product():
    illegal = set(itertools.product(CaseState, CaseState)) - LEGAL_TRANSITIONS
    assert len(illegal) + len(LEGAL_TRANSITIONS) == len(CaseState) ** 2


def test_named_landmark_rejections_from_the_unsplittable_collection():
    """The readable landmarks, asserted IN ADDITION to the derived sweep."""
    landmarks = fx.illegal_transition_cases()
    assert len(landmarks) == 6            # returned together; cannot be trimmed one at a time
    for src, dst in landmarks:
        with pytest.raises(IllegalTransition):
            assert_legal(src, dst)


def test_no_transition_leaves_a_terminal_state():
    for terminal in TERMINAL_STATES:
        for dst in CaseState:
            assert is_legal(terminal, dst) is False


def test_the_illegal_transition_error_names_both_states():
    with pytest.raises(IllegalTransition) as excinfo:
        assert_legal(CaseState.SUBMITTED, CaseState.COMMITTED)
    assert excinfo.value.src is CaseState.SUBMITTED
    assert excinfo.value.dst is CaseState.COMMITTED
