# NFR Requirements — `case-lifecycle` (U24, Scope B)

**Stage**: BUILD → NFR Requirements (per-unit), **Part 2 (Generation)** · **Unit**: U24 · **Scope B** ·
**Depth**: **comprehensive** · **Date**: 2026-07-20.
**Built ON** the frozen FD (**`BR-CASE-1..14`**; the five-state model + the internal `failed` state and its disclosed
wire-projection; the CANON-SER byte-identity design; the explicit `route_borderline` invocation; the namespaced +
collision-guarded migration sequence; the injected-dependency tier-U discipline; the frozen commit-boundary composition) —
**re-opening none.** Answers **Q1–Q3 (all A)** + folds **CASE-Req-Fold-1..3**.

**Tiers**: **tier-U** = fast, deterministic, in CI — **no live LLM, no key, no network, no Docker, no live DB**; every
LLM-bearing dependency **injected** and driven by an **offline double**; **every scan carries a detector self-test**.
**tier-I** = the existing `@pytest.mark.integration` marker (Docker + testcontainers Postgres), guarded by **`database`'s
known-good `_docker_available()` pattern** so it **SKIPS CLEANLY**. **tier-B** = **NOT authorized, NOT required.**

> **⚑ Baseline hold**: **1308 passed / 31 skipped / 5 pre-existing `audit_store` Docker-absence errors.** The **5 errors
> must stay exactly unchanged**. U24's tier-I tests **add new CLEAN SKIPS** when Docker is absent — an **expected,
> stated delta on the 31**, to be reported explicitly at Code-Gen, never discovered.

---

## 1. Finalized `NFR-CASE-*` targets — assertion · acceptance · tier · rigor

### ⚑ FULL RIGOR (HIGHEST) — the three LOAD-BEARING targets

#### NFR-CASE-CANON-1 — CANON-SER byte-identity (BR-CASE-7) — **[LOAD-BEARING]**

> **Why load-bearing, as a mechanism**: this target carries **CASE-GAP-1's entire resolution**. If canonicalization drifts,
> hash equality breaks **silently on a later run** and surfaces only at replay — the worst possible failure location for an
> audit system. It is **behavioural**: it proves the bytes actually round-trip and the hash actually catches a mutation.

- **Assertion**: the two rich shapes serialize **byte-identically across runs**, round-trip with **type fidelity**, and
  their `content_hash` **detects mutation**.
- **Acceptance** *(all tier-U — **no database required**; this is a pure `bytes → object → bytes` property)*:
  **(a)** `serialize → deserialize → serialize` is **byte-identical** for both `ApplicantProfile` and `RuleResultReport`;
  **(b)** **`Decimal` and `date` return as themselves**, not strings (CANON-SER **P2/P3** fidelity);
  **(c)** `content_hash` is **stable across repeated runs** of the same logical content (**P1/P4** — no key-order or
  volatile-field drift);
  **(d) mutation detector** — flipping a single stored byte makes the hash check **FAIL**;
  **(e)** a `float` anywhere in the payload **raises** (P2 is enforced, not hoped for).
- **Tier**: tier-U (component). **Rigor**: **full (highest) — LOAD-BEARING**.

#### NFR-CASE-ADAPTER-1 — the frozen adapter is never bypassed (BR-CASE-8) — **[LOAD-BEARING]**

> **⚑ Deliberately PAIRED with CANON-1, by a DIFFERENT mechanism.** CANON-1 would **still pass on a correct-but-FORKED
> serializer**; ADAPTER-1 would **still pass on a broken one**. **Neither alone is sufficient** — together they give *the
> encoding is correct* **and** *it is the single frozen encoding*. No single edit can weaken both.

- **Assertion**: **every** canonicalization in U24 goes through the **frozen `audit_store.CanonSerAdapter`**; nothing
  re-implements or bypasses it.
