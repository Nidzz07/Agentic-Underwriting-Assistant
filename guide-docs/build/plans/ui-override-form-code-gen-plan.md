# Code Generation — Plan (Part 1) — `ui-override-form` (U8)

**Stage**: BUILD → per-unit loop → Code Generation **Part 1 (Plan)** · **Unit**: U8 `ui-override-form` · C-cluster UI · Phase 1 · **Date**: 2026-07-09
**Story**: US-UI-5 (override-with-mandatory-reason) · **Requirements**: FR-UI-4 / FR-UI-3 (`data-testid`) / FR-UI-5 (no-TS) / **CON-BR4** (the human override gate — advisory-only + human-in-the-loop + mandatory reason).
**Built ON** the frozen FD (**BR-OVR-1..12**) + approved NFR Requirements (**twenty `NFR-OVR-*`**; dual-operation reason-carrying single-double; **NFR-OVR-Fold-A/1/2/3**) + approved NFR Design (patterns **P1–P12**; components **C1–C10**; **ND-OVR-Fold-i/ii/iii**) — **re-opening none**. **JS/JSX, NO TypeScript; Vitest + React Testing Library + jsdom** — mirroring the realized `ui-shell`/`ui-queue`/`ui-memo-view`/`ui-approval-gate` convention (`frontend/src/<unit>/` + `__tests__/`; shared `vitest.config.js` / `eslint.config.js` / `eslint-rules/`). Full-TDD, tests/lint-first, leaf-first. **This plan is the single source of truth for ui-override-form Code Generation.**

