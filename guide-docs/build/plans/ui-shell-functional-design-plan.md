# Functional Design Plan — `ui-shell` (`ui-common` / U10)

**Phase / Stage**: BUILD → Functional Design (per-unit, plan-then-generate) · **RESUMED session** (prior carryover check interrupted at usage limit; disk re-verified clean, no partial artifact).
**Unit covered**: U10 `ui-shell` (C5, Phase 1) — the **FIRST frontend/React unit** in the build (track switch from Python). Owns the **UI-wide invariant** (advisory-only "recommendation" copy convention + `data-testid` convention) as a **shared contract** every C5 view unit conforms to. Story **US-UI-7**; owns **CON-BR4 (language facet)**, FR-UI-3/4/5.
**Date**: 2026-07-07 · **Stack**: React + Tailwind, **NO TypeScript** (FR-UI-5, pinned) · **Depth**: proposed **standard** (confirm at Q6).
**Status**: **Plan — awaiting `[Answer]:` tags.** No FD artifacts generated yet. Stop after this plan.

This plan is the **altitude drop to internals** for a **shared shell / design-system unit** whose entire job is to be the
**single source** of the app-wide UI conventions the five C5 view units (`ui-queue`, `ui-memo-view`, `ui-approval-gate`,
`ui-override-form`, `ui-history`) — plus the Phase-2 `ui-outlier-view` — **conform to**. It **reconciles against, and
re-opens none of**, the seven completed backend units' actual code or design docs; it consumes their **shapes** by
reference only. **ui-shell owns NO business logic** — no rule evaluation, no authorization decision, no LLM, no commit.

---

## 1. Unit context (analyzed — Step 1) ✅

### 1.1 `ui-shell` (U10, C5, Phase 1) — from the frozen `unit-of-work.md §U10`
- **Purpose**: own the **UI-wide invariant** — advisory-only "recommendation" copy conventions + the `data-testid`
  lint/convention — as a **shared contract** every view unit conforms to (incl. Phase-2 `ui-outlier-view`). Prevents any
  single view unit from owning app-wide conventions.
- **Story**: US-UI-7.
- **Owned invariants**: **CON-BR4 (language facet)** / advisory-only vocabulary (single source of the *copy* convention),
  **FR-UI-3** (`data-testid`), **FR-UI-4** (advisory copy), **FR-UI-5** (React + Tailwind, **no TypeScript**).
- **Depth** (`unit-of-work.md`): *"standard (convention + lint), but the advisory-only rule is invariant-bearing."* →
  treated as a genuine decision at **Q6**.
