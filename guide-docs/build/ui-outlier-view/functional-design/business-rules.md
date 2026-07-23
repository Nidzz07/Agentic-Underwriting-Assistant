# Business Rules — `ui-outlier-view` (U20, C5, Phase 2)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U20 `ui-outlier-view` · C5 · **Phase 2** · **Depth**: lighter (display) · **Date**: 2026-07-17 · Story **US-UI-3** · FR-OUT-2.
**Nature**: `ui-outlier-view` owns **no business logic** — no scoring, no rule eval, no authorization *decision*, no LLM, no commit. It is a **presentational, read-only** React view that fetches WIRE-1 **R4** and renders the **`outlier` (`OutlierResult | null`)** slice as **statistical anomaly signals** — advisory input for the underwriter, **never a verdict or recommendation**. The rules below (**BR-OUTV-\***) are **checkable** presentational/structural invariants, each grounded in a frozen contract or a settled answer. Built on **Q1–Q5 (A/A/A/B/A)** + the ambiguity-check folds **OUTV-FD-Fold-1..3**, re-opening none of WIRE-1 / `ui-shell` / `ui-memo-view` / `outlier-model` (U18).

**React + Tailwind, NO TypeScript** (FR-UI-5). Consumes R4 shapes **by value** (reference-not-own); imports **no** backend Python and **no** sibling view unit.

---

## Rules

### BR-OUTV-1 — Standalone read-only display of the R4 `outlier` slice (Q1-A)
`ui-outlier-view` lives at **`frontend/src/outlierView/`** as its **own** view, fetching **R4** (`GET /applications/{application_id}/memo`) independently via its **own local `fetchSeam`** (injected — the `ui-memo-view`/`ui-queue` prop-injection precedent), and reads **only** the `outlier` slice of the `MemoView` body (`+ status`/`application_id` as needed). It **composes** frozen `ui-shell` primitives and **imports no sibling view unit**. On-screen co-location with the memo panel is a **later shell/router/app-integration concern** (deferred).
- **Grounded**: Q1-A; `ui-memo-view` `domain-entities §1` (own `frontend/src/memoView/` + own fetchSeam, no sibling import); WIRE-1 R4 (WIRE1-Fold-4).
- **Checkable**: the unit fetches R4 via the injected `fetchSeam`; it reads `view.outlier` off the R4 body; no `import` of any sibling view module (`memoView`/`queue`/etc.) — a `reference-not-own` scan; no backend Python import.

### BR-OUTV-2 — Anomaly-signal framing: flags are statistical signals, never a verdict (Q3-A; OUTV-FD-Fold-2)
The view renders each flagged feature as a **statistical anomaly signal** and frames the whole panel as **"statistical outlier analysis / advisory signal, not a decision."** It renders **no `Recommendation`/`Confidence` namespace at all** — so isolation from the system verdict is **structural-by-absence** (nothing within the unit to separate *from*). **Forward-looking (OUTV-FD-Fold-2)**: if a future integration (Q1-deferred) co-renders `ui-memo-view`'s RO `Recommendation` region beside this panel, **cross-panel** separation is the **integrator's** responsibility; this unit's guarantee is that it (a) contributes no `Recommendation` element and (b) frames its panel advisory-statistical.
- **Grounded**: Q3-A; PROJECT-BRIEF §11 (advisory-only); `outlier-model` `NFR-OUT-ADVISORY-1` (OutlierResult has no verdict field); `ui-memo-view` `NFR-MEMO-SEPARATION-1` (the RO-vs-narrative precedent, here satisfied by absence).
- **Checkable**: no `RecommendationBadge`/`ConfidenceBadge` import or render in `outlierView/`; no `Recommendation` wire value (`APPROVE`/`REFER`/`DECLINE-RECOMMEND`) appears in the view's static source; the panel chrome is advisory (BR-OUTV-5); the forward-looking cross-panel note is present in `domain-entities.md §7`.

