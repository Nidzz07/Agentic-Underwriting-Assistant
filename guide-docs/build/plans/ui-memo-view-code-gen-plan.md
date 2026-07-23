# Code Generation — Plan (Part 1) — `ui-memo-view` (U6)

**Stage**: BUILD → per-unit loop → Code Generation **Part 1 (Plan)** · **Unit**: U6 `ui-memo-view` · C5 · Phase 1 · **Date**: 2026-07-09
**Story**: US-UI-2 · **Requirements**: FR-MEMO-3 (memo view) / NFR-EXPLAIN-1 (explainability) / FR-UI-3 (`data-testid`) / FR-UI-5 (no-TS).
**Built ON** the frozen FD (BR-MEMO-1..11) + approved NFR Requirements (fourteen `NFR-MEMO-*`; D6 single injected/capturing
fetch-double; NFR-MEMO-Fold-A/B/C) + approved NFR Design (patterns P1–P10; components C1–C9; NFR-DESIGN-Fold-1) —
**re-opening none**. **JS/JSX, NO TypeScript; Vitest + React Testing Library + jsdom** — mirroring the realized
`ui-shell`/`ui-queue` convention (`frontend/src/<unit>/` + `__tests__/`; shared `vitest.config.js` / `eslint.config.js` /
`eslint-rules/`). Full-TDD, tests/lint-first, leaf-first. **This plan is the single source of truth for ui-memo-view Code Generation.**

> **Part 1 (Plan) only — NO code generated, NO file under `frontend/src/memoView/` created.** After you review + fill the
> Q1–Q6 answers, I run the ambiguity-check, then generate Part 2 **on your explicit go**.

---

## 0. Unit context

- **Stories**: **US-UI-2** (memo view) — the only story this unit implements.
- **Dependencies**: `ui-shell` (frozen U10) — imports `ReadOnlyRegion` (**first use**), `RecommendationBadge`/
  `ConfidenceBadge`, `Panel`/`AppFrame`, `shell/copy` labels + the **one `FORBIDDEN_TERMS`**, `RoleContext` (read-only, not
  gated). `ui-queue` (frozen U5) — its `fetchSeam`/`StructuralGuard`/testid-lint are **mirrored as a convention, NOT
  imported**. **WIRE-1 R4** consumed **by shape** (mocked in tests via the injected `memoFetchSeam`).
- **Interfaces/contracts**: consumes R4 `GET /applications/{application_id}/memo` → `MemoView`
  `{ application_id, recommendation_id|null, status:"ready"|"pending", profile|null, report|null, memo|null }`; the `ready`
  `memo` is a `DecisionMemo` (three regions L/D/RO + M); error envelope `{error:{code,message,detail?}}`. **Emits nothing**
  (view-only, no outward action).
- **Database entities owned**: **none** (read-only view; no persistence, no migration).
- **Boundaries**: no authz decision (VIEWONLY-1), no router (VIEWONLY-1), no write/commit (U7/U8), no LLM, no real network;
  **renders `narrative_prose` as-is, never lints/rewrites it** (BR-MEMO-2 governance).

## 1. Component → module map (production under `frontend/src/memoView/`)

