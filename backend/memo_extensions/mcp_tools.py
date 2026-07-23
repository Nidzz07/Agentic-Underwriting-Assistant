"""MCP tool surfaces + the append-only prompt composer (C-MEXT-2/3/4).

Two READ-ONLY tool surfaces (``services.md:46``) — ``RulebookTools`` and
``DecisionsTools`` — plus ``McpToolService``, which composes them into supplementary
context and performs the APPEND-ONLY prompt composition carrying the non-citable
marker (Q3-A). NFR-MEXT-MCPRO-1 / GROUND-1 / MISS-1 / BIAS-1.

**Header-comment deliverables (documentation only — NEVER enforcement):**
- Both surfaces are **read-only**: there is **no** ``commit*``/``write*``/``persist*``/
  ``update*`` member on either, and **no** ``DecisionCommitService`` / write-transport /
  session-write import (NFR-MEXT-MCPRO-1). The human approval gate is untouched and
  outside this unit.
- Both are **supplementary only**: **no citation may originate from a retrieval** — the
  handed ``RuleResultReport`` remains the SOLE citable grounding source (BR-MEXT-6);
  ``SUPPLEMENT_MARKER`` marks the block explicitly NON-CITABLE.
- Both are **demographic-free by construction** (CON-BR1 / BR-MEXT-9): ``describe_rules``
  takes **no applicant parameter**, and ``PrecedentSummary`` declares **no**
  ``full_name``/``gender``/``city``/``demographics`` field — a demographic is
  UNREPRESENTABLE in the return type.
- ``compose_prompt`` / ``supplementary_block`` are **PURE, non-persisting** members —
  they persist nothing, touch no transport/DB/session/record, mutate no argument, have no
  side effect. This module does **not** import ``memo_agent_core.prompt_builder`` (Fold-2):
  U4's ``build()`` output arrives as a ``str`` parameter and is **only appended to**;
  ``str`` immutability makes modification of it *unrepresentable* (Fold-1).
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Final, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:  # annotation-only frozen edges (audit_store / rules_engine are R edges)
    from backend.audit_store.record_schema import AuditRecord
    from backend.rules_engine.report_schema import RuleResultReport
    from backend.rules_engine.rulebook_schema import Rulebook


#: Explicit NON-CITABLE banner prepended to the supplementary block (GROUND-1c).
SUPPLEMENT_MARKER: Final[str] = (
    "\n\n===== SUPPLEMENTARY CONTEXT (NON-CITABLE) =====\n"
    "The material below is supplementary, human-readable context retrieved via MCP "
    "tools. It is NOT a grounding source. Cite ONLY rules present in the handed rule "
    "report; nothing in this section may be cited.\n"
)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class RuleDescription(_Frozen):
    """A read-only, human-readable rule description (rulebook-tools projection).

    A handler-side READ PROJECTION — NOT an LLM-output contract (CONTRACT-1 carve-out,
    Q5-A). Demographic-free by construction: sourced from the ``Rulebook``, which carries
    no applicant data at all.
    """

    rule_id: str
    category: str
    description: str
    irdai_ref: str = ""


class PrecedentSummary(_Frozen):
    """A demographic-free precedent projection (decisions-tools).

    The ``FeatureInputs`` analog (BR-MEXT-9 / NFR-MEXT-BIAS-1): declares **no**
    ``full_name``/``gender``/``city``/``demographics`` field, so a demographic is
    UNREPRESENTABLE in the return type. A handler-side READ PROJECTION — NOT an
    LLM-output contract (CONTRACT-1 carve-out, Q5-A).
    """

    recommendation: str
    confidence: str
    rulebook_version: str


class PrecedentQuery(_Frozen):
    """The precedent lookup criteria. Carries **no** demographic field (input-side
    by-construction, P-MEXT-6d) — a demographic cannot enter this surface."""

    limit: int = 5


class SupplementaryContext(_Frozen):
    """The composed supplementary context. ``retrieval_ok=False`` makes a retrieval
    miss OBSERVABLE (surfaced for U21's traces) rather than silent (NFR-MEXT-MISS-1)."""

    rule_descriptions: list[RuleDescription] = Field(default_factory=list)
    precedents: list[PrecedentSummary] = Field(default_factory=list)
    retrieval_ok: bool = True


@runtime_checkable
class DecisionRecordSource(Protocol):
    """Injected read-only seam over committed decision records (audit-store ``R``).

    The real binding reads audit-store at composition; a fake drives it at tier-U, so
    there is **no live DB** in U19's test path (the ``audit_store`` Docker-guard gap stays
    untouched and out of path).
    """

    def recent_records(self, query: PrecedentQuery) -> Sequence["AuditRecord"]: ...


class RulebookTools:
    """Read-only supplementary rule descriptions from the active ``Rulebook``
    (``rules-engine`` ``R``). Supplementary only — NEVER a citation source.
    ``describe_rules`` takes **no applicant parameter**, so it is demographic-free by
    construction. No write/mutate/commit member exists."""

    def __init__(self, rulebook: "Rulebook") -> None:
        self._rules_by_id = {rule.rule_id: rule for rule in rulebook.rules}

    def describe_rules(self, rule_ids: Sequence[str]) -> list[RuleDescription]:
        descriptions: list[RuleDescription] = []
        for rule_id in rule_ids:
            rule = self._rules_by_id.get(rule_id)
            if rule is None:
                continue
            descriptions.append(
                RuleDescription(
                    rule_id=rule.rule_id,
                    category=rule.category.value,
                    description=rule.rationale_message,
                    irdai_ref=rule.irdai_ref,
                )
            )
        return descriptions


class DecisionsTools:
    """Read-only demographic-free precedent from committed decision records
    (``audit-store`` ``R``) through an injected record-source seam. ``PrecedentSummary``
    carries no demographic field — demographic-free by construction. No write/mutate/
    commit member exists."""

    def __init__(self, record_source: DecisionRecordSource) -> None:
        self._record_source = record_source

    def recent_precedent(self, query: PrecedentQuery) -> list[PrecedentSummary]:
        summaries: list[PrecedentSummary] = []
        for record in self._record_source.recent_records(query):
            # Project ONLY the demographic-free fields; the applicant profile snapshot
            # (which carries full_name/gender/city) is deliberately never read.
            report = record.audit_tuple.rule_results
            summaries.append(
                PrecedentSummary(
                    recommendation=report.recommendation.value,
                    confidence=report.confidence.value,
                    rulebook_version=record.audit_tuple.rulebook_version,
                )
            )
        return summaries


class McpToolService:
    """Composes the two read-only handler surfaces into supplementary context and
    performs the APPEND-ONLY prompt composition carrying the non-citable marker (Q3-A).

    ``compose_prompt`` / ``supplementary_block`` are PURE (no persistence, no transport,
    no mutation, no side effect); this module never imports U4's ``PromptBuilder`` — the
    base prompt arrives as a ``str`` (Fold-2).
    """

    def __init__(self, rulebook_tools: RulebookTools, decisions_tools: DecisionsTools) -> None:
        self._rulebook_tools = rulebook_tools
        self._decisions_tools = decisions_tools

    def supplementary_context(
        self, rule_report: "RuleResultReport", query: PrecedentQuery | None = None
    ) -> SupplementaryContext:
        effective_query = query if query is not None else PrecedentQuery()
        try:
            descriptions = self._rulebook_tools.describe_rules(
                [result.rule_id for result in rule_report.rule_results]
            )
            precedents = self._decisions_tools.recent_precedent(effective_query)
        except Exception:
            # NFR-MEXT-MISS-1: a retrieval miss is NON-FATAL — degrade to the handed
            # report alone; observable via retrieval_ok=False, never raised.
            return SupplementaryContext(rule_descriptions=[], precedents=[], retrieval_ok=False)
        return SupplementaryContext(
            rule_descriptions=descriptions, precedents=precedents, retrieval_ok=True
        )

    def supplementary_block(self, context: SupplementaryContext) -> str:
        """Render the supplementary context to a plain string. Empty when there is
        nothing to add (a miss), so ``compose_prompt`` adds no content. PURE."""
        if not context.rule_descriptions and not context.precedents:
            return ""
        lines: list[str] = []
        for description in context.rule_descriptions:
            lines.append(
                f"- rule {description.rule_id} ({description.category}): {description.description}"
            )
        for precedent in context.precedents:
            lines.append(
                f"- precedent: {precedent.recommendation} ({precedent.confidence}) "
                f"under rulebook {precedent.rulebook_version}"
            )
        return "\n".join(lines)

    def compose_prompt(self, base_prompt: str, context: SupplementaryContext) -> str:
        """Append-only: ``base + marker + block``. U4's ``build()`` output (``base_prompt``)
        is never parsed, edited, reordered, or re-templated — only appended to. ``str`` is
        immutable, so ``base_prompt`` cannot be modified even by accident. A miss (empty
        block) adds NO content (MISS-1). PURE — no side effect, no persistence."""
        block = self.supplementary_block(context)
        if not block:
            return base_prompt
        return base_prompt + SUPPLEMENT_MARKER + block
