# Scope B — R2–R5 + the pending-application lifecycle · SCOPING PLAN (Part 1)

**Stage**: POST-BUILD → **SCOPE B, scoping/planning pass** (plan-then-answer + `[Answer]:` tags)
**Date**: 2026-07-19 · **Status**: **Q1–Q8 ANSWERED (all A) · ambiguity-check RAN → NOT CLEAN (2 folds resolved + 1 GENUINE GAP) → SURFACED AND STOPPED at Question 9.** NO U24 extension logged · NO FD begun · NO code, NO wiring, NO FD artifact.
**Authorization**: explicit, user-given, **logged in `audit.md` BEFORE this plan was written**, mirroring the discipline the
original composition-root **Scope A** pass was logged under.

> **⚑ Two things held untouchable for the entire 23-unit build are now deliberately opened:**
> **(1)** the **CLOSED composition root** (`backend/app/`) is **RE-OPENED under Scope B**;
> **(2)** the **completed 23-unit decomposition** is being **EXTENDED** with domain-state work no existing unit owns.

**Holds for this pass**: all 23 completed units consumed **BY SHAPE, editing NONE of their internals**. Any need to touch a
frozen unit is surfaced as its **own authorization question (Q3)** — never assumed. **WIRE-1's contract text NOT touched ·
tier-B NOT authorized · the `audit_store` Docker-guard gap NOT touched · no code generated.**

---

## 1. Ground truth — re-established from disk this session

Everything below was **read on disk**, not reconstructed from memory or from prior conversation summaries.

### 1.1 The frozen WIRE-1 contracts (`guide-docs/build/wire-1/api-contract.md`)

| Route | Contract | Response | Authz |
|---|---|---|---|
| **R2** | `GET /applications?page=&size=` | list wrapper of **`ApplicationSummary`** | authenticated (any role) |
| **R3** | `GET /applications/{application_id}` | **`ApplicantProfile`** | authenticated |
| **R4** | `GET /applications/{application_id}/memo` | **`MemoView`** (carries `status`) | authenticated |
| **R5** | `POST /recommendations/{recommendation_id}/commit` | **`CommittedDecision`** | **`underwriter` only** (`RBAC_COMMIT`) |
| R1 / R6 / R7 | `GET /session` · `GET /decisions` · `GET /decisions/{id}` | **LIVE today** | R1 authenticated · R6/R7 see §1.6 |

**Shapes pinned by the frozen contract** — Scope B must satisfy these exactly, not redesign them:
- **`ApplicationSummary`** = `{ application_id, recommendation_id | null, recommendation | null, confidence | null }` —
  *"`null` until a recommendation is drafted"*. **⚑ The contract already presumes a pre-commit lifecycle with a nullable
  recommendation.**
- **`MemoView`** carries a **`status` discriminator (`ready` | `pending`)** — WIRE1-Fold-2, *"so `ui-memo-view` always has a
  defined shape whether or not a memo has been drafted"*, and — **decisive for Q4** — **"the sync-vs-async model is an
  implementation detail (Build & Test)"**. The contract deliberately does **not** pin the drafting trigger.
- **`MemoView.outlier`** = `OutlierResult | null` (WIRE1-Fold-4, additive amendment), **`null` when `status: pending`**.
- **R5 is keyed by `recommendation_id`**, *"matching `DecisionCommitService.commit(recommendation_id, underwriter_id,
  action, reason)`"*, and **R4's response carries the `recommendation_id` the client then commits**.
- WIRE-1 §9 already records: *"R4 is a `501` stub … the wire-up lands whenever R4 is actually wired (Build & Test / **a
  future composition-root scope**)."* — **this pass is that scope.**

### 1.2 The composition root as it stands (`backend/app/`)

`main.py` · `dependencies.py` · `errors.py` · `projections.py` · `routes/` · `tests/` — **355 lines, composition only**.
Its docstring states each stub's reason verbatim:

```
R2  GET  /applications                 501  not wired — no pending-application store
R3  GET  /applications/{id}            501  not wired — no pre-commit profile store
R4  GET  /applications/{id}/memo       501  not wired — no store, no drafting trigger
R5  POST /recommendations/{id}/commit  501  not wired — only a TEST-FAKE context provider exists
```

**Already wired and reusable by Scope B (no redesign needed):**
- **Fail-closed `Settings` boot** — `secrets-config` read at **request** time, never at import, so importing the app needs
  no environment.
- **Two-engine least-privilege binding**, *derived from the frozen `0002_grants.sql`, not chosen*: `DATABASE_URL` (owner)
  for `app_user`; `AUDIT_READER_URL` (SELECT-only) for audit reads. **No writer engine is ever constructed in Scope A.**
- **Header-based identity resolution** — a **stub `X-User-Id`** resolved against `app_user`; fail-closes to 401. The role
  is **never trusted from the header** — only the user id is; the role comes from `app_user` via the frozen `to_role`
  canonicaliser.
- **The WIRE-1 §4 error envelope** applied app-wide via exception handlers.
- **`INV-FAITHFUL`**: *"no write path is reachable"* — asserted by `tests/test_no_write_route.py` (CR-Fold-7).
  **⚑ Scope B necessarily changes this**, since R5 is a write path. That test is a composition-root test, in the re-opened
  territory — but the change must be deliberate and logged, not incidental.

### 1.3 What Scope A said it was deferring (`composition-root/integration-summary.md` §9, verbatim)

> *"The **core underwriting path (queue → memo → commit) remains unwired**; R2–R5 stay unbacked because the
> pending-application/recommendation lifecycle is **un-designed domain state**, which belongs in its own stage
> **(Scope B/C)**, not smuggled into a wiring pass. … **The Q1-B divergence remains open.**"*

**Inherited verbatim, not re-derived**: the missing pieces are **(a)** a pending-application store, **(b)** a pre-commit
profile store, **(c)** a drafting trigger, **(d)** a real `CommitContextProvider`.

### 1.4 `database` (U15) on disk — what exists and what does not

**Migrations**: `0001_initial_schema.sql` · `0002_grants.sql` · `checksums.json`.
**Tables that EXIST**: `audit_record` (+ index on `application_id`) · `applicant_profile_snapshot` · `app_user`.
**Tables that DO NOT exist**: **no pending-application table · no pending-recommendation table.** Confirmed — the build's
claim holds.

**⚑ How migrations work — and the decisive finding for Q3.** `migration_runner.py`:
```python
MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
def migration_files(migrations_dir: Path = MIGRATIONS_DIR) -> list[Path]: ...
class MigrationRunner:
    def __init__(self, engine, migrations_dir: Path = MIGRATIONS_DIR, env=None) -> None: ...
