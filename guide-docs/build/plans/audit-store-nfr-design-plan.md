# NFR Design Plan (Part 1) — `audit-store` (C5 / U12)

**Phase / Stage**: BUILD → NFR Design, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: cluster unit **3 of 4** · FD ✅ · **NFR Requirements ✅ (APPROVED 2026-07-05)** → **NFR Design ← here** → [Infra likely SKIP] → Code-Gen.
**Unit**: U12 `audit-store` — the CON-BR4 write-gate, append-only audit persistence, replay-as-detection, auditor read-only surface.
**Date**: 2026-07-05 · **Runtime**: Python **3.12 pinned** · **Depth**: **comprehensive**.
**Status**: **Plan — awaiting `[Answer]:` tags. NO NFR-Design artifacts generated this stage. Stop after this plan.**

This plan maps **each approved `NFR-AUDIT-*` target → a design pattern (the "how")**, built **ON** the frozen FD +
the approved NFR targets — **re-opening neither** (not the C5 contract, the `AuditRecord` superset shape, the commit
predicate, the replay equality set, nor any NFR target). **Reference-not-own throughout.** Mermaid is required in the
**artifacts** (validated against the 7 rules + text alternative) — **not** in this plan.

---

## 1. What NFR Design builds ON (frozen / approved — NOT re-opened)
- **Frozen C5 contract**: `DecisionCommitService.commit(recommendation_id, underwriter_id, action, reason=None) ->
  CommittedDecision`; `AuditStore.persist(audit_tuple) -> None`; `ReplayService.replay(decision_id) -> RuleResultReport`;
  `AuthRBAC.authorize(user, action) -> bool`.
- **Frozen FD**: the `AuditRecord` superset (6-tuple `AuditTuple` + `CommittedDecision` + `ApplicantProfileSnapshot` +
  OOS-7 seam); BR-COMMIT-GATE / BR-AUTHZ-RECHECK / BR-PERSIST-ATOMIC / BR-APPEND-ONLY / BR-STATUS-WRITE-ONCE /
  BR-AUDIT-READ / BR-REPLAY-* ; the single CANON-SER §2.1.
- **Approved NFR targets** (14 `NFR-AUDIT-*`): GATE-1, AUTHZ-1, ATOMIC-1, TUPLE-1, APPEND-1, STATUS-1, REPLAY-1,
  REPLAY-2, BR1-1, READ-1, LOG-1, CANON-1, PERF-1, OBS-1.
- **Reference-not-own**: rules-engine `evaluate()` + `evaluation_output()` (`backend/rules_engine/report.py`); intake's
  `ApplicantProfile`; shared `backend/common/canon_ser.py` (unchanged) + `decimal_context.py`; `database` DDL /
  migrations / role-grants (`audit_writer`/`audit_reader`); `auth-rbac` policy; observability stack; `memo-agent-core`
  `memo_hash`/`model_version` computation.

## 2. Pattern approach per target group (draft — finalized in the artifacts after the answers)
- **GATE-1 / AUTHZ-1** → a single **fail-closed commit-gate wrapper** (the closed negative matrix as one total-function
  predicate) + an **independent backend authz re-check** call site — mirrors intake's `IntakeGate` and rules-engine's
  total-function patterns.
- **ATOMIC-1** → the **transaction mechanism** that makes assemble+persist **decomposition-agnostic both-or-neither**
  (the genuine deferred decision — **Q2**).
- **TUPLE-1** → **assemble the full `AuditRecord` superset as one immutable object *before* the persist boundary**, so the
  write is a single atomic write of a complete record.
- **APPEND-1 / STATUS-1** → **append-only structural guarantee** (the repository exposes **only insert + read**, no
  update/delete method) + **derived-superseded-ness as a read query** (never a write path).
