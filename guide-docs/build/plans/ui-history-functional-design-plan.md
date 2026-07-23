# Functional Design — Part 1 (PLAN) · `ui-history` (U9)

**Stage**: BUILD → per-unit loop → Functional Design **Part 1 (Planning ONLY — NO FD artifact generated)** · **Date**: 2026-07-14
**Unit**: `ui-history` (U9; C5; Phase 1) — the **decision-history browse + audit-tuple detail** UI facet. **US-UI-6 · FR-UI-1 · CON-AUDIT-1 (read surface).**
**Status**: **FD Part 1 APPROVED (all six answers = A, 2026-07-14); ambiguity-check RUN → CLEAN (four folds, no STOP); FD Part 2 GENERATED.** STOPPED at the FD 2-option completion gate (1. Request Changes / 2. Continue → NFR Requirements).

This is the **last remaining P1 unit** and the **6th (final) frontend/React unit** in the working sequence. It is a **read-only view over the audit trail** that the two now-frozen write-path units (`ui-approval-gate` U7 / `ui-override-form` U8) *produce*. It is the **first UI unit to consume `decision_id`, `timestamp`, and the full `AuditRecord` shape** — none of which either write-path unit needed. Its lineage is therefore **selectively** inherited: it mirrors the **read-only seam shape** of the display units (`ui-queue` R2 list, `ui-memo-view` R4 by-id), **not** the write-body-builder / commit-gate / mandatory-reason discipline of the write-path units.

---

## §0 — DISCOVER-carryover check (CLEAN)

- **No** `guide-docs/build/ui-history/` directory.
- **No** `frontend/src/history/` (or any history) source.
- **No** `ui-history-*.md` plan file.

→ Greenfield unit. No partial artifact to reconcile. (`unit-of-work.md` reserves the `history/` frontend folder as a *planned* path, not an existing artifact.)

## §1 — Frozen contracts re-read (consumed **by value / by shape**, never edited)

