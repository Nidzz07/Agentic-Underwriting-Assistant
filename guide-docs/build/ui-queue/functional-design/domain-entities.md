# Domain Entities — `ui-queue` (U5)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U5 `ui-queue` · C5 · Phase 1 · **Depth**: lighter (display) +
async-state addendum · **Date**: 2026-07-09 · Story **US-UI-1** · FR-UI-1 / FR-UI-3 / PER-1.
**Scope**: the application-queue view — a **presentational, read-only** view that fetches WIRE-1 **R2**
(`GET /applications?page=&size=`) and renders a paginated list of `ApplicationSummary` rows. A UI unit's "entities" are its
**component/module + prop-shape inventory** (not data records) — per the plan (Q2-A, no dedicated `frontend-components.md`),
the component hierarchy/props are folded here. **React + Tailwind, NO TypeScript** (FR-UI-5). ui-queue owns **no business
logic** — no rule eval, no authorization *decision*, no LLM, no commit; it **imports no backend production code** and
consumes backend **shapes by value** (reference-not-own).

---

## 1. Location & composition boundary

`ui-queue` lives at **`frontend/src/queue/`**. It **imports** `ui-shell` (frozen, U10) primitives + copy + session
context and **composes** them; it **defines its own local list/table** (Q2-A) — **nothing is promoted into `ui-shell`**
(ui-shell stays frozen). It renders exactly one screen (the queue) inside the shell `AppFrame`.

| Consumes from `ui-shell` (frozen) | Used for |
|---|---|
| `AppFrame` | page shell / layout chrome (queue mounts inside it) |
| `Panel` / `Region` | bordered container for the queue table + states |
| `RecommendationBadge { value, testid }` | renders a row's system `Recommendation` value (looks up its own label) |
| `ConfidenceBadge { value, testid }` | renders a row's `Confidence` value |
| `shell/copy` (`RECOMMENDATION_LABELS` / `CONFIDENCE_LABELS`, `ADVISORY_VOCABULARY`) | **all** display strings (BR-QUEUE-1: never inline) |
| `shell/session` (`RoleContext`, `useCurrentRole()`) | available, but **not read at row level** (Q7-A view-only) |

> **Not consumed**: `RoleGate` (Q7-A — no per-row gating); `ReadOnlyRegion` (that wraps memo three-region content, a
> `ui-memo-view` concern). No backend Python import (the cross-language reference-not-own boundary, U10 §5).

---

## 2. Consumed value shapes (by value, from WIRE-1 R2 — **not owned, not re-cased**)

These mirror the **frozen** WIRE-1 §5 shapes verbatim; enum fields carry the §1 wire values (Recommendation UPPERCASE
incl. `DECLINE-RECOMMEND`; Confidence Title-case). ui-queue **defines no schema** — it reads these off the R2 response.

| Shape | Definition (as delivered by WIRE-1 R2) | Notes |
|---|---|---|
| **`ApplicationSummary`** (row) | `{ application_id: str, recommendation_id: str \| null, recommendation: <Recommendation value> \| null, confidence: <Confidence value> \| null }` | the four fields are **co-present or co-null** (N1) — null ⇒ "pending / not yet drafted" (BR-QUEUE-2) |
| **List wrapper** (R2 body) | `{ items: ApplicationSummary[], page: { page: int, size: int, total: int } }` | `page` is **1-based** (WIRE-1 §2); drives `PaginationControls` |
| **Error envelope** (non-2xx) | `{ error: { code: str, message: str, detail?: obj } }` | `message` → user; `code` → testid binding; `detail` **never** rendered raw (BR-QUEUE-3) |

---

## 3. Render-state model (the async-state addendum — first-class FD concern)

A single closed enum drives what `QueueView` renders. Full transition semantics live in `business-logic-model.md §1`.

| State | Meaning | Renders |
|---|---|---|
| `loading` | R2 fetch for the current page in flight | skeleton/placeholder rows (`QueueStateView`) |
| `ready` | fetch resolved, `items` non-empty | `QueueTable` + `PaginationControls` |
| `empty` | fetch resolved, `items: []` / `total: 0` | a distinct **"No applications in the queue"** message (`QueueStateView`) |
| `error` | R2 fetch failed (any non-2xx or transport error) | `error.message` + a **Retry** affordance (`QueueStateView`) |

> **State enum** (a local view constant, not a backend enum): `QUEUE_STATE = { LOADING, READY, EMPTY, ERROR }`.

---

## 4. Component / module inventory (hierarchy + prop shapes — JS/JSX, no TS)

**Hierarchy**

```text
AppFrame (ui-shell)
└── Panel  (ui-shell — queue container)
    └── QueueView            [owns fetch + render-state; the only stateful component]
        ├── QueueStateView   [loading | empty | error presentational states]
        ├── QueueTable       [ready state: header + rows]  (local, Q2-A)
        │   └── QueueRow (×N) [one ApplicationSummary]      (local, Q2-A)
        │       ├── RecommendationBadge (ui-shell)  |  pending placeholder
        │       └── ConfidenceBadge     (ui-shell)  |  pending placeholder
        └── PaginationControls [prev / next / page indicator]  (local)
```

