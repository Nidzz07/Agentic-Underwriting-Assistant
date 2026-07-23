# NFR Design — Plan (Part 1) — `ui-outlier-view` (U20, C5, **Phase 2**)

**Stage**: BUILD → per-unit loop → **NFR Design Part 1 (Plan)** · **Unit**: U20 `ui-outlier-view` · C5 · **Phase 2** · **Depth**: **lighter (display)** · **Date**: 2026-07-17 · Story **US-UI-3** · FR-OUT-2.
**Built ON** (re-opening none): the frozen **FD** (**BR-OUTV-1..10**; the component/prop inventory `OutlierView`/`OutlierStateView`/`OutlierScoreRegion`/`FlaggedFeaturesRegion`; the **four-state render model** with the field-derived `NOT_AVAILABLE`; the advisory-statistical framing; the reference-not-own boundary + **OUTV-FD-Fold-2**) **and** the approved **NFR Requirements** (**thirteen `NFR-OUTV-*`**; the load-bearing **STATE-1 / NOVERDICT-1** pair; folds **Fold-A..D**). Mirrors the **frozen UI NFR-Design precedent**: `ui-memo-view` (§P1..P10 named patterns; **by-construction via prop signatures**) + `ui-history` (`CommittedActionRegion`/`SystemRecommendationRegion` **prop-exclusion**; the **header-comment self-evidence** convention, NFR-DESIGN-Fold-1; the **visible-graph-property** Mermaid).

**Status**: **Part 2 GENERATED — the THREE `[Answer]` tags (§4) are FILLED (Q1-A, Q2-A, Q3-A — all structural); ambiguity-check RUN → CLEAN (one fold, no surface-and-stop); the two NFR-Design artifacts generated** under `guide-docs/build/ui-outlier-view/nfr-design/` (`nfr-design-patterns.md` [P-OUTV-1..10, P-OUTV-1/2 load-bearing] · `logical-components.md` [six components + exact prop shapes + reference-not-own + component→target coverage + validated Mermaids]). **STOPPED at the NFR Design 2-option completion gate** (1. Request Changes / 2. Continue → Infrastructure Design). Full Q&A re-embedded (§4, standing convention).

### Part-2 ambiguity-check verdict (CLEAN — one fold, not improvised)
- **NFR-ND-OUTV-Fold-1** — the **header-comment self-evidence convention is PINNED MANDATORY** (no longer a "candidate", §3): a header comment is a **non-optional Code-Gen deliverable** on `OutlierView` (state-machine failure-routing + field-derived `NOT_AVAILABLE`), `OutlierScoreRegion` + `FlaggedFeaturesRegion` (no `recommendation`/`confidence`/`provenance` path), and `fetchSeam` (read-only R4 seam, no write, mirrors-not-imports) — mirroring `ui-history` NFR-DESIGN-Fold-1 + `ui-approval-gate`'s explicit call-out. **Documentation only, NOT enforcement** (the prop signatures + the branch ordering + the StructuralGuard scans are the enforcement). Consistent with choosing structural-A for all three by-construction guarantees.

---

## 1. By-construction mechanism for this unit (stated once, upheld everywhere)

Like every frozen UI unit, a "by-construction" guarantee is realized through the mechanisms React actually affords: **(i) prop signatures where the forbidden thing has no path** (a region whose props carry no `recommendation`/`confidence`/`provenance` cannot render one — the `ui-history` `CommittedActionRegion` precedent); **(ii) state-transition ordering where the forbidden state is unreachable on a branch** (a failure routed to `ERROR` before the `outlier`-null check is ever evaluated); **(iii) the `StructuralGuard` substrate (lint/AST/import scans + detector self-tests)** as the regression layer; **(iv) header comments as documentation only — NOT enforcement** (the `ui-history` NFR-DESIGN-Fold-1 self-evidence convention). The three `[Answer]` questions (§4) decide, per the user's framing, whether the two load-bearing guarantees are **structural (A)** or **test-only (B)**.

