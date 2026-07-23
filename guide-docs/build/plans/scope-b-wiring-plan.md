# Scope B — In-Place Composition-Root Wiring Pass (R2–R5 → U24) · SCOPING PLAN

**Stage**: POST-BUILD → **SCOPE B, final authorized step** — the in-place composition-root wiring pass
**Nature**: **SCOPING / PLANNING ONLY.** No wiring code is generated in this pass. Plan-then-answer + `[Answer]:` tags.
**Date**: 2026-07-20 · **Predecessor**: `scope-b-r2-r5-plan.md` (Q1–Q9, all A) · **Vehicle**: `case-lifecycle` (U24), complete 5/5 stages
**Composition root**: ⚑ **REOPENED — 2nd and FINAL time** under Scope B authorization (logged to `audit.md` and `guide-state.md` *before* this plan was written)

> **STOP AT THE PLAN-FILE GATE.** Eleven `[Answer]:` tags below, **none pre-filled**. Three of them (Q1, Q2, Q3) are
> **blockers found on disk** that make the briefed goal — *"the demo path is runnable end-to-end"* — **unachievable by
> this wiring pass alone**. They are surfaced, not improvised around.

---

## 0. Executive summary — what the ground-truth pass actually found

The wiring itself is **mechanically small and low-risk**: the composition root already has a proven two-layer
thin-adapter pattern (`Depends(...)` an injected frozen service → hand the result to a pure projection), U24's public
surface is clean, and **U23's frozen assertion needs zero edits** (verified, §2.5). If the only question were *"can
R2–R5 be wired in place following the existing pattern"*, the answer is **yes, straightforwardly**.

But the ground-truth pass surfaced **three hard blockers** that no prior artifact anticipated. Each is a **missing
piece of U24's public surface or of the frozen route set** — not a design preference:

| # | Blocker | Why it blocks | Question |
|---|---|---|---|
| **B1** | **`CaseStore` exposes no list/browse method** | R2 is `GET /applications?page=&size=` — a **paginated list**. U24 can fetch **one** application by id and **one** recommendation by id. There is **no enumeration primitive at all.** | **Q1** |
| **B2** | **No production `CaseSeams`, no production `recommendation_id_factory`** | `CasePipeline.__init__` requires both. The only implementations are **test doubles** in `case_lifecycle/tests/fixtures.py`. The pipeline **cannot be constructed outside tests.** | **Q3** |
| **B3** | **Nothing populates the pending store** | WIRE-1 pins **exactly** R1–R7 and contains **no ingestion route**. `submit()` therefore has **no HTTP caller**, and none may be added (the frozen route set is exact — §2.5). R2/R3/R4 read a **permanently empty** table. | **Q2** |

⇒ **Wiring R2–R5 exactly as briefed produces**: R2 that cannot be implemented at all (B1), and — even if it could —
R2/R3/R4 returning empty/404 forever (B3), with R5 unreachable because no `recommendation_id` can ever come into
existence (B2+B3). **R5's code path would be correct and permanently unexercised.**

Two further **genuine gaps** were found that are narrower but must be decided, not discovered later:

- **G1 — the `CommitRejected` mapping is ambiguous.** WIRE-1 §4 assigns a **blank-reason override → 409** and an
  **action outside `{approve, override}` → 422**. The frozen `_gate` raises the **same flat `CommitRejected` type** for
  both (plus for a missing `underwriter_id`). The route **cannot distinguish them** without either string-matching the
  exception message (fragile) or pre-checking in the route (which duplicates the gate — the explicitly rejected Q5-B).
  **See Q6.**
- **G2 — the `drafted → committed` transition is never performed by any code.** It is declared legal in
  `LEGAL_TRANSITIONS` and `COMMITTED` is in `TERMINAL_STATES`, but a repo-wide scan finds **no caller**. `CasePipeline`
  transitions only to `FAILED`. Consequence: **nothing marks a recommendation as committed**, so WIRE-1 §4's
  *"already-committed recommendation → 409"* has **no enforcement** and the same `recommendation_id` can be committed
  **repeatedly**, writing a **duplicate `AuditRecord` each time**. **See Q6.**

---

## 1. Ground truth — re-established from disk this session

Read in full, no assumed history. **Seven divergences from the session brief are reported rather than absorbed.**

### 1.1 Divergences from the brief

| # | Brief said | Disk says |
|---|---|---|
| 1 | `guide-docs/PROJECT-BRIEF.md` | **Repo root** — `PROJECT-BRIEF.md`. Read from the real location. |
| 2 | "the **five** `_not_wired` stubs for R2–R5" | **Four** stubs — `list_applications` (R2) · `get_application` (R3) · `get_application_memo` (R4) · `commit_recommendation` (R5). One route each. |
| 3 | "the **five composition-root tests**" | Five **test functions inside ONE file**, `backend/app/tests/test_no_write_route.py` — not five files. Count confirmed; three survivors confirmed (§2.4). |
| 4 | register "currently **14** items" | `BUILD-COMPLETION-REPORT.md` records **12**. #13 and #14 were opened later (Scope B plan · U24 `states.py`) and **never folded back into the report**. **14 in substance, 12 in that document** — a documentation lag. |
| 5 | — | ⛔ **B1** — `CaseStore` has **no list/browse method**. |
| 6 | — | ⛔ **B2** — no production `CaseSeams` / `recommendation_id_factory`. |
| 7 | — | ⛔ **B3** — nothing populates the pending store; no ingestion route exists or may be added. |

### 1.2 How R1/R6/R7 are wired today — the pattern R2–R5 must follow

**R1 — `routes/session.py`** (the whole handler):
```python
@router.get("/session")
def get_session(identity: Identity = Depends(current_identity)) -> dict[str, Any]:
    return {"user_id": identity.user_id, "role": identity.role.value}
```
`Depends` → dict projection. **No logic.** No authorization (R1 delivers identity, it gates nothing).

**R6/R7 — `routes/decisions.py`**: `Depends(require_read_audit)` (authz) + `Depends(get_audit_service)` (the frozen
service) → call `service.browse_history()` / `service.get(id)` → hand to a **pure projection**
(`decision_list_wrapper` / `audit_record_wire`). R7's `None` → `WireError(NOT_FOUND, "No such decision.")` with a
**static message carrying no caller value**. **No logic in the handler.**

⇒ **The R2–R5 handler shape is fixed by precedent**: `Depends(...)` an injected U24 object, call **one** method, hand
the result to a **pure projection function in `projections.py`**, map the absent case to a `WireError`.

### 1.3 The four `_not_wired` stubs as registered today

`routes/not_wired.py` — one module-level `router`, a static `NOT_WIRED_MESSAGE`, and a `_not_wired(route)` helper that
raises `WireError(NOT_IMPLEMENTED, NOT_WIRED_MESSAGE, {"route": route})`:

| Handler | Decorator | Signature | Body |
|---|---|---|---|
| `list_applications` | `@router.get("/applications")` | `() -> None` | `_not_wired("R2")` |
| `get_application` | `@router.get("/applications/{application_id}")` | `(application_id: str) -> None` | `_not_wired("R3")` |
| `get_application_memo` | `@router.get("/applications/{application_id}/memo")` | `(application_id: str) -> None` | `_not_wired("R4")` |
| `commit_recommendation` | `@router.post("/recommendations/{recommendation_id}/commit")` | `(recommendation_id: str) -> None` | `_not_wired("R5")` |

⚑ **Note**: the stubs take **no `Depends`, no body, no query params** — R2 does not even declare `page`/`size` today.
Registered in `main.py` as `app.include_router(not_wired.router)  # R2-R5 markers`.

### 1.4 `dependencies.py` — the current DI

- **Two engines, `lru_cache(maxsize=1)`, lazy**: `app_engine()` → `DATABASE_URL` (owner; the **only** engine that may
  read `app_user`) · `reader_engine()` → `AUDIT_READER_URL` (SELECT-only). **Derived from the frozen `0002_grants.sql`,
  not chosen** — audit roles cannot read `app_user`. **`AUDIT_WRITER_URL` is never read.**
- **Settings read at REQUEST time, never at import** — `create_app()` constructs no engine and reads no setting, so
  importing `main` needs no environment. Frozen `Settings` is **fail-closed**: all six fields required
  (`DATABASE_URL`, `AUDIT_WRITER_URL`, `AUDIT_READER_URL`, `AUDIT_WRITER_PASSWORD`, `AUDIT_READER_PASSWORD`,
  `GEMINI_API_KEY`), with `postgresql://` scheme validators.
- **Identity**: `USER_ID_HEADER = "X-User-Id"` → `current_identity()` resolves it against `app_user` via the frozen
  `PostgresUserRoleRepository`. **The role never comes from the request** — only the user id does; `to_role` fail-closes
  to `None` → 401. **A claimed role cannot elevate.**
- **Authorization**: `require_read_audit()` applies the frozen `PERMISSION_MATRIX` verbatim through `ApiAuthGuard`
  (Q1-B divergence recorded in the docstring, **unresolved, not touched by this pass**).

### 1.5 `projections.py` — the current contract

Documented verbatim as *"The composition root's **ONLY** transformation layer"* — **pure functions, no I/O, no state**.
Four functions today: `decision_summary` · `paginate` · `decision_list_wrapper` · `audit_record_wire`. `DEFAULT_PAGE_SIZE
= 20`. `paginate` is **1-based**, returns `(page_items, total)` with `total` = the **full** count, and an out-of-range
page yields an **empty slice, never an error**. **Enum wire values are emitted BY VALUE and never re-cased** (WIRE-1 §1).

### 1.6 U24's public surface **as built** (read from `backend/case_lifecycle/`, not as planned)

