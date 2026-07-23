# Code Generation Plan (Part 1) — `audit-store` (C5 / U12)

**Phase / Stage**: BUILD → Code Generation, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: cluster unit **3 of 4** · FD ✅ · NFR Requirements ✅ · NFR Design ✅ · **Infrastructure Design
SKIPPED (logged 2026-07-05)** → **Code-Gen ← here — the THIRD unit's code** (after `intake`+`document-sanitizer` and
`rules-engine`, both COMPLETE).
**Unit**: U12 `audit-store` — the CON-BR4 write-gate, append-only audit persistence, replay-as-detection, auditor read-only surface.
**Stories**: US-PLAT-8 (commit gate), US-PLAT-2 (auditor read-only history), US-RULES-4 (replay a past decision).
**Date**: 2026-07-05 · **Runtime**: Python **3.12 pinned** (venv on 3.12.10).
**Status**: **Plan — awaiting `[Answer]:` tags. NO CODE, NO TESTS, NO IMPLEMENTATION this stage. Stop after this plan.**

This plan follows `.project-guide-rule-details/build/code-generation.md` (Part 1) + the project's plan-then-generate
discipline. **TDD is binding** (QA-6, pytest-cov ≥ 90%): **tests FIRST, then implementation**. Code-Gen **builds ON** the
frozen C5 contract, the frozen FD, the approved `NFR-AUDIT-*` targets, the NFR design patterns, and the 6 logical
components — **re-opening none of them.** **Reference-not-own throughout.**

---

## 1. Unit context (analyzed)

### 1.1 What Code-Gen builds on (frozen — NOT re-opened)
- **C5 contract** (`component-methods.md`): `DecisionCommitService.commit(recommendation_id, underwriter_id, action,
  reason=None) -> CommittedDecision`; `AuditStore.persist(audit_tuple) -> None`; `ReplayService.replay(decision_id) ->
  RuleResultReport`; `AuthRBAC.authorize(user, action) -> bool`.
- **FD**: the `AuditRecord` superset (6-tuple `AuditTuple` + `CommittedDecision` + `ApplicantProfileSnapshot` + OOS-7 seam);
  BR-COMMIT-GATE / BR-AUTHZ-RECHECK / BR-PERSIST-ATOMIC / BR-APPEND-ONLY / BR-STATUS-WRITE-ONCE / BR-AUDIT-READ /
  BR-REPLAY-*; the single CANON-SER §2.1.
- **NFR targets** (14 `NFR-AUDIT-*`): GATE-1, AUTHZ-1, ATOMIC-1, TUPLE-1, APPEND-1, STATUS-1, REPLAY-1, REPLAY-2, BR1-1,
  READ-1, LOG-1, CANON-1, PERF-1, OBS-1.
- **NFR patterns + 6 components** (`nfr-design/`): DecisionCommitService, AuditStore (repository — insert+read only),
  ReplayService, AuditService, CanonSerAdapter, TelemetryEmitter (+ referenced AuthRBAC, injected `decision_id` generator),
  incl. the **2 sharpenings** (ATOMIC-1 co-location constraint on `database`; assemble+validate-**before**-BEGIN at the
  repository/unit-of-work seam).

### 1.2 Dependencies & interfaces (reference-not-own)
- **Imports read-only**: rules-engine `evaluate()` (via its `RulesEngine`) + `evaluation_output()` + `RuleResultReport`
  (`backend/rules_engine/`); intake's `ApplicantProfile` (`backend/intake/schema.py`); shared `backend/common/canon_ser.py`
  + `decimal_context.py` (**unchanged**).
- **Referenced (not authored here)**: `database` PostgreSQL **schema / migrations / role-grant DDL** (`audit_writer`
  INSERT-only + `audit_reader` SELECT-only) — see Q2/Q8; `auth-rbac` `AuthRBAC.authorize` **policy** (injected `Authorizer`
  seam — Q4); the **orchestrator / pipeline** pending-recommendation context (injected `CommitContextProvider` seam —
  **confirmed 2026-07-05**, §1.5); `observability` stack; `memo-agent-core` `memo_hash`/`model_version` computation
  (persisted here, never computed here).
