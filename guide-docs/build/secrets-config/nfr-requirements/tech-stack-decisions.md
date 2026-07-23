# Tech-Stack Decisions — `secrets-config` (EPIC-6 / U16)

**Stage**: BUILD → NFR Requirements (per-unit) · companion to `nfr-requirements.md`
**Unit**: U16 `secrets-config` · **Date**: 2026-07-07 · **Runtime**: Python **3.12 pinned** (D6).
**Theme**: **no new dependency** — a typed settings schema over env vars + a hermetic test pattern. **Reference-not-own**:
no consumer / `database` import (enforced by NFR-SEC-LEAF-1). **No LLM.** **SEC-3** — no credential/URL values here.

---

| # | Decision | Choice | Rationale |
|---|---|---|---|
| **D1** | Settings framework | **Pydantic v2 `BaseSettings`** via **`pydantic-settings`** (already in the stack) | the typed, declarative schema every unit uses; required fields with no default fail-close at construction (BR-SEC-1). |
| **D2** | URL-scheme validator | **`secrets-config`'s OWN** check — `sqlalchemy.make_url` (already in stack) or `urllib.parse` (stdlib) | validates `postgresql://` for the three URL vars **without importing `database`'s `DbUrlGuard`** (no circular dep; DATA-5 spirit reused independently). |
| **D3** | Test framework | **pytest** | the established backend suite; unit-tier. |
| **D4** | Hermetic env fixture | **`monkeypatch.delenv` all six keys (`raising=False`) → set only the case's fields → construct with `_env_file=None`** | `pydantic-settings` reads `os.environ` regardless of `_env_file`; clearing first prevents a real shell var from masking a "missing" case (NFR-SEC-FAILCLOSED-1). Dummies are **throwaway literals**, never real values (SEC-3). |
| **D5** | Property fuzz (optional) | **Hypothesis** (already in the stack) — optional, for invalid-URL / malformed-value fuzz over the scheme validator | strengthens SCHEME-1; a parametrized set also suffices. No new dependency. |
| **D6** | Leaf structural test | **`ast`-based no-forbidden-imports scan** (stdlib) + non-vacuous file guard + detector self-test | NFR-SEC-LEAF-1 — the auth-rbac mechanism; realizes BR-SEC-5 structurally. |
| **D7** | Governance artifacts | a committed **`.env.example`** (placeholder-only) + a **`.gitignore`** entry for `.env` | NFR-SEC-GOV-1; the checkable governance pieces (no value committed). |
| **D8** | Runtime | **Python 3.12** (pinned, project D6) | consistency across dev/CI/Render. |
| **D9** | New dependencies | **None** | pytest / pydantic-settings / Hypothesis / sqlalchemy are all already in the stack; the logic is a small schema + validators. |
| **D10** | LLM | **None** — no model anywhere | a config unit (BR-SEC-7). |
| **D11** | Reference-not-own | import **no** consumer / `database` production code | enforced structurally by NFR-SEC-LEAF-1; consumers depend on `secrets-config`, never the reverse (no circular dep). |

---

## Deferred (not pinned at NFR Requirements)
- The **concrete composition-root invocation** (`Settings()` once at startup) — the app-assembly / `deploy-config` unit's
  Code-Gen; `secrets-config` ships the fail-closed `Settings` class + accessors, not the call site.
- The **actual per-environment VALUES** (dev / CI / Render) — **`deploy-config`** (SEC-3; never here).
- The **repo-wide `detect-secrets` sweep** — **`quality-gates` / CI** aggregation (NFR-SEC-GOV-1 owns only this unit's
  own module/`.env.example`/`.gitignore` hygiene).
- **Infrastructure Design** for `secrets-config` — **likely a logged SKIP** (pure-config unit; no independent cloud
  topology), confirmed at that stage.
