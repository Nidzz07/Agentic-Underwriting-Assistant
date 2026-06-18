# Story Generation Plan — Agentic Underwriting Assistant

**Stage**: DISCOVER → User Stories (Part 1 — Planning)
**Role**: Product Owner
**Date**: 2026-06-17
**Status**: Plan approved; Part 2 generated (stories.md, personas.md, user-journey.md); awaiting approval at the User Stories gate

This plan defines **how** we will convert the approved `requirements.md` into
user stories. It does not write the stories yet — Part 2 (generation) runs only
after you answer the questions in Section C and approve this plan.

---

## A. Methodology & Execution Checklist (Part 2 will follow this)

- [x] Derive personas from PER-1..6 → `personas.md` (underwriter, compliance/audit reviewer, system administrator)
- [x] Convert requirements into INVEST stories (Independent, Negotiable, Valuable, Estimable, Small, Testable)
- [x] Organise stories using the approved **breakdown approach** (see Q4)
- [x] Write acceptance criteria for each story in the approved **format** (see Q5)
- [x] Trace every story back to one or more `requirements.md` IDs (FR-/NFR-/PER-/CON-/SEC-/QA-)
- [x] Explicitly cover the invariant-bearing flows: human approval gate (FR-UI-2), override-with-reason (CON-BR4), RBAC separation (PER-4), advisory-only language (FR-UI-4)
- [x] Map personas → stories
- [x] Produce `user-journey.md` (Mermaid) for the primary underwriting-review workflow
- [x] Items OOS-1..6 are Phase 3 / future-release, documented in requirements.md only; generate Phase 1 + Phase 2 stories this round, each phase-tagged (1 or 2)
- [x] Tag EVERY story with a MANDATORY Phase tag (Phase 1 or Phase 2); "what's in Phase 1" must be a first-class, sliceable backlog view
- [x] UI epic = journey-style stories; backend epics (intake/rules/outlier/memo) = capability stories phrased from the benefiting persona (per Q4 refinement 2)
- [x] Map each epic → its component's build units + definition-of-done (requirement → epic → story → unit → test) (per Q4 refinement 3)

## B. Mandatory Artifacts (produced in Part 2)

- [x] `guide-docs/discover/user-stories/stories.md`
- [x] `guide-docs/discover/user-stories/personas.md`
- [x] `guide-docs/discover/user-stories/user-journey.md` (Mermaid)

---

## C. Planning Questions

**How to answer**: write your choice's letter after each `[Answer]:` tag (e.g.
`[Answer]: B`). You may select multiple letters and add free-text notes. Choose
**Other** if nothing fits. Answer all questions, then tell me you're done.

### Question 1 — Persona coverage depth
The approved personas are underwriter (primary), compliance/audit reviewer
(read-only), and system administrator (CLI-only, minimal). How much story
coverage should each persona get?

A) Full stories for all three personas (underwriter, auditor, admin)
B) Full stories for underwriter + auditor; **minimal** stories for admin (reflecting CLI-only, no admin UI)
C) Underwriter stories only this round; auditor + admin as a thin follow-up set
D) Other (please describe after [Answer]: tag below)

*PO recommendation: B — matches PER-3 (admin is CLI/migration, no full UI).*

[Answer]: B — Full stories for underwriter + auditor; minimal for admin. Admin is CLI/migration only with no UI (PER-3), so full UI-style stories would describe screens that don't exist. Coverage should match where each persona actually interacts.

### Question 2 — How should non-functional / quality requirements appear?
The brief's acceptance gates (reproducibility, bias-swap delta 0, groundedness,
coverage, observability) and the binding constraints (CON-BR1..4) are not
classic user features.

A) Capture them as **acceptance criteria woven into** the relevant functional stories
B) Capture them as **separate explicit stories** (e.g. "As a compliance reviewer, I need a bias-swap report…") where a persona benefits, and as cross-cutting acceptance criteria otherwise
C) Keep them entirely out of stories (they live in requirements.md only)
D) Other (please describe after [Answer]: tag below)

*PO recommendation: B — auditor-facing quality artifacts (bias report, audit trail) deserve their own stories; purely internal invariants stay as acceptance criteria.*

[Answer]: B — Quality/NFR requirements become their own stories where a persona benefits from a user-facing artifact (e.g. auditor needs a bias-swap report and an audit trail), and remain cross-cutting acceptance criteria otherwise. Important: blocking gates must keep their exact strength when written as criteria — "bias-swap delta = 0 (any delta blocking)" and "decision reproducibility = 100%" must not be softened into "minimal" or "high" during story conversion.

### Question 3 — Story granularity
What level of granularity do you want for stories?