- **Produces**: persisted `AuditRecord`s (the SEC-5 trail); `CommittedDecision` (commit return); the replay verdict; emitted telemetry.

### 1.3 Monorepo placement (single monorepo — package `audit_store`, underscore)
```
backend/
├── common/                    # shared (EXISTS — imported, unchanged): canon_ser.py, decimal_context.py
├── intake/schema.py           # EXISTS — ApplicantProfile imported read-only
├── rules_engine/              # EXISTS — evaluate()/evaluation_output()/RuleResultReport imported read-only
└── audit_store/               # UNIT: audit-store (C5)
    ├── record_schema.py       #   AuditRecord / AuditTuple / CommittedDecision / ApplicantProfileSnapshot + enums (Pydantic v2, frozen)
    ├── canon_adapter.py       #   CanonSerAdapter (rule_results + profile_canonical -> shared canon_ser; content_hash)
    ├── repository.py          #   AuditRepository Protocol + InMemoryAuditRepository (fake) + the unit-of-work/atomic seam
    ├── commit_service.py      #   DecisionCommitService (CON-BR4 predicate + authz re-check + assemble-before-BEGIN + atomic write)
    ├── replay_service.py      #   ReplayService (load -> deserialize -> rules-engine evaluate() -> evaluation_output() both -> compare)
    ├── audit_service.py       #   AuditService (read-only get/browse + derived-superseded read)
    ├── telemetry.py           #   TelemetryEmitter (allowlist emit-only; no demographic/free-text)
    ├── pg_repository.py        #   PostgresAuditRepository (SQLAlchemy 2.x/psycopg; integration-tested)
    ├── seams.py               #   injected IdGenerator + Clock + Authorizer + CommitContextProvider protocols (+ prod/fake impls)
    └── tests/                 #   co-located; unit (fake) + integration (testcontainers) + the interim/TEST-only DDL fixture
```
*(Exact module split refined at generation; the mapping above is the plan of record.)*

### 1.4 Guardrails held (skill)
- **CON-BR4** (no unaccountable committed decision); **CON-AUDIT-1** (atomic 6-tuple persist + append-only + replay);
  **CON-BR1** (storage ≠ influence — snapshot stores demographics, `evaluate()` excludes them); **CON-DET-1** (replay
  determinism — CANON-SER + excluded volatile/forensic, no false mismatch); **advisory-only** (`action` is the one correct
  use of "decision"); **DATA-4** (synthetic only); **DATA-5** (PostgreSQL, no SQLite). **No LLM anywhere in audit-store.**

### 1.5 `CommitContextProvider` seam (confirmed 2026-07-05 — resolves the commit-context delivery gap)
The frozen `commit(recommendation_id, underwriter_id, action, reason=None)` carries only the **4 human-gate fields**, and
`AuditStore.persist(audit_tuple)` takes a **pre-built tuple** — but `AuditRecord` assembly (TUPLE-1) needs the **6
`AuditTuple` fields + the original `ApplicantProfile`** for that `recommendation_id`. FD §2 notes these as extra inputs but
does not pin their delivery. **Resolution — a 4th injected seam** (analogous to `Authorizer` / `RulesEngine`; keeps every
frozen signature unchanged):

> **`CommitContextProvider.get(recommendation_id) -> CommitContext{rule_results, memo_hash, model_version, engine_version,
> rulebook_version, applicant_profile}`** — **owned by the orchestrator / pipeline** (which just produced that output),
> **referenced-not-owned** by audit-store. `commit()` keeps its **frozen 4-parameter signature**; it fetches the context
> **internally** via the injected provider. A **fake provider drives the unit tests** (Step 5) — **no real orchestrator
> needed yet**, the same non-blocking pattern as `Authorizer` / `RulesEngine`. audit-store owns the **Protocol + the
> assembly**, never the pending-recommendation source.

