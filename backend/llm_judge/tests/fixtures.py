"""Shared fixture substrate (C-JUDGE-4) — FIVE deliberately-separate NAMED FAMILIES (Q1-A).

One module per unit with purpose-built families that are NOT reused across targets whose
failure modes differ — the exact U18/U19 convention (U18: ``swap_pair`` bias-only,
``outlier_profile`` threshold-only).

  * ``in_gate_samples()``            -> INGATE-1            (gemini + claude)
  * ``exempt_witness_sample()``      -> EXEMPT-1 positive   (ollama; its OWN family)
  * ``degenerate_all_in_gate_set()`` -> EXEMPT-1 negative   (⚑ a GENUINELY SEPARATE builder)
  * ``anchoring_pair()``             -> ANCHOR-1            (close + divergent, TOGETHER)
  * ``reference_memo()``             -> ANCHOR-1 / NODEMO-1 (the ONE canonical exemplar)

⚑ **The anchoring pair is its OWN family, never overlapped onto the provider-tagged
samples** — so a provider-scope edit cannot silently move the anchoring baseline.

⚑ **``degenerate_all_in_gate_set()`` is NOT an alias of ``in_gate_samples()``** (Req-Fold-1).
Their invariants differ IN KIND and merely coincide today: ``in_gate_samples()`` promises
*"contains gemini and claude"* — which says NOTHING about an exempt sample being absent —
while the degenerate set promises *"contains NO exempt sample"*. Three mechanisms keep them
apart: DISTINCT ``sample_id`` prefixes (never identity-equal, asserted disjoint by
``test_exempt.py``), NO call into ``in_gate_samples()``, and a SELF-ASSERTING precondition so
the builder fails at construction rather than letting EXEMPT-1's guard go vacuous.

⚑ **The ``DeclaredScoreEngine`` fake lives HERE, not in production** (Q1-A) — matching the
measured convention of every sibling unit (U19's ``CapturingThinkingClient``, U21's
``RecordingTraceSink``). No unit in this build has a ``tests/fakes.py``. Because ``tests/``
is excluded from every production scan, CLIDEFER-1 still has a clean production set.

⚑ **Verdict tokens appear here BY NECESSITY** (CG-JUDGE-Fold-2): the frozen U4
``DecisionMemo.recommendation`` field is REQUIRED, so every memo fixture must carry one.
That is the memo UNDER JUDGMENT — judge INPUT, never judge OUTPUT — which is why ADVISORY-1's
token scan is scoped to PRODUCTION modules only.

**Demographic-free (NODEMO-1)**: no applicant identifier of any kind appears in any prose
below, mirroring U4's ``PromptBuilder``, which deliberately omits them. (The attribute names
themselves are deliberately not spelled out here — the NODEMO-1 scan reads this file, and it
matches on whole words.) **Advisory-only**: the prose says *recommendation*, never a bare
*decision*. No RNG, no wall-clock — every value is fixed.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Mapping, Sequence

from backend.llm_judge.schemas import (
    DimensionScore,
    GroundednessRubric,
    JudgedSample,
    ProviderScopeTag,
)
from backend.memo_agent_core.schemas import DecisionMemo
from backend.rules_engine.report_schema import (
    Confidence,
    Operator,
    OutcomeTier,
    Recommendation,
    RuleCategory,
    RuleResult,
    RuleResultReport,
    RuleStatus,
)

# --- distinct sample_id families (Q2-A) -------------------------------------------------
# Distinct literal PREFIXES per family, so no two families can ever be identity-equal.
# `test_exempt.py` asserts the id sets are DISJOINT - the separation is ASSERTED, not assumed.
INGATE_IDS = ("ingate-gemini-1", "ingate-claude-1")
EXEMPT_ID = "exempt-ollama-1"
DEGENERATE_IDS = ("degen-1", "degen-2")
ANCHOR_CLOSE_ID = "anchor-close-1"
ANCHOR_DIVERGENT_ID = "anchor-divergent-1"

_RULE_ID = "DTI-001"


def _rule_report() -> RuleResultReport:
    """The grounding source. Money values are ``Decimal`` (never ``float`` - CON-DET-1)."""
    return RuleResultReport(
        rule_results=[
            RuleResult(
                rule_id=_RULE_ID,
                category=RuleCategory.FINANCIAL_DTI,
                status=RuleStatus.FAIL,
                actual_value=Decimal("46"),
                operator=Operator.LTE,
                threshold=Decimal("40"),
                outcome_tier=OutcomeTier.REFER_TRIGGER,
                message="debt-to-income ratio above the permitted band",
            )
        ],
        recommendation=Recommendation.REFER,
        confidence=Confidence.MEDIUM,
        rulebook_version="rb-test-v1",
        content_hash="deadbeef",
        engine_version="engine-test-v1",
        refer_reasons=["debt-to-income ratio above the permitted band"],
    )


def _memo(narrative_prose: str, *, memo_hash: str) -> DecisionMemo:
    """A frozen U4 ``DecisionMemo``. Instantiating a frozen model is USING it, not modifying
    it (import-to-read != edit). ``recommendation``/``confidence`` are the injected
    read-only values carried by the memo under judgment."""
    return DecisionMemo(
        narrative_prose=narrative_prose,
        cited_rule_ids=[_RULE_ID],
        missing_information=[],
        recommendation=Recommendation.REFER,
        confidence=Confidence.MEDIUM,
        memo_hash=memo_hash,
        model_version="model-test-v1",
    )


_REFERENCE_PROSE = (
    "The applicant's debt-to-income ratio of 46 percent exceeds the permitted band of 40 "
    "percent, triggering rule DTI-001. On that evidence the recommendation is to refer this "
    "application to an underwriter for review. No other rule failed."
)

_CLOSE_PROSE = (
    "The applicant's debt-to-income ratio of 46 percent exceeds the permitted band of 40 "
    "percent, triggering rule DTI-001. On that evidence the recommendation is to refer this "
    "application for underwriter review. No further rule failed."
)

_DIVERGENT_PROSE = (
    "Numbers looked off so this one goes to a human. See DTI-001. Nothing else to add here "
    "and no further commentary is offered on the file."
)


def reference_memo() -> DecisionMemo:
    """The ONE canonical style/structure exemplar (Fold-3).

    Held by the judge as a SCORING COMPARISON TARGET - it is **never** a prompt input, so
    U4 never sees it and needs no change. It lives in U22's own fixture module and was NOT
    added to ``memo_agent_core/tests/`` (that would be a frozen-unit edit).
    Advisory-only wording; no demographic identifier.
    """
    return _memo(_REFERENCE_PROSE, memo_hash="ref-hash")


def _sample(sample_id: str, provider: ProviderScopeTag, prose: str) -> JudgedSample:
    return JudgedSample(
        sample_id=sample_id,
        memo=_memo(prose, memo_hash=f"hash-{sample_id}"),
        rule_report=_rule_report(),
        provider=provider,
    )


def in_gate_samples() -> list[JudgedSample]:
    """INGATE-1's positive family: the two in-gate provider-tagged samples.

    Invariant: *contains a gemini sample and a claude sample*. It promises NOTHING about
    whether an exempt sample is absent - that is a different contract entirely.
    """
    return [
        _sample(INGATE_IDS[0], ProviderScopeTag.GEMINI, _CLOSE_PROSE),
        _sample(INGATE_IDS[1], ProviderScopeTag.CLAUDE, _CLOSE_PROSE),
    ]


def exempt_witness_sample() -> JudgedSample:
    """EXEMPT-1's positive witness: the Ollama sample - its OWN family, so EXEMPT-1 can
    never be weakened by another target's edits."""
    return _sample(EXEMPT_ID, ProviderScopeTag.OLLAMA, _CLOSE_PROSE)


