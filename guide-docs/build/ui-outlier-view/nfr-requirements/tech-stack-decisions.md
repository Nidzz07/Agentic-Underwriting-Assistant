# Tech-Stack Decisions — `ui-outlier-view` (U20, C5, Phase 2)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U20 `ui-outlier-view` · C5 · **Phase 2** · **Depth**: lighter (display) · **Date**: 2026-07-17.
**Principle**: **inherit the frozen React/Tailwind/Vitest/RTL/jsdom/ESLint substrate unchanged; add only what is genuinely new to this unit** (the fetch-double + fixture-construction decisions from the ambiguity-check). **No new dependency.** Grounded in `frontend/package.json` + the `ui-shell`/`ui-queue`/`ui-memo-view` precedents (all re-read on disk).

---

## 1. Inherited, unchanged (D-INH)

| # | Decision | Source (frozen) |
|---|---|---|
| **D-INH-1** | **React + Tailwind, JS/JSX, NO TypeScript** | FR-UI-5; every frozen UI unit |
| **D-INH-2** | **Vitest + React Testing Library + jsdom** as the test runner/tier | `frontend/package.json` (`vitest run`, `@testing-library/react`, `jsdom`); `ui-memo-view` D3 |
| **D-INH-3** | **Frozen ESLint lints** `advisory-vocabulary` + `no-inline-label`, registered on `src/outlierView/**` | `ui-shell` `shell/copy` lint mechanism; `ui-memo-view` `NFR-MEMO-ADVISORY-1`/`COPY-1` |
| **D-INH-4** | **`ui-shell` primitives/copy/session/tokens** composed by import (never edited/promoted-into) | `ui-shell` (U10, frozen); FD §4 |
| **D-INH-5** | **`shell/tokens` aesthetic values deferred** to NFR-Design / Code-Gen | `ui-shell` §4 (values deferred) |
| **D-INH-6** | **Testid convention** `outlier-<element>-<purpose>` (applying the frozen `shell-*`/`memo-*` convention) + an `outlier-testid-convention` lint | FR-UI-3; `ui-memo-view` `NFR-MEMO-TESTID-1` |

**No new runtime or dev dependency is introduced by U20.** The entire NFR set runs on the substrate `ui-shell`/`ui-queue`/`ui-memo-view` already established.

---

## 2. New to this unit (D-OUTV — from the FD + the ambiguity-check folds)

| # | Decision | Rationale / fold |
|---|---|---|
| **D-OUTV-1 (Fold-A)** | **A single injected/capturing `fetchSeam` double** — one double construction per test, injected into `OutlierView` as the `fetchSeam` prop; it resolves the R4 body (or rejects) and **captures** the call so Retry can be asserted to re-fetch the **same** `applicationId`. | the `ui-queue`/`ui-memo-view` single-double precedent; drives `NFR-OUTV-FETCH-1` + the four-state teeth |
| **D-OUTV-2 (Fold-C)** | **Three distinct outlier fixtures** built by a small local `outlierView` test-fixtures helper: **(1) `outlier: null`** (→ `NOT_AVAILABLE`, from both a `pending` body and a Phase-1 `ready`+null body); **(2) `outlier: {…, flagged_features: []}`** (→ `READY` "no anomalies", `EMPTY-1`); **(3) `outlier: {…, flagged_features: […]}`** (→ `READY`-with-data, incl. a **deliberately non-sorted** list for `LISTORDER-1`). | the `null`-vs-`{flagged_features:[]}` distinction is structurally unambiguous (falsy-null vs truthy-object); mirrors `ui-memo-view` NFR-MEMO-Fold-C; drives `STATE-1`/`EMPTY-1`/`LISTORDER-1` |
| **D-OUTV-3 (Fold-B)** | **Rendered-absence technique for `NOVERDICT-1`**: the **structural import-absence scan** (no `RecommendationBadge`/`ConfidenceBadge` import) is the **primary robust guarantee**; the rendered half uses **RTL `queryBy*` returning null** over the **enumerated finite set** {`APPROVE`, `REFER`, `DECLINE-RECOMMEND`, the shell `RECOMMENDATION_LABELS`/`CONFIDENCE_LABELS` values} — **never** a broad `container.textContent.includes(...)` substring sweep. | the project's text-scan-false-positive history (AST-over-text; comment-stripping) applies equally to a rendered-absence assertion |
| **D-OUTV-4 (Fold-D)** | **Distinctive collision-proof provenance sentinels for `PROV-1`**: `seed` = a large tagged integer (e.g. `987654321`), `corpus_version` = a tagged string (e.g. `"SENTINEL-CORPUS-DO-NOT-RENDER"`) — chosen so they cannot overlap any legitimately-rendered value (a score, a `z_score`, a feature name, a testid), making the negative "sentinel absent" assertion sound in both directions. | avoids the false-fail (incidental overlap) and the weak-sentinel false-pass class |
| **D-OUTV-5** | **`outlier_model_version` footnote is a single Code-Gen realization** (Q3-A), **not** a runtime-configurable prop — so no dual present/absent test matrix; `PROV-1` gates the `seed`/`corpus_version` negative regardless. | Q3-A; keeps the NFR set testing behavior, not configurability |

---

## 3. Explicitly NOT adopted
- **No live backend / no MSW / no network** — R4 is the injected `fetchSeam` double (D-OUTV-1); the unit builds + tests with no server.
- **No new component library / no charting dependency** — the outlier signals render with `ui-shell` primitives + Tailwind; any richer SHAP visualization is a **later** aesthetic concern (Code-Gen / a future iteration), not a new NFR dependency.
- **No TypeScript, no router, no state-management library** — view-only, single-fetch, local state only (FR-UI-5 / BR-OUTV-4).
- **tier-B corpus run** — **not applicable** (a UI unit never touches the corpus) and **not authorized**.

## 4. Settled / deferred
- **Settled**: the test tier (D-INH-2), the lint substrate (D-INH-3), the single fetch double (D-OUTV-1), the three fixtures (D-OUTV-2), the rendered-absence technique (D-OUTV-3), the provenance sentinels (D-OUTV-4).
- **Deferred to NFR-Design / Code-Gen**: the exact `FLAG_DIRECTION_LABELS`/copy strings, the `shell/tokens` values, the `fetchSeam` realization signature, whether the `outlier_model_version` footnote is included (D-OUTV-5).
