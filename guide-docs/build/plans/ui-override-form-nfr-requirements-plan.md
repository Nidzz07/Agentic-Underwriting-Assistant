# NFR Requirements Part 1 (Plan) — `ui-override-form` (U8)

**Stage**: BUILD → per-unit loop → NFR Requirements → Part 1 (Planning)
**Unit**: `ui-override-form` (U8) · C-cluster UI · Phase 1 · **Depth**: **COMPREHENSIVE** (consistent with the FD depth decision — the **second and final write-path UI unit**, the one that exercises the **mandatory-reason gate**)
**Date**: 2026-07-09
**Status**: **Part 1 plan — ANSWERED (Q1–Q4 all A) · ambiguity-check CLEAN (three folds, all VERIFIED on disk) · Part 2 GENERATED.** The four `[Answer]` tags are embedded (§3). Ambiguity-check run against the four answers + the frozen FD — no genuine gap → three clarity-folds (§3A). Part 2 (`nfr-requirements.md` + `tech-stack-decisions.md`) generated under `guide-docs/build/ui-override-form/nfr-requirements/`. WIRE-1 / ui-shell / ui-queue / ui-memo-view / ui-approval-gate (all frozen) untouched; tier-B NOT authorized; no other unit started. **STOPPED at the NFR-Requirements 2-option completion gate.**