```python
# pipeline.py
class CasePipeline:
    def __init__(self, store: CaseStore, seams: CaseSeams,
                 recommendation_id_factory: Callable[[str], str]) -> None
    def submit(self, application_id: str, raw: object) -> PendingApplication
    def draft(self, application_id: str) -> DraftOutcome
    def read(self, application_id: str) -> Optional[PendingApplication]

@dataclass(frozen=True)
class DraftOutcome:
    memo: Optional[object] = None; outlier: Optional[object] = None
    thinking_mode: Optional[object] = None; failure_reason: Optional[str] = None
    @property
    def succeeded(self) -> bool          # memo is not None

class CaseSeams(Protocol):               # ⚑ NO production implementation exists
    def profile(self, raw) -> object; def evaluate(self, profile) -> object
    def score_outlier(self, profile) -> Optional[object]
    def draft_memo(self, profile, report, thinking_mode) -> Optional[object]

# provider.py
class PendingCommitContextProvider:
    def __init__(self, store: CaseStore) -> None
    def get(self, recommendation_id: str) -> CommitContext   # raises UnknownPendingRecommendation
class UnknownPendingRecommendation(KeyError)

# states.py
def case_to_memo_view_state(case: PendingApplication) -> Literal["ready", "pending"]
    # drafted -> "ready"; EVERYTHING else INCLUDING failed -> "pending"  (register #14)

# store.py — the CaseStore Protocol  ⚑ NOTE THE ABSENCE OF ANY LIST METHOD
atomic() · put_application · get_application · put_recommendation · get_recommendation
· recommendation_for_application

# repository.py
class PostgresCaseStore:
    def __init__(self, engine: sa.Engine) -> None        # writes require being inside atomic()

# migrate.py
def apply_case_migrations(engine: sa.Engine) -> list[str]   # guard-first; the ONLY sanctioned entry point
def assert_no_collision_with_database() -> None
```

⚑ **`PendingApplication` carries `profile_canonical: bytes` + `rule_results_canonical: Optional[bytes]`** — CANON-SER
bytes, **not** JSON. Rehydration is via the frozen `CanonSerAdapter.profile_from_canonical` /
`report_from_canonical`. **`PendingApplication` does NOT carry `recommendation` or `confidence`** — those live inside
the canonical report bytes and on the drafted memo.

### 1.7 The frozen commit surface R5 delegates to

```python
class DecisionCommitService:
    def __init__(self, *, repository: AuditRepository, context_provider: CommitContextProvider,
                 authorizer: Authorizer, id_generator: IdGenerator, clock: Clock) -> None
    def commit(self, recommendation_id: str, underwriter_id: str,
               action: Union[CommitAction, str], reason: Optional[str] = None) -> CommittedDecision
```
Order **inside** `commit()`: **(1)** CON-BR4 `_gate` — total, **before any assembly** · **(2)** independent authz
re-check (`RBAC_COMMIT`) → `UnauthorizedCommit` · **(3)** `context_provider.get(recommendation_id)` · **(4)** assemble +
validate the complete record **in memory, before BEGIN** · **(5)** `with repository.atomic(): repository.insert(record)`.

Exceptions: `CommitRejected(Exception)` and `UnauthorizedCommit(CommitRejected)` — **only two types, one of them a
subclass of the other** (→ **G1**, Q6).

### 1.8 The frozen WIRE-1 shapes R2–R5 must satisfy exactly

- **ApplicationSummary** (R2 item): `{application_id, recommendation_id|null, recommendation|null, confidence|null}`
- **ApplicantProfile** (R3): `intake.schema.ApplicantProfile` **verbatim** — intake's contract governs
- **MemoView** (R4): `{application_id, recommendation_id|null, status: "ready"|"pending", profile|null, report|null,
  memo|null, outlier|null}` — `outlier` is **`null` in Phase 1 even when `ready`** (WIRE1-Fold-4)
- **Commit body** (R5): `{action: "approve"|"override", reason}` — **`underwriter_id` is NOT in the body**, it comes
  from the authenticated session; `recommendation_id` from the **path**
- **CommittedDecision** (R5 success): `{recommendation_id, underwriter_id, action, reason|null}`
- **R5 auth**: **`underwriter` only** (`RBAC_COMMIT`)

---

## 2. What is *not* at risk — verified, not assumed

### 2.5 ✅ U23's frozen assertion stays green with **ZERO edits** — confirmed by reading it

`backend/deploy_config/tests/test_routes.py` has **two** relevant assertions, and **both already accommodate wired
R2–R5**:

```python
_EXPECTED = {("/session","get"), ("/decisions","get"), ("/decisions/{decision_id}","get"),
             ("/applications","get"), ("/applications/{application_id}","get"),
             ("/applications/{application_id}/memo","get"),
             ("/recommendations/{recommendation_id}/commit","post")}      # ⚑ R2–R5 ALREADY PRESENT

def test_route_table_equals_the_frozen_composition_root():                # keyed by (path, METHOD)
    assert _route_set(create_app().openapi()["paths"]) == _EXPECTED

def test_no_new_route_file_added_under_backend_app_by_u23():              # keyed by FILENAME
    assert route_files == {"__init__.py", "session.py", "decisions.py", "not_wired.py"}
```

⇒ In-place wiring changes **neither the (path, method) set nor the filename set**. **Zero edits to U23. Confirmed by
reading the file, not inferred from the earlier plan.**

⚑ **The binding constraint this creates**: because `_EXPECTED` pins **(path, method)** pairs, the wiring **may not add
any route** — including a drafting-trigger endpoint (**relevant to Q2/Q5**) — without editing a frozen unit's test.

### 2.4 ✅ The five test revisions — confirmed exactly five, with exactly three survivors

All eight test functions live in **one file**, `backend/app/tests/test_no_write_route.py`. Read on disk this session:

| # | Test function | Asserts today | Verdict |
|---|---|---|---|
| 1 | `test_the_route_table_has_exactly_one_non_get_route` | the only non-GET is `("/recommendations/{recommendation_id}/commit","POST")` | ✅ **SURVIVES UNTOUCHED** |
| 2 | `test_every_other_route_is_read_only` | every other path's methods `<= {GET, HEAD}` | ✅ **SURVIVES UNTOUCHED** |
| 3 | `test_the_seven_wire1_routes_are_the_whole_surface` | the path set is exactly the seven WIRE-1 routes | ✅ **SURVIVES UNTOUCHED** |
| 4 | `test_its_first_statement_raises_the_marker` | AST: `commit_recommendation`'s body is **exactly one** statement, a call to `_not_wired` | ⚠️ **MUST BE REVISED** |
| 5 | `test_the_marker_module_constructs_no_service_and_reads_no_body` | `not_wired.py` contains none of `DecisionCommitService` · `CommitContext` · `Depends` · `Body` · `Request` | ⚠️ **MUST BE REVISED** |
| 6 | `test_no_writer_engine_is_ever_constructed` | no production file contains `AUDIT_WRITER_URL` / `AUDIT_WRITER_PASSWORD` | ⚠️ **MUST BE REVISED** |
| 7 | `test_no_commit_service_or_context_provider_exists` | no production file contains `DecisionCommitService` · `CommitContextProvider` · `DictCommitContextProvider` · `CommitContext` | ⚠️ **MUST BE REVISED** |
| 8 | `test_no_repository_write_method_is_called` | no production file contains `.insert(` · `.atomic(` · `.commit(` | ⚠️ **MUST BE REVISED** |

Plus `TestDetectorSelfTests` (3 tests) — the comment-stripper self-tests. **These stay as they are**; they test the
detector substrate, not the guarantee.

⚑ **The substantive reframing that must not be lost**: the guarantee changes from **"no write path is reachable"** —
false by design once R5 is live — to **"every write path goes through the frozen `DecisionCommitService`"**. The
revision must **assert that positively**, not merely delete the old assertions. See **Q7** for the proposed before/after.

### 2.7 ✅ No domain logic enters `backend/app/`

Following §1.2's established pattern, every R2–R5 handler is `Depends` + one call + one pure projection. **All lifecycle
logic stays in U24.** The one place this is *at risk* is **B2/Q3** — a production `CaseSeams` is a **composition** of five
frozen units, and where that composition lives is a genuine decision, not a formality.

---

## 3. Open decisions — fill each `[Answer]:` tag

**Eleven questions. None pre-filled. Q1–Q3 are the blockers; answer them first, since Q4–Q11 partly depend on them.**

---

### Question 1 — ⛔ **B1**: R2 is a paginated list, and `CaseStore` has no way to enumerate anything. How is R2's list sourced?

`CaseStore` exposes exactly five methods (§1.6) — **none of them lists**. `PostgresCaseStore` issues `select(...).where(pk
== value)` only. R2's contract is `GET /applications?page=&size=` returning a **list wrapper of `ApplicationSummary`**.
There is no primitive to build it from.

**A) Add a `list_applications(...)` method to U24's `CaseStore` Protocol + `PostgresCaseStore` + the in-memory fake.**
The honest fix: R2 needs enumeration, U24 owns pending state, so the method belongs to U24. **But U24 is complete
(5/5 stages approved)** — this **reopens a just-closed unit**, needs its own authorization, and touches U24's
`store.py` · `repository.py` · `tests/fixtures.py` plus the structural scans that pin `EXPECTED_PRODUCTION_MODULES` and
the Protocol shape. *(Not a frozen-unit edit in the original-23 sense — U24 is Scope B's own unit — but it is
**reopening an approved unit**, which is exactly the kind of thing this discipline requires be decided, not assumed.)*

**B) The composition root issues its own `SELECT` against `pending_application`.**
Cheapest to write. **Rejected as a recommendation**: it puts **SQL and domain knowledge into `backend/app/`**, breaking
the composition root's own load-bearing invariant (*"contains no domain logic"*, *"owns no persistence"* — asserted by
`test_frozen_untouched.py`), and it would **bypass U24's only-SQL-in-`repository.py` discipline** (C-CASE-3, ADAPTER-1).

**C) R2 returns an empty list wrapper `{items: [], page: {...}}` — wired, contract-shaped, honestly empty.**
Wires R2 to the **real** pagination projection with a **real** `total` of `0`. Given **B3** (nothing populates the store),
this is **behaviourally identical to A and B today** — all three return zero items — while adding no method and no SQL.
**Cost**: R2 is structurally incapable of ever returning a row, which is a **lie of a different kind** unless disclosed
as a register item.

**D) Leave R2 as the `501` marker; wire only R3/R4/R5.**
Honest and zero-risk: R2 is *genuinely* not implementable against U24's surface. **Cost**: the primary UI journey
(`ui-queue`) stays dead, and the pass no longer delivers "R2–R5 wired".

