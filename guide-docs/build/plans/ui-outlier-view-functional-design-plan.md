# Functional Design — Plan (Part 1) — `ui-outlier-view` (U20, C5, **Phase 2**)

**Stage**: BUILD → per-unit loop → **Functional Design Part 1 (Plan)** · **Unit**: U20 `ui-outlier-view` · C5 · **Phase 2** · **Depth**: **lighter (display)** · **Date**: 2026-07-17 · Story **US-UI-3** · FR-OUT-2.
**Built ON** (re-opening none): the frozen **WIRE-1 `api-contract.md`** — specifically the **2026-07-17 additive amendment (WIRE1-Fold-4)**: R4 `MemoView.outlier: OutlierResult | null` + the new `OutlierResult`/`FlaggedFeature`/`OutlierProvenance` wire shapes + the fifth `FlagDirection` (`high`/`low`) enum; the frozen **`ui-shell` (U10)** substrate (`shell/components` `AppFrame`/`Panel`/`Region`/`ReadOnlyRegion`/badges/`RoleGate`; `shell/copy` incl. `ADVISORY_VOCABULARY` + the one `FORBIDDEN_TERMS`; `shell/session` `RoleContext`/`useCurrentRole()`; `shell/tokens`); the frozen **`outlier-model` (U18)** `OutlierResult`/`FlaggedFeature`/`OutlierProvenance` **Python** schemas (confirmed to match the wire shapes exactly, §3); and the most-relevant **sibling precedent `ui-memo-view` (U6)** — its lighter 3-artifact FD set, its own-fetch/mirror-not-import composition, and its load-bearing **NFR-MEMO-SEPARATION-1** (RO-region-vs-narrative isolation).

**Status**: **Part 2 GENERATED — the FIVE `[Answer]` tags (§6) are FILLED (Q1-A, Q2-A, Q3-A, Q4-B, Q5-A); ambiguity-check RUN → CLEAN (three folds, no surface-and-stop); the lighter 3-artifact FD set generated** under `guide-docs/build/ui-outlier-view/functional-design/` (`business-rules.md` [BR-OUTV-1..10] · `domain-entities.md` [component/prop inventory + consumed shapes + 4-state render model] · `business-logic-model.md` [fetch/render lifecycle + validated Mermaid]). **STOPPED at the FD 2-option completion gate** (1. Request Changes / 2. Continue → NFR Requirements). Full Q&A re-embedded (§6, standing convention).

### Part-2 ambiguity-check verdict (CLEAN — three folds, none improvised)
- **OUTV-FD-Fold-1 (check i)** — the null-`outlier` "not available" state is a **fourth, distinct render state** ({LOADING · READY[outlier present] · NOT_AVAILABLE[resolved 2xx + `outlier===null`] · ERROR}); `NOT_AVAILABLE` is derived **only on a successful resolution** off the `outlier` **field**, so it never masks a genuine fetch ERROR. Mirrors `ui-memo-view`'s 4-state shape (its `pending` is our `NOT_AVAILABLE` analog); the intentional difference is field-derived-not-`status`-derived (a `ready` view can carry `outlier:null` in Phase 1).
- **OUTV-FD-Fold-2 (check ii)** — "isolation-by-absence" is **documented as forward-looking, not assumed**: if a later integration (Q1-deferred) co-renders `ui-memo-view`'s RO `Recommendation` region beside this panel, the **cross-panel** separation is the **integrator's** responsibility; this unit's contribution is that it renders **no `Recommendation` namespace** and frames its panel advisory-statistical (a boundary note in `business-rules.md`/`domain-entities.md`).
- **OUTV-FD-Fold-3 (check iii)** — `direction` (`high`/`low`) is rendered via outlier-local `FLAG_DIRECTION_LABELS` framing it as a **statistical position relative to the corpus distribution** (above/below the typical range), keyed by value, **advisory-vocabulary-lint-subject**, never a bare severity/verdict word — the `ui-memo-view` `MISSING_INFO_SOURCE_LABELS` precedent.

---

