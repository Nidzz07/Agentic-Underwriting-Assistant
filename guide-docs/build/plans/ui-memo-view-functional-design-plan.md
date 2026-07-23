# Functional Design — Plan (Part 1) — `ui-memo-view` (U6)

**Stage**: BUILD → per-unit loop → Functional Design **Part 1 (Plan)** · **Unit**: U6 `ui-memo-view` · C5 · Phase 1
**Story**: US-UI-2 · **Requirements**: FR-MEMO-3, NFR-EXPLAIN-1, FR-UI-3/5 · **Date**: 2026-07-09
**Depth**: **lighter (display) + fetch-lifecycle addendum + three-region read-only-separation addendum** (confirmed — §2).
**Scope**: the memo view — fetches WIRE-1 **R4** (`GET /applications/{application_id}/memo`) and renders the
**MemoView** (`status: ready|pending`), whose `ready` form carries the **DecisionMemo three-region** shape. The **second**
data-fetching UI unit; applies `ui-queue`'s established fetchSeam + StructuralGuard **convention** (not an import).
**React + Tailwind, NO TypeScript.** Owns no business logic — no rule eval, no authorization decision, no LLM, no commit.

> **Part 1 (Plan) only.** Embeds the Q1–Q6 Q&A + the ambiguity-check; lists the Part 2 FD artifacts to generate **after**
> approval. **No FD artifact (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`) is generated here.**

---

## 0. DISCOVER-carryover check — ✅ CLEAN
- [x] No `guide-docs/build/ui-memo-view/` directory exists — no partial FD artifact. Clean start.

## 1. Frozen surfaces re-read (built ON — consumed by value/shape, **not modified**)
- [x] Re-read on disk before planning:

| Frozen surface | Source | What `ui-memo-view` consumes |
|---|---|---|
| **`ui-shell` `ReadOnlyRegion`** | `frontend/src/shell/components/ReadOnlyRegion.jsx` (`{children, testid}`, `aria-readonly`) | wraps the **RO** memo region — first use (Q5) |
| **`ui-shell` primitives/copy/tokens/session** | `frontend/src/shell/*` (frozen U10) | `AppFrame`/`Panel`, `RecommendationBadge`/`ConfidenceBadge`, `shell/copy` labels + the **one `FORBIDDEN_TERMS`**, tokens, `RoleContext` (not gated) |
| **`ui-queue` convention** | `frontend/src/queue/*` (frozen U5) | the **fetchSeam pattern** (injected/capturing, `normalizeError`/CG-Fold-1) + **StructuralGuard** substrate — as an **established sibling convention**, NOT an import dependency (Q6-A) |
| **WIRE-1 R4 MemoView** | `guide-docs/build/wire-1/api-contract.md` §3/§5 (PINNED) | `{ application_id, recommendation_id\|null, status: "ready"\|"pending", profile\|null, report\|null, memo\|null }` |
| **memo-agent-core `DecisionMemo`** | `backend/memo_agent_core/schemas.py` | three regions — **L** `narrative_prose`+`cited_rule_ids` · **D** `missing_information[]` of `{source ∈ MissingInfoSource, detail}` · **RO** `recommendation`+`confidence` (injected read-only) · **M** `memo_hash`+`model_version`; **CON-BR2-TYPE** (LLM never produces recommendation/confidence) |

> `MissingInfoSource` (`missing_document`/`unparseable_document`/`not_evaluated_rule`/`incomplete_flag`) has **no** display
> labels in `shell/copy` (frozen) — see Q4.

## 2. Depth decision — **lighter (display) + two addenda** (Q1 = A)
- [x] `unit-of-work.md` classes U6 **"lighter (display)"** — holds: the view owns **no business rules of its own**.
- [x] **Addendum 1 (fetch-lifecycle)** — R4 is a real (mocked-in-tests) fetch; reuse `ui-queue`'s established fetchSeam +
  four-state convention (a genuinely-new concern the shell never had, already normalized by ui-queue).
- [x] **Addendum 2 (three-region read-only separation)** — this is the **first** view to render the DecisionMemo three
  regions; the **RO** region (`recommendation`/`confidence`) must be rendered **visually + structurally distinct** from the
  **L** narrative (LLM-authored), so the UI never implies the LLM produced the recommendation — a direct visual
  expression of **CON-BR2-TYPE**. Load-bearing, but still a **display/structure** concern → not *comprehensive*
  (that tier stays U7/U8).

---

## 3. Functional-Design questions — Q1–Q6 (full text + filled answers, all **A**)
- [x] Surfaced, answered by the user (2026-07-09), embedded here per the standing convention.

### Q1 — Depth confirmation
**A.** lighter + fetch-lifecycle addendum + three-region read-only-separation · **B.** plain lighter · **C.** comprehensive.
**[Answer]: A** — lighter (display) + fetch-lifecycle addendum + three-region read-only-separation addendum. Doesn't
warrant comprehensive (reserved for U7/U8); the two addenda capture what's genuinely new (R4 fetch lifecycle, reusing the
established convention) and genuinely load-bearing (CON-BR2-TYPE's visual/structural separation, which this view must
respect as the first to render the three-region memo).

### Q2 — MemoView `status: "pending"` (full-page not-yet-drafted state)
**A.** single page-level pending state · **B.** progressive (render `profile` if present + pending banner).
**[Answer]: A** — a single page-level pending state: `status:"pending"` → a clear "memo not yet drafted for this
application" message; `report`/`memo` are null so there's nothing else to render. Matches the lighter depth — the memo is
this view's entire purpose, so a partial/progressive render of a not-yet-existing memo would be confusing, not helpful.

### Q3 — `cited_rule_ids` (L) + `missing_information` (D) list rendering
**A.** both local presentational lists · **B.** promote a shared list primitive (touches frozen ui-shell).
**[Answer]: A** — both `cited_rule_ids` and `missing_information` as local presentational lists defined inside
ui-memo-view, no shared list primitive; consistent with ui-queue's precedent of keeping list markup local and ui-shell frozen.

### Q4 — `MissingInfoSource` source labels (no labels in frozen `shell/copy`)
**A.** `detail` primary + `source` via a memo-view-local copy module · **B.** `detail` only · **C.** add to `shell/copy` (rejected).
**[Answer]: A** — render the human-readable `detail` as primary text, with the `source` shown via a memo-view-local copy
module (mirroring ui-queue's local `copy.js` precedent); not added to the frozen `shell/copy`.

### Q5 — `ReadOnlyRegion` composition for the RO region (first use)
**A.** compose frozen `ReadOnlyRegion` around RO, engine-attributed · **B.** local wrapper.
**[Answer]: A** — compose the frozen `ReadOnlyRegion` to wrap the RO region (`RecommendationBadge` + `ConfidenceBadge`),
visually/structurally separated from the L narrative, framed as attributable to the deterministic engine, not the LLM —
exactly the primitive's intended purpose and a direct visual expression of CON-BR2.

### Q6 — Fetch-seam for R4
**A.** own local memo fetchSeam (mirror pattern, no ui-queue import) · **B.** import ui-queue's `normalizeError` · **C.** shared util (rejected).
**[Answer]: A** — ui-memo-view defines its own local memo fetchSeam (R4 request builder + failure normalization),
mirroring ui-queue's established pattern without importing from ui-queue (now frozen); keeps the two sibling UI units decoupled.

---

## 4. Ambiguity-check (RUN 2026-07-09) — grounded on the frozen surfaces
- [x] Ran against the six answers + the frozen contracts (ui-shell `ReadOnlyRegion`/primitives/copy/tokens/session;
  ui-queue's fetchSeam/StructuralGuard **convention, not an import**; WIRE-1 R4 MemoView; memo-agent-core `DecisionMemo`
  three-region + CON-BR2-TYPE). **CLEAN — no genuine gap, no STOP.** Two folds surfaced (both resolvable against the
  frozen contracts, no improvisation):

### MEMO-Fold-1 (your check a) — reuse the ONE `FORBIDDEN_TERMS`; advisory-conformance scope — **CLEAN**
The memo view **is** where CON-BR2's language distinctions matter most, so ui-memo-view **reuses the one
`FORBIDDEN_TERMS`** exactly as ui-queue did — registering the shell `no-inline-label` + `advisory-vocabulary` lints on
`src/memoView/**` (a new `eslint.config.js` block, **no new word-list**). Its **memo-view-local copy module** (Q4 —
`MissingInfoSource` labels + region headings + pending/chrome text) is therefore **lint-subject**: it may not inline a
shell display label (no-inline-label) or contain forbidden system-output vocabulary (advisory-vocabulary). **Scope
boundary (recorded):** the lints check the view's **static code** (labels, headings, chrome, region framing); the
**runtime `narrative_prose`** is LLM-authored content whose advisory conformance is **memo-agent-core's** backend concern
(CON-BR2 enforced there) — the view's job is the **structural read-only separation** (RO distinct from L) + advisory-clean
**chrome**, not linting runtime prose. No gap.

### MEMO-Fold-2 (your check b) — three-region separation → `data-testid` additions — **CLEAN**
The testid convention is the **same shape**, memo-namespaced (`memo-<element>-<purpose>`, analogous to `queue-…`). The
three-region separation (Q5) adds **region-level testids** so a **structural test can assert the RO region is a DISTINCT
node from the L narrative** (the concrete CON-BR2 structural check) — e.g. `memo-region-narrative`, `memo-region-citations`,
`memo-region-missinginfo`, `memo-region-readonly`, `memo-recommendation`, `memo-confidence`, plus the state testids
`memo-state-loading` / `memo-state-pending` / `memo-state-error`. Applying the established convention with a `memo-`
prefix + a new `queue`-style ESLint testid rule (`memo-testid-convention`) — not inventing a scheme. No gap.

### Grounded notes (non-gaps)
- **N1 — state machine**: states are `loading → ready | pending | error` (+ `error --retry--> loading`). Unlike ui-queue's
  `empty` (derived from `items.length`), **`pending` is derived from the R4 `status` discriminator** — a small, pinned twist.
- **N2 — view-only**: R4 is authenticated any-role; the memo view is **display-only, no `RoleGate`, no commit affordance**
  (the commit path is U7 `ui-approval-gate`); navigation to commit is deferred/router — the view emits no outward action in Phase 1.
- **N3 — RO attribution**: the `recommendation`/`confidence` render **only** inside the `ReadOnlyRegion` (RO), never inside
  or attributed to the L narrative — a business rule (Part 2) + a structural test (MEMO-Fold-2). `profile` renders as a
  minimal context header; its detailed treatment is a Part-2 FD-artifact detail (lighter — no new gate question).

---

## 5. FD **Part 2** plan — artifacts to generate **after** approval (checkboxes, not started)
- [ ] **`guide-docs/build/ui-memo-view/functional-design/domain-entities.md`** — component/prop inventory:
  `MemoView` (stateful owner; local memo `fetchSeam` R4; four-state machine loading/ready/pending/error), `MemoStateView`
  (loading/pending/error), the **ready** three-region composition — `NarrativeRegion` (L: `narrative_prose` +
  `CitationsList` of `cited_rule_ids`), `MissingInfoRegion` (D: `missing_information` list of `{source-label, detail}`),
  `ReadOnlyRecommendationRegion` (RO: composes frozen `ReadOnlyRegion` + `RecommendationBadge`/`ConfidenceBadge`,
  engine-attributed) — a minimal profile/context header; the consumed **MemoView**/**DecisionMemo** value shapes; the
  four-state render enum; the **memo-local copy module** (MissingInfoSource labels + headings/chrome); the full
  `memo-<element>-<purpose>` `data-testid` inventory incl. the **region testids** (MEMO-Fold-2).
- [ ] **`guide-docs/build/ui-memo-view/functional-design/business-rules.md`** — BR-MEMO-*: labels via `shell/copy` +
  memo-local copy only (never inlined); **reuse the one `FORBIDDEN_TERMS`** for advisory conformance (MEMO-Fold-1);
  **three-region structural separation** — RO region distinct from L narrative (CON-BR2 visual respect); **recommendation/
  confidence render ONLY in the RO region** (N3); `status:"pending"` → page-level pending; error `message`-only / `code`
  via testid / `detail` never rendered (reuse ui-queue's ERROR pattern); view-only, no `RoleGate`; no router import;
  `missing_information` deterministic list; `cited_rule_ids` list; system `Recommendation` namespace, never a `CommitAction`.
- [ ] **`guide-docs/build/ui-memo-view/functional-design/business-logic-model.md`** — the fetch/state lifecycle
  (`loading → ready | pending | error`; `error --retry--> loading`; `pending` from the `status` discriminator, N1) as a
  **validated Mermaid** (7-rule convention) + text alternative; the ready-state three-region composition flow.

## 6. Holds / guardrails (this Part 1)
- [x] **No FD artifact generated** — only this plan file written.
- [x] **WIRE-1 untouched** (R4 by shape); **ui-shell (frozen) untouched** (ReadOnlyRegion/primitives/copy/`FORBIDDEN_TERMS`
  consumed by import/shape); **ui-queue (frozen) untouched** — its fetchSeam/StructuralGuard are a **convention**, not imported.
- [x] **No application code** written. **No LLM. No TypeScript.**
- [x] **tier-B corpus run NOT authorized**; **no other unit started**; `audit_store` Docker-guard gap still deferred.