**E) Other (describe after `[Answer]:`)**

> **Recommendation: A**, *if* reopening U24 is acceptable — it is the only option that makes R2 genuinely work and keeps
> both the composition root's and U24's invariants intact. **If reopening U24 is not authorized, D** (honest `501`) is
> preferable to **C** (a wired route that can never return data) and far preferable to **B** (SQL in the composition
> root). **This is a real fork and I will not pick it for you.**

[Answer]:

---

### Question 2 — ⛔ **B3**: Nothing can put an application into the pending store. How does a case come to exist?

`CasePipeline.submit(application_id, raw)` is built, tested, and **has no caller outside U24's tests**. WIRE-1 §3 pins
**exactly seven routes** and **contains no ingestion route**, and U23's `_EXPECTED` (§2.5) pins the **(path, method)**
set — so **adding `POST /applications` would break a frozen load-bearing test**. Without a decision here, R2/R3/R4 read a
**permanently empty** table and R5 is **permanently unreachable** (no `recommendation_id` can exist).

**A) A seed/CLI script outside the route layer** (e.g. `backend/scripts/`) that constructs the pipeline and calls
`submit()` (and, per **Q5**, `draft()`) for demo cases. **Adds no route** → U23 stays green; keeps ingestion **out of**
the API surface, which is where WIRE-1 says it isn't. **Cost**: the demo path is *"run a script, then use the API"* —
**not** a self-contained API demo. Pairs naturally with **Q9**'s migration entrypoint.

**B) Amend WIRE-1 to add an ingestion route (R8 `POST /applications`).**
The architecturally honest end-state — a real system ingests over HTTP. **But** it **amends WIRE-1's contract text**
(a stated HOLD of this pass), **and** breaks U23's frozen `_EXPECTED`, requiring a frozen-unit test edit — i.e. it
collides with **two** holds at once. Would need its own authorization.

**C) Seed via a test/dev fixture only** — the pending tables are populated by an integration-test fixture, and the demo
is exercised through tests rather than a running server. **Cost**: there is no runnable demo, only a green suite.

**D) Accept that R2/R3/R4 return empty/404 forever** in this pass, and treat "runnable demo" as **explicitly out of
scope** — wiring correctness is the deliverable, exercisability is a later pass.

**E) Other (describe after `[Answer]:`)**

> **Recommendation: A.** It is the only option that produces something actually runnable **without** amending WIRE-1 or
> editing a frozen test, and it puts the seam exactly where the contract implies it belongs (outside the pinned route
> set). **It should be chosen with eyes open**: it means the honest claim is *"the API layer is exercisable after a seed
> script"*, **not** *"the demo path is runnable end-to-end"*. See **Q11**.

[Answer]:

---

### Question 3 — ⛔ **B2**: `CasePipeline` cannot be constructed in production. Who supplies `CaseSeams` and the id factory?

`CasePipeline.__init__(store, seams, recommendation_id_factory)`. A repo-wide scan finds **`CaseSeams` implemented only
by test doubles** (`fx.drafting_success_double()` / `fx.drafting_failure_double()`) and **`recommendation_id_factory`
defined only in `case_lifecycle/tests/fixtures.py:275`**. A production `CaseSeams` must compose **five frozen units**:
`intake` (profile) → `rules_engine` (evaluate) → `outlier_model` (score) → `memo_agent_core` /
`LangGraphOrchestrator` (draft memo). **This is the single largest piece of real work in the pass**, and it is
**composition**, which is the composition root's job — but it is also **substantial**, which strains the
*"`backend/app/` contains no domain logic"* invariant.

**A) A production `CaseSeams` adapter in `dependencies.py`**, constructed from the five frozen units and injected.
Consistent with *"`dependencies.py` is the ONLY place frozen units are constructed"*. **Cost**: `dependencies.py`
roughly doubles, and the adapter — while pure composition — is the most logic-shaped thing in the package.

**B) A production `CaseSeams` adapter as a new module under `backend/case_lifecycle/`** (U24 owns the Protocol, so it
owns the production implementation), injected by `dependencies.py`. Architecturally cleanest — the Protocol and its real
implementation ship together. **Cost**: **reopens U24** (as does Q1-A; if Q1-A is taken, these pair naturally into one
reopening).

**C) A production `CaseSeams` adapter as a new module under `backend/app/`** (e.g. `backend/app/case_seams.py`).
**Permitted** — U23's filename assertion covers `backend/app/routes/` **only**, not `backend/app/` itself (verified,
§2.5). **Cost**: puts a five-unit pipeline composition in the composition root as its own module — defensible as
composition, but it is the largest non-`routes` addition the package has seen.

**D) Do not construct `CasePipeline` in the composition root at all.**
R2/R3/R4 need only **reads** (`CaseStore.get_application` + `case_to_memo_view_state`) and R5 needs only
`PendingCommitContextProvider` — **none of the four wired routes calls `submit()` or `draft()`**. So the pipeline is
needed **only by the drafting trigger** (Q5) and the seed path (Q2-A). If both live in a script, the **seams adapter can
live there too** and the composition root **never constructs `CasePipeline`**. ⚑ **This is a real and under-appreciated
finding**: the four routes genuinely do not need it.

**E) Other (describe after `[Answer]:`)**

> **Recommendation: D**, paired with **Q2-A**. It is the smallest change that satisfies the four routes, keeps
> `dependencies.py` proportionate, and puts the LLM-bearing pipeline composition **outside** the request path entirely —
> which also keeps R4 trivially side-effect-free (**BR-CASE-4 / TRIGGER-1**). Fall back to **B** if `CasePipeline` must
> be constructible in-process; **A** if reopening U24 is refused.

