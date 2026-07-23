"""NFR-CASE-PROJECT-1 (P-CASE-8) — the failed->pending wire projection, DISCLOSED. BR-CASE-6.

⚑ WIRE-1's `MemoView.status` is a CLOSED two-value discriminator. U24's internal `failed` state
has NO wire representation and projects to `"pending"` — the only legal value. The imprecision is
DISCLOSED as register #14, never hidden. WIRE-1's contract text is NOT amended.

The disclosure is verified by a DOC-1-style token checklist (the `llm-judge` DISCLOSE-1 lineage).
"""
from __future__ import annotations

import pytest

from backend.case_lifecycle import states as states_module
from backend.case_lifecycle.schemas import PendingApplication
from backend.case_lifecycle.states import CaseState, case_to_memo_view_state

_REGISTER_TOKENS = (
    "MEMOVIEW-FAILED-STATE-UNMODELLED",   # the register item's name
    "WIRE-1",                              # the owner surface
    "amendment",                           # the owner: a future authorized WIRE-1 amendment
)


def _case(state: CaseState) -> PendingApplication:
    return PendingApplication(
        application_id="case-x",
        state=state,
        profile_canonical=b"{}",
        profile_content_hash="h",
    )


@pytest.mark.parametrize(
    "state,expected",
    [
        (CaseState.SUBMITTED, "pending"),
        (CaseState.PROFILED, "pending"),
        (CaseState.EVALUATED, "pending"),
        (CaseState.DRAFTED, "ready"),
        (CaseState.FAILED, "pending"),     # ⚑ the disclosed projection
        (CaseState.COMMITTING, "pending"), # ⚑ register #19: mid-commit is NEVER "ready"
        (CaseState.COMMITTED, "pending"),
    ],
)
def test_every_state_projects_to_a_wire_valid_status(state, expected):
    assert case_to_memo_view_state(_case(state)) == expected


def test_only_two_wire_values_are_ever_emitted():
    emitted = {case_to_memo_view_state(_case(s)) for s in CaseState}
    assert emitted == {"ready", "pending"}      # WIRE-1's closed discriminator


def test_a_failed_case_is_reported_as_pending_not_as_a_third_status():
    assert case_to_memo_view_state(_case(CaseState.FAILED)) == "pending"


def test_the_projection_is_pure_and_does_no_io():
    case = _case(CaseState.DRAFTED)
    first = case_to_memo_view_state(case)
    second = case_to_memo_view_state(case)
    assert first == second == "ready"


# --- the DOC-1-style token checklist for register #14 ------------------------------------


def test_the_register_item_is_disclosed_by_name_with_its_owner_and_rationale():
    doc = states_module.__doc__ or ""
    for token in _REGISTER_TOKENS:
        assert token in doc, token


def test_no_u24_artifact_claims_wire_one_models_a_failed_state():
    doc = states_module.__doc__ or ""
    assert "no wire representation" in doc
    assert "claims NO discharge" in doc


def test_detector_removing_the_disclosure_token_fails_the_check():
    doctored = (states_module.__doc__ or "").replace("MEMOVIEW-FAILED-STATE-UNMODELLED", "")
    assert "MEMOVIEW-FAILED-STATE-UNMODELLED" not in doctored
