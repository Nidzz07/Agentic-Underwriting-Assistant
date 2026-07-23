# Code Summary — `ui-shell` (`ui-common` / U10)

**Stage**: BUILD → Code Generation (Part 2, executed) · **Date**: 2026-07-07
**Unit**: U10 `ui-shell` — the FIRST frontend/React unit (JS-native, **NO TypeScript**).
**Depth**: full-TDD; lighter overall EXCEPT full rigor on the invariant / AC-bearing targets.
**Result**: ESLint clean · **47 Vitest tests passed** · **100% coverage** on `frontend/src/shell` (QA-6 ≥90% PASSED).
Backend pytest suite **untouched** (zero backend files modified; separate runner/tree — 733 passed / 3 skipped / 99.76% stands).

Built ON the frozen FD + approved `NFR-UI-*` + NFR-Design patterns/components (C1–C4) — **re-opening none**. TDD tests/lint-first,
leaf-first per plan §4. Six Code-Gen answers all **A**; ambiguity-check CLEAN with four clarity-folds (below).

---

## 1. Module inventory (production — `frontend/src/shell/`)

| Component | File | Exports | Backs |
|---|---|---|---|
| **C1 copy** | `copy/index.js` | `RECOMMENDATION_LABELS`, `CONFIDENCE_LABELS`, `ROLE_LABELS`, `COMMIT_ACTION_LABELS {approve, override}`, `ADVISORY_VOCABULARY` | COPY-1, ADVISORY-1, GATE-1 |
| **C1 forbidden** | `copy/forbiddenTerms.js` | the ONE `FORBIDDEN_TERMS` object (both lints consume it) | ADVISORY-1, GATE-1 (fold 1) |
| **C4 tokens** | `tokens/tokens.js` | `CSS_VARIABLES`, `STATUS_ACCENT`, `TOKENS` (named vars + **neutral placeholder values**, Q4) | AESTHETIC-1 |
| **C2 primitives** | `components/AppFrame.jsx`, `Panel.jsx`, `ReadOnlyRegion.jsx`, `RecommendationBadge.jsx`, `ConfidenceBadge.jsx`, `RoleGate.jsx` | presentational primitives; badges look up labels from C1; RoleGate cosmetic | COPY-1(b), TESTID-1, RBAC-1 |
| **C3 session** | `session/roleContext.js` | `RoleContext`, `RoleProvider`, `useCurrentRole()` (seam; populated later by WIRE-1) | RBAC-1 |

**Scaffold / substrate (test-only, not production components):** `package.json` (vitest, @testing-library/react, jsdom,
eslint — **no TS toolchain**), `vitest.config.js` (jsdom + v8 coverage on `src/shell`), `vitest.setup.js`, `eslint.config.js`
(flat), `.gitignore`, `eslint-rules/index.js` (the three custom lints + exported detectors). npm scripts: `test`, `test:cov`, `lint`.

**RoleGate prop shape** = `{ can, children, fallback }` (`can ∈ {"act","read"}`); reads Role via `useCurrentRole()` — **no `role` prop**.

---

## 2. Test → `NFR-UI-*` target map (every target at its NFR-pinned tier)

| Target | Test (file :: name) | Tier | Outcome |
|---|---|---|---|
| **COPY-1** | `eslint.rules.test.js` no-inline-label RuleTester + `copy.badge.test.jsx` look-up | lint (+ RTL) | ✅ (self-test flags synthetic inline) |
| **ADVISORY-1** | `eslint.rules.test.js` advisory-vocabulary RuleTester + `findForbiddenSystemOutput` self-test | lint | ✅ (bare DECLINE / decision / approved / declined fail; canonical pass) |
| **GATE-1** | `vocabulary.test.js` key-disjoint + override≠DECLINE-RECOMMEND + **same FORBIDDEN_TERMS object** + synthetic-collision self-test | structural / unit | ✅ (no view/gate render — U7 owns render-context) |
| **TESTID-1** | `eslint.rules.test.js` testid-convention RuleTester + `testid.test.jsx` presence + `isValidTestid` self-test | lint / component | ✅ |
| **NOTS-1** | `nots.test.js` no_ts_files + no_tsconfig + predicate self-test | structural | ✅ (0 `.ts`/`.tsx`, 0 tsconfig) |
| **RBAC-1** | `rolegate.test.jsx` underwriter/auditor/admin/null via stub `RoleContext.Provider` + no-authz-import static | component + structural | ✅ |
| **REFNOTOWN-1** | `refnotown.test.js` no_backend_import + no_real_fetch + synthetic-violation self-test | structural | ✅ |
| **AESTHETIC-1** | — (categories/shapes; VALUES deferred per Q4) | N/A / soft | tokens compile; values deferred |
| **PERF-1 / A11Y-1** | — (observed) | observed | non-gating |
| **SCOPE-1** | — (governance/exclusion) | N/A | render-context → U7; no view/backend/WIRE-1 touched |

