# NFR Requirements — `ui-approval-gate` (U7)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U7 `ui-approval-gate` · C-cluster UI · Phase 1 · **Depth**: **COMPREHENSIVE** (Q1-A — first UI write path, first real `RoleGate` composition, first interactive `CommitAction` namespace) · **Date**: 2026-07-09
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md` — **BR-AG-1..11**, the component/prop inventory, the full client state machine **including the split `ErrorRead`/`ErrorCommit` recovery paths**, the AUTHZ-1 defense-in-depth structural note) — **re-opening none of it**. Each `NFR-AG-*` target is a **pass/fail testable assertion** traced to its FD rule.
**Tier convention inherited from `ui-shell` (frozen U10), applied by `ui-queue` (U5) + `ui-memo-view` (U6)**: Vitest + React Testing Library + jsdom · ESLint over the **single** `FORBIDDEN_TERMS` source · file/import structural scans · detector self-tests (non-vacuous). **Advisory-only; no LLM; no live backend** (WIRE-1 R4 **and** R5 mocked via a **single injected/capturing double**). **Q1–Q6 all A.**

---

## 0. Central testability principle — the dual-operation seam

`ui-approval-gate`'s properties are testable **without a running backend**. Unlike ui-queue/ui-memo-view (each a **single**-operation read seam), this unit's `commitFetchSeam` has **two** operations: `fetchContext` (R4 read) **and** `submitApprove` (R5 write). The load-bearing targets are behavioral **teeth** that count transport calls **per operation**.

**NFR-AG-Fold-1 (dual-operation single-double; Q2-A)** — there is **one** injected double, exposing its two operations under the **exact seam names** `fetchContext` / `submitApprove`, **each an independently-counted spy** with its own call log (never a shared generic `calls` array). This **extends** ui-memo-view's single-double fold to a dual-operation seam — one double, two counted operations, no divergent patterns. **Non-vacuous cross-guard**: the CONFIRM-1 pre-`Confirm` checkpoint asserts **both** `submitApprove.calls.length === 0` **and** `fetchContext.calls.length === 1`; because the expected counts **differ (0 vs 1)**, a test that watched the wrong counter — or swapped the assertions — **fails**. NOREFETCH-1 asserts **both** counts frozen after success.

Four test modalities:
1. **Build-failing lints + structural scans** — COPY-1 / ADVISORY-1 / NAMESPACE-1 reuse ui-shell's ESLint + the **one** `FORBIDDEN_TERMS` source (never a second word-list); NOTS-1 / RBAC-1(structural) / REFNOTOWN-1 / SCOPE-APPROVE-1(structural) are file/import/render scans; each detector carries a **self-test**.
2. **Component-render + interaction (RTL + jsdom)** — CONFIRM-1, CANCEL-1, ERROR-1, RBAC-1(stub `RoleProvider`), SCOPE-APPROVE-1, FETCH-1 per-state renders.
3. **Dual-operation capturing-double** — the transport-call-count teeth (CONFIRM-1, CANCEL-1, NOREFETCH-1, RECOVERY-1) + BODY-1's recorded request body + RECOVERY-1's recorded `applicationId`.
4. **Observed/soft** — PERF-1 (bounded R4 + single R5, non-gating) and A11Y-1 (semantic + focusable confirm/cancel, recorded target).

**Scope**: tests **only** `ui-approval-gate`'s own behavior — not other UI units, not any backend unit's internals, not the WIRE-1 route implementation (R5/R4 impl → Build & Test). **Reuses** ui-shell's frozen mechanisms (copy / `FORBIDDEN_TERMS` / ESLint / `RoleGate` / `ReadOnlyRegion` / badges / testid convention); **mirrors** the sibling fetchSeam/StructuralGuard convention **without modifying or importing** either.

---

## 1. Finalized `NFR-AG-*` targets (pass/fail; acceptance criteria; test tier; rigor)

### FULL RIGOR — the commit-lifecycle teeth (load-bearing)

#### NFR-AG-NOFINAL-1 — no client finalize (BR-AG-1)
- **Assertion**: no UI path finalizes an outcome; the **only** call site of `submitApprove` is the `CommitConfirmDialog` `Confirm` handler; mount / R4 read / `confirming`-toggle issue no R5 POST.
- **Acceptance**: (a) **structural** — a source scan finds `submitApprove(` invoked from exactly one site (the confirm handler); (b) **teeth** (shared with CONFIRM-1) — across `mount → Approve → open dialog`, `submitApprove.calls.length === 0`; (c) detector self-test (a synthetic second call-site is flagged).
- **Tier**: structural + component. **Rigor**: full.

#### NFR-AG-CONFIRM-1 — confirm-before-commit teeth (BR-AG-2) — **load-bearing**
- **Assertion**: clicking `Approve` opens the confirm dialog and **does not commit**; the R5 POST fires **only** on the dialog's `Confirm`.
- **Acceptance** (dual-operation double, NFR-AG-Fold-1): (a) after `Approve`-click the state is `confirming` and **`submitApprove.calls.length === 0` AND `fetchContext.calls.length === 1`** (the cross-guard); (b) after `Confirm`, **`submitApprove.calls.length === 1`** exactly; (c) **teeth** — the test fails if any POST occurs before `Confirm`.
- **Tier**: component (teeth). **Rigor**: **full (highest)**.

#### NFR-AG-CANCEL-1 — cancelable-without-side-effect teeth (BR-AG-3)
- **Assertion**: opening or canceling the confirm dialog performs no fetch, no commit, and no state mutation beyond the local `confirming` flag; `Cancel` returns to `ready(idle)` unchanged.
- **Acceptance**: with the dual-operation double — (a) across `Approve → open → Cancel`, **both** `submitApprove.calls.length === 0` **and** `fetchContext.calls.length` is unchanged from its post-mount value (`=== 1`); (b) the rendered recommendation context is **identical** (same testids/text) before open and after cancel; (c) state is `ready(idle)`.
- **Tier**: component (teeth). **Rigor**: **full (highest)**.

### FULL RIGOR — authorization-adjacent + write-shape

#### NFR-AG-RBAC-1 — RoleGate cosmetic-only (BR-AG-4)
- **Assertion**: `RoleGate can="act"` cosmetically shows/hides the approve affordance; it makes **no** authorization decision, imports **no** backend, calls **no** authz function. The real gate is AUTHZ-1 (server-side).
- **Acceptance**: (a) **structural** — `frontend/src/approvalGate/` imports no backend module and calls no authz function (StructuralGuard scan + detector self-test); (b) **RTL stub `RoleProvider`, all three roles + null (Q3-A / NFR-AG-Fold-3)** — `underwriter` → the approve affordance is **present**; `auditor` → **absent** (fallback); `admin` → **absent**; `null` (unauthenticated) → **absent**. Pins the frozen `COSMETIC_CAPABILITIES` `act:false` cells for **both** non-underwriter roles + the null case.
- **Tier**: structural + component. **Rigor**: full.

#### NFR-AG-BODY-1 — session-derived committer; approve-only body (BR-AG-5)
- **Assertion**: the R5 body carries **only** `{ action: "approve" }`; `underwriter_id` is **never** client-sent; `recommendation_id` comes from the R4 context and goes in the path.
- **Acceptance**: unit test on `buildCommitRequest(recommendationId)` — (a) the body **deep-equals** `{ action: 'approve' }` (assert **no** `underwriter_id` key **and no** `reason` key); (b) `path` contains the R4-supplied `recommendation_id`; (c) method is `POST`.
- **Tier**: unit. **Rigor**: full.

#### NFR-AG-ERROR-1 — per-status surfacing via the shared envelope (BR-AG-6)
- **Assertion**: R5 outcomes surface **distinctly per documented status** through the **one** envelope shape with `message` VISIBLE, `code` in a `hidden` testid node, `detail` NEVER in the DOM.
- **Acceptance**: table-driven RTL, each status programmed on the double — (a) **200** → the committed-confirmation state; (b) **403** → not-permitted; (c) **409** → already-committed/conflict; (d) **400** and **422** → generic invalid (both render the same generic state); (e) for every non-2xx: `approval-error-message` shows `message`, `approval-error-code` carries `code` and is **not** visible text, and a DOM scan finds `detail`'s content **nowhere**.
- **Tier**: component (table-driven). **Rigor**: full.

#### NFR-AG-SCOPE-APPROVE-1 — approve-only scope (BR-AG-8)
- **Assertion**: this unit renders **only** the `approve` affordance — no override control, no reason input, no reason field in the request.
- **Acceptance**: (a) **structural / RTL** — no override control and no reason `input`/`textarea` in the tree; (b) `buildCommitRequest` emits no `reason` key (shared with BODY-1); (c) the sole commit affordance is approve.
- **Tier**: structural + component. **Rigor**: full.

#### NFR-AG-NOREFETCH-1 — confirmation without re-fetch teeth (BR-AG-9)
- **Assertion**: the committed-confirmation renders from the R5 `CommittedDecision` echo + the R4 context already in hand — with **no** separate re-fetch.
- **Acceptance**: RTL — after a successful commit, (a) the confirmation shows `action=approve` + `recommendation_id` + `underwriter_id` (from the echo) + the recommendation value (from R4 context); (b) **teeth** — **both** `fetchContext.calls.length` and `submitApprove.calls.length` are **unchanged** from their immediate post-commit values (`1` and `1`); no further transport call occurs.
- **Tier**: component (teeth). **Rigor**: full.

#### NFR-AG-REFNOTOWN-1 — reference-not-own / decoupled (BR-AG-10)
- **Assertion**: no backend import; no `ui-queue` / `ui-memo-view` import; own-local seam + copy.
- **Acceptance**: StructuralGuard scans (each non-vacuous, detector self-test) over `frontend/src/approvalGate/` — `noBackendImport`, `noUiQueueImport`, `noMemoViewImport`, `noRouterImport`; a synthetic offending import is flagged.
- **Tier**: structural. **Rigor**: full.

#### NFR-AG-RECOVERY-1 — cause-differentiated recovery teeth (BR-AG-11)
- **Assertion**: an R4 (context-read) failure's `Retry` re-issues the R4 read for the same `applicationId`; an R5 (commit) failure returns to `ready(idle)` — never an automatic resubmit.
- **Acceptance** (dual-operation double): (a) **ErrorRead leg** — fail `fetchContext` for `applicationId = X`; activating `approval-error-retry` issues **exactly one** further `fetchContext` whose recorded arg **=== X** (`fetchContext.calls.length === 2`, second arg X); (b) **ErrorCommit leg** — fail `submitApprove`; the state transitions to `ready(idle)` and **`submitApprove.calls.length` stays at `1`** (no automatic follow-up); a fresh `Approve → Confirm` cycle is required to reach `submitApprove.calls.length === 2`.
- **Tier**: component (teeth). **Rigor**: full.

#### NFR-AG-FETCH-1 — dual-operation seam + full state machine (state-machine addendum)
- **Assertion**: R4/R5 flow through the **injected** double; every render state renders correctly; the transitions are covered.
- **Acceptance**: (a) the seam is received via **prop**, never hard-wired (no real `fetch`/`axios`/XHR in production source); (b) **per-state renders** — `loading`, `pending` (no affordance), `ready(idle)`, `confirming`, `submitting`, `committed`, `ErrorRead`, `ErrorCommit`; (c) **ONE consolidated transition test (Q5-A / NFR-AG-Fold-4)** on the same dual-operation double covering `loading→ready`, `loading→pending`, `loading→ErrorRead`, `ErrorRead --Retry--> loading`, `ready→confirming` (zero POST), `confirming --Cancel--> ready` (zero POST), `confirming --Confirm--> submitting → committed`, `submitting → ErrorCommit`, `ErrorCommit --> ready` — mirroring ui-memo-view's consolidated transition test, extended for the write path + split recovery.
- **Tier**: component. **Rigor**: full.

### FULL RIGOR — inherited conventions

#### NFR-AG-COPY-1 — no inlined display label (reused ui-shell COPY convention)
- **Assertion**: no Recommendation/Confidence label literal in `frontend/src/approvalGate/`; badges render by **value look-up** from `shell/copy`; chrome lives in the approval-local copy module.
- **Acceptance**: (a) the ui-shell `no-inline-label` ESLint (build-failing) flags any label literal outside `shell/copy`; (b) the `RecommendationBadge`/`ConfidenceBadge` render sourced labels; (c) detector self-test (a synthetic inlined label is flagged).
- **Tier**: lint. **Rigor**: full.

#### NFR-AG-ADVISORY-1 — reuse the ONE advisory-vocabulary lint, UNMODIFIED (BR-AG-1 naming facet; Q4-A)
- **Assertion**: the ui-shell `advisory-vocabulary` lint is registered on `src/approvalGate/**` (a config block mirroring the sibling — **no `src/shell` edit, no new word-list**); this unit's static copy contains **no** forbidden system-output token.
- **Acceptance**: (a) the reused lint passes over `src/approvalGate/` static code; (b) **no** new word-list exists under `src/approvalGate/`; (c) `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS` (single source); (d) **detector self-test** — a synthetic forbidden token fails the lint. **Governance (§4 / NFR-AG-Fold-2)**: the reserved-word constraint is honored **semantically** — all 14 `APPROVAL_COPY` strings are advisory-clean (the one offending draft string `confirmBody` was corrected at the FD source), so the lint applies **unmodified**.
- **Tier**: lint. **Rigor**: full.

#### NFR-AG-TESTID-1 — `data-testid` convention (reused convention)
- **Assertion**: every assertion-relevant element carries a stable `approval-<element>-<purpose>` `data-testid`.
- **Acceptance**: (a) an `approval-testid-convention` lint/test (mirroring the sibling) asserts the convention across approval-gate elements; (b) the state + error + affordance testids are present (`approval-state-*`, `approval-error-message`/`-code`/`-retry`, `approval-affordance-approve`, `approval-confirm-*`, `approval-committed-*`); (c) detector self-test (a misnamed testid is flagged).
- **Tier**: lint / component. **Rigor**: full.

#### NFR-AG-NOTS-1 — no TypeScript (FR-UI-5)
- **Assertion**: `frontend/src/approvalGate/` is plain JS/JSX.
- **Acceptance**: a file-scan finds **zero** `.ts`/`.tsx` under the tree and no `tsconfig*.json`; CI fails otherwise.
- **Tier**: structural. **Rigor**: full.

### MEDIUM RIGOR

#### NFR-AG-NAMESPACE-1 — human `approve` never the system `APPROVE` (BR-AG-7)
- **Assertion**: the human `approve` (lowercase `CommitAction`) is never rendered as / serialized as the system `APPROVE` (uppercase `Recommendation`); `override` is not present (deferred) and never equals `DECLINE-RECOMMEND`.
- **Acceptance**: (a) **structural** — the committed body/action value is the literal `"approve"`; the approve **label** comes from `COMMIT_ACTION_LABELS.approve` (not a `RECOMMENDATION_LABELS` value); (b) reuses the `FORBIDDEN_TERMS` collision guard so a bare `DECLINE` or a system value emitted as the human action is flagged; (c) `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS`; (d) detector self-test.
- **Tier**: structural. **Rigor**: medium.

### SOFT / OBSERVED (Q6-A)

#### NFR-AG-PERF-1 — bounded fetch; observed, non-gating
- **Assertion**: R4 fetches one resource by `applicationId`; R5 posts one commit; no list/all-rows path.
- **Acceptance**: (a) **structural** — `buildMemoRequest`/`buildCommitRequest` target exactly one resource each (no list path, no query string); no production module issues a real `fetch`/`axios`/XHR (seam injected) — the sibling `boundedFetch` scan; (b) latency/bundle observed, **no SLO gate** in Phase 1.
- **Tier**: structural (bounding) + observed. **Rigor**: soft.

#### NFR-AG-A11Y-1 — semantic + focusable controls; recorded target, non-gating
- **Assertion**: the unit uses semantic markup, and `Approve`/`Confirm`/`Cancel`/`Retry` are keyboard-focusable controls.
- **Acceptance** (Q6-A): recorded as a target; the confirm-dialog **focus-trap** and **Escape-to-cancel** are **recorded NFR-Design targets**, **not** Phase-1 gates. **Note**: the **BR-AG-3 "cancelable" invariant is still gated** as full-rigor behavioral teeth via the `Cancel` control (**NFR-AG-CANCEL-1**) — only the a11y **polish** stays soft.
- **Tier**: observed / soft. **Rigor**: soft.

### GOVERNANCE

#### NFR-AG-SCOPE-1 — scoped exclusions *(not a runtime test)*
- **Statement**: the set tests **only** `ui-approval-gate`'s own behavior — not other UI units, backend internals, or the WIRE-1 **route implementation** (`backend/app/main.py` → Build & Test). It **reuses** ui-shell's frozen copy/`FORBIDDEN_TERMS`/ESLint/`RoleGate`/`ReadOnlyRegion`/badges/testid mechanisms and **mirrors** the sibling fetchSeam/StructuralGuard convention **without modifying or importing** either; WIRE-1 R4/R5 consumed **by shape**, mocked via the injected double. Enforced by review.
- **Tier**: N/A (governance).

---

## 2. Traceability (target → FD rule → tier → rigor) — no orphan

| Target | FD rule | Tier | Rigor |
|---|---|---|---|
| NFR-AG-NOFINAL-1 | BR-AG-1 | structural + component | full |
| NFR-AG-CONFIRM-1 | BR-AG-2 | component (teeth) | **full (highest)** |
| NFR-AG-CANCEL-1 | BR-AG-3 | component (teeth) | **full (highest)** |
| NFR-AG-RBAC-1 | BR-AG-4 | structural + component | full |
| NFR-AG-BODY-1 | BR-AG-5 | unit | full |
| NFR-AG-ERROR-1 | BR-AG-6 | component (table-driven) | full |
| NFR-AG-NAMESPACE-1 | BR-AG-7 | structural | medium |
| NFR-AG-SCOPE-APPROVE-1 | BR-AG-8 | structural + component | full |
| NFR-AG-NOREFETCH-1 | BR-AG-9 | component (teeth) | full |
| NFR-AG-REFNOTOWN-1 | BR-AG-10 | structural | full |
| NFR-AG-RECOVERY-1 | BR-AG-11 | component (teeth) | full |
| NFR-AG-FETCH-1 | state-machine addendum | component | full |
| NFR-AG-COPY-1 | reused COPY convention | lint | full |
| NFR-AG-ADVISORY-1 | BR-AG-1 (naming facet) / Q4-A | lint | full |
| NFR-AG-TESTID-1 | reused testid convention | lint / component | full |
| NFR-AG-NOTS-1 | FR-UI-5 | structural | full |
| NFR-AG-PERF-1 | view-perf precedent | structural + observed | soft |
| NFR-AG-A11Y-1 | FR-UI (view) / Q6-A | observed | soft |
| NFR-AG-SCOPE-1 | — | N/A | governance |

**No orphaned FD rule**: BR-AG-1→NOFINAL-1 (+ADVISORY-1 naming facet), 2→CONFIRM-1, 3→CANCEL-1, 4→RBAC-1, 5→BODY-1, 6→ERROR-1, 7→NAMESPACE-1, 8→SCOPE-APPROVE-1, 9→NOREFETCH-1, 10→REFNOTOWN-1, 11→RECOVERY-1. COPY/TESTID/NOTS/FETCH/PERF/A11Y cover inherited + addendum concerns.

**Folds crystallized**: NFR-AG-Fold-1 (dual-operation single-double + cross-guard, Q2-A) · NFR-AG-Fold-2 (Q4-A copy realization — `confirmBody` corrected, lint unmodified) · NFR-AG-Fold-3 (all-three-roles+null stub coverage, Q3-A) · NFR-AG-Fold-4 (one consolidated transition test incl. split recovery, Q5-A).

---

## 3. Security-Guardrails extension — compliance (enabled extension)

First UI unit with a real **authorization-adjacent write surface** (an interactive write that triggers server-side authz). RBAC/authz rows carry **real content**.

| Control | Status | Rationale |
|---|---|---|
| **Least-privilege UI framing (RBAC-affordance)** | **Compliant** | The approve affordance is wrapped in `RoleGate can="act"` — cosmetically visible **only** to the `underwriter` cosmetic role (`act:true`); `auditor`/`admin`/`null` see the fallback (NFR-AG-RBAC-1, all-roles+null). Mirrors the frozen `auth_rbac` semantics (only `underwriter` holds `RBAC_COMMIT`) as **value shapes**, never imported. |
| **Authorization server-authoritative (defense-in-depth)** | **Compliant** | `RoleGate` makes **no** authz decision (NFR-AG-RBAC-1 structural — no backend import, no authz call). The real gate is AUTHZ-1: `DecisionCommitService` re-checks `authorize(underwriter_id, RBAC_COMMIT)` and raises `UnauthorizedCommit` (→ 403) even if the cosmetic guard were bypassed; the client renders 403 as a **genuine error** (NFR-AG-ERROR-1), never a silent success. |
| **No client-side authorization datum** | **Compliant** | `underwriter_id` is **never** client-sent (NFR-AG-BODY-1 — body deep-equals `{action:'approve'}`); it is session-derived server-side, so a client cannot commit *as another user* or self-elevate. |
| **Human-in-the-loop enforcement** | **Compliant** | No auto-commit path (NFR-AG-NOFINAL-1); an explicit confirm step gates every commit (NFR-AG-CONFIRM-1); the dialog is cancelable with zero side effects (NFR-AG-CANCEL-1); a commit failure never auto-retries the write (NFR-AG-RECOVERY-1). |
| **Error / output hygiene (no leakage)** | **Compliant** | Failures surface via the shared envelope: `message` visible, `code` in a hidden testid node, `detail` **never** rendered (NFR-AG-ERROR-1), aligned with WIRE-1 §4 ("no secret VALUE in message/detail"). |
| **Advisory-only naming** | **Compliant** | The system output is called a **recommendation**, never a *decision* (NFR-AG-ADVISORY-1, honored semantically — §4); the human `approve` namespace is never conflated with the system `APPROVE` (NFR-AG-NAMESPACE-1). |
| **Input validation (untrusted parsing)** | **N/A** | Parses no untrusted document/file; reads a typed WIRE-1 JSON body and posts a fixed constant action. Applicant-input validation is intake's SEC-2 (server-side). |
| **Prompt-injection / LLM safety** | **N/A** | No LLM anywhere in this unit; it issues no model call and renders no model output on the write path. |
| **Secrets management** | **N/A** | Holds/sends no secret value; session/auth-handshake material is the composition root's concern (WIRE-1 deferred seam), `secrets-config`'s SEC-3. |
| **Audit-trail persistence** | **N/A (delegated)** | Persists nothing. The full audit tuple is written server-side by audit-store's `DecisionCommitService` on the commit this action triggers — not this unit's responsibility. |

**No blocking finding.**

---

## 4. Governance note — Q4-A advisory-vocabulary resolution (semantic, not literal-exemption)

The single `FORBIDDEN_TERMS.systemOutput` forbids the bare token `decision`; the reserved-word rule (underwriting hard-constraint #1) *permits* "decision" for the **human's committed action**. This unit honors the constraint **semantically, not by exempting the literal token**:

- The **system recommendation is never called a *decision*** anywhere in this unit's copy — that is the substance of the constraint.
- The **human's committed action** is framed via **"approve" / "approval" / "record" / "committed"** — conveying the deliberate, finalizing weight of the commit **without** using the literal token `decision`.
- The one draft string that used the literal token (`confirmBody`) was **corrected at the FD source** (`domain-entities.md §3` — a LINT-SUBJECT realization refinement the FD deferred to NFR/Code-Gen, **not** an FD re-open). All **14** `APPROVAL_COPY` strings are now advisory-clean.
- Consequently the shared `advisory-vocabulary` lint applies **UNMODIFIED** — **no** carve-out, **no** second word-list, **no** split `FORBIDDEN_TERMS`. Cross-unit lint identity is preserved (NFR-AG-ADVISORY-1, NFR-AG-Fold-2).

---

## 5. Settled items held (not re-opened)
- The **frozen FD** (BR-AG-1..11 + inventory + state machine incl. split `ErrorRead`/`ErrorCommit` + AUTHZ-1 note) is the substrate — NFR builds testable targets **on** it. (The `domain-entities.md §3` `confirmBody` copy refinement is the LINT-SUBJECT realization the FD deferred — not an invariant change.)
- **ui-shell (frozen)** — its Vitest/RTL/ESLint/`FORBIDDEN_TERMS`/`RoleGate`/`ReadOnlyRegion`/badges/testid mechanisms are **reused**, not modified; `RoleContext` stub (all-roles+null) is RBAC-1's injection point; `RoleGate`/`ReadOnlyRegion`/badges are composed (first real `RoleGate` use).
- **ui-queue / ui-memo-view (frozen)** — their fetchSeam/StructuralGuard/testid-lint conventions are **mirrored**, **not imported** (REFNOTOWN-1 enforces the non-import).
- **WIRE-1** — R4 + R5 + `MemoView` + `CommittedDecision` + envelopes consumed **by shape**, mocked via the single injected double; the **route implementation** stays deferred to Build & Test (SCOPE-1).
- **Deferred values**: aesthetic token values, confirm-dialog a11y polish (focus-trap / Escape — Q6-A recorded for NFR-Design), state-holding mechanics (hook/store), bundler/deploy topology → NFR-Design / Code-Gen / `deploy-config` (P2). Infrastructure Design for `ui-approval-gate` not pre-committed (likely a logged SKIP — source-level view; Vercel topology is `deploy-config` P2) — confirmed at that stage.
