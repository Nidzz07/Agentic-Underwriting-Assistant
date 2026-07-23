# Code Summary — `ui-memo-view` (U6)

**Stage**: BUILD → Code Generation (Part 2, executed) · **Date**: 2026-07-09
**Unit**: U6 `ui-memo-view` — the decision-memo view; the SECOND UI unit that fetches (WIRE-1 R4, mocked) and the FIRST to
render the DecisionMemo three-region shape + compose the frozen `ReadOnlyRegion`.
**Depth**: lighter (display) + fetch-lifecycle addendum + three-region read-only-separation addendum · full-TDD,
tests/lint-first, leaf-first per plan §3.
**Result**: ESLint clean · **161 Vitest tests passed** (43 files) · **100% coverage** on `frontend/src/memoView` (QA-6 ≥90%
PASSED). `frontend/src/shell` **and** `frontend/src/queue` stay **100% (untouched)**. Backend pytest suite **untouched**
(separate runner/tree — 850 passed / 31 skipped / 99.82% stands; not re-run for this frontend unit).

Built ON the frozen FD (BR-MEMO-1..11) + approved `NFR-MEMO-*` + NFR-Design patterns P1–P10 / components C1–C9 —
**re-opening none**. Six Code-Gen answers all **A**; ambiguity-check CLEAN with **CG-MEMO-Fold-1** (below).

---

## 1. Module inventory (production — `frontend/src/memoView/`)

| Comp | File | Exports | Backs |
|---|---|---|---|
| **C2 memoFetchSeam** | `memoFetchSeam.js` | `buildMemoRequest`, `normalizeError`, `createMemoFetch` | FETCH-1, ERROR-1(retry), PERF-1 |
| **C1 MemoView** | `MemoView.jsx` | `MemoView` — stateful owner; four-state machine; status discriminator; sibling composition; injected `memoFetchSeam` prop | FETCH-1, ERROR-1, PENDING-1, VIEWONLY-1, SEPARATION-1 |
| **C3 MemoStateView** | `components/MemoStateView.jsx` | loading (single neutral placeholder, Q1-A) / pending / error (P3) | ERROR-1, FETCH-1(states), PENDING-1(render), A11Y-1 |
| **C4 ProfileContextHeader** | `components/ProfileContextHeader.jsx` | minimal identifying header (application_id, name, age, requested cover — Q2-A) | A11Y-1, TESTID-1 |
| **C5 NarrativeRegion** | `components/NarrativeRegion.jsx` | L region; `{ narrative, citedRuleIds }` — **no rec/conf prop**; ships the header comment (NFR-DESIGN-Fold-1) | SEPARATION-1(L), TESTID-1 |
| **C6 CitationsList** | `components/CitationsList.jsx` | L sub-list; delivered order; empty neutral copy | LISTORDER-1, TESTID-1 |
| **C7 MissingInfoRegion** | `components/MissingInfoRegion.jsx` | D list; delivered order; `detail` + source label; empty neutral copy | LISTORDER-1, COPY-1, TESTID-1 |
| **C8 ReadOnlyRecommendationRegion** | `components/ReadOnlyRecommendationRegion.jsx` | RO region; composes frozen `ReadOnlyRegion` (aria-readonly, first use) + badges; SOLE rec/conf render site | SEPARATION-1(RO), COPY-1, NAMESPACE-1, TESTID-1 |
| — | `copy.js` | `MEMO_COPY` + `MISSING_INFO_SOURCE_LABELS` — memo-local UI strings (lint-subject; realization note §4) | supports COPY-1/ADVISORY-1 |

**Scaffold / substrate (Q6-A — shared frontend infra, NOT `src/shell` or `src/queue`):** `eslint-rules/memoView.js` (new —
the `memo-testid-convention` rule + `isValidMemoTestid`); `eslint.config.js` (+1 block for `src/memoView`, reusing shell's
`no-inline-label`/`advisory-vocabulary`); `vitest.config.js` (include paths added; **thresholds unchanged**). **No file
under `frontend/src/shell/` or `frontend/src/queue/` was created or edited.**

**C9 StructuralGuard (test-only):** the file/import/lint scans below, each with a detector self-test.

---

## 2. Test → `NFR-MEMO-*` target map (every target at its NFR-pinned tier — all green)

