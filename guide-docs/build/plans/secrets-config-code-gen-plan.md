# Code Generation Plan (Part 1) — `secrets-config` (EPIC-6 / U16)

**Phase / Stage**: BUILD → Code Generation, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags, **TDD tests-first**)
**Loop position**: `secrets-config` · FD ✅ · NFR Requirements ✅ · NFR Design ✅ · **Infrastructure Design ✅ SKIPPED-logged 2026-07-07**
→ **Code Generation ← here (the LAST stage for `secrets-config` — completes the SEVENTH fully-complete unit).**
**Unit**: U16 `secrets-config` · **Date**: 2026-07-07 · **Runtime**: Python **3.12 pinned** (D6) · **Depth**: standard.
**Status**: **Plan — awaiting `[Answer]:` tags. NO code generated this stage. Stop after this plan.**

Realizes the **3 approved NFR-Design components (C1–C3)** + the governance deliverables + the test substrate as code
under `backend/secrets_config/`, built **ON** the frozen FD (six required shapes; 3 `postgresql://` URL + 3 non-empty
secrets), the approved `NFR-SEC-*` targets, and the NFR-Design patterns — **re-opening none**. **TDD: every `NFR-SEC-*`
target gets its test first**, at the tier NFR Design pinned (unit / structural). **No production import of `database` or
any consumer anywhere** — structurally verified by the actual AST scanner test (fold 1). **No credential/URL VALUE**
(SEC-3). **No LLM.**

---

## 1. What Code-Gen builds (and what it must NOT touch)

### 1.1 Builds
The `Settings` class (six required fields + validators), the self-contained `is_postgres_url` validator, the typed
access surface, the governance artifacts (`.env.example` + a `.gitignore` `.env` entry), and the test substrate
(hermetic fixture, AST scanner, drift guard) — each with its test at the NFR-pinned tier.

### 1.2 Does NOT touch (held closed)
- **No `database` / consumer production import** — the scheme validator is `secrets-config`'s **own**
  (`sqlalchemy.make_url`, third-party); `database`'s `DbUrlGuard` is **referenced in spirit, not imported/edited**.
- **No credential/URL VALUE** anywhere; **no** real `.env` committed (only a placeholder `.env.example`).
- No consuming unit's code; no `PROJECT-BRIEF.md`/`user-journey.md` edits; Phase-2 seams reserved-not-authored.

