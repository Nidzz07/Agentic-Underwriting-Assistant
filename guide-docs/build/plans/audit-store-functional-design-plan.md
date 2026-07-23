# Functional Design Plan — `audit-store` (EPIC-6 / U12)

**Phase / Stage**: BUILD → Functional Design (per-unit, plan-then-generate)
**Cluster**: Deterministic-core cluster-FD-first — **unit 3 of 4** (`intake`+`document-sanitizer` ✅,
`rules-engine` ✅ approved 2026-07-03; **`audit-store` ← here**; then `memo-agent-core`; **all four
FDs designed before any Code-Gen**).
**Unit covered**: U12 `audit-store` (EPIC-6, Phase 1) — the **decision-commit + audit + replay
backend boundary**.
**Date**: 2026-07-03
**Status**: **Plan — awaiting `[Answer]:` tags.** No FD artifacts generated yet. Stop after this plan.

This plan follows `.project-guide-rule-details/build/functional-design.md`. It is the **altitude
drop to INTERNALS**: the field-level `AuditRecord` (the CON-AUDIT-1 **6-tuple** + the commit
linkage + the OOS-7 seam), the `DecisionCommitService` write-gate logic (CON-BR4), and the
`ReplayService` orchestration (replay-as-detection). **The contract *shapes* are frozen at
Application Design (`component-methods.md`) — Functional Design fills the internals, it does NOT
re-open the contract shape.**

---

## 1. Unit context (analyzed — Step 1) ✅

### 1.1 `audit-store` (U12, EPIC-6, Phase 1)
- **Purpose** (`unit-of-work.md §3` U12): the **decision-write + audit + replay backend boundary** —
  **not passive storage**. Owns three services, single-sourced here:
  - **`DecisionCommitService`** — the **CON-BR4 write-gate**: rejects any commit lacking
    `underwriter_id` + `reason`; re-checks authz (defense-in-depth, SEC-4).
  - **`AuditService`** — persists the CON-AUDIT-1 **6-tuple** on every **committed decision**
    (append-only); backs the read-only audit-trail surface (SEC-5, US-PLAT-2).
  - **`ReplayService`** — re-evaluates any past decision against its **original** `rulebook_version`
    and draws the **match/mismatch branch** (replay-as-detection, G4 / OOS-8).
- **Stories**: US-PLAT-2 (read-only audit-trail + decision history, SEC-4/SEC-5/CON-AUDIT-1),
  US-PLAT-8 (persist full audit tuple + replay, CON-AUDIT-1/SEC-5/DATA-5).
- **Owned invariants** (`unit-of-work.md §5`): **CON-AUDIT-1** (6-tuple + replay — single source),
  **CON-BR4** (decision-write enforcement — **single backend source**; UI facets U7/U8 consume it),
  **SEC-5** (audit logging). Read-only-role segregation for the auditor = **SEC-4**.
- **Depends on**: `database` (U15 — shared PostgreSQL, **no SQLite**, DATA-5).
- **Depth**: **comprehensive** (audit tuple, replay-as-detection, write-gate — invariant-bearing).

### 1.2 Frozen contract shapes (from `component-methods.md` — internals only below)
- `DecisionCommitService.commit(recommendation_id, underwriter_id, action, reason=None) ->
  CommittedDecision` — the human-gate backend boundary; **rejects any write lacking `underwriter_id`
  + `reason`** (CON-BR4).
- `AuditStore.persist(audit_tuple: AuditTuple) -> None` — persist the full audit tuple on every
  committed decision.
- `ReplayService.replay(decision_id) -> RuleResultReport` — re-evaluate a past decision against its
  **original** `rulebook_version`.
- `AuditTuple` = **6-tuple** `{rulebook_version, rule_results, timestamp, model_version, memo_hash,
  engine_version}` (`engine_version` = git SHA of the rules engine — code-drift forensic field).
