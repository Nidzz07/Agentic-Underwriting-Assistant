# Functional Design Plan — `secrets-config` (EPIC-6 / U16)

**Phase / Stage**: BUILD → Functional Design (per-unit, plan-then-generate)
**Unit covered**: U16 `secrets-config` (EPIC-6, Phase 1) — the **single source** for provider/service credential + URL
**values** via env/secrets; **build fails on a hardcoded secret**. Story **US-PLAT-12**; owns **SEC-3**.
**Date**: 2026-07-07 · **Runtime**: Python **3.12 pinned** (D6) · **Depth**: proposed lighter/standard (confirm at Q7).
**Status**: **Plan — awaiting `[Answer]:` tags.** No FD artifacts generated yet. Stop after this plan.

This plan is the **altitude drop to internals** for a **pure-wiring/config unit** whose entire job is to reconcile the
**already-named accumulated contract** (shapes, never values) from the five completed units into a **typed Settings
surface** + the **SEC-3 fail-closed control**. It **reconciles against, and re-opens none of**, the consuming units'
actual code or design docs. **No credential VALUE appears anywhere** (SEC-3).

---

## 1. Unit context (analyzed — Step 1) ✅

### 1.1 `secrets-config` (U16, EPIC-6, Phase 1)
- **Purpose** (`unit-of-work.md §U16`): provider/service keys via env/secrets; **build fails on hardcoded secret**;
  **SEC-3 single source**. Application-Design `SecretsService` (`services.md`): *"Provider/service keys via env/secrets;
  no hardcoding."* **No `component-methods.md` entry** — a wiring/config unit, not a domain-method service.
- **Owned invariant**: **SEC-3** (no hardcoded secrets; single source of credential/URL values).
- **Consumed by** (reference-not-own, in reverse): every value-needing unit reads its shape from here — but
  `secrets-config` imports **none** of them. It is a **dependency leaf** (depends on nothing).
- **Depth**: unit-of-work says *"lighter (single control)"* — treated as a genuine decision at **Q7** (small but
  SEC-3-critical).

### 1.2 The compiled accumulated contract (confirmed 2026-07-07 across all five completed units)
**Phase-1 REQUIRED shapes (names only — values are what this unit sources, never authors):**

| Shape | Named by | Purpose | URL-shaped? |
|---|---|---|---|
| `DATABASE_URL` | database §5 + auth-rbac | app/owner connection; schema/migration/admin; auth-rbac reads `app_user` over it | **yes** (`postgresql://`) |
| `AUDIT_WRITER_URL` | database §5 → audit-store | least-privilege runtime **write** connection (as `audit_writer`) | **yes** (`postgresql://`) |
| `AUDIT_READER_URL` | database §5 → audit-store | least-privilege runtime **read** connection (as `audit_reader`) | **yes** (`postgresql://`) |
| `AUDIT_WRITER_PASSWORD` | database §5 | substituted into the `audit_writer` grant at migration execution | no (secret string) |
| `AUDIT_READER_PASSWORD` | database §5 | substituted into the `audit_reader` grant | no (secret string) |
| Gemini API key *(name TBD — Q2/Q6)* | memo-agent-core D2 | the P1 Gemini adapter's provider key (prod path; tests use the fake) | no (secret string) |

> **Precision note**: of the six, **exactly three are `postgresql://` URL-shaped** (`DATABASE_URL`,
> `AUDIT_WRITER_URL`, `AUDIT_READER_URL`) — scheme-validation (Q2) applies to these three. The two passwords and the
> Gemini key are **non-URL** secret strings (non-empty validation).

**Governance controls named:** SEC-3 no-hardcoded-secrets (US-PLAT-12 / `services.md` / req Q13); **build fails on a
hardcoded secret** (U16 + database BR-DB-13); dev `.env` **gitignored, never committed** (database §5.2 FOLD #4 —
enforcement owned here).

**Phase-2 seams — named-not-authored (reserve the pattern, do NOT design here — Q6):** `ANTHROPIC_API_KEY` / Ollama
endpoint / MCP config (memo-extensions); `LANGFUSE_*` / Prometheus / Grafana (observability).

### 1.3 Binding constraints held through this FD (guardrails skill + project)
- **SEC-3** — the schema/rules name **shapes only**; **no value** appears in any artifact or committed file; the dev
  `.env` (real local values) is gitignored.
