# `ui-approval-gate` (U7) — Functional Design · Business Rules

**Stage**: BUILD → per-unit loop → Functional Design → Part 2 · **Depth**: COMPREHENSIVE
**Date**: 2026-07-09
**Scope**: the invariant-bearing rules of the first UI **write path** (the interactive approve affordance firing WIRE-1 R5). Each rule has an explicit **condition** and, where checkable, the **mechanism** that will land at NFR/Code-Gen. No frozen artifact is re-opened.

---

## 1. Rules — BR-AG-1 .. BR-AG-10 (finalized exactly as drafted in the plan §3)

### BR-AG-1 — Advisory-only / no client finalize
**Condition**: no UI code path finalizes an outcome. A `CommittedDecision` exists **only** as the result of an **explicit human confirm → R5 commit**; there is no auto-commit, no optimistic finalize, no timer/undo path that commits without a human action.
**Mechanism (checkable)**: the R5 POST is issued **only** from `CommitConfirmDialog`'s `Confirm` handler; a structural/unit test asserts no other code path calls `submitApprove`, and that mount/read/`confirming`-toggle issue no POST.

### BR-AG-2 — Confirm-before-commit
**Condition**: clicking the Approve affordance **opens** `CommitConfirmDialog`; it does **not** commit. The R5 POST fires **only** on the dialog's `Confirm` action (Q2-A).
**Mechanism (checkable)**: RTL test — clicking Approve transitions to `confirming` and issues **zero** fetch calls on the injected double; only `Confirm` produces exactly one R5 POST.

### BR-AG-3 — Cancelable-without-side-effect
**Condition**: opening or canceling `CommitConfirmDialog` performs **no fetch, no commit, and no state mutation** beyond the local `confirming` flag; `Cancel` returns to `ready(idle)` unchanged (**AG-Fold-1**, ambiguity-check i).
**Mechanism (checkable)**: RTL test — open then Cancel; assert the injected transport double received **no** call across open+cancel, and the rendered context is identical before and after.

### BR-AG-4 — RoleGate cosmetic-only (not authorization)
**Condition**: `RoleGate can="act"` hides the approve affordance from non-underwriters **cosmetically**; it is **not** an authorization decision. No client-side authz function is called; the frozen ui-shell `RoleGate` reads Role internally via `useCurrentRole()` and imports no backend (Q3-A, SEC-4). The **real** gate is AUTHZ-1 (`DecisionCommitService` backend re-check).
**Mechanism (checkable)**: stub-`RoleProvider` RTL test — `underwriter` sees the affordance, `auditor`/`admin` see the fallback; a structural test asserts the unit imports no backend module and calls no authz function client-side.

### BR-AG-5 — Session-derived committer (never client-sent)
**Condition**: the R5 body carries **only** `{ action: "approve" }`. `underwriter_id` is **never** sent from the client — it is derived server-side from the authenticated session; `recommendation_id` comes from the R4 context and is placed in the **path** (WIRE1-Fold-1 / **AG-Fold-3**, ambiguity-check iii).
**Mechanism (checkable)**: unit test on `buildCommitRequest` — the body deep-equals `{ action: 'approve' }` (no `underwriter_id`, no `reason` key); the path contains the R4-supplied `recommendation_id`.

### BR-AG-6 — Per-status surfacing via the shared error envelope
**Condition**: R5 outcomes are surfaced **distinctly per documented status** (Q4-A): 200 → committed-confirmation; 409 → already-committed/conflict; 403 → not-permitted; 400/422 → generic invalid — **all** via the shared envelope with `message` VISIBLE, `code` in a `hidden` testid node, `detail` NEVER rendered.
**Mechanism (checkable)**: table-driven RTL tests — each status renders its distinct state; `message` is in the DOM, `code` only in the hidden testid node, `detail` absent from the DOM.

### BR-AG-7 — CommitAction namespace-distinctness
**Condition**: the human `approve` (lowercase, `CommitAction`) is **never** rendered as, serialized as, or conflated with the system `APPROVE` (uppercase, `Recommendation`); `override` (deferred) ≠ `DECLINE-RECOMMEND` (WIRE-1 §1).
**Mechanism (checkable)**: namespace test — the committed body/action value is the literal `"approve"`; a lint/unit check asserts the copy module and commit builder never emit an uppercase `Recommendation` value as the human action, and the two namespaces share no key.

### BR-AG-8 — Approve-only scope
**Condition**: this unit renders **only** the `approve` affordance — no override control, no reason input, no reason field in the request (Q6-A). Override is U8 `ui-override-form`.
**Mechanism (checkable)**: structural/RTL test — no override control in the tree; `buildCommitRequest` emits no `reason` key.

### BR-AG-9 — Confirmation renders without re-fetch
**Condition**: the committed-confirmation state renders from the **R5 `CommittedDecision` echo + the R4 context already in hand** — with **no separate R6/R7/history re-fetch** (**AG-Fold-2**, ambiguity-check ii).
**Mechanism (checkable)**: RTL test — after a successful commit, the confirmation shows `action=approve` + `recommendation_id` + `underwriter_id` from the echo (plus the recommendation value from R4 context) while the injected transport receives **no** further call.

### BR-AG-10 — Reference-not-own / decoupled
**Condition**: no backend import; no `ui-queue` / `ui-memo-view` import; the unit uses its **own-local** `commitFetchSeam` + `copy` (**AG-Fold-4**). Cross-unit error-shape consistency comes from the shared WIRE-1 §4 contract, not shared code.
**Mechanism (checkable)**: StructuralGuard tests (`noBackendImport`, `noUiQueueImport`, `noMemoViewImport`, `noRouterImport`) — the established sibling convention, each non-vacuous (detector self-test).

