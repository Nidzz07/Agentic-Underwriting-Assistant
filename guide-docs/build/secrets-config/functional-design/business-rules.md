# Business Rules — `secrets-config` (EPIC-6 / U16)

**Stage**: BUILD → Functional Design (per-unit) · pure-wiring/config unit · **Depth**: standard
**Unit**: U16 `secrets-config` · **Date**: 2026-07-07 · owns **SEC-3**.
**Scope**: The **governance + integrity rules** for the single credential/URL source. Each rule states its condition
explicitly. **No credential/URL VALUE appears here** (SEC-3). **No LLM.**

---

## 1. Fail-closed load

### BR-SEC-1 — Missing/invalid required var → hard error (no silent default)
- **Condition**: constructing `Settings` **validates every required field**; a **missing** required var, an **empty /
  whitespace-only** secret, or a **non-`postgresql://`** URL var **raises** (a Pydantic `ValidationError`) — **never** a
  silent default, empty string, or `None`. The failure is **loud and at construction time**.
- **Why**: SEC-3 — a mis-configured deployment must fail fast and visibly, not run with a missing/blank secret. (The
  behavior is intrinsic to `Settings()` construction — see `business-logic-model.md §1`, fold 2.)

### BR-SEC-2 — Per-shape validation
- **Condition**: `DATABASE_URL`, `AUDIT_WRITER_URL`, `AUDIT_READER_URL` validate to a **`postgresql://` scheme**
  (independent check, DATA-5 spirit); `AUDIT_WRITER_PASSWORD`, `AUDIT_READER_PASSWORD`, `GEMINI_API_KEY` validate to
  **non-empty** (after strip). All six are **required**.
- **Why**: catches a `sqlite://`/malformed URL (DATA-5) and an empty secret at load, consistently.

---

## 2. Governance — checkable, not just policy (the three pieces)

### BR-SEC-3 — Dev `.env` gitignored; a placeholder-only `.env.example` is committed
- **Condition**: (a) a committed **`.env.example`** names every shape with **placeholder/empty values only** (never a
  real value); (b) **`.gitignore` includes `.env`** so a developer's real local `.env` is **never committed**.
- **Checkable**: a test asserts `.env` is listed in `.gitignore` **and** `.env` is **not git-tracked**, and that
  `.env.example` contains the shape **names** with **no real secret literal**.

### BR-SEC-4 — No secret literal in the module (build fails on a hardcoded secret)
- **Condition**: the `secrets-config` module declares **no default value** for any required secret (missing → error,
  BR-SEC-1) and contains **no hardcoded credential/URL literal**. A **hardcoded secret is a build failure**.
- **Checkable**: a test asserts the required `Settings` fields have **no defaults** (Pydantic model introspection) and
  the module/`.env.example` carry no value-shaped literal. The **repo-wide `detect-secrets`-style sweep** across the
  whole codebase is **`quality-gates`/CI**'s aggregation (referenced, not owned here); these three pieces are each
  **independently testable now** without it.

---

## 3. Boundaries — reference-not-own + extension

### BR-SEC-5 — `secrets-config` is a dependency LEAF (fold 1)
- **Condition**: `secrets-config` production code imports **no** consumer production module (`backend.database`,
  `backend.audit_store`, `backend.memo_agent_core`, `backend.auth_rbac`, `backend.intake`, …) and **not**
  `database`'s `DbUrlGuard`. It uses **only** third-party (`pydantic-settings`, and stdlib/`sqlalchemy.make_url` for the
  scheme check) + stdlib. **No circular dependency** (consumers depend on `secrets-config` for values; not vice-versa).
- **Checkable**: **structurally testable** by a **no-forbidden-imports test** (AST scan of `secrets-config` production
  sources for `from backend.<consumer>` / `import backend.<consumer>`) — the **same mechanism as auth-rbac's**; it
  **lands at NFR/Code-Gen** for this unit. Stated here as the binding boundary.

### BR-SEC-6 — One-place extension; Phase-2 seams reserved-not-authored
- **Condition**: adding a required/optional shape is a **single new field** on `Settings`. The Phase-2 seams
  (`ANTHROPIC_API_KEY` / Ollama endpoint / MCP — memo-extensions; `LANGFUSE_*` / Prometheus / Grafana — observability)
  are **named reserved placeholders only** — **authored by their owning unit at its own FD**, never declared/required
  here (adding them now would fail-closed on absent Phase-2 secrets in Phase 1).

### BR-SEC-7 — SEC-3 single source; no value anywhere; advisory-only; no LLM
- **Condition**: `secrets-config` is the **single source** of credential/URL **values** (sourced from env/secrets); **no
  value** appears in any artifact or committed file. It is a config unit — **no recommendation/decision language**
  (advisory-only holds trivially), **no model** (no LLM).

---

## 4. Rule index

| Rule | Condition summary | Traces |
|---|---|---|
| BR-SEC-1 | missing/invalid required → hard error, no silent default | SEC-3; US-PLAT-12 |
| BR-SEC-2 | per-shape validation (3 URL scheme / 3 non-empty) | DATA-5 spirit; database §5 |
| BR-SEC-3 | `.env` gitignored + placeholder `.env.example` | database §5.2 FOLD #4; SEC-3 |
| BR-SEC-4 | no secret literal / no default → build fails on hardcoded secret | U16; BR-DB-13 |
| BR-SEC-5 | dependency leaf; no consumer/`database` import; no circular dep | reference-not-own (fold 1) |
| BR-SEC-6 | one-place extension; Phase-2 reserved-not-authored | memo-extensions / observability |
| BR-SEC-7 | single source; no value anywhere; no LLM | SEC-3; advisory-only |

---

## 5. Security-Guardrails compliance (enabled extension)

| Control | Status | Rationale |
|---|---|---|
| Input validation | **Compliant** | Every required var is validated at load (scheme / non-empty); invalid → hard error (BR-SEC-1/2). |
| Prompt-injection defense | **N/A** | No LLM/prompt path in `secrets-config`. |
| Secrets management | **Compliant (owns SEC-3)** | This unit IS the SEC-3 single source — no hardcoded value, `.env` gitignored, build fails on a hardcoded secret (BR-SEC-3/4/7). |
| Read-only DB access for audit role | **N/A (referenced)** | `secrets-config` supplies the `AUDIT_WRITER_URL`/`AUDIT_READER_URL` **shapes**; the role grants + read-only enforcement are `database`'s (referenced, not owned). |
| Audit logging | **N/A** | No audit trail here; it sources config, persists nothing. |

No blocking finding.
