# NFR Requirements — `secrets-config` (EPIC-6 / U16)

**Stage**: BUILD → NFR Requirements (per-unit) · pure-wiring/config unit · **Depth**: standard
**Unit**: U16 `secrets-config` — the SEC-3 single source for credential/URL values via env/secrets. Story **US-PLAT-12**.
**Date**: 2026-07-07 · **Runtime**: Python **3.12 pinned** (D6).
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`) — **re-opening none
of it**. Each `NFR-SEC-*` target is a **pass/fail testable assertion** traced to its FD rule (BR-SEC-1..7) + invariant,
with an explicit test tier. **No credential/URL VALUE appears here** (SEC-3). **No LLM.**

---

## 0. Central testability principle

`secrets-config`'s invariants are **pure config-validation properties**, tested **unit-tier, hermetically**: each case
constructs `Settings` from an **explicit/monkeypatched env** with `_env_file=None`, so tests **never depend on the
developer's real environment**. Two structural properties anchor the set: the **fail-closed matrix** (every field ×
missing/invalid) and the **dependency-leaf** AST guard (BR-SEC-5's promise realized as an actual target). **No target
tests a consumer's internals** (reference-not-own — SCOPE-1).

---

## 1. Finalized `NFR-SEC-*` targets (pass/fail; test tier stated)

### NFR-SEC-FAILCLOSED-1 — fail-closed load, each field independent (BR-SEC-1 / BR-SEC-2)
- **Assertion**: constructing `Settings` **raises** (`ValidationError`) when **any one** required field is **missing** or
  **invalid**, and **succeeds** only when **all six** are present + valid. Realized as a **parametrized matrix**:
  - **missing** — for each of the six fields, that field absent → raises (**6 cases**);
  - **invalid** — the three URL fields with `sqlite://` **and** with a malformed value; the three secrets with `""`
    **and** with whitespace → (**~12 cases**);
  - **success** — all six present/valid → constructs (**1 case**). → **≥19 independent cases**; each varies **one**
    field, so a regression in any field is isolated.
- **Hermetic fixture (fold — concrete, not assumed)**: each case **(a)** `monkeypatch.delenv(<each of the six keys>,
  raising=False)` **first** — because `pydantic-settings` reads `os.environ` **regardless of `_env_file`**, a real
  shell-set variable would otherwise **mask** a "missing" case; **(b)** sets **only** the fields the case needs —
  **valid throwaway dummy values** for the other five, the field under test **omitted** (missing) or **corrupted**
  (invalid); **(c)** constructs with **`_env_file=None`**. The dummies are **throwaway fixture literals, never real
  values** (SEC-3).
- **Test tier**: **unit** (hermetic; no container, no network).

### NFR-SEC-SCHEME-1 — URL-scheme validation, independent of `database` (BR-SEC-2)
- **Assertion**: for each of `DATABASE_URL` / `AUDIT_WRITER_URL` / `AUDIT_READER_URL`: `postgresql://` (and driver
  variants, e.g. `postgresql+psycopg2://`) is **accepted**; `sqlite://`, another scheme, and a malformed URL are
  **rejected** — via `secrets-config`'s **own** scheme validator (`sqlalchemy.make_url` / `urllib.parse` — third-party/
  stdlib), **not** `database`'s `DbUrlGuard`. Independence is **enforced by NFR-SEC-LEAF-1** (no import).
- **Test tier**: **unit**.

### NFR-SEC-LEAF-1 — dependency-leaf, structurally proven (BR-SEC-5; the FD promise realized)
- **Assertion**: a **no-forbidden-imports AST test** parses every `secrets_config` **production** `.py` (excluding
  `tests/`) and asserts **none** imports `backend.database`, `backend.audit_store`, `backend.memo_agent_core`,
  `backend.auth_rbac`, or `backend.intake` (either `import X` or `from X import …`, prefix-matched). With a
  **non-vacuous file-presence guard** (the real production modules are in the scanned set) **and** a **detector
  self-test** (proves it flags a synthetic forbidden import) — the **exact auth-rbac mechanism**. This realizes BR-SEC-5
  and guarantees NFR-SEC-SCHEME-1's independence.
- **Test tier**: **structural** (unit).

### NFR-SEC-GOV-1 — governance checkable (BR-SEC-3 / BR-SEC-4)
- **Assertion (four independent checks)**: (i) `.gitignore` lists `.env` **and** `.env` is **not git-tracked**
  (`git ls-files`); (ii) `.env.example` exists, names **all six** shapes, and carries **placeholder-only** values (no
  real secret); (iii) the required `Settings` fields have **no default** (Pydantic `model_fields` introspection —
  nothing baked in); (iv) **no secret literal** in the `secrets_config` module source. Each is **verifiable purely from
  the repo state `secrets-config` produces** — none waits on `deploy-config` or `quality-gates`. The repo-wide
  `detect-secrets` sweep = `quality-gates`/CI (referenced).