- **Fail-closed** — a missing/invalid **required** var is a **hard error at load**, never a silent default/empty.
- **Reference-not-own (in reverse)** — `secrets-config` imports **no** consumer production code; **no circular
  dependency** (it must NOT import `database`'s `DbUrlGuard` — that would cycle with database→secrets-config).
- **Advisory-only / no LLM** — a config unit; no recommendation/decision language, no model.

---

## 2. Functional Design execution plan (checkboxes — Step 2)

Artifacts to generate **after** answers + ambiguity-check, under `guide-docs/build/secrets-config/functional-design/`:
- `domain-entities.md` — the **typed Settings schema**: the six Phase-1 required shapes (name, type, required/optional,
  per-shape validation rule) + the Phase-2 **reserved placeholders** (named, not authored). (Diagram only if it aids —
  likely text tables suffice for a config schema.)
- `business-rules.md` — **BR-SEC-\***: fail-closed load (missing/invalid required → hard error); no-value-in-repo +
  `.env` gitignored + **build-fails-on-hardcoded-secret as a checkable rule**; reference-not-own / no-circular-dep;
  one-place extension; SEC-3 single-source. Each rule states its condition; Security-Guardrails compliance table.
- `business-logic-model.md` — the **load/validation flow** (env → Settings → validate → hard-error-on-missing), the
  **when/where it loads** (per Q3), the **consumer access surface + composition-root injection** (per Q5), the
  **FD↔later boundary** (`deploy-config` wires actual env per environment), a consumer/dependency map, and an invariant
  self-check. A **validated Mermaid** (7 rules) + text alternative for the load/validation + consumer-access flow.

- [ ] **P1. Analyze unit context** (§1 — done).
- [ ] **P2. Collect `[Answer]:` tags** (§3); run the mandatory ambiguity-check; clarification file only if needed.
- [ ] **P3. Generate `domain-entities.md`** (Settings schema + reserved Phase-2 placeholders).
- [ ] **P4. Generate `business-rules.md`** (BR-SEC-\* + Security-Guardrails compliance).
- [ ] **P5. Generate `business-logic-model.md`** (load/validation flow + Mermaid, consumer surface, FD↔later boundary).
- [ ] **P6. Contract-coverage check** — verify all six Phase-1 shapes + the three governance controls are covered;
  verify **no consumer production code is imported** and **no circular dependency** with `database`.
- [ ] **P7. Guardrail compliance pass + 2-option completion message** (SEC-3 no-values, fail-closed, reference-not-own,
  advisory-only, no-LLM). Then Request Changes / Continue → **NFR Requirements** for `secrets-config`.

---

## 3. Clarifying questions (Step 3 — fill each `[Answer]:` tag)

Letter after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe. These decide the **schema +
mechanism** — they do **not** re-open any consuming unit's frozen code/design.

## Question 1 — Settings schema mechanism
How is the typed Settings surface built?

A) **Pydantic v2 `BaseSettings`** (via `pydantic-settings`, **already in the stack**) — a typed `Settings` class with the
   six fields, sourcing from **environment variables** (+ an optional dev `.env`). Required fields have **no default**
   (missing → a validation error at construction). Types + validators pin per-shape rules (Q2). **Recommended** — no new
   dependency; the same Pydantic-v2 discipline every unit uses. **Advisory-only naming; no LLM.**
B) Plain `os.environ` dict access with hand-rolled checks (rejected — loses typing + a single declarative schema; more
   error-prone for a SEC-3-critical control).
C) A third-party secrets manager SDK (rejected — over-engineered for Phase-1 env/secrets; free-tier scope).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — Pydantic v2 BaseSettings (via pydantic-settings, already in the stack) — a typed Settings class with the six fields, sourcing from environment variables (+ an optional dev .env). Required fields have no default (missing → a validation error at construction). No new dependency.

## Question 2 — Per-shape validation rules
What does each shape validate to?

A) **Per-shape**: the **three `postgresql://` URL-shaped** vars (`DATABASE_URL`, `AUDIT_WRITER_URL`, `AUDIT_READER_URL`)
   validate to a **`postgresql://` scheme** — **reusing the DATA-5 / `DbUrlGuard` SPIRIT via an INDEPENDENT check in
   `secrets-config`** (a small scheme validator), **NOT importing `database`'s `DbUrlGuard`** (that would create a
   circular dependency database↔secrets-config). The two passwords + the Gemini key validate to **non-empty** secret
   strings. All six are **required** (Q3 handles missing). **Recommended.**