def exemption_composition() -> list[JudgedSample]:
    """The THREE-SAMPLE composition EXEMPT-1's positive teeth run over."""
    return [*in_gate_samples(), exempt_witness_sample()]


def degenerate_all_in_gate_set() -> list[JudgedSample]:
    """⚑ EXEMPT-1's NEGATIVE fixture - a GENUINELY SEPARATE builder (Req-Fold-1).

    Invariant: *contains NO exempt-tagged sample*, i.e. ``exempt_count == 0``. It does NOT
    call ``in_gate_samples()`` and its ids share no prefix with any other family.

    The ``assert`` below is the SELF-ASSERTING PRECONDITION: if a future edit ever
    introduced an exempt sample here, this builder FAILS AT CONSTRUCTION rather than
    silently making EXEMPT-1's degenerate-configuration guard vacuous.
    """
    samples = [
        _sample(DEGENERATE_IDS[0], ProviderScopeTag.GEMINI, _CLOSE_PROSE),
        _sample(DEGENERATE_IDS[1], ProviderScopeTag.CLAUDE, _CLOSE_PROSE),
    ]
    assert all(  # noqa: S101 - the builder's own precondition, deliberate
        s.provider is not ProviderScopeTag.OLLAMA for s in samples
    ), "degenerate_all_in_gate_set() must contain NO exempt-tagged sample"
    return samples


