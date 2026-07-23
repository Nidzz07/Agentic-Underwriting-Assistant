# Code Summary — `ui-approval-gate` (U7)

**Stage**: BUILD → per-unit loop → Code Generation **Part 2 (executed)** · **Date**: 2026-07-09
**Result**: **237 frontend Vitest tests passed (61 files) · `src/approvalGate` 100% coverage (Stmts/Branch/Funcs/Lines) — QA-6 ≥90% PASSED · `src/shell` + `src/queue` + `src/memoView` stay 100% (untouched) · ESLint clean · backend pytest 850/31 untouched (separate runner/tree, zero backend files modified).**
The **14th** fully-complete unit and the **4th** completed frontend/React unit (after ui-shell, ui-queue, ui-memo-view).

---

## 1. Module inventory (new — under `frontend/src/approvalGate/`)

| Comp | File | Role |
|---|---|---|
| C9 | `copy.js` | `APPROVAL_COPY` — advisory-clean per NFR-AG-Fold-2 (no literal `decision`/`approved`/`declined`/bare `DECLINE`) |
| C2 | `commitFetchSeam.js` | own-local **dual-operation** seam `createCommitFetch(transport) → { fetchContext, submitApprove }` + `buildMemoRequest`/`buildCommitRequest` (narrow) + `normalizeError` + JSDoc contract |
| C4 | `components/RecommendationContext.jsx` | read-only rec/conf via frozen `ReadOnlyRegion` + badges |
| C7 | `components/CommittedConfirmation.jsx` | `{ decision, context }`-only success render (**no seam** — header comment) |
| C3 | `components/CommitStateView.jsx` | loading / pending / errorRead / errorCommit (four-status envelope render) |
| C6 | `components/CommitConfirmDialog.jsx` | sole `onConfirm` commit-trigger holder (**header comment**) |
| C5 | `components/ApproveAffordance.jsx` | `{ onApprove }`-only, `RoleGate can="act"` wrapped (**header comment**; first real RoleGate use) |
| C1 | `ApprovalGateView.jsx` | stateful orchestrator; owns the machine; **wires `onConfirm` ONLY to `CommitConfirmDialog`** |

**Build infra (extended, no frozen-src edit)**: `vitest.config.js` (+`src/approvalGate` include/coverage), `eslint-rules/approvalGate.js` (new `approval-testid-convention`), `eslint.config.js` (+`src/approvalGate` block reusing the shell lints). **No file under `src/shell/`, `src/queue/`, or `src/memoView/` modified.**

## 2. Test → target map (37 test cases across the `NFR-AG-*` set; all at NFR-pinned tier)

| Target | Test file(s) |
|---|---|
| NOFINAL-1 | `singleCallSite.test.js` (one `.submitApprove(` call site; ApproveAffordance no invocation/seam import) |
| CONFIRM-1 *(teeth)* | `approvalGate.confirm.test.jsx` (Approve → 0 submit / 1 fetch cross-guard; Confirm → 1) |
| CANCEL-1 *(teeth)* | `approvalGate.cancel.test.jsx` (open+Cancel → both counts unchanged, context identical) |
| RBAC-1 | `approvalGate.rbac.test.jsx` (all 3 roles + null) + `refNotOwn.imports.test.js` (no backend/authz) |
| BODY-1 | `commitFetchSeam.test.js` (body deep-equals `{action:'approve'}`, no `underwriter_id`/`reason`) |
| ERROR-1 | `approvalGate.error.test.jsx` (table 403/409/400/422 + detail-never + 200 success) |
| SCOPE-APPROVE-1 | `approvalGate.scope.test.jsx` (no override control / no reason input) |
| NOREFETCH-1 *(teeth)* | `approvalGate.norefetch.test.jsx` (both counts frozen after success) |
| RECOVERY-1 *(2-way teeth)* | `approvalGate.recovery.test.jsx` (ErrorRead Retry same id; ErrorCommit → ready, no auto-resubmit) |
| FETCH-1 | `approvalGate.state.test.jsx` (per-state) + `approvalGate.transition.test.jsx` (consolidated, incl. both recovery legs) |
| COPY-1 / ADVISORY-1 / TESTID-1 | `eslint.approval.rules.test.js` (reused shell lints UNMODIFIED + approval testid rule + self-tests) |
| NAMESPACE-1 | `namespace.test.jsx` (`COMMIT_ACTION_LABELS.approve`; `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS`) |
| NOTS-1 | `nots.test.js` |
| REFNOTOWN-1 | `refNotOwn.imports.test.js` (no backend/queue/memoView/router import + **no-`createCommitFetch`-in-presentational**, ND-Fold-3) |
| PERF-1 | `boundedFetch.test.js` (bounded R4 + R5, no real fetch) |
| TESTID-1 (presence) | `testid.test.jsx` |
| C3/C4/C6/C7 units | `components.test.jsx` |

## 3. Folds realized
- **CG-Fold-1** — `makeCommitDouble()` factory: fresh instance per call, each op an independently-counted spy (own `calls[]`); no cross-test leakage.
- **CG-Fold-2** — spies are programmable/sequenceable (`resolveWith`/`rejectWith`/`hang`/`sequence`); RECOVERY-1 uses a fail-then-succeed sequence distinct from the static ERROR-1 table, same one factory.
- **CG-Fold-3** — consistent module vocabulary (seam / commit trigger / single call site) across the C2 JSDoc + C5/C6/C7 header comments.
- **NFR-AG-Fold-1** — CONFIRM-1 cross-guard asserts `submitApprove===0` AND `fetchContext===1` (differing counts).
- **NFR-AG-Fold-2** — advisory-vocabulary lint UNMODIFIED; `copy.js` avoids the literal `decision` token.
- **ND-Fold-1/2/3** — the by-construction header comments (C5 `{onApprove}`-only, C6 sole `onConfirm`, C7 `{decision,context}`-only) shipped as explicit deliverables; ND-Fold-3 structurally guarded.

## 4. Holds honored
- **ui-shell / ui-queue / ui-memo-view (all frozen) untouched** — reused via import (shell) or mirrored-never-imported (siblings); enforced by `refNotOwn.imports.test.js`. No file under those trees created/edited.
- **No local `FORBIDDEN_TERMS`** — the one source reused; advisory-vocabulary lint UNMODIFIED.
- **By-construction guarantees** — C5 `{onApprove}`-only (no submit capability), C6 sole `onConfirm` holder (single call site), C7 `{decision,context}`-only (no seam), C2 narrow `buildCommitRequest` (no `reason`/`underwriter_id`) — each enforced by teeth + StructuralGuard.
- **WIRE-1 R4/R5 consumed by shape only** — no real network call; real wiring deferred to composition root / Build & Test.
- **`RoleGate` cosmetic only** (AUTHZ-1 server-side is the real gate); **no LLM; no TypeScript**; tier-B unauthorized; no other unit started.

## 5. Coverage evidence
`src/approvalGate`: **100% Stmts / 100% Branch / 100% Funcs / 100% Lines**. Frontend total: **852/852 stmts, 210/210 branch, 44/44 funcs, 852/852 lines — 100%**; `src/shell` + `src/queue` + `src/memoView` unchanged at 100%. Backend pytest **850 passed / 31 skipped** untouched (zero backend files modified; `testresults.txt` records the frontend result alongside, not merged).

> Note: React `act(...)` advisory warnings surface on the async error/commit state-settle legs; they are non-fatal (all 237 tests pass; `findBy*` polls within act) and do not affect coverage or correctness.