### BR-AG-11 — Error-recovery is cause-differentiated
**Condition**: error recovery differs by cause. An **R4 (context-read) failure's** `Retry` **re-issues the R4 read** for the same `applicationId`. An **R5 (commit) failure** returns the state to **`ready(idle)`** — **never an automatic resubmit** — requiring the underwriter to deliberately **re-open the confirm dialog and re-confirm** before any retry of the commit itself.
**Mechanism (checkable)**: RTL tests — (a) an R4-error `Retry` click re-issues **exactly one** R4 `GET` for the same `applicationId`; (b) an R5-error transitions to `ready(idle)` with **zero** automatic follow-up calls to `submitApprove`, requiring a fresh Approve→Confirm cycle before the next commit attempt.

---

## 2. Rule index

| Rule | Title | Invariant class | Checkable-at |
|---|---|---|---|
| BR-AG-1 | Advisory-only / no client finalize | advisory-only | NFR / Code-Gen (structural + unit) |
| BR-AG-2 | Confirm-before-commit | human-in-the-loop | Code-Gen (RTL) |
| BR-AG-3 | Cancelable-without-side-effect | human-in-the-loop | Code-Gen (RTL) |
| BR-AG-4 | RoleGate cosmetic-only (not authz) | least-privilege / defense-in-depth | Code-Gen (stub-provider RTL + structural) |
| BR-AG-5 | Session-derived committer | authorization integrity | Code-Gen (unit) |
| BR-AG-6 | Per-status surfacing via shared envelope | error-hygiene | Code-Gen (table-driven RTL) |
| BR-AG-7 | CommitAction namespace-distinctness | namespace-distinctness | NFR / Code-Gen (namespace + lint) |
| BR-AG-8 | Approve-only scope | scope boundary | Code-Gen (structural / RTL) |
| BR-AG-9 | Confirmation without re-fetch | efficiency / scope split | Code-Gen (RTL) |
| BR-AG-10 | Reference-not-own / decoupled | decoupling | NFR / Code-Gen (StructuralGuard) |
| BR-AG-11 | Error-recovery is cause-differentiated | human-in-the-loop / no auto-resubmit | Code-Gen (RTL) |

---

## 3. Security-Guardrails compliance table

This is the **first UI unit with a real authorization-adjacent surface** (an interactive write that triggers server-side authz). The RBAC / authorization rows carry **real content**, not N/A.

| Guardrail | Status | Rationale |
|---|---|---|
| **Least-privilege UI framing (RBAC-affordance)** | **Compliant** | The approve affordance is wrapped in `RoleGate can="act"` — cosmetically visible **only** to the `underwriter` cosmetic role (`act:true`); `auditor`/`admin` (`act:false`) see the fallback. Mirrors the frozen `auth_rbac` semantics (only `underwriter` holds `RBAC_COMMIT`) as **value shapes**, never imported (BR-AG-4). |
| **Authorization is server-authoritative (defense-in-depth)** | **Compliant** | `RoleGate` is **cosmetic only** — it makes **no** authz decision. The real boundary is AUTHZ-1: `DecisionCommitService` independently re-checks `authorize(underwriter_id, RBAC_COMMIT)` and raises `UnauthorizedCommit` (→ 403) even if the cosmetic guard were bypassed. The client treats 403 as a **genuine error**, never a silent success (BR-AG-4 / BR-AG-6, Q3-A). |
| **No client-side authorization datum** | **Compliant** | `underwriter_id` is **never** sent from the client (BR-AG-5) — it is derived from the authenticated session server-side, so a client cannot commit *as another user* or self-elevate. `role` (from `GET /session`) is chrome/affordance only, not an authz input. |
| **Human-in-the-loop enforcement** | **Compliant** | No auto-commit path (BR-AG-1); an explicit confirm step (BR-AG-2) gates every commit; the confirm dialog is cancelable with zero side effects (BR-AG-3). A **commit failure must not silently or automatically retry the write** — an R5 error returns to `ready(idle)` and requires a fresh Approve→Confirm cycle (BR-AG-11). The advisory `Recommendation` becomes a human `decision` **only** through this deliberate action. |
| **Error / output hygiene (no leakage)** | **Compliant** | Failures surface via the shared envelope: `message` visible, `code` in a hidden testid node, `detail` **never** rendered (BR-AG-6). `normalizeError` guarantees a well-formed envelope so no raw exception (or backend internal) reaches the DOM. |
| **Advisory-only naming** | **Compliant** | UI copy uses "recommendation" for the system's advisory output and reserves "decision" for the human's committed action (`copy.js`); the human `approve` namespace is never conflated with the system `APPROVE` (BR-AG-7). |
| **Input validation (untrusted parsing)** | **N/A** | This unit parses no untrusted document/file; it reads a typed WIRE-1 JSON body and posts a fixed constant action. Input validation of the applicant profile is intake's scope (server-side). |
| **Prompt-injection / LLM safety** | **N/A** | No LLM anywhere in this unit — it issues no model call and renders no model output on the write path (no-LLM constraint). |
| **Secrets handling** | **N/A** | The client holds and sends no secret value; no credential/URL is referenced. Session/auth-handshake material is the composition root's concern (WIRE-1 deferred seam). |
| **Audit-trail persistence** | **N/A (delegated)** | This unit persists nothing. The full audit tuple (`rulebook_version`, `rule_results`, `timestamp`, `model_version`, `memo_hash`) is written server-side by audit-store's `DecisionCommitService` on the commit this action triggers — not this unit's responsibility. |

> **N/A rationale (non-blocking)**: the four N/A rows reflect that this is a **client-side read-context + single-action-write** unit with no untrusted parsing, no LLM, no secret material, and no persistence of its own. They are correctly N/A, not gaps.