## 2. Draft pattern set `P-OUTV-1..10` (each → its `NFR-OUTV-*` target + component; no orphan)

| Pattern | → Target(s) | Component(s) | By-construction mechanism |
|---|---|---|---|
| **P-OUTV-1 FieldDerivedStateMachinePattern** *(LOAD-BEARING)* | **NFR-OUTV-STATE-1** | `OutlierView` | The state machine routes a fetch **failure → `ERROR`** on a branch evaluated **before** the `outlier`-null check; `NOT_AVAILABLE` is reachable **only** on the success branch where `outlier === null`. **Contrast** `ui-memo-view`'s `StatusDiscriminatorPattern` (pending off `view.status`): here the discriminator is the **`outlier` field** on a **resolved** response, so a Phase-1 `ready`+null still ⇒ `NOT_AVAILABLE`. *(Q1: structural failure-routing vs test-only.)* |
| **P-OUTV-2 NamespaceExclusionByPropSignaturePattern** *(LOAD-BEARING)* | **NFR-OUTV-NOVERDICT-1** | `OutlierScoreRegion`, `FlaggedFeaturesRegion` | Prop signatures carry **no `recommendation`/`confidence` prop or path** — mirroring `ui-history` `CommittedActionRegion` (`{action,reason,underwriterId,testid}` only, no system-namespace path). A verdict is **structurally unnameable** in this unit's render tree. *(Q2: structural prop-exclusion vs test-only.)* |
| **P-OUTV-3 ProvenanceExclusionByPropSignaturePattern** | **NFR-OUTV-PROV-1** | `OutlierScoreRegion`, `FlaggedFeaturesRegion` | The rendering regions **never receive `provenance`/`seed`/`corpus_version` as props at all** — the negative guarantee is structural (a region cannot render what it never receives). Any `outlier_model_version` footnote (single realization, Q3-A of NFR-Req) is the **only** provenance prop, passed to a distinct footnote slot, never `seed`/`corpus_version`. *(Q3: structural provenance prop-exclusion vs test-only.)* |
| **P-OUTV-4 DistinctBranchEmptyVsAbsentPattern** | NFR-OUTV-EMPTY-1 | `FlaggedFeaturesRegion` (empty) vs `OutlierStateView` (not-available) | "analyzed, no anomalies" and "not analyzed" are **two structurally distinct render branches** (different components + testids `outlier-region-flags`-empty vs `outlier-state-notavailable`), not two messages in one branch. |
| **P-OUTV-5 OrderPreservingListPattern** | NFR-OUTV-LISTORDER-1 | `FlaggedFeaturesRegion` | renders `flagged_features` **in the delivered order**; no comparator/`.sort()` — the frozen `ui-memo-view` `OrderPreservingListPattern` precedent. |
| **P-OUTV-6 FetchSeamPattern** | NFR-OUTV-FETCH-1 (+ ERROR-1 Retry) | `fetchSeam` (injected), `OutlierView` | an **own local thin `outlierView/fetchSeam`** builds the R4 request by `applicationId`; **injected** into `OutlierView`; tests inject a **single capturing double** (Fold-A). |
| **P-OUTV-7 ErrorEnvelopeToRenderPattern** | NFR-OUTV-ERROR-1 | `OutlierStateView` | maps the WIRE-1 error envelope `{error:{code,message,detail}}` to the error state — `message` visible, `code` hidden testid, `detail` **never** raw; Retry re-fetches the same `applicationId`. |
| **P-OUTV-8 RoleInvariantRenderingPattern** | NFR-OUTV-VIEWONLY-1 | `OutlierView` | composes **no `RoleGate`**, imports **no router**, exposes **no commit affordance**, gates on nothing (`shell/session` available, not gated). |
| **P-OUTV-9 SharedForbiddenTermsReusePattern** | NFR-OUTV-ADVISORY-1 + NFR-OUTV-COPY-1 | `outlierView/copy.js`, `StructuralGuard` | **reuses `ui-shell`'s ONE `FORBIDDEN_TERMS` + ESLint** (`advisory-vocabulary`/`no-inline-label`) on `src/outlierView/**` — no new word-list; `FLAG_DIRECTION_LABELS` frames `direction` as a **statistical position**, keyed by value, no severity word (OUTV-FD-Fold-3). |
| **P-OUTV-10 StructuralGuardPattern** | NFR-OUTV-SCOPE-1 + NFR-OUTV-TESTID-1 + NFR-OUTV-NOTS-1 (+ structural halves of NOVERDICT/ADVISORY) | `StructuralGuard` (test-only substrate) | **one substrate** of independent scans, **each with a detector self-test** (non-vacuity): no-sibling/backend-import (SCOPE-1); testid-convention (TESTID-1); no-`.ts`/`.tsx` (NOTS-1); no-`RecommendationBadge`/`ConfidenceBadge`-import (the structural half of NOVERDICT-1); the advisory lints. |

