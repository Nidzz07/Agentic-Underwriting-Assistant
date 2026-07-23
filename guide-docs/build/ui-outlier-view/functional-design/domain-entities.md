# Domain Entities — `ui-outlier-view` (U20, C5, Phase 2)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U20 `ui-outlier-view` · C5 · **Phase 2** · **Depth**: lighter (display) · **Date**: 2026-07-17 · Story **US-UI-3** · FR-OUT-2.
**Scope**: the outlier view — a **presentational, read-only** view that fetches WIRE-1 **R4** and renders the **`outlier` (`OutlierResult | null`)** slice as **statistical anomaly signals**. A UI unit's "entities" are its **component/module + prop-shape inventory** (folded here, mirroring `ui-memo-view`/`ui-queue` — no dedicated `frontend-components.md`) + the consumed value shapes + the render-state model. **React + Tailwind, NO TypeScript** (FR-UI-5). Built on **Q1–Q5 (A/A/A/B/A)** + **OUTV-FD-Fold-1..3**, re-opening none. **NO code in this stage.**

---

## 1. Location & composition boundary (Q1-A)

`ui-outlier-view` lives at **`frontend/src/outlierView/`**. It **imports** frozen `ui-shell` (U10) primitives + copy + session context and **composes** them; it **defines its own local regions + a local R4 `fetchSeam`** and **nothing is promoted into `ui-shell`** (ui-shell stays frozen). It **does not import** `ui-memo-view` (U6) or any sibling view — it **mirrors** their fetchSeam + StructuralGuard **convention**, not the module. It renders exactly one panel (the outlier analysis) inside the shell `AppFrame`.

| Consumes from `ui-shell` (frozen) | Used for |
|---|---|
| `AppFrame` | page shell / layout chrome (the outlier panel mounts inside it) |
| `Panel` / `Region { title, children, testid }` | bordered container for the outlier panel + its states |
| **`ReadOnlyRegion { children, testid }`** | frames the outlier panel as **read-only / advisory** (the read-only cue; no recommendation inside it) |
| `shell/copy` (`ADVISORY_VOCABULARY`, the one `FORBIDDEN_TERMS`) | advisory-vocabulary conformance for the outlier-local copy (reuse `advisory-vocabulary` / `no-inline-label` lints) |
| `shell/session` (`RoleContext`, `useCurrentRole()`) | available for chrome, **not gated on** (Q2-A / BR-OUTV-4) |
| `shell/tokens` | aesthetics (values deferred to NFR-Design / Code-Gen) |

> **Not consumed**: `RoleGate` (Q2-A — view-only, no gating). `RecommendationBadge` / `ConfidenceBadge` (BR-OUTV-2 — this unit renders **no** `Recommendation`/`Confidence` namespace). No backend Python import (cross-language reference-not-own). No `ui-memo-view` / `ui-queue` import (sibling convention, not a dependency).

---

## 2. Consumed value shapes (by value, from WIRE-1 R4 `outlier` — **not owned, not re-cased**)

These mirror the **frozen** WIRE-1 §5 (WIRE1-Fold-4) + `outlier_model.schemas` (U18) shapes **verbatim** (confirmed field-for-field, plan §3). `ui-outlier-view` **defines no schema** — it reads these off the R4 response.

| Shape | Definition (as delivered by WIRE-1 R4) | Notes |
|---|---|---|
| **`MemoView`** (R4 body) | `{ application_id, recommendation_id, status: "ready"\|"pending", profile, report, memo, outlier: OutlierResult \| null }` | the view reads **only** `outlier` (+ `application_id`; `status` **not** the outlier discriminator — BR-OUTV-3) |
| **`OutlierResult`** (`outlier`, when present) | `{ outlier_score: float, is_outlier: bool, flagged_features: FlaggedFeature[], provenance: OutlierProvenance }` | `flagged_features` **MAY be empty** (a normal applicant → a valid, non-anomalous result). **No verdict field** (advisory-only, U18 NFR-OUT-ADVISORY-1) |
| **`FlaggedFeature`** (list item) | `{ feature: str, z_score: float, shap_value: float, direction: <FlagDirection value: high\|low> }` | rendered as one statistical-anomaly-signal row; `direction` via `FLAG_DIRECTION_LABELS` (BR-OUTV-5) |
| **`OutlierProvenance`** (`provenance`) | `{ corpus_version: str, seed: int, outlier_model_version: str }` | **not rendered by default** (Q5-A / BR-OUTV-9); at most an `outlier_model_version` footnote; `seed`/`corpus_version` never shown |
| **`FlagDirection`** | `high` \| `low` (WIRE-1 §1 by-value) | statistical position vs the corpus mean (above / below the typical range) — **never** a severity/verdict word (OUTV-FD-Fold-3) |
| **Error envelope** (non-2xx / transport) | `{ error: { code, message, detail? } }` | `message` → user; `code` → hidden testid; `detail` **never** raw (BR-OUTV-7) |

