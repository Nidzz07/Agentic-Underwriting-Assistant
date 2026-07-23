# Domain Entities — `secrets-config` (EPIC-6 / U16)

**Stage**: BUILD → Functional Design (per-unit) · pure-wiring/config unit · **Depth**: standard
**Unit**: U16 `secrets-config` — the **single source** for provider/service credential + URL **values** via env/secrets.
Story **US-PLAT-12**; owns **SEC-3**. **Date**: 2026-07-07 · **Runtime**: Python **3.12 pinned** (D6).
**Scope**: The **typed `Settings` schema** over the six Phase-1 required shapes (compiled from the five completed units)
+ the Phase-2 **reserved-not-authored** placeholders. **No credential/URL VALUE appears anywhere** (SEC-3 — this unit
*sources* values from the environment; it never authors or echoes one). **No LLM.**

---

## 1. The `Settings` schema (Phase-1 required shapes)

A typed **Pydantic v2 `BaseSettings`** (`pydantic-settings`, already in the stack) sourcing from **environment
variables** (+ an optional dev `.env`). **Every field below is required** and has **no default** — a missing value
raises at construction (fail-closed; see `business-rules.md` BR-SEC-1). Types + validators pin the per-shape rule.

| # | Field (env var) | Type | Required | Validation rule | Sourced-for (named by) |
|---|---|---|---|---|---|
| 1 | `DATABASE_URL` | str | **yes** | **`postgresql://` scheme** (independent check, DATA-5 spirit) | app/owner connection — database §5; auth-rbac reads `app_user` over it |
| 2 | `AUDIT_WRITER_URL` | str | **yes** | **`postgresql://` scheme** | least-privilege runtime **write** connection (as `audit_writer`) — database §5 → audit-store |
| 3 | `AUDIT_READER_URL` | str | **yes** | **`postgresql://` scheme** | least-privilege runtime **read** connection (as `audit_reader`) — database §5 → audit-store |
| 4 | `AUDIT_WRITER_PASSWORD` | str | **yes** | **non-empty** (after strip) | substituted into the `audit_writer` grant at migration execution — database §5 |
| 5 | `AUDIT_READER_PASSWORD` | str | **yes** | **non-empty** (after strip) | substituted into the `audit_reader` grant — database §5 |
| 6 | `GEMINI_API_KEY` | str | **yes** | **non-empty** (after strip) | the P1 Gemini adapter's provider key — memo-agent-core D2 (**name pinned here**, fold 3) |

- **`GEMINI_API_KEY` name pinned (fold 3)**: memo-agent-core deferred the concrete name to `secrets-config`. Pinned to
  **`GEMINI_API_KEY`**, matching the **`google-generativeai` SDK's own convention** — `secrets-config`'s naming
  authority. (Tests use the scripted fake provider; the value is only needed on the prod Gemini path.)
- **Scheme validation (three URL vars)**: an **independent** `postgresql://`-scheme validator inside `secrets-config`
  (stdlib/`sqlalchemy.make_url` — third-party only). It **reuses the DATA-5 / `DbUrlGuard` SPIRIT** but **does NOT
  import `database`'s `DbUrlGuard`** (that would create a circular dependency; see `business-rules.md` BR-SEC-4).
- **No VALUE**: the table names **shapes + rules only**. The dev `.env` (real local values) is **gitignored** (BR-SEC-3).

---

## 2. Phase-2 reserved placeholders (named, NOT authored here)

Adding a shape is a **one-place change** (a new field on `Settings` — BR-SEC-6). The following are **reserved seams**:
they are **named** so the single-source pattern is visible, but **authored by their owning unit at its own FD**, **not
designed, typed, or required here** (adding them now would fail-closed on absent Phase-2 secrets in Phase 1).

| Reserved shape | Future owner | Notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | `memo-extensions` (Phase 2) | Claude secondary provider key |
| Ollama endpoint (e.g. `OLLAMA_HOST`) | `memo-extensions` (Phase 2) | showcase provider — endpoint, typically no key |
| MCP config (server URLs/tokens) | `memo-extensions` (Phase 2) | `rulebook-tools` / `decisions-tools` MCP |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` / `LANGFUSE_HOST` | `observability` (Phase 2) | LLM trace keys |
| Prometheus / Grafana credentials | `observability` (Phase 2) | metrics/dashboards |

**These are placeholders only** — no field, type, or validator is declared for them in Phase 1.

---

## 3. What this schema is NOT (boundaries held)

- **Not** a store of any **value** — `secrets-config` sources values from the environment at runtime; **no credential /
  connection-string value** appears in any artifact or committed file (SEC-3). The dev `.env` is gitignored.
- **Not** a re-opening of any consuming unit — the shapes are **read from the compiled accumulated contract** (database
  §5, audit-store, memo-agent-core, auth-rbac); no consuming unit's code/design is edited or imported.
- **Not** an importer of `database`'s `DbUrlGuard` — the scheme check is **independent** (no circular dependency).
- **Not** the Phase-2 provider/observability keys — those are **reserved-not-authored** (§2).

---

## 4. Traceability

| Field / element | Traces to |
|---|---|
| `DATABASE_URL` | database `infrastructure-design.md §5`; auth-rbac app-owner connection (BR-AUTH-9) |
| `AUDIT_WRITER_URL` / `AUDIT_READER_URL` | database §5 (APPEND-1 prod role-scoped connections) → audit-store runtime engine |
| `AUDIT_WRITER_PASSWORD` / `AUDIT_READER_PASSWORD` | database §5 (grants substitution); BR-DB-13 (no secrets in schema) |
| `GEMINI_API_KEY` | memo-agent-core D2 (Gemini adapter P1); name pinned here (US-PLAT-12) |
| `postgresql://` scheme validation | DATA-5 (BR-DB-6) / `DbUrlGuard` spirit — independent, no import |
| fail-closed required fields | SEC-3 / US-PLAT-12 (build fails on hardcoded/absent secret) |
| Phase-2 reserved seams | memo-extensions / observability (their own future FD) |