---

## 2. Code-Generation execution plan (numbered steps — TDD, tests FIRST)

**Discipline**: each component's test suite is written **before** its implementation, encoding the mapped `NFR-AUDIT-*`
target(s) + FD rule(s). **Leaf-first, then composing components.** App code → `backend/audit_store/…`; markdown summary →
`guide-docs/build/audit-store/code/`.

- [x] **Step 0 — Package skeleton + deps**: create `backend/audit_store/` + co-located `tests/`; extend the root
  `pyproject.toml` cov to `backend/audit_store`; add deps `SQLAlchemy>=2.0`, `psycopg[binary]`, `testcontainers[postgresql]`
  (test-only); add an **`integration` pytest marker** (requires Docker/Postgres — **auto-skipped when unavailable**, run in
  CI; mirrors intake's `posix_only`). *(No app code — skeleton + config.)*
- [x] **Step 1 — `record_schema.py` (data models, leaf)**: TEST FIRST (Pydantic v2 `frozen`/`extra=forbid`; closed enums
  `status∈{active,superseded}`, `action∈{approve,override}`; `AuditRecord` embeds `AuditTuple` + `CommittedDecision` +
  `ApplicantProfileSnapshot` + seam; 6-tuple non-null) → implement the frozen FD superset. Maps: TUPLE-1; FD
  `domain-entities.md §2–§5`.
- [x] **Step 2 — `canon_adapter.py` (CanonSerAdapter, composes shared canon_ser)**: TEST FIRST (round-trip fidelity for
  both `rule_results` + `profile_canonical`; `content_hash = sha256(canon bytes)` tamper-evidence; delegates to the
  **unchanged** shared util — bytes equal `common.canon_ser.canon_ser`) → implement. Maps: CANON-1.
- [x] **Step 3 — `seams.py` (injected seams, leaf)**: TEST FIRST (`IdGenerator` → deterministic fake vs UUID; `Clock` →
  fixed fake vs real; **`Authorizer` Protocol** `authorize(user_id, rbac_action) -> bool` referencing `AuthRBAC.authorize`
  — the `rbac_action` param is the **RBAC operation** (e.g. a `"commit"`/write permission), **named distinctly from
  `CommittedDecision.action` (approve/override)** so the two are never conflated [sharpening 2]; **`CommitContextProvider`
  Protocol** `get(recommendation_id) -> CommitContext` [§1.5] with a fake) → implement the seam protocols + prod/fake impls.
  Maps: the determinism / reference-not-own seams (Q3/Q4 + the §1.5 provider).
- [x] **Step 4 — `repository.py` (AuditRepository Protocol + in-memory fake + unit-of-work seam)**: TEST FIRST (the fake
  supports insert + read **only** — no update/delete method; the `atomic()`/unit-of-work context; a fault-injection hook
  for ATOMIC-1) → implement. Maps: APPEND-1 (service-layer structural), the ATOMIC-1 boundary seam.
- [x] **Step 5 — `commit_service.py` (DecisionCommitService)**: TEST FIRST (**GATE-1** exhaustive negative matrix +
  Hypothesis ∀ blank/whitespace reason; **AUTHZ-1** auditor-role → reject via the injected `Authorizer` — called with the
  RBAC `rbac_action` [not the commit `action`]; **context fetch** — `commit` fetches the pending-recommendation context via
  the injected **`CommitContextProvider`** [§1.5, a **fake provider** in tests — no real orchestrator needed], keeping its
  **frozen 4-param signature**; **TUPLE-1** assemble-complete-**before**-BEGIN from the 4 gate fields + the fetched context
  + the seams [validation failure opens no txn]; **ATOMIC-1** both-or-neither via the fake's fault-injection [reject→0,
  accept→1 logical record, fault→rollback]) → implement gate predicate + authz re-check + context fetch + assembly + atomic
  write via the repository. Maps: GATE-1, AUTHZ-1, TUPLE-1, ATOMIC-1 (behavioral, on the fake).
