# Business Rules — `ui-memo-view` (U6)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U6 `ui-memo-view` · **Date**: 2026-07-09 · Story **US-UI-2**.
**Nature**: `ui-memo-view` owns **no domain business rules** (no rule eval, no authorization decision, no LLM, no commit).
The rules below are **display / structural / behavioral conformance rules** (BR-MEMO-*) governing how the memo view
renders WIRE-1 R4 data and the DecisionMemo three-region shape, and how it conforms to the frozen `ui-shell`,
memo-agent-core, and WIRE-1 contracts. Each is **checkable** (test/lint) and grounded in a frozen contract — none
introduces new domain logic. The load-bearing ones are **BR-MEMO-3/4/5** (the structural expression of CON-BR2-TYPE).

---

## Rules

### BR-MEMO-1 — Display strings come from `shell/copy` (enums) + memo-local copy (chrome) only — never inlined
Every human-visible `Recommendation` / `Confidence` label is looked up from `ui-shell`'s `shell/copy`
(`RECOMMENDATION_LABELS`, `CONFIDENCE_LABELS`) **by value** via the reused shell badges; every memo-specific chrome string
(region headings, pending/loading/retry text, `MissingInfoSource` labels) comes from the **memo-local copy module**
(`domain-entities.md §5`). The view **inlines no display string** in a component. Conformance to the frozen U10 `BR-UI-1`
fold, extended by Q4-A's local copy module.
- **Grounded**: ui-shell domain-entities §2 (single-source copy); Q4-A (memo-local copy for `MissingInfoSource`).
- **Checkable**: no string literal used as a display label in `frontend/src/memoView/` components; badges receive a
  **value**, not a label; the `no-inline-label` lint (reused, §BR-MEMO-2) passes.

### BR-MEMO-2 — Reuse the ONE `FORBIDDEN_TERMS`; advisory conformance scoped to the view's STATIC code (MEMO-Fold-1)
`ui-memo-view` **reuses the single `shell/copy` `FORBIDDEN_TERMS`** (no new word-list) by registering the shell
`no-inline-label` + `advisory-vocabulary` lints on `src/memoView/**` (a new `eslint.config.js` block mirroring the
ui-queue block; **no `src/shell` file modified**). The **scope boundary is binding**: the lints check the view's
**static code** — component labels, region headings, chrome, and the RO-region framing — which must never inline a shell
label or contain a `FORBIDDEN_TERMS.systemOutput` token (`DECLINE` / `decision` / `approved` / `declined`). The
**runtime `narrative_prose`** is LLM-authored content whose advisory conformance is **memo-agent-core's backend concern**
(CON-BR2 enforced there, at draft time) — the view **neither lints nor rewrites** it. The view's obligation is the
**structural read-only separation** (BR-MEMO-3) + advisory-clean **chrome**, not linting runtime prose.
- **Grounded**: `shell/copy/forbiddenTerms.js` (the one list, two checks — lexical + namespace); ui-queue's reuse
  precedent (`eslint.config.js` queue block); MEMO-Fold-1; CON-BR2 (memo-agent-core `schemas.py`).
- **Checkable**: the memo-local copy module + memo components pass the reused `no-inline-label` + `advisory-vocabulary`
  lints; **no** new word-list exists under `src/memoView/`; a detector self-test confirms a synthetic forbidden term in
  the static code fails the lint; **no** assertion is made against `narrative_prose` content (out of scope by design).

### BR-MEMO-3 — Three-region structural separation: the RO region is a DISTINCT node from the L narrative
The memo renders its **three regions as structurally separate nodes**: the **L** `NarrativeRegion` (LLM-authored prose +
citations), the **D** `MissingInfoRegion`, and the **RO** `ReadOnlyRecommendationRegion` (recommendation/confidence). The
**RO region is a visually + structurally distinct node from the L narrative** — never nested inside it, never
interleaved — so the UI **never implies the LLM produced the recommendation**. This is the **direct visual/structural
expression of CON-BR2-TYPE** (the LLM's `MemoDraftOutput` has no recommendation/confidence field; the memo's are injected
read-only).
- **Grounded**: memo-agent-core `schemas.py` (`DecisionMemo` three regions; `MemoDraftOutput` declares no
  recommendation/confidence — CON-BR2-TYPE); Q5-A; MEMO-Fold-2 (region testids make this testable).
- **Checkable** (the concrete CON-BR2 structural test): `memo-region-readonly` and `memo-region-narrative` are **distinct
  DOM nodes**, neither an ancestor/descendant of the other; the recommendation/confidence render inside
  `memo-region-readonly` and **not** within `memo-region-narrative`.

