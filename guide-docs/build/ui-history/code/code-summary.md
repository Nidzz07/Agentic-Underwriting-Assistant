# Code Generation — Summary (Part 2) — `ui-history` (U9)

**Stage**: BUILD → per-unit loop → Code Generation **Part 2** · **Unit**: U9 `ui-history` · C5 · Phase 1 · **Date**: 2026-07-16
**Story**: US-UI-6 (full decision history / audit-trail view) · **Requirements**: FR-UI-1 / FR-UI-3 / FR-UI-5 / **CON-AUDIT-1** (read surface).
**Built ON** the frozen FD (**BR-HIST-1..11**; the component/prop/testid inventory; the `HISTORY_STATE` master-detail machine with position-preserving Back; the namespace-distinct detail composition) + approved NFR Requirements (**seventeen `NFR-HIST-*`**; the single injected/capturing **dual-read** double; Fold-A/B/C/D) + approved NFR Design (patterns **P1–P13**; components **C1–C12**; NFR-DESIGN-Fold-1) — **re-opening none**. **JS/JSX, NO TypeScript; Vitest + RTL + jsdom.** Full-TDD tests-first, leaf-first, per plan §3 Steps 0–12 (all twelve `[x]`).

The **sixth and final frontend unit**, the **last remaining P1 unit overall**, and the **first UI unit to render BOTH namespaces** — the system advisory `Recommendation` and the human committed `CommitAction` — in one view. It is the **read surface over the audit trail the two frozen write-path units (U7/U8) produce**: the defining property of this unit is the **absence** of the write path they own. `ui-shell` is **reused (imported)**; all five sibling UI units are **mirrored-not-imported**; WIRE-1 R6/R7 is **consumed by shape**. No frozen file was created or edited.

---

## 1. Module list (production under `frontend/src/history/`)

