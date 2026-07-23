"""memo-agent-core data contracts — the frozen FD shapes (``domain-entities.md``).

Pydantic v2 realization of the field-by-field FD. Value objects: ``frozen=True``
(immutable once built — CON-DET-1 discipline) + ``extra="forbid"`` (reject
unknown fields). No field or behaviour beyond the FD.

**CON-BR2-TYPE (type layer).** The model's structured output is ``MemoDraftOutput``,
which declares **only** ``narrative_prose`` + ``cited_rule_ids`` — it has **no**
``recommendation``/``confidence`` field, so "the LLM changed the recommendation"
is *unrepresentable*. ``DecisionMemo.recommendation``/``.confidence`` are injected
**read-only** by the ``MemoAssembler`` from the handed report; ``DecisionMemo`` is
``frozen`` (no setter).

**SEC-1-FORENSIC (SEC1-1).** ``MemoAgentInput`` carries **only** clean artifacts —
it has **no** ``original_span``/``SanitizationReport`` field, so no forensic span
can reach any LLM-bound payload.

Reference-not-own: ``ApplicantProfile`` (intake) and ``RuleResultReport`` /
``Recommendation`` / ``Confidence`` (rules-engine) are imported **unchanged**.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from backend.intake.schema import ApplicantProfile
from backend.rules_engine.report_schema import (
    Confidence,
    Recommendation,
    RuleResultReport,
)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class MissingInfoSource(str, Enum):
    """Where a missing-information gap came from (FD ``domain-entities.md §2.1``).

    The **declared order here IS the fixed source-major sort key** for the
    deterministic total order (MISSINGINFO-1): ``missing_document`` <
    ``unparseable_document`` < ``not_evaluated_rule`` < ``incomplete_flag``.
    """
    MISSING_DOCUMENT = "missing_document"
    UNPARSEABLE_DOCUMENT = "unparseable_document"
    NOT_EVALUATED_RULE = "not_evaluated_rule"
    INCOMPLETE_FLAG = "incomplete_flag"


class MissingInformationItem(_Frozen):
    """One deterministic missing-information gap (D region of the memo)."""
    source: MissingInfoSource
    detail: str


class CitationOutcome(str, Enum):
    VALID = "valid"
    CITATION_FAILURE = "citation_failure"


class CitationValidationResult(_Frozen):
    """The hallucination-guard output (frozen ``validate_citations``)."""
    all_valid: bool
    offending_cited_ids: list[str] = Field(default_factory=list)
    outcome: CitationOutcome


class ThinkingMode(str, Enum):
    """``route_borderline`` return type — a **named Phase-2 seam**
    (``memo-extensions``); NOT wired in Phase 1 (FR-MEMO-6/7)."""
    STANDARD = "standard"
    EXTENDED = "extended"


class MemoDraftOutput(_Frozen):
    """The LLM's structured output — the ONLY thing the model fills.

    **CON-BR2-TYPE**: declares **no** ``recommendation``/``confidence`` field
    (unrepresentable); ``extra="forbid"`` rejects any attempt to emit one.
    """
    narrative_prose: str
    cited_rule_ids: list[str] = Field(default_factory=list)


class MemoAgentInput(_Frozen):
    """What the agent is handed — clean, read-only artifacts ONLY (FD §4).

    **SEC1-1**: structurally NO ``original_span``/``SanitizationReport`` field.
    ``recommendation``/``confidence`` are the injected read-only values.
    """
    applicant_profile: ApplicantProfile   # clean facts (intake) — no forensic span
    rule_report: RuleResultReport         # the SOLE grounding source (rules-engine)
    recommendation: Recommendation        # injected read-only
    confidence: Confidence                # injected read-only


class DecisionMemo(_Frozen):
    """The three-region memo (FD §2). ``L`` LLM-authored · ``D`` deterministic ·
    ``RO`` injected read-only · ``M`` metadata. ``frozen`` → no setter (CON-BR2-TYPE)."""
    narrative_prose: str                                                              # L
    cited_rule_ids: list[str] = Field(default_factory=list)                           # L
    missing_information: list[MissingInformationItem] = Field(default_factory=list)   # D
    recommendation: Recommendation                                                    # RO
    confidence: Confidence                                                            # RO
    memo_hash: str                                                                    # M
    model_version: str                                                                # M