- **Is NOT**: a view unit (no queue/memo/gate/override/history screen lives here); an owner of authorization logic (that
  is `auth-rbac`); an owner of the commit gate (that is `audit-store`'s `DecisionCommitService`).

### 1.2 The consumed backend surfaces (compiled 2026-07-07 across all seven completed units — SHAPES by reference only)
ui-shell renders/guards against these; it **imports none of their production code** and re-opens none of their design docs.

| Producer unit | Surface ui-shell conforms to | What the shell provides for it |
|---|---|---|
| **rules-engine** | `Recommendation {APPROVE, REFER, DECLINE-RECOMMEND}` (the **`-RECOMMEND` suffix is mandatory copy**, FR-RULES-5) + `Confidence {High, Medium, Low}`; `RuleResultReport` (per-rule pass/fail, each citing the triggering value) | canonical **display labels** for the three recommendations + three confidences (single copy source), never a bare "DECLINE" |
| **memo-agent-core** | `DecisionMemo` three-region shape: LLM `narrative_prose` + `cited_rule_ids` · deterministic `missing_information` · read-only `recommendation`/`confidence` · `memo_hash`/`model_version` | layout/typography primitives + copy conventions the memo view composes; **read-only region** framing |
| **audit-store** | read-only `AuditService` surface (get / browse_history / effective_status — READ-1/LOG-1); commit path = `DecisionCommitService` (requires `underwriter_id` + `reason`) | history/read display primitives; the **human-gate framing** (Q3) that keeps commit-triggering copy honest |
| **auth-rbac** | `Role {underwriter = acts, auditor = read-only, admin}` (SEC-4 single source; backend enforces at API + `DecisionCommitService` re-check) | a **thin presentational render-guard** pattern (Q4) — cosmetics/defense-in-depth, **never** the security boundary |

### 1.3 Binding constraints held through this FD (guardrails skill + project + frontend-design skill)
- **Advisory-only (underwriting-rules hard-constraint #1 / CON-BR4)** — user-facing and internal naming say
  **"recommendation"**, never "decision", for system output; "decision" is reserved for the **human underwriter's**
  committed action. The `-RECOMMEND` suffix is preserved in DECLINE copy. **This is the unit's owned invariant.**
- **Human-in-the-loop gate (hard-constraint #2)** — no shell copy/label may imply auto-finalization; the gate's action
  labels are explicitly the human's (Accept/Decline + mandatory reason), named distinctly from any system output.
- **No business logic in the shell** — no rule eval, no authorization *decision*, no LLM, no commit. The RBAC render-guard
  is cosmetic; the real boundary is `auth-rbac` + `DecisionCommitService` (**reference-not-own**).
- **`data-testid` (FR-UI-3)** and **no TypeScript (FR-UI-5)** — pinned, checkable, non-aesthetic (Q5).
- **frontend-design skill — RECONCILED, not applied raw**: the skill's *maximalist* default is **overridden** for this
  **BFSI audit-grade** surface in favor of the skill's **refined-minimalism** branch — legible, trustworthy-professional,
  restraint over spectacle, distinctive-but-professional type + a restrained palette via CSS/Tailwind theme tokens
  (**no** generic Inter/Roboto/Arial default; **no** purple-gradient cliché). Aesthetic **direction** is pinned here;
  specific token values are a later (NFR-Design / Code-Gen) detail. The invariant-bearing parts above are
  **project-PINNED, not aesthetic preference**.

---

## 2. Functional Design execution plan (checkboxes — Step 2)

Artifacts to generate **after** answers + ambiguity-check, under `guide-docs/build/ui-shell/functional-design/`:
- `domain-entities.md` — the **shared design-system surface** (a UI unit's "entities" = its module/primitive inventory):
  the shell primitives/layout components (names + prop shapes, no view screens), the **design-tokens** surface, the
  **copy/strings** module (the canonical Recommendation/Confidence labels + advisory vocabulary), and the **RoleGate**
  render-guard primitive (props: role + affordance, no authz logic). Text tables suffice; a diagram only if it aids.
- `business-rules.md` — **BR-UI-\***: advisory-only copy as an **enforceable single source** (Q2); **human-gate framing**
  as a **checkable rule** (Q3); the **RBAC-render-guard-is-cosmetic-not-security** rule (Q4); **`data-testid` convention**
  + **no-TypeScript** as checkable rules (Q5); each rule states its condition; Security-Guardrails compliance table.
- `business-logic-model.md` — the **consume-and-conform flow**: how a C5 view imports the shell primitives + tokens +
  copy module + RoleGate and thereby inherits the conventions; the **shell↔view boundary** (what the shell owns vs. what
  each view owns); the **backend-surface map** (which shell copy maps to which producer shape, reference-not-own); a
  consumer/dependency map; an invariant self-check. A **validated Mermaid** (7 rules) + text alternative for the
  shell→views→backend-surface relationship.

- [x] **P1. Analyze unit context** (§1 — done).
- [x] **P2. Collect `[Answer]:` tags** (§3 — all A); ambiguity-check RUN — 4/5 clean (2 folds), ONE unpinned gap FLAGGED (wire contract) → resolved by the user as **Option A + hardened WIRE-1**.
- [x] **P3. Generate `domain-entities.md`** (copy module + wire map + primitives + tokens + RoleGate seam) — done 2026-07-07.
- [x] **P4. Generate `business-rules.md`** (BR-UI-1..7 + Security-Guardrails compliance) — done 2026-07-07.
- [x] **P5. Generate `business-logic-model.md`** (consume-and-conform flow + validated Mermaid + WIRE-1 checkpoint + backend map + self-check) — done 2026-07-07.
- [x] **P6. Contract-coverage check** — five owned invariants each covered (advisory copy → BR-UI-1/2; human-gate framing → BR-UI-3; RBAC cosmetic → BR-UI-4; data-testid → BR-UI-5; no-TS → BR-UI-6); no backend production code imported; no business logic (rules/authz/LLM/commit) in the shell (BR-UI-7). Both folds recorded; WIRE-1 registered.
- [x] **P7. Guardrail compliance pass + standardized 2-option completion message** (advisory-only, human-gate, no-LLM, reference-not-own, no-business-logic) — **presenting the FD gate now.** Request Changes / Continue → **NFR Requirements** for `ui-shell`.

---

## 3. Clarifying questions (Step 3 — fill each `[Answer]:` tag)

Put a letter after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe. These decide the
**shared design-system shape + the enforcement mechanisms** — they do **not** re-open any completed unit's frozen
code/design. **Each is a genuine decision.**

## Question 1 — What "shared" means: the shape of the design-system single source
`ui-shell` is the single source every C5 view conforms to. In what artifact form does it own that?

A) **BOTH** — a small **React components library** (shell primitives/layout: page frame, panel/region, read-only-region
   wrapper, status/recommendation badge, the RoleGate guard) **AND** a **design-tokens module** (color/spacing/typography
   as CSS/Tailwind theme variables — the single aesthetic source, refined-minimalism direction per §1.3). Views compose
   the primitives and inherit the tokens; nothing app-wide is redefined per view. **Recommended** — covers both the
   *structural* convention (primitives + testid) and the *aesthetic* single source (tokens) the unit exists to centralize.
B) **Design-tokens file only** (no shared components) — rejected: leaves layout, testid placement, and copy scattered
   across each view; the app-wide *structural* convention would have no home.
C) **Components library only** (no tokens module) — rejected: aesthetic values (color/type/spacing) scatter and drift
   per view, defeating the single-source purpose.
D) Other (please describe after [Answer]: tag below)

