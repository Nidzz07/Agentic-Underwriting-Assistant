# Code Summary — `audit-store` (C5 / U12) · BUILD → Code Generation

**Unit**: U12 `audit-store` — CON-BR4 write-gate, append-only audit persistence, replay-as-detection, auditor read-only surface.
**Date**: 2026-07-05 · **Runtime**: Python **3.12** (pinned).
**Result**: **82 unit tests pass + 1 integration module (CI-only)**; audit_store **source coverage 100%** (full backend
suite **468 passed / 4 skipped / 99.69%**, QA-6 ≥90% gate reached). App code at `backend/audit_store/` (never `guide-docs/`).
Implements the frozen C5 contract + FD + approved `NFR-AUDIT-*` targets + patterns + 6 components — **re-opening none**;
plus the confirmed **`CommitContextProvider`** seam + the marked-TEST interim schema. **Reference-not-own throughout.**

---

## 1. Modules generated (`backend/audit_store/`)

| Module | Component | Role |
|---|---|---|
| `record_schema.py` | (data) | Frozen `AuditRecord` superset + `AuditTuple` / `CommittedDecision` / `ApplicantProfileSnapshot` + `CommitContext` + enums (`DecisionStatus`, `CommitAction`). Embeds imported `RuleResultReport` + `ApplicantProfile` (not re-declared). |
| `canon_adapter.py` | CanonSerAdapter | Delegates to the **unchanged** shared `canon_ser` for both payloads; `content_hash` + round-trip deserialize. |
| `seams.py` | (seams) | `IdGenerator` / `Clock` / `Authorizer` (`rbac_action` ≠ `CommittedDecision.action`) / **`CommitContextProvider`** protocols + prod/fake impls. |
| `repository.py` | AuditStore (repository) | `AuditRepository` Protocol (insert + read only — **no update/delete**) + in-memory fake + `atomic()` unit-of-work + derived-superseded read. |
| `commit_service.py` | DecisionCommitService | Fail-closed CON-BR4 gate + backend authz re-check + `CommitContextProvider` fetch + **assemble-before-BEGIN** + atomic write. |
| `replay_service.py` | ReplayService | Load → call rules-engine `evaluate()` → **single-sourced** `evaluation_output()` on both → match/mismatch + forensic delta. |
| `audit_service.py` | AuditService | Read-only `get` / `browse_history` + derived-superseded `effective_status`. |
| `telemetry.py` | TelemetryEmitter | Emit-only allowlist (metadata ids + enums + int timing; no demographic/free-text). |
| `pg_repository.py` | (Postgres impl) | SQLAlchemy 2.x Core over Postgres; CANON-SER columns; CI integration-tested (omitted from unit cov). |

Shared, **reference-not-own** (imported, unchanged): `backend/common/canon_ser.py` + `decimal_context.py`; rules-engine
`evaluate()` / `evaluation_output()` / `RuleResultReport`; intake `ApplicantProfile`.

## 2. Tests → target map (`backend/audit_store/tests/`)

| Target / invariant | Test(s) — tier |
|---|---|
| **GATE-1** negative matrix + ∀ blank/whitespace (Hypothesis) | `test_commit_service::test_gate_rejects_the_negative_matrix[0-7]` · `test_forall_blank_override_reason_rejected` — unit |
| **AUTHZ-1** reject independent of API | `test_commit_service::test_auditor_is_rejected_at_the_service_even_with_valid_payload` — unit |
| **ATOMIC-1** fault → both-or-neither | `test_commit_service::test_atomic_fault_mid_persist_rolls_back` (fake) · `test_pg_integration::test_fault_mid_transaction_rolls_back_both_rows` (real PG, multi-row) |
| **TUPLE-1** assemble-before-BEGIN + persisted | `test_commit_service::test_commit_assembles_complete_record_from_context_and_seams` / `test_pre_write_failure_opens_no_transaction` · `test_pg_integration::test_full_record_round_trips` |
| **APPEND-1** no-mutation + DB-role | `test_repository::test_repository_has_no_mutation_methods` · `test_pg_integration::test_writer_role_cannot_update_or_delete` / `test_reader_role_is_select_only` |
| **STATUS-1** derived-superseded read | `test_audit_service::test_effective_status_is_derived_superseded_from_a_newer_record` |
| **REPLAY-1** single-sourced projection + forensic-not-equality | `test_replay_service::test_projection_is_single_sourced_from_rules_engine` / `test_engine_version_only_difference_still_matches` / `test_genuine_output_difference_is_a_blocking_mismatch_with_delta` |
| **REPLAY-2** pure-evaluate referenced + no-recommit + ×N | `test_replay_service::test_replay_is_read_only_no_recommit_no_extra_records` / `test_replay_is_byte_identical_across_ten_runs` |
| **BR1-1** bias-swap on snapshot | `test_replay_service::test_bias_swap_on_snapshot_yields_identical_projection` |
| **READ-1 / LOG-1** auditor surface | `test_audit_service::*` · `test_pg_integration::test_browse_and_get_over_real_postgres` |
| **CANON-1** round-trip + tamper | `test_canon_adapter::*` |
| **OBS-1 / PERF-1** allowlist + observed | `test_telemetry::test_only_str_leaves_are_metadata_ids` / `test_perf_timing_observed_not_gated` |