B) Import and call `database.db_url_guard.require_postgres_url` for the URL vars (rejected — creates a **circular
   dependency** with `database`, which depends on `secrets-config` for its values; the shared spirit is reused
   independently instead).
C) Presence-only, no scheme/non-empty validation (rejected — a `sqlite://` or empty value would slip through; DATA-5 /
   SEC-3 want it caught at load).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — per-shape: the three postgresql:// URL-shaped vars (DATABASE_URL, AUDIT_WRITER_URL, AUDIT_READER_URL) validate to a postgresql:// scheme via an INDEPENDENT check in secrets-config (a small scheme validator), NOT importing database's DbUrlGuard (would create a circular dependency). The two passwords + the Gemini key validate to non-empty secret strings. All six required.

## Question 3 — Fail-closed load: WHEN/WHERE does validation happen? (genuine decision)
Missing/invalid required var → hard error. At what point is that enforced?

A) **Eager, at a single application-startup config-load step** — the composition root constructs `Settings()` **once at
   startup**; a missing/invalid required var **raises immediately**, before the app serves any request (fail-fast, no
   silent default/empty). The **same validation logic is reusable** by a CI/`quality-gates` check (Q4) and by
   `admin-cli`. **Recommended** — SEC-3 wants the failure loud and early.
B) **Lazy, on first use** — each consumer triggers validation when it first reads its var (rejected — allows a partial
   startup where some paths run before a missing secret surfaces; a late failure is worse for a SEC-3 control).
C) **A dedicated `validate()` step only** (CI/pre-deploy), not at runtime startup (weaker — a mis-deploy could still
   start with a missing var; A's eager-at-startup subsumes this and can also expose `validate()` for CI).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — eager, at a single application-startup config-load step: the composition root constructs Settings() once at startup; a missing/invalid required var raises immediately, before the app serves any request (fail-fast, no silent default/empty). The same validation logic is reusable by a CI/quality-gates check and by admin-cli.

## Question 4 — `.env` / `.gitignore` governance + build-fails-on-hardcoded-secret as a CHECKABLE rule
How is "no hardcoded secret / .env never committed" made checkable (not just policy)?

A) **Three checkable pieces**: (i) a committed **`.env.example`** template naming the shapes with **placeholder/empty
   values only**; (ii) **`.gitignore` includes `.env`** (real dev values never committed); (iii) a **checkable guard** —
   at minimum a `secrets-config` test asserting `.env` is gitignored + not tracked, **and** that the `secrets-config`
   module/`.env.example` contain **no real secret literal** (only shapes/placeholders). The **repo-wide hardcoded-secret
   scan aggregation** (e.g. a `detect-secrets`-style CI sweep across the whole repo) is **`quality-gates`/CI**'s concern
   (referenced, not owned here). **Recommended** — makes SEC-3 checkable at this unit without owning the whole repo scan.
B) A policy statement only, no test/artifact (rejected — the user requires it checkable, not prose).
C) Own the entire repo-wide secret scan here (rejected — that is `quality-gates`/CI's aggregation; this unit owns the
   naming + its own module/`.env.example` hygiene + the `.gitignore` rule).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — three checkable pieces: (i) a committed .env.example template naming the shapes with placeholder/empty values only; (ii) .gitignore includes .env; (iii) a checkable guard — a secrets-config test asserting .env is gitignored + not tracked, and that the secrets-config module/.env.example contain no real secret literal. The repo-wide hardcoded-secret scan aggregation is quality-gates/CI's concern, referenced not owned here.

## Question 5 — Consumer access surface (reference-not-own, in reverse)
How do database / audit-store / memo-agent-core / auth-rbac obtain their shape without `secrets-config` importing their
production code?