| Comp | Module (file) | Exports / role | Backs |
|---|---|---|---|
| **C2** | `memoView/memoFetchSeam.js` | the own-local injected/capturing R4 seam: builds the request **by `applicationId`**, returns the `MemoView` body / surfaces the error envelope; **JSDoc contract** (Q3); **duck-typed, no formal interface** (D-Fold); **mirrors ui-queue's `fetchSeam`, NOT imported** | FETCH-1, ERROR-1(retry), PERF-1 |
| **C6** | `memoView/components/CitationsList.jsx` | `{ citedRuleIds, testid }` — L sub-list, **delivered order** (no sort); empty → neutral copy | LISTORDER-1, TESTID-1 |
| **C7** | `memoView/components/MissingInfoRegion.jsx` | `{ items, testid }` — D list, **delivered order**; each row `detail` + `MISSING_INFO_SOURCE_LABELS[source]`; empty → neutral copy | LISTORDER-1, COPY-1, TESTID-1 |
| **C8** | `memoView/components/ReadOnlyRecommendationRegion.jsx` | `{ recommendation, confidence, testid }` — **composes the frozen `ReadOnlyRegion`** (`aria-readonly`, **first use**) + `RecommendationBadge`/`ConfidenceBadge`, engine-attributed; the **sole** rec/conf render site | SEPARATION-1(RO), COPY-1, NAMESPACE-1, TESTID-1 |
| **C5** | `memoView/components/NarrativeRegion.jsx` | `{ narrative, testid }` **ONLY** — renders `narrative_prose` read-only; composes `CitationsList`. **Carries the header comment** documenting `{narrative, testid}`-only props / **no rec/conf prop or path** (NFR-DESIGN-Fold-1 — an explicit deliverable) | SEPARATION-1(L), TESTID-1 |
| **C4** | `memoView/components/ProfileContextHeader.jsx` | `{ profile, testid }` — minimal identifying read-only header (fields per Q2) | A11Y-1, TESTID-1 |
| **C3** | `memoView/components/MemoStateView.jsx` | `{ state, error, onRetry, testid }` — loading (placeholder, Q1) / pending ("not yet drafted") / error (message-visible/code-testid/detail-never) | ERROR-1, FETCH-1(states), PENDING-1(render), A11Y-1 |
| **C1** | `memoView/MemoView.jsx` | the stateful owner: calls `memoFetchSeam` (injected prop), holds `{state, view, error}`, drives the four-state machine + **status-discriminator** selection, and **composes the three regions as SIBLINGS** (establishes the structural isolation) | FETCH-1, ERROR-1(transition), PENDING-1(discriminator), VIEWONLY-1(render), SEPARATION-1(sibling composition) |
| **C9** | *(test-only)* `memoView/__tests__/*` + shared `eslint-rules`/`vitest.config` extension (Q6) | the StructuralGuard substrate: scans + lints + detector self-tests | TESTID-1, NOTS-1, structural halves |
| — | `memoView/copy.js` | `MEMO_COPY` / `MISSING_INFO_SOURCE_LABELS` — memo-local UI strings + source labels (lint-subject; not a domain-enum label source) | supports COPY-1/ADVISORY-1 |

**Tests** live in `frontend/src/memoView/__tests__/` (mirroring `shell/__tests__/` + `queue/__tests__/`). **No file under
`frontend/src/shell/` or `frontend/src/queue/` is created or modified.**

> **NarrativeRegion header comment (explicit deliverable, not implicit)** — C5 ships with a header comment (the frozen
> `ReadOnlyRegion.jsx` / `fetchSeam.js` convention) stating: *props `{narrative, testid}` only — no `recommendation`/
> `confidence` prop or path; the RO region (`ReadOnlyRecommendationRegion`) is the sole holder (CON-BR2-TYPE)*. This makes
> the by-construction isolation self-evident in isolation (NFR-DESIGN-Fold-1).

## 2. TDD test → `NFR-MEMO-*` target map (every target at its NFR-pinned tier)