**No orphan**: STATE-1→P1; NOVERDICT-1→P2(+P10 import half); PROV-1→P3; EMPTY-1→P4; LISTORDER-1→P5; FETCH-1→P6; ERROR-1→P7; VIEWONLY-1→P8; ADVISORY-1/COPY-1→P9; SCOPE-1/TESTID-1/NOTS-1→P10. **Load-bearing pair**: **P-OUTV-1** (field-derived state machine) + **P-OUTV-2** (namespace exclusion by prop signature).

## 3. Logical components (named; responsibilities + ownership + the exact prop shapes that enforce each guarantee)

| Component | Module (planned) | Responsibility / ownership | Prop shape (the by-construction surface) |
|---|---|---|---|
| **`OutlierView`** | `outlierView/OutlierView.jsx` | the **only** stateful component: fetches R4, owns the **four-state machine** (P-OUTV-1) + failure-routing, selects `OutlierStateView` vs the ready composition. Emits nothing upward. | `{ applicationId, fetchSeam }` — no outward mutating event |
| **`fetchSeam`** | `outlierView/fetchSeam.js` | own local thin R4 request seam; **injected**; mirrors the sibling read seams **without importing** them. | `createOutlierFetch(transport) → { fetchOutlier(applicationId) }`; `normalizeError(cause) → {error:{code,message,detail}}` |
| **`OutlierStateView`** | `outlierView/OutlierStateView.jsx` | presentational loading / **not-available** / error states (P-OUTV-4/7). | `{ state, error, onRetry, testid }` — `state ∈ {loading, not_available, error}` |
| **`OutlierScoreRegion`** | `outlierView/OutlierScoreRegion.jsx` | presentational score + is_outlier, advisory chrome. | `{ outlierScore, isOutlier, testid }` — **no `recommendation`/`confidence`/`provenance`/`seed`/`corpus_version` prop** (P-OUTV-2/3) |
| **`FlaggedFeaturesRegion`** | `outlierView/FlaggedFeaturesRegion.jsx` | presentational flag rows in delivered order (P-OUTV-5); empty → "no anomalies" branch (P-OUTV-4). | `{ flaggedFeatures, testid }` — **no `recommendation`/`confidence`/`provenance` prop** (P-OUTV-2/3) |
| **`StructuralGuard`** | `outlierView/__tests__/*` | test-only scan substrate (P-OUTV-9/10). | — |

> **Header-comment self-evidence (candidate — folded into Q1/Q2/Q3 option A)**: each region + the seam carry a header comment stating their by-construction restriction (the `ui-history` NFR-DESIGN-Fold-1 convention) — **documentation only, not enforcement**.