- [x] **Step 6 — `replay_service.py` (ReplayService)**: TEST FIRST (**REPLAY-2** loads + deserializes `profile_canonical`
  → exact intake `ApplicantProfile`, calls injected rules-engine `evaluate()` [imported, not reimplemented], no LLM/no
  re-draft/no re-commit, ×N byte-identical; **REPLAY-1** applies rules-engine's imported `evaluation_output()` to **both**
  the deserialized recorded report + the fresh report [single-sourced], match / engine_version+content_hash-only diff →
  still match / genuine diff → blocking mismatch + forensic delta; **BR1-1** bias-swap-on-snapshot → delta 0) → implement.
  Maps: REPLAY-1, REPLAY-2, BR1-1.
- [x] **Step 7 — `audit_service.py` (AuditService, read-only)**: TEST FIRST (**READ-1** get-by-`decision_id` + browse-history,
  **no write method**; **STATUS-1** derived-superseded read over the reserved `supersedes_decision_id` ONLY [Phase-1/2 →
  always `active`]; **LOG-1** every committed decision retrievable) → implement read-only queries. Maps: READ-1, LOG-1, STATUS-1.
- [x] **Step 8 — `telemetry.py` (TelemetryEmitter)**: TEST FIRST (**OBS-1** allowlist schema — no applicant-profile/
  demographic/free-text field, schema-level assertion; **PERF-1** commit/replay timing emitted, never gated; distinct from
  the audit trail) → implement. Maps: OBS-1, PERF-1.
- [x] **Step 9 — `pg_repository.py` (PostgresAuditRepository, SQLAlchemy 2.x/psycopg) + the interim/TEST-only DDL fixture**:
  TEST FIRST (**integration**, `@pytest.mark.integration`, real Postgres via testcontainers): implement the Postgres impl
  behind the same `AuditRepository` Protocol; the **test-fixture DDL** (the `audit_record` + separate
  `applicant_profile_snapshot` child tables + the `audit_writer`/`audit_reader` roles + grants) **lives under `tests/`
  (NOT a `migrations/` dir) with a banner comment** [sharpening 1]: *the 2-table normalized shape is a **test-harness
  choice to exercise multi-row atomicity (ATOMIC-1), NOT a prescription** of the production schema — the production shape
  (single-table vs normalized) is the `database` unit's call, bound only by the co-location constraint*. **Clearly marked
  NOT production DDL.** Maps: (drives the Step-10 integration targets).
- [x] **Step 10 — Integration tests (testcontainers, real Postgres — DATA-5)**: **ATOMIC-1** (fault injected mid-persist →
  full rollback of the multi-row write, both-or-neither — meaningful on the normalized interim schema, Q8); **APPEND-1**
  (connect as `audit_writer`/`audit_reader` → `UPDATE`/`DELETE` raises insufficient-privilege); **READ-1/LOG-1** (auditor
  read-only end-to-end); **TUPLE-1-persisted** (full record round-trips). Maps: ATOMIC-1, APPEND-1, READ-1, LOG-1, TUPLE-1.