- **REPLAY-1 / REPLAY-2 / BR1-1** → the **`ReplayService` orchestration** (load → deserialize to intake `ApplicantProfile`
  → call rules-engine `evaluate()` → apply rules-engine's `evaluation_output()` to **both** sides → compare), with the
  **single-sourced projection** made concrete (**Q5**).
- **READ-1 / LOG-1** → the **`AuditService` read-only query pattern**, DB-role-backed + backend-enforced.
- **CANON-1** → the **audit-store-local `CanonSerAdapter`** delegating to the **unchanged** shared util, for both payloads.
- **PERF-1 / OBS-1** → the **emit-only allowlist `TelemetryEmitter`** (no demographic/free-text field), distinct from the
  `AuditService` read path.
- **Repository abstraction** → the seam that realizes the NFR-Req **unit-vs-integration test split** (**Q9**).

---

## 3. Clarifying questions (fill each `[Answer]:` tag)

Letter choice after each `[Answer]:`; if none fit, choose the last option (Other) and describe. These decide **NFR-Design
patterns** — they do **not** re-open the FD / C5 contract / NFR targets.

## Question 1 — Commit-gate pattern (GATE-1 / AUTHZ-1)
How is the CON-BR4 gate + the backend authz re-check structured?

A) **A single fail-closed boundary wrapper** in `DecisionCommitService`: one **total-function predicate** evaluates the
   closed negative matrix (reject iff `underwriter_id`∅ / `action`∅-or-∉enum / override+trim-empty reason) **before** any
   assembly, and an **independent `AuthRBAC.authorize` re-check** (defense-in-depth, not the API layer) gates the same
   boundary. Nothing reaches assembly/persist unless **both** pass — mirrors intake's `IntakeGate` / rules-engine's
   total-function patterns. *(Recommended.)*
B) Scatter the checks across call sites (rejected — no single fail-closed boundary).
C) Other (describe).

[Answer]: A — a single fail-closed boundary wrapper in DecisionCommitService: one total-function predicate evaluates the closed negative matrix before any assembly, and an independent AuthRBAC.authorize re-check gates the same boundary. Nothing reaches assembly/persist unless both pass.

## Question 2 — ATOMIC-1 transaction mechanism (the genuine deferred decision)
BR-PERSIST-ATOMIC needs **decomposition-agnostic both-or-neither**. What mechanism?

A) **A single ACID database transaction** wraps the **entire** assemble→persist (the `AuditRecord` + any normalized rows,
   e.g. a separate `ApplicantProfileSnapshot`): one `BEGIN … COMMIT`; a fault at any step → the transaction **rolls back**
   → zero trace. Appropriate because this is a **single-service monolith writing to one Postgres** (no cross-service /
   cross-datastore write) — the strongest, simplest guarantee; no outbox/saga complexity. *(Recommended — but a real
   decision, not a rubber-stamp: it rests on the single-datastore assumption.)*
B) **Outbox / saga** (a durable outbox row + async projector, or compensating actions) — warranted only if the write
   spanned **multiple datastores / services**. Not the case here; adds complexity + eventual-consistency windows.
C) Other (describe).

[Answer]: A — a single ACID database transaction wraps the entire assemble→persist (the AuditRecord + any normalized rows): one BEGIN...COMMIT; a fault at any step → rollback → zero trace. Appropriate because this is a single-service monolith writing to one Postgres (no cross-service/cross-datastore write) — the strongest, simplest guarantee, no outbox/saga complexity or eventual-consistency window for a unit whose core property is atomicity.

## Question 3 — AuditRecord assembly pattern (TUPLE-1)
How is the 6-tuple + snapshot + linkage + seam assembled relative to the transaction?

A) **Assemble the complete immutable `AuditRecord` superset in memory FIRST** (all six tuple fields + the
   `ApplicantProfileSnapshot` [profile → CANON-SER + `content_hash`] + the `CommittedDecision` linkage + the seam
   [`status=active`, `supersedes_decision_id=null`]), validated by the Pydantic models, **then** perform the single
   atomic write (Q2). No field is computed mid-transaction; a missing/null tuple field fails **before** the write.
   *(Recommended — completeness is a pre-persist invariant.)*
B) Assemble incrementally inside the transaction (weaker — partial-assembly risk).
C) Other (describe).

[Answer]: A — assemble the complete immutable AuditRecord superset in memory FIRST (all six tuple fields + ApplicantProfileSnapshot + CommittedDecision linkage + the seam), validated by the Pydantic models, THEN perform the single atomic write. No field computed mid-transaction; a missing/null tuple field fails before the write.

## Question 4 — Append-only + derived-superseded (APPEND-1 / STATUS-1)
How is append-only + the OOS-7 derived-superseded-ness structured?

A) **Repository exposes ONLY `insert` + read methods — no `update`, no `delete` method exists** (a structural, testable
   guarantee at the service layer), complemented by the `database` unit's INSERT-only write role (referenced). **`status`
   is written once `active`**; **superseded-ness is a pure READ query** (`exists a record with supersedes_decision_id ==
   this decision_id`) — **never a write path**, so no `active→superseded` in-place flip. Phase-1/2 the query always
   returns `active`. *(Recommended.)*
B) Provide a guarded `update` that only flips `status` (rejected — introduces a mutation path; contradicts append-only).
C) Other (describe).

[Answer]: A — repository exposes ONLY insert + read methods, no update/delete method exists (structural, testable), complemented by the database unit's INSERT-only write role (referenced). status written once active; superseded-ness is a pure READ query, never a write path.

