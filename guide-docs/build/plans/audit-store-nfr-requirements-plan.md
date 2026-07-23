# NFR Requirements Plan (Part 1) — `audit-store` (C5 / U12)

**Phase / Stage**: BUILD → NFR Requirements, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: cluster unit **3 of 4** · **FD ✅** → **NFR Requirements ← here** → NFR Design → [Infra likely SKIP] → Code-Gen.
(`intake`+`document-sanitizer` COMPLETE; `rules-engine` COMPLETE — this is the THIRD cluster unit.)
**Unit**: U12 `audit-store` — the CON-BR4 write-gate, append-only audit persistence, replay-as-detection, auditor read-only surface.
**Date**: 2026-07-05 · **Runtime**: Python **3.12 pinned** (D6) — venv already on 3.12.10.
**Depth**: **comprehensive** (invariant-bearing deterministic-core / audit unit — same rule that applied to `intake` and `rules-engine`).
**Status**: **Plan — awaiting `[Answer]:` tags. NO NFR-Requirements artifacts generated this stage. Stop after this plan.**

This plan follows `.project-guide-rule-details/build/nfr-requirements.md` (Part 1) + the project's plan-then-generate
discipline. It is built **ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`)
and the frozen C5 contract — **re-opening none of them**. Every `NFR-AUDIT-*` target below is drafted to be
**pass/fail testable**; the exact set is finalized into `nfr-requirements.md` only after the `[Answer]:` tags are filled.

---

## 1. Unit context (analyzed)

### 1.1 What NFR Requirements builds ON (frozen — NOT re-opened)
- **Frozen C5 contract** (`component-methods.md`): `DecisionCommitService.commit(recommendation_id, underwriter_id,
  action, reason=None) -> CommittedDecision`; `AuditStore.persist(audit_tuple) -> None`;
  `ReplayService.replay(decision_id) -> RuleResultReport`; `AuthRBAC.authorize(user, action) -> bool` (enforced at the
  API layer **and** inside `DecisionCommitService`).
- **Frozen FD**: the `AuditRecord` **superset** (6-tuple `AuditTuple` + `CommittedDecision` + `ApplicantProfileSnapshot`
  + OOS-7 seam `decision_id`/`status`/`supersedes_decision_id`); the **BR-COMMIT-GATE** predicate; **BR-AUTHZ-RECHECK**;
  **BR-PERSIST-ATOMIC**; **BR-APPEND-ONLY** + **BR-STATUS-WRITE-ONCE**; **BR-AUDIT-READ**; **BR-REPLAY-EQUALITY /
  -VERDICT / -NO-MEMO**; the single **CANON-SER** convention (`domain-entities.md §2.1`) for both `rule_results` and
  `profile_canonical`.

### 1.2 Dependencies & interfaces (reference-not-own)
- **Consumes** `rules-engine` (U3, COMPLETE): `ReplayService` calls its **pure `evaluate()`** (referenced, **never
  reimplemented**); persists its **`RuleResultReport`** field-for-field; the replay equality set mirrors rules-engine's
  **`evaluation_output` projection** (`backend/rules_engine/report.py` — `{rule_results, recommendation, confidence,
  decline_reasons, refer_reasons}`, excluding `rulebook_version`/`content_hash`/`engine_version`). **See Q2.**
- **Consumes** `intake` (COMPLETE): `ApplicantProfileSnapshot.profile_canonical` round-trips back to the **exact
  `ApplicantProfile`** — intake's contract governs (imported, **not re-declared**).
- **Shared (reference-not-own)**: `backend/common/canon_ser.py` (the single CANON-SER — audit-store is its **spec
  authority** but `backend/common/` is only the shared location; **unchanged**, no §2.1 change) + `decimal_context.py`.
- **Owned elsewhere (referenced, not built here)**: `database` (U — PostgreSQL provisioning / migrations / role grants /
  DDL — **DATA-5**); `auth-rbac` (the `AuthRBAC.authorize` policy — audit-store owns only the **re-check enforcement
  point**); `observability` (metrics/trace stack); `quality-gates` (blocking bias-swap / calibration verification
  aggregation); `memo-agent-core` (owns `memo_hash` / `model_version` — audit-store **persists** them, never computes).

### 1.3 Guardrails held (skill)
- **CON-BR4** human-gate write predicate (no unaccountable committed decision); **CON-AUDIT-1** (6-tuple + atomic
  persist + append-only + replayability); **SEC-4/SEC-5** (auditor read-only, backend-enforced; audit trail);
  **CON-BR1** (storage ≠ influence — snapshot stores demographics; `evaluate()` structurally excludes them);
  **CON-DET-1** (replay determinism boundary — CANON-SER + excluded volatile/forensic fields, no false mismatch);
  **advisory-only** (`action` = the one correct use of "decision"; system output stays a "recommendation");
  **DATA-4** (synthetic only, no real PII); **DATA-5** (PostgreSQL, no SQLite). **No LLM anywhere in audit-store**
  (replay re-evaluates rules only; memo integrity = `memo_hash` comparison).

---

## 2. Draft `NFR-AUDIT-*` targets (pass/fail testable — finalized after the answers)

Each target names its invariant, the FD rule it realizes, and a **pass/fail test shape**. IDs are provisional.

### CON-BR4 — commit write-gate
- **NFR-AUDIT-GATE-1** — `commit` is a **total function over the closed negative matrix** (BR-COMMIT-GATE): **REJECT iff**
  `underwriter_id` missing/empty **OR** `action` missing **OR** `action ∉ {approve, override}` **OR**
  (`action == override` AND `trim(reason) == ""`). Test: an **exhaustive negative matrix** (each clause, incl.
  **whitespace-only** reason) → reject; the **accept** cases (`approve` with no reason; `override` with a non-blank
  reason) → accept. **Property**: no accepted commit is ever unaccountable (carries WHO + WHAT + WHY-or-endorsement).
- **NFR-AUDIT-AUTHZ-1** (SEC-4) — the **backend authz re-check** rejects a non-underwriter (auditor) committer
  **independent of the API layer**. Test: drive `commit` with an auditor-role id while the API-layer authz is
  bypassed/stubbed → **reject at the service** (defense-in-depth; the service is the last line).

### CON-AUDIT-1 — atomic persist + 6-tuple completeness
- **NFR-AUDIT-ATOMIC-1** — commit + `AuditRecord` write are **one atomic operation**: a rejected gate writes **zero**
  records; an accepted commit writes **exactly one**; a fault mid-persist leaves **neither** (both-or-neither). Test:
  reject → 0 rows; accept → 1 row; **injected fault** after the decision row / before the audit row → full rollback.
- **NFR-AUDIT-TUPLE-1** — every persisted `AuditRecord` carries the **full 6-tuple** (`rulebook_version`,
  `rule_results`, `timestamp`, `model_version`, `memo_hash`, `engine_version`) **non-null** + the
  `ApplicantProfileSnapshot` + the `CommittedDecision` linkage + the seam (`status=active`, `supersedes_decision_id=null`).
  Test: assert presence + non-null of each field on a committed record.

### Append-only (CON-AUDIT-1 / SEC-5)
- **NFR-AUDIT-APPEND-1** — append-only at **two layers**: (a) **service** exposes **no UPDATE/DELETE** API (structural —
  only insert + read); (b) **DB-role** — the write role is **INSERT-only**, the auditor role **read-only** (SEC-4).
  Test: service-level negative (no mutation method exists) **+** a **DB-role integration test** (against real Postgres,
  DATA-5) where `UPDATE`/`DELETE` on a committed record **raises a permission error**. **See Q3** for the ownership
  boundary of the role-grant DDL.
- **NFR-AUDIT-STATUS-1** — `status` is **written once as `active`** and never flipped in place; **`superseded`-ness is a
  DERIVED read-time projection** (a record is superseded **iff** a newer record's `supersedes_decision_id` points at it).
  Test: Phase-1/2 has **no code path** that writes `superseded`; the derived-superseded projection is a pure read.

### Replay (CON-AUDIT-1 + CON-DET-1 boundary)
- **NFR-AUDIT-REPLAY-1** — the replay verdict is decided by **equality of the evaluation-output PROJECTION only**, over
  the single **CANON-SER**, **excluding** volatile (`timestamp`/`underwriter_id`/`reason`/`memo_hash`) and forensic
  (`engine_version`/`content_hash`; `rulebook_version` = load key) fields. The projection **matches rules-engine's
  `evaluation_output` field-for-field** (**see Q2**). Test: (a) unchanged record → **match**; (b) an
  `engine_version`/`content_hash`-only difference → **still match** (no false mismatch — an engine refactor must not
  mass-flag history); (c) a genuine `rule_results`/`recommendation`/`confidence` difference → **mismatch (blocking) +
  forensic delta** (which field diverged, drift flags). **Cross-checked field-for-field against rules-engine's projection.**
- **NFR-AUDIT-REPLAY-2** — replay determinism boundary: `ReplayService` **calls rules-engine's pure `evaluate()`**
  (reference-not-own — no evaluation logic of its own); the `profile_canonical` **round-trips through CANON-SER back to
  the exact intake `ApplicantProfile`** fed to `evaluate()`; **no LLM / no memo re-draft** in replay (memo integrity =
  `memo_hash` comparison, recorded-vs-recomputed). Test: replay invokes no LLM; deserialized profile **equals** the
  original; replay ×N is **byte-identical** (deterministic); memo is never re-drafted.
- **NFR-AUDIT-BR1-1** (CON-BR1 storage ≠ influence) — the snapshot **stores** the segregated `demographics`, but a
  replay re-evaluation **cannot let them influence** the output (rules-engine's `evaluate()` structurally excludes them).
  Test: a **bias-swap on the snapshot** (swap demographic fields, identical financials) → **identical** replay output
  (delta = 0). *(Blocking bias-swap verification is single-sourced in `quality-gates`; this asserts the storage≠influence
  property at the replay boundary.)*

### SEC-4 / SEC-5 — auditor surface + audit trail
- **NFR-AUDIT-READ-1** — the auditor read surface (`AuditService`: get-by-`decision_id`, browse-history) is **read-only,
  backend-enforced** (read-only DB role + backend re-check), **not merely UI-hidden**. Test: an auditor reads the full
  6-tuple + replay outcome; any write attempt (commit / update / delete) by an auditor is **rejected at the backend**.
- **NFR-AUDIT-LOG-1** (SEC-5) — the persisted `AuditRecord` history **IS** the SEC-5 audit trail (queryable decision
  history); this is **distinct** from emit-only observability telemetry (**Q8**). Test: every committed decision is
  retrievable in the trail with its full tuple.

### CANON-SER / determinism boundary
- **NFR-AUDIT-CANON-1** — CANON-SER is the **single** serialization convention for **both** `rule_results` **and**
  `profile_canonical`; audit-store **references the shared `backend/common/canon_ser.py` unchanged** (no fork, no §2.1
  change) via an audit-store-local adapter; `content_hash` = CANON-SER hash used as a **pre-replay integrity check**.
  Test: `profile_canonical` round-trip fidelity; `content_hash` tamper-evidence; the adapter delegates to the unchanged
  shared util (byte-identical).

### Performance / observability (scoped to this unit)
- **NFR-AUDIT-PERF-1** — commit + replay latency is **observed-only (soft budget)**, **not gated** — correctness /
  auditability / determinism take precedence (mirrors rules-engine PERF-1; no untrusted parsing here). Test: duration
  emitted; no latency-failing check.
- **NFR-AUDIT-OBS-1** — observability telemetry is **emit-only, allowlist schema** — no applicant-profile / demographic /
  free-text field (mirrors rules-engine OBS-1). **Distinct from the SEC-5 audit trail** (which deliberately DOES persist
  the full record for audit). Test: the telemetry schema structurally carries no demographic/free-text field.

### tech-stack (to be recorded in `tech-stack-decisions.md`)
PostgreSQL (**DATA-5**, no SQLite) · Pydantic v2 (record models) · the DB access layer (**Q7**) · shared CANON-SER +
`decimal_context` referenced · intake `ApplicantProfile` + rules-engine `evaluate()`/`RuleResultReport` referenced ·
**no LLM** · Python 3.12. The `database` unit owns provisioning/migrations/role-grants (reference-not-own).

---

## 3. Clarifying questions (fill each `[Answer]:` tag)

Letter choice after each `[Answer]:`; if none fit, choose the last option (Other) and describe. These decide
**NFR-Requirements specifics** — they do **not** re-open the FD or the frozen contract.

## Question 1 — Test toolchain
What is the test toolchain (TDD, ≥90% QA-6)?

A) **pytest + pytest-cov (≥90%, QA-6)** as the base, **plus Hypothesis** for the universal-quantifier invariants this unit
   rests on — the **CON-BR4 negative matrix** (∀ blank/whitespace/missing combination → reject) and the **replay
   projection-invariance** (∀ forensic-only difference → still match) — alongside explicit example tests. Same toolchain
   as `intake` / `rules-engine`. Postgres-touching targets (append-only DB-role, atomicity) are **integration tests**
   against a real Postgres (Q7); pure predicate/projection logic is unit-tested.
B) pytest + pytest-cov only, no property-based testing.
C) Other (describe).

[Answer]: A — pytest + pytest-cov (≥90%, QA-6) + Hypothesis for the universal-quantifier invariants (CON-BR4 negative matrix; replay projection-invariance ∀ forensic-only difference → still match); Postgres-touching targets as integration tests against real Postgres, pure predicate/projection logic unit-tested.

## Question 2 — Replay equality-set projection: field-for-field with rules-engine (THE key cross-unit alignment)
rules-engine's actual `evaluation_output` (`backend/rules_engine/report.py`) returns **`{rule_results, recommendation,
confidence, decline_reasons, refer_reasons}`** (excluding `rulebook_version`/`content_hash`/`engine_version`). The FD §5
describes the equality set as **"per-rule rows + recommendation + confidence"** (doesn't name the two `*_reasons`). Which
is the replay equality set?

A) **Match rules-engine's `evaluation_output` field-for-field** — include `decline_reasons` + `refer_reasons` (they are a
   **deterministic canonical projection of the per-rule rows** — pure function, canonically sorted — so they can never
   cause a *false* mismatch, and exact parity with rules-engine's real projection prevents cross-unit drift). Treat the
   FD §5 phrasing "per-rule rows + recommendation + confidence" as the **same evaluation-output set** described at a
   higher level (reasons are a projection of the rows). **audit-store consumes rules-engine's `evaluation_output` as the
   single source of the projection** (reference-not-own) rather than re-deriving a parallel one. *(Recommended — one
   projection, single-sourced, field-for-field.)*
B) Use the **narrower** literal FD §5 set (per-rule rows + `recommendation` + `confidence` only; exclude the `*_reasons`).
   Requires audit-store to compute its own projection distinct from rules-engine's — accept the divergence risk.
C) Other (describe).

[Answer]: A — match rules-engine's evaluation_output field-for-field (include decline_reasons + refer_reasons — deterministic canonical projections of the rows, can never cause a false mismatch). Treat FD §5's phrasing as the same set described at a higher level. audit-store consumes rules-engine's evaluation_output as the single source of the projection, reference-not-own, rather than re-deriving a parallel one.

## Question 3 — Append-only DB-role enforcement: ownership boundary + test
BR-APPEND-ONLY is enforced at the service **and** DB-role layers, but the `database` unit owns provisioning/DDL/grants.
How is the DB-role half owned + tested here?

A) **Service-layer structural assertion owned here** (no UPDATE/DELETE API — a unit test) **+ the DB-role grant is a
   `database`-unit deliverable REFERENCED here**, verified by an **integration test** against real Postgres (Docker):
   the write role is `INSERT`-only and the auditor role read-only → `UPDATE`/`DELETE` on a committed record **raises a
   permission error**. audit-store **owns the behavioral assertion**; `database` owns the grant DDL (reference-not-own).
   *(Recommended.)*
B) audit-store authors the role-grant DDL itself (would overlap the `database` unit's ownership).
C) Other (describe).

[Answer]: A — service-layer structural assertion (no UPDATE/DELETE API) owned here + the DB-role grant is a database-unit deliverable referenced here, verified by an integration test against real Postgres (write role INSERT-only, auditor read-only, UPDATE/DELETE raises a permission error). audit-store owns the behavioral assertion; database owns the grant DDL.

## Question 4 — Atomicity mechanism + test
BR-PERSIST-ATOMIC = commit + audit-write are one atomic op (both-or-neither). What is the target + test?

A) **Single DB transaction** boundary in the service (one `BEGIN … COMMIT`); the NFR **target** is the observable
   **both-or-neither** behavior (the mechanism detail is refined at NFR Design). Test: an **injected fault** after the
   decision row / before the audit row → **full rollback** (0 committed decisions, 0 audit records); happy path → exactly
   one of each. *(Recommended — target = behavior, tested by fault injection.)*
B) Application-level compensating writes (non-transactional) — weaker; rejected unless justified.
C) Other (describe).

[Answer]: A — single DB transaction boundary in the service; the NFR target is the observable both-or-neither behavior (mechanism refined at NFR Design). Tested by injected fault after the decision row / before the audit row → full rollback; happy path → exactly one of each.

## Question 5 — `decision_id` generation (determinism seam)
`decision_id` is a system-generated PK. How is it generated + kept test-deterministic?

A) **Injected id-generator seam** (constructor/param — like intake's `application_id` generator and rules-engine's
   injected `engine_version`): **UUID in production**, a deterministic fake in tests. `decision_id` is **audit metadata,
   NOT part of the replay equality set**, so it never threatens replay determinism; the seam only keeps tests clean +
   avoids wall-clock/global state in the service. *(Recommended.)*
B) Generate inline (e.g. `uuid4()` called directly) — non-injected; harder to test deterministically.
C) Other (describe).

[Answer]: A — injected id-generator seam (constructor/param, like intake's application_id and rules-engine's injected engine_version): UUID in production, deterministic fake in tests. decision_id is audit metadata, not in the replay equality set.

## Question 6 — CANON-SER reuse (reference-not-own)
How does audit-store serialize `rule_results` + `profile_canonical`?

A) **Reference the shared `backend/common/canon_ser.py` UNCHANGED** for both, via an **audit-store-local adapter**
   (the `CanonSerAdapter`/`RulebookCanonAdapter` precedent). audit-store is the **spec authority** for §2.1 but
   `backend/common/` is the shared **location**; **no fork, no §2.1 change, no re-declaration**. `content_hash` =
   `sha256(CANON-SER bytes)`. *(Recommended — single convention across intake / rules-engine / audit-store.)*
B) audit-store re-declares its own serializer (rejected — would fork CANON-SER and risk replay-comparison drift).
C) Other (describe).

[Answer]: A — reference the shared backend/common/canon_ser.py unchanged for both rule_results and profile_canonical, via an audit-store-local adapter. audit-store is the §2.1 spec authority; backend/common/ is only the shared location. No fork, no re-declaration. content_hash = sha256(CANON-SER bytes).

## Question 7 — DB access layer + Postgres test strategy
What is the persistence access layer, and how are Postgres-touching targets tested (DATA-5, no SQLite)?

A) **SQLAlchemy 2.x (Core or thin ORM) over psycopg** for the audit-store service + record model + queries; **real
   Postgres via Docker / testcontainers in CI** for the DB-role / atomicity / append-only integration tests; the pure
   predicate + projection logic is unit-tested behind a **repository abstraction** (an in-memory fake) so those tests
   need no DB. `database` unit owns provisioning/migrations. *(Recommended — DATA-5 honored, fast unit tests + real-PG
   integration tests.)*
B) Raw `psycopg` SQL, no ORM.
C) Other (describe).

[Answer]: A — SQLAlchemy 2.x over psycopg for the service + record model + queries; real Postgres via Docker/testcontainers in CI for DB-role/atomicity/append-only integration tests; pure predicate + projection logic unit-tested behind a repository abstraction (in-memory fake). database unit owns provisioning/migrations.

## Question 8 — SEC-5 audit trail vs observability telemetry (distinct surfaces)
Confirm the two are distinct.

A) **Distinct**: the **persisted `AuditRecord` history IS the SEC-5 audit trail** (queried by `AuditService`; deliberately
   carries the full record incl. the segregated demographics snapshot — safe, storage≠influence); **observability
   telemetry is a separate emit-only allowlist** surface with **no demographic/free-text field** (OBS-1). *(Recommended.)*
B) Fold both into one channel (rejected — conflates the audit trail with metrics; risks demographic leakage into telemetry).
C) Other (describe).

[Answer]: A — distinct: the persisted AuditRecord history IS the SEC-5 audit trail (full record incl. segregated demographics snapshot — safe, storage≠influence); observability telemetry is a separate emit-only allowlist surface with no demographic/free-text field (OBS-1).

## Question 9 — `ApplicantProfileSnapshot` round-trip (reference-not-own intake)
How is the snapshot's profile shape governed + tested?

A) **intake's `ApplicantProfile` contract governs** — audit-store **imports** it, serializes via CANON-SER, and
   **deserializes back to the exact intake object** (not a re-declared parallel field list). Target: **round-trip
   fidelity** (persist → load → `== original`) is a testable NFR. *(Recommended — reference-not-own.)*
B) Re-declare the profile fields in audit-store (rejected — drift risk vs intake's schema).
C) Other (describe).

[Answer]: A — intake's ApplicantProfile contract governs; audit-store imports it, serializes via CANON-SER, deserializes back to the exact intake object (not a re-declared parallel field list). Round-trip fidelity (persist → load → == original) is a testable NFR.

## Question 10 — Depth confirmation
Confirm the NFR-Requirements depth.

A) **Comprehensive** — audit-store is an invariant-bearing deterministic-core / audit unit (CON-BR4 + CON-AUDIT-1 +
   SEC-4/5), same class as `intake` / `rules-engine`. *(Recommended.)*
B) Lighter depth (describe justification).
C) Other (describe).

[Answer]: A — comprehensive. audit-store is an invariant-bearing deterministic-core/audit unit (CON-BR4 + CON-AUDIT-1 + SEC-4/5), same class as intake/rules-engine.

## Question 11 — Performance / observability scope
Confirm the perf/obs posture.

A) **Soft-budget, observed-not-gated** for commit + replay (correctness/auditability/determinism take precedence; no hard
   latency gate — mirrors rules-engine PERF-1) **+ emit-only allowlist telemetry** (OBS-1, demographic-free), distinct
   from the SEC-5 audit trail. *(Recommended.)*
B) A hard latency gate on commit/replay (describe justification).
C) Other (describe).

[Answer]: A — soft-budget, observed-not-gated for commit + replay (correctness/auditability/determinism take precedence, no hard latency gate, mirrors rules-engine PERF-1) + emit-only allowlist telemetry (OBS-1, demographic-free), distinct from the SEC-5 audit trail.

---

## 4. Story traceability (targets ↔ stories)
| Story / invariant | Draft target(s) |
|---|---|
| US-PLAT-8 (commit gate, CON-BR4) | NFR-AUDIT-GATE-1, NFR-AUDIT-AUTHZ-1 |
| CON-AUDIT-1 (persist + 6-tuple + replay) | NFR-AUDIT-ATOMIC-1, NFR-AUDIT-TUPLE-1, NFR-AUDIT-REPLAY-1/-2 |
| US-PLAT-2 (auditor read-only history) | NFR-AUDIT-READ-1, NFR-AUDIT-LOG-1, NFR-AUDIT-APPEND-1 |
| US-RULES-4 (replay a past decision) | NFR-AUDIT-REPLAY-1/-2, NFR-AUDIT-CANON-1 |
| SEC-4 / SEC-5 | NFR-AUDIT-AUTHZ-1, NFR-AUDIT-APPEND-1, NFR-AUDIT-READ-1, NFR-AUDIT-LOG-1 |
| CON-BR1 (storage ≠ influence) | NFR-AUDIT-BR1-1 |
| OOS-7 seam (append-only supersession) | NFR-AUDIT-STATUS-1, NFR-AUDIT-APPEND-1 |

## 5. Constraints & settled items held (not re-opened)
- **Frozen FD + frozen C5 contract** are the inputs — NFR Requirements pins **testable targets ON** them, re-opening none.
- **Reference-not-own**: rules-engine `evaluate()` + `RuleResultReport` + `evaluation_output` projection; shared CANON-SER
  (`backend/common/canon_ser.py`, unchanged) + `decimal_context`; intake's `ApplicantProfile`; `database` provisioning /
  migrations / role-grants; `auth-rbac` policy; observability stack; `quality-gates` verification; `memo-agent-core`
  `memo_hash`/`model_version`.
- **No LLM anywhere in audit-store** (replay re-evaluates rules only; memo integrity = `memo_hash` comparison).
- **DATA-5** PostgreSQL (no SQLite); **DATA-4** synthetic only. Runtime **Python 3.12**.
- **OOS-7 / OOS-8** are Phase-3 (seam reserved / detection-only now) — settled, not re-opened.
- Deferred production-rulebook authoring (rules-engine) remains tracked — unrelated to this unit.

## 6. Next step (STOP here)
Fill the eleven `[Answer]:` tags above. On your signal I will read the answers, run the mandatory ambiguity-check
(adding a clarification file only if needed), then **generate Part 2** — `nfr-requirements.md` (the finalized
`NFR-AUDIT-*` pass/fail targets) + `tech-stack-decisions.md` — and stop at the NFR-Requirements 2-option gate.
**NO NFR-Requirements artifacts are generated until the answers are in, checked, and you give the explicit go.**