- [x] **Step 11 — Coverage gate + documentation**: confirm pytest-cov **≥90%** for the unit on Python 3.12 (unit tier
  reaches the gate; `pg_repository.py` is **CI-covered via integration** and/or `omit`-ed like intake's `parse_worker`);
  write the **code summary** to `guide-docs/build/audit-store/code/` (modules, tests→target map, coverage).
- [x] **Step 12 — Present the standardized 2-option completion message** (code-generation.md format) → Request Changes /
  Continue → next cluster unit's Code-Gen (`memo-agent-core`, the LAST cluster unit) per the dependency order.

**N/A step-categories** (code-generation.md Step 2 — justified skips, see Q7): **API Layer** (FastAPI orchestrator
composition root — the commit/replay/read endpoints wire these services), **Frontend** (backend unit), **DB provisioning /
migrations / role-grant DDL** (the `database` unit — audit-store references, never authors), **memo_hash computation**
(`memo-agent-core`). This unit generates **business logic + persistence + its tests + a code summary** only.

---

## 3. Clarifying questions (fill each `[Answer]:` tag)

## Question 1 — Test framework + property-based testing
A) **pytest + pytest-cov (≥90%, QA-6) + Hypothesis** (GATE-1 negative-matrix ∀ blank/whitespace reason; REPLAY-1
   projection-invariance ∀ forensic-only diff → still match) + **`testcontainers[postgresql]`** for the real-Postgres
   integration tier; same base toolchain as intake / rules-engine. *(Recommended.)*
B) pytest + pytest-cov only. · C) Other.

[Answer]: A — pytest + pytest-cov (≥90%, QA-6) + Hypothesis (GATE-1 negative-matrix ∀ blank/whitespace reason; REPLAY-1 projection-invariance ∀ forensic-only diff → still match) + testcontainers[postgresql] for the integration tier; same base toolchain as intake/rules-engine.

## Question 2 — Repository fake vs real-Postgres fixture strategy
A) **A repository Protocol with an in-memory fake** (unit tier — pure predicate/assembly/projection/CANON logic) **+ a
   testcontainers real-Postgres fixture** (integration tier — ATOMIC-1/APPEND-1/READ-1/LOG-1/TUPLE-1-persisted). The
   integration DDL (tables + `audit_writer`/`audit_reader` roles+grants) is authored as a **TEST FIXTURE clearly marked
   "NOT production DDL — production owned by the `database` unit"**. *(Recommended — realizes the NFR-Req tier split;
   DATA-5 honored.)*
B) Only real Postgres (no fake) — slower, couples pure-logic tests to the DB. · C) Other.

[Answer]: A — a repository Protocol with an in-memory fake (unit tier) + a testcontainers real-Postgres fixture (integration tier). The integration DDL (tables + audit_writer/audit_reader roles+grants) is a TEST FIXTURE clearly marked "NOT production DDL — production owned by the database unit."

## Question 3 — decision_id + timestamp seams
A) **Both injected** into `DecisionCommitService` — `IdGenerator` (UUID prod / deterministic fake) + `Clock` (real
   `timestamp` prod / fixed fake). `decision_id` + `timestamp` are **audit metadata, NOT in the replay equality set**, so
   they never threaten replay determinism; the seams keep tests deterministic + wall-clock out of the pure logic.
   *(Recommended — mirrors rules-engine's injected `engine_version` / intake's `application_id`.)*
B) Inline `uuid4()` / `datetime.now()` — non-injected, harder to test. · C) Other.

[Answer]: A — both injected into DecisionCommitService: IdGenerator (UUID prod / deterministic fake) + Clock (real timestamp prod / fixed fake). decision_id + timestamp are audit metadata, not in the replay equality set, so they never threaten replay determinism.

## Question 4 — AuthRBAC reference (auth-rbac not yet built)
A) **Inject an `Authorizer` Protocol** (`authorize(user_id, action) -> bool`) referencing `auth-rbac`'s `AuthRBAC.authorize`
   contract; a fake in tests; the **real `auth-rbac` wired at the composition root**. audit-store owns the **re-check call
   site** (AUTHZ-1), never the policy. *(Recommended — reference-not-own; unblocks Code-Gen before auth-rbac exists.)*
B) Import a concrete `auth-rbac` class now (rejected — auth-rbac not built; would couple/duplicate). · C) Other.