[Answer]: A — both a small React components library (shell primitives/layout: page frame, panel/region, read-only-region wrapper, status/recommendation badge, the RoleGate guard) and a design-tokens module (color/spacing/typography as CSS/Tailwind theme variables — the single aesthetic source, refined-minimalism direction). Views compose the primitives and inherit the tokens; nothing app-wide is redefined per view.

## Question 2 — Advisory-only vocabulary as an ENFORCEABLE single source (not a per-view convention)
CON-BR4 / FR-UI-4: "recommendation" never "decision" for system output; the three Recommendation labels (with the
mandatory `-RECOMMEND` suffix) + three Confidence labels live in ONE place. By what mechanism is that enforced?

A) **BOTH** — (i) a **shared copy/strings module** exporting the canonical labels + advisory vocabulary (the ONLY place
   the three `Recommendation` and three `Confidence` display strings are defined; views import, never inline), **AND**
   (ii) a **lint/test rule** that **fails the build** if a C5 view hardcodes a forbidden string (a bare `"DECLINE"`
   without `-RECOMMEND`, or the word "decision" used for *system* output). **Recommended** — a constants module gives the
   canonical source; the lint makes bypassing it a build failure, so the single source is genuinely enforced.
B) **Shared constants module only** — weaker: nothing stops a view from inlining its own string and bypassing the source.
C) **Lint rule only** — weaker: forbids bad strings but offers no canonical labels to import; each view still re-authors.
D) Other (please describe after [Answer]: tag below)

[Answer]: A — both a shared copy/strings module exporting the canonical labels + advisory vocabulary (the ONLY place the three Recommendation and three Confidence display strings are defined; views import, never inline), and a lint/test rule that fails the build if a C5 view hardcodes a forbidden string (a bare "DECLINE" without -RECOMMEND, or "decision" used for system output).

## Question 3 — Human-gate framing as a CHECKABLE rule (not a style-guide sentence)
Hard-constraint #2: no shell copy/label may imply auto-finalization. How is that made checkable?

A) **A checkable rule** — the shell copy module is the **only** source of action/label strings for **system output**, and
   a **test asserts** no view renders finalization-implying verbs (e.g. "approved"/"declined"/"decision" as *system*
   output) outside the human-gate context; the **gate's own action affordances** (the underwriter's **Accept / Decline
   with a mandatory reason**) are defined as explicitly **human** actions, **named distinctly** from any system-output
   string so the two can never be confused. **Recommended** — the user asked for checkable, not prose.
B) **A style-guide sentence only** — rejected: the user requires it checkable, not policy text.
C) **Rely on per-view code review** — rejected: not enforceable and not single-source (the anti-goal U10 exists to prevent).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — a checkable rule: the shell copy module is the only source of action/label strings for system output, and a test asserts no view renders finalization-implying verbs (e.g. "approved"/"declined"/"decision" as system output) outside the human-gate context; the gate's own action affordances (the underwriter's Accept/Decline with a mandatory reason) are defined as explicitly human actions, named distinctly from any system-output string.

## Question 4 — Role-based rendering boundary (thin consuming pattern; ui-shell owns NO authz logic)
Views must reflect the auth-rbac `Role` distinction (underwriter acts / auditor read-only). How does the shell expose that
without owning any authorization business logic?

A) **A thin presentational render-guard** — the shell exposes a `RoleGate` primitive (e.g. `<RoleGate can="act">…` /
   a `canAct(role)` render helper) that **consumes** the auth-rbac Role to **show/hide/disable action affordances** for
   readability, but owns **NO authorization decision**: the real boundary is **auth-rbac's backend `authorize` +
   `DecisionCommitService` re-check** (SEC-4 single source). The UI guard is **defense-in-depth cosmetics** — the server
   still rejects an unauthorized action even if the UI were bypassed. **Recommended** — the same reference-not-own posture
   as the backend units, in the UI. (The `Role` enum values are consumed as a shape; auth-rbac code is not imported.)
B) **ui-shell owns an authorization decision function** — rejected: duplicates/undermines auth-rbac's single source
   (SEC-4) and puts a security decision in the client; a reference-not-own violation.
C) **Each view re-implements its own role check** — rejected: scatters the pattern across views (the exact anti-goal U10
   exists to prevent) and risks per-view divergence.
