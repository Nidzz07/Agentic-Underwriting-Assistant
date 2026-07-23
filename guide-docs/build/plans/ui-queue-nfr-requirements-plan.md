# NFR Requirements — Plan (Part 1) — `ui-queue` (U5)

**Stage**: BUILD → per-unit loop → NFR Requirements **Part 1 (Plan)** · **Unit**: U5 `ui-queue` · C5 · Phase 1
**Depth**: **lighter (display) + async-state addendum** (consistent with the FD depth decision) · **Date**: 2026-07-09
**Story**: US-UI-1 · **Requirements**: FR-UI-1 / FR-UI-3 / FR-UI-5 / PER-1.
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md` — **BR-QUEUE-1..9**, the
component/prop inventory, the four-state render enum, the `data-testid` inventory, the pagination/selection flows) —
**re-opening none of it**. Each draft `NFR-QUEUE-*` target is a **pass/fail testable assertion** traced to its FD rule.

> **Part 1 (Plan) only.** This file lists the **draft** target map + open [Answer] questions and the Part 2 artifacts to
> generate **after** approval. **No NFR artifact (`nfr-requirements.md` / `tech-stack-decisions.md`) is generated here.**

---

## 0. Prerequisites & grounding (read, not re-derived)

- [x] FD complete for `ui-queue` (three artifacts, gate approved 2026-07-09; Mermaid convention-corrected).
- [x] **Tier convention inherited from `ui-shell` (frozen, U10) tech-stack — grounded, not invented**:
  - **D1/D2** React + Tailwind, **no TypeScript** (plain JS/JSX).
  - **D3** test tier = **Vitest + React Testing Library + jsdom**; component targets drive RTL renders; **no live backend**.
  - **D4** **ESLint over the single `FORBIDDEN_TERMS` source** backs build-failing lints; each lint ships a **detector
    self-test** (non-vacuous — can never pass vacuously).
  - **D5** **file/import scan in CI** for structural targets (no-TS, no-backend-import).
- [x] **The one genuinely-new concern vs `ui-shell`**: `ui-shell` **fetched nothing real** (its `NFR-UI-REFNOTOWN-1`
  asserted no real fetch). `ui-queue` is the **first UI unit that actually fetches** — WIRE-1 **R2**
  (`GET /applications?page=&size=`), **mocked in tests via a capturing/injected fetch double** (no live backend). So the
  NFR set adds a **fetch-double + four-state-machine** target the shell never needed (§2, NFR-QUEUE-FETCH-1).

---

## 1. Draft `NFR-QUEUE-*` target map (BR-QUEUE-1..9 → pass/fail target · tier · rigor)

Every FD rule maps to a target (no orphan). Tiers use the inherited convention (unit = Vitest; component = RTL+jsdom;
structural = file/import scan or ESLint). Targets marked *(Q#)* have an **open tier/scope question in §3**.

| # | Target | FD rule | Draft pass/fail assertion | Tier | Rigor |
|---|---|---|---|---|---|
| T1 | **NFR-QUEUE-COPY-1** | BR-QUEUE-1 | No Recommendation/Confidence **label literal** anywhere in `frontend/src/queue/`; every label imported from `shell/copy`; badges render by **value look-up**. **Reuses ui-shell's ESLint/`FORBIDDEN_TERMS` mechanism** (D4) + detector self-test. | structural / lint | full |
| T2 | **NFR-QUEUE-PENDING-1** | BR-QUEUE-2 | RTL: a row with `recommendation`/`confidence` = `null` renders `queue-row-pending-<id>` and **no** `RecommendationBadge`/`ConfidenceBadge`; the row is **present** (not filtered). | component (RTL) | full |
| T3 | **NFR-QUEUE-ERROR-1** | BR-QUEUE-3 | RTL + mocked error body `{error:{code,message,detail}}`: `queue-error-message` shows **`message`**; `queue-error-code` carries **`code`** (not visible text); **`detail` never appears in the DOM**. | component (RTL) + structural | full |
| T4 | **NFR-QUEUE-RETRY-1** | BR-QUEUE-4 | **Capturing** fetch-double fails page **N**; activating Retry issues a re-fetch whose **captured request targets page N** — **with teeth**: the test **fails if Retry reset to page 1**. | component (RTL) + capturing double *(Q1)* | full |
| T5 | **NFR-QUEUE-SELECT-1** | BR-QUEUE-5 | RTL: activating a row's select affordance calls **`onSelect(application_id)`** with the right id; **no navigation occurs** (mechanism *(Q4)*). | component + structural *(Q4)* | full |
| T6 | **NFR-QUEUE-VIEWONLY-1** | BR-QUEUE-6 | Structural: **no `RoleGate` import** in `queue/`. RTL: render is **identical** with a stub `RoleContext.Provider` set to `underwriter` / `auditor` / `admin`. | structural + component | full |
| T7 | **NFR-QUEUE-NAMESPACE-1** | BR-QUEUE-7 | Structural: only **system** `Recommendation` values render (incl. `DECLINE-RECOMMEND`, never bare `DECLINE`); **no** lowercase human `approve`/`override` string rendered — reuses the `FORBIDDEN_TERMS` collision guard. | structural | medium |
| T8 | **NFR-QUEUE-TESTID-1** | BR-QUEUE-8 | A lint/test asserts the **`queue-<element>-<purpose>`** convention across queue elements (`domain-entities.md §5`); **detector self-test** — a missing/misnamed testid is flagged (non-vacuous). | lint / component | full |
| T9 | **NFR-QUEUE-PAGINATION-1** | BR-QUEUE-9 | RTL over a mocked `page:{page,size,total}` wrapper: **page 1 → `queue-pagination-prev` disabled**; **last page (`page*size≥total`) → `queue-pagination-next` disabled**; `queue-page-indicator` reflects `page` / derived total. | component (RTL) | full |

### Cross-cutting / addendum targets

| # | Target | Source | Draft assertion | Tier | Rigor |
|---|---|---|---|---|---|
| T10 | **NFR-QUEUE-NOTS-1** | FR-UI-5 / D2 | File-scan: **zero `.ts`/`.tsx`** under `frontend/src/queue/`; no TS config. (Inherited from ui-shell NOTS-1.) | structural | full |
| T11 | **NFR-QUEUE-FETCH-1** | async-state addendum | R2 fetched via an **injected/capturing fetch double** *(Q1)*; each of the **four render states** (`loading`/`ready`/`empty`/`error`) has a render assertion; **state-transition coverage** *(Q3)*. | component (RTL) | full |
| T12 | **NFR-QUEUE-PERF-1** | PER-1 | Queue payload is **bounded by pagination** (never fetches the whole table). Whether this is a **gating SLO** or an **observed/soft** budget → *(Q5)*. | *(Q5)* | *(Q5)* |
| T13 | **NFR-QUEUE-A11Y-1** | FR-UI (view unit) | Semantic table markup + keyboard-focusable row-select & pagination controls with accessible labels. Gating vs soft → *(Q6)*. (ui-shell A11Y-1 explicitly **deferred detailed a11y to the view units** — this is that unit.) | *(Q6)* | *(Q6)* |

**No orphaned FD rule**: BR-QUEUE-1..9 → T1..T9; T10–T13 cover the inherited/addendum concerns.

---

## 2. The fetch-double + four-state machine (the addendum, made testable)

`ui-queue` is the first UI unit to exercise a real fetch (R2), **mocked** in tests. The NFR set must pin how R2 is
doubled and how the `loading → ready | empty | error` (+ `error --retry--> loading`, `ready --page--> loading`) machine is
covered — **without a live backend** (per the inherited convention). The construction of the double (Q1), the loading-
state assertions (Q2), and whether a **dedicated transition test** is required beyond per-state renders (Q3) are the three
open decisions §3 asks. RETRY-1 (T4) and PAGINATION-1 (T9) already cover two transitions; Q3 decides the rest.

---

## 3. Open NFR-tier questions ([Answer] tags — lettered per the standing convention)

> To be answered at this gate; the **full Q&A is embedded into this file once answered**, before Part 2.

### Q1 — R2 fetch-double construction
- **A.** **Injected/capturing fetch double** — `QueueView` receives its fetch function via prop/context; tests pass a
  capturing double that records the requested page; production wires the real fetch at the composition root. *(Recommended
  — makes T4's "captured request targeted page N" assertion clean and is exactly a capturing/injected double.)*
- **B.** **Global `fetch` mock** (e.g. `vi.stubGlobal` / an MSW-style URL interceptor) — more realistic, but capturing the
  exact requested page for T4 is indirect.
- **C.** **Module-level fetch client** mocked via `vi.mock` — a mocked client module.

`[Answer]:` **A** — injected/capturing fetch double; `QueueView` receives its fetch function via prop/context; tests pass
a capturing double that records the requested page; production wires the real fetch at the composition root.

### Q2 — Loading-state (`queue-state-loading`) assertions
- **A.** Assert **`queue-state-loading` present** during the in-flight fetch **AND no table/rows render** while loading;
  the **skeleton-row count is a visual value deferred** to Code-Gen (like token values). *(Recommended.)*
- **B.** Assert **only** `queue-state-loading` container presence (nothing about the table).
- **C.** Assert loading present **and a specific skeleton-row count** (pins the count now).

`[Answer]:` **A** — assert `queue-state-loading` present during the in-flight fetch AND no table/rows render while
loading; the skeleton-row count is a visual value deferred to Code-Gen, like token values.

### Q3 — Dedicated state-transition test beyond per-state renders?
- **A.** **Yes** — one consolidated transition test exercising `loading→ready`, `loading→empty`, `loading→error`,
  `error--retry-->loading`, `ready--page-->loading`, in addition to the per-state render tests (T2/T3/T11) and
  T4/T9. Gives the state machine explicit teeth. *(Recommended — cheap in RTL.)*
- **B.** **No** — the per-state render tests + T4 (retry) + T9 (pagination) already cover every transition; no separate
  machine test.

`[Answer]:` **A** — yes, one consolidated state-transition test exercising `loading→ready`, `loading→empty`,
`loading→error`, `error--retry-->loading`, `ready--page-->loading`, in addition to the per-state render tests and T4/T9.
Gives the state machine explicit teeth.

### Q4 — NFR-QUEUE-SELECT-1 "no navigation" assertion mechanism (no router exists in ui-queue yet, Q5-A deferred)
- **A.** **Structural** — a static scan asserts `queue/` **imports no router/navigation module**, plus an RTL assertion
  that `onSelect` is the only outward call on select. *(Recommended — there is no router to spy on; matches BR-QUEUE-5.)*
- **B.** **Injected navigation spy seam** — pass a navigation callback spy and assert it is **never** called.

`[Answer]:` **A** — structural: a static scan asserts `queue/` imports no router/navigation module, plus an RTL
assertion that `onSelect` is the only outward call on select.

### Q5 — PER-1 treatment for the queue
- **A.** **Observed / soft, bounded-by-pagination** — assert structurally that the queue **only ever fetches one page**
  (never the whole table); render latency/bundle are **observed, non-gating** (matches ui-shell PERF-1). *(Recommended.)*
- **B.** **Gating SLO** — set a concrete numeric budget (e.g. a max render time / max page size) enforced as a test.

`[Answer]:` **A** — observed/soft, bounded-by-pagination; assert structurally that the queue only ever fetches one page;
render latency/bundle observed, non-gating, matching ui-shell's PERF-1 precedent.

### Q6 — A11Y rigor for the queue (ui-shell deferred detailed a11y to the view units — this is one)
- **A.** **Soft/observed** — semantic `<table>` + keyboard-focusable controls + accessible labels as a **recorded target**,
  detailed a11y verification not gating in Phase 1. *(Recommended, consistent with the lighter/display depth.)*
- **B.** **Gating** — a concrete a11y assertion set (roles, keyboard nav, name/label) enforced as tests now.

`[Answer]:` **A** — soft/observed; semantic `<table>` + keyboard-focusable controls + accessible labels as a recorded
target, not gating in Phase 1, consistent with the lighter/display depth.

---

## 4. NFR Requirements **Part 2** plan — artifacts to generate **after** approval (checkboxes, not started)

- [x] **`guide-docs/build/ui-queue/nfr-requirements/nfr-requirements.md`** — the finalized `NFR-QUEUE-*` targets (T1–T13
  resolved with the Q1–Q6 answers folded in), each a pass/fail assertion with acceptance criteria + test tier + rigor; a
  **traceability table** (target → FD rule → tier → rigor, no orphan); and the **Security-Guardrails extension compliance
  table** (see §5 preview).
- [x] **`guide-docs/build/ui-queue/nfr-requirements/tech-stack-decisions.md`** — the queue's tech decisions, **inheriting**
  ui-shell's substrate (React/Tailwind/no-TS/Vitest/RTL/jsdom/ESLint) and adding **only** what's new: the **R2 fetch-double
  construction** (Q1), any state-management note (deferred mechanics per Fold-B), and deferred items (page-`size` value,
  bundler/deploy topology → `deploy-config` P2).

## 5. Security-Guardrails extension — applicability preview (full table lands in Part 2)

`ui-queue` is a **read-only display view** (no secrets, no LLM, no write path). Preview: **Input validation** N/A
(referenced — intake's SEC-2); **Prompt-injection** N/A (no LLM); **Secrets** N/A (none handled); **Audit logging** N/A
(persists nothing); **Read-only auditor distinction** N/A-referenced (surfaced cosmetically; enforced server-side, SEC-4);
**Least-privilege UI framing** **Compliant** — the queue is view-only with **no `RoleGate`/no act affordance**
(BR-QUEUE-6) and never renders a human `CommitAction` (BR-QUEUE-7). No blocking finding anticipated.

## 6. Holds / guardrails (this Part 1)

- [x] **No NFR artifact generated** — only this plan file written.
- [x] **Frozen FD not re-opened** — targets built **on** BR-QUEUE-1..9 / the inventory / the flows.
- [x] **WIRE-1 untouched** (R2 consumed by shape, mocked in tests); **`ui-shell` (frozen) untouched** (tier convention +
  `FORBIDDEN_TERMS`/ESLint mechanism **reused**, not modified).
- [x] **No application code** and **no test code** written (design/targets only).
- [x] **tier-B corpus run NOT authorized**; **no other unit started**; `audit_store` Docker-guard gap still deferred.