- `CommittedDecision` = the human-committed outcome: links `recommendation` + `underwriter_id` +
  `action` + `reason`. **Reserved OOS-7 seam** (contract-named, schema designed here): `decision_id`,
  `status` (`active`/`superseded`), nullable `supersedes_decision_id`. **Phase 1/2 writes
  `status=active` only.**

### 1.3 Carry-forward into this FD (from the user + prior cluster units — held, not re-opened)
- **`RuleResultReport` field-for-field** (rules-engine FD, approved): what `audit-store` persists as
  `rule_results` must **match it field-for-field** — all per-rule rows (tri-state `status`,
  `actual_value`, `operator`, `threshold`, `outcome_tier`, `message`), `recommendation`,
  deterministic `confidence`, `rulebook_version` + `content_hash` + `engine_version`,
  `decline_reasons`/`refer_reasons`.
- **The 6-tuple** is the field-level persistence design owned here; `engine_version` is the
  code-drift forensic field (reviewer feedback).
- **Replay boundary (rules-engine Q11)**: `ReplayService` owns replay **orchestration** (loads the
  original `rulebook_version` + original profile, **calls rules-engine's pure `evaluate()`** to
  re-derive, compares to recorded `rule_results`); **`rules-engine` owns `evaluate()`**. Replay is
  **DETECTION** — it draws the match/mismatch branch (G4); mismatch = **blocking reproducibility
  failure**; incident-handling workflow is Phase 3 (OOS-8).
- **CON-BR4**: `DecisionCommitService` is the backend write-gate single-sourced **inside**
  `audit-store` — the decision-commit-and-audit boundary, not passive storage; rejects any commit
  lacking `underwriter_id` + `reason`.
- **CON-AUDIT-1**: the audit tuple is persisted on every **COMMITTED DECISION** (not every
  recommendation — the corrected wording); **append-only**.
- **OOS-7 amendment seam**: `decision_id` / `status` (`active`/`superseded`) /
  `supersedes_decision_id` reserved now, `status=active` only in Phase 1/2; **field-level schema is
  designed HERE at FD** (per requirements.md OOS-7 / §12). *(The OOS-7 README/case-study
  documentation commitment stays a closed settled item — this FD designs the seam **fields**, not
  the docs.)*

### 1.4 Binding constraints held through this FD (guardrails skill)
- **CON-BR4**: no committed decision without explicit underwriter action + reason; the write-path
  rejects a record lacking `underwriter_id` + `reason` (backend, not UI copy). Defense-in-depth
  authz re-check (SEC-4) inside the service.
- **CON-AUDIT-1**: every committed decision persists the full **6-tuple**; any past decision is
  **replayable** against its **original** `rulebook_version`; **append-only** (never mutate).
- **CON-DET-1 boundary**: replay re-evaluation is deterministic (calls the pure `evaluate()`); the
  `timestamp` is **audit metadata captured at commit** — it is **not** in the evaluation path and is
  **never** part of the replay comparison (only `rule_results` are compared).
