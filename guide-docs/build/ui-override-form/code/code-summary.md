# Code Generation — Summary (Part 2) — `ui-override-form` (U8)

**Stage**: BUILD → per-unit loop → Code Generation **Part 2** · **Unit**: U8 `ui-override-form` · C-cluster UI · Phase 1 · **Date**: 2026-07-09
**Story**: US-UI-5 (override-with-mandatory-reason) · **Requirements**: FR-UI-4 / FR-UI-3 / FR-UI-5 / **CON-BR4** (advisory-only + human-in-the-loop + mandatory reason).
**Built ON** the frozen FD (**BR-OVR-1..12**) + approved NFR Requirements (twenty `NFR-OVR-*`; Fold-A/1/2/3) + approved NFR Design (patterns **P1–P12**; components **C1–C10**; ND-OVR-Fold-i/ii/iii) — **re-opening none**. **JS/JSX, NO TypeScript; Vitest + RTL + jsdom.** Full-TDD tests-first, leaf-first, per plan §3 Steps 0–12.

The **second and final UI write path** — the `override` sibling of the frozen `approve` unit (U7) — and the one that realizes the mandatory-reason gate U7 deferred. The sibling `ui-shell`/`ui-queue`/`ui-memo-view`/`ui-approval-gate` conventions are **reused (ui-shell, imported) / mirrored-not-imported (the three sibling UI units) / consumed-by-shape (WIRE-1)**; no frozen file created or edited.

---

## 1. Module list (production under `frontend/src/overrideForm/`)

| Comp | Module | Role | Coverage |
|---|---|---|---|
| **C1** | `OverrideFormView.jsx` | stateful orchestrator; sole seam holder; owns the phase machine **and the independent `reason` slice** (P8); computes the **single `isReasonPresent` predicate** (exported); wires `onConfirm` **ONLY** to `OverrideConfirmDialog` (P1) | 100% stmts/funcs/lines · **97.05% branch** (see note) |
| **C2** | `overrideFetchSeam.js` | own-local **dual-operation reason-carrying** seam: `createOverrideFetch(transport) → { fetchContext, submitOverride(recommendationId, reason) }` + `buildMemoRequest` / `buildOverrideRequest(recommendationId, reason)` (**reason-required**) + `normalizeError`; **JSDoc contract** (Q5-A) | 100% |
| **C3** | `components/CommitStateView.jsx` | `loading` / `pending` / four-status `errorRead`+`errorCommit` render (`message` visible / `code` hidden testid / `detail` never; **409 dual-cause** under one `commit_conflict`) | 100% |
| **C4** | `components/RecommendationContext.jsx` | read-only rec/conf via frozen `ReadOnlyRegion` + badges (label look-up by value) | 100% |
| **C5** | `components/OverrideReasonInput.jsx` | **NEW** controlled `{ value, onChange }`-only `<textarea>`; **header comment**; no seam | 100% |
| **C6** | `components/OverrideAffordance.jsx` | `RoleGate can="act"`-wrapped `{ onOverride, disabled }`-only button (`disabled` **derived from the one predicate**); **header comment**; no commit capability | 100% |
| **C7** | `components/OverrideConfirmDialog.jsx` | **sole `onConfirm` holder** = single call site; **echoes the reason read-only** (`override-confirm-reason-echo`); **header comment**; open/cancel a pure toggle | 100% |
| **C8** | `components/CommittedConfirmation.jsx` | `{ decision, context }`-only echo render (committed `reason` from **`decision.reason`**, ND-OVR-Fold-ii); **header comment**; no seam | 100% |
| **C10** | `copy.js` | `OVERRIDE_COPY` — 21 advisory-clean strings, consumed **verbatim** from the FD (Q8-A); LINT-SUBJECT | 100% |
| **C9** | `__tests__/*` + `eslint-rules/overrideForm.js` + shared-config extension | StructuralGuard substrate (test-only) | n/a |