**Sub-question 3a — `recommendation_id_factory`.** The test factory is deterministic (derived from `application_id`).
Production needs a real one. Options: **(i)** reuse `audit-store`'s frozen `IdGenerator` seam · **(ii)** a `uuid4`-based
factory defined wherever 3's answer puts the seams · **(iii)** reopen U24 to ship a production factory beside the
Protocol. *(Recommendation: **(i)** if the seam's shape fits — it avoids inventing a second id discipline; else **(ii)**.)*

[Answer]:

---

### Question 4 — R2/R3: how do the read routes compose U24's surface into the frozen wire shapes?

**Assumes Q1 and Q2 are answered.** Both are GETs over pending state. WIRE-1 §3 marks R2 **"authenticated (any role)"**
and R3 **"authenticated"** — **neither carries a named permission**, so the natural guard is `Depends(current_identity)`
(as R1 uses), **not** `require_read_audit` (which is R6/R7's `READ_AUDIT` and would wrongly import the **Q1-B
divergence** into new routes).

**R3** is mechanically clean: `store.get_application(id)` → `None` → **404 `not_found`** (R7's precedent, static
message, no caller value echoed) → else rehydrate via the frozen `CanonSerAdapter.profile_from_canonical(
case.profile_canonical)` → serialize the frozen `ApplicantProfile` **verbatim** (`model_dump(mode="json")`, mirroring
`audit_record_wire`).

**R2** needs `ApplicationSummary = {application_id, recommendation_id|null, recommendation|null, confidence|null}`.
⚑ **`PendingApplication` carries none of the last three** — `recommendation`/`confidence` live **inside the canonical
rule-results bytes**, and `recommendation_id` lives on the **separate `PendingRecommendation`** row
(`recommendation_for_application(application_id)`). So each summary costs **a rehydration + a second store lookup**.

**4a — where does the projection live?** **(i)** New pure functions in `projections.py` (`application_summary`,
`application_list_wrapper`, `memo_view`) reusing the existing `paginate` — **consistent with the module's stated role as
the ONLY transformation layer** · **(ii)** in U24 as wire-facing projections beside `case_to_memo_view_state` (reopens
U24) · **(iii)** inline in the handlers *(rejected — breaks the established pattern)*.
*(Recommendation: **(i)**.)*

**4b — pagination.** `paginate()` already does 1-based slicing with a full `total` and an empty-not-error past-the-end
page, and `DEFAULT_PAGE_SIZE = 20` with `ge=1, le=100` bounds on R6. **Reuse verbatim for R2** so both list routes
behave identically? *(Recommendation: **yes** — reuse, do not re-derive.)* ⚑ Note this inherits **CR-Fold-4's N+1**, and
for R2 it is **worse than R6's**: materializing every application **plus** a per-row recommendation lookup **plus** a
per-row CANON-SER rehydration, all to serve one page. **Disclose as a register item rather than optimize** (optimizing
means pushing `limit/offset` into U24 — see Q1-A).

**4c — R2's ordering.** No frozen artifact pins it (exactly as **Q3-A** found for R6). Emit whatever the store returns
and **assert that honestly**, as `test_pagination.py::TestOrderingIsBrowsesDecisionIdOrder` does? *(Recommendation:
**yes** — same honesty discipline, no invented guarantee.)*

**4d — does R2 include committed/failed cases?** `case_to_memo_view_state` maps `failed → "pending"`, but
`ApplicationSummary` has **no status field at all**, so a `failed` case is **indistinguishable from a fresh one** in the
queue. Options: **(i)** include all rows · **(ii)** filter to non-terminal states *(needs a filter primitive — Q1-A)* ·
**(iii)** include all and disclose. *(Recommendation: **(iii)** — filtering silently is a domain decision the composition
root must not make; and see **register #14**, whose blast radius this widens.)*

[Answer]:

---

### Question 5 — R4: the memo view, and where the drafting trigger lives

**R4 must stay a pure, side-effect-free GET** (**BR-CASE-4 / TRIGGER-1**, and `CasePipeline.read()` is documented
*"Invokes NO pipeline step and mutates NOTHING"*). Composition: `store.get_application(id)` → `None` → **404** → else
`case_to_memo_view_state(case)` gives the `status` discriminator, and:

| MemoView field | Source when `ready` | When `pending` |
|---|---|---|
| `application_id` | `case.application_id` | same |
| `status` | `case_to_memo_view_state(case)` — the pure frozen projection | same |
| `recommendation_id` | `recommendation_for_application(id).recommendation_id` | `null` |
| `profile` | `CanonSerAdapter.profile_from_canonical(case.profile_canonical)` | ⚠️ **see 5a** |
| `report` | `report_from_canonical(case.rule_results_canonical)` | `null` |
| `memo` | rehydrated from `PendingRecommendation.memo_canonical` | `null` |
| `outlier` | ⚑ **`null` — Phase 1, per WIRE1-Fold-4, even when `ready`** | `null` |

**5a — `profile` on a `pending` view.** WIRE-1 says *"`profile` **may** still be present once intake has parsed it"*.
U24 reaches `evaluated` **eagerly in one transaction**, so `profile_canonical` is **always** populated for any row that
exists. Emit the profile even when `pending` (contract-permitted, more useful) or `null` it for a simpler
discriminator? *(Recommendation: **emit it** — it is always available and the contract explicitly allows it.)*

**5b — `outlier` stays `null`.** WIRE1-Fold-4 binds `outlier: null` in Phase 1 **even for a `ready` view**. ⚑ But U24's
`DraftOutcome` **does** carry an `outlier`, and `PendingRecommendation.outlier_canonical` **does** persist it — so the
data **exists** and the contract says **don't send it**. Confirm we honor the contract and emit `null`?
*(Recommendation: **yes, honor WIRE-1** — sending it would be an un-authorized contract change. Disclose the
now-visible mismatch as a register item, since "the data exists but the contract forbids it" is exactly the kind of
thing that should be reconciled deliberately later, not quietly now.)*

**5c — ⚑ where the drafting trigger lives.** This is the question the brief flagged, and the ground-truth pass
**sharpens** it: **no HTTP route may be added** (U23's `_EXPECTED` pins the (path, method) set — §2.5), so a
`POST /applications/{id}/draft` endpoint is **not available** without a frozen-test edit. Options:
- **(i)** The trigger lives in the **same out-of-band script as Q2-A's seeding** — seed → submit → draft, then the API
  serves a `ready` R4. **No route added; U23 green.**
- **(ii)** Draft **synchronously on the R4 GET** — **rejected**: violates BR-CASE-4/TRIGGER-1, makes a GET perform a
  non-idempotent LLM call with a write side effect, and races two concurrent reads. Q4-A already rejected this.
- **(iii)** Add a drafting route — **needs a WIRE-1 amendment + a frozen-test edit** (two holds).
- **(iv)** No trigger at all — R4 reports `pending` forever; the `ready` branch ships **untested against real data**.

*(Recommendation: **(i)**, paired with Q2-A and Q3-D. It is the only option that makes `evaluated → drafted` actually
advance without touching a hold. **⚑ If (iv) is chosen, say so plainly in the completion report**: R4's entire `ready`
branch — the primary memo-view journey — would be **unexercised**.)*

[Answer]:

---

### Question 6 — R5: commit wiring, the writer engine, and the error envelope

Per **Q5-A** (already answered): the route is a **thin adapter** — resolve identity → call
`DecisionCommitService.commit(recommendation_id, underwriter_id, action, reason)` → map exceptions to the §4 envelope.
**The frozen service stays the sole enforcer**; the route re-implements **nothing**.

**6a — the RBAC_COMMIT layer guard.** Keep `Depends`-level `RBAC_COMMIT` as **defence in depth** while the frozen
service remains the real gate (mirroring how R6/R7 guard at the layer *and* rely on the service)? *(Recommendation:
**yes** — this is the established pattern; the layer guard fails fast, the service guard is authoritative. Note it must
be a **new** dependency, e.g. `require_commit`, **not** `require_read_audit`.)*

**6b — the writer engine.** `AUDIT_WRITER_URL` must be constructed **exactly once and only here**. Follow the existing
`@lru_cache(maxsize=1)` **lazy** pattern (`writer_engine()`), so it is constructed **only when R5 is first exercised**,
never at boot, preserving *Settings-read-at-request-time*? *(Recommendation: **yes** — lazy, cached, matching
`app_engine`/`reader_engine` exactly. This makes it the **third** engine; see Q8.)*

**6c — ⛔ G1: the `CommitRejected` → status mapping is genuinely ambiguous.** WIRE-1 §4 assigns:

| Cause | WIRE-1 status | Frozen exception raised |
|---|---|---|
| override with blank/missing reason | **409** `commit_conflict` | `CommitRejected` |
| already-committed recommendation | **409** `commit_conflict` | ⚠️ **none — never detected (G2, 6d)** |
| action outside `{approve, override}` | **422** `unprocessable` | `CommitRejected` — **the same type** |
| missing `underwriter_id` | *(unassigned)* | `CommitRejected` — **the same type** |
| non-underwriter caller | **403** `forbidden` | `UnauthorizedCommit` ✅ distinguishable |
| unknown `recommendation_id` | **404** `not_found` | `UnknownPendingRecommendation` ✅ distinguishable |

`UnauthorizedCommit` and `UnknownPendingRecommendation` map cleanly. **The 409-vs-422 split does not** — one flat type
carries both. Options:
- **(i)** **Validate `action` at the Pydantic body model** (`Literal["approve","override"]`), so a bad action is
  rejected **before** `commit()` is called → the route maps it to **422** itself, and **every** `CommitRejected` that
  reaches the handler is therefore a **gate rejection → 409**. ⚑ **This is validation of the wire shape, not a
  re-implementation of the gate** — the gate still runs inside `commit()` and still rejects independently; the route
  merely refuses a body the contract says is malformed. **Distinct from the rejected Q5-B.**
- **(ii)** String-match the exception message *(rejected — fragile, couples the route to frozen prose)*.
- **(iii)** Map **all** `CommitRejected` → 409 and accept that a bad action returns 409 instead of 422 *(a knowing,
  disclosed contract deviation)*.
- **(iv)** Reopen `audit-store` to split the exception type *(a frozen-unit edit — forbidden by this pass's holds)*.

*(Recommendation: **(i)**. It satisfies WIRE-1 §4 exactly, adds no domain logic, and keeps the frozen gate sovereign.
**Please confirm explicitly**, since it is the one place the route touches commit-adjacent validation.)*

**6d — ⛔ G2: nothing ever marks a recommendation committed.** `LEGAL_TRANSITIONS` contains
`(DRAFTED, COMMITTED)` and `COMMITTED ∈ TERMINAL_STATES`, but **no code performs that transition** — `CasePipeline`
transitions only to `FAILED`. Consequences: **(a)** WIRE-1 §4's *"already-committed recommendation → 409"* has **no
enforcement**; **(b)** the same `recommendation_id` can be committed **repeatedly**, each time writing a **duplicate
`AuditRecord`** through the frozen service; **(c)** a committed case still shows `status: "ready"` on R4 forever.
Options:
- **(i)** Reopen U24 to add the `drafted → committed` transition and have R5 invoke it after a successful commit
  *(pairs with Q1-A/Q3-B if U24 is reopened anyway)*. ⚠️ Note this straddles a **commit-boundary** concern
  (COMMITBOUND-1) and needs care: the transition is **not** inside the frozen service's transaction.
- **(ii)** Disclose as a **new register item** and accept idempotency-free double-commit in this pass.
- **(iii)** Have R5 check `recommendation_for_application`/state before delegating *(rejected — a pre-check that
  duplicates enforcement, the explicitly-rejected Q5-B shape)*.

*(Recommendation: **(ii)** for this pass unless U24 is being reopened for Q1/Q3 anyway, in which case **(i)** — but
(i) needs its own commit-boundary review and should not be folded in casually. **Double-commit is a real BFSI-relevant
defect and must be disclosed either way.**)*

[Answer]:

---

### Question 7 — The exact revision of the five tests in `test_no_write_route.py`

Three survive untouched (§2.4). The five revisions, proposed **before/after** — the substantive guarantee moves from
**"no write path is reachable"** to **"every write path goes through the frozen `DecisionCommitService`"**:

| # | Test | Before | Proposed after |
|---|---|---|---|
| 4 | `test_its_first_statement_raises_the_marker` | AST: R5's handler body is exactly one `_not_wired` call | **Reframe → `test_the_r5_handler_delegates_to_the_frozen_commit_service`**: AST-assert the handler calls **`.commit(`** on an **injected** dependency and contains **no** `insert`/`atomic`/gate/authz re-implementation. |
| 5 | `test_the_marker_module_constructs_no_service_and_reads_no_body` | `not_wired.py` contains none of `DecisionCommitService`/`CommitContext`/`Depends`/`Body`/`Request` | **Reframe → `test_the_route_module_constructs_nothing_and_only_injects`**: the module contains **no direct construction** of services/engines (every dependency arrives via `Depends`), and — per §2.7 — **no SQL and no lifecycle logic**. |
| 6 | `test_no_writer_engine_is_ever_constructed` | `AUDIT_WRITER_URL` appears in no production file | **Narrow → `test_the_writer_engine_is_constructed_exactly_once_and_only_in_dependencies`**: `AUDIT_WRITER_URL` appears in **exactly one** production file (`dependencies.py`), in **exactly one** function, which is `lru_cache`d — i.e. **one writer, one place**. |
| 7 | `test_no_commit_service_or_context_provider_exists` | neither name appears anywhere | **Invert → `test_the_only_commit_path_is_the_frozen_service_with_the_real_provider`**: `DecisionCommitService` is **imported from `backend.audit_store`, never re-declared** under `backend/app/`; the provider is U24's **`PendingCommitContextProvider`**; and ⚑ **`DictCommitContextProvider` (the test fake) appears nowhere in production** — that prohibition **must survive verbatim**. |
| 8 | `test_no_repository_write_method_is_called` | `.insert(` / `.atomic(` / `.commit(` appear nowhere | **Narrow → `test_no_route_writes_except_through_commit`**: `.insert(` and `.atomic(` still appear **nowhere** under `backend/app/` (the composition root **never** writes directly); `.commit(` appears **only** in the R5 handler, **only** on the injected frozen service. |

**7a — confirm the reframing.** Does this preserve the intent (**INV-FAITHFUL**, advisory-only, human-in-the-loop) while
telling the truth about the new capability? *(Recommendation: **yes** — each revision **narrows** rather than deletes,
and #7's fake-provider prohibition and #8's direct-write prohibition **survive verbatim**, which is what stops the
revision from being a rubber stamp.)*

**7b — the module docstrings must change too.** `main.py`'s header (*"INV-FAITHFUL: no write path is reachable"*),
`not_wired.py`'s entire header, and `dependencies.py`'s (*"No writer engine is ever constructed"*) all become **false**
once R5 is live. They must be rewritten in the same pass. ⚑ **Note the interaction**: `strip_comments_and_docstrings`
means the scans **ignore prose** — so a stale docstring would **not** fail any test. It would simply be a **lie the
suite cannot catch**. Confirm docstring correction is in scope? *(Recommendation: **yes** — explicitly, precisely
because no test enforces it.)*

**7c** — Confirm **no frozen test tree is touched**: all five revisions live in `backend/app/tests/`, inside the
reopened territory. U23's tests, U24's tests, and all 22 other units' tests are **untouched**. *(Verified §2.5/§2.4.)*

[Answer]:

---

### Question 8 — `dependencies.py`: engine topology and the case-store injection point

Today: **two** lazy `lru_cache`d engines. R2–R5 add **pending-table reads** (R2/R3/R4) and **an audit write** (R5).

**8a — how many engines, and which does the case store use?** The pending tables (`pending_application`,
`pending_recommendation`) are created by **U24's own migration sequence** and are **not** covered by
`0002_grants.sql` — so **no audit role has any grant on them**, and the audit reader **cannot** read them. That leaves
the **owner** engine (`DATABASE_URL`), exactly as R1 uses for `app_user`. Proposed end-state:

| Engine | URL | Used by |
|---|---|---|
| `app_engine()` | `DATABASE_URL` (owner) | R1 (`app_user`) **+ NEW: the `CaseStore` for R2/R3/R4/R5's context reads** |
| `reader_engine()` | `AUDIT_READER_URL` (SELECT-only) | R6/R7 |
| **`writer_engine()`** ⚑ **NEW** | `AUDIT_WRITER_URL` | **R5 only** — the frozen `DecisionCommitService`'s repository |

⇒ **A third engine (the writer), and the case store reuses the existing owner engine.** Confirm? *(Recommendation:
**yes** — it is the least-privilege-consistent choice available and invents no new grant. ⚑ **Flag**: the pending tables
having **no explicit grants** means they are owner-only by default; whether that is deliberate least-privilege or an
**unreviewed gap in U24's migration** is worth stating — it is **not** something this pass should silently decide.)*

**8b — lazy or at boot?** Keep **all three lazy + `lru_cache`d**, so `create_app()` still constructs no engine and reads
no setting, and the writer is built **only when R5 is first exercised**? *(Recommendation: **yes** — preserves the
fail-closed Settings-at-request-time discipline verbatim and keeps `test_engine_binding.py`'s "no live DB" property.)*

**8c — the new providers.** Proposed additions, each following the existing one-function-per-frozen-object pattern:
`get_case_store()` → `PostgresCaseStore(app_engine())` · `get_commit_context_provider()` →
`PendingCommitContextProvider(get_case_store())` · `get_commit_service()` → the frozen `DecisionCommitService(...)`
wired with the **writer** repository, the provider, the frozen authorizer, and **an `IdGenerator` + `Clock`** ⚑ —
**which are frozen seams whose production implementations must be identified** (they may be in the same
test-fake-only state as `CaseSeams`; **this must be checked before code is written**, and if they are fakes-only it is a
**fourth blocker**). *(Recommendation: confirm the shape, and **treat the `IdGenerator`/`Clock` check as a gating item**
for the code pass.)*

[Answer]:

---

### Question 9 — `apply_case_migrations`: how do the pending tables come to exist at runtime?

**Directly on the critical path.** `apply_case_migrations(engine)` exists and is the **only sanctioned entry point**
(guard-first). But **register #8 `DEPLOY-MIGRATE-DEFERRED` is still open**: `render.yaml`'s `preDeployCommand`
references a migration runner with **no CLI entrypoint** (`backend/database/migrate.py` is **absent**), and **U24
deliberately authored none** (asserted by MIGSCOPE-1). So today **nothing invokes either sequence** — U15's or U24's.
⚑ Without an answer here, the wired routes hit **tables that do not exist**, failing at runtime with a DB error, not a
contract error.

**A) A CLI entrypoint that runs BOTH sequences** (U15's then U24's) — discharging register #8. Fits `render.yaml`'s
existing `preDeployCommand` and Q2-A's seed script. **Cost**: it is the composition's deliverable, so it belongs to this
pass — but #8 was scoped to *"`database`/composition"*, and discharging it here **widens this pass beyond wiring**.

**B) A migration call inside the Q2-A seed script only** — the demo path works; **#8 stays open** for real deploys.
Smaller, honest, leaves the register item exactly as it is.

**C) FastAPI startup hook** — call `apply_case_migrations()` on app startup. **Rejected as a recommendation**: it makes
**boot** require a live DB (breaking the *"importing/creating the app needs no environment"* property that
`test_engine_binding.py` asserts), and running migrations from a web process is poor practice under multi-worker deploys.

**D) Leave it entirely** — document that tables must be created manually before the demo. *(Honest but hostile.)*

**E) Other (describe after `[Answer]:`)**

> **Recommendation: B for this pass, with A named as the follow-on.** B keeps the pass scoped to wiring while making the
> demo actually work; A is the right end-state but is **register #8's own discharge** and deserves its own decision
> rather than being absorbed here. ⚑ **Either way, state it now** — this was explicitly flagged as something not to
> discover at the local-run checklist.

[Answer]:

---

### Question 10 — The frontend boundary

**Scope B's Q7-A** already decided: **backend-only**; the four author-only fetch seams get bound in a **separate
follow-on**. Ground truth confirms the frontend is **not browser-runnable** (no bundler; `deploy-config` owns that) and
`frontend/src/app/` is **author-only** (Decision 5).

**A) Confirm backend-only — no frontend file is touched in this pass.** *(Recommendation.)*
**B) Extend to binding the four fetch seams** — expands the pass beyond its authorization and beyond Q7-A.
**C) Other (describe after `[Answer]:`)**

