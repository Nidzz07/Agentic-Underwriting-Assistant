# `ui-override-form` (U8) — Functional Design · Business Rules

**Stage**: BUILD → per-unit loop → Functional Design → Part 2 · **Depth**: COMPREHENSIVE
**Date**: 2026-07-09
**Scope**: the invariant-bearing rules of the second UI **write path** — the interactive **override** affordance with a **mandatory reason**, firing WIRE-1 R5 with `action="override"`. Each rule has an explicit **condition** and, where checkable, the **mechanism** that will land at NFR/Code-Gen. No frozen artifact is re-opened. The one thing U7 deferred — the mandatory-reason gate — is realized here (BR-OVR-8).

---

## 1. Rules — BR-OVR-1 .. BR-OVR-12

### BR-OVR-1 — Advisory-only / no client finalize
**Condition**: no UI code path finalizes an outcome. A `CommittedDecision` exists **only** as the result of an **explicit human confirm → R5 override commit**; there is no auto-commit, no optimistic finalize, no timer/undo path that commits without a human action.
**Mechanism (checkable)**: the R5 POST is issued **only** from `OverrideConfirmDialog`'s `Confirm` handler; a structural/unit test asserts no other code path calls `submitOverride`, and that mount/read/reason-typing/`confirming`-toggle issue no POST.

### BR-OVR-2 — Confirm-before-commit
**Condition**: clicking the Override affordance **opens** `OverrideConfirmDialog`; it does **not** commit. The R5 POST fires **only** on the dialog's `Confirm` action (Q3-A).
**Mechanism (checkable)**: RTL test — clicking Override (with a non-blank reason) transitions to `confirming` and issues **zero** fetch calls on the injected double; only `Confirm` produces exactly one R5 POST.

### BR-OVR-3 — Cancelable-without-side-effect
**Condition**: opening or canceling `OverrideConfirmDialog` performs **no fetch, no commit, and no state mutation** beyond the local `confirming` flag; `Cancel` returns to `ready(idle)` with the reason **preserved** (BR-OVR-12).
**Mechanism (checkable)**: RTL test — open then Cancel; assert the injected transport double received **no** call across open+cancel, the rendered context is identical before and after, and the typed reason is still present.

### BR-OVR-4 — RoleGate cosmetic-only (not authorization)
**Condition**: `RoleGate can="act"` hides the override affordance from non-underwriters **cosmetically**; it is **not** an authorization decision. No client-side authz function is called; the frozen ui-shell `RoleGate` reads Role internally via `useCurrentRole()` and imports no backend (Q-inherited, SEC-4). The **real** gate is AUTHZ-1 (`DecisionCommitService` backend re-check).
**Mechanism (checkable)**: stub-`RoleProvider` RTL test — `underwriter` sees the affordance, `auditor`/`admin` see the fallback; a structural test asserts the unit imports no backend module and calls no authz function client-side.

### BR-OVR-5 — Session-derived committer (never client-sent)
**Condition**: the R5 body carries **only** `{ action: "override", reason }`. `underwriter_id` is **never** sent from the client — it is derived server-side from the authenticated session; `recommendation_id` comes from the R4 context and is placed in the **path** (WIRE1-Fold-1 / **OVR-Fold-3**).
**Mechanism (checkable)**: unit test on `buildOverrideRequest` — the body deep-equals `{ action: 'override', reason }` (has `action` + `reason`, **no** `underwriter_id` key); the path contains the R4-supplied `recommendation_id`.

### BR-OVR-6 — Per-status surfacing via the shared error envelope
**Condition**: R5 outcomes are surfaced **distinctly per documented status** (Q4-A): 200 → committed-confirmation; 409 → conflict (already-committed **or** blank-reason race/bypass tail — same code); 403 → not-permitted; 400/422 → generic invalid — **all** via the shared envelope with `message` VISIBLE, `code` in a `hidden` testid node, `detail` NEVER rendered.
**Mechanism (checkable)**: table-driven RTL tests — each status renders its distinct state; `message` is in the DOM, `code` only in the hidden testid node, `detail` absent from the DOM.