- **Acceptance**:
  **(a) AST scan** over **every U24 production module** — **no direct `canon_ser(...)` / `canon_deserialize(...)` call**,
  and **no re-implementation of the `.model_dump(mode="python")` reduction**;
  **(b) ⚑ the SQL-exec shim IS IN THIS SCAN SET** (CASE-Req-Fold-3) — the coverage `omit` is about *where a module is
  exercised*, **never** about *what it may contain*. The scan additionally asserts **positively** that the shim
  **contains no canonicalization call at all**: it receives **already-canonicalized bytes** and only executes SQL. *"The
  shim doesn't canonicalize"* is thus a **tested property, not a design intention**;
  **(c) detector self-tests** — a synthetic direct `canon_ser(...)` **is flagged**; a synthetic
  `model_dump(mode="json")` **is flagged** *(this is load-bearing: `mode="json"` pre-stringifies `Decimal`s so the `$dec`
  envelope never fires, **silently losing P2 fidelity**)*;
  **(d)** **no `$`-prefixed key** appears in any U24 payload (CANON-SER reserves them).
- **Tier**: tier-U (structural). **Rigor**: **full (highest) — LOAD-BEARING**.

#### NFR-CASE-COMMITBOUND-1 — U24 never finalizes a decision (BR-CASE-13) — **[LOAD-BEARING]**

> **Why load-bearing**: this is **the assertion that the system cannot commit without underwriter action** — the single
> most consequential invariant in the build. A defect here is the one that breaks human-in-the-loop.

- **Assertion**: U24 supplies **context only**. The CON-BR4 gate and the independent authz re-check run **inside the frozen
  `DecisionCommitService.commit()`** and are **never re-implemented**.
- **Acceptance**:
  **(a) Structural scan** — **no U24 module implements a commit gate, an authorization check, or a write to
  `audit_record`** (+ a **detector self-test for each of the three**);
  **(b) Behavioural** — `PendingCommitContextProvider.get()` returns a **`CommitContext` and nothing more**: it performs no
  authz, reaches no write path, and **raises for an unknown `recommendation_id`** (which R5 maps to **404**);
  **(c) ⚑ A `failed` case can never reach the boundary (CASE-Req-Fold-2)** — asserted **positively**, not assumed:
  **no `PendingRecommendation` exists for any case in state `failed`**, and driving `drafting_failure_double()` to `failed`
  then calling the provider **raises**. *(R5 is keyed by `recommendation_id`, the PK of `PendingRecommendation`, which is
  created **only** at the `drafted` transition — so the failed path and the commit path **structurally do not
  intersect**.)*;
  **(d) Atomicity** — creating the `PendingRecommendation` and moving to `drafted` occur in **ONE transaction**, closing
  the only route by which (c) could ever open.
- **Tier**: tier-U (structural + component). **Rigor**: **full (highest) — LOAD-BEARING**.

### FULL RIGOR

#### NFR-CASE-STATE-1 — the legal transition set (BR-CASE-1)
- **Assertion**: `submitted → profiled → evaluated → drafted → committed` is accepted, plus `→ failed` from the drafting
  attempt; each transition's artifact comes from the corresponding **frozen seam**, driven and never re-implemented.
- **Acceptance**: teeth over **every** legal transition; each asserts the producing frozen unit was **actually driven**
  (the injected double/spy records the call), so no transition is faked.
- **Tier**: tier-U. **Rigor**: full.

#### NFR-CASE-STATE-2 — illegal transitions are rejected, **exhaustively** (BR-CASE-2)
- **Assertion**: every non-legal transition is **rejected**.
- **Acceptance**: **(a)** explicit rejection teeth over the illegal set — `submitted→drafted` (skipping evaluation) ·
  `submitted→committed` · every **backward** move (`evaluated→profiled`, `drafted→evaluated`, …) · any transition **out of
  a terminal state** (`committed`, `failed`); **(b) ⚑ exhaustiveness detector** — the illegal set is enumerated **against
  the full state cross-product**, so a rejection that is *missing from the table* is caught, not just the ones anticipated;
  **(c)** the fixture returns them **as one collection** (Q2-A) so the set **cannot be trimmed one case at a time**.
