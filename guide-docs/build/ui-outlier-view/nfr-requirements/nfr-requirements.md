# NFR Requirements — `ui-outlier-view` (U20, C5, Phase 2)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U20 `ui-outlier-view` · C5 · **Phase 2** · **Depth**: lighter (display) · **Date**: 2026-07-17 · Story **US-UI-3** · FR-OUT-2.
**Built ON** the frozen FD (**BR-OUTV-1..10**; the four-component inventory; the four-state render model with the field-derived `NOT_AVAILABLE`; the advisory-statistical framing; the reference-not-own boundary + **OUTV-FD-Fold-2**; the outlier-local copy incl. `FLAG_DIRECTION_LABELS`) — **re-opening none.** Answers **Q1–Q3 (all A)** + folds **NFR-OUTV-Fold-A..D**. Each `NFR-OUTV-*` is a **pass/fail testable assertion** traced to its `BR-OUTV-*`.

**Tier**: **Vitest + React Testing Library + jsdom**, **no live backend**, **R4 mocked via a single injected/capturing `fetchSeam` double** (Fold-A). Structural/advisory conformance via the **frozen ESLint lints** (`advisory-vocabulary`, `no-inline-label`) on `src/outlierView/**` + AST/source scans. **No new dependency; no TypeScript** (FR-UI-5).

**Folds (from the ambiguity-check)**: **Fold-A** — one `fetchSeam` double (the `ui-queue`/`ui-memo-view` precedent). **Fold-B** — rendered-absence via `queryBy*`-null over an enumerated finite set + a structural import-absence scan, never a substring `textContent` sweep. **Fold-C** — three distinct outlier fixtures (`null` / present-empty / present-populated). **Fold-D** — distinctive collision-proof provenance sentinels.

---

## 1. Finalized `NFR-OUTV-*` targets (pass/fail; acceptance; tier)

### THE LOAD-BEARING PAIR

#### NFR-OUTV-STATE-1 — four-state model; the field-derived `NOT_AVAILABLE` reached only from a 2xx+null resolution (BR-OUTV-3) — **LOAD-BEARING**
- **Assertion**: the view renders exactly one of `{LOADING, READY, NOT_AVAILABLE, ERROR}`, and `NOT_AVAILABLE` is a **successful-resolution** state derived off the **`outlier` field**, never an error and never `status`-derived.
- **Acceptance**: **(a)** each state renders its container (`outlier-state-loading` / the ready composition / `outlier-state-notavailable` / `outlier-state-error`). **(b) teeth (Fold-C fixtures)** — `NOT_AVAILABLE` renders for **both** a `status:"pending"` body **and** a Phase-1 `status:"ready"` body carrying `outlier:null` (proving it is **field-derived, not `status`-derived**). **(c) teeth** — a fetch **failure** (non-2xx / transport) renders `ERROR` (with Retry), **never** `NOT_AVAILABLE` — so the not-available state **cannot mask an error**. **Teeth**: fails if `NOT_AVAILABLE` is reached from an error, or if a `ready`+`outlier:null` body renders anything but `NOT_AVAILABLE`.
- **Tier**: component (RTL). **Rigor**: full (highest).

