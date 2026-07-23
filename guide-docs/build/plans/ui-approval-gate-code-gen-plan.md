# Code Generation — Plan (Part 1) — `ui-approval-gate` (U7)

**Stage**: BUILD → per-unit loop → Code Generation **Part 1 (Plan)** · **Unit**: U7 `ui-approval-gate` · C-cluster UI · Phase 1 · **Date**: 2026-07-09
**Story**: US-UI-3 (approve gate) · **Requirements**: FR-UI-3 (`data-testid`) / FR-UI-5 (no-TS) / the human approval gate (advisory-only + human-in-the-loop hard constraints).
**Built ON** the frozen FD (**BR-AG-1..11**) + approved NFR Requirements (**nineteen `NFR-AG-*`**; dual-operation single-double; **NFR-AG-Fold-1..4**) + approved NFR Design (patterns **P1–P10**; components **C1–C9**; **ND-Fold-1..3**, ND-Fold-A/B) — **re-opening none**. **JS/JSX, NO TypeScript; Vitest + React Testing Library + jsdom** — mirroring the realized `ui-shell`/`ui-queue`/`ui-memo-view` convention (`frontend/src/<unit>/` + `__tests__/`; shared `vitest.config.js` / `eslint.config.js` / `eslint-rules/`). Full-TDD, tests/lint-first, leaf-first. **This plan is the single source of truth for ui-approval-gate Code Generation.**

> **Part 2 EXECUTED 2026-07-09** — Q1–Q6 all **A**; ambiguity-check CLEAN (§6.5, three folds); Steps 0–11 generated (§3 all `[x]`). **237 Vitest tests / 100% coverage on `src/approvalGate` (QA-6 PASSED); `src/shell` + `src/queue` + `src/memoView` stay 100%; ESLint clean; backend pytest 850/31 untouched.** See `guide-docs/build/ui-approval-gate/code/code-summary.md`.

---

## 0. Unit context