[Answer]: A — inject an Authorizer Protocol (authorize(user_id, action) -> bool) referencing auth-rbac's AuthRBAC.authorize contract; a fake in tests; the real auth-rbac wired at the composition root. audit-store owns the re-check call site, never the policy.

## Question 5 — rules-engine `evaluate()` acquisition in ReplayService
A) **Inject a rules-engine `RulesEngine` instance** (or an `evaluate` callable) into `ReplayService`, and **import**
   `evaluation_output()` + `RuleResultReport` from `backend.rules_engine` — **reference-not-own, no reimplementation**.
   Tests inject a **real `RulesEngine`** over a test rulebook (rules-engine's own representative rulebook) so replay is a
   genuine end-to-end re-evaluation. *(Recommended.)*
B) Re-instantiate rules-engine internals inside audit-store (rejected — reimplementation/coupling). · C) Other.

[Answer]: A — inject a rules-engine RulesEngine instance (or an evaluate callable) into ReplayService, and import evaluation_output() + RuleResultReport from backend.rules_engine — reference-not-own, no reimplementation. Tests inject a real RulesEngine over rules-engine's own representative rulebook so replay is a genuine end-to-end re-evaluation.

## Question 6 — Module placement + shared-utility reference
A) **`backend/audit_store/`** (underscore), the 6 components mapped to modules (§1.3); **imports** rules-engine
   `evaluate()`/`evaluation_output()`/`RuleResultReport`, intake `ApplicantProfile`, and shared `canon_ser`/`decimal_context`
   **read-only, unchanged**; the `CanonSerAdapter` is audit-store-local. No shared-code edit. *(Recommended.)*
B) A different placement / re-declare a shared utility (rejected — reference-not-own). · C) Other.

[Answer]: A — backend/audit_store/ (underscore), the 6 components mapped to modules per §1.3; imports rules-engine evaluate()/evaluation_output()/RuleResultReport, intake ApplicantProfile, and shared canon_ser/decimal_context read-only, unchanged. CanonSerAdapter is audit-store-local. No shared-code edit.

## Question 7 — Confirm the N/A step-categories
A) **Confirm N/A**: **API Layer** = FastAPI orchestrator composition root; **Frontend** = backend unit; **DB provisioning/
   migrations/role-grant DDL** = the `database` unit (referenced); **memo_hash computation** = `memo-agent-core`. This unit
   generates **business logic + persistence + tests + a code summary** only. *(Recommended.)*
B) Some apply (describe). · C) Other.

[Answer]: A — confirm N/A: API Layer = FastAPI orchestrator composition root; Frontend = backend unit; DB provisioning/migrations/role-grant DDL = the database unit (referenced); memo_hash computation = memo-agent-core. This unit generates business logic + persistence + tests + a code summary only.

## Question 8 — Interim/TEST schema shape (for the repository + testcontainers)
The production schema/normalization is the `database` unit's. What shape does the **interim/TEST** schema take so ATOMIC-1
is **meaningfully** tested?
A) **Normalized interim/TEST schema** — an `audit_record` table **+ a separate `applicant_profile_snapshot` child row**
   (FK), co-located in one Postgres DB. This makes the ATOMIC-1 fault-injection a **genuine multi-row both-or-neither** test
   (fault between the two writes → both roll back), and directly exercises the co-location constraint. **Clearly marked
   TEST/interim — production normalization is the `database` unit's call** (it must keep them co-located per the cross-unit
   constraint). *(Recommended — a meaningful atomicity test.)*
B) Single-table JSONB superset (one row) — atomicity becomes trivial (one write); weaker ATOMIC-1 test. · C) Other.

[Answer]: A — normalized interim/TEST schema: an audit_record table + a separate applicant_profile_snapshot child row (FK), co-located in one Postgres DB. This makes the ATOMIC-1 fault-injection a genuine multi-row both-or-neither test and directly exercises the co-location constraint. Clearly marked TEST/interim — production normalization is the database unit's call, and it must keep them co-located per the cross-unit constraint.

