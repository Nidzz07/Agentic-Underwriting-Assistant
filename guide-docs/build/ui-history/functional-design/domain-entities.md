# Domain Entities — `ui-history` (U9)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U9 `ui-history` · C5 · Phase 1 · **Depth**: lighter (display) + two named display-side invariants (INV-FAITHFUL, INV-NAMESPACE) + a **master-detail (list↔detail) addendum** · **Date**: 2026-07-14 · Story **US-UI-6** · FR-UI-1 / CON-AUDIT-1 (read surface) / FR-UI-3 / FR-UI-5.
**Scope**: the decision-history view — a **presentational, read-only** view that fetches WIRE-1 **R6** (`GET /decisions?page=&size=`, the paged list of **DecisionSummary**) and, on selecting a row, WIRE-1 **R7** (`GET /decisions/{decision_id}`, the full **AuditRecord**), and renders the audit trail the frozen write-path units (U7/U8) produced. A UI unit's "entities" are its **component/module + prop-shape inventory** (not data records) — the full component hierarchy/props are also broken out in `frontend-components.md` (per this unit's four-artifact set). **React + Tailwind, NO TypeScript** (FR-UI-5). `ui-history` owns **no business logic** — no rule eval, no authorization *decision*, no LLM, and **no write path** (no commit, no gate, no mutation seam); it **imports no backend production code** and consumes backend **shapes by value** (reference-not-own).

---

## 1. Location & composition boundary

`ui-history` lives at **`frontend/src/history/`**. It **imports** `ui-shell` (frozen, U10) primitives + copy + session context and **composes** them; it **defines its own local list/detail components + a local read-only `historyFetchSeam`** (Q2-A), **mirroring** — never importing — the frozen sibling read-only seam shapes (`ui-queue` R6-analog list seam; `ui-memo-view` R4-analog by-id seam). **Nothing is promoted into `ui-shell`** (ui-shell stays frozen). It renders exactly one surface (history: a list and its per-record detail) inside the shell `AppFrame`.

| Consumes from `ui-shell` (frozen) | Used for |
|---|---|
| `AppFrame` | page shell / layout chrome (the history view mounts inside it) |
| `Panel` / `Region` | bordered container for the list, the detail, and the state screens |
| **`ReadOnlyRegion { children, testid }`** (`aria-readonly`) | wraps the **system-recommendation** sub-region of the detail so it is framed read-only & **engine-attributed** (INV-NAMESPACE; the CON-BR2/advisory framing, reused as `ui-memo-view` did) |
| `RecommendationBadge { value, testid }` | renders the **system** `Recommendation` value (from `audit_tuple.rule_results.recommendation`) inside the detail's read-only system region (looks up its own label) |
| `ConfidenceBadge { value, testid }` | renders the system `Confidence` value (from `audit_tuple.rule_results.confidence`) inside the same region |
| `shell/copy` (`RECOMMENDATION_LABELS` / `CONFIDENCE_LABELS` / `COMMIT_ACTION_LABELS`, `ADVISORY_VOCABULARY`, the one `FORBIDDEN_TERMS`) | **all** enum display strings — **system** recommendation/confidence **and** the **human** `CommitAction` (`approve`/`override`) — looked up **by value** (BR-HIST-1); advisory-vocabulary conformance (BR-HIST-2) |
| `shell/session` (`RoleContext`, `useCurrentRole()`) | available, but **not gated on** — history is view-only for all roles (Q3-A / BR-HIST-7) |