- **Advisory-only naming**: the persisted human action is a **decision** (the one place "decision"
  is correct — the human's committed choice); the system's output remains a **recommendation**.
- **SEC-4 / SEC-5**: auditor read-only (read-only DB role); audit logging underpins the
  auditability deliverable.
- **DATA-5**: PostgreSQL only (no SQLite — dialect-drift guard).

### 1.5 Cluster-FD-first position (unit 3 of 4)
- **Consumes** `rules-engine`'s `RuleResultReport` (persist `rule_results`) — the field-for-field
  match is why the cluster FDs are designed together.
- **Reserves** `memo_hash` + `model_version` (produced by `memo-agent-core`, **unit 4**) at
  contract altitude — the memo's internal schema is unit 4's concern; the **hash + model_version
  fields audit-store persists** are named here so unit 4's FD lands against a stable audit contract.
- The `AuditRecord` field-level contract must be **stable for the cluster** before any Code-Gen.

---

## 2. Functional Design execution plan (checkboxes — Step 2)

Artifacts to be generated **after** answers are collected and ambiguity-checked:
`guide-docs/build/audit-store/functional-design/` → `domain-entities.md`, `business-rules.md`,
`business-logic-model.md`. (No `frontend-components.md` — backend unit; the C5 read surfaces
US-PLAT-2 are their own UI units.)

- [x] **P1. Analyze unit context** (§1 above — done).
- [x] **P2. Collect `[Answer]:` tags** (§3); run the mandatory ambiguity-check (§4 of the rule
  file); raise a clarification file only if any answer is vague/combined/contradictory. **DONE
  2026-07-03 — all 12 answered; ambiguity-check CLEAN (no clarification file needed). 5
  design-elaboration resolutions surfaced for generation (see audit 2026-07-03T13:05 entry) — incl.
  the confirmed GAP: the frozen AuditTuple 6-tuple does NOT persist the original ApplicantProfile, so
  the AuditRecord (superset entity) must persist it for self-contained replay (Q7). Awaiting explicit
  go to generate.**
- [x] **P3. `domain-entities.md`** — the field-by-field **`AuditRecord`** (the CON-AUDIT-1 6-tuple:
  `rulebook_version`, `rule_results` [= `RuleResultReport` field-for-field], `timestamp`,
  `model_version`, `memo_hash`, `engine_version`) + the **commit linkage** (`recommendation_id`,
  `underwriter_id`, `action`, `reason`) + the **OOS-7 seam** (`decision_id`, `status`,
  `supersedes_decision_id`); `CommittedDecision`; the read-only audit-trail view shape. Entity/schema
  Mermaid (validated per visual-and-syntax-standards, text alternative).
- [x] **P4. `business-rules.md`** — the **`DecisionCommitService` write-gate rules** (CON-BR4:
  reject missing `underwriter_id`/`reason`; the reason-mandatory semantics; authz re-check);
  **append-only** enforcement; the **persisted-on-committed-decision** rule; **replay
  match/mismatch** rules (field-for-field comparison; blocking-failure on mismatch; forensic
  distinction via `engine_version`/`content_hash`); the OOS-7 `status=active`-only Phase-1/2 rule.
  Every rule states its condition explicitly.
- [x] **P5. `business-logic-model.md`** — the **commit → persist** pipeline (human gate → CON-BR4
  gate → append-only 6-tuple write); the **replay orchestration** logic and its **ownership boundary
  with `rules-engine` `evaluate()`** (replay-as-detection; memo NOT re-drafted; `memo_hash`
  integrity check); the append-only + OOS-7 supersession model (reserved, not built); data-flow
  Mermaid (validated + text alternative); invariant self-check table (as intake's/rules-engine's).
- [x] **P6. Cross-consumer contract check** — verify the `AuditRecord` covers every known need:
  `rules-engine` `rule_results` (replay-comparable), `memo-agent-core` `memo_hash`/`model_version`
  (reserved), the C5 read surfaces (US-PLAT-2), and the replay path — stable for the cluster before
  Code-Gen.
- [x] **P7. Guardrail compliance pass + present the standardized 2-option completion message**
  — **APPROVED at the gate 2026-07-03** (Continue to Next Stage → `memo-agent-core` FD, the last
  cluster unit) after the review-beat correction set (ApplicantProfileSnapshot by-reference + single
  CANON-SER; replay equality projection excluding embedded provenance; CON-BR4 closed-enum +
  trim-then-empty).
  (CON-AUDIT-1, CON-BR4, SEC-4/SEC-5, append-only, replay-determinism, advisory-only naming; record
  compliant/N/A per Security-Guardrails control). Then Request Changes / Continue to Next Stage →
  the final cluster unit's Functional Design, **`memo-agent-core`**.

---

## 3. Clarifying questions (Step 3 — fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe.
These decide **internals only** — the contract shapes in §1.2 stay frozen.

### A. Audit record & persistence schema

## Question 1 — `AuditRecord` field-by-field (the persisted record)
The persisted record must carry the CON-AUDIT-1 6-tuple + the commit linkage + the OOS-7 seam. How
is it structured?

A) **One `AuditRecord` entity keyed by `decision_id`**, embedding: the **6-tuple**
   (`rulebook_version`, `rule_results`, `timestamp`, `model_version`, `memo_hash`, `engine_version`),
   the **commit linkage** (`recommendation_id`, `underwriter_id`, `action`, `reason`), and the
   **OOS-7 seam** (`decision_id`, `status`, `supersedes_decision_id`). One row = one committed
   decision; append-only.
