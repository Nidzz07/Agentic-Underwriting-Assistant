# Tech-Stack Decisions — `audit-store` (C5 / U12)

**Stage**: BUILD → NFR Requirements (per-unit) · cluster unit 3 of 4
**Unit**: U12 `audit-store` · **Date**: 2026-07-05 · **Runtime**: Python **3.12 pinned**.
**Scope**: the technology choices backing the `NFR-AUDIT-*` targets — built on the frozen FD + C5 contract, **reference-not-own**
throughout. No choice re-opens a frozen shape.

---

| # | Decision | Rationale | Reference-not-own boundary |
|---|---|---|---|
| **D1** | **SQLAlchemy 2.x (Core / thin ORM) over `psycopg`** for the `audit-store` service, the `AuditRecord` record model, and the read queries. | Typed, explicit SQL with transaction control for the atomic assemble+persist (ATOMIC-1) and the read-only auditor queries (READ-1/LOG-1). Mature, no bespoke SQL string-building. | audit-store owns the **service + model + queries**; it does **not** own DDL/migrations/roles (D9). |
| **D2** | **Real PostgreSQL via Docker / testcontainers in CI** for DB-touching integration tests; a **repository abstraction** with an **in-memory fake** for pure-logic unit tests. | **DATA-5: PostgreSQL everywhere, no SQLite** — dialect drift could break replay/versioning, so DB-role/atomicity/append-only are verified against **real** Postgres. The repository seam keeps GATE-1 / REPLAY-1 / CANON-1 / predicate + projection logic fast and DB-free. | Provisioning of the Postgres instance + the CI service is `database`/deploy-config (D9). |
| **D3** | **Shared `backend/common/canon_ser.py` referenced UNCHANGED** via an **audit-store-local CANON-SER adapter**, for **both** `rule_results` and `profile_canonical`; `content_hash = sha256(CANON-SER bytes)`. | One deterministic serialization convention across intake / rules-engine / audit-store → meaningful replay comparison + integrity checks (CANON-1). audit-store is the **§2.1 spec authority**; `backend/common/` is only the shared **location**. | **No fork, no §2.1 change, no re-declaration** — the adapter delegates to the single shared util (the `CanonSerAdapter` / `RulebookCanonAdapter` precedent). |
| **D4** | **intake's `ApplicantProfile` referenced** (imported) as the `ApplicantProfileSnapshot` shape; serialize → CANON-SER, deserialize → the **exact** intake object. | Round-trip fidelity (REPLAY-2 / Q9) with **no drift** vs intake's schema. | Snapshot shape is **governed by intake's contract**, never a re-declared parallel field list. |
| **D5** | **rules-engine referenced** — `ReplayService` calls the pure **`evaluate()`**, persists the **`RuleResultReport`** field-for-field, and applies rules-engine's **`evaluation_output()`** projection (`backend/rules_engine/report.py`) to **both** the fresh and the recorded report. | Single-sourced replay equality set (REPLAY-1); no parallel projection; the `decline_reasons`/`refer_reasons` inclusion inherits rules-engine's verified DET-2 permutation-invariance. | audit-store owns **load + call + compare**; **rules-engine owns `evaluate()`** and the projection function. |
| **D6** | **Injected `decision_id` generator seam** (constructor/param): **UUID in production**, a deterministic fake in tests. | Test determinism + no wall-clock/global state in the service (mirrors intake's `application_id` generator and rules-engine's injected `engine_version`). `decision_id` is **audit metadata, not in the replay equality set**, so it never threatens replay determinism. | — |
| **D7** | **No LLM anywhere in audit-store.** | Replay re-evaluates rules only (deterministic); memo integrity = `memo_hash` recompute-and-compare (REPLAY-2). The LLM lives only in `memo-agent-core`. | `memo_hash` / `model_version` are **persisted here, computed in `memo-agent-core`**. |
| **D8** | **Python 3.12** (pinned; `.python-version` + `pyproject` `requires-python`). | Build-wide NFKC/Unicode + serialization determinism (CON-DET-1), matching intake / rules-engine. | Single source of truth = repo-root `.python-version`. |
| **D9** | **`database` unit owns provisioning / migrations / role-grant DDL** — incl. the **`audit_writer` (INSERT-only)** and **`audit_reader` (SELECT-only)** roles the APPEND-1/READ-1 integration tests reference. | Clean ownership split (Q3): audit-store asserts **behavior**, `database` authors the **grants**. | audit-store's integration test **references** those real roles as a fixture; it **does not** author or duplicate the grant DDL. |
| **D10** | **Pydantic v2** for the `AuditRecord` / `AuditTuple` / `CommittedDecision` / `ApplicantProfileSnapshot` record models (validation, `frozen` value objects, enum `status`/`action`). | Consistent with intake / rules-engine; enforces the closed `action` enum + tuple completeness (GATE-1 / TUPLE-1) at the type level. | — |
| **D11** | **`auth-rbac` owns the `AuthRBAC.authorize` policy**; audit-store owns only the **commit-time re-check enforcement point** (AUTHZ-1). | Defense-in-depth (API layer + service) without duplicating the RBAC policy. | Policy referenced; the re-check call site is audit-store's. |
| **D12** | **New dependencies**: `SQLAlchemy>=2.0`, `psycopg[binary]`, `testcontainers[postgresql]` (test-only). No others. | Minimal footprint; everything else (pydantic, the shared CANON-SER/decimal_context) already present. | Added to the root dependency set at Code-Gen. |

---

## Observability / audit-trail split (D-note)
The **persisted `AuditRecord` history IS the SEC-5 audit trail** (queried by `AuditService`; deliberately carries the
full record incl. the segregated demographics snapshot — safe, **storage ≠ influence**). **Observability telemetry** is a
**separate emit-only allowlist** surface (OBS-1) with **no demographic/free-text field**, wired by the `observability`
unit (reference-not-own). The two are never conflated.

*End of tech-stack-decisions.md.*
