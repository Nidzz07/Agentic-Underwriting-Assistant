# NFR Requirements — `ui-queue` (U5)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U5 `ui-queue` · C5 · Phase 1 · **Depth**: lighter (display) +
async-state addendum · **Date**: 2026-07-09 · Story **US-UI-1** · FR-UI-1 / FR-UI-3 / FR-UI-5 / PER-1.
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md` — **BR-QUEUE-1..9**, the
component/prop inventory, the four-state render enum, the `data-testid` inventory, the pagination/selection flows) —
**re-opening none of it**. Each `NFR-QUEUE-*` target is a **pass/fail testable assertion** traced to its FD rule.
**Tier convention inherited from `ui-shell`** (frozen U10 tech-stack): Vitest + React Testing Library + jsdom · ESLint over
the single `FORBIDDEN_TERMS` · file/import scan · detector self-tests. **Advisory-only; no LLM; no live backend** (WIRE-1
R2 mocked via a capturing/injected fetch double).

---

## 0. Central testability principle

`ui-queue`'s properties are testable **without a running backend** — R2 is exercised through a **single injected/capturing
fetch double** (Q1-A) — four ways:
1. **Build-failing lints + structural scans** — COPY-1 / NAMESPACE-1 / TESTID-1 reuse `ui-shell`'s ESLint + the **one**
   `FORBIDDEN_TERMS` source (not a second word-list); NOTS-1 / VIEWONLY-1 / SELECT-1(structural) are file/import scans.
   Each lint carries a **detector self-test** so it can never pass vacuously.
2. **Component-render assertions (RTL + jsdom)** — PENDING-1, ERROR-1, PAGINATION-1, VIEWONLY-1(render), and the four
   per-state renders of FETCH-1, using a stub `RoleContext.Provider` where role is relevant.
3. **Capturing-double assertions** — RETRY-1 (and the transition test's page leg) assert on the **requested page** recorded
   by the injected double.
4. **Observed/soft** — PERF-1 (bounded-by-pagination, non-gating) and A11Y-1 (semantic + keyboard, recorded target).

**NFR-QUEUE-Fold-1 (single-double, from the ambiguity-check)**: there is **one** fetch-double construction — the injected
function of Q1-A. Every state/transition test **programs that same double** (resolve non-empty → `ready`; resolve
`items:[]`/`total:0` → `empty`; reject / error-envelope → `error`) and reads its **recorded requested-page** only where
page-targeting is asserted (RETRY-1, the `ready→loading` page leg). **No divergent double patterns** in the suite.

**Scope**: the `NFR-QUEUE-*` set tests **only** `ui-queue`'s own view behavior; it does **not** test other UI units, any
backend unit's internals, or the WIRE-1 route implementation (R2 impl → Build & Test). It **reuses** ui-shell's frozen
mechanisms (copy/`FORBIDDEN_TERMS`/ESLint/testid convention) **without modifying** them.

---

## 1. Finalized `NFR-QUEUE-*` targets (pass/fail; acceptance criteria; test tier)

### FULL RIGOR

#### NFR-QUEUE-COPY-1 — single-source copy; no inlined display label (BR-QUEUE-1)
- **Assertion**: no Recommendation/Confidence **label literal** appears anywhere in `frontend/src/queue/`; every label is
  **imported** from `shell/copy`; badges render their label by **value look-up**.
- **Acceptance**: (a) a **build-failing ESLint rule** (the ui-shell mechanism, D4) flags any label literal outside
  `shell/copy`; (b) a `QueueRow` given `recommendation="DECLINE-RECOMMEND"` renders the label sourced from
  `RECOMMENDATION_LABELS` (never a bare `DECLINE`); (c) **detector self-test** — a synthetic inlined label is flagged.
- **Tier**: structural / lint (unit).

#### NFR-QUEUE-PENDING-1 — null recommendation/confidence → pending placeholder (BR-QUEUE-2)
- **Assertion**: a row whose `recommendation`/`confidence` are `null` renders the **pending placeholder** and no badge,
  and the row remains present.
- **Acceptance**: (a) RTL render of an `ApplicationSummary` with null values shows `queue-row-pending-<application_id>`;
  (b) **no** `RecommendationBadge`/`ConfidenceBadge` renders for that row; (c) the row is **present** (not filtered out).
- **Tier**: component (RTL).

#### NFR-QUEUE-ERROR-1 — error surfaces `message` only; `code` via testid; `detail` never raw (BR-QUEUE-3)
- **Assertion**: on an R2 failure, the visible text is `error.message` only; `error.code` is exposed only via testid;
  `error.detail` never reaches the DOM.
- **Acceptance**: with the double resolving an error body `{error:{code,message,detail}}` — (a) `queue-error-message`
  renders `message`; (b) `queue-error-code` carries `code` and it is **not** visible UI text; (c) a DOM scan finds
  `detail`'s content **nowhere** in the render.
- **Tier**: component (RTL) + structural.

#### NFR-QUEUE-RETRY-1 — Retry re-fetches the last-requested page (BR-QUEUE-4 / Fold-B)
- **Assertion**: Retry from an error on page **N** re-requests **page N**, not page 1.
- **Acceptance**: (a) the **capturing** double is configured to fail on a fetch for page **N** (N ≠ 1); (b) activating
  `queue-error-retry` issues a re-fetch whose **recorded request targets page N**; (c) **teeth** — the assertion is
  `requestedPage === N`, so the test **fails if Retry reset to page 1**.
- **Tier**: component (RTL) + capturing double (Q1-A).

#### NFR-QUEUE-SELECT-1 — selection emits only; no navigation (BR-QUEUE-5 / Q4-A)
- **Assertion**: a row's select affordance calls `onSelect(application_id)` and nothing else; `ui-queue` performs no
  navigation.
- **Acceptance**: (a) RTL — activating `queue-row-select-<application_id>` calls a spy `onSelect` **once** with that
  `application_id`; (b) **structural static scan** — `frontend/src/queue/` imports **no** router/navigation module;
  (c) no other outward call fires on select.
- **Tier**: component + structural (Q4-A).

#### NFR-QUEUE-VIEWONLY-1 — view-only; no `RoleGate` at row level (BR-QUEUE-6)
- **Assertion**: the queue renders no `RoleGate` and gates nothing by Role; render is role-invariant.
- **Acceptance**: (a) **structural** — no `RoleGate` import/usage in `frontend/src/queue/`; (b) RTL — the rendered output
  is **identical** with a stub `RoleContext.Provider` set to `underwriter`, `auditor`, and `admin` (all hold `VIEW_QUEUE`).
- **Tier**: structural + component.

#### NFR-QUEUE-TESTID-1 — `data-testid` convention (BR-QUEUE-8)
- **Assertion**: every assertion-relevant queue element carries a stable `queue-<element>-<purpose>` testid
  (`domain-entities.md §5`), applying the frozen ui-shell `shell-<primitive>-<purpose>` convention to the view namespace.
- **Acceptance**: (a) a lint/test asserts the convention across queue elements; (b) **detector self-test** — a
  missing/misnamed testid is flagged (non-vacuous).
- **Tier**: lint / component.

#### NFR-QUEUE-NOTS-1 — no TypeScript (FR-UI-5 / D2)
- **Assertion**: `frontend/src/queue/` is plain JS/JSX — no `.ts`/`.tsx`, no TS config.
- **Acceptance**: a file-scan finds **zero** `.ts`/`.tsx` under the queue tree and no `tsconfig*.json`; CI fails otherwise.
- **Tier**: structural.

#### NFR-QUEUE-FETCH-1 — R2 fetch-double + four-state machine coverage (async-state addendum / Q1-A · Q2-A · Q3-A)
- **Assertion**: R2 is fetched through the **injected/capturing double**; each of the four render states renders
  correctly; the state machine's transitions are covered by **one consolidated transition test** (Q3-A).
- **Acceptance**: (a) `QueueView` receives its fetch function via prop/context and never imports a hard-wired fetch
  (Q1-A); (b) **per-state renders** — `loading` shows `queue-state-loading` **and no table/rows render while loading**
  (Q2-A; skeleton-row count deferred), `ready` shows `queue-table`, `empty` shows `queue-state-empty`, `error` per
  ERROR-1; (c) **one consolidated transition test** exercises `loading→ready`, `loading→empty`, `loading→error`,
  `error--retry-->loading`, `ready--page-->loading`, all on the **same** double (Fold-1).
- **Tier**: component (RTL).

### MEDIUM RIGOR

#### NFR-QUEUE-NAMESPACE-1 — system `Recommendation` only, never human `CommitAction` (BR-QUEUE-7)
- **Assertion**: only system `Recommendation` values render (incl. `DECLINE-RECOMMEND`, never bare `DECLINE`); no
  lowercase human `approve`/`override` string is rendered anywhere in the queue.
- **Acceptance**: (a) **structural** — only `RecommendationBadge` (value ∈ {APPROVE, REFER, "DECLINE-RECOMMEND"}) appears;
  (b) reuses the `FORBIDDEN_TERMS` collision guard so a queue string equal to a human `CommitAction` label is flagged;
  (c) **detector self-test** — a synthetic `approve`/`override` render is flagged.
- **Tier**: structural.

### SOFT / OBSERVED

#### NFR-QUEUE-PERF-1 — bounded-by-pagination; observed, non-gating (PER-1 / Q5-A)
- **Assertion**: the queue **only ever fetches one page** (never the whole table); render latency/bundle are observed,
  non-gating (matches ui-shell PERF-1).
- **Acceptance**: (a) **structural** — each fetch carries `page`+`size` (no unbounded/all-rows fetch path exists);
  (b) latency/bundle are observed, **no SLO gate** in Phase 1.
- **Tier**: structural (bounding) + observed (latency).

#### NFR-QUEUE-A11Y-1 — semantic + keyboard; recorded target, non-gating (Q6-A)
- **Assertion**: the queue uses a **semantic `<table>`**, keyboard-focusable row-select and pagination controls, and
  accessible labels.
- **Acceptance**: recorded as a target; detailed a11y verification **not gating** in Phase 1 (consistent with the
  lighter/display depth; ui-shell A11Y-1 deferred detailed a11y to the view units — this is that unit).
- **Tier**: observed / soft.

### GOVERNANCE

#### NFR-QUEUE-SCOPE-1 — scoped exclusions *(not a runtime test)*
- **Statement**: the set tests **only** `ui-queue`'s view behavior. It does **not** test other UI units, backend
  internals, or the WIRE-1 **route implementation** (`backend/app/main.py` → Build & Test). It **reuses** ui-shell's
  frozen copy/`FORBIDDEN_TERMS`/ESLint/testid mechanisms **without modifying** them; WIRE-1 R2 is consumed **by shape**,
  mocked in tests. Enforced by review.
- **Tier**: N/A (governance).

---

## 2. Traceability (target → FD rule → tier → rigor)

| Target | FD rule | Tier | Rigor |
|---|---|---|---|
| NFR-QUEUE-COPY-1 | BR-QUEUE-1 | lint | full |
| NFR-QUEUE-PENDING-1 | BR-QUEUE-2 | component | full |
| NFR-QUEUE-ERROR-1 | BR-QUEUE-3 | component + structural | full |
| NFR-QUEUE-RETRY-1 | BR-QUEUE-4 | component + capturing double | full |
| NFR-QUEUE-SELECT-1 | BR-QUEUE-5 | component + structural | full |
| NFR-QUEUE-VIEWONLY-1 | BR-QUEUE-6 | structural + component | full |
| NFR-QUEUE-TESTID-1 | BR-QUEUE-8 | lint / component | full |
| NFR-QUEUE-NOTS-1 | FR-UI-5 (D2) | structural | full |
| NFR-QUEUE-FETCH-1 | async addendum (BR-QUEUE-3/4/9 states) | component | full |
| NFR-QUEUE-NAMESPACE-1 | BR-QUEUE-7 | structural | medium |
| NFR-QUEUE-PAGINATION-1 | BR-QUEUE-9 | component | full |
| NFR-QUEUE-PERF-1 | PER-1 | structural + observed | soft |
| NFR-QUEUE-A11Y-1 | FR-UI (view) | observed | soft |
| NFR-QUEUE-SCOPE-1 | — | N/A | governance |

**No orphaned FD rule**: BR-QUEUE-1..9 each map (BR-QUEUE-1→COPY-1, 2→PENDING-1, 3→ERROR-1(+FETCH-1), 4→RETRY-1(+FETCH-1),
5→SELECT-1, 6→VIEWONLY-1, 7→NAMESPACE-1, 8→TESTID-1, 9→PAGINATION-1(+FETCH-1)).

> **NFR-QUEUE-PAGINATION-1** (BR-QUEUE-9) — RTL over a mocked `page:{page,size,total}` wrapper: page 1 → `queue-pagination-prev`
> disabled; last page (`page*size ≥ total`) → `queue-pagination-next` disabled; `queue-page-indicator` reflects `page` /
> derived total. **Tier**: component (RTL). **Rigor**: full. *(Listed here to complete the map; grouped with FULL RIGOR.)*

---

## 3. Security-Guardrails extension — compliance (enabled extension; expands §5 preview)

`ui-queue` is a **read-only display view** — no secrets, no LLM, no persistence, no write path.

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A (referenced)** | The queue submits nothing; application-input validation is `intake`'s SEC-2. It only **renders** R2 responses. |
| Prompt-injection defense | **N/A** | No LLM / prompt path in `ui-queue`. |
| Secrets management | **N/A** | No secret handled; env/keys are `secrets-config`'s SEC-3. |
| Read-only DB access for audit role | **N/A (referenced)** | The auditor read-only distinction is enforced server-side (`auth-rbac` + `audit-store`, SEC-4). The queue is read-only for **all** roles (VIEWONLY-1). |
| Audit logging | **N/A** | The queue persists nothing (no commit path — that is U7/U8). |
| Error hygiene (no secret/PII leak) | **Compliant** | ERROR-1 surfaces `message` only, `code` via testid, and **never** renders `error.detail` raw — aligned with WIRE-1 §4 ("no secret VALUE in message/detail"). |
| **Least-privilege UI framing (advisory-only + read-only)** | **Compliant** | The queue is view-only with **no `RoleGate`/no act affordance** (VIEWONLY-1) and renders only the **system** `Recommendation`, never a human `CommitAction` (NAMESPACE-1) — advisory-only framing upheld. |

**No blocking finding.**

---

## 4. Settled items held (not re-opened)
- The **frozen FD** (BR-QUEUE-1..9 + inventory + flows) is the substrate — NFR builds testable targets **on** it.
- **ui-shell (frozen)** — its Vitest/RTL/ESLint/`FORBIDDEN_TERMS`/testid mechanisms are **reused**, not modified;
  `RoleContext` stub is the injection point for VIEWONLY-1.
- **WIRE-1** — R2 + ApplicationSummary + envelopes consumed **by shape**, mocked via the injected double; the **route
  implementation** stays deferred to Build & Test (SCOPE-1).
- **Fold-B (Retry position-preserving)** — realized checkably as RETRY-1; state-holding **mechanics** deferred to Code-Gen.
- **Deferred values**: skeleton-row count (Q2-A), default page `size` (N2), aesthetic token values, bundler/deploy
  topology → NFR-Design / Code-Gen / `deploy-config` (P2). Infrastructure Design for `ui-queue` not pre-committed (likely
  a logged SKIP — source-level view; Vercel topology is `deploy-config` P2) — confirmed at that stage.