| Comp | Module | Role | Coverage |
|---|---|---|---|
| **C1** | `HistoryView.jsx` | the only **fetch-stateful** component and sole seam holder; owns the seven-state master-detail machine (P5), the `{page, items, pageInfo}` **retention across the detail excursion** (P6 — Back never refetches), the `items.length` empty derivation (P7) and **per-operation Retry targeting** (P8); no Role, no `RoleGate`, no router, no write reference | 100% |
| **C2** | `historyFetchSeam.js` | own-local **READ-ONLY dual-read** seam: `createHistoryFetch(transport) → { fetchList, fetchDetail }` + `buildHistoryListRequest(page,size)` / `buildHistoryDetailRequest(decisionId)` (**both GET-only**) + `normalizeError`; export surface **exactly** those four members; **self-evidence header comment** (NFR-DESIGN-Fold-1) | 100% |
| **C3** | `components/HistoryList.jsx` | R6 rows in delivered order (`history-row-<decision_id>`, human action + timestamp, `onSelect(decision_id)`); no system recommendation in a row (no N+1) | 100% |
| **C4** | `components/HistoryPagination.jsx` | derived-state prev/next/indicator over the R6 `page` wrapper → one bounded page per change (mirrors ui-queue's `PaginationControls`, not imported) | 100% |
| **C5** | `components/HistoryStateView.jsx` | the five non-content states; `message` visible / `code` testid-only / `detail` never; the **404 uses the same generic detail path** | 100% |
| **C6** | `components/DecisionDetail.jsx` | read-only composer; the five regions as **siblings**, each given only its own `AuditRecord` slice; no edit affordance; **header comment** | 100% |
| **C7** | `components/SystemRecommendationRegion.jsx` | **`{recommendation, confidence, testid}`-only**; composes the frozen `ReadOnlyRegion` + badges, engine-attributed; sole system render site; **header comment** | 100% |
| **C8** | `components/CommittedActionRegion.jsx` | **`{action, reason, underwriterId, testid}`-only**; sole human render site; `reason` iff `override`; **header comment** | 100% |
| **C9** | `components/ForensicTupleRegion.jsx` | the read-only 6-tuple + content hash + `status` (display-only; no supersede branch) | 100% |
| **C10** | `components/RuleResultsRegion.jsx` | mounted-but-hidden faithful disclosure (every entry mounted, delivered order, `hidden` collapse, focusable toggle); owns only its local disclosure state | 100% |
| **C11** | `components/ProfileSnapshotRegion.jsx` | the read-only verbatim snapshot + tamper-evidence hash; no edit affordance | 100% |
| **(copy)** | `copy.js` | `HISTORY_COPY` — advisory-clean chrome + forensic labels, authored to the Fold-D binding rule and consumed verbatim; LINT-SUBJECT | 100% |
| **(ids)** | `testids.js` | `slugSegment` / `historyRowTestid` / `historyRuleResultTestid` — the dynamic-segment builders (see realization note 3) | 100% |
| **C12** | `__tests__/*` (25 files) + `eslint-rules/history.js` + shared-config extension | the StructuralGuard substrate (test-only) | n/a |

**Shared-config extension (Q1-A)** — `vitest.config.js` `include` + `coverage.include`/`exclude` add `src/history` (**thresholds unchanged**); `eslint.config.js` registers a new `src/history` block reusing `shell/no-inline-label` + `shell/advisory-vocabulary` + the new `history/history-testid-convention` (`eslint-rules/history.js`, mirroring `eslint-rules/queue.js`; `eslint-rules/index.js` untouched). **No file under `src/shell/`, `src/queue/`, `src/memoView/`, `src/approvalGate/` or `src/overrideForm/` created or edited** — mtime-verified.

---

## 2. Test → `NFR-HIST-*` target map (25 test files + `fixtures.js`/`refNotOwn.js`; all seventeen targets at their NFR-pinned tier)

| Target | Test file(s) | Tier |
|---|---|---|
| **SEPARATION-1** *(load-bearing)* | `history.separation.test.jsx` (Fold-B containment teeth: `!system.contains(human)` **and** the converse; rec/conf only in system, action/reason only in human; `aria-readonly`; each value renders exactly once; the **override** record used so conflation would be maximally visible) | component (teeth) |
| **FAITHFUL-1** *(load-bearing)* | `noWriteSeam.test.js` (zero `submit*`, zero commit/override builder, zero non-GET method, zero `body:`; exact four-member export; both builders GET-only; no commit-seam import; self-tests incl. comment-immunity) | structural / AST |
| **DUALREAD-1** | `history.dualread.test.jsx` (select → 1 `fetchDetail(id)` + 0 new `fetchList`; page → 1 `fetchList(target)` + 0 `fetchDetail`) + `noRouterImport.test.js` | component + double + structural |
| **RULERESULTS-1** | `history.ruleresults.test.jsx` (N unsorted → all N in input order via a DOM-level query, collapsed **and** expanded; hidden-not-unmounted; length-1; focusable toggle; + the same through the real detail render) | component |
| **REASON-1** | `history.reason.test.jsx` (+ `components.test.jsx` unit half) | component |
| **VIEWONLY-1** | `history.viewonly.test.jsx` (4 role values → byte-identical **list and detail**; zero input/textarea/form; only the two read-navigation buttons) + `noRoleGateImport.test.js` | component + structural |
| **EMPTY-1** | `history.empty.test.jsx` (both directions + `items.length` proven against a misleading `total`) | component |
| **ERROR-1** | `history.error.test.jsx` (table-driven; detail-needle nowhere; listError Retry → page *k*; detailError Retry → same id; **generic-404 teeth**: byte-identical structure to `internal_error`) | component + double |
| **TESTID-1** | `eslint.history.rules.test.js` (RuleTester + `isValidHistoryTestid` self-test) + `testid.test.jsx` (rows, the two region ids, per-field/state ids, slugger self-test) | lint / component |
| **NOSUPERSEDE-1** | `noSupersede.test.js` (no `'superseded'` comparison in any operand order/case; **zero** reads of `supersedes_decision_id`; status read-only; self-tests) | structural |
| **NOTS-1** | `nots.test.js` | structural |
| **STATEMACHINE-1** | `history.state.test.jsx` (7 per-state) + `history.transition.test.jsx` (consolidated, all 7 legs, Q6-A own file) | component |
| **BACKPRESERVE-1** | `history.backpreserve.test.jsx` (before/after snapshot → zero refetch; page *k* + same rows/order; the excursion is a sub-state, not a remount) | component + double |
| **COPY-1 / ADVISORY-1** | `eslint.history.rules.test.js` (reused shell lints **UNMODIFIED**; `LINT_FORBIDDEN_TERMS === FORBIDDEN_TERMS`; **every** `HISTORY_COPY` string through the **real** `findForbiddenSystemOutput`) + `components.test.jsx` | lint (+ RTL) |
| **PERF-1** | `boundedFetch.test.js` (bounded R6/R7; no real network; no `fetchDetail` in a `.map` → no N+1) | structural / observed |
| **A11Y-1** | semantic regions + `aria-readonly` + focusable row/pagination/Back/Retry/toggle + `hidden` a11y-tree removal — observed/soft, non-gating | observed / soft |
| **SCOPE-1** | `noBackendImport` + `noUiQueueImport` + `noMemoViewImport` + `noApprovalGateImport` + **`noOverrideFormImport` (NEW)** + `noRouterImport`, each + self-test | structural / governance |

Fixtures (`fixtures.js`, Q2/Q3/Q8-A): `makeHistoryDouble()` (dual-read, independently-counted, sequenceable), the page-*k* list + `emptyListBody`, `makeAuditRecord`/`overrideRecord`/`approveRecord`, the N-unsorted + length-1 `rule_results`, the five named envelopes incl. `notFoundEnvelope` and the `DETAIL_NEEDLE`, plus `renderHistory`/`openDetail`.

---

## 3. Result

- **Frontend suite (Vitest)**: **486 passed** (114 test files) — **+146 tests / +25 files**, all this unit's. **ESLint clean** (exit 0).
- **Coverage — `src/history` 100% statements / branches / functions / lines on EVERY file. QA-6 (≥90%) PASSED.** All-files: 100% stmt/func/line, 99.73% branch.
- **All five frozen trees stand at their baselines**: `src/shell`, `src/queue`, `src/memoView`, `src/approvalGate` = 100%; `src/overrideForm` = 100% stmt/func/line · 98.36% branch (its **pre-existing, already-flagged** belt-and-suspenders branch — the one sub-100% figure in the run, unchanged and not a ui-history finding). No file in any was created or edited.
- **Backend pytest suite (850 passed / 31 skipped) untouched** — zero backend files modified (mtime-verified); separate runner/tree, not re-run. `testresults.txt` records the frontend result **alongside**, not merged.

### Flagged realization notes

1. **CG-HIST-Fold-2 — the reused `advisory-vocabulary` lint also scans testid literals, and a *hyphen*-delimited "decision" IS flagged.** Fold-D established that `decision_id` passes (underscore is a word char). The corollary: a hyphen is **not** a word char, so a literal testid `history-detail-decision-id` would **fail the build**. The frozen FD §6 inventory contains no such id — it is already lint-safe — and the seam's `/decisions?page=` / `/decisions/${id}` paths are plural and clean. Asserted explicitly as a RuleTester invalid fixture + a detector self-test, so the constraint is now regression-guarded rather than tacit.
2. **CG-HIST-Fold-3 — BR-HIST-5's "decision linkage" had no pinned testid and no region prop to carry it.** `DecisionDetail` (which holds the whole `record`) renders `decision_id`/`recommendation_id` at the detail root under `history-detail-record-id` / `history-detail-recommendation-id` — token-avoiding (note 1) and convention-compliant, honoring the faithfulness clause without touching C7/C8's by-construction prop restrictions. These sit in **neither** namespace region, so the SEPARATION-1 teeth are unaffected.
3. **`testids.js` is one module beyond the plan's §1 map.** Q5-A required the dynamic segment to be "lower-cased/kebab-safe", and real `rule_id`s are upper-case/underscored (`INCOME_MIN`), so `history-detail-ruleresult-INCOME_MIN` would violate the convention. The slugger is extracted rather than duplicated across `HistoryList` and `RuleResultsRegion`; its self-test asserts the raw, unslugged id **would** violate the convention, so the helper is load-bearing, not decorative.
4. **CG-HIST-Fold-4 — `contentHash` is a prop of both C9 and C11.** `history-detail-content-hash` stays with the forensic group (C9, per FD §6); C11 renders the same value as the snapshot's own tamper-evidence marker under `history-detail-profile-hash`. Both frozen prop shapes honored; no duplicate testid.
5. **`HistoryStateView` takes `{state, error, onRetry}`, omitting the FD's `testid` prop** — following the frozen `QueueStateView`, which does exactly the same: its three container ids are state-determined, so a `testid` override would be dead-with-a-default and would cost a branch. The four 2-segment root ids (`history-view`/`-list`/`-detail`/`-pagination`) are testid-prop defaults rendered as `data-testid={testid}`, exactly as `queue-view`/`queue-pagination` are (**CG-HIST-Fold-1**).
6. **Two structural detectors needed comment-stripping.** `findRealNetwork` and `findRoleGateUsage` initially flagged **their own units' header comments** (`"a bounded single-page R6 fetch (PERF-1)"`, `` `can="read"` is deliberately NOT used ``). Since every by-construction guarantee here is documented by prose that names the construct it forbids, the scans assert the absence of **code**, not of words — the frozen `ui-approval-gate` `singleCallSite` precedent — and each now carries a self-test proving a comment does not trip it.
7. **`RuleResultsRegion` holds local disclosure state**, which the plan explicitly assigned it (§1 C10). FD §2's "only stateful component" is about **fetch/Role/router/write** state: `HistoryView` remains the sole seam holder, and no child holds any of those.

### Holds upheld
- **ui-shell (frozen) untouched** — `Panel`/`ReadOnlyRegion`/`RecommendationBadge`/`ConfidenceBadge`/`shell/copy` (incl. `COMMIT_ACTION_LABELS` + the **one** `FORBIDDEN_TERMS`)/`RoleContext` reused via import only.
- **All five sibling UI units (frozen) untouched** — fetchSeam/StructuralGuard/by-construction/testid-lint **mirrored, never imported** (REFNOTOWN incl. the **NEW `noOverrideFormImport`**).
- **No local `FORBIDDEN_TERMS` word-list** — the one source reused; `advisory-vocabulary` applied **UNMODIFIED** (Fold-D), with every `HISTORY_COPY` string verified against the **real** detector in-suite.
- **The by-construction guarantees are hard requirements**, each with its header comment: **C2** exact four-member GET-only export, no request-body builder / no `submit*` — **a write capability is structurally absent** · **C7** system-namespace-only props · **C8** human-namespace-only props · **C6** read-only composer, five sibling regions.
- **WIRE-1 R6/R7 consumed by shape only** — no real network call; the real `historyFetchSeam` wiring + the R6/R7 route implementation stay deferred to the composition root / Build & Test.
- **View-only for all roles** — no `RoleGate`, `can="read"` deliberately unused (admin not excluded); the auditor read-only distinction is server-side (`auth-rbac` SEC-4). **No write path anywhere** (INV-FAITHFUL). **No premature superseded handling** (NOSUPERSEDE-1). **No LLM. No TypeScript.** tier-B corpus run **NOT** authorized; **no other unit started**.
