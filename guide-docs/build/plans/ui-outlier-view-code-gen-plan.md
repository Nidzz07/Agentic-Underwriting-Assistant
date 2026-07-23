# Code Generation Plan (Part 1) — `ui-outlier-view` (U20, C5, Phase 2)

**Stage**: BUILD → Code Generation (per-unit) · **Unit**: U20 `ui-outlier-view` · C5 · **Phase 2** (the 2nd P2 unit) · **Depth**: lighter (display) · **Date**: 2026-07-17
**Status**: **PART 2 GENERATED 2026-07-17** — Q1–Q8 answered (**all A**, embedded in §7); ambiguity-check **RUN → CLEAN** (four folds **CG-OUTV-Fold-1..4**, no surface-and-stop, §7.9); §4 Steps 0–8 **all `[x]`**. **682 passed / 137 files** (baseline 524/117 — zero regression); `src/outlierView` **100% on every metric, every file**; ESLint clean; backend mtime-verified untouched. **STOPPED at the Code-Generation 2-option completion gate.**
**This is the LAST stage for U20** (Infrastructure Design ✓ SKIPPED-logged 2026-07-17 — the 18th skip; approved at its gate).

**Built ON (re-opening none)**: the frozen **FD** (`business-rules.md` BR-OUTV-1..10 · `domain-entities.md` · `business-logic-model.md`; Q1–Q5 **A/A/A/B/A**; OUTV-FD-Fold-1..3) · the approved **NFR Requirements** (thirteen `NFR-OUTV-*`; load-bearing **STATE-1 + NOVERDICT-1**; Q1–Q3 **all A**; Fold-A..D; `tech-stack-decisions.md` D-INH-1..6 / D-OUTV-1..5) · the approved **NFR Design** (`nfr-design-patterns.md` **P-OUTV-1..10** · `logical-components.md` **C-OUTV-1..6**; Q1–Q3 **all A — structural**; **NFR-ND-OUTV-Fold-1** mandatory header comments).

**Realized sibling convention re-read on disk** (mirrored, never imported): `frontend/src/memoView/` (`MemoView.jsx` · `memoFetchSeam.js` · `copy.js` · `components/` · `__tests__/`) · `frontend/src/history/` (adds `testids.js` + `__tests__/refNotOwn.js`) · `frontend/eslint.config.js` (six per-unit blocks) · `frontend/eslint-rules/` (`index.js` + five per-unit rule modules) · `frontend/vitest.config.js` · `frontend/package.json`.

---

## 1. Verified baseline (measured, not assumed — 2026-07-17)

| Fact | Value | How verified |
|---|---|---|
| **Frontend test baseline** | **524 passed / 117 files** (all green) | `npx vitest run` executed this session |
| Existing `src/` trees (6 units + composition root) | `shell` · `queue` · `memoView` · `approvalGate` · `overrideForm` · `history` · `app` | `ls frontend/src` |
| `frontend/src/outlierView/` | **ABSENT** (correct — nothing pre-created) | `ls` (NOT PRESENT) |
| Coverage gate | v8, **thresholds `lines/functions/statements/branches: 90`** (QA-6) | `vitest.config.js` |
| The ONE `FORBIDDEN_TERMS` | `systemOutput: ['DECLINE','decision','approved','declined']`, `required: 'recommendation'` | `src/shell/copy/forbiddenTerms.js` |
| Real advisory detector | `findForbiddenSystemOutput(text)` — `/decline(?!-?recommend)/i` **substring** + `\bterm\b` word-boundary for `decision`/`approved` | `eslint-rules/index.js` |
| U18 wire feature names (nine) | `age_years_derived` · `bmi_derived` · `verifiable_income_annual` · `existing_debt_obligations_annual` · `requested_cover_amount` · `dti_ratio` · `income_multiple` · `health_flag_count` · `documents_missing_count` — **snake_case** | `backend/outlier_model/feature_fields.py` (read-only) |

**Part 2 re-measures this baseline before and after generation; `524 / 117` must not regress and U20's tests are purely additive.**

---

## 2. Component → module map (C-OUTV-1..6 → concrete files; JS/JSX, **no TypeScript**)

All under **`frontend/src/outlierView/`** — mirroring the realized `memoView`/`history` layout (root view + seam + copy + `components/` + `__tests__/`).