### 1.3 Guardrails held (skill)
SEC-3 (single source; no value; fail-closed); DATA-5 spirit (postgresql:// scheme, independent); reference-not-own /
dependency-leaf / no circular dep; determinism (pure construction); advisory-only; **no production `database`/consumer
import**; **no LLM.**

---

## 2. Module / package layout (`backend/secrets_config/`) — C1–C3 mapping

```text
backend/secrets_config/
├── __init__.py
├── url_validation.py     # C2 — is_postgres_url(value) -> bool  (sqlalchemy.make_url; own module)
├── settings.py           # C1 — Settings(BaseSettings): 6 required no-default fields + validators; get_settings()
└── tests/
    ├── __init__.py
    ├── conftest.py                 # hermetic env fixture (delenv all six + _env_file=None)
    ├── test_url_validation.py      # SCHEME-1 — is_postgres_url accept/reject
    ├── test_settings.py            # FAILCLOSED-1 (~19 hermetic cases) + DET-1 + PERF-1
    ├── test_governance.py          # GOV-1 — .gitignore/.env-untracked, .env.example placeholder-only, no-default, no-literal, drift guard
    └── test_no_forbidden_imports.py# LEAF-1 — AST scan (own modules) + non-vacuous guard + detector self-test

# repo-root governance deliverables (see Q4):
.env.example              # all six shapes, placeholder-only; commented Phase-2 reserved lines
.gitignore                # ensure it contains a `.env` entry
```

| Component / item | Module / file | Backs |
|---|---|---|
| **C1 Settings** | `settings.py` | FAILCLOSED-1, GOV-1 (no-default), DET-1, PERF-1 |
| **C2 is_postgres_url** | `url_validation.py` | SCHEME-1 |
| **C3 access surface** | `settings.py` (`get_settings()` + attribute access) | consumer access |
| Governance | `.env.example`, `.gitignore` | GOV-1 |
| Test substrate | `tests/conftest.py` (fixture), `test_no_forbidden_imports.py` (scanner), drift guard in `test_governance.py` | LEAF-1, GOV-1 |

---

## 3. TDD test → target map (every `NFR-SEC-*` at its NFR-pinned tier)

| Target | Test file / name | Tier | Assertion |
|---|---|---|---|
| **FAILCLOSED-1** | `test_settings.py::test_missing_field_raises[<6>]` + `::test_invalid_field_raises[<~12>]` + `::test_complete_valid_env_constructs` | unit (hermetic) | ~19 cases; each varies one field via the `delenv`-all-six fixture |
| **SCHEME-1** | `test_url_validation.py::test_postgres_accepted` / `::test_sqlite_rejected` / `::test_other_scheme_rejected` / `::test_malformed_rejected` | unit | own `is_postgres_url`; independent of `DbUrlGuard` |
| **LEAF-1** | `test_no_forbidden_imports.py::test_no_database_or_consumer_import` + `::test_scan_sees_own_modules` + `::test_scanner_detects_a_forbidden_import` | structural | AST over `backend/secrets_config`; **guard names THIS unit's own modules** (fold 1) + self-test |
| **GOV-1** | `test_governance.py::test_gitignore_lists_dotenv` / `::test_dotenv_not_tracked` / `::test_env_example_placeholder_only` / `::test_required_fields_have_no_default` / `::test_no_secret_literal_in_module` / `::test_env_example_matches_settings_fields` (drift guard, fold 2) | unit / structural | four governance pieces + the drift guard |
| **DET-1** | `test_settings.py::test_same_env_identical_result` + `::test_module_imports_no_network_or_clock` | unit | repeat-invariance + import-absence |
| **PERF-1** | `test_settings.py::test_construction_latency_observed` | observed | measured, non-gating |
| **SCOPE-1** | — | **N/A (governance/exclusion)** | documented boundary |
| **OBS-1** | — | **N/A** | observability-owned |

No `NFR-SEC-*` target unmapped; no test imports `database`/a consumer or tests a consumer's internals.

---

## 4. Implementation order (leaf-first, tests-first per step)

0. **Scaffold**: `backend/secrets_config/__init__.py`, `tests/__init__.py`, `tests/conftest.py` (hermetic fixture). Add
   `--cov=backend/secrets_config` to `pyproject` `addopts` (Q6).
1. **C2 `is_postgres_url`** (`url_validation.py`) — **test first** (`test_url_validation.py`: SCHEME-1 accept/reject).
2. **C1 `Settings`** (`settings.py`) — six required no-default fields + validators (URL→`is_postgres_url`, secrets→
   non-empty-after-strip) + `get_settings()`. **Test first** (`test_settings.py`: FAILCLOSED-1 ~19 hermetic cases +
   DET-1 + PERF-1).
3. **C3 access surface** — `get_settings()` (constructs the validated `Settings`, the fail-closed entry point) +
   attribute access (Q2). Covered by step-2 tests.
4. **Governance artifacts** — `.env.example` (all six placeholder-only + commented Phase-2 lines) + ensure `.gitignore`
   has `.env` (Q4). **Test first** (`test_governance.py`: the four checks + the **drift guard**, fold 2).
5. **LEAF-1 AST scanner** (`test_no_forbidden_imports.py`) — dynamic `rglob` over `backend/secrets_config`; forbidden
   prefixes `backend.database`/`audit_store`/`memo_agent_core`/`auth_rbac`/`intake`; **non-vacuous guard names THIS
   unit's own modules** (fold 1) + detector self-test.
6. **Coverage gate** — full backend suite; `backend/secrets_config` source ≥90% (QA-6). Refresh `testresults.txt`.
7. **Code summary** — `guide-docs/build/secrets-config/code/code-summary.md` (module list + test→target map + flagged
   notes) + back-annotate guide-state.md; completion + 2-option gate.

---

## 5. Clarifying questions (fill each `[Answer]:` tag)

Letter after each `[Answer]:` tag; last option = Other. These decide **Code-Gen realization** — they do **not** re-open
the FD, the NFR targets, or the patterns.

## Question 1 — Test framework
A) **pytest** (established) + **Hypothesis** (already in the stack) — optional, for invalid-URL / malformed-value fuzz
   over `is_postgres_url`; parametrized elsewhere. **No new dependency.** **Recommended.**