### BR-MEMO-4 — The RO region composes the frozen `ReadOnlyRegion`, engine-attributed
The RO region **composes the frozen `ui-shell` `ReadOnlyRegion`** (`aria-readonly`, first use) to wrap the
`RecommendationBadge` + `ConfidenceBadge`, framed via memo-local chrome as **attributable to the deterministic rules
engine**, not the LLM. This is the primitive's intended purpose (its own comment: "wraps read-only memo regions … the
memo-agent-core three-region shape") and a direct visual expression of CON-BR2.
- **Grounded**: `frontend/src/shell/components/ReadOnlyRegion.jsx` (frozen); Q5-A; N3.
- **Checkable**: the RO region renders a `ReadOnlyRegion` (carrying `aria-readonly` + `testid="memo-region-readonly"`)
  wrapping exactly the recommendation + confidence badges; the region heading frames it as engine-attributed (advisory),
  drawn from memo-local copy (never inlined).

### BR-MEMO-5 — Recommendation + confidence render ONLY in the RO region
The system `recommendation` / `confidence` (`memo.recommendation` / `memo.confidence`) render **only** inside the
`ReadOnlyRecommendationRegion` (RO) — **never** inside, adjacent to, or attributed to the L `NarrativeRegion`. The
narrative prose is displayed as-is but is **not** a render site for the recommendation/confidence values.
- **Grounded**: CON-BR2-TYPE (injected read-only, not LLM-authored); N3; Q5-A.
- **Checkable**: a `RecommendationBadge` / `ConfidenceBadge` appears **exactly once**, inside `memo-region-readonly`; no
  recommendation/confidence value is rendered within `memo-region-narrative`.

