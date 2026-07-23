"""PromptBuilder — the memo prompt, scoped to MemoAgentInput (GROUND-1 / ADVISORY-1).

The prompt is built **only** from the handed ``MemoAgentInput`` clean artifacts —
**no tool fetch / no MCP** re-derives what fired (retrieval-miss guard). The
system template enforces **advisory-only** language ("recommendation", never
"decision") and instructs the model that the recommendation is fixed/read-only
and that it may cite ONLY rules present in the handed report.

Demographic identifiers (name, city, gender) are **deliberately excluded** from
the prompt — bias-free by design; the memo prose never sees them.
"""
from __future__ import annotations

from backend.memo_agent_core.schemas import MemoAgentInput

_SYSTEM_PROMPT = (
    "You are an underwriting decision-memo assistant. Draft a concise, audit-ready "
    "ADVISORY memo for a human underwriter. Always use the word 'recommendation'; "
    "never call it a 'decision' — the decision is the underwriter's to make. You "
    "MUST NOT change, override, or state a different recommendation than the one "
    "provided below; it is fixed and read-only. Cite ONLY rule ids that appear in "
    "the RULE REPORT below; never invent or infer a rule that is not listed."
)


class PromptBuilder:
    """Builds the LLM prompt from ``MemoAgentInput`` and nothing else."""

    system_prompt = _SYSTEM_PROMPT

    def build(self, agent_input: MemoAgentInput) -> str:
        report = agent_input.rule_report
        profile = agent_input.applicant_profile

        lines = [_SYSTEM_PROMPT, ""]
        lines.append(f"RECOMMENDATION (read-only): {agent_input.recommendation.value}")
        lines.append(f"CONFIDENCE (read-only): {agent_input.confidence.value}")
        lines.append("")
        lines.append("RULE REPORT (the only citable rules):")
        for result in report.rule_results:
            lines.append(f"- {result.rule_id} [{result.status.value}] {result.message}")
        lines.append("")
        lines.append("APPLICANT FACTS (non-demographic):")
        lines.append(f"- age_years: {profile.age_years_derived}")
        lines.append(f"- verifiable_income_annual: {profile.verifiable_income_annual}")
        lines.append(f"- requested_cover_amount: {profile.requested_cover_amount}")
        if profile.bmi_derived is not None:
            lines.append(f"- bmi: {profile.bmi_derived}")
        # Demographics (name / city / gender) are intentionally omitted (bias-free).
        return "\n".join(lines)