B) pytest only (acceptable — a parametrized set covers SCHEME-1; Hypothesis just adds a property flavor).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — pytest (established) + Hypothesis (already in the stack) — optional, for invalid-URL/malformed-value fuzz over is_postgres_url; parametrized elsewhere. No new dependency.

## Question 2 — Access surface shape (C3)
How do consumers obtain a validated `Settings`?

A) **A module-level `get_settings() -> Settings`** — constructs the validated `Settings` (the **fail-closed entry
   point**; optionally `@lru_cache` for a single construction) — and consumers read **attributes** (`settings.database_url`,
   `settings.gemini_api_key`, …). **No separate per-field accessor functions** (attribute access on the one validated
   object is the single source). **Recommended** — minimal, one source of truth.
B) Explicit per-field accessor functions (`database_url()`, `audit_writer_url()`, …) (more surface for no Phase-1
   benefit; attribute access already reads the one validated `Settings`).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — a module-level get_settings() -> Settings — constructs the validated Settings (the fail-closed entry point; optionally @lru_cache for a single construction) — consumers read attributes (settings.database_url, settings.gemini_api_key, etc.). No separate per-field accessor functions.

## Question 3 — Module split (C1 / C2)
A) **`url_validation.py`** (C2 `is_postgres_url`) **separate from** `settings.py` (C1 imports it) — keeps the validator
   independently unit-testable and the leaf scan sees both. `get_settings()` lives in `settings.py` (re-exported from
   `__init__` if useful). **Recommended.**
B) One module holding everything (rejected — a separate tiny validator module is cleaner + independently testable).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — url_validation.py (C2 is_postgres_url) separate from settings.py (C1 imports it) — keeps the validator independently unit-testable and the leaf scan sees both. get_settings() lives in settings.py (re-exported from __init__ if useful).

## Question 4 — Governance-artifact location + content
A) **`.env.example` at the repo root** — names **all six** shapes with **placeholder-only** values (e.g.
   `DATABASE_URL=postgresql://user:pass@host:5432/dbname`-style **non-secret placeholders**, or empty) **plus commented
   Phase-2 reserved lines** (`# ANTHROPIC_API_KEY=`, `# LANGFUSE_PUBLIC_KEY=`, …); ensure the **repo-root `.gitignore`
   contains `.env`** (add the line if absent). The governance/drift tests reference these repo-root paths. **Recommended.**
B) Place them under `backend/secrets_config/` (rejected — `.env.example`/`.gitignore` are conventional repo-root files;
   `deploy-config` + developers expect them there).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — .env.example at the repo root — names all six shapes with placeholder-only values plus commented Phase-2 reserved lines; ensure the repo-root .gitignore contains .env (add the line if absent). The governance/drift tests reference these repo-root paths.

## Question 5 — LEAF-1 AST scanner (fold 1) + drift guard (fold 2)
A) **The auth-rbac AST-scan mechanism, adapted**: dynamic `rglob` over `backend/secrets_config` (excluding `tests/`);
   forbidden prefixes `backend.database`/`backend.audit_store`/`backend.memo_agent_core`/`backend.auth_rbac`/
   `backend.intake`; a **non-vacuous guard naming THIS unit's OWN actual modules** (`settings.py`, `url_validation.py` —
   **not** auth-rbac's file names, fold 1); + a **detector self-test**. The **drift guard** compares
   `{name.upper() for name in Settings.model_fields}` to the **ACTIVE (uncommented)** `.env.example` keys, **excluding
   commented Phase-2 lines** (fold 2). **Recommended.**