- **Tier**: tier-U. **Rigor**: full.

#### NFR-CASE-EAGER-1 — eager advance, all-or-nothing (BR-CASE-3)
- **Acceptance**: submission reaches **`evaluated`**; **both** canonical payloads **and** their hashes are persisted; on a
  mid-way failure **NO partial row** exists (asserted by row/state count before and after). All steps are **LLM-free**.
- **Tier**: tier-U. **Rigor**: full.

#### NFR-CASE-TRIGGER-1 — R4 is a pure read (BR-CASE-4)
- **Acceptance**: **⚑ the R4 read path invokes the pipeline ZERO times** — the injected double records **no** calls and the
  case state is **unchanged** after the read; after the explicit trigger the state is `drafted` and R4 reports `ready`.
- **Tier**: tier-U. **Rigor**: full.

#### NFR-CASE-FAILED-1 — the failed terminal state is real (BR-CASE-5)
- **Acceptance**: a **failing** injected double drives the case to **`failed`**; `failed` is **internally distinguishable
  from `evaluated`** (a never-triggered case ≠ a broken one). Driven by **`drafting_failure_double()` — its own fixture
  family** (Q2-A), so this target **cannot be weakened by a success-path edit**.
- **Tier**: tier-U. **Rigor**: full.

#### NFR-CASE-CANONTIME-1 — canonicalization at the finalizing transition (BR-CASE-9)
- **Acceptance**: after submission **both** payloads **and** hashes exist; at drafting the **four version stamps** exist;
  `content_hash` **always matches** its stored bytes (co-located call site, so it cannot drift from what it attests).
- **Tier**: tier-U. **Rigor**: full.

#### NFR-CASE-ROUTE-1 — routing is invoked, and the mode is re-derivable (BR-CASE-10)
- **Acceptance**: **(a)** a **spy** records that `route_borderline` was called **with the real
  `(rule_report, outlier_result)` arguments** — not merely that a mode was produced; **(b)** a `REFER` report yields
  **`EXTENDED`** and **the adapter actually receives it**; **(c) ⚑ re-derivability** — recomputing the mode **from stored
  state alone** reproduces the same value, which is what makes **not persisting `ThinkingMode`** safe for reproducibility.
- **Tier**: tier-U. **Rigor**: full.

#### NFR-CASE-MIGNAME-1 — migration namespacing + collision guard (BR-CASE-11)
- **Acceptance**: U24's migration filenames are **disjoint** from U15's; **detector self-test — a synthetic colliding
  filename IS flagged**; `verify_checksums` passes against **U24's own manifest**. *(The hazard being guarded: the shared
  `applied_migrations` PK is the **bare filename**, so a collision would be **silently skipped as already-applied — a
  no-op, not an error**.)*
- **Tier**: tier-U (structural + detector). **Rigor**: full.

#### NFR-CASE-MIGSCOPE-1 — invocation confined to U24's own sequence (BR-CASE-12)
- **Acceptance**: a scan asserts U24 **never** passes `database`'s default `MIGRATIONS_DIR`, **never edits U15**, and
  **authors no CLI entrypoint** — **#8 `DEPLOY-MIGRATE-DEFERRED` is NOT adopted and NOT made worse**.
  **⚑ Plus the containment condition (CASE-Req-Fold-1)**: U24's migration **grants to no U15-owned role**, which is what
  keeps the tier-I test self-contained.
- **Tier**: tier-U (structural). **Rigor**: full.

#### NFR-CASE-PERSIST-1 — the SQL round-trip actually round-trips (Q1-A) — **tier-I**
- **Assertion**: the persisted `BYTEA` returns the **exact bytes** written, and U24's migration produces the tables it
  claims.