**47 tests, all passing.** Every `NFR-UI-*` target mapped; no test imports a backend module, renders a view/gate, or exercises WIRE-1.

---

## 3. Folds realized (real, build-failing, non-vacuous)

- **Fold 1** — ONE `FORBIDDEN_TERMS` source object, TWO consumers: `vocabulary.test.js::same_forbidden_terms_object`
  asserts `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS` (the lint and the copy module resolve to the identical object).
- **Fold 2** — every detector ships a non-vacuous self-test (RuleTester invalid fixtures MUST error; `findForbiddenSystemOutput` /
  `isValidTestid` / `findBackendImport` / `findRealFetch` / `isTsArtifact` / `keyNamespacesDisjoint` each flag a synthetic).

## 4. Realization notes (clarity-folds — flagged for gate review; no artifact re-opened)

1. **ESLint custom-rule detail**: the three lints read the SINGLE `shell/copy` + `FORBIDDEN_TERMS` source (never a second
   list — protects fold 1); the copy module is exempt from the two vocabulary lints (it *defines* the vocabulary). GATE-1 is a
   Vitest structural test, not a lint. Each lint ships a `RuleTester` self-test.
2. **`data-testid` convention**: FD/NFR pin `shell-<primitive>-<purpose>`; concretized as `^shell-[a-z]+(-[a-z0-9]+)+$`.
   TESTID-1 = the ESLint naming rule (any literal `data-testid`) **+** the `testid.test.jsx` presence test over primitives.
3. **RoleGate cosmetic capability map**: mirrors the frozen `auth_rbac` role semantics as VALUE SHAPES (not imported) —
   underwriter = act+read; auditor = read-only; admin = not-an-underwriting-actor. The two RBAC-1 AC cells (underwriter/act→render,
   auditor/act→hidden) + auditor/read→render are the invariant-bearing tests; admin/read cells are cosmetic only (SEC-4:
   server-enforced). Owns NO authorization decision; imports no `auth_rbac`; calls no `authorize()`; issues no fetch.
4. **GATE-1 set-disjointness**: realized over the enum **KEY namespaces** (case-sensitive: `{approve,override}` ∩
   `{APPROVE,REFER,DECLINE-RECOMMEND}` = ∅) plus the specific `override ≠ DECLINE-RECOMMEND` guard at key AND label level —
   exactly FD §2.1 ("distinct value space and namespace"; "override never rendered as DECLINE-RECOMMEND"). The benign
   human-`approve` vs system-`APPROVE` English-word overlap is key-distinct by casing per §2.1, so label-value disjointness is
   NOT asserted (it would false-fail on that intended overlap).

## 5. Holds honored (not violated)

- **NO TypeScript** anywhere (NOTS-1 green: 0 `.ts`/`.tsx`, 0 tsconfig). **No backend production import; no real fetch**
  (REFNOTOWN-1 green). **No view or gate rendered/tested** — U7 owns the render-context attribution (GATE-1 delegation).
- **WIRE-1 untouched** — `RoleContext` is a seam fed by a stub in tests; no api-contract authored or called. **No LLM.**
- **Aesthetic token VALUES deferred** (Q4 — neutral placeholders). **Bundler / Vercel topology** = `deploy-config` (D6), not here.
- Backend pytest suite **untouched** (separate runner/tree); `testresults.txt` notes the frontend result **alongside**, not merged.
- Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, every built unit's code/design.

## 6. Frontend coverage evidence

`npm run test:cov` → `frontend/src/shell`: Statements 100% (166/166) · Branches 100% (17/17) · Functions 100% (8/8) ·
Lines 100% (166/166). **QA-6 ≥90% PASSED.** (Full detail in `testresults.txt`, frontend section.)