- **Story**: **US-UI-3** (the underwriter approve gate) — the first UI **write path**.
- **Dependencies**: `ui-shell` (frozen U10) — imports `RoleGate` (**first real use**), `ReadOnlyRegion`, `RecommendationBadge`/`ConfidenceBadge`, `Panel`/`AppFrame`, `shell/copy` labels + `COMMIT_ACTION_LABELS` + the **one `FORBIDDEN_TERMS`**, `RoleContext`/`useCurrentRole`. `ui-queue` (frozen U5) + `ui-memo-view` (frozen U6) — their `fetchSeam`/`StructuralGuard`/testid-lint are **mirrored as a convention, NOT imported**. **WIRE-1 R4 + R5** consumed **by shape** (mocked in tests via the injected dual-operation `commitFetchSeam`).
- **Interfaces/contracts**: reads R4 `GET /applications/{application_id}/memo` → `MemoView` (for the recommendation context); writes R5 `POST /recommendations/{recommendation_id}/commit` with body `{ action: "approve" }` → `CommittedDecision`; error envelope `{error:{code,message,detail?}}` per WIRE-1 §4. **Approve-only** (no `reason`; `underwriter_id` NOT in the body — session-derived).
- **Database entities owned**: **none** (the atomic write + audit tuple are audit-store's `DecisionCommitService`, server-side; this unit persists nothing).
- **Boundaries**: `RoleGate` is **cosmetic** (AUTHZ-1 is the server's real gate); **no override** (U8); **no LLM**; **no real network**; **no persistence**.

## 1. Component → module map (production under `frontend/src/approvalGate/`)

| Comp | Module (file) | Exports / role | Backs |
|---|---|---|---|
| **C9** | `approvalGate/copy.js` | `APPROVAL_COPY` — approval-local UI strings, **advisory-clean per NFR-AG-Fold-2** (no literal `decision`/`approved`/`declined`/bare `DECLINE`); LINT-SUBJECT; not a domain-enum label source | COPY-1, ADVISORY-1 |
| **C2** | `approvalGate/commitFetchSeam.js` | the own-local **dual-operation** seam: `createCommitFetch(transport)` → `{ fetchContext(applicationId), submitApprove(recommendationId) }` + `buildMemoRequest`/`buildCommitRequest` (P3 narrow signature) + `normalizeError`; **JSDoc contract** (Q4); duck-typed (ND-D-Fold); **mirrors sibling `fetchSeam`, NOT imported** | FETCH-1, BODY-1, RECOVERY-1, PERF-1 |
| **C4** | `approvalGate/components/RecommendationContext.jsx` | `{ recommendation, confidence, testid }` — **composes the frozen `ReadOnlyRegion`** + `RecommendationBadge`/`ConfidenceBadge`, engine-attributed (the recommendation being approved) | NAMESPACE-1, COPY-1, TESTID-1 |
| **C7** | `approvalGate/components/CommittedConfirmation.jsx` | **`{ decision, context }` ONLY** (Q3-A / ND-Fold-3) — renders the `CommittedDecision` echo + R4 context; **no seam reference**. **Carries the header comment** ("props `{decision, context}` only — no seam; renders from the echo, never re-fetches") — an explicit deliverable | NOREFETCH-1, TESTID-1 |
| **C3** | `approvalGate/components/CommitStateView.jsx` | `{ state, error, onRetry, testid }` — `loading` / `pending` (no affordance) / **`ErrorRead` + `ErrorCommit`** envelope render (four-status: `message`-visible / `code`-testid / `detail`-never) | ERROR-1, FETCH-1(states), RECOVERY-1(render) |
| **C6** | `approvalGate/components/CommitConfirmDialog.jsx` | **`{ onConfirm, onCancel, ...display }`** — the confirm step; its `Confirm` handler is the **single `submitApprove` call site** (via `onConfirm`); open/cancel a pure toggle. **Carries the header comment** ("SOLE commit-trigger holder; `onConfirm` is the single call site") — an explicit deliverable | NOFINAL-1, CONFIRM-1, CANCEL-1 |
| **C5** | `approvalGate/components/ApproveAffordance.jsx` | **`{ onApprove }` (+ cosmetic display) ONLY** (Q2-A / ND-Fold-1) — the approve button, wrapped in **`<RoleGate can="act">`** (first real use); `onClick` → `onApprove()` opens the dialog; **no `submitApprove`/seam/`onConfirm`**. **Carries the header comment** ("props `{onApprove}` (+cosmetic) only — no `submitApprove`/seam/`onConfirm`; opens the dialog, cannot commit") — an explicit deliverable | RBAC-1, NOFINAL-1 |
| **C1** | `approvalGate/ApprovalGateView.jsx` | the stateful owner: holds the injected `commitFetchSeam` (**sole** holder), runs the initial R4 read, drives the machine (`loading→ready(idle)→confirming→submitting→{committed\|ErrorCommit}` + `pending` + `ErrorRead`), and **wires `onConfirm` ONLY to `CommitConfirmDialog`** (P1) | FETCH-1, RECOVERY-1, all composition |
| **C8** | *(test-only)* `approvalGate/__tests__/*` + `eslint-rules/approvalGate.js` + shared-config extension (Q1) | the StructuralGuard substrate: scans + lints + detector self-tests, incl. the **single-call-site scan** (P1) and the **no-`createCommitFetch`-import-in-presentational-components** guard (ND-Fold-3) | TESTID-1, NOTS-1, REFNOTOWN-1, NOFINAL-1(structural) |

**Tests** live in `frontend/src/approvalGate/__tests__/` (mirroring `shell`/`queue`/`memoView`). **No file under `frontend/src/shell/`, `frontend/src/queue/`, or `frontend/src/memoView/` is created or modified.**

> **Header comments are explicit Code-Gen deliverables (not implicit)** — C5, C6, C7 each ship a header comment (the frozen `ReadOnlyRegion.jsx`/`fetchSeam.js`/`NarrativeRegion.jsx` self-evidence convention) making the by-construction guarantee self-evident when reading the component in isolation (ND-Fold-1/2/3). Called out here exactly as `NarrativeRegion`'s header comment was in ui-memo-view's plan.

## 2. TDD test → `NFR-AG-*` target map (every target at its NFR-pinned tier)

| Target | Test (file :: focus) | Tier |
|---|---|---|
| **NOFINAL-1** | `singleCallSite.test.js` (structural: `submitApprove` has exactly one call site — the confirm handler; mount/read/toggle issue no POST) + detector self-test | structural |
| **CONFIRM-1** *(teeth, full-highest)* | `approvalGate.confirm.test.jsx` (dual-op double, Q2): `Approve`-click → **`submitApprove.calls.length===0` AND `fetchContext.calls.length===1`** (Fold-1 cross-guard); only `Confirm` → `===1` | component (teeth) |
| **CANCEL-1** *(teeth, full-highest)* | `approvalGate.cancel.test.jsx`: `Approve`→open→`Cancel` → **both** ops' counts unchanged; context identical before/after; state `ready(idle)` | component (teeth) |
| **RBAC-1** | `approvalGate.rbac.test.jsx` (stub `RoleProvider` **all three roles + null**, Fold-3: `underwriter`→affordance present; `auditor`/`admin`/`null`→absent) + `noBackendImport.test.js` + no-authz-call structural | component + structural |
| **BODY-1** | `commitFetchSeam.test.js` (`buildCommitRequest(recId)` body **deep-equals** `{action:'approve'}` — no `underwriter_id`, no `reason`; `recommendation_id` in path; method POST) | unit |
| **ERROR-1** | `approvalGate.error.test.jsx` (table-driven, Q3: **200**→committed / **403**→not-permitted / **409**→conflict / **400 & 422**→generic; `approval-error-message` visible, `approval-error-code` hidden testid, `detail` absent from DOM) | component (table-driven) |
| **SCOPE-APPROVE-1** | `approvalGate.approveOnly.test.jsx` (no override control / no reason input in the tree) + `commitFetchSeam.test.js` (no `reason` key) | structural + component |
| **NOREFETCH-1** *(teeth)* | `approvalGate.norefetch.test.jsx`: after a successful commit, **both** `fetchContext.calls.length` and `submitApprove.calls.length` unchanged (`1`,`1`); confirmation shows echo + context | component (teeth) |
| **RECOVERY-1** *(two-directional teeth)* | `approvalGate.recovery.test.jsx`: (a) `ErrorRead` Retry → exactly one further `fetchContext`, recorded arg `===X`; (b) `ErrorCommit` → `ready(idle)`, `submitApprove.calls.length` stays `1` | component (teeth) |
| **FETCH-1** | `approvalGate.state.test.jsx` (per-state renders: loading/pending/ready(idle)/confirming/submitting/committed/ErrorRead/ErrorCommit) + `approvalGate.transition.test.jsx` (**one consolidated transition test**, Q5, all legs incl. **both** recovery paths) — all on the **single dual-op double** (Fold-1/4) | component (RTL) |
| **COPY-1** | `eslint.approval.rules.test.js` (no-inline-label RuleTester, **reuses** ui-shell `FORBIDDEN_TERMS`) + `recommendationContext.test.jsx` (label look-up) + detector self-test | lint (+ RTL) |
| **ADVISORY-1** | `eslint.approval.rules.test.js` (advisory-vocabulary RuleTester over `src/approvalGate/**` static code, **UNMODIFIED**, Q4-A; `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS`) + synthetic self-test | lint / structural |
| **NAMESPACE-1** | `namespace.test.jsx` (the human `approve` label from `COMMIT_ACTION_LABELS.approve`, never a `RECOMMENDATION_LABELS` value; **collision guard** over the reused `FORBIDDEN_TERMS`; no bare `DECLINE`) + self-test | structural |
| **TESTID-1** | `eslint.approval.rules.test.js` (approval-testid-convention `^approval-[a-z]+(-[a-z0-9]+)+$`) + `testid.test.jsx` presence + `isValidApprovalTestid` self-test | lint / component |
| **NOTS-1** | `nots.test.js` (0 `.ts`/`.tsx` under `src/approvalGate`; predicate self-test) | structural |
| **REFNOTOWN-1** | `noBackendImport.test.js` + `noUiQueueImport.test.js` + `noMemoViewImport.test.js` + `noRouterImport.test.js` + **`noCreateCommitFetchImportInPresentational.test.js`** (ND-Fold-3) — each with a detector self-test | structural |
| **PERF-1** | `boundedFetch.test.js` (structural: R4 one resource by `applicationId` + R5 one commit by `recommendationId`; no list/all-rows path) — observed, non-gating | structural + observed |
| **A11Y-1** | recorded/observed — semantic markup + focusable `Approve`/`Confirm`/`Cancel`/`Retry`; confirm-dialog focus-trap/Escape **recorded** NFR-Design→Code-Gen target, **non-gating** (Q6-A of NFR-Req) | observed / soft |
| **SCOPE-1** | governance/exclusion — no test imports a backend module, `ui-queue`, `ui-memo-view`, or exercises the real R4/R5 wire | N/A |

Every `NFR-AG-*` target mapped; no orphan. No test imports a backend module, a sibling UI unit, or hits the real network.

## 3. Leaf-first build order (numbered Part-2 steps — EXECUTED 2026-07-09)

- [x] **Step 0 — Scaffold + shared-config extension (Q1)**: created `frontend/src/approvalGate/` tree + `approvalGate/copy.js`; extended the **shared** `vitest.config.js` (`include` + `coverage.include` add `src/approvalGate`; **thresholds unchanged**) + registered the reused lints + the new `approval-testid-convention` rule (`eslint-rules/approvalGate.js`) for `src/approvalGate` in `eslint.config.js` — **no file under `src/shell/`, `src/queue/`, or `src/memoView/` touched**.
- [x] **Step 1 — C9 `copy.js`**: `APPROVAL_COPY`, **advisory-clean** (Fold-2). (COPY-1/ADVISORY-1)
- [x] **Step 2 — C2 `commitFetchSeam.js`**: the **dual-operation** seam + `buildMemoRequest`/`buildCommitRequest` (narrow) + `normalizeError` + **JSDoc contract** (Q4). (FETCH-1, BODY-1, RECOVERY-1, PERF-1)
- [x] **Step 3 — C4 `RecommendationContext.jsx`**: read-only rec/conf via frozen `ReadOnlyRegion` + badges. (NAMESPACE-1, COPY-1)
- [x] **Step 4 — C7 `CommittedConfirmation.jsx`**: props-only `{decision, context}` + **header comment**; no seam. (NOREFETCH-1)
- [x] **Step 5 — C3 `CommitStateView.jsx`**: loading / pending / four-status `ErrorRead`/`ErrorCommit` render. (ERROR-1, FETCH-1 states)
- [x] **Step 6 — C6 `CommitConfirmDialog.jsx`**: sole `onConfirm` holder + **header comment**; open/cancel pure toggle. (CONFIRM-1/CANCEL-1)
- [x] **Step 7 — C5 `ApproveAffordance.jsx`**: `RoleGate can="act"`-wrapped, `{onApprove}`-only + **header comment**; no commit capability. (RBAC-1)
- [x] **Step 8 — C1 `ApprovalGateView.jsx`**: composes C2–C7, owns the machine, **wires `onConfirm` ONLY to C6**; the CONFIRM/CANCEL/NOREFETCH/RECOVERY teeth on the dual-op double. (FETCH-1, CONFIRM-1, CANCEL-1, NOREFETCH-1, RECOVERY-1)
- [x] **Step 9 — C8 StructuralGuard**: single-call-site scan (NOFINAL-1), no-backend/`ui-queue`/`ui-memo-view`/router import, **no-`createCommitFetch`-import-in-presentational** (ND-Fold-3), no-TS, bounded-fetch, testid convention, `FORBIDDEN_TERMS` reuse — each with a detector self-test. (NOFINAL-1, TESTID-1, NOTS-1, REFNOTOWN-1)
- [x] **Step 10 — Coverage / quality gate**: **237 Vitest passed / `src/approvalGate` 100% (QA-6 PASSED)**; `src/shell` + `src/queue` + `src/memoView` stay **100%**; ESLint clean; backend pytest untouched.
- [x] **Step 11 — Code summary**: `guide-docs/build/ui-approval-gate/code/code-summary.md` written; `testresults.txt` refreshed.

## 6.5 Ambiguity-check (RUN 2026-07-09, after the Q1–Q6 answers) — **CLEAN, no STOP** (three folds)

Ran against the six answers (all A) + the frozen FD (BR-AG-1..11) + approved NFR Requirements (nineteen `NFR-AG-*`) + approved NFR Design (P1–P10, C1–C9, all folds). **No genuine gap.** The three user-flagged checks:
- **(i) makeCommitDouble reset/teardown → CG-Fold-1** — the factory returns a **fresh instance per call** (each op an independently-counted spy with its own `calls[]`); each test constructs its own double (never a shared module-level mutable one), plus RTL's auto-cleanup — no cross-test call-count leakage, so the "exactly 0" / "exactly 1" assertions are isolated.
- **(ii) RECOVERY-1 vs the static ERROR-1 table → CG-Fold-2** — the factory's spies are **programmable/sequenceable** (`resolveWith`/`rejectWith`/`hang`/`sequence`); RECOVERY-1 uses its own **fail-then-succeed sequence** (a transition), distinct from the static ERROR-1 render table — all on the SAME one factory.
- **(iii) JSDoc + header-comment terminology → CG-Fold-3** — one consistent module vocabulary: **"the seam"** = `commitFetchSeam`, **"the commit trigger"** = the `onConfirm`→`submitApprove` invocation, **"the single call site"** = `CommitConfirmDialog`'s Confirm handler; the C2 JSDoc + the C5/C6/C7 header comments all use these terms (verified at authoring).

## 4. HOLDS restated (binding through Part 2)

- **ui-shell (frozen) untouched** — `RoleGate` / `ReadOnlyRegion` / badges / `shell/copy` + `COMMIT_ACTION_LABELS` + `FORBIDDEN_TERMS` / `RoleContext`/`useCurrentRole` **reused via import only, never modified**; **no file under `frontend/src/shell/` created or edited**.
- **ui-queue + ui-memo-view (frozen) untouched** — their `fetchSeam`/`StructuralGuard`/testid-lint patterns are **mirrored, never imported**; **no file under `frontend/src/queue/` or `frontend/src/memoView/` created or edited** (REFNOTOWN-1 enforces `noUiQueueImport`/`noMemoViewImport`).
- **No local `FORBIDDEN_TERMS` word-list** — the unit reuses the **one** source (COPY-1/ADVISORY-1/NAMESPACE-1); `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS`. The `advisory-vocabulary` lint applies **UNMODIFIED** (Q4-A / Fold-2; copy honors the reserved-word constraint semantically — no literal `decision` token).
- **The by-construction guarantees are HARD Code-Gen requirements, not optional**, each with its header comment: **C5** `{onApprove}`-only props (no `submitApprove`/seam) · **C6** the sole `onConfirm` holder / single call site · **C7** `{decision, context}`-only props (no seam) · **C2** `buildCommitRequest(recommendationId)` narrow signature (structurally cannot emit `reason`/`underwriter_id`). Enforced by teeth + StructuralGuard scans.
- **WIRE-1 R4/R5 consumed by shape only** — no real network call in the unit or its tests; **real `commitFetchSeam` wiring + R4/R5 route implementation deferred to the composition root / Build & Test**.
- **`RoleGate` is cosmetic** — no authz decision, no backend import (AUTHZ-1 is the server's real gate).
- **No LLM. No TypeScript** (NOTS-1). **tier-B run stays unauthorized and out of scope. No other unit started.**

## 5. Coverage / quality gate (frontend Vitest — NOT the Python pytest suite)

- **Runner**: JS/React unit → **Vitest coverage folded into the frontend test run**, the established convention — **NOT** the backend `pytest --cov=backend/*` suite.
- **Baseline (from `ui-memo-view` completion)**: `frontend/src/shell` = **100%**, `frontend/src/queue` = **100%**, `frontend/src/memoView` = **100%** (161 Vitest tests). ui-approval-gate adds `src/approvalGate` coverage; **none of the three existing trees may regress** (no file in any is touched, so all three stand) and `src/approvalGate` must meet **QA-6 ≥ 90%**.
- **Backend untouched (confirm)**: this is a pure frontend addition — the backend **pytest suite (850 passed / 31 skipped**, unchanged since admin-cli) must remain **completely untouched** (zero backend files modified; separate runner/tree). `testresults.txt` records the frontend result **alongside**, not merged.

## 6. Open Code-Gen-only questions (`[Answer]` tags — LEFT BLANK; lettered; full text below)

> Fill these; I then run the ambiguity-check (§6.5), then Part 2 (§3 Steps 0–11) **on your explicit go**. Per the standing convention the full Q&A is re-embedded here once answered.

### Q1 — Shared frontend config extension (coverage scope + lint registration) without touching frozen src
- **A.** **Extend the shared frontend config** — add `src/approvalGate` to `vitest.config.js` `include` + `coverage.include`, and register the reused `no-inline-label` + `advisory-vocabulary` lints + a **new `approval-testid-convention` rule** (`eslint-rules/approvalGate.js`, mirroring `eslint-rules/memoView.js`) for `src/approvalGate` in `eslint.config.js`. **No file under `src/shell/`, `src/queue/`, or `src/memoView/` modified; `vitest.config.js` thresholds unchanged** — all three frozen coverage gates stand. *(Recommended — consistent with the single frontend run.)*
- **B.** **approvalGate-scoped config** (separate Vitest project / ESLint override) leaving the shared config untouched.

`[Answer]:` A

### Q2 — Dual-operation capturing double construction (proving the independent-counting guarantee, Fold-1)
- **A.** **A shared `makeCommitDouble()` factory** (in `approvalGate/__tests__/fixtures.js`) returning a **single object `{ fetchContext, submitApprove }`** where each operation is an **independently-counted spy** (its own `calls` array of recorded args); programmable per operation (`fetchContext` resolves `MemoView` / rejects an envelope; `submitApprove` resolves `CommittedDecision` / rejects an envelope). Teeth read `double.fetchContext.calls.length` / `double.submitApprove.calls.length` (the cross-guard: `0` vs `1`). **One construction reused across all teeth tests** (extends the sibling single-double Fold-A). *(Recommended.)*
- **B.** **Two separate injected doubles** (one per operation) — diverges from the single-double convention.
- **C.** **Inline per-test spies** in each test file.

`[Answer]:` A

### Q3 — ERROR-1 four-status fixture construction
- **A.** **A shared named envelope-fixtures set** (in `fixtures.js`): a success `CommittedDecision` (200) + `forbiddenEnvelope` (403) / `conflictEnvelope` (409) / `invalidEnvelope` (400) / `unprocessableEnvelope` (422), each a well-formed `{error:{code,message,detail}}`; driven **table-style** `[{status, programmed, expectedTestid}]` reused across the ERROR-1 cases. *(Recommended — DRY, table-driven, mirrors the single-fixtures discipline.)*
- **B.** **Inline per-status** fixtures in the error test file.

`[Answer]:` A

### Q4 — `commitFetchSeam` JSDoc contract wording (the two operations)
- **A.** **A JSDoc block on `createCommitFetch`** documenting **both** operations: `fetchContext(applicationId)` → resolves the `MemoView` body / rejects a normalized `{error:{code,message,detail}}` envelope; `submitApprove(recommendationId)` → POSTs `{action:'approve'}` → resolves `CommittedDecision` / rejects the normalized envelope; **duck-typed, no formal interface** (ND-D-Fold); `normalizeError` produces the **WIRE-1 §4 shape** (own-local, **not imported** from a sibling). *(Recommended — self-documenting; the dual-op double is the worked example.)*
- **B.** **A minimal one-line comment** per export.

`[Answer]:` A

### Q5 — Consolidated state-transition test file location (mirroring the sibling convention)
- **A.** Its **own file** `approvalGate.transition.test.jsx`, alongside the per-state `approvalGate.state.test.jsx`. *(Recommended — one-file-per-concern, matches ui-shell/ui-queue/ui-memo-view.)*
- **B.** In the **same file** as the per-state tests.

`[Answer]:` A

### Q6 — Confirm-dialog / committed copy wording verification against the corrected advisory-clean `copy.js`
- **A.** **Use the corrected `APPROVAL_COPY` strings verbatim** (from `domain-entities.md §3` — `confirmBody` = "You are about to approve this recommendation. Your approval will be recorded.", `committedTitle` = "Approval recorded", etc.), all **advisory-clean** (no literal `decision`/`approved`/`declined`/bare `DECLINE`); the **unmodified `advisory-vocabulary` lint** is the build-failing enforcement; a detector self-test confirms non-vacuity. *(Recommended — the Fold-2 resolution is already applied at the FD source; Code-Gen consumes it verbatim.)*
- **B.** **Re-draft** the confirm/committed copy at Code-Gen.

`[Answer]:` A

---

## 7. Gate
**Part 2 EXECUTED** (§3 Steps 0–11 `[x]`); ambiguity-check CLEAN (§6.5, three folds). **237 Vitest tests / 100% coverage on `src/approvalGate` (QA-6 PASSED); `src/shell` + `src/queue` + `src/memoView` stay 100%; ESLint clean; backend pytest 850/31 untouched.** WIRE-1 · ui-shell · ui-queue · ui-memo-view (all frozen) untouched; tier-B NOT authorized; no other unit started. **STOPPED at the standardized Code-Gen 2-option completion gate** (1. Request Changes / 2. Continue → this is the LAST stage for ui-approval-gate) for the user's diff review.
