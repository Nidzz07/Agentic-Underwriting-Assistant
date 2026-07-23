# NFR Requirements Plan (Part 1) — `secrets-config` (EPIC-6 / U16)

**Phase / Stage**: BUILD → NFR Requirements, **Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `secrets-config` · **FD ✅ (approved 2026-07-07)** → **NFR Requirements ← here** → [Infra likely SKIP]
→ Code-Gen. **Unit**: U16 `secrets-config` — the SEC-3 single source for credential/URL values via env/secrets.
**Date**: 2026-07-07 · **Runtime**: Python **3.12 pinned** (D6) · **Depth**: standard (small but SEC-3-critical).
**Status**: **Plan — awaiting `[Answer]:` tags. NO NFR-Requirements artifacts generated this stage. Stop after this plan.**

Built **ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`) — **re-opening none
of it**. Every `NFR-SEC-*` target is drafted **pass/fail testable**; finalized into `nfr-requirements.md` only after the
`[Answer]:` tags are filled. **No credential/URL VALUE appears here** (SEC-3). **No LLM.**

---

## 1. Unit context (analyzed)

### 1.1 What NFR Requirements builds ON (frozen FD — NOT re-opened)
- **Settings schema** (`domain-entities.md §1`): six Phase-1 required shapes — `DATABASE_URL`, `AUDIT_WRITER_URL`,
  `AUDIT_READER_URL` (`postgresql://`-scheme), `AUDIT_WRITER_PASSWORD`, `AUDIT_READER_PASSWORD`, `GEMINI_API_KEY`
  (non-empty). Phase-2 seams reserved-not-authored.
- **BR-SEC-1..7** (`business-rules.md`): fail-closed load (1); per-shape validation (2); `.env` gitignored +
  placeholder `.env.example` (3); no-secret-literal / no-default → build-fails-on-hardcoded-secret (4); **dependency
  LEAF, no consumer/`database` import, structurally testable (5)**; one-place extension + Phase-2 reserved (6); SEC-3
  single-source / no-value / no-LLM (7).
- **Behavioral model** (`business-logic-model.md`): fail-closed intrinsic to `Settings()` **construction** (testable
  standalone, no forward dependency); startup/composition-root = named downstream note; consumer access surface;
  FD↔later boundary (`deploy-config` wires actual VALUES; `quality-gates` owns the repo-wide sweep).

### 1.2 Dependencies & interfaces (reference-not-own — the boundaries NFR targets must respect)
- **Consumed by** database / audit-store / memo-agent-core / auth-rbac (they read shapes); **`secrets-config` imports
  none of them** and **not `database`** — NFR targets test **secrets-config's own** schema/validation/governance/leaf
  property, **not** any consumer's internals (Q6). `deploy-config` (later) wires actual values; `quality-gates`/CI owns
  the repo-wide secret sweep — both **referenced, not tested here**.

### 1.3 Guardrails held (skill)
**SEC-3** (single source; no value anywhere; fail-closed); **DATA-5 spirit** (`postgresql://` scheme for the 3 URL
vars, independent check); **reference-not-own / no circular dependency**; **advisory-only**; **determinism** (validation
is a pure step). **No LLM.**