[Answer]:

---

### Question 11 — How is the "demo path runnable" claim to be scoped, honestly?

Given **B1/B2/B3**, the completion claim must be **precise**. Depending on Q1/Q2/Q5's answers, the truthful claim is one
of:

**A) "The API layer is exercisable after running a seed script"** — the honest end-state if **Q2-A + Q5-A(i)** are
chosen: seed → submit → draft via script, then R2–R7 serve real data over HTTP. **Not** a clickable browser UI
(Q10-A), and **not** self-contained API ingestion (no R8).
**B) "R2–R5 are wired and contract-correct, but unexercised against real data"** — the honest end-state if **Q2-D** is
chosen: the code is right, the routes return empty/404, R4's `ready` branch and R5 are **never executed**.
**C) "The demo path is runnable end-to-end"** — ⚑ **only true if an ingestion route is added (Q2-B)**, which requires
amending WIRE-1 **and** editing a frozen test — **two of this pass's stated holds**. **Not available under the current
authorization.**

> **Recommendation: A**, contingent on Q2-A/Q3-D/Q5-A(i). **⚑ The brief's phrasing — "the demo path runnable" — maps to
> C, which this pass cannot deliver without breaking its own holds.** Flagged here rather than quietly downgraded at the
> completion report.

[Answer]:

---

## 4. Anticipated register items from this pass (to be confirmed at the code gate, not created now)

| Proposed | What it would record |
|---|---|
| **R2 N+1 amplified** | R2's per-row recommendation lookup + CANON-SER rehydration is **worse than R6's** CR-Fold-4 N+1. |
| **`COMMITTED`-transition-never-performed** (**G2**) | `drafted → committed` is legal but **never executed**; double-commit writes duplicate `AuditRecord`s; WIRE-1's "already-committed → 409" is unenforced. |
| **`outlier` data exists but the contract forbids sending it** | `PendingRecommendation.outlier_canonical` persists it; WIRE1-Fold-4 binds `null` in Phase 1. |
| **Pending tables have no explicit grants** | Owner-only by default — deliberate least privilege, or an unreviewed gap in U24's migration? |
| **#14 `MEMOVIEW-FAILED-STATE-UNMODELLED` blast radius widens** | Once R4 is live, `failed` cases really do render as `pending` to a real client. |
| **#13 `NOTWIRED-FILENAME-STALE` realized** | `not_wired.py` will hold four **wired** routes on the primary user journey. |

---

## 5. HOLDS for this pass (upheld — verified, not asserted)

- **NO code · NO wiring · NO route file edited** until the eleven `[Answer]:` tags are filled and the **mandatory
  ambiguity-check** has run, **surfacing-and-stopping** on any genuine gap.
