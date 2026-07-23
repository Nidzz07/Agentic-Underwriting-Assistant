# NFR Requirements — `ui-override-form` (U8)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U8 `ui-override-form` · C-cluster UI · Phase 1 · **Depth**: **COMPREHENSIVE** (Q1-A — the second/final UI write path; the one unit that exercises the mandatory-reason gate) · **Date**: 2026-07-09
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md` — **BR-OVR-1..12**, the component/prop inventory incl. the **capability-free `OverrideReasonInput`**, the full client state machine **including reason preservation across cancel/error**, the **two-server-gate** (AUTHZ-1 + BR-COMMIT-GATE) defense-in-depth note) — **re-opening none of it**. Each `NFR-OVR-*` target is a **pass/fail testable assertion** traced to its FD rule.
**Tier convention inherited from `ui-shell` (frozen U10), applied by `ui-queue` (U5) + `ui-memo-view` (U6) + `ui-approval-gate` (U7)**: Vitest + React Testing Library + jsdom · ESLint over the **single** `FORBIDDEN_TERMS` source · file/import structural scans · detector self-tests (non-vacuous). **Advisory-only; no LLM; no live backend** (WIRE-1 R4 **and** R5 mocked via a **single injected/capturing dual-operation double**). **Q1–Q4 all A.**

---

## 0. Central testability principle — the dual-operation seam (reason-carrying)

`ui-override-form`'s properties are testable **without a running backend**. Like U7, its `overrideFetchSeam` has **two** operations: `fetchContext` (R4 read) **and** `submitOverride` (R5 write) — but `submitOverride(recommendationId, reason)` carries a **second argument** (the mandatory reason). The load-bearing targets are behavioral **teeth** that count transport calls **per operation** **and** inspect the recorded `reason`.

**NFR-OVR-Fold-A (dual-operation reason-carrying single-double; §0 / mirror of U7 NFR-AG-Fold-1)** — there is **one** injected double, exposing its two operations under the **exact seam names** `fetchContext` / `submitOverride`, **each an independently-counted spy** with its own call log recording **args** (so the `reason` passed to `submitOverride` is inspectable) — never a shared generic `calls` array. This **mirrors** (does not import) U7's dual-double fold, extended to capture the reason argument. **Non-vacuous cross-guard**: the CONFIRM-1 pre-`Confirm` checkpoint asserts **both** `submitOverride.calls.length === 0` **and** `fetchContext.calls.length === 1`; because the expected counts **differ (0 vs 1)**, a test that watched the wrong counter — or swapped the assertions — **fails**. NOREFETCH-1 asserts **both** counts frozen after success; BODY-1 / REASONGATE-1 read `submitOverride.calls[0]` to assert the recorded `{recommendationId, reason}`.

Four test modalities:
1. **Build-failing lints + structural scans** — COPY-1 / ADVISORY-1 / NAMESPACE-1 reuse ui-shell's ESLint + the **one** `FORBIDDEN_TERMS` source (never a second word-list); NOTS-1 / RBAC-1(structural) / REFNOTOWN-1 / CAPFREE-1 / NOFINAL-1(scan) are file/import/render scans; each detector carries a **self-test**.
2. **Component-render + interaction (RTL + jsdom)** — CONFIRM-1, CANCEL-1, REASONGATE-1, REASONKEEP-1, ERROR-1, RBAC-1(stub `RoleProvider`), CAPFREE-1(prop-contract), FETCH-1 per-state renders.
3. **Dual-operation capturing-double** — the transport-call-count teeth (CONFIRM-1, CANCEL-1, REASONGATE-1, NOREFETCH-1, RECOVERY-1) + BODY-1's recorded request body (incl. `reason`) + RECOVERY-1's recorded `applicationId`.
4. **Observed/soft** — PERF-1 (bounded R4 + single R5, non-gating) and A11Y-1 (semantic + focusable override/confirm/cancel/retry + the reason `<textarea>` label association, recorded target).

**Scope**: tests **only** `ui-override-form`'s own behavior — not other UI units, not any backend unit's internals, not the WIRE-1 route implementation (R5/R4 impl → Build & Test). **Reuses** ui-shell's frozen mechanisms (copy / `FORBIDDEN_TERMS` / ESLint / `RoleGate` / `ReadOnlyRegion` / badges / `COMMIT_ACTION_LABELS.override` / testid convention); **mirrors** the sibling fetchSeam/StructuralGuard/by-construction convention **without modifying or importing** any sibling (incl. frozen `ui-approval-gate`).

---

## 1. Finalized `NFR-OVR-*` targets (pass/fail; acceptance criteria; test tier; rigor)

### FULL RIGOR — the commit-lifecycle teeth (load-bearing)

#### NFR-OVR-NOFINAL-1 — no client finalize (BR-OVR-1)
- **Assertion**: no UI path finalizes an outcome; the **only** call site of `submitOverride` is the `OverrideConfirmDialog` `Confirm` handler; mount / R4 read / reason-typing / `confirming`-toggle issue no R5 POST.
- **Acceptance**: (a) **structural** — a source scan finds `submitOverride(` **invoked** from exactly one site (the confirm handler) and finds **no seam import** in the non-dialog components (the U7 invocation/import refinement — header comments naming `submitOverride` to document its absence do **not** trip it); (b) **teeth** (shared with CONFIRM-1) — across `mount → type reason → Override → open dialog`, `submitOverride.calls.length === 0`; (c) detector self-test (a synthetic second call-site is flagged).
- **Tier**: structural + component. **Rigor**: full.

#### NFR-OVR-CONFIRM-1 — confirm-before-commit teeth (BR-OVR-2) — **load-bearing**
- **Assertion**: clicking `Override` (with a non-blank reason) opens the confirm dialog and **does not commit**; the R5 POST fires **only** on the dialog's `Confirm`.
- **Acceptance** (dual-operation double, NFR-OVR-Fold-A): (a) after `Override`-click the state is `confirming` and **`submitOverride.calls.length === 0` AND `fetchContext.calls.length === 1`** (the cross-guard); (b) after `Confirm`, **`submitOverride.calls.length === 1`** exactly; (c) **teeth** — the test fails if any POST occurs before `Confirm`.
- **Tier**: component (teeth). **Rigor**: **full (highest)**.

#### NFR-OVR-CANCEL-1 — cancelable-without-side-effect teeth (BR-OVR-3)
- **Assertion**: opening or canceling the confirm dialog performs no fetch, no commit, and no state mutation beyond the local `confirming` flag; `Cancel` returns to `ready(idle)` with the reason **preserved**.
- **Acceptance**: with the dual-operation double — (a) across `type reason → Override → open → Cancel`, **both** `submitOverride.calls.length === 0` **and** `fetchContext.calls.length` unchanged from its post-mount value (`=== 1`); (b) the rendered recommendation context is **identical** (same testids/text) before open and after cancel; (c) state is `ready(idle)`; (d) **the reason input still holds the typed value** (cross-ref REASONKEEP-1).
- **Tier**: component (teeth). **Rigor**: **full (highest)**.

### FULL RIGOR — the mandatory-reason gate (load-bearing, the NEW U8 target)

#### NFR-OVR-REASONGATE-1 — mandatory non-blank reason teeth (BR-OVR-8) — **load-bearing**
- **Assertion**: an override requires a non-blank reason. While the reason is blank/whitespace-only the `Override → confirm → submit` path is disabled and **zero** `submitOverride` calls occur; with a non-blank reason, exactly **one** `submitOverride` call carrying that reason on `Confirm`. The UI guard is `String.prototype.trim()`-based and **non-authoritative** (the backend `_gate` is the single source of truth); it is **not** claimed byte-identical to Python `str.strip()`.
- **Acceptance** (Q3-A — the whitespace fixture set + the send-as-entered payload + the divergence-documentation test):
  - (a) **Blank set (zero POSTs each)** — for each of `""`, `" "` (space), `"\t"` (tab), `"\n"` (newline), `" \t\n "` (mixed): the Override→confirm→submit path stays disabled and `submitOverride.calls.length === 0` (no reachable path fires a POST).
  - (b) **Non-blank control (exactly one POST, payload as-entered)** — with `reason = " I disagree because X "` (surrounding spaces around content), `Confirm` yields `submitOverride.calls.length === 1` and the **recorded reason argument === `" I disagree because X "` verbatim** — the guard `trim()`s **only** for the enable/disable decision, **never** the sent value; the backend stores what it receives (verified — NFR-OVR-Fold-1).
  - (c) **Divergence-documentation test** — an explicit test/asserted note that the UI guard is `String.prototype.trim()`-based and **not** byte-identical to Python `str.strip()` (FD-OVR-Fold-1): a reason of only `""` or `""` would pass the UI `trim()` but the backend strips it to empty and returns **409** — the divergence is **acknowledged, resolved via the 409 tail (ERROR-1)**, and **not** silently assumed-equal. The exotic full-Unicode matrix is **out of scope** (option C rejected — over-build against the non-authoritative design).
- **Tier**: component (teeth) + unit (doc). **Rigor**: **full (highest)**.

### FULL RIGOR — authorization-adjacent + write-shape

#### NFR-OVR-RBAC-1 — RoleGate cosmetic-only (BR-OVR-4)
- **Assertion**: `RoleGate can="act"` cosmetically shows/hides the override affordance; it makes **no** authorization decision, imports **no** backend, calls **no** authz function. The real gate is AUTHZ-1 (server-side).
- **Acceptance**: (a) **structural** — `frontend/src/overrideForm/` imports no backend module and calls no authz function (StructuralGuard scan + detector self-test); (b) **RTL stub `RoleProvider`, all three roles + null (inherited U7 Q3-A)** — `underwriter` → the override affordance is **present**; `auditor` → **absent** (fallback); `admin` → **absent**; `null` (unauthenticated) → **absent**. Pins the frozen `COSMETIC_CAPABILITIES` `act:false` cells for **both** non-underwriter roles + the null case.
- **Tier**: structural + component. **Rigor**: full.

#### NFR-OVR-BODY-1 — session-derived committer; override body carries the reason (BR-OVR-5)
- **Assertion**: the R5 body carries **only** `{ action: "override", reason }`; `underwriter_id` is **never** client-sent; `recommendation_id` comes from the R4 context and goes in the path.
- **Acceptance**: unit test on `buildOverrideRequest(recommendationId, reason)` — (a) the body **deep-equals** `{ action: 'override', reason }` (assert `action` + `reason` keys present, **no** `underwriter_id` key); (b) `path` contains the R4-supplied `recommendation_id`; (c) method is `POST`; (d) the `reason` in the body is the exact value passed (as-entered, no trim).
- **Tier**: unit. **Rigor**: full.

#### NFR-OVR-ERROR-1 — per-status surfacing via the shared envelope (BR-OVR-6)
- **Assertion**: R5 outcomes surface **distinctly per documented status** through the **one** envelope shape with `message` VISIBLE, `code` in a `hidden` testid node, `detail` NEVER in the DOM.
- **Acceptance**: table-driven RTL, each status programmed on the double — (a) **200** → the committed-confirmation state; (b) **403** → not-permitted; (c) **409** → conflict — the **same** rendered state for **both** already-committed **and** the blank-reason race/bypass tail (one `commit_conflict` code, no special-casing beyond copy); (d) **400** and **422** → generic invalid; (e) for every non-2xx: `override-error-message` shows `message`, `override-error-code` carries `code` and is **not** visible text, and a DOM scan finds `detail`'s content **nowhere**.
- **Tier**: component (table-driven). **Rigor**: full.

#### NFR-OVR-NOREFETCH-1 — confirmation without re-fetch teeth (BR-OVR-9)
- **Assertion**: the committed-confirmation renders from the R5 `CommittedDecision` echo (incl. the committed `reason`) + the R4 context already in hand — with **no** separate re-fetch.
- **Acceptance**: RTL — after a successful override, (a) the confirmation shows `action=override` + the committed `reason` + `recommendation_id` + `underwriter_id` (from the echo) + the recommendation value (from R4 context); (b) **teeth** — **both** `fetchContext.calls.length` and `submitOverride.calls.length` are **unchanged** from their immediate post-commit values (`1` and `1`); no further transport call occurs; (c) **the displayed committed `reason` equals the sent (as-entered) reason** — precisely because the backend does not normalize (NFR-OVR-Fold-1, verified against `record_schema.py`/`commit_service.py`).
- **Tier**: component (teeth). **Rigor**: full.

#### NFR-OVR-REFNOTOWN-1 — reference-not-own / decoupled (BR-OVR-10)
- **Assertion**: no backend import; no `ui-queue` / `ui-memo-view` / **`ui-approval-gate`** import; own-local seam + copy.
- **Acceptance**: StructuralGuard scans (each non-vacuous, detector self-test) over `frontend/src/overrideForm/` — `noBackendImport`, `noUiQueueImport`, `noMemoViewImport`, **`noApprovalGateImport`** (NEW — the first sibling that must also not import frozen U7), `noRouterImport`; a synthetic offending import is flagged.
- **Tier**: structural. **Rigor**: full.

#### NFR-OVR-RECOVERY-1 — cause-differentiated recovery teeth (BR-OVR-11)
- **Assertion**: an R4 (context-read) failure's `Retry` re-issues the R4 read for the same `applicationId`; an R5 (override commit) failure returns to `ready(idle)` — never an automatic resubmit — with the reason preserved.
- **Acceptance** (dual-operation double): (a) **errorRead leg** — fail `fetchContext` for `applicationId = X`; activating `override-error-retry` issues **exactly one** further `fetchContext` whose recorded arg **=== X** (`fetchContext.calls.length === 2`, second arg X); (b) **errorCommit leg** — fail `submitOverride`; the state transitions to `ready(idle)` and **`submitOverride.calls.length` stays at `1`** (no automatic follow-up), **and the reason input still holds the typed value**; a fresh `Override → Confirm` cycle is required to reach `submitOverride.calls.length === 2`.
- **Tier**: component (teeth). **Rigor**: full.

#### NFR-OVR-REASONKEEP-1 — reason preservation + read-only echo (BR-OVR-12) — the NEW U8 target
- **Assertion**: the entered `reason` survives `Cancel` and `errorCommit` transitions unchanged; and the confirm dialog renders the current `reason` as a **read-only echo** before submission.
- **Acceptance** (Q4-A — two distinct assertions, may share one file):
  - (a) **Preservation teeth** — type a reason; (i) `Override → open → Cancel` → the reason input's value is **unchanged**; (ii) trigger an `errorCommit` → after returning to `ready(idle)` the reason input's value is **unchanged**.
  - (b) **Dedicated echo DOM assertion** — in the `confirming` state, a node `override-confirm-reason-echo` renders the current `reason` text and is **read-only** (not an editable `input`/`textarea`) — a **separate** assertion from (a) so a preservation regression and an echo-rendering regression fail **different** tests. This node is **distinct** from the post-submission `override-committed-reason` (NFR-OVR-NOREFETCH-1) — different state, node, and data source (client `reason` state pre-submission vs R5 echo post-submission; NFR-OVR-Fold-2).
- **Tier**: component. **Rigor**: full.

#### NFR-OVR-CAPFREE-1 — capability-free components (BR-OVR-3 / by-construction; Q2-A) — the NEW U8 target
- **Assertion**: the presentational components hold no commit capability. `OverrideAffordance` holds only `onOverride`; **`OverrideReasonInput` holds only `{ value, onChange }`** and imports no seam; `CommittedConfirmation` is `{ decision, context }`-only; the single `submitOverride` call site is `OverrideConfirmDialog`.
- **Acceptance** (Q2-A — structural import-scan + prop-contract RTL): (a) **structural** — a StructuralGuard scan asserts `OverrideReasonInput` and `OverrideAffordance` **import no seam module** (`createOverrideFetch` / `overrideFetchSeam`) and **reference no** `submitOverride` (reusing U7's invocation/import refinement, not a bare-word scan); each detector **non-vacuous** (a synthetic seam import is flagged); (b) **prop-contract RTL** — `OverrideReasonInput` renders from `{ value, onChange }` alone: it displays `value`, typing calls `onChange`, and it exposes no other capability. Together: the import scan proves the **structural absence** of a commit path; the RTL proves the **controlled-input contract** behaviorally.
- **Tier**: structural + component. **Rigor**: full.

#### NFR-OVR-FETCH-1 — dual-operation seam + full state machine (state-machine addendum)
- **Assertion**: R4/R5 flow through the **injected** double; every render state renders correctly; the transitions are covered.
- **Acceptance**: (a) the seam is received via **prop**, never hard-wired (no real `fetch`/`axios`/XHR in production source); (b) **per-state renders** — `loading`, `pending` (no affordance / no reason input), `ready(idle)` (context + reason input), `confirming` (reason echoed), `submitting`, `committed`, `errorRead`, `errorCommit`; (c) **ONE consolidated transition test (mirror of U7 Q5-A)** on the same dual-operation double covering `loading→ready`, `loading→pending`, `loading→errorRead`, `errorRead --Retry--> loading`, `ready→confirming` (zero POST), `confirming --Cancel--> ready` (zero POST, reason preserved), `confirming --Confirm--> submitting → committed`, `submitting → errorCommit`, `errorCommit --> ready` (reason preserved) — extended for the write path + split recovery + the reason-carrying states.
- **Tier**: component. **Rigor**: full.

### FULL RIGOR — inherited conventions

#### NFR-OVR-COPY-1 — no inlined display label (reused ui-shell COPY convention)
- **Assertion**: no Recommendation/Confidence/CommitAction label literal in `frontend/src/overrideForm/`; badges + `COMMIT_ACTION_LABELS.override` render by **value look-up** from `shell/copy`; chrome lives in the override-local copy module.
- **Acceptance**: (a) the ui-shell `no-inline-label` ESLint (build-failing) flags any label literal outside `shell/copy`; (b) the `RecommendationBadge`/`ConfidenceBadge` + the override label render sourced values; (c) detector self-test (a synthetic inlined label is flagged).
- **Tier**: lint. **Rigor**: full.

#### NFR-OVR-ADVISORY-1 — reuse the ONE advisory-vocabulary lint, UNMODIFIED (BR-OVR-1/7 naming facet)
- **Assertion**: the ui-shell `advisory-vocabulary` lint is registered on `src/overrideForm/**` (a config block mirroring the sibling — **no `src/shell` edit, no new word-list**); this unit's static copy contains **no** forbidden system-output token and never renders the human `override` as the system `DECLINE-RECOMMEND`.
- **Acceptance**: (a) the reused lint passes over `src/overrideForm/` static code; (b) **no** new word-list exists under `src/overrideForm/`; (c) `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS` (single source); (d) **detector self-test** — a synthetic forbidden token fails the lint. **Governance (§4 / NFR-OVR-Fold-3)**: all **21** `OVERRIDE_COPY` strings were audited **now** against the real `FORBIDDEN_TERMS.systemOutput` detector — **zero** trip (unlike U7, no copy correction was needed); the lint applies **unmodified**.
- **Tier**: lint. **Rigor**: full.

#### NFR-OVR-TESTID-1 — `data-testid` convention (reused convention)
- **Assertion**: every assertion-relevant element carries a stable `override-<element>-<purpose>` `data-testid`.
- **Acceptance**: (a) an `override-testid-convention` lint/test (mirroring the sibling) asserts the convention across override-form elements; (b) the state + error + affordance + reason testids are present (`override-state-*`, `override-error-message`/`-code`/`-retry`, `override-affordance-override`, `override-reason-input`, `override-confirm-*`, `override-confirm-reason-echo`, `override-committed-*`, `override-committed-reason`); (c) detector self-test (a misnamed testid is flagged).
- **Tier**: lint / component. **Rigor**: full.

#### NFR-OVR-NOTS-1 — no TypeScript (FR-UI-5)
- **Assertion**: `frontend/src/overrideForm/` is plain JS/JSX.
- **Acceptance**: a file-scan finds **zero** `.ts`/`.tsx` under the tree and no `tsconfig*.json`; CI fails otherwise.
- **Tier**: structural. **Rigor**: full.

### MEDIUM RIGOR

#### NFR-OVR-NAMESPACE-1 — human `override` never the system `DECLINE-RECOMMEND` (BR-OVR-7)
- **Assertion**: the human `override` (lowercase `CommitAction`) is never rendered as / serialized as / conflated with the system `DECLINE-RECOMMEND` (uppercase `Recommendation`).
- **Acceptance**: (a) **structural** — the committed body/action value is the literal `"override"`; the override **label** comes from `COMMIT_ACTION_LABELS.override` (not a `RECOMMENDATION_LABELS` value); (b) reuses the `FORBIDDEN_TERMS` collision guard so a bare `DECLINE` or a system value emitted as the human action is flagged; (c) `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS`; (d) detector self-test.
- **Tier**: structural. **Rigor**: medium.

### SOFT / OBSERVED

#### NFR-OVR-PERF-1 — bounded fetch; observed, non-gating
- **Assertion**: R4 fetches one resource by `applicationId`; R5 posts one override; no list/all-rows path.
- **Acceptance**: (a) **structural** — `buildMemoRequest`/`buildOverrideRequest` target exactly one resource each (no list path, no query string); no production module issues a real `fetch`/`axios`/XHR (seam injected) — the sibling `boundedFetch` scan; (b) latency/bundle observed, **no SLO gate** in Phase 1.
- **Tier**: structural (bounding) + observed. **Rigor**: soft.

#### NFR-OVR-A11Y-1 — semantic + focusable controls + labeled reason input; recorded target, non-gating
- **Assertion**: the unit uses semantic markup; `Override`/`Confirm`/`Cancel`/`Retry` are keyboard-focusable controls; the reason `<textarea>` has an associated label.
- **Acceptance**: recorded as a target; the confirm-dialog **focus-trap** / **Escape-to-cancel** and the reason input's label association are **recorded NFR-Design targets**, **not** Phase-1 gates. **Note**: the **BR-OVR-3 "cancelable" invariant (NFR-OVR-CANCEL-1)** and the **BR-OVR-8 "blank blocks submit" invariant (NFR-OVR-REASONGATE-1)** remain gated as full-rigor behavioral teeth — only the a11y **polish** stays soft.
- **Tier**: observed / soft. **Rigor**: soft.

### GOVERNANCE

#### NFR-OVR-SCOPE-1 — scoped exclusions *(not a runtime test)*
- **Statement**: the set tests **only** `ui-override-form`'s own behavior — not other UI units, backend internals, or the WIRE-1 **route implementation** (`backend/app/main.py` → Build & Test). It **reuses** ui-shell's frozen copy/`FORBIDDEN_TERMS`/ESLint/`RoleGate`/`ReadOnlyRegion`/badges/testid mechanisms and **mirrors** the sibling fetchSeam/StructuralGuard/by-construction convention **without modifying or importing** any sibling (incl. frozen `ui-approval-gate`); WIRE-1 R4/R5 consumed **by shape**, mocked via the injected double. Enforced by review.
- **Tier**: N/A (governance).

---

## 2. Traceability (target → FD rule → tier → rigor) — no orphan

| Target | FD rule | Tier | Rigor |
|---|---|---|---|
| NFR-OVR-NOFINAL-1 | BR-OVR-1 | structural + component | full |
| NFR-OVR-CONFIRM-1 | BR-OVR-2 | component (teeth) | **full (highest)** |
| NFR-OVR-CANCEL-1 | BR-OVR-3 | component (teeth) | **full (highest)** |
| NFR-OVR-REASONGATE-1 | BR-OVR-8 | component (teeth) + unit | **full (highest)** |
| NFR-OVR-RBAC-1 | BR-OVR-4 | structural + component | full |
| NFR-OVR-BODY-1 | BR-OVR-5 | unit | full |
| NFR-OVR-ERROR-1 | BR-OVR-6 | component (table-driven) | full |
| NFR-OVR-NAMESPACE-1 | BR-OVR-7 | structural | medium |
| NFR-OVR-NOREFETCH-1 | BR-OVR-9 | component (teeth) | full |
| NFR-OVR-REFNOTOWN-1 | BR-OVR-10 | structural | full |
| NFR-OVR-RECOVERY-1 | BR-OVR-11 | component (teeth) | full |
| NFR-OVR-REASONKEEP-1 | BR-OVR-12 | component | full |
| NFR-OVR-CAPFREE-1 | BR-OVR-3 / Q3-A by-construction | structural + component | full |
| NFR-OVR-FETCH-1 | state-machine addendum | component | full |
| NFR-OVR-COPY-1 | reused COPY convention | lint | full |
| NFR-OVR-ADVISORY-1 | BR-OVR-1/7 (naming facet) | lint | full |
| NFR-OVR-TESTID-1 | reused testid convention | lint / component | full |
| NFR-OVR-NOTS-1 | FR-UI-5 | structural | full |
| NFR-OVR-PERF-1 | view-perf precedent | structural + observed | soft |
| NFR-OVR-A11Y-1 | FR-UI (view) | observed | soft |
| NFR-OVR-SCOPE-1 | — | N/A | governance |

**No orphaned FD rule**: BR-OVR-1→NOFINAL-1 (+ADVISORY-1 naming facet), 2→CONFIRM-1, 3→CANCEL-1 (+CAPFREE-1), 4→RBAC-1, 5→BODY-1, 6→ERROR-1, 7→NAMESPACE-1, 8→REASONGATE-1, 9→NOREFETCH-1, 10→REFNOTOWN-1, 11→RECOVERY-1, 12→REASONKEEP-1. COPY/TESTID/NOTS/FETCH/PERF/A11Y cover inherited + addendum concerns; CAPFREE-1 carries the by-construction guarantees.

**Folds crystallized**: NFR-OVR-Fold-A (dual-operation reason-carrying single-double + cross-guard) · **NFR-OVR-Fold-1** (Q3-A "send as-entered" ↔ committed echo consistency — VERIFIED: backend `CommittedDecision.reason` is un-normalized) · **NFR-OVR-Fold-2** (REASONKEEP-1 confirm echo vs NOREFETCH-1 committed display are distinct states/nodes/sources) · **NFR-OVR-Fold-3** (all 21 `OVERRIDE_COPY` strings verified clean against the real detector NOW — no copy change, lint unmodified).

---

## 3. Security-Guardrails extension — compliance (enabled extension)

Second UI unit with a real **authorization-adjacent write surface**, and the **first** carrying the mandatory-reason gate. RBAC/authz **and** the reason-gate rows carry **real content**.

| Control | Status | Rationale |
|---|---|---|
| **Least-privilege UI framing (RBAC-affordance)** | **Compliant** | The override affordance is wrapped in `RoleGate can="act"` — cosmetically visible **only** to the `underwriter` cosmetic role (`act:true`); `auditor`/`admin`/`null` see the fallback (NFR-OVR-RBAC-1, all-roles+null). Mirrors the frozen `auth_rbac` semantics as **value shapes**, never imported. |
| **Authorization server-authoritative (defense-in-depth)** | **Compliant** | `RoleGate` makes **no** authz decision (NFR-OVR-RBAC-1 structural — no backend import, no authz call). The real gate is AUTHZ-1: `DecisionCommitService` re-checks `authorize(underwriter_id, RBAC_COMMIT)` and raises `UnauthorizedCommit` (→ 403) even if the cosmetic guard were bypassed; the client renders 403 as a **genuine error** (NFR-OVR-ERROR-1), never a silent success. |
| **Mandatory-reason gate server-authoritative (defense-in-depth)** | **Compliant** | The UI non-blank reason guard (NFR-OVR-REASONGATE-1) is **cosmetic/UX only** — `trim()`-based and **non-authoritative**. The real boundary is the backend `_gate` (`BR-COMMIT-GATE`: `reason.strip()==""` → `CommitRejected` → 409). A blank-reason override that slips past the UI (race / bypass / trim-divergence) is **rejected server-side** and surfaced generically (NFR-OVR-ERROR-1's 409). **CON-BR4 stays single-sourced in `audit-store`**. |
| **No client-side authorization datum** | **Compliant** | `underwriter_id` is **never** client-sent (NFR-OVR-BODY-1 — body deep-equals `{action:'override', reason}`, no `underwriter_id`); it is session-derived server-side, so a client cannot commit *as another user* or self-elevate. |
| **Human-in-the-loop enforcement** | **Compliant** | No auto-commit path (NFR-OVR-NOFINAL-1); an explicit confirm step gates every commit (NFR-OVR-CONFIRM-1); a **mandatory reason** is required (NFR-OVR-REASONGATE-1); the dialog is cancelable with zero side effects and echoes the reason for review (NFR-OVR-CANCEL-1 / NFR-OVR-REASONKEEP-1); a commit failure never auto-retries and preserves the reason (NFR-OVR-RECOVERY-1). |
| **Error / output hygiene (no leakage)** | **Compliant** | Failures surface via the shared envelope: `message` visible, `code` in a hidden testid node, `detail` **never** rendered (NFR-OVR-ERROR-1), aligned with WIRE-1 §4. The reason is user-authored free text; it is sent and echoed, no secret/PII handling beyond what the underwriter enters. |
| **Advisory-only naming** | **Compliant** | The system output is a **recommendation**, never a *decision* (NFR-OVR-ADVISORY-1 — all 21 copy strings verified clean); the human `override` is never rendered as the system `DECLINE-RECOMMEND` (NFR-OVR-NAMESPACE-1). |
| **Input validation (untrusted parsing)** | **N/A (reason validated server-side)** | Parses no untrusted document/file; the underwriter's `reason` is free text with **only** a non-blank UX check — all authoritative validation is the backend's. Reads a typed WIRE-1 JSON body and posts a fixed action + reason. |
| **Prompt-injection / LLM safety** | **N/A** | No LLM anywhere in this unit; the reason text never enters an LLM path. |
| **Secrets management** | **N/A** | Holds/sends no secret value; session/auth-handshake material is the composition root's concern (WIRE-1 deferred seam), `secrets-config`'s SEC-3. |
| **Audit-trail persistence** | **N/A (delegated)** | Persists nothing. The full audit tuple + the committed `reason` are written server-side by audit-store's `DecisionCommitService` on the override this action triggers — not this unit's responsibility. |

**No blocking finding.**

---

## 4. Governance note — advisory-vocabulary + the reason-gate single-sourcing (both verified, not assumed)

- **Advisory vocabulary (NFR-OVR-Fold-3)** — the single `FORBIDDEN_TERMS.systemOutput = ['DECLINE','decision','approved','declined']` forbids the bare token `decision`; the reserved-word rule permits it for the **human's committed action**. This unit honors the constraint **semantically**: the system recommendation is never called a *decision*; the human action is framed via **"override" / "reason" / "record" / "committed"**. Unlike U7 (whose `confirmBody` had to be corrected), **all 21 `OVERRIDE_COPY` strings were audited against the real detector and trip zero** — so the `advisory-vocabulary` lint applies **UNMODIFIED** (no carve-out, no second word-list, no split `FORBIDDEN_TERMS`).
- **Reason-gate single-sourcing (NFR-OVR-Fold-1)** — the UI non-blank guard is a **non-authoritative** UX layer; the backend `_gate` (`reason.strip()==""`) is the **single source of truth** (CON-BR4 in `audit-store`). Verified against `record_schema.py` + `commit_service.py`: `CommittedDecision.reason` is un-normalized (plain `Optional[str]`, no validator; `_gate` does not mutate; `_assemble` passes it verbatim) — so the client's "send as-entered" and the committed echo are consistent, and any UI↔backend `trim()`/`strip()` divergence resolves to the backend via the 409 tail (NFR-OVR-REASONGATE-1(c) + NFR-OVR-ERROR-1).

---

## 5. Settled items held (not re-opened)
- The **frozen FD** (BR-OVR-1..12 + inventory + state machine incl. reason preservation + two-server-gate note) is the substrate — NFR builds testable targets **on** it (no FD re-open; the `OVERRIDE_COPY` audit confirmed the copy clean as-drafted, no correction needed).
- **ui-shell (frozen)** — its Vitest/RTL/ESLint/`FORBIDDEN_TERMS`/`RoleGate`/`ReadOnlyRegion`/badges/`COMMIT_ACTION_LABELS.override`/testid mechanisms are **reused**, not modified; `RoleContext` stub (all-roles+null) is RBAC-1's injection point.
- **ui-queue / ui-memo-view / ui-approval-gate (frozen)** — their fetchSeam/StructuralGuard/by-construction/testid-lint conventions are **mirrored**, **not imported** (REFNOTOWN-1 enforces the non-import, incl. the NEW `noApprovalGateImport`).
- **WIRE-1** — R4 + R5 + `MemoView` + `CommittedDecision` + envelopes consumed **by shape**, mocked via the single injected double; the **route implementation** stays deferred to Build & Test (SCOPE-1).
- **Deferred values**: aesthetic token values, confirm-dialog a11y polish (focus-trap / Escape) + reason-input label association (recorded for NFR-Design), state-holding mechanics (hook/store), bundler/deploy topology → NFR-Design / Code-Gen / `deploy-config` (P2). Infrastructure Design for `ui-override-form` not pre-committed (likely a logged SKIP — source-level view; Vercel topology is `deploy-config` P2) — confirmed at that stage.
