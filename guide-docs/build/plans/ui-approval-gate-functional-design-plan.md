# FD Part 1 (Planning) — `ui-approval-gate` (U7)

**Stage**: BUILD → per-unit loop → Functional Design → Part 1 (Planning)
**Unit**: `ui-approval-gate` (U7) — the 4th UI-cluster unit (working sequence: ui-queue → ui-memo-view → **ui-approval-gate** → ui-override-form → ui-history)
**Depth**: **COMPREHENSIVE** (confirmed — see §1)
**Date**: 2026-07-09
**Status**: **Part 1 plan — STOPPED at the plan-file gate for the user's review.** No FD artifact (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`) generated yet; no code under `frontend/src/approvalGate/`; WIRE-1 untouched; ui-shell / ui-queue / ui-memo-view (all frozen) untouched; tier-B NOT authorized; no other unit started.

---

## 0. What this unit is (scope) — and what it is NOT

`ui-approval-gate` is the **first UI unit with a real write path**: the interactive **approve** affordance that fires **WIRE-1 R5** `POST /recommendations/{recommendation_id}/commit`. It is:

- the **first real composition of ui-shell `RoleGate`** (cosmetic capability gating, `can="act"`);
- the **first interactive rendering of the `CommitAction` human namespace** (`approve` / `override`) — a *different value space* from the system `Recommendation` namespace (`APPROVE` / `REFER` / `DECLINE-RECOMMEND`), per WIRE-1 §1 namespace-distinctness;
- **approve-only** in this unit (`action: "approve"`, no reason). **Override** (`action: "override"` + mandatory non-blank reason) is deferred to **U8 `ui-override-form`** per the working sequence (Q6-A).