### 1.4 The distinguishing NFR theme
`secrets-config`'s invariants are **pure config-validation properties** — testable **unit-tier**, hermetically (each
case constructs `Settings` from an **explicit/monkeypatched env**, `_env_file=None`, so tests never depend on the
developer's real environment). Two structural properties stand out: the **fail-closed matrix** (every field × missing/
invalid) and the **dependency-leaf** AST guard (the FD's BR-SEC-5 promise realized as an actual test).

---

## 2. Draft `NFR-SEC-*` targets (pass/fail testable — finalized after the answers)

- **NFR-SEC-FAILCLOSED-1** (BR-SEC-1/2): **each of the six required fields** independently rejects **missing** (6 cases)
  and **invalid** (URLs: non-`postgresql` scheme + malformed; secrets: empty + whitespace → ~12 cases) at construction
  (`ValidationError` raised), **plus** a **complete-valid-env success** case → **≥19 parametrized cases**, so a
  regression in any one field is isolated. *(See Q1.)*
- **NFR-SEC-SCHEME-1** (BR-SEC-2): the three URL fields accept `postgresql://` and reject `sqlite://` / other-scheme /
  malformed — validated by `secrets-config`'s **own** scheme check, **independent of `database`'s `DbUrlGuard`** (no
  import; enforced by NFR-SEC-LEAF-1). *(See Q2.)*
- **NFR-SEC-LEAF-1** (BR-SEC-5; the FD promise realized): a **structural no-forbidden-imports test** — AST-scan of
  `secrets_config` **production** sources asserting **no** `import`/`from` of `backend.database`, `backend.audit_store`,
  `backend.memo_agent_core`, `backend.auth_rbac`, `backend.intake` — with a **non-vacuous file guard** + a **detector
  self-test** (the exact auth-rbac mechanism). *(See Q3.)*
- **NFR-SEC-GOV-1** (BR-SEC-3/4): governance checkable — (i) `.gitignore` includes `.env` + `.env` **not git-tracked**;
  (ii) `.env.example` names all six shapes with **placeholder-only** values (no real secret); (iii) required `Settings`
  fields have **no default** (Pydantic `model_fields` introspection); (iv) **no secret literal** in the module source.
  The repo-wide `detect-secrets` sweep = `quality-gates`/CI (referenced). *(See Q4.)*
- **NFR-SEC-DET-1** (determinism / no-side-effects): `Settings()` construction is a **pure validation step** — same env
  → identical result (repeat), and the validation performs **no network I/O** and **no wall-clock branch** (behavioral
  + a light structural import-absence check). *(See Q5.)*
- **NFR-SEC-SCOPE-1** (scoped exclusions — **governance statement, not a runtime test**): targets test **only**
  `secrets-config`'s schema/validation/governance/leaf property — **not** database/audit-store/memo-agent-core/auth-rbac
  internals, **not** `deploy-config`'s env wiring, **not** `quality-gates`' repo-wide sweep. *(See Q6.)*
- **NFR-SEC-PERF-1 / OBS-1** (soft/N-A): construction latency is trivially soft/observed; metrics/traces are
  `observability`'s concern (N/A). *(Folded into Q8 depth; minimal.)*

---

## 3. Clarifying questions (Step — fill each `[Answer]:` tag)

Letter after each `[Answer]:` tag; last option = Other. These decide the **testable-target shape + tech stack** — they
do **not** re-open the frozen FD.

## Question 1 — Fail-closed matrix (each field × missing/invalid, independent + success)
How is BR-SEC-1/2 made pass/fail?

A) **A parametrized matrix**: **each of the six fields** gets its own **missing** case (env var absent → raises) and its
   own **invalid** case(s) (URLs: a `sqlite://` **and** a malformed value; secrets: `""` **and** whitespace) → **~18+
   independent cases**, **plus** one **complete-valid-env success** case (all six present/valid → constructs). Each case
   varies **one field**, so a regression in any field's handling is caught in isolation. **Recommended.**
B) One "rejects bad config" lump test (rejected — hides which field/case regressed; the user asked for each independent).
C) Only test the missing cases, skip invalid (rejected — a `sqlite://` URL or blank secret must be caught too).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — a parametrized matrix: each of the six fields gets its own missing case (env var absent → raises) and its own invalid case(s) (URLs: sqlite:// and a malformed value; secrets: "" and whitespace) → ~18+ independent cases, plus one complete-valid-env success case. Each case varies one field, isolating any regression.

## Question 2 — URL-scheme validation, independent of `database`
How is NFR-SEC-SCHEME-1 tested?

A) For **each** of `DATABASE_URL` / `AUDIT_WRITER_URL` / `AUDIT_READER_URL`: `postgresql://` (and driver variants like
   `postgresql+psycopg2://`) **accepted**; `sqlite://`, another scheme, and a malformed URL **rejected** — using
   `secrets-config`'s **own** scheme validator. Independence from `database`'s `DbUrlGuard` is **guaranteed by
   NFR-SEC-LEAF-1** (no import). **Recommended.**