- `not_wired.py` **keeps its filename** (Q9-A; register #13 stands).
- **No new file under `backend/app/routes/`** — U23's frozen exact-set assertion stays green with **zero edits** (§2.5).
  *(Note: `backend/app/` itself is not covered by that assertion — relevant to Q3-C.)*
- **No frozen unit's internals touched** — U24 and all 23 original units consumed **only** through public interfaces and
  existing seams. ⚑ **Q1-A / Q3-B / Q6-d(i) would each REOPEN U24** — that is a decision for the user, flagged as such,
  **not taken here**.
- **WIRE-1's contract text NOT amended** — ⚑ **Q2-B would amend it**; flagged as unavailable under current holds.
- **Q1-B (register #1) NOT resolved** — it remains recorded, not touched. New routes must **not** import
  `require_read_audit` and so must not propagate the divergence (Q4).
- The frozen **`DecisionCommitService` is composed with, never bypassed or re-implemented** in the route layer.
- **tier-B NOT authorized.** The **`audit_store` Docker-guard gap untouched** — **5 pre-existing errors must stay
  exactly 5**.
- **Frontend untouched** (Q10-A).

---

## 6. Next step — **STOP**

Fill the **eleven `[Answer]:` tags** in §3, starting with the three blockers **Q1 · Q2 · Q3**. On your signal I will read
the answers, run the **mandatory ambiguity-check**, and **surface-and-stop** on any genuine gap before any wiring code is
written.

**Nothing has been generated. The composition root is reopened and logged; the plan gate is not passed.**

---

# PART 2 — Answers as given (Q1–Q11), and the MANDATORY AMBIGUITY-CHECK

**Answered**: 2026-07-20 · **Answer set**: Q1-A · Q2-A · Q3-D(+3a) · Q4(i/yes/yes/iii) · Q5(yes/yes/i) ·
Q6(yes/yes/i/ii) · Q7(yes/yes/confirmed) · Q8(yes/yes/confirmed+gating) · Q9-B · Q10-A · Q11-A

## 7. Answers as given — verbatim decisions

| Q | Answer | The decision |
|---|---|---|
| **Q1** | **A** | **Reopen U24** to add `list_application_ids()` (or equivalent enumeration primitive) to the `CaseStore` Protocol, `PostgresCaseStore`, and the in-memory fake. Treated as a **small, explicitly scoped reopening of Scope B's own unit** — not one of the original frozen 23 — **authorized and logged separately** from U24's original build authorization, on the same discipline every prior reopening used. Chosen because it is the only option that makes R2 genuinely functional rather than putting SQL in the composition root (B), shipping a route that can structurally never return data (C), or leaving the queue journey dead (D). |
| **Q2** | **A** | An **out-of-band seed script** (`backend/scripts/`) outside the route layer, constructing the pipeline and calling `submit()`. **Adds no route** so U23's frozen (path, method) set is untouched, zero edits. The honest consequence in Q11 is accepted: *"run a script, then use the API"*, not a self-contained HTTP journey. |
| **Q3** | **D** | **Do not construct `CasePipeline` in the composition root at all.** Confirmed by the ground-truth finding that **none** of R2/R3/R4/R5 calls `submit()` or `draft()` — they need only `CaseStore.get_application`, `case_to_memo_view_state`, and `PendingCommitContextProvider`. Pipeline + production `CaseSeams` live **entirely in the seed script**, keeping `backend/app/` free of any five-unit composition and making R4 side-effect-free **by construction rather than by discipline**. |
| **Q3a** | **(i) then (ii)** | Reuse `audit-store`'s frozen `IdGenerator` **if its shape fits**; else a `uuid4` factory **in the seed script only**. Check at the start of the code pass. |
| **Q4** | **(i) · yes · yes · (iii)** | New pure functions in `projections.py` (`application_summary`, `application_list_wrapper`, `memo_view`) reusing `paginate` **verbatim**; emit **store order honestly** and assert it as such, inventing no guarantee; **include all rows regardless of state** and disclose the failed-indistinguishable-from-fresh gap as a register item — filtering silently would be an undisclosed domain decision made inside the composition root. |
| **Q5** | **yes · yes · (i)** | Emit `profile` even when `status: pending` (always populated given U24's eager transaction; contract explicitly permits it). **Honor WIRE-1 and emit `outlier: null`** despite `outlier_canonical` holding real data — sending it would be an unauthorized contract change; disclose the mismatch as a register item. The **drafting trigger lives in the same out-of-band script** as Q2-A's seeding (seed then submit then draft) so **no route is added**. |
| **Q6** | **yes · yes · (i) · (ii)** | Keep `RBAC_COMMIT` as **defence-in-depth** via a **new `require_commit`** dependency distinct from `require_read_audit`, the frozen service staying authoritative. **Lazy `@lru_cache(maxsize=1)` `writer_engine()`**, built only when R5 is first exercised. Validate `action` at the Pydantic body model as `Literal["approve","override"]` so a malformed action is a **422 before `commit()` is called**, making every subsequent `CommitRejected` unambiguously a gate rejection mapped to **409**. **Disclose G2** (never-performed `drafted`→`committed`, double-commit/duplicate-`AuditRecord` risk) as a register item and **do NOT fold a fix into this pass** even though U24 is already reopened for Q1-A — it touches COMMITBOUND-1 and deserves its own dedicated review. |
| **Q7** | **yes · yes · confirmed** | The five revisions **narrow rather than delete**; the fake-provider prohibition (#7) and direct-write prohibition (#8) **survive verbatim** inside their revised forms. **Docstring correction is explicitly in scope** for `main.py`, `not_wired.py`, `dependencies.py` — precisely because the comment-stripping scans cannot catch a stale docstring, which would otherwise be an undetectable lie. All five revisions live in `backend/app/tests/`; U23's, U24's and all 22 other units' tests stay untouched. |
| **Q8** | **yes · yes · confirmed + gating** | **Third engine** (`writer_engine()`, `AUDIT_WRITER_URL`, R5 only) plus the case store reusing `app_engine()`. **Flag, do not resolve**, whether the pending tables' absent grants are deliberate least privilege or an unreviewed gap — state it as an open observation. All three engines **lazy + `lru_cache`d**; `create_app()` still constructs nothing. **The `IdGenerator`/`Clock` production check is a hard gating item at the very start of the code pass** — if either is fakes-only, **stop and report a fourth blocker** before any wiring code. |
| **Q9** | **B** | Invoke `apply_case_migrations()` (and U15's, if unapplied) **from inside the seed script only**. **Register #8 stays open and unchanged**; a real CLI entrypoint discharging it for both sequences is a **named follow-on**, not absorbed here. |
| **Q10** | **A** | **Backend-only confirmed** — no frontend file touched, consistent with Scope B's Q7-A. |
| **Q11** | **A** | The honest claim is **"the API layer is exercisable after running a seed script."** Explicitly **NOT** *"the demo path is runnable end-to-end"* — option C would require an ingestion route needing **both** a WIRE-1 amendment **and** a frozen-test edit, neither permitted. **State precisely; do not let it drift toward the stronger claim.** |

## 8. Anticipated register items — CONFIRMED as expected (not newly created yet)

Carried forward from §4, confirmed by the answer set. **To be created at the code gate, not now.**

| Proposed item | Confirmed by |
|---|---|
| **R2 N+1 amplified** | Q4b (reuse `paginate` verbatim) + Q1-A's id-based enumeration, giving per-row `get_application` + per-row CANON-SER rehydration + per-row recommendation lookup. |
| **G2 `COMMITTED`-transition-never-performed** | Q6d(ii) — disclosed, explicitly **not fixed** in this pass. |
| **`outlier` data-exists-but-contract-forbids-it** | Q5b — WIRE-1 honored, mismatch disclosed. |
| **Pending tables have no explicit grants** | Q8a — flagged as an open observation, deliberately undecided. |
| **#14 blast radius widens** | Q4d(iii) — `failed` cases render indistinguishably in a live R2/R4. |
| **#13 realized** | `not_wired.py` will hold four **wired** routes on the primary journey. |

---

## 9. MANDATORY AMBIGUITY-CHECK — **NOT CLEAN: 1 clean · 1 GENUINE BLOCKER · 1 GENUINE FOLD → SURFACE-AND-STOP**

**Ran**: 2026-07-20, against the full Q1–Q11 answer set plus everything re-established in §1–§2.
**Result: STOP. Part 2 code generation NOT started.**

### CHECK (i) — Q1-A's list method vs COMMITBOUND-1 / ADAPTER-1 — **CLEAN**, with one correction

Read on disk: `case_lifecycle/tests/structural.py`, `test_adapter.py`, `test_commitbound.py`.

- **ADAPTER-1's positive assertion is NOT weakened.** `test_the_shim_contains_no_canonicalization_call_at_all` forbids
  `repository.py` from calling `canon_ser` · `canon_deserialize` · `canonical_bytes` · `content_hash` · `model_dump`,
  and from importing `CanonSerAdapter`. An enumeration method **returns ids (or rows) and performs no
  canonicalization** — exactly like the existing `get_application`, which already constructs a `PendingApplication`
  from row bytes (`bytes(row[...])`) **and passes today**. The shim boundary is **not reopened** and the assertion is
  **not weakened**.
- **ADAPTER-1's scan scope is unchanged.** `production_py_files()` globs `*.py` excluding `tests/` — a **new method in
  an existing module** changes nothing about what is scanned.
- **COMMITBOUND-1 is unaffected.** `FORBIDDEN_COMMIT_TOKENS = ("audit_record", "authorize", "RBAC_COMMIT")`; an
  enumeration method uses none of them.
- **CORRECTION to the answer as given**: Q1-A anticipated *"EXPECTED_PRODUCTION_MODULES updates"*. **None are
  required.** That set names the **seven production modules** (`states` · `schemas` · `store` · `repository` ·
  `pipeline` · `provider` · `migrate`); Q1-A adds **methods to two existing modules** and **no new module**. Touching
  the set would be wrong. The in-memory fake (`tests/fixtures.InMemoryCaseStore`) **does** need the method, and
  **PERSIST-1** is what keeps the two implementations honest.

### CHECK (ii) — Q3-D's seed script vs Q9-B's migration invocation — **GENUINE BLOCKER (B4)**

The required sequence is *"apply migrations, construct pipeline with production `CaseSeams`, submit, draft."*
**Step 2 cannot be completed under this pass's holds.** Tracing `draft_memo` to its root:

```
CaseSeams.draft_memo -> LangGraphOrchestrator.run(MemoAgentInput)
  LangGraphOrchestrator(provider: ProviderAbstraction, *, rulebook, model_version, telemetry=None)
    GeminiAdapter(client: LLMClient, *, model="gemini-2.5-flash")
      LLMClient.generate(*, model, prompt, temperature) -> str      <-- NO PRODUCTION IMPLEMENTATION
```

`memo_agent_core/provider.py` states it outright: *"The real google-genai client is wrapped to this at **composition**
(deploy-config/secrets)."* **Composition never built it.** This is the **exact same failure mode as the `CaseSeams`
blocker** — a seam deferred to "composition time" where composition then closed without supplying it.

**The one real adapter that exists is out of reach**: `corpus_generator/build.py::_GeminiLLMClient` wraps the real
client, but it is a **tier-B out-of-band entrypoint**, and **tier-B is NOT authorized** (a standing hold of this pass).

**Compounding finding — the declared SDK does not match the code.** `requirements.txt` declares
**`google-generativeai>=0.8.0`** (the legacy SDK). Both `build.py` and any new adapter would `from google import genai`
— the **new `google-genai` SDK**, a **different distribution**. `google-genai` is **not declared anywhere**; it appears
only in a `pyproject.toml` comment. So even reusing the tier-B adapter would need a **new dependency**, which U24
explicitly avoided (*"`requirements.txt` NOT edited; no new dependency"*).

**Therefore `draft()` cannot run in the seed script.** Without it, no `PendingRecommendation` is ever created, so **R4
never reaches `ready`** and **R5 remains unreachable** — precisely the outcome Q5-A(i) was chosen to avoid. **This needs
the user's decision; it is not improvised.** Options are stated as **Question 12**.

### CHECK (iii) — Q6-c's `Literal` validation vs WIRE-1's frozen commit body — **GENUINE FOLD (400 vs 422)**

**The contract half is clean**: WIRE-1 §5 pins `{ "action": "approve | override", ... }` and §4 assigns *"action outside
{approve, override}"* to **422**. A `Literal["approve","override"]` rejects **exactly** what the contract already
declares invalid, so it is **additive validation, not a de facto amendment**. That half of the check passes.

**But the status code it produces is wrong.** A Pydantic `Literal` mismatch raises `RequestValidationError`, and the
composition root's **global** handler maps that to **400 `invalid_request`**:

```python
async def validation_error_handler(_request, _exc) -> JSONResponse:
    status, code = INVALID_REQUEST          # 400 — NOT 422
```

So Q6-c(i) as specified yields **400**, while WIRE-1 §4 mandates **422** — and the handler is **app-global**, so it
cannot be changed for R5 without changing it for every route (regressing `test_error_envelope.py`'s *"malformed query
gives 400, not the framework's 422"*). **Q6-c's stated goal is not reachable by the stated mechanism.** Options are
stated as **Question 13**.

### RESOLVED EARLY — Q8c's gating check is **CLEAN** (no fourth blocker there)

Checked now rather than at the code pass: `audit_store/seams.py` ships **real production implementations** —
**`UuidGenerator`** (docstring: *"Production `decision_id` generator"*) and **`SystemClock`**. Neither is fakes-only,
so **`DecisionCommitService` is fully constructible.** *(The fakes-only failure mode landed on `LLMClient` instead —
check (ii).)*

**Q3a resolves as (ii)**: `IdGenerator.new_id()` takes **no argument**, but `recommendation_id_factory` is
`Callable[[str], str]` (it receives `application_id`). **The shapes do not fit**, so per Q3a's own fallback, a
**`uuid4`-based factory in the seed script**. Determined from disk, not chosen.

---

## 10. Two new questions — **fill before any code is written**

### Question 12 — **B4**: the seed script's `draft()` step has no production LLM client. How does a memo get drafted?

**A) Write a production `LLMClient` wrapper and declare the `google-genai` dependency.** The architecturally correct
fix. **Cost**: a **new dependency** (which U24 explicitly avoided), a **live `GEMINI_API_KEY`**, **real network and API
spend** per seeded case, and it arguably discharges part of the deferred composition work. Also needs the
`google-generativeai`-vs-`google-genai` mismatch resolved.

**B) Reuse `corpus_generator/build.py::_GeminiLLMClient`.** No new adapter code. **But** it lives in a **tier-B
out-of-band entrypoint** and **tier-B is NOT authorized** — this would require lifting that hold, and still needs the
undeclared `google-genai` package.

**C) A deterministic offline `LLMClient` double in the seed script**, returning canned XML. Keeps the pass offline with
no dependency, no key and no spend, and **exercises the entire wiring path end-to-end including `draft()`**. **Cost**:
the seeded memos are **not real LLM output** — the demo's memo prose is synthetic. **Must be disclosed loudly** so no
one reads a seeded memo as a genuine model artifact.

**D) Skip `draft()` in the seed script** — seed only to `evaluated`. R4 serves `pending` truthfully; **R4's `ready`
branch and all of R5 stay unexercised.** The honest minimum (this is Q5-A(iv), which Q5's answer rejected).

**E) Other (describe after `[Answer]:`)**

> **Recommendation: C.** It is the only option that exercises the full wired path — including R4 `ready` and R5 commit —
> **without** a new dependency, a live key, real spend, or lifting the tier-B hold. Given Q11-A already scopes the claim
> to *"the API layer is exercisable after a seed script"*, a **deterministic seeded memo is consistent with that claim**
> provided it is **explicitly disclosed** as synthetic, both in the script and in the completion summary. **A** is the
> right end-state but is materially larger than this wiring pass and touches the deferred-composition boundary. **This
> is your call — it has not been assumed.**

[Answer]: **C** — *(recorded retroactively 2026-07-21 from `audit.md`'s `2026-07-20T09:18:40Z` entry; see §12)*

> "Q12 [Answer]: C — a disclosed deterministic offline double in the seed script, standing in for LLMClient. [...]"
>
> — logged user input, verbatim. The `[...]` elisions are **present in the audit log itself** and are reproduced
> rather than filled in, since no fuller record of the wording exists.

**Realized in code as**: `backend/scripts/seed_demo_cases.py::_OfflineLLMClient`, stamping every seeded memo
`model_version="OFFLINE-DOUBLE-NOT-A-REAL-LLM"`. See **register #18** and §12.3.

---

### Question 13 — the 400-vs-422 fold on R5's malformed `action`

**A) Accept `action: str` in the body model; the handler does an explicit membership check** against the frozen
`CommitAction` values and raises `WireError(UNPROCESSABLE, ...)` giving **422**, before delegating. Every
`CommitRejected` reaching the handler afterwards is then unambiguously a gate rejection giving **409**. **Satisfies
WIRE-1 §4 exactly.** **Cost**: a small explicit check in the route — slightly more than pure wire-shape validation,
though it duplicates only the **closed-enum membership** test, never the gate's reason/underwriter logic. The frozen
`_gate` still runs and still rejects independently.

**B) Keep the `Literal` and accept 400** for a malformed action — a **knowing, disclosed deviation** from §4's 422.
Simplest; the deviation is real and must be registered.

**C) Add an R5-specific validation handler** so only that route's body-validation failure maps to 422. **Cost**: the
handler is currently app-global by design; per-route divergence weakens the *"every non-2xx leaves as one envelope,
built one way"* property and risks `test_error_envelope.py`.