## Question 9 — SQLAlchemy Core vs ORM
A) **SQLAlchemy 2.x Core** (explicit `Table` + `insert`/`select`) with the frozen **Pydantic** `record_schema` models at
   the boundary (Core rows ↔ Pydantic) — **no double-modeling** of the frozen shapes, explicit SQL/transaction control for
   ATOMIC-1. *(Recommended.)*
B) SQLAlchemy declarative ORM (a second model layer alongside Pydantic — duplication risk). · C) Other.

[Answer]: A — SQLAlchemy 2.x Core (explicit Table + insert/select) with the frozen Pydantic record_schema models at the boundary (Core rows ↔ Pydantic) — no double-modeling of the frozen shapes, explicit SQL/transaction control for ATOMIC-1.

---

## 4. Story traceability
| Story | Covered by (steps) |
|---|---|
| US-PLAT-8 (commit gate, CON-BR4) | Steps 5 (GATE-1/AUTHZ-1/TUPLE-1/ATOMIC-1), 10 (ATOMIC-1 integration) |
| US-PLAT-2 (auditor read-only history) | Steps 7 (READ-1/LOG-1/STATUS-1), 9–10 (APPEND-1/READ-1 integration) |
| US-RULES-4 (replay a past decision) | Steps 6 (REPLAY-1/-2/BR1-1), 2 (CANON-1) |

> The **`CommitContextProvider` seam** (§1.5) supplies the assembly inputs for **TUPLE-1 + ATOMIC-1** at Step 5 — it is the
> reference-not-own delivery of the pending-recommendation context (tuple fields + `ApplicantProfile`) that the frozen
> `commit` signature leaves open; tested via a fake provider (no orchestrator dependency).

## 5. Constraints & settled items held (not re-opened)
- **Frozen C5 contract + FD + approved NFR targets + patterns + 6 components** are the inputs — Code-Gen implements them
  exactly; re-opens none.
- **TDD binding**: tests FIRST, pytest-cov ≥ 90% (QA-6), on **Python 3.12**. No code this stage.
- **Reference-not-own**: rules-engine `evaluate()`/`evaluation_output()`/`RuleResultReport` (imported); intake
  `ApplicantProfile` (imported); shared CANON-SER (`backend/common/canon_ser.py`, unchanged) + `decimal_context`;
  `database` schema/migrations/grants (referenced, TEST-only DDL marked as such); `auth-rbac` policy (injected `Authorizer`);
  the **orchestrator/pipeline** pending-recommendation context (injected `CommitContextProvider`, §1.5); observability
  stack; `memo-agent-core` `memo_hash` computation. **Infrastructure Design SKIPPED (logged).**
- **Carry-forward (memo-hash verification ownership)**: BR-REPLAY-NO-MEMO's "memo integrity = `memo_hash` recompute-and-
  compare" belongs to **`memo-agent-core`** (it holds the memo text + computes the hash). audit-store **stores** `memo_hash`
  (TUPLE-1) and **never recomputes** it (it has no memo text); its `ReplayService` correctly re-evaluates rules only
  (REPLAY-2). Recorded in the cross-unit constraints register so memo-agent-core owns it at its Code-Gen.
- **ATOMIC-1 co-location constraint** on the `database` unit recorded in the cross-unit constraints register — honored (not
  re-decided) here.
- **No LLM anywhere.** Advisory-only vocabulary (`action` is the sole correct "decision").

## 6. Next step (STOP here)
Fill the nine `[Answer]:` tags above. On your signal I will read the answers, run the mandatory ambiguity-check (adding a
clarification file only if needed), then **execute Part 2 (Generation)** — tests FIRST, then implementation, step-by-step
per §2, and present the standardized 2-option completion message. **NO code, NO tests, NO implementation is written until
the answers are in, checked, and you give the explicit go.**
