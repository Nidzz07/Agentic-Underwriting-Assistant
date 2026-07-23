# Code Summary — `ui-queue` (U5)

**Stage**: BUILD → Code Generation (Part 2, executed) · **Date**: 2026-07-09
**Unit**: U5 `ui-queue` — the application-queue view; the FIRST UI unit that actually fetches (WIRE-1 R2, mocked).
**Depth**: lighter (display) + async-state addendum · full-TDD, tests/lint-first, leaf-first per plan §3.
**Result**: ESLint clean · **98 Vitest tests passed** (22 files) · **100% coverage** on `frontend/src/queue` (QA-6 ≥90%
PASSED). `frontend/src/shell` stays **100% (untouched)**. Backend pytest suite **untouched** (separate runner/tree —
850 passed / 31 skipped / 99.82% stands; not re-run for this frontend unit).

Built ON the frozen FD (BR-QUEUE-1..9) + approved `NFR-QUEUE-*` + NFR-Design patterns P1–P10 / components C1–C7 —
**re-opening none**. Six Code-Gen answers all **A**; ambiguity-check CLEAN with **CG-Fold-1** (below).

---

## 1. Module inventory (production — `frontend/src/queue/`)

| Comp | File | Exports | Backs |
|---|---|---|---|
| **C2 fetchSeam** | `fetchSeam.js` | `DEFAULT_PAGE_SIZE` (20), `buildQueueRequest`, `normalizeError`, `createQueueFetch` | FETCH-1, RETRY-1, PERF-1 |
| **C1 QueueView** | `QueueView.jsx` | `QueueView` — stateful owner; four-state machine; injected `fetchSeam` prop | FETCH-1, RETRY-1, VIEWONLY-1 |
| **C3 QueueStateView** | `components/QueueStateView.jsx` | loading (3 skeleton rows) / empty / error (P3) | ERROR-1, FETCH-1(states), A11Y-1 |
| **C4 QueueTable** | `components/QueueTable.jsx` | semantic `<table>`; one `QueueRow` per item | COPY-1, TESTID-1, A11Y-1 |
| **C5 QueueRow** | `components/QueueRow.jsx` | badges (reused ui-shell) or pending; emission-only select | PENDING-1, COPY-1, NAMESPACE-1, SELECT-1 |
| **C6 PaginationControls** | `components/PaginationControls.jsx` | derived prev/next/indicator; boundary disabling | PAGINATION-1, TESTID-1 |
| — | `copy.js` | `QUEUE_COPY` — queue-local UI strings (realization note §4) | (supports the above) |

**Scaffold / substrate (Q6-A — shared frontend infra, NOT `src/shell`):** `eslint-rules/queue.js` (new — the
`queue-testid-convention` rule + `isValidQueueTestid`); `eslint.config.js` (+1 block for `src/queue`, reusing shell's
`no-inline-label`/`advisory-vocabulary`); `vitest.config.js` (include paths added; **thresholds unchanged**). **No file
under `frontend/src/shell/` was created or edited.**

**C7 StructuralGuard (test-only):** the file/import/lint scans below, each with a detector self-test.

---

## 2. Test → `NFR-QUEUE-*` target map (every target at its NFR-pinned tier — all green)

| Target | Test (file :: focus) | Tier | Outcome |
|---|---|---|---|
| **COPY-1** | `eslint.queue.rules.test.js` (no-inline-label RuleTester, reused) + `queueRow.test.jsx` look-up | lint (+ RTL) | ✅ (self-test flags synthetic inline) |
| **NAMESPACE-1** | `namespace.test.jsx` (system-only render; `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS`) | structural | ✅ (single source, no 2nd word-list) |
| **PENDING-1** | `queueRow.test.jsx` (null → `queue-row-pending-<id>`, no badge, row present) | component | ✅ |
| **ERROR-1** | `queueStateView.test.jsx` (message visible / code testid-only+hidden / detail never in DOM) | component + structural | ✅ |
| **RETRY-1** | `queueView.retry.test.jsx` (page-N teeth — fails if reset to page 1) | component + capturing double | ✅ |
| **SELECT-1** | `queueRow.test.jsx` (onSelect once w/ id) + `noRouterImport.test.js` | component + structural | ✅ |
| **VIEWONLY-1** | `queueView.roleInvariant.test.jsx` (identical HTML across roles) + `noRoleGateImport.test.js` | component + structural | ✅ |
| **TESTID-1** | `eslint.queue.rules.test.js` (queue-`<element>`-`<purpose>` RuleTester + `isValidQueueTestid` self-test) | lint / component | ✅ |
| **NOTS-1** | `nots.test.js` (0 `.ts`/`.tsx` under `src/queue`; predicate self-test) | structural | ✅ |
| **FETCH-1** | `queueView.state.test.jsx` (4 per-state) + `queueView.transition.test.jsx` (consolidated, Q5-A) | component | ✅ (single injected double, Fold-1) |
| **PAGINATION-1** | `paginationControls.test.jsx` (both boundaries) | component | ✅ |
| **PERF-1** | `boundedFetch.test.js` (page+size always present; no real fetch in unit) | structural + observed | ✅ (non-gating latency) |
| **A11Y-1** | `queueTable.test.jsx` (semantic table/columnheaders) | observed / soft | ✅ (non-gating) |
| **SCOPE-1** | governance — no test imports a backend module or exercises the real R2 wire | N/A | ✅ |

