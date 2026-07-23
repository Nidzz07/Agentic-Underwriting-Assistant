# `ui-override-form` (U8) — Functional Design · Domain Entities

**Stage**: BUILD → per-unit loop → Functional Design → Part 2 · **Depth**: COMPREHENSIVE
**Date**: 2026-07-09
**Reference-not-own**: this unit **owns no backend and no persisted entity**. It consumes frozen WIRE-1 **shapes by value** and composes frozen ui-shell components. No frozen artifact is re-declared or re-opened. It re-realizes the sibling `fetchSeam` pattern **locally** (convention, not import — mirror-not-import; U7 `ui-approval-gate` is frozen). It is the **second and final write-path UI unit** — the `override` sibling of the frozen `approve` unit (U7).

---

## 1. Consumed frozen shapes (by value — none re-declared)

All shapes below are **read from WIRE-1** and the five built Pydantic schemas it grounds. The client keys on the **exact wire values** (WIRE-1 §1 — no re-casing, no remapping).

### 1.1 R4 read — recommendation context (`GET /applications/{application_id}/memo`)
This unit is **stand-alone** (Q5-A): it performs its **own** R4 fetch to obtain the recommendation context it will override against. It does **not** import `ui-memo-view`, and it does **not** import the frozen `ui-approval-gate` (mirror-not-import).

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
- `status: "ready"` → `recommendation_id` present → an **overridable** recommendation exists.
- `status: "pending"` / `recommendation_id: null` → **nothing to commit** → no override affordance / no reason input rendered (**OVR-Fold-5**, mirroring AG-Fold-5).
- This unit reads only the fields it needs for context + commit: `application_id`, `recommendation_id`, and (for display) `report.recommendation` / `report.confidence` via the frozen ui-shell badges. It renders **no** memo narrative (that is `ui-memo-view`'s scope).

### 1.2 R5 write request — **override with a mandatory reason** (`POST /recommendations/{recommendation_id}/commit`)
```
Commit request body = { "action": "override", "reason": <non-blank string> }
```
- **Override** (Q2-A): `action` is the constant `"override"`. Unlike the frozen approve path (which sends **no** `reason`), this unit sends a **`reason`** — the underwriter's mandatory justification.
- **`reason` is required and non-blank** iff `action == "override"` (WIRE-1 §5 / **BR-COMMIT-GATE**). The client applies a **best-effort non-blank UX guard** before enabling submission (§2, BR-OVR-8) — **non-authoritative**; the backend gate is the single source of truth (FD-OVR-Fold-1).
- **`underwriter_id` is NOT in the body** (WIRE1-Fold-1 / **OVR-Fold-3**). It is derived server-side from the authenticated session (the identity R1 `GET /session` returns). The client cannot commit *as another user*.
- **`recommendation_id`** is taken from the R4 context (§1.1) and placed in the **path**, matching `DecisionCommitService.commit(recommendation_id, underwriter_id, action, reason)`.

### 1.3 R5 success response — `CommittedDecision`
```
CommittedDecision = {
  recommendation_id: str,
  underwriter_id:    str,
  action:            "override",   # CommitAction value (lowercase — human namespace)
  reason:            str           # non-null on override (the justification just committed)
}
```
- This is a **thin linkage echo** — it deliberately omits `decision_id` / `timestamp` (those live on audit-store's `AuditRecord`, surfaced by **ui-history** R6/R7). The committed-confirmation state renders from **this echo + the R4 context already in hand** — **no re-fetch** (**OVR-Fold-2**). The confirmation echoes the committed `reason` back so the underwriter sees exactly what was recorded.

### 1.4 Error envelope (every non-2xx — WIRE-1 §4)
```
Error envelope = { "error": { "code": str, "message": str, "detail": object } }
```
The statuses this unit handles distinctly (Q4-A), all through the **one** envelope shape:

| HTTP | Meaning here | `code` slug | Client render |
|--:|---|---|---|
| **200** | override accepted | — (success body §1.3) | `CommittedConfirmation` |
| **403** | role-forbidden (AUTHZ-1 rejected — non-underwriter; only reachable if the cosmetic guard were bypassed) | `forbidden` | not-permitted error |
| **409** | conflict — **already-committed** *(normally reachable)* **or** a **blank-reason override** *(the race/bypass tail — see below)* (`BR-COMMIT-GATE`) | `commit_conflict` | conflict state |
| **400 / 422** | malformed / unprocessable request | `invalid_request` / `unprocessable` | generic invalid |

**409 is a live, non-dead handler (Q4-A / FD-OVR-Fold-1).** Two distinct server rejections share the single `commit_conflict` code:
1. **already-committed** — normally reachable (the recommendation was committed by an earlier action);
2. **blank-reason override** — with the client UX guard (BR-OVR-8) a blank reason is normally **unsubmittable**, so this fires only on a **race / bypass / trim-divergence tail** (see FD-OVR-Fold-1: the JS `trim()` guard is not byte-identical to the backend `str.strip()`; a reason of only U+001C–U+001F or U+0085 passes the UI but the backend rejects it).

Both surface **generically by `error.code`** — the client does **not** special-case blank vs already-committed beyond copy (they share the code). This is the AUTHZ-1 defense-in-depth shape applied to the **reason** gate: the server is authoritative; the UI guard decides nothing.

Rendering discipline (sibling convention, `CommitStateView`): **`message` VISIBLE**, **`code` in a `hidden` testid node** (assertion/console only), **`detail` NEVER rendered**. `normalizeError` (§2) guarantees a well-formed envelope so no raw exception is ever unpacked.

### 1.5 `CommitAction` — the human namespace (WIRE-1 §1 namespace-distinctness)
`"override"` (lowercase, `CommitAction`) is a **different value space** from the system `Recommendation` `APPROVE` / `REFER` / `DECLINE-RECOMMEND` (uppercase). This unit renders the human `override` affordance; it **never** serializes or displays the human `override` as the system `DECLINE-RECOMMEND`. The label is the frozen `COMMIT_ACTION_LABELS.override` (`'Override'`) from ui-shell copy — reused, not re-declared. **The human "override" (I disagree with the recommendation) must never read as a system verdict.**

---

## 2. Own-local module — `overrideFetchSeam.js` (R4 read + R5 override write)

Mirrors the frozen sibling `queue/fetchSeam` + `memoView/memoFetchSeam` + `approvalGate/commitFetchSeam` pattern (`createXFetch(transport) → seam`, `normalizeError`-to-WIRE-1-envelope) **re-realized locally** — it **does NOT import** any sibling seam (all frozen, kept decoupled; **OVR-Fold-4**). Cross-unit error-shape consistency comes from the **shared WIRE-1 §4 contract**, not shared code.

```
// overrideForm/overrideFetchSeam.js  (own-local — imports NO sibling seam, NO backend)

buildMemoRequest(applicationId)
  -> { method: 'GET',  path: `/applications/${applicationId}/memo` }

buildOverrideRequest(recommendationId, reason)          // override; reason is a REQUIRED positional param
  -> { method: 'POST', path: `/recommendations/${recommendationId}/commit`,
       body: { action: 'override', reason } }           // underwriter_id NOT in body

normalizeError(cause)   // ANY failure -> a well-formed { error: { code, message, detail } }
  // a parsed non-2xx body already well-formed passes through;
  // a transport error / missing / malformed body -> synthesized { code:'network_error', ... }

createOverrideFetch(transport)   // `transport` INJECTED + duck-typed (capturing double in tests;
                                 // real HTTP wired at the composition root — deferred / Build & Test)
  -> {
       fetchContext(applicationId): Promise<MemoView>                     // R4 read; rejects with envelope
       submitOverride(recommendationId, reason): Promise<CommittedDecision> // R5 write; rejects with envelope
     }
```
- **`buildOverrideRequest(recommendationId, reason)`** takes `reason` as a **required positional param** — unlike the frozen `buildCommitRequest(recommendationId)`, which structurally could emit **only** `{ action:'approve' }` and had no `reason` param at all. This is the genuine **widening** the override path requires (Q2-A) — a new builder, not a reuse of the frozen one.
- **`buildOverrideRequest` does NOT itself enforce non-blank** — it serializes whatever `reason` it is handed. The non-blank UX guard lives in `OverrideFormView` (BR-OVR-8), keeping validation testable independently of serialization (Q2-A rejects option C). The **backend** `_gate` remains the authoritative non-blank enforcement.
- Both operations **reject with a well-formed envelope** (never a raw exception), exactly like the sibling seams.
- The seam makes **no real network call itself** — the real transport is injected. **PERF-1**: R4 fetches a single bounded resource; R5 posts one commit. No list/all-rows path.

---

## 3. Own-local module — `copy.js` (override-local UI strings)

Local UI chrome kept OUT of the components (sibling convention). **NOT** domain-enum display labels — those are looked up by value via the reused ui-shell badges (`RecommendationBadge` / `ConfidenceBadge`) and `COMMIT_ACTION_LABELS.override`. **LINT-SUBJECT** (lands at NFR/Code-Gen): contains **no forbidden system-output vocabulary** (advisory-vocabulary lint, UNMODIFIED — reused single `FORBIDDEN_TERMS`) and **no value equal to a shell display label** (no-inline-label lint).

```
OVERRIDE_COPY = {
  loadingLabel:            'Loading recommendation',
  pendingMessage:          'No recommendation has been drafted yet for this application.',
  contextHeading:          'Recommendation from the rules engine',
  reasonPromptLabel:       'Reason for overriding this recommendation',   // the mandatory justification
  reasonPlaceholder:       'Explain why you are overriding this recommendation',
  reasonRequiredHint:      'A reason is required to override.',           // shown while the reason is blank
  overrideLabel:           'Override recommendation',                     // human action — override namespace
  confirmTitle:            'Confirm override',
  confirmBody:             'You are about to override this recommendation. Your override and reason will be recorded.',
  confirmReasonHeading:    'Your reason',                                 // echoes the reason for final review
  confirmSubmitLabel:      'Confirm override',
  confirmCancelLabel:      'Cancel',
  submittingLabel:         'Submitting override',
  committedTitle:          'Override recorded',
  committedByLabel:        'Committed by',
  committedReasonHeading:  'Reason recorded',
  conflictMessage:         'This recommendation has already been committed.',
  notPermittedMessage:     'You are not permitted to override recommendations.',
  retryLabel:              'Retry',
  backLabel:               'Back to review',
  unknownErrorMessage:     'Something went wrong.'
}
```
> **Advisory-clean by construction (Q-vocabulary hold, mirrors U7 NFR-AG-Fold-2).** The system output is called a **"recommendation"**, never a *decision*; the human's committed action is framed via **"override" / "reason" / "record" / "committed"** — honoring the reserved-word constraint **semantically** **without** the literal forbidden token **"decision"**, and **without** rendering the human `override` as the system `DECLINE-RECOMMEND`. This lets the shared `advisory-vocabulary` lint apply **UNMODIFIED** (single `FORBIDDEN_TERMS`, no carve-out, no second word-list). Every `OVERRIDE_COPY` string is advisory-clean (no bare `decision` / `approved` / `declined` / bare `DECLINE`).

---

## 4. Component inventory (composes frozen ui-shell primitives + `RoleGate`)

| Component | Kind | Responsibility | Composes (frozen ui-shell) |
|---|---|---|---|
| **`OverrideFormView`** | stateful orchestrator (the ONLY stateful component) | owns the client state machine (§5) **and the `reason` state** (Q3-A); own R4 read → renders context + gated override affordance + reason input → confirm → R5 write → confirmation/error; `overrideFetchSeam` **injected as a prop** (sibling convention); the **single call site** of `submitOverride` is this view's `onConfirm` (closes over the current `reason`), passed **only** to `OverrideConfirmDialog` | `AppFrame` / `Panel` |
| **`CommitStateView`** | presentational | the non-committed states: `loading` placeholder, `pending` "nothing to override", and the `error` envelope render (`message` visible / `code` testid-hidden / `detail` never); `Retry` re-runs R4 read | `Panel`, `ReadOnlyRegion` |
| **`RecommendationContext`** | presentational | read-only display of the recommendation being overridden (`report.recommendation` + `report.confidence`) via the frozen badges, framed as engine-authored/advisory | `ReadOnlyRegion`, `RecommendationBadge`, `ConfidenceBadge` |
| **`OverrideReasonInput`** | presentational — **controlled, capability-free** | the mandatory-reason `<textarea>`; takes `{ value, onChange }` (+ testid); **holds NO seam reference** — it echoes/edits text only (Q3-A). Holding reason *text* is **not** a commit capability (the refined invariant: capability = holding the *trigger/seam*, not the *payload*) | (plain textarea + `ReadOnlyRegion` for the hint) |
| **`OverrideAffordance`** | presentational | the override button; wrapped in `RoleGate can="act"` (cosmetic hide from non-underwriters); receives **only** an open-callback (`onOverride`) — **holds NO `submitOverride` reference**; clicking it **opens the confirm dialog — it does not commit** (BR-OVR-2); disabled while the reason fails the best-effort non-blank guard (BR-OVR-8) | `RoleGate` (`{ can:'act', children, fallback }`) |
| **`OverrideConfirmDialog`** | presentational | the Q3-A explicit confirm step; **sole holder of the commit trigger** — its `onConfirm` IS the wired `submitOverride` invocation (supplied only here by the view) = **the single call site**; **echoes the `reason`** (read-only) for final review; **pure client-side toggle** — rendering/canceling it triggers **no fetch, no commit, no state mutation** beyond the local `confirming` flag; `Confirm` fires the R5 write, `Cancel` returns to `ready(idle)` with the reason **preserved** | `Panel`, `ReadOnlyRegion` |
| **`CommittedConfirmation`** | presentational — `{ decision, context }`-only | the success state; renders from the R5 `CommittedDecision` echo + R4 context in hand — **no re-fetch** (OVR-Fold-2); shows `action=override`, the committed `reason`, `recommendation_id`, `underwriter_id`, and the recommendation value | `Panel`, `RecommendationBadge` |

**RoleGate composition (reused pattern).** `<RoleGate can="act">` reads the current Role **internally** via `useCurrentRole()` (no `role` prop). For `underwriter` (`act:true`) the override affordance renders; for `auditor` / `admin` (`act:false`) it renders the `fallback` (nothing / a read-only note). This is **cosmetic only** — see `business-logic-model.md` §3 and BR-OVR-4.

**By-construction guarantees (Q3-A; StructuralGuard, FD-OVR-Fold-2):** `OverrideAffordance` holds only `onOverride` (no `submitOverride`/seam ref); `OverrideReasonInput` holds only `{ value, onChange }` (**no seam ref** — the NEW capability-free component U7 had no analog for); `OverrideConfirmDialog` is the **sole** `onConfirm` holder = single call site; `CommittedConfirmation` is `{ decision, context }`-only (no seam). Each is enforced by a StructuralGuard scan at NFR/Code-Gen, mirroring U7's `refNotOwn.imports.test.js` and growing by one for `OverrideReasonInput`.

---

## 5. Client state machine (full)

```
        (mount)
           │
           ▼
   ┌───────────────┐   R4 reject (envelope)
   │    loading    │ ─────────────────────────► errorRead
   └───────────────┘                                │ Retry re-issues R4 read (same applicationId)
       │ R4 resolve                                 ▼
       │                                          loading
       ├── status "pending" / recommendation_id null ──► pending   (no override affordance, no reason input — OVR-Fold-5)
       │
       └── status "ready" ──► ready(idle)
                                  │   shows: recommendation context + OverrideReasonInput (controlled) + Override button
                                  │   Override button is ENABLED only when reason passes the best-effort non-blank guard (BR-OVR-8)
                                  │
                (type reason ─ updates reason state; button enable/disable tracks it)
                                  │
                (click Override — RoleGate can=act gates the button; reason non-blank required)
                                  ▼
                             confirming          ◄── PURE client-side toggle; NO fetch / NO commit /
                                  │                   NO state mutation beyond the dialog flag; dialog ECHOES the reason
                    ┌── Cancel ───┤                   (Cancel PRESERVES the reason — BR-OVR-12)
                    │             │ Confirm
              ready(idle)         ▼
              (reason kept)   submitting  ── R5 POST { action:"override", reason } via submitOverride(recommendationId, reason) ──┐
                                  │                                                                                                │
                    ┌─────────────┼──────────────────────────────────────────────┐                                             │
                    ▼             ▼                                               ▼                                             │
                committed    errorCommit (403 not-permitted /                errorCommit (400/422                               │
              (CommittedDecision  409 conflict = already-committed             generic)                                        │
               echo incl. reason  OR blank-reason race/bypass tail)              │                                             │
               + R4 context;          │                                          │                                             │
               NO re-fetch)  ◄────────┴── returns to ready(idle), reason PRESERVED, NO auto-resubmit (BR-OVR-11) ───────────────┘
                    │
              (terminal — no re-override; a committed recommendation is final for this unit)
```

- **States**: `loading` → `ready(idle)` → `confirming` → `submitting` → `{ committed | errorCommit }`, plus `pending` and `errorRead`.
- **`ready(idle)` carries the reason input**: the underwriter types the justification; the `reason` state lives in `OverrideFormView`; the Override button's enablement tracks the best-effort non-blank guard.
- **`confirming` is a pure client-side toggle** with **no side effects** — the R5 override fires **only** on the dialog's `Confirm`, never on the Override click, never on dialog open, never on Cancel. The dialog **echoes the reason** so the human reviews exactly what will be recorded (reinforcing the human-in-the-loop deliberateness).
- **Reason preservation (BR-OVR-12)**: `Cancel` and a commit error both return to `ready(idle)` with the typed `reason` **preserved** — the underwriter never loses a justification to a cancel or a transient failure; they re-open and re-confirm deliberately (never an auto-resubmit).
- **`errorRead` Retry**: on a *read* (R4) error, `Retry` re-runs the R4 read (same `applicationId`). On a *commit* (R5) error, the state returns to `ready(idle)` (reason preserved) so the underwriter re-confirms deliberately.
- Orchestration mirrors the frozen `ApprovalGateView` / `MemoView` pattern (`useState`/`useEffect`/`useCallback`, injected seam as a prop, `Panel` wrapping) — convention, not import.

---

## 6. Boundary (what this unit does NOT do)

- **No authorization decision** — `RoleGate` is cosmetic; AUTHZ-1 (`DecisionCommitService` backend re-check) is the real gate.
- **No authoritative reason validation** — the UI non-blank guard is **best-effort / non-authoritative** (FD-OVR-Fold-1); the backend `_gate` (`reason.strip()==""` → reject) is the single source of truth. A UI↔backend trim disagreement resolves to the backend via the generic 409.
- **No memo rendering** — narrative/citations/missing-info are `ui-memo-view`'s scope; this unit shows only the recommendation being overridden.
- **No approve path** — `action="approve"` is the frozen U7 `ui-approval-gate`. This unit renders **only** the `override` affordance + reason input.
- **No combined approve+override screen** — that is a **deferred composition-root concern** (Q6-A / FD-OVR-Fold-3): `OverrideFormView({ overrideFetchSeam, applicationId })` is a self-contained view a future composition root mounts alongside the frozen `ApprovalGateView`; **no speculative composition prop is added now**.
- **No decision receipt with `decision_id`/`timestamp`** — that is `ui-history` (R6/R7).
- **No LLM, no rule evaluation, no persistence** — the unit only reads context and posts one explicit human action + reason.
- **No backend import, no sibling-unit import** — own-local seam + copy; enforced by StructuralGuard tests at NFR/Code-Gen.
