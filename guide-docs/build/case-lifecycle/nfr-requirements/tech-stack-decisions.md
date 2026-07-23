# Tech-Stack Decisions — `case-lifecycle` (U24, Scope B)

**Stage**: BUILD → NFR Requirements (per-unit), **Part 2 (Generation)** · **Unit**: U24 · **Scope B** ·
**Depth**: **comprehensive** · **Date**: 2026-07-20.
**Built ON** the frozen FD + the finalized `NFR-CASE-*` targets — **re-opening none.** Answers **Q1–Q3 (all A)** + folds
**CASE-Req-Fold-1..3**.

> **HEADLINE: NO NEW DEPENDENCY.** Everything U24 needs is **already floored AND installed** — including
> `testcontainers[postgresql]`, which `database`'s own integration tier already uses. **`requirements.txt` is NOT edited.**

---

## 1. Dependency verification (measured on disk, not assumed)

| Library | `requirements.txt` | Installed | Role at U24 |
|---|---|---|---|
| `pytest` / `pytest-cov` | floored + installed | INSTALLED | tier-U runner + the QA-6 coverage gate (every prior unit) |
| **`testcontainers[postgresql]`** | **`>=4.0.0` (floored, L33)** | **INSTALLED** | the **tier-I** Postgres container — **already used by `database`'s own tests** |
| `docker` (a testcontainers dependency) | transitive | INSTALLED | the **`_docker_available()` daemon ping** that makes the skip clean |
| `sqlalchemy` | floored + installed | INSTALLED | the engine/SQL-exec shim (the omitted module, §3) |
| `pydantic` v2 | floored + installed | INSTALLED | the frozen shapes U24 consumes; `.model_dump(mode="python")` inside the **frozen** adapter |

**`requirements.txt` is NOT edited. U24 adds no library.**
**⚑ Contrast with `llm-judge` (U22)**: there, a floored dependency (`promptfoo`) turned out to be a **shim with an absent
engine** — a genuine disclosable gap. **Here there is no such gap**: `testcontainers` is floored, installed, **and already
exercised in CI by a sibling unit's integration tier.** Nothing is deferred on the dependency axis.

---

## 2. Decisions (CASE-D1..CASE-D9)

- **CASE-D1 — tier-U runner: `pytest`.** No new dependency. **tier-U** = no live LLM, no key, no network, **no Docker, no
  live DB**. Every LLM-bearing dependency is **injected** and driven by an **offline double**; every scan carries a
  **detector self-test**.

- **CASE-D2 — ONE shared `tests/fixtures.py` with deliberately-separate NAMED FAMILIES (Q2-A)** — the
  `outlier-model` / `memo-extensions` / `llm-judge` convention:

  | Family | Serves | Why it is its own family |
  |---|---|---|
  | `clean_case()` | STATE-1 · EAGER-1 | the baseline that advances to `evaluated` |
  | **`illegal_transition_cases()`** | **STATE-2** | **returned as ONE collection — UNSPLITTABLE**, mirroring `anchoring_pair()`, so the rejection set **cannot be trimmed one case at a time** |
  | `drafting_success_double()` | STATE-1 · TRIGGER-1 · ROUTE-1 | the injected offline double for the happy drafting path |
  | **`drafting_failure_double()`** | **FAILED-1 · COMMITBOUND-1(c)** | **its OWN family**, mirroring `exempt_witness_sample()`, so **FAILED-1 can never be weakened by a success-path edit** |
  | `borderline_refer_case()` | ROUTE-1 | a `REFER` report that **must** route `EXTENDED` |

