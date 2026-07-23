# Code Generation Plan (Part 1) — `ui-shell` (`ui-common` / U10)

**Phase / Stage**: BUILD → Code Generation, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags, **TDD tests-first**)
**Loop position**: `ui-shell` · FD ✅ · NFR Requirements ✅ · NFR Design ✅ · **Infrastructure Design ✅ SKIPPED-logged 2026-07-07**
→ **Code Generation ← here (the LAST stage for `ui-shell`; the FIRST frontend/React unit — a NEW track).**
**Unit**: U10 `ui-shell` · **Date**: 2026-07-07 · **Stack**: React + Tailwind, **NO TypeScript** (FR-UI-5) · **Depth**:
mirror NFR — lighter overall EXCEPT full rigor on the invariant / AC-bearing targets.
**Status**: **Plan — awaiting `[Answer]:` tags. NO code generated this stage; NO files under `frontend/` created. Stop
after this plan.**

Realizes the **4 approved NFR-Design components (C1–C4)** + the test/lint substrate as code under `frontend/src/shell/`,
built **ON** the frozen FD (incl. GATE-1's BR-UI-3 clarification + the RoleGate single-mechanism amendment), the approved
`NFR-UI-*` targets, and the NFR-Design patterns — **re-opening none**. **TDD: every `NFR-UI-*` target gets its test/lint
first**, at the NFR-pinned tier. **No backend production import; no real fetch; no view/gate render** (U7 owns the
render-context attribution). **No TypeScript. No LLM. WIRE-1 untouched** (external boundary).

---

## 1. What Code-Gen builds (and what it must NOT touch)

### 1.1 Builds
`shell/copy` (labels + the one `FORBIDDEN_TERMS` object), `shell/tokens` (categories/shapes — VALUES per Q4),
`shell/components` primitives (AppFrame, Panel, ReadOnlyRegion, RecommendationBadge, ConfidenceBadge, RoleGate),
`shell/session` (RoleContext + useCurrentRole seam), and the test/lint substrate (ESLint rules + detector self-tests;
Vitest + RTL + jsdom) — each with its test/lint first, at the NFR-pinned tier. Plus the **Step-0 frontend package**
scaffold (Q1).

### 1.2 Does NOT touch (held closed)
- **No backend production import** anywhere in `frontend/src/shell/`; **no real network fetch** (REFNOTOWN-1); Role /
  Recommendation / Confidence consumed as **value shapes** only.
- **No view or gate rendered/tested** — the human-gate render-context attribution is **`ui-approval-gate` (U7)**'s.
- **No TypeScript** (no `.ts`/`.tsx`, no `tsconfig`). **No LLM.** **WIRE-1** (api-contract / RoleContext population) is
  the composition-root's external boundary — **not designed or called** here.
- No Python/backend files; no `PROJECT-BRIEF.md`/`user-journey.md` edits; no built unit's code; Vercel/bundler **deploy**
  topology stays `deploy-config`'s (D6).

### 1.3 Guardrails held (skill)
CON-BR4 language facet (advisory copy single source; human-gate framing vocabulary; `-RECOMMEND` preserved; "recommendation"
not "decision"); SEC-4 cosmetic-only RBAC (no authz decision in the shell); reference-not-own (no backend import, no
view/gate render); **no LLM**; determinism (pure presentational components; no unseeded randomness / wall-clock).

---

## 2. Module / package layout (`frontend/src/shell/`) — C1–C4 mapping

```text
frontend/                              # Step 0 — NEW frontend package (Q1); JS-native, no TS
├── package.json                       # vitest, @testing-library/react, jsdom, eslint (+ custom rule) — no TS toolchain
├── vitest.config.js                   # jsdom env; coverage on src/shell (Q5)
├── eslint.config.js                   # flat config; the no-inline-string / advisory-vocabulary / testid rules (Q3)
├── .gitignore                         # node_modules, coverage
└── src/
    └── shell/
        ├── copy/
        │   ├── index.js               # C1 — RECOMMENDATION_LABELS, CONFIDENCE_LABELS, ROLE_LABELS,
        │   │                          #      COMMIT_ACTION_LABELS {approve, override}, ADVISORY_VOCABULARY
        │   └── forbiddenTerms.js       # C1 — the ONE FORBIDDEN_TERMS object (ADVISORY-1 + GATE-1 both import it)
        ├── tokens/
        │   └── tokens.js              # C4 — token categories/shapes; VALUES per Q4 (deferred vs pinned)
        ├── components/
        │   ├── AppFrame.jsx           # C2
        │   ├── Panel.jsx              # C2
        │   ├── ReadOnlyRegion.jsx     # C2
        │   ├── RecommendationBadge.jsx# C2 — looks up label from C1 by value (no inline)
        │   ├── ConfidenceBadge.jsx    # C2 — looks up label from C1 by value
        │   └── RoleGate.jsx           # C2 — { can, children, fallback }; useCurrentRole(); no role prop; no authz call
        ├── session/
        │   └── roleContext.js         # C3 — RoleContext + useCurrentRole() seam (populated later by WIRE-1)
        └── __tests__/                 # co-located Vitest specs + ESLint rule-tester fixtures
            ├── copy.badge.test.jsx        # COPY-1(b) RTL badge look-up
            ├── vocabulary.test.js          # GATE-1 set-disjointness + fold-1 same-object + fold-2 self-test
            ├── eslint.rules.test.js        # COPY-1 no-inline + ADVISORY-1 lexical + TESTID-1 (RuleTester) + self-tests
            ├── nots.test.js                # NOTS-1 file/config scan
            ├── rolegate.test.jsx           # RBAC-1 stub RoleContext.Provider + static no-authz-import
            └── refnotown.test.js           # REFNOTOWN-1 no backend import / no real fetch + self-test
```

| Component / item | Module / file | Backs |
|---|---|---|
| **C1 `shell/copy`** | `copy/index.js` + `copy/forbiddenTerms.js` | COPY-1, ADVISORY-1, GATE-1 |
| **C2 `shell/components`** | `components/*.jsx` | COPY-1(b), TESTID-1, RBAC-1 |
| **C3 `shell/session`** | `session/roleContext.js` | RBAC-1 |
| **C4 `shell/tokens`** | `tokens/tokens.js` | AESTHETIC-1 |
| Test/lint substrate | `eslint.config.js` (+ custom rule), `__tests__/*` | COPY-1, ADVISORY-1, GATE-1, TESTID-1, NOTS-1, RBAC-1, REFNOTOWN-1 |

---

## 3. TDD test → target map (every `NFR-UI-*` at its NFR-pinned tier)

| Target | Test / lint (file :: name) | Tier | Assertion |
|---|---|---|---|
| **COPY-1** | ESLint `no-inline-label` (`eslint.rules.test.js`) + `copy.badge.test.jsx::badge_looks_up_by_value` | lint (+ RTL) | no label literal outside `shell/copy`; badge renders label by value look-up; **self-test** flags a synthetic inline |
| **ADVISORY-1** | ESLint `advisory-vocabulary` over `FORBIDDEN_TERMS` (`eslint.rules.test.js`) | lint | bare `DECLINE` / "decision"/"approved"/"declined" as system output fail; canonical labels pass; **self-test** |
| **GATE-1** | `vocabulary.test.js::commitaction_disjoint_from_recommendation` + `::override_not_decline_recommend` + `::same_forbidden_terms_object` + `::detects_synthetic_collision` | structural / unit | `COMMIT_ACTION_LABELS ∩ RECOMMENDATION_LABELS = ∅`; `override` ≠ `DECLINE-RECOMMEND`; **same `FORBIDDEN_TERMS` object** as ADVISORY-1 (fold 1); self-test (fold 2). **No view/gate render — U7's** |
| **TESTID-1** | ESLint / test `data-testid` convention (`eslint.rules.test.js`) | lint / component | every interactive primitive exposes a stable `data-testid`; **self-test** flags a missing/misnamed id |
| **NOTS-1** | `nots.test.js::no_ts_files` + `::no_tsconfig` | structural | zero `.ts`/`.tsx`; no `tsconfig*` in the unit |
| **RBAC-1** | `rolegate.test.jsx::underwriter_renders_act` + `::auditor_hidden_or_disabled` + `::no_authz_import` | component + structural | via a **stub `RoleContext.Provider`**; `RoleGate` calls no authz fn / imports no backend module |
| **REFNOTOWN-1** | `refnotown.test.js::no_backend_import` + `::no_real_fetch` + `::detects_synthetic_violation` | structural | no import from a backend path; no real `fetch`/`axios`; self-test |
| **AESTHETIC-1** | — (categories/shapes; VALUES per Q4) | N/A / soft | no gating test |
| **PERF-1 / A11Y-1** | — (observed / soft) | observed | non-gating |
| **SCOPE-1** | — (governance/exclusion) | N/A | documented boundary; render-context → U7 |

No `NFR-UI-*` target unmapped; **no test imports a backend module, renders a view/gate, or exercises WIRE-1**.

---

## 4. Implementation order (leaf-first, tests/lint-first per step)

0. **Step 0 — Scaffold the frontend package** (Q1, Q2, Q5): `frontend/package.json` (vitest, @testing-library/react,
   jsdom, eslint + custom rule — **no TS**), `vitest.config.js` (jsdom + coverage on `src/shell`), `eslint.config.js`
   (flat), `.gitignore`, the `src/shell/**` dirs. **Adds NO Python/backend dependency; touches NO built unit's code.**
1. **C1 `shell/copy`** (`copy/index.js` + `copy/forbiddenTerms.js`) — **tests/lint first**: ADVISORY-1 lexical lint,
   GATE-1 set-disjointness (+ same-`FORBIDDEN_TERMS`-object, self-tests), COPY-1 no-inline lint.
2. **C4 `shell/tokens`** (`tokens/tokens.js`) — categories/shapes; VALUES per **Q4**.
3. **C2 primitives** — AppFrame/Panel/ReadOnlyRegion, then RecommendationBadge/ConfidenceBadge (look up C1). **Tests
   first**: COPY-1(b) RTL badge look-up; TESTID-1 data-testid convention.
4. **C3 `shell/session`** (`session/roleContext.js`) — RoleContext + `useCurrentRole()` seam (stub-injectable).
5. **RoleGate** (`components/RoleGate.jsx`, depends on C3) — **tests first**: RBAC-1 stub-provider render + no-authz-import.
6. **Cross-cutting scans** — NOTS-1 (file/config) + REFNOTOWN-1 (no backend import / no real fetch) + self-tests.
7. **Coverage gate** (Q5) — Vitest coverage ≥90% on `src/shell` own JS; run as a **separate** frontend command, **not**
   the Python pytest suite; confirm the **733-passing backend does not regress** (different runner/tree, untouched).
8. **Code summary** — `guide-docs/build/ui-shell/code/code-summary.md` (module list + test→target map + flagged notes) +
   back-annotate guide-state.md; standardized completion + 2-option gate.

---

## 5. Clarifying questions (fill each `[Answer]:` tag)

Letter after each `[Answer]:` tag; last option = Other. These decide **Code-Gen realization** — they do **not** re-open
the FD, the NFR targets, or the patterns.

## Question 1 — Step-0 frontend package scaffolding (NEW track)
How is the frontend package introduced?

A) **A new `frontend/` package** with `package.json` (vitest, @testing-library/react, jsdom, eslint + a small custom
   rule — **plain JS, no TS toolchain**), `vitest.config.js`, `eslint.config.js` (flat), `.gitignore`, and `src/shell/**`.
   npm scripts: `test`, `test:cov`, `lint`. **Adds NO Python/backend dependency; touches NO built unit's code.**
   **Recommended.**
