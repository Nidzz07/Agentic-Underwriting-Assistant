# NFR Design Plan — `ui-shell` (`ui-common` / U10)

**Phase / Stage**: BUILD → NFR Design (per-unit, plan-then-generate)
**Unit covered**: U10 `ui-shell` — the shared shell/design-system; owns **CON-BR4 (language facet)**, FR-UI-3/4/5.
**Date**: 2026-07-07 · **Depth**: **mirror NFR Requirements — lighter overall EXCEPT full rigor on the invariant /
AC-bearing facets** (per user direction). **Status**: answers from the user's explicit pattern/component mapping;
ambiguity-check RUN (below); generating Part 2 this turn, then STOP at the NFR-Design gate.

Built **ON** the frozen FD (incl. the GATE-1 rescope's BR-UI-3 clarification + the RoleGate single-mechanism amendment)
and the approved `nfr-requirements.md` — **re-opening neither**. **Advisory-only; no LLM; reference-not-own + WIRE-1 held
(external boundary, NOT designed here).**

---

## 1. Pattern + component mapping (from the user's explicit direction)

| NFR-UI-* target | Pattern | Component(s) |
|---|---|---|
| COPY-1 | **SingleSourceCopyModulePattern** | `shell/copy`; badges look up by value |
| ADVISORY-1 + GATE-1 | **SharedVocabularySourcePattern** (ONE `FORBIDDEN_TERMS` object, TWO checks: lexical vs namespace-distinctness) | `shell/copy` (+ `FORBIDDEN_TERMS`) |
| TESTID-1 | **DataTestidConventionPattern** (+ detector self-test) | `shell/components` primitives |
| NOTS-1 | **StructuralFileScanPattern** (no `.ts`/`.tsx`, no `tsconfig`) | whole unit / CI |
| RBAC-1 | **CosmeticRoleGatePattern** (reads injected `RoleContext` via `useCurrentRole()`, no authz call, stub-provider test; no `role` prop) | `RoleGate` + `shell/session` |
| REFNOTOWN-1 | **ReferenceNotOwnStructuralGuardPattern** (no backend import, no real fetch; value shapes; WIRE-1 held) | all components |
| AESTHETIC-1 | **DesignTokenPattern** (direction pinned, VALUES deferred; categories only) | `shell/tokens` |
| PERF-1 / A11Y-1 / SCOPE-1 | **ReferencedBoundaryPattern** (soft / governance) | boundary |

---

## 2. Ambiguity-check (RUN before generating) — CLEAN (1 reconciliation noted, not a gap)

- **Coverage (no orphan)**: all 11 `NFR-UI-*` targets → a pattern + ≥1 component (table above). ✅
- **Depth matches**: full rigor on COPY/ADVISORY/GATE/TESTID/NOTS (+ medium RBAC); soft on AESTHETIC/PERF/A11Y +
  the SCOPE governance statement. ✅
- **No new scope / WIRE-1 held**: `RoleGate` reads `RoleContext` via `useCurrentRole()`; **how `RoleContext` is populated
  is WIRE-1**, NOT designed here (stub provider for tests). Token VALUES deferred. GATE-1's render-context attribution
  stays **U7-owned**. ✅
- **Reconciliation noted (NOT a gap — a frozen-requirement realization)**: the amended **GATE-1** (frozen
  `nfr-requirements.md`) requires the copy module to **define the `CommitAction` labels `{approve, override}`** so it can
  assert them **≠** `RECOMMENDATION_LABELS`. FD §2.1 already establishes `CommitAction` as a copy-module namespace kept
  distinct; FD §2.2's contents list enumerated the other label sets but not this export by name. NFR Design therefore
  names **`COMMIT_ACTION_LABELS`** as a `shell/copy` export — **realizing what GATE-1 already mandates**, not adding
  scope or improvising. Surfaced here for transparency; **not a stop-gap** (no frozen artifact is re-opened or changed).
- **Testable without backend/wire**: lints (ESLint) + structural set-disjointness test (GATE-1) + file-scan (NOTS-1) +
  stub-provider RTL (COPY-1(b), RBAC-1) — all run with stubs; none needs WIRE-1. ✅

**Verdict: CLEAN** — proceed to generate.

---

## 3. Artifacts to generate (Part 2)

Under `guide-docs/build/ui-shell/nfr-design/`:
- `nfr-design-patterns.md` — one §-pattern per group, each structurally meeting its `NFR-UI-*` target + a pattern-
  integration Mermaid (7-rule validated + text alt) + a traceability section.
- `logical-components.md` — the shell components (C1 `shell/copy`, C2 `shell/components`, C3 `shell/session`,
  C4 `shell/tokens`) + the test/lint substrate + ownership + a **reference-not-own check** + a **component→target
  coverage** table (no orphan) + a component-relationship Mermaid (7-rule validated + text alt).

- [x] P1. Fill pattern/component mapping from the user's direction (§1).
- [x] P2. Run the ambiguity-check (§2) — CLEAN (1 reconciliation noted).
- [x] P3. Generate `nfr-design-patterns.md`.
- [x] P4. Generate `logical-components.md`.
- [x] P5. Coverage + guardrail pass; update guide-state + audit; present the NFR-Design 2-option gate. **STOP.**

---

## 4. Held constraints (not re-opened)
- Frozen FD (BR-UI-1..7 + design-system surface, incl. GATE-1's BR-UI-3 clarification + RoleGate single-mechanism) +
  approved `NFR-UI-*` targets — patterns/components realize them, re-opening neither.
- **Reference-not-own (cross-language)** + **WIRE-1** — held; `RoleContext` population is WIRE-1's, not designed here.
- **Aesthetic token VALUES** deferred to Code-Gen. **Infrastructure Design** not pre-committed (likely SKIP, confirmed
  after NFR Design). **Advisory-only; no LLM.** Settled non-edits stay closed.
