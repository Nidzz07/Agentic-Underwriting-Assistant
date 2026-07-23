# Domain Entities — `ui-memo-view` (U6)

**Stage**: BUILD → Functional Design (per-unit) · **Unit**: U6 `ui-memo-view` · C5 · Phase 1 · **Depth**: lighter (display) +
fetch-lifecycle addendum + three-region read-only-separation addendum · **Date**: 2026-07-09 · Story **US-UI-2** ·
FR-MEMO-3 / NFR-EXPLAIN-1 / FR-UI-3 / FR-UI-5.
**Scope**: the memo view — a **presentational, read-only** view that fetches WIRE-1 **R4**
(`GET /applications/{application_id}/memo`) and renders the **MemoView** envelope, whose `ready` form carries the
**DecisionMemo three-region** shape (L narrative · D missing-info · RO recommendation). A UI unit's "entities" are its
**component/module + prop-shape inventory** (not data records) — the component hierarchy/props are folded here (mirroring
`ui-queue` domain-entities §, no dedicated `frontend-components.md`). **React + Tailwind, NO TypeScript** (FR-UI-5).
`ui-memo-view` owns **no business logic** — no rule eval, no authorization *decision*, no LLM, no commit; it **imports no
backend production code** and consumes backend **shapes by value** (reference-not-own).

---

## 1. Location & composition boundary

`ui-memo-view` lives at **`frontend/src/memoView/`**. It **imports** `ui-shell` (frozen, U10) primitives + copy + session
context + the `ReadOnlyRegion` primitive and **composes** them; it **defines its own local regions/lists + a local memo
`fetchSeam`** (Q3-A / Q6-A) — **nothing is promoted into `ui-shell`** (ui-shell stays frozen). It **does not import
`ui-queue`** (frozen, U5) — it **mirrors** ui-queue's fetchSeam + StructuralGuard **convention** (Q6-A), not the module.
It renders exactly one screen (the memo) inside the shell `AppFrame`.

| Consumes from `ui-shell` (frozen) | Used for |
|---|---|
| `AppFrame` | page shell / layout chrome (the memo view mounts inside it) |
| `Panel` / `Region` | bordered container for the memo regions + states |
| **`ReadOnlyRegion { children, testid }`** (`aria-readonly`) | **first use** — wraps the **RO** region so it is framed read-only & engine-attributed (Q5-A) |
| `RecommendationBadge { value, testid }` | renders the memo's system `Recommendation` value inside the RO region (looks up its own label) |
| `ConfidenceBadge { value, testid }` | renders the memo's `Confidence` value inside the RO region |
| `shell/copy` (`RECOMMENDATION_LABELS` / `CONFIDENCE_LABELS`, `ADVISORY_VOCABULARY`, the one `FORBIDDEN_TERMS`) | **all** enum display strings + advisory-vocabulary conformance (BR-MEMO-1 / BR-MEMO-2: never inline) |
| `shell/session` (`RoleContext`, `useCurrentRole()`) | available, but **not gated on** (N2 view-only) |

> **Not consumed**: `RoleGate` (N2 — view-only, no gating; the commit path is U7 `ui-approval-gate`). No backend Python
> import (the cross-language reference-not-own boundary, U10 §5). No `ui-queue` import (Q6-A — sibling convention, not a
> dependency).

---

## 2. Consumed value shapes (by value, from WIRE-1 R4 — **not owned, not re-cased**)

These mirror the **frozen** WIRE-1 §5 + `memo_agent_core.schemas` shapes verbatim; enum fields carry the WIRE-1 §1 wire
values (Recommendation UPPERCASE incl. `DECLINE-RECOMMEND`; Confidence Title-case). `ui-memo-view` **defines no schema** —
it reads these off the R4 response.