B) Put the shell under an existing path / no dedicated `frontend/` package (rejected — the unit-of-work tree pins
   `frontend/src/shell/`; a dedicated JS package keeps the new track cleanly separate from the Python backend).
C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 2 — Bundler / dev-server presence in THIS unit
Does `ui-shell` add a bundler/dev-server now?

A) **NO bundler/dev-server in this unit** — `ui-shell` is a **source-level library** exercised only by **Vitest (jsdom)**;
   the bundler/dev-server (e.g. Vite) + Vercel **deploy** topology stay **`deploy-config`'s P2 scope** (D6). Keeps
   Code-Gen to source + tests. **Recommended.**
B) Add a Vite dev-server/bundler now (rejected for this unit — deploy topology is deferred; a runtime app shell belongs
   with the view units / deploy-config, not the shared design-system).
C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 3 — Lint mechanism for the copy/vocabulary/testid checks
How are COPY-1 / ADVISORY-1 / TESTID-1 enforced?

A) **ESLint (flat config) with a small custom rule / `no-restricted-syntax`** reading the **single `FORBIDDEN_TERMS`
   source** — build-failing; **GATE-1's set-disjointness is a Vitest structural test** (not a lint) over the copy module;
   each lint ships an **ESLint `RuleTester` detector self-test**. **Recommended.**
