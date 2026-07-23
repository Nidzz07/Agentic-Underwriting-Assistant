"""The canonical groundedness rubric (C-JUDGE-1) — QA-4 / AC-2 / AC-6.

**Header comment — DOCUMENTATION ONLY, never enforcement** (each property is scan-enforced
in C-JUDGE-5): holds no LLM; edits no frozen unit; declares no verdict; no network at tier-U.

Two scored dimensions, both with teeth (standard depth, per the frozen FD):

* ``groundedness`` — the AC-2 *"zero unexplained recommendations"* criterion. It COMPLEMENTS
  U4's deterministic ``validate_citations`` (which answers *"is this rule id real?"*); the
  rubric answers *"is the prose actually grounded in the handed evidence?"*. It never
  replaces that guard.
* ``anchoring_consistency`` — QA-4's SCORING half. Per QA-4 this is *"not claimed
  bit-identical"*, so it scores STYLE/STRUCTURE adherence against one canonical reference
  memo, never textual identity.

**Advisory-only wording throughout**: every description says *recommendation*, never a bare
*decision*, and no description names a demographic attribute.

⛔ QA-4's GENERATION half (few-shot exemplars supplied to the memo prompt at draft time) is
**NOT implemented anywhere in the build and is NOT implemented here** — it is disclosed by
name as ``FEWSHOT-ANCHOR-UNIMPLEMENTED`` in ``engine.DEFERRED_REGISTER``, owned by
``memo-agent-core`` (U4). U22 claims NO discharge of it.
"""
from __future__ import annotations

from backend.llm_judge.schemas import GroundednessRubric, RubricDimension

DIMENSION_GROUNDEDNESS = "groundedness"
DIMENSION_ANCHORING_CONSISTENCY = "anchoring_consistency"

GROUNDEDNESS_DIMENSION = RubricDimension(
    dimension_id=DIMENSION_GROUNDEDNESS,
    description=(
        "Is every claim in the memo narrative supported by the handed rule report, and is "
        "every cited rule id actually present in it? Score the prose only; the "
        "recommendation itself is injected read-only and is never under review."
    ),
)

ANCHORING_CONSISTENCY_DIMENSION = RubricDimension(
    dimension_id=DIMENSION_ANCHORING_CONSISTENCY,
    description=(
        "Is the memo narrative's wording and structure consistent with the reference memo? "
        "Consistency is not bit-identity; score style and structure adherence only."
    ),
)

#: The canonical rubric. ``dimensions`` order IS the deterministic report order.
GROUNDEDNESS_RUBRIC = GroundednessRubric(
    rubric_id="groundedness-v1",
    dimensions=(GROUNDEDNESS_DIMENSION, ANCHORING_CONSISTENCY_DIMENSION),
    threshold=4,
    scale_max=5,
)
