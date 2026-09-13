"""⚠️ THE OFFLINE ``LLMClient`` DOUBLE FOR THE REQUEST PATH (WIRE1-Fold-6, Q5(a)).

⛔ **NOT A MODEL. NOT REAL INFERENCE.** Every memo it produces is stamped
``OFFLINE-DOUBLE-NOT-A-REAL-LLM``, so a synthetic memo is visible in the API response, the
database, and any ``AuditRecord`` it is later committed into. **Register #18's gap (iii) —
synthetic memo prose — is NOT closed by this and must not be described as closed.**

⚑ **WHY THIS MODULE EXISTS, AND WHY IT IS A DELIBERATE DECISION RATHER THAN A CONVENIENCE.**

Q5(a) chose the offline double for R11's path *"free, safe, deterministic … honest by
construction"*, over Q5(b)'s real LLM, which *"puts spend behind an HTTP route with no rate
limit, no per-user cap and no abuse story"*. R11 lives in ``backend/app/``, so the double it
drafts with must be importable from ``backend/app/``.

⛔ **The only other offline double in this build is NOT importable from here.** It lives in
``backend/scripts/seed_demo_cases.py``, whose own module docstring states the boundary
verbatim: *"``backend/scripts/`` is outside ``backend/app/`` … so the offline double below
cannot be mistaken for, or accidentally wired into, a production path."* That tree is also
absent from every ``--cov=`` entry, so importing it from the composition root would point a
production route at uncovered, explicitly out-of-band code.

⚑ **The precedent for the placement is this package's own ``llm_client.py``**, which holds the
REAL client for the same frozen seam and explains why: *"this module lives in the composition
root, which is where both frozen docstrings in ``memo_agent_core/provider.py`` say the real
client belongs — 'wrapped to this at composition'."* The offline stand-in for that same seam
belongs beside it, by the same argument.

⚠️ **DISCLOSED COST — this is the SECOND implementation of the same double.** The seed script's
copy is deliberately left in place: moving it would edit an out-of-band script and its tests for
no benefit to this pass, and importing across the boundary is what this module exists to avoid.
**Deduplicating them is a named follow-on, not an oversight.** The two must stay behaviourally
equivalent; if they drift, this one governs the request path.
"""
from __future__ import annotations

import re

#: ⚠️ Stamped onto every memo this double produces, so the placeholder is visible everywhere it
#: travels. ⚑ The VALUE is deliberately identical to the seed script's ``OFFLINE_MODEL_VERSION``:
#: an operator reading a database row must not have to know which path wrote it to know it is
#: synthetic. Matched by value, not imported — the same reference-not-own discipline the build
#: applies to ``RBAC_COMMIT``.
OFFLINE_MODEL_VERSION = "OFFLINE-DOUBLE-NOT-A-REAL-LLM"

#: Matches a rule id as it appears in U4's prompt (e.g. ``DTI-CEIL-1``, ``IRDAI-EMP-SALARIED-1``).
_RULE_ID_PATTERN = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b")

#: ⛔ **LOAD-BEARING — these two strings BOUND the search region** (authorization §3.3, register
#: **#35**). They are the literal section headers ``PromptBuilder.build()`` emits, matched by value
#: rather than imported (the same reference-not-own discipline as ``OFFLINE_MODEL_VERSION`` above —
#: ``backend/app/`` must not reach into the frozen unit for a constant). ⚠️ **Rewording either header
#: in ``memo_agent_core/prompt_builder.py`` without changing it here silently breaks extraction and
#: sends every case to ``FAILED``** — change both in the same commit.
_REPORT_START_MARKER = "RULE REPORT (the only citable rules):"
_REPORT_END_MARKER = "APPLICANT FACTS (non-demographic):"


def first_cited_rule_id(prompt: str) -> str:
    """The first rule id **in the prompt's rule-report section**, or ``""`` if there is none.

    ⚑ **DISCOVERED, never hardcoded.** The seed script's copy of this double originally cited a
    hardcoded ``DTI-001`` — a rule id that does not exist in this build — so the emitted
    ``<rule_id>`` was always empty, U4's ``CitationValidator`` always rejected, and **every
    seeded case silently landed in ``FAILED``**. Discovering the id from the prompt is what
    makes citation validation pass for the RIGHT reason rather than by coincidence.

    ⛔ **The search is BOUNDED AT BOTH ENDS — register #35** ``OFFLINE-DOUBLE-CITES-THE-RECOMMENDATION``.
    It previously searched the **whole** prompt, and ``PromptBuilder`` writes
    ``RECOMMENDATION (read-only): <value>`` **above** the rule report.
    ``Recommendation.DECLINE_RECOMMEND.value`` is ``"DECLINE-RECOMMEND"``, which this module's
    rule-id regex matches — so ⛔ **every DECLINE-RECOMMEND case cited the recommendation itself**,
    ``CitationValidator`` rejected the fabricated id, and the case landed in ``FAILED``. ⚠️
    ``APPROVE`` and ``REFER`` escaped only because their values contain no hyphen: **luck, not
    correctness.**

    ⚑ **Why BOTH ends and not just the start** (§6.1, approved at sign-off): the start bound alone
    fixes the recommendation leak, but leaves the region running to the end of the prompt — so the
    ``REQUIRED OUTPUT FORMAT`` block appended **after** the applicant facts would fall inside it and
    its worked example would be extracted instead. Bounding at both ends keeps that out
    **independently** of the ``EXAMPLE_RULE_ID`` placeholder's underscore, which is the second
    defense. Neither depends on the other, which is what Q2 required.

    Returning ``""`` when the section genuinely contains no rule id is correct and deliberate:
    the draft is then legitimately blocked by ``CitationValidator``, which is the honest outcome
    rather than inventing a citation. ⚠️ **A MISSING marker returns ``""`` for the same reason** —
    if the prompt's shape is not the one this function was written against, it cannot know which
    tokens are citable, and guessing would fabricate a citation.
    """
    start = prompt.find(_REPORT_START_MARKER)
    if start == -1:
        return ""
    region_start = start + len(_REPORT_START_MARKER)

    end = prompt.find(_REPORT_END_MARKER, region_start)
    if end == -1:
        return ""

    match = _RULE_ID_PATTERN.search(prompt, region_start, end)
    return match.group(0) if match else ""


class OfflineMemoLLMClient:
    """Satisfies the frozen ``memo_agent_core.LLMClient`` seam STRUCTURALLY — no import, no
    inheritance — by returning fixed, valid structured XML.

    ⚑ The prose announces itself as a placeholder, so it is obvious even to someone reading a
    committed audit record with no other context. ``model`` and ``temperature`` are accepted and
    ignored: there is no model to select and no sampling to control.
    """

    def generate(self, *, model: str, prompt: str, temperature: float) -> str:
        cited = first_cited_rule_id(prompt)
        return (
            "<memo>"
            "<narrative_prose>"
            "PLACEHOLDER MEMO - GENERATED OFFLINE, NOT BY A LANGUAGE MODEL. This text exists "
            "only to exercise the wired submission path and carries no underwriting judgement "
            "of any kind. It must not be relied upon, shown to a customer, or read as an "
            "advisory recommendation. Refer this case to a human underwriter."
            "</narrative_prose>"
            f"<cited_rule_ids><rule_id>{cited}</rule_id></cited_rule_ids>"
            "</memo>"
        )