```
and `migration_checksum.py`:
```python
def verify_checksums(migrations_dir: Path = MIGRATIONS_DIR, manifest_path: Path = MANIFEST_PATH) -> None: ...
```
**Both the runner and the checksum verifier are PARAMETERIZED on `migrations_dir`.** The forward-only sequence is
discovered by `glob("[0-9][0-9][0-9][0-9]_*.sql")` **within whichever directory is passed**, and immutability is enforced
against **whichever manifest is passed**. The frozen `migration_checksum` docstring also states the rule explicitly:
*"**editing** a published migration → **fail**; **appending** a new migration + its manifest entry → **allowed**."*
⇒ **A Scope-B-owned migration directory is runnable through the frozen machinery with ZERO edits to U15.** This makes Q3 a
genuine, well-grounded fork rather than a forced frozen-unit touch.

### 1.5 ⚑ `CommitContext` — the frozen shape that already specifies the pending store

`audit_store/record_schema.py`:
```python
class CommitContext(_Frozen):
    """The pending-recommendation context the orchestrator/pipeline supplies to
    DecisionCommitService via the injected CommitContextProvider — the assembly inputs
    the frozen 4-param commit signature does not carry."""
    rule_results: RuleResultReport
    memo_hash: str
    model_version: str
    engine_version: str
    rulebook_version: str
    applicant_profile: ApplicantProfile
