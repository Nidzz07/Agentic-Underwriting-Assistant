# Business Rules — `ui-shell` (`ui-common` / U10)

**Stage**: BUILD → Functional Design (per-unit) · shared shell / design-system unit · **Depth**: standard
**Unit**: U10 `ui-shell` · **Date**: 2026-07-07 · owns **CON-BR4 (language facet)**, FR-UI-3/4/5 · Story **US-UI-7**.
**Scope**: The **enforceable conventions** every C5 view conforms to. Each rule states its condition explicitly and, where
it is checkable, names the mechanism. **Advisory-only language throughout; no LLM; no business logic in `ui-shell`.**

---

## 1. Advisory-only copy as an enforceable single source (CON-BR4 language facet / FR-UI-4)

### BR-UI-1 — The copy module is the single source; no primitive or view inlines a display string (fold)
- **Condition**: every Recommendation / Confidence / Role **display string** is defined **only** in `shell/copy`
  (`domain-entities.md §2`). **No shell primitive and no view inlines a string** — including the `RecommendationBadge`,
  which receives the domain **value** as a prop and **looks up** its label from `RECOMMENDATION_LABELS`. The badge is
  itself a **consumer** of the copy module.
- **Why (Q1 + Q2 fold)**: a components library (primitives) and a copy module are **separate concerns that compose
  cleanly** — the primitive owns *how it looks*, the copy module owns *what it says*. This guarantees **one** source of
  recommendation-related strings, not two.
- **Checkable**: a lint/test asserts no view/primitive literal contains a Recommendation/Confidence label outside
  `shell/copy` (lands at NFR/Code-Gen).

### BR-UI-2 — Advisory vocabulary (lexical): "recommendation" not "decision"; the `-RECOMMEND` suffix is mandatory
- **Condition**: for **system output**, the required term is **"recommendation"**; the word **"decision"** is reserved
  for the **human underwriter's** committed action and must **never** label system output. The decline label **preserves
  the `-RECOMMEND` suffix** (`DECLINE-RECOMMEND`); a **bare `"DECLINE"`** is forbidden.
- **Why**: CON-BR4 / underwriting-rules hard-constraint #1 (advisory only) + FR-RULES-5.
- **Checkable (Q2 lint — lexical)**: a build-failing lint over `FORBIDDEN_TERMS` catches a bare `"DECLINE"`, or
  "decision"/"approved"/"declined" used as **system** output. Applies to **any system-output string, anywhere** —
  including inside the gate view.

---

## 2. Human-gate framing (CON-BR4 / hard-constraint #2)

### BR-UI-3 — Finalization framing only in the human-gate context; named as the human's action (Q3)
- **Condition**: no shell copy/label may imply **auto-finalization**. Finalization-implying framing may appear **only**
  in the **human-gate context**, where the affordances are the underwriter's **Approve / Override**, where **Override
  carries a mandatory non-blank reason and Approve requires none** (matching `CommittedDecision.reason` — mandatory on
  override only) — defined as explicitly **human** actions (the `CommitAction` namespace `{approve, override}`,
  `domain-entities.md §2.1`), **named distinctly** from any system-output string (in particular the human `override` is
  **not** the system `DECLINE-RECOMMEND`) so the two can never be confused.
- **Why (Q3 vs Q2 — distinct responsibilities; shared source fold)**: BR-UI-2 is **lexical/vocabulary** correctness
  (right words, sourced from the module) and applies to any system-output string anywhere. **BR-UI-3 is
  contextual/attribution** correctness (finalization framing only in-gate, attributed to the human). Each catches what
  the other cannot:
  - BR-UI-2 catches a **wrong-vocabulary** label even inside the gate (a bare "DECLINE").
  - BR-UI-3 catches a **correctly-worded** label placed in the **wrong context/attribution** (a screen implying the
    *system* finalized).
- **Checkable + fold**: both checks are backed by **ONE co-located forbidden/required-vocabulary source**
  (`FORBIDDEN_TERMS` next to the copy module) so there are **no two divergent word-lists**; BR-UI-3 layers the
  **context/attribution** assertion (finalization verbs render only within the human-gate component; the human action
  namespace stays distinct from system output) on top of that single source. Lands at NFR/Code-Gen.
- **Scope boundary (which layer verifies what)**: `ui-shell` owns and tests the single **`FORBIDDEN_TERMS`/namespace
  SOURCE** and the **namespace-distinctness** check (the `CommitAction {approve, override}` labels ≠ the `Recommendation`
  labels; `override` ≠ `DECLINE-RECOMMEND`). The **render-context assertion** — "finalization verbs render only within
  the human-gate component" — is verified by **`ui-approval-gate` (U7)**, which composes the shell and owns the gate
  component; `ui-shell` owns **no** gate component or view, so it does not render one (reference-not-own between UI units;
  keeps NFR-UI-SCOPE-1 consistent and prevents this scope confusion resurfacing at Code-Gen).