- **CASE-D3 — tier-I uses `database`'s KNOWN-GOOD guard, never `audit_store`'s (Q1-A).** **Measured**: the two existing
  guards behave differently, and the difference **is** register item #4.

  ```python
  def _docker_available() -> bool:
      try:
          import docker; docker.from_env().ping(); return True
      except Exception:
          return False

  @pytest.fixture(scope="session")
  def migrated_engine():
      if not _docker_available():
          pytest.skip(...)                    # ⚑ INSIDE the fixture body → CLEAN SKIP
      with PostgresContainer("postgres:16") as pg: ...
  ```
  **⚑ The ping happens INSIDE the fixture body, before any container is constructed** — that is precisely why it skips
  cleanly, whereas `audit_store`'s `importorskip`-only pattern reaches container construction and **errors** (the 5
  pre-existing errors). **U24 mirrors `database`'s template exactly** and therefore **adds ZERO errors**.
  **⚑ Stated, not discovered**: U24's tier-I tests **WILL add new CLEAN SKIPS** to the 31 when Docker is absent. This is an
  **expected delta to be reported explicitly at Code-Gen.** *(Adopting `audit_store`'s pattern was rejected: it would
  **grow the error count**, breaking the standing hold and propagating a known defect sitting one directory from a
  known-good alternative.)*

- **CASE-D4 — the tier-I test is SELF-CONTAINED (CASE-Req-Fold-1).** It applies **only U24's own migration sequence** to a
  fresh container via `MigrationRunner(engine, migrations_dir=<U24's>)`. **U15's migrations are NOT required**, because:
  **(1)** no cross-unit FK — `PendingRecommendation` FKs to `PendingApplication`, both U24's; the `recommendation_id` later
  seen in `audit_record` is a **logical reference, not a DB FK** (the `BR-DB-11` posture); **(2)** U24's store uses the
  **owner engine**, so its migration **grants to no U15 role** and needs no `0002_grants.sql`; **(3)** `applied_migrations`
  is created **idempotently** (`CREATE TABLE IF NOT EXISTS`). **⚑ Condition pinned**: if U24's migration ever granted to a
  U15-owned role, containment would break — **MIGSCOPE-1 asserts it does not.**

- **CASE-D5 — canonicalization goes through the FROZEN `audit_store.CanonSerAdapter`, never re-implemented (BR-CASE-8).**
  U24 calls `CanonSerAdapter.canonical_bytes(model)` / `.content_hash(model)`. **⚑ Why this matters mechanically**:
  `canon_ser` takes **plain values, not Pydantic models**, and the reduction **must** be `.model_dump(mode="python")` —
  `mode="json"` pre-stringifies `Decimal`s so the `$dec` envelope never fires, **silently losing P2 type fidelity**. The
  frozen adapter already encodes this; **U24 must not re-derive it**, and ADAPTER-1 scans for exactly that.

- **CASE-D6 — CANON-SER `BYTEA` + `content_hash`, mirroring `0001_initial_schema.sql` (Q8-A of FD).** The two rich shapes
  are stored as canonical bytes with a hash; the **four version stamps** are **first-class scalar columns**. This makes the
  **pending and committed sides byte-identical**, so **no conversion sits on the replay path**.

- **CASE-D7 — `route_borderline` is an EXPLICIT pipeline step (BR-CASE-10).** It is **not** internal to the orchestrator
  (measured: zero routing references there). U24 calls it and passes the resulting `ThinkingMode` to the adapter's
  **constructor**. **`ThinkingMode` is NOT persisted** — it is a pure function of two persisted shapes, hence
  **re-derivable**; ROUTE-1(c) asserts that re-derivation.

- **CASE-D8 — `temperature=0` is NOT U24's to set.** It stays **centrally fixed inside U19's frozen adapters**; U24
  **neither sets nor overrides it** and constructs no provider client of its own beyond injecting the frozen ones.

- **CASE-D9 — module layout OPEN.** Sized to the FD's components (state machine + transitions · the pending store + its
  SQL-exec shim · the canonicalization call sites · `CasePipeline` · `PendingCommitContextProvider` · the migration
  sequence). Exact module names finalized at **NFR Design / Code-Gen**.

---

