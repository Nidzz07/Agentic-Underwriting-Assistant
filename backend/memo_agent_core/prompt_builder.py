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

#: ⛔ **Register #33 change (l)** — the worked example's placeholder. ⚠️ **The UNDERSCORE is
#: load-bearing.** A regex sweep confirmed `EXAMPLE-RULE-ID`, `RULE-ID-HERE`, `XXX-000` and
#: `FILL-IN` all match the offline double's rule-id pattern
#: (``\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b``) and would be mis-cited as a real rule;
#: ``EXAMPLE_RULE_ID`` cannot match it, because the pattern requires a hyphen. ⚑ This is the
#: **second, independent** defense against #35 — the first is that
#: ``offline_memo_double.first_cited_rule_id`` bounds its search between the ``RULE REPORT`` and
#: ``APPLICANT FACTS`` markers, and this block is appended **after** both. **Neither defense
#: depends on the other** (Q2). ⛔ Do not "tidy" this to a hyphenated spelling.
EXAMPLE_RULE_ID = "EXAMPLE_RULE_ID"

_SYSTEM_PROMPT = (
    "You are an underwriting decision-memo assistant. Draft a concise, audit-ready "
    "ADVISORY memo for a human underwriter. Always use the word 'recommendation'; "
    "never call it a 'decision' — the decision is the underwriter's to make. You "
    "MUST NOT change, override, or state a different recommendation than the one "
    "provided below; it is fixed and read-only. Cite ONLY rule ids that appear in "
    "the RULE REPORT below; never invent or infer a rule that is not listed. "
    # ⛔ Register #33 change (j) — added AFTER the four constraints above, which are
    # unchanged. The model was never asked for XML at all, so it answered in Markdown
    # and the parse raised on the first live call.
    "Reply with ONLY the XML document specified under REQUIRED OUTPUT FORMAT at the end "
    "of this prompt: no preamble, no commentary, no Markdown, and no code fence around it."
)

#: ⛔ **Register #33 change (k)** — appended **LAST** by :meth:`PromptBuilder.build`, after the
#: applicant facts. ⚑ **The exact element names are the point.** ``GeminiAdapter._parse_xml``
#: reads ``narrative_prose`` and ``./cited_rule_ids/rule_id`` **by exact path**, so a well-formed
#: document using any other names ⛔ **parses to silence** — empty prose, no citations, and no
#: exception — surfacing downstream only as *"drafting produced no memo"*.
#: ⚠️ **This block is deliberately placed after the ``APPLICANT FACTS`` marker**, which is the
#: closing bound of the offline double's citation-extraction region (register #35). Moving it
#: above that marker would put its worked example back inside the search region.
_OUTPUT_FORMAT_BLOCK = (
    "REQUIRED OUTPUT FORMAT:\n"
    "Reply with exactly this XML document and nothing else:\n"
    "<memo>\n"
    "  <narrative_prose>Your advisory memo prose goes here.</narrative_prose>\n"
    "  <cited_rule_ids>\n"
    f"    <rule_id>{EXAMPLE_RULE_ID}</rule_id>\n"
    "  </cited_rule_ids>\n"
    "</memo>\n"
    "The element names above are exact; do not rename, translate or nest them differently. "
    f"Emit one <rule_id> element per rule you cite, replacing {EXAMPLE_RULE_ID} with an id "
    "copied verbatim from the RULE REPORT above. "
    f"{EXAMPLE_RULE_ID} is a placeholder and must never appear in your reply."
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
        # ⛔ Register #33 change (k) — LAST, after the APPLICANT FACTS section. The position is
        # load-bearing for #35: see _OUTPUT_FORMAT_BLOCK.
        lines.append("")
        lines.append(_OUTPUT_FORMAT_BLOCK)
        return "\n".join(lines)