## 1. Carryover check + depth classification (verified, not assumed)

- **DISCOVER-carryover: CLEAN — first touch of U20.** No `guide-docs/build/ui-outlier-view/` dir, no `ui-outlier-view-*` plan, no `frontend/src/outlierView/` on disk. Nothing to resume; nothing to reconcile.
- **Depth: LIGHTER (display).** Verified on disk — `unit-of-work.md:247`: *"`ui-outlier-view` … outlier flags + SHAP in the memo view; conforms to the `ui-shell` contract (U10). US-UI-3. FR-OUT-2. **Depth: lighter (display); no write/commit control → no RBAC facet**."* `unit-of-work.md:261–263` lists `ui-outlier-view` among the display-only *lighter* candidates. Recommendation is **lighter** — a single presentational, read-only view for one story (US-UI-3), one route field (R4 `outlier`), no write path — matching the frozen `ui-memo-view`/`ui-queue`/`ui-history` lighter precedent. (Per `unit-of-work.md §4` the lighter tag is revisitable; **no reason to escalate** — this unit bears no invariant-write like `ui-approval-gate`/`ui-override-form`.)
- **FD Part 2 will produce the lighter 3-artifact set** under `guide-docs/build/ui-outlier-view/functional-design/`: `business-rules.md` (**BR-OUTV-\***), `domain-entities.md` (component/prop inventory folded, per the frozen UI-unit convention — no separate `frontend-components.md`), `business-logic-model.md` (the fetch/render-state lifecycle). Mirrors `ui-memo-view`'s exact FD set.

## 2. What `ui-outlier-view` builds (scope) and what it must NOT touch

### 2.1 Builds — a standalone presentational, read-only outlier view (`frontend/src/outlierView/`)
Fetches WIRE-1 **R4** and renders the **`outlier` (`OutlierResult | null`)** slice: the holistic `outlier_score` + `is_outlier`, and the per-feature `flagged_features` (`feature` · `z_score` · `shap_value` · `direction`) as **statistical anomaly signals**. Composes frozen `ui-shell` primitives; defines its **own local regions + a local R4 `fetchSeam`** (the `ui-memo-view`/`ui-queue` prop-injection precedent). **React + Tailwind, NO TypeScript** (FR-UI-5). Owns **no business logic** — no scoring, no rule eval, no authorization *decision*, no LLM, no commit; **imports no backend production code** and consumes the R4 shapes **by value** (reference-not-own).

### 2.2 Does NOT touch (held closed)
- **WIRE-1** (frozen; just amended — consumed **by shape**, **not** edited further).
- **`outlier-model` (U18, now frozen)** — reached only **`(orchestrated)`** via R4 (`unit-of-work-dependency.md:49`), **never imported** (cross-language reference-not-own; and `ui_outlier_view` is exactly a name the U18 `StructuralGuard` `reference_not_own` scan forbids importing).
- **`ui-shell` (U10)** and **`ui-memo-view` (U6)** and the other 5 frozen UI units — **composed/mirrored, never edited or promoted-into**; **no sibling-view import** (mirror the fetchSeam + StructuralGuard *convention*, not the module).
- **The closed composition root** (`backend/app/`, `frontend/src/app/`); **the tier-B corpus run** (unauthorized); the **`audit_store` Docker-guard gap**; **no other unit.**

### 2.3 The `(orchestrated)` edge — confirmed to mean no direct import
`unit-of-work-dependency.md:49` lists `ui-outlier-view (2) → ui-shell, auth-rbac, (orchestrated) outlier-model R`. `(orchestrated)` = the outlier data reaches the view **through the API/R4 orchestration**, not a direct module edge — exactly as `ui-memo-view` consumes `memo-agent-core`'s `DecisionMemo` through R4, never importing `memo_agent_core`. So `ui-outlier-view` has **no code edge to `outlier-model`**; it reads `OutlierResult` off the R4 body by shape.

## 3. Wire ↔ frozen-Python match (confirmed field-for-field — the amendment carries U18 verbatim)