## 3. Confirmed resolution + realization notes
- **`CommitContextProvider` seam** (confirmed): `DecisionCommitService.commit` keeps its **frozen 4-param signature** and
  fetches the pending-recommendation context (tuple fields + `ApplicantProfile`) via the injected provider (orchestrator-owned,
  reference-not-own; fake in unit tests). No frozen signature touched.
- **`rbac_action` ≠ `CommittedDecision.action`**: `Authorizer.authorize(user_id, rbac_action)` with `RBAC_COMMIT="commit"`,
  distinct from the human's approve/override.
- **Injected seams** (`IdGenerator`/`Clock`): `decision_id`/`timestamp` are audit metadata, not in the replay equality set.
- **TEST-only interim schema**: the 2-table normalized shape (`audit_record` + `applicant_profile_snapshot` child) + the
  `audit_writer`/`audit_reader` roles live **under `tests/` with a banner** — a test-harness choice for multi-row atomicity,
  **NOT a production prescription** (the `database` unit owns production DDL/grants; co-location constraint recorded).

## 4. Carry-forwards (cross-unit constraints register)
- **`database` unit**: co-locate audit-store's tables in one Postgres DB/connection (ATOMIC-1) + own the `audit_writer`/`audit_reader` grants.
- **`memo-agent-core`**: owns memo-hash recompute-and-compare (holds the memo text); audit-store only stores/carries `memo_hash`.

## 5. N/A layers (justified — plan Q7)
API layer (FastAPI orchestrator), Frontend, DB provisioning/migrations/role-grant DDL (`database`), `memo_hash` computation
(`memo-agent-core`). This unit generates **business logic + persistence + tests + this summary** only.

## 6. Coverage note (why the two `pyproject.toml` coverage changes exist)
Two coverage-config changes were made for this unit — **neither hides a real coverage gap**:

1. **`pg_repository.py` is omitted from unit-tier coverage** (`[tool.coverage.run] omit += "*/pg_repository.py"`) — it is
   the SQLAlchemy/Postgres impl, exercised via **testcontainers integration in CI**, not by unit imports (mirrors intake's
   `parse_worker` omit). The unit tier reaches **100%** on all other source.
2. **Two `typing.Protocol` stub-exclude patterns were added to `[tool.coverage.report] exclude_lines`**:
   `': \.\.\.\s*$'` and `'^\s*\.\.\.\s*$'`. **Rationale (so a later `pyproject.toml` reader is not misled):** the
   `AuditRepository` / `IdGenerator` / `Clock` / `Authorizer` / `CommitContextProvider` **Protocols** declare method
   signatures whose bodies are a literal `...` ellipsis (structural typing — these stub bodies are **never executed**; the
   concrete impls/fakes run instead). With branch coverage on, those 9 stub lines showed as **partial branches** despite
   being unreachable. Excluding lines that are exactly `...` (or a `def …: ...` one-liner) removes that artifact so the
   source reads a true 100%. **This is NOT a way to hide untested logic** — it only excludes ellipsis stub lines, which by
   definition contain no logic; every real statement/branch remains measured (0 missed across 286 statements).

Integration tests (`test_pg_integration.py`, `@pytest.mark.integration`) are **auto-skipped locally** (no
Docker/SQLAlchemy/testcontainers) and **run in CI** (DATA-5 real Postgres).