## 3.1 Reference-not-own check
- **Consumed, not modified** (frozen `ui-shell`): `AppFrame`/`Panel`/`Region`/`ReadOnlyRegion`; `shell/copy` (`ADVISORY_VOCABULARY` + the one `FORBIDDEN_TERMS`); `shell/session`; `shell/tokens`. **Not** `RecommendationBadge`/`ConfidenceBadge` (P-OUTV-2), **not** `RoleGate` (P-OUTV-8).
- **Not imported, reached only via R4 orchestration**: `outlier-model` (U18 — `(orchestrated)`, cross-language boundary); `ui-memo-view`/`ui-queue` (sibling views — mirror the fetchSeam/StructuralGuard convention, not the module). No backend module.
- **Edits nothing frozen**; the only cross-unit surface is the WIRE-1 R4 `outlier` shape, consumed by value.

## 3.2 Component → target coverage (no orphan)
| Component | Targets met | Patterns |
|---|---|---|
| `OutlierView` | STATE-1, FETCH-1, VIEWONLY-1 | P-OUTV-1/6/8 |
| `fetchSeam` | FETCH-1, ERROR-1(build/normalize) | P-OUTV-6/7 |
| `OutlierStateView` | ERROR-1, EMPTY-1(not-available branch) | P-OUTV-4/7 |
| `OutlierScoreRegion` | NOVERDICT-1, PROV-1 | P-OUTV-2/3 |
| `FlaggedFeaturesRegion` | NOVERDICT-1, PROV-1, EMPTY-1, LISTORDER-1 | P-OUTV-2/3/4/5 |
| `StructuralGuard` + `copy.js` | SCOPE-1, ADVISORY-1, COPY-1, TESTID-1, NOTS-1 (+ NOVERDICT-1 import half) | P-OUTV-9/10 |

## 3.3 Component-relationship Mermaid (Part-2 deliverable — the no-verdict guarantee as a VISIBLE structural property)
Part 2 will include a **validated** Mermaid (alphanumeric IDs; double-quoted labels; **no hyphens/semicolons/bare colons/parentheses/special characters**; balanced; **rectangle-only**) showing the render tree, with a **dashed `blocked` edge from a `Recommendation Confidence source` node into the render tree** (no real edge exists) — the `ui-history` visible-graph-property precedent — plus the text alternative.

## 4. Clarifying questions (`[Answer]` tags — LEFT BLANK; lettered; full text below)

> Fill these; I then run the ambiguity-check against the answers + the frozen FD + the thirteen `NFR-OUTV-*` + the `ui-memo-view`/`ui-history` NFR-Design precedent, then Part 2 (`nfr-design-patterns.md` + `logical-components.md`) **on your explicit go**. **No improvising on any ambiguity — flag and stop.**

### Q1 — `P-OUTV-1`: is the state machine's failure-routing a STRUCTURAL guarantee or test-only?
- **A.** **Structural (by construction).** `OutlierView`'s state-transition logic routes a fetch **failure → `ERROR`** on a branch evaluated **before** the `outlier`-null check is ever reached, so `NOT_AVAILABLE` is **unwritable** from a failure path (not merely tested-not-to). A header comment documents it; `NFR-OUTV-STATE-1`'s teeth are then the **regression layer** on a design-level guarantee. *(Recommended — matches this build's by-construction philosophy for load-bearing targets; the failure-before-null-check ordering is a real structural property, the analog of `ui-memo-view`'s status-discriminator being a single evaluated branch.)*
- **B.** **Test-only.** The four states are correct **because** `NFR-OUTV-STATE-1` asserts them; no structural ordering guarantee is claimed. *(Leaner, but the load-bearing state-derivation correctness rests only on the test, not the design.)*
- **C.** Other (describe).

`[Answer]:` A