**Shared-config extension (Q1-A)** — `vitest.config.js` `include` + `coverage.include` add `src/overrideForm` (**thresholds unchanged**); `eslint.config.js` registers a new `src/overrideForm` block reusing `shell/no-inline-label` + `shell/advisory-vocabulary` + the new `override/override-testid-convention` rule (`eslint-rules/overrideForm.js`). **No file under `src/shell/`, `src/queue/`, `src/memoView/`, or `src/approvalGate/` created or edited.**

---

## 2. Test → `NFR-OVR-*` target map (28 test files + `fixtures.js`; all twenty targets at their NFR-pinned tier)

| Target | Test file(s) | Tier |
|---|---|---|
| **NOFINAL-1** | `singleCallSite.test.js` (one `.submitOverride(` site; affordance no invocation/import; belt-and-suspenders one-predicate reuse ≥2) | structural |
| **CONFIRM-1** | `overrideForm.confirm.test.jsx` (teeth: Override→0 submit/1 fetch cross-guard; Confirm→1, reason verbatim) | component (teeth) |
| **CANCEL-1** | `overrideForm.cancel.test.jsx` (teeth: open+Cancel → both counts unchanged, context identical, reason preserved) | component (teeth) |
| **REASONGATE-1** | `overrideForm.reasongate.test.jsx` (5 `BLANK_REASONS` → disabled + 0 submit across full attempt; `NONBLANK_REASON` → exactly 1 POST, reason as-entered) + `reasonTrimDivergence.test.js` (trim() vs str.strip() non-byte-identity, U+001C–U+001F/U+0085) | component (teeth) + unit (doc) |
| **RBAC-1** | `overrideForm.rbac.test.jsx` (3 roles + null) + `noBackendImport.test.js` (no backend + no client authz call) | component + structural |
| **BODY-1** | `overrideFetchSeam.test.js` (body deep-equals `{action:'override', reason}`; no `underwriter_id`; reason as-entered) | unit |
| **ERROR-1** | `overrideForm.error.test.jsx` (table 403/409/400/422; detail-never; 200 success; 409 dual-cause one code) | component (table) |
| **NOREFETCH-1** | `overrideForm.norefetch.test.jsx` (teeth: both counts frozen at 1; reason echo from `decision.reason`) | component (teeth) |
| **RECOVERY-1** | `overrideForm.recovery.test.jsx` (2-way teeth: errorRead Retry same id; errorCommit→ready, no auto-resubmit, reason preserved) | component (teeth) |
| **REASONKEEP-1** | `overrideForm.reasonkeep.test.jsx` (preservation across Cancel + errorCommit; read-only echo distinct from committed node) | component |
| **CAPFREE-1** | `capabilityFree.imports.test.js` (ReasonInput/Affordance no seam + no submit) + `noCreateOverrideFetchImportInPresentational.test.js` + `overrideReasonInput.test.jsx` (prop-contract) | structural + component |
| **FETCH-1** | `overrideForm.state.test.jsx` (7 per-state) + `overrideForm.transition.test.jsx` (consolidated, both recovery legs + reason-carrying) | component |
| **COPY-1 / ADVISORY-1 / TESTID-1** | `eslint.override.rules.test.js` (reused shell lints UNMODIFIED + `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS` + override testid RuleTester + self-tests) + `recommendationContext.test.jsx` + `testid.test.jsx` | lint (+ RTL) |
| **NAMESPACE-1** | `namespace.test.jsx` (`COMMIT_ACTION_LABELS.override`; action node never a Recommendation label esp. DECLINE-RECOMMEND; single `FORBIDDEN_TERMS` `===`) | structural |
| **NOTS-1** | `nots.test.js` (0 `.ts`/`.tsx`) | structural |
| **REFNOTOWN-1** | `noBackendImport` + `noUiQueueImport` + `noMemoViewImport` + **`noApprovalGateImport` (NEW)** + `noRouterImport` + `noCreateOverrideFetchImportInPresentational` — each + self-test | structural |
| **PERF-1** | `boundedFetch.test.js` (R4 one resource + R5 one commit; no real fetch) | structural / observed |
| **A11Y-1** | `<textarea>` label/`aria-label` association (`overrideReasonInput.test.jsx`) + focusable controls — observed/soft, non-gating; confirm-dialog focus-trap/Escape recorded → not Phase-1-gated | observed / soft |
| **SCOPE-1** | governance — no test imports a backend module, a sibling UI unit, or hits the real R4/R5 wire | n/a |

