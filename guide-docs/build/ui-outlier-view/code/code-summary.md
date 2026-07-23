# Code Summary — `ui-outlier-view` (U20, C5, Phase 2)

**Stage**: BUILD → Code Generation (per-unit, Part 2 GENERATED) · **Unit**: U20 `ui-outlier-view` · C5 · **Phase 2** (the 2nd P2 unit) · **Depth**: lighter (display) · **Date**: 2026-07-17
**Built ON**: the frozen FD (BR-OUTV-1..10) + approved NFR Requirements (thirteen `NFR-OUTV-*`) + approved NFR Design (P-OUTV-1..10, C-OUTV-1..6) + the eight Code-Gen answers (**Q1–Q8 all A**) + folds **CG-OUTV-Fold-1..4** — re-opening none.
**This was the LAST stage for U20.**

---

## 1. Results (measured)

| Gate | Result |
|---|---|
| **Frontend suite** | **682 passed / 137 files** — baseline was **524 / 117** ⇒ **+158 tests / +20 files, zero regression** |
| **`src/outlierView` coverage** | **100% statements / 100% branches / 100% functions / 100% lines — on EVERY file** (QA-6 ≥90% cleared) |
| Project coverage gate | `All files` 100 / 99.79 / 100 / 100 — thresholds (90×4) **UNCHANGED**, held. The 99.79 branch is pre-existing `overrideForm/OverrideFormView.jsx:67` at its frozen baseline, untouched |
| **ESLint** | **clean (exit 0)** across the whole frontend, incl. the new `src/outlierView/**` block |
| **Backend** | **mtime-verified UNTOUCHED** (newest `backend/**/*.py` = 11:01, predating this session); Python suite **not re-run**, stays at 1011 passed / 31 skipped |

## 2. Modules produced (9 production files + 13 test files)

All under `frontend/src/outlierView/` — JS/JSX, **no TypeScript**, mirroring the realized `memoView`/`history` layout.

| Component | File | Header comment (Fold-1) |
|---|---|---|
| C-OUTV-1 `OutlierView` | `OutlierView.jsx` (+ exported `deriveOutlierState`, `OUTLIER_STATE`) | ✅ MANDATORY |
| C-OUTV-2 `fetchSeam` | `fetchSeam.js` | ✅ MANDATORY |
| C-OUTV-3 `OutlierStateView` | `components/OutlierStateView.jsx` | — |
| C-OUTV-4 `OutlierScoreRegion` | `components/OutlierScoreRegion.jsx` | ✅ MANDATORY |
| C-OUTV-5 `FlaggedFeaturesRegion` | `components/FlaggedFeaturesRegion.jsx` | ✅ MANDATORY |
| — outlier-local copy | `copy.js` (`OUTLIER_COPY`, `FLAG_DIRECTION_LABELS`) | — (lint-subject) |
| — dynamic testids (Q2-A) | `testids.js` (`slugSegment`, `outlierFlagTestid`) | — |
| C-OUTV-6 `StructuralGuard` | `__tests__/*` (+ `refNotOwn.js`, `fixtures.js`) | — (test-only) |

**All four mandatory header comments are present and asserted** by `__tests__/headerComments.test.js` — documentation only, never enforcement.

### Shared config — three additive edits (no frozen `src/` tree touched)
- `eslint-rules/outlierView.js` — **NEW**; `outlier-testid-convention`, the **`*` family** (Q1-A).
- `eslint.config.js` — **ADDED** one `src/outlierView/**` block reusing `shell/no-inline-label` + `shell/advisory-vocabulary`. Six existing blocks untouched.
- `vitest.config.js` — **ADDED** the include + coverage.include/exclude paths. **Thresholds UNCHANGED.**

## 3. Test → target map (all thirteen `NFR-OUTV-*`; no orphan)

| Target | Test file(s) | Tier |
|---|---|---|
| **STATE-1** (load-bearing) | `outlierView.state.test.jsx` (11) + `outlierView.transition.test.jsx` (5) | component — **full/highest** |
| **NOVERDICT-1** (load-bearing) | `noVerdictImport.test.js` (6, structural+self-tests) + `outlierView.namespace.test.jsx` (13) | structural + component — **full/highest** |
| PROV-1 | `outlierView.provenance.test.jsx` (5) | component (negative) |
| EMPTY-1 | `outlierView.empty.test.jsx` (4) | component |
| LISTORDER-1 | `outlierView.listorder.test.jsx` (4) | component + structural |
| FETCH-1 | `fetchSeam.test.js` (10) + `outlierView.fetch.test.jsx` (7) | component |
| ERROR-1 | `outlierView.error.test.jsx` (7) | component |
| VIEWONLY-1 | `outlierView.roleInvariant.test.jsx` (3) + `noWriteSeam.test.js` (7) | structural + component |
| ADVISORY-1 / COPY-1 | `eslint.outlier.rules.test.js` (22) + `copy.test.js` (10) | structural (lint) + component |
| SCOPE-1 | `noBackendImport.test.js` (4) + `noSiblingImport.test.js` (9) | structural + self-tests |
| TESTID-1 | `testid.test.jsx` (4) + `testids.test.js` (17) | structural + component |
| NOTS-1 | `nots.test.js` (4) | structural |
| *(Fold-1 documentation)* | `headerComments.test.js` (6) | structural |