B) Split across normalized tables (decision header + rule-results child rows + commit metadata)
   joined by `decision_id`.
C) A single opaque JSON blob per decision with no first-class columns.
D) Other (please describe after [Answer]: tag below)

[Answer]: Full-fidelity 6-tuple, each field typed: rulebook_version (immutable str ref), rule_results (the COMPLETE per-rule result set — every rule's id/outcome/actual-vs-threshold, not a summary), timestamp, model_version, memo_hash, engine_version (git SHA). rule_results must be complete because replay compares against it field-by-field.

## Question 2 — `rule_results` persistence fidelity (carry: match `RuleResultReport` field-for-field)
`rule_results` in the tuple is what `rules-engine` produced. How is it stored so replay comparison
is exact?

A) **Store the full `RuleResultReport` serialized field-for-field** (all per-rule rows incl.
   tri-state `status`, `actual_value`, `operator`, `threshold`, `outcome_tier`, `message`;
   `recommendation`; `confidence`; `rulebook_version` + `content_hash` + `engine_version`;
   `decline_reasons`/`refer_reasons`) using a **canonical serialization** (stable key order,
   Decimal-as-string) so a replayed report compares **byte-for-byte / field-for-field** deterministically.
B) Store only the recommendation + fired (failing) rules; drop passes.
C) Store a hash of the report only (compare hashes on replay, no field-level diff).
D) Other (please describe after [Answer]: tag below)

[Answer]: rule_results stored in a CANONICAL deterministic serialization — stable key ordering, Decimal-as-string (never float), no volatile fields embedded. This is what makes replay-match meaningful: non-canonical serialization could show a false byte-mismatch even when logic reproduced identically.

## Question 3 — `timestamp` determinism boundary (CON-DET-1 vs audit)
`timestamp` is real commit time (audit needs it), but CON-DET-1 forbids wall-clock in **evaluation**.
How is this reconciled?

A) **`timestamp` is audit metadata captured ONCE at commit** (the human-gate action time) — it is
   **not** in the evaluation path and is **never** part of the replay comparison. Replay compares
   **only `rule_results`**; `timestamp`, `underwriter_id`, `reason`, `memo_hash` are recorded
   metadata, re-read not re-derived. (CON-DET-1 intact — determinism is about `evaluate()`, not
   audit metadata.)
B) Derive `timestamp` inside `evaluate()` (rejected — would break CON-DET-1).
C) Store no timestamp (rejected — CON-AUDIT-1 requires it).
D) Other (please describe after [Answer]: tag below)

[Answer]: timestamp is captured-once at commit and persisted (audit fact), but EXCLUDED from the replay-compared set. Replay compares the deterministic decision content {rulebook_version, rule_results, recommendation, confidence, engine_version}; wall-clock/timestamp fields are not compared, so replay at a later time cannot false-mismatch.

### B. `DecisionCommitService` — the CON-BR4 write-gate

## Question 4 — Reason-mandatory semantics (CON-BR4 vs the Approve/Override actions)
CON-BR4 rejects any write lacking `underwriter_id` + `reason`; the frozen signature has
`reason=None`; `services.md §5` shows **Approve** (agree) vs **Override-with-reason** (disagree).
When is `reason` mandatory?

