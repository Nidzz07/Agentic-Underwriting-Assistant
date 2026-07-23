# NFR Requirements Part 1 (Plan) — `ui-approval-gate` (U7)

**Stage**: BUILD → per-unit loop → NFR Requirements → Part 1 (Planning)
**Unit**: `ui-approval-gate` (U7) · C-cluster UI · Phase 1 · **Depth**: **COMPREHENSIVE** (consistent with the FD depth decision — first UI write path, first real `RoleGate` composition, first interactive `CommitAction` namespace)
**Date**: 2026-07-09
**Status**: **Part 1 plan — ANSWERED (Q1–Q6 all A) · ambiguity-check CLEAN (two folds) · Part 2 GENERATED.** The six `[Answer]` tags are embedded (§3). Ambiguity-check run against the six answers + the frozen FD — no genuine gap → two clarity-folds (§3A). Part 2 (`nfr-requirements.md` + `tech-stack-decisions.md`) generated. WIRE-1 / ui-shell / ui-queue / ui-memo-view (all frozen) untouched; tier-B NOT authorized; no other unit started. **STOPPED at the NFR-Requirements 2-option completion gate.**

**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md` — **BR-AG-1..11**, the component/prop inventory, the full client state machine **including the split `ErrorRead`/`ErrorCommit` recovery paths**, the AUTHZ-1 defense-in-depth structural note) — **re-opening none of it**. Each `NFR-AG-*` target is a **pass/fail testable assertion** traced to its FD rule.

**Tier convention inherited from `ui-shell` (frozen U10), applied by `ui-queue` (U5) and `ui-memo-view` (U6)**: Vitest + React Testing Library + jsdom · ESLint over the **single** `FORBIDDEN_TERMS` source · file/import structural scans · detector self-tests (non-vacuous). **Advisory-only; no LLM; no live backend** — WIRE-1 **R4 and R5** are exercised through a **single injected/capturing double** (see §0). No frozen mechanism is modified or imported from a sibling; sibling `fetchSeam`/`StructuralGuard` conventions are **mirrored**, not imported.

---

## 0. Central testability principle — the dual-operation seam

`ui-approval-gate`'s properties are testable **without a running backend**. Unlike ui-queue/ui-memo-view (each a **single**-operation read seam), this unit's `commitFetchSeam` has **two** operations: `fetchContext` (R4 read) **and** `submitApprove` (R5 write). The **load-bearing** targets are behavioral **teeth** that count transport calls per operation:

- **Commit-only-on-Confirm** (BR-AG-1/2/3): assert **zero** `submitApprove` calls across `mount → Approve-click → open dialog → Cancel`, and **exactly one** `submitApprove` call **only** on `Confirm`.
- **No re-fetch after commit** (BR-AG-9): assert **zero** further transport calls (both operations) after a successful commit.
- **Cause-differentiated recovery** (BR-AG-11): assert an `ErrorRead` `Retry` re-issues **exactly one** R4 `fetchContext` for the same `applicationId`; an `ErrorCommit` returns to `ready(idle)` with **zero** automatic `submitApprove`.

Because both operations share one capturing double, each needs **independent call-count tracking** — this is **Q2** (genuinely open; the sibling single-double Fold does not directly specify the dual-operation shape).

Four test modalities (mirroring the sibling §0):
1. **Build-failing lints + structural scans** — COPY-1 / ADVISORY-1 / NAMESPACE-1 reuse ui-shell's ESLint + the **one** `FORBIDDEN_TERMS` source (never a second word-list); NOTS-1 / RBAC-1(structural) / REFNOTOWN-1 / SCOPE-APPROVE-1(structural) are file/import/render scans; each detector carries a **self-test**.
2. **Component-render + interaction assertions (RTL + jsdom)** — CONFIRM-1, CANCEL-1, ERROR-1, RBAC-1(render, stub `RoleProvider`), SCOPE-APPROVE-1(render), FETCH-1's per-state renders.
3. **Dual-operation capturing-double assertions** — the transport-call-count teeth (CONFIRM-1, CANCEL-1, NOREFETCH-1, RECOVERY-1) + BODY-1's recorded request body + RECOVERY-1's recorded `applicationId`.
4. **Observed/soft** — PERF-1 (bounded R4 + single R5, non-gating) and A11Y-1 (semantic + focusable confirm/cancel, recorded target).

**Scope**: the `NFR-AG-*` set tests **only** `ui-approval-gate`'s own behavior — not other UI units, not any backend unit's internals, not the WIRE-1 route implementation (R5/R4 impl → Build & Test). It **reuses** ui-shell's frozen mechanisms (copy / `FORBIDDEN_TERMS` / ESLint / `RoleGate` / `ReadOnlyRegion` / badges / testid convention) and **mirrors** ui-queue/ui-memo-view's fetchSeam/StructuralGuard convention **without modifying or importing** either.

---

## 1. Draft `NFR-AG-*` target map (BR-AG-1..11 → pass/fail target; no orphan)

### FULL RIGOR — the commit-lifecycle teeth (load-bearing)

- **NFR-AG-NOFINAL-1** (BR-AG-1) — **no client finalize.** Structural: the **only** call site of `submitApprove` is the `CommitConfirmDialog` `Confirm` handler; mount/read/`confirming`-toggle issue no R5 POST. **Teeth** shared with CONFIRM-1. *Tier*: structural + component. *Rigor*: full.
- **NFR-AG-CONFIRM-1** (BR-AG-2) — **confirm-before-commit teeth.** RTL on the dual-operation double: `Approve`-click transitions to `confirming` and produces **zero** `submitApprove` calls; **only** the dialog `Confirm` produces **exactly one** R5 POST. *Tier*: component (teeth). *Rigor*: **full (highest)**.
- **NFR-AG-CANCEL-1** (BR-AG-3) — **cancelable-without-side-effect teeth.** RTL: `Approve` → open → `Cancel`; assert **zero** calls on **both** operations across open+cancel, and the rendered context is identical before/after; state returns to `ready(idle)`. *Tier*: component (teeth). *Rigor*: **full (highest)**.

### FULL RIGOR — authorization-adjacent + write-shape

- **NFR-AG-RBAC-1** (BR-AG-4) — **RoleGate cosmetic-only.** (a) **structural** — no backend import, no authz-function call in `frontend/src/approvalGate/` (StructuralGuard scan + detector self-test); (b) **RTL** stub `RoleProvider` render coverage (role set → **Q3**): `underwriter` sees the affordance; non-underwriter roles see the fallback. *Tier*: structural + component. *Rigor*: full.
- **NFR-AG-BODY-1** (BR-AG-5) — **session-derived committer.** Unit test on `buildCommitRequest(recommendationId)`: the request body **deep-equals** `{ action: 'approve' }` (no `underwriter_id` key, no `reason` key); the path contains the R4-supplied `recommendation_id`. *Tier*: unit. *Rigor*: full.
- **NFR-AG-ERROR-1** (BR-AG-6) — **per-status surfacing.** Table-driven RTL across the four documented statuses (**200 → committed**; **403 → not-permitted**; **409 → already-committed/conflict**; **400 & 422 → generic invalid**), each programmed on the double; envelope discipline: `message` VISIBLE, `code` in a `hidden` testid node, `detail` NEVER in the DOM. *Tier*: component (table-driven). *Rigor*: full.
- **NFR-AG-SCOPE-APPROVE-1** (BR-AG-8) — **approve-only scope.** (a) structural — no override control and no `reason` input in the tree; `buildCommitRequest` emits no `reason` key; (b) RTL — the rendered affordance is approve-only. *Tier*: structural + component. *Rigor*: full.
- **NFR-AG-NOREFETCH-1** (BR-AG-9) — **confirmation without re-fetch teeth.** RTL: after a successful commit, the confirmation shows `action=approve` + `recommendation_id` + `underwriter_id` (echo) + the recommendation value (R4 context in hand), while **both** operations on the double receive **zero** further calls. *Tier*: component (teeth). *Rigor*: full.
- **NFR-AG-REFNOTOWN-1** (BR-AG-10) — **reference-not-own.** StructuralGuard scans (mirroring the sibling convention, each non-vacuous): `noBackendImport`, `noUiQueueImport`, `noMemoViewImport`, `noRouterImport`. *Tier*: structural. *Rigor*: full.
- **NFR-AG-RECOVERY-1** (BR-AG-11) — **cause-differentiated recovery teeth.** RTL two-directional (the rule's own mechanism): (a) an `ErrorRead` `Retry` click re-issues **exactly one** `fetchContext` for the **same** `applicationId` (recorded id === X); (b) an `ErrorCommit` transitions to `ready(idle)` with **zero** automatic `submitApprove` follow-ups, requiring a fresh `Approve → Confirm` cycle. *Tier*: component (teeth). *Rigor*: full.
- **NFR-AG-FETCH-1** (state-machine addendum) — **dual-operation seam + full state machine.** (a) the seam is **injected as a prop** (never a hard-wired fetch); (b) per-state renders — `loading`, `pending` (no affordance), `ready(idle)`, `confirming`, `submitting`, `committed`, `ErrorRead`, `ErrorCommit`; (c) a transition test covering all legs incl. **both** split-error recovery paths (consolidation → **Q5**). *Tier*: component. *Rigor*: full.

### FULL RIGOR — inherited conventions

- **NFR-AG-COPY-1** (reused ui-shell COPY convention) — **no inlined display label.** No Recommendation/Confidence label literal in `frontend/src/approvalGate/`; badges render by **value look-up** from `shell/copy`; chrome lives in the approval-local copy module. Build-failing `no-inline-label` ESLint (ui-shell mechanism) + detector self-test. *Tier*: lint. *Rigor*: full.
- **NFR-AG-ADVISORY-1** (advisory-only naming facet of BR-AG-1) — **reuse the ONE advisory-vocabulary lint.** The ui-shell `advisory-vocabulary` lint is registered on `src/approvalGate/**` (a config block mirroring the sibling; no `src/shell` edit, no new word-list); this unit's **static copy** contains no forbidden system-output token. **Scope for this unit's human-action copy → Q4** (genuine collision: the lint forbids the token `decision`, which the reserved-word rule permits for the human's committed action). *Tier*: lint. *Rigor*: full.
- **NFR-AG-TESTID-1** (reused testid convention) — every assertion-relevant element carries a stable `approval-<element>-<purpose>` `data-testid`; a convention lint/test (mirroring the sibling) + detector self-test (non-vacuous). *Tier*: lint / component. *Rigor*: full.
- **NFR-AG-NOTS-1** (FR-UI-5) — `frontend/src/approvalGate/` is plain JS/JSX; a file-scan finds **zero** `.ts`/`.tsx` and no `tsconfig*.json`. *Tier*: structural. *Rigor*: full.

### MEDIUM RIGOR

- **NFR-AG-NAMESPACE-1** (BR-AG-7) — **namespace-distinctness.** Reuse the `FORBIDDEN_TERMS` collision guard + `COMMIT_ACTION_LABELS` (mirroring the sibling NAMESPACE-1): the human `approve` (lowercase `CommitAction`) is never rendered as the system `APPROVE` (uppercase `Recommendation`); `override` is not present (deferred) and never equals `DECLINE-RECOMMEND`; assert `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS` (single source); detector self-test. *Tier*: structural. *Rigor*: medium.

### SOFT / OBSERVED

- **NFR-AG-PERF-1** — bounded: R4 fetches one resource by `applicationId`, R5 posts one commit; no list/all-rows path (structural bounding, mirroring the sibling `boundedFetch` scan). Latency/bundle observed, non-gating. *Tier*: structural + observed. *Rigor*: soft.
- **NFR-AG-A11Y-1** — semantic markup + focusable `Approve`/`Confirm`/`Cancel`/`Retry`; the confirm dialog's focus/keyboard behavior. Gating-vs-soft → **Q6**. *Tier*: observed. *Rigor*: soft (baseline).

### GOVERNANCE

- **NFR-AG-SCOPE-1** — *(not a runtime test)* the set tests **only** `ui-approval-gate`'s own behavior; it does not test other UI units, backend internals, or the WIRE-1 route implementation (R5/R4 impl → Build & Test). Reuses ui-shell's frozen mechanisms and mirrors the sibling fetchSeam/StructuralGuard convention **without modifying or importing** either; WIRE-1 R4/R5 consumed **by shape**, mocked via the injected double. *Tier*: N/A (governance).

---

## 2. Draft traceability (target → FD rule → tier → rigor) — no orphan

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
| NFR-AG-ADVISORY-1 | BR-AG-1 (naming facet) / Q4 | lint | full |
| NFR-AG-TESTID-1 | reused testid convention | lint / component | full |
| NFR-AG-NOTS-1 | FR-UI-5 | structural | full |
| NFR-AG-PERF-1 | view-perf precedent | structural + observed | soft |
| NFR-AG-A11Y-1 | FR-UI (view) / Q6 | observed | soft |
| NFR-AG-SCOPE-1 | — | N/A | governance |

**No orphaned FD rule**: BR-AG-1→NOFINAL-1 (+ADVISORY-1 naming facet), 2→CONFIRM-1, 3→CANCEL-1, 4→RBAC-1, 5→BODY-1, 6→ERROR-1, 7→NAMESPACE-1, 8→SCOPE-APPROVE-1, 9→NOREFETCH-1, 10→REFNOTOWN-1, 11→RECOVERY-1. COPY/TESTID/NOTS/FETCH/PERF/A11Y cover inherited + addendum concerns.

---

## 3. Open questions — full text + lettered options (`[Answer]` BLANK; standing convention)

### Q1 — NFR depth
Confirm the NFR-Requirements depth for this unit.
- **A. COMPREHENSIVE** — consistent with the FD depth decision (write path / RoleGate / CommitAction namespace); full rigor on the invariant-bearing teeth.
- B. Lighter (display) with an interaction addendum.

**[Answer]:** A

### Q2 — Dual-operation capturing double (the "zero transport calls" teeth construction) *(user-flagged)*
The seam has **two** operations (`fetchContext` R4 + `submitApprove` R5). The teeth (BR-AG-1/2/3/9) need **independent call-count tracking** of each on **one** double. How is the double constructed?
- **A. Single injected seam object `{ fetchContext, submitApprove }`, each an independently-counted spy** (records its own call count + args). Teeth assert `submitApprove.calls.length === 0` across `mount → Approve → open → Cancel` (while `fetchContext.calls.length === 1` from the initial read), and `=== 1` only after `Confirm`; NOREFETCH-1 asserts **both** counts unchanged after success. **Extends** ui-memo-view's single-double Fold to a dual-operation seam — **one** double, **two** counted operations, no divergent patterns.
- B. **Two separate injected doubles** (one per operation) — diverges from the single-double convention.
- C. **One call-log array** capturing `{ op, args }` tuples, filtered by `op` for counts.

**[Answer]:** A

### Q3 — RoleGate stub-provider coverage *(user-flagged)*
`RoleGate can="act"` is a **binary** act/no-act gate. Which roles does the RBAC-1 stub-`RoleProvider` render test cover?
- **A. All three explicit roles + null** — `underwriter` → affordance **present**; `auditor` → **absent**; `admin` → **absent**; `null` (unauthenticated) → **absent**. Pins the frozen `COSMETIC_CAPABILITIES` `act:false` cells for **both** non-underwriter roles + the null case; catches a regression where any non-underwriter role gained the affordance, even though the gate is binary.
- B. **Binary only** — `underwriter` vs one representative non-underwriter, since `act` is binary.

**[Answer]:** A

### Q4 — advisory-vocabulary lint scope vs the human-action copy *(genuine collision — flagged, not improvised)*
The **single** `FORBIDDEN_TERMS.systemOutput` = `['DECLINE','decision','approved','declined']`; the ui-shell `advisory-vocabulary` lint flags the bare token **`decision`** anywhere in static copy (word-boundary, case-insensitive). But **this unit is the human decision point**, where the reserved-word rule (underwriting hard-constraint #1) *permits* "decision" for the **human's committed action** (the `FORBIDDEN_TERMS` comment itself says `decision` is *"reserved for the HUMAN underwriter's committed action"*). The illustrative FD copy string `"This records your decision."` would trip the lint. How is the lint applied here?
- **A. Apply the sibling `advisory-vocabulary` lint UNMODIFIED** (single `FORBIDDEN_TERMS`, **no** carve-out, **no** second word-list); **this unit's static copy avoids the literal forbidden tokens** (incl. `decision`) — the human-action framing uses `approval` / `approve` / `record` / `committed` and **never** the bare tokens `decision` / `approved` / `declined` / bare `DECLINE`. The reserved-word constraint is honored **semantically** (the system recommendation is never called a decision; the human action is framed without needing the literal token). The illustrative FD copy `"This records your decision."` is **realized at Code-Gen without the token `decision`** (a **LINT-SUBJECT realization refinement** — the FD marked copy as LINT-SUBJECT, so this is **not** an FD re-open). Preserves cross-unit lint identity.
- B. **Scoped carve-out** exempting `decision` for this unit (a second word-list / per-unit lint config) — **diverges** from the single-`FORBIDDEN_TERMS` fold.
- C. **Split `FORBIDDEN_TERMS`** into system-context vs human-context lists — divergence.

**[Answer]:** A

### Q5 — Consolidated state-machine transition test (given the split `ErrorRead`/`ErrorCommit` + dual-operation seam)
How is FETCH-1's transition coverage structured?
- **A. ONE consolidated transition test** on the same dual-operation double covering `loading→ready`, `loading→pending`, `loading→ErrorRead`, `ErrorRead --Retry--> loading`, `ready→confirming` (zero POST), `confirming --Cancel--> ready` (zero POST), `confirming --Confirm--> submitting → committed`, `submitting → ErrorCommit`, `ErrorCommit --> ready` — mirroring ui-memo-view's consolidated transition test, extended for the write path + split recovery.
- B. **Separate per-transition tests.**

**[Answer]:** A

### Q6 — PERF-1 / A11Y-1 soft-vs-gating (this unit adds an interactive confirm dialog)
Unlike the display-only siblings, this unit has an interactive confirm dialog (focusable `Approve`/`Confirm`/`Cancel`/`Retry`, possible Escape-to-cancel, focus management). Are PERF-1/A11Y-1 gating or soft?
- **A. Observed/soft**, consistent with the ui-shell/ui-queue/ui-memo-view precedent (recorded target; detailed a11y **not** gating in Phase 1). The confirm-dialog focus / keyboard-Escape / focus-trap behaviors are **recorded as NFR-Design targets**, not Phase-1 gates. (Note: the **BR-AG-3 "cancelable" invariant is still gated** as behavioral teeth via the `Cancel` control — CANCEL-1, full rigor; only the a11y niceties stay soft.)
- B. **Gate A11Y** for the confirm dialog (focus-trap + Escape) in Phase 1.

**[Answer]:** A

---

## 3A. Ambiguity-check (RUN against Q1–Q6 all-A + the frozen FD) — **CLEAN, two folds, no STOP**

The two explicitly-requested checks resolve as clarity-folds; no genuine gap.

- **NFR-AG-Fold-1 — check (i): dual-operation spy clarity (guard against asserting on the wrong operation's count).** The single injected double (Q2-A) exposes its two operations under the **exact seam names** `fetchContext` / `submitApprove`, each with its **own** call log — **never** a shared generic `calls` array that a test could read ambiguously. Hardening (non-vacuous cross-guard): the CONFIRM-1 pre-`Confirm` checkpoint asserts **both** `submitApprove.calls.length === 0` **and** `fetchContext.calls.length === 1` — because the two expected counts **differ (0 vs 1)**, a test that accidentally watched the wrong counter **fails**; a swap of the two assertions flips 0/1 and fails. NOREFETCH-1 similarly asserts **both** counts frozen after success. A clarity-fold on the test-harness API, not a gap.

- **NFR-AG-Fold-2 — check (ii): Q4-A applied to the actual `copy.js` draft (adjusted NOW, not a vague promise).** All **14** `APPROVAL_COPY` draft strings in `domain-entities.md §3` were audited against the frozen `findForbiddenSystemOutput` detector (bare `decline` / `decision` / `approved` / `declined`). **Exactly one** tripped: `confirmBody`'s `"…This records your decision."` (bare `decision`, `\bdecision\b`). **Fixed now** in `domain-entities.md §3` — `confirmBody` → `"You are about to approve this recommendation. Your approval will be recorded."` + the §3 note rewritten to state the reserved-word constraint is honored **semantically** (the system recommendation is never called a *decision*) **without** the literal token. This is a **LINT-SUBJECT realization refinement** the FD explicitly deferred to NFR/Code-Gen — **not** an FD re-open. The other **13** strings were already clean (`approve` / `approval` / `Approval` / `committed`; none contains `approved` / `declined` / bare `decline`). Consequently the `advisory-vocabulary` lint applies **UNMODIFIED** (single `FORBIDDEN_TERMS`, no carve-out, no second word-list) — the ADVISORY-1 target holds as written.

---

## 4. Planned Part-2 structure (NOT generated yet)

On the user's filled answers → ambiguity-check → explicit go, Part 2 generates in `guide-docs/build/ui-approval-gate/nfr-requirements/`:
- **`nfr-requirements.md`** — the finalized `NFR-AG-*` targets (§1, adjusted per answers), each with pass/fail acceptance criteria + tier + rigor; the traceability table (§2, no orphan); the folds crystallized from the answers; the Security-Guardrails compliance table (§5).
- **`tech-stack-decisions.md`** — D1..Dn inheriting the frozen substrate (Vitest + RTL + jsdom + ESLint over the one `FORBIDDEN_TERMS`; no live backend; no new heavy dependency), with the **dual-operation capturing double** (Q2) and any answer-driven decisions recorded.

Per the standing convention, the plan file is **re-saved with the filled answers + folds embedded** at that point.

---

## 5. Security-Guardrails preview (expanded at Part 2)
First UI unit with a real authorization-adjacent write surface. Anticipated: **Compliant** on least-privilege UI framing (RoleGate cosmetic), authorization server-authoritative (AUTHZ-1 real gate), no client-side authz datum (session-derived committer), human-in-the-loop (confirm + cancel + no auto-resubmit), error hygiene (envelope discipline), advisory naming (Q4-scoped). **N/A** (with rationale) on input-validation / prompt-injection / secrets / audit-persistence (client-side read-context + single-action-write; no untrusted parsing, no LLM, no secret material, no own persistence).

---

## 6. Holds (this stage)
- **No NFR artifact generated** — `nfr-requirements.md` / `tech-stack-decisions.md` deferred to Part 2 on explicit go.
- **No code** under `frontend/src/approvalGate/`; **WIRE-1 · ui-shell · ui-queue · ui-memo-view (all frozen) untouched**; no backend file touched.
- Frozen FD (BR-AG-1..11 + inventory + state machine incl. split recovery + AUTHZ-1 note) is the substrate — **not re-opened**.
- **tier-B NOT authorized**; **no other unit started**; `audit_store` Docker-guard gap still deferred.
- **Genuine gap resolved (Q4-A applied)**: the advisory-vocabulary/`decision`-token collision was surfaced as Q4, answered A, and **applied concretely** to `copy.js` (`confirmBody` fixed, §3 note rewritten) — NFR-AG-Fold-2. No literal token exemption; the shared lint stays unmodified.

---

## 7. Gate
**Part 2 GENERATED** (`guide-docs/build/ui-approval-gate/nfr-requirements/nfr-requirements.md` + `tech-stack-decisions.md`). **STOPPED at the NFR-Requirements 2-option completion gate (1. Request Changes / 2. Continue to Next Stage → NFR Design)** for the user's review of both artifacts. Did NOT advance past the gate.
