"""Register #35 ``OFFLINE-DOUBLE-CITES-THE-RECOMMENDATION`` — the citation invariant.

⛔ **The invariant**: whatever ``first_cited_rule_id`` pulls out of a prompt must be a rule id
**from the handed report**, or ``""`` when the report lists none. Anything else is a fabricated
citation, which ``CitationValidator`` then rejects — so the memo is blocked and the case lands in
``FAILED``.

⚑ **The absence of exactly this test is why #35 shipped.** The extraction searched the **whole**
prompt, and ``PromptBuilder`` writes ``RECOMMENDATION (read-only): <value>`` **above** the rule
report. ``Recommendation.DECLINE_RECOMMEND.value`` is ``"DECLINE-RECOMMEND"`` — which the rule-id
regex matches — so ⛔ **every DECLINE-RECOMMEND case extracted the recommendation itself as its
citation.** ⚠️ ``APPROVE`` and ``REFER`` passed only because their values happen to contain no
hyphen: **luck, not correctness**, which is why this test is parametrized over **every** value
rather than the one that broke.

⛔ **The EMPTY-rule-report case is not padding.** It is the cell that exposes single-ended
anchoring: with the region bounded only at its start, the ``REQUIRED OUTPUT FORMAT`` block that
X1 appends **after** the applicant facts would fall inside the search region, and its worked
example would be extracted as the citation. Bounding at **both** ends is what keeps that out —
and the ``EXAMPLE_RULE_ID`` placeholder (underscore, unmatchable by the regex) is the second,
independent defense.
"""
from __future__ import annotations

import pytest

from backend.app.offline_memo_double import first_cited_rule_id
from backend.memo_agent_core.prompt_builder import PromptBuilder
from backend.memo_agent_core.tests.fixtures.factories import make_input, make_report
from backend.rules_engine.report_schema import Recommendation

_RULE_IDS = ("R-AGE-1", "R-DTI-1")


def _prompt_for(*, recommendation: Recommendation, rule_ids=_RULE_IDS):
    report = make_report(rule_ids=rule_ids, recommendation=recommendation)
    agent_input = make_input(report=report)
    return PromptBuilder().build(agent_input), [r.rule_id for r in report.rule_results]


# --------------------------------------------------------------------------
# The invariant, over EVERY Recommendation value — not just the one that broke
# --------------------------------------------------------------------------
@pytest.mark.parametrize("recommendation", list(Recommendation))
def test_the_extracted_citation_is_always_a_rule_id_FROM_THE_REPORT(recommendation):
    prompt, citable = _prompt_for(recommendation=recommendation)

    extracted = first_cited_rule_id(prompt)

    assert extracted in citable, (
        f"{recommendation.value}: extracted {extracted!r}, which is not one of the citable "
        f"rule ids {citable} — a fabricated citation"
    )


# --------------------------------------------------------------------------
# ⛔ The empty-report cell — the one that exposes single-ended anchoring
# --------------------------------------------------------------------------
def test_an_EMPTY_rule_report_yields_no_citation_rather_than_something_else():
    """⚑ With no citable rules, ``""`` is the only honest answer: the draft is then legitimately
    blocked by ``CitationValidator`` instead of carrying an invented id. ⛔ This is also the cell
    that catches a worked example leaking in from further down the prompt."""
    prompt, citable = _prompt_for(recommendation=Recommendation.APPROVE, rule_ids=())
    assert citable == []  # the fixture really did hand over an empty report

    assert first_cited_rule_id(prompt) == ""