B) Reuse/import `database.db_url_guard` in the test (rejected — even in a test it muddies the leaf property; the unit's
   own validator is what ships, and the leaf test forbids the production import anyway).
C) Presence-only, no scheme assertion (rejected — DATA-5 wants `sqlite://` caught).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — for each of the three URL fields: postgresql:// (and driver variants like postgresql+psycopg2://) accepted; sqlite://, another scheme, and a malformed URL rejected, using secrets-config's own scheme validator. Independence from database's DbUrlGuard guaranteed by NFR-SEC-LEAF-1 (no import).

## Question 3 — Dependency-leaf structural test (realize the BR-SEC-5 promise)
How is the leaf property proven?

A) **A no-forbidden-imports AST test** (the **auth-rbac mechanism**): parse every `secrets_config` **production** `.py`
   (excluding `tests/`) and assert **none** imports `backend.database` / `backend.audit_store` / `backend.memo_agent_core`
   / `backend.auth_rbac` / `backend.intake` — with a **non-vacuous file-presence guard** (the real modules are scanned)
   **and** a **detector self-test** (proves it flags a synthetic forbidden import). **Recommended** — this is where the
   FD's "structurally testable" promise becomes an actual target.
B) Only document the leaf property (rejected — the FD explicitly promised a structural test here).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — a no-forbidden-imports AST test (the auth-rbac mechanism): parse every secrets_config production .py (excluding tests/) and assert none imports backend.database/backend.audit_store/backend.memo_agent_core/backend.auth_rbac/backend.intake — with a non-vacuous file-presence guard and a detector self-test.

## Question 4 — Governance checkability (BR-SEC-3/4)
Which governance properties become pass/fail here?

A) **Four checkable assertions**: (i) `.gitignore` lists `.env` **and** `.env` is **not git-tracked**; (ii) `.env.example`
   exists, names **all six** shapes, and carries **placeholder-only** values (no real secret); (iii) the required
   `Settings` fields have **no default** (Pydantic `model_fields` — nothing baked in); (iv) **no secret literal** in the
   `secrets_config` module source. The repo-wide `detect-secrets` sweep stays **`quality-gates`/CI** (referenced). Each
   is **independently testable now**. **Recommended.**
B) Only (iii)+(iv) (module hygiene), skip the `.env`/`.gitignore` checks (weaker — the user wants all three governance
   pieces checkable).
C) Policy statement only (rejected — must be checkable).
D) Other (please describe after [Answer]: tag below)

[Answer]: A — four checkable assertions: (i) .gitignore lists .env and .env is not git-tracked; (ii) .env.example exists, names all six shapes, placeholder-only values; (iii) required Settings fields have no default (Pydantic model_fields); (iv) no secret literal in the module source. Repo-wide detect-secrets sweep stays quality-gates/CI, referenced.

## Question 5 — Determinism / no-side-effects
How is NFR-SEC-DET-1 tested?

A) **Behavioral + light structural**: (behavioral) constructing `Settings` from the **same env** yields an **identical**
   result across repeats (no randomness); (structural) the validation path performs **no network I/O** and **no
   wall-clock branch** — asserted by an import-absence check (no `requests`/`httpx`/`socket`; no time-dependent branch in
   the validators) and by the construction being **offline/hermetic**. **Recommended.**
B) Assume purity because it is "just config" (rejected — the project makes determinism a checkable target).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — behavioral + light structural: constructing Settings from the same env yields an identical result across repeats; the validation path performs no network I/O and no wall-clock branch (import-absence check; no time-dependent branch in validators); construction is offline/hermetic.

## Question 6 — Scoped exclusions (explicit)
What does NFR-SEC-SCOPE-1 exclude?