### Q2 — `P-OUTV-2`: is `OutlierScoreRegion`/`FlaggedFeaturesRegion`'s exclusion of `recommendation`/`confidence` a STRUCTURAL prop-signature guarantee or test-only?
- **A.** **Structural (by construction, prop signature).** The two regions' prop shapes carry **no `recommendation`/`confidence` prop or path** (`{outlierScore,isOutlier,testid}` / `{flaggedFeatures,testid}`) — a verdict is **structurally unnameable** in this unit's render tree, mirroring `ui-history` `CommittedActionRegion` (no system-namespace path) + a header comment. `NFR-OUTV-NOVERDICT-1`'s import-absence scan + rendered `queryBy*`-null teeth are the **regression layer**. *(Recommended — the same by-construction philosophy as `ui-memo-view` SEPARATION-1 / `ui-history` namespace isolation; the load-bearing no-verdict guarantee earns a structural mechanism, not just teeth.)*
- **B.** **Test-only.** No verdict renders **because** `NFR-OUTV-NOVERDICT-1` asserts its absence; the prop shapes are a convention, not a guarantee. *(Leaner, but the load-bearing advisory guarantee rests only on the test.)*
- **C.** Other (describe).

`[Answer]:` A

### Q3 — `P-OUTV-3`: is the regions' exclusion of `provenance`/`seed`/`corpus_version` a STRUCTURAL prop-signature guarantee or test-only?
- **A.** **Structural (by construction, prop signature).** The rendering regions **never receive `provenance`/`seed`/`corpus_version` as props at all** — the `NFR-OUTV-PROV-1` negative guarantee is structural (a region cannot render what it never receives); any `outlier_model_version` footnote (single realization) is a distinct footnote slot, never `seed`/`corpus_version`. Header comment documents it; the sentinel-based negative teeth (Fold-D) are the **regression layer**. *(Recommended — makes the "seed/corpus_version never rendered" guarantee a design property, not just a rendering choice a future edit could quietly break.)*
- **B.** **Test-only.** `seed`/`corpus_version` are absent from the render **because** `NFR-OUTV-PROV-1` asserts it; the regions could technically receive provenance but choose not to render it. *(Leaner, but a future prop-passing edit could regress it silently between test runs.)*
- **C.** Other (describe).

`[Answer]:` A

---

## 5. HOLDS (binding through Part 2)
- **No NFR-Design artifact generated in Part 1**; `guide-docs/build/ui-outlier-view/nfr-design/` NOT created; no code; no `frontend/src/outlierView/`.
- **Re-opening none** of the frozen FD (BR-OUTV-1..10 + the folds) or the approved NFR Requirements (thirteen NFR-OUTV-* + Fold-A..D); **WIRE-1 consumed by shape, not touched**; **`outlier-model` (U18) reached only via R4, never imported**; **`ui-shell`/`ui-memo-view`/`ui-history` composed/mirrored, never edited**; **no sibling-view or backend import**.
- The **17 frozen P1 units + the closed composition root UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap** untouched; **no other unit started**; the 23-unit decomposition unchanged.

## 6. Gate
**Part 1 (Plan) WRITTEN — STOPPED at the plan-file gate.** The three `[Answer]` tags (Q1–Q3) are **BLANK**. On the filled answers: run the mandatory **ambiguity-check** against the answers + the frozen FD + the thirteen `NFR-OUTV-*` + the `ui-memo-view`/`ui-history` NFR-Design precedent — **surface-and-stop on any genuine gap, do not improvise** — then, **on the explicit go**, generate Part 2 (`nfr-design-patterns.md` [P-OUTV-1..10 + the validated Mermaid] + `logical-components.md` [the six components + exact prop shapes + reference-not-own + component→target coverage + the validated Mermaid]). **Depth: lighter.** NO NFR-Design artifact generated in Part 1. WIRE-1 · `outlier-model` (U18) · `ui-shell`/`ui-memo-view`/`ui-history` · the 17 frozen P1 units · the closed composition root UNTOUCHED; tier-B NOT authorized; the `audit_store` Docker-guard gap untouched; no other unit started; the 23-unit decomposition unchanged.
