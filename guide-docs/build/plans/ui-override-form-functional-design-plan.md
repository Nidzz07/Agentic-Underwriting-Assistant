# Functional Design — Part 1 (PLAN) · `ui-override-form` (U8)

**Stage**: BUILD → per-unit loop → Functional Design **Part 1 (Planning ONLY — NO FD artifact generated)** · **Date**: 2026-07-09
**Unit**: `ui-override-form` (U8; C5; Phase 1) — the **override-with-mandatory-reason** UI facet. **US-UI-5 · FR-UI-4 · CON-BR4 (UI facet).**
**Status**: **STOPPED at the plan-file gate** — awaiting the six `[Answer]` tags below before any FD artifact is written.

This is the **second and final write-path UI unit** and the **only one that exercises the mandatory-reason gate**. It is the sibling of the now-frozen `ui-approval-gate` (U7): it selectively **inherits** U7's proven patterns rather than copying them wholesale, and it introduces the one thing U7 deliberately deferred — the `action="override"` path with a **mandatory non-blank reason**.

---

## §0 — DISCOVER-carryover check (CLEAN)

- **No** `guide-docs/build/ui-override-form/` directory.
- **No** `frontend/src/overrideForm/` (or any override) source.
- **No** `ui-override-form-*.md` plan file.

→ Greenfield unit. No partial artifact to reconcile.

## §1 — Frozen contracts re-read (consumed **by value / by shape**, never edited)

| Source (frozen) | What U8 consumes | Key fact for U8 |
|---|---|---|
| `unit-of-work.md §U8` | classification | **comprehensive / invariant-bearing**; deps `ui-shell` + `auth-rbac` + `audit-store`; **CON-BR4 write-enforcement is single-sourced in `audit-store`** — the UI is a *consuming facet*, not a re-implementer (§4 realization). |
| `audit_store/commit_service.py` `DecisionCommitService._gate` | the authoritative reason gate | override rejected **iff** `reason is None or reason.strip() == ""` — **trim-then-empty** (whitespace-only = blank). Plus AUTHZ-1 independent authz re-check. This rejection surfaces as WIRE-1 **409 `commit_conflict`**. |
| `WIRE-1 §3/§4/§5` R5 | the wire | `POST /recommendations/{recommendation_id}/commit`, body `{ action, reason }` where **`reason` is required-non-blank iff `action=="override"`**; `underwriter_id` from the authenticated session (never the body); **underwriter-only** (403 otherwise); blank-reason override → **409**. |
| `shell/components/RoleGate.jsx` | cosmetic affordance guard | `RoleGate can="act"` — `underwriter {act:true}` / `auditor {act:false}` / `admin {act:false}`; reads role **internally** via `useCurrentRole()` (no `role` prop). **Cosmetic only** — AUTHZ-1 is the real gate. |
| `shell/session/roleContext.js` | role value-shape | `currentRole ∈ {underwriter, auditor, admin} \| null`. |
| `shell/copy/index.js` | display labels + advisory vocabulary | **`COMMIT_ACTION_LABELS.override = 'Override'` is ALREADY frozen** (U8 reuses, does not add). `ADVISORY_VOCABULARY` = system output is a *recommendation*. The human **`override`** must **never** render as the system `DECLINE-RECOMMEND`. |
| `approvalGate/commitFetchSeam.js` (U7, frozen) | seam **shape**, mirror-not-import | `createCommitFetch(transport) → { fetchContext, submitApprove }`; **`buildCommitRequest(recommendationId)` STRUCTURALLY emits only `{ action:'approve' }` — there is NO `reason` param**, so U8 genuinely needs a *widened/new* builder (Q2). |
| `approvalGate/ApproveAffordance.jsx` (U7, frozen) | by-construction pattern | `{ onApprove }`-only — holds no seam/submit reference → cannot commit (structural, not conventional). |
| `approvalGate/CommitConfirmDialog.jsx` (U7, frozen) | single-call-site pattern | the **sole** holder of `onConfirm` = **the single call site** of the commit. |
| `approvalGate/ApprovalGateView.jsx` (U7, frozen) | state machine + standalone read | owns `loading → pending/errorRead / ready → confirming → submitting → committed/errorCommit`; **Q5-A**: it did its **own R4 read**, decoupled from `ui-memo-view`. |