#### NFR-OUTV-NOVERDICT-1 — no `Recommendation` namespace in rendered output (BR-OUTV-2) — **LOAD-BEARING**
- **Assertion**: the view renders **no** system verdict — no `Recommendation`/`Confidence` value or label reaches the DOM.
- **Acceptance (Q1-A + Fold-B)**: **(a) structural (primary, robust)** — no `RecommendationBadge`/`ConfidenceBadge` import anywhere in `outlierView/**` (AST/source scan + self-test); a component you never import cannot render. **(b) rendered absence** — over a **populated `READY` fixture**, RTL `queryBy*` returns **null** for **each** member of the **enumerated finite set** {`APPROVE`, `REFER`, `DECLINE-RECOMMEND`, the shell `RECOMMENDATION_LABELS` values, the `CONFIDENCE_LABELS` values} (exact matching) — **not** a broad `textContent.includes` substring sweep (Fold-B; the project's text-scan-false-positive caution). **Teeth**: fails if any badge is imported, or if any enumerated verdict token is queryable in the DOM.
- **Tier**: structural + component. **Rigor**: full (highest).

### FULL RIGOR

#### NFR-OUTV-ADVISORY-1 — reuse the frozen advisory lints; static-source scope only (BR-OUTV-2/5)
- **Acceptance**: the frozen `advisory-vocabulary` + `no-inline-label` ESLint rules are **registered + green** on `src/outlierView/**` (component labels, region chrome, the local `copy.js`); a **synthetic** forbidden-term insertion **fails** the lint (non-vacuity). The lints scope to **static source only** — they never lint runtime R4 data.
- **Tier**: structural (lint). **Rigor**: full.

#### NFR-OUTV-COPY-1 — single-source copy; `direction` as a statistical position (BR-OUTV-5 / OUTV-FD-Fold-3)
- **Acceptance**: **(a)** no inlined `shell/copy` display label (the `no-inline-label` mechanism). **(b)** `FLAG_DIRECTION_LABELS` maps `high`/`low` to **statistical-position** phrases (above / below the typical corpus range), keyed **by value**, containing **no** severity/verdict word (a `high` label must not read as "high risk"). **(c)** no value in `outlierView/copy.js` equals a `shell/copy` display label or contains a `FORBIDDEN_TERMS.systemOutput` token.
- **Tier**: structural + component. **Rigor**: full.

#### NFR-OUTV-EMPTY-1 — empty `flagged_features` renders "no anomalies", distinct from `NOT_AVAILABLE` (BR-OUTV-3/6 / Q2-A)
- **Acceptance (Fold-C)**: a `READY` fixture with `outlier` **present** but `flagged_features: []` (a normal applicant, valid `outlier_score`) renders the neutral **"no anomalous features"** message + a valid score in the **`READY`** composition, and is **asserted distinct** from the `NOT_AVAILABLE` state (a different container/testid + a different message). **Teeth**: fails if empty-flags renders `NOT_AVAILABLE`, or if `NOT_AVAILABLE` renders the "no anomalies" message — "analyzed, no anomalies found" ≠ "not analyzed".
- **Tier**: component (RTL). **Rigor**: full.

#### NFR-OUTV-LISTORDER-1 — deterministic `flagged_features` order preserved; no client re-sort (BR-OUTV-6)
- **Acceptance**: RTL over a **deliberately non-sorted** `flagged_features` fixture — the rendered `outlier-flag-<feature>` row order **equals** the input order; **(b)** no comparator/`.sort()` on the list in the view source (structural). Mirrors `ui-memo-view` `NFR-MEMO-LISTORDER-1`.
- **Tier**: component + structural. **Rigor**: full.

#### NFR-OUTV-ERROR-1 — error `message`-only / `code` via testid / `detail` never raw; same-resource Retry (BR-OUTV-7)
- **Acceptance**: a non-2xx / transport failure renders `error.message` (visible, `outlier-error-message`) + `error.code` (hidden `outlier-error-code`, not visible text) + a **Retry** (`outlier-error-retry`) that re-fetches R4 for the **same** `applicationId`; `error.detail` is **never** rendered raw. Mirrors `ui-memo-view` `NFR-MEMO-ERROR-1`.
- **Tier**: component. **Rigor**: full.

#### NFR-OUTV-VIEWONLY-1 — view-only; no `RoleGate`, no router, no commit (BR-OUTV-4)
- **Acceptance**: no `RoleGate` import/render; no router import; no commit/`POST`; no outward mutating event prop; `shell/session` (`RoleContext`/`useCurrentRole()`) may be present but is **not gated on**. Mirrors `ui-memo-view` `NFR-MEMO-VIEWONLY-1`.
- **Tier**: structural + component. **Rigor**: full.

#### NFR-OUTV-PROV-1 — provenance not rendered by default; `seed`/`corpus_version` never shown (BR-OUTV-9 / Q3-A / Fold-D)
- **Acceptance**: **(a) negative teeth (Fold-D)** — a `READY` fixture whose `provenance` carries **distinctive, collision-proof sentinels** (a large tagged integer `seed`, e.g. `987654321`; a tagged `corpus_version` string, e.g. `"SENTINEL-CORPUS-DO-NOT-RENDER"`) — the rendered output contains **neither** sentinel (`queryByText`-null + a safe distinctive-sentinel non-inclusion check). **(b) single realization (Q3-A)** — Code-Gen decides once whether the `outlier_model_version` footnote exists; **if present**, one test asserts **only** `outlier_model_version` renders (never `seed`/`corpus_version`); **if omitted**, only the negative invariant is tested. No dual present/absent configuration coverage (the "optional" is realization latitude, not a runtime toggle).
- **Tier**: component (negative). **Rigor**: full.

#### NFR-OUTV-CORPUS — *(n/a; not a target — corpus is backend-only)*

#### NFR-OUTV-TESTID-1 — `data-testid` convention (BR-OUTV-8)
- **Acceptance**: every state container + flag row + `outlier-score`/`outlier-isoutlier` + error `message`/`code`/`retry` carry `outlier-<element>-<purpose>` testids; the `outlier-testid-convention` lint is green (applying, not re-inventing, the frozen `shell-*`/`memo-*` convention).
- **Tier**: structural + component. **Rigor**: full.

#### NFR-OUTV-SCOPE-1 — reference-not-own; no sibling/backend import (BR-OUTV-10)
- **Acceptance**: a structural scan finds **no import** of `outlier-model`, `ui-memo-view`, `ui-queue`, any other sibling view, or any backend module in `outlierView/**`; the only imports are `ui-shell` + the injected `fetchSeam` + React/Tailwind. **+ a detector self-test** feeding a synthetic forbidden import and asserting the scan flags it (non-vacuity).
- **Tier**: structural. **Rigor**: full.

#### NFR-OUTV-FETCH-1 — R4 fetch-double + four-state machine coverage (BR-OUTV-1/3 / Fold-A)
- **Acceptance**: R4 is fetched via the **single injected `fetchSeam` double** (Fold-A — one double construction, captured); the four-state machine is exercised end-to-end (`LOADING` → each of `READY`/`NOT_AVAILABLE`/`ERROR`); the double **captures** the R4 call so Retry re-fetches the **same** `applicationId`.
- **Tier**: component. **Rigor**: full.

#### NFR-OUTV-NOTS-1 — no TypeScript (FR-UI-5)
- **Acceptance**: no `.ts`/`.tsx` under `outlierView/`; JS/JSX only.
- **Tier**: structural. **Rigor**: full.

---

## 2. Traceability (target → BR-OUTV-* / requirement → tier)

| Target | BR-OUTV / requirement | Tier | Rigor |
|---|---|---|---|
| **NFR-OUTV-STATE-1** | BR-OUTV-3 | component | **full (highest)** |
| **NFR-OUTV-NOVERDICT-1** | BR-OUTV-2 | structural + component | **full (highest)** |
| NFR-OUTV-ADVISORY-1 | BR-OUTV-2/5 | structural (lint) | full |
| NFR-OUTV-COPY-1 | BR-OUTV-5 | structural + component | full |
| NFR-OUTV-EMPTY-1 | BR-OUTV-3/6 | component | full |
| NFR-OUTV-LISTORDER-1 | BR-OUTV-6 | component + structural | full |
| NFR-OUTV-ERROR-1 | BR-OUTV-7 | component | full |
| NFR-OUTV-VIEWONLY-1 | BR-OUTV-4 | structural + component | full |
| NFR-OUTV-PROV-1 | BR-OUTV-9 | component (negative) | full |
| NFR-OUTV-TESTID-1 | BR-OUTV-8 | structural + component | full |
| NFR-OUTV-SCOPE-1 | BR-OUTV-10 | structural | full |
| NFR-OUTV-FETCH-1 | BR-OUTV-1/3 | component | full |
| NFR-OUTV-NOTS-1 | FR-UI-5 | structural | full |

**No orphaned BR-OUTV rule**: 1→FETCH-1; 2→NOVERDICT-1+ADVISORY-1; 3→STATE-1+EMPTY-1; 4→VIEWONLY-1; 5→COPY-1+ADVISORY-1; 6→LISTORDER-1+EMPTY-1; 7→ERROR-1; 8→TESTID-1; 9→PROV-1; 10→SCOPE-1; FR-UI-5→NOTS-1. **Load-bearing pair**: **STATE-1** (field-derived state correctness) + **NOVERDICT-1** (no rendered verdict).

---

## 3. Security-Guardrails extension — compliance (enabled extension)

`ui-outlier-view` is a **read-only presentational display** — no secret, no LLM/prompt, no persistence/write, no PII authored; it renders advisory statistical signals from an already-validated R4 body.

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A (referenced)** | Renders an already-validated R4 `outlier` body; application-input validation is the backend's (intake/R4). The view renders no free input. |
| Prompt-injection defense | **N/A** | **No LLM / prompt path** — pure presentational React. |
| Secrets management | **N/A** | **No secret** is used or rendered. |
| Read-only DB access | **N/A** | **No DB access, no persistence** — reads R4 via the injected `fetchSeam`, writes nothing. |
| Audit logging | **N/A** | Persists nothing; renders provenance's real consumer is `observability` (U21). |
| Error hygiene (no secret/PII leak) | **Compliant** | `error.message` only to the user; `error.detail` **never** rendered raw (NFR-OUTV-ERROR-1); `seed`/`corpus_version` **never** rendered (NFR-OUTV-PROV-1). |
| **Advisory-only (no verdict) — load-bearing** | **Compliant (load-bearing)** | Renders **no** `Recommendation`/`Confidence` namespace (NFR-OUTV-NOVERDICT-1: import-absence scan + rendered `queryBy*`-null over the enumerated set); advisory-vocabulary lints green (NFR-OUTV-ADVISORY-1); `direction` framed as a statistical position, never severity (NFR-OUTV-COPY-1). |
| **Bias-free framing (CON-BR1 downstream)** | **Compliant** | The view renders only the demographic-excluded statistical signals U18 produces (U18 `NFR-OUT-BIAS-1` upstream); it introduces no demographic field and no verdict. |
| Correct not-available vs no-anomaly signalling | **Compliant** | `NOT_AVAILABLE` (not analyzed) is asserted distinct from empty-`flagged_features` (analyzed, no anomalies) — NFR-OUTV-STATE-1 + NFR-OUTV-EMPTY-1 — so the underwriter is never misled. |

**No blocking finding.**

---

## 4. Settled items held (not re-opened)
- The **frozen FD** (BR-OUTV-1..10 + the four-state model + the folds) is the substrate — targets attach to it.
- **Q1-A**: `NFR-OUTV-NOVERDICT-1` is its **own** target (rendered-output absence ≠ import scan ≠ source lint).
- **Q2-A**: `NFR-OUTV-EMPTY-1` is its **own** target (analyzed-no-anomalies ≠ not-analyzed).
- **Q3-A**: the `outlier_model_version` footnote is a **single Code-Gen realization**; `NFR-OUTV-PROV-1` always gates the `seed`/`corpus_version` negative regardless.
- **Fold-B/C/D**: rendered-absence via `queryBy*`-null over an enumerated set (not substring); three distinct outlier fixtures (null / present-empty / present-populated); distinctive collision-proof provenance sentinels.
- **Deferred to NFR-Design / Code-Gen**: the exact `FLAG_DIRECTION_LABELS`/copy strings, the `shell/tokens` aesthetic values, the `fetchSeam` realization, whether the `outlier_model_version` footnote is included. **tier-B stays out-of-band / not required** (this is a UI unit; it never touches the corpus).
