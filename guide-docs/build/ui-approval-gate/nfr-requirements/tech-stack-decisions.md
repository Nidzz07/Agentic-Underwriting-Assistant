# Tech-Stack Decisions — `ui-approval-gate` (U7)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U7 `ui-approval-gate` · **Date**: 2026-07-09
**Principle**: inherit the frozen `frontend/` substrate **unchanged**; add **only** the answer-driven decisions for this unit's write path + dual-operation seam. **No new dependency.**

---

| # | Decision | Rationale / source |
|---|---|---|
| **D1** | **Vitest + React Testing Library + jsdom** as the test substrate. | Inherited from ui-shell (U10) and applied by ui-queue (U5) / ui-memo-view (U6). No live backend; component + interaction assertions run in jsdom. **No new dependency.** |
| **D2** | **Plain JS/JSX — no TypeScript.** | FR-UI-5 (NFR-AG-NOTS-1). Consistent with the whole `frontend/` package. |
| **D3** | **ESLint over the single `shell/copy` + `FORBIDDEN_TERMS` source**, registered on `src/approvalGate/**` via a config block **mirroring** the sibling blocks — **no `src/shell` edit, no second word-list**. | NFR-AG-COPY-1 / ADVISORY-1 / TESTID-1. `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS` asserted (single source). |
| **D4** | **`advisory-vocabulary` lint applied UNMODIFIED (Q4-A).** The unit's copy avoids the literal forbidden tokens (incl. `decision`); the reserved-word constraint is honored **semantically**. | Q4-A / NFR-AG-Fold-2. No carve-out, no split list — cross-unit lint identity preserved. The one offending FD draft string (`confirmBody`) was corrected at the FD source. |
| **D5** | **Single injected/capturing double for BOTH operations (Q2-A) — the dual-operation seam.** One object `{ fetchContext, submitApprove }`, each an **independently-counted spy** (own call log under the exact seam name; never a shared generic `calls` array). | Q2-A / NFR-AG-Fold-1. Extends ui-memo-view's single-double fold to a dual-operation seam. **Non-vacuous cross-guard**: CONFIRM-1 asserts `submitApprove.calls.length === 0` **and** `fetchContext.calls.length === 1` at the pre-`Confirm` checkpoint (differing counts → a wrong-counter/ swapped assertion fails). |
| **D6** | **StructuralGuard scans** (file/import walkers + detector self-tests) for `noBackendImport` / `noUiQueueImport` / `noMemoViewImport` / `noRouterImport` and the `boundedFetch` scan. | NFR-AG-REFNOTOWN-1 / PERF-1. Mirrors the sibling `boundedFetch`/`no*Import` pattern **without importing** it. |
| **D7** | **RoleGate render coverage via a stub `RoleProvider` over all three roles + null (Q3-A).** `underwriter` → affordance present; `auditor`/`admin`/`null` → absent. | Q3-A / NFR-AG-Fold-3 / NFR-AG-RBAC-1. `RoleProvider`/`useCurrentRole` is ui-shell's frozen seam (reused, not modified). Pins both non-underwriter `act:false` cells + the unauthenticated case. |
| **D8** | **ONE consolidated transition test (Q5-A)** on the same dual-operation double, covering all state-machine legs **including both split-error recovery paths** (`ErrorRead --Retry--> loading`, `ErrorCommit --> ready`). | Q5-A / NFR-AG-Fold-4 / NFR-AG-FETCH-1. Mirrors ui-memo-view's consolidated transition test, extended for the write path + split recovery. |
| **D9** | **`data-testid` convention `approval-<element>-<purpose>`** enforced by an `approval-testid-convention` lint/test (+ detector self-test), mirroring the sibling testid-convention. | NFR-AG-TESTID-1. Namespaced to `approval-*` so tests target this unit unambiguously. |
| **D10** | **PERF-1 / A11Y-1 observed/soft (Q6-A).** Confirm-dialog focus-trap + Escape-to-cancel are **recorded NFR-Design targets**, not Phase-1 gates. | Q6-A / NFR-AG-PERF-1 / A11Y-1. The **BR-AG-3 "cancelable" invariant is still gated** as full-rigor teeth (NFR-AG-CANCEL-1) — only the a11y polish is soft, consistent with the sibling precedent. |
| **D11** | **Frontend tests fold into the existing Vitest run** (separate runner from the backend pytest tree); no change to the backend suite. QA-6 ≥90% coverage on `frontend/src/approvalGate` at Code-Gen. | Consistent with ui-shell/ui-queue/ui-memo-view — the Vitest suite grows; the backend pytest total is untouched (separate runner/tree). |

**No new dependency** is introduced: Vitest + RTL + jsdom + ESLint + the ui-shell mechanisms already exist in `frontend/`. This unit adds source + tests only.

---

## Deferred to later stages (not decided here)
- **NFR-Design**: the pattern/component realization of the dual-operation seam, the confirm-dialog component + its a11y (focus-trap / Escape) design, state-holding mechanics (hook vs store).
- **Code-Gen**: the concrete `commitFetchSeam` + `copy.js` + component modules + co-located specs; the QA-6 coverage gate on `frontend/src/approvalGate`.
- **Infrastructure Design**: not pre-committed — likely a logged SKIP (source-level view; Vercel/bundler topology is `deploy-config` P2) — assessed at that stage.
- **`deploy-config` (P2)**: bundler, CORS, deploy topology, aesthetic token values.