| Target | Test (file :: focus) | Tier |
|---|---|---|
| **COPY-1** | `eslint.memo.rules.test.js` (no-inline-label RuleTester, **reuses** ui-shell's `FORBIDDEN_TERMS`) + `missingInfoRegion.test.jsx` / `readOnlyRecommendationRegion.test.jsx` (label look-up) + detector self-test | lint (+ RTL) |
| **ADVISORY-1** | `eslint.memo.rules.test.js` (advisory-vocabulary RuleTester over `src/memoView/**` **static code**; `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS`) + synthetic self-test; **no assertion against `narrative_prose` content** (governance) | lint / structural |
| **NAMESPACE-1** | `namespace.test.jsx` (only `Recommendation` values render, incl. `DECLINE-RECOMMEND` never bare `DECLINE`; **collision guard** over the reused `FORBIDDEN_TERMS`; no `approve`/`override`) + synthetic self-test | structural |
| **SEPARATION-1** *(load-bearing, teeth)* | `memoView.separation.test.jsx` (DOM-containment, Fold-B): `!narrative.contains(readonly) && !readonly.contains(narrative)`; `within(readonly).getByTestId('memo-recommendation')`+`memo-confidence` present; `within(narrative).queryByTestId('memo-recommendation')` **null**; RO carries `aria-readonly` — **teeth: fails if rec rendered inside/under narrative** | component (RTL + jsdom) |
| **ERROR-1** | `memoStateView.error.test.jsx` (mocked envelope → `memo-error-message`=message, `memo-error-code`=code not visible, `detail` absent from DOM) + `memoView.retry.test.jsx` (capturing double fails id **X**; Retry → captured request `applicationId===X`; **teeth: fails if a different/absent id**) | component + capturing double + structural |
| **VIEWONLY-1** | `memoView.roleInvariant.test.jsx` (identical render across stub `RoleContext.Provider` underwriter/auditor/admin) + `noRoleGateImport.test.js` + `noRouterImport.test.js` (structural) | component + structural |
| **PENDING-1** *(discriminator teeth)* | `memoView.pending.test.jsx` (Fold-C): `status:"pending"` → `memo-state-pending`, no region; **`status:"ready"` with empty `missing_information`/`cited_rule_ids` → renders ready, NOT pending** (teeth on the `status` discriminator) | component (RTL) |
| **LISTORDER-1** *(no-re-sort teeth)* | `missingInfoRegion.test.jsx` + `citationsList.test.jsx` (populated non-sorted fixture → rendered order equals input order; **teeth: fails if client sort introduced**; empty-lists fixture → neutral copy) | component (RTL) |
| **TESTID-1** | `eslint.memo.rules.test.js` (testid-convention RuleTester `^memo-[a-z]+(-[a-z0-9]+)+$` **incl. region-level testids**) + `testid.test.jsx` presence (region testids asserted) + `isValidMemoTestid` self-test | lint / component |
| **NOTS-1** | `nots.test.js` (0 `.ts`/`.tsx` under `src/memoView`; predicate self-test) | structural |
| **FETCH-1** | `memoView.state.test.jsx` (four per-state renders: loading/ready/pending/error) + `memoView.transition.test.jsx` (one consolidated transition test, Q5) — **all on the single injected capturing double** (Fold-A) | component (RTL) |
| **PERF-1** | `boundedFetch.test.js` (structural: fetches a single resource by `applicationId`; no list/all-rows path) — latency observed, non-gating | structural + observed |
| **A11Y-1** | recorded/observed — semantic regions + headings + `aria-readonly` (frozen `ReadOnlyRegion`) + keyboard-focusable Retry + accessible labels; **non-gating** (Q7-A of NFR-Req) | observed / soft |
| **SCOPE-1** | governance/exclusion — no test imports a backend module, `ui-queue`, another UI unit, or exercises the real R4 wire; **no test asserts `narrative_prose` content** | N/A |

Every `NFR-MEMO-*` target mapped; no orphan. No test imports a backend module, `ui-queue`, renders another UI unit, or
hits the real network.

## 3. Leaf-first build order (numbered Part-2 steps — EXECUTED)

- [x] **Step 1 — Scaffold + shared-config extension (Q6)**: created `frontend/src/memoView/` tree + `memoView/copy.js`;
  extended the **shared** `vitest.config.js` coverage scope to include `src/memoView` and registered the reused lints + the
  new `memo-testid-convention` rule (`eslint-rules/memoView.js`) for `src/memoView` in `eslint.config.js` — **no file under
  `src/shell/` or `src/queue/` touched; thresholds unchanged**.
- [x] **Step 2 — C2 `memoFetchSeam.js`** (leaf, no deps): the seam interface (build R4 request by `applicationId`) +
  **JSDoc contract** (Q3) + `normalizeError` (CG-MEMO-Fold-1); TDD with the capturing double. (FETCH-1 seam, ERROR-1 retry, PERF-1)
- [x] **Step 3 — C6 `CitationsList.jsx` + C7 `MissingInfoRegion.jsx`** (pure order-preserving lists): TDD delivered-order
  rendering + source labels + empty-list neutral copy. (LISTORDER-1, COPY-1)
- [x] **Step 4 — C8 `ReadOnlyRecommendationRegion.jsx`** (composes frozen `ReadOnlyRegion` + badges — **first use**):
  TDD `aria-readonly` wrapper + engine-attributed badges; sole rec/conf render site. (SEPARATION-1 RO, COPY-1, NAMESPACE-1)
- [x] **Step 5 — C5 `NarrativeRegion.jsx`** (depends on C6; **carries the header-comment guarantee**): TDD narrative render
  + citations composition; the header comment shipped as an explicit deliverable. (SEPARATION-1 L)
- [x] **Step 6 — C4 `ProfileContextHeader.jsx`** (minimal field set, Q2): TDD read-only header render. (A11Y-1, TESTID-1)
- [x] **Step 7 — C3 `MemoStateView.jsx`** (depends on memo-local copy for pending/error/loading text): TDD loading (Q1) /
  pending / error-envelope render. (ERROR-1, FETCH-1 states, PENDING-1 render)
- [x] **Step 8 — C1 `MemoView.jsx`** (composes C2+C3+C4+C5+C7+C8, owns the state machine, **establishes the sibling
  composition**): TDD four per-state renders + the consolidated transition test (Q5) + retry (same-id teeth) +
  status-discriminator (empty-lists ready teeth) + the **SEPARATION-1 DOM-containment teeth** + role-invariant render.
  (FETCH-1, ERROR-1, PENDING-1, SEPARATION-1, VIEWONLY-1)
- [x] **Step 9 — C9 StructuralGuard**: the structural scans + lints over everything above (no-router / no-`RoleGate` /
  no-TS / bounded-fetch / no-`ui-queue`-import / testid convention incl. region testids / `FORBIDDEN_TERMS` reuse), each
  with a **detector self-test**. (TESTID-1, NOTS-1, structural halves)
- [x] **Step 10 — Coverage / quality gate** (§5): ran the frontend Vitest suite — **161 passed / 43 files**; `src/memoView`
  **100%** (QA-6 ≥90% PASSED); `src/shell` + `src/queue` stay **100%** (untouched); ESLint clean; backend pytest untouched.
- [x] **Step 11 — Code summary**: `guide-docs/build/ui-memo-view/code/code-summary.md` written (module inventory,
  test→target map, folds realized, holds honored, coverage evidence) — mirroring ui-queue's code-summary.

## 4. HOLDS restated (binding through Part 2)

- **ui-shell (frozen) untouched** — `shell/copy` / `FORBIDDEN_TERMS` / `RoleContext` / **`ReadOnlyRegion`** / testid
  convention **reused via import only, never modified**; **no file under `frontend/src/shell/` created or edited**.
- **ui-queue (frozen) untouched** — its `fetchSeam`/`StructuralGuard`/testid-lint pattern is **mirrored, never imported**;
  **no file under `frontend/src/queue/` created or edited**.
- **No local word-list** — the view reuses the **one** `FORBIDDEN_TERMS` (COPY-1/ADVISORY-1/NAMESPACE-1); no second list.
- **No `RoleGate` composition** (VIEWONLY-1); **no router import** (VIEWONLY-1); **`memoFetchSeam` stays a duck-typed seam
  with no formal interface** (D-Fold).
- **By-construction structural isolation is a HARD requirement** — `NarrativeRegion` has **no `recommendation`/`confidence`
  prop or path**; `ReadOnlyRecommendationRegion` is the **sole** rec/conf holder; the header comment ships (NFR-DESIGN-Fold-1).
  Not optional.
- **WIRE-1 R4 consumed by shape only** — no real network call in the unit or its tests; **real `memoFetchSeam` wiring +
  R4 route implementation deferred to the composition root / Build & Test**.
- **`narrative_prose` rendered as-is** — never linted or rewritten (BR-MEMO-2 governance; the lints cover static code only).
- **No LLM. No TypeScript** (NOTS-1). **tier-B run stays unauthorized and out of scope. No other unit started.**

## 5. Coverage / quality gate (frontend Vitest — NOT the Python pytest suite)

- **Runner**: this is a JS/React unit → **Vitest coverage folded into the frontend test run** (`npm run test:cov`), the
  established convention — **NOT** the backend `pytest --cov=backend/*` suite.
- **Baseline (from `ui-queue` completion)**: `frontend/src/shell` = **100%** and `frontend/src/queue` = **100%** (98 Vitest
  tests). ui-memo-view adds `src/memoView` coverage; **neither `src/shell` nor `src/queue` may regress** (no file in either
  is touched, so both stand) and `src/memoView` must meet **QA-6 ≥ 90%**.
- **Backend untouched (confirm)**: this is a pure frontend addition — the backend **pytest suite (850 passed / 31 skipped**
  since admin-cli) must remain **completely untouched** (zero backend files modified; separate runner/tree).
  `testresults.txt` records the frontend result **alongside**, not merged.

## 6. Open Code-Gen-only questions ([Answer] tags — lettered; full text below)

> Answered by the user (2026-07-09) — **all A**; the full Q&A is embedded here per the standing convention. Ambiguity-check
> ran after the answers (§6.5, CLEAN); Part 2 executed (§3 Steps 1–11 [x]).

### Q1 — Loading-state placeholder markup (`memo-state-loading` must be implemented)
- **A.** A **single neutral placeholder** — a "Loading memo" text / spinner block with `memo-state-loading` on the
  container, **no memo region rendered while loading** (asserted by container presence + "no region", not by markup
  detail). *(Recommended — the memo view has no table to skeleton like the queue; a single placeholder fits the
  single-resource render; the exact markup is a cosmetic detail.)*
- **B.** A **three-region skeleton** mimicking the ready layout (placeholder narrative + lists + RO block).
- **C.** A bare spinner only.

`[Answer]:` **A** — a single neutral placeholder ("Loading memo" text/spinner block) with `memo-state-loading` on the
container, no memo region rendered while loading; asserted by container presence + "no region", not markup detail.

### Q2 — Minimal profile-context-header field set (`ProfileContextHeader` — deferred by NFR-Design D11)
- **A.** A **minimal identifying set**: `application_id`, applicant name (`demographics.full_name`), derived age
  (`age_years_derived`), and `requested_cover_amount`. *(Recommended — enough to identify the application in context
  without turning the header into a full profile dump; demographics is display-only here, never a rule/feature input, so
  CON-BR1 is unaffected.)*
- **B.** **`application_id` only** (barest header).
- **C.** A **fuller set** (add income, employment, smoking status, BMI, etc.).

`[Answer]:` **A** — a minimal identifying set: `application_id`, applicant name (`demographics.full_name`), derived age
(`age_years_derived`), and `requested_cover_amount`; enough to identify the application without a full profile dump.
Demographics is display-only here, never a rule/feature input, so CON-BR1 is unaffected. *(Ambiguity-check verified all
four field names exist verbatim on the frozen `ApplicantProfile` — no renaming needed.)*

### Q3 — `memoFetchSeam` failure convention (drives the JSDoc contract wording)
- **A.** `memoFetchSeam(applicationId)` **rejects** on non-2xx, the rejection carrying a **normalized** error envelope
  `{error:{code,message,detail}}` (an **own-local `normalizeError`** mirroring ui-queue's CG-Fold-1 — a transport/malformed
  failure → a synthesized `network_error` envelope, **NOT imported** from ui-queue); resolves the `MemoView` body on
  success. `MemoView` `catch` → error state. *(Recommended — idiomatic; ERROR-1/Retry assert on the caught envelope; the
  seam is the single normalization boundary so `MemoStateView` never unpacks a raw exception.)*
- **B.** `memoFetchSeam` **resolves a discriminated union** `{ok:true, data}` | `{ok:false, error}`; `MemoView` branches on `ok`.

`[Answer]:` **A** — `memoFetchSeam(applicationId)` rejects on non-2xx, the rejection carrying a normalized error envelope
`{error:{code,message,detail}}` via an **own-local `normalizeError`** mirroring ui-queue's CG-Fold-1 (**NOT imported**);
resolves the `MemoView` body on success; `MemoView` catch → error state. *(CG-MEMO-Fold-1: the own-local `normalizeError`
produces the SAME shape as WIRE-1 §4 / ui-queue's, so ERROR-1 is structurally consistent across both units — via the
shared WIRE-1 contract, not a code import.)*

### Q4 — The two Fold-C ready-memo fixtures — construction (PENDING-1 empty-lists vs LISTORDER-1 populated non-sorted)
- **A.** **Two explicit named fixtures in a shared test-fixtures module** (`memoView/__tests__/fixtures.js`): an
  **empty-lists ready memo** (`missing_information: []`, `cited_rule_ids: []`) and a **populated non-sorted ready memo**
  (deliberately out-of-order `missing_information` + `cited_rule_ids`), reused across PENDING-1 / LISTORDER-1 / SEPARATION-1
  / FETCH-1. *(Recommended — DRY, mirrors the single-double discipline (Fold-A); two intentional fixtures, no per-test
  ad-hoc data.)*
- **B.** **Inline per-test** fixtures constructed in each test file.

`[Answer]:` **A** — two explicit named fixtures in a shared test-fixtures module (`memoView/__tests__/fixtures.js`): an
empty-lists ready memo and a populated non-sorted ready memo, reused across PENDING-1/LISTORDER-1/SEPARATION-1/FETCH-1.
*(Ambiguity-check ii: a `makeMemoView(overrides)` factory + named fixtures keeps it extensible, not a dumping ground.)*

### Q5 — Consolidated state-transition test file location (mirroring ui-queue Q5)
- **A.** Its **own file** `memoView.transition.test.jsx`, alongside the per-state `memoView.state.test.jsx`.
  *(Recommended — one-file-per-concern, matches ui-shell/ui-queue's test layout.)*
- **B.** In the **same file** as `MemoView`'s per-state tests.

`[Answer]:` **A** — its own file `memoView.transition.test.jsx`, alongside the per-state `memoView.state.test.jsx`.

### Q6 — Shared frontend config extension for the memo view (coverage scope + lint registration) without touching frozen src
- **A.** **Extend the shared frontend config** — add `src/memoView` to `vitest.config.js` coverage `include`, and register
  the reused `FORBIDDEN_TERMS` lints + a **new `memo-testid-convention` rule** (in `eslint-rules/memoView.js`, mirroring
  `eslint-rules/queue.js`) for `src/memoView` in `eslint.config.js`. These are **frontend-wide build infra, not `ui-shell`
  or `ui-queue` source** — **no file under `src/shell/` or `src/queue/` is modified; `vitest.config.js` thresholds
  unchanged**, so both frozen coverage gates stand. *(Recommended — consistent with the single frontend test run.)*
- **B.** **memoView-scoped config** (a separate Vitest project / ESLint override) leaving the shared config untouched.

`[Answer]:` **A** — extend the shared frontend config (`vitest.config.js` coverage include + a new
`eslint-rules/memoView.js` `memo-testid-convention` rule + `eslint.config.js` registration for `src/memoView`); no file
under `src/shell/` or `src/queue/` modified; thresholds unchanged.

## 6.5 Ambiguity-check (RUN 2026-07-09, after the Q1–Q6 answers) — **CLEAN, no STOP** (1 fold + 2 verifications)

Ran against the six answers (all A) + the frozen FD (BR-MEMO-1..11) + approved NFR Requirements (fourteen `NFR-MEMO-*`) +
approved NFR Design (P1–P10, C1–C9, all folds). **No genuine gap.** The three user-flagged checks:
- **(i) Q2 field names vs the frozen `ApplicantProfile`** — **VERIFIED verbatim**: `application_id`, `demographics.full_name`,
  `age_years_derived`, `requested_cover_amount` all exist with those exact names in `backend/intake/schema.py`. No
  renaming/mapping needed.
- **(ii) Q4 shared-fixtures extensibility** — resolved: `fixtures.js` exports a **`makeMemoView(overrides)` factory** + the
  two named canonical fixtures (+ `pendingMemoView` / `errorEnvelope`); a future variant is one override, so the module
  stays extensible and does not become a dumping ground.
- **(iii) Q3 own-local `normalizeError` shape consistency** — **CG-MEMO-Fold-1**: the own-local `normalizeError` produces
  the identical `{error:{code,message,detail}}` envelope as WIRE-1 §4 (and ui-queue's CG-Fold-1). ERROR-1's assertions are
  therefore structurally consistent across both UI units **because both conform to the shared WIRE-1 contract**, NOT
  because of any code import (ui-queue remains un-imported — enforced by `noUiQueueImport.test.js`). No gap, no STOP.

## 7. Part 2 execution note — EXECUTED (2026-07-09)

Executed Steps 1–11 (TDD/leaf-first) on the user's explicit go after the CLEAN ambiguity-check. **Result: 161 Vitest tests
passed (43 files), 100% coverage on `src/memoView` (QA-6 PASSED); `src/shell` + `src/queue` stay 100% (untouched); ESLint
clean; backend pytest 850/31 untouched.** See `guide-docs/build/ui-memo-view/code/code-summary.md`. Presenting the
standardized 2-option completion message (the **last** stage for `ui-memo-view`).