| Target | Test (file :: focus) | Tier | Outcome |
|---|---|---|---|
| **COPY-1** | `eslint.memo.rules.test.js` (no-inline-label RuleTester, reused) + region look-up | lint (+ RTL) | ✅ (self-test flags synthetic inline) |
| **ADVISORY-1** | `eslint.memo.rules.test.js` (advisory-vocabulary RuleTester over static code) | lint / structural | ✅ (no narrative_prose assertion — governance) |
| **NAMESPACE-1** | `namespace.test.jsx` (system-only render; `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS`) | structural | ✅ (single source, no 2nd word-list) |
| **SEPARATION-1** | `memoView.separation.test.jsx` (DOM-containment teeth: RO ≠ L, non-nested; rec/conf only in RO; aria-readonly) | component (RTL+jsdom) | ✅ **(load-bearing; teeth)** |
| **ERROR-1** | `memoStateView.test.jsx` (message/code/detail) + `memoView.retry.test.jsx` (same-applicationId teeth) | component + capturing double | ✅ |
| **VIEWONLY-1** | `memoView.roleInvariant.test.jsx` (identical HTML across roles) + `noRoleGateImport.test.js` + `noRouterImport.test.js` | component + structural | ✅ |
| **PENDING-1** | `memoView.pending.test.jsx` (status discriminator teeth: ready+empty-lists ≠ pending) | component | ✅ |
| **LISTORDER-1** | `citationsList.test.jsx` + `missingInfoRegion.test.jsx` (delivered order, both lists; no re-sort) | component | ✅ |
| **TESTID-1** | `eslint.memo.rules.test.js` (`memo-<element>-<purpose>` RuleTester incl. region testids + `isValidMemoTestid` self-test) + `testid.test.jsx` | lint / component | ✅ |
| **NOTS-1** | `nots.test.js` (0 `.ts`/`.tsx` under `src/memoView`; predicate self-test) | structural | ✅ |
| **FETCH-1** | `memoView.state.test.jsx` (4 per-state) + `memoView.transition.test.jsx` (consolidated, Q5-A) | component | ✅ (single injected double, Fold-A) |
| **PERF-1** | `boundedFetch.test.js` (single memo by applicationId; no list path; no real fetch) | structural + observed | ✅ (non-gating latency) |
| **A11Y-1** | semantic regions + `aria-readonly` + focusable Retry (via separation/state tests) | observed / soft | ✅ (non-gating) |
| **SCOPE-1** | `noUiQueueImport.test.js` (ui-queue mirrored, never imported); no backend/real-wire/narrative_prose assertion | N/A | ✅ |

**161 tests, all passing.** Every `NFR-MEMO-*` target mapped; no test imports a backend module, `ui-queue`, or hits the
real network.

## 3. Folds realized (real, non-vacuous)

- **NFR-MEMO-Fold-A** — ONE injected/capturing fetch-double serves every state/transition test; `memoFetchSeam` is a
  plain prop (Q1-A); tests program the double per case. No divergent double patterns.
- **NFR-MEMO-Fold-B** — SEPARATION-1's DOM-containment teeth use jsdom `Node.contains()` (arbitrary-depth) + scoped
  `within()` queries: `!narrative.contains(readonly) && !readonly.contains(narrative)`, rec/conf present in RO and **null**
  in the narrative. Sound sibling non-containment, not testid-presence-only. Verified in `memoView.separation.test.jsx`.
- **NFR-MEMO-Fold-C** — two distinct ready fixtures (`emptyListsReadyMemoView` + `unsortedReadyMemoView`) in
  `__tests__/fixtures.js` (+ a `makeMemoView` factory): the empty-lists fixture proves PENDING-1's discriminator teeth (and
  the empty-list neutral-copy branch); the non-sorted fixture proves LISTORDER-1's no-re-sort teeth. No shared/ad-hoc fixture.
