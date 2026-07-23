# Frontend Components — `ui-history` (U9)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U9 `ui-history` · C5 · Phase 1 · **Date**: 2026-07-14 · Story **US-UI-6** · FR-UI-1 / FR-UI-3 / FR-UI-5.
**Scope**: the component-structure view of `ui-history` — hierarchy, props/state, user-interaction flows, and the WIRE-1 R6/R7 integration points each component consumes. **React + Tailwind, NO TypeScript** (FR-UI-5). This file complements `domain-entities.md §4` (which folds the same inventory into the entity model); it is included per this unit's four-artifact set. **No form validation section applies** — `ui-history` has **no input, no form, no write path** (INV-FAITHFUL); the only interactions are read-navigation (select a row, change page, back, retry).

---

## 1. Component hierarchy

```text
AppFrame (ui-shell, frozen)
└── Panel (ui-shell, frozen — history container)
    └── HistoryView                       [STATEFUL — the only stateful component; owns both reads + master-detail state]
        ├── HistoryStateView              [presentational — loading / empty / error screens]
        ├── (list state)
        │   ├── HistoryList               [presentational — R6 rows]
        │   │   └── (DecisionSummary row × N)
        │   └── HistoryPagination         [presentational — page controls over page.total]
        └── (detail state)
            └── DecisionDetail            [presentational — R7 AuditRecord, strictly read-only]
                ├── SystemRecommendationRegion   [presentational — SYSTEM namespace, engine-attributed]
                │   └── ReadOnlyRegion (ui-shell, frozen)
                │       ├── RecommendationBadge (ui-shell, frozen)
                │       └── ConfidenceBadge     (ui-shell, frozen)
                ├── CommittedActionRegion         [presentational — HUMAN namespace]
                ├── ForensicTupleRegion           [presentational — forensic/replay fields, read-only]
                ├── RuleResultsRegion             [presentational — rule_results, faithful/summarized-expandable]
                └── ProfileSnapshotRegion         [presentational — ApplicantProfile snapshot, read-only]
```

Two regions are the **load-bearing structural pair**: `SystemRecommendationRegion` (system) and `CommittedActionRegion` (human) are **distinct sibling nodes** — the concrete BR-HIST-2 namespace separation. All ui-shell components are **frozen** (imported + composed, never edited); all `History*`/`*Region` components are **local** to `frontend/src/history/`.

---

## 2. State ownership (single stateful component)

`HistoryView` is the **only** stateful component. It holds:

| State | Type / values | Purpose |
|---|---|---|
| `state` | `HISTORY_STATE ∈ {LIST_LOADING, LIST, LIST_EMPTY, LIST_ERROR, DETAIL_LOADING, DETAIL, DETAIL_ERROR}` | drives which subtree renders (`business-logic-model.md §1`) |
| `page` | `int` (1-based) | the **current list page** — **preserved across the detail excursion** (HIST-Fold-1) |
| `items` | `DecisionSummary[]` | the current page's rows — **retained** while in detail so **Back** needs no refetch |
| `pageInfo` | `{ page, size, total }` | R6 `page` wrapper — drives `HistoryPagination` |
| `record` | `AuditRecord \| null` | the resolved R7 detail (null until a row is selected) |
| `error` | `{ error:{code,message,detail} } \| null` | the last normalized error envelope (list or detail) |

> All child components are **presentational** (pure functions of props). No child holds fetch state, Role, a router, or any write/commit reference (INV-FAITHFUL / BR-HIST-3/7).

---

## 3. Component props & responsibilities

| Component | Props (JSX) | Responsibility | API integration |
|---|---|---|---|
| **`HistoryView`** | `{ fetchSeam }` — `fetchSeam = { fetchList(page,size), fetchDetail(decision_id) }` (injected) | Owns state (§2) + the master-detail machine. Mount → R6 page 1. Row select → R7 by id → detail. Back → list at preserved page (no refetch). Retry → state-aware refetch. Emits nothing upward; reads no Role; imports no router; holds no write seam. | **R6 + R7** (via injected `historyFetchSeam`) |
| **`HistoryStateView`** | `{ state, error, onRetry, testid }` | Presentational screens for `*Loading` (placeholder), `listEmpty` ("no decisions yet"), `listError`/`detailError` (`error.message` + Retry). Renders `error.code` only via testid; never renders `error.detail`. | — (renders the error envelope; 404 generic) |
| **`HistoryList`** | `{ items, onSelect, testid }` | Renders each `DecisionSummary` as a row (`history-row-<decision_id>`) showing the **human** `COMMIT_ACTION_LABELS[action]` + `timestamp`; a row calls `onSelect(decision_id)`. Preserves backend order. **No system recommendation in the row** (R6 omits it — Q4-A). | consumes **R6** `items` |
| **`HistoryPagination`** | `{ page, size, total, onPageChange, testid }` | Prev/next/page controls over `total`; a page change calls `onPageChange(next)` → bounded single-page R6 fetch (PERF-1). Mirrors `ui-queue`'s local `PaginationControls`. | drives **R6** paging |
| **`DecisionDetail`** | `{ record, testid }` where `record: AuditRecord` | Composes the five read-only regions; **no edit affordance, no mutation seam** (BR-HIST-3). Renders `status` display-only; no superseded behavior (BR-HIST-11). | consumes **R7** `record` |
| **`SystemRecommendationRegion`** | `{ recommendation, confidence, testid }` (from `audit_tuple.rule_results`) | Composes frozen `ReadOnlyRegion` around `RecommendationBadge` + `ConfidenceBadge`, framed engine-attributed (**system** namespace). Values render **only** here (BR-HIST-2). | R7 `audit_tuple.rule_results` |
| **`CommittedActionRegion`** | `{ action, reason, underwriterId, testid }` (from `committed_decision`) | **Human** namespace: `COMMIT_ACTION_LABELS[action]`; `reason` shown **iff** `action === 'override'`; `underwriter_id`. Distinct node from the system region; `override` never rendered as `DECLINE-RECOMMEND`. Heading realizes CON-BR4 "decision" per HIST-Fold-4. | R7 `committed_decision` |
| **`ForensicTupleRegion`** | `{ auditTuple, contentHash, status, testid }` | Read-only forensic/replay fields: `rulebook_version`, `model_version`, `engine_version`, `memo_hash`, `content_hash`, tuple `timestamp`, `status` (display-only). Frames the record as immutable audit metadata. | R7 `audit_tuple` + `applicant_profile_snapshot.content_hash` + `status` |
| **`RuleResultsRegion`** | `{ ruleResults, testid }` where `ruleResults: RuleResultReport` | Renders `rule_results` **faithfully** (every entry, backend order) at a **summarized/expandable** level; concrete widget deferred (HIST-Fold-2). No lossy truncation. | R7 `audit_tuple.rule_results` |
| **`ProfileSnapshotRegion`** | `{ profile, applicationId, contentHash, testid }` | Renders the verbatim `ApplicantProfile` snapshot **read-only**; demographics are displayed forensic input, not a scored feature. | R7 `applicant_profile_snapshot` |