**Status**: **Part 2 COMPLETE (2026-07-09).** Eight `[Answer]` tags filled (Q1–Q8 all **A**, embedded below); mandatory ambiguity-check RUN → **CLEAN** (one consistency point resolved without a gap: the TESTID-1 `^override-[a-z]+(-[a-z0-9]+)+$` regex is the `queue`-family ≥3-segment form matching the plan's own `override-<element>-<purpose>` convention verbatim — every testid named 3-part). §3 Steps 0–12 executed leaf-first, tests-first; **all 13 checkboxes [x]**. **340 frontend tests pass** (89 files), **ESLint clean**, `src/overrideForm` **100% stmt/func/line · 98.36% branch** (QA-6 ≥90% PASSED; one intentionally-unreachable belt-and-suspenders branch flagged, `code/code-summary.md` §3). All four frozen trees still 100% (untouched); backend pytest 850/31 untouched. STOPPED at the standardized 2-option completion gate for the user's diff review — this is the last stage for ui-override-form.

---

## 0. Unit context

- **Story**: **US-UI-5** (the underwriter override-with-mandatory-reason gate) — the **second and final** UI **write path**, and the one that exercises the mandatory-reason gate.
- **Dependencies**: `ui-shell` (frozen U10) — imports `RoleGate`, `ReadOnlyRegion`, `RecommendationBadge`/`ConfidenceBadge`, `Panel`/`AppFrame`, `shell/copy` labels + `COMMIT_ACTION_LABELS.override` + the **one `FORBIDDEN_TERMS`**, `RoleContext`/`useCurrentRole`. `ui-queue` (frozen U5) + `ui-memo-view` (frozen U6) + **`ui-approval-gate` (frozen U7)** — their `fetchSeam`/`StructuralGuard`/by-construction/testid-lint are **mirrored as a convention, NOT imported** (incl. the **NEW `noApprovalGateImport`** requirement). **WIRE-1 R4 + R5** consumed **by shape** (mocked in tests via the injected dual-operation reason-carrying `overrideFetchSeam`).
- **Interfaces/contracts**: reads R4 `GET /applications/{application_id}/memo` → `MemoView` (recommendation context); writes R5 `POST /recommendations/{recommendation_id}/commit` with body `{ action: "override", reason }` → `CommittedDecision`; error envelope `{error:{code,message,detail?}}` per WIRE-1 §4. **Override with a mandatory reason** (`reason` a required positional in the builder; `underwriter_id` NOT in the body — session-derived).
- **Database entities owned**: **none** (the atomic write + audit tuple + the committed `reason` are audit-store's `DecisionCommitService`, server-side; this unit persists nothing).
- **Boundaries**: `RoleGate` is **cosmetic** (AUTHZ-1 is the server's real gate); the UI non-blank reason guard is **non-authoritative** (the backend `_gate` is the single source of truth — CON-BR4); **no approve path** (frozen U7); **no LLM**; **no real network**; **no persistence**.

## 1. Component → module map (production under `frontend/src/overrideForm/`)

| Comp | Module (file) | Exports / role | Backs |
|---|---|---|---|
| **C10** | `overrideForm/copy.js` | `OVERRIDE_COPY` — override-local UI strings, **advisory-clean (all 21 verified against the real detector, NFR-OVR-Fold-3)**; LINT-SUBJECT; not a domain-enum label source | COPY-1, ADVISORY-1 |
| **C2** | `overrideForm/overrideFetchSeam.js` | the own-local **dual-operation reason-carrying** seam: `createOverrideFetch(transport)` → `{ fetchContext(applicationId), submitOverride(recommendationId, reason) }` + `buildMemoRequest`/`buildOverrideRequest(recommendationId, reason)` (P4 **reason-required** signature) + `normalizeError`; **JSDoc contract** (Q5); duck-typed (ND-D-Fold); **mirrors sibling `fetchSeam`, NOT imported** | FETCH-1, BODY-1, RECOVERY-1, PERF-1 |
| **C4** | `overrideForm/components/RecommendationContext.jsx` | `{ recommendation, confidence, testid }` — **composes the frozen `ReadOnlyRegion`** + `RecommendationBadge`/`ConfidenceBadge`, engine-attributed (the recommendation being overridden) | NAMESPACE-1, COPY-1, TESTID-1 |
| **C5** | `overrideForm/components/OverrideReasonInput.jsx` | **`{ value, onChange, testid }` ONLY** (P9, CAPFREE-1) — a **controlled** `<textarea>`; **no seam reference**. **Carries the header comment** ("controlled textarea, `{ value, onChange }` only, no seam reference, holds text not a commit capability") — an explicit deliverable | REASONGATE-1, REASONKEEP-1, CAPFREE-1 |
| **C8** | `overrideForm/components/CommittedConfirmation.jsx` | **`{ decision, context, testid }` ONLY** (P6 / NFR-OVR-Fold-2) — renders the `CommittedDecision` echo (incl. the committed `reason`, sourced from `decision.reason` — **the echo, not the client slice**, ND-OVR-Fold-ii) + R4 context; **no seam reference**. **Carries the header comment** ("props `{decision, context}` only — no seam; renders the committed echo, cannot re-fetch") — an explicit deliverable | NOREFETCH-1, TESTID-1 |
| **C3** | `overrideForm/components/CommitStateView.jsx` | `{ state, error, onRetry, onBack, testid }` — `loading` / `pending` (no affordance / no reason input) / **`errorRead` + `errorCommit`** envelope render (four-status: `message`-visible / `code`-testid / `detail`-never; **409 dual-cause** under one code) | ERROR-1, FETCH-1(states), RECOVERY-1(render) |
| **C7** | `overrideForm/components/OverrideConfirmDialog.jsx` | **`{ onConfirm, onCancel, reason, testid }`** — the confirm step; its `Confirm` handler is the **single `submitOverride` call site** (via `onConfirm`, closing over the current reason); **echoes the `reason` read-only** (`override-confirm-reason-echo`); open/cancel a pure toggle (reason preserved). **Carries the header comment** ("SOLE commit-trigger holder; `onConfirm` is the single call site; echoes the reason read-only") — an explicit deliverable | NOFINAL-1, CONFIRM-1, CANCEL-1, REASONKEEP-1(echo) |
| **C6** | `overrideForm/components/OverrideAffordance.jsx` | **`{ onOverride, disabled, testid }` ONLY** (P1/P2) — the override button, wrapped in **`<RoleGate can="act">`**; `disabled` **derived from the single `isReasonPresent` predicate** (P2); `onClick` → `onOverride()` opens the dialog; **no `submitOverride`/seam/`onConfirm`**. **Carries the header comment** ("props `{onOverride, disabled}` only — no `submitOverride`/seam/`onConfirm`; opens the dialog, cannot commit; disabled derived from the one reason predicate") — an explicit deliverable | RBAC-1, NOFINAL-1, REASONGATE-1 |
| **C1** | `overrideForm/OverrideFormView.jsx` | the stateful owner: holds the injected `overrideFetchSeam` (**sole** holder), runs the initial R4 read, owns the machine (`loading→ready(idle)→confirming→submitting→{committed\|errorCommit}` + `pending` + `errorRead`) **and the independent `reason` slice** (P8 — Cancel/errorCommit never call `setReason`), computes the **single `isReasonPresent(reason)=reason.trim()!==''` predicate** (P2), and **wires `onConfirm` ONLY to `OverrideConfirmDialog`** (P1; the handler closes over the reason + optional belt-and-suspenders re-check, ND-OVR-Fold-i) | FETCH-1, REASONGATE-1, REASONKEEP-1, RECOVERY-1, all composition |
| **C9** | *(test-only)* `overrideForm/__tests__/*` + `eslint-rules/overrideForm.js` + shared-config extension (Q1) | the StructuralGuard substrate: scans + lints + detector self-tests, incl. the **single-call-site scan** (P1), the **capability-free import scans** (CAPFREE-1), the **NEW `noApprovalGateImport`**, and the **no-`createOverrideFetch`-import-in-presentational** guard | TESTID-1, NOTS-1, REFNOTOWN-1, NOFINAL-1(structural), CAPFREE-1(structural) |

**Tests** live in `frontend/src/overrideForm/__tests__/` (mirroring `shell`/`queue`/`memoView`/`approvalGate`). **No file under `frontend/src/shell/`, `frontend/src/queue/`, `frontend/src/memoView/`, or `frontend/src/approvalGate/` is created or modified.**

> **Header comments are explicit Code-Gen deliverables (not implicit)** — **C5, C6, C7, and C8** each ship a header comment (the frozen self-evidence convention) making the by-construction guarantee discoverable when reading the component in isolation. Called out here exactly as ui-approval-gate's plan called out the C5/C6/C7 header comments — and **extended to C5 `OverrideReasonInput`** (the new capability-free component with no U7 analog).

## 2. TDD test → `NFR-OVR-*` target map (every target at its NFR-pinned tier)

| Target | Test (file :: focus) | Tier |
|---|---|---|
| **NOFINAL-1** | `singleCallSite.test.js` (structural: `submitOverride` has exactly one call site — the confirm handler; **no seam import** in non-dialog components; mount/read/reason-typing/toggle issue no POST) + detector self-test | structural |
| **CONFIRM-1** *(teeth, full-highest)* | `overrideForm.confirm.test.jsx` (dual-op double, Q2): with a non-blank reason, `Override`-click → **`submitOverride.calls.length===0` AND `fetchContext.calls.length===1`** (Fold-A cross-guard); only `Confirm` → `===1` | component (teeth) |
| **CANCEL-1** *(teeth, full-highest)* | `overrideForm.cancel.test.jsx`: type reason → `Override`→open→`Cancel` → **both** ops' counts unchanged; context identical; state `ready(idle)`; **reason preserved** | component (teeth) |
| **REASONGATE-1** *(teeth, full-highest — NEW)* | `overrideForm.reasongate.test.jsx` (Q3 fixtures): each blank in `BLANK_REASONS` keeps the affordance `disabled` and the full `Override→Confirm` attempt yields **0** `submitOverride`; a non-blank control → **exactly 1** POST carrying the reason **verbatim/as-entered**; + `reasonTrimDivergence.test.js` (documents `trim()` vs `str.strip()` non-byte-identity, FD-OVR-Fold-1 — **not** a byte-equality claim) | component (teeth) + unit (doc) |
| **RBAC-1** | `overrideForm.rbac.test.jsx` (stub `RoleProvider` **all three roles + null**: `underwriter`→affordance present; `auditor`/`admin`/`null`→absent) + `noBackendImport.test.js` + no-authz-call structural | component + structural |
| **BODY-1** | `overrideFetchSeam.test.js` (`buildOverrideRequest(recId, reason)` body **deep-equals** `{action:'override', reason}` — has `action`+`reason`, **no** `underwriter_id`; `recommendation_id` in path; method POST; `reason` sent as-entered) | unit |
| **ERROR-1** | `overrideForm.error.test.jsx` (table-driven, Q4: **200**→committed / **403**→not-permitted / **409**→conflict **for BOTH already-committed and blank-reason-race under one code** / **400 & 422**→generic; `override-error-message` visible, `override-error-code` hidden testid, `detail` absent from DOM) | component (table-driven) |
| **NOREFETCH-1** *(teeth)* | `overrideForm.norefetch.test.jsx`: after a successful override, **both** `fetchContext.calls.length` and `submitOverride.calls.length` unchanged (`1`,`1`); confirmation shows `action=override` + the committed `reason` (**from `decision.reason`**) + context | component (teeth) |
| **RECOVERY-1** *(two-directional teeth)* | `overrideForm.recovery.test.jsx`: (a) `errorRead` Retry → exactly one further `fetchContext`, recorded arg `===X`; (b) `errorCommit` → `ready(idle)`, `submitOverride.calls.length` stays `1`, **reason preserved** | component (teeth) |
| **REASONKEEP-1** *(two distinct assertions — NEW)* | `overrideForm.reasonkeep.test.jsx` (Q6): (a) preservation teeth — reason survives `Cancel` **and** `errorCommit` unchanged; (b) dedicated read-only echo DOM assertion — `override-confirm-reason-echo` renders the current reason read-only, **distinct** from the committed display node | component |
| **CAPFREE-1** *(structural + prop-contract — NEW)* | `capabilityFree.imports.test.js` (structural: `OverrideReasonInput`/`OverrideAffordance` import no seam module + reference no `submitOverride`) + `overrideReasonInput.test.jsx` (prop-contract RTL: renders from `{value,onChange}` alone; typing calls `onChange`) + detector self-tests | structural + component |
| **FETCH-1** | `overrideForm.state.test.jsx` (per-state renders: loading/pending/ready(idle)/confirming/submitting/committed/errorRead/errorCommit) + `overrideForm.transition.test.jsx` (**one consolidated transition test**, Q7, all legs incl. **both** recovery paths + the reason-carrying states) — all on the **single dual-op reason-carrying double** (Fold-A) | component (RTL) |
| **COPY-1** | `eslint.override.rules.test.js` (no-inline-label RuleTester, **reuses** ui-shell `FORBIDDEN_TERMS`) + `recommendationContext.test.jsx` (label look-up) + detector self-test | lint (+ RTL) |
| **ADVISORY-1** | `eslint.override.rules.test.js` (advisory-vocabulary RuleTester over `src/overrideForm/**` static code, **UNMODIFIED**; `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS`; the already-verified-clean `OVERRIDE_COPY` consumed verbatim, Q8) + synthetic self-test | lint / structural |
| **NAMESPACE-1** | `namespace.test.jsx` (the human `override` label from `COMMIT_ACTION_LABELS.override`, never a `RECOMMENDATION_LABELS` value — esp. never `DECLINE-RECOMMEND`; **collision guard** over the reused `FORBIDDEN_TERMS`) + self-test | structural |
| **TESTID-1** | `eslint.override.rules.test.js` (override-testid-convention `^override-[a-z]+(-[a-z0-9]+)+$`) + `testid.test.jsx` presence (incl. the **distinct** `override-confirm-reason-echo` vs `override-committed-reason`, Q6) + `isValidOverrideTestid` self-test | lint / component |
| **NOTS-1** | `nots.test.js` (0 `.ts`/`.tsx` under `src/overrideForm`; predicate self-test) | structural |
| **REFNOTOWN-1** | `noBackendImport.test.js` + `noUiQueueImport.test.js` + `noMemoViewImport.test.js` + **`noApprovalGateImport.test.js`** (NEW) + `noRouterImport.test.js` + **`noCreateOverrideFetchImportInPresentational.test.js`** — each with a detector self-test | structural |
| **PERF-1** | `boundedFetch.test.js` (structural: R4 one resource by `applicationId` + R5 one commit by `recommendationId`; no list/all-rows path) — observed, non-gating | structural + observed |
| **A11Y-1** | recorded/observed — semantic markup + focusable `Override`/`Confirm`/`Cancel`/`Retry` + the reason `<textarea>` label association; confirm-dialog focus-trap/Escape **recorded** NFR-Design→Code-Gen target, **non-gating** | observed / soft |
| **SCOPE-1** | governance/exclusion — no test imports a backend module, `ui-queue`, `ui-memo-view`, `ui-approval-gate`, or exercises the real R4/R5 wire | N/A |

Every `NFR-OVR-*` target mapped; no orphan. No test imports a backend module, a sibling UI unit, or hits the real network.

## 3. Leaf-first build order (numbered Part-2 steps — NOT executed; on the user's explicit go)

- [x] **Step 0 — Scaffold + shared-config extension (Q1)**: create `frontend/src/overrideForm/` tree + `overrideForm/copy.js`; extend the **shared** `vitest.config.js` (`include` + `coverage.include` add `src/overrideForm`; **thresholds unchanged**) + register the reused lints + a **new `override-testid-convention` rule** (`eslint-rules/overrideForm.js`) for `src/overrideForm` in `eslint.config.js` — **no file under `src/shell/`, `src/queue/`, `src/memoView/`, or `src/approvalGate/` touched**.
- [x] **Step 1 — C10 `copy.js`**: `OVERRIDE_COPY`, **advisory-clean** (Fold-3, already verified — consumed verbatim, Q8). (COPY-1/ADVISORY-1)
- [x] **Step 2 — C2 `overrideFetchSeam.js`**: the **dual-operation reason-carrying** seam + `buildMemoRequest`/`buildOverrideRequest(recommendationId, reason)` (**reason-required**) + `normalizeError` + **JSDoc contract** (Q5). (FETCH-1, BODY-1, RECOVERY-1, PERF-1)
- [x] **Step 3 — C4 `RecommendationContext.jsx`**: read-only rec/conf via frozen `ReadOnlyRegion` + badges. (NAMESPACE-1, COPY-1)
- [x] **Step 4 — C5 `OverrideReasonInput.jsx`**: controlled `{value, onChange}`-only + **header comment**; no seam. (REASONGATE-1 input, REASONKEEP-1, CAPFREE-1)
- [x] **Step 5 — C8 `CommittedConfirmation.jsx`**: props-only `{decision, context}` + **header comment**; no seam; reason from `decision.reason` (echo, not the client slice). (NOREFETCH-1)
- [x] **Step 6 — C3 `CommitStateView.jsx`**: loading / pending / four-status `errorRead`/`errorCommit` render (409 dual-cause). (ERROR-1, FETCH-1 states)
- [x] **Step 7 — C7 `OverrideConfirmDialog.jsx`**: sole `onConfirm` holder + reason read-only echo + **header comment**; open/cancel pure toggle (reason preserved). (CONFIRM-1/CANCEL-1/REASONKEEP-1 echo)
- [x] **Step 8 — C6 `OverrideAffordance.jsx`**: `RoleGate can="act"`-wrapped, `{onOverride, disabled}`-only (disabled **derived from the single predicate**) + **header comment**; no commit capability. (RBAC-1, REASONGATE-1)
- [x] **Step 9 — C1 `OverrideFormView.jsx`**: composes C2–C8, owns the machine **and the independent reason slice** (Cancel/errorCommit never `setReason`), computes the **single `isReasonPresent` predicate**, **wires `onConfirm` ONLY to C7** (closing over the reason + optional belt-and-suspenders re-check); the CONFIRM/CANCEL/REASONGATE/NOREFETCH/RECOVERY/REASONKEEP teeth on the dual-op reason-carrying double. (FETCH-1, all teeth)
- [x] **Step 10 — C9 StructuralGuard**: single-call-site scan (NOFINAL-1), capability-free import scans (CAPFREE-1), no-backend/`ui-queue`/`ui-memo-view`/**`ui-approval-gate`**/router import, **no-`createOverrideFetch`-import-in-presentational**, no-TS, bounded-fetch, testid convention, `FORBIDDEN_TERMS` reuse — each with a detector self-test. (NOFINAL-1, CAPFREE-1, TESTID-1, NOTS-1, REFNOTOWN-1)
- [x] **Step 11 — Coverage / quality gate**: Vitest run; `src/overrideForm` meets **QA-6 ≥ 90%**; `src/shell` + `src/queue` + `src/memoView` + `src/approvalGate` stay **100%** (untouched); ESLint clean; backend pytest **850/31 untouched**.
- [x] **Step 12 — Code summary**: `guide-docs/build/ui-override-form/code/code-summary.md` written; `testresults.txt` refreshed.

## 4. HOLDS restated (binding through Part 2)

- **ui-shell (frozen) untouched** — `RoleGate` / `ReadOnlyRegion` / badges / `shell/copy` + `COMMIT_ACTION_LABELS.override` + `FORBIDDEN_TERMS` / `RoleContext`/`useCurrentRole` **reused via import only, never modified**; **no file under `frontend/src/shell/` created or edited**.
- **ui-queue + ui-memo-view + ui-approval-gate (all frozen) untouched** — their `fetchSeam`/`StructuralGuard`/by-construction patterns are **mirrored, never imported**; **no file under `frontend/src/queue/`, `frontend/src/memoView/`, or `frontend/src/approvalGate/` created or edited** (REFNOTOWN-1 enforces `noUiQueueImport`/`noMemoViewImport`/**`noApprovalGateImport`**).
- **No local `FORBIDDEN_TERMS` word-list** — the unit reuses the **one** source (COPY-1/ADVISORY-1/NAMESPACE-1); `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS`. The `advisory-vocabulary` lint applies **UNMODIFIED** (Fold-3; the `OVERRIDE_COPY` is already verified clean — no copy change).
- **The by-construction guarantees are HARD Code-Gen requirements, not optional**, each with its header comment: **C5** `{value, onChange}`-only props (no seam) · **C6** `{onOverride, disabled}`-only props (no `submitOverride`/seam; `disabled` **derived from the single predicate**) · **C7** the sole `onConfirm` holder / single call site + reason echo · **C8** `{decision, context}`-only props (no seam) · **C2** `buildOverrideRequest(recommendationId, reason)` **reason-required** signature (structurally cannot omit `reason`; no `underwriter_id`). Enforced by teeth + StructuralGuard scans.
- **The reason state slice is structurally independent of the phase slice** (P8) — `Cancel`/`errorCommit` transitions **never call `setReason`**; the reason survives by-construction.
- **WIRE-1 R4/R5 consumed by shape only** — no real network call in the unit or its tests; **real `overrideFetchSeam` wiring + R4/R5 route implementation deferred to the composition root / Build & Test**.
- **`RoleGate` is cosmetic** (AUTHZ-1 is the server's real gate); **the UI non-blank reason guard is non-authoritative** (the backend `_gate` is the single source of truth — CON-BR4).
- **No LLM. No TypeScript** (NOTS-1). **tier-B run stays unauthorized and out of scope. No other unit started.**

## 5. Coverage / quality gate (frontend Vitest — NOT the Python pytest suite)

- **Runner**: JS/React unit → **Vitest coverage folded into the frontend test run**, the established convention — **NOT** the backend `pytest --cov=backend/*` suite.
- **Baseline (from `ui-approval-gate` completion)**: `frontend/src/shell` = **100%**, `frontend/src/queue` = **100%**, `frontend/src/memoView` = **100%**, `frontend/src/approvalGate` = **100%** (frontend total **852/852 stmts, 100%**). ui-override-form adds `src/overrideForm` coverage; **none of the four existing trees may regress** (no file in any is touched, so all four stand) and `src/overrideForm` must meet **QA-6 ≥ 90%**.
- **Backend untouched (confirm)**: this is a pure frontend addition — the backend **pytest suite (850 passed / 31 skipped**, unchanged) must remain **completely untouched** (zero backend files modified; separate runner/tree). `testresults.txt` records the frontend result **alongside**, not merged.

## 6. Open Code-Gen-only questions (`[Answer]` tags — LEFT BLANK; lettered; full text below)

> Fill these; I then run the ambiguity-check (§6.5), then Part 2 (§3 Steps 0–12) **on your explicit go**. Per the standing convention the full Q&A is re-embedded here once answered.

### Q1 — Shared frontend config extension (coverage scope + lint registration) without touching frozen src
- **A.** **Extend the shared frontend config** — add `src/overrideForm` to `vitest.config.js` `include` + `coverage.include`, and register the reused `no-inline-label` + `advisory-vocabulary` lints + a **new `override-testid-convention` rule** (`eslint-rules/overrideForm.js`, mirroring `eslint-rules/approvalGate.js`) for `src/overrideForm` in `eslint.config.js`. **No file under `src/shell/`, `src/queue/`, `src/memoView/`, or `src/approvalGate/` modified; `vitest.config.js` thresholds unchanged** — all four frozen coverage gates stand. *(Recommended — consistent with the single frontend run.)*
- **B.** **overrideForm-scoped config** (separate Vitest project / ESLint override) leaving the shared config untouched.

`[Answer]:` A

### Q2 — Dual-operation reason-carrying capturing double construction (proving the independent-counting guarantee, Fold-A)
- **A.** **A shared `makeOverrideDouble()` factory** (in `overrideForm/__tests__/fixtures.js`) returning a **single object `{ fetchContext, submitOverride }`** where each operation is an **independently-counted spy** (its own `calls` array of recorded args — `submitOverride.calls[i]` records **`[recommendationId, reason]`** so the reason is inspectable); programmable per operation (`fetchContext` resolves `MemoView` / rejects an envelope; `submitOverride` resolves `CommittedDecision` / rejects an envelope; sequenceable for RECOVERY-1's fail-then-succeed). Teeth read `double.fetchContext.calls.length` / `double.submitOverride.calls.length` (the cross-guard: `0` vs `1`) and `double.submitOverride.calls[0]` (the reason). **One construction reused across all teeth tests** (mirrors the sibling single-double Fold). *(Recommended.)*
- **B.** **Two separate injected doubles** (one per operation) — diverges from the single-double convention.
- **C.** **Inline per-test spies** in each test file.

`[Answer]:` A

### Q3 — REASONGATE-1 whitespace-fixture literal construction (the NEW load-bearing teeth)
- **A.** **A shared named fixture set** (in `fixtures.js`): **`BLANK_REASONS = ['', ' ', '\t', '\n', ' \t\n ']`** (empty, space, tab, newline, mixed — each must keep the affordance `disabled` and yield **0** `submitOverride`), plus **`NONBLANK_REASON = ' I disagree because X '`** (surrounding spaces around content — proves the payload is sent **as-entered/untrimmed**, exactly one POST with the reason verbatim). The blank cases drive the full `Override→Confirm` attempt (not merely asserting the `disabled` attribute), so a broken predicate→`disabled` wiring is caught. Plus a separate **`reasonTrimDivergence.test.js`** asserting the guard is `String.prototype.trim()`-based and **not** byte-identical to Python `str.strip()` (FD-OVR-Fold-1) — **not** a hard byte-equality claim. *(Recommended.)*
- **B.** **Inline whitespace literals** per test.
- **C.** **A full Unicode-whitespace matrix** (incl. U+001C–U+001F / U+0085 / U+FEFF) at the UI. *(Rejected — over-build against the non-authoritative design; the divergence is documented, not UI-exhaustively-tested.)*

`[Answer]:` A

### Q4 — ERROR-1 four-status fixture construction (dual-cause 409)
- **A.** **A shared named envelope-fixtures set** (in `fixtures.js`): a success `CommittedDecision` (200) + `forbiddenEnvelope` (403) / `conflictEnvelope` (409) / `invalidEnvelope` (400) / `unprocessableEnvelope` (422), each a well-formed `{error:{code,message,detail}}`; driven **table-style** `[{status, programmed, expectedTestid}]`. The **409 `conflictEnvelope` is reused for BOTH** the already-committed and the blank-reason-race cases (same `commit_conflict` code, one rendered state — no special-casing beyond copy). *(Recommended — DRY, table-driven.)*
- **B.** **Inline per-status** fixtures in the error test file.

`[Answer]:` A

### Q5 — `overrideFetchSeam` JSDoc contract wording (the two operations, incl. the reason parameter)
- **A.** **A JSDoc block on `createOverrideFetch`** documenting **both** operations: `fetchContext(applicationId)` → resolves the `MemoView` body / rejects a normalized `{error:{code,message,detail}}` envelope; **`submitOverride(recommendationId, reason)`** → POSTs `{action:'override', reason}` (reason **as-entered**) → resolves `CommittedDecision` / rejects the normalized envelope; **duck-typed, no formal interface** (ND-D-Fold); `normalizeError` produces the **WIRE-1 §4 shape** (own-local, **not imported** from a sibling). The `reason` parameter is documented as **required + sent verbatim** (non-blankness is the orchestrator's gate, not the seam's). *(Recommended — self-documenting; the dual-op double is the worked example.)*
- **B.** **A minimal one-line comment** per export.

`[Answer]:` A

### Q6 — testid naming for the confirm-echo vs committed-reason display nodes (keep unambiguously distinct)
- **A.** **Two distinct namespaced testids** — **`override-confirm-reason-echo`** (pre-submission, inside `OverrideConfirmDialog`, sourced from the **client `reason` state**, read-only) vs **`override-committed-reason`** (post-submission, inside `CommittedConfirmation`, sourced from **`decision.reason`** — the R5 echo). Both follow the `override-<element>-<purpose>` convention; a TESTID-1/REASONKEEP-1 assertion confirms **both exist and are distinct**, so a test never conflates the two states/sources (ND-OVR-Fold-ii). *(Recommended.)*
- **B.** **A single shared testid** reused in both the confirm dialog and the committed confirmation. *(Rejected — conflates two distinct states/sources; a preservation regression and an echo regression would be indistinguishable.)*

`[Answer]:` A

### Q7 — Consolidated state-transition test file location (mirroring the sibling convention)
- **A.** Its **own file** `overrideForm.transition.test.jsx`, alongside the per-state `overrideForm.state.test.jsx`. *(Recommended — one-file-per-concern, matches ui-shell/ui-queue/ui-memo-view/ui-approval-gate.)*
- **B.** In the **same file** as the per-state tests.

`[Answer]:` A

### Q8 — Confirm-dialog / committed markup wording verification against the already-verified-clean `OVERRIDE_COPY`
- **A.** **Use the `OVERRIDE_COPY` strings verbatim** (from `domain-entities.md §3` — already audited **clean** against the real `FORBIDDEN_TERMS` detector, NFR-OVR-Fold-3: `confirmBody` = "You are about to override this recommendation. Your override and reason will be recorded.", `committedTitle` = "Override recorded", `reasonPromptLabel`, `confirmReasonHeading`, `committedReasonHeading`, etc.); the **unmodified `advisory-vocabulary` lint** is the build-failing enforcement; a detector self-test confirms non-vacuity. *(Recommended — the copy is already clean at the FD source; Code-Gen consumes it verbatim, no re-draft.)*
- **B.** **Re-draft** the confirm/committed copy at Code-Gen.

`[Answer]:` A

---

## 7. Gate
**Part 2 COMPLETE — stopped at the standardized 2-option completion gate.** The eight `[Answer]` tags (Q1–Q8 all **A**) are embedded above; the mandatory ambiguity-check ran **CLEAN** (no genuine gap); §3 Steps 0–12 executed leaf-first / tests-first with all 13 checkboxes **[x]**. **340 frontend tests pass**, ESLint clean, `src/overrideForm` **100% stmt/func/line · 98.36% branch** (QA-6 ≥90% PASSED — one flagged intentionally-unreachable belt-and-suspenders branch). Deliverables written: `code/code-summary.md`, refreshed `testresults.txt`, back-annotated `guide-state.md`, appended `audit.md`. **This is the last stage for ui-override-form** — awaiting the user's diff review before approval. WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate (all frozen) untouched; no file under any frozen `src/` tree created or edited; backend pytest 850/31 untouched; tier-B corpus run NOT authorized; no other unit started.