- **CG-MEMO-Fold-1** — `memoFetchSeam` normalizes **every** failure to a well-formed `{error:{code,message,detail}}`
  envelope (own-local `normalizeError`) — the SAME shape as WIRE-1 §4 (and ui-queue's CG-Fold-1), so `MemoStateView`
  (ERROR-1) never unpacks a raw exception. Structural consistency across both UI units comes from the shared WIRE-1
  contract, **not** from importing ui-queue. Verified in `memoFetchSeam.test.js`.
- **NFR-DESIGN-Fold-1** — the by-construction isolation is self-evident in isolation: `NarrativeRegion` carries a header
  comment stating `{ narrative, citedRuleIds }` only, **no rec/conf prop or path**; the RO region is the sole holder.

## 4. Realization notes (flagged; no artifact re-opened)

1. **`memoView/copy.js`** — a memo-local UI-strings module (loading/pending/retry/heading/empty text + the
   `MISSING_INFO_SOURCE_LABELS` for the four `MissingInfoSource` values) so components inline no chrome. Lint-subject
   (MEMO-Fold-1): it passes the reused `no-inline-label` + `advisory-vocabulary` lints; not a domain-enum label source
   (those stay in `shell/copy`, looked up via the reused badges).
2. **`NarrativeRegion` prop set** = `{ narrative, citedRuleIds }` — `citedRuleIds` is **L-region content** it forwards to
   `CitationsList`. The load-bearing isolation guarantee is specifically the **absence of any `recommendation`/`confidence`
   prop/path**, which holds; the header comment documents exactly this. (The FD shorthand "{narrative, testid} only" meant
   "no rec/conf"; citations are L content.)
3. **`memo-error-code`** rendered in a `hidden` span — present for test/console assertion, not visible UI text (ERROR-1).
4. **Loading placeholder** = a single neutral "Loading memo" node (Q1-A) — no three-region skeleton; the memo view has no
   table to skeleton. Tests assert container presence + "no memo region while loading", not markup detail.
5. **Config extension (Q6-A)** touched only shared frontend infra (`eslint.config.js`, `vitest.config.js`,
   `eslint-rules/memoView.js`); `vitest.config.js` **thresholds unchanged** (only include paths added), so the ui-shell and
   ui-queue coverage gates are not weakened. Per-file memoView coverage reported (all 100%), nothing masked.
6. **`memo-testid-convention` pattern** = `^memo-[a-z0-9]+(-[a-z0-9]+)*$` — accepts the documented inventory's
   single-purpose root/badge testids (`memo-view`, `memo-recommendation`, `memo-confidence`) as well as the multi-segment
   region testids (`memo-region-readonly`, `memo-state-loading`, …). Self-tested non-vacuous.

## 5. Holds honored (not violated)

- **ui-shell (frozen) untouched** — no `frontend/src/shell/` file created or edited; reused via import only
  (`ReadOnlyRegion` first use / `RecommendationBadge` / `ConfidenceBadge` / `Panel` / `copy` / `FORBIDDEN_TERMS` /
  `RoleContext`). **No new word-list.**
- **ui-queue (frozen) untouched** — no `frontend/src/queue/` file created or edited; its fetchSeam/StructuralGuard/testid
  pattern is **mirrored, never imported** (enforced by `noUiQueueImport.test.js`).
- **By-construction structural isolation** — `NarrativeRegion` has no rec/conf prop/path; header comment ships; the RO
  region is the sole rec/conf render site (SEPARATION-1 teeth confirm). **`narrative_prose` rendered as-is, never linted.**
- **No `RoleGate` composition** (VIEWONLY-1); **no router import** (VIEWONLY-1); **no real network call** (PERF-1 —
  transport injected); **no LLM; no TypeScript** (NOTS-1: 0 `.ts`/`.tsx`).
- **WIRE-1 R4 consumed by shape only** — the real `memoFetchSeam` transport wiring + R4 route implementation stay deferred
  to the composition root / Build & Test. **tier-B NOT authorized; no other unit started.**
- Backend pytest suite **untouched** (separate runner/tree); `testresults.txt` records the frontend result **alongside**.

## 6. Frontend coverage evidence

`npm run test:cov` → `frontend/src/memoView`: Statements 100% · Branches 100% · Functions 100% · Lines 100%.
Whole frontend (shell + queue + memoView): 589/589 statements, 125/125 branches, 31/31 functions, 589/589 lines = **100%**.
**QA-6 ≥90% PASSED.** ESLint: clean (`npm run lint`, exit 0). (Full detail in `testresults.txt`, frontend section.)