```
**This is the single most useful discovery of the ground-truth pass**: the pending-recommendation store's contents are
**already specified by a frozen shape**. Whatever Scope B persists must be sufficient to reconstruct a `CommitContext`.
The seam is `CommitContextProvider` (a `Protocol` with `get(recommendation_id) -> CommitContext`); today only
`DictCommitContextProvider` (an explicit **test/fake**) implements it. **Scope B's job at R5 is to supply a REAL
implementation** — not to touch `DecisionCommitService`.

### 1.6 The frozen enforcement Scope B composes with (never re-implements)

`DecisionCommitService.commit()` executes, in order: **(1)** the **CON-BR4 gate predicate** (`GATE-1`, a total function,
**before any assembly**) · **(2)** an **independent backend authz re-check** (`AUTHZ-1`, `RBAC_COMMIT`, raising
`UnauthorizedCommit`) · **(3)** fetch context via the injected provider · **(4)** assemble + validate the complete record
in memory **before** `BEGIN` · **(5)** an atomic write wrapping **only** the write.
⇒ **The human-in-the-loop constraint is already enforced server-side, independently of the API layer.** Scope B must
**compose with this**, so the invariant is satisfied by existing frozen code (see Q5).

**Q1-B, verbatim from `dependencies.py`** (still open, still recorded in code):
> *"RECORDED DIVERGENCE (unresolved, deliberately carried): WIRE-1 §3 marks R6/R7 'authenticated' (ANY role), while
> `PERMISSION_MATRIX` excludes admin from `READ_AUDIT`. For an admin caller the two FROZEN artifacts disagree (200 vs 403).
> This is TWO-SIDED, not a one-sided oversight … Reconciliation (Option C: enforce `READ_AUDIT` *and* amend WIRE-1 §3's
> wording) is future deliberate work. WIRE-1 is NOT amended here."*

### 1.7 Frozen shapes confirmed consumable BY SHAPE

| Shape / service | Owner | Confirmed on disk |
|---|---|---|
| `ApplicantProfile` · sanitizer | `intake` (U1/U2) | `backend/intake/schema.py`, `intake/sanitizer/` |
| `RuleResultReport` · `Recommendation` · `Confidence` | `rules-engine` (U3) | `rules_engine/report_schema.py` |
| `OutlierResult` (`outlier_score`, `is_outlier`, `flagged_features`, `provenance`) — **no verdict field** | `outlier-model` (U18) | `outlier_model/schemas.py` |
| `DecisionMemo` · `MemoDraftOutput` · `MemoAgentInput` · `MemoAssembler` · `LangGraphOrchestrator.run(agent_input) -> DecisionMemo \| None` | `memo-agent-core` (U4) | `memo_agent_core/{schemas,assembler,orchestrator}.py` |
| provider adapters + `route_borderline` | `memo-extensions` (U19) | `memo_extensions/{provider_secondary,provider_showcase,borderline_router}.py` |
| `DecisionCommitService` · `CommitContextProvider` · `CommitContext` · `CommittedDecision` | `audit-store` (U12) | `audit_store/{commit_service,seams,record_schema}.py` |
| `Role` · `to_role` · `AuthRBAC` · `ApiAuthGuard` · `RBAC_COMMIT` · `READ_AUDIT` | `auth-rbac` (U11) | `auth_rbac/{roles,authorizer,api_guard}.py` |
| `MigrationRunner` · `verify_checksums` (**both parameterized**) | `database` (U15) | `database/{migration_runner,migration_checksum}.py` |

**All are consumable by shape** — every one is either an importable frozen value object or an injected seam. **Scope B
needs to edit none of them** (Q3 is the one place that could change, and it is asked, not assumed).

### 1.8 Frontend (for Q7)

Fetch seams exist and are **author-only** today: `memoView/memoFetchSeam.js` · `approvalGate/commitFetchSeam.js` ·
`overrideForm/overrideFetchSeam.js` · `outlierView/fetchSeam.js` · `history/historyFetchSeam.js` · `app/seams.js`.
`history/` is the one already backed (R6/R7). **The bundler now exists** — `deploy-config` (U23) built `index.html`,
`src/main.jsx`, `vite.config.js`, `vercel.json`. Frontend suite currently **682 passed / 137 files** (verified live).

---

## 2. Clarifying questions — fill each `[Answer]:` tag

> **I will improvise none of these.** Each is a genuine fork. **Options are lettered; a recommendation is given only where
> the ground-truth pass produced a genuinely grounded one.** No answer is pre-filled.

---

### Question 1 — The vehicle: new unit(s) through the full BUILD loop, or a Scope-A-style integration pass?

**The honest tension**: Scope A was a **pure wiring pass** and was explicitly logged as *out-of-band*. But Scope A's own §9
says R2–R5 are **"un-designed domain state … which belongs in its own stage"**. Ground truth confirms that: this pass must
invent a **lifecycle state model** (Q2) and **new persistent tables** (Q3) — that is **design work**, not wiring. A
Scope-A-style pass would therefore **under-serve it**, and would repeat exactly the smuggling §9 warned against.

**A) ONE new unit — `case-lifecycle` (U24) — through the full per-unit BUILD loop, then a THIN composition-root wiring pass
(RECOMMENDED).**
The new unit owns the lifecycle state model, the pending stores, the drafting orchestration, and the real
`CommitContextProvider`. The composition root then does what it already does well: **construct and inject**, adding four
route modules and nothing else. **Why**: it honours §9 literally (the domain state gets its own designed stage with FD →
NFR → gates); it keeps the composition root **composition-only**, preserving the property every prior unit's NOEDIT scan
depended on; and the per-unit loop's ambiguity-checks are exactly the discipline un-designed state needs. **Cost**: five
stages plus a wiring pass — the heaviest option.

**B) TWO new units — a `case-store` (persistence + lifecycle) and a `case-orchestration` (the drafting trigger + pipeline
drive) — plus a thin wiring pass.**
Separates persistence from orchestration, mirroring how `database`/`audit-store` were split. **Cost**: two full loops;
possibly over-decomposed for one lifecycle, and it introduces a seam between the two halves that may not earn its keep.

**C) A single extended composition-root pass (Scope A shape), designing the lifecycle inline.**
Fastest. **But** it puts domain logic **inside `backend/app/`**, breaking the composition-root's own stated invariant
(*"this package contains no domain logic"*) — the exact thing §9 warned against. *(Available, but I cannot recommend it on
the evidence.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 2 — The pending-application lifecycle: what are the states and transitions?

Nothing on disk defines this — it is genuinely un-designed. The frozen artifacts do constrain it: `ApplicationSummary`
implies *"`null` until a recommendation is drafted"*, `MemoView.status` is **`ready` | `pending`**, and `CommitContext`
(§1.5) enumerates exactly what must exist **before** a commit is possible.

**A) FIVE states — `submitted → profiled → evaluated → drafted → committed` (RECOMMENDED).**
Each transition is produced by **exactly one frozen unit**, so no new domain logic is invented:

| Transition | Produced by | Artifact |
|---|---|---|
| `submitted → profiled` | **`intake`** (U1/U2) | `ApplicantProfile` (sanitised) |
| `profiled → evaluated` | **`rules-engine`** (U3) | `RuleResultReport` (+ `Recommendation`, `Confidence`) |
| `evaluated → drafted` | **`outlier-model`** (U18) + **`memo-agent-core`/`memo-extensions`** (U4/U19) | `OutlierResult` + `DecisionMemo` |
| `drafted → committed` | **`audit-store`** (U12) | `CommittedDecision` — **the boundary** |

**The boundary is sharp and already frozen**: everything up to and including `drafted` is **pending (pre-commit) state
owned by Scope B**; `committed` is **`audit_record`, owned by the existing frozen audit store**, and is reached **only**
through `DecisionCommitService`. R2/R3/R4 read pending state; **R5 is the one transition that crosses the boundary**.
Mapping to the contract: `status: pending` covers `submitted`/`profiled`/`evaluated`; `status: ready` means `drafted`;
`ApplicationSummary.recommendation_id` is `null` until `evaluated`/`drafted`.

**B) THREE states — `pending → ready → committed`** (collapse the interior). Matches `MemoView.status` exactly and is the
minimum the contract requires. *(Simpler; but it cannot express "profiled but not yet evaluated", so a partial-pipeline
failure has no representable state — an observability and retry problem later.)*

**C) Event-sourced** — persist the artifacts and derive state. *(Most faithful to the replay/audit ethos; materially more
machinery, and the audit store already owns the committed-side replay story.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 3 — ⚑ New persistent state: does it touch `database` (U15)'s frozen territory?

**This is the authorization fork, and the ground-truth pass changed the answer.** New tables are certainly needed (§1.4:
no pending-application and no pending-recommendation table exist). The question is **where the migration lives** — and,
critically, whether Scope B must touch a frozen unit at all.

**⚑ Measured**: `MigrationRunner(engine, migrations_dir=...)` and `verify_checksums(migrations_dir=..., manifest_path=...)`
are **both parameterized**; the sequence is globbed from **whichever directory is passed**, and immutability is checked
against **whichever manifest is passed**.

**A) A SCOPE-B-OWNED migration directory, run through the frozen (parameterized) machinery — NO frozen edit
(RECOMMENDED).**
Scope B owns e.g. `backend/<new_unit>/migrations/0001_case_lifecycle.sql` + its own `checksums.json`, executed by the
**frozen `MigrationRunner` with `migrations_dir=` pointed at it**, and verified by the **frozen `verify_checksums`**.
**Why**: it **needs no reopening of `database` (U15) at all** — the seam is already parameterized, so this is *using* U15,
not editing it (`import-to-read ≠ edit`); it keeps forward-only + immutability guarantees by **reusing** the frozen
mechanism rather than reimplementing it; and it keeps the Scope-B blast radius to *the composition root + genuinely-new
artifacts*, exactly as the authorization scoped it. **Open sub-question it raises** (surfaced, not hidden): **two
independent sequences both writing to one database** need a convention so their `applied_migrations` tracking and grant
expectations don't collide — that is a design detail for the FD stage, not a blocker.

**B) A new `0003_*.sql` appended INSIDE `backend/database/migrations/`, with `checksums.json` updated.**
**⚑ This IS a frozen-unit edit and would need its own explicit authorization**, which this pass does **not** assume.
In its favour: the frozen checksum docstring explicitly sanctions *"appending a new migration + its manifest entry"*, and
one database arguably deserves one migration sequence. Against: it writes into a frozen unit's tree and **modifies its
committed `checksums.json`** — a file whose whole purpose is immutability — and would be **the first frozen-unit edit in
the entire build**.

**C) No new tables — hold pending state in memory / a non-persistent store.** *(Rejected on the evidence: the lifecycle
must survive a restart for a queue to be meaningful, and `CommitContext` requires durable pre-commit artifacts.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 4 — The R4 drafting trigger: how does a memo come to exist?

**The frozen contract deliberately leaves this open** — WIRE1-Fold-2 states *"the sync-vs-async model is an implementation
detail"*, and the `ready | pending` discriminator exists precisely so the client is well-defined either way. So this is a
real, unconstrained choice. In **all** options the pipeline is driven through existing seams — `intake` → `rules-engine` →
`outlier-model` → `LangGraphOrchestrator.run(MemoAgentInput) -> DecisionMemo | None` — **editing none of them**.

**A) A SEPARATE explicit trigger; R4 is a pure read (RECOMMENDED).**
R4 returns `status: pending` until a memo exists and `status: ready` once drafted; drafting is kicked off by its own
action (a separate internal call/endpoint, or on submission). **Why**: R4 stays a **GET with no side effects** — an HTTP
semantic the frozen contract's read-only framing implies; it makes the LLM call's cost/latency explicit rather than hidden
inside a queue-detail fetch; and `status: pending` already exists to express it. **Cost**: something must invoke the
trigger — a Scope-B design detail.

**B) Synchronously on the GET (draft-on-first-read).** Simplest to demo — R4 always returns `ready`. **But** it makes a GET
perform an expensive, non-idempotent LLM call with a write side effect, and two concurrent reads race to draft.

**C) A queued/background step** (worker polls `evaluated` → drafts → marks `drafted`). Most production-faithful; **but** it
introduces a worker process and queue infrastructure — new deployment topology beyond what `deploy-config` (U23) designed,
and Infrastructure Design implications.

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 5 — R5 commit: how does the route compose with the frozen `DecisionCommitService`?

**The frozen service already does the work** (§1.6): the CON-BR4 gate runs **before any assembly**, and an **independent
backend authz re-check** runs regardless of what the API layer did. **Scope B must not re-implement any of this.** What is
genuinely missing is a **real `CommitContextProvider`** — today only `DictCommitContextProvider` (an explicit test/fake)
exists.

**A) Scope B supplies a REAL `CommitContextProvider` backed by the pending store; the route is a thin adapter
(RECOMMENDED).**
The R5 route: resolves identity (existing `current_identity`), calls
`DecisionCommitService.commit(recommendation_id, underwriter_id, action, reason)`, and maps its exceptions to the WIRE-1
error envelope (`UnauthorizedCommit` → **403**, unknown `recommendation_id` → **404**, gate rejection → **400/422**).
**The human-in-the-loop invariant is satisfied by the frozen service, not by the route** — the route cannot bypass it,
because the gate and the authz re-check run **inside** `commit()`. The new provider reads the pending-recommendation store
and returns a `CommitContext` (§1.5 pins its exact fields). **The API-layer `RBAC_COMMIT` guard is kept as well** — defence
in depth, matching how R6/R7 already guard at the layer *and* rely on the service.
**⚑ Consequence to accept deliberately**: this makes a **write path reachable** for the first time, so a **writer engine
(`AUDIT_WRITER_URL`)** must be constructed, and the composition root's `INV-FAITHFUL` / `test_no_write_route.py` assertion
**must be deliberately revised** — flagged here, not done silently.

**B) The route performs its own pre-checks before delegating.** *(Rejected as the default: duplicating the gate invites
drift from the single-sourced frozen enforcement.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 6 — The Q1-B divergence (register item #1): resolve now, or continue deferring?

Scope B re-opens the very module that carries this divergence in code (§1.6). Doing nothing is a choice; so is fixing it.
Neither should happen silently.

**A) Continue deferring — Scope B does NOT resolve Q1-B (RECOMMENDED).**
Q1-B is a **two-sided disagreement between two frozen artifacts** (WIRE-1 §3 vs `PERMISSION_MATRIX`), and the recorded
reconciliation (*"Option C: enforce `READ_AUDIT` **and** amend WIRE-1 §3's wording"*) requires **amending WIRE-1** — which
this pass's holds explicitly forbid (*"Do not touch WIRE-1's frozen contract text"*). It also concerns **R6/R7**, which are
**already live and outside Scope B's R2–R5 remit**. **Why**: resolving it would exceed the authorized scope and couple an
unrelated fix to this lifecycle work. Deferral stays **recorded, not forgotten**.

**B) Resolve it now under a widened authorization** — enforce `READ_AUDIT` and amend WIRE-1 §3. *(Coherent — the root is
open and the fix is known — but it requires **separately authorizing a WIRE-1 contract-text amendment**, which today's
holds exclude.)*

**C) Resolve the code side only** (leave WIRE-1 wording untouched). *(Rejected: it would make the divergence **worse** —
the artifacts would still disagree, but now silently, with no recorded note where a reader would look.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 7 — Frontend wiring: how far does Scope B go?

**Measured**: the fetch seams already exist and are **author-only** (`memoFetchSeam.js`, `commitFetchSeam.js`,
`overrideFetchSeam.js`, `outlierView/fetchSeam.js`); `history/` is the one already backed by live routes. **The previously
deferred bundler now EXISTS** — `deploy-config` (U23) delivered `index.html`, `main.jsx`, `vite.config.js`, `vercel.json`.
**So nothing appears to remain pulled-forward on the frontend side** beyond binding seams to now-live routes.

**A) Backend-only in Scope B; frontend seam-binding is a separate follow-on (RECOMMENDED).**
Scope B makes R2–R5 live and verifies them at the API layer. The four author-only modules are bound in their own pass.
**Why**: it keeps this scope to one coherent concern (the lifecycle + its routes); the frontend units are **frozen** and
binding their seams is a distinct change with its own test surface (currently **682 passing** tests that must not
regress). **Cost**: the browser demo still isn't clickable at the end of Scope B — the API is exercisable, the UI is not
yet joined.

**B) Include frontend seam-binding in Scope B** — one pass to a clickable end-to-end demo. *(Delivers the demo in one go;
but it widens the scope to touching frozen frontend units and mixes two verification surfaces.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 8 — Confirm the frozen invariants binding Scope B (restated for a lifecycle/wiring context)

Stated for explicit confirmation rather than assumption. **No option is recommended because A is a confirmation, not a
choice** — but B exists so you can add to the list.

**A) All five bind, as restated below.**
1. **Advisory-only / human-in-the-loop** — no recommendation is finalized without explicit underwriter action. In Scope B
   this is satisfied **by the frozen `DecisionCommitService`'s CON-BR4 gate**, which runs before any assembly; the pending
   store holds **recommendations**, never decisions. A `CommittedDecision` exists **only** as R5's result.
2. **No LLM in the deterministic rules path** — the lifecycle drives `rules-engine` (pure Python) and the memo agent as
   **separate, ordered** transitions; no LLM output ever re-enters rule evaluation.
3. **`temperature=0` on production LLM calls** — **centrally fixed inside the frozen adapters**; **Scope B neither sets nor
   overrides it**, and constructs no provider client of its own beyond injecting the frozen ones.
4. **Bias-free** — no demographic attribute enters rule evaluation, the outlier features, or any prompt; the pending store
   persists `ApplicantProfile` as a frozen shape without widening it.
5. **Reproducibility** — the pending store persists the **version stamps `CommitContext` already requires**
   (`rulebook_version`, `engine_version`, `model_version`, `memo_hash`), so a committed decision stays replayable against
   the exact rulebook version active at decision time.

**B) These five plus additional invariant(s) I will name (describe after `[Answer]:`).**

[Answer]: A

---

## 2.9 Answers as given — Q1–Q8 all **A**, with the user's verbatim rationale

- **Q1: A** — *"one new unit, `case-lifecycle` (U24), through the full per-unit BUILD loop … followed by a thin
  composition-root wiring pass that only constructs, injects, and adds the four route modules. This honours Scope A §9's
  'un-designed domain state belongs in its own designed stage' literally, keeps the composition root composition-only
  (preserving the property every prior NOEDIT scan depended on), and gives the lifecycle the per-unit ambiguity-check
  discipline it needs."*
- **Q2: A** — *"five states: submitted → profiled → evaluated → drafted → committed, each transition produced by exactly
  one frozen unit … The boundary is sharp and already frozen: everything up to and including 'drafted' is pending
  pre-commit state owned by U24; 'committed' is `audit_record`, reached only through `DecisionCommitService`. R2/R3/R4 read
  pending state; R5 is the one transition crossing the boundary."*
- **Q3: A** — *"a Scope-B-owned migration directory run through the frozen, parameterized `MigrationRunner` and
  `verify_checksums` … with NO edit to `database` (U15) — using the frozen seam as designed, not editing it. Address the
  surfaced sub-question … as a design detail at the FD stage. This keeps the blast radius to the composition root plus
  genuinely-new artifacts and avoids the first-ever frozen-P1 edit."*
- **Q4: A** — *"a separate explicit drafting trigger; R4 stays a pure side-effect-free GET … The pipeline is driven through
  the existing frozen seams … editing none of them. … How the trigger is invoked is a U24 design detail for the FD stage."*
- **Q5: A** — *"Scope B supplies a real `CommitContextProvider` backed by the pending-recommendation store … the R5 route is
  a thin adapter … The human-in-the-loop invariant is satisfied by the frozen service's CON-BR4 gate and independent authz
  re-check running inside `commit()`, never re-implemented in the route … Accept deliberately: this makes a write path
  reachable for the first time, so a writer engine (`AUDIT_WRITER_URL`) is constructed and the composition root's
  `INV-FAITHFUL` / `test_no_write_route.py` assertion must be deliberately and explicitly revised, not silently dropped."*
- **Q6: A** — *"continue deferring Q1-B; Scope B does not resolve it. … Deferral stays recorded in code, not forgotten."*
- **Q7: A** — *"backend-only in Scope B … Binding the four author-only frontend fetch seams … is a separate follow-on pass
  … The browser demo becomes clickable in that follow-on, not at the end of Scope B."*
- **Q8: A** — *"all five invariants bind as restated."*

---

## 2.5 Mandatory ambiguity-check — **NOT CLEAN: 2 folds RESOLVED + 1 GENUINE GAP → SURFACE-AND-STOP**

**Ran**: 2026-07-19 against the eight answers + the §1 ground truth. **Result: 2 checks resolve; check (iii) surfaced a
real obstacle that a stated element of Q1-A would break. NO U24 extension logged, NO FD begun** — per the standing
"surface-and-stop rather than improvise" instruction.

### ✅ SCOPEB-Fold-1 [check (i)] — RESOLVED: two sequences CAN share one database, with two constraints to pin at FD

**Measured in `migration_runner.py`:**
```python
def _ensure_tracking_table(self):   # CREATE TABLE IF NOT EXISTS applied_migrations (
                                    #   filename VARCHAR PRIMARY KEY, applied_at TIMESTAMPTZ ...)