| Shape | Definition (as delivered by WIRE-1 R4) | Notes |
|---|---|---|
| **`MemoView`** (R4 body) | `{ application_id: str, recommendation_id: str \| null, status: "ready" \| "pending", profile: ApplicantProfile \| null, report: RuleResultReport \| null, memo: DecisionMemo \| null }` | `status` is the **render discriminator** (N1) — `pending` ⇒ `report`/`memo` null (memo not yet drafted); `ready` ⇒ all present |
| **`DecisionMemo`** (`memo`, ready only) | `{ narrative_prose: str, cited_rule_ids: str[], missing_information: MissingInformationItem[], recommendation: <Recommendation value>, confidence: <Confidence value>, memo_hash: str, model_version: str }` | the **three regions** — L (`narrative_prose`+`cited_rule_ids`) · D (`missing_information`) · RO (`recommendation`+`confidence`, injected read-only) · M (`memo_hash`+`model_version`); **CON-BR2-TYPE** (the LLM never produced recommendation/confidence) |
| **`MissingInformationItem`** (D list item) | `{ source: <MissingInfoSource value>, detail: str }` | `source ∈ {missing_document, unparseable_document, not_evaluated_rule, incomplete_flag}`; **no** display label in frozen `shell/copy` → memo-local copy (§5, Q4-A). Order is the backend's deterministic total order (MISSINGINFO-1) — the view **preserves** it (BR-MEMO-9) |
| **`ApplicantProfile`** (`profile`) | `intake.schema.ApplicantProfile` (verbatim) | source for the **minimal context header** (§4); the view reads a small identifying subset, renders it read-only |
| **Error envelope** (non-2xx / transport) | `{ error: { code: str, message: str, detail?: obj } }` | `message` → user; `code` → testid binding; `detail` **never** rendered raw (BR-MEMO-6) — same shape ui-queue's `normalizeError` guarantees |

> **`report` (RuleResultReport)** is delivered on `ready` but the memo's RO region renders **`memo.recommendation` /
> `memo.confidence`** (the injected read-only values that CON-BR2-TYPE governs), not `report`. `report` is **not** a
> render source in this lighter view (no rule-result table in Phase 1) — named-not-rendered here.

---

## 3. Render-state model (the fetch-lifecycle addendum — first-class FD concern)

A single closed enum drives what `MemoView` renders. Full transition semantics live in `business-logic-model.md §1`.

| State | Meaning | Renders |
|---|---|---|
| `loading` | R4 fetch in flight | a loading placeholder (`MemoStateView`) |
| `ready` | fetch resolved, `status: "ready"` | the **three-region memo** (context header + `NarrativeRegion` + `MissingInfoRegion` + `ReadOnlyRecommendationRegion`) |
| `pending` | fetch resolved, `status: "pending"` | a distinct full-page **"memo not yet drafted for this application"** message (`MemoStateView`) — **derived from the `status` discriminator, not an empty-array check** (N1) |
| `error` | R4 fetch failed (any non-2xx or transport error) | `error.message` + a **Retry** affordance (`MemoStateView`) |

> **State enum** (a local view constant, not a backend enum): `MEMO_STATE = { LOADING, READY, PENDING, ERROR }`.
> **Contrast with `ui-queue`**: ui-queue's `empty` is derived from `items.length`; here `pending` is derived from the R4
> **`status`** field — a pinned twist (N1), pinned in `business-logic-model.md §1`.

---

## 4. Component / module inventory (hierarchy + prop shapes — JS/JSX, no TS)

**Hierarchy**

```text
AppFrame (ui-shell)
└── Panel  (ui-shell — memo container)
    └── MemoView                       [owns fetch + render-state; the only stateful component]
        ├── MemoStateView              [loading | pending | error presentational states]
        └── (ready state)
            ├── ProfileContextHeader   [minimal identifying header from profile]      (local)
            ├── NarrativeRegion        [L: narrative_prose]                            (local)
            │   └── CitationsList      [L: cited_rule_ids -> presentational list]      (local, Q3-A)
            ├── MissingInfoRegion      [D: missing_information -> presentational list] (local, Q3-A)
            │   └── (row x N)          [{ source-label (memo copy), detail }]
            └── ReadOnlyRecommendationRegion   [RO region]                            (local, Q5-A)
                └── ReadOnlyRegion (ui-shell)  [frozen wrapper, engine-attributed]
                    ├── RecommendationBadge (ui-shell)
                    └── ConfidenceBadge     (ui-shell)
```

**Prop shapes**