A) **`secrets-config` exposes a typed `Settings` object** (+ optionally small typed accessors, e.g. `database_url()`,
   `audit_writer_url()`, `audit_reader_url()`, `gemini_api_key()`); **consumers / the composition root READ from it** and
   inject the value into the **already-built injected seams** (the injected `Engine`, injected provider, injected
   connection). `secrets-config` **imports NONE** of the consumers' production code and **does not import `database`**
   (no circular dep, Q2). It is a **dependency leaf** the others read. **Recommended** — the same reference-not-own
   posture as database's `fidelity_comparator` / auth-rbac's duck-typed conformance, in reverse.
B) `secrets-config` imports each consumer to push values into them (rejected — reference-not-own violation + circular
   dependencies).
C) Global mutable singletons consumers mutate (rejected — hidden global state; harms testability/determinism).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — secrets-config exposes a typed Settings object (+ optionally small typed accessors, e.g. database_url(), audit_writer_url(), audit_reader_url(), gemini_api_key()); consumers/the composition root READ from it and inject the value into the already-built injected seams. secrets-config imports NONE of the consumers' production code and does not import database (no circular dep). A dependency leaf the others read.

## Question 6 — Phase-2 extension pattern + reserved seams
How is adding a future shape handled, and how are the Phase-2 vars represented now?

A) **One-place change**: adding a required/optional shape is a **single new field** on the `Settings` class. The
   **Phase-2 seams** — `ANTHROPIC_API_KEY` / Ollama endpoint / MCP (memo-extensions); `LANGFUSE_*` / Prometheus / Grafana
   (observability) — are named as **reserved-not-authored placeholders** (documented as future fields, e.g. commented or
   optional-`None`), **authored by those units at their own FD**, **not designed or required here**. **Recommended.**
B) Author all Phase-2 vars now as required (rejected — pulls unbuilt units' scope forward; would fail-closed on absent
   Phase-2 secrets in Phase 1).
C) Make no provision for extension (rejected — the one-place pattern is the point of a single source).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — one-place change: adding a required/optional shape is a single new field on the Settings class. The Phase-2 seams (ANTHROPIC_API_KEY/Ollama/MCP for memo-extensions; LANGFUSE_*/Prometheus/Grafana for observability) are named as reserved-not-authored placeholders, authored by those units at their own FD, not designed or required here.

## Question 7 — Depth confirmation (genuine decision — small but SEC-3-critical)
What depth for this FD?

A) **Standard** — pin the Settings schema + per-shape validation + the fail-closed load + the governance control + the
   consumer surface + a light lifecycle model, with the three FD artifacts (kept concise). Right for a **single-control
   but SEC-3-critical** unit. **Recommended.**
B) Minimal — schema sketch only (rejected — SEC-3 is a hard constraint; the fail-closed + governance rules need to be
   pinned, not sketched).
C) Comprehensive — full heavy treatment (rejected — over-weight for a single-control wiring unit; standard suffices).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — standard: pin the Settings schema + per-shape validation + the fail-closed load + the governance control + the consumer surface + a light lifecycle model, with the three FD artifacts kept concise. Right for a single-control but SEC-3-critical unit.

---

## 4. Constraints & settled items held (not re-opened)
- The **compiled accumulated contract** (six Phase-1 required shapes + three governance controls) is the substrate —
  the FD pins the **schema + rules** on it, re-opening **no** consuming unit's code/design.
- **Reference-not-own (in reverse)** — `secrets-config` imports **no** consumer production code and **not `database`**
  (no circular dependency; the URL scheme check reuses the DATA-5 *spirit* independently, Q2).
- **SEC-3** — **no credential/URL VALUE** in any artifact or committed file; the dev `.env` is gitignored; build fails
  on a hardcoded secret (checkable, Q4). **Fail-closed** load (Q3). **Advisory-only / no LLM.**
- **Phase-2 seams** (Claude/Ollama/MCP; Langfuse/Prometheus) are **reserved-not-authored** (Q6) — memo-extensions /
  observability own them at their own FD.
- **Settled non-edits stay closed**: `PROJECT-BRIEF.md`, `user-journey.md`, and every built unit's code/design docs
  (database §5, audit-store, memo-agent-core, auth-rbac are **referenced**, not re-opened).

---

## 5. Next step (STOP here)
Fill the seven `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check
(adding a clarification file only if needed), then generate the three `secrets-config` Functional Design artifacts
(`domain-entities.md`, `business-rules.md`, `business-logic-model.md`) and present the standardized 2-option completion
message. **No FD artifacts or code are generated until the answers are in and checked.**