| Wire shape (WIRE-1 §5, WIRE1-Fold-4) | Frozen Python (`outlier_model.schemas`, U18) | Match |
|---|---|---|
| `OutlierResult { outlier_score: float, is_outlier: bool, flagged_features: FlaggedFeature[], provenance: OutlierProvenance }` | `OutlierResult(outlier_score: float, is_outlier: bool, flagged_features: list[FlaggedFeature], provenance: OutlierProvenance)` | ✅ exact |
| `FlaggedFeature { feature: str, z_score: float, shap_value: float, direction: <FlagDirection> }` | `FlaggedFeature(feature: str, z_score: float, shap_value: float, direction: FlagDirection)` | ✅ exact |
| `OutlierProvenance { corpus_version: str, seed: int, outlier_model_version: str }` | `OutlierProvenance(corpus_version: str, seed: int, outlier_model_version: str)` | ✅ exact |
| `FlagDirection` = `high` \| `low` (§1 by-value) | `class FlagDirection(str, Enum): HIGH="high"; LOW="low"` | ✅ exact |

**No verdict/`Recommendation` field anywhere in `OutlierResult`** (U18 `NFR-OUT-ADVISORY-1`, by construction) — the advisory-only property the view inherits for free (nothing to accidentally render as a decision). `flagged_features` **MAY be empty** (a normal applicant). The view **defines no schema** — it reads these off R4.

## 4. `ui-shell` substrate this unit composes (frozen — imported, never edited)