# --------------------------------------------------------------------------
# ⛔ The two marker guards (§6.3) — a prompt whose SHAPE is not the one this
# function was written against must yield "", never a guess
# --------------------------------------------------------------------------
def test_a_prompt_with_NO_rule_report_marker_yields_no_citation():
    """⚠️ If `PromptBuilder`'s section header is reworded, extraction must fail CLOSED — return
    `""` and let `CitationValidator` block the draft — rather than fall back to searching the
    whole prompt, which is exactly the #35 behaviour being removed."""
    prompt = (
        "RECOMMENDATION (read-only): DECLINE-RECOMMEND\n"
        "SOME OTHER SECTION:\n"
        "- R-AGE-1 [PASS] age within band\n"
        "APPLICANT FACTS (non-demographic):\n"
    )

    assert first_cited_rule_id(prompt) == ""


def test_a_prompt_with_NO_applicant_facts_marker_yields_no_citation():
    """⚑ The END guard is a separate branch from the START guard and fails for a separate reason:
    the region's start is known but its extent is not, so everything after the report — including
    a `REQUIRED OUTPUT FORMAT` block — would be in scope. ⛔ Unbounded is exactly what #35 was."""
    prompt = (
        "RECOMMENDATION (read-only): DECLINE-RECOMMEND\n"
        "RULE REPORT (the only citable rules):\n"
        "- R-AGE-1 [PASS] age within band\n"
    )

    assert first_cited_rule_id(prompt) == ""


# --------------------------------------------------------------------------
# ⚑ Step 6.4 — the two doubles must stay BEHAVIOURALLY EQUIVALENT
# --------------------------------------------------------------------------
@pytest.mark.parametrize("recommendation", list(Recommendation))
def test_the_seed_scripts_MIRROR_extracts_identically(recommendation):
    """⚠️ `backend/scripts/seed_demo_cases.py` carries a second copy of this double, deliberately
    (`offline_memo_double.py:28-32`): *"the two must stay behaviourally equivalent; if they drift,
    this one governs the request path."* ⛔ **Nothing but this test enforces that.** `backend/scripts/`
    is in no `--cov=` entry, so the mirror is **tested but not measured** — pre-existing and correct,
    not an omission."""
    from backend.scripts.seed_demo_cases import _first_cited_rule_id as mirror

    prompt, _ = _prompt_for(recommendation=recommendation)

    assert mirror(prompt) == first_cited_rule_id(prompt)


# --------------------------------------------------------------------------
# ⛔ (l) — the SECOND defense, asserted against the REAL regex.
#
# ⚑ This assertion lives on the APP side deliberately. It needs both the frozen
# unit's placeholder and this module's rule-id pattern, and a file inside
# `memo_agent_core/` may NOT import `backend.app` — the dependency arrow points
# one way, and `test_frozen_untouched.py` enforces it. The composition root
# importing a unit is the legal direction, so the cross-unit check belongs here.
# --------------------------------------------------------------------------
def test_the_worked_examples_placeholder_CANNOT_be_mistaken_for_a_rule_id():
    """⛔ The second, independent defense against #35. ⚑ Asserted against **the real pattern
    object**, not a copy of the regex, so the two cannot silently drift apart."""
    from backend.app.offline_memo_double import _RULE_ID_PATTERN
    from backend.memo_agent_core.prompt_builder import EXAMPLE_RULE_ID

    assert _RULE_ID_PATTERN.search(EXAMPLE_RULE_ID) is None, (
        f"{EXAMPLE_RULE_ID!r} matches the rule-id pattern and would be cited as a real rule"
    )


def test_the_placeholder_is_IN_the_prompt_yet_still_not_extracted():
    """⛔ **Both defenses exercised together, which is the point of staging #35's fix before X1.**
    The worked example really is in the prompt; the extractor really does not pick it up — and it
    would not even if the anchoring were removed, because of the underscore. ⚠️ Defense one
    (bounding) and defense two (the underscore) each suffice alone; Q2 required exactly that."""
    from backend.memo_agent_core.prompt_builder import EXAMPLE_RULE_ID

    prompt, citable = _prompt_for(recommendation=Recommendation.DECLINE_RECOMMEND)

    assert EXAMPLE_RULE_ID in prompt, "the worked example should be present in the prompt"
    assert first_cited_rule_id(prompt) in citable