- **Test tier**: **unit / structural** (repo-state assertions).

### NFR-SEC-DET-1 — determinism / no side-effects (reproducibility guardrail; BR-SEC-7)
- **Assertion**: `Settings()` construction is a **pure validation step** — **(behavioral)** the same env yields an
  **identical** result across repeats (no randomness); **(structural)** the validation path performs **no network I/O**
  and **no wall-clock branch** (an import-absence check — no `requests`/`httpx`/`socket`, no time-dependent branch in the
  validators — and offline/hermetic construction). Asserts the **absence** of nondeterminism the design already avoids;
  adds no behavior.
- **Test tier**: **unit** (behavioral + light structural).

### NFR-SEC-SCOPE-1 — scoped exclusions *(GOVERNANCE / EXCLUSION STATEMENT — not a runtime test)*
- **Statement**: the `NFR-SEC-*` set tests **only** `secrets-config`'s own schema / validation / governance / leaf
  property. It does **NOT** test `database` / `audit-store` / `memo-agent-core` / `auth-rbac` **internals**,
  `deploy-config`'s per-environment value wiring, or `quality-gates`' repo-wide secret sweep. Enforced by review.
- **Test tier**: **N/A (governance statement)**.

### NFR-SEC-PERF-1 / NFR-SEC-OBS-1 — soft / N-A
- **PERF-1**: `Settings()` construction is a trivial in-memory validation — latency **observed, non-gating** (no SLO).
- **OBS-1**: metrics/traces are **`observability`'s** concern — **N/A / referenced**.
- **Test tier**: **observed / N/A**.

---

## 2. Traceability (target → FD rule → invariant → tier)

| Target | FD rule | Invariant | Tier |
|---|---|---|---|
| NFR-SEC-FAILCLOSED-1 | BR-SEC-1, BR-SEC-2 | SEC-3 fail-closed | unit |
| NFR-SEC-SCHEME-1 | BR-SEC-2 | DATA-5 spirit (postgresql only) | unit |
| NFR-SEC-LEAF-1 | BR-SEC-5 | reference-not-own / no circular dep | structural |
| NFR-SEC-GOV-1 | BR-SEC-3, BR-SEC-4 | SEC-3 no-hardcoded-secret / .env hygiene | unit / structural |
| NFR-SEC-DET-1 | BR-SEC-7 | reproducibility (pure step) | unit |
| NFR-SEC-SCOPE-1 | BR-SEC-5/7 | reference-not-own boundary | N/A (governance) |
| NFR-SEC-PERF-1 | — | soft budget | observed |
| NFR-SEC-OBS-1 | — | observability-owned | N/A |

---

## 3. Security-Guardrails compliance (enabled extension)

| Control | Status | Rationale |
|---|---|---|
| Input validation | **Compliant** | FAILCLOSED-1 / SCHEME-1 — every required var validated at load; invalid → hard error. |
| Prompt-injection defense | **N/A** | No LLM/prompt path. |
| Secrets management | **Compliant (owns SEC-3)** | GOV-1 — no hardcoded value / no default, `.env` gitignored, `.env.example` placeholder-only; no VALUE in any artifact/test (throwaway dummies only). |
| Read-only DB access for audit role | **N/A (referenced)** | `secrets-config` supplies the `AUDIT_*_URL` shapes; the role grants + enforcement are `database`'s. |
| Audit logging | **N/A** | Sources config; persists nothing. |

No blocking finding.

---

## 4. Settled items held (not re-opened)
- The **frozen FD** (Settings schema + BR-SEC-1..7 + the load model) is the substrate — NFR builds testable targets
  **on** it, re-opening nothing.
- **Reference-not-own** — targets test `secrets-config`'s own property; the **leaf property** (no consumer/`database`
  import, no circular dep) is realized as **NFR-SEC-LEAF-1** and guards SCHEME-1's independence.
- **SEC-3** — no credential/URL VALUE in any artifact/test (only throwaway fixture dummies); **fail-closed** matrix;
  **`.env` hermetic** in tests (delenv-all-six + `_env_file=None`).
- **`deploy-config`** (actual per-env values) + **`quality-gates`** (repo-wide sweep) = referenced, not tested here.
- **Infrastructure Design** for `secrets-config` is **likely a logged SKIP** (pure-config unit) — confirmed at that
  stage. Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, every built unit's code/design.