| From `ui-shell` (frozen) | Used for |
|---|---|
| `AppFrame` / `Panel` / `Region { title, children, testid }` | page/layout chrome; the outlier panel container |
| `ReadOnlyRegion { children, testid }` *(candidate — see Q3)* | frame the outlier panel as read-only / advisory, if chosen |
| `shell/copy` (`ADVISORY_VOCABULARY`, the one `FORBIDDEN_TERMS`) | advisory-vocabulary conformance for outlier-local chrome (reuse the `advisory-vocabulary`/`no-inline-label` lints) |
| `shell/session` (`RoleContext`, `useCurrentRole()`) | available for chrome, **not gated on** (see Q2) |
| `shell/tokens` | aesthetics (values deferred to NFR-Design/Code-Gen) |
| **not** `RecommendationBadge`/`ConfidenceBadge` | this unit renders **no** `Recommendation`/`Confidence` namespace (those are `ui-memo-view`'s RO region) |
| **not** `RoleGate` | view-only, no gating (Q2) |

**Draft `BR-OUTV-*` rules to be authored in Part 2** (sketch, for grounding — pinned after the answers): BR-OUTV-1 read-only presentational display of the R4 `outlier` slice; BR-OUTV-2 the anomaly-signal framing (flags read as statistical signals, never a verdict — Q3); BR-OUTV-3 the null-`outlier` render state (Q4); BR-OUTV-4 view-only / no `RoleGate` / no router / no commit (Q2); BR-OUTV-5 single-source copy + advisory-vocabulary (reuse the frozen lints); BR-OUTV-6 deterministic `flagged_features` order preserved (no client re-sort); BR-OUTV-7 error `message`-only + Retry (the `ui-memo-view` error precedent); BR-OUTV-8 `data-testid` convention (`outlier-<element>-<purpose>`); BR-OUTV-9 provenance handling (Q5); BR-OUTV-10 reference-not-own (no backend import, no sibling-view import).

## 5. HOLDS (binding through Part 2)
- **No FD artifact generated in Part 1**; `guide-docs/build/ui-outlier-view/functional-design/` NOT created; no code; no `frontend/src/outlierView/`.
- **WIRE-1 consumed by shape, not edited further**; **`outlier-model` (U18) reached only via R4, never imported**; **`ui-shell`/`ui-memo-view` composed/mirrored, never edited**; **no sibling-view import**; **no backend Python import**.
- The **17 frozen P1 units + the closed composition root UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap** untouched; **no other unit started**; the 23-unit decomposition unchanged.

## 6. Clarifying questions (`[Answer]` tags — LEFT BLANK; lettered; full text below)

> Fill these; I then run the ambiguity-check against the answers + the frozen WIRE-1 (WIRE1-Fold-4) + `ui-shell` + `ui-memo-view` precedent + the U18 `OutlierResult` schema, then Part 2 (the FD artifact set) **on your explicit go**. Per the standing convention the full Q&A is re-embedded once answered. **No improvising on any ambiguity — flag and stop.**

### Q1 — Structural relationship to `ui-memo-view` (R4 is now shared by both units)
- **A.** **Stand entirely alone** — `ui-outlier-view` is its **own** view at `frontend/src/outlierView/`, fetching **R4 independently** via its **own local `fetchSeam`**, reading **only** the `outlier` slice (+ `status`/`application_id` as needed), composing `ui-shell` primitives, importing **no** sibling view unit (mirrors the `ui-queue`/`ui-memo-view` **fetchSeam + StructuralGuard convention**, not the module). On-screen co-location of the memo + outlier panels is a **later shell/router/app-integration concern** (deferred, exactly as `ui-memo-view` deferred navigation-to-commit). *(Recommended — the established "own fetch, no cross-unit import" pattern every prior UI unit used; reopens nothing frozen; the whole-R4-body-but-read-your-own-slice discipline mirrors how `ui-memo-view` reads `memo` and ignores `report`.)*
- **B.** **Extend `ui-memo-view`'s frozen component tree** — add the outlier panel as a new region *inside* the memo screen's composition. *(Rejected — this **reopens a frozen UI unit (U6)**; violates the frozen-unit hold.)*
- **C.** **A new shared composition** owning both panels (promoted into `ui-shell` or a new orchestrator). *(Rejected — promotes into frozen `ui-shell` or invents an unplanned unit; screen composition belongs to the deferred app/router integration.)*
- **D.** Other (describe).

`[Answer]:` A

### Q2 — The RoleGate-cosmetic-vs-authz pattern here (a read-only advisory display)
- **A.** **No `RoleGate`; view-only, read-only advisory display** — mirror `ui-memo-view`'s `NFR-MEMO-VIEWONLY-1` + `ui-history`: `shell/session` (`RoleContext`/`useCurrentRole()`) is **available** for chrome but **not gated on**; `auth-rbac` is a dependency only for **session/role context**, never a gating decision. Consistent with `unit-of-work.md:247` (*"no write/commit control → no RBAC facet"*); R4 is authenticated-any-role and the real boundary stays server-side. *(Recommended — this is a display like `ui-memo-view`/`ui-history`, not a write path like `ui-approval-gate`/`ui-override-form`; the classification explicitly says no RBAC facet.)*
- **B.** **A cosmetic `RoleGate`** on some element (e.g. show provenance/audit detail only to `auditor`/`admin`). *(Only if a role-conditional display is genuinely wanted — it adds a gating facet the classification says this unit does not have.)*
- **C.** Other (describe).

`[Answer]:` A

### Q3 — Displaying `flagged_features`/`shap_value`/`direction` as statistical signals, NOT a verdict (the SEPARATION analog)
- **A.** **Advisory statistical framing + reuse the frozen advisory lints; isolation-by-absence.** Render each flag as a clearly-labeled **statistical anomaly signal** — `feature` (via outlier-local copy) + `direction` (`high`/`low` = above/below the corpus mean) + `z_score` + `shap_value` attribution — under outlier-local chrome that frames the whole panel as **"statistical outlier analysis / advisory signal, not a decision"**, and **register the frozen `advisory-vocabulary` + `no-inline-label` lints on `src/outlierView/**`** (the `NFR-MEMO-ADVISORY-1`/`COPY-1` mechanism). This unit renders **no `Recommendation` namespace at all**, so isolation from the system verdict is **structural-by-absence** — there is nothing *within* the unit to separate *from* (unlike `ui-memo-view`'s LLM-narrative-vs-RO tension); the separation from the R4 `Recommendation` (which lives in `ui-memo-view`) is cross-unit and automatic. Optionally frame the panel with the frozen `ReadOnlyRegion` wrapper for a read-only/advisory cue. *(Recommended — grounded, lighter, reuses the frozen advisory machinery; honors "advisory-only" without cloning a separation whose teeth would have nothing to assert against inside this unit.)*
- **B.** **A dedicated isolation region with DOM-containment teeth** — build an `AnomalySignalRegion` wrapped like `ReadOnlyRegion` and assert (à la `NFR-MEMO-SEPARATION-1`) it is a **distinct DOM node** from any recommendation element. *(Heavier; and since no `Recommendation` is co-rendered in this unit, the containment teeth would assert against an absent sibling — lower value than in `ui-memo-view`.)*
- **C.** Other (describe).

`[Answer]:` A

### Q4 — Surfacing the null-`outlier` semantics (WIRE1-Fold-4: null in Phase 1 **and** when `status: pending`)
- **A.** **"Nothing renders"** — a null `outlier` ⇒ the outlier panel renders nothing (absent). *(The simplest, most honest reading of the wire rule; but for a standalone panel a blank panel can read as a missing/broken panel.)*
- **B.** **One explicit, neutral "outlier analysis not available" state** — a single derived state covering **both** null-causes (`status: pending` **and** Phase-1 `status: ready` with `outlier: null`), mirroring `ui-memo-view`'s explicit `pending` state (`NFR-MEMO-PENDING-1`). Note the null-`outlier` is **not** cleanly captured by R4 `status` alone (a `ready` view can still carry `outlier: null` in Phase 1), so the view derives its own `outlier-present | not-available` discriminator off the **field**, not the `status`. *(Recommended — honest + testable for a standalone panel; parallels the frozen sibling's explicit not-yet state; one neutral state, not two.)*
- **C.** Other (describe).

`[Answer]:` B

### Q5 — Whether/how `provenance` (`corpus_version`, `seed`, `outlier_model_version`) surfaces in the UI
- **A.** **Do not render provenance by default** (optionally a minimal `outlier_model_version` audit footnote). Provenance is **reproducibility/audit metadata** consumed by `observability` (U21), not display data; `ui-outlier-view` displays **flags + SHAP + score + `is_outlier`** (per `outlier-model` `domain-entities §6`). If an audit cue is wanted, surface **only** `outlier_model_version` as an unobtrusive footnote (the `ui-memo-view` `memo_hash`/`model_version` M-region precedent) — **not** `seed`/`corpus_version` in the visible UI. *(Recommended — keeps the advisory panel focused on the signals; provenance's real consumer is U21.)*
- **B.** **Render the full provenance triple** as an audit/attribution footer (parallels `ui-memo-view`'s M region). *(More auditable, but exposes `seed`/`corpus_version` in the UI for little display value.)*
- **C.** **Render no provenance at all** (drop it entirely from the view). *(Cleanest panel; loses even the version audit cue.)*
- **D.** Other (describe).

`[Answer]:` A

---

## 7. Gate
**Part 1 (Plan) WRITTEN — STOPPED at the plan-file gate.** The five `[Answer]` tags (Q1–Q5) are **BLANK**. On the filled answers: run the mandatory **ambiguity-check** against the answers + the frozen WIRE-1 (WIRE1-Fold-4) + the `ui-shell` substrate + the `ui-memo-view` precedent + the U18 `OutlierResult` schema — **surface-and-stop on any genuine gap, do not improvise** — then, **on the explicit go**, generate FD Part 2 (the lighter 3-artifact set: `business-rules.md` / `domain-entities.md` / `business-logic-model.md`). **Depth: lighter.** NO FD artifact generated in Part 1; `guide-docs/build/ui-outlier-view/functional-design/` NOT created; no code; no `frontend/src/outlierView/`. WIRE-1 · `outlier-model` (U18) · the 17 frozen P1 units · the closed composition root UNTOUCHED; tier-B NOT authorized; the `audit_store` Docker-guard gap untouched; no other unit started; the 23-unit decomposition unchanged.
