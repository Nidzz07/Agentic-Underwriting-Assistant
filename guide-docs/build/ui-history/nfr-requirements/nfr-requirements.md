# NFR Requirements — `ui-history` (U9)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U9 `ui-history` · C5 · Phase 1 · **Depth**: lighter (display) + INV-FAITHFUL + INV-NAMESPACE via StructuralGuard + focused teeth · **Date**: 2026-07-14 · Story **US-UI-6** · FR-UI-1 / CON-AUDIT-1 (read surface) / FR-UI-3 / FR-UI-5.
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md` / `frontend-components.md` — **BR-HIST-1..11**, the component/prop inventory, the `HISTORY_STATE` master-detail machine with position-preserving Back, the namespace-distinct detail composition, the `history-<element>-<purpose>` testid inventory incl. the two region-level testids) — **re-opening none of it**. Each `NFR-HIST-*` target is a **pass/fail testable assertion** traced to its FD rule. **Tier convention inherited from `ui-shell` (frozen U10) and applied by the frozen sibling UI units (U5–U8)**: Vitest + React Testing Library + jsdom · ESLint over the single `FORBIDDEN_TERMS` · file/import scan · detector self-tests. **Advisory-only; no LLM; no live backend** (WIRE-1 R6/R7 mocked via a single injected/capturing **dual-read** double). Q1–Q3 all **A**.

---

## 0. Central testability principle

`ui-history`'s properties are testable **without a running backend** — R6 (list) and R7 (detail-by-id) are exercised through a **single injected/capturing dual-read double** (Q1-A — the FD's local `historyFetchSeam`, passed to `HistoryView` as a prop; production wires the real transport at the composition root) — four ways:
1. **Build-failing lints + structural scans** — COPY-1 / ADVISORY-1 / TESTID-1 reuse `ui-shell`'s ESLint + the **one** `FORBIDDEN_TERMS` source (not a second word-list); NOTS-1 / VIEWONLY-1 / FAITHFUL-1 (no-write-seam) / NOSUPERSEDE-1 are file/import/AST scans. Each lint/scan carries a **detector self-test** so it can never pass vacuously.
2. **Component-render assertions (RTL + jsdom)** — SEPARATION-1 (load-bearing), REASON-1, EMPTY-1, ERROR-1, RULERESULTS-1, VIEWONLY-1(render), and the per-state renders + consolidated transition of STATEMACHINE-1, using a stub `RoleContext.Provider` where role is relevant.
3. **Capturing dual-read-double assertions** — DUALREAD-1 (read-attribution: select→`fetchDetail` only, page→`fetchList` only), ERROR-1's Retry legs (listError→last page, detailError→same `decision_id`), and BACKPRESERVE-1 (Back adds **zero** new `fetchList` calls; `page`/`items` identical) assert on the **recorded args + call-counts** of the injected double.
4. **Observed/soft** — PERF-1 (bounded reads, non-gating) and A11Y-1 (semantic regions + keyboard, recorded target).

**NFR-HIST-Fold-A (single dual-read double, inherited from ui-queue Fold-1 / ui-memo-view Fold-A, adapted for two READS)**: there is **one** double construction — the injected `historyFetchSeam` of Q1-A, exposing **`{ fetchList, fetchDetail }`** as two **independently-capturing** spies (`fetchList.calls[i]=[page,size]`, `fetchDetail.calls[i]=[decision_id]`), each programmable/sequenceable. Every state/transition test **programs that same double**. Because both operations are **reads**, there is **no "zero write calls before Confirm" gate** (contrast U7/U8's asymmetric read+write double); the load-bearing count teeth become **read-attribution** (DUALREAD-1), **retry-targeting** (ERROR-1), and **Back-triggers-zero-new-list-fetches** (BACKPRESERVE-1). A **fresh double instance per test** (the `ui-approval-gate` CG-Fold-1 pattern) + RTL auto-cleanup isolates counts, so a **simple before/after snapshot** of `fetchList.calls.length` around the Back action is sufficient for BACKPRESERVE-1 — **no before/after-mount discrimination is built into the double** (NFR-HIST-Fold-2).

**NFR-HIST-Fold-B (DOM-containment in jsdom, the load-bearing SEPARATION-1)**: the SEPARATION-1 teeth use `Node.contains()` (jsdom-supported for **arbitrary-depth** descendants, `false` for a sibling subtree) + scoped `within()` queries — so the **sibling non-containment** assertion between `history-detail-system-region` and `history-detail-human-region` is sound, not just parent-child. Mirrors `ui-memo-view` SEPARATION-1 exactly, applied to the two namespace regions. No bespoke DOM walking.

**NFR-HIST-Fold-C (rule_results disclosure: mounted-but-hidden + DOM-level query, Q3-A / NFR-HIST-Fold-1)**: the `rule_results` progressive disclosure collapses via the HTML **`hidden` attribute / `display:none`** — which **removes collapsed entries from the accessibility tree** (so a screen reader does not announce them; **no separate `aria-hidden` needed**) while keeping **every entry mounted in the DOM** (INV-FAITHFUL). RULERESULTS-1's "all N present" assertion therefore uses a **DOM-level query** (`getAllByTestId(...)` / `container.querySelectorAll(...)`) that finds mounted-but-hidden nodes — **not** a visibility-filtering `getByRole`/`getByText` query (which would miss collapsed entries and false-fail). The toggle is keyboard-focusable (A11Y-1).

**NFR-HIST-Fold-D (advisory-vocabulary verified against the REAL detector, Q2-A / NFR-HIST-Fold-3)**: representative history-local draft strings were run through the **actual** `eslint-rules/index.js` `findForbiddenSystemOutput`. The detector is a **word-boundary** matcher (`/\bdecision\b/i`, suffix-aware `/decline(?!-?recommend)/i`, `/\bapproved\b/i`), **not a substring scan** — so **plural "decisions" and compound "decision_id" pass**, and only the **standalone singular word "decision"** (plus bare `decline`/`declined`/`approved`) is forbidden. Verified: `System recommendation` / `Underwriter's committed action` / `Committed outcome` / `No decisions yet` / `History` / all forensic labels → **clean**; the literal `Underwriter's decision` / `Decision history` / `approved` / `declined` → **correctly FLAGGED**. Q2-A's token-avoiding wording is thus **non-vacuously satisfiable with the frozen lint reused unmodified**. Binding rule for Code-Gen: static copy may use **plural "decisions"** freely but must **avoid the standalone singular "decision"** (title "History"/"Decisions", human region "Underwriter's committed action").

**Scope**: the `NFR-HIST-*` set tests **only** `ui-history`'s own view behavior; it does **not** test other UI units, any backend unit's internals, or the WIRE-1 route implementation (R6/R7 impl → Build & Test). It **reuses** ui-shell's frozen mechanisms (copy / `FORBIDDEN_TERMS` / ESLint / `ReadOnlyRegion` / badges / testid convention) and **mirrors** the sibling fetchSeam/StructuralGuard/testid-lint convention **without modifying or importing** any of them.

---

## 1. Finalized `NFR-HIST-*` targets (pass/fail; acceptance criteria; test tier)

### FULL RIGOR

#### NFR-HIST-COPY-1 — single-source copy; no inlined display label (BR-HIST-1)
- **Assertion**: no `Recommendation`/`Confidence`/`CommitAction` **label literal** appears anywhere in `frontend/src/history/`; every enum label is looked up from `shell/copy` **by value** (badges + value lookups); history-specific chrome + forensic field labels live in the **history-local `copy.js`**.
- **Acceptance**: (a) a **build-failing ESLint rule** (the ui-shell `no-inline-label` mechanism, D4) flags any label literal outside `shell/copy`; (b) a system region given `recommendation="DECLINE-RECOMMEND"` renders the label sourced from `RECOMMENDATION_LABELS` (never a bare `DECLINE`); the human region renders `action` from `COMMIT_ACTION_LABELS`; (c) **detector self-test** — a synthetic inlined label is flagged.
- **Tier**: structural / lint. **Rigor**: full.

#### NFR-HIST-SEPARATION-1 — namespace-distinct DOM separation, with teeth (BR-HIST-2) — **the load-bearing target**
- **Assertion**: on a `detail` render, the **system** region (`history-detail-system-region`) and the **human** region (`history-detail-human-region`) are **distinct, non-nested DOM nodes**; the system `recommendation`/`confidence` render **exclusively** in the system region; the human `action`/`reason` render **exclusively** in the human region. The structural expression of advisory namespace-distinctness (system vs human "committed action").
- **Acceptance** (Q-flagged — **direct DOM-tree containment, real teeth; NFR-HIST-Fold-B**): obtain both region nodes; assert (a) **`!system.contains(human)` AND `!human.contains(system)`** (neither ancestor/descendant of the other); (b) **`within(system).getByTestId('history-detail-recommendation')`** and **`history-detail-confidence`** are present, and **`within(human).queryByTestId('history-detail-recommendation')` is `null`**; (c) **`within(human).getByTestId('history-detail-action')`** is present, and **`within(system).queryByTestId('history-detail-action')` is `null`**; (d) the system region composes the frozen `ReadOnlyRegion` (`aria-readonly`) with an engine-attributed heading. **Teeth**: the test **fails** if either namespace were rendered in the other region.
- **Tier**: component (RTL + jsdom). **Rigor**: **full (highest)**.

#### NFR-HIST-FAITHFUL-1 — INV-FAITHFUL: zero write-capable call sites (BR-HIST-3) — **the load-bearing structural guarantee**
- **Assertion**: nothing under `frontend/src/history/` can mutate/commit/submit the record — no `submit*` / `buildCommitRequest`-analog, no write transport, no mutation seam, no edit affordance; `historyFetchSeam` exposes **only** `fetchList` / `fetchDetail` (+ `buildHistoryListRequest` / `buildHistoryDetailRequest` / `normalizeError`) and **no** request-body builder.
- **Acceptance**: (a) a **`noWriteSeam` structural/AST scan** (the write-path units' single-call-site guard **inverted to ZERO call sites**) finds **no** `submit`-prefixed function, no `buildCommitRequest`/`buildOverrideRequest`-analog, and no request with a body/method other than `GET` anywhere in the tree; (b) `historyFetchSeam`'s exported surface is exactly `{ fetchList, fetchDetail }` (+ the two builders + `normalizeError`) — asserted structurally; (c) **detector self-test** — a synthetic `submitOverride(`-style call (or a non-GET request builder) is **flagged** (non-vacuous).
- **Tier**: structural / AST. **Rigor**: **full (highest)**.

#### NFR-HIST-DUALREAD-1 — master-detail: read-attribution across the dual-read double (BR-HIST-4)
- **Assertion**: `HistoryView` owns both reads through **one** injected `historyFetchSeam`; a row select issues exactly one `fetchDetail(decision_id)` and **no** `fetchList`; a page change issues exactly one `fetchList(page,size)` and **no** `fetchDetail`; `HistoryView` is the **only** stateful history component.
- **Acceptance** (Q1-A / NFR-HIST-Fold-A): (a) with the dual-read double, **selecting** a `history-row-<decision_id>` records **one** `fetchDetail` call whose arg == that `decision_id` and **zero** new `fetchList` calls; (b) a **page change** records **one** `fetchList` call whose arg == the target page and **zero** `fetchDetail` calls; (c) **structural** — no sibling-unit import and no router import under `frontend/src/history/`; a single stateful component. **Teeth**: fails if a select triggered a list fetch, or a page change triggered a detail fetch.
- **Tier**: component (RTL) + capturing double + structural. **Rigor**: full.

#### NFR-HIST-RULERESULTS-1 — faithful `rule_results` rendering; no entry dropped (BR-HIST-5)
- **Assertion**: the detail renders **every** `audit_tuple.rule_results.rule_results[]` entry, in the delivered order, with **none dropped or truncated**, regardless of the disclosure (collapsed/expanded) state.
- **Acceptance** (Q3-A / NFR-HIST-Fold-C): (a) render a `detail` whose report has **N deliberately-unsorted** entries; a **DOM-level query** (`getAllByTestId('history-detail-ruleresult-*')` / `container.querySelectorAll`) finds **all N** (count == input length) in the **input order** (no client re-sort) — **teeth**: a non-sorted input renders in the same non-sorted order and all N are present; (b) the assertion holds **in both collapsed and expanded states** because collapse is **`hidden`/`display:none`, never unmount** (entries stay in the DOM); (c) both a large-N and a length-1 fixture pass. The disclosure `history-detail-ruleresults-toggle` is keyboard-focusable.
- **Tier**: component (RTL + jsdom). **Rigor**: full.

#### NFR-HIST-REASON-1 — conditional reason display; human namespace (BR-HIST-6)
- **Assertion**: the human region renders `reason` **iff** `committed_decision.action === 'override'` (present/non-blank), and **not** on `approve`; `action` via `COMMIT_ACTION_LABELS`; `underwriter_id` rendered.
- **Acceptance**: (a) an **`override`** record renders `history-detail-reason` (== `committed_decision.reason`) **within** `history-detail-human-region`; (b) an **`approve`** record renders **no** `history-detail-reason` node; (c) `history-detail-action` == `COMMIT_ACTION_LABELS[action]`, `history-detail-underwriter` == `underwriter_id`. **Teeth**: fails if reason appeared on approve or was absent on override.
- **Tier**: component (RTL). **Rigor**: full.

#### NFR-HIST-VIEWONLY-1 — view-only; no `RoleGate`, no router (BR-HIST-7)
- **Assertion**: `ui-history` renders no `RoleGate`, imports no router/navigation module, and renders **identically** across roles; R6/R7 are authenticated any-role.
- **Acceptance**: (a) **structural** — no `RoleGate` import/usage and no router import in `frontend/src/history/` (a `noRoleGateImport` scan mirroring ui-queue's) + detector self-test; (b) RTL — the rendered output is **identical** with a stub `RoleContext.Provider` set to `underwriter`, `auditor`, `admin`, and `null`. Confirms `can="read"` is **not** used (admin is not cosmetically excluded).
- **Tier**: structural + component. **Rigor**: full.

#### NFR-HIST-EMPTY-1 — empty state derived from `items.length` (BR-HIST-8)
- **Assertion**: an R6 body with `items: []` → a single page-level "no decisions yet" state; a non-empty body → the list; derivation keys on **`items.length`** (contrast `ui-memo-view`'s `status` discriminator).
- **Acceptance**: (a) `items: []` renders `history-state-empty` and **none** of `history-list` / `history-pagination`; (b) a non-empty body renders `history-list`; (c) the state selection reads **`items.length`** (an explicit anti-regression note vs the memo `status` pattern). **Teeth**: fails if a non-empty list rendered empty, or vice-versa.
- **Tier**: component (RTL). **Rigor**: full.

#### NFR-HIST-ERROR-1 — error `message`-only / `code` via testid / `detail` never raw; position/id-preserving Retry; generic 404 (BR-HIST-9)
- **Assertion**: on an R6 **or** R7 failure, the visible text is `error.message` only; `error.code` via testid only; `error.detail` never in the DOM. A `listError` Retry re-fetches the **last-requested page**; a `detailError` Retry re-fetches the **same `decision_id`**; the R7 **404 `not_found`** is surfaced through the **generic** `detailError` path.
- **Acceptance** (capturing double): (a) `history-error-message` renders `message`; (b) `history-error-code` carries `code` and it is **not** visible UI text; (c) a DOM scan finds `detail`'s content **nowhere**; (d) **listError Retry teeth** — fail the double at page *k*; Retry issues `fetchList` whose recorded arg == page *k* (not page 1); (e) **detailError Retry teeth** — fail the double for `decision_id = X`; Retry issues `fetchDetail` whose recorded arg == `X`; (f) **generic-404 teeth** — an R7 response with `error.code === 'not_found'` renders `history-state-error-detail` via the **same** generic path (asserts **no** dedicated not-found branch/message distinct from other detail errors).
- **Tier**: component (RTL) + capturing double. **Rigor**: full.

#### NFR-HIST-TESTID-1 — `data-testid` convention incl. rows + the two region testids (BR-HIST-10)
- **Assertion**: every assertion-relevant element carries a stable `history-<element>-<purpose>` testid (`domain-entities.md §6`), **including every row** (`history-row-<decision_id>`) and the **two region-level testids** (`history-detail-system-region` / `history-detail-human-region`) + per-field detail ids + state ids.
- **Acceptance**: (a) a `history-testid-convention` lint (mirroring `queue-testid-convention`; regex = queue-family `^history-[a-z]+(-[a-z0-9]+)+$`, pinned in `tech-stack-decisions.md`) asserts the convention; (b) **every list row** carries `history-row-<decision_id>`; (c) the **two region testids** are present and **distinct**; (d) **detector self-test** — a missing/misnamed testid is flagged (non-vacuous).
- **Tier**: lint / component. **Rigor**: full.

#### NFR-HIST-NOSUPERSEDE-1 — no premature superseded/versioning handling (BR-HIST-11)
- **Assertion**: `status` and `supersedes_decision_id` are **display-only**; there is **no** conditional branch keyed on `status === 'superseded'`, **no** dereference/link of `supersedes_decision_id`, and **no** supersede/version affordance.
- **Acceptance**: (a) a **structural/AST scan** finds **no** branch/comparison against `'superseded'` and **no** read of `supersedes_decision_id` beyond a plain display render, and **no** version/supersede control under `frontend/src/history/`; (b) `history-detail-status` renders the `status` value read-only; (c) **detector self-test** — a synthetic `status === 'superseded'` branch (or a `supersedes_decision_id` dereference) is **flagged** (non-vacuous).
- **Tier**: structural / governance. **Rigor**: full.

#### NFR-HIST-NOTS-1 — no TypeScript (FR-UI-5 / D2)
- **Assertion**: `frontend/src/history/` is plain JS/JSX — no `.ts`/`.tsx`, no TS config.
- **Acceptance**: a file-scan finds **zero** `.ts`/`.tsx` under the history tree and no `tsconfig*.json`; CI fails otherwise.
- **Tier**: structural. **Rigor**: full.

#### NFR-HIST-STATEMACHINE-1 — master-detail machine: per-state renders + one consolidated transition (master-detail addendum)
- **Assertion**: R6/R7 are fetched through the injected dual-read double; each of the seven `HISTORY_STATE` values renders correctly; the machine's transitions are covered by **one consolidated transition test**.
- **Acceptance** (Q1-A / NFR-HIST-Fold-A): (a) `HistoryView` receives its `fetchSeam` via **prop** and never imports a hard-wired fetch; (b) **per-state renders** — `listLoading` / `list` / `listEmpty` / `listError` / `detailLoading` / `detail` / `detailError` each render their pinned testid and no foreign content; (c) **one consolidated transition test** exercises `listLoading→list`/`listEmpty`/`listError`, `list→detailLoading→detail`/`detailError`, `detailError→detailLoading` (Retry), and `detail→list` (Back), all on the **same** double.
- **Tier**: component (RTL). **Rigor**: full.

#### NFR-HIST-BACKPRESERVE-1 — position-preserving Back: zero refetch, byte-identical page/items (HIST-Fold-1)
- **Assertion**: returning from `detail` to `list` preserves the list's page position and rows and issues **no** new list fetch.
- **Acceptance** (NFR-HIST-Fold-2): from `list` at page *k*, open a row → `detail`, then activate **Back**; assert (a) `fetchList.calls.length` is **unchanged** by Back (a **before/after snapshot** around the Back action — zero refetch); (b) the rendered list `page` == *k* and `items` are the **same rows in the same order** as before the detail excursion. **Teeth**: fails if Back reset to page 1 or triggered a refetch.
- **Tier**: component (RTL) + capturing double. **Rigor**: full.

### FULL RIGOR — advisory / lint

#### NFR-HIST-ADVISORY-1 — reuse the ONE `FORBIDDEN_TERMS`, unmodified & blanket; token-avoiding human-region wording (BR-HIST-2 / HIST-Fold-4)
- **Assertion**: the shell `no-inline-label` + `advisory-vocabulary` lints are registered on `src/history/**` (a new `eslint.config.js` block mirroring the sibling blocks — **no `src/shell` edit, no new word-list, no new lint mechanism**); the view's static copy contains **no** `FORBIDDEN_TERMS.systemOutput` token (`DECLINE`/`decision`/`approved`/`declined`) and no bare `DECLINE`. The **human-committed region uses namespace-distinct wording that avoids the standalone singular "decision"** ("Underwriter's committed action" / "Committed outcome"), so the reused blanket lint stays green (Q2-A).
- **Acceptance** (Q2-A / NFR-HIST-Fold-D — **verified against the real detector**): (a) the reused lints pass over `src/history/` static code; (b) **no** new word-list exists under `src/history/`; (c) **detector self-test** — a synthetic forbidden term (e.g. a heading "Underwriter's decision") **fails** the lint; (d) representative draft strings were audited against the **actual** `findForbiddenSystemOutput` (word-boundary matcher) — the token-avoiding wording + forensic labels are **clean**, the literal "Underwriter's decision"/"Decision history" are **flagged** (§0 Fold-D table). The full `copy.js` is authored + lint-verified at Code-Gen.
- **Tier**: structural / lint. **Rigor**: full.

### SOFT / OBSERVED

#### NFR-HIST-PERF-1 — bounded reads; observed, non-gating (PER precedent)
- **Assertion**: R6 fetches a **single bounded page** (`buildHistoryListRequest(page,size)` — no all-rows path); R7 fetches a **single record by id** (**no N+1 per-row enrichment** — the Q4-A guarantee, the reason the list omits the system recommendation); render latency/bundle observed, non-gating (matches ui-shell/sibling PERF).
- **Acceptance**: (a) **structural** — the fetch paths target exactly one bounded page (R6) and one record (R7); no unbounded/list-of-details or per-row R7 fetch path exists; (b) latency/bundle observed, **no SLO gate** in Phase 1.
- **Tier**: structural (bounding) + observed (latency). **Rigor**: soft.

#### NFR-HIST-A11Y-1 — semantic regions + keyboard; recorded target, non-gating (view a11y)
- **Assertion**: `ui-history` uses **semantic region markup + headings**, keyboard-focusable **row / pagination / Back / Retry / rule-results-toggle** controls, accessible labels, and the read-only system region's `aria-readonly` (frozen `ReadOnlyRegion`). Collapsed `rule_results` entries are removed from the a11y tree via `hidden`/`display:none` (NFR-HIST-Fold-C).
- **Acceptance**: recorded as a target; detailed a11y verification **not gating** in Phase 1 (consistent with the lighter/display depth; ui-shell deferred detailed a11y to the view units — this is that unit).
- **Tier**: observed / soft. **Rigor**: soft.

### GOVERNANCE

#### NFR-HIST-SCOPE-1 — scoped exclusions *(not a runtime test)*
- **Statement**: the set tests **only** `ui-history`'s view behavior. It does **not** test other UI units, backend internals, or the WIRE-1 **route implementation** (`backend/app/main.py` R6/R7 → Build & Test). It **reuses** ui-shell's frozen copy/`FORBIDDEN_TERMS`/ESLint/`ReadOnlyRegion`/badges/testid mechanisms and **mirrors** the sibling fetchSeam/StructuralGuard/testid-lint convention **without modifying or importing** any of them; WIRE-1 R6/R7 + `audit_store` shapes are consumed **by shape**, mocked in tests. **No write path is introduced** (INV-FAITHFUL, FAITHFUL-1). Enforced by review.
- **Tier**: N/A (governance).

---

## 2. Traceability (target → FD rule → tier → rigor)

| Target | FD rule | Tier | Rigor |
|---|---|---|---|
| NFR-HIST-COPY-1 | BR-HIST-1 | lint | full |
| NFR-HIST-SEPARATION-1 | BR-HIST-2 (namespace-distinct DOM) | component | **full (highest)** |
| NFR-HIST-ADVISORY-1 | BR-HIST-2 (advisory vocab / HIST-Fold-4) | lint | full |
| NFR-HIST-FAITHFUL-1 | BR-HIST-3 (INV-FAITHFUL) | structural / AST | **full (highest)** |
| NFR-HIST-DUALREAD-1 | BR-HIST-4 | component + capturing double + structural | full |
| NFR-HIST-RULERESULTS-1 | BR-HIST-5 | component | full |
| NFR-HIST-REASON-1 | BR-HIST-6 | component | full |
| NFR-HIST-VIEWONLY-1 | BR-HIST-7 | structural + component | full |
| NFR-HIST-EMPTY-1 | BR-HIST-8 | component | full |
| NFR-HIST-ERROR-1 | BR-HIST-9 | component + capturing double | full |
| NFR-HIST-TESTID-1 | BR-HIST-10 | lint / component | full |
| NFR-HIST-NOSUPERSEDE-1 | BR-HIST-11 | structural / governance | full |
| NFR-HIST-NOTS-1 | FR-UI-5 (D2) | structural | full |
| NFR-HIST-STATEMACHINE-1 | master-detail addendum (states) | component | full |
| NFR-HIST-BACKPRESERVE-1 | HIST-Fold-1 | component + capturing double | full |
| NFR-HIST-PERF-1 | view perf (PER precedent) | structural + observed | soft |
| NFR-HIST-A11Y-1 | FR-UI (view unit) | observed | soft |
| NFR-HIST-SCOPE-1 | — | N/A | governance |

**No orphaned FD rule**: BR-HIST-1→COPY-1, **2→SEPARATION-1 (+ADVISORY-1)**, **3→FAITHFUL-1**, 4→DUALREAD-1, 5→RULERESULTS-1, 6→REASON-1, 7→VIEWONLY-1, 8→EMPTY-1, 9→ERROR-1, 10→TESTID-1, 11→NOSUPERSEDE-1. STATEMACHINE-1 / BACKPRESERVE-1 / NOTS-1 / PERF-1 / A11Y-1 cover the addendum + inherited concerns.

---

## 3. Security-Guardrails extension — compliance (enabled extension; expands the plan §5 preview)

`ui-history` is a **read-only display view** — no secrets, no LLM, no persistence, **no write path**. It **reads** the audit trail the write-path units (U7/U8) produced.

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A (referenced)** | The history view submits nothing; application-input validation is `intake`'s SEC-2. It only **reads** R6/R7 responses. |
| Prompt-injection defense | **N/A** | No LLM / prompt path in `ui-history`. It renders **persisted forensic data** (incl. `memo_hash`, not the memo body) — it constructs no prompt and executes no LLM. |
| Secrets management | **N/A** | No secret handled; env/keys are `secrets-config`'s SEC-3. |
| Read-only DB access for audit role | **N/A (referenced)** | The auditor read-only distinction is enforced server-side (`auth-rbac` + `audit-store`, SEC-4). The history view is read-only for **all** roles (VIEWONLY-1) and introduces **no** write path (FAITHFUL-1). |
| Audit logging | **N/A (consumer)** | `ui-history` **persists nothing** — it is a **read consumer** of the audit trail; the write/commit path is U7/U8. |
| Error hygiene (no secret/PII leak) | **Compliant** | ERROR-1 surfaces `message` only, `code` via testid, and **never** renders `error.detail` raw — aligned with WIRE-1 §4 ("no secret VALUE in message/detail"), across **both** reads. |
| **Least-privilege UI framing (advisory-only + read-only + immutable)** | **Compliant** | View-only with **no `RoleGate`/no write affordance** (VIEWONLY-1 / FAITHFUL-1 zero-write-call-site scan); renders the **system** `Recommendation` and the **human** `CommittedDecision` in **structurally distinct** read-only regions (SEPARATION-1), never conflating the namespaces; renders the immutable forensic record with **no edit affordance and no premature superseded handling** (FAITHFUL-1 / NOSUPERSEDE-1) — never implies the record could be altered. |

**No blocking finding.**

---

## 4. Settled items held (not re-opened)
- The **frozen FD** (BR-HIST-1..11 + inventory + flows) is the substrate — NFR builds testable targets **on** it.
- **ui-shell (frozen)** — its Vitest/RTL/ESLint/`FORBIDDEN_TERMS`/`ReadOnlyRegion`/badges/testid mechanisms are **reused**, not modified; `RoleContext` stub is the injection point for VIEWONLY-1; `ReadOnlyRegion` is composed by SEPARATION-1's system region.
- **The frozen sibling UI units (U5–U8)** — their fetchSeam/StructuralGuard/testid-lint are **mirrored as a convention**, **not imported**.
- **WIRE-1** — R6/R7 + `DecisionSummary` + `AuditRecord` + envelopes consumed **by shape**, mocked via the injected dual-read double; the **route implementation** stays deferred to Build & Test (SCOPE-1).
- **Q2-A advisory resolution (HIST-Fold-4 / Fold-D)** — token-avoiding human-region wording, verified against the real detector; the reused blanket lint stays unmodified; the full `copy.js` is Code-Gen.
- **Deferred values**: aesthetic token values, the exact profile-snapshot field subset, the `rule_results` disclosure widget markup + state-holding mechanics (hook/store, request cancellation on rapid row switches), bundler/deploy topology → NFR-Design / Code-Gen / `deploy-config` (P2). Infrastructure Design for `ui-history` not pre-committed (likely a logged SKIP — source-level view; Vercel topology is `deploy-config` P2) — confirmed at that stage.
