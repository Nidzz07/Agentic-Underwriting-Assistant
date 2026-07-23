# Business Rules — `ui-queue` (U5)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U5 `ui-queue` · **Date**: 2026-07-09 · Story **US-UI-1**.
**Nature**: `ui-queue` owns **no domain business rules** (no rule eval, no authorization decision, no commit). The rules
below are **display / behavioral conformance rules** (BR-QUEUE-*) governing how the queue view renders WIRE-1 R2 data and
conforms to the frozen `ui-shell` conventions. Each is **checkable** (test/lint) and grounded in a frozen contract — none
introduces new domain logic.

---

## Rules

### BR-QUEUE-1 — Display strings come from `shell/copy` only (never inlined)
Every human-visible Recommendation / Confidence / advisory label is looked up from `ui-shell`'s `shell/copy`
(`RECOMMENDATION_LABELS`, `CONFIDENCE_LABELS`, `ADVISORY_VOCABULARY`); the queue **inlines no display string**. Conformance
to the frozen U10 `BR-UI-1` fold.
- **Grounded**: ui-shell domain-entities §2 (single-source copy module).
- **Checkable**: no string literal used as a Recommendation/Confidence label in `frontend/src/queue/`; badges receive a
  **value**, not a label. Any bare `"DECLINE"` or system use of `"decision"`/`"approved"`/`"declined"` fails the shell
  `FORBIDDEN_TERMS` lint.

### BR-QUEUE-2 — Null recommendation/confidence → "pending / not yet drafted" placeholder (not hidden)
When an `ApplicationSummary` row has `recommendation` / `confidence` = `null`, the row is **still shown**, rendering a
neutral **"pending / not yet drafted"** placeholder cell (no badge) in place of the badges (Q4-A). The queue lists **all**
applications including not-yet-scored ones.
- **Grounded**: WIRE-1 §5 (ApplicationSummary nullable "until a recommendation is drafted"); mirrors WIRE-1 `MemoView
  status: pending`. Null-atomicity per N1 (recommendation + confidence co-null, since `RuleResultReport` always carries
  both).
- **Checkable**: a row with null values renders `queue-row-pending-<application_id>` and **no** `RecommendationBadge`/
  `ConfidenceBadge`; the row is present (not filtered out).

### BR-QUEUE-3 — Error surfaces `message` only; `code` via testid; `detail` never raw
On an R2 failure, the visible error text is **`error.message`** only. `error.code` is exposed **only** through the
`queue-error-code` testid/console binding (for test assertion), **not** as visible UI text. `error.detail` is **never**
rendered raw to the user.
- **Grounded**: WIRE-1 §4 error envelope `{error:{code,message,detail?}}`; Q3-A sub-decision. (WIRE-1 §4 also holds "no
  secret VALUE in `message`/`detail`" — the queue additionally never surfaces `detail`.)
- **Checkable**: `queue-error-message` renders `error.message`; `queue-error-code` carries `error.code`; no element
  renders `error.detail`.

### BR-QUEUE-4 — Retry re-fetches the **last-requested** page (position-preserving)
The error-state **Retry** re-requests the **exact page that failed** (the last-requested page *N*), **not** a reset to
page 1. A transient fetch failure must not cost the user their place in the queue. (Initial-load failure ⇒ last-requested
page is page 1, so Retry there re-fetches page 1.)
- **Grounded**: Fold-B (PINNED at FD, accepted with no override). State-holding mechanics/debounce/cancellation → Code-Gen.
- **Checkable**: from `error` on page *N*, activating `queue-error-retry` issues an R2 fetch for **page *N***.

### BR-QUEUE-5 — Row emits selection only; navigation deferred
A row exposes a selection affordance that calls **`onSelect(application_id)`** and nothing more. `ui-queue` performs **no
navigation** and knows **no route** (the memo route R4 target is a later shell/router integration).
- **Grounded**: Q5-A.
- **Checkable**: activating `queue-row-select-<application_id>` calls `onSelect` with that `application_id`; the queue
  imports no router and defines no route target.

### BR-QUEUE-6 — View-only for all roles; **no `RoleGate`** at row level
The queue renders **no** `RoleGate` and gates **no** affordance by Role. R2 is authenticated **any-role** and all roles
(underwriter/auditor/admin) hold `VIEW_QUEUE`; the act/commit path lives entirely in `ui-approval-gate` / `ui-override-form`.
- **Grounded**: Q7-A; `auth_rbac.roles` (`VIEW_QUEUE` in every role's matrix; `RBAC_COMMIT` underwriter-only, irrelevant
  to the queue); ui-shell §5/BR-UI-4 (UI RBAC is cosmetic, real boundary server-side).
- **Checkable**: no `RoleGate` import/usage in `frontend/src/queue/`; the queue renders identically for every Role.

### BR-QUEUE-7 — System `Recommendation` namespace, never the human `CommitAction`
The queue renders only **system** `Recommendation` values (UPPERCASE, incl. the full `DECLINE-RECOMMEND` — **never** a
bare `DECLINE`). It **never** renders a human `CommitAction` (`approve` / `override`) — the queue is read-only and has no
commit affordance. The two namespaces are never conflated.
- **Grounded**: WIRE-1 §1 + ui-shell §2.1 namespace-distinctness note (N3).
- **Checkable**: only `RecommendationBadge` (value ∈ {APPROVE, REFER, "DECLINE-RECOMMEND"}) appears; no lowercase
  `approve`/`override` string is rendered anywhere in the queue.

### BR-QUEUE-8 — `data-testid` naming convention holds (assertion)
Every assertion-relevant queue element carries a stable `data-testid` of shape **`queue-<element>-<purpose>`** (the
inventory in `domain-entities.md §5`), applying the frozen ui-shell `shell-<primitive>-<purpose>` convention (§6) to the
view namespace.
- **Grounded**: FR-UI-3; ui-shell §6 / BR-UI-5 analogue; Fold-A.
- **Checkable**: a lint/test asserts the convention across queue elements (enforced at NFR/Code-Gen).

### BR-QUEUE-9 — Pagination reflects the R2 `page` wrapper; boundaries disabled
`PaginationControls` derives its display and enablement **only** from the R2 `page:{page,size,total}` wrapper — **prev**
disabled on page 1, **next** disabled on the last page (`page * size >= total`). The queue computes no totals of its own.
- **Grounded**: WIRE-1 §2 (1-based offset/limit wrapper); Q6-A; PER-1.
- **Checkable**: on page 1 `queue-pagination-prev` is disabled; on the last page `queue-pagination-next` is disabled;
  `queue-page-indicator` reflects `page` / derived total pages.

---

## Rule → source traceability

| Rule | Frozen source / decision |
|---|---|
| BR-QUEUE-1 | ui-shell §2 `shell/copy` (BR-UI-1) |
| BR-QUEUE-2 | WIRE-1 §5 ApplicationSummary nullable + MemoView `pending`; N1; Q4-A |
| BR-QUEUE-3 | WIRE-1 §4 error envelope; Q3-A |
| BR-QUEUE-4 | Fold-B (accepted); Q3-A Retry |
| BR-QUEUE-5 | Q5-A |
| BR-QUEUE-6 | auth-rbac `VIEW_QUEUE` any-role; ui-shell §5 BR-UI-4; Q7-A |
| BR-QUEUE-7 | WIRE-1 §1 / ui-shell §2.1 namespace-distinctness; N3 |
| BR-QUEUE-8 | FR-UI-3; ui-shell §6 (BR-UI-5); Fold-A |
| BR-QUEUE-9 | WIRE-1 §2 list wrapper; Q6-A; PER-1 |