### BR-OVR-7 — CommitAction namespace-distinctness (override ≠ DECLINE-RECOMMEND)
**Condition**: the human `override` (lowercase, `CommitAction`) is **never** rendered as, serialized as, or conflated with the system `DECLINE-RECOMMEND` (uppercase, `Recommendation`) — nor with any system verdict (WIRE-1 §1). "Override" means the underwriter **disagrees**, not that the system declined.
**Mechanism (checkable)**: namespace test — the committed body/action value is the literal `"override"`; the display label is the frozen `COMMIT_ACTION_LABELS.override` (`'Override'`); a lint/unit check asserts the copy module and override builder never emit an uppercase `Recommendation` value (esp. `DECLINE-RECOMMEND`) as the human action, and the two namespaces share no key.

### BR-OVR-8 — Mandatory non-blank reason (a **non-authoritative** UX guard — the U8 core rule)
**Condition**: an override **requires a non-blank reason**. The UI **disables submission** (the Override affordance / the path to confirm) while the `reason` is blank under a **best-effort** `String.prototype.trim()`-is-empty check — so the client normally never sends a request the server would reject. This UI check is **explicitly non-authoritative** (FD-OVR-Fold-1): **CON-BR4 / BR-COMMIT-GATE stays single-sourced in `audit-store`** (`_gate`: `reason is None or reason.strip()==""` → reject); the UI guard is the same **defense-in-depth** relationship `RoleGate` has to AUTHZ-1 — it improves UX and blocks obviously-doomed requests but **decides nothing**. The UI trim is **NOT** claimed byte-identical to Python `str.strip()`; any divergence (e.g. a reason of only U+001C–U+001F or U+0085 passes the UI but the backend rejects it) **resolves to the backend via the generic 409** (BR-OVR-6). Inventing a custom Unicode-whitespace matcher to force byte-equality is deliberately **out of scope** (would over-build beyond the non-authoritative design).
**Mechanism (checkable)**: RTL tests — (a) with a blank / whitespace-only reason the Override→confirm path is disabled and **zero** POSTs are issued; (b) with a non-blank reason exactly one POST carrying that `reason` is issued on Confirm; (c) a unit test documents the trim divergence and asserts the guard is `trim()`-based (best-effort), with the backend `_gate` cited as authoritative.

### BR-OVR-9 — Confirmation renders without re-fetch
**Condition**: the committed-confirmation state renders from the **R5 `CommittedDecision` echo (incl. the committed `reason`) + the R4 context already in hand** — with **no separate R6/R7/history re-fetch** (**OVR-Fold-2**).
**Mechanism (checkable)**: RTL test — after a successful override, the confirmation shows `action=override` + the committed `reason` + `recommendation_id` + `underwriter_id` from the echo (plus the recommendation value from R4 context) while the injected transport receives **no** further call.

### BR-OVR-10 — Reference-not-own / decoupled
**Condition**: no backend import; no `ui-queue` / `ui-memo-view` / **`ui-approval-gate`** import; the unit uses its **own-local** `overrideFetchSeam` + `copy` (**OVR-Fold-4**). Cross-unit error-shape consistency comes from the shared WIRE-1 §4 contract, not shared code.
**Mechanism (checkable)**: StructuralGuard tests (`noBackendImport`, `noUiQueueImport`, `noMemoViewImport`, **`noApprovalGateImport`**, `noRouterImport`) — the established sibling convention, each non-vacuous (detector self-test).

### BR-OVR-11 — Error-recovery is cause-differentiated
**Condition**: error recovery differs by cause. An **R4 (context-read) failure's** `Retry` **re-issues the R4 read** for the same `applicationId`. An **R5 (override commit) failure** returns the state to **`ready(idle)`** with the reason **preserved** — **never an automatic resubmit** — requiring the underwriter to deliberately **re-open the confirm dialog and re-confirm** before any retry of the commit itself.
**Mechanism (checkable)**: RTL tests — (a) an R4-error `Retry` click re-issues **exactly one** R4 `GET` for the same `applicationId`; (b) an R5-error transitions to `ready(idle)` with **zero** automatic follow-up calls to `submitOverride`, the reason still present, requiring a fresh Override→Confirm cycle before the next commit attempt.