B) A superficial string search (rejected — AST is robust; the folds require the own-module guard + the active-key drift
   compare).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — the auth-rbac AST-scan mechanism, adapted: dynamic rglob over backend/secrets_config (excluding tests/); forbidden prefixes for database/audit_store/memo_agent_core/auth_rbac/intake; a non-vacuous guard naming THIS unit's OWN actual modules (settings.py, url_validation.py — not auth-rbac's file names); + a detector self-test. The drift guard compares uppercased Settings.model_fields to the ACTIVE (uncommented) .env.example keys, excluding commented Phase-2 lines.

## Question 6 — Coverage config
A) **Add `--cov=backend/secrets_config` to `pyproject` `addopts`**; all modules are **pure-logic, unit-covered to ≥90%
   (QA-6)** — **no `pg_repository`-style omit needed** (no live-DB module). No coverage-threshold change. **Recommended.**
B) Leave coverage config untouched (rejected — the new package would be uncounted).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — add --cov=backend/secrets_config to pyproject addopts; all modules are pure-logic, unit-covered to ≥90% (QA-6) — no pg_repository-style omit needed (no live-DB module). No coverage-threshold change.

## Question 7 — Infrastructure layers (confirm N/A) + depth + completion
A) **Compute / Storage / Messaging / Networking / Deployment = N/A** (Infrastructure Design SKIPPED-logged — pure-config
   unit; values + wiring are `deploy-config`'s). **Standard** Code-Gen: full TDD build of C1–C3 + governance + test
   substrate + every `NFR-SEC-*` test; a `guide-docs/build/secrets-config/code/code-summary.md`; `testresults.txt`
   refreshed; guide-state.md back-annotated; then the standardized **2-option** completion gate. **Recommended.**
B) Minimal (rejected — SEC-3-critical; the fail-closed matrix + governance + leaf test must be real).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — Compute/Storage/Messaging/Networking/Deployment = N/A (Infrastructure Design SKIPPED-logged — pure-config unit; values + wiring are deploy-config's). Standard Code-Gen: full TDD build of C1–C3 + governance + test substrate + every NFR-SEC-* test; a code-summary.md; testresults.txt refreshed; guide-state.md back-annotated; then the standardized 2-option completion gate.

---

## 6. SEC-3 / reference-not-own confirmation (explicit)
- **No credential/URL VALUE anywhere** — `Settings` sources values from env at runtime; `.env.example` carries
  **placeholder-only** values; the real `.env` is **gitignored, never committed**. Test env uses **throwaway dummy
  literals** (never real values).
- **No production import of `database` or any consumer** anywhere in `backend/secrets_config/` — the scheme validator is
  the unit's own (`sqlalchemy.make_url`); **structurally verified** by `test_no_forbidden_imports.py` (Q5). No `database`
  file edited/imported. **No LLM.**

---

## 7. Constraints & settled items held (not re-opened)
- FD (six required shapes + BR-SEC-1..7) + approved `NFR-SEC-*` + NFR-Design patterns/components (C1–C3) are the
  substrate — Code-Gen realizes them, re-opening none.
- **Reference-not-own / dependency leaf** — own scheme validator (spirit, not code); no consumer/`database` import; no
  shared `backend` module coupling; verified by LEAF-1.
- **SEC-3** no values; fail-closed; `.env` gitignored; `.env.example` placeholder-only + drift-guarded. **DET-1** purity.
  **Advisory-only. No LLM.** Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, every built unit's code.

---

## 8. Next step (STOP here)
Fill the seven `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check
(clarification file only if needed), then generate the `secrets-config` code **TDD tests-first, leaf-first** per §4, run
the suite, write the code summary, back-annotate guide-state.md, and present the standardized completion + 2-option
message. **No code is generated until the answers are in and checked.**