## Question 5 — ReplayService orchestration + the single-sourced projection (REPLAY-1 / -2 / BR1-1)
How concrete is the replay projection?

A) **`ReplayService` owns load + call + compare only.** It (i) loads the `AuditRecord`; (ii) **deserializes**
   `profile_canonical` (CANON-SER) back to the **exact intake `ApplicantProfile`** (Pydantic `model_validate`);
   (iii) calls **rules-engine's pure `evaluate()`**; (iv) **deserializes the recorded `rule_results` (CANON-SER) into a
   rules-engine `RuleResultReport`** and applies **rules-engine's own `evaluation_output()`** to **both** it **and** the
   fresh report — a **single imported projection function**, not re-derived here; (v) compares the two projections over
   CANON-SER → match / mismatch-with-forensic-delta. `engine_version`/`content_hash` are surfaced (forensic), never
   compared. **No LLM, no memo re-draft, no re-commit; replay ×N byte-identical.** *(Recommended — single-sourced,
   reference-not-own.)*
B) Re-derive a local projection in audit-store (rejected — parallel projection, drift risk vs rules-engine).
C) Other (describe).

[Answer]: A — ReplayService owns load + call + compare only: loads the AuditRecord; deserializes profile_canonical back to the exact intake ApplicantProfile; calls rules-engine's pure evaluate(); deserializes the recorded rule_results and applies rules-engine's own evaluation_output() to both it and the fresh report (single imported projection, not re-derived); compares over CANON-SER → match/mismatch-with-forensic-delta. engine_version/content_hash surfaced forensic, never compared. No LLM, no memo re-draft, no re-commit; replay ×N byte-identical.

## Question 6 — AuditService read-only query pattern (READ-1 / LOG-1)
How is the auditor read surface structured?

A) **A read-only `AuditService`** exposing `get(decision_id)` + `browse_history(application_id | across cases)`, backed by
   the **read-only DB role** (`audit_reader`, referenced) and the **backend authz** — **backend-enforced, not UI-hidden**.
   It returns the full 6-tuple + the replay outcome; it has **no write method**. *(Recommended.)*
B) Fold reads into `DecisionCommitService` (rejected — conflates the write-gate with the read surface).
C) Other (describe).

[Answer]: A — a read-only AuditService exposing get(decision_id) + browse_history(application_id | across cases), backed by the read-only DB role (audit_reader, referenced) and backend authz — backend-enforced, not UI-hidden. Returns the full 6-tuple + replay outcome; no write method.

## Question 7 — CanonSerAdapter (CANON-1)
How does audit-store serialize both `rule_results` and `profile_canonical`?

A) **An audit-store-local `CanonSerAdapter`** delegating to the **UNCHANGED** shared `backend/common/canon_ser.py` for
   both payloads (the `RulebookCanonAdapter`/intake-`CanonSerAdapter` precedent); `content_hash = sha256(canon bytes)`;
   a **pre-replay tamper check** (recomputed hash vs recorded). **No fork, no §2.1 change, no re-declaration** — audit-store
   is the §2.1 spec authority, `backend/common/` is the shared location. *(Recommended.)*
B) Call the shared util inline everywhere (no adapter) — workable but scatters the convention; less cohesive.
C) Other (describe).

[Answer]: A — an audit-store-local CanonSerAdapter delegating to the UNCHANGED shared backend/common/canon_ser.py for both payloads; content_hash = sha256(canon bytes); a pre-replay tamper check (recomputed hash vs recorded). No fork, no §2.1 change, no re-declaration.

## Question 8 — TelemetryEmitter (PERF-1 / OBS-1)
How is observability structured, kept distinct from the audit trail?

A) **An emit-only allowlist `TelemetryEmitter`** — a Pydantic allowlist schema of **ids/enums/int counts/int timing
   only**, **no applicant-profile/demographic/free-text field** (schema-level assertion, mirroring intake/rules-engine).
   Commit/replay **duration is emitted, never gated** (PERF-1). **Distinct from** the `AuditService` read path (the SEC-5
   trail deliberately persists the full record). *(Recommended.)*
B) Emit through the audit trail (rejected — conflates metrics with the trail; demographic-leak risk).
C) Other (describe).

[Answer]: A — an emit-only allowlist TelemetryEmitter: a Pydantic allowlist schema of ids/enums/int counts/int timing only, no applicant-profile/demographic/free-text field. Commit/replay duration emitted, never gated. Distinct from the AuditService read path.