| Component | Prop shape (JSX) | Role / behavior |
|---|---|---|
| **`MemoView`** | `{ applicationId, fetchSeam }` — `fetchSeam` injected (Q6-A, mirrors ui-queue's prop injection) | The **only** stateful component: fetches R4 for `applicationId`, holds `{ state, view, error }` (`view` = the resolved `MemoView` body), and selects `MemoStateView` vs the ready three-region composition. Emits nothing upward (view-only, N2). |
| **`MemoStateView`** | `{ state, error, onRetry, testid }` — `state ∈ {loading, pending, error}` | Presentational. `loading` → loading placeholder; `pending` → the distinct **"memo not yet drafted"** page (memo-local copy, §5); `error` → `error.message` + a Retry button wired to `onRetry`. Renders **no** memo regions. |
| **`ProfileContextHeader`** | `{ profile, testid }` where `profile: ApplicantProfile` | Presentational. Renders a **minimal** identifying context header (e.g. `application_id`, applicant name, derived age, requested cover) read from `profile`; renders **read-only**, no affordance. Full profile-field treatment deferred to Code-Gen (lighter — no gate question, N3). |
| **`NarrativeRegion`** | `{ narrative, testid }` where `narrative: str` (`narrative_prose`) | Presentational (**L** region). Renders the LLM-authored `narrative_prose` as read-only body text; **visually + structurally distinct** from the RO region (BR-MEMO-3). Composes `CitationsList`. The view **does not lint** this runtime prose (MEMO-Fold-1 scope boundary — that is memo-agent-core's CON-BR2 concern). |
| **`CitationsList`** | `{ citedRuleIds, testid }` where `citedRuleIds: str[]` | Presentational (**L** sub-list, Q3-A). Renders `cited_rule_ids` as a local presentational list **in the order given** (BR-MEMO-9); empty array → renders nothing / a neutral "no rule citations" via memo-local copy. No shared list primitive (ui-shell frozen). |
| **`MissingInfoRegion`** | `{ items, testid }` where `items: MissingInformationItem[]` | Presentational (**D** region, Q3-A). Renders `missing_information` as a local presentational list, **preserving the backend deterministic order** (BR-MEMO-9); each row shows `detail` as primary text + the `source` via the **memo-local `MISSING_INFO_SOURCE_LABELS`** (§5, Q4-A); empty → neutral "no missing information" (memo-local copy). |
| **`ReadOnlyRecommendationRegion`** | `{ recommendation, confidence, testid }` | Presentational (**RO** region, Q5-A). **Composes the frozen `ReadOnlyRegion`** wrapper (`aria-readonly`) around a `RecommendationBadge` (`value=recommendation`) + `ConfidenceBadge` (`value=confidence`), framed as **attributable to the deterministic engine** via memo-local chrome — a direct visual expression of CON-BR2 (BR-MEMO-4/5). Renders the recommendation/confidence **only** here, never inside `NarrativeRegion` (N3 / BR-MEMO-5). |

> **No outward event** (contrast ui-queue's `onSelect`): `ui-memo-view` emits **nothing** in Phase 1 — no selection, no
> commit affordance, no navigation. The commit path (R5) is U7 `ui-approval-gate`; navigation to it is a later
> shell/router integration (N2 / BR-MEMO-7). `MemoView` imports **no router**.

---

## 5. Memo-local copy module (`memoView/copy.js` — realization detail, lint-subject)

Memo-specific chrome + the `MissingInfoSource` labels are kept **out of the components** in a local copy module, mirroring
`ui-queue`'s local `copy.js` precedent (Q4-A). These are **not** domain-enum display labels — those (`Recommendation` /
`Confidence`) live in `shell/copy` and are looked up **by value** via the reused ui-shell badges. **This module is
lint-subject** (MEMO-Fold-1): it may **not** inline a shell display label (`no-inline-label`) and may **not** contain
forbidden system-output vocabulary (`advisory-vocabulary`, the **one** `FORBIDDEN_TERMS`).

| Key | Purpose | Notes |
|---|---|---|
| `MISSING_INFO_SOURCE_LABELS` | human labels for the four `MissingInfoSource` values | `missing_document` / `unparseable_document` / `not_evaluated_rule` / `incomplete_flag` → neutral phrases; **no** forbidden term; keyed **by value** (Q4-A) |
| `pendingMessage` | the full-page "memo not yet drafted for this application" text | the `status: "pending"` state (Q2-A) |
| `loadingLabel` | loading placeholder text | — |
| `retryLabel` | Retry control text | reused pattern from ui-queue chrome |
| `narrativeHeading` / `citationsHeading` / `missingInfoHeading` / `recommendationHeading` | the four region headings | region chrome; `recommendationHeading` frames the RO region as **engine-attributed** (advisory, not a decision) |
| `noCitationsLabel` / `noMissingInfoLabel` | neutral empty-list text | for empty `cited_rule_ids` / `missing_information` |
| `unknownErrorMessage` | fallback error text | mirrors ui-queue's synthesized-envelope fallback |

> **Value-collision guard (COPY/NAMESPACE)**: no value in this module equals a `shell/copy` display label, and none
> contains a `FORBIDDEN_TERMS.systemOutput` token (`DECLINE` / `decision` / `approved` / `declined`) — checked by the
> reused lints (BR-MEMO-1/2).

---

## 6. `data-testid` inventory (MEMO-Fold-2 — `memo-<element>-<purpose>`, region-level testids added)

Every assertion-relevant element carries a stable `data-testid` of shape **`memo-<element>-<purpose>`** (applying, not
re-inventing, the frozen ui-shell `shell-<primitive>-<purpose>` / ui-queue `queue-<element>-<purpose>` convention). The
**region-level** testids make the three-region separation **structurally testable** (MEMO-Fold-2): a test can assert the
**RO region is a DISTINCT node from the L narrative** (the concrete CON-BR2 structural check, BR-MEMO-3). Enforced by a
`memo-testid-convention` lint (BR-MEMO-10).

| Element | `data-testid` | Notes |
|---|---|---|
| Memo container (ready root) | `memo-view` | the `ready`-state composition root |
| Profile context header | `memo-header-context` | the minimal identifying header |
| **L narrative region** | `memo-region-narrative` | **distinct node** asserted vs the RO region (MEMO-Fold-2) |
| Citations list (L) | `memo-region-citations` | `cited_rule_ids` presentational list root |
| A single citation | `memo-citation-<rule_id>` | interpolates the cited rule id |
| **D missing-info region** | `memo-region-missinginfo` | `missing_information` list root |
| A single missing-info row | `memo-missinginfo-<index>` | index-stable per deterministic order (BR-MEMO-9) |
| **RO recommendation region** | `memo-region-readonly` | the `ReadOnlyRegion`-wrapped RO node (**distinct** from `memo-region-narrative`) |
| Recommendation value (RO) | `memo-recommendation` | the `RecommendationBadge` inside the RO region (value ∈ {APPROVE, REFER, DECLINE-RECOMMEND}) |
| Confidence value (RO) | `memo-confidence` | the `ConfidenceBadge` inside the RO region |
| Loading state | `memo-state-loading` | loading placeholder container |
| Pending state | `memo-state-pending` | the "not yet drafted" full-page message (derived from `status`, N1) |
| Error state | `memo-state-error` | error container |
| Error message (visible) | `memo-error-message` | carries `error.message` (BR-MEMO-6) |
| Error code (hidden binding) | `memo-error-code` | carries `error.code` for test assertion / console — **not** visible UI text |
| Retry control | `memo-error-retry` | wired to `onRetry` (re-fetch R4 for the same `applicationId`, BR-MEMO-6) |

> Region-level shell badges reuse the shell testid convention passed through as props (the view supplies
> `memo-recommendation` / `memo-confidence`; the badge is a frozen shell primitive). The frozen `ReadOnlyRegion` receives
> `testid="memo-region-readonly"`.

---

## 7. Boundary — what `ui-memo-view` does NOT own

- **No authorization decision** — R4 is authenticated any-role; the memo view renders **no `RoleGate`** and gates nothing
  (N2). The real boundary stays `auth-rbac` server-side.
- **No commit / gate / override** — no write path, **no commit affordance**; those are U7 `ui-approval-gate` / U8
  `ui-override-form`. The view never renders a human `CommitAction` (`approve`/`override`) — only the **system**
  `Recommendation` (N3 / BR-MEMO-11). The two namespaces are never conflated.
- **No routing** — the view emits **no** outward action in Phase 1 and imports **no router**; navigation to the commit
  path is a later shell/router integration (N2 / BR-MEMO-7).
- **No advisory-language authoring** — the view renders the LLM-authored `narrative_prose` as-is; it **does not lint or
  rewrite** runtime prose (MEMO-Fold-1 scope boundary — CON-BR2 conformance of the prose is memo-agent-core's backend
  concern). The view's job is the **structural read-only separation** + advisory-clean **chrome**.
- **No display-string definition for enums** — every `Recommendation`/`Confidence` label comes from `shell/copy`
  (BR-MEMO-1); the memo-local copy holds only chrome + `MissingInfoSource` labels (§5), which are lint-subject.
- **No token values / no schema** — aesthetics come from `shell/tokens` (values deferred); shapes come from WIRE-1 R4 /
  memo-agent-core (by value).
- **No route implementation** — the R4 endpoint itself is `backend/app/main.py`, deferred to Build & Test (WIRE-1 §, not
  this unit); `ui-memo-view` consumes the R4 **contract shape**, fetching a mocked R4 (via the injected `fetchSeam`) in tests.