| # | Component (NFR-Design) | File | Header comment (Fold-1) | Deps |
|---|---|---|---|---|
| C-OUTV-2 | `fetchSeam` | **`outlierView/fetchSeam.js`** | ✅ **MANDATORY** | none (leaf) |
| — | outlier-local copy | **`outlierView/copy.js`** | — (lint-subject) | none (leaf) |
| — | dynamic testid builders | **`outlierView/testids.js`** *(subject to Q2)* | — | none (leaf) |
| C-OUTV-4 | `OutlierScoreRegion` | **`outlierView/components/OutlierScoreRegion.jsx`** | ✅ **MANDATORY** | `copy.js`, ui-shell |
| C-OUTV-5 | `FlaggedFeaturesRegion` | **`outlierView/components/FlaggedFeaturesRegion.jsx`** | ✅ **MANDATORY** | `copy.js`, `testids.js`, ui-shell |
| C-OUTV-3 | `OutlierStateView` | **`outlierView/components/OutlierStateView.jsx`** | — (not in the Fold-1 four) | `copy.js`, ui-shell |
| C-OUTV-1 | `OutlierView` | **`outlierView/OutlierView.jsx`** | ✅ **MANDATORY** | all of the above |
| C-OUTV-6 | `StructuralGuard` substrate | **`outlierView/__tests__/*`** + `eslint-rules/outlierView.js` | — (test-only) | — |

### 2.1 The four MANDATORY header comments are explicit Code-Gen deliverables (NFR-ND-OUTV-Fold-1 — pinned, NOT implicit)

Each is a **non-optional generated artifact**, asserted by a dedicated test (**documentation only — NOT enforcement**; the prop signatures + branch ordering + scans are the enforcement):

1. **`OutlierView.jsx`** — state derivation is **failure-first** (`REJECTED → ERROR` **before** the `outlier`-null check), so `NOT_AVAILABLE` is **unwritable from a failure path**; the discriminator is the **`outlier` field** on a resolved response, **not** R4 `status`.
2. **`OutlierScoreRegion.jsx`** — props are `{outlierScore, isOutlier, testid}` **only** — no `recommendation`/`confidence`/`provenance`/`seed`/`corpus_version` prop; renders no system verdict, no provenance.
3. **`FlaggedFeaturesRegion.jsx`** — props are `{flaggedFeatures, testid}` **only** — no verdict/provenance prop; flags render as statistical signals **in delivered order**; empty ⇒ no-anomalies branch.
4. **`fetchSeam.js`** — **READ-ONLY** R4 seam; builder emits **only** `GET`; **no request-body builder, no `submit*` — write structurally absent**; **mirrors** the sibling read seams **WITHOUT importing** them.

### 2.2 The only two SHARED files edited (additive-only; precedented ×6)

Neither is a frozen unit's `src/` tree; both are shared root config that **every** prior UI unit extended the same way:

- **`frontend/eslint.config.js`** — **ADD** one `src/outlierView/**` block (ignoring `__tests__/**`) reusing `shell/no-inline-label` + `shell/advisory-vocabulary` (**the ONE `FORBIDDEN_TERMS` — no new word-list**) + the new `outlier/outlier-testid-convention`. The six existing blocks are **untouched**.
- **`frontend/eslint-rules/outlierView.js`** — **NEW** module exporting the `outlier-testid-convention` rule (pattern per **Q1**), mirroring `memoView.js`/`history.js`.
- **`frontend/vitest.config.js`** — **ADD** `src/outlierView/__tests__/**` to `include` + `src/outlierView/**` to `coverage.include` (and `__tests__` to `coverage.exclude`). **Thresholds UNCHANGED** — all seven existing gates stand, none weakened.

---

## 3. TDD test → target map (every `NFR-OUTV-*` at its NFR-pinned tier; TDD per QA-6 — test first, then implementation)

### 3.1 THE LOAD-BEARING PAIR — full/highest rigor

#### `NFR-OUTV-STATE-1` → **P-OUTV-1** — `__tests__/outlierView.state.test.jsx` + `__tests__/outlierView.transition.test.jsx`
- **(a) four states render their containers**: `outlier-state-loading` / the ready composition / `outlier-state-notavailable` / `outlier-state-error`.
- **(b) FIELD-DERIVED teeth (Fold-C fixtures 1a + 1b)** — `NOT_AVAILABLE` renders for **BOTH**: a **`status:"pending"`** body carrying `outlier:null`, **AND** a **Phase-1 `status:"ready"`** body carrying `outlier:null`. The second fixture is what **proves field-derived, not `status`-derived** — a `status`-keyed implementation would render `READY` and fail.
- **(c) FAILURE-FIRST branch-ordering teeth (the genuine-failure fixture)** — a rejected fetch renders **`ERROR`** (with Retry) and **never** `NOT_AVAILABLE`; asserted **both** ways: `outlier-state-error` present **AND** `outlier-state-notavailable` **absent** (`queryBy*`-null). Proves `NOT_AVAILABLE` is unreachable from an error path.
- **Teeth**: fails if `NOT_AVAILABLE` is reached from an error, or if a `ready`+`outlier:null` body renders anything but `NOT_AVAILABLE`.

