# NFR Requirements — Plan (Part 1) — `ui-memo-view` (U6)

**Stage**: BUILD → per-unit loop → NFR Requirements **Part 1 (Plan)** · **Unit**: U6 `ui-memo-view` · C5 · Phase 1
**Depth**: **lighter (display) + fetch-lifecycle addendum + three-region read-only-separation addendum** (consistent with
the FD depth decision) · **Date**: 2026-07-09
**Story**: US-UI-2 · **Requirements**: FR-MEMO-3 / NFR-EXPLAIN-1 / FR-UI-3 / FR-UI-5.
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md` — **BR-MEMO-1..11**, the
component/prop inventory, the four-state render enum, the `data-testid` inventory incl. region-level testids, the
fetch/state and three-region composition flows) — **re-opening none of it**. Each draft `NFR-MEMO-*` target is a
**pass/fail testable assertion** traced to its FD rule.

> **Part 1 (Plan) only.** This file lists the **draft** target map + open [Answer] questions and the Part 2 artifacts to
> generate **after** approval. **No NFR artifact (`nfr-requirements.md` / `tech-stack-decisions.md`) is generated here.**

---

## 0. Prerequisites & grounding (read, not re-derived)

- [x] FD complete for `ui-memo-view` (three artifacts, gate approved 2026-07-09; §1 Mermaid convention-corrected to
  rectangle-only).
- [x] **Tier convention inherited from `ui-shell` (frozen U10) and applied by `ui-queue` (frozen U5) — grounded, not invented**:
  - **D1/D2** React + Tailwind, **no TypeScript** (plain JS/JSX).
  - **D3** test tier = **Vitest + React Testing Library + jsdom**; component targets drive RTL renders; **no live backend**.
  - **D4** **ESLint over the single `FORBIDDEN_TERMS` source** backs build-failing lints; each lint ships a **detector
    self-test** (non-vacuous — can never pass vacuously). **Reused, not modified** (no second word-list).
  - **D5** **file/import scan in CI** for structural targets (no-TS, no-RoleGate-import, no-router-import).
  - **D6** **injected/capturing fetch double** for the real fetch (WIRE-1 R4), **one** double construction for the suite
    (the `ui-queue` NFR-QUEUE-Fold-1 precedent).
- [x] **The genuinely-new concerns vs `ui-queue`** (which this plan must make testable):
  1. **A single-resource R4 fetch** (`GET /applications/{application_id}/memo`) with a **`status` discriminator**
     (`ready`|`pending`) rather than a paged list — so `pending` is derived from **`status`**, not `items.length`
     (BR-MEMO-8 / N1). No pagination.
  2. **The three-region read-only-separation triad (BR-MEMO-3/4/5)** — the **load-bearing** target: the RO region must be
     a **distinct, non-nested DOM node** from the L narrative, with recommendation/confidence rendered **exclusively** in
     the RO region. This is the concrete structural expression of **CON-BR2-TYPE** and needs the **highest-rigor test with
     teeth** (a test that fails if the recommendation were rendered inside/under the narrative).
  3. **The FORBIDDEN_TERMS reuse scope boundary (BR-MEMO-2)** — lints cover the view's **static code only**; they must
     **explicitly exclude** any assertion against runtime `narrative_prose` content (memo-agent-core's CON-BR2 concern).

---

## 1. Draft `NFR-MEMO-*` target map (BR-MEMO-1..11 → pass/fail target · tier · rigor)

Every FD rule maps to a target (no orphan). Tiers use the inherited convention (unit = Vitest; component = RTL+jsdom;
structural = file/import scan or ESLint). Targets marked *(Q#)* have an **open tier/scope question in §3**.

| # | Target | FD rule | Draft pass/fail assertion | Tier | Rigor |
|---|---|---|---|---|---|
| T1 | **NFR-MEMO-COPY-1** | BR-MEMO-1 | No Recommendation/Confidence **label literal** anywhere in `frontend/src/memoView/`; every enum label imported from `shell/copy` (badges render by **value look-up**); memo-local chrome + `MISSING_INFO_SOURCE_LABELS` live in the memo-local copy module. **Reuses ui-shell's ESLint `no-inline-label`** (D4) + detector self-test. | structural / lint | full |
| T2 | **NFR-MEMO-ADVISORY-1** | BR-MEMO-2 | **Reuse the ONE `FORBIDDEN_TERMS`** — register shell `no-inline-label` + `advisory-vocabulary` lints on `src/memoView/**` (a new `eslint.config.js` block mirroring the queue block; **no `src/shell` edit, no new word-list**); the memo-local copy + components pass. **Scope boundary (explicit): the lints assert the view's STATIC code only; NO assertion is made against `narrative_prose` content** *(Q6 wording of the exclusion)*. Detector self-test (a synthetic forbidden term in static code fails). | structural / lint | full |
| T3 | **NFR-MEMO-SEPARATION-1** *(the load-bearing triad)* | BR-MEMO-3 / 4 / 5 | **Highest-rigor, with teeth** *(Q2)*: (a) `memo-region-readonly` and `memo-region-narrative` are **distinct DOM nodes** with **neither an ancestor/descendant of the other** (non-containment); (b) the RO region **composes the frozen `ReadOnlyRegion`** (`aria-readonly` present) framed engine-attributed via memo-local chrome; (c) `RecommendationBadge`/`ConfidenceBadge` render **exclusively inside** `memo-region-readonly` and **never inside** `memo-region-narrative` — the assertion **fails** if the recommendation were rendered within/under the narrative. | component (RTL) *(Q2)* | **full (highest)** |
| T4 | **NFR-MEMO-ERROR-1** | BR-MEMO-6 | RTL + mocked error body `{error:{code,message,detail}}`: `memo-error-message` shows **`message`**; `memo-error-code` carries **`code`** (not visible text); **`detail` never appears in the DOM**. **Same-resource Retry** *(Q4)*: activating `memo-error-retry` re-fetches R4 for the **same `applicationId`** — with teeth (fails if it fetched a different/absent id). | component (RTL) + capturing double *(Q4)* | full |
| T5 | **NFR-MEMO-VIEWONLY-1** | BR-MEMO-7 | **Structural**: `frontend/src/memoView/` imports **no `RoleGate`** and **no router/navigation module**, and exposes **no commit affordance**. **RTL**: render is **identical** with a stub `RoleContext.Provider` set to `underwriter` / `auditor` / `admin` (all authenticated any-role for R4). | structural + component | full |
| T6 | **NFR-MEMO-PENDING-1** | BR-MEMO-8 | **Teeth on the discriminator** *(Q3)*: a `status:"pending"` body renders `memo-state-pending` and **none** of the three regions; a `status:"ready"` body renders the memo (not pending) **even when `missing_information` / `cited_rule_ids` are empty arrays** — proving the state is keyed on **`status`, not array-emptiness**. (Reverse artificial case — `status:"pending"` with a non-null memo — is a **contract violation**, not honestly constructible; see §2 / Q3.) | component (RTL) *(Q3)* | full |
| T7 | **NFR-MEMO-LISTORDER-1** | BR-MEMO-9 | RTL: the rendered order of `memo-missinginfo-*` equals the input `missing_information` array order, and `memo-citation-*` equals the input `cited_rule_ids` order — **no client-side re-sort** occurs (teeth: a deliberately non-sorted input renders in the same non-sorted order). Each missing-info row renders `detail` + a `MISSING_INFO_SOURCE_LABELS[source]` label. | component (RTL) | full |
| T8 | **NFR-MEMO-TESTID-1** | BR-MEMO-10 | A lint/test asserts the **`memo-<element>-<purpose>`** convention across memo elements incl. the **region-level testids** (`memo-region-narrative`/`-citations`/`-missinginfo`/`-readonly` + `memo-recommendation`/`memo-confidence` + state testids); **detector self-test** — a missing/misnamed testid is flagged (non-vacuous). Mirrors ui-queue's `queue-testid-convention`. | lint / component | full |
| T9 | **NFR-MEMO-NAMESPACE-1** | BR-MEMO-11 | **Structural**: only **system** `Recommendation` values render (incl. `DECLINE-RECOMMEND`, never bare `DECLINE`); **no** lowercase human `approve`/`override` string rendered anywhere in the memo view — **reuses the `FORBIDDEN_TERMS` collision guard**. Detector self-test (a synthetic `approve`/`override`/bare-`DECLINE` render is flagged). | structural | medium |

### Cross-cutting / addendum targets

| # | Target | Source | Draft assertion | Tier | Rigor |
|---|---|---|---|---|---|
| T10 | **NFR-MEMO-NOTS-1** | FR-UI-5 / D2 | File-scan: **zero `.ts`/`.tsx`** under `frontend/src/memoView/`; no TS config. (Inherited from ui-shell / ui-queue NOTS-1.) | structural | full |
| T11 | **NFR-MEMO-FETCH-1** | fetch-lifecycle addendum | R4 fetched via an **injected/capturing fetch double** *(Q1)*; each of the **four render states** (`loading`/`ready`/`pending`/`error`) has a render assertion; **state-transition coverage** *(Q5)*. `MemoView` never imports a hard-wired fetch. | component (RTL) | full |
| T12 | **NFR-MEMO-PERF-1** | (view perf; ui-shell/ui-queue PERF precedent) | The memo view fetches a **single bounded resource** (one memo by `applicationId`; no list/all-rows path). Observed/soft, non-gating *(Q7)*. | *(Q7)* | soft |
| T13 | **NFR-MEMO-A11Y-1** | FR-UI (view unit) / NFR-EXPLAIN-1 | Semantic region markup + headings, the RO region's `aria-readonly` (frozen `ReadOnlyRegion`), keyboard-focusable Retry control, accessible labels. Gating vs soft → *(Q7)*. | *(Q7)* | soft |

**No orphaned FD rule**: BR-MEMO-1→T1, 2→T2, **3/4/5→T3**, 6→T4(+T11 error state), 7→T5, 8→T6(+T11 pending state), 9→T7,
10→T8, 11→T9; T10–T13 cover the inherited/addendum concerns (NOTS, the fetch-double + four-state machine, perf, a11y).

---

## 2. The fetch-double, four-state machine, and the separation teeth — made testable (the addenda)

`ui-memo-view` is the **second** UI unit to exercise a real fetch (R4), **mocked** in tests via an injected/capturing
double (no live backend). Three things the NFR set must pin:

- **(a) The R4 double + four-state machine** — how R4 is doubled (Q1) and how the `loading → ready | pending | error`
  (+ `error --retry--> loading`) machine is covered (per-state renders + a possible consolidated transition test, Q5).
  Unlike ui-queue there is **no pagination** and **no `empty`** state; the fourth state is **`pending`, derived from the
  `status` discriminator** (T6).
- **(b) The BR-MEMO-8 discriminator teeth — constructibility check (Q3).** WIRE-1 §5 **guarantees co-presence keyed on
  `status`**: `status:"ready"` ⇒ `profile`/`report`/`memo` present; `status:"pending"` ⇒ `report`/`memo` null. Therefore:
  - The **honest, contract-legitimate** teeth is a **`status:"ready"` memo whose `missing_information` and
    `cited_rule_ids` are empty arrays** (both legitimately default to `[]` in `memo_agent_core.schemas`). The view must
    render this as **ready** (all three regions, with empty lists showing their neutral empty copy) and **NOT** as
    `pending` — proving the derivation keys on **`status`**, not on list emptiness.
  - The **reverse artificial case** (`status:"pending"` carrying a non-null `memo`) is a **WIRE-1 contract violation** and
    would be a **dishonest** fixture — so it is **not** manufactured. Q3 confirms this framing (assert the honest
    direction; do not fabricate an impossible response).
- **(c) The separation teeth (Q2)** — the load-bearing T3. The question is whether "distinct nodes, non-containment,
  badges-only-in-RO" is proven by a **direct DOM-tree containment assertion** (real teeth: query both region nodes and
  assert `!narrative.contains(recommendation)` and `readonly.contains(recommendation)`) or merely by **testid presence**
  (weaker — presence alone does not prove non-nesting). Q2 decides; the recommendation is the DOM-containment assertion so
  the test genuinely fails if the recommendation were nested under the narrative.

RETRY (T4) and PENDING (T6) already cover two transitions; Q5 decides whether a dedicated consolidated transition test is
added for the rest.

---

## 3. Open NFR-tier questions ([Answer] tags — lettered per the standing convention)

> Answered by the user (2026-07-09) — **all A**; the full Q&A is embedded here per the standing convention, before Part 2.

### Q1 — R4 fetch-double construction
- **A.** **Injected/capturing fetch double** — `MemoView` receives its fetch function via **prop** (`fetchSeam`, per the
  FD); tests pass a capturing double that records the requested `applicationId` and returns programmed responses;
  production wires the real fetch at the composition root. **One** double construction for the whole suite (ui-queue
  Fold-1 precedent). *(Recommended — matches the FD's injected local memo fetchSeam (Q6-A) and makes T4's "same
  applicationId" assertion clean.)*
- **B.** **Global `fetch` mock** (`vi.stubGlobal` / MSW-style URL interceptor) — more realistic, but capturing the exact
  requested `applicationId` for T4 is indirect.
- **C.** **Module-level fetch client** mocked via `vi.mock`.

`[Answer]:` **A** — injected/capturing fetch double via **prop** (`fetchSeam` per the FD); tests pass a capturing double
recording the requested `applicationId`; production wires the real fetch at the composition root; **one** double
construction for the suite.

### Q2 — Structural-separation teeth test construction (BR-MEMO-3/4/5, the load-bearing T3)  *(user-flagged)*
- **A.** **Direct DOM-tree containment assertion (real teeth)** — render the ready memo; obtain the `memo-region-readonly`
  and `memo-region-narrative` nodes; assert **(i)** neither `node.contains()` the other (non-ancestor/descendant),
  **(ii)** `memo-recommendation` + `memo-confidence` are **within** `memo-region-readonly` (via `within()`/`.contains()`),
  and **(iii)** they are **NOT within** `memo-region-narrative`. The RO node also carries `aria-readonly` (frozen
  `ReadOnlyRegion`). This **fails** if the recommendation were rendered inside/under the narrative. *(Recommended — this is
  genuine structural proof of CON-BR2-TYPE, not mere testid presence.)*
- **B.** **Testid-presence / sibling check only** — assert all region testids exist and `memo-recommendation` is a
  descendant of `memo-region-readonly`; do **not** assert non-containment against the narrative. *(Weaker — presence alone
  does not prove the RO region isn't nested under the narrative; rejected as insufficient teeth for the load-bearing rule.)*

`[Answer]:` **A** — direct DOM-tree containment assertion: neither region node contains the other;
`RecommendationBadge`/`ConfidenceBadge` are **within** `memo-region-readonly` and **NOT within** `memo-region-narrative`;
the RO node carries `aria-readonly`. Real teeth, not testid-presence-only.

### Q3 — BR-MEMO-8 discriminator teeth: constructibility given WIRE-1's contract  *(user-flagged)*
- **A.** **Assert the honest, contract-legitimate direction** — teeth = a **`status:"ready"` memo with empty
  `missing_information` and `cited_rule_ids` arrays** renders as **ready** (not `pending`), proving the state is keyed on
  the **`status`** field and **not** on list emptiness; plus a `status:"pending"` body renders `memo-state-pending`. The
  **reverse** (`status:"pending"` with a non-null memo) is a **WIRE-1 contract violation** and is **not** fabricated as a
  fixture. *(Recommended — this is the constructible, honest teeth; it directly refutes an "empty ⇒ pending" heuristic
  without manufacturing an impossible response.)*
- **B.** **Treat the discriminator teeth as non-constructible** and assert only that `status:"pending"` → pending and
  `status:"ready"` → ready with fully-populated fixtures (no empty-list edge case). *(Weaker — does not refute an
  accidental array-emptiness heuristic, which is the exact risk N1 calls out.)*

`[Answer]:` **A** — assert the honest, contract-legitimate direction: a `status:"ready"` memo with **empty**
`missing_information`/`cited_rule_ids` arrays must render as **ready, not pending**, proving the state keys on `status`
not list-emptiness. The reverse (`status:"pending"` with a non-null memo) is a **contract violation** and is **NOT**
fabricated as a fixture.

### Q4 — Same-resource Retry assertion (single memo, not a page — BR-MEMO-6)
- **A.** **Capturing double records the requested `applicationId`** — the double is configured to fail the first R4 fetch
  for `applicationId = X`; activating `memo-error-retry` issues a re-fetch whose **recorded request targets the same
  `applicationId = X`** (teeth: fails if it fetched a different/absent id). *(Recommended — mirrors ui-queue RETRY-1's
  capturing approach, adapted to the single-resource case; there is no page position to preserve.)*
- **B.** **Presence-only** — assert only that Retry triggers a second fetch, without asserting the target id.

`[Answer]:` **A** — the capturing double records the requested `applicationId`; Retry re-fetch must target the **same**
`applicationId`, **with teeth** (fails if a different/absent id is fetched).

### Q5 — Dedicated state-transition test beyond per-state renders?
- **A.** **Yes** — one consolidated transition test exercising `loading→ready`, `loading→pending`, `loading→error`, and
  `error--retry-->loading`, in addition to the per-state render tests (T3/T4/T6) — all on the **same** injected double
  (Fold-1). Gives the state machine explicit teeth. *(Recommended — cheap in RTL; mirrors ui-queue's FETCH-1 consolidated
  transition test.)*
- **B.** **No** — the per-state render tests + T4 (retry) + T6 (pending) already cover every transition; no separate
  machine test.

`[Answer]:` **A** — one consolidated state-transition test exercising `loading→ready`, `loading→pending`,
`loading→error`, `error--retry-->loading`, in addition to the per-state render tests, all on the **same** injected double.

### Q6 — Explicit wording of the FORBIDDEN_TERMS scope-exclusion (BR-MEMO-2 / MEMO-Fold-1)
- **A.** **Record the exclusion as an explicit governance statement in `nfr-requirements.md`** — "the advisory-vocabulary /
  no-inline-label lints assert the view's **static source only** (labels, headings, chrome, region framing); the runtime
  `narrative_prose` is LLM-authored and its advisory conformance is **memo-agent-core's** CON-BR2 concern — **no
  `NFR-MEMO-*` target asserts anything about `narrative_prose` content**." *(Recommended — makes the scope boundary a
  first-class, auditable statement so no later stage mistakes it for a gap.)*
- **B.** Leave it implicit in the lint config (lints simply don't run over prose because prose isn't static code).

`[Answer]:` **A** — record the FORBIDDEN_TERMS scope-exclusion as an explicit governance statement in
`nfr-requirements.md`: the lints assert **static source only**; `narrative_prose`'s advisory conformance is
memo-agent-core's CON-BR2 concern; **no `NFR-MEMO-*` target asserts anything about `narrative_prose` content**.

### Q7 — PERF-1 + A11Y-1 rigor for the memo view
- **A.** **Both observed / soft, non-gating** — PERF: assert structurally the view fetches a **single bounded resource**
  (no list/all-rows path); render latency/bundle observed, non-gating. A11Y: semantic regions + headings + `aria-readonly`
  + keyboard-focusable Retry + accessible labels as a **recorded target**, detailed a11y verification not gating in
  Phase 1. *(Recommended — consistent with the lighter/display depth and the ui-shell/ui-queue PERF/A11Y precedent; the
  view unit is where ui-shell deferred detailed a11y.)*
- **B.** **Gating** — set concrete numeric PERF budgets and/or a gating a11y assertion set enforced as tests now.

`[Answer]:` **A** — both PERF-1 and A11Y-1 **observed/soft, non-gating**, consistent with the ui-shell/ui-queue precedent.

---

## 3.5 Ambiguity-check (RUN 2026-07-09, after the Q1–Q7 answers) — **CLEAN, no STOP** (2 folds)

Ran against the seven answers (all A) + the frozen FD (BR-MEMO-1..11) + the frozen contracts (ui-shell `ReadOnlyRegion`/
copy/`FORBIDDEN_TERMS`; WIRE-1 R4 `MemoView`; memo-agent-core `DecisionMemo`/`MissingInfoSource` defaults). **No genuine
gap.** Two folds surfaced (both resolvable against the frozen contracts + the established Vitest/RTL/jsdom substrate, no
improvisation):

### NFR-MEMO-Fold-1 (check i) — Q2's DOM-containment assertion in the RTL/jsdom environment — **CLEAN**
`Node.contains()` is implemented in **jsdom** and returns `true` for **any descendant at arbitrary depth** (not just a
direct child) — and `false` for a sibling's subtree — so the sibling **non-containment** check is sound, not just the
parent-child case. The assertion is realized with jsdom-supported primitives: obtain both region nodes via
`getByTestId('memo-region-readonly')` / `getByTestId('memo-region-narrative')`, then assert
`!narrative.contains(recommendationNode) && !readonly.contains(narrative) && !narrative.contains(readonly)` **and**
`within(readonly).getByTestId('memo-recommendation')` present **and**
`within(narrative).queryByTestId('memo-recommendation')` **null**. All are standard jsdom/RTL operations — no bespoke DOM
walking. **Recorded as an implementation note** in `tech-stack-decisions.md` (D-new). No gap.

### NFR-MEMO-Fold-2 (check ii) — Q3's empty-arrays ready memo vs T7 LISTORDER-1's ordering fixture — **CLEAN (distinct, complementary fixtures)**
T6 (PENDING discriminator teeth) and T7 (LISTORDER teeth) require **fixtures of opposite shape** and therefore **do not
share one**: T6's teeth needs a `status:"ready"` memo with **empty** `missing_information`/`cited_rule_ids` (to prove
`ready ≠ pending` isn't an emptiness heuristic); T7's teeth needs a `status:"ready"` memo with **non-empty, deliberately
non-sorted** lists (to prove no client re-sort). These are **complementary, not conflicting** — the suite carries (at
least) **two ready fixtures**: an **empty-lists ready memo** (serves T6's discriminator teeth **and incidentally exercises
the empty-list neutral-copy branch** of BR-MEMO-9 — `noCitationsLabel`/`noMissingInfoLabel`) and a **populated non-sorted
ready memo** (serves T7's ordering teeth). No single fixture is asked to prove both emptiness-independence and
order-preservation, so there is **no conflict**. **Recorded** so Code-Gen builds the two fixtures deliberately. No gap.

> Both folds are testability refinements resolvable within the established substrate; **no STOP**. They are carried into
> Part 2 (`nfr-requirements.md` §0 testability principle + `tech-stack-decisions.md` notes).

---

## 4. NFR Requirements **Part 2** plan — artifacts generated **after** approval (checkboxes)

- [x] **`guide-docs/build/ui-memo-view/nfr-requirements/nfr-requirements.md`** — the finalized `NFR-MEMO-*` targets
  (T1–T13 resolved with the Q1–Q7 answers folded in), each a pass/fail assertion with acceptance criteria + test tier +
  rigor; a **central testability principle** (R4 via the single injected/capturing double; no live backend); the
  **BR-MEMO-2 scope-exclusion governance statement** (Q6); a **traceability table** (target → FD rule → tier → rigor, no
  orphan); and the **Security-Guardrails extension compliance table** (see §5 preview).
- [x] **`guide-docs/build/ui-memo-view/nfr-requirements/tech-stack-decisions.md`** — the memo view's tech decisions,
  **inheriting** ui-shell/ui-queue's substrate (React/Tailwind/no-TS/Vitest/RTL/jsdom/ESLint) and adding **only** what's
  new: the **R4 fetch-double construction** (Q1), the **DOM-containment separation-teeth approach** (Q2), the
  **discriminator teeth framing** (Q3), any state-management note (deferred mechanics), and deferred items (aesthetic token
  values, minimal profile-header field set, bundler/deploy topology → `deploy-config` P2).

## 5. Security-Guardrails extension — applicability preview (full table lands in Part 2)

`ui-memo-view` is a **read-only display view** (no secrets, no LLM, no persistence, no write path). Preview: **Input
validation** N/A (referenced — intake's SEC-2; the view submits nothing); **Prompt-injection** N/A (no LLM/prompt path —
the view **renders** LLM-authored prose but authors/executes none; SEC-1 is memo-agent-core's); **Secrets** N/A (none
handled); **Audit logging** N/A (persists nothing — commit is U7/U8); **Read-only auditor distinction** N/A-referenced
(enforced server-side, SEC-4; the view is read-only for **all** roles, T5); **Error hygiene (no secret/PII leak)**
**Compliant** — T4 surfaces `message` only, `code` via testid, and **never** renders `error.detail` raw (WIRE-1 §4);
**Least-privilege UI framing (advisory-only + read-only)** **Compliant** — view-only with **no `RoleGate`/no commit
affordance** (T5), renders only the **system** `Recommendation` never a human `CommitAction` (T9), and enforces the
**structural read-only separation** of the RO region (T3, the CON-BR2 visual respect). No blocking finding anticipated.

## 6. Holds / guardrails (this Part 1)

- [x] **No NFR artifact generated** — only this plan file written.
- [x] **Frozen FD not re-opened** — targets built **on** BR-MEMO-1..11 / the inventory / the flows.
- [x] **WIRE-1 untouched** (R4 consumed by shape, mocked in tests); **`ui-shell` (frozen) untouched** (tier convention +
  `FORBIDDEN_TERMS`/ESLint/`ReadOnlyRegion`/testid mechanism **reused**, not modified); **`ui-queue` (frozen) untouched**
  (its fetchSeam/StructuralGuard/testid-lint are a **convention** mirrored, not imported).
- [x] **No application code** and **no test code** written (design/targets only). **No LLM. No TypeScript.**
- [x] **tier-B corpus run NOT authorized**; **no other unit started**; `audit_store` Docker-guard gap still deferred.