A) **`underwriter_id` is always mandatory. `reason` (free-text) is mandatory on
   `action=override` (disagreement); on `action=approve` (agreement with the recommendation) the
   action itself is the rationale of record** — the gate accepts approve without free-text but
   **records the action as the reason-of-record**, so no committed decision is ever unexplained
   (CON-BR4 satisfied: every commit carries `underwriter_id` + an explicit rationale, free-text or
   action-of-record). Matches `services.md §5`.
B) `reason` (free-text) is mandatory on **every** commit including approve (gate rejects approve
   without free-text).
C) `reason` is always optional; only `underwriter_id` is enforced.
D) Other (please describe after [Answer]: tag below)

[Answer]: underwriter_id ALWAYS mandatory. Free-text reason MANDATORY on Override-with-reason (disagree). On Approve (agree), the recorded action + the endorsed recommendation IS the rationale-of-record — CON-BR4's "reason" is satisfied structurally, no separate free-text required. The gate still hard-rejects any write lacking underwriter_id or a recorded action; Override still hard-requires free-text. (Reconciles CON-BR4 literal with services.md §5.)

## Question 5 — Authz re-check inside the service (SEC-4, defense-in-depth)
`services.md §5` shows RBAC enforced at the API layer **and** re-checked in `DecisionCommitService`.
How is the service-level re-check modelled?

A) **`DecisionCommitService.commit` independently re-checks the caller is an underwriter role**
   (not relying on the API-layer check) — a read-only **auditor is structurally rejected at the
   service** even if the API check were bypassed. Defense-in-depth: two enforcement points, the
   service is the last line (SEC-4).
B) Trust the API-layer RBAC; no service-level re-check.
C) Re-check only for override, not approve.
D) Other (please describe after [Answer]: tag below)

[Answer]: DecisionCommitService re-verifies the committer's role (underwriter, not auditor) at commit time, at the BACKEND boundary, independent of the UI-layer check — defense in depth (SEC-4). A commit from a read-only role is rejected even if the UI control were bypassed.

## Question 6 — Persistence trigger = commit (carry: persisted on committed decision, not recommendation)
CON-AUDIT-1 persists on every **committed decision**, not every recommendation. What triggers the
`AuditRecord` write?

A) **Persistence is triggered by `DecisionCommitService.commit`** (the human gate). The
   `AuditRecord` binds the recommendation's `rule_results` + `memo_hash`/`model_version` + the human
   `action`/`reason` into **one committed record keyed by `decision_id`**. A **pending recommendation
   that is never committed produces no `AuditRecord`** (an uncommitted recommendation may leave an
   observability trace, but not a CON-AUDIT-1 audit record).
B) Persist an audit record when the recommendation is produced (before the human gate).
C) Persist twice — once at recommendation, once at commit.
D) Other (please describe after [Answer]: tag below)

[Answer]: The audit tuple is assembled and persisted ATOMICALLY as part of the commit, on every COMMITTED DECISION (not every recommendation). Commit + audit-write are one atomic operation — no committed decision without its persisted audit tuple (CON-AUDIT-1).

### C. `ReplayService` — replay-as-detection (rules-engine Q11 boundary)

## Question 7 — Replay orchestration + source of the original profile
`ReplayService.replay(decision_id)` re-evaluates against the **original** `rulebook_version`. What
does it own, and where does the original profile come from?

A) **`ReplayService` owns orchestration**: load the `AuditRecord`, obtain the **exact original
   `ApplicantProfile` + `rulebook_version`** (stored with / referenced by the record so replay is
   **self-contained and deterministic**), **call `rules-engine.evaluate(profile,
   original_rulebook_version)`** to re-derive a fresh `RuleResultReport`, and compare to the recorded
   `rule_results`. **`rules-engine` owns `evaluate()`**; audit-store owns load + call + compare
   (clean split, rules-engine Q11).