| Source (frozen) | What U9 consumes | Key fact for U9 |
|---|---|---|
| `unit-of-work.md §U9` | classification | **U9 — `ui-history` (C5; Phase 1)** — "decision history browse; **links to audit tuple**." **US-UI-6. CON-AUDIT-1 (read surface). Depth: lighter (display).** Deps: `ui-shell` + `audit-store` (read surface). |
| `stories.md` **US-UI-6** (Gherkin) | acceptance | "…I see each past decision with **its recommendation, the committed outcome, and timestamp** / each entry **links to the audit tuple** / **history rows carry data-testid**." **Traces FR-UI-1, CON-AUDIT-1.** *(See the Q4 tension: R6's list item does NOT carry the system recommendation — only R7 does.)* |
| `user-journey.md` (auditor path) | second consumer | Auditor **browses history read-only**, **opens a past decision read-only — "cannot edit" (SEC-4 / US-PLAT-2)**, views `rulebook_version` / `rule_results` / `memo_hash`. **Replay is a rules-engine / CLI concern — NO WIRE-1 UI route — OUT of U9 scope.** |
| `WIRE-1 §3` **R6** | the list wire | `GET /decisions?page=&size=` → **list wrapper** `{ "items": DecisionSummary[], "page": { "page":int, "size":int, "total":int } }` (A4 offset/limit, **1-based** `page`). **Auth: authenticated — ANY role** (no `RBAC_*` restriction). |
| `WIRE-1 §3` **R7** | the detail wire | `GET /decisions/{decision_id}` → **`AuditRecord`** (full). **Auth: authenticated — ANY role.** Single-resource-**by-id** shape (mirrors R3/R4). 404 `not_found` if no such decision. |
| `WIRE-1 §5` **DecisionSummary** (R6 item) | list projection | `{ decision_id, application_id, recommendation_id, action:<CommitAction>, timestamp:ISO-8601 }`. **Carries the HUMAN `action` (approve/override) + timestamp — but NO system `recommendation`/`confidence`.** |
| `audit_store/record_schema.py` **`AuditRecord`** (R7) | the detail entity | `{ decision_id, application_id, recommendation_id, audit_tuple, applicant_profile_snapshot, committed_decision, status, supersedes_decision_id\|null }`. Frozen; `frozen=True` + `extra="forbid"`. |
| ↳ `AuditTuple` | forensic/replay 6-tuple | `{ rulebook_version, rule_results:RuleResultReport, timestamp, model_version, memo_hash, engine_version }`. **The system `recommendation`/`confidence` live INSIDE `rule_results`** (`RuleResultReport.recommendation` / `.confidence`). |
| ↳ `CommittedDecision` | the human linkage | `{ recommendation_id, underwriter_id, action:CommitAction(approve/override), reason\|null }`. The **only** place "decision" is the correct word (the human's committed action). |
| ↳ `ApplicantProfileSnapshot` | persisted input | `{ application_id, profile:ApplicantProfile, content_hash }` — the verbatim original input + tamper-evidence hash. |
| ↳ `status` / `supersedes_decision_id` | OOS-7 seam | `status ∈ {active, superseded}` — **write-once `active` in Phase 1/2**; `supersedes_decision_id` **always `null`** in Phase 1/2. |
| `shell/copy/index.js` | display labels + advisory vocabulary | **`RECOMMENDATION_LABELS`** (Approve/Refer/**Decline-Recommend** — never a bare "DECLINE") and **`COMMIT_ACTION_LABELS`** (`approve→Approve`, `override→Override`) are **ALREADY frozen — a DISTINCT namespace**. Both reused, none added. `ADVISORY_VOCABULARY.required = 'recommendation'`. |
| `shell/components/RoleGate.jsx` | cosmetic capability shape | `COSMETIC_CAPABILITIES`: underwriter `{act,read}` · auditor `{act:false, read:true}` · **admin `{act:false, read:false}`**. Cosmetic only (SEC-4 / BR-UI-4); server is the real gate. **NB: `can="read"` would cosmetically HIDE history from `admin` — a tension with R6/R7 "authenticated ANY role" (see Q3).** |
| `queue/fetchSeam.js` (U5, frozen) | read-only **list** seam shape, mirror-not-import | `createQueueFetch(transport) → fetchSeam(page,size)`; `buildQueueRequest(page,size)`; `normalizeError` → `{error:{code,message,detail}}`; `DEFAULT_PAGE_SIZE=20`; **PERF-1 bounded single-page (never an all-rows path)**. **No write-body builder** — this is the pattern U9 mirrors. |
| `memoView/memoFetchSeam.js` (U6, frozen) | read-only **by-id** seam shape | R4 `GET /applications/{id}/memo` single-resource-by-id — the shape U9's R7 detail read mirrors. |
| `queue/QueueView.jsx` + `noRoleGateImport.test.js` (U5, frozen) | **VIEWONLY-1** precedent | ui-queue "reads NO Role, composes NO RoleGate; render IDENTICAL across roles" — the *view-only-for-everyone* precedent for a pure-read display unit, enforced by a structural `noRoleGateImport` guard. |

**Domain guardrails (underwriting-rules skill) binding on U9**:
1. **Advisory-only namespace (constraint 1)** — the system output is a **recommendation** (`RECOMMENDATION_LABELS`, 3-enum incl. `Decline-Recommend`); "decision"/`action` is reserved for the **human's** committed act (`COMMIT_ACTION_LABELS` approve/override). U9 is the **first unit that renders BOTH together** → the namespace-distinctness invariant is load-bearing here (Q4).
2. **Human-in-the-loop / no new outcome path** — U9 has **NO write surface**: no commit, no gate, no mandatory-reason, no `submit*` builder. It only reads a record the human already committed.
3. **Faithful, immutable render (SEC-4 "cannot edit" + full-explainability)** — the audit tuple is a **forensic/immutable** record; the view must render it faithfully and **never imply it can be altered** (no edit affordance, no mutation seam). U9 does **not** replay/re-evaluate (no WIRE-1 route; backend/CLI concern).
4. No LLM; no TypeScript.

## §2 — Depth recommendation — **LIGHTER (display)** with two named display-side invariants (confirm at Q1)

`unit-of-work.md §U9` classifies U9 **"lighter (display)"** — a **read surface** over CON-AUDIT-1, in shape closer to `ui-queue`/`ui-memo-view` than to the write-path units. There is **no commit, no gate, no mandatory-reason, no RBAC-restricted route** (R6/R7 are authenticated-any-role), so the comprehensive write-path rigor of U7/U8 is **not** warranted.

**But two display-side invariants keep this from being a zero-invariant list** (and argue for a StructuralGuard + targeted teeth, not for full comprehensive treatment):
- **INV-FAITHFUL** — the audit tuple is forensic/immutable (SEC-4 "cannot edit"): the view must be **strictly read-only, with NO edit affordance and NO write/mutation seam**, and never imply the record could be altered. Verified structurally (no `submit*`/commit call site, no write-body builder, no RoleGate `act`) — the read-surface mirror of the write units' single-call-site guard.
- **INV-NAMESPACE** — the system **recommendation** and the human **action** must render as **distinct namespaces** (constraint 1), reusing the frozen label maps; the human `override` must **never** render as the system `DECLINE-RECOMMEND`.

**Recommendation: LIGHTER (display)** — classification-forced — **plus** the two invariants above verified by a StructuralGuard and focused teeth (not a comprehensive NFR sweep). Confirm at **Q1**; if you judge the forensic-faithfulness invariant deserves heavier (comprehensive) treatment, that is your call (Q1-B).

## §3 — Proposed approach (CONTINGENT on the answers below)

A self-contained `frontend/src/history/` unit mirroring the **read-only** display-unit structure (mirror-not-import; the siblings are frozen), with a **master-detail (list ↔ detail)** shape that is genuinely new to this unit:

```
history/
  copy.js                         # history-local strings, advisory-clean (reuses shell RECOMMENDATION_LABELS + COMMIT_ACTION_LABELS)
  historyFetchSeam.js             # read-only seam: createHistoryFetch(transport) -> { fetchList(page,size), fetchDetail(decision_id) }  [Q2]
                                  #   buildHistoryListRequest(page,size) [R6] + buildHistoryDetailRequest(decision_id) [R7]; normalizeError; DEFAULT_PAGE_SIZE
                                  #   NO write-body builder (no buildCommitRequest analog) — INV-FAITHFUL
  HistoryView.jsx                 # sole stateful orchestrator; owns list<->detail state + both reads [Q2]; reads NO Role (VIEWONLY-1) [Q3]
  components/
    HistoryList.jsx               # R6 list rows: human action + timestamp + testid per row [Q4]; onSelect(decision_id) -> detail
    HistoryStateView.jsx          # loading / empty / errorList / errorDetail / not_found(404) envelope render (mirror ERROR-1)
    DecisionDetail.jsx            # R7 AuditRecord render: system recommendation + human action side-by-side (namespace-distinct) [Q4]; forensic fields [Q6]; read-only, no edit affordance [INV-FAITHFUL]
```

The precise seam shape and where the detail read lives (Q2), RoleGate applicability (Q3), the dual system-recommendation-vs-human-action display and the **R6-omits-system-recommendation tension** (Q4), pagination/filtering (Q5), and the detail-view rendering scope + faithfulness invariant (Q6) are **open** — worked through below rather than assumed transferable.

**Realization notes (not questions):** every history row + interactive element carries a `data-testid` (US-UI-6 / US-UI-7; a `history-*` testid family + convention lint, realized at NFR-Design/Code-Gen as the siblings did); advisory-vocabulary lint reused UNMODIFIED.

---

## §4 — Open design questions (answer each `[Answer]:` tag with a letter)

### Q1 — Depth
Confirm the depth for `ui-history`.
- **A. Lighter (display), plus INV-FAITHFUL + INV-NAMESPACE verified by a StructuralGuard + focused teeth** *(Recommended)* — matches the `unit-of-work.md §U9` "lighter (display)" classification; read-only surface, no write path; the two named invariants get structural/targeted verification, not a comprehensive NFR sweep.
- **B. Comprehensive** — treat the forensic-faithfulness invariant as invariant-bearing enough to warrant U7/U8-level rigor. *(Available if you want the immutability/faithful-render guarantee held to the higher bar; heavier than the classification asks.)*
- **C. Minimal** — pure display, no structural invariant verification. *(Rejected — under-serves INV-FAITHFUL / INV-NAMESPACE, which are real for an audit surface.)*

`[Answer]:` A — lighter (display), plus INV-FAITHFUL + INV-NAMESPACE verified by a StructuralGuard + focused teeth; matches `unit-of-work.md`'s classification, no comprehensive sweep warranted for a read-only, no-write-path surface.

---

### Q2 — List + detail structure: does U9 own the R7 detail read, and is it one unit with two states or emit-upward?
US-UI-6 requires both a browse list (R6) and "each entry **links to the audit tuple**" (R7 detail). Prior units differ: `ui-queue` emitted `onSelect` **upward** (SELECT-1, no router — the selection crossed into a *different* unit, `ui-memo-view`); `ui-approval-gate`/`ui-memo-view` did their **own** single-resource read. For U9 the detail (the audit tuple) belongs to **history itself**, not another unit — so this is a genuinely **new in-unit master-detail** pattern, not the cross-unit hand-off the queue used.

- **A. One self-contained `HistoryView` with list↔detail state; U9 owns BOTH reads (R6 list + R7 detail-by-id via its own `historyFetchSeam`)** *(Recommended)*.
  `HistoryView` owns a small machine (`listLoading → list/errorList → detailLoading → detail/errorDetail/notFound → back`). Selecting a row fetches R7 by `decision_id` (the single-resource-by-id shape `ui-memo-view`'s R4 seam already established, mirror-not-import). No router dependency; a future composition root can still mount `HistoryView` wholesale. The detail is history's own audit tuple, so keeping it in-unit is correct (unlike queue→memo, which crossed units).
- **B. List only; emit `onSelect(decision_id)` upward (mirror `ui-queue` SELECT-1); detail owned by a parent/composition root.** Defers the R7 read to an undesigned router/shell and splits one cohesive audit-tuple surface across a boundary. *(Viable but adds an undesigned dependency now and fragments US-UI-6's "entry links to the audit tuple" across units.)*
- **C. Two separately-mounted units (a list unit + a detail unit).** Over-decomposition of one "lighter (display)" unit. *(Rejected.)*

`[Answer]:` A — one self-contained `HistoryView` with list↔detail state; U9 owns BOTH reads (R6 list + R7 detail-by-id via its own `historyFetchSeam`). The audit tuple belongs to history itself, not another unit, so keeping the detail in-unit is correct — unlike queue→memo, which crossed units.

---

### Q3 — How RoleGate applies here, if at all
R6/R7 are **authenticated — ANY role** (no `RBAC_*` restriction). The auditor is a first-class read consumer (auditor path); `admin` has **no UI journey** (operates via CLI). `ui-queue` set the **VIEWONLY-1** precedent: pure-read display units read no Role and compose no RoleGate → render identical across roles. History has **no act-affordance to gate** (it is pure read).

- **A. No RoleGate — history renders identically for all authenticated roles (mirror `ui-queue` VIEWONLY-1), enforced by a `noRoleGateImport` structural guard** *(Recommended)*.
  Rationale: (1) RoleGate gates **act**-affordances; U9 has none, so there is nothing to gate; (2) matches WIRE-1 R6/R7 "authenticated ANY role"; (3) the auditor's "read-only distinction" is meaningful on units that *have* write affordances (U7/U8), not on a pure-read surface; (4) **`RoleGate can="read"` would cosmetically HIDE history from `admin` (`read:false`)** — a UI/contract divergence from R6/R7 any-authenticated, and admin has no UI journey anyway. Cleanest and contract-faithful.
- **B. Wrap in `RoleGate can="read"`.** Surfaces the cosmetic read distinction — **but hides history from `admin` (`read:false`), diverging from the frozen R6/R7 "authenticated ANY role"** and introducing a UI-vs-contract mismatch. *(Rejected unless you specifically want admin cosmetically excluded from the history UI — a real product call about the frozen contract, so it must be your explicit decision, not my improvisation.)*
- **C. Differentiated per-role rendering (auditor sees a different/emphasized read-only history vs underwriter).** No requirement calls for divergent history rendering; the record is identical for both. *(Rejected — speculative; the read-only-ness is universal for this surface.)*

`[Answer]:` A — no RoleGate; history renders identically for all authenticated roles (mirror `ui-queue`'s VIEWONLY-1), enforced by a `noRoleGateImport` structural guard. There is no act-affordance to gate, R6/R7 are authenticated-any-role, and `can="read"` would cosmetically exclude admin — a real UI/contract divergence not chosen.

---

### Q4 — Displaying the system **recommendation** and the human **action** together — namespace-distinctness **and** a frozen-contract data tension
U9 is the **first unit that must show BOTH** the system recommendation (advisory, `RECOMMENDATION_LABELS`: Approve/Refer/**Decline-Recommend**) and the human action (`COMMIT_ACTION_LABELS`: Approve/Override + reason). The frozen labels keep them **namespace-distinct** — the human `override` must **never** render as the system `DECLINE-RECOMMEND`. **But there is a real data tension**: US-UI-6's Gherkin says each **list** row shows "its **recommendation**, the committed **outcome**, and timestamp" — yet the frozen **R6 `DecisionSummary` carries only the human `action` + `timestamp`, NOT the system `recommendation`** (which lives only inside **R7**'s `AuditRecord.audit_tuple.rule_results.recommendation`). This must be resolved without editing the frozen R6 shape and without improvising.

- **A. List shows what R6 provides (human `action` outcome + timestamp + ids, namespace-distinct labels); the system `recommendation` appears in the R7 DETAIL the row "links to"** *(Recommended)*.
  Reads US-UI-6's "its recommendation" as satisfied at the **linked audit-tuple detail** (R7), honoring the frozen R6 shape (no widening) and the story's own "each entry links to the audit tuple" clause. In the **detail**, both values render **side by side under distinct labels** (`RECOMMENDATION_LABELS[report.recommendation]` = system, advisory; `COMMIT_ACTION_LABELS[committed_decision.action]` = human, + reason when override) with explicit "System recommendation" vs "Underwriter's decision" framing — the INV-NAMESPACE realization. No frozen contract touched.
- **B. Enrich each list row with the system recommendation by fetching R7 per row.** N+1 reads over a page — violates PERF-1 bounded-single-page and the read-only-list shape. *(Rejected.)*
- **C. Request widening frozen R6 `DecisionSummary` to include `recommendation`/`confidence`.** Would make the list self-sufficient for US-UI-6's literal wording — **but WIRE-1 is FROZEN and this is a cross-unit contract change** affecting the backend and the pinned api-contract. *(Not an improvisation I will make — if you want the system recommendation in each list row, this is a deliberate frozen-contract change and must be your explicit call; otherwise A.)*

`[Answer]:` A — the list shows what R6 actually provides (human `action` outcome + timestamp + ids, namespace-distinct labels); the system recommendation appears in the R7 detail the row links to, honoring the frozen R6 shape without widening it. In the detail, both values render side by side under distinct labels with explicit "System recommendation" vs "Underwriter's decision" framing. **Q4-C (widening R6) is explicitly DECLINED** — not needed, since A satisfies US-UI-6 via the linked detail.

---

### Q5 — Pagination (and whether filtering applies)
R6 is `GET /decisions?page=&size=` — the **same offset/limit list wrapper** `ui-queue`'s R2 used (`{items, page:{page,size,total}}`, 1-based, `DEFAULT_PAGE_SIZE`). The frozen R6 has **no filter params** (no date/underwriter/outcome).

- **A. Mirror `ui-queue`'s offset/limit pagination exactly; NO filtering in Phase 1** *(Recommended)*.
  `buildHistoryListRequest(page,size)` = queue's PERF-1 bounded single-page shape; page controls (prev/next or page-number) over `page.total`. **No filtering**, because R6 exposes no filter params and client-side filtering would filter only the *current page* (a misleading partial view of full history). Consistent with the queue; contract-faithful.
- **B. Add client-side filtering (by date / underwriter / outcome) over the fetched page.** Misleading — filters one page, not the full history; implies a completeness the data doesn't have. *(Rejected.)*
- **C. Request R6 widening with server-side filter params (date/underwriter/outcome).** A plausible real product need for history at scale — **but a frozen-contract change** (new R6 query params, backend work). *(Deferred: name it as a Phase-2 seam, do NOT author it now; if you want it in Phase 1 that is your explicit frozen-contract call.)*

`[Answer]:` A — mirror `ui-queue`'s offset/limit pagination exactly; no filtering in Phase 1, since R6 has no filter params and client-side filtering would misleadingly imply completeness over a single page. **Q5-C (server-side filter params) is explicitly DEFERRED as a named Phase-2 seam**, not authored now.

---

### Q6 — Detail-view rendering scope + the faithful/immutable-render invariant
The R7 `AuditRecord` is deeply nested (full `rule_results` `RuleResultReport`; `applicant_profile_snapshot.profile` = the whole `ApplicantProfile`; forensic `rulebook_version`/`model_version`/`engine_version`/`memo_hash`/`content_hash`; `status`; `supersedes_decision_id`). How much does the detail render — and how is INV-FAITHFUL held?

- **A. Render the decision linkage + the forensic/replay tuple faithfully, present `rule_results` at a readable (summarized/expandable) level, render the profile snapshot read-only — ALL strictly read-only, NO edit affordance, NO implied mutability; do NOT replay** *(Recommended)*.
  Detail shows: system `recommendation`/`confidence` (from `rule_results`), the human `action`+`reason`+`underwriter_id`, `timestamp`, and the forensic fields the auditor path names (`rulebook_version`, `rule_results`, `memo_hash`) plus `model_version`/`engine_version`/`content_hash`/`status`. `rule_results` rendered at a summary-with-detail level (full explainability preserved, faithful to the report). The profile snapshot renders read-only (its demographic fields are the *persisted forensic input*, **not** a feature vector — displaying them is not a bias-swap concern). **No edit control, no mutation seam, no "supersede" affordance** (`status` is display-only; `supersedes_decision_id` is always `null` in Phase 1/2). **No replay** (no WIRE-1 route; backend/CLI).
- **B. Minimal: DecisionSummary-level fields + raw hash strings only; don't render nested `rule_results`/profile.** Under-serves US-UI-6 "links to the audit tuple" and the auditor path's explicit `rule_results`/`memo_hash` need. *(Rejected.)*
- **C. Re-render the full DecisionMemo narrative in the detail.** The `AuditRecord` carries only `memo_hash`, **not** the memo body (no `DecisionMemo` embedded, no route returns it) — the data isn't present, so this can't be honored without a non-existent route. *(Rejected — data not available.)*

`[Answer]:` A — render the decision linkage + the forensic/replay tuple faithfully, `rule_results` at a readable summarized/expandable level, the profile snapshot read-only — all strictly read-only, no edit affordance, no implied mutability, no replay (no route exists for it).

---

## §4.5 — Mandatory ambiguity-check (RUN 2026-07-14 — CLEAN, no STOP; four clarity-folds, the fourth surfaced while grounding)

Ran against the six answers (all **A**) + the frozen contracts re-read in §1 (WIRE-1 R6/R7 + list wrapper; `DecisionSummary`; `AuditRecord`/`AuditTuple`/`CommittedDecision`/`ApplicantProfileSnapshot`/`status`/`supersedes_decision_id`; `shell/copy` frozen label maps; `RoleGate` `COSMETIC_CAPABILITIES`; the queue/memoView read-only seam shapes + queue `QueueView.jsx` state discipline — all re-read on disk). The three user-flagged checks + the general sweep:

**HIST-Fold-1 (check i — page-position preservation; RESOLVED by the approved answer + the frozen queue precedent, no gap).** Q2-A's single `HistoryView` holds the list `page` in **orchestrator state**. Grounded in the frozen `queue/QueueView.jsx`: the queue keeps `page` in component state and its RETRY-1 / Fold-B is explicitly **position-preserving** (retry/return re-fetches the **last-requested** page, never resets to page 1 — `load(page)`, `setPage(targetPage)`). By the same discipline, HistoryView's list `page` **survives the detail excursion** — detail is a *sub-state*, not a remount — so **"back to list" returns to the SAME page position**, not page 1. Determined by the approved Q2-A ("one component, two states") + the established queue precedent; a **clarity-fold, not a gap**. **Binding on the FD:** the list page index is orchestrator state, preserved across `list → detail → back`.

**HIST-Fold-2 (check ii — `rule_results` rendering is shape-only in FD, concrete interaction DEFERRED to NFR-Design, with a faithfulness constraint; no gap).** Q6-A's "readable summarized/expandable level" does **not** require pinning a concrete widget/interaction now. FD (technology-agnostic business logic) pins only the **shape + the invariant**: `rule_results` is a list of per-rule entries rendered **faithfully with NO lossy omission** — INV-FAITHFUL forbids *dropping* entries, so "summarized" must mean **progressive disclosure (expand/collapse), never truncation-that-hides-data**. The concrete interaction pattern (the expand affordance, any windowing) is an **NFR-Design/Code-Gen realization** — the same FD↔NFR boundary the siblings observed. **Binding on the FD:** state the faithfulness rule + the list shape; defer the widget. A **clarity-fold, not a gap** (and explicitly NOT a place to invent a truncation strategy that would violate faithfulness).

**HIST-Fold-3 (check iii — 404 is generic; NO premature superseded/null-`supersedes` handling; a guardrail confirmation, no gap).** The R7 **404** (`not_found` — invalid/non-existent `decision_id`) is surfaced by the **generic `errorDetail` / not-found state** (mirror `ERROR-1`) — **no special-casing** distinct from any other detail-fetch failure. Crucially, **no handling is designed for states that cannot occur in Phase 1/2**: `status` renders **display-only** (write-once `active`); `supersedes_decision_id` is **always `null`** in Phase 1/2, so the FD designs **no** "superseded" branch, **no** dereference/link of `supersedes_decision_id`, and **no** supersede affordance — that is the OOS-7 / Phase-3 seam, **named-not-designed**. Designing for the null/superseded case now would be improvising for an unreachable state — deliberately NOT done (this is itself an INV-FAITHFUL/no-premature-abstraction guardrail). A **clarity-fold** confirming the correct non-action.

**HIST-Fold-4 (advisory-lint vs the human "decision" namespace — a genuinely NEW finding surfaced while grounding, resolved at FD level, mechanics deferred — no STOP).** The frozen `shell/copy/forbiddenTerms.js` `FORBIDDEN_TERMS.systemOutput` = `['DECLINE', 'decision', 'approved', 'declined']`, and its own comment scopes them "forbidden **as SYSTEM output**" — "`decision`" is explicitly "**reserved for the HUMAN underwriter's committed action, never system output**." The reused `advisory-vocabulary` lint is a **blanket lexical scan** over a unit's static copy (per the sibling `BR-MEMO-2` realization) — which was safe for `ui-memo-view` **only because that unit has no human-namespace copy** (everything it renders is system output, so blanket == system-output-scoped). **`ui-history` is the FIRST unit that legitimately renders the human `CommittedDecision` namespace**, where the word "decision" is the **CON-BR4-correct** term — and the user's approved **Q4-A** frames the human region as **"Underwriter's decision"**. A naive blanket reuse of the lexical lint would false-positive on that CON-BR4-correct heading. **Resolution (no STOP — grounded in the lint's own stated intent + the approved answers):** the FD records the rule at the **intent level** (BR-HIST-2) — **system-output copy** must avoid the verdict tokens; the **human-committed region** is namespace-distinct and legitimately carries committed-action/"decision" language — and pins that `ui-history`'s advisory conformance must be **system-output-scoped**, realized WITHOUT modifying frozen `shell` (either a system-output-scoped lint block for `src/history/**`, or human-region wording that avoids the bare lexical token while staying namespace-distinct, e.g. "Underwriter's committed action"). The **exact lint scoping / final heading wording** is an **NFR-Design/Code-Gen realization** (the same class of decision the siblings deferred), flagged here for the reviewer at the gate. This is surfaced transparently, not silently picked.

**General sweep:** advisory-copy cleanliness — history strings reuse the frozen `RECOMMENDATION_LABELS` / `COMMIT_ACTION_LABELS` (never inline a display string), and the detail's explicit "System recommendation" vs human-committed-action framing keeps the two namespaces distinct (the human `override` never renders as the system `DECLINE-RECOMMEND`; see HIST-Fold-4 for the "decision"-token nuance) — realized in FD Part 2 `copy.js`. The `data-testid` `history-*` family + convention lint = an NFR/Code-Gen realization, consistent with the siblings. No other under-specified point. **→ CLEAN. Proceeding to FD Part 2.**

## §5 — What FD Part 2 will produce (once these are answered & approved)
FD artifacts under `guide-docs/build/ui-history/functional-design/` (mirroring the sibling FD set):
- `domain-entities.md` — the R6 `DecisionSummary` list item + `page` wrapper, the R7 `AuditRecord` shape (embedding `audit_tuple`/`committed_decision`/`applicant_profile_snapshot`), the list↔detail state machine (per Q2), and the by-construction component/prop inventory (read-only, no write seam).
- `business-rules.md` — `BR-HIST-*`: INV-FAITHFUL (read-only, no edit affordance, no mutation seam), INV-NAMESPACE (system recommendation vs human action, distinct frozen labels; override never renders as Decline-Recommend), pagination/no-filter (per Q5), RoleGate applicability (per Q3), 404/empty/error surfacing (mirror ERROR-1), testid coverage (US-UI-6/US-UI-7).
- `business-logic-model.md` — the list → select → detail read/render flow + **validated** Mermaid (validated per `visual-and-syntax-standards.md` before write) + consumer/dependency map + FD↔later-stage boundary + invariant self-check.
- `frontend-components.md` — component hierarchy (`HistoryView` / `HistoryList` / `DecisionDetail` / `HistoryStateView`), props/state, the list↔detail interaction flow, and the R6/R7 integration points (which read each component consumes).

## §6 — Holds (this stage)
- **NO FD artifact generated** — plan + questions only.
- **No frozen artifact touched**: WIRE-1 · `ui-shell` · `ui-queue` · `ui-memo-view` · `ui-approval-gate` · `ui-override-form` all consumed **by value/shape**, none edited.
- **No write surface introduced** — U9 is a pure read consumer of the audit trail (INV-FAITHFUL).
- **No LLM; no TypeScript**; tier-B corpus run **NOT authorized**; **no other unit started**.

---

**GATE — Functional Design Part 1 (Plan).** Answer **Q1–Q6** above (letter per `[Answer]:` tag; add notes if you want a variant). On your answers I will run the mandatory ambiguity-check, embed the full Q&A back into this plan file, and only then generate the FD Part 2 artifacts. **No FD artifact and no code will be written until you approve.** Note the two frozen-contract decisions parked for your explicit call: **Q4-C** (widen R6 to carry the system recommendation per row) and **Q5-C** (add R6 filter params) — both left as *your* decisions, not improvised.