---

## 4. User-interaction flows

**Flow A — browse the list (R6)**
1. `HistoryView` mounts → `listLoading` → `fetchSeam.fetchList(1, size)`.
2. Resolves non-empty → `list`: `HistoryList` renders rows, `HistoryPagination` renders controls.
3. Resolves empty → `listEmpty`: "no decisions yet".
4. Fails → `listError`: message + Retry (re-fetches the **last-requested page**, HIST-Fold-1).
5. Page change → `onPageChange(next)` → `listLoading` for that page (PERF-1 single page).

**Flow B — open a decision detail (R7)**
1. In `list`, activating a row → `onSelect(decision_id)` → `detailLoading` → `fetchSeam.fetchDetail(decision_id)`. `page`/`items` retained.
2. Resolves → `detail`: `DecisionDetail` renders the five read-only regions + **Back**.
3. Fails (incl. **404 `not_found`**) → `detailError`: message + Retry (re-fetches the **same `decision_id`**); 404 handled generically (HIST-Fold-3).

**Flow C — back to list**
1. In `detail`, activating **Back** (`history-detail-back`) → `state = list` at the **same page**, **same items**, **no refetch** (HIST-Fold-1).

> **No write/commit/edit flow exists** — there is no Approve/Override/Confirm/submit interaction anywhere in `ui-history` (INV-FAITHFUL / BR-HIST-3). The only interactions are read-navigation (select, paginate, back, retry).

---

## 5. WIRE-1 integration points (which endpoint each component depends on)

| Endpoint (frozen WIRE-1) | Shape | Consumed by | Notes |
|---|---|---|---|
| **R6** `GET /decisions?page=&size=` | list wrapper of `DecisionSummary` | `HistoryView` (fetch) → `HistoryList` + `HistoryPagination` | authenticated any-role; offset/limit 1-based; PERF-1 bounded single page; carries the **human** `action` + `timestamp`, **not** the system recommendation |
| **R7** `GET /decisions/{decision_id}` | `AuditRecord` | `HistoryView` (fetch) → `DecisionDetail` + its five regions | authenticated any-role; single-resource-by-id; **404 `not_found`** surfaced generically; the **only** source of the system recommendation (via `audit_tuple.rule_results`) |

Both reads go through the injected **`historyFetchSeam`** (`createHistoryFetch(transport) → { fetchList, fetchDetail }` + `buildHistoryListRequest` / `buildHistoryDetailRequest` + `normalizeError`), which **mirrors** — never imports — the frozen `queue/fetchSeam.js` (list) and `memoView/memoFetchSeam.js` (by-id) shapes, and contains **no write-body builder** (BR-HIST-3/4). The real transport is wired at the composition root (deferred / Build & Test); a capturing double is used in tests.

---

## 6. What is NOT a component here (boundary)

- **No `RoleGate`** — view-only for all authenticated roles; a `noRoleGateImport` StructuralGuard enforces its absence (BR-HIST-7 / Q3-A). `can="read"` deliberately not used (would exclude `admin`).
- **No form / input / submit / commit component** — no write path (INV-FAITHFUL); no Approve/Override affordance (those are U7/U8).
- **No router** — master-detail navigation is internal `HistoryView` state; no cross-unit or cross-route navigation is designed in Phase 1.
- **No shared primitive added to `ui-shell`** — `HistoryPagination` and the list/detail regions are **history-local** (ui-shell frozen); the reused frozen primitives are `AppFrame` / `Panel` / `ReadOnlyRegion` / `RecommendationBadge` / `ConfidenceBadge` only.
- **No superseded/version component** — `status`/`supersedes_decision_id` are display-only fields, not a navigable version tree (BR-HIST-11 / HIST-Fold-3).