### BR-OUTV-3 — Four-state render model; the null-`outlier` "not available" state is field-derived (Q4-B; OUTV-FD-Fold-1)
A single closed local state enum drives the view: **`OUTLIER_STATE = { LOADING, READY, NOT_AVAILABLE, ERROR }`**. `READY` ⇒ fetch resolved 2xx **and** `outlier` non-null (render the signals). **`NOT_AVAILABLE`** ⇒ fetch resolved 2xx **and** `outlier === null` — a single neutral **"outlier analysis not available for this application"** state covering **both** null-causes (`status: pending` **and** Phase-1 `status: ready` with `outlier: null`). `NOT_AVAILABLE` is derived off the **`outlier` field**, not off R4 `status` (a `ready` view can carry `outlier: null` in Phase 1), and **only on a successful resolution** — it never masks a genuine fetch `ERROR`.
- **Grounded**: Q4-B; WIRE1-Fold-4 (null in Phase 1 **and** when pending); `ui-memo-view` `NFR-MEMO-PENDING-1` (explicit not-yet state precedent, there derived off `status`).
- **Checkable**: a resolved response with `outlier: null` (from a `pending` body **or** a Phase-1 `ready` body) renders the `NOT_AVAILABLE` state; a resolved response with `outlier` present renders `READY`; a fetch failure renders `ERROR` (not `NOT_AVAILABLE`); a `NOT_AVAILABLE`-cause is never reached from an error path.

### BR-OUTV-4 — View-only: no `RoleGate`, no router, no commit affordance (Q2-A)
The view renders **no `RoleGate`** and gates nothing; `shell/session` (`RoleContext`/`useCurrentRole()`) is **available** for chrome but **not gated on**. It emits **no** outward action (no selection, no commit, no navigation) and imports **no router**. There is **no write path** — consistent with `unit-of-work.md:247` ("no write/commit control → no RBAC facet"). The real authorization boundary stays `auth-rbac` server-side.
- **Grounded**: Q2-A; `unit-of-work.md:247`; `ui-memo-view` `NFR-MEMO-VIEWONLY-1`.
- **Checkable**: no `RoleGate` import/render in `outlierView/`; no router import; no `POST`/commit call; the view exposes no outward event prop that mutates.