B) Vitest-only string scans instead of ESLint (weaker for the *inline-literal* checks — ESLint sees the AST/JSX; keep
   Vitest for the structural set-disjointness + scans).
C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 4 — `shell/tokens` VALUES: pin the refined-minimalism values now, or defer? *(genuinely open)*
AESTHETIC-1 pinned the **direction** (refined-minimalism) and deferred VALUES. For Code-Gen:

A) **DEFER concrete values** — author `shell/tokens` as **named CSS/Tailwind theme variables (categories/shapes) with
   neutral placeholder values** so primitives compile and tests run, but the **final palette / type pairing / spacing
   scale are set later** (Code-Gen of the view units / a design pass). Consistent with AESTHETIC-1. **Recommended.**
B) **PIN the concrete refined-minimalism values now** — choose the distinctive-but-professional type pairing, restrained
   palette, spacing scale in this unit (still no purple-gradient / Inter-Roboto-Arial default). Pulls the aesthetic
   decision forward into the shared shell.
C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 5 — Frontend coverage runner + gate (separate from pytest)
How is the QA-6 ≥90% gate run for the frontend?

A) **Vitest coverage (v8 provider)** gated **≥90%** on **`frontend/src/shell`** own JS, run as a **separate
   `npm run test:cov`** command — **NOT** part of the Python `pytest` suite. State explicitly that it uses a **different
   runner and tree**, so the **733-passing backend suite is untouched and does not regress**; `testresults.txt` notes the
   frontend result alongside (not merged into) the pytest total. **Recommended.**
