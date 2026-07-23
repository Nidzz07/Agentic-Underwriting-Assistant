# NFR Requirements Plan — `ui-shell` (`ui-common` / U10)

**Phase / Stage**: BUILD → NFR Requirements (per-unit, plan-then-generate)
**Unit covered**: U10 `ui-shell` — the shared shell/design-system; owns **CON-BR4 (language facet)**, FR-UI-3/4/5.
**Date**: 2026-07-07 · **Depth**: **lighter overall EXCEPT full rigor on the invariant / acceptance-criteria-bearing
facets** (per user direction 2026-07-07). **Status**: answers filled from the user's explicit direction; ambiguity-check
RUN (below); generating Part 2 this turn, then STOP at the NFR gate.

Built **ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`, incl. the RoleGate
single-mechanism amendment) — re-opening none of it. **Advisory-only; no LLM; reference-not-own + WIRE-1 held as
constraints, not new scope.**

---

## 1. Answers (from the user's explicit direction — not assumptions)

| # | Decision | Answer |
|---|---|---|
| A1 | **Depth** | **Lighter overall** (display-only shared surface) **EXCEPT full rigor** on CON-BR4 language facet (BR-UI-2/BR-UI-3), single-source copy (BR-UI-1), data-testid (BR-UI-5), no-TS (BR-UI-6). |
| A2 | **Full-rigor targets get checkable acceptance criteria** | Yes — each stated as a **pass/fail testable NFR** with explicit AC + tier. |
| A3 | **Aesthetics / perf / bundle** | **Lighter** — record shapes/targets, token values stay **deferred** to NFR-Design/Code-Gen; perf/bundle **observed, non-gating**. |
| A4 | **RoleGate cosmetic (BR-UI-4)** | Include as a testable NFR (coverage — it is invariant-bearing / SEC-4 facet), medium rigor. |
| A5 | **Reference-not-own + WIRE-1** | **Held constraints, not new scope** — realized as one **light structural** guard; no wire/serialization work here (fetches nothing real). |
| A6 | **Test/lint substrate** | Name the concrete substrate so the NFRs are checkable (test runner + RTL + ESLint-based lint + file-scan) — **no heavy new scope**; bundler/deploy topology **deferred** (Infra / deploy-config). |

---

## 2. Ambiguity-check (RUN before generating) — CLEAN, 2 clarity-folds carried from the FD

- **Coverage (no orphan)**: every FD rule maps to a target — BR-UI-1→COPY-1, BR-UI-2→ADVISORY-1, BR-UI-3→GATE-1,
  BR-UI-4→RBAC-1, BR-UI-5→TESTID-1, BR-UI-6→NOTS-1, BR-UI-7→REFNOTOWN-1. ✅
- **Depth matches direction**: full rigor on COPY/ADVISORY/GATE/TESTID/NOTS (+ medium RBAC); lighter/soft on
  AESTHETIC/PERF/A11Y + the SCOPE governance statement. ✅
- **No new scope**: WIRE-1 + reference-not-own reaffirmed as **held**; token values deferred; REFNOTOWN-1 only *checks*
  the existing constraint, it designs nothing. ✅
- **Testable without the backend / wire**: all targets are lints / structural scans / component-render assertions
  runnable with **stubs** (a stub `RoleContext.Provider`); none needs the real WIRE-1 contract. ✅
- **Fold 1 (carried from FD Q2/Q3)**: ADVISORY-1 (lexical lint) and GATE-1 (contextual/attribution test) **share the ONE
  `FORBIDDEN_TERMS` source** — the NFRs must **not** spawn two divergent word-lists. Recorded on both targets.
- **Fold 2 (non-vacuous lint discipline — the auth-rbac/secrets-config mechanism)**: each lint (COPY-1, ADVISORY-1,
  TESTID-1) carries a **detector self-test** proving it flags a synthetic violation, so it can't pass vacuously.

**Verdict: CLEAN** — proceed to generate.

---

## 3. Targets to generate (Part 2)

Artifacts under `guide-docs/build/ui-shell/nfr-requirements/`:
- `nfr-requirements.md` — the `NFR-UI-*` targets (pass/fail + AC + tier + traceability + Security-Guardrails).
- `tech-stack-decisions.md` — D1–Dn (React + Tailwind + no-TS pinned; the test/lint substrate; deferrals).

- [x] P1. Fill answers from the user's direction (§1).
- [x] P2. Run the ambiguity-check (§2) — CLEAN.
- [x] P3. Generate `nfr-requirements.md`.
- [x] P4. Generate `tech-stack-decisions.md`.
- [x] P5. Coverage + guardrail pass; update guide-state + audit; present the NFR-Requirements 2-option gate. **STOP.**

---

## 4. Held constraints (not re-opened)
- The **frozen FD** (BR-UI-1..7 + the design-system surface) is the substrate; NFR builds testable targets **on** it.
- **Reference-not-own (cross-language)** + **WIRE-1** — held; `ui-shell` fetches nothing real; no backend import.
- **SEC-3 / no-LLM / advisory-only** — no secret, no model, no "decision" for system output.
- **Aesthetic token values** deferred to NFR-Design/Code-Gen; **Infrastructure Design** not pre-committed (likely SKIP,
  confirmed after NFR). Settled non-edits stay closed.
