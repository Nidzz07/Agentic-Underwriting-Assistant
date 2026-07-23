# NFR Design Plan (Part 1) — `secrets-config` (EPIC-6 / U16)

**Phase / Stage**: BUILD → NFR Design, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `secrets-config` · FD ✅ · **NFR Requirements ✅ (approved 2026-07-07)** → **NFR Design ← here** →
[Infra likely SKIP] → Code-Gen. **Unit**: U16 `secrets-config` — the SEC-3 single source for credential/URL values.
**Date**: 2026-07-07 · **Runtime**: Python **3.12 pinned** (D6) · **Depth**: standard (small but SEC-3-critical).
**Status**: **Plan — awaiting `[Answer]:` tags. NO NFR-Design artifacts generated this stage. Stop after this plan.**

Maps each approved **`NFR-SEC-*`** target to a **named design pattern** + the **logical components** that realize it,
built **ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`) + the approved
`nfr-requirements.md` — **re-opening neither**. **No credential/URL VALUE** (SEC-3). **No LLM.**

---

## 1. Unit context (analyzed)

### 1.1 What NFR Design builds ON (frozen — NOT re-opened)
- **FD**: the typed `Settings` schema (six required shapes; 3 `postgresql://` URL + 3 non-empty secrets; Phase-2
  reserved); BR-SEC-1..7; the fail-closed-at-construction model + consumer access surface.
- **NFR targets** (`nfr-requirements.md`): FAILCLOSED-1 (≥19 hermetic cases; `delenv`-all-six fixture), SCHEME-1
  (3 URL own validator, independent of `DbUrlGuard`), LEAF-1 (AST no-forbidden-imports — auth-rbac mechanism), GOV-1
  (four checkable governance pieces), DET-1 (pure construction), SCOPE-1 (governance/exclusion), PERF-1/OBS-1 (soft/N-A).

### 1.2 The distinguishing design theme
A **single Pydantic-v2 `Settings` class** whose **required-ness + per-field validators compose into one
construction-time fail-closed check** — plus a **self-contained scheme validator** (no shared module with `database`).
`secrets-config` is a **dependency leaf** — production code imports **no** consumer / `database` module (structurally
proven by LEAF-1, the auth-rbac posture). Purity (DET-1) is **structurally guaranteed** — validators are pure functions
of the value + static schema; env is the only input source; no network/time/random imports.

### 1.3 Guardrails held (skill)
SEC-3 (no value; fail-closed; single source); DATA-5 spirit (postgresql:// scheme, independent); reference-not-own /
no circular dependency; determinism (pure construction); advisory-only. **No LLM.**

---

## 2. Draft pattern → target map (finalized after the answers)

| Pattern | Backs | Shape |
|---|---|---|
| **SettingsClassPattern** | FAILCLOSED-1 | one Pydantic-v2 `BaseSettings`; six **required, no-default** fields + per-field validators → one construction-time fail-closed check (missing/invalid → `ValidationError`) |
| **FieldValidatorPattern** | FAILCLOSED-1, SCHEME-1 | per-field validators: `postgresql://` scheme (the 3 URLs, via C2) + non-empty-after-strip (the 3 secrets) |
| **IndependentSchemeValidatorPattern** | SCHEME-1 | a **self-contained** `is_postgres_url` / validator (`sqlalchemy.make_url` or `urllib.parse`) in `secrets-config`'s **own** module — **no shared module with, and no import of, `database`'s `DbUrlGuard`** |
| **NoForbiddenImportsTestPattern** | LEAF-1 | the **auth-rbac AST-scan** structure adapted for `secrets_config`'s module set + non-vacuous guard + detector self-test |
| **GovernanceArtifactPattern** | GOV-1 | committed `.env.example` (placeholder-only) kept **in sync** with the `Settings` fields (drift-guarded) + `.gitignore` rule + no-default / no-literal / `.env`-untracked structural checks |
| **PureConstructionPattern** | DET-1 | validators are **pure functions** of (value, static schema); env is the only input; **no network/time/random** import in the module — purity **structurally guaranteed**, not just tested |
| **ReferencedBoundaryPattern** | SCOPE-1, PERF-1, OBS-1 | SCOPE-1 governance statement; PERF-1 soft-observed; OBS-1 N/A (observability-owned) |

---

## 3. Draft logical components (finalized after the answers)

- **C1 `Settings`** — the Pydantic-v2 `BaseSettings` class (six required fields + validators); the fail-closed surface.
- **C2 `is_postgres_url`** — the self-contained scheme validator (used by C1's URL field validators).
- **C3 typed accessors** — small getters over `Settings` (e.g. `database_url()`, `audit_writer_url()`,
  `audit_reader_url()`, `gemini_api_key()`) that consumers / the composition root read *(may be plain attribute access —
  Q7)*.
- **Governance deliverables** (not code): `.env.example` (placeholder-only) + a `.gitignore` `.env` entry.
- **Test substrate** (test-only, not a production component): the **hermetic env fixture** (`delenv`-all-six +
  `_env_file=None`) + the **AST no-forbidden-imports scanner**.

---

## 4. Clarifying questions (fill each `[Answer]:` tag)

Letter after each `[Answer]:` tag; last option = Other. These decide the **pattern shape** — they do **not** re-open the
FD or the approved NFR targets.

## Question 1 — Settings-class pattern (FAILCLOSED-1)
How do the six fields' required-ness + validators compose into one fail-closed check?

A) **One Pydantic-v2 `BaseSettings`** with the six fields declared **required (no default)** and typed `str`; per-field
   **validators** (scheme for URLs, non-empty for secrets — Q2) run **at construction**. A missing var (no default) and
   an invalid var (validator) **both raise a `ValidationError` at `Settings()` construction** — one composed fail-closed
   check, no separate per-field code path. **Recommended.**
B) Manual `os.environ` reads with hand-rolled per-field `if` checks (rejected — scatters the check; loses the single
   declarative schema).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — one Pydantic-v2 BaseSettings with the six fields declared required (no default) and typed str; per-field validators (scheme for URLs, non-empty for secrets) run at construction. A missing var (no default) and an invalid var (validator) both raise a ValidationError at Settings() construction — one composed fail-closed check, no separate per-field code path.

