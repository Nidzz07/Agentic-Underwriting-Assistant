# `ui-approval-gate` (U7) — Functional Design · Domain Entities

**Stage**: BUILD → per-unit loop → Functional Design → Part 2 · **Depth**: COMPREHENSIVE
**Date**: 2026-07-09
**Reference-not-own**: this unit **owns no backend and no persisted entity**. It consumes frozen WIRE-1 **shapes by value** and composes frozen ui-shell components. No frozen artifact is re-declared or re-opened. It re-realizes the sibling `fetchSeam` pattern **locally** (convention, not import — AG-Fold-4).

---

## 1. Consumed frozen shapes (by value — none re-declared)

All shapes below are **read from WIRE-1** and the five built Pydantic schemas it grounds. The client keys on the **exact wire values** (WIRE-1 §1 — no re-casing, no remapping).

### 1.1 R4 read — recommendation context (`GET /applications/{application_id}/memo`)
This unit is **stand-alone** (Q5-A): it performs its **own** R4 fetch to obtain the recommendation context it will commit against. It does **not** import `ui-memo-view`.

```
MemoView (R4 body) = {
  application_id:     str,
  recommendation_id:  str | null,
  status:             "ready" | "pending",
  profile:            ApplicantProfile | null,
  report:             RuleResultReport | null,
  memo:               DecisionMemo | null
}
```
- `status: "ready"` → `recommendation_id` present → an **approvable** recommendation exists.
- `status: "pending"` / `recommendation_id: null` → **nothing to commit** → no approve affordance rendered (**AG-Fold-5**).
- This unit reads only the fields it needs for context + commit: `application_id`, `recommendation_id`, and (for display) `report.recommendation` / `report.confidence` via the frozen ui-shell badges. It renders **no** memo narrative (that is `ui-memo-view`'s scope).

### 1.2 R5 write request — **approve-only** (`POST /recommendations/{recommendation_id}/commit`)
```
Commit request body = { "action": "approve" }
```
- **Approve-only** (Q6-A): `action` is the constant `"approve"`. **No `reason`** field is sent (reason is mandatory only for `override`, deferred to U8 `ui-override-form`).
- **`underwriter_id` is NOT in the body** (WIRE1-Fold-1 / **AG-Fold-3**). It is derived server-side from the authenticated session (the identity R1 `GET /session` returns). The client cannot commit *as another user*.
- **`recommendation_id`** is taken from the R4 context (§1.1) and placed in the **path**, matching `DecisionCommitService.commit(recommendation_id, underwriter_id, action, reason)`.

### 1.3 R5 success response — `CommittedDecision`
```
CommittedDecision = {
  recommendation_id: str,
  underwriter_id:    str,
  action:            "approve",   # CommitAction value (lowercase — human namespace)
  reason:            str | null   # null on approve
}
```
- This is a **thin linkage echo** — it deliberately omits `decision_id` / `timestamp` (those live on audit-store's `AuditRecord`, surfaced by **ui-history** R6/R7). The committed-confirmation state renders from **this echo + the R4 context already in hand** — **no re-fetch** (**AG-Fold-2**).

### 1.4 Error envelope (every non-2xx — WIRE-1 §4)
```
Error envelope = { "error": { "code": str, "message": str, "detail": object } }
```
The four statuses this unit handles distinctly (Q4-A), all through the **one** envelope shape:

| HTTP | Meaning here | `code` slug | Client render |
|--:|---|---|---|
| **200** | commit accepted | — (success body §1.3) | `CommittedConfirmation` |
| **403** | role-forbidden (AUTHZ-1 rejected — non-underwriter; only reachable if the cosmetic guard were bypassed) | `forbidden` | not-permitted error |
| **409** | already-committed / conflict (`BR-COMMIT-GATE`; a blank-reason override cannot arise here — approve-only) | `commit_conflict` | already-committed / conflict state |
| **400 / 422** | malformed / unprocessable request | `invalid_request` / `unprocessable` | generic invalid |

Rendering discipline (sibling convention, `MemoStateView`): **`message` VISIBLE**, **`code` in a `hidden` testid node** (assertion/console only), **`detail` NEVER rendered**. `normalizeError` (§2) guarantees a well-formed envelope so no raw exception is ever unpacked.

### 1.5 `CommitAction` — the human namespace (WIRE-1 §1 namespace-distinctness)
`"approve"` (lowercase, `CommitAction`) is a **different value space** from the system `Recommendation` `APPROVE` / `REFER` / `DECLINE-RECOMMEND` (uppercase). This unit renders the human `approve` affordance; it **never** serializes or displays it as the system `APPROVE`. `override` (≠ `DECLINE-RECOMMEND`) is deferred to U8.

---

## 2. Own-local module — `commitFetchSeam.js` (R4 read + R5 write)

Mirrors the frozen sibling `queue/fetchSeam` + `memoView/memoFetchSeam` pattern (`createXFetch(transport) → seam`, `normalizeError`-to-WIRE-1-envelope) **re-realized locally** — it **does NOT import** either sibling seam (both frozen, kept decoupled; **AG-Fold-4**). Cross-unit error-shape consistency comes from the **shared WIRE-1 §4 contract**, not shared code.

```
// approvalGate/commitFetchSeam.js  (own-local — imports NO sibling seam, NO backend)

buildMemoRequest(applicationId)
  -> { method: 'GET',  path: `/applications/${applicationId}/memo` }

buildCommitRequest(recommendationId)                    // approve-only; underwriter_id NOT in body
  -> { method: 'POST', path: `/recommendations/${recommendationId}/commit`,
       body: { action: 'approve' } }

normalizeError(cause)   // ANY failure -> a well-formed { error: { code, message, detail } }
  // a parsed non-2xx body already well-formed passes through;
  // a transport error / missing / malformed body -> synthesized { code:'network_error', ... }

createCommitFetch(transport)   // `transport` INJECTED + duck-typed (capturing double in tests;
                               // real HTTP wired at the composition root — deferred / Build & Test)
  -> {
       fetchContext(applicationId): Promise<MemoView>            // R4 read; rejects with envelope
       submitApprove(recommendationId): Promise<CommittedDecision> // R5 write; rejects with envelope
     }
```
- Both operations **reject with a well-formed envelope** (never a raw exception), exactly like the sibling seams.
- `submitApprove` sends **only** `{ action: 'approve' }` — enforcing AG-Fold-3 at the request-builder level.
- The seam makes **no real network call itself** — the real transport is injected. **PERF-1**: R4 fetches a single bounded resource; R5 posts one commit. No list/all-rows path.

---

## 3. Own-local module — `copy.js` (memo-local UI strings)

Local UI chrome kept OUT of the components (sibling convention). **NOT** domain-enum display labels — those are looked up by value via the reused ui-shell badges (`RecommendationBadge` / `ConfidenceBadge`). **LINT-SUBJECT** (lands at NFR/Code-Gen): contains **no forbidden system-output vocabulary** (advisory-vocabulary lint) and **no value equal to a shell display label** (no-inline-label lint).

```
APPROVAL_COPY = {
  loadingLabel:            'Loading recommendation',
  pendingMessage:          'No recommendation has been drafted yet for this application.',
  approveLabel:            'Approve recommendation',        // human action — approve namespace
  confirmTitle:            'Confirm approval',
  confirmBody:             'You are about to approve this recommendation. Your approval will be recorded.',
  confirmSubmitLabel:      'Confirm approval',
  confirmCancelLabel:      'Cancel',
  submittingLabel:         'Submitting approval',
  committedTitle:          'Approval recorded',
  committedByLabel:        'Committed by',
  conflictMessage:         'This recommendation has already been committed.',
  notPermittedMessage:     'You are not permitted to approve recommendations.',
  retryLabel:              'Retry',
  unknownErrorMessage:     'Something went wrong.'
}
```
> Wording holds (NFR Q4-A): uses **"recommendation"** for the system's advisory output and **never** applies a finalizing token to it; the human's committed action is framed via **"approve" / "approval" / "record" / "committed"**, honoring the reserved-word constraint **semantically** — the system recommendation is never called a *decision* — **without** using the literal forbidden token **"decision"** in static copy. This lets the shared `advisory-vocabulary` lint apply **unmodified** (single `FORBIDDEN_TERMS`, no carve-out). All 14 `APPROVAL_COPY` strings are advisory-clean (no bare `decision` / `approved` / `declined` / bare `DECLINE`).

---

## 4. Component inventory (composes frozen ui-shell primitives + `RoleGate`)

| Component | Kind | Responsibility | Composes (frozen ui-shell) |
|---|---|---|---|
| **`ApprovalGateView`** | stateful orchestrator (the ONLY stateful component) | owns the client state machine (§5); own R4 read → renders context + gated approve affordance → confirm → R5 write → confirmation/error; `commitFetchSeam` **injected as a prop** (sibling convention) | `AppFrame` / `Panel` |
| **`CommitStateView`** | presentational | the non-committed states: `loading` placeholder, `pending` "nothing to approve", and the `error` envelope render (`message` visible / `code` testid-hidden / `detail` never); `Retry` re-runs R4 read | `Panel`, `ReadOnlyRegion` |
| **`RecommendationContext`** | presentational | read-only display of the recommendation being approved (`report.recommendation` + `report.confidence`) via the frozen badges, framed as engine-authored/advisory | `ReadOnlyRegion`, `RecommendationBadge`, `ConfidenceBadge` |
| **`ApproveAffordance`** | presentational | the approve button, wrapped in `RoleGate can="act"` (cosmetic hide from non-underwriters); clicking it **opens the confirm dialog — it does not commit** (BR-AG-2) | `RoleGate` (`{ can:'act', children, fallback }`) |
| **`CommitConfirmDialog`** | presentational | the Q2-A explicit confirm step; **pure client-side toggle** — rendering/canceling it triggers **no fetch, no commit, no state mutation** beyond the local `confirming` flag (**AG-Fold-1**); `Confirm` fires the R5 write, `Cancel` returns to `ready(idle)` | `Panel` |
| **`CommittedConfirmation`** | presentational | the success state; renders from the R5 `CommittedDecision` echo + R4 context in hand — **no re-fetch** (AG-Fold-2); shows `action=approve`, `recommendation_id`, `underwriter_id`, and the recommendation value | `Panel`, `RecommendationBadge` |

**RoleGate composition (first real use).** `<RoleGate can="act">` reads the current Role **internally** via `useCurrentRole()` (no `role` prop). For `underwriter` (`act:true`) the approve affordance renders; for `auditor` / `admin` (`act:false`) it renders the `fallback` (nothing / a read-only note). This is **cosmetic only** — see `business-logic-model.md` §3 and BR-AG-4.

---

## 5. Client state machine (full)

```
        (mount)
           │
           ▼
   ┌───────────────┐   R4 reject (envelope)
   │    loading    │ ─────────────────────────► error
   └───────────────┘
       │ R4 resolve
       ├── status "pending" / recommendation_id null ──► pending      (no approve affordance — AG-Fold-5)
       │
       └── status "ready" ──► ready(idle)
                                  │
                (click Approve — RoleGate can=act gates the button)
                                  ▼
                             confirming            ◄── PURE client-side toggle; NO fetch / NO commit /
                                  │                    NO state mutation beyond the dialog flag (AG-Fold-1)
                    ┌── Cancel ───┤
                    │             │ Confirm
              ready(idle)         ▼
                              submitting  ── R5 POST { action:"approve" } ──┐
                                  │                                          │
                    ┌─────────────┼──────────────────────────────┐         │
                    ▼             ▼                               ▼         │
                committed    error(403 not-permitted /       error(400/422 │
              (CommittedDecision  409 already-committed)       generic)     │
               echo + R4 context;                                          │
               NO re-fetch)  ◄──────────────────────────────────────────────┘
                    │
              (terminal — no re-approve; a committed recommendation is final for this unit)
```

- **States**: `loading` → `ready(idle)` → `confirming` → `submitting` → `{ committed | error }`, plus `pending`.
- **`confirming` is a pure client-side toggle** with **no side effects** (AG-Fold-1) — the single most important behavioral invariant of this unit: the R5 commit fires **only** on the dialog's `Confirm`, never on the initial Approve click.
- **`error` Retry**: on a *read* (R4) error, `Retry` re-runs the R4 read (same `applicationId`). On a *commit* (R5) error, the state returns to `ready(idle)` so the underwriter can re-confirm deliberately (never an auto-resubmit).
- Orchestration mirrors the frozen `MemoView` pattern (`useState`/`useEffect`/`useCallback`, injected seam as a prop, `Panel` wrapping) — convention, not import.

---

## 6. Boundary (what this unit does NOT do)

- **No authorization decision** — `RoleGate` is cosmetic; AUTHZ-1 (`DecisionCommitService` backend re-check) is the real gate.
- **No memo rendering** — narrative/citations/missing-info are `ui-memo-view`'s scope; this unit shows only the recommendation being approved.
- **No override** — `action="override"` + mandatory reason is U8 `ui-override-form`.
- **No decision receipt with `decision_id`/`timestamp`** — that is `ui-history` (R6/R7).
- **No LLM, no rule evaluation, no persistence** — the unit only reads context and posts one explicit human action.
- **No backend import, no sibling-unit import** — own-local seam + copy; enforced by StructuralGuard tests at NFR/Code-Gen.
