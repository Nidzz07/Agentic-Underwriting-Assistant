# NFR Requirements — `admin-cli` (U17)

**Stage**: BUILD → NFR Requirements (per-unit) · out-of-band admin CLI · **Depth**: **LIGHTER overall + FULL rigor on the two invariant-bearing mutations**
**Unit**: U17 `admin-cli` · **Date**: 2026-07-08 · Stories **US-ADMIN-1/2** · PER-3/6, FR-RULES-6.
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md` — **BR-ADMIN-1..9**, the module inventory, the **injected-`Engine` seam**, the **sole-gate-vs-open-VARCHAR** analysis, the five answers A/A/B/A/A, the three ADMIN-Folds) — **re-opening none**. Each `NFR-ADMIN-*` target is a **pass/fail testable assertion** traced to its BR-ADMIN rule. Four NFR-tier answers (all **A**) + three resolved folds (ADMIN-NFR-Fold-1/2/3) locked in the plan.

---

## 0. Central testability principle (tiers + folds)

Two tiers, matching the **auth-rbac/database precedent**:
- **U — unit / offline** (CI): publish file-IO over a `tmp_path` rulebook dir; the **canonical-role gate** proven with a **spy engine**; AST/import structural scans; no-secret-values; CLI-only scope; provider-deferred governance. Every invariant target's *logic* proves out here.
- **Integration — testcontainers `postgres:16`** (`@pytest.mark.integration`, Docker-gated, CI; auto-skipped locally): the **real** `app_user` INSERT/UPDATE + explicit "already exists"/"no such user" errors + the **fault-injection** sole-gate proof, over a **test-only minimal `app_user`** harness.

**New NFR-tier folds (ambiguity-check resolutions):**
- **ADMIN-NFR-Fold-1 — fault-injection isolation.** The fault-injection raw-SQL insert (ROLEGATE-1(b)) runs **only** against the **disposable per-fixture `PostgresContainer("postgres:16")`** (ephemeral, random port, torn down via `eng.dispose()`), gated by `@pytest.mark.integration` + a `_docker_available()` skip, connected via the container's generated URL — **never** `DATABASE_URL` or a persistent/production-adjacent DB. Same isolation every prior unit's integration tier uses.
- **ADMIN-NFR-Fold-2 — spy asserts on `connect`/`begin`, not `.execute`.** In **SQLAlchemy 2.0** the `Engine` exposes **no `.execute`** — the only Engine→DB entry points are `engine.connect()` and `engine.begin()` (`.execute` is on `Connection`). So the spy engine records **`connect()` and `begin()`** and asserts **neither** is called on a non-canonical role; the role gate runs **before** any connection is acquired. This is the true "no SQL touched the DB" boundary (tightens ROLEGATE-1(a)).
- **ADMIN-NFR-Fold-3 — test-only `app_user` is a harness (SCOPE-1).** The integration tier seeds its **own** minimal `app_user` (`user_id`/`subject`/`role`, **open VARCHAR, no CHECK** — mirroring the real column's openness so the fault-injection is faithful); it is **NOT** database's migration and **asserts nothing** about database's schema correctness (that is database's FIDELITY-1) — the exact auth-rbac `test_pg_adapter.py` posture. Reference-not-own preserved.

---

## 1. Finalized `NFR-ADMIN-*` targets (pass/fail; tier stated)

### FULL RIGOR — invariant-bearing (the two mutations)

#### NFR-ADMIN-PUBLISH-1 — publish = validate-then-append-only (BR-ADMIN-1, ADMIN-Fold-2)
- **Assertion**: publishing a rulebook version writes `{version}.yaml`, validates by load, is append-only, and never mutates an existing version.
- **Acceptance criteria**: (a) a **valid** new `{version}.yaml` publishes and `RulebookLoader.load_rulebook(version)` succeeds; (b) **append-only teeth** — re-publishing an **existing** version is **rejected** and the existing file is **byte-identical** before/after (no mutation); (c) a **schema-invalid** source is **rejected by `build_rulebook`** with **no** published file left behind; (d) a source whose declared `rulebook_version` ≠ target is rejected.
- **Tier**: **U** (tmp_path rulebook dir).

#### NFR-ADMIN-PUBVALID-1 — `build_rulebook` is the sole validator (BR-ADMIN-2)
- **Assertion**: admin-cli delegates all rulebook validation to `build_rulebook`/`RulebookLoader`; no local re-implementation.
- **Acceptance criteria**: (a) the publish path imports + calls `build_rulebook`/`RulebookLoader`; (b) **structural** — no local rulebook schema / allowlist / threshold-shape check / hasher in `backend/admin_cli/`.
- **Tier**: **U (structural)**.

#### NFR-ADMIN-ROLEGATE-1 — canonical-role SOLE gate (BR-ADMIN-5, ADMIN-Fold-1/2)
- **Assertion**: a non-canonical role is rejected **before any SQL runs**; the open-VARCHAR DB is **not** a gate — admin-cli's pre-write validation is the sole enforcement.
- **Acceptance criteria**: (a) **gate-before-SQL (tier U, spy engine)** — for a non-canonical role (`superuser`, `Admin`, blank, `None`), `create-user`/`set-role` raise `RoleValidationError` and the **spy engine's `connect()` and `begin()` are BOTH never called** (Fold 2 — no connection acquired, so no SQL is possible); a **canonical** role (`underwriter`/`auditor`/`admin`) passes the gate. (b) **sole-gate evidence (Integration, fault-injection)** — a **raw SQL** INSERT of a non-canonical role **directly** (`conn.exec_driver_sql`, **bypassing `AppUserWriter`**) is **accepted by the DB** (no error) over the disposable testcontainers `app_user` (Fold 1/3), proving the open-VARCHAR has **no CHECK** ⇒ the gate is the SOLE enforcement (ADMIN-Fold-1). The fault-injection **never** calls admin-cli's write path, so it cannot weaken the gate.
- **Tier**: **U + Integration**.

### FULL RIGOR — structural guards

#### NFR-ADMIN-REFNOTOWN-1 — reference-not-own; no local re-implementation (BR-ADMIN-6)
- **Assertion**: no `database`/`auth_rbac` **production** import; no local DDL/CHECK; the write is a parameterized injected-`Engine` call.
- **Acceptance criteria**: (a) **structural** — `backend/admin_cli/` imports `build_rulebook`/`RulebookLoader` + `auth_rbac.roles.Role` **only** (call-only), and no `database`/`auth_rbac` production **write** module, no local `hashlib`/rulebook-schema, no DDL/CHECK; (b) **non-vacuous self-test** — a planted local re-implementation is flagged.
- **Tier**: **U (structural)**.

#### NFR-ADMIN-NOSECRET-1 — no secret VALUES (BR-ADMIN-7 / SEC-3)
- **Assertion**: no secret literal in the package; command output / error messages carry no injected URL / credential VALUE.
- **Acceptance criteria**: (a) **structural** — no secret literal in `backend/admin_cli/`; the DB `Engine`/URL is injected; (b) error/stderr messages and status lines contain **no** URL/credential VALUE (names/status only).
- **Tier**: **U (structural)**.

### STANDARD — behaviour + scope

#### NFR-ADMIN-CREATE-1 — create-user INSERT + explicit already-exists (BR-ADMIN-3)
- **Assertion**: a real INSERT succeeds; a duplicate raises an explicit error (not a silent upsert).
- **Acceptance criteria**: (a) INSERT of `app_user(user_id, subject, role)` succeeds and is read back; (b) a duplicate `user_id`/`subject` raises **`UserWriteError` "already exists"** (UNIQUE violation surfaced).
- **Tier**: **Integration**.

#### NFR-ADMIN-SETROLE-1 — set-role UPDATE + explicit no-such-user (BR-ADMIN-4)
- **Assertion**: a real UPDATE changes the role; an absent user raises an explicit error (not a silent no-op).
- **Acceptance criteria**: (a) UPDATE `role WHERE user_id` on an existing user changes the role; (b) **0 rows affected** (absent user) raises **`UserWriteError` "no such user"**.
- **Tier**: **Integration**.

#### NFR-ADMIN-SCOPE-1 — CLI-only; no LLM / rule-eval / decision path (BR-ADMIN-8)
- **Assertion**: argparse CLI only; no underwriting surface.
- **Acceptance criteria**: **structural** — no LLM client / rule-evaluation / commit-service import in `backend/admin_cli/`; no admin UI.
- **Tier**: **U (structural)**.

#### NFR-ADMIN-CLIERR-1 — typed-exception taxonomy + exit codes (BR-ADMIN-8 scaffolding, Q4)
- **Assertion**: handlers raise a typed exception; the entrypoint maps to an exit code + a no-secret message.
- **Acceptance criteria**: (a) `AdminCliError` base → `RulebookPublishError` / `UserWriteError` / `RoleValidationError`; (b) each error path → a **non-zero exit code** + a human-readable **stderr** message with **no** secret VALUE; (c) success → **exit 0** + a names-only status line.
- **Tier**: **U**.

### SOFT — governance

#### NFR-ADMIN-PROVIDER-DEFER-1 — provider-config management deferred to P2 (BR-ADMIN-9, ADMIN-Fold-3-plan / Q3-B)
- **Statement**: Phase-1 admin-cli exposes only `publish-rulebook` + `create-user` + `set-role`.
- **Acceptance criteria**: **governance/structural** — no `set-provider` command and no provider-config store exist in `backend/admin_cli/`.
- **Tier**: **governance (+ light structural, U)**.

---

## 2. Traceability (target → BR-ADMIN → tier → rigor)

| Target | BR-ADMIN | Tier | Rigor |
|---|---|---|---|
| NFR-ADMIN-PUBLISH-1 | 1 | U | full |
| NFR-ADMIN-PUBVALID-1 | 2 | U (structural) | full |
| NFR-ADMIN-ROLEGATE-1 | 5 | U + Integration | full |
| NFR-ADMIN-REFNOTOWN-1 | 6 | U (structural) | full |
| NFR-ADMIN-NOSECRET-1 | 7 | U (structural) | full |
| NFR-ADMIN-CREATE-1 | 3 | Integration | standard |
| NFR-ADMIN-SETROLE-1 | 4 | Integration | standard |
| NFR-ADMIN-SCOPE-1 | 8 | U (structural) | standard |
| NFR-ADMIN-CLIERR-1 | 8 | U | standard |
| NFR-ADMIN-PROVIDER-DEFER-1 | 9 | governance (+ structural) | soft |

**No orphan** — BR-ADMIN-1..9 each map to a target (BR-ADMIN-8 → SCOPE-1 + CLIERR-1).

---

## 3. Security-Guardrails compliance (enabled extension)

| Control | Status | Rationale |
|---|---|---|
| Input validation | **Compliant (owns it)** | `role` validated against canonical `Role` (ROLEGATE-1); `<version>` validated by `build_rulebook`; `user_id`/`subject` parameterized (no injection), respecting PK/UNIQUE. |
| Prompt-injection defense | **N/A** | No LLM; no untrusted document parsed. |
| Secrets management | **Compliant (owns it)** | **NOSECRET-1 / SEC-3** — no secret VALUE read or printed; the DB `Engine`/URL is injected (secrets-config's). |
| Read-only DB access for audit role | **N/A** | admin-cli writes `app_user` (own injected engine) + rulebook files; it does not touch the audit read/write roles (SEC-5 is `audit-store`'s). |
| Audit logging | **N/A** | Out-of-band config management, not the runtime decision audit trail. |
| **Canonical-role authorization gate** | **Compliant (owns it)** | **ROLEGATE-1 / SEC-4** — non-canonical role rejected **before** persistence; the open-VARCHAR DB is not a gate (BR-DB-12). |

No blocking finding.

---

## 4. Settled items held (not re-opened)
- The **frozen FD** (BR-ADMIN-1..9, the module inventory, the injected-`Engine` seam, the sole-gate analysis) is the substrate — NFR builds testable targets **on** it.
- **Reference-not-own** — the four surfaces call-only, none edited; `build_rulebook` sole rulebook validator; `Role` sole canonical set; no schema/CHECK added; the test-only `app_user` is a harness asserting nothing about database's schema (ADMIN-NFR-Fold-3).
- **Canonical-role sole gate** (SEC-4, spy asserts on `connect`/`begin` — Fold 2). **SEC-3** no secret VALUES. **Provider-config management deferred to P2.**
- **No new production dependency** (argparse + testcontainers/spy are test-substrate; testcontainers already used by auth-rbac/database). **No LLM; no rule-eval; no decision/commit; no admin UI; WIRE-1 untouched; tier-B NOT authorized; no other unit started.**