## Question 2 — The per-field validators
What validates each field?

A) **Pydantic field validators**: the three URL fields → **`is_postgres_url`** (Q3, the independent scheme check); the
   three secret fields → **non-empty-after-strip** (reject `""`/whitespace). All six are **required (no default)** so
   absence is caught before the validator even runs. **Recommended.**
B) `min_length=1` constraints only (rejected — a whitespace-only `"   "` secret would pass `min_length`; a strip-then-
   check validator is needed; and URL scheme needs a real validator, not a length).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — Pydantic field validators: the three URL fields → is_postgres_url (the independent scheme check); the three secret fields → non-empty-after-strip (reject "" / whitespace). All six required (no default) so absence is caught before the validator even runs.

## Question 3 — Independent scheme-validator pattern (SCHEME-1 self-containment)
How is the `postgresql://` check self-contained + independent of `database`?

A) **A self-contained function in `secrets-config`'s own module** — `is_postgres_url(value) -> bool` using
   **`sqlalchemy.make_url(value).get_backend_name() == "postgresql"`** (third-party, already in stack) — accepting
   driver variants, rejecting `sqlite://` / other / malformed. It lives **only** in `secrets_config` (no shared helper
   module with `database`), and **does not import `database`'s `DbUrlGuard`** (no circular dependency; enforced by
   LEAF-1). Reuses the DATA-5 *spirit*, not the code. **Recommended.**
B) Import `database.db_url_guard.require_postgres_url` (rejected — circular dependency; LEAF-1 would fail).
C) Put the validator in `backend/common/` and share it with `database` (rejected — a refactor of `database`'s built
   code + a new shared surface; `secrets-config`'s own small check is simpler and keeps the leaf property clean).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — a self-contained function in secrets-config's own module — is_postgres_url(value) -> bool using sqlalchemy.make_url(value).get_backend_name() == "postgresql" (third-party, already in stack) — accepting driver variants, rejecting sqlite:///other/malformed. Lives only in secrets_config (no shared helper module with database), does not import database's DbUrlGuard (no circular dependency, enforced by LEAF-1). Reuses the DATA-5 spirit, not the code.

## Question 4 — No-forbidden-imports test pattern (LEAF-1)
How is the leaf property proven?

A) **The auth-rbac AST-scan pattern, adapted**: parse every `secrets_config` production `.py` (excluding `tests/`);
   assert none imports `backend.database` / `backend.audit_store` / `backend.memo_agent_core` / `backend.auth_rbac` /
   `backend.intake` (prefix-matched, `import` + `from`); with a **non-vacuous file-presence guard** + a **detector
   self-test**. **Recommended.**
B) Only a prose statement (rejected — LEAF-1 is a structural target).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — the auth-rbac AST-scan pattern, adapted: parse every secrets_config production .py (excluding tests/); assert none imports backend.database/backend.audit_store/backend.memo_agent_core/backend.auth_rbac/backend.intake (prefix-matched, import + from); with a non-vacuous file-presence guard + a detector self-test.