**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md` — **BR-OVR-1..12**, the component/prop inventory incl. the **capability-free `OverrideReasonInput`**, the full client state machine **including reason preservation across cancel/error**, the **two-server-gate** (authz AUTHZ-1 + reason BR-COMMIT-GATE) defense-in-depth structural note) — **re-opening none of it**. Each `NFR-OVR-*` target is a **pass/fail testable assertion** traced to its FD rule.

**Tier convention inherited from `ui-shell` (frozen U10), applied by `ui-queue` (U5), `ui-memo-view` (U6), and `ui-approval-gate` (U7)**: Vitest + React Testing Library + jsdom · ESLint over the **single** `FORBIDDEN_TERMS` source · file/import structural scans · detector self-tests (non-vacuous). **Advisory-only; no LLM; no live backend** — WIRE-1 **R4 and R5** are exercised through a **single injected/capturing dual-operation double** (see §0), mirroring U7's NFR-AG-Fold-1. No frozen mechanism is modified or imported from a sibling (incl. frozen `ui-approval-gate`); sibling `fetchSeam`/`StructuralGuard`/by-construction conventions are **mirrored**, not imported.

---

## 0. Central testability principle — the dual-operation seam (reason-carrying)

`ui-override-form`'s properties are testable **without a running backend**. Like U7, its `overrideFetchSeam` has **two** operations: `fetchContext` (R4 read) **and** `submitOverride` (R5 write) — but `submitOverride(recommendationId, reason)` now carries a **second argument** (the mandatory reason). The **load-bearing** targets are behavioral **teeth** that count transport calls per operation **and** inspect the recorded `reason` argument:

- **Commit-only-on-Confirm** (BR-OVR-1/2/3): assert **zero** `submitOverride` calls across `mount → type reason → Override-click → open dialog → Cancel`, and **exactly one** `submitOverride` call **only** on `Confirm`.
- **Mandatory non-blank reason** (BR-OVR-8, the NEW load-bearing target): assert **zero** `submitOverride` calls while the reason is blank/whitespace-only, and **exactly one** call carrying the entered `reason` on `Confirm` when non-blank; **document** (not byte-assert) the `trim()` vs `str.strip()` divergence per FD-OVR-Fold-1.
- **No re-fetch after commit** (BR-OVR-9): assert **zero** further transport calls (both operations) after a successful commit; the echo includes the committed `reason`.
- **Cause-differentiated recovery** (BR-OVR-11): assert an `errorRead` `Retry` re-issues **exactly one** R4 `fetchContext` for the same `applicationId`; an `errorCommit` returns to `ready(idle)` with **zero** automatic `submitOverride` — and the reason is **preserved** (BR-OVR-12).

The double follows U7's resolved shape (**mirrored, not imported**): a **single injected seam object** `{ fetchContext, submitOverride }`, each an **independently-counted spy** recording its own call count **and args** (so the `reason` argument is inspectable). The genuinely-new NFR-tier questions this unit raises are the **capability-free verification of the new `OverrideReasonInput`** (§3 Q2), the **whitespace-variant coverage of the blank-reason teeth** (§3 Q3), and the **reason-echo assertion structure** (§3 Q4).

Four test modalities (mirroring the sibling §0):
1. **Build-failing lints + structural scans** — COPY-1 / ADVISORY-1 / NAMESPACE-1 reuse ui-shell's ESLint + the **one** `FORBIDDEN_TERMS` source (never a second word-list); NOTS-1 / RBAC-1(structural) / REFNOTOWN-1 / CAPFREE-1 / NOFINAL-1(scan) are file/import/render scans; each detector carries a **self-test**.
2. **Component-render + interaction assertions (RTL + jsdom)** — CONFIRM-1, CANCEL-1, REASONGATE-1, REASONKEEP-1, ERROR-1, RBAC-1(render, stub `RoleProvider`), FETCH-1's per-state renders.
3. **Dual-operation capturing-double assertions** — the transport-call-count teeth (CONFIRM-1, CANCEL-1, REASONGATE-1, NOREFETCH-1, RECOVERY-1) + BODY-1's recorded request body (incl. `reason`) + RECOVERY-1's recorded `applicationId`.
4. **Observed/soft** — PERF-1 (bounded R4 + single R5, non-gating) and A11Y-1 (semantic + focusable override/confirm/cancel/retry + the reason `<textarea>` label association, recorded target).

**Scope**: the `NFR-OVR-*` set tests **only** `ui-override-form`'s own behavior — not other UI units, not any backend unit's internals, not the WIRE-1 route implementation (R5/R4 impl → Build & Test). It **reuses** ui-shell's frozen mechanisms (copy / `FORBIDDEN_TERMS` / ESLint / `RoleGate` / `ReadOnlyRegion` / badges / `COMMIT_ACTION_LABELS.override` / testid convention) and **mirrors** the sibling fetchSeam/StructuralGuard/by-construction convention **without modifying or importing** any sibling (incl. frozen `ui-approval-gate`).

---

## 1. Draft `NFR-OVR-*` target map (BR-OVR-1..12 → pass/fail target; no orphan)

### FULL RIGOR — the commit-lifecycle teeth (load-bearing)

- **NFR-OVR-NOFINAL-1** (BR-OVR-1) — **no client finalize.** Structural: the **only** call site of `submitOverride` is the `OverrideConfirmDialog` `Confirm` handler; mount/read/reason-typing/`confirming`-toggle issue no R5 POST. Scan asserts **no invocation + no seam import** in the non-dialog components (reusing U7's NOFINAL **scan refinement** — invocation/import scan, not a bare-word textual scan, since header comments legitimately name `submitOverride` to document its absence). **Teeth** shared with CONFIRM-1. *Tier*: structural + component. *Rigor*: full.
- **NFR-OVR-CONFIRM-1** (BR-OVR-2) — **confirm-before-commit teeth.** RTL on the dual-operation double: with a non-blank reason, `Override`-click transitions to `confirming` and produces **zero** `submitOverride` calls; **only** the dialog `Confirm` produces **exactly one** R5 POST. *Tier*: component (teeth). *Rigor*: **full (highest)**.
- **NFR-OVR-CANCEL-1** (BR-OVR-3) — **cancelable-without-side-effect teeth.** RTL: type reason → `Override` → open → `Cancel`; assert **zero** calls on **both** operations across open+cancel, the rendered context is identical before/after, the state returns to `ready(idle)`, and **the reason is preserved** (cross-ref BR-OVR-12). *Tier*: component (teeth). *Rigor*: **full (highest)**.

### FULL RIGOR — the NEW mandatory-reason target (load-bearing)

- **NFR-OVR-REASONGATE-1** (BR-OVR-8) — **mandatory non-blank reason teeth (the genuinely new load-bearing target).** RTL + double: (a) while the reason is blank/whitespace-only, the `Override → confirm → submit` path is disabled and **zero** `submitOverride` calls occur; (b) with a non-blank reason, exactly **one** `submitOverride` call carrying that `reason` on `Confirm`; (c) an explicit **documentation test** asserting the UI guard is `String.prototype.trim()`-based and **NOT** claimed byte-identical to the backend `str.strip()` (citing FD-OVR-Fold-1) — the guard is **non-authoritative**, the backend `_gate` is the single source of truth. **Whitespace-variant coverage → Q3.** *Tier*: component (teeth) + unit (doc). *Rigor*: **full (highest)**.

### FULL RIGOR — authorization-adjacent + write-shape

- **NFR-OVR-RBAC-1** (BR-OVR-4) — **RoleGate cosmetic-only.** (a) **structural** — no backend import, no authz-function call in `frontend/src/overrideForm/` (StructuralGuard scan + detector self-test); (b) **RTL** stub `RoleProvider` render coverage (inheriting U7 Q3-A — **all three roles + null**): `underwriter` sees the affordance; `auditor` / `admin` / `null` see the fallback. *Tier*: structural + component. *Rigor*: full.
- **NFR-OVR-BODY-1** (BR-OVR-5) — **session-derived committer + reason inclusion.** Unit test on `buildOverrideRequest(recommendationId, reason)`: the request body **deep-equals** `{ action: 'override', reason }` (has `action` + `reason`, **no** `underwriter_id` key); the path contains the R4-supplied `recommendation_id`. *Tier*: unit. *Rigor*: full.
- **NFR-OVR-ERROR-1** (BR-OVR-6) — **per-status surfacing.** Table-driven RTL across the documented statuses (**200 → committed**; **403 → not-permitted**; **409 → conflict** — covering **both** already-committed **and** the blank-reason race/bypass tail **under the one `commit_conflict` code**; **400 & 422 → generic invalid**), each programmed on the double; envelope discipline: `message` VISIBLE, `code` in a `hidden` testid node, `detail` NEVER in the DOM. *Tier*: component (table-driven). *Rigor*: full.
- **NFR-OVR-NOREFETCH-1** (BR-OVR-9) — **confirmation without re-fetch teeth.** RTL: after a successful override, the confirmation shows `action=override` + the committed `reason` + `recommendation_id` + `underwriter_id` (echo) + the recommendation value (R4 context in hand), while **both** operations on the double receive **zero** further calls. *Tier*: component (teeth). *Rigor*: full.
- **NFR-OVR-REFNOTOWN-1** (BR-OVR-10) — **reference-not-own.** StructuralGuard scans (mirroring the sibling convention, each non-vacuous): `noBackendImport`, `noUiQueueImport`, `noMemoViewImport`, **`noApprovalGateImport`** (NEW — the first sibling unit that must also not import the frozen U7), `noRouterImport`. *Tier*: structural. *Rigor*: full.
- **NFR-OVR-RECOVERY-1** (BR-OVR-11) — **cause-differentiated recovery teeth.** RTL two-directional: (a) an `errorRead` `Retry` click re-issues **exactly one** `fetchContext` for the **same** `applicationId`; (b) an `errorCommit` transitions to `ready(idle)` with **zero** automatic `submitOverride` follow-ups **and the reason preserved**, requiring a fresh `Override → Confirm` cycle. *Tier*: component (teeth). *Rigor*: full.
- **NFR-OVR-REASONKEEP-1** (BR-OVR-12) — **reason preservation + echo (the NEW target).** Teeth: the entered `reason` survives a `Cancel` and an `errorCommit` transition **unchanged**; and the confirm dialog renders the current `reason` as a **read-only echo** before submission. **Echo-assertion structure → Q4.** *Tier*: component. *Rigor*: full.
- **NFR-OVR-CAPFREE-1** (BR-OVR-3/Q3-A by-construction) — **capability-free components scan (extends U7's ND-Fold-3).** Structural + prop-contract: `OverrideAffordance` holds only `onOverride` (no seam import, no `submitOverride` reference); **`OverrideReasonInput` holds only `{ value, onChange }` and imports no seam** (the NEW capability-free component); `CommittedConfirmation` is `{ decision, context }`-only; the single `submitOverride` call site is `OverrideConfirmDialog`. **Verification structure → Q2.** *Tier*: structural + component. *Rigor*: full.
- **NFR-OVR-FETCH-1** (state-machine addendum) — **dual-operation seam + full state machine.** (a) the seam is **injected as a prop** (never a hard-wired fetch); (b) per-state renders — `loading`, `pending` (no affordance / no reason input), `ready(idle)` (context + reason input), `confirming` (reason echoed), `submitting`, `committed`, `errorRead`, `errorCommit`; (c) a **consolidated** transition test covering all legs incl. both split-error recovery paths **and the reason-carrying states** (mirroring U7 Q5-A's one-consolidated-test). *Tier*: component. *Rigor*: full.

### FULL RIGOR — inherited conventions

- **NFR-OVR-COPY-1** (reused ui-shell COPY convention) — **no inlined display label.** No Recommendation/Confidence/CommitAction label literal in `frontend/src/overrideForm/`; badges + `COMMIT_ACTION_LABELS.override` render by **value look-up** from `shell/copy`; chrome lives in the override-local copy module. Build-failing `no-inline-label` ESLint (ui-shell mechanism) + detector self-test. *Tier*: lint. *Rigor*: full.
- **NFR-OVR-ADVISORY-1** (advisory-only naming facet of BR-OVR-1/7) — **reuse the ONE advisory-vocabulary lint UNMODIFIED.** The ui-shell `advisory-vocabulary` lint is registered on `src/overrideForm/**` (a config block mirroring the sibling; no `src/shell` edit, no new word-list); this unit's **static copy** (`OVERRIDE_COPY`) contains no forbidden system-output token (`DECLINE`/`decision`/`approved`/`declined`) and never renders the human `override` as the system `DECLINE-RECOMMEND`. *(Preliminary: the FD `OVERRIDE_COPY` draft already reads clean — "override"/"reason"/"record"/"committed"/"recommendation" — so, unlike U7's `confirmBody`, no `decision`-token collision is anticipated; confirmed at the ambiguity-check.)* *Tier*: lint. *Rigor*: full.
- **NFR-OVR-TESTID-1** (reused testid convention) — every assertion-relevant element carries a stable `override-<element>-<purpose>` `data-testid` (incl. the reason input and the reason echo); a convention lint/test (mirroring the sibling) + detector self-test (non-vacuous). *Tier*: lint / component. *Rigor*: full.
- **NFR-OVR-NOTS-1** (FR-UI-5) — `frontend/src/overrideForm/` is plain JS/JSX; a file-scan finds **zero** `.ts`/`.tsx` and no `tsconfig*.json`. *Tier*: structural. *Rigor*: full.

### MEDIUM RIGOR

- **NFR-OVR-NAMESPACE-1** (BR-OVR-7) — **namespace-distinctness (override ≠ DECLINE-RECOMMEND).** Reuse the `FORBIDDEN_TERMS` collision guard + `COMMIT_ACTION_LABELS.override` (mirroring the sibling NAMESPACE-1): the human `override` (lowercase `CommitAction`) is never rendered as, serialized as, or conflated with the system `DECLINE-RECOMMEND` (uppercase `Recommendation`); assert `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS` (single source); detector self-test. *Tier*: structural. *Rigor*: medium.

### SOFT / OBSERVED

- **NFR-OVR-PERF-1** — bounded: R4 fetches one resource by `applicationId`, R5 posts one override; no list/all-rows path (structural bounding, mirroring the sibling `boundedFetch` scan). Latency/bundle observed, non-gating. *Tier*: structural + observed. *Rigor*: soft.
- **NFR-OVR-A11Y-1** — semantic markup + focusable `Override`/`Confirm`/`Cancel`/`Retry`; the reason `<textarea>` has an associated label; the confirm dialog's focus/keyboard behavior. Soft, consistent with the sibling precedent (the **BR-OVR-3 "cancelable" + BR-OVR-8 "blank blocks submit" invariants remain gated** as behavioral teeth; only the a11y niceties stay soft). *Tier*: observed. *Rigor*: soft (baseline).

### GOVERNANCE

- **NFR-OVR-SCOPE-1** — *(not a runtime test)* the set tests **only** `ui-override-form`'s own behavior; it does not test other UI units, backend internals, or the WIRE-1 route implementation (R5/R4 impl → Build & Test). Reuses ui-shell's frozen mechanisms and mirrors the sibling conventions **without modifying or importing** any sibling (incl. frozen `ui-approval-gate`); WIRE-1 R4/R5 consumed **by shape**, mocked via the injected double. *Tier*: N/A (governance).

---

## 2. Draft traceability (target → FD rule → tier → rigor) — no orphan

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

---

## 3. Open questions — full text + lettered options (`[Answer]` BLANK; standing convention)

### Q1 — NFR depth
Confirm the NFR-Requirements depth for this unit.
- **A. COMPREHENSIVE** *(Recommended)* — consistent with the FD depth decision (the second/final write path; the mandatory-reason gate); full rigor on the invariant-bearing teeth.
- **B. Lighter (display)** with an interaction addendum. *(Rejected — contradicts the §U8 invariant-bearing classification.)*

**[Answer]:** A

### Q2 — Verifying `OverrideReasonInput` is genuinely capability-free *(user-flagged 1)*
`OverrideReasonInput` is a **new** controlled component with no analog in U7. How does NFR-OVR-CAPFREE-1 prove it is genuinely **capability-free** (mirroring U7's no-`createCommitFetch`-import-in-presentational StructuralGuard scan, extended to this component)?
- **A. Structural import-scan + prop-contract RTL** *(Recommended)*. (a) A StructuralGuard scan asserts `OverrideReasonInput` **imports no seam module** (`createOverrideFetch` / `overrideFetchSeam`) and references **no** `submitOverride` — extending the sibling `refNotOwn`-style import scan and reusing U7's **invocation/import** refinement (not a bare-word textual scan). The same scan covers `OverrideAffordance` (only `onOverride`, no seam) and confirms the single `submitOverride` call site is `OverrideConfirmDialog`. Each detector is **non-vacuous** (self-test). (b) A prop-contract RTL test asserts `OverrideReasonInput` renders from `{ value, onChange }` alone — a controlled `<textarea>` where typing calls `onChange` and it holds no other capability. Together: the import scan proves *absence of a commit path structurally*; the RTL proves *the controlled-input contract behaviorally*.
- **B. RTL behavioral-only** — assert that typing in the textarea issues zero transport calls, without a structural import scan. *(Weaker — proves this path didn't call the seam, not that the seam is un-importable/absent.)*
- **C. Structural import scan only** — no prop-contract RTL. *(Misses the controlled-component `{value,onChange}` contract.)*

**[Answer]:** A

### Q3 — Whitespace-variant coverage of the blank-reason teeth *(user-flagged 2)*
Given the FD-OVR-Fold-1 `trim()` vs `str.strip()` divergence, does NFR-OVR-REASONGATE-1's "blank blocks submit" teeth test **multiple** whitespace variants, or just the empty string?
- **A. A representative whitespace SET + a non-blank control + a divergence-documentation test** *(Recommended)*. The blank cases that must yield **zero** `submitOverride`: empty `""`, a single space `" "`, a tab `"\t"`, a newline `"\n"`, and a mixed `" \t\n "` — all treated blank by the `trim()` guard. Plus a **non-blank control** `" I disagree because X "` that **must** submit — and the payload sent is the reason **as entered** (the guard `trim()`s only for the *enable/disable decision*, **not** for the sent value; the backend stores what it receives). Plus an explicit **documentation test** asserting the guard is `String.prototype.trim()`-based and **not** byte-identical to Python `str.strip()` (FD-OVR-Fold-1), so the U+001C–U+001F / U+0085 divergence is **acknowledged, not silently assumed-equal**. *(Confirm the "send as-entered, not trimmed" payload sub-decision — the natural reading of the FD, called out here so it is explicit.)*
- **B. Just the empty string `""`** — minimal. *(Misses tabs/newlines — the realistic "looks blank" inputs — and the divergence documentation.)*
- **C. A full Unicode-whitespace matrix** incl. U+001C–U+001F / U+0085 / U+FEFF at the UI. *(Over-build — the FD made the guard deliberately non-authoritative; exhaustively UI-testing exotic code points contradicts the "backend is authoritative, divergence resolves via 409" resolution. The divergence is documented, not UI-exhaustively-tested.)*

**[Answer]:** A

### Q4 — Structure of the reason-echo assertion vs the reason-preservation teeth *(user-flagged 3)*
BR-OVR-12 has two facets: the reason **survives** Cancel/error transitions, and the reason is **echoed read-only** in the confirm dialog. Do these get **separate** assertions or **one** combined test?
- **A. Two distinct assertions (may share one test file)** *(Recommended)*. (1) **Preservation teeth** — the entered `reason` survives a `Cancel` and an `errorCommit` transition **unchanged** (a state assertion on the input's value). (2) A **dedicated DOM assertion** — the confirm dialog renders the current `reason` in a **read-only echo node** (its own `data-testid`, e.g. `override-confirm-reason-echo`) that is **not** an editable input. Keeping them logically separate keeps each failure **diagnosable** — a preservation regression and an echo-rendering regression fail **different** assertions. They may live in one file for cohesion.
- **B. One combined test** — after typing, open the dialog and assert the reason is both preserved and echoed in a single flow. *(Fewer tests, but a failure is ambiguous between preservation and echo.)*
- **C. Echo assertion only** (fold preservation into it). *(Under-covers preservation across the `errorCommit` transition, which never opens the dialog.)*

**[Answer]:** A

---

## 3A. Ambiguity-check (RUN against Q1–Q4 all-A + the frozen FD) — **CLEAN, three folds, no STOP (all VERIFIED on disk)**

The three explicitly-requested checks were **verified against real code**, not assumed; each resolves as a clarity-fold — no genuine gap.

- **NFR-OVR-Fold-1 — check (i): the "send as-entered" payload does NOT diverge from the committed echo (VERIFIED).** Re-read `audit_store/record_schema.py` + `commit_service.py`: `CommittedDecision.reason` is a plain `Optional[str] = None` with **no field validator and no normalization**; `_gate` checks `reason.strip()==""` for rejection but **does not mutate** `reason`; `_assemble` passes `reason=reason` **verbatim** into `CommittedDecision`. Therefore the backend **stores the reason exactly as received** — so the UI's "send as-entered" (Q3-A) and the R5 `CommittedDecision.reason` echo (BR-OVR-9) are **consistent**: the committed echo reflects exactly what was sent (leading/trailing whitespace included). **No UI↔echo divergence.** A NOREFETCH-1 assertion records that the committed echo equals the sent (as-entered) reason **precisely because the backend does not normalize** — verified, not assumed.

- **NFR-OVR-Fold-2 — check (ii): REASONKEEP-1's confirm echo and NOREFETCH-1's committed display are genuinely distinct states, not the same logic tested twice.** They differ on **state**, **DOM node**, and **data source**: (a) REASONKEEP-1's echo renders in the **`confirming`** state (pre-submission) from the **client `reason` state**, in node `override-confirm-reason-echo`; (b) NOREFETCH-1's display renders in the **`committed`** state (post-submission) from the **R5 `CommittedDecision.reason`** echo, in a distinct node (`override-committed-reason`). They share a *visual pattern* (read-only reason text) but test different things — the pre-submission "review what you will send" echo vs the post-submission "this is what was recorded" receipt. Per Fold-1 the two displayed values coincide (backend doesn't normalize), but they remain **separately sourced and separately asserted** (distinct testids). Not redundant — a clarity-fold confirming the two targets are distinct.

- **NFR-OVR-Fold-3 — check (iii): ADVISORY-1 verified NOW against the real detector (not deferred), matching U7's NFR-AG-Fold-2 discipline.** Audited **all 21** drafted `OVERRIDE_COPY` strings against the real frozen `FORBIDDEN_TERMS.systemOutput = ['DECLINE','decision','approved','declined']` (word-boundary, case-insensitive — the actual `shell/copy/forbiddenTerms.js`). **Zero** strings trip: none contains `decision` / `approved` / `declined` / a bare `DECLINE`. Unlike U7 (whose `confirmBody` originally read "your decision" and had to be corrected), **U8's copy is clean as-drafted** — the override framing uses `override` / `reason` / `record` / `committed` / `recommendation` and never renders the human `override` as the system `DECLINE-RECOMMEND`. So ADVISORY-1 holds with **zero copy change** and the `advisory-vocabulary` lint applies **UNMODIFIED** (single `FORBIDDEN_TERMS`, no carve-out, no second word-list). **Verified, not assumed.**

**→ CLEAN. Proceeding to Part 2.**

---

## 4. Planned Part-2 structure (generated)

On the user's filled answers → ambiguity-check → explicit go, Part 2 generates in `guide-docs/build/ui-override-form/nfr-requirements/`:
- **`nfr-requirements.md`** — the finalized `NFR-OVR-*` targets (§1, adjusted per answers), each with pass/fail acceptance criteria + tier + rigor; the traceability table (§2, no orphan); the folds crystallized from the answers; the Security-Guardrails compliance table (incl. the mandatory-reason-gate row as real content).
- **`tech-stack-decisions.md`** — D1..Dn inheriting the frozen substrate (Vitest + RTL + jsdom + ESLint over the one `FORBIDDEN_TERMS`; no live backend; no new heavy dependency), with the **dual-operation reason-carrying capturing double** (§0) and any answer-driven decisions recorded.

Per the standing convention, the plan file is **re-saved with the filled answers + folds embedded** at that point.

---

## 5. Security-Guardrails preview (expanded at Part 2)
Second UI unit with a real authorization-adjacent write surface, and the **first** carrying the mandatory-reason gate. Anticipated: **Compliant** on least-privilege UI framing (RoleGate cosmetic), authorization server-authoritative (AUTHZ-1 real gate), **mandatory-reason gate server-authoritative** (backend `_gate` real, UI guard non-authoritative — BR-OVR-8), no client-side authz datum (session-derived committer), human-in-the-loop (confirm + mandatory reason + cancel + reason preservation + no auto-resubmit), error hygiene (envelope discipline), advisory naming (override ≠ DECLINE-RECOMMEND). **N/A** (with rationale) on input-validation (reason is user-authored free text validated authoritatively server-side) / prompt-injection / secrets / audit-persistence (client-side read-context + single-justified-action-write; no untrusted parsing, no LLM, no secret material, no own persistence).

---

## 6. Holds (this stage)
- **No NFR artifact generated** — `nfr-requirements.md` / `tech-stack-decisions.md` deferred to Part 2 on explicit go; **no ambiguity-check run yet** (follows the answers).
- **No code** under `frontend/src/overrideForm/`; **WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate (all frozen) untouched**; no backend file touched.
- Frozen FD (BR-OVR-1..12 + inventory + state machine incl. reason preservation + two-server-gate note) is the substrate — **not re-opened**.
- **tier-B NOT authorized**; **no other unit started**; `audit_store` Docker-guard gap still deferred.

---

## 7. Gate
**Part 2 GENERATED** (`guide-docs/build/ui-override-form/nfr-requirements/nfr-requirements.md` + `tech-stack-decisions.md`) after the four answers (all A) + the CLEAN ambiguity-check (§3A, three verified folds). **STOPPED at the NFR-Requirements 2-option completion gate (1. Request Changes / 2. Continue to Next Stage → NFR Design)** for the user's review of both artifacts. Did NOT advance past the gate. WIRE-1 · ui-shell · ui-queue · ui-memo-view · ui-approval-gate (all frozen) untouched; tier-B NOT authorized; no other unit started.