## 3. Coverage — `--cov=backend/case_lifecycle` with a NARROW persistence-shim omit (Q3-A)

**⚑ The expectation going in was "no omit". Measured on disk, a carve-out is the build's ESTABLISHED precedent** —
`pyproject.toml`'s `[tool.coverage.run] omit` already excludes **every** live-DB/SQL-exec module in the build:

```
"*/pg_repository.py",                 # SQLAlchemy/Postgres impl — exercised via testcontainers
                                      # integration in CI, not unit-import-covered
"*/database/migration_runner.py",     # live-DB modules ... omitted exactly like pg_repository.py
"*/database/schema_introspector.py",
"*/database/fidelity_comparator.py",
"*/admin_cli/pg_writer.py",           # the SQL-exec shim ... omitted exactly like pg_repository.py
```
…each carrying the **same stated rule**: *"the pure-logic modules stay counted and are unit-covered to >=90% (QA-6)."*

**The decision**: add `--cov=backend/case_lifecycle` and omit **exactly one module** — U24's **SQL-exec/repository shim**
(the module that issues SQL), following `pg_repository.py` **verbatim**. **Everything else stays counted and is expected at
100%**: the state machine, the transition rules, the canonicalization call sites, `CasePipeline`, the provider's assembly
logic, and the migration-sequence definition. **`--cov-fail-under=90` UNCHANGED.** The omit comment will state **which
precedent it follows** and **which modules remain counted**.

**Why not "no omit" (option B)**: `observability` and `llm-judge` could say "no omit" at zero cost because they have **no
SQL-exec module at all**. U24 has one, so the same words would mean something different here — either the shim gets
imported at tier-U (defeating the tier split) or the number drops for a reason unrelated to test quality.

### ⚑ Coverage-omit ≠ scan-exclusion (CASE-Req-Fold-3)

**These are two different sets and must not be conflated:**

| | coverage `omit` | ADAPTER-1's structural scan |
|---|---|---|
| Purpose | excludes from **line-coverage measurement** | asserts **no module bypasses the frozen adapter** |
| Scope | the SQL-exec shim only | **EVERY U24 production module — INCLUDING the shim** |

**The shim is in the scan set precisely BECAUSE it is out of the coverage set.** Its coverage exclusion is about *where it
is exercised* (tier-I); the scan is about *what it may contain*. If the scan inherited the omit, a direct `canon_ser(...)`
call inside the shim would be **structurally invisible**. ADAPTER-1 therefore asserts **positively** that the shim
**contains no canonicalization call at all** — it receives **already-canonicalized bytes** and only executes SQL — making
*"the shim doesn't canonicalize"* a **tested property, not a design intention**.

---

## 4. Held

- **No new dependency**; **`requirements.txt` NOT edited**; **`pyproject.toml` NOT edited at this stage** (the `--cov` line
  and its omit entry land at **Code-Gen**).
- **No code · no wiring · `backend/case_lifecycle/` ABSENT · nothing under `backend/app/` touched.**
- **The frozen FD re-opened NONE.**
- **Baseline hold**: **1308 passed / 31 skipped / 5 pre-existing `audit_store` Docker-absence errors** — the **5 errors
  stay exactly unchanged**; the **skip delta from U24's tier-I tests is expected and will be stated**, not discovered.
- **Untouched**: **WIRE-1's contract text** · **Q1-B** · **`not_wired.py`** · **U23's test** · every frozen unit's
  internals (`canon_ser.py`, `canon_adapter.py`, `borderline_router.py`, `MigrationRunner`, `DecisionCommitService`
  consumed **read-only / through existing seams**) · the **`audit_store` Docker-guard gap** · **tier-B (NOT authorized)**.
- **Disclosed, not adopted**: **#8 `DEPLOY-MIGRATE-DEFERRED`** (U24 makes it no worse) · **#14
  `MEMOVIEW-FAILED-STATE-UNMODELLED`** (disclosed by PROJECT-1).