### How the load-bearing pair is proven
- **STATE-1** — `NOT_AVAILABLE` renders for **both** null-causes (a `pending` body **and** a Phase-1 `ready`+`outlier:null` body — the fixture that proves derivation reads the **field**, not `status`). A failure renders `ERROR` with `outlier-state-notavailable` **asserted absent**, for **both** failure modes. `deriveOutlierState` is exported and tested as a pure function: for **every** payload — including the null-outlier payload that would otherwise derive `NOT_AVAILABLE` — a rejected fetch still yields `ERROR`, with the mirror-image test proving the same payload *does* yield `NOT_AVAILABLE` once resolved (non-vacuous).
- **NOVERDICT-1** — the **import-absence scan** (primary, robust) plus scans proving no `recommendation`/`confidence`/`provenance`/`seed`/`corpus_version` identifier appears in production **code**; and rendered absence via `queryBy*`-null over the **enumerated finite set** (`APPROVE`/`REFER`/`DECLINE-RECOMMEND` + all `RECOMMENDATION_LABELS` + all `CONFIDENCE_LABELS`, imported from `shell/copy`) with **exact matching**, never a substring sweep. Both regions are additionally rendered **with verdict/provenance props forced on them** and shown to render neither.

## 4. Realization notes (flagged)

- **CG-OUTV-Fold-1 (load-bearing)** — the four mandatory header comments deliberately **name** the tokens the scans hunt (`recommendation`, `seed`, `no request-body builder`). Every structural scan therefore runs over **comment-stripped** source (`__tests__/refNotOwn.js` `stripComments`, mirroring the frozen `ui-approval-gate`→`ui-history` precedent). `noVerdictImport.test.js` includes a test proving the strip is load-bearing: raw source **does** contain the words, stripped source does **not** contain the code.
- **CG-OUTV-Fold-2 (Q6-A)** — the `outlier_model_version` footnote is **OMITTED**; provenance is entirely absent from the render. The FD's **conditional** entries (`modelVersionFootnoteLabel`, testid `outlier-provenance-modelversion`) are therefore **deliberately not realized** — the FD authorized either ("optional", "only if surfaced"), so this realizes it faithfully. `copy.test.js` asserts no provenance-bearing copy key exists at all.
- **CG-OUTV-Fold-3 (Q2-A + Q3-A)** — the row **displays the raw wire string** (`dti_ratio`) while its **testid is slugged** (`outlier-flag-dti-ratio`). Intentional asymmetry: the convention requires kebab; the faithful-renderer principle (BR-OUTV-6) requires raw display. `testids.test.js` asserts all **nine real U18 feature names** slug to convention-satisfying ids, and that a **naive unslugged** interpolation **would** have violated the convention (non-vacuous).
- **CG-OUTV-Fold-4 (Q7-A)** — `FLAG_DIRECTION_LABELS` = "Above/Below the typical range". `copy.test.js` proves the avoided trap is **real**: a bare `High`/`Low` **is** a `CONFIDENCE_LABELS` value, so it would have tripped `no-inline-label` **and** false-failed the NOVERDICT-1 teeth. Every copy value is run through the **imported real detector** (`findForbiddenSystemOutput`), never a re-implementation.
- **Q1-A precedent split** — the six prior units use **two incompatible** testid regex families. The `*` (memoView/approvalGate) family was adopted so the frozen FD's three two-segment ids (`outlier-view`/`outlier-score`/`outlier-isoutlier`) generate **verbatim**; the `+` family would have rejected them.
- **`user-event` is NOT a dependency** — the Retry interaction uses `fireEvent` from `@testing-library/react`, matching the frozen sibling convention. **No new dependency** was introduced.
- **One extra test file beyond the plan** — `headerComments.test.js`, asserting the Fold-1 deliverables. `noSiblingImport.test.js` consolidates the plan's four separate per-sibling scan files into one parameterized file covering **all six** sibling trees (a superset of the planned coverage).

## 5. Holds honoured

`ui-shell` (frozen) **untouched** — primitives/copy/session/tokens imported and composed only, nothing promoted into it. `outlier-model` (U18, frozen) **never imported** — reached only `(orchestrated)` via R4; the nine feature names are mirrored **by value** in a test constant, not imported (cross-language boundary). All sibling UI units **untouched** — conventions mirrored by reading, never imported (asserted by `noSiblingImport.test.js`). **No local `FORBIDDEN_TERMS`** — the ONE shell source reused (asserted `===` identical). WIRE-1 consumed **by shape only**, no real network call, **not touched further** (R4 remains a `501` stub). No LLM. No TypeScript. **tier-B N/A and not authorized.** The 17 frozen P1 units and the closed composition root (`backend/app`, `frontend/src/app`) **untouched**. No other unit started.