A) **Targets test ONLY** `secrets-config`'s own schema / validation / governance / leaf property. They **do NOT** test:
   database / audit-store / memo-agent-core / auth-rbac **internals**; `deploy-config`'s per-environment value wiring;
   `quality-gates`' repo-wide secret sweep. **Labeled a governance/exclusion statement (not a runtime test)** — same as
   prior units' SCOPE targets. **Recommended.**
B) Leave the boundary implicit (rejected — the user asked for it explicit).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — targets test ONLY secrets-config's own schema/validation/governance/leaf property. They do NOT test database/audit-store/memo-agent-core/auth-rbac internals, deploy-config's per-environment value wiring, or quality-gates' repo-wide secret sweep. Labeled a governance/exclusion statement, not a runtime test.

## Question 7 — Test substrate + tech stack (companion `tech-stack-decisions.md`)
What does the NFR tech-stack pin?

A) **pytest**; **hermetic env per case** — construct `Settings` from an **explicit mapping / monkeypatched env** with
   **`_env_file=None`**, so tests **never depend on the developer's real environment** (no leakage of a real
   `DATABASE_URL`); **`pydantic-settings`** (already in the stack); **Hypothesis** (in stack) optional for invalid-URL
   fuzz; **Python 3.12**; **no new dependency**; **no LLM**. **Reference-not-own**: import no consumer / `database`
   production code (enforced by NFR-SEC-LEAF-1). **Recommended.**
B) Rely on the real process env in tests (rejected — non-hermetic; a developer's env could mask a missing-var case).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — pytest; hermetic env per case — construct Settings from an explicit mapping/monkeypatched env with _env_file=None, so tests never depend on the developer's real environment; pydantic-settings (already in stack); Hypothesis (in stack) optional for invalid-URL fuzz; Python 3.12; no new dependency; no LLM. Reference-not-own enforced by NFR-SEC-LEAF-1.

## Question 8 — Depth confirmation
What depth for this NFR Requirements stage?

A) **Standard** — the full pass/fail `NFR-SEC-*` set (fail-closed matrix, scheme validation, dependency-leaf,
   governance checkability, determinism, scoped exclusions; perf/obs soft/N-A), each traced to its FD rule, matching the
   single-control-but-SEC-3-critical weight. **Recommended.**
B) Minimal / Comprehensive (rejected — minimal under-serves a SEC-3 control; comprehensive over-weights a config unit).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — standard: the full pass/fail NFR-SEC-* set (fail-closed matrix, scheme validation, dependency-leaf, governance checkability, determinism, scoped exclusions; perf/obs soft/N-A), each traced to its FD rule, matching the single-control-but-SEC-3-critical weight.

---

## 4. Constraints & settled items held (not re-opened)
- The **frozen FD** (Settings schema + BR-SEC-1..7 + the load model) is the substrate — NFR builds testable targets
  **on** it, re-opening nothing.
- **Reference-not-own** — targets test `secrets-config`'s own schema/validation/governance/leaf property; **no consumer
  internals**; the **leaf property** (no `database`/consumer import, no circular dep) is realized as **NFR-SEC-LEAF-1**.
- **SEC-3** — no credential/URL VALUE in any artifact/test; **fail-closed** matrix; **`.env` hermetic** in tests.
- **DATA-5 spirit** — `postgresql://` scheme validation independent of `database` (NFR-SEC-SCHEME-1 + LEAF-1).
- **`deploy-config`** (actual per-env values) + **`quality-gates`** (repo-wide sweep) = referenced, not tested here.
- **Infrastructure Design** for `secrets-config` is **likely a logged SKIP** (pure-config unit — no independent cloud
  topology; `deploy-config` owns the per-env wiring). Confirmed at that stage, not pre-committed.
- Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, every built unit's code/design.

---

## 5. Next step (STOP here)
Fill the eight `[Answer]:` tags above. On your signal, I will read the answers, run the mandatory ambiguity-check
(adding a clarification file only if needed), then generate the two `secrets-config` NFR Requirements artifacts
(`nfr-requirements.md` + `tech-stack-decisions.md`) and present the standardized 2-option completion message. **No NFR
Requirements artifacts or code are generated until the answers are in and checked.**