**D) Other (describe after `[Answer]:`)**

> **Recommendation: A.** It is the only option that honors WIRE-1 §4 **and** keeps the global envelope handler intact.
> It is defensible against the Q5-B "no pre-checks" principle because the check is **closed-enum membership on the wire
> shape** — the same thing the `Literal` would have done — not a re-implementation of the CON-BR4 gate, which continues
> to run inside `commit()` and remains the sole authoritative enforcer.

[Answer]: **A** — *(recorded retroactively 2026-07-21 from `audit.md`'s `2026-07-20T09:18:40Z` entry; see §12)*

> "Q13 [Answer]: A — accept action: str on the request body model with an explicit membership check in the route,
> mapping a non-matching value to 422 directly [...]"
>
> — logged user input, verbatim. The `[...]` elision is **present in the audit log itself**.

**Realized in code as**: the membership check in `backend/app/routes/not_wired.py`'s R5 handler, verified by
`test_wire1_pending_shapes.py::TestR5Commit::test_an_action_outside_the_enum_is_422_not_400`.

---

## 11. Status — ~~STOPPED at the ambiguity-check gate~~ · ⚑ **SUPERSEDED — see §12**

> ⚑ **THIS SECTION IS HISTORICAL AND NO LONGER DESCRIBES THE TREE.** It recorded the state at the Q11
> ambiguity-check gate on 2026-07-20, **before** Q12/Q13/Q14 were answered and before any code was written. It is
> **preserved unaltered** below because it is an accurate record of *that moment* — the plan file's value is that it
> shows how the decisions were reached, and deleting a superseded status would destroy that. **For the actual
> outcome, read §12.**

**[Historical, 2026-07-20, at the Q11 gate]** — *Part 2 code generation NOT started. No U24 file touched · no
`backend/app/` file touched · no seed script written · no test revised. The U24 reopening is AUTHORIZED and LOGGED but
NOT YET ACTED UPON.*

*All holds intact: WIRE-1's text unamended · Q1-B unresolved · `not_wired.py` not renamed · U23's test not edited ·
`audit_store` Docker-guard gap untouched · tier-B not authorized · no route or file added under `backend/app/routes/` ·
frontend untouched.*

*Next: answer Q12 and Q13, then the code pass proceeds in the sequence already agreed (U24 reopening, then wiring, then
seed script, then the full-suite run).*

⇒ **Q12, Q13 and Q14 were subsequently answered and Part 2 was carried out in full. §12 records what actually
happened.**

---

# PART 3 — Q14, and the COMPLETED code pass

> ⚑ **RECONCILIATION NOTE — read this first, it governs how §12 should be trusted.**
> **Written 2026-07-21, retroactively.** This part was authored **after** the work it describes, during an explicit
> reconciliation pass. The plan file was **never updated during the code pass itself** — the session that carried out
> the work was interrupted twice (a 529 API error, then a laptop restart) before it reached its documentation step, so
> §11 was left saying *"NOT started"* while the tree in fact held a complete, green implementation.
>
> **Nothing here is reconstructed from memory.** Q12/Q13/Q14's decisions and rationale are copied **verbatim from
> `audit.md`**, which *was* written contemporaneously; the completion facts in §12.4 are copied from a **live test run
> and a live disk inspection performed on 2026-07-21**, not from any prior claim. Where the audit log itself contains
> `[...]` elisions, those are **reproduced as-is** rather than filled in.

---

## 12. Q14 — B5, and the completed pass

### 12.1 Question 14 — **B5**: R4's `ready` branch has no sanctioned way to rehydrate the memo

**Surfaced mid-implementation, 2026-07-20T09:18:40Z**, while wiring R4 — *not* anticipated by this plan. Logged
verbatim in `audit.md`:

> **⛔ B5 — GENUINE GAP, SURFACED WHILE WIRING R4: there is NO sanctioned way to rehydrate the memo.** WIRE-1 §5 binds
> `status: "ready"` to mean `memo` is PRESENT. R4 must therefore turn `PendingRecommendation.memo_canonical` back into
> a `DecisionMemo`. **The frozen `CanonSerAdapter` exposes exactly four methods** — `canonical_bytes`, `content_hash`,
> `profile_from_canonical`, `report_from_canonical` — **hardcoded to `ApplicantProfile` and `RuleResultReport`. There
> is no `memo_from_canonical` anywhere in the build.** Measured convention: every unit reaches the shared
> `backend.common.canon_ser` **through its own thin adapter** (`intake/canon_ser_adapter.py`,
> `rules_engine/canon_adapter.py`, `audit_store/canon_adapter.py`, `memo_agent_core/memo_hash_adapter.py`) — **no
> production module calls `canon_deserialize` ad hoc.** Every route forward costs something the holds forbid or that
> needs authorization: edit frozen `audit_store` (forbidden) · edit frozen `memo_agent_core` (forbidden) · reopen U24
> again beyond the authorized list-method scope (needs authorization) · call `canon_deserialize` directly in
> `backend/app/` (breaks the unit-adapter convention, and **no scan would catch it** — precisely why it deserves a
> decision) · emit `memo: null` when `ready` (violates WIRE-1 §5). **Raised as Question 14. Not improvised.**

**[Answer]: A refinement of "reopen U24"** — authorized 2026-07-20T11:03:25Z. Logged user input, verbatim:

> "Q14 [Answer]: A refinement of 'reopen U24' — but scoped precisely to match the measured convention rather than
> either editing a frozen unit or violating the per-unit-adapter pattern. Reopen U24 (a third, narrowly-scoped
> extension to the already-twice-reopened unit, logged with the same explicit rationale as the list-method reopening)
> to add a small, U24-owned rehydration function — e.g. memo_from_canonical(bytes) -> DecisionMemo — that calls
> canon_deserialize directly, living in provider.py or a new equally-thin module. This is not the same as 'call
> canon_deserialize directly in backend/app/': it follows the exact convention every other unit already uses (every
> unit reaches backend.common.canon_ser through its own thin adapter), it does not touch audit_store's frozen
> CanonSerAdapter, and it stays inside U24's own scanned tree rather than living unscanned inside the composition
> root. Why not the other three: editing audit_store's CanonSerAdapter to add a memo_from_canonical method is a
> frozen-unit edit, forbidden outright. Calling canon_deserialize directly from backend/app/ would put U24-shaped
> domain knowledge (how to rehydrate a DecisionMemo from canonical bytes) inside the composition root, breaking the
> same 'no domain logic in backend/app/' invariant this whole pass has been careful to preserve, and — as you noted —
> no scan would catch that violation, which is exactly why it's the wrong place for it even though it would 'work.'
> Emitting memo: null when status is 'ready' is a direct WIRE-1 §5 violation and isn't available. This reopening is
> authorized now. Extend U24's own ADAPTER-1-style scan (or add a parallel structural assertion) to confirm the new
> rehydration function calls canon_deserialize through the same discipline CanonSerAdapter itself uses — reuse the
> mechanism, don't reinvent a second canonicalization discipline. Log this as U24's third explicitly-authorized
> reopening, distinct from the list-method reopening, with its own rationale in audit.md and guide-state.md, before
> writing the function."