A) Coarse — epic-level stories (one per major capability), few in number
B) Medium — feature-level stories with 3–7 acceptance criteria each
C) Fine — small, narrowly-scoped stories (many stories, each tiny)
D) Other (please describe after [Answer]: tag below)

*PO recommendation: B — feature-level keeps stories INVEST-compliant and testable without fragmenting.*

[Answer]: B — Feature-level stories with 3–7 acceptance criteria each. Coarse epic-level stories aren't testable enough; fine-grained tiny stories fragment the backlog. Feature-level is the INVEST sweet spot and keeps each story estimable and testable.

### Question 4 — Story breakdown / organisation approach
How should stories be grouped?

A) **User Journey-Based** — follow the underwriter's workflow (queue → review memo → check flags → approve/override → history)
B) **Feature-Based** — grouped by system capability (intake, rules, outlier, memo, UI)
C) **Persona-Based** — grouped by user type (underwriter / auditor / admin)
D) **Epic-Based** — hierarchical epics (aligned to the 5 components) with sub-stories
E) **Hybrid** — epics aligned to components, stories told as user-journey steps within them
F) Other (please describe after [Answer]: tag below)

*PO recommendation: E — component epics give traceability to requirements/units; journey-based stories inside keep them user-centered.*

[Answer]: E (with refinements) — component epics aligned to the 5 components (Intake, Rules, Outlier, Memo, UI) for traceability to requirements/units. Refinements (per project direction): (1) every story carries a MANDATORY Phase tag (1 or 2) so the backlog is sliceable by build sequence — "what's in Phase 1" must be a first-class view. (2) UI epic stories are journey-style (queue → review memo → check flags → approve/override → history); backend epics (intake/rules/outlier/memo) are capability stories phrased from the benefiting persona ("As an underwriter, I receive a memo citing every triggered rule…"). (3) Each epic maps to its component's build units + definition-of-done, closing requirement → epic → story → unit → test.

### Question 5 — Acceptance-criteria format
What format for acceptance criteria?

A) **Gherkin** (Given/When/Then) — precise, automation-friendly, maps to the data-testid UI
B) **Bulleted checklist** — lighter weight, faster to read
C) **Hybrid** — Gherkin for interactive/UI stories, bullets for analytical/report stories
D) Other (please describe after [Answer]: tag below)

*PO recommendation: A — Gherkin aligns with the brief's automated-testing posture and data-testid attributes (FR-UI-3).*

[Answer]: A (with C as fallback) — Gherkin (Given/When/Then) as the default, because the brief mandates data-testid on every UI element (FR-UI-3) and an automated-testing posture, and Gherkin maps almost 1:1 to automated UI tests. Fallback: where a story is analytical/report-style rather than interactive (e.g. a bias-swap report or coverage report), and Gherkin reads awkwardly, use a bulleted-checklist format for that story instead (the hybrid approach from option C). Keep Gherkin as the norm; use bullets only where Given/When/Then genuinely doesn't fit.

### Question 6 — User-journey diagram scope
The mandatory `user-journey.md` Mermaid diagram should depict:

A) The **primary underwriter** review-to-decision journey only
B) Underwriter journey **plus** the read-only auditor review path
C) All three personas' touchpoints (underwriter, auditor, admin) in one diagram
D) Other (please describe after [Answer]: tag below)

*PO recommendation: B — the underwriter and auditor are the UI personas; admin is CLI and out of a UI journey.*

[Answer]: B — Underwriter journey plus the read-only auditor review path. These are the two UI-facing personas; admin is CLI and has no UI journey to diagram. Consistent with the Q1 coverage decision.

### Question 7 — Story ID / traceability convention
How should stories link back to requirements?

A) Each story carries a **Traceability** line listing the `requirements.md` IDs it satisfies (e.g. `Traces: FR-UI-2, CON-BR4`)
B) A separate traceability matrix at the end of `stories.md` mapping stories ↔ requirement IDs
C) Both — per-story line **and** a summary matrix
D) Other (please describe after [Answer]: tag below)

*PO recommendation: C — per-story line for context, matrix for coverage auditing (consistent with the requirements doc's traceability discipline).*

[Answer]: C — Both: a per-story Traceability line listing the requirements.md IDs each story satisfies, AND a summary matrix at the end mapping stories ↔ requirement IDs. The per-story line gives context while reading; the matrix lets you audit coverage (every requirement exercised by ≥1 story), consistent with the traceability discipline already in requirements.md.

---

## D. Approval

After you answer Section C, I will:
1. Analyze the answers for ambiguity/contradiction and raise focused follow-ups if needed.
2. Present this plan for your explicit approval.
3. Only then run Part 2 to generate `stories.md`, `personas.md`, and `user-journey.md`.

*Stop point: no stories are generated until you answer the questions and approve this plan.*