D) Other (please describe after [Answer]: tag below)

[Answer]: A — a thin presentational render-guard: the shell exposes a RoleGate primitive that consumes the auth-rbac Role to show/hide/disable action affordances for readability, but owns NO authorization decision — the real boundary is auth-rbac's backend authorize + DecisionCommitService re-check (SEC-4 single source). The UI guard is defense-in-depth cosmetics; the server still rejects an unauthorized action even if the UI were bypassed.

## Question 5 — `data-testid` + no-TypeScript as FD-level PINNED rules (not aesthetic, not negotiable)
FR-UI-3 and FR-UI-5. Confirm both as checkable rules pinned at FD.

A) **Pin both as non-negotiable checkable rules**: (i) every interactive / assertion-relevant shell primitive exposes a
   **stable `data-testid`** per a documented naming convention, enforced by a lint/test; (ii) the unit is authored in
   **plain JS/JSX + React + Tailwind, NO TypeScript** (FR-UI-5) — checkable (no `.ts`/`.tsx`, no TS toolchain/config).
   Both are **structural requirements**, independent of the aesthetic direction. **Recommended.**
B) **Treat as guidance only** — rejected: FR-UI-3 and FR-UI-5 are pinned project requirements, not preferences.
D) Other (please describe after [Answer]: tag below)

[Answer]: A — pin both as non-negotiable checkable rules: (i) every interactive/assertion-relevant shell primitive exposes a stable data-testid per a documented naming convention, enforced by a lint/test; (ii) the unit is authored in plain JS/JSX + React + Tailwind, NO TypeScript — checkable (no .ts/.tsx, no TS toolchain/config). Both structural requirements, independent of aesthetic direction.

## Question 6 — Depth confirmation (genuine decision — convention+lint, but invariant-bearing)
What depth for this FD?

A) **Standard** — pin the shared design-system scope (primitives + tokens, Q1), the advisory-copy single source + lint
   (Q2), the human-gate framing rule (Q3), the RBAC render-guard pattern (Q4), the `data-testid` + no-TS rules (Q5), and
   the refined-minimalism aesthetic **direction** (values deferred to later stages), across the three FD artifacts kept
   concise. Right for a **convention+lint** unit whose advisory-only rule is **invariant-bearing** (per `unit-of-work.md`).
   **Recommended.**
B) **Minimal** — schema/primitive sketch only (rejected — the advisory-only + human-gate invariants must be **pinned**,
   not sketched; they are hard constraints).
C) **Comprehensive** — full heavy treatment (rejected — over-weight for a shell/convention unit; standard suffices).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — standard: pin the shared design-system scope (primitives + tokens), the advisory-copy single source + lint, the human-gate framing rule, the RBAC render-guard pattern, the data-testid + no-TS rules, and the refined-minimalism aesthetic direction (values deferred to later stages), across the three FD artifacts kept concise. Right for a convention+lint unit whose advisory-only rule is invariant-bearing.

---

## 4. Constraints & settled items held (not re-opened)
- The **consumed backend surfaces** (§1.2) are the substrate — the FD pins the shell's **conventions + primitives** that
  render/guard against them, re-opening **no** producer unit's code/design (rules-engine, memo-agent-core, audit-store,
  auth-rbac, database, secrets-config, intake/document-sanitizer are **referenced**, not re-opened).
- **Advisory-only / CON-BR4** — "recommendation" never "decision" for system output; the `-RECOMMEND` suffix preserved;
  single copy source (Q2). **Human-gate framing** checkable (Q3). **No LLM, no rule eval, no authz decision, no commit**
  in the shell.
- **Reference-not-own** — the shell imports **no** backend production code; consumes `Recommendation`/`Confidence`/`Role`
  as **shapes**; the RBAC guard is **cosmetic**, never the security boundary (Q4).
- **`data-testid` (FR-UI-3)** + **no TypeScript (FR-UI-5)** pinned + checkable (Q5).
- **frontend-design skill reconciled** — refined-minimalism direction pinned (§1.3); **not** the maximalist default;
  specific token/font/color values deferred to NFR-Design / Code-Gen.
- **Infrastructure Design not pre-committed** — likely a logged SKIP (source-level shell; Vercel topology is
  `deploy-config`'s P2 scope; npm/Node is a Code-Gen tech-stack detail) — **confirmed at the Infra stage after NFR**, not
  assumed here.
- **Settled non-edits stay closed**: `PROJECT-BRIEF.md`, `user-journey.md`, and every built unit's code/design docs.

---

## 5. Next step (STOP here)
Fill the six `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check (adding a
clarification file only if needed), then generate the three `ui-shell` Functional Design artifacts (`domain-entities.md`,
`business-rules.md`, `business-logic-model.md`) and present the standardized 2-option completion message. **No FD
artifacts or code are generated until the answers are in and checked.**