> **Not consumed**: `RoleGate` (Q3-A — pure read surface, nothing to gate; a `noRoleGateImport` StructuralGuard enforces this, mirroring `ui-queue`'s VIEWONLY-1). No backend Python import (the cross-language reference-not-own boundary). No sibling-unit import (`ui-queue`/`ui-memo-view`/`ui-approval-gate`/`ui-override-form` are **mirrored conventions, not dependencies**). **No `submit*` / commit builder, no write transport** (INV-FAITHFUL — the write-path discipline of U7/U8 is deliberately NOT inherited).

---

## 2. Consumed value shapes (by value, from WIRE-1 R6/R7 — **not owned, not re-cased**)

These mirror the **frozen** WIRE-1 §5 + `audit_store.record_schema` shapes verbatim; enum fields carry the WIRE-1 §1 wire values (Recommendation UPPERCASE incl. `DECLINE-RECOMMEND`; Confidence Title-case; `CommitAction` lowercase `approve`/`override`). `ui-history` **defines no schema** — it reads these off the R6/R7 responses.

| Shape | Definition (as delivered by WIRE-1) | Notes |
|---|---|---|
| **List wrapper** (R6 body) | `{ items: DecisionSummary[], page: { page:int, size:int, total:int } }` | A4 offset/limit, **1-based** `page`; the same wrapper `ui-queue`'s R2 uses. `items: []` ⇒ the **empty** state (BR-HIST-8). |
| **`DecisionSummary`** (R6 list item) | `{ decision_id: str, application_id: str, recommendation_id: str, action: <CommitAction value>, timestamp: ISO-8601 }` | The list item carries the **HUMAN `action`** (`approve`/`override`) + `timestamp` + ids — **NOT** the system `recommendation`/`confidence` (Q4-A: those live only in R7's detail). `decision_id` is the R7 key. |
| **`AuditRecord`** (R7 body) | `{ decision_id, application_id, recommendation_id, audit_tuple, applicant_profile_snapshot, committed_decision, status, supersedes_decision_id \| null }` | `audit_store.record_schema.AuditRecord` verbatim (`frozen=True`, `extra="forbid"`). The detail render source (BR-HIST-4/5/6). |
| ↳ **`AuditTuple`** | `{ rulebook_version: str, rule_results: RuleResultReport, timestamp, model_version: str, memo_hash: str, engine_version: str }` | The forensic/replay 6-tuple. **The system `recommendation`/`confidence` live INSIDE `rule_results`** (`RuleResultReport.recommendation` / `.confidence`) — the detail's system-region source (Q4-A). |
| ↳ **`RuleResultReport`** (`rule_results`) | `{ rule_results[], recommendation, confidence, rulebook_version, content_hash, engine_version, decline_reasons[], refer_reasons[] }` | Rendered **faithfully with no lossy omission** at a **summarized/expandable** level (Q6-A / HIST-Fold-2); `recommendation`/`confidence` surface as the **system** advisory values in the read-only system region. |
| ↳ **`CommittedDecision`** (`committed_decision`) | `{ recommendation_id: str, underwriter_id: str, action: <CommitAction>, reason: str \| null }` | The **human** committed-action linkage (the one place "decision" is the correct word). `reason` is present (non-blank) on `override`, `null`/absent on `approve`. The detail's human-region source (Q4-A / BR-HIST-6). |
| ↳ **`ApplicantProfileSnapshot`** (`applicant_profile_snapshot`) | `{ application_id: str, profile: ApplicantProfile, content_hash: str }` | The persisted verbatim original input + tamper-evidence hash; rendered **read-only** (Q6-A). Its demographic fields are **persisted forensic input, NOT a feature vector** → displaying them is not a bias-swap concern (HIST note). |
| ↳ **`status` / `supersedes_decision_id`** | `status ∈ {active, superseded}`; `supersedes_decision_id: str \| null` | **Write-once `active` in Phase 1/2**; `supersedes_decision_id` **always `null`** in Phase 1/2. Rendered **display-only** — **no** superseded branch, **no** dereference/link, **no** supersede affordance is designed (HIST-Fold-3; OOS-7/Phase-3 seam, named-not-designed). |
| **Error envelope** (non-2xx / transport, R6 or R7) | `{ error: { code: str, message: str, detail?: obj } }` | `message` → user; `code` → testid binding; `detail` **never** rendered raw (BR-HIST-9). R7's `not_found` (404) flows through this **generic** shape — no special-casing (HIST-Fold-3). Same shape the mirrored `normalizeError` guarantees. |

> **`decision_id` is the join** between the two reads: a `DecisionSummary.decision_id` in the list is the path key for the R7 detail fetch (`buildHistoryDetailRequest(decision_id)`). The list carries `recommendation_id` (the committed pending recommendation) but the **system recommendation VALUE** is only obtainable via R7 (Q4-A).

---

## 3. Render-state model (the master-detail fetch-lifecycle addendum — first-class FD concern)

A single closed enum drives what `HistoryView` renders. Full transition semantics live in `business-logic-model.md §1`. Unlike the single-resource `ui-memo-view`, `ui-history` has **two** read surfaces (a paged list and a by-id detail) in **one** stateful component.

| State | Meaning | Renders |
|---|---|---|
| `listLoading` | R6 fetch in flight | a loading placeholder (`HistoryStateView`) |
| `list` | R6 resolved, `items` non-empty | the **paged decision list** (`HistoryList` + pagination) |
| `listEmpty` | R6 resolved, `items: []` | a page-level **"no decisions yet"** message (`HistoryStateView`) — derived from `items.length === 0` (the `ui-queue` `empty` precedent) |
| `listError` | R6 fetch failed (any non-2xx / transport) | `error.message` + a **Retry** that re-fetches the **last-requested page** (position-preserving, HIST-Fold-1) |
| `detailLoading` | R7 fetch in flight (a row was selected) | a loading placeholder (`HistoryStateView`) |
| `detail` | R7 resolved | the **read-only `AuditRecord` detail** (`DecisionDetail`) + a **Back** control |
| `detailError` | R7 fetch failed (any non-2xx incl. **404 `not_found`**, or transport) | `error.message` + a **Retry** that re-fetches the **same `decision_id`**; **404 is surfaced generically** (HIST-Fold-3) |

> **State enum** (a local view constant, not a backend enum): `HISTORY_STATE = { LIST_LOADING, LIST, LIST_EMPTY, LIST_ERROR, DETAIL_LOADING, DETAIL, DETAIL_ERROR }`.
> **Page position is orchestrator state, preserved across the detail excursion** (HIST-Fold-1): selecting a row → `detailLoading`; **Back** returns to `list` at the **same page** with the **same items** (no refetch), because `HistoryView` holds `{ page, items }` — the position-preserving discipline the frozen `QueueView.jsx` established (its Retry re-fetches the last-requested page, never resets to page 1).

---

## 4. Component / module inventory (hierarchy + prop shapes — JS/JSX, no TS)

**Hierarchy** (also in `frontend-components.md`)

```text
AppFrame (ui-shell)
└── Panel  (ui-shell — history container)
    └── HistoryView                      [owns both reads + master-detail state; the only stateful component]
        ├── HistoryStateView             [listLoading | listEmpty | listError | detailLoading | detailError]
        ├── (list state)
        │   ├── HistoryList               [R6 rows: action + timestamp; onSelect(decision_id)]   (local)
        │   │   └── (row x N)             [{ decision_id, action-label (shell copy), timestamp }]
        │   └── HistoryPagination         [prev/next/page over page.total]                        (local, mirrors queue)
        └── (detail state)
            └── DecisionDetail            [R7 AuditRecord, read-only, no edit affordance]          (local, Q6-A)
                ├── SystemRecommendationRegion  [engine-attributed, read-only]                     (local)
                │   └── ReadOnlyRegion (ui-shell) [frozen wrapper]
                │       ├── RecommendationBadge (ui-shell)  [value = rule_results.recommendation]
                │       └── ConfidenceBadge     (ui-shell)  [value = rule_results.confidence]
                ├── CommittedActionRegion        [human namespace: action + reason + underwriter]   (local, Q4-A)
                ├── ForensicTupleRegion          [rulebook/model/engine version + hashes + status]  (local)
                ├── RuleResultsRegion            [rule_results faithful, summarized/expandable]      (local, HIST-Fold-2)
                └── ProfileSnapshotRegion        [ApplicantProfile snapshot, read-only]             (local)
```

**Prop shapes**

| Component | Prop shape (JSX) | Role / behavior |
|---|---|---|
| **`HistoryView`** | `{ fetchSeam }` — `fetchSeam` injected (Q2-A, mirrors the sibling prop-injection convention); `fetchSeam = { fetchList(page,size), fetchDetail(decision_id) }` | The **only** stateful component. Holds `{ state, page, items, pageInfo, record, error }`. On mount fetches R6 page 1; on row `onSelect(decision_id)` fetches R7 and enters `detailLoading→detail`; on **Back** returns to `list` at the preserved page (no refetch, HIST-Fold-1). Emits **nothing** upward (view-only). Reads **no** Role, composes **no** `RoleGate` (Q3-A). Holds **no** write/commit reference (INV-FAITHFUL). |
| **`HistoryStateView`** | `{ state, error, onRetry, testid }` — `state ∈ {listLoading, listEmpty, listError, detailLoading, detailError}` | Presentational. `*Loading` → loading placeholder; `listEmpty` → the **"no decisions yet"** page (history-local copy); `listError`/`detailError` → `error.message` (visible) + `error.code` (testid-only) + a **Retry** wired to `onRetry`. Renders **no** list/detail content. |
| **`HistoryList`** | `{ items, onSelect, testid }` where `items: DecisionSummary[]` | Presentational. Renders each `DecisionSummary` as a row carrying a stable `data-testid` (US-UI-6 "rows carry data-testid"): the **human** `action` via `COMMIT_ACTION_LABELS[action]` + the `timestamp` (+ ids for testid keys). A row activates `onSelect(decision_id)`. **No system recommendation in the row** (Q4-A — R6 does not carry it). Preserves the backend-delivered order (re-sorts nothing). |
| **`HistoryPagination`** | `{ page, size, total, onPageChange, testid }` | Presentational. Prev/next/page controls over `page.total`; activating a page issues `onPageChange(next)` → a bounded single-page R6 fetch (PERF-1). Mirrors `ui-queue`'s local `PaginationControls` convention (ui-shell frozen; a history-local component, not a shared primitive). |
| **`DecisionDetail`** | `{ record, testid }` where `record: AuditRecord` | Presentational, **strictly read-only, no edit affordance, no mutation seam** (INV-FAITHFUL). Composes the five detail sub-regions below. Renders `status` **display-only**; designs **no** superseded/`supersedes_decision_id` behavior (HIST-Fold-3). |
| **`SystemRecommendationRegion`** | `{ recommendation, confidence, testid }` (from `audit_tuple.rule_results`) | Presentational. **Composes the frozen `ReadOnlyRegion`** around a `RecommendationBadge` (`value = recommendation`) + `ConfidenceBadge` (`value = confidence`), framed via history-local chrome as **engine-attributed** (the **system**, advisory namespace — INV-NAMESPACE). The system recommendation renders **only** here, never mixed into the human region. |
| **`CommittedActionRegion`** | `{ action, reason, underwriterId, testid }` (from `committed_decision`) | Presentational (**human** namespace, Q4-A). Renders the `CommitAction` via `COMMIT_ACTION_LABELS[action]` (`Approve`/`Override`), the `reason` when `action === 'override'` (present/non-blank), and `underwriter_id`. Framed as the **human's committed action** — distinct from the system region (INV-NAMESPACE; BR-HIST-2 governs the "decision" vocabulary). The human `override` is **never** rendered as the system `DECLINE-RECOMMEND`. |
| **`ForensicTupleRegion`** | `{ auditTuple, contentHash, status, testid }` | Presentational. Renders the forensic/replay fields read-only: `rulebook_version`, `model_version`, `engine_version`, `memo_hash`, `content_hash`, the tuple `timestamp`, and `status` (display-only). No copy/edit affordance beyond plain display; frames these as an **immutable audit record** (never implies alterability). |
| **`RuleResultsRegion`** | `{ ruleResults, testid }` where `ruleResults: RuleResultReport` | Presentational (HIST-Fold-2). Renders `rule_results` **faithfully** — **every entry preserved, none dropped** — at a **summarized/expandable** level (progressive disclosure), preserving backend order. The concrete expand/collapse widget is an **NFR-Design/Code-Gen** realization; the FD pins only the **faithfulness rule + shape**. |
| **`ProfileSnapshotRegion`** | `{ profile, applicationId, contentHash, testid }` | Presentational. Renders the `ApplicantProfileSnapshot` (the verbatim persisted input) **read-only**. Its demographic fields are **displayed forensic input, not a scored feature** (no bias-swap concern). Field-level treatment (which subset, layout) deferred to Code-Gen. |

> **No outward event, no write path** (contrast the write-path units' `onConfirm`/`submit*`): `ui-history` emits **nothing** upward in Phase 1 and holds **no** commit/submit reference — the master-detail navigation is **internal** (`HistoryView` state), not a cross-unit hand-off (contrast `ui-queue`'s `onSelect` to `ui-memo-view`). `HistoryView` imports **no router**.

---

## 5. History-local copy module (`history/copy.js` — realization detail, lint-subject)

History-specific chrome (region headings, empty/loading/retry/back labels, forensic field labels) is kept **out of the components** in a local copy module, mirroring the `ui-queue`/`ui-memo-view` local `copy.js` precedent. These are **not** domain-enum display labels — those (`Recommendation` / `Confidence` / `CommitAction`) live in `shell/copy` and are looked up **by value** via the reused shell badges/maps (BR-HIST-1). **This module is lint-subject** (BR-HIST-2): it may **not** inline a shell display label (`no-inline-label`), and its **system-output** copy may **not** contain a `FORBIDDEN_TERMS.systemOutput` token (`DECLINE` / `decision` / `approved` / `declined`).

| Key | Purpose | Notes |
|---|---|---|
| `emptyMessage` | the page-level "no decisions yet" text | the `listEmpty` state (BR-HIST-8) |
| `loadingLabel` / `retryLabel` | list/detail loading + Retry text | reused chrome pattern from the siblings |
| `backLabel` | the detail's **Back to list** control text | returns to the preserved-page list (HIST-Fold-1) |
| `systemRecommendationHeading` | frames the read-only **system** region as **engine-attributed** (advisory) | must not read as a final verdict; system-output-scoped advisory copy |
| `committedActionHeading` | frames the **human** committed-action region | the **human** namespace — governed by **BR-HIST-2 / HIST-Fold-4**: the CON-BR4 concept "decision" is legitimate here, but the reused blanket advisory lint forbids the lexical token as system output; the exact heading wording/lint-scoping is pinned at NFR-Design (e.g. "Underwriter's committed action") **without** modifying frozen `shell` |
| `reasonHeading` / `underwriterHeading` | labels for the human `reason` / `underwriter_id` | human namespace |
| `rulebookVersionHeading` / `modelVersionHeading` / `engineVersionHeading` / `memoHashHeading` / `contentHashHeading` / `statusHeading` / `timestampHeading` | forensic-tuple field labels | plain read-only labels; frame the record as immutable audit metadata |
| `ruleResultsHeading` / `expandLabel` / `collapseLabel` | rule-results region chrome | progressive-disclosure affordance labels (HIST-Fold-2) |
| `profileSnapshotHeading` | profile-snapshot region label | read-only |
| `unknownErrorMessage` | fallback error text | mirrors the siblings' synthesized-envelope fallback |

> **Value-collision guard (COPY/NAMESPACE)**: no value in this module equals a `shell/copy` display label, and no **system-output** value contains a `FORBIDDEN_TERMS.systemOutput` token — checked by the reused lints (BR-HIST-1/2). The **human-committed** region's copy is the one place the CON-BR4 "decision" concept applies; its realization is pinned per HIST-Fold-4.

---

## 6. `data-testid` inventory (`history-<element>-<purpose>` — rows + region-level testids)

Every assertion-relevant element carries a stable `data-testid` of shape **`history-<element>-<purpose>`** (applying, not re-inventing, the frozen `shell-<primitive>-<purpose>` / `queue-<element>-<purpose>` / `memo-<element>-<purpose>` convention). US-UI-6 **requires** history **rows** to carry data-testid; the **region-level** detail testids make the **namespace-distinct** system-vs-human rendering **structurally testable** (INV-NAMESPACE). Enforced by a `history-testid-convention` lint (BR-HIST-10); the exact regex form is pinned at NFR-Design mirroring the queue-family convention.

| Element | `data-testid` | Notes |
|---|---|---|
| History container (root) | `history-view` | the view composition root |
| List root | `history-list` | the `list`-state list root |
| A single decision row | `history-row-<decision_id>` | interpolates `decision_id`; **carries data-testid** per US-UI-6; activating it selects the detail |
| Row human action | `history-row-action` | `COMMIT_ACTION_LABELS[action]` (Approve/Override) — the human namespace |
| Row timestamp | `history-row-timestamp` | the `DecisionSummary.timestamp` |
| Pagination control | `history-pagination` | prev/next/page over `page.total` |
| Detail root | `history-detail` | the `detail`-state composition root |
| **System recommendation region** | `history-detail-system-region` | the `ReadOnlyRegion`-wrapped **engine-attributed** region (distinct node from the human region) |
| System recommendation value | `history-detail-recommendation` | `RecommendationBadge` (value ∈ {APPROVE, REFER, DECLINE-RECOMMEND}) — **system** |
| System confidence value | `history-detail-confidence` | `ConfidenceBadge` (value ∈ {High, Medium, Low}) |
| **Human committed-action region** | `history-detail-human-region` | **distinct node** from the system region (INV-NAMESPACE structural check) |
| Human action value | `history-detail-action` | `COMMIT_ACTION_LABELS[action]` (approve/override) — **human** |
| Human reason | `history-detail-reason` | rendered when `action === 'override'` (present/non-blank) |
| Underwriter id | `history-detail-underwriter` | `committed_decision.underwriter_id` |
| Forensic tuple region | `history-detail-forensic-region` | the read-only forensic/replay fields container |
| Rulebook version | `history-detail-rulebook-version` | `audit_tuple.rulebook_version` |
| Model version | `history-detail-model-version` | `audit_tuple.model_version` |
| Engine version | `history-detail-engine-version` | `audit_tuple.engine_version` |
| Memo hash | `history-detail-memo-hash` | `audit_tuple.memo_hash` |
| Content hash | `history-detail-content-hash` | `applicant_profile_snapshot.content_hash` |
| Status | `history-detail-status` | `status` — **display-only** (write-once `active`; no superseded behavior, HIST-Fold-3) |
| Rule-results region | `history-detail-ruleresults` | `rule_results` faithful/summarized-expandable (HIST-Fold-2) |
| Profile snapshot region | `history-detail-profile` | the read-only `ApplicantProfile` snapshot |
| Back to list control | `history-detail-back` | returns to the preserved-page list (HIST-Fold-1) |
| Loading state | `history-state-loading` | list/detail loading placeholder |
| Empty state | `history-state-empty` | the "no decisions yet" page (BR-HIST-8) |
| List error state | `history-state-error-list` | R6 error container |
| Detail error state | `history-state-error-detail` | R7 error container (incl. generic **404 `not_found`**, HIST-Fold-3) |
| Error message (visible) | `history-error-message` | carries `error.message` (BR-HIST-9) |
| Error code (hidden binding) | `history-error-code` | carries `error.code` for test assertion — **not** visible UI text |
| Retry control | `history-error-retry` | re-fetch last list page **or** same `decision_id` per state (HIST-Fold-1 / BR-HIST-9) |

> The frozen `ReadOnlyRegion` / `RecommendationBadge` / `ConfidenceBadge` receive their `history-*` testids as props (the view supplies them; the badge is a frozen shell primitive).

---

## 7. Boundary — what `ui-history` does NOT own

- **No write path / no mutation** — **no commit, no gate, no override, no `submit*` builder, no write transport, no edit affordance** (INV-FAITHFUL). The view **only reads** records the human already committed (U7/U8). A `noWriteSeam` / single-source StructuralGuard confirms no `buildCommitRequest`-analog or `submit*` exists under `frontend/src/history/`.
- **No authorization decision** — R6/R7 are authenticated **any-role**; the view renders **no `RoleGate`** and gates nothing (Q3-A / BR-HIST-7). The real boundary stays `auth-rbac` server-side. `can="read"` is deliberately **not** used (it would cosmetically exclude `admin`, diverging from the frozen contract).
- **No replay / re-evaluation** — the view **does not** re-run rules or the memo agent; replay is a rules-engine/CLI concern with **no WIRE-1 UI route**. The detail renders the **persisted** `AuditRecord` only.
- **No superseded/versioning logic** — `status` and `supersedes_decision_id` are rendered **display-only**; **no** superseded branch, dereference, or supersede affordance is designed (write-once `active`, `supersedes_decision_id` always `null` in Phase 1/2 — HIST-Fold-3; OOS-7/Phase-3 seam, named-not-designed).
- **No memo body** — the `AuditRecord` carries only `memo_hash`, **not** the `DecisionMemo` narrative (no embed, no route) — the detail renders the hash as a forensic field, **not** a re-rendered memo (Q6-A rejected C).
- **No display-string definition for enums** — every `Recommendation` / `Confidence` / `CommitAction` label comes from `shell/copy` (BR-HIST-1); the history-local copy holds only chrome + forensic field labels (§5), which are lint-subject.
- **No routing** — the view emits **no** outward action and imports **no** router; the master-detail navigation is **internal** to `HistoryView`. Any future cross-surface navigation is a later shell/router integration.
- **No token values / no schema** — aesthetics come from `shell/tokens` (values deferred); shapes come from WIRE-1 R6/R7 / `audit_store` (by value).
- **No route implementation** — the R6/R7 endpoints themselves are `backend/app/main.py`, deferred to Build & Test (WIRE-1 §, not this unit); `ui-history` consumes the R6/R7 **contract shapes**, fetching mocked R6/R7 (via the injected `fetchSeam`) in tests.
