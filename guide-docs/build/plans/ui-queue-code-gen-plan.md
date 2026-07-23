# Code Generation — Plan (Part 1) — `ui-queue` (U5)

**Stage**: BUILD → per-unit loop → Code Generation **Part 1 (Plan)** · **Unit**: U5 `ui-queue` · C5 · Phase 1 · **Date**: 2026-07-09
**Story**: US-UI-1 · **Requirements**: FR-UI-1 (queue) / FR-UI-3 (`data-testid`) / FR-UI-5 (no-TS) / PER-1 (queue perf).
**Built ON** the frozen FD (BR-QUEUE-1..9) + approved NFR Requirements (fourteen `NFR-QUEUE-*`; D6 single injected/capturing
fetch-double; NFR-QUEUE-Fold-1) + approved NFR Design (patterns P1–P10; components C1–C7; D-Fold-1) — **re-opening none**.
**JS/JSX, NO TypeScript; Vitest + React Testing Library + jsdom** — mirroring the realized `ui-shell` convention
(`frontend/src/shell/` + `__tests__/`; shared `vitest.config.js` / `eslint.config.js` / `eslint-rules/`). Full-TDD,
tests/lint-first, leaf-first. **This plan is the single source of truth for ui-queue Code Generation.**

> **Part 1 (Plan) only — NO code generated, NO file under `frontend/src/queue/` created.** After you review + fill the
> Q1–Q6 answers, I run the ambiguity-check, then generate Part 2 **on your explicit go**.

---

## 0. Unit context

- **Stories**: **US-UI-1** (application queue) — the only story this unit implements.
- **Dependencies**: `ui-shell` (frozen U10) — imports `RecommendationBadge`/`ConfidenceBadge`, `Panel`/`AppFrame`,
  `shell/copy` labels + the **one `FORBIDDEN_TERMS`**, `RoleContext` (read-only, not gated). **WIRE-1 R2** consumed **by
  shape** (mocked in tests via the injected `fetchSeam`).
- **Interfaces/contracts**: consumes R2 `GET /applications?page=&size=` → `{items, page:{page,size,total}}` of
  `ApplicationSummary`; error envelope `{error:{code,message,detail?}}`. Emits `onSelect(application_id)` upward.
- **Database entities owned**: **none** (read-only view; no persistence, no migration).
- **Boundaries**: no authz decision (VIEWONLY-1), no router (SELECT-1), no write/commit (U7/U8), no LLM, no real network.

## 1. Component → module map (production under `frontend/src/queue/`)

| Comp | Module (file) | Exports / role | Backs |
|---|---|---|---|
| **C2** | `queue/fetchSeam.js` | the injected/capturing R2 seam: builds the `page`+`size` request, returns the list wrapper / surfaces the error envelope; **JSDoc contract** (Q4); **duck-typed, no formal interface** (D-Fold-1) | FETCH-1, RETRY-1, PERF-1 |
| **C6** | `queue/components/PaginationControls.jsx` | `{ page, size, total, onPageChange, testid }` — derived `isFirstPage`/`isLastPage`/indicator; boundary disabling | PAGINATION-1, TESTID-1 |
| **C3** | `queue/components/QueueStateView.jsx` | `{ state, error, onRetry, testid }` — loading (skeleton, Q1) / empty / error (P3 message-visible/code-testid/detail-never) | ERROR-1, FETCH-1(states), A11Y-1 |
| **C5** | `queue/components/QueueRow.jsx` | `{ summary, onSelect, testid }` — badges (reused from ui-shell) or pending placeholder; emission-only select | PENDING-1, COPY-1, NAMESPACE-1, SELECT-1, TESTID-1 |
| **C4** | `queue/components/QueueTable.jsx` | `{ items, onSelect, testid }` — semantic `<table>` + one `QueueRow` per item | COPY-1(look-up), TESTID-1, A11Y-1 |
| **C1** | `queue/QueueView.jsx` | the stateful owner: calls `fetchSeam` (injected, Q3), holds `{state,page,items,error}`, drives the four-state machine, selects `QueueStateView` vs `QueueTable`+`PaginationControls` | FETCH-1, RETRY-1, VIEWONLY-1(render) |
| **C7** | *(test-only)* `queue/__tests__/*` + shared `eslint-rules`/`vitest.config` extension (Q6) | the StructuralGuard substrate: scans + lints + detector self-tests | TESTID-1, NOTS-1, structural halves |