def anchoring_pair() -> tuple[JudgedSample, JudgedSample]:
    """⚑ ANCHOR-1's pair: ``(close, divergent)`` returned TOGETHER.

    One return value, so the pair is UNSPLITTABLE at the type level - a test cannot take
    one without the other. Its OWN family: never overlapped onto the provider-tagged
    samples, so a provider-scope edit cannot silently move the anchoring baseline.
    """
    close = _sample(ANCHOR_CLOSE_ID, ProviderScopeTag.GEMINI, _CLOSE_PROSE)
    divergent = _sample(ANCHOR_DIVERGENT_ID, ProviderScopeTag.GEMINI, _DIVERGENT_PROSE)
    return close, divergent


class DeclaredScoreEngine:
    """The tier-U offline deterministic fake - FIXTURE-DECLARED scores, exactly as the
    frozen FD defines the tier-U binding.

    ⚑ It does NOT compute similarity, and that is deliberate (Q2-A / P-JUDGE-6). Giving it
    a heuristic would make U22 own a scoring heuristic that is NOT what the real engine
    does, and a green ANCHOR-1 would then attest to U22's own heuristic rather than to the
    rubric - the same false-confidence failure mode already rejected for the by-value
    interop replica.

    No Node, no npx, no network, no telemetry, no key, no live LLM.
    """

    def __init__(
        self,
        declared: Mapping[str, Sequence[int]] | None = None,
        default: Sequence[int] = (4, 4),
    ) -> None:
        self._declared = dict(declared or {})
        self._default = tuple(default)
        self.calls: list[str] = []

    def score(
        self, sample: JudgedSample, rubric: GroundednessRubric
    ) -> list[DimensionScore]:
        self.calls.append(sample.sample_id)
        scores = self._declared.get(sample.sample_id, self._default)
        return [
            DimensionScore(
                dimension_id=dimension.dimension_id,
                score=score,
                justification=(
                    "declared fixture score for the "
                    f"{dimension.dimension_id} dimension; the recommendation itself is "
                    "not under review"
                ),
            )
            for dimension, score in zip(rubric.dimensions, scores)
        ]


def anchoring_engine() -> DeclaredScoreEngine:
    """The fake configured so the CLOSE sample outscores the DIVERGENT one."""
    return DeclaredScoreEngine(
        {ANCHOR_CLOSE_ID: (5, 5), ANCHOR_DIVERGENT_ID: (4, 2)}
    )