B) `ReplayService` re-implements evaluation itself (no call to rules-engine).
C) Replay against the **latest** rulebook version (rejected — must be the original).
D) Other (please describe after [Answer]: tag below)

[Answer]: ReplayService loads the ORIGINAL rulebook_version AND the original ApplicantProfile AS-PERSISTED with the decision record (not re-parsed from source documents), then calls rules-engine's pure evaluate() to re-derive. rules-engine owns evaluate(); ReplayService owns orchestration (Q11 boundary from rules-engine). [Confirm the ApplicantProfile is persisted in/with the audit record so replay can reload the exact original input.]

## Question 8 — Match/mismatch comparison + blocking-failure semantics (G4, OOS-8)
How is match determined, and what does a mismatch produce?

A) **Field-for-field equality on the canonical-serialized `rule_results`** (Q2 form): **match →
   replay OK** (decision reproduced); **mismatch → a blocking reproducibility-failure flag**,
   surfaced read-only (**detection only**; the incident-handling workflow is Phase 3 / OOS-8).
   `engine_version` (code drift) + `content_hash` (rulebook byte-identity) let an investigator
   distinguish engine drift vs rulebook drift vs a real regression. Replay is **not assumed to
   pass** — it is a detection mechanism.
B) Compare only the final `recommendation` (not the per-rule results).
C) Mismatch silently re-writes the record to the new result (rejected — violates append-only).
D) Other (please describe after [Answer]: tag below)

[Answer]: Replay compares the re-derived result to the recorded rule_results (canonical, per Q2/Q3): match → reproducibility VERIFIED; mismatch → flagged as a BLOCKING reproducibility failure (reviewer G4 detection). Detection is in scope now; the incident-handling WORKFLOW is Phase 3 (OOS).

## Question 9 — Replay excludes memo re-draft + re-commit (determinism, no LLM)
Does replay re-run the memo or the human gate?

A) **No. Replay re-evaluates ONLY `rule_results`** (deterministic, pure `evaluate()`); it **never
   re-drafts the memo** (no LLM in replay) and **never re-commits**. Memo integrity is verified
   separately via **`memo_hash`** comparison (recorded vs recomputed hash of the stored memo). Keeps
   replay deterministic and LLM-free (CON-DET-1, CON-BR2 spirit).
B) Replay re-drafts the memo via the LLM to check it too (rejected — non-deterministic, LLM in
   replay).
C) Replay re-runs the full pipeline including a new commit.
D) Other (please describe after [Answer]: tag below)

[Answer]: On mismatch, capture a forensic DELTA (which field/rule diverged, recorded-vs-re-derived, and whether engine_version differs) for the Phase-3 incident workflow — this is why engine_version is captured now. Replay NEVER re-drafts the memo: it re-evaluates RULES only and verifies the memo by memo_hash comparison, never calling the LLM (which would be non-deterministic).

### D. OOS-7 amendment seam · append-only · auditor read surface

## Question 10 — OOS-7 seam field-level schema (reserved now, `status=active` only)
The Phase-3 append-only supersession seam is designed (fields) now. How?

A) **Every `AuditRecord` carries: `decision_id`** (stable, **system-generated** PK — same pattern as
   intake's system-assigned `application_id`), **`status`** (enum `active`/`superseded`, **defaulting
   `active`; Phase 1/2 NEVER writes `superseded`**), and **nullable `supersedes_decision_id`** (FK,
   always null in Phase 1/2). The **supersession WRITE path is not built** (documented OOS-7), but
   the columns exist so a Phase-3 append-only amendment slots in **without migrating** existing
   records.
B) Add the seam columns only when Phase 3 arrives (rejected — requires a later migration; the seam
   is meant to be reserved now).
C) Model supersession as an in-place `status` UPDATE (rejected — violates append-only).
D) Other (please describe after [Answer]: tag below)