#### `NFR-OUTV-NOVERDICT-1` → **P-OUTV-2** — `__tests__/noVerdictImport.test.js` (structural) + `__tests__/outlierView.namespace.test.jsx` (rendered)
- **(a) STRUCTURAL (primary, robust)** — an import-absence scan over `outlierView/**`: **no** `RecommendationBadge`/`ConfidenceBadge` import anywhere (a component never imported cannot render) **+ a detector self-test** (synthetic import line → asserted flagged; non-vacuous).
- **(b) RENDERED ABSENCE (Fold-B)** — over the **populated `READY`** fixture, RTL `queryBy*` returns **null** for **each** member of the **enumerated finite set** — `APPROVE`, `REFER`, `DECLINE-RECOMMEND`, every `RECOMMENDATION_LABELS` value, every `CONFIDENCE_LABELS` value (imported from `shell/copy`, **exact matching**). **NOT** a `container.textContent.includes(...)` substring sweep (the project's text-scan-false-positive caution).
- **(c)** prop-signature assertion: neither region accepts a `recommendation`/`confidence` prop path.

### 3.2 FULL RIGOR

| Target | Pattern | Test file(s) | Teeth |
|---|---|---|---|
| **PROV-1** | P-OUTV-3 | `__tests__/outlierView.provenance.test.jsx` | **Sentinel negative (Fold-D)** — a `READY` fixture whose `provenance` carries the **collision-proof pinned sentinels** (**Q5**): `seed: 987654321`, `corpus_version: "SENTINEL-CORPUS-DO-NOT-RENDER"` → **neither** appears in the render (`queryByText`-null + a distinctive-sentinel non-inclusion check). Regions never receive `provenance` as a prop. Footnote per **Q6** (single realization). |
| **EMPTY-1** | P-OUTV-4 | `__tests__/outlierView.empty.test.jsx` | **Distinct-branch teeth** — `outlier` **present** + `flagged_features: []` (valid score) ⇒ **`READY`** + the neutral "no anomalous features" message in `outlier-region-flags`, **asserted distinct** from `NOT_AVAILABLE` (different container/testid + different message). Fails if empty-flags renders `NOT_AVAILABLE`, or if `NOT_AVAILABLE` renders the no-anomalies message. "analyzed, no anomalies" ≠ "not analyzed". |
| **LISTORDER-1** | P-OUTV-5 | `__tests__/outlierView.listorder.test.jsx` | **Non-sorted fixture** (Fold-C fixture 3) — rendered `outlier-flag-*` row order **equals** input order; **+ structural**: no `.sort()`/comparator on the list in source. |
| **FETCH-1** | P-OUTV-6 | `__tests__/fetchSeam.test.js` + `__tests__/outlierView.fetch.test.jsx` | **Single injected/capturing `fetchSeam` double** (D-OUTV-1 / Fold-A) — one double per test; drives `LOADING → {READY / NOT_AVAILABLE / ERROR}` end-to-end; the capture proves Retry re-fetches the **same** `applicationId`. Builder emits **only** `{method:'GET', path}`. |
| **ERROR-1** | P-OUTV-7 | `__tests__/outlierView.error.test.jsx` | `error.message` visible (`outlier-error-message`); `error.code` on a **hidden** testid (`outlier-error-code`, not visible text); `error.detail` **never** raw; Retry (`outlier-error-retry`) re-fetches the same `applicationId`. |
| **VIEWONLY-1** | P-OUTV-8 | `__tests__/noRoleGateImport.test.js` · `noRouterImport.test.js` · `noWriteSeam.test.js` · `outlierView.roleInvariant.test.jsx` | No `RoleGate` import/render; no router import; no `POST`/commit; no outward mutating event prop; rendering **invariant across all three Roles** (`shell/session` present but not gated on). |
| **ADVISORY-1** | P-OUTV-9 | `__tests__/eslint.outlier.rules.test.js` | The frozen `advisory-vocabulary` + `no-inline-label` **registered + green** on `src/outlierView/**` (RuleTester, sibling precedent); **a synthetic forbidden-term insertion FAILS** (non-vacuity). Static source only — never lints runtime R4 data. |
| **COPY-1** | P-OUTV-9 | `__tests__/copy.test.js` | **(a)** no inlined `shell/copy` display label; **(b)** `FLAG_DIRECTION_LABELS` maps `high`/`low` → **statistical-position** phrases, keyed **by value**, **no severity/verdict word** — **verified against the REAL detector** `findForbiddenSystemOutput` imported from `eslint-rules/index.js` (**Q7**), not assumed; **(c)** no `copy.js` value equals a `shell/copy` label or contains a `FORBIDDEN_TERMS.systemOutput` token. |
| **SCOPE-1** | P-OUTV-10 | `__tests__/noBackendImport.test.js` · `noOutlierModelImport.test.js` · `noMemoViewImport.test.js` · `noUiQueueImport.test.js` (+ `refNotOwn.js` helper) | **No import** of `outlier-model`, `ui-memo-view`, `ui-queue`, any sibling view, or any backend module in `outlierView/**`; only `ui-shell` + the injected seam + React. **+ detector self-test** (synthetic forbidden import → asserted flagged; non-vacuous). |
| **TESTID-1** | P-OUTV-10 | `__tests__/testid.test.jsx` (+ `testids.test.js` per **Q2**) | Every state container + flag row + `outlier-score`/`outlier-isoutlier` + error `message`/`code`/`retry` carry `outlier-*` testids; the `outlier-testid-convention` lint green (pattern per **Q1**); the dynamic-segment slug builder self-tested (**Q2**). |
| **NOTS-1** | P-OUTV-10 | `__tests__/nots.test.js` | No `.ts`/`.tsx` anywhere under `outlierView/`; JS/JSX only. |

**All thirteen `NFR-OUTV-*` covered; no orphan.**

---

## 4. Leaf-first build order (TDD per step: test → implementation → green)

- [x] **Step 0** — Re-measure the frontend baseline (`524 / 117`), confirm `frontend/src/outlierView/` absent.
- [x] **Step 1** — **`fetchSeam.js`** (no deps) — header comment; `buildOutlierRequest(applicationId)` emits **only** `{method:'GET', path}`; `normalizeError(cause)`; `createOutlierFetch(transport)`. **No write path, no `submit*`.** → FETCH-1, ERROR-1 (build/normalize), SCOPE-1.
- [x] **Step 2** — **`copy.js`** (no deps) — `FLAG_DIRECTION_LABELS` (**Q7** wording, detector-verified) + the FD §5 chrome strings (`notAvailableMessage`, `loadingLabel`, `retryLabel`, `panelHeading`/`scoreHeading`/`flagsHeading`, `noFlagsLabel`, `outlierScoreLabel`/`isOutlierLabel`, `modelVersionFootnoteLabel`, `unknownErrorMessage`). **No local `FORBIDDEN_TERMS`.** → COPY-1, ADVISORY-1.
- [x] **Step 2b** — **`testids.js`** (**Q2**) — dynamic flag-row testid builder + slug, mirroring the realized `history/testids.js`. → TESTID-1.
- [x] **Step 3** — **`components/OutlierScoreRegion.jsx`** + **`components/FlaggedFeaturesRegion.jsx`** (dep: `copy.js`) — header comments; the **exact** prop shapes `{outlierScore, isOutlier, testid}` / `{flaggedFeatures, testid}` — **no verdict/provenance path**; order-preserving map, empty ⇒ no-anomalies branch. → NOVERDICT-1, PROV-1, EMPTY-1, LISTORDER-1.
- [x] **Step 4** — **`components/OutlierStateView.jsx`** (dep: `copy.js`) — the **distinct** `loading` / `not_available` / `error` branches; `{state, error, onRetry, testid}`. → EMPTY-1 (not-available branch), ERROR-1.
- [x] **Step 5** — **`OutlierView.jsx`** (composes all) — header comment; the **failure-first** state derivation (`REJECTED → ERROR` **before** the `outlier`-null check); `{applicationId, fetchSeam}`; emits nothing upward. → STATE-1, FETCH-1, VIEWONLY-1.
- [x] **Step 6** — **`StructuralGuard`** — the scan substrate over everything above, **each with its detector self-test**; `eslint-rules/outlierView.js` + the `eslint.config.js` block (additive). → SCOPE-1, TESTID-1, NOTS-1, ADVISORY-1, the NOVERDICT-1 import half.
- [x] **Step 7** — **Coverage/quality gate** — fold `src/outlierView/**` into the frontend run (additive include; **thresholds UNCHANGED**); `npx vitest run` (no regression vs `524 / 117`; U20 tests purely additive); `npx vitest run --coverage` (`src/outlierView` ≥90%, targeting per-file 100% per the `src/history` precedent); `npx eslint .` clean. **Backend mtime-verified untouched.**
- [x] **Step 8** — Write `guide-docs/build/ui-outlier-view/code/code-summary.md`; refresh `testresults.txt`; update this plan's checkboxes + `guide-state.md`; append to `audit.md`; present the 2-option completion gate.

---

## 5. HOLDS (restated — binding on Part 2)

- **`ui-shell` (U10, frozen) UNTOUCHED** — primitives (`AppFrame`/`Panel`/`Region`/`ReadOnlyRegion`) + `shell/copy` + `shell/session` + `shell/tokens` reused **via import only**; nothing edited, **nothing promoted into** `ui-shell`.
- **`outlier-model` (U18, frozen) reached ONLY via R4, NEVER imported** — the reciprocal of U18's `StructuralGuard` forbidding `ui_outlier_view`. Cross-language boundary; no backend Python import.
- **`ui-memo-view` / `ui-queue` / `ui-approval-gate` / `ui-override-form` / `ui-history` — UNTOUCHED**; conventions **mirrored, never imported**.
- **No local `FORBIDDEN_TERMS` word-list** — the ONE `shell/copy/forbiddenTerms.js` source, reused.
- **All four by-construction guarantees are HARD requirements** with their **mandatory header comments** (§2.1): failure-first state ordering; `recommendation`/`confidence` prop-exclusion; `provenance`/`seed`/`corpus_version` prop-exclusion; read-only GET-only seam.
- **WIRE-1 consumed BY SHAPE only** (the R4 `outlier` slice) — **no real network call**; real transport wiring deferred to the composition root (**R4 stays a `501` stub**); WIRE-1 **not touched further**.
- **No LLM. No TypeScript. No new dependency** (D-INH-1..6; no MSW, no charting library).
- **tier-B NOT APPLICABLE and NOT authorized** — a UI unit never touches the corpus.
- **The 17 frozen P1 units + the closed composition root (`backend/app`, `frontend/src/app`) UNTOUCHED**; `audit_store` Docker-guard gap untouched; **no other unit started**; 23-unit decomposition unchanged.
- **Only new files under `frontend/src/outlierView/`** + the three additive shared-config edits in §2.2.

---

## 6. Coverage / quality gate

- **Additive frontend module** — U20 adds `src/outlierView/**` and its `__tests__`; the seven existing coverage gates (`shell`/`queue`/`memoView`/`approvalGate`/`overrideForm`/`history`/`app`) are **unchanged and must not weaken**.
- **No regression** vs the measured **524 passed / 117 files**; U20's tests are strictly additive.
- **QA-6**: `src/outlierView` ≥90% on all four metrics; **target per-file 100%** (the `src/history` precedent).
- **Backend untouched** — mtime-verified; the Python suite (1011 passed / 31 skipped) is not re-run by this unit's work.

---

## 7. `[Answer]` questions — genuinely open Code-Gen-only choices

> Every question is written out in full with lettered options and a recommendation. **None is improvised** — Q1/Q2/Q3 were surfaced by reading the realized siblings + U18's real feature names on disk. **ANSWERED 2026-07-17 — Q1–Q8 all A** (embedded below with their realization). The ambiguity-check ran after these were filled → **CLEAN** (§7.9); Part 2 generated on explicit go.

### Q1 — The `outlier-testid-convention` regex family (TWO incompatible realized precedents exist)

Reading `frontend/eslint-rules/` on disk, the six prior units did **not** use one pattern — they split into **two families**:
- **queue/history family**: `/^queue-[a-z]+(-[a-z0-9]+)+$/` — the `+` quantifier requires **at least two segments** after the prefix (min. `queue-a-b`).
- **memoView/approvalGate family**: `/^memo-[a-z0-9]+(-[a-z0-9]+)*$/` — the `*` quantifier permits a **two-segment** id (`memo-confidence`, `memo-recommendation` are real, in-use testids).

**This matters concretely**: the frozen FD `data-testid` inventory (`domain-entities.md §6`) contains **three two-segment ids** — **`outlier-view`**, **`outlier-score`**, **`outlier-isoutlier`**. Under the **queue/history `+` family these three would be REJECTED by the lint**; under the memoView/approvalGate `*` family they pass.

- **(A) Adopt the memoView/approvalGate `*` family** — `/^outlier-[a-z0-9]+(-[a-z0-9]+)*$/`. The frozen FD testid inventory is generated **verbatim**, no FD artifact is re-opened, and the precedent is an equally-frozen sibling. **(Recommended)**
- **(B) Adopt the queue/history `+` family** — `/^outlier-[a-z]+(-[a-z0-9]+)+$/` and **rename** the three ids (e.g. `outlier-view-root`, `outlier-score-value`, `outlier-flag-isoutlier`). This **edits the frozen FD inventory** at Code-Gen — a re-opening of an approved artifact.
- **(C)** Adopt the `+` family and add a per-id carve-out/exception list to the rule.

**[Answer]**: **A — adopt the memoView/approvalGate `*` family** (`/^outlier-[a-z0-9]+(-[a-z0-9]+)*$/`); the frozen FD testid inventory (including the three two-segment ids `outlier-view`/`outlier-score`/`outlier-isoutlier`) generates verbatim, no FD artifact re-opened. → **REALIZED** in `eslint-rules/outlierView.js`.
### Q2 — The dynamic flag-row testid `outlier-flag-<feature>` (the wire feature names are snake_case)

The FD pins one **dynamic** testid: **`outlier-flag-<feature>`**, interpolating the wire `feature` string. Verified on disk (`backend/outlier_model/feature_fields.py`, read-only), the nine real values are **snake_case**: `age_years_derived`, `bmi_derived`, `verifiable_income_annual`, `existing_debt_obligations_annual`, `requested_cover_amount`, `dti_ratio`, `income_multiple`, `health_flag_count`, `documents_missing_count`.

A naive template literal yields **`outlier-flag-age_years_derived`** — **underscores violate the kebab convention** in every family. This is exactly the problem the realized **`history/testids.js`** already solved (its `slugSegment` slugs backend ids like `INCOME_MIN`), noting that the lint inspects **literal** `data-testid` attributes only, so a template literal is **invisible to it** — the builder + its self-test are the only enforcement.

- **(A) Add `outlierView/testids.js` with `slugSegment` + `outlierFlagTestid(feature)`**, mirroring `history/testids.js` verbatim in spirit, plus a **self-test** asserting every one of the **nine real U18 feature names** slugs to a convention-satisfying id (e.g. `outlier-flag-age-years-derived`). **(Recommended)** — a realized precedent solving the identical problem; the self-test is the enforcement the lint structurally cannot provide.
- **(B) Inline the template literal** in `FlaggedFeaturesRegion.jsx` with no slug — silently emits non-conforming ids (the lint cannot see them). **Rejected on the merits.**
- **(C)** Slug, but inline the helper in the component rather than a separate module (no self-test seam).

**[Answer]**: **A — add `outlierView/testids.js` with `slugSegment` + `outlierFlagTestid(feature)`**, mirroring `history/testids.js`, with a self-test asserting all nine real U18 feature names slug to convention-satisfying ids. → **REALIZED**; `testids.test.js` (17 tests) also proves a naive unslugged interpolation WOULD violate the convention.
### Q3 — Rendering the feature name (the frozen FD copy inventory has NO feature-label map)

`FlaggedFeaturesRegion` renders "the `feature` label". The frozen FD `copy.js` inventory (`domain-entities.md §5`) lists ten keys — `FLAG_DIRECTION_LABELS`, `notAvailableMessage`, `loadingLabel`, `retryLabel`, `panelHeading`/`scoreHeading`/`flagsHeading`, `noFlagsLabel`, `outlierScoreLabel`/`isOutlierLabel`, `modelVersionFootnoteLabel`, `unknownErrorMessage` — and **no** feature-name label map. So the raw wire string (`dti_ratio`) would render as-is.

- **(A) Render the raw wire `feature` string verbatim** — the frozen FD copy inventory is generated exactly as approved, no new copy key, no FD re-opening. Faithful-renderer principle (BR-OUTV-6): the view displays what R4 delivers. **(Recommended)**
- **(B) Add a `FEATURE_LABELS` map** to `copy.js` (nine human labels, keyed by value) — nicer display, but **adds a copy key beyond the frozen FD §5 inventory**, i.e. a Code-Gen-time FD extension.
- **(C) Humanize generically** at render (`dti_ratio` → "Dti ratio") via a formatter — no new copy key, but invents display text outside the copy module (`no-inline-label` philosophy tension).

**[Answer]**: **A — render the raw wire feature string verbatim**; no new copy key, no FD re-opening, faithful-renderer principle per BR-OUTV-6. → **REALIZED**; the raw/slug asymmetry documented as CG-OUTV-Fold-3.
### Q4 — Fixture construction (the three NFR-pinned fixtures + the genuine-failure fixture)

NFR-Requirements Fold-C pins **three** outlier fixtures; STATE-1's failure teeth need a **fourth** (a genuine failure). The realized siblings both use a local `__tests__/fixtures.js`.

- **(A) One `outlierView/__tests__/fixtures.js`** exporting **four** builders: `makePendingBody()` (`status:"pending"`, `outlier:null`) · `makeReadyNullOutlierBody()` (**Phase-1 `status:"ready"` + `outlier:null`** — the field-derived teeth) · `makeReadyEmptyFlagsBody()` (`outlier` present, `flagged_features: []`) · `makeReadyPopulatedBody()` (**deliberately non-sorted** flags + sentinel provenance) — plus `makeFailingTransport()` for the rejection path. **(Recommended)** — mirrors `memoView`/`history` `fixtures.js`; keeps the null/pending vs null/ready distinction explicit as two separate builders.
- **(B)** One parameterized `makeBody({status, outlier})` factory — fewer exports, but the load-bearing "pending-null vs ready-null" distinction becomes a call-site argument rather than a named, greppable fixture.
- **(C)** Inline fixtures per test file — no shared module.

**[Answer]**: **A — one `outlierView/__tests__/fixtures.js`** exporting four builders (`makePendingBody`, `makeReadyNullOutlierBody`, `makeReadyEmptyFlagsBody`, `makeReadyPopulatedBody`) plus `makeFailingTransport()`, mirroring the sibling `fixtures.js` precedent. → **REALIZED** (+ `makeCapturingTransport`, and `POPULATED_FEATURE_ORDER` for the LISTORDER-1 teeth).
### Q5 — Sentinel values for the PROV-1 negative teeth

NFR-Requirements Fold-D / `tech-stack-decisions.md` D-OUTV-4 pin **collision-proof** sentinels: `seed` = a large tagged integer **`987654321`**, `corpus_version` = a tagged string **`"SENTINEL-CORPUS-DO-NOT-RENDER"`**.

- **(A) Use the pinned values verbatim** — `seed: 987654321`, `corpus_version: "SENTINEL-CORPUS-DO-NOT-RENDER"`, exactly as approved at NFR-Requirements, with no Code-Gen drift. **(Recommended)** — Code-Gen realizes the pin; it does not re-decide it. (Confirmed lint-safe: neither contains a `FORBIDDEN_TERMS.systemOutput` token, and both live in `__tests__/`, which the lint blocks ignore.)
- **(B)** Choose different sentinel values at Code-Gen (requires re-opening the approved D-OUTV-4 pin).

**[Answer]**: **A — use the pinned sentinel values verbatim** (`seed: 987654321`, `corpus_version: "SENTINEL-CORPUS-DO-NOT-RENDER"`), exactly as approved at NFR-Requirements Fold-D, no Code-Gen drift. → **REALIZED** verbatim (+ a third `SENTINEL-MODEL-DO-NOT-RENDER` so the Q6-A omission is also asserted).
### Q6 — The optional `outlier_model_version` footnote (the single realization D-OUTV-5 defers to here)

Q5-A (FD) + Q3-A (NFR-Req) + D-OUTV-5 agreed the footnote is a **single Code-Gen realization**, not a runtime toggle — and that `PROV-1` gates the `seed`/`corpus_version` negative **either way**. The FD reserves the copy key `modelVersionFootnoteLabel` + testid `outlier-provenance-modelversion`. **This is the decision point.**

- **(A) OMIT the footnote** — provenance is **entirely** absent from the render; `modelVersionFootnoteLabel`/`outlier-provenance-modelversion` are not realized. The strongest reading of BR-OUTV-9 ("not rendered by default"); provenance's real consumer is `observability` (U21). PROV-1 tests the negative invariant only. **(Recommended)** — maximal consistency with P-OUTV-3's prop-exclusion (nothing to render, by construction).
- **(B) INCLUDE the footnote** — render `outlier_model_version` only, via a **distinct footnote slot** (never the score/flags regions, which keep total provenance prop-exclusion); PROV-1 adds a positive test that **only** `outlier_model_version` renders while both sentinels stay absent.

**[Answer]**: **A — omit the footnote**; provenance is entirely absent from the render; PROV-1 tests only the negative invariant. Maximal consistency with P-OUTV-3's total prop-exclusion. → **REALIZED**; the FD's CONDITIONAL `modelVersionFootnoteLabel` / `outlier-provenance-modelversion` entries deliberately not realized (CG-OUTV-Fold-2).
### Q7 — `FLAG_DIRECTION_LABELS` wording, verified against the REAL detector (not assumed)

Every prior unit verified its copy against the **actual** `findForbiddenSystemOutput` detector rather than eyeballing it. Read on disk (`eslint-rules/index.js`), the detector is **`/decline(?!-?recommend)/i` (a SUBSTRING test — any word containing "decline" flags)** plus `\bdecision\b` / `\bapproved\b` word-boundary tests, all case-insensitive. OUTV-FD-Fold-3 requires `high`/`low` to read as a **statistical position**, never severity.

- **(A) `high` → "Above the typical range" · `low` → "Below the typical range"**, with `copy.test.js` asserting **every** `copy.js` value through the **imported real detector** (`findForbiddenSystemOutput`) returns **no hits**, and that no value collides with a `shell/copy` `LABEL_VALUES` entry — the detector imported, not re-implemented. **(Recommended)** — matches the FD's own phrasing ("above / below the typical corpus range"); verified, not assumed.
- **(B) `high` → "Unusually high" · `low` → "Unusually low"** — shorter, but "unusually" edges toward a severity read (Fold-3 risk).
- **(C) `high` → "Above corpus mean" · `low` → "Below corpus mean"** — precise but exposes internal model vocabulary to the underwriter.

**[Answer]**: **A — `high` → "Above the typical range", `low` → "Below the typical range"**, with `copy.test.js` asserting every `copy.js` value through the imported real `findForbiddenSystemOutput` detector returns no hits. → **REALIZED**; `copy.test.js` additionally proves the avoided trap is real (a bare `High`/`Low` IS a `CONFIDENCE_LABELS` value — CG-OUTV-Fold-4).
### Q8 — Test-file layout for the state machine (the sibling convention splits state vs transition)

Both realized siblings ship **two** files: `memoView.state.test.jsx` + `memoView.transition.test.jsx`; `history.state.test.jsx` + `history.transition.test.jsx`.

- **(A) Mirror the sibling split** — `outlierView.state.test.jsx` (each of the four states renders its container, incl. **both** null-causes) + `outlierView.transition.test.jsx` (the **ordering/transition** teeth: failure ⇒ `ERROR` and never `NOT_AVAILABLE`; Retry ⇒ `LOADING` ⇒ re-resolve). **(Recommended)** — the load-bearing failure-first proof gets its own named home, matching six frozen precedents.
- **(B) One consolidated `outlierView.state.test.jsx`** holding both.
- **(C)** A dedicated third file for the failure-first ordering proof alone.

**[Answer]**: **A — mirror the sibling split**: `outlierView.state.test.jsx` (per-state container rendering, both null-causes) + `outlierView.transition.test.jsx` (the failure-first ordering/transition teeth). → **REALIZED** (11 + 5 tests).
### 7.9 Ambiguity-check — RUN 2026-07-17 against the eight filled answers → **CLEAN** (four folds, no surface-and-stop)

Run against the eight answers + the frozen FD (BR-OUTV-1..10) + the thirteen approved `NFR-OUTV-*` + the ten patterns + the six components + every fold — all re-read on disk, none re-opened. **No genuine gap → no STOP.** The four folds are recorded resolutions, not deferrals.

- **CG-OUTV-Fold-1 (LOAD-BEARING) — the header comments name the tokens the scans hunt.** The four MANDATORY Fold-1 header comments deliberately name `recommendation` / `confidence` / `provenance` / `seed` / `corpus_version` / "no request-body builder, no `submit*`" — precisely the tokens the NOVERDICT-1 / PROV-1 / SCOPE-1 / VIEWONLY-1 structural scans hunt. A scan over **raw** text would flag the very prose that makes each guarantee self-evident, forcing a false choice between the mandatory documentation and the mandatory scans. **Resolved by the frozen precedent** (`ui-approval-gate` `singleCallSite` → `ui-history` `__tests__/refNotOwn.js` `stripComments`): every scan runs over **comment-stripped** source — the guarantee is the absence of **code**, not of the words. Mirrored, never imported. `noVerdictImport.test.js` carries a test proving the strip is load-bearing (raw source **does** contain the words; stripped source does **not** contain the code).
- **CG-OUTV-Fold-2 — Q6-A leaves two CONDITIONAL FD inventory entries unrealized.** FD §5's `modelVersionFootnoteLabel` and §6's `outlier-provenance-modelversion` were both explicitly conditional ("optional (Q5-A)", "only if surfaced"); Q6-A (omit) means **neither is realized** and `copy.js` carries no footnote key. This **realizes** the optional entry faithfully — the FD authorized either — rather than contradicting it. Recorded so a reviewer diffing `copy.js` against FD §5 sees why. `copy.test.js` asserts no provenance-bearing key exists at all.
- **CG-OUTV-Fold-3 — the Q3-A/Q2-A asymmetry is intentional.** The flag row **displays the raw wire string** (`dti_ratio` — Q3-A, faithful-renderer BR-OUTV-6) while its **testid is slugged** (`outlier-flag-dti-ratio` — Q2-A, the kebab convention). Both derive from the same wire value; the divergence is deliberate and must not later be "fixed" by collapsing one into the other. Documented in `testids.js` + `FlaggedFeaturesRegion.jsx`.
- **CG-OUTV-Fold-4 — Q7-A's wording verified safe against the real label values.** NOVERDICT-1(b) queries `CONFIDENCE_LABELS`' values with **exact** matching, and those values (read on disk) are **`High` / `Medium` / `Low`**. A bare `High`/`Low` direction label — i.e. Q7-B/Q7-C-style wording — would have **collided exactly**, tripping `no-inline-label` **and** false-failing the NOVERDICT-1 teeth. Q7-A ("Above/Below the typical range") cannot collide. `copy.test.js` proves the trap is **real** (`LABEL_VALUES.has('High') === true`) and that our labels dodge it.

**Also checked, no gap**: Q1-A's `*` pattern accepts **every** id in the frozen FD §6 inventory (verified id-by-id); Q5-A's sentinels are lint-safe and `__tests__`-scoped; Q3-A's raw feature strings are **runtime data**, which the lints correctly never inspect (static source only); the three structural-A NFR-Design answers are mutually consistent with all eight Code-Gen answers.

**One deviation surfaced during generation (not an ambiguity — a HOLD protection)**: `@testing-library/user-event` is **NOT** in `devDependencies`. The Retry interaction therefore uses **`fireEvent`** from `@testing-library/react`, matching the frozen sibling convention (`memoView.retry.test.jsx`) — **no new dependency** introduced, as D-INH-2 requires.

---

## 8. Gate

**PART 2 GENERATED 2026-07-17 — STOPPED at the Code-Generation 2-option completion gate** (1. Request Changes / 2. Continue to Next Stage).

Completed, in order: **(1)** Q1–Q8 filled (all A, embedded in §7 with their realization) → **(2)** the mandatory ambiguity-check RAN → **CLEAN** (§7.9, four folds, no surface-and-stop) → **(3)** Part 2 generated per §4 Steps 0–8 (all `[x]`) → **(4)** this gate. **682 passed / 137 files** (baseline 524/117, zero regression, purely additive); **`src/outlierView` 100% statements/branches/functions/lines on every file**; ESLint clean; backend mtime-verified untouched. Summary → `guide-docs/build/ui-outlier-view/code/code-summary.md`; `testresults.txt` refreshed. **U20 is the 2nd of 6 Phase-2 units; this was its LAST stage — the per-unit loop for U20 is complete pending gate approval.**