**Targeted pre-check, logged before implementation and RE-VERIFIED live on 2026-07-21**: a full `backend/`-wide grep
for `DecisionMemo` combined with canonical/deserialize terms. At authorization time it returned **zero hits**; today it
returns **exactly the two lines of `memo_adapter.py` itself** — confirming the adapter was built because nothing
existed, not in duplication of something that did.

**⚑ ADAPTER-1 was NARROWED, NOT WEAKENED** — flagged in advance rather than discovered in a diff. `canon_ser` (the
SERIALIZE direction) remains forbidden in **every** U24 production module without exception. `canon_deserialize`
becomes permitted in **exactly one named allowlisted module** and stays forbidden everywhere else, with a **positive
thinness assertion** and a **detector self-test**. *Before*: no module may call it. *After*: exactly one designated
module may, for rehydration only. **Strictly more specific, not more permissive.**

**⚑ Deliberately opposite calls on `EXPECTED_PRODUCTION_MODULES`**: reopening #1 (Q1-A) added **methods to existing
modules**, so the set correctly stayed **unchanged** at 7. Reopening #2 (Q14-A) adds a **new production module**, so
the set **does** change, 7 → 8. Opposite calls, opposite reasons.

### 12.2 The two authorized U24 reopenings

| # | Authorized by | Scope | Why it could not be avoided | On disk |
|---|---|---|---|---|
| **1** | **Q1-A** | `list_application_ids()` on the `CaseStore` Protocol, `PostgresCaseStore`, and the in-memory fake | R2 is a **paginated list** and the Protocol had **no enumeration primitive at all** — R2 was not implementable | `store.py` · `repository.py` · `tests/fixtures.py` · `tests/test_enumerate.py` |
| **2** | **Q14-A** | a U24-owned `memo_from_canonical(bytes) -> DecisionMemo` thin adapter | WIRE-1 §5 binds `status: "ready"` to a **present** `memo`, and **no memo rehydration existed anywhere in the build** | `memo_adapter.py` · `tests/test_memo_adapter.py` · `tests/test_adapter.py` |

Both were logged **before** the corresponding code was written, each with its own distinct rationale, separate from
U24's original build authorization.

### 12.3 What was built

| Area | Outcome |
|---|---|
| **U24 reopening #1** | `list_application_ids()` — PK column only, `ORDER BY application_id`, rehydrating nothing. New tier-U target **ENUMERATE-1** (8 tests) incl. a **structural** re-assertion that the shim performs no canonicalization. **PERSIST-1 extended** with a tier-I agreement test. |
| **U24 reopening #2** | `memo_adapter.py::MemoCanonAdapter.memo_from_canonical`. Rehydration only — **no serialize direction, deliberately**, so the frozen adapter keeps sole ownership of canonicalization. |
| **Composition root** | `dependencies.py` (third lazy `writer_engine()` + U24 injection points + `require_commit`) · `projections.py` (`application_summary` / `application_list_wrapper` / `memo_view`, reusing `paginate` verbatim) · `routes/not_wired.py` (R2–R5 wired **in place**). |
| **Docstrings (Q7b)** | `main.py`, `not_wired.py`, `dependencies.py` all corrected — the *"no write path is reachable"* claim is now stated as **false by design**, replaced by *"every write path goes through the frozen `DecisionCommitService`."* Done precisely because **no scan can catch a stale docstring**. |
| **The five test revisions (Q7)** | All five applied per the before/after table. Each **narrows rather than deletes**; #7's fake-provider prohibition and #8's direct-write prohibition **survive verbatim**. |
| **`test_not_wired.py`** | Rewritten as `TestTheMarkerIsGone` — the new guarantee is stated **positively and explicitly**, not silently patched. |
| **R2–R5 route tests** | `test_wire1_pending_shapes.py` — ~40 tests over all four routes, incl. the 422-not-400 case and a layer-guard-bypass test proving the **frozen service**, not the API guard, is the real gate. |
| **Seed script (Q2-A/Q3-D/Q9-B)** | `backend/scripts/seed_demo_cases.py` — migrations → pipeline (production `CaseSeams` composed from the frozen units) → submit → draft. Contains the **Q12-C offline LLM double**, loudly disclosed. |

**Q3-D held**: `CasePipeline` is **never constructed in `backend/app/`**. R4 is side-effect-free **by construction**,
not by discipline.

### 12.4 Verified state — live run, 2026-07-21

| Scope | Passed | Failed | Skipped | Errors |
|---|---|---|---|---|
| `backend/case_lifecycle/` | 129 | **0** | 6 | **0** |
| `backend/app/` | 165 | **0** | 0 | **0** |
| **Full `backend/`** | **1492** | **0** | **37** | **5** |

Coverage gate: **99.87%, `--cov-fail-under=90` held.** The **5 errors are exactly the 5 pre-existing `audit_store`
Docker-absence errors**, unchanged and untouched. **Pre-wiring baseline was 1418 / 36 / 5 ⇒ +74 passed, +1 skipped,
errors identical. ZERO REGRESSION.**

### 12.5 The honest scope claim — **Q11-A, unchanged and not drifted**

> **"The API layer is exercisable after running the seed script."**

Explicitly **NOT** *"the demo path is runnable end-to-end"* (that needs an ingestion route — a WIRE-1 amendment **and**
a frozen-test edit, neither permitted) and **not** a clickable browser UI (Q10-A: frontend untouched). Additionally,
per **Q12-C**, seeded memo prose is **synthetic** — a deterministic offline double, not a real model call.

### 12.6 Six new register items opened by this pass

**#15** R2's amplified N+1 · **#16** failed-indistinguishable-from-fresh · **#17** outlier-data-exists-but-contract-
forbids-it · **#18** no production `LLMClient` (B4) · **#19** `COMMITTED`-transition-never-performed (G2, double-commit
risk) · **#20** pending-tables-no-explicit-grants.

Full disclosure with code locations, owners and blocking status: **`guide-docs/build/composition-root/scope-b-wiring-summary.md`**.
The register moves **14 → 20**, folded back into `BUILD-COMPLETION-REPORT.md` (which had lagged at 12).

### 12.7 Holds — all upheld, verified on disk

WIRE-1's contract text **unamended** · Q1-B **unresolved** · `not_wired.py` **NOT renamed** (register #13 now
*realized* — the file holds four wired routes under a stale name) · U23's frozen test **NOT edited** (its `_EXPECTED`
already accommodated R2–R5; zero edits needed) · `audit_store` Docker-guard gap **untouched** (5 errors exactly 5) ·
tier-B **NOT authorized** · **nothing added under `backend/app/routes/`** · frontend **untouched**.

**Status: Scope B wiring pass COMPLETE.** This was Scope B's final authorized step.