### BR-OUTV-5 — Single-source copy + advisory-vocabulary; `direction` framed as a statistical position (Q3-A; OUTV-FD-Fold-3)
All chrome/labels live in an **outlier-local `outlierView/copy.js`** (mirroring `ui-memo-view`'s local `copy.js`) — **lint-subject**: the frozen `advisory-vocabulary` + `no-inline-label` lints are registered on `src/outlierView/**` (the `NFR-MEMO-ADVISORY-1`/`COPY-1` mechanism). The `direction` enum (`high`/`low`) is rendered via **`FLAG_DIRECTION_LABELS`** framing it as a **statistical position relative to the corpus distribution** (above / below the typical range), keyed **by value** — **never** a bare severity/verdict word (`high` must not read as "high risk"). No value equals a `shell/copy` display label; none contains a `FORBIDDEN_TERMS.systemOutput` token.
- **Grounded**: Q3-A; OUTV-FD-Fold-3; `ui-memo-view` `MISSING_INFO_SOURCE_LABELS` precedent (memo-local, keyed by value, lint-subject); `ui-shell` `shell/copy` `ADVISORY_VOCABULARY`/`FORBIDDEN_TERMS`.
- **Checkable**: `FLAG_DIRECTION_LABELS` maps `high`/`low` to statistical-position phrases (not "risk"/severity/verdict words); the `advisory-vocabulary`/`no-inline-label` lints pass on `outlierView/**`; no forbidden system-output token in the local copy.

### BR-OUTV-6 — Deterministic `flagged_features` order preserved; no client re-sort
The view renders `flagged_features` **in the order delivered by R4** — it performs **no client-side re-sort/re-rank**. (The backend order is a deterministic property of the frozen U18 model; the view is a faithful renderer.)
- **Grounded**: `outlier-model` determinism (U18 `NFR-OUT-DET-1`, stable field order); `ui-memo-view` `NFR-MEMO-LISTORDER-1` (preserve backend order) precedent.
- **Checkable**: RTL over a populated, deliberately non-sorted `flagged_features` fixture — the rendered row order equals the input order; no comparator/`.sort()` on the list in the view source.

### BR-OUTV-7 — Error is `message`-only; `code` via testid; `detail` never raw; same-resource Retry
On an R4 fetch failure (any non-2xx or transport error), the view renders `error.message` to the user, binds `error.code` to a hidden testid (not visible text), **never** renders `error.detail` raw, and offers a **Retry** that re-fetches R4 for the **same** `applicationId`. Mirrors `ui-memo-view`'s error contract (the shared `normalizeError` envelope, WIRE-1 §4).
- **Grounded**: WIRE-1 §4 error envelope; `ui-memo-view` `NFR-MEMO-ERROR-1`.
- **Checkable**: a non-2xx / transport failure renders `error.message` + a Retry; `error.code` is on a hidden testid; `error.detail` is never rendered raw; Retry re-fetches the same `applicationId`.

### BR-OUTV-8 — `data-testid` convention (`outlier-<element>-<purpose>`)
Every assertion-relevant element carries a stable `data-testid` of shape **`outlier-<element>-<purpose>`** (applying, not re-inventing, the frozen `shell-<primitive>-<purpose>` / `memo-<element>-<purpose>` convention), enforced by an `outlier-testid-convention` lint. This makes the four states + the per-flag rows structurally testable.
- **Grounded**: FR-UI-3; `ui-shell` testid convention; `ui-memo-view` `NFR-MEMO-TESTID-1`.
- **Checkable**: the state containers + the flag rows + score/`is_outlier` elements + error message/code/retry carry `outlier-*` testids; the convention lint passes.

### BR-OUTV-9 — Provenance not rendered by default; at most an `outlier_model_version` footnote (Q5-A)
The view does **not** render `provenance` by default. `provenance` is reproducibility/audit metadata whose real consumer is `observability` (U21). At most, a **minimal `outlier_model_version` footnote** may be surfaced (the `ui-memo-view` `memo_hash`/`model_version` M-region precedent) — **never** `seed` or `corpus_version` in the visible UI.
- **Grounded**: Q5-A; `outlier-model` `domain-entities §6` (ui-outlier-view needs flags+SHAP+score+`is_outlier`; observability needs provenance); `outlier-model` `NFR-OUT-SEC-1` (provenance non-PII but audit-scoped).
- **Checkable**: `seed` and `corpus_version` never appear in the view's rendered output; if present, only `outlier_model_version` is surfaced, as an unobtrusive footnote.

### BR-OUTV-10 — Reference-not-own: consume R4 shapes by value; edit nothing frozen; import no consumer/sibling (Q1-A)
The view consumes `OutlierResult`/`FlaggedFeature`/`OutlierProvenance`/`FlagDirection` **by value** off R4 and **re-declares none**; it imports **no** backend Python (cross-language boundary), **no** `outlier-model` (reached only `(orchestrated)` via R4), and **no** sibling view unit; it **composes** `ui-shell` primitives without editing or promoting-into `ui-shell`.
- **Grounded**: Q1-A; `unit-of-work-dependency.md:49` (`(orchestrated) outlier-model R`); `ui-memo-view` reference-not-own boundary; U18 `StructuralGuard` forbids importing `ui_outlier_view` (the reciprocal boundary).
- **Checkable**: no backend/Python import; no `outlier-model`/`memoView`/`queue`/other sibling import; `ui-shell` imported read-only (no edit, nothing promoted); the view defines no schema.

---

## Rule → source traceability

| Rule | Frozen source / decision |
|---|---|
| BR-OUTV-1 | Q1-A; ui-memo-view own-fetch precedent; WIRE-1 R4 (WIRE1-Fold-4) |
| BR-OUTV-2 | Q3-A; OUTV-FD-Fold-2; PROJECT-BRIEF §11; U18 NFR-OUT-ADVISORY-1; ui-memo-view SEPARATION-1 |
| BR-OUTV-3 | Q4-B; OUTV-FD-Fold-1; WIRE1-Fold-4; ui-memo-view PENDING-1 |
| BR-OUTV-4 | Q2-A; unit-of-work.md:247; ui-memo-view VIEWONLY-1 |
| BR-OUTV-5 | Q3-A; OUTV-FD-Fold-3; ui-memo-view MISSING_INFO_SOURCE_LABELS; ui-shell copy |
| BR-OUTV-6 | U18 NFR-OUT-DET-1; ui-memo-view LISTORDER-1 |
| BR-OUTV-7 | WIRE-1 §4; ui-memo-view ERROR-1 |
| BR-OUTV-8 | FR-UI-3; ui-shell testid; ui-memo-view TESTID-1 |
| BR-OUTV-9 | Q5-A; U18 domain-entities §6; U18 NFR-OUT-SEC-1 |
| BR-OUTV-10 | Q1-A; unit-of-work-dependency.md:49; ui-memo-view reference-not-own |

**No orphan**: US-UI-3 / FR-OUT-2 → the display rules (BR-OUTV-1/2/6/8/9); the advisory-only constraint → BR-OUTV-2/5; the null/lifecycle semantics → BR-OUTV-3/7; the view-only boundary → BR-OUTV-4/10.