- **Acceptance** *(tier-I, `@pytest.mark.integration`)*: against a **fresh testcontainers Postgres** with **only U24's
  migration sequence applied**: **(a)** the two tables exist with their declared columns; **(b)** a written `BYTEA`
  round-trips **byte-identically**, and its `content_hash` still verifies; **(c)** the scalar stamps round-trip.
  **⚑ Guarded by `database`'s `_docker_available()` pattern — the ping happens INSIDE the fixture body**, so it **SKIPS
  CLEANLY and adds ZERO errors** (never `audit_store`'s `importorskip`-only pattern, which is what produces the 5).
  **Self-contained**: no U15 migration, no cross-unit FK, no U15 role required.
- **Tier**: **tier-I**. **Rigor**: full (within its tier).

### GOVERNANCE / DISCLOSURE

#### NFR-CASE-PROJECT-1 — the failed→pending wire projection, disclosed (BR-CASE-6)
- **Assertion**: a `failed` case yields a **WIRE-1-VALID** `MemoView` with **`status == "pending"`** — the only legal
  value — and the imprecision is **disclosed, never hidden**.
- **Acceptance**: **(a)** the projection produces a contract-valid `MemoView`; **(b) a DOC-1-style token checklist** for
  register **#14 `MEMOVIEW-FAILED-STATE-UNMODELLED`** — its **name + owner (a future authorized WIRE-1 amendment) +
  rationale** are present, and **no U24 artifact claims WIRE-1 models a failed state**; **(c) detector self-test** —
  removing the disclosure token **fails** the check. *(Mirrors `llm-judge`'s DISCLOSE-1 exactly.)*
  **WIRE-1's contract text is NOT amended.**
- **Tier**: tier-U + governance. **Rigor**: governance (structural teeth on presence).

#### NFR-CASE-NOMETRIC-1 — no new metric (BR-CASE-14)
- **Acceptance**: **(a) provenance scan** — **no U24 module declares a metric name or `MetricDefinition`** (+ detector);
  **(b) corroborating static check** — `observability`'s **five** `METRIC_DEFINITIONS` and `deploy-config`'s
  `grafana-dashboard.json` (**five panels, no nested `panels` key**) read **read-only** and asserted unchanged.
  **⚑ NEITHER UNIT'S SUITE IS RE-RUN.** *(Mirrors `llm-judge`'s NOMETRIC-1 exactly.)*
- **Tier**: tier-U (structural). **Rigor**: full.

### SOFT / OBSERVED · GOVERNANCE

#### NFR-CASE-PERF-1 — observed, never gated
- **Assertion / Acceptance**: **U24 owns no runtime SLO.** The drafting step's cost is **out-of-band** (its own trigger,
  not a request-path read). Nothing is timed at tier-U — the LLM is an offline double. **No U24 test asserts a timing
  failure.**
- **Tier**: observed / soft. **Rigor**: soft.

#### NFR-CASE-SEC-1 — scoped exclusions *(not a runtime test)*
- **Statement**: this set tests **only** `case-lifecycle`. It does **not** test other units, the WIRE-1 route bindings (a
  later wiring pass), the frozen commit enforcement (**U12's**), memo generation (**U4's**), routing *logic* (**U19's** —
  U24 asserts only that it is **invoked**), or the tier-B corpus (**NOT authorized**). Enforced by review + the structural
  scans above.
- **Tier**: N/A (governance).

---

## 2. Traceability — target → `BR-CASE` → tier → rigor (**NO ORPHAN**)