[Answer]: OOS-7 seam fields typed now: decision_id (stable unique key identifying the committed decision — distinct from application_id), status (enum active/superseded), supersedes_decision_id (nullable self-FK). Phase 1/2 writes status=active only, supersedes_decision_id always null. Field-level schema designed here; amendment behavior is Phase 3.

## Question 11 — Append-only enforcement (CON-AUDIT-1 / SEC-5)
How is append-only enforced?

A) **The audit table is append-only by construction**: **no `UPDATE`/`DELETE` on committed
   records**, enforced at both the service layer (no mutation API) and the **DB-role** level
   (write-role may `INSERT` only; auditor role is **read-only**, SEC-4). Corrections (Phase 3) happen
   via a **new superseding record** (Q10), never mutation — tying immutability to the supersession
   model.
B) Enforce append-only in application code only (no DB-role constraint).
C) Allow updates but keep a change-log table.
D) Other (please describe after [Answer]: tag below)

[Answer]: Append-only enforced STRUCTURALLY at the persistence boundary — no UPDATE/DELETE on committed audit records. Corrections (Phase 3) are new superseding records (status transition via a new append), never in-place edits. This is what makes CON-AUDIT-1 integrity and the Q10 seam work.

## Question 12 — Auditor read-only surface (US-PLAT-2, SEC-4)
What does the auditor read-only surface expose, and how is write blocked?

A) **`AuditService` exposes read-only queries** — get decision by `decision_id`, browse decision
   history — backed by a **read-only DB role** (SEC-4). The auditor can open any past decision (the
   full 6-tuple: `rulebook_version`, `rule_results`, `timestamp`, `model_version`, `memo_hash`,
   `engine_version`) + its replay outcome, but **cannot modify any record** (append-only + read-only
   role). This is the US-PLAT-2 surface the C5 `ui-history` / `ui-memo-view` consume. **No write
   capability on this path.**
B) Expose read + write to the auditor (rejected — SEC-4 segregation).
C) Expose only the recommendation, not the full tuple (rejected — CON-AUDIT-1 traceability).
D) Other (please describe after [Answer]: tag below)

[Answer]: Auditor role (SEC-4) can READ audit records and run replay, but has NO write/commit/amend capability — enforced at the BACKEND (DecisionCommitService rejects any write from the auditor role), not just hidden in the UI. Read-only segregation is structural.

---

## 4. Constraints & settled items held (not re-opened)
- Contract **shapes** frozen at Application Design (`component-methods.md`) — FD fills internals only
  (`DecisionCommitService.commit` / `AuditStore.persist` / `ReplayService.replay`; `AuditTuple`
  6-tuple; `CommittedDecision` + OOS-7 seam).
- Cluster-FD-first: unit 3 of 4; the `AuditRecord` field-level contract must be stable across the
  cluster (consumes `rules-engine`'s `RuleResultReport`; reserves `memo-agent-core`'s
  `memo_hash`/`model_version`) before any Code-Gen.
- Carry-forwards (§1.3): `RuleResultReport` field-for-field persistence; 6-tuple + `engine_version`;
  replay boundary (audit-store orchestrates, rules-engine `evaluate()`); CON-BR4 write-gate
  single-sourced here; persisted-on-committed-decision (append-only); OOS-7 seam schema designed here.
- Guardrails (§1.4): CON-AUDIT-1, CON-BR4, CON-DET-1 replay boundary, SEC-4/SEC-5, DATA-5,
  advisory-only naming ("decision" = the human's committed action).
- Three settled non-edits stay closed: `PROJECT-BRIEF.md`, the **OOS-7 README/case-study doc
  commitment** (this FD designs the seam **fields**, not the docs), `user-journey.md`.

---

## 5. Next step (STOP here)
Fill the twelve `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory
ambiguity-check (adding a clarification file only if needed), then generate the three `audit-store`
Functional Design artifacts and present the 2-option completion message. **No FD artifacts or code
are generated until the answers are in and checked.**