## Question 9 — Repository abstraction (realizes the unit/integration test split)
How is persistence abstracted so pure logic is unit-testable and DB behavior is integration-tested?

A) **A repository interface (Protocol/ABC)** with a **SQLAlchemy-2.x/Postgres implementation** + an **in-memory fake**.
   The pure predicate (GATE-1), assembly (TUPLE-1), projection (REPLAY-1), and CANON-SER (CANON-1) logic is unit-tested
   against the fake; ATOMIC-1 (fault injection), APPEND-1 (DB-role), READ-1/LOG-1 run against **real Postgres**
   (testcontainers). *(Recommended — realizes the NFR-Req §4 tier split; DATA-5 honored.)*
B) No abstraction — every test hits Postgres (slower; couples pure-logic tests to the DB).
C) Other (describe).

[Answer]: A — a repository interface (Protocol/ABC) with a SQLAlchemy-2.x/Postgres implementation + an in-memory fake. Pure predicate/assembly/projection/CANON-SER logic unit-tested against the fake; ATOMIC-1/APPEND-1/READ-1/LOG-1 run against real Postgres (testcontainers).

## Question 10 — decision_id generator seam placement
Where does the injected `decision_id` generator live?

A) **Injected into `DecisionCommitService`** (constructor param) — UUID in production, deterministic fake in tests
   (mirrors rules-engine's injected `engine_version` / intake's `application_id` seam). Called once at assembly; not part
   of the replay equality set. *(Recommended.)*
B) A module-level global / inline `uuid4()` (rejected — non-injected, harder to test).
C) Other (describe).

[Answer]: A — injected into DecisionCommitService (constructor param): UUID in production, deterministic fake in tests. Called once at assembly; not part of the replay equality set.

## Question 11 — Logical component set + the two Mermaid diagrams
Confirm the components + the artifact diagrams.

A) **Six components** — `DecisionCommitService` (gate + assemble + atomic persist), `AuditStore`/**repository** (insert +
   read, no mutation), `ReplayService` (load + call rules-engine + compare), `AuditService` (read-only queries),
   `CanonSerAdapter` (shared-util delegation), `TelemetryEmitter` (allowlist emit-only) — plus **`AuthRBAC` referenced**
   (the commit re-check) and the **injected `decision_id` generator**. The artifacts carry **two validated Mermaid
   diagrams** (pattern-integration + component-relationships) + text alternatives, consistent with the FD entities.
   *(Recommended.)*
B) A different component decomposition (describe).
C) Other (describe).

[Answer]: A — six components (DecisionCommitService, AuditStore/repository, ReplayService, AuditService, CanonSerAdapter, TelemetryEmitter) plus referenced AuthRBAC and the injected decision_id generator. Two validated Mermaid diagrams (pattern-integration + component-relationships) + text alternatives in the artifacts.

---

## 4. Logical components (to be detailed in `logical-components.md`)
`DecisionCommitService` · `AuditStore` (repository — insert + read only) · `ReplayService` · `AuditService` ·
`CanonSerAdapter` · `TelemetryEmitter` · (referenced: `AuthRBAC.authorize`, rules-engine `evaluate()`/`evaluation_output()`,
the injected `decision_id` generator). Responsibilities + relationships mapped to the FD entities (`AuditRecord`,
`AuditTuple`, `CommittedDecision`, `ApplicantProfileSnapshot`), with **no reference-not-own violation**.

## 5. Constraints & settled items held (not re-opened)
- **Frozen FD + approved NFR targets** are the inputs — NFR Design gives each a **pattern**, re-opening none.
- **Do NOT re-open**: the C5 contract, the `AuditRecord` superset shape, the commit predicate, the replay equality set,
  any NFR target.
- **Reference-not-own**: rules-engine `evaluate()`/`evaluation_output()`; intake `ApplicantProfile`; shared CANON-SER
  (unchanged) + `decimal_context`; `database` DDL/migrations/grants; `auth-rbac` policy; observability stack;
  `memo-agent-core` `memo_hash`/`model_version`.
- **No LLM anywhere in audit-store.** Mermaid (artifacts only) validated against the 7 rules + text alternative.

## 6. Next step (STOP here)
Fill the eleven `[Answer]:` tags above. On your signal I will read the answers, run the mandatory ambiguity-check
(adding a clarification file only if needed), then **generate Part 2** — `nfr-design-patterns.md` (the pattern per
`NFR-AUDIT-*` target) + `logical-components.md` (the six components + relationships + two validated Mermaid diagrams) —
and stop at the NFR-Design 2-option gate. **NO NFR-Design artifacts are generated until the answers are in, checked, and
you give the explicit go.**