**Prop shapes**

| Component | Prop shape (JSX) | Role / behavior |
|---|---|---|
| **`QueueView`** | `{ }` (no props; reads page from local state, size from config) | The **only** stateful component: fetches R2 for the current page, holds `{ state, items, page, error }`, and selects `QueueStateView` vs `QueueTable`+`PaginationControls`. Emits nothing upward (top of the view). |
| **`QueueStateView`** | `{ state, error, onRetry, testid }` — `state ∈ {loading, empty, error}` | Presentational. `loading` → skeleton rows; `empty` → "no applications" copy; `error` → `error.message` + a Retry button wired to `onRetry`. Renders **no** table. |
| **`QueueTable`** | `{ items, onSelect, testid }` | Presentational. Renders a semantic table header + one `QueueRow` per item; forwards `onSelect`. Pure — no fetch, no state. |
| **`QueueRow`** | `{ summary, onSelect, testid }` where `summary: ApplicationSummary` | Presentational. Renders `application_id`; a `RecommendationBadge`/`ConfidenceBadge` **iff** the value is non-null, else the **pending placeholder** cell (BR-QUEUE-2); exposes the **selection affordance** that calls `onSelect(summary.application_id)` (BR-QUEUE-5 / Q5-A). |
| **`PaginationControls`** | `{ page, size, total, onPageChange, testid }` | Presentational. Renders a **current-page / total** indicator and **prev/next**; disables prev on page 1 and next on the last page (boundary logic in `business-logic-model.md §2`); calls `onPageChange(nextPage)`. |

**Selection event shape** (Q5-A): `onSelect(application_id: str) → void`. `ui-queue` **only emits** the selected
`application_id`; the **route target / navigation wiring is deferred** to a later shell/router integration (BR-QUEUE-5).
No import of a router, no knowledge of the memo route (R4) here.

---

## 5. `data-testid` inventory (Fold-A — analogous to `ui-shell` §6 `shell-<primitive>-<purpose>`, view-namespaced)

Every assertion-relevant element carries a stable, documented testid of shape **`queue-<element>-<purpose>`** (applying,
not re-inventing, the frozen ui-shell convention). Enforced by a lint/test assertion (BR-QUEUE-6).

| Element | `data-testid` | Notes |
|---|---|---|
| Queue container / table | `queue-table` | the `ready`-state table root |
| A single row | `queue-row-<application_id>` | interpolates the row's `application_id` (stable per row) |
| Selection affordance on a row | `queue-row-select-<application_id>` | the click target that emits `onSelect` |
| Pending placeholder cell | `queue-row-pending-<application_id>` | rendered instead of the badges when values are null |
| Loading state | `queue-state-loading` | skeleton container |
| Empty state | `queue-state-empty` | "no applications" message |
| Error state | `queue-state-error` | error container |
| Error message (visible) | `queue-error-message` | carries `error.message` (BR-QUEUE-3) |
| Error code (hidden binding) | `queue-error-code` | carries `error.code` for test assertion / console — **not** visible UI text (Q3 sub-decision) |
| Retry control | `queue-error-retry` | wired to `onRetry` (re-fetch last-requested page, BR-QUEUE-4) |
| Pagination prev / next | `queue-pagination-prev` / `queue-pagination-next` | disabled at boundaries |
| Page indicator | `queue-page-indicator` | current-page / total display |

> Row-level shell badges reuse the shell testid convention passed through as props, e.g. a row's recommendation badge
> testid `queue-row-recommendation-<application_id>` (the view supplies the testid; the badge is a frozen shell primitive).

---

## 6. Boundary — what `ui-queue` does NOT own

- **No authorization decision** — the queue is authenticated any-role (all roles hold `VIEW_QUEUE`); it renders no
  RoleGate and gates nothing (Q7-A). The real boundary stays `auth-rbac` server-side.
- **No commit / gate / override** — no write path; those are U7 `ui-approval-gate` / U8 `ui-override-form`. The queue
  never renders a human `CommitAction` (`approve`/`override`) — only the **system** `Recommendation` (N3 / BR-QUEUE-7).
- **No routing** — it emits `onSelect(application_id)` and stops (Q5-A); the navigation target is a later integration.
- **No display-string definition** — every label comes from `shell/copy` (BR-QUEUE-1); the queue inlines none.
- **No token values / no schema** — aesthetics come from `shell/tokens` (values deferred); shapes come from WIRE-1.
- **No route implementation** — the R2 endpoint itself is `backend/app/main.py`, deferred to Build & Test (WIRE-1 §, not
  this unit); ui-queue consumes the R2 **contract shape**, fetching a mocked R2 in tests.
