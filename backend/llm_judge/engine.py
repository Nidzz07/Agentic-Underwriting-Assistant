"""The injected ``RubricEngine`` seam + the disclosed deferral register (C-JUDGE-3).

**Header comment — DOCUMENTATION ONLY, never enforcement** (each property is scan-enforced
in C-JUDGE-5): holds no LLM; edits no frozen unit; declares no verdict; reaches no
network / Node / npx / promptfoo at tier-U.

**P-JUDGE-5 — a TWO-PART contract, and the second part is part of the pattern, not a
footnote:**

1. **Delivered.** ``RubricEngine`` is a ``runtime_checkable`` Protocol. At tier-U an OFFLINE
   deterministic fake (``tests/fixtures.DeclaredScoreEngine``) drives every test, and the
   seam is proven **satisfiable** (``isinstance(fake, RubricEngine)``) AND **non-vacuous**
   (``not isinstance(object(), RubricEngine)`` — the exact U19 assertion). **This module
   imports no promptfoo shim**, so the whole suite runs with no Node, no npx, no network,
   no telemetry and no key.
2. **Deliberately NOT delivered.** There is **no by-value interop replica** of the real
   engine's output shape. The precondition for such a replica — a FROZEN, ON-DISK shape to
   mirror — is **ABSENT** here: the promptfoo CLI is not present and its output shape is
   external, version-dependent and unpinned. A replica would attest to an ASSUMPTION and
   pass green while the real interop was broken. Real-shape interop is therefore the FIFTH
   named discharge criterion of ``PROMPTFOO-CLI-DEFERRED`` below.

**Q3-A.** ``DEFERRED_REGISTER`` gives DISCLOSE-1's checklist and CLIDEFER-1's
discharge-criteria a STRUCTURED subject: ``discharged is False`` is asserted as a field,
never by prose-matching. **Anti-conflation**: DISCLOSE-1 keys on ``name`` + ``owner``,
CLIDEFER-1 keys on ``discharge_criteria`` — and each detector self-test proves the other
item's presence does NOT mask its own removal.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from backend.llm_judge.schemas import DimensionScore, GroundednessRubric, JudgedSample


@runtime_checkable
class RubricEngine(Protocol):
    """The ONE substitutable point in the unit — *the act of judging*.

    tier-U binding: the offline deterministic fake. Real binding: deferred
    (``PROMPTFOO-CLI-DEFERRED``).
    """

    def score(
        self, sample: JudgedSample, rubric: GroundednessRubric
    ) -> list[DimensionScore]:
        ...  # pragma: no cover - Protocol stub


@dataclass(frozen=True)
class DeferredItem:
    """One openly-disclosed register item. ``discharged`` is a FIELD, not prose — so the
    negative assertion is structural."""
    name: str
    owner: str
    rationale: str
    discharge_criteria: tuple[str, ...]
    discharged: bool = False


PROMPTFOO_CLI_DEFERRED = DeferredItem(
    name="PROMPTFOO-CLI-DEFERRED",
    owner="llm-judge (U22)",
    rationale=(
        "promptfoo is already floored in requirements.txt, but the installed pip package is "
        "a thin Python shim around the Node.js promptfoo CLI, and the Node engine is ABSENT. "
        "Invoking it would npx-fetch an unpinned package over the network at run time and "
        "pulls posthog telemetry - both unacceptable at tier-U and in a BFSI system. The "
        "engine is therefore reached only through the injected RubricEngine Protocol, with "
        "an offline deterministic fake at tier-U."
    ),
    discharge_criteria=(
        "Node and npx present",
        "promptfoo CLI pinned to an exact version (no unpinned npx run-time fetch)",
        "telemetry opt-out configured (the posthog concern)",
        "the real adapter bound to the RubricEngine Protocol",
        "real-shape interop verified against the seeded fixtures",
    ),
)

JUDGE_EVAL_DEFERRED = DeferredItem(
    name="JUDGE-EVAL-DEFERRED",
    owner="llm-judge (U22)",
    rationale=(
        "U22 is built and verified at tier-U on a seeded fixture set, mirroring the "
        "outlier-model precedent. The real >=4/5 gate evaluated over the tier-B corpus is a "
        "separately-authorized run. tier-B is NOT authorized and is NOT required for U22's "
        "completion."
    ),
    discharge_criteria=(
        "tier-B corpus authorized and built",
        "live Gemini and Claude keys available via secrets-config",
        "the >=4/5 gate actually evaluated over real drafted memos",
        "PROMPTFOO-CLI-DEFERRED discharged FIRST (the one-way prerequisite)",
    ),
)

FEWSHOT_ANCHOR_UNIMPLEMENTED = DeferredItem(
    name="FEWSHOT-ANCHOR-UNIMPLEMENTED",
    owner="memo-agent-core (U4) or a future explicitly-authorized change",
    rationale=(
        "QA-4's anchoring clause has two halves. U22 delivers the SCORING half (the "
        "anchoring_consistency dimension). The GENERATION half - supplying few-shot "
        "exemplars to the memo prompt so the draft is anchored at draft time - is NOT "
        "implemented anywhere in the build (a repo-wide scan returns zero hits; U4's frozen "
        "PromptBuilder carries no reference memo and no exemplars). It CANNOT be implemented "
        "here: it would require passing exemplars INTO a frozen P1 unit's PromptBuilder. "
        "Disclosed by name, never silently dropped. U22 claims NO discharge of it."
    ),
    discharge_criteria=(
        "an explicit, separate authorization to edit the frozen memo-agent-core (U4)",
        "few-shot exemplars supplied to PromptBuilder at draft time",
    ),
)

#: The three openly-disclosed register items. NONE is discharged by U22.
DEFERRED_REGISTER: tuple[DeferredItem, ...] = (
    PROMPTFOO_CLI_DEFERRED,
    JUDGE_EVAL_DEFERRED,
    FEWSHOT_ANCHOR_UNIMPLEMENTED,
)


def register_item(name: str, register: tuple[DeferredItem, ...] = DEFERRED_REGISTER):
    """The named item, or ``None``. Takes ``register`` as a parameter so a detector
    self-test can pass a DOCTORED register and prove the check is non-vacuous."""
    for item in register:
        if item.name == name:
            return item
    return None