---

## 3. Role-based rendering (Q4) — cosmetic only

### BR-UI-4 — `RoleGate` is a cosmetic render-guard; it owns NO authorization decision
- **Condition**: `RoleGate` (`domain-entities.md §3/§5`) **consumes** the current Role to show/hide/disable action
  affordances for readability. It owns **NO authorization decision**. The **real boundary** stays `auth-rbac`'s backend
  `authorize` + audit-store's `DecisionCommitService` re-check (SEC-4) — the server **rejects an unauthorized action even
  if the UI guard were bypassed**.
- **Reference-not-own (cross-language)**: the Role is consumed as a **value shape** from an abstracted session seam; **no
  `auth_rbac` Python is imported** into the React codebase. Role retrieval over the wire is **WIRE-1** (§5 of
  `business-logic-model.md`), not authored here.
- **Checkable**: a test asserts `RoleGate` renders/hides purely on the injected Role value and calls **no** authorization
  function; the shell imports no backend authz module.

---

## 4. Structural pinned rules (Q5) — not aesthetic, not negotiable

### BR-UI-5 — `data-testid` convention (FR-UI-3)
- **Condition**: every interactive / assertion-relevant shell primitive exposes a **stable `data-testid`** per the
  documented naming convention (`domain-entities.md §6`).
- **Checkable**: a lint/test asserts the convention over shell primitives (NFR/Code-Gen).

### BR-UI-6 — No TypeScript (FR-UI-5)
- **Condition**: the unit is authored in **plain JS/JSX + React + Tailwind** — **no TypeScript**: no `.ts`/`.tsx`, no TS
  toolchain/config.
- **Checkable**: a test/CI check asserts no `.ts`/`.tsx` files and no TS config in the unit.

---

## 5. Boundaries — no business logic; WIRE-1 dependency

### BR-UI-7 — No business logic; no LLM; the wire contract is WIRE-1 (reference-not-own)
- **Condition**: `ui-shell` performs **no rule evaluation, no authorization decision, no commit, no memo drafting, and
  runs no LLM**. It consumes backend **shapes** by value (`domain-entities.md §2.1`) and **imports no backend production
  code**. The frontend↔backend **wire/serialization contract** (endpoints, response envelope, error shape, session-role
  delivery) is **WIRE-1**, owned by the future FastAPI composition-root api-contract artifact — **not authored here**;
  `ui-shell` fetches nothing real and proceeds on the abstracted seams.
- **Serialization invariant (WIRE-1)**: enums serialize **by value**; the four canonical casings
  (`domain-entities.md §2.1`) are the canonical wire map — WIRE-1 **must not remap or re-case** them; the copy module
  keys on these values.

---

## 6. Rule index

| Rule | Condition summary | Traces |
|---|---|---|
| BR-UI-1 | copy module = single source; no primitive/view inlines a string (badge looks up by value) | Q1+Q2 fold; CON-BR4; FR-UI-4 |
| BR-UI-2 | "recommendation" not "decision"; `-RECOMMEND` mandatory; no bare "DECLINE" (lexical lint) | CON-BR4; FR-RULES-5; hard-constraint #1 |
| BR-UI-3 | finalization framing only in the human-gate context, named as the human's action (attribution test) | CON-BR4; hard-constraint #2; Q3 |
| BR-UI-4 | RoleGate cosmetic; no authz decision; no `auth_rbac` import | SEC-4; Q4; reference-not-own |
| BR-UI-5 | `data-testid` convention (checkable) | FR-UI-3; Q5 |
| BR-UI-6 | no TypeScript (checkable) | FR-UI-5; Q5 |
| BR-UI-7 | no business logic / no LLM; wire contract is WIRE-1 | reference-not-own; WIRE-1 |

---

## 7. Security-Guardrails compliance (enabled extension)

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A (referenced)** | `ui-shell` renders/guards; it validates no application input (that is `intake`'s SEC-2). It fetches nothing real (BR-UI-7). |
| Prompt-injection defense | **N/A** | No LLM/prompt path in `ui-shell` (SEC-1 is `document-sanitizer`'s). |
| Secrets management | **N/A** | No secret handled in the shell; env/keys are `secrets-config`'s SEC-3. |
| Read-only DB access for audit role | **N/A (referenced)** | The auditor read-only distinction is surfaced **cosmetically** via `RoleGate` (BR-UI-4); enforcement is `auth-rbac` + `audit-store` (SEC-4). |
| Audit logging | **N/A** | The shell persists nothing; the audit trail is `audit-store`'s CON-AUDIT-1. |
| **Least-privilege UI framing (advisory-only + human-gate)** | **Compliant (owns the copy facet)** | CON-BR4 language facet single-sourced here: advisory vocabulary (BR-UI-1/2), human-gate framing (BR-UI-3), cosmetic RBAC (BR-UI-4). |

No blocking finding.
