"""llm-judge data contracts — the frozen FD shapes (``domain-entities.md``).

C-JUDGE-1. Frozen dataclasses (immutable once built — CON-DET-1 discipline).

**Header comment — DOCUMENTATION ONLY, never enforcement.** Every property below is
independently enforced by a C-JUDGE-5 scan carrying a detector self-test:
  * holds no LLM, builds no prompt, opens no socket;
  * edits no frozen unit (frozen shapes are imported READ-ONLY);
  * declares NO verdict;
  * reaches no network / Node / npx at tier-U.

**ADVISORY-1 / NOVERDICT-1 (P-JUDGE-10).** No type here declares a ``Recommendation``-typed
or verdict-typed field, so *"the judge changed the recommendation"* is **unrepresentable**,
not merely forbidden. The judge scores PROSE. A ``Recommendation`` reaches this unit only
INSIDE the frozen ``DecisionMemo`` under judgment — judge INPUT, never judge OUTPUT.

**P-JUDGE-1.** ``EvalRunResult.exempt_count`` is a REQUIRED field: the Ollama exemption is
proven BY PRESENCE (a counted witness), never by absence.

**Bias-free (NODEMO-1).** ``JudgedSample`` carries ``memo`` + ``rule_report`` + ``provider``
ONLY — there is deliberately NO ``ApplicantProfile`` field, so no demographic value can
structurally enter a judged sample.

Reference-not-own: ``DecisionMemo`` (memo-agent-core) and ``RuleResultReport``
(rules-engine) are imported **unchanged, read-only**.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from backend.memo_agent_core.schemas import DecisionMemo
from backend.rules_engine.report_schema import RuleResultReport


class ProviderScopeTag(str, Enum):
    """The FR-PROV-GATE-2 boundary — the SINGLE place in-gate vs exempt is represented.

    Ollama is exempt from **memo-quality gates ONLY**; it still holds every
    decision-level gate (``temperature=0``, CON-BR2-TYPE), which frozen U19 asserts
    directly (``memo_extensions/tests/test_provgate.py``). *Exempt never means "not covered
    by tests"* — the Ollama adapter IS unit-tested offline by frozen U19.
    """
    GEMINI = "gemini"    # IN-GATE (primary)
    CLAUDE = "claude"    # IN-GATE (secondary, tested)
    OLLAMA = "ollama"    # EXEMPT from memo-quality gates only


class EvalTier(str, Enum):
    """``unit`` = the seeded fixture set (here). ``live`` = the deferred authorized run
    (``JUDGE-EVAL-DEFERRED``; tier-B NOT authorized, NOT required for U22's completion)."""
    UNIT = "unit"
    LIVE = "live"


#: EXEMPTSCOPE-1's explicit reason tag — names *memo-quality* as the exemption's SCOPE,
#: so an exempt record can never be read as "not covered by tests".
EXEMPT_REASON_MEMO_QUALITY = (
    "exempt from memo-quality gates only; holds all decision-level gates"
)


@dataclass(frozen=True)
class RubricDimension:
    """One scored dimension. ``description`` is judge-facing criterion text —
    advisory-only wording, no demographic reference."""
    dimension_id: str
    description: str
    weight: int = 1


@dataclass(frozen=True)
class GroundednessRubric:
    """The declarative rubric. ``dimensions`` is an ORDERED tuple — the declared order
    IS the deterministic report order (P-JUDGE-8)."""
    rubric_id: str
    dimensions: tuple[RubricDimension, ...]
    threshold: int = 4    # AC-6 / QA-4 — ">= 4/5"
    scale_max: int = 5


@dataclass(frozen=True)
class JudgedSample:
    """One memo submitted for scoring.

    Only ``memo.narrative_prose`` (the ``L`` region) is judged; the ``D`` / ``RO`` / ``M``
    regions are deterministic or injected and are NEVER scored — scoring them would
    re-open CON-BR2-TYPE.
    """
    sample_id: str
    memo: DecisionMemo                # frozen U4 shape — imported READ-ONLY
    rule_report: RuleResultReport     # frozen grounding source — imported READ-ONLY
    provider: ProviderScopeTag


@dataclass(frozen=True)
class DimensionScore:
    """``score`` is on the 1..5 integer scale AC-6's '>= 4/5' presupposes."""
    dimension_id: str
    score: int
    justification: str


@dataclass(frozen=True)
class SampleScore:
    """One sample's result.

    For an EXEMPT sample ``dimension_scores`` is empty and ``aggregate`` / ``passed`` are
    ``None`` — deliberately NOT ``0.0`` / ``False``, which would read as *"failed"* rather
    than *"not scored"*. ``exempt_reason`` then names the exemption's scope (EXEMPTSCOPE-1).
    """
    sample_id: str
    provider: ProviderScopeTag
    dimension_scores: tuple[DimensionScore, ...]
    aggregate: Optional[float]
    passed: Optional[bool]
    in_gate: bool
    exempt_reason: Optional[str] = None


@dataclass(frozen=True)
class EvalRunResult:
    """The run report — the ONLY thing U22 emits (Q6-A: no Prometheus metric, no panel).

    ``sample_scores`` holds ALL samples in deterministic input order, INCLUDING exempt
    ones. ``exempt_count`` is the load-bearing POSITIVE WITNESS (P-JUDGE-1).
    """
    rubric_id: str
    sample_scores: tuple[SampleScore, ...]
    scored_count: int
    exempt_count: int
    aggregate_score: float
    gate_passed: bool
    tier: EvalTier = EvalTier.UNIT
    dimension_ids: tuple[str, ...] = field(default_factory=tuple)