def _applied_set(self):             # SELECT filename FROM applied_migrations
def apply_all(self):                # for path in migration_files(self._migrations_dir):
                                    #     if path.name in already: continue
```
1. **The tracking table is created idempotently** (`CREATE TABLE IF NOT EXISTS`), so a second sequence's runner creating it
   is **safe** — no collision on setup.
2. **Tracking is keyed by `filename`, not by ordinal or path.** U15's `0001_initial_schema.sql` and a U24
   `0001_case_lifecycle.sql` are **distinct primary keys** — so **both may be numbered `0001` without colliding**.
3. **Each runner only skips files present in its own directory** (`migration_files(self._migrations_dir)` ∩ `already`), so
   the two sequences **coexist correctly** in one shared tracking table.

**⚑ CONSTRAINT 1 (a real hazard, to pin at FD)**: because the primary key is the **bare filename**, if U24 ever used a name
**identical** to a U15 one, the second would be seen as already applied and **silently SKIPPED — a no-op, not an error**.
U24's migration names must be **distinctly descriptive**. Note the glob is `[0-9][0-9][0-9][0-9]_*.sql`, so a `u24_` *prefix*
would not match — **the namespace must live in the descriptive part** (`0001_case_lifecycle.sql`, not `u24_0001_*.sql`).

**⚑ CONSTRAINT 2 (grants — measured in `0002_grants.sql`)**: the audit roles are granted on **`audit_record` and
`applicant_profile_snapshot` ONLY**. New U24 tables therefore have **no `audit_reader`/`audit_writer` grants at all** ⇒
**U24's pending store must be reached via the `DATABASE_URL` (owner) engine** — which the composition root **already
constructs** for R1. **No new grants are required and no U15 edit is implied.** *(Optionally U24 could define its own
least-privilege roles in its own grants migration — an FD design option, not a requirement.)*

**⇒ Q3-A is sound. Not a blocker.**

### ✅ SCOPEB-Fold-2 [check (ii)] — RESOLVED: no contradiction between Q2-A and Q4-A; the risk is real and belongs at FD

**Q2-A (five states) and Q4-A (separate trigger) are consistent** — Q2-A defines *what* the states are and which frozen
unit produces each transition; Q4-A defines *that* advancement is explicit rather than a side effect of a GET. They do not
conflict.

**But the check's concern is legitimate and must not be lost**: with a separate trigger and five states, **an application
CAN sit at `submitted` (or `profiled`, or `evaluated`) indefinitely if nothing invokes the next transition** — and R4 would
honestly report `status: pending` forever. That is an **under-specification both answers acknowledge** (Q4-A says
explicitly: *"How the trigger is invoked is a U24 design detail for the FD stage"*), **not a contradiction**.

**⇒ Carried forward as a NAMED FD question**, with the specific sub-decisions it must settle: **(a)** is
`submitted → profiled → evaluated` **eager on submission** (one atomic advance) or **three separately-triggered steps**?
**(b)** what invokes `evaluated → drafted` — the same trigger, or a second one? **(c)** is there any
retry/re-drive path for an application stuck mid-pipeline, or does a failed transition leave it parked with an explicit
state? **Not a blocker; explicitly routed to FD.**

### ⛔ SCOPEB-GAP-1 [check (iii)] — **GENUINE GAP. A FROZEN unit's LOAD-BEARING test would be broken by Q1-A as stated.**

The check asked whether the `INV-FAITHFUL` revision is *"genuinely confined to the composition root's own test."*
**Measured answer: the writer-engine half is confined — but a DIFFERENT assertion, in a FROZEN unit, is not.**

**What is safely confined (verified):**
- `backend/app/tests/test_no_write_route.py` — including `test_no_writer_engine_is_ever_constructed` (asserts
  `"AUDIT_WRITER_URL" not in code`) — lives in `backend/app/tests/`, i.e. **inside the re-opened territory**. Revising it
  is within Scope B, exactly as Q5-A accepted.
- `llm_judge/tests/test_noedit.py` (U22) — scans **U22's OWN authored set** (`backend/llm_judge/**`). Scope B writing under
  `backend/app/` **does not affect it**.
- `deploy_config/tests/test_noedit.py` (U23) — same shape: iterates **U23's own** authored paths. Its
  `assert sg.is_under_frozen("backend/app/main.py")` is a **detector** on the prefix set, unaffected by new files.
- `deploy_config/tests/test_boot.py` (U23) — asserts `render.yaml`'s `startCommand` contains `backend.app.main:app`, the
  env shapes, and the `preDeployCommand`. **Unaffected** — the module path does not change.
- `deploy_config/tests/test_routes.py::test_route_table_equals_the_frozen_composition_root` — asserts the **(path, method)
  set** equals the frozen seven. **Scope B adds NO route**: R2–R5 already exist at exactly those paths/methods and merely
  stop raising `501`. **The set is unchanged → this test still passes.** ✓

**⛔ What is NOT confined — the gap:**

`backend/deploy_config/tests/test_routes.py` — part of **`NFR-DEP-ROUTES-1`, a LOAD-BEARING full-highest target of the
FROZEN `deploy-config` (U23)** — contains:

```python
def test_no_new_route_file_added_under_backend_app_by_u23():
    routes_dir = sg.REPO_ROOT / "backend" / "app" / "routes"
    route_files = {p.name for p in routes_dir.glob("*.py")}
    assert route_files == {"__init__.py", "session.py", "decisions.py", "not_wired.py"}
```

**This is an EXACT-SET EQUALITY over `backend/app/routes/`.** **Q1-A states the wiring pass "adds the four route
modules."** Adding **any** file there — or renaming/removing `not_wired.py` once R2–R5 are real — **BREAKS this frozen
test.**

**⚑ Why this is a genuine gap and not a detail**: the test's **stated intent** is a *provenance* claim about U23
(*"U23 owns no file under `backend/app/`"*), but its **implementation** is a directory-wide exact-set assertion that fires
on **any author's** addition. Intent and implementation diverge, and Scope B is the first thing to hit the difference.
Discovering this at the wiring pass — **after U24's five full stages** — is precisely the late failure this discipline
exists to prevent, and it is cheap to decide now.

**⇒ This needs a decision that is the user's, not mine. Raised as Question 9. NO U24 extension logged; NO FD begun.**

---

### Question 9 — How does Scope B's route wiring satisfy the frozen U23 exact-set assertion?

**A) Implement R2–R5 IN PLACE inside the existing three route files — the file set never changes.**
`not_wired.py`'s four `501` markers are replaced by real handlers in the same file (or R2/R3/R4 move into a renamed-in-place
concept without adding files). **The frozen U23 test passes untouched, no frozen unit is edited, and Scope B's blast radius
stays exactly as authorized.** *(Cost: the filename `not_wired.py` becomes actively misleading once its contents are wired —
a naming lie in the composition root, which is itself a small honesty problem.)*

**B) Authorize a narrow, surgical edit to U23's `test_routes.py`** — relax the exact-set equality to the **provenance check
its docstring already says it is** (e.g. assert U23 authored no file there, or assert the frozen three remain present)
while leaving `NFR-DEP-ROUTES-1`'s route-table assertion untouched. *(Honest and durable — it makes the test assert what it
says it asserts. **But it edits a FROZEN unit's test and therefore needs its own explicit authorization**, which this pass's
holds currently forbid. It would be the first frozen-unit edit in the build.)*

**C) Add the new route modules and accept that U23's test fails** — recording it as a known, deliberate regression.
*(Rejected as a default: it would break a LOAD-BEARING full-highest target and leave the suite red, which no prior stage in
this build has ever accepted.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

**User's rationale (verbatim)**: *"implement R2–R5 in place within the existing three route files … so the file set under
`backend/app/routes/` never changes and U23's frozen exact-set assertion passes untouched with zero frozen edits. … I chose
A over B deliberately. B … is the more honest long-term fix — the test's exact-set implementation genuinely diverges from
its stated intent, and that divergence is a real latent defect. But editing a frozen unit's test would be the first
frozen-unit edit in the entire build, and this Scope B pass's holds explicitly forbid touching frozen units' internals.
That edit deserves its own separate, deliberate authorization decision, made on its own merits, not folded into this pass
as a side effect. C is correctly rejected — leaving a load-bearing target red is not an acceptable end state."*

### ⚑ NEW REGISTER ITEM — `NOTWIRED-FILENAME-STALE` (register item #13)

| Field | Value |
|---|---|
| **What it is** | Once R2–R5 are implemented **in place** inside `backend/app/routes/not_wired.py`, that filename **no longer describes its contents** — the routes it holds are wired and no longer raise `501`. |
| **Why deferred, not resolved** | U23's frozen `NFR-DEP-ROUTES-1` test asserts **exact-set equality** over `backend/app/routes/` rather than the **provenance claim its docstring describes**. Scope B must therefore keep the filename to keep that frozen test green. **Renaming the file and relaxing the test are a MATCHED PAIR** — the same underlying issue — and belong to their own authorized change. |
| **Owner** | a **future authorized change** (the same pass that would take up Q9-B's test relaxation) |
| **Blocking?** | **Non-blocking** — naming honesty only; no behaviour, contract or invariant depends on the name. |
| **Explicitly NOT done in Scope B** | **The file is NOT renamed. U23's test is NOT edited.** Scope B **lives with the stale name and discloses it**, exactly as the build disclosed `DEPLOY-MIGRATE-DEFERRED` and the `fixtures.py`-vs-`fakes.py` discrepancy rather than silently reconciling them. |

---

## 2.6 Ambiguity-check RE-RUN (Q1–Q9) after Q9-A changed where R2–R5 code lives — **CLEAN**

**Ran**: 2026-07-19 · **Result**: **CLEAN — 2 folds resolved, no new gap.** Q9-A altered a load-bearing assumption, so the
full answer set was re-checked for consequences.

### ✅ SCOPEB-Fold-3 — Q1-A's wiring clause is RESTATED, and the restatement is binding

**Superseded wording (Q1-A as originally written):** *"a thin composition-root wiring pass that only constructs, injects,
and **adds the four route modules**."*

**⚑ BINDING RESTATEMENT (Q9-A):** *"a thin composition-root wiring pass that **constructs, injects, and wires R2–R5 IN
PLACE in the existing route files, adding NO new file under `backend/app/routes/`**."*

Everything else in Q1-A is **unchanged**: U24 still goes through the full five-stage per-unit BUILD loop; the composition
root still only constructs and injects. **Verified consequence**: `backend/app/routes/` keeps exactly
`{__init__.py, session.py, decisions.py, not_wired.py}`, so U23's frozen exact-set assertion **passes untouched** and
**zero frozen units are edited**.

### ✅ SCOPEB-Fold-4 — in-place wiring does NOT push domain logic into `backend/app/`

**The concern is real** — implementing four routes "in place" could mean writing lifecycle logic into the composition root,
breaking its own stated invariant (*"this module (and this package) contains no domain logic"*). **Measured on disk, it
does not**, because the composition root **already has an established two-layer thin-adapter pattern** that Scope B simply
extends:

- **`routes/session.py` (R1)** — the whole handler is `Depends(current_identity)` + a dict projection. **No logic.**
- **`routes/decisions.py` (R6/R7)** — `Depends(get_audit_service, require_read_audit)`, call the frozen service, hand the
  result to a projection function. **No logic.**
- **`projections.py`** — documented verbatim as *"The composition root's **ONLY** transformation layer … **pure functions,
  no I/O, no state**"*, projecting frozen shapes onto the WIRE-1 §5 wire shapes.

⇒ **Scope B's R2–R5 handlers take the identical shape**: `Depends(...)` an **injected U24 service**, call it, hand the
result to a **pure projection** for the `ApplicationSummary` / `MemoView` / `CommittedDecision` wire shapes. **All domain
logic — the lifecycle state model, the pending stores, the drafting trigger, the real `CommitContextProvider` — lives in
U24**, constructed in `dependencies.py` and injected, exactly as every frozen service already is. **The invariant holds by
following the existing pattern, not by exception.**

### ✅ Composition-root tests requiring deliberate revision — enumerated precisely, ALL confined

Q5-A accepted revising `INV-FAITHFUL`. Naming **exactly** which assertions that means, so the revision is deliberate and
complete rather than discovered one failure at a time. **Every one lives in `backend/app/tests/` — inside the re-opened
territory. No frozen unit's test is touched.**

| Assertion in `backend/app/tests/test_no_write_route.py` | Effect of Scope B |
|---|---|
| `test_the_route_table_has_exactly_one_non_get_route` | **STILL PASSES** — R5 remains the only POST |
| `test_the_seven_wire1_routes_are_the_whole_surface` | **STILL PASSES** — no route added or removed |
| `test_every_other_route_is_read_only` | **STILL PASSES** — R2/R3/R4 stay GET |
| `test_its_first_statement_raises_the_marker` | **must be revised** — R5's handler no longer raises a marker |
| `test_the_marker_module_constructs_no_service_and_reads_no_body` | **must be revised** — the module now injects services |
| `test_no_writer_engine_is_ever_constructed` | **must be revised** — `AUDIT_WRITER_URL` is now constructed (Q5-A) |
| `test_no_commit_service_or_context_provider_exists` | **must be revised** — both now exist by design |
| `test_no_repository_write_method_is_called` | **must be revised** — the commit path writes |

**⚑ What must NOT be lost in the revision**: the *substantive* guarantee is no longer "no writes exist" — that is false by
design now — but that **every write goes through the frozen `DecisionCommitService`**, whose CON-BR4 gate and independent
authz re-check run **inside `commit()`**. The revised tests must assert **that**, not simply delete the old assertions.

**⇒ Re-check CLEAN. Vehicle confirmed: `case-lifecycle` (U24).**

---

## 3. Explicit HOLDS for this pass

- **NO code · NO wiring · NO FD artifact** until the `[Answer]` tags are filled, followed by the **mandatory
  ambiguity-check**, **surfacing-and-stopping** on any genuine gap.
- **All 23 completed units consumed BY SHAPE; NONE edited.** Any frozen-unit touch is **Q3's** to authorize explicitly.
- **WIRE-1's frozen contract text NOT touched** (this is also why Q6-A defers Q1-B).
- **tier-B NOT authorized** · the **`audit_store` Docker-guard gap NOT touched** (31 skips + 5 Docker errors to stay
  unchanged) · **no new dependency assumed**.
- **The re-opening is scoped to**: the composition root (`backend/app/`) **+ genuinely-new Scope-B artifacts** — nothing
  else.
- **Two consequences flagged for deliberate acceptance, not silent drift**: **(i)** R5 makes a **write path reachable**,
  so `INV-FAITHFUL` / `test_no_write_route.py` must be **deliberately revised** (Q5); **(ii)** a **writer engine**
  (`AUDIT_WRITER_URL`) gets constructed for the first time.

---

## 4. Next step (STOP here)

Fill the eight `[Answer]:` tags in §2. On your signal I will read the answers, run the **mandatory ambiguity-check**,
**embed the full Q&A in this plan file**, and proceed to whatever vehicle **Q1** selects — **not before**.
**No design or wiring artifact is produced until the answers are in and checked.**