**98 tests, all passing.** Every `NFR-QUEUE-*` target mapped; no test imports a backend module or hits the real network.

## 3. Folds realized (real, non-vacuous)

- **NFR-QUEUE-Fold-1** — ONE injected/capturing fetch-double serves every state/transition test; `fetchSeam` is a plain
  prop (Q3-A); tests program the double per case. No divergent double patterns.
- **CG-Fold-1** — `fetchSeam` normalizes **every** failure to a well-formed `{error:{code,message,detail}}` envelope
  (`normalizeError`): a parsed non-2xx envelope passes through; a transport error / malformed body → a synthesized
  `network_error` envelope. So `QueueStateView` (ERROR-1) never unpacks a raw exception. Verified in `fetchSeam.test.js`.
- **Fold-B** — Retry re-fetches the **last-requested page** (position-preserving); `queueView.retry.test.jsx` has TEETH
  (asserts the retry requested page N, not page 1).
- **D-Fold-1** — `fetchSeam` is a duck-typed injected seam with **no formal interface** (admin-cli precedent; no-TS
  a fortiori); JSDoc + the capturing double self-document the contract.

## 4. Realization notes (flagged; no artifact re-opened)

1. **`queue/copy.js`** — a small queue-local UI-strings module (empty/pending/retry/pagination/column text) was added so
   components inline no chrome text. Not a domain-enum label source (those stay in `shell/copy`, looked up via the reused
   badges). Consistent with the single-source discipline; not a new design decision.
2. **Loading skeleton** = a fixed **3** placeholder rows (Q1-A) — a cosmetic constant; tests assert only container
   presence + "no real table while loading", never the count.
3. **`queue-error-code`** rendered in a `hidden` span — present for test/console assertion, not visible UI text (ERROR-1).
4. **Config extension (Q6-A)** touched only shared frontend infra (`eslint.config.js`, `vitest.config.js`,
   `eslint-rules/queue.js`); `vitest.config.js` **thresholds were left unchanged** (only include paths added), so
   ui-shell's coverage gate is not weakened. Per-file queue coverage reported (all 100%), so nothing is masked.

## 5. Holds honored (not violated)

- **ui-shell (frozen) untouched** — no `frontend/src/shell/` file created or edited; reused via import only
  (`RecommendationBadge`/`ConfidenceBadge`/`Panel`/`copy`/`FORBIDDEN_TERMS`/`RoleContext`). **No new word-list.**
- **No `RoleGate` composition** (VIEWONLY-1); **no router import** (SELECT-1); **no real network call** (PERF-1 —
  transport injected); **no LLM; no TypeScript** (NOTS-1: 0 `.ts`/`.tsx`).
- **WIRE-1 R2 consumed by shape only** — the real `fetchSeam` transport wiring + R2 route implementation stay deferred to
  the composition root / Build & Test. **tier-B NOT authorized; no other unit started.**
- Backend pytest suite **untouched** (separate runner/tree); `testresults.txt` records the frontend result **alongside**.

## 6. Frontend coverage evidence

`npm run test:cov` → `frontend/src/queue`: Statements 100% · Branches 100% · Functions 100% · Lines 100%.
Whole frontend (shell + queue): 381/381 statements, 70/70 branches, 20/20 functions, 381/381 lines = **100%**.
**QA-6 ≥90% PASSED.** ESLint: clean (`npm run lint`, exit 0). (Full detail in `testresults.txt`, frontend section.)