**It is NOT** an authorization authority (RoleGate is defense-in-depth cosmetic only; the backend AUTHZ-1 re-check in `DecisionCommitService` is the real gate — Q3-A), it does **not** finalize a decision by itself (the human's explicit confirm→commit is the only path; advisory-only + human-in-the-loop hard constraints), it runs **no LLM / no rule evaluation / no authz decision** client-side, and it **imports no backend and no sibling UI unit** (stand-alone; Q5-A).

### Builds ON (frozen — consumed by shape/convention, re-derived by none)

| Frozen surface | Where | How consumed |
|---|---|---|
| **ui-shell** `RoleGate` (`{ can, children, fallback }`, `can∈{act,read}`, `useCurrentRole()`, no `role` prop, cosmetic-only SEC-4), `AppFrame`/`Panel`/`ReadOnlyRegion`/`RecommendationBadge`/`ConfidenceBadge`, `shell/copy`, `shell/tokens`, `shell/session` RoleContext | `frontend/src/shell/**` (U10, frozen) | composed directly (import) |
| **ui-queue / ui-memo-view** `fetchSeam` + `StructuralGuard` sibling conventions | `frontend/src/queue/**`, `frontend/src/memoView/**` (U5/U6, frozen) | **convention only — NOT imported** (kept decoupled; own-local re-realization) |
| **WIRE-1 R5** `POST /recommendations/{recommendation_id}/commit` + R4 `GET /applications/{id}/memo` + error envelope §4 | `guide-docs/build/wire-1/api-contract.md` (PINNED) | request/response **shapes** consumed by value |
| **auth-rbac** `Role` / `PERMISSION_MATRIX` / `RBAC_COMMIT` (only `underwriter` holds `RBAC_COMMIT`) | `backend/auth_rbac/roles.py` (U11, frozen) | referenced as the semantic source RoleGate mirrors; **not imported** (cross-language) |
| **audit-store** `DecisionCommitService.commit(...)` (GATE-1 BR-COMMIT-GATE + independent AUTHZ-1 `UnauthorizedCommit`), `CommittedDecision`, `CommitAction∈{approve,override}` | `backend/audit_store/{commit_service,record_schema}.py` (U4, frozen) | the **real server-side enforcement** this UI action triggers; consumed as R5's response shape (`CommittedDecision`) |

---

## 1. Depth confirmation

**Q1 [Answer]: A — COMPREHENSIVE.** This is the first UI unit with an actual write path, the first real composition of `RoleGate`, and the first interactive rendering of the `CommitAction` human namespace — genuinely invariant-bearing (advisory-only, human-in-the-loop, namespace-distinctness), not display-only like ui-queue/ui-memo-view. COMPREHENSIVE depth is warranted.

---

## 2. The six questions — full text, options, and filled answers (embedded per standing convention)

### Q1 — Design depth
Confirm the FD depth for this unit.
- **A. COMPREHENSIVE** — first write path / first real RoleGate composition / first interactive CommitAction namespace; invariant-bearing.
- B. STANDARD — treat like a display-only view.
- C. MINIMAL — trivial affordance.

**[Answer]: A** — COMPREHENSIVE. (Rationale in §1.)

### Q2 — Commit interaction: confirm step vs single click
Should the approve affordance commit on a single click, or require an explicit confirm step first?
- **A. Explicit confirm step** before the R5 commit submits — the commit is the one place a decision is finalized, so it should never be a single stray click. Human-in-the-loop deliberateness.
- B. Single-click commit (with optimistic UI).
- C. Single-click with an undo window.

**[Answer]: A** — An explicit confirm step before the R5 commit submits; the commit is the one place a decision is finalized, so it should never be a single stray click. Human-in-the-loop deliberateness.

### Q3 — RoleGate vs backend authorization
What is `RoleGate can="act"`'s authority relative to the backend commit gate?
- **A. Cosmetic defense-in-depth only** — `RoleGate can="act"` cosmetically hides the approve affordance from non-underwriters, but the commit **always** submits to R5 where AUTHZ-1's backend re-check is the real gate; RoleGate is defense-in-depth only, never authorization; a **403** (if the cosmetic guard were somehow bypassed) surfaces as a genuine error, not a silent success.
- B. RoleGate is the authorization decision (client-authoritative).
- C. No RoleGate; rely solely on the server.

**[Answer]: A** — Cosmetic defense-in-depth only; AUTHZ-1's backend re-check is the real gate; a 403 surfaces as a genuine error, never a silent success.

### Q4 — Commit result surfacing (per documented status)
How are R5 outcomes surfaced to the underwriter?
- **A. Distinct handling per documented status** — success → committed-decision confirmation state; **409** → already-committed / conflict state; **403** → not-permitted defense-in-depth error; **400/422** → generic invalid — **all via the shared error-envelope pattern** (`message`-visible / `code`-testid / `detail`-never), reusing the sibling convention.
- B. A single generic "failed" toast for all non-2xx.
- C. Raw exception surfaced.

**[Answer]: A** — Distinct handling per documented status (success confirmation; 409 already-committed/conflict; 403 not-permitted; 400/422 generic invalid), all via the shared error-envelope pattern (message-visible / code-testid / detail-never), reusing the sibling convention.

### Q5 — Structural relation to ui-memo-view
How does the approval gate obtain the recommendation context it commits against?
- **A. Stand-alone with its own R4 fetch** for recommendation context, composing ui-shell primitives directly; **does not import ui-memo-view** (frozen), keeping the units decoupled per the established sibling-convention principle.
- B. Extend / wrap ui-memo-view (import it).
- C. Receive full context purely as props from a parent that already fetched it.

**[Answer]: A** — Stand-alone with its own R4 fetch for recommendation context, composing ui-shell primitives directly; does not import ui-memo-view (frozen), keeping the units decoupled per the established sibling-convention principle.

### Q6 — Approve-only vs approve+override in this unit
Which CommitAction affordances does this unit render?
- **A. Approve-only** affordance in this unit (`action="approve"`, no reason); **override** (`action="override"` + mandatory non-blank reason) deferred to **U8 `ui-override-form`**, matching the working sequence's unit split.
- B. Both approve and override here.
- C. Approve here; override never built.

**[Answer]: A** — Approve-only affordance in this unit (action="approve", no reason); override (action="override" + mandatory non-blank reason) deferred to U8 ui-override-form, matching the working sequence's unit split.

---

## 3. Planned Part-2 structure (NOT generated yet)

On the user's explicit go, Part 2 generates three artifacts in `guide-docs/build/ui-approval-gate/functional-design/`:

**`domain-entities.md`** — the build-time UI surface:
- **Consumed frozen shapes** (by value, none re-declared): R4 `MemoView` (`{ application_id, recommendation_id|null, status:"ready"|"pending", profile|null, report|null, memo|null }`) for recommendation context; R5 request body `{ action: "approve" }` (**approve-only — no `reason`; `underwriter_id` NOT in body**, AG-Fold-3); R5 success `CommittedDecision` `{ recommendation_id, underwriter_id, action, reason|null }`; the WIRE-1 §4 error envelope `{ error: { code, message, detail } }`; `CommitAction` value `"approve"`; the four §4 statuses this unit handles (200 / 403 / 409 / 400 / 422).
- **Own-local modules** (mirroring the sibling convention, NOT importing it): `approvalGate/commitFetchSeam.js` (own-local R4 read + **R5 write** seam via a duck-typed injected `transport`; `buildMemoRequest` for R4, `buildCommitRequest(recommendationId)` for R5 → `{ method:'POST', path:'/recommendations/${recommendationId}/commit', body:{ action:'approve' } }`; `normalizeError` → the same WIRE-1 envelope shape, **not shared code** — AG-Fold-4); `approvalGate/copy.js` (local UI strings, LINT-SUBJECT for forbidden system-output vocabulary + no shell-label duplication); the `ApprovalGateView` orchestrator + a `CommitStateView` (non-committed states) + a `CommitConfirmDialog` (the Q2-A confirm step) + a `CommittedConfirmation` (success state) — all composing ui-shell primitives + `RoleGate can="act"`.
- The **client state machine** (§ business-logic-model): `loading → ready(idle) → confirming → submitting → {committed | error}`, plus `pending` (no `recommendation_id` → **no approve affordance**, AG-Fold-5) and `error` (envelope). `confirming` is a **pure client-side dialog toggle** — opening/canceling it performs **no fetch and no state mutation** beyond the local dialog-open flag (AG-Fold-1).

**`business-rules.md`** — draft `BR-AG-1..n` + Security-Guardrails table. Draft rule set (to be finalized in Part 2):
- BR-AG-1 **Advisory-only / no client finalize** — the UI never finalizes; only an explicit human confirm→R5 commit produces a `CommittedDecision`; no auto-commit path.
- BR-AG-2 **Confirm-before-commit** — the R5 POST fires **only** on the confirm action inside `CommitConfirmDialog`; a single click on approve opens the dialog, it does not commit (Q2-A).
- BR-AG-3 **Cancelable-without-side-effect** — opening/canceling the confirm dialog does no fetch, no commit, no state mutation beyond the local dialog flag (AG-Fold-1, ambiguity-check i).
- BR-AG-4 **RoleGate cosmetic-only** — `RoleGate can="act"` hides the affordance from non-underwriters cosmetically; it is **not** authorization; AUTHZ-1 backend re-check is the real gate (Q3-A, SEC-4). No client-side authz decision.
- BR-AG-5 **Session-derived committer** — the R5 body carries **only** `{ action:"approve" }`; `underwriter_id` is derived server-side from the authenticated session (WIRE1-Fold-1), never sent from the client; `recommendation_id` comes from the fetched R4 context, placed in the **path** (AG-Fold-3, ambiguity-check iii).
- BR-AG-6 **Per-status surfacing via shared envelope** — success → committed-confirmation; 409 → already-committed/conflict; 403 → not-permitted; 400/422 → generic invalid; all via `message`-visible / `code`-testid(hidden) / `detail`-never (Q4-A).
- BR-AG-7 **CommitAction namespace-distinctness** — the human `approve` (lowercase, `CommitAction`) is never rendered as or conflated with the system `APPROVE` (uppercase, `Recommendation`); `override`≠`DECLINE-RECOMMEND` (deferred to U8) (WIRE-1 §1).
- BR-AG-8 **Approve-only scope** — this unit renders only the `approve` affordance; no override control, no reason input (Q6-A).
- BR-AG-9 **Confirmation renders without re-fetch** — the committed-confirmation state renders from the R4 context already in hand + the R5 `CommittedDecision` echo; **no separate R7/history re-fetch** (AG-Fold-2, ambiguity-check ii).
- BR-AG-10 **Reference-not-own / decoupled** — no backend import, no ui-memo-view/ui-queue import; own-local seam + copy; enforced by StructuralGuard tests (NFR stage).

**`business-logic-model.md`** — the confirm→commit flow (7-rule-validated Mermaid + text alternative), the state machine, the R4-read-then-R5-write sequence, the AUTHZ-1 defense-in-depth note (cosmetic gate → server is authoritative), consumer/dependency map, and an invariant self-check mapping each hard constraint → mechanism.

---

## 4. Mandatory ambiguity-check (RUN against the six answers + the frozen re-read) — **CLEAN**

Grounded on the on-disk re-read of WIRE-1 R5/R4 + §4, `DecisionCommitService.commit` / `_gate` (GATE-1) + AUTHZ-1 (`UnauthorizedCommit`), `CommittedDecision` / `CommitAction`, `auth_rbac.roles` (`RBAC_COMMIT`, PERMISSION_MATRIX), and the frozen sibling `memoFetchSeam` / `MemoStateView` / `copy` conventions. **No genuine external gap → no STOP.** Five clarity-folds; the three explicitly-requested checks resolve as follows:

- **AG-Fold-1 — check (i): is the confirm step (Q2-A) cancelable without side effects?** **Yes, by design.** `CommitConfirmDialog` is a **pure client-side UI-state toggle** (a local `confirming` boolean). Opening it performs **no R5 POST, no R4 re-fetch, and no other state mutation**; the R5 commit fires **only** on the dialog's confirm action; canceling returns to `ready(idle)` with zero side effects. This is intrinsic to the human-in-the-loop deliberateness Q2-A chose and to the established client-only patterns — a clarity-fold, not a gap. (→ BR-AG-2 / BR-AG-3.)

- **AG-Fold-2 — check (ii): does R5 success (`CommittedDecision`) return enough to render a meaningful confirmation, or is a re-fetch needed?** **Enough — no re-fetch.** `CommittedDecision = { recommendation_id, underwriter_id, action, reason|null }`. The view already holds the **R4 context** (`application_id`, `recommendation` value, `confidence`) from its own stand-alone fetch (Q5-A). The committed-confirmation state composes **(R4 context already in hand) + (R5 `CommittedDecision` echo)** → a meaningful acknowledgment ("Approved — application `<id>`, recommendation was `<value>`, committed by `<underwriter_id>`") **without** a separate re-fetch. `CommittedDecision` deliberately omits `decision_id` / `timestamp` (audit-store's `AuditRecord` fields) — surfacing those is **ui-history's** (R6/R7) scope, not this unit's, so NOT showing them here is consistent with the unit split. Clarity-fold, not a gap. (→ BR-AG-9.)

- **AG-Fold-3 — check (iii): does `underwriter_id`-from-session (WIRE1-Fold-1) need explicit restatement here?** **Yes — restated explicitly as this is the first UI unit to exercise commit.** The R5 request body carries **only** `{ action: "approve" }`. `underwriter_id` is **NOT** in the body — it is derived server-side from the authenticated session (the same identity R1 `GET /session` returns), and the backend re-checks `authorize(underwriter_id, RBAC_COMMIT)` independently (AUTHZ-1), so a client cannot commit **as another user**. `recommendation_id` comes from the fetched R4 context and goes in the **path**. This is a restatement of a frozen WIRE-1 fact (not a new decision) — pinned into `domain-entities.md` §R5-request and BR-AG-5 so the seam cannot drift. Clarity-fold, not a gap.

- **AG-Fold-4 — sibling seam is convention, not import.** `commitFetchSeam.js` re-realizes the `createXFetch(transport) → seam(...)` + `normalizeError`-to-WIRE-1-envelope pattern **locally**; it does **not** import `queue/fetchSeam` or `memoView/memoFetchSeam` (both frozen, kept decoupled). Cross-unit error-shape consistency comes from the **shared WIRE-1 §4 contract**, not shared code (matching CG-MEMO-Fold-1's precedent). A StructuralGuard `noUiQueueImport` / `noMemoViewImport` test enforces this at the NFR/Code-Gen stage.

- **AG-Fold-5 — R4 `status:"pending"` (no `recommendation_id`) → no approve affordance.** When R4 returns `status:"pending"` / `recommendation_id: null`, there is **nothing to commit**; the unit renders a defined "not yet drafted — nothing to approve" state and offers **no** approve control. This is a direct consequence of the frozen R4 `MemoView` shape (WIRE1-Fold-2), not a new design — a clarity-fold ensuring the write path can't fire without a `recommendation_id`.

---

## 5. Holds (this stage)

- **No FD artifact generated** — `domain-entities.md` / `business-rules.md` / `business-logic-model.md` deferred to Part 2 on explicit go.
- **No code** under `frontend/src/approvalGate/`; **WIRE-1 untouched**; **ui-shell / ui-queue / ui-memo-view (all frozen) untouched**; no backend file touched.
- **Advisory-only + human-in-the-loop + namespace-distinctness + RoleGate-cosmetic-not-authz + no-LLM** hard constraints held (domain guardrails re-loaded and cross-checked against all six answers — no conflict).
- **tier-B NOT authorized**; **no other unit started**; `audit_store` Docker-guard gap still deferred (non-blocking).

---

## 6. Gate

**STOPPED at the FD Part 1 plan-file gate.** Awaiting the user's review of this plan (the six answers + comprehensive depth + the CLEAN ambiguity-check with five folds). On explicit go → Part 2 generates the three FD artifacts. No Part-2 generation until then.
