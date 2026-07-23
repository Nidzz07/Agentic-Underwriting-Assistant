# Tech-Stack Decisions — `auth-rbac` (EPIC-6 / U11)

**Stage**: BUILD → NFR Requirements (per-unit) · companion to `nfr-requirements.md`
**Unit**: U11 `auth-rbac` · **Date**: 2026-07-07 · **Runtime**: Python **3.12 pinned** (D6).
**Theme**: **no new production dependency** — the authz policy is a few lines of pure Python over a static matrix
+ an injected role read model. Reference-not-own: import audit-store's `Authorizer` Protocol **read-only**; consume
`database`'s `app_user` contract; **edit neither**. **No LLM.** **SEC-3** — no credentials here.

---

| # | Decision | Choice | Rationale |
|---|---|---|---|
| **D1** | Test framework | **pytest** (+ existing markers) | The established backend suite; unit-tier primary. |
| **D2** | Primary test substrate | **Unit-tier against fakes** — a **fake `UserRoleRepository`** returning the raw `str | None` role value | auth-rbac's invariants are pure-logic policy properties; fakes make DENY-1/MATRIX-1/COMMIT-1/SSOT-1/BIAS-1/DET-1 fast + hermetic (the audit-store fake-repository pattern). |
| **D3** | Role read contract | **`UserRoleRepository.get_role(user_id) -> str | None`** (raw `app_user.role`; None = no row) | Per the frozen-FD §2.5 back-annotation — canonicalization + fail-close live in `authorize`; the **fake and the real Postgres-backed impl share this one Protocol** (no drift). The real impl is a `database`-`app_user`-backed adapter, wired later (Code-Gen). |
| **D4** | Protocol conformance | **Read-only import** of `backend.audit_store.seams.Authorizer` (`@runtime_checkable`) for `isinstance` + a call-shape/return-type assertion | NFR-AUTH-PROTOCOL-1 (two-assertion). The same Protocol object `commit_service.py` imports; auth-rbac edits no audit-store file. |
| **D5** | Property/exhaustiveness | **Hypothesis** (already in the stack) — optional, over the **finite** `Role × rbac_action` grid | NFR-AUTH-MATRIX-1 total coverage; a parametrized test also suffices. No new dependency. |
| **D6** | `Role` representation | **Pydantic v2** enum (already in the stack) — or a stdlib `enum.Enum` — for the canonical `{underwriter, auditor, admin}` set, closed at the app layer | domain-entities §2.2; the DB `role` column stays open `VARCHAR` (BR-DB-12, no CHECK). |
| **D7** | Permission matrix | **A plain Python data structure** (`dict[Role, frozenset[str]]`) — no policy engine | The matrix is a few lines; Casbin/OPA/etc. would be an unjustified dependency for Phase-1 scope. |
| **D8** | Optional integration smoke | **Reuse the existing `testcontainers` Postgres** (`@pytest.mark.integration`, auto-skip locally, CI) — a thin check that the real adapter reads a seeded `app_user` row via the contract | Asserts **nothing** about `database`'s schema correctness (that is `database`'s FIDELITY-1/MIGRATE-1). No new dependency. |
| **D9** | Runtime | **Python 3.12** (pinned, project D6) | Consistency across dev/CI/Render. |
| **D10** | New dependencies | **None** | pytest / Hypothesis / Pydantic / testcontainers are all already in the stack; the authz logic is pure Python. |
| **D11** | LLM | **None** — no model anywhere in `auth-rbac` | authz is deterministic pure logic (BR-AUTH-12). |
| **D12** | Reference-not-own | Import `Authorizer` **read-only**; consume `app_user` contract; **edit no** audit-store / database / UI code | The conformance + consumption boundaries the FD pinned. |

---

## Deferred (not pinned at NFR Requirements)
- The **composition-root wiring** of the real `AuthRBAC` into audit-store's `DecisionCommitService` — the integration/app
  unit's Code-Gen (auth-rbac ships the conforming impl; the wiring lives where the app is assembled).
- The **concrete API-layer guard** (FastAPI dependency) implementation — auth-rbac Code-Gen; the NFR pins its **testable
  property** (SSOT-1 delegation), not the framework wiring.
- The **app-owner connection URL** + any future **dedicated auth DB role** — `secrets-config` / `database` (deferred-open
  Q7-A / BR-AUTH-9). **SSO/OAuth** authentication flow — Phase 3 / OOS-3.
- **Infrastructure Design** for `auth-rbac` — **likely a logged SKIP** (pure-logic authz unit; no independent cloud
  topology), confirmed at that stage.