### BR-MEMO-6 — Error surfaces `message` only; `code` via testid; `detail` never raw; Retry re-fetches the same memo
On an R4 failure, the visible error text is **`error.message`** only. `error.code` is exposed **only** through the
`memo-error-code` testid/console binding (for test assertion), **not** as visible UI text. `error.detail` is **never**
rendered raw. The error-state **Retry** re-requests **R4 for the same `applicationId`** (the memo view fetches a single
resource — there is no page position to preserve, unlike ui-queue's paged Retry).
- **Grounded**: WIRE-1 §4 error envelope `{error:{code,message,detail?}}` ("no secret VALUE in message/detail"); ui-queue
  `BR-QUEUE-3` ERROR pattern + `normalizeError` (CG-Fold-1) reused as a **convention** (the local memo fetchSeam
  guarantees a well-formed envelope, Q6-A).
- **Checkable**: `memo-error-message` renders `error.message`; `memo-error-code` carries `error.code`; no element renders
  `error.detail`; activating `memo-error-retry` issues an R4 fetch for the **same `applicationId`**.

### BR-MEMO-7 — View-only for all roles; no `RoleGate`, no commit affordance, no router import
The memo view renders **no** `RoleGate`, gates **no** affordance by Role, exposes **no** commit affordance, and emits
**no** outward action in Phase 1. R4 is authenticated **any-role**; the act/commit path lives entirely in
`ui-approval-gate` (U7) / `ui-override-form` (U8). The view **imports no router** and knows no route target; navigation to
the commit path is a later shell/router integration.
- **Grounded**: WIRE-1 §3 (R4 authenticated any role; R5 commit is `underwriter`-only, a different unit); N2; ui-shell §5
  / BR-UI-4 (UI RBAC is cosmetic, real boundary server-side); ui-queue `BR-QUEUE-5/6` precedent.
- **Checkable**: no `RoleGate` import/usage and no router import in `frontend/src/memoView/` (StructuralGuard scans,
  mirroring ui-queue's `noRoleGateImport` / `noRouterImport`); the view renders identically for every Role; no commit
  affordance element exists.

### BR-MEMO-8 — `status: "pending"` → a single page-level "not yet drafted" state (derived from `status`)
When R4 resolves with `status: "pending"` (`report`/`memo` null), the view renders a **single page-level** "memo not yet
drafted for this application" message (`memo-state-pending`) — **no** partial/progressive render of a non-existent memo.
The `pending` state is **derived from the `status` discriminator**, not from an empty-array check.
- **Grounded**: WIRE-1 §5 `MemoView status: ready|pending` (WIRE1-Fold-2); Q2-A; N1.
- **Checkable**: an R4 body with `status:"pending"` renders `memo-state-pending` and **none** of the three memo regions;
  the state derivation keys on `view.status`, not `memo`/`report` array contents.

### BR-MEMO-9 — Deterministic list rendering: `missing_information` + `cited_rule_ids` preserve backend order
Both the **D** `missing_information` list and the **L** `cited_rule_ids` list are rendered as **local presentational
lists** (Q3-A, no shared primitive) that **preserve the order delivered by the backend** — the view **re-sorts nothing**.
`missing_information` order is memo-agent-core's deterministic total order (MISSINGINFO-1: source-major, the declared
`MissingInfoSource` enum order); `cited_rule_ids` order is as authored. Each `missing_information` row shows `detail` as
primary text + the `source` via the memo-local `MISSING_INFO_SOURCE_LABELS` (Q4-A).
- **Grounded**: memo-agent-core `schemas.py` (`MissingInfoSource` "declared order IS the fixed source-major sort key",
  MISSINGINFO-1); Q3-A / Q4-A; ui-queue's local-list precedent (ui-shell frozen).
- **Checkable**: the rendered order of `memo-missinginfo-*` / `memo-citation-*` equals the input array order (no client
  sort); each missing-info row renders `detail` + a `MISSING_INFO_SOURCE_LABELS[source]` label; no shared list primitive
  is imported/added to ui-shell.

### BR-MEMO-10 — `data-testid` naming convention holds, incl. region-level testids (MEMO-Fold-2)
Every assertion-relevant memo element carries a stable `data-testid` of shape **`memo-<element>-<purpose>`** (the
inventory in `domain-entities.md §6`), applying the frozen ui-shell `shell-<primitive>-<purpose>` / ui-queue
`queue-<element>-<purpose>` convention to the memo namespace. The **region-level** testids
(`memo-region-narrative` / `-citations` / `-missinginfo` / `-readonly`, plus `memo-recommendation` / `memo-confidence`)
are **required** so the BR-MEMO-3 structural separation is testable.
- **Grounded**: FR-UI-3; ui-shell §6 (BR-UI-5) / ui-queue `BR-QUEUE-8`; MEMO-Fold-2.
- **Checkable**: a `memo-testid-convention` ESLint rule (mirroring ui-queue's `queue-testid-convention`) + a self-test
  assert the convention across memo elements; the four region testids + `memo-recommendation`/`memo-confidence` are present.

### BR-MEMO-11 — System `Recommendation` namespace, never the human `CommitAction`
The memo view renders only **system** `Recommendation` values (UPPERCASE, incl. the full `DECLINE-RECOMMEND` — **never** a
bare `DECLINE`). It **never** renders a human `CommitAction` (`approve` / `override`) — the view is read-only with no
commit affordance (BR-MEMO-7). The system-advisory namespace (`Recommendation`) and the human-committed namespace
(`CommitAction`) are **never conflated**; the human `override` is never rendered as, or confused with, the system
`DECLINE-RECOMMEND`.
- **Grounded**: WIRE-1 §1 namespace-distinctness (binding) + ui-shell §2.1; `shell/copy/forbiddenTerms.js` (bare
  `DECLINE` forbidden); N3.
- **Checkable**: only `RecommendationBadge` (value ∈ {APPROVE, REFER, `DECLINE-RECOMMEND`}) appears; no lowercase
  `approve`/`override` string and no bare `DECLINE` is rendered anywhere in the memo view.

---

## Rule → source traceability

| Rule | Frozen source / decision |
|---|---|
| BR-MEMO-1 | ui-shell §2 `shell/copy` (BR-UI-1); Q4-A memo-local copy |
| BR-MEMO-2 | `shell/copy/forbiddenTerms.js` (the one list); ui-queue eslint reuse; MEMO-Fold-1; CON-BR2 |
| BR-MEMO-3 | memo-agent-core `schemas.py` CON-BR2-TYPE (three-region; `MemoDraftOutput` no rec/conf); Q5-A; MEMO-Fold-2 |
| BR-MEMO-4 | `ReadOnlyRegion.jsx` (frozen); Q5-A; N3 |
| BR-MEMO-5 | CON-BR2-TYPE (injected read-only); N3; Q5-A |
| BR-MEMO-6 | WIRE-1 §4 error envelope; ui-queue BR-QUEUE-3 + `normalizeError` (CG-Fold-1) convention; Q6-A |
| BR-MEMO-7 | WIRE-1 §3 (R4 any-role; R5 underwriter-only); ui-shell §5 BR-UI-4; ui-queue BR-QUEUE-5/6; N2 |
| BR-MEMO-8 | WIRE-1 §5 MemoView `status` (WIRE1-Fold-2); Q2-A; N1 |
| BR-MEMO-9 | memo-agent-core MISSINGINFO-1 (deterministic order); Q3-A / Q4-A |
| BR-MEMO-10 | FR-UI-3; ui-shell §6 (BR-UI-5) / ui-queue BR-QUEUE-8; MEMO-Fold-2 |
| BR-MEMO-11 | WIRE-1 §1 / ui-shell §2.1 namespace-distinctness; `forbiddenTerms.js`; N3 |