**Domain guardrails (underwriting-rules skill) binding on U8**: advisory-only vocabulary (constraint 1 — "recommendation" for the system, "decision" reserved for the human's committed record; override copy must not read as a system verdict); human-in-the-loop gate with a **mandatory override reason** (constraint 2 — the heart of this unit); no LLM; no TypeScript.

## §2 — Depth recommendation — **COMPREHENSIVE** (confirm at Q1)

`unit-of-work.md §U8` classifies this unit **comprehensive (invariant-bearing)** — same tier as U7 — because it carries **CON-BR4 / FR-UI-4** and is the write-path unit that actually exercises the mandatory-reason gate. This is classification-forced, not a per-unit "lighter" candidate. **Recommendation: COMPREHENSIVE.**

## §3 — Proposed approach (CONTINGENT on the answers below)

A self-contained `frontend/src/overrideForm/` unit mirroring U7's realized structure (mirror-not-import; U7 is frozen), diverging **only** where the override/reason path requires it:

```
overrideForm/
  copy.js                         # C9-analog: override-local strings, advisory-clean (reuses shell COMMIT_ACTION_LABELS.override)
  overrideFetchSeam.js            # C2-analog: createOverrideFetch(transport) -> { fetchContext, submitOverride }   [Q2]
  OverrideFormView.jsx            # C1-analog: sole stateful orchestrator; owns the machine + the reason state [Q3]; single call site [Q3]
  components/
    RecommendationContext.jsx     # C4-analog: read-only rec/confidence from the own R4 read [Q5]
    OverrideReasonInput.jsx       # NEW: the mandatory-reason <textarea> (advisory-clean label) — capability-free input [Q3]
    OverrideAffordance.jsx        # C5-analog: opens the confirm flow; holds NO submitOverride reference [Q3]
    OverrideConfirmDialog.jsx     # C6-analog: sole onConfirm holder = single call site; onConfirm closes over reason [Q3]
    CommitStateView.jsx           # C3-analog: loading / pending / errorRead / errorCommit envelope render
    CommittedConfirmation.jsx     # C7-analog: {decision, context}-only success render (action='override' + reason echo)
```

The precise shape of `overrideFetchSeam`/`buildOverrideRequest` (Q2), where the reason state lives relative to the single-call-site discipline (Q3), how 409 is surfaced (Q4), the own-vs-shared R4 read (Q5), and the standalone-vs-combined view boundary (Q6) are **open** — worked through below rather than assumed transferable from U7.

---

## §4 — Open design questions (answer each `[Answer]:` tag with a letter)

### Q1 — Depth
Confirm the depth for `ui-override-form`.
- **A. Comprehensive** *(Recommended)* — classification-forced (invariant-bearing, CON-BR4/FR-UI-4; the write-path unit that exercises the mandatory-reason gate).
- **B. Standard** — treat as a display-ish unit. *(Rejected — contradicts the §U8 classification.)*
- **C. Minimal.** *(Rejected.)*

`[Answer]:` A

---

### Q2 — Shape of the widened commit-request builder + **where non-blankness is enforced**
The frozen `buildCommitRequest(recommendationId)` can emit only `{action:'approve'}` — no `reason` param. U8 needs an override builder. **Two coupled decisions**: (a) the builder's signature, and (b) which layer enforces non-blank reason — and if the UI enforces it, whether that is a *second authoritative gate* or a *non-authoritative UX guard*.

- **A. New own-local `overrideFetchSeam` + reason-carrying builder + UI guard as non-authoritative defense-in-depth** *(Recommended)*.
  `overrideForm/overrideFetchSeam.js` mirrors (does **not** import) U7's frozen seam: `createOverrideFetch(transport) → { fetchContext, submitOverride }`, with `buildOverrideRequest(recommendationId, reason)` taking `reason` as a **required positional param** and emitting `{ action:'override', reason }`. The **UI enforces non-blank** using **trim-then-empty** semantics **identical to the backend** (`reason.trim() === ''` ⇔ backend `reason.strip() == ""`) as a **first / UX gate** — it disables submission for a blank reason so the client never sends a request the server would 409 on. This UI check is **explicitly non-authoritative**: CON-BR4 stays **single-sourced in `audit-store`** (per unit-of-work §4); the client guard is the same *defense-in-depth* relationship RoleGate has to AUTHZ-1 — it improves UX and blocks obviously-doomed requests but decides nothing. (Mirror-not-import keeps U8 decoupled from the frozen U7 seam.)
- **B. Optional `reason` param, enforcement deferred entirely to the server.** `buildOverrideRequest(recommendationId, reason?)`; the UI never blocks, always submits, and surfaces the 409. *(Simplest, but it knowingly sends bad requests and gives no live feedback — poor UX for a mandatory field.)*
- **C. Enforce only inside the request-builder (builder throws on blank).** Couples validation to serialization; awkward for live per-keystroke UX feedback and harder to test the input independently. *(Rejected.)*

**Note (binding whichever is chosen):** the UI's blank definition **must** match the backend's `str.strip()` trim-then-empty, or the two gates disagree (a whitespace-only reason the UI accepts would surprise-409, or vice-versa).

`[Answer]:` A

---

### Q3 — How the reason state threads through the by-construction **single-call-site** discipline
U7's guarantee: `ApproveAffordance` holds only `onApprove` and cannot commit; `CommitConfirmDialog` is the **sole** `onConfirm` holder = the single call site. Adding a mandatory reason introduces **new pre-commit state** (the reason text). Where does it live, and does that weaken "no commit capability"?

- **A. Reason state in the orchestrator; affordance stays capability-free; single call site preserved** *(Recommended)*.
  `OverrideFormView` (the sole stateful component) owns the `reason` state. The `OverrideReasonInput` is a **controlled, capability-free** `<textarea>` (holds/echoes text, holds **no** seam reference). `OverrideAffordance` receives only an open-callback (`{ onOverride }`-analog) — it opens the confirm flow and, like U7's affordance, **holds no `submitOverride` reference**. `submitOverride` is invoked in **exactly one place** — the view's `onConfirm`, which **closes over the current `reason`** — and `onConfirm` is passed **only** to `OverrideConfirmDialog`. **Refinement of the invariant:** "no commit capability" means *holds no seam/submit reference* — it is about the **trigger**, not the **payload**. Holding reason *text* is not a commit capability; the single-call-site discipline is therefore **unchanged**, just parameterized by `reason`.
- **B. The confirm dialog owns the reason input too.** `OverrideConfirmDialog` holds both the `<textarea>` and the Confirm button; its handler calls `onConfirm(reason)`. Keeps reason + trigger co-located (arguably the tightest single-owner), but the dialog now holds input state and the reason can't be shown/edited in the ready region before confirming. *(Viable; weaker for a "review your reason, then confirm" flow.)*
- **C. The affordance holds the reason text and opens the dialog with it.** Makes the affordance a combined input+opener. *(Muddies single-responsibility; "no commit capability" technically still holds but the affordance stops being a pure opener — rejected.)*

`[Answer]:` A

---

### Q4 — Surfacing the **409 blank-reason** response (a new client-visible path)
Given a UI guard (Q2-A) that blocks blank submissions, is 409-for-blank-reason even reachable, and how is it surfaced?

- **A. 409 handled generically (defense-in-depth mirror of AUTHZ-1); blank-reason-409 is a race/bypass tail, but 409 is still live because it also covers already-committed** *(Recommended)*.
  With the Q2-A client guard, a **blank-reason override is normally unsubmittable**, so 409-*for-blank* fires only on a race/bypass (guard skipped, stale state, direct API call) — exactly the AUTHZ-1 shape (client guard cosmetic, server `BR-COMMIT-GATE` authoritative). But the **409 handler is not dead code**: WIRE-1 §4 maps **already-committed** to the *same* `409 commit_conflict`, which **is** normally reachable. So U8 surfaces 409 **generically** by `error.code` (a conflict message), mirroring U7's ERROR-1 table (which already handled 409 already-committed) — **no special-casing** blank vs already-committed beyond copy, since both share the code. The reason gate is thus treated **identically to the authz gate**: the server is the real gate; the UI never assumes its own guard is authoritative.
- **B. Treat 409-blank as unreachable and rely on the generic error state.** Essentially the tail of A without stating the AUTHZ-1 parallel. *(A states it explicitly — preferred.)*
- **C. No client guard; 409-blank is a normal path surfaced with a specific "reason required" message.** *(Contradicts Q2-A; sends known-bad requests.)*

`[Answer]:` A

---

### Q5 — Own R4 read vs shared context
U7 (Q5-A) did its **own** R4 `MemoView` read, decoupled from `ui-memo-view`. Does U8 mirror that, given it presents the **same** recommendation context as the approve gate?

- **A. Standalone own R4 read (mirror U7's Q5-A)** *(Recommended)* — U8 owns its own `fetchContext` (via its own `overrideFetchSeam`, mirror-not-import), decoupled from **both** `ui-memo-view` **and** the frozen `ui-approval-gate`. Each write-path view is self-sufficient; presents `RecommendationContext` from its own R4 body. Consistent with U7; zero cross-unit import coupling.
- **B. Import U7's `fetchContext` to share the read.** *(Rejected — U7 is frozen; importing couples U8 to a frozen sibling, violating mirror-not-import.)*
- **C. Receive the context as a prop from a parent composition root (no own read).** Defers the read to a not-yet-designed router/shell. *(Possible if Q6 goes combined-view, but adds an undesigned dependency now.)*

`[Answer]:` A

---

### Q6 — Component boundary: **two separate views** vs **one combined approve+override view**
This determines the whole component boundary. `ui-approval-gate` (approve) is a **frozen** separate unit (U7); `ui-override-form` (override) is this unit (U8). Is the underwriter presented **two views a router chooses between**, or **one view with both affordances side by side**?

- **A. Two separate mounted views; any side-by-side composition is a deferred composition-root concern** *(Recommended)*.
  U8 ships a self-contained `OverrideFormView`, sibling to the frozen `ApprovalGateView`. Rationale: (1) U7 is **frozen** — it cannot be edited to host a combined approve+override screen; (2) the decomposition assigns **approve → U7 / override → U8** as separate facets (`unit-of-work.md §U7/§U8`); (3) a genuinely combined "approve **or** override on one screen" would require either editing frozen U7 or duplicating its approve path. So U8 stays standalone, and the actual "one screen offering both" is a **higher-level composition-root/router concern — deferred, named-not-designed** (the same way U7 deferred its real transport wiring to Build & Test). U8's affordance/region is designed to be **composable** into such a screen later.
- **B. One combined view (owned by U8) offering approve + override side by side.** *(Rejected for Phase 1 — would edit frozen U7 or duplicate its approve path; and it re-merges two deliberately-separated units.)*
- **C. Ship standalone now, but with an explicit forward-seam note that a future combined view will slot in both affordances.** = A plus an emphasized forward note. *(Fold into A unless you want the seam called out as a first-class deferred item.)*

**Transparency note:** the eventual *user journey* likely wants one screen where the underwriter sees the recommendation and chooses Approve **or** Override-with-reason. Recommendation **A** keeps U8 decoupled and honest **now** (given frozen U7) while leaving that composition to a later, deliberate step. If you prefer to commit to a combined-view product shape now, choose **B** — but that is a real decision about the frozen-U7 relationship, so it must be your explicit call, not my improvisation.

`[Answer]:` A

---

## §4.5 — Mandatory ambiguity-check (RUN 2026-07-09 — CLEAN, no STOP; three folds, one a verified correction)

Ran against the six answers (all **A**) + the frozen contracts (`DecisionCommitService._gate` trim-then-empty + AUTHZ-1; WIRE-1 R5 body + 409; `RoleGate`/`COMMIT_ACTION_LABELS.override`/copy; U7's by-construction patterns as mirror-not-import reference). The three user-flagged checks + the general sweep:

**FD-OVR-Fold-1 (check i — VERIFIED, a real correction to the Q2-A wording, not a design change).** The Q2-A claim that the UI `String.prototype.trim()` guard is *"identical to the backend's `str.strip()`"* is **empirically FALSE**. Tested both runtimes on-disk (CPython 3.12 `str.strip()` vs Node `String.prototype.trim()`):

| Code point | Python `strip()`→"" | JS `trim()`→"" | Divergence direction |
|---|---|---|---|
| U+001C U+001D U+001E U+001F (FS/GS/RS/US) | **yes** | **no** | UI-**looser** (UI allows, backend 409s) |
| U+0085 (NEL) | **yes** | **no** | UI-**looser** |
| U+FEFF (ZWNBSP/BOM) | **no** | **yes** | UI-**stricter** (UI blocks, backend accepts) |
| U+200B (ZWSP) + all common WS (U+0009–U+000D, U+0020, U+00A0, U+1680, U+2000–U+200A, U+2028/9, U+202F, U+205F, U+3000) | agree | agree | — |

**Resolution (no STOP — the approved answers already determine it):** this does **not** require a design change, because Q2-A makes the UI guard **explicitly non-authoritative** and Q4-A surfaces the backend **409 generically**. The **UI-looser** cases (U+001C–U+001F, U+0085 — a reason of *only* those characters) are exactly the **"race/bypass 409 tail"** Q4-A already covers: the UI would allow submit, the backend `_gate` rejects (`str.strip()==""`), and the generic `409 commit_conflict` handler surfaces it — **CON-BR4 stays single-sourced and correct**. The **UI-stricter** case (U+FEFF-only reason) is a harmless false-block on a degenerate reason. **Corrected framing (binding on the FD):** the UI check is a **best-effort `String.prototype.trim()`-based guard**, **NOT** claimed byte-identical to Python `str.strip()`; the **backend gate is authoritative**, and any UI↔backend trim disagreement **resolves to the backend via the 409 tail**. Inventing a custom Unicode-whitespace matcher to force byte-equality would be **improvising beyond the approved non-authoritative design** — deliberately NOT done. (This is the same defense-in-depth logic as RoleGate↔AUTHZ-1: the client guard need not be a perfect mirror of the server for the invariant to hold, because the server is the single source of truth.)

**FD-OVR-Fold-2 (check ii — confirmed extension, no gap).** Q3-A's capability-free components **do** need an analogous StructuralGuard scan, mirroring U7's `refNotOwn.imports.test.js` no-`createCommitFetch`-in-presentational guard (ND-Fold-3). U8's guard set extends cleanly and **grows by one** for the NEW component: (a) exactly **one** `submitOverride` call site (NOFINAL-analog); (b) `OverrideAffordance` — no `submitOverride` invocation + no seam import; (c) **`OverrideReasonInput` — no seam import** (the new capability-free component U7 had no analog for); (d) no `createOverrideFetch` import in any presentational component. This is an **affirmative confirmation** (the scan is a real, listed deliverable), realized at NFR-Design/Code-Gen exactly as U7 did — **not** an open question.

**FD-OVR-Fold-3 (check iii — legitimately punted, zero design cost paid now).** Q6-A's "designed to be composable later" costs **nothing now** and needs **no** concrete prop-shape decision: composability is the **standard React mount** — `OverrideFormView({ overrideFetchSeam, applicationId })` (mirroring `ApprovalGateView({ commitFetchSeam, applicationId })`) is already a self-contained component a future composition root mounts alongside `ApprovalGateView`. **No speculative composition prop is added now** (that would be YAGNI/improvising). The FD explicitly records that the future combined "approve **or** override on one screen" view is a **deferred composition-root concern** consuming two existing self-contained views — punted with no design debt.

**General sweep:** no other under-specified point. The override-copy advisory-cleanliness (override label from frozen `COMMIT_ACTION_LABELS.override`, `reason` prompt wording that never reads as a system verdict / never renders `DECLINE-RECOMMEND`) follows U7's NFR-AG-Fold-2 pattern (shared advisory-vocabulary lint UNMODIFIED) — a realization detail for FD Part 2 copy, not an ambiguity. **→ CLEAN. Proceeding to FD Part 2.**

---

## §5 — What FD Part 2 will produce (once these are answered & approved)
Three FD artifacts under `guide-docs/build/ui-override-form/functional-design/` (mirroring the sibling FD set):
- `domain-entities.md` — the override request/response shapes (widened builder per Q2), the reason value + trim-then-empty rule, the R4 read body, the state machine (with the reason-carrying `confirming` state per Q3), and the by-construction component/prop inventory.
- `business-rules.md` — `BR-OVR-*` (mandatory-non-blank-reason UX guard as **non-authoritative** defense-in-depth; server `BR-COMMIT-GATE` single-sourced; 409 surfacing per Q4; RoleGate-cosmetic; advisory-only override copy that never reads as `DECLINE-RECOMMEND`).
- `business-logic-model.md` — the load/override/confirm/commit flow + **validated** Mermaid (validated per `visual-and-syntax-standards.md` before write) + consumer/dependency map + FD↔later-stage boundary + invariant self-check.

## §6 — Holds (this stage)
- **NO FD artifact generated** — plan + questions only.
- **No frozen artifact touched**: WIRE-1 · `ui-shell` · `ui-queue` · `ui-memo-view` · `ui-approval-gate` all consumed **by value/shape**, none edited.
- CON-BR4 write-enforcement stays **single-sourced in `audit-store`** — U8 is a consuming facet.
- **No LLM; no TypeScript**; tier-B corpus run **NOT authorized**; **no other unit started**.

---

**GATE — Functional Design Part 1 (Plan).** Answer **Q1–Q6** above (letter per `[Answer]:` tag; add notes if you want a variant). On your answers I will run the mandatory ambiguity-check, embed the full Q&A back into this plan file, and only then generate the three FD Part 2 artifacts. **No FD artifact and no code will be written until you approve.**