Fixtures (`fixtures.js`, Q2/Q3/Q4-A): `makeOverrideDouble()` (dual-op, `submitOverride.calls[i] = [recommendationId, reason]`), `makeMemoView`/`pendingMemoView`/`makeCommittedOverride`, `BLANK_REASONS`/`NONBLANK_REASON`, the four error envelopes (409 reused for both causes), `renderForm`.

---

## 3. Result

- **Frontend suite (Vitest)**: **340 passed** (89 test files); **ESLint clean** (`npm run lint`, exit 0).
- **Coverage — all-files 100% stmts/funcs/lines, 99.66% branch**. `src/overrideForm`: **100% stmts/funcs/lines, 98.36% branch** — **QA-6 (≥90%) PASSED**. Every component file 100% on all metrics; the only sub-100% branch is `OverrideFormView.jsx` at 97.05% (see realization note).
- **Frozen trees untouched, still 100%**: `src/shell`, `src/queue`, `src/memoView`, `src/approvalGate` (no file created or edited in any).
- **Backend pytest suite (850 passed / 31 skipped) untouched** — zero backend files modified; separate runner/tree, not re-run. Frontend result recorded **alongside** in `testresults.txt`, not merged.

### Flagged realization note
- **`OverrideFormView.jsx:67` — one uncovered branch (belt-and-suspenders guard).** The `onConfirm` handler re-applies the single `isReasonPresent(reason)` predicate before submitting (`if (!isReasonPresent(reason)) { setPhase('ready'); return; }`). Its **true-branch is unreachable by construction**: the reason is **frozen during `confirming`** (the editable `OverrideReasonInput` renders only in `ready(idle)`), and the affordance is `disabled` when blank, so `onConfirm` can never run with a blank reason. This is exactly the **documented optional insurance** of **ND-OVR-Fold-i / P2** — retained to guard a future refactor that might make the reason editable during `confirming`, and **deliberately not elevated to a hard gate**. Its *presence* is asserted non-vacuously in `singleCallSite.test.js` (the one predicate is reused ≥2×: the affordance `disabled` derivation + this re-check). Rather than contrive a test that bypasses the component's own invariant to force the branch, it is reported honestly; 97.05% branch on this file (98.36% unit) clears the ≥90% QA-6 gate.

### Holds upheld
- **ui-shell (frozen) untouched** — `RoleGate`/`ReadOnlyRegion`/badges/`Panel`/`shell/copy`+`COMMIT_ACTION_LABELS.override`+`FORBIDDEN_TERMS`/`RoleContext` reused via import only.
- **ui-queue + ui-memo-view + ui-approval-gate (frozen) untouched** — fetchSeam/StructuralGuard/by-construction/testid-lint **mirrored, never imported** (REFNOTOWN-1 incl. the **NEW `noApprovalGateImport`**).
- **No local `FORBIDDEN_TERMS` word-list** — the one source reused; `advisory-vocabulary` lint applied **UNMODIFIED** (Fold-3; `OVERRIDE_COPY` clean at the FD source, consumed verbatim).
- **By-construction guarantees are hard requirements** with header comments: C5 `{value,onChange}`-only · C6 `{onOverride,disabled}`-only (disabled derived from the one predicate) · C7 sole `onConfirm` holder / single call site + reason echo · C8 `{decision,context}`-only · C2 `buildOverrideRequest(recommendationId, reason)` reason-required.
- **Reason slice structurally independent of the phase slice** (P8) — Cancel/errorCommit never call `setReason`; the reason survives by-construction.
- **WIRE-1 R4/R5 consumed by shape only** — no real network call; real wiring deferred to the composition root / Build & Test.
- **RoleGate cosmetic only** (AUTHZ-1 server-side is the real gate); **the UI non-blank reason guard is non-authoritative** (backend `_gate` is the single source of truth — CON-BR4).
- **No LLM. No TypeScript. tier-B corpus run NOT authorized. No other unit started.**