B) Attempt to merge frontend coverage into the Python coverage total (rejected — different language/runner; keep the two
   suites separate, both green).
C) Other (please describe after [Answer]: tag below)

[Answer]: A

## Question 6 — Test framework confirm + depth + completion
Confirm the substrate + Code-Gen depth.

A) **Vitest + React Testing Library + jsdom** (NFR-Design-pinned) for component targets (COPY-1(b), RBAC-1) + ESLint for
   the lints + Vitest structural for GATE-1/NOTS-1/REFNOTOWN-1. **Standard** Code-Gen: full TDD build of C1–C4 + substrate
   + every `NFR-UI-*` test at its tier; a `guide-docs/build/ui-shell/code/code-summary.md`; guide-state.md back-annotated;
   then the standardized **2-option** completion gate. **Recommended.**
B) Minimal (rejected — the CON-BR4 language facet + the folds must be real, build-failing checks).
C) Other (please describe after [Answer]: tag below)

[Answer]: A

---

## 6. Reference-not-own / no-LLM / WIRE-1 confirmation (explicit)
- **No backend production import** anywhere in `frontend/src/shell/`; **no real network fetch** (REFNOTOWN-1, structurally
  verified). Role / Recommendation / Confidence consumed as **value shapes** only. **No view or gate rendered/tested** —
  U7 owns the render-context attribution.
- **WIRE-1** (api-contract / RoleContext population) is **not designed or called** here — `RoleContext` is a seam fed by a
  stub in tests. **No TypeScript. No LLM.**

---

## 7. Constraints & settled items held (not re-opened)
- FD (BR-UI-1..7 + design-system surface, incl. GATE-1's BR-UI-3 clarification + RoleGate single-mechanism) + approved
  `NFR-UI-*` + NFR-Design patterns/components (C1–C4) are the substrate — Code-Gen realizes them, re-opening none.
- **Reference-not-own** — no backend import; no view/gate render; RBAC cosmetic-only; verified by REFNOTOWN-1 / RBAC-1.
- **No TypeScript** (NOTS-1); **advisory-only / CON-BR4** (COPY-1/ADVISORY-1/GATE-1); **no LLM**; **WIRE-1 untouched**.
- **Aesthetic token VALUES** per Q4. **Deploy topology (bundler/Vercel)** = `deploy-config` (D6). Settled non-edits stay
  closed: `PROJECT-BRIEF.md`, `user-journey.md`, every built unit's code/design.

---

## 8. Next step (STOP here)
Fill the six `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check
(clarification file only if needed), then generate the `ui-shell` code **TDD tests/lint-first, leaf-first** per §4, run the
frontend suite + coverage, write the code summary, back-annotate guide-state.md, and present the standardized completion +
2-option message. **No code is generated, and no files under `frontend/` are created, until the answers are in and
checked.**
