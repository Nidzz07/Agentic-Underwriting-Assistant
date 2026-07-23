"""NFR-JUDGE-DISCLOSE-1 (P-JUDGE-7) — the token checklist. BR-JUDGE-6 / CG-JUDGE-GAP-1.

A rule whose entire content is *"this is honestly not implemented"* has NO behaviour to
exercise, so it cannot have executable teeth. The established precedent is ``deploy-config``'s
**DOC-1**: a TOKEN-SET checklist matching tokens, not headings or prose, with a detector
self-test. Labelling this governance/documentation-presence is HONEST, not a gap.

⚑ ANTI-CONFLATION (Req-Fold-3). DISCLOSE-1 and CLIDEFER-1 both *"honestly disclose an
undelivered thing"*, so their checks must not become interchangeable. They key on DIFFERENT
fields — DISCLOSE-1 on ``name`` + ``owner``, CLIDEFER-1 on ``discharge_criteria`` — and the
self-tests below prove IN BOTH DIRECTIONS that one item's presence does NOT mask the other's
removal.
"""
from __future__ import annotations

from backend.llm_judge.engine import (
    DEFERRED_REGISTER,
    FEWSHOT_ANCHOR_UNIMPLEMENTED,
    PROMPTFOO_CLI_DEFERRED,
    register_item,
)


def test_the_unimplemented_generation_half_is_disclosed_by_name():
    item = register_item("FEWSHOT-ANCHOR-UNIMPLEMENTED")
    assert item is FEWSHOT_ANCHOR_UNIMPLEMENTED
    assert item.name == "FEWSHOT-ANCHOR-UNIMPLEMENTED"


def test_the_disclosure_carries_its_u4_owner_attribution():
    item = register_item("FEWSHOT-ANCHOR-UNIMPLEMENTED")
    assert "memo-agent-core" in item.owner
    assert "U4" in item.owner


def test_the_disclosure_carries_its_rationale():
    rationale = FEWSHOT_ANCHOR_UNIMPLEMENTED.rationale.lower()
    assert "zero hits" in rationale          # the measured evidence
    assert "promptbuilder" in rationale      # why it cannot be done here
    assert "frozen" in rationale


def test_u22_claims_no_discharge_of_the_generation_half():
    """The negative assertion - STRUCTURAL (``discharged is False``), not prose-matching."""
    assert FEWSHOT_ANCHOR_UNIMPLEMENTED.discharged is False
    assert "claims NO discharge" in FEWSHOT_ANCHOR_UNIMPLEMENTED.rationale


def test_all_three_register_items_are_present_and_none_discharged():
    names = {item.name for item in DEFERRED_REGISTER}
    assert names == {
        "PROMPTFOO-CLI-DEFERRED",
        "JUDGE-EVAL-DEFERRED",
        "FEWSHOT-ANCHOR-UNIMPLEMENTED",
    }
    assert all(item.discharged is False for item in DEFERRED_REGISTER)


# --- detector self-tests: the token checklist cannot pass vacuously ---------------------


def test_detector_removing_the_disclosure_token_fails_the_check():
    doctored = tuple(
        i for i in DEFERRED_REGISTER if i.name != "FEWSHOT-ANCHOR-UNIMPLEMENTED"
    )
    assert register_item("FEWSHOT-ANCHOR-UNIMPLEMENTED", doctored) is None


def test_anti_conflation_clidefers_tokens_do_not_mask_a_missing_disclose_token():
    """⚑ Direction 1: CLIDEFER-1's item present, DISCLOSE-1's removed -> STILL flagged."""
    doctored = (PROMPTFOO_CLI_DEFERRED,)
    assert register_item("PROMPTFOO-CLI-DEFERRED", doctored) is not None  # present
    assert register_item("FEWSHOT-ANCHOR-UNIMPLEMENTED", doctored) is None  # not masked


def test_anti_conflation_disclose_tokens_do_not_mask_a_missing_clidefer_token():
    """⚑ Direction 2: the converse holds too - the checks are non-interchangeable."""
    doctored = (FEWSHOT_ANCHOR_UNIMPLEMENTED,)
    assert register_item("FEWSHOT-ANCHOR-UNIMPLEMENTED", doctored) is not None
    assert register_item("PROMPTFOO-CLI-DEFERRED", doctored) is None


def test_the_two_items_key_on_different_fields():
    """DISCLOSE-1 keys on name+owner; CLIDEFER-1 keys on discharge_criteria."""
    assert FEWSHOT_ANCHOR_UNIMPLEMENTED.owner != PROMPTFOO_CLI_DEFERRED.owner
    assert set(FEWSHOT_ANCHOR_UNIMPLEMENTED.discharge_criteria).isdisjoint(
        set(PROMPTFOO_CLI_DEFERRED.discharge_criteria)
    )
    # the generation half is NOT U22's to discharge; the CLI half IS
    assert "memo-agent-core" in FEWSHOT_ANCHOR_UNIMPLEMENTED.owner
    assert "llm-judge" in PROMPTFOO_CLI_DEFERRED.owner