> **`profile`/`report`/`memo`/`recommendation`/`confidence`** are delivered on the R4 body but are **not** render sources for this unit (they are `ui-memo-view`'s territory) — **named-not-rendered here**.

---

## 3. Render-state model (Q4-B / OUTV-FD-Fold-1 — a fourth, field-derived state)

A single closed enum drives what the view renders: **`OUTLIER_STATE = { LOADING, READY, NOT_AVAILABLE, ERROR }`** (a local view constant, not a backend enum).

| State | Meaning | Renders |
|---|---|---|
| `LOADING` | R4 fetch in flight | a loading placeholder (`OutlierStateView`) |
| `READY` | fetch resolved 2xx **and** `outlier` non-null | the **signals**: `OutlierScoreRegion` (`outlier_score` + `is_outlier`) + `FlaggedFeaturesRegion` (the `flagged_features` rows) |
| `NOT_AVAILABLE` | fetch resolved 2xx **and** `outlier === null` | a distinct neutral **"outlier analysis not available for this application"** message (`OutlierStateView`) — covers **both** null-causes (`status: pending` **and** Phase-1 `status: ready` + `outlier: null`), **derived off the `outlier` field**, not `status` |
| `ERROR` | R4 fetch failed (any non-2xx or transport error) | `error.message` + a **Retry** affordance (`OutlierStateView`) |

> **Distinct from a genuine error (OUTV-FD-Fold-1)**: `NOT_AVAILABLE` is reached **only on a successful (2xx) resolution** with `outlier === null`; a fetch failure routes to `ERROR` (never `NOT_AVAILABLE`), so the "not available" state can never mask a real error. **Contrast `ui-memo-view`**: its `pending` derives from the R4 `status`; here `NOT_AVAILABLE` derives from the **`outlier` field** (a `ready` view can still carry `outlier: null` in Phase 1).

---

## 4. Component / module inventory (hierarchy + prop shapes — JS/JSX, no TS)

**Hierarchy**

```text
AppFrame (ui-shell)
└── Panel  (ui-shell — outlier container)
    └── OutlierView                       [owns fetch + render-state; the only stateful component]
        ├── OutlierStateView              [loading | not-available | error presentational states]
        └── (ready state)
            └── ReadOnlyRegion (ui-shell) [frozen wrapper — frames the panel read-only/advisory]
                ├── OutlierScoreRegion    [outlier_score + is_outlier, advisory chrome]     (local)
                └── FlaggedFeaturesRegion [flagged_features -> statistical-signal rows]      (local)
                    └── (row x N)         [{ feature-label, direction-label, z_score, shap_value }]
```

**Prop shapes**

| Component | Prop shape (JSX) | Role / behavior |
|---|---|---|
| **`OutlierView`** | `{ applicationId, fetchSeam }` — `fetchSeam` injected (mirrors `ui-memo-view`) | The **only** stateful component: fetches R4 for `applicationId`, holds `{ state, outlier, error }`, selects `OutlierStateView` vs the ready composition. Derives `state` per §3 (`NOT_AVAILABLE` off `outlier === null`). Emits **nothing** upward (view-only, BR-OUTV-4). |
| **`OutlierStateView`** | `{ state, error, onRetry, testid }` — `state ∈ {loading, not_available, error}` | Presentational. `loading` → placeholder; `not_available` → the neutral "outlier analysis not available" message (outlier-local copy); `error` → `error.message` + a Retry wired to `onRetry`. Renders **no** signal regions. |
| **`OutlierScoreRegion`** | `{ outlierScore, isOutlier, testid }` | Presentational (advisory). Renders `outlier_score` + `is_outlier` under outlier-local chrome framing them as a **statistical anomaly score**, not a verdict (BR-OUTV-2). No affordance. |
| **`FlaggedFeaturesRegion`** | `{ flaggedFeatures, testid }` where `flaggedFeatures: FlaggedFeature[]` | Presentational. Renders the flags **in the delivered order** (BR-OUTV-6); empty array → a neutral "no anomalous features" message (outlier-local copy). Each row shows the `feature` label + the `direction` via `FLAG_DIRECTION_LABELS` (statistical position) + `z_score` + `shap_value` — framed as a statistical signal (BR-OUTV-5). |

> **No outward event**: `ui-outlier-view` emits **nothing** — no selection, no commit, no navigation. It imports **no router** (BR-OUTV-4).

---

## 5. Outlier-local copy module (`outlierView/copy.js` — realization detail, lint-subject)

Outlier-specific chrome + the `FlagDirection` labels are kept **out of the components** in a local copy module (the `ui-memo-view` `copy.js` precedent). **Lint-subject** (BR-OUTV-5): may **not** inline a `shell/copy` display label (`no-inline-label`) and may **not** contain forbidden system-output vocabulary (`advisory-vocabulary`, the one `FORBIDDEN_TERMS`).

| Key | Purpose | Notes |
|---|---|---|
| `FLAG_DIRECTION_LABELS` | human labels for the two `FlagDirection` values | `high` / `low` → **statistical-position phrases** (above / below the typical corpus range); keyed **by value**; **no** severity/verdict word (OUTV-FD-Fold-3) |
| `notAvailableMessage` | the "outlier analysis not available for this application" text | the `NOT_AVAILABLE` state (Q4-B) |
| `loadingLabel` | loading placeholder text | — |
| `retryLabel` | Retry control text | reused pattern from `ui-memo-view` chrome |
| `panelHeading` / `scoreHeading` / `flagsHeading` | panel + region headings | advisory chrome; frame the panel as **statistical / advisory**, not a decision |
| `noFlagsLabel` | neutral empty-list text | for empty `flagged_features` (a normal applicant) |
| `outlierScoreLabel` / `isOutlierLabel` | labels for the score + is_outlier | statistical framing, not severity |
| `modelVersionFootnoteLabel` | optional `outlier_model_version` footnote label (Q5-A) | **only** `outlier_model_version`; never `seed`/`corpus_version` |
| `unknownErrorMessage` | fallback error text | mirrors `ui-memo-view`'s fallback |

> **Value-collision guard**: no value equals a `shell/copy` display label, and none contains a `FORBIDDEN_TERMS.systemOutput` token — checked by the reused lints (BR-OUTV-5).

---

## 6. `data-testid` inventory (`outlier-<element>-<purpose>` — BR-OUTV-8)

| Element | `data-testid` | Notes |
|---|---|---|
| Outlier container (ready root) | `outlier-view` | the `READY`-state composition root (inside `ReadOnlyRegion`) |
| Score region | `outlier-region-score` | `outlier_score` + `is_outlier` |
| Outlier score value | `outlier-score` | the holistic score |
| Is-outlier flag | `outlier-isoutlier` | the boolean decision-boundary indicator |
| Flagged-features region | `outlier-region-flags` | the `flagged_features` list root |
| A single flag row | `outlier-flag-<feature>` | interpolates the feature name |
| Loading state | `outlier-state-loading` | loading placeholder |
| Not-available state | `outlier-state-notavailable` | the field-derived neutral state (Q4-B) |
| Error state | `outlier-state-error` | error container |
| Error message (visible) | `outlier-error-message` | carries `error.message` (BR-OUTV-7) |
| Error code (hidden binding) | `outlier-error-code` | carries `error.code` — **not** visible UI text |
| Retry control | `outlier-error-retry` | re-fetch R4 for the same `applicationId` |
| Model-version footnote (optional) | `outlier-provenance-modelversion` | only if surfaced (Q5-A); `outlier_model_version` only |

---

## 7. Boundary — what `ui-outlier-view` does NOT own

- **No verdict / recommendation** — renders **no** `Recommendation`/`Confidence` namespace; `OutlierResult` has no verdict field (BR-OUTV-2). **Forward-looking (OUTV-FD-Fold-2)**: when a future integration (Q1-deferred) co-renders `ui-memo-view`'s RO `Recommendation` region beside this panel, the **cross-panel** visual/structural separation is that **integrating unit's** responsibility; `ui-outlier-view`'s guarantee is that it contributes no `Recommendation` element and frames its panel advisory-statistical. **This is a documented forward-looking note, not an assumption that co-rendering never happens.**
- **No authorization decision** — no `RoleGate`, gates nothing (Q2-A). R4 is authenticated any-role; the boundary stays `auth-rbac` server-side.
- **No write / commit / routing** — no commit affordance, no router, no outward mutating event (BR-OUTV-4).
- **No scoring / no re-sort** — the view never computes or re-ranks; it renders R4's `outlier` faithfully, in the delivered order (BR-OUTV-6). Scoring is `outlier-model`'s (U18) frozen concern, reached only `(orchestrated)` via R4.
- **No provenance display by default** — `seed`/`corpus_version` never shown; at most an `outlier_model_version` footnote (Q5-A / BR-OUTV-9).
- **No token values / no schema** — aesthetics from `shell/tokens` (deferred); shapes from WIRE-1 R4 (by value).
- **No route implementation** — the R4 endpoint is `backend/app/main.py`, deferred to Build & Test; `ui-outlier-view` consumes the R4 **contract shape**, fetching a mocked R4 (via the injected `fetchSeam`) in tests.
