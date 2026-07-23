# NFR Requirements — `ui-memo-view` (U6)

**Stage**: BUILD → NFR Requirements (per-unit) · **Unit**: U6 `ui-memo-view` · C5 · Phase 1 · **Depth**: lighter (display)
+ fetch-lifecycle addendum + three-region read-only-separation addendum · **Date**: 2026-07-09 · Story **US-UI-2** ·
FR-MEMO-3 / NFR-EXPLAIN-1 / FR-UI-3 / FR-UI-5.
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md` — **BR-MEMO-1..11**, the
component/prop inventory, the four-state render enum, the `data-testid` inventory incl. region-level testids, the
fetch/state + three-region composition flows) — **re-opening none of it**. Each `NFR-MEMO-*` target is a **pass/fail
testable assertion** traced to its FD rule. **Tier convention inherited from `ui-shell` (frozen U10) and applied by
`ui-queue` (frozen U5)**: Vitest + React Testing Library + jsdom · ESLint over the single `FORBIDDEN_TERMS` · file/import
scan · detector self-tests. **Advisory-only; no LLM; no live backend** (WIRE-1 R4 mocked via a single injected/capturing
fetch double). Q1–Q7 all **A**.

---

## 0. Central testability principle

`ui-memo-view`'s properties are testable **without a running backend** — R4 is exercised through a **single
injected/capturing fetch double** (Q1-A — the FD's local memo `fetchSeam`, passed to `MemoView` as a prop; production
wires the real transport at the composition root) — four ways:
1. **Build-failing lints + structural scans** — COPY-1 / ADVISORY-1 / TESTID-1 reuse `ui-shell`'s ESLint + the **one**
   `FORBIDDEN_TERMS` source (not a second word-list); NOTS-1 / VIEWONLY-1 / NAMESPACE-1 are file/import/render scans. Each
   lint carries a **detector self-test** so it can never pass vacuously.
2. **Component-render assertions (RTL + jsdom)** — SEPARATION-1, ERROR-1, PENDING-1, LISTORDER-1, VIEWONLY-1(render), and
   the four per-state renders of FETCH-1, using a stub `RoleContext.Provider` where role is relevant.
3. **Capturing-double assertions** — ERROR-1's Retry leg (and the transition test's retry leg) assert on the **requested
   `applicationId`** recorded by the injected double.
4. **Observed/soft** — PERF-1 (single-resource bounded, non-gating) and A11Y-1 (semantic regions + `aria-readonly` +
   keyboard, recorded target).

**NFR-MEMO-Fold-A (single-double, inherited from ui-queue Fold-1)**: there is **one** fetch-double construction — the
injected function of Q1-A. Every state/transition test **programs that same double** (resolve `status:"ready"` → `ready`;
resolve `status:"pending"` → `pending`; reject / error-envelope → `error`) and reads its **recorded requested
`applicationId`** only where target-identity is asserted (ERROR-1 Retry, the transition test's retry leg). **No divergent
double patterns** in the suite.

**NFR-MEMO-Fold-B (DOM-containment in jsdom, from the ambiguity-check, Q2)**: the SEPARATION-1 teeth use `Node.contains()`
(jsdom-supported for **arbitrary-depth** descendants, `false` for a sibling subtree) + scoped `within()` queries — so the
**sibling non-containment** assertion is sound, not just parent-child. No bespoke DOM walking.

**NFR-MEMO-Fold-C (two distinct ready fixtures, from the ambiguity-check, Q3)**: PENDING-1's discriminator teeth and
LISTORDER-1's ordering teeth need **fixtures of opposite shape** and therefore **do not share one** — an **empty-lists
ready memo** (PENDING-1; also exercises BR-MEMO-9's empty-list neutral-copy branch) and a **populated non-sorted ready
memo** (LISTORDER-1). Complementary, no conflict.

**Scope**: the `NFR-MEMO-*` set tests **only** `ui-memo-view`'s own view behavior; it does **not** test other UI units,
any backend unit's internals, or the WIRE-1 route implementation (R4 impl → Build & Test). It **reuses** ui-shell's frozen
mechanisms (copy / `FORBIDDEN_TERMS` / ESLint / `ReadOnlyRegion` / testid convention) and **mirrors** ui-queue's
fetchSeam/StructuralGuard/testid-lint convention **without modifying or importing** either.

### Governance — BR-MEMO-2 advisory-conformance scope exclusion (Q6-A, binding)

The `advisory-vocabulary` / `no-inline-label` lints assert the view's **static source only** — component labels, region
headings, chrome, `MissingInfoSource` labels, and the RO-region framing. The runtime **`narrative_prose`** is LLM-authored
content whose advisory conformance is **memo-agent-core's** concern (CON-BR2 enforced at draft time). **No `NFR-MEMO-*`
target asserts anything about `narrative_prose` content.** The view's obligation is the **structural read-only separation**
(SEPARATION-1) + advisory-clean **chrome** (COPY-1 / ADVISORY-1 / NAMESPACE-1), never linting or rewriting runtime prose.

---

## 1. Finalized `NFR-MEMO-*` targets (pass/fail; acceptance criteria; test tier)

### FULL RIGOR

#### NFR-MEMO-COPY-1 — single-source copy; no inlined display label (BR-MEMO-1)
- **Assertion**: no Recommendation/Confidence **label literal** appears anywhere in `frontend/src/memoView/`; every enum
  label is **imported** from `shell/copy` (badges render by **value look-up**); memo-specific chrome + `MissingInfoSource`
  labels live in the **memo-local copy module**.
- **Acceptance**: (a) a **build-failing ESLint rule** (the ui-shell `no-inline-label` mechanism, D4) flags any label
  literal outside `shell/copy`; (b) an RO region given `recommendation="DECLINE-RECOMMEND"` renders the label sourced from
  `RECOMMENDATION_LABELS` (never a bare `DECLINE`); (c) **detector self-test** — a synthetic inlined label is flagged.
- **Tier**: structural / lint (unit). **Rigor**: full.

#### NFR-MEMO-ADVISORY-1 — reuse the ONE `FORBIDDEN_TERMS`; static-code scope only (BR-MEMO-2 / MEMO-Fold-1)
- **Assertion**: the shell `no-inline-label` + `advisory-vocabulary` lints are registered on `src/memoView/**` (a new
  `eslint.config.js` block mirroring the queue block — **no `src/shell` edit, no new word-list**); the memo-local copy +
  components contain **no** `FORBIDDEN_TERMS.systemOutput` token (`DECLINE`/`decision`/`approved`/`declined`) and inline no
  shell label. **`narrative_prose` content is out of scope** (governance §0).
- **Acceptance**: (a) the reused lints pass over `src/memoView/` static code; (b) **no** new word-list exists under
  `src/memoView/`; (c) **detector self-test** — a synthetic forbidden term in static code fails the lint; (d) **no**
  assertion is made against `narrative_prose` content (by design).
- **Tier**: structural / lint. **Rigor**: full.

#### NFR-MEMO-SEPARATION-1 — three-region read-only separation, with teeth (BR-MEMO-3 / 4 / 5) — **the load-bearing target**
- **Assertion**: on a `ready` render, the RO region is a **distinct, non-nested DOM node** from the L narrative;
  recommendation/confidence render **exclusively** inside the RO region; the RO region composes the frozen `ReadOnlyRegion`
  (`aria-readonly`). The structural expression of **CON-BR2-TYPE**.
- **Acceptance** (Q2-A — **direct DOM-tree containment, real teeth; NFR-MEMO-Fold-B**): obtain `memo-region-readonly` and
  `memo-region-narrative`; assert (a) **`!narrative.contains(readonly)` AND `!readonly.contains(narrative)`** (neither is
  an ancestor/descendant of the other); (b) **`within(readonly).getByTestId('memo-recommendation')`** and
  **`memo-confidence`** are present; (c) **`within(narrative).queryByTestId('memo-recommendation')` is `null`** (and
  likewise `memo-confidence`); (d) the RO node carries **`aria-readonly`** and an engine-attributed heading from
  memo-local copy. **Teeth**: the test **fails** if the recommendation were rendered inside/under the narrative region.
- **Tier**: component (RTL + jsdom). **Rigor**: **full (highest)**.

#### NFR-MEMO-ERROR-1 — error `message`-only / `code` via testid / `detail` never raw; same-resource Retry (BR-MEMO-6)
- **Assertion**: on an R4 failure, the visible text is `error.message` only; `error.code` is exposed only via testid;
  `error.detail` never reaches the DOM. Retry re-fetches R4 for the **same `applicationId`**.
- **Acceptance**: with the double resolving/rejecting an error body `{error:{code,message,detail}}` — (a)
  `memo-error-message` renders `message`; (b) `memo-error-code` carries `code` and it is **not** visible UI text; (c) a
  DOM scan finds `detail`'s content **nowhere** in the render; (d) **Retry teeth** (Q4-A) — the **capturing** double is
  failed for `applicationId = X`; activating `memo-error-retry` issues a re-fetch whose **recorded request targets the
  same `applicationId = X`** — the assertion is `requestedId === X`, so the test **fails if Retry fetched a
  different/absent id**.
- **Tier**: component (RTL) + capturing double (Q1-A / Q4-A). **Rigor**: full.

#### NFR-MEMO-VIEWONLY-1 — view-only; no `RoleGate`, no router, no commit affordance (BR-MEMO-7)
- **Assertion**: the memo view renders no `RoleGate`, imports no router/navigation module, exposes no commit affordance,
  and gates nothing by Role; render is role-invariant.
- **Acceptance**: (a) **structural** — no `RoleGate` import/usage and no router import in `frontend/src/memoView/`
  (StructuralGuard scans mirroring ui-queue's `noRoleGateImport` / `noRouterImport`); no commit-affordance element exists;
  (b) RTL — the rendered output is **identical** with a stub `RoleContext.Provider` set to `underwriter`, `auditor`, and
  `admin` (all authenticated any-role for R4).
- **Tier**: structural + component. **Rigor**: full.

#### NFR-MEMO-PENDING-1 — `pending` derived from the `status` discriminator, with teeth (BR-MEMO-8)
- **Assertion**: `status:"pending"` → a single page-level "not yet drafted" state; `status:"ready"` → the memo; the state
  is keyed on the **`status`** field, **not** on list-emptiness.
- **Acceptance** (Q3-A — **honest constructible teeth; NFR-MEMO-Fold-C**): (a) a `status:"pending"` body renders
  `memo-state-pending` and **none** of the three regions; (b) a `status:"ready"` body renders the three-region memo (not
  pending) **even when `missing_information` and `cited_rule_ids` are empty arrays** (both legitimately default to `[]`) —
  proving the derivation keys on `status`, refuting an "empty ⇒ pending" heuristic; (c) the state selection reads
  `view.status`, not `memo`/`report` contents. The **reverse** case (`status:"pending"` with a non-null memo) is a
  **WIRE-1 contract violation** and is **not** fabricated as a fixture.
- **Tier**: component (RTL). **Rigor**: full.

#### NFR-MEMO-LISTORDER-1 — deterministic list order preserved; no client re-sort (BR-MEMO-9)
- **Assertion**: the rendered order of `missing_information` and `cited_rule_ids` equals the delivered array order — the
  view **re-sorts nothing**.
- **Acceptance**: (a) RTL over a **populated, deliberately non-sorted** ready memo (NFR-MEMO-Fold-C's second fixture) —
  the rendered `memo-missinginfo-*` order equals the input `missing_information` order, and `memo-citation-*` equals the
  input `cited_rule_ids` order (**teeth**: a non-sorted input renders in the same non-sorted order, so the test fails if a
  client sort were introduced); (b) each missing-info row renders `detail` (primary) + a `MISSING_INFO_SOURCE_LABELS[source]`
  label; (c) the empty-list branch (empty arrays → `noCitationsLabel` / `noMissingInfoLabel`) is exercised by the
  empty-lists ready fixture (shared with PENDING-1).
- **Tier**: component (RTL). **Rigor**: full.

#### NFR-MEMO-TESTID-1 — `data-testid` convention incl. region testids (BR-MEMO-10 / MEMO-Fold-2)
- **Assertion**: every assertion-relevant memo element carries a stable `memo-<element>-<purpose>` testid
  (`domain-entities.md §6`), **including** the region-level testids (`memo-region-narrative`/`-citations`/`-missinginfo`/
  `-readonly` + `memo-recommendation`/`memo-confidence` + state testids), applying the frozen ui-shell / ui-queue
  convention to the memo namespace.
- **Acceptance**: (a) a `memo-testid-convention` lint/test (mirroring ui-queue's `queue-testid-convention`) asserts the
  convention across memo elements; (b) the four region testids + `memo-recommendation`/`memo-confidence` are present;
  (c) **detector self-test** — a missing/misnamed testid is flagged (non-vacuous).
- **Tier**: lint / component. **Rigor**: full.

#### NFR-MEMO-NOTS-1 — no TypeScript (FR-UI-5 / D2)
- **Assertion**: `frontend/src/memoView/` is plain JS/JSX — no `.ts`/`.tsx`, no TS config.
- **Acceptance**: a file-scan finds **zero** `.ts`/`.tsx` under the memoView tree and no `tsconfig*.json`; CI fails otherwise.
- **Tier**: structural. **Rigor**: full.

#### NFR-MEMO-FETCH-1 — R4 fetch-double + four-state machine coverage (fetch-lifecycle addendum / Q1-A · Q5-A)
- **Assertion**: R4 is fetched through the **injected/capturing double**; each of the four render states renders
  correctly; the state machine's transitions are covered by **one consolidated transition test** (Q5-A).
- **Acceptance**: (a) `MemoView` receives its fetch function via **prop** and never imports a hard-wired fetch (Q1-A);
  (b) **per-state renders** — `loading` shows `memo-state-loading` **and no memo region renders while loading**, `ready`
  shows the three regions, `pending` shows `memo-state-pending` (per PENDING-1), `error` per ERROR-1; (c) **one
  consolidated transition test** exercises `loading→ready`, `loading→pending`, `loading→error`, `error--retry-->loading`,
  all on the **same** double (NFR-MEMO-Fold-A).
- **Tier**: component (RTL). **Rigor**: full.

### MEDIUM RIGOR

#### NFR-MEMO-NAMESPACE-1 — system `Recommendation` only, never human `CommitAction` (BR-MEMO-11)
- **Assertion**: only system `Recommendation` values render (incl. `DECLINE-RECOMMEND`, never bare `DECLINE`); no
  lowercase human `approve`/`override` string is rendered anywhere in the memo view.
- **Acceptance**: (a) **structural** — only `RecommendationBadge` (value ∈ {APPROVE, REFER, "DECLINE-RECOMMEND"}) appears
  (inside the RO region); (b) reuses the `FORBIDDEN_TERMS` collision guard so a memo string equal to a human
  `CommitAction` label — or a bare `DECLINE` — is flagged; (c) **detector self-test** — a synthetic `approve`/`override`/
  bare-`DECLINE` render is flagged.
- **Tier**: structural. **Rigor**: medium.

### SOFT / OBSERVED

#### NFR-MEMO-PERF-1 — single-resource bounded; observed, non-gating (Q7-A)
- **Assertion**: the memo view fetches a **single bounded resource** (one memo by `applicationId`; never a list/all-rows
  path); render latency/bundle are observed, non-gating (matches ui-shell / ui-queue PERF).
- **Acceptance**: (a) **structural** — the fetch path targets exactly one `applicationId` memo (no unbounded/list fetch
  path exists); (b) latency/bundle observed, **no SLO gate** in Phase 1.
- **Tier**: structural (bounding) + observed (latency). **Rigor**: soft.

#### NFR-MEMO-A11Y-1 — semantic regions + `aria-readonly` + keyboard; recorded target, non-gating (Q7-A / NFR-EXPLAIN-1)
- **Assertion**: the memo view uses **semantic region markup + headings**, the RO region's **`aria-readonly`** (frozen
  `ReadOnlyRegion`), a keyboard-focusable **Retry** control, and accessible labels.
- **Acceptance**: recorded as a target; detailed a11y verification **not gating** in Phase 1 (consistent with the
  lighter/display depth; ui-shell A11Y deferred detailed a11y to the view units — this is that unit).
- **Tier**: observed / soft. **Rigor**: soft.

### GOVERNANCE

#### NFR-MEMO-SCOPE-1 — scoped exclusions *(not a runtime test)*
- **Statement**: the set tests **only** `ui-memo-view`'s view behavior. It does **not** test other UI units, backend
  internals, or the WIRE-1 **route implementation** (`backend/app/main.py` → Build & Test). It **reuses** ui-shell's frozen
  copy/`FORBIDDEN_TERMS`/ESLint/`ReadOnlyRegion`/testid mechanisms and **mirrors** ui-queue's fetchSeam/StructuralGuard/
  testid-lint convention **without modifying or importing** either; WIRE-1 R4 is consumed **by shape**, mocked in tests.
  Per BR-MEMO-2 (§0 governance), **no target asserts against `narrative_prose` content**. Enforced by review.
- **Tier**: N/A (governance).

---

## 2. Traceability (target → FD rule → tier → rigor)

| Target | FD rule | Tier | Rigor |
|---|---|---|---|
| NFR-MEMO-COPY-1 | BR-MEMO-1 | lint | full |
| NFR-MEMO-ADVISORY-1 | BR-MEMO-2 | lint | full |
| NFR-MEMO-SEPARATION-1 | BR-MEMO-3 / 4 / 5 | component | **full (highest)** |
| NFR-MEMO-ERROR-1 | BR-MEMO-6 | component + capturing double | full |
| NFR-MEMO-VIEWONLY-1 | BR-MEMO-7 | structural + component | full |
| NFR-MEMO-PENDING-1 | BR-MEMO-8 | component | full |
| NFR-MEMO-LISTORDER-1 | BR-MEMO-9 | component | full |
| NFR-MEMO-TESTID-1 | BR-MEMO-10 | lint / component | full |
| NFR-MEMO-NAMESPACE-1 | BR-MEMO-11 | structural | medium |
| NFR-MEMO-NOTS-1 | FR-UI-5 (D2) | structural | full |
| NFR-MEMO-FETCH-1 | fetch-lifecycle addendum (states) | component | full |
| NFR-MEMO-PERF-1 | view perf (PER precedent) | structural + observed | soft |
| NFR-MEMO-A11Y-1 | FR-UI (view) / NFR-EXPLAIN-1 | observed | soft |
| NFR-MEMO-SCOPE-1 | — | N/A | governance |

**No orphaned FD rule**: BR-MEMO-1→COPY-1, 2→ADVISORY-1, **3/4/5→SEPARATION-1**, 6→ERROR-1(+FETCH-1 error state),
7→VIEWONLY-1, 8→PENDING-1(+FETCH-1 pending state), 9→LISTORDER-1, 10→TESTID-1, 11→NAMESPACE-1. FETCH-1/NOTS-1/PERF-1/
A11Y-1 cover the inherited + addendum concerns.

---

## 3. Security-Guardrails extension — compliance (enabled extension; expands the plan §5 preview)

`ui-memo-view` is a **read-only display view** — no secrets, no LLM, no persistence, no write path. It **renders**
LLM-authored prose but authors/executes none.

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A (referenced)** | The memo view submits nothing; application-input validation is `intake`'s SEC-2. It only **renders** R4 responses. |
| Prompt-injection defense | **N/A (referenced)** | No LLM / prompt path in `ui-memo-view`. It displays `narrative_prose` but constructs no prompt; SEC-1 (forensic-span isolation) is memo-agent-core's, and the `MemoView` payload carries no forensic span (SEC1-1). |
| Secrets management | **N/A** | No secret handled; env/keys are `secrets-config`'s SEC-3. |
| Read-only DB access for audit role | **N/A (referenced)** | The auditor read-only distinction is enforced server-side (`auth-rbac` + `audit-store`, SEC-4). The memo view is read-only for **all** roles (VIEWONLY-1). |
| Audit logging | **N/A** | The memo view persists nothing (no commit path — that is U7/U8). |
| Error hygiene (no secret/PII leak) | **Compliant** | ERROR-1 surfaces `message` only, `code` via testid, and **never** renders `error.detail` raw — aligned with WIRE-1 §4 ("no secret VALUE in message/detail"). |
| **Least-privilege UI framing (advisory-only + read-only)** | **Compliant** | View-only with **no `RoleGate`/no commit affordance** (VIEWONLY-1); renders only the **system** `Recommendation`, never a human `CommitAction` (NAMESPACE-1); enforces the **structural read-only separation** of the RO region so the UI never implies the LLM produced the recommendation (SEPARATION-1, the CON-BR2 visual respect). |

**No blocking finding.**

---

## 4. Settled items held (not re-opened)
- The **frozen FD** (BR-MEMO-1..11 + inventory + flows) is the substrate — NFR builds testable targets **on** it.
- **ui-shell (frozen)** — its Vitest/RTL/ESLint/`FORBIDDEN_TERMS`/`ReadOnlyRegion`/testid mechanisms are **reused**, not
  modified; `RoleContext` stub is the injection point for VIEWONLY-1; `ReadOnlyRegion` is composed (first use) by
  SEPARATION-1.
- **ui-queue (frozen)** — its fetchSeam/StructuralGuard/testid-lint are **mirrored as a convention**, **not imported**.
- **WIRE-1** — R4 + `MemoView` + `DecisionMemo` + envelopes consumed **by shape**, mocked via the injected double; the
  **route implementation** stays deferred to Build & Test (SCOPE-1).
- **BR-MEMO-2 scope exclusion (Q6-A)** — recorded as a binding governance statement (§0); no target touches
  `narrative_prose` content.
- **Deferred values**: aesthetic token values, the minimal profile-header field set, state-holding mechanics (hook/store,
  retry debounce, cancellation), bundler/deploy topology → NFR-Design / Code-Gen / `deploy-config` (P2). Infrastructure
  Design for `ui-memo-view` not pre-committed (likely a logged SKIP — source-level view; Vercel topology is
  `deploy-config` P2) — confirmed at that stage.