**Tests** live in `frontend/src/queue/__tests__/` (mirroring `shell/__tests__/`). **No file under `frontend/src/shell/`
is created or modified.**

## 2. TDD test → `NFR-QUEUE-*` target map (every target at its NFR-pinned tier)

| Target | Test (file :: focus) | Tier |
|---|---|---|
| **COPY-1** | `eslint.queue.rules.test.js` (no-inline-label RuleTester, **reuses** ui-shell's `FORBIDDEN_TERMS`) + `queueRow.copy.test.jsx` (badge look-up) + detector self-test | lint (+ RTL) |
| **NAMESPACE-1** | `namespace.test.js` (only `Recommendation` values render; **collision guard** over the reused `FORBIDDEN_TERMS`; no `approve`/`override` string) + synthetic self-test | structural |
| **PENDING-1** | `queueRow.pending.test.jsx` (null rec/conf → `queue-row-pending-<id>`, no badge, row present) | component (RTL) |
| **ERROR-1** | `queueStateView.error.test.jsx` (mocked envelope → `queue-error-message`=message, `queue-error-code`=code not visible, `detail` absent from DOM) | component + structural |
| **RETRY-1** | `queueView.retry.test.jsx` (capturing double fails page **N**; Retry → captured request `page===N`; **teeth: fails if reset to 1**) | component + capturing double |
| **SELECT-1** | `queueRow.select.test.jsx` (`onSelect` spy called once with `application_id`) + `noRouterImport.test.js` (structural: no router/nav import in `queue/`) | component + structural |
| **VIEWONLY-1** | `queueView.roleInvariant.test.jsx` (identical render across stub `RoleContext.Provider` underwriter/auditor/admin) + `noRoleGateImport.test.js` (structural) | component + structural |
| **TESTID-1** | `eslint.queue.rules.test.js` (testid-convention RuleTester `^queue-[a-z]+(-[a-z0-9]+)+$`) + `testid.test.jsx` presence + `isValidTestid` self-test | lint / component |
| **NOTS-1** | `nots.test.js` (0 `.ts`/`.tsx` under `src/queue`; predicate self-test) | structural |
| **FETCH-1** | `queueView.state.test.jsx` (four per-state renders) + `queueView.transition.test.jsx` (one consolidated transition test, Q5) — **all on the single injected capturing double** (Fold-1) | component (RTL) |
| **PAGINATION-1** | `paginationControls.test.jsx` (page 1 → prev disabled; last → next disabled; indicator reflects page/total) | component (RTL) |
| **PERF-1** | `boundedFetch.test.js` (structural: only ever fetches one page; no all-rows path) — latency observed, non-gating | structural + observed |
| **A11Y-1** | recorded/observed — semantic `<table>` + keyboard-focusable controls + accessible labels; **non-gating** (Q6-A of NFR-Req) | observed / soft |
| **SCOPE-1** | governance/exclusion — no test imports a backend module, another UI unit, or exercises the real R2 wire | N/A |

Every `NFR-QUEUE-*` target mapped; no orphan. No test imports a backend module, renders another UI unit, or hits the real
network.

## 3. Leaf-first build order (numbered Part-2 steps — checkboxes, not started)

- [x] **Step 1 — Scaffold + shared-config extension (Q6)**: create `frontend/src/queue/` tree; extend the **shared**
  `vitest.config.js` coverage scope to include `src/queue` and register the reused lints for `src/queue` in
  `eslint.config.js`/`eslint-rules/` — **no file under `src/shell/` touched**.
- [x] **Step 2 — C2 `fetchSeam.js`** (leaf, no deps): the seam interface + **JSDoc contract** (Q4); TDD with the capturing
  double. (backs FETCH-1 seam, RETRY-1, PERF-1)
- [x] **Step 3 — C6 `PaginationControls.jsx`** (pure derived-state, no deps): TDD boundary disabling. (PAGINATION-1)
- [x] **Step 4 — C3 `QueueStateView.jsx`** (depends on `shell/copy` for empty/error text): TDD loading (Q1) / empty /
  error-envelope render. (ERROR-1, FETCH-1 states)
- [x] **Step 5 — C5 `QueueRow.jsx`** (depends on ui-shell `RecommendationBadge`/`ConfidenceBadge` + copy): TDD
  pending/badges + emission-only select. (PENDING-1, COPY-1, NAMESPACE-1, SELECT-1)
- [x] **Step 6 — C4 `QueueTable.jsx`** (composes C5): TDD semantic table + row mapping. (COPY-1 look-up, TESTID-1, A11Y-1)
- [x] **Step 7 — C1 `QueueView.jsx`** (composes C2+C3+C4+C6, owns the state machine): TDD four per-state renders + the
  consolidated transition test (Q5) + retry (page-N teeth) + role-invariant render. (FETCH-1, RETRY-1, VIEWONLY-1)
- [x] **Step 8 — C7 StructuralGuard**: the structural scans + lints over everything above (no-router / no-`RoleGate` /
  no-TS / bounded-fetch / testid convention / `FORBIDDEN_TERMS` reuse), each with a **detector self-test**. (TESTID-1,
  NOTS-1, structural halves)
- [x] **Step 9 — Coverage / quality gate** (§5): run the frontend Vitest suite; assert `src/queue` ≥ 90% (QA-6); confirm
  `src/shell` stays 100% (untouched) and the backend pytest suite is untouched.
- [x] **Step 10 — Code summary**: `guide-docs/build/ui-queue/code/code-summary.md` (module inventory, test→target map,
  folds realized, holds honored, coverage evidence) — mirroring ui-shell's code-summary.

## 4. HOLDS restated (binding through Part 2)

- **ui-shell (frozen) untouched** — `shell/copy` / `FORBIDDEN_TERMS` / `RoleContext` / testid convention **reused via
  import only, never modified**; **no file under `frontend/src/shell/` created or edited**.
- **No local word-list** — the queue reuses the **one** `FORBIDDEN_TERMS` (COPY-1/NAMESPACE-1); no second list.
- **No `RoleGate` composition** (VIEWONLY-1); **no router import** (SELECT-1); **`fetchSeam` stays a duck-typed seam with
  no formal interface** (D-Fold-1).
- **WIRE-1 R2 consumed by shape only** — no real network call in the unit or its tests; **real `fetchSeam` wiring +
  R2 route implementation deferred to the composition root / Build & Test**.
- **No LLM. No TypeScript** (NOTS-1). **tier-B run stays unauthorized and out of scope. No other unit started.**

## 5. Coverage / quality gate (frontend Vitest — NOT the Python pytest suite)

- **Runner**: this is a JS/React unit → **Vitest coverage folded into the frontend test run** (`npm run test:cov`), the
  established `ui-shell` convention — **NOT** the backend `pytest --cov=backend/*` suite.
- **Baseline (from `ui-shell`)**: `frontend/src/shell` = **100%** (statements/branches/functions/lines), **47 Vitest tests**.
  ui-queue adds `src/queue` coverage; **the shell's 100% must not regress** (no shell file touched, so it stands) and
  `src/queue` must meet **QA-6 ≥ 90%**.
- **Backend untouched (confirm)**: this is a pure frontend addition — the backend **pytest suite (850 passed / 31 skipped**
  per the admin-cli completion) must remain **completely untouched** (zero backend files modified; separate runner/tree).
  `testresults.txt` records the frontend result **alongside**, not merged.

## 6. Open Code-Gen-only questions ([Answer] tags — lettered; full text below)

> Answer at this gate; I embed the Q&A, run the ambiguity-check, then generate Part 2 on your explicit go.

### Q1 — Loading-state skeleton markup/count (now that `queue-state-loading` must be implemented)
- **A.** A small **fixed count of skeleton `<tr>` placeholder rows** (e.g. **3**) inside the table shell, with
  `queue-state-loading` on the container; count is a **cosmetic constant** (Q2-A of NFR-Req deferred it — asserted only by
  container presence + "no real rows", not the number). *(Recommended.)*
- **B.** A single spinner / "Loading…" text (no skeleton rows), `queue-state-loading` on it.
- **C.** Skeleton rows sized dynamically to the page `size`.

`[Answer]:` **A** — a fixed count (3) of skeleton placeholder rows inside the table shell, with `queue-state-loading` on
the container; the count is a cosmetic constant, asserted only by container presence + "no real rows", not the number.

### Q2 — Default page `size` value (N2 — must be concretized now)
- **A.** **20**. *(Recommended — a common queue page size; bounded per PER-1.)*
- **B.** 10.
- **C.** 25 or 50.

`[Answer]:` **A** — default page size **20**.

### Q3 — `fetchSeam` injection mechanism into `QueueView` (Q1-A of NFR-Design said "prop/context")
- **A.** **Plain prop** — `QueueView` receives `fetchSeam` as a prop; tests pass the capturing double directly; the
  composition root passes the real seam. *(Recommended — `QueueView` is the top of the view, a single injection point;
  simplest, and the capturing double is trivial.)*
- **B.** **React Context** (`QueueFetchContext` + `useQueueFetch()`), mirroring ui-shell's `RoleContext` pattern; tests
  wrap in a provider.

`[Answer]:` **A** — plain prop; `QueueView` receives `fetchSeam` as a prop; tests pass the capturing double directly;
the composition root passes the real seam.

### Q4 — `fetchSeam` failure convention (drives the JSDoc contract wording)
- **A.** `fetchSeam(page, size)` **rejects** on non-2xx, the rejection carrying the parsed error envelope
  `{error:{code,message,detail}}`; resolves `{items, page:{page,size,total}}` on success. `QueueView` `catch` → error
  state. *(Recommended — idiomatic promise rejection; RETRY-1/ERROR-1 assert on the caught envelope.)*
- **B.** `fetchSeam` **resolves a discriminated union** `{ok:true, data}` | `{ok:false, error}`; `QueueView` branches on
  `ok`.

`[Answer]:` **A** — `fetchSeam(page, size)` rejects on non-2xx, the rejection carrying the parsed error envelope
`{error:{code,message,detail}}`; resolves `{items, page:{page,size,total}}` on success; `QueueView` catch → error state.
(Refined by CG-Fold-1: the seam normalizes transport/malformed failures to a well-formed envelope too.)

### Q5 — Consolidated state-transition test file location
- **A.** Its **own file** `queueView.transition.test.jsx`, alongside the per-state `queueView.state.test.jsx`.
  *(Recommended — one-file-per-concern, matches ui-shell's test layout.)*
- **B.** In the **same file** as `QueueView`'s per-state tests.

`[Answer]:` **A** — its own file `queueView.transition.test.jsx`, alongside the per-state `queueView.state.test.jsx`.

### Q6 — Shared frontend config extension for the queue (coverage scope + lint registration) without touching `ui-shell` src
- **A.** **Extend the shared frontend config** — add `src/queue` to `vitest.config.js` coverage `include`, and register
  the reused `FORBIDDEN_TERMS`/testid lints for `src/queue` in `eslint.config.js`/`eslint-rules/`. These are **frontend-wide
  build infra, not `ui-shell` source** — **no file under `src/shell/` is modified**, so the ui-shell-frozen hold stands.
  *(Recommended — consistent with ui-shell's single frontend test run.)*
- **B.** **Queue-scoped config** (a separate Vitest project / ESLint override) leaving the shared config untouched.

`[Answer]:` **A** — extend the shared frontend config (`vitest.config.js` coverage include + `eslint.config.js` /
`eslint-rules/` lint registration for `src/queue`); frontend-wide build infra, no file under `src/shell/` modified.

## 7. Part 2 execution note

On your explicit go (after answers + a CLEAN ambiguity-check): execute Steps 1–10 in order, TDD/leaf-first, marking each
`[ ]`→`[x]` in this plan as completed; then present the standardized 2-option completion message (this is the **last**
stage for `ui-queue`; next is either **Request Changes** or **Continue** — the per-unit loop for U5 completes, and the
next move is a separate decision).
