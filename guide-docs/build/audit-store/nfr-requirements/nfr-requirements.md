# NFR Requirements — `audit-store` (C5 / U12)

**Stage**: BUILD → NFR Requirements (per-unit) · cluster unit **3 of 4**
**Unit**: U12 `audit-store` — the CON-BR4 write-gate, append-only audit persistence, replay-as-detection, auditor read-only surface.
**Date**: 2026-07-05 · **Runtime**: Python **3.12 pinned** (D6/D8) · **Depth**: comprehensive (invariant-bearing audit unit).
**Status**: Part 2 (Generation) — finalized `NFR-AUDIT-*` targets. Awaiting the NFR-Requirements 2-option gate.

Built **ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`) and the frozen C5
contract (`component-methods.md`: `DecisionCommitService.commit`, `AuditStore.persist`, `ReplayService.replay`,
`AuthRBAC.authorize`) — **re-opening neither**. Every target below is a **pass/fail testable assertion**. Toolchain:
**pytest + pytest-cov (≥90%, QA-6) + Hypothesis** for the universal-quantifier invariants; **real Postgres
(Docker/testcontainers)** for DB-touching targets, **repository-abstraction fakes** for pure-logic unit tests (§5).

---

## 1. Scope & the reference-not-own boundary

`audit-store` **owns**: the `DecisionCommitService` write-gate + authz re-check, the atomic assemble+persist of the
`AuditRecord` superset, append-only enforcement (service layer + the behavioral DB-role assertion), the `AuditService`
read-only surface, the `ReplayService` orchestration + the replay equality-set **projection**, and the audit-store-local
CANON-SER adapter. **Referenced, not owned**:

- `rules-engine` (COMPLETE) — its **pure `evaluate()`**, its `RuleResultReport`, and its **`evaluation_output()`
  projection** (`backend/rules_engine/report.py`) are **called/consumed**, never reimplemented.
- `intake` (COMPLETE) — its `ApplicantProfile` **governs** the snapshot shape (imported, not re-declared).
- shared **`backend/common/canon_ser.py`** — the single CANON-SER; audit-store is the **§2.1 spec authority**, but
  `backend/common/` is the shared **location** (unchanged, no fork); `decimal_context.py` likewise.
- `database` unit — PostgreSQL **provisioning / migrations / role-grant DDL** (DATA-5).
- `auth-rbac` — the `AuthRBAC.authorize` **policy** (audit-store owns only the commit-time **re-check enforcement point**).
- `observability` (stack), `quality-gates` (blocking bias-swap/calibration aggregation), `memo-agent-core`
  (`memo_hash` / `model_version` — persisted here, never computed here).

**No LLM anywhere in audit-store.** Replay re-evaluates rules only; memo integrity = `memo_hash` comparison.

---

## 2. Finalized `NFR-AUDIT-*` targets (pass/fail testable)

### CON-BR4 — commit write-gate

**NFR-AUDIT-GATE-1** — *Commit predicate is a total function over the closed negative matrix.*
Realizes **BR-COMMIT-GATE** (`business-rules.md §1`). `commit` **REJECTS iff**: `underwriter_id` missing/empty **OR**
`action` missing **OR** `action ∉ {approve, override}` **OR** (`action == override` **AND** `trim(reason) == ""`).
**PASS/FAIL test**: an **exhaustive negative matrix** — each clause independently, incl. a **whitespace-only** (`"  \t "`)
override reason and `null` reason — every case → **reject**; the **accept** cases (`approve` with no reason;
`override` with a non-blank reason) → **accept**. **Hypothesis ∀**: for all blank/whitespace strings, an `override`
with that reason is rejected. **Property asserted**: no accepted commit is unaccountable (carries WHO + WHAT +
WHY-on-override / endorsement-on-approve). *(Unit — pure predicate, repository fake.)*

**NFR-AUDIT-AUTHZ-1** — *Backend authz re-check is independent of the API layer.*
Realizes **BR-AUTHZ-RECHECK** (SEC-4). `commit` independently re-checks the committer holds the underwriter role at the
service boundary. **PASS/FAIL test**: drive `commit` with an **auditor-role** id while the API-layer authz is
bypassed/stubbed → **reject at the service** (the last line of defense-in-depth). An underwriter-role id passes the
re-check. *(Unit — `AuthRBAC.authorize` faked; the enforcement point is audit-store's.)*

### CON-AUDIT-1 — atomic persist + tuple completeness

**NFR-AUDIT-ATOMIC-1** — *Commit + audit persistence are both-or-neither (decomposition-agnostic).* **[Sharpening 1]**
Realizes **BR-PERSIST-ATOMIC** (`business-rules.md §2`). The target is the **observable both-or-neither behavior**, **not**
a specific transaction mechanism (mechanism deferred to NFR Design). **PASS/FAIL test**: (a) a **rejected** gate →
**zero** trace (no committed decision, no `AuditRecord`); (b) an **accepted** commit → **exactly one logical
`AuditRecord`** (whatever physical decomposition NFR Design chooses — a single superset row **or** normalized tables such
as a separate `ApplicantProfileSnapshot` row — **all-or-nothing** together); (c) an **injected fault at *any* step** of
assemble+persist (after any partial write, before completion) → **full rollback, zero trace** — no partial `AuditRecord`,
no orphan snapshot row. The assertion never presumes a two-row "decision row / audit row" split. *(Integration — real
Postgres; fault injected via the repository seam.)*

**NFR-AUDIT-TUPLE-1** — *Every persisted record carries the complete 6-tuple + snapshot + linkage + seam.*
Realizes CON-AUDIT-1 / `domain-entities.md §2–§4`. **PASS/FAIL test**: a committed `AuditRecord` has all six
`AuditTuple` fields (`rulebook_version`, `rule_results`, `timestamp`, `model_version`, `memo_hash`, `engine_version`)
**non-null**, plus the `ApplicantProfileSnapshot` (`application_id`, `profile_canonical`, `content_hash`), the
`CommittedDecision` linkage, and the seam (`status == active`, `supersedes_decision_id is null`). Absence of any → test
fails. *(Unit + integration.)*

### Append-only (CON-AUDIT-1 / SEC-5)

**NFR-AUDIT-APPEND-1** — *Append-only at two layers; the DB-role half references the `database` unit's real grant.* **[Sharpening 2]**
Realizes **BR-APPEND-ONLY** (`business-rules.md §3`). **PASS/FAIL test**: (a) **service layer** — a structural assertion
that `audit-store` exposes **no UPDATE and no DELETE** API on a committed record (only insert + read); introspect the
service/repository surface → no mutation method. (b) **DB-role layer** — an **integration test against real Postgres**
that connects as the **write role `audit_writer` (INSERT-only)** and as the **read-only auditor role `audit_reader`
(SELECT-only)**, and asserts that **`UPDATE`/`DELETE` on a committed `audit_record` raises an insufficient-privilege
error** for both roles. **These two roles + their grants are the `database` unit's real deliverable** (its role-grant
migration) — the audit-store integration test **references that actual artifact as a fixture**, and does **not**
author/duplicate the grant DDL here (reference-not-own; the Q3 boundary). *(Integration — real Postgres, database-unit grants.)*

**NFR-AUDIT-STATUS-1** — *`status` is write-once `active`; superseded-ness is a derived read-time projection.*
Realizes **BR-STATUS-WRITE-ONCE** (`business-rules.md §3`, OOS-7 seam). **PASS/FAIL test**: (a) **no Phase-1/2 code path
writes `status = superseded`** (structural — the write path only ever sets `active`; a negative/introspection assertion);
(b) the **derived-superseded** query is a **pure read** — a record is reported superseded **iff** a newer `AuditRecord`
carries `supersedes_decision_id == that decision_id`; with the Phase-1/2 seam always null, **every record reads
`active`**, and no `active → superseded` in-place UPDATE ever occurs. *(Unit for the projection; integration confirms no
UPDATE path.)*

### Replay (CON-AUDIT-1 + CON-DET-1 boundary)

**NFR-AUDIT-REPLAY-1** — *Replay verdict = equality of the single-sourced evaluation-output projection; volatile/forensic excluded.* **[Sharpening 3]**
Realizes **BR-REPLAY-EQUALITY / -VERDICT** (`business-rules.md §5`). The verdict compares the **evaluation-output
projection only**, **single-sourced** by applying **rules-engine's own `evaluation_output()`** (`backend/rules_engine/
report.py`) to **both** the fresh `evaluate()` report **and** the deserialized recorded `rule_results` — audit-store does
**not** re-derive a parallel projection. The projection = **`{rule_results, recommendation, confidence, decline_reasons,
refer_reasons}`**, over CANON-SER. **`decline_reasons` / `refer_reasons` are included** because they are **pure
canonically-sorted deterministic projections of the per-rule rows** (rules-engine `aggregator.py`: `sorted(f"{rule_id}:
{message}")` over the rows' `outcome_tier`/`rule_id`/`message`) — **permutation-invariant** per rules-engine's **DET-2**
(`test_det2_whole_report_byte_identity_under_any_permutation`), hence **redundant with the rows but consistent**, and
**cannot cause a false mismatch nor hide a real one**. **Excluded** from equality (so they never cause a *false*
mismatch): `timestamp`, `underwriter_id`, `reason`, `memo_hash`, and the provenance fields embedded *inside*
`rule_results` — `rulebook_version` (the replay **load key**), `content_hash`, `engine_version` (**forensic**).
**PASS/FAIL test**: (a) an unchanged record → **match** (reproducibility verified); (b) a record differing **only** in
`engine_version` / `content_hash` → **still match** (an engine refactor / new git SHA must not mass-flag history);
(c) a genuine difference in `rule_results` / `recommendation` / `confidence` → **mismatch (blocking) + forensic delta**
(which rule/field diverged; `engine_version`/`content_hash` drift flags). **Cross-checked field-for-field against
rules-engine's `evaluation_output`.** *(Unit — pure projection over recorded + fresh reports.)*

**NFR-AUDIT-REPLAY-2** — *Replay determinism boundary: pure `evaluate()`, exact profile round-trip, no LLM, no re-commit.*
Realizes **BR-REPLAY-NO-MEMO** + `business-logic-model.md §4`. **PASS/FAIL test**: (a) `ReplayService` **calls
rules-engine's pure `evaluate()`** and has **no evaluation logic of its own** (reference-not-own — asserted structurally);
(b) `profile_canonical` **round-trips through CANON-SER back to the exact intake `ApplicantProfile`** fed to `evaluate()`
(`deserialize(serialize(profile)) == profile`); (c) replay invokes **no LLM** and **never re-drafts the memo** (memo
integrity is a separate `memo_hash` recompute-and-compare); (d) replay **never re-commits / never mutates** the record;
(e) replay ×N of the same `decision_id` is **byte-identical** (deterministic). *(Unit — rules-engine referenced; LLM
absence structural.)*

**NFR-AUDIT-BR1-1** — *Storage ≠ influence: the stored demographics cannot move a replayed result.*
Realizes CON-BR1 (`business-rules.md §6`, `domain-entities.md §4`). The snapshot **stores** the segregated
`demographics`, but `evaluate()` structurally excludes them. **PASS/FAIL test**: a **bias-swap on the snapshot** — take a
committed record, swap the demographic fields (`full_name` / `gender` / `city`) while holding all financial/medical/
lifestyle facts identical, replay → **identical evaluation-output projection (delta = 0)**. *(Unit. Blocking bias-swap
verification is single-sourced in `quality-gates`; this asserts the storage≠influence property at the replay boundary.)*

### SEC-4 / SEC-5 — auditor surface + audit trail

**NFR-AUDIT-READ-1** — *Auditor surface is read-only, backend-enforced, not UI-hidden.*
Realizes **BR-AUDIT-READ** (SEC-4/SEC-5). **PASS/FAIL test**: an **auditor** can read the full 6-tuple + the replay
outcome via `AuditService` (get-by-`decision_id`, browse-history by `application_id` / across cases); **any** write
attempt by an auditor — `commit`, or a raw `UPDATE`/`DELETE` — is **rejected at the backend** (the AUTHZ-1 re-check +
the read-only DB role), **not** merely absent from a UI. *(Integration — real Postgres roles; + unit for the service authz.)*

**NFR-AUDIT-LOG-1** — *The persisted `AuditRecord` history IS the SEC-5 audit trail.*
Realizes SEC-5 (`business-rules.md §4`). **PASS/FAIL test**: every committed decision is **retrievable** in the trail
with its full tuple; browsing by `application_id` returns its decision(s); the trail is **distinct** from observability
telemetry (OBS-1). *(Integration.)*

### CANON-SER / determinism boundary

**NFR-AUDIT-CANON-1** — *One CANON-SER for both `rule_results` and `profile_canonical`; shared util unchanged.*
Realizes `domain-entities.md §2.1`. audit-store uses an **audit-store-local adapter** that delegates to the **unchanged
shared `backend/common/canon_ser.py`** for **both** payloads; `content_hash = sha256(CANON-SER bytes)` is a **pre-replay
integrity check**. **PASS/FAIL test**: (a) `profile_canonical` and `rule_results` round-trip byte-identically; (b)
`content_hash` is **tamper-evident** (a mutated `profile_canonical` → hash mismatch → replay refused); (c) the adapter's
bytes **equal** `backend.common.canon_ser.canon_ser(...)` applied to the same value (delegates to the single shared util,
no fork). *(Unit.)*

### Performance / observability (scoped)

**NFR-AUDIT-PERF-1** — *Commit + replay latency is observed-only (soft budget), never gated.*
Mirrors rules-engine PERF-1. **PASS/FAIL test**: commit/replay **duration is emitted** (telemetry); there is **no
latency-failing check** — a slow operation never raises/aborts. Correctness / auditability / determinism take precedence.
*(Unit — telemetry emission; no gate.)*

**NFR-AUDIT-OBS-1** — *Observability telemetry is emit-only, allowlist, demographic-free — distinct from the audit trail.*
Mirrors rules-engine OBS-1. **PASS/FAIL test**: the telemetry schema **structurally carries no applicant-profile /
demographic / free-text field** (only ids/enums/int counts/timing); a schema-level assertion proves no such field exists.
**Distinct** from the SEC-5 audit trail (which deliberately persists the full record). *(Unit — schema introspection.)*

---

## 3. Target → FD rule / invariant / story traceability

| Target | FD rule | Invariant | Story |
|---|---|---|---|
| NFR-AUDIT-GATE-1 | BR-COMMIT-GATE §1 | CON-BR4 | US-PLAT-8 |
| NFR-AUDIT-AUTHZ-1 | BR-AUTHZ-RECHECK §1 | SEC-4 | US-PLAT-8 |
| NFR-AUDIT-ATOMIC-1 | BR-PERSIST-ATOMIC §2 | CON-AUDIT-1 | US-PLAT-8 |
| NFR-AUDIT-TUPLE-1 | domain-entities §2–§4 | CON-AUDIT-1 | US-PLAT-8 |
| NFR-AUDIT-APPEND-1 | BR-APPEND-ONLY §3 | CON-AUDIT-1 / SEC-5 | US-PLAT-2 |
| NFR-AUDIT-STATUS-1 | BR-STATUS-WRITE-ONCE §3 | CON-AUDIT-1 / OOS-7 | US-PLAT-2 |
| NFR-AUDIT-REPLAY-1 | BR-REPLAY-EQUALITY/-VERDICT §5 | CON-AUDIT-1 / CON-DET-1 | US-RULES-4 |
| NFR-AUDIT-REPLAY-2 | BR-REPLAY-NO-MEMO §5 / logic §4 | CON-AUDIT-1 / CON-DET-1 | US-RULES-4 |
| NFR-AUDIT-BR1-1 | domain-entities §4 / BR §6 | CON-BR1 | US-RULES-4 |
| NFR-AUDIT-READ-1 | BR-AUDIT-READ §4 | SEC-4 / SEC-5 | US-PLAT-2 |
| NFR-AUDIT-LOG-1 | BR-AUDIT-READ §4 | SEC-5 | US-PLAT-2 |
| NFR-AUDIT-CANON-1 | domain-entities §2.1 | CON-DET-1 | US-RULES-4 |
| NFR-AUDIT-PERF-1 | — (scoped) | perf posture | — |
| NFR-AUDIT-OBS-1 | — (scoped) | CON-BR1 / SEC-5 | — |

## 4. Test-tier split (§5 of the plan — DATA-5 honored)
- **Unit** (repository-abstraction fake, no DB): GATE-1, AUTHZ-1, STATUS-1 (projection), REPLAY-1, REPLAY-2, BR1-1,
  CANON-1, OBS-1, PERF-1, TUPLE-1 (assembly).
- **Integration** (real Postgres via Docker/testcontainers, **no SQLite** — DATA-5): ATOMIC-1 (fault injection),
  APPEND-1 (DB-role grants — references the `database` unit's `audit_writer`/`audit_reader` roles), READ-1, LOG-1,
  TUPLE-1 (persisted).

## 5. Extension compliance (Security Guardrails — enabled, scoped)
- **Input validation** — the commit gate is a total function over a closed enum (`action`) + trim-then-empty reason
  (GATE-1); no unvalidated write reaches persistence. **Compliant.**
- **Authz / least privilege** — backend authz re-check (AUTHZ-1) + read-only auditor DB role (APPEND-1/READ-1);
  defense-in-depth. **Compliant.**
- **Audit logging** — the full `AuditRecord` trail (LOG-1) is the SEC-5 deliverable. **Compliant.**
- **Secrets management** — DB credentials are `database`-unit/deploy-config concerns (reference-not-own). **N/A here.**
- **Prompt-injection defense** — no LLM in audit-store. **N/A.**
No blocking findings.

---

*End of nfr-requirements.md. Tech-stack decisions → `tech-stack-decisions.md`; the design patterns realizing each
target → NFR Design (next stage).*