| Target | BR-CASE | Tier | Rigor |
|---|---|---|---|
| **NFR-CASE-CANON-1** | **BR-CASE-7** | tier-U (component) | **full (highest) — LOAD-BEARING** |
| **NFR-CASE-ADAPTER-1** | **BR-CASE-8** | tier-U (structural) | **full (highest) — LOAD-BEARING** |
| **NFR-CASE-COMMITBOUND-1** | **BR-CASE-13** | tier-U (structural + component) | **full (highest) — LOAD-BEARING** |
| NFR-CASE-STATE-1 | BR-CASE-1 | tier-U | full |
| NFR-CASE-STATE-2 | BR-CASE-2 | tier-U | full |
| NFR-CASE-EAGER-1 | BR-CASE-3 | tier-U | full |
| NFR-CASE-TRIGGER-1 | BR-CASE-4 | tier-U | full |
| NFR-CASE-FAILED-1 | BR-CASE-5 | tier-U | full |
| NFR-CASE-PROJECT-1 | BR-CASE-6 (+ register #14) | tier-U + governance | governance |
| NFR-CASE-CANONTIME-1 | BR-CASE-9 | tier-U | full |
| NFR-CASE-ROUTE-1 | BR-CASE-10 | tier-U | full |
| NFR-CASE-MIGNAME-1 | BR-CASE-11 | tier-U (detector) | full |
| NFR-CASE-MIGSCOPE-1 | BR-CASE-12 | tier-U (structural) | full |
| NFR-CASE-NOMETRIC-1 | BR-CASE-14 | tier-U (structural) | full |
| **NFR-CASE-PERSIST-1** | BR-CASE-7/9 *(the persistence half)* | **tier-I** | full (in tier) |
| NFR-CASE-PERF-1 | (soft perf) | observed | soft |
| NFR-CASE-SEC-1 | governance | N/A | governance |

**No orphan** — every `BR-CASE-1..14` maps to ≥1 target: 1→STATE-1 · 2→STATE-2 · 3→EAGER-1 · 4→TRIGGER-1 · 5→FAILED-1 ·
6→PROJECT-1 · **7→CANON-1 + PERSIST-1** · **8→ADAPTER-1** · 9→CANONTIME-1 (+PERSIST-1) · 10→ROUTE-1 · 11→MIGNAME-1 ·
12→MIGSCOPE-1 · **13→COMMITBOUND-1** · 14→NOMETRIC-1. PERF-1/SEC-1 cover cost + governance.

**The five inherited invariants** → advisory-only/human-in-the-loop: **COMMITBOUND-1** · no LLM in the rules path:
EAGER-1 · `temperature=0`: TECH-DEC (centrally fixed in frozen adapters; U24 sets nothing) · bias-free: the shape is
persisted unwidened · reproducibility: **CANON-1 + ADAPTER-1 + CANONTIME-1 + ROUTE-1(c)**.

---

## 3. Security-Guardrails extension — compliance (enabled extension)

`case-lifecycle` **adds the first reachable write path in the system** and a **new persistent store**, so the controls are
assessed against exactly those additions.

| Control | Status | Rationale |
|---|---|---|
| **⚑ Human-in-the-loop (advisory-only)** | **Compliant — LOAD-BEARING** | **NFR-CASE-COMMITBOUND-1.** U24 supplies **context only**; the CON-BR4 gate and the independent authz re-check run **inside the frozen `DecisionCommitService`**. The pending store holds **recommendations, never decisions**; a `CommittedDecision` exists **only** as R5's result. **A `failed` case structurally cannot reach the boundary** (COMMITBOUND-1(c)). |
| Input validation | **Compliant (referenced)** | Applications enter through **frozen `intake`** — the Pydantic gate and the sanitizer are U1/U2's and are **driven, never bypassed**. U24 adds no parallel parsing path. |
| Prompt-injection defense | **Compliant (referenced)** | Injection-bearing text is neutralised **upstream** by `document-sanitizer` **before** U24 assembles anything; U24 builds no prompt of its own. |
| Secrets management | **Compliant (referenced)** | Engines come from **`secrets-config`** (SEC-3); **no key is read at tier-U**; tier-I uses a **throwaway fixture-scoped** container password, never a real credential. |
| **Least-privilege DB access** | **Compliant** | U24's store is reached via the **`DATABASE_URL` owner engine**; it **grants nothing to `audit_writer`/`audit_reader`** and **does not widen** their frozen grants (MIGSCOPE-1). |
| **Append-only / no destructive path** | **Compliant** | U24 writes **pending** rows only; it performs **no write to `audit_record`** (COMMITBOUND-1(a)) — the append-only audit surface stays exclusively the frozen service's. |
| Audit logging | **Compliant (composes, does not persist)** | U24 assembles the `CommitContext`; the **audit record itself is written only by `DecisionCommitService`**, atomically. |
| Error hygiene (no secret/PII leak) | **Compliant** | No secret exists at tier-U to leak; the provider raises a **bare not-found** for an unknown id (no caller data echoed); tier-I passwords are throwaway. |
| **Bias-free by design (CON-BR1)** | **Compliant** | No demographic attribute enters rule evaluation, outlier features, or any prompt. `ApplicantProfile` is persisted **as a frozen shape, not widened**. |
| **Reproducibility (CON-DET-1)** | **Compliant — LOAD-BEARING** | **CANON-1 + ADAPTER-1**: byte-identical CANON-SER on **both sides of the commit boundary**, `content_hash` tamper-evidence, the **four version stamps** as first-class columns, and `ThinkingMode` **re-derivable** from stored state. |
| No LLM in the deterministic rules path | **Compliant** | The eager transaction (`profiled`/`evaluated`) is **LLM-free by construction**; the LLM sits **strictly after** rule evaluation. |
| Full explainability | **Compliant (carries, does not author)** | U24 persists and serves the memo, rule report and outlier result unchanged; it adds no unexplained field and **declares no verdict of its own**. |
| **Deliverable transparency** | **Compliant (registered)** | **#14 `MEMOVIEW-FAILED-STATE-UNMODELLED`** disclosed by name with owner + rationale (PROJECT-1); **#8 `DEPLOY-MIGRATE-DEFERRED`** referenced and **not adopted** (MIGSCOPE-1). **U24 claims no discharge of either.** |

**No blocking finding.**

---

## 4. Settled items held (not re-opened)

- The **frozen FD** (`BR-CASE-1..14` + the five states + the CANON-SER design + the explicit routing step + the migration
  namespacing + the commit-boundary composition) is the substrate.
- **Q1-A** — two tiers; pure logic at tier-U **with no database at all**; only the SQL round-trip at **tier-I** with
  **`database`'s clean guard**. **CASE-Req-Fold-1**: the tier-I test is **self-contained** (no cross-unit FK, no U15 role,
  idempotent tracking table) — **conditional on U24's migration granting to no U15 role**, which MIGSCOPE-1 asserts.