### BR-OVR-12 — Reason is preserved across cancel/error and echoed for review
**Condition**: the typed `reason` is **preserved** (not cleared) across a `Cancel` of the confirm dialog and across a commit error's return to `ready(idle)` — the underwriter never loses a justification to a cancel or a transient failure. The confirm dialog **echoes the reason** (read-only) so the human reviews exactly what will be recorded before confirming.
**Mechanism (checkable)**: RTL tests — (a) type a reason, open→Cancel, assert the reason is still in the input; (b) trigger a commit error, assert the reason is still in the input after returning to `ready(idle)`; (c) the confirm dialog renders the current reason text (read-only echo).

---

## 2. Rule index

| Rule | Title | Invariant class | Checkable-at |
|---|---|---|---|
| BR-OVR-1 | Advisory-only / no client finalize | advisory-only | NFR / Code-Gen (structural + unit) |
| BR-OVR-2 | Confirm-before-commit | human-in-the-loop | Code-Gen (RTL) |
| BR-OVR-3 | Cancelable-without-side-effect | human-in-the-loop | Code-Gen (RTL) |
| BR-OVR-4 | RoleGate cosmetic-only (not authz) | least-privilege / defense-in-depth | Code-Gen (stub-provider RTL + structural) |
| BR-OVR-5 | Session-derived committer | authorization integrity | Code-Gen (unit) |
| BR-OVR-6 | Per-status surfacing via shared envelope | error-hygiene | Code-Gen (table-driven RTL) |
| BR-OVR-7 | CommitAction namespace-distinctness (override ≠ DECLINE-RECOMMEND) | namespace-distinctness | NFR / Code-Gen (namespace + lint) |
| **BR-OVR-8** | **Mandatory non-blank reason (non-authoritative UX guard)** | **human-in-the-loop / defense-in-depth** | **Code-Gen (RTL + unit; trim-divergence documented)** |
| BR-OVR-9 | Confirmation without re-fetch | efficiency / scope split | Code-Gen (RTL) |
| BR-OVR-10 | Reference-not-own / decoupled | decoupling | NFR / Code-Gen (StructuralGuard) |
| BR-OVR-11 | Error-recovery is cause-differentiated | human-in-the-loop / no auto-resubmit | Code-Gen (RTL) |
| BR-OVR-12 | Reason preserved across cancel/error + echoed | human-in-the-loop / UX integrity | Code-Gen (RTL) |

> **Inheritance note**: BR-OVR-1..7 and BR-OVR-9..11 mirror the frozen U7 `BR-AG-1..11` (selective inheritance, not copy — the override/reason path is re-realized locally). **BR-OVR-8** (mandatory non-blank reason) and **BR-OVR-12** (reason preservation + echo) are the genuinely new rules this unit adds — the mandatory-reason gate U7 deliberately deferred.

---

## 3. Security-Guardrails compliance table

The **second UI unit with a real authorization-adjacent surface**, and the **first** to carry the mandatory-reason gate. The RBAC / authorization / human-in-the-loop rows carry **real content**, not N/A.