## Question 5 — Governance-artifact pattern (GOV-1) + drift guard
How are `.env.example` / `.gitignore` / the structural checks realized?

A) **A committed `.env.example`** naming **all six** shapes with **placeholder-only** values; a **`.gitignore` entry**
   for `.env`; and **structural checks**: (i) required `Settings` fields have **no default** (`model_fields`); (ii) **no
   secret literal** in the module; (iii) `.env` **not git-tracked**; **plus a drift guard** — a test asserting
   `.env.example`'s keys **equal the `Settings` required field names** (so the template can't silently drift from the
   schema). The repo-wide `detect-secrets` sweep = `quality-gates`/CI (referenced). **Recommended.**
B) Hand-maintain `.env.example` with no drift guard (weaker — it silently rots as fields change).
C) Auto-generate `.env.example` from `Settings` at build time (heavier; A's committed template + drift-guard test is
   simpler and equally safe).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — a committed .env.example naming all six shapes with placeholder-only values; a .gitignore entry for .env; and structural checks: (i) required Settings fields have no default; (ii) no secret literal in the module; (iii) .env not git-tracked; plus a drift guard — a test asserting .env.example's keys equal the Settings required field names, so the template can't silently drift from the schema.

## Question 6 — Pure-construction pattern (DET-1)
How is purity structurally guaranteed (not just tested)?

A) **Structural guarantee**: the validators are **pure functions** of (the field value, the static schema); the **only
   input source** is env / the optional `_env_file`; the module imports **no** `requests`/`httpx`/`socket`/`time`/`random`
   and has **no wall-clock or random branch**. Construction performs **no network I/O**. DET-1 asserts the **absence** of
   these; the design **avoids introducing** them. **Recommended.**
B) Allow a lazy network/remote-secret fetch inside construction (rejected — introduces I/O + nondeterminism; Phase-1 is
   env/secrets only, no remote secrets manager).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — structural guarantee: the validators are pure functions of (the field value, the static schema); the only input source is env/the optional _env_file; the module imports no requests/httpx/socket/time/random and has no wall-clock or random branch. Construction performs no network I/O.

## Question 7 — Logical components + accessor shape + depth
Confirm the components, the accessor shape, and the depth.

A) **Components**: C1 `Settings` (BaseSettings), C2 `is_postgres_url` (independent validator), C3 **typed accessors**
   (small getters — **or plain attribute access** on the `Settings` instance; a realization detail, both delegate to the
   one validated `Settings`); + governance deliverables (`.env.example`, `.gitignore`) + test substrate (hermetic
   fixture, AST scanner). **Standard depth** — two artifacts (`nfr-design-patterns.md` + `logical-components.md`), each
   with **one validated Mermaid** (7 rules) + text alternative. **Recommended.**
B) Fewer / more components, or minimal/comprehensive depth (rejected — standard fits a single-control SEC-3 unit).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — components: C1 Settings (BaseSettings), C2 is_postgres_url (independent validator), C3 typed accessors (small getters, or plain attribute access — a realization detail, both delegate to the one validated Settings); + governance deliverables (.env.example, .gitignore) + test substrate (hermetic fixture, AST scanner). Standard depth — two artifacts, each with one validated Mermaid + text alternative.

---

## 5. Constraints & settled items held (not re-opened)
- The **frozen FD** (Settings schema + BR-SEC-1..7) + the approved **`NFR-SEC-*`** targets are the substrate — patterns/
  components realize them, re-opening neither.
- **Reference-not-own / dependency leaf** — no consumer / `database` import; the scheme validator is `secrets-config`'s
  **own** (no shared module, no `DbUrlGuard` import); proven by LEAF-1. **No circular dependency.**
- **SEC-3** — no value in any artifact; fail-closed; `.env` gitignored; `.env.example` placeholder-only + drift-guarded.
- **DET-1** purity structurally guaranteed. **Advisory-only. No LLM.**
- **Infrastructure Design** for `secrets-config` remains **likely a logged SKIP** — decided at that stage.
- Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, every built unit's code/design (incl.
  `database`'s `DbUrlGuard` — **referenced in spirit, not imported/edited**).

---

## 6. Next step (STOP here)
Fill the seven `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check
(clarification file only if needed), then generate the two `secrets-config` NFR Design artifacts
(`nfr-design-patterns.md` + `logical-components.md`, each with a validated Mermaid + text alternative) and present the
standardized 2-option completion message. **No NFR-Design artifacts or code are generated until the answers are in and
checked.**