- **Q2-A** — one shared `tests/fixtures.py` with **named families**; `illegal_transition_cases()` returned **as one
  collection** (unsplittable) and `drafting_failure_double()` as **its own family**.
- **Q3-A** — `--cov=backend/case_lifecycle` with a **narrow SQL-exec-shim omit** (the `pg_repository.py` precedent
  verbatim); everything else counted and expected at **100%**; `--cov-fail-under=90` **UNCHANGED**.
  **CASE-Req-Fold-3**: **coverage-omit ≠ scan-exclusion** — the shim **remains in ADAPTER-1's scan set**, with a
  **positive assertion** that it contains no canonicalization call.
- **CASE-Req-Fold-2** — a `failed` case **structurally cannot** reach the commit boundary; asserted positively, with
  **transactional atomicity** closing the only route that could open it.
- **Deferred to NFR Design / Code-Gen**: module layout under `backend/case_lifecycle/`; the exact scan token sets; the
  fixture builders' precise signatures; the `pyproject.toml` `--cov` line and omit entry.
- **Untouched**: **WIRE-1's contract text** · **Q1-B** · **`not_wired.py`** · **U23's test** · every frozen unit's
  internals · the **`audit_store` Docker-guard gap** (**5 errors unchanged**) · **tier-B (NOT authorized)**.