| Guardrail | Status | Rationale |
|---|---|---|
| **Least-privilege UI framing (RBAC-affordance)** | **Compliant** | The override affordance is wrapped in `RoleGate can="act"` — cosmetically visible **only** to the `underwriter` cosmetic role (`act:true`); `auditor`/`admin` (`act:false`) see the fallback. Mirrors the frozen `auth_rbac` semantics (only `underwriter` holds `RBAC_COMMIT`) as **value shapes**, never imported (BR-OVR-4). |
| **Authorization is server-authoritative (defense-in-depth)** | **Compliant** | `RoleGate` is **cosmetic only** — it makes **no** authz decision. The real boundary is AUTHZ-1: `DecisionCommitService` independently re-checks `authorize(underwriter_id, RBAC_COMMIT)` and raises `UnauthorizedCommit` (→ 403) even if the cosmetic guard were bypassed. The client treats 403 as a **genuine error**, never a silent success (BR-OVR-4 / BR-OVR-6). |
| **Mandatory-reason gate is server-authoritative (defense-in-depth)** | **Compliant** | The UI non-blank reason guard (BR-OVR-8) is **cosmetic/UX only** — it makes **no** authoritative validation decision. The real boundary is the backend `_gate` (`BR-COMMIT-GATE`: `reason.strip()==""` → `CommitRejected` → 409). A blank-reason override that slips past the UI (race / bypass / trim-divergence) is **rejected by the server** and surfaced generically. **CON-BR4 stays single-sourced in `audit-store`** — the UI never re-implements or claims to own the reason invariant. |
| **No client-side authorization datum** | **Compliant** | `underwriter_id` is **never** sent from the client (BR-OVR-5) — it is derived from the authenticated session server-side, so a client cannot commit *as another user* or self-elevate. `role` (from `GET /session`) is chrome/affordance only, not an authz input. |
| **Human-in-the-loop enforcement** | **Compliant** | No auto-commit path (BR-OVR-1); an explicit confirm step (BR-OVR-2) gates every commit; the confirm dialog is cancelable with zero side effects (BR-OVR-3) and **echoes the reason** for final review (BR-OVR-12); a **mandatory reason** is required (BR-OVR-8); a commit failure **must not** silently or automatically retry — an R5 error returns to `ready(idle)` with the reason preserved and requires a fresh Override→Confirm cycle (BR-OVR-11). The advisory `Recommendation` becomes a human `decision` **only** through this deliberate, justified action. |
| **Error / output hygiene (no leakage)** | **Compliant** | Failures surface via the shared envelope: `message` visible, `code` in a hidden testid node, `detail` **never** rendered (BR-OVR-6). `normalizeError` guarantees a well-formed envelope so no raw exception (or backend internal) reaches the DOM. The typed reason is user-authored free text; it is sent to the backend and echoed back — no secret/PII handling beyond what the underwriter enters. |
| **Advisory-only naming** | **Compliant** | UI copy uses "recommendation" for the system's advisory output and reserves "decision" for the human's committed action (`copy.js`); the human `override` namespace is **never** rendered as the system `DECLINE-RECOMMEND` (BR-OVR-7); the shared advisory-vocabulary lint applies UNMODIFIED. |
| **Input validation (untrusted parsing)** | **N/A (reason is user-authored, sent to a validating backend)** | This unit parses no untrusted document/file; the underwriter's `reason` is free text with **only** a non-blank UX check (BR-OVR-8) — all authoritative validation (incl. any length/content policy) is the backend's. It reads a typed WIRE-1 JSON body and posts a fixed action + reason. |
| **Prompt-injection / LLM safety** | **N/A** | No LLM anywhere in this unit — it issues no model call and renders no model output on the write path (no-LLM constraint). The reason text never enters an LLM path here. |
| **Secrets handling** | **N/A** | The client holds and sends no secret value; no credential/URL is referenced. Session/auth-handshake material is the composition root's concern (WIRE-1 deferred seam). |
| **Audit-trail persistence** | **N/A (delegated)** | This unit persists nothing. The full audit tuple (`rulebook_version`, `rule_results`, `timestamp`, `model_version`, `memo_hash`) + the committed `reason` are written server-side by audit-store's `DecisionCommitService` on the override this action triggers — not this unit's responsibility. |

> **N/A rationale (non-blocking)**: the N/A rows reflect that this is a **client-side read-context + single-justified-action-write** unit with no untrusted document parsing, no LLM, no secret material, and no persistence of its own. They are correctly N/A, not gaps. The reason free-text is validated authoritatively server-side.
