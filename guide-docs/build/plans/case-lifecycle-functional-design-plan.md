# Functional Design Plan (Part 1) — `case-lifecycle` (U24, Scope B)

**Phase / Stage**: BUILD → per-unit loop → **Functional Design, Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `case-lifecycle` (**U24**) — **FD ← here (the 1st of U24's 5 stages)**
**Unit**: U24 · **Scope B** · **Date**: 2026-07-19
**Status**: **Q1–Q7 ANSWERED (all A) · ambiguity-check RAN → NOT CLEAN (2 folds resolved + 1 GENUINE GAP) → SURFACED AND STOPPED at Question 8.** NO FD artifact; no code; no wiring; `backend/case_lifecycle/` ABSENT.

> **⚑ U24 is the FIRST unit added after the original 23-unit decomposition was completed.** It exists because Scope B was
> explicitly authorized, and it enters the **full per-unit BUILD loop** exactly as all 23 prior units did.
> **The in-place composition-root wiring pass comes ONLY after U24's five stages complete.**

**Built ON** the Scope B scoping plan's answers **Q1–Q9 (all A)** and folds **SCOPEB-Fold-1..4** — **re-opening none.**

---

## 0. DISCOVER-carryover check

**Result: CLEAN — no carryover blocks U24. Three register items bear directly on scope and become questions.**

- **#2 (R2–R5 unwired / demo path not runnable)** — **this is the item U24 exists to address.** Not a blocker; the goal.
- **#3 tier-B** — **NOT authorized, and not required**: U24's lifecycle is verifiable at tier-U on fixtures, the same
  posture every prior unit held. No corpus is read. *(No question needed — settled by the standing hold.)*
- **#1 Q1-B divergence** — **explicitly NOT resolved by Scope B** (Q6-A). U24 inherits the frozen `PERMISSION_MATRIX` and
  applies it; it neither re-decides nor amends WIRE-1. *(Settled; recorded here so it is not re-derived.)*
- **#13 `NOTWIRED-FILENAME-STALE`** — a **wiring-pass** concern, not U24's. U24 authors nothing under `backend/app/`.
- **#4 `audit_store` Docker-guard gap** — untouched; U24 adds no Docker-dependent test. **31 skips + 5 errors stay
  unchanged.**
- **#8 `DEPLOY-MIGRATE-DEFERRED`** — ⚑ **genuinely adjacent**: U24 introduces a **second migration sequence**, and the
  absent migration CLI entrypoint is exactly what would run it in a deployment. **Surfaced as Q5**, not assumed.

---

## 1. Depth recommendation — **comprehensive**, with justification

**Checked, not assumed.** U24 has no `unit-of-work.md` line (it postdates that artifact), so depth is argued from the
build's own precedent rather than inherited:

- `execution-plan.md` L199's *Comprehensive* class is **units that design real topology or bear real invariants**; L200's
  *Lighter* class is *"pure-logic units … display units … `admin-cli` has none."*
- **U24 is neither lighter case.** It **invents a lifecycle state model**, **introduces new persistent state and a second
  migration sequence**, **drives the full frozen pipeline**, and **sits on the human-in-the-loop commit boundary** — the
  system's single most consequential invariant.
- Precedent: `audit-store` (U12), which also owns a commit boundary and an invariant-bearing service, ran **comprehensive**.
- **⚑ It is also the first unit whose failure could make the system finalize a decision without underwriter action** — if
  the commit path were mis-composed. That alone argues against a lighter treatment.

**⇒ Recommendation: comprehensive.** *(Confirmed by Q1 below — stated as a recommendation, not pre-filled.)*

---

## 2. The frozen contracts U24 builds ON — re-read, NOT re-derived

Re-read on disk during the Scope B ground-truth pass (`scope-b-r2-r5-plan.md` §1) and **inherited verbatim**:

| Contract | Owner | What U24 must honour |
|---|---|---|
| **`ApplicationSummary`** `{application_id, recommendation_id\|null, recommendation\|null, confidence\|null}` | WIRE-1 | R2's list item; *"null until a recommendation is drafted"* |
| **`MemoView`** with **`status: ready\|pending`** + **`outlier: OutlierResult\|null`** | WIRE-1 (Folds 2 & 4) | R4's shape; **the contract deliberately does NOT pin the drafting trigger** |
| **`CommittedDecision`**; R5 keyed by **`recommendation_id`** | WIRE-1 / `audit-store` | R4 carries the `recommendation_id` the client then commits |
| **`CommitContext`** = `rule_results` · `memo_hash` · `model_version` · `engine_version` · `rulebook_version` · `applicant_profile` | `audit-store` (U12) | **⚑ Already specifies what the pending store must hold** |
| **`CommitContextProvider`** `Protocol: get(recommendation_id) -> CommitContext` | `audit-store` (U12) | U24 supplies the **real** implementation (only a test fake exists) |
| **`DecisionCommitService.commit()`** — CON-BR4 gate **before assembly**, independent authz re-check, atomic write | `audit-store` (U12) | **Composed with, NEVER re-implemented** |
| `ApplicantProfile` + sanitizer · `RuleResultReport`/`Recommendation`/`Confidence` · `OutlierResult` · `MemoAgentInput`/`DecisionMemo` · `LangGraphOrchestrator.run()` · provider adapters | U1/U2 · U3 · U18 · U4 · U19 | Driven **through existing seams**, editing none |
| `MigrationRunner(engine, migrations_dir=…)` · `verify_checksums(migrations_dir=…, manifest_path=…)` | `database` (U15) | **Consumed through the parameterized seam ONLY** (Q3-A) |
| `Role` · `to_role` · `AuthRBAC` · `RBAC_COMMIT` | `auth-rbac` (U11) | Applied, not re-decided |

**Settled by Scope B — NOT re-opened here**: the **five-state model** (Q2-A) · the **separate drafting trigger** (Q4-A) ·
the **Scope-B-owned migration directory** (Q3-A) · the **real `CommitContextProvider` + thin R5 adapter** (Q5-A) ·
**backend-only scope** (Q7-A) · **the five binding invariants** (Q8-A) · **in-place wiring** (Q9-A).

---

## 3. Proposed FD scope (3 artifacts, the established structure)

`guide-docs/build/case-lifecycle/functional-design/` — `domain-entities.md` · `business-rules.md` (**`BR-CASE-1..N`**) ·
`business-logic-model.md` (the lifecycle + a validated Mermaid + text alternative).

---

## 4. Clarifying questions — fill each `[Answer]:` tag

> **I will improvise none of these.** Options are lettered; a recommendation is given where the ground-truth pass produced
> a grounded one. **No answer is pre-filled.**

---

### Question 1 — Confirm the depth

**A) Comprehensive (RECOMMENDED — see §1).** U24 invents a lifecycle, adds persistent state and a migration sequence,
drives the full pipeline, and sits on the human-in-the-loop commit boundary — the one place a defect could let a decision
finalize without underwriter action. Precedent: `audit-store` (U12).

**B) Standard.** *(Available; but it would treat the commit-boundary unit more lightly than `audit-store`, which owns the
same invariant.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 2 — The pending-store schema: how is `CommitContext` reconstructed?

`CommitContext` requires **six** things: `rule_results` (a whole `RuleResultReport`), `memo_hash`, `model_version`,
`engine_version`, `rulebook_version`, `applicant_profile` (a whole `ApplicantProfile`). Two are **nested frozen Pydantic
models**, not scalars. **How they are persisted is genuinely open**, and it determines replay fidelity.

**A) Store the two rich shapes as validated JSON columns; the four stamps as scalar columns (RECOMMENDED).**
`rule_results` and `applicant_profile` are round-tripped through their **frozen Pydantic models** (`model_dump_json` /
`model_validate_json`), so what is read back is **exactly** the frozen shape — no hand-mapped field list to drift. The four
version stamps become first-class columns (indexable, queryable, and directly visible for the reproducibility invariant).
**Why**: the frozen models are the schema; re-declaring their fields in DDL would duplicate a frozen contract and rot the
moment either changes. Precedent: `applicant_profile_snapshot` already persists a profile as a stored artifact.
**Cost**: JSON columns are opaque to SQL-level querying — acceptable, since R2/R3/R4 fetch by id, not by profile predicate.

**B) Fully normalized columns for every field of both shapes.** *(Queryable; but it re-declares two frozen schemas in DDL
and must be re-migrated whenever either changes — a frozen-contract duplication the build has consistently avoided.)*

**C) Store the whole `CommitContext` as one JSON blob.** *(Simplest; but the version stamps stop being first-class, which
weakens the reproducibility story exactly where it matters most.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 3 — Migration namespacing, given SCOPEB-Fold-1's two measured constraints

Fold-1 established: the shared `applied_migrations` table is keyed by **bare `filename`** (PK), and the runner globs
**`[0-9][0-9][0-9][0-9]_*.sql`** — so a `u24_` *prefix* would not match, and an **identically-named** file would be
**silently skipped as already-applied (a no-op, not an error)**.

**A) Distinctly descriptive names + a startup collision assertion (RECOMMENDED).**
U24's files are named `0001_case_lifecycle.sql`, `0002_case_lifecycle_grants.sql` (if needed) — numerically independent of
U15's sequence but **descriptively unmistakable**. **Plus a guard**: U24 asserts at migration time that its filenames are
**disjoint from U15's**, so a future collision **fails loudly instead of silently no-op'ing**. **Why**: the silent-skip
hazard is the dangerous half of Fold-1, and a name convention alone is a promise, not an enforcement.

**B) Descriptive names only, no guard.** *(Simpler; leaves the silent-skip hazard unguarded — a future migration named the
same as a U15 one would be skipped with no error.)*

**C) A separate tracking table for U24's sequence** (pass a distinct `TRACKING_TABLE`). *(Fully isolates the two
sequences — but `TRACKING_TABLE` is a **module-level constant** in the frozen runner, **not** a parameter, so this would
require either editing U15 or not using its runner. **Rejected under Q3-A's no-frozen-edit hold** — surfaced so the
rejection is on record.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 4 — What invokes the lifecycle transitions, and can an application get stuck?

SCOPEB-Fold-2 routed this here. Q4-A settled **that** advancement is explicit (R4 stays a side-effect-free GET) but **not
what invokes it**. The open sub-decisions: is `submitted → profiled → evaluated` **one eager advance** or **three separate
steps**? What drives `evaluated → drafted`? **And can an application sit at an intermediate state forever with R4 honestly
reporting `pending`?**

**A) Eager deterministic advance on submission; a SEPARATE explicit trigger for drafting (RECOMMENDED).**
Submission runs `submitted → profiled → evaluated` **synchronously in one transaction** — all three are **deterministic,
LLM-free, fast** (`intake` parse/sanitize → `rules-engine` evaluate). **Only `evaluated → drafted` needs its own trigger**,
because that is the **one expensive, non-deterministic, LLM-bearing step**. **Why**: it puts the boundary exactly where the
cost boundary actually is; it means an application is **never stuck in a half-parsed state** — it is `evaluated` (fully
useful for R2/R3) or it failed submission outright; and only the LLM step can leave `pending`, which is precisely what the
frozen `status: pending` exists to express. **A `failed` terminal state is proposed** so a stuck application is
*representable* rather than silently parked.

**B) Every transition separately triggered.** *(Maximum control and retryability per step; but four trigger surfaces to
drive, and an application really can sit at `submitted` — the risk Fold-2 named.)*

**C) Fully eager including drafting** (submission drafts the memo too). *(One step, always `ready`; but it makes
submission slow and non-deterministic, and couples intake to LLM availability — a submission would fail if the provider
were down.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 5 — How does U24's migration sequence actually get run? (the `DEPLOY-MIGRATE-DEFERRED` adjacency)

Register item **#8** records that `render.yaml`'s `preDeployCommand` names a migration runner with **no CLI entrypoint**
(`backend/database/migrate.py` is absent). U24 now adds a **second** sequence that also needs running. **This is a real
adjacency, surfaced rather than assumed.**

**A) U24 owns an in-process migration call at its own composition point; the CLI entrypoint stays `DEPLOY-MIGRATE-DEFERRED`
(RECOMMENDED).**
U24 exposes a callable that applies **its own** sequence through the frozen parameterized runner. **How it is invoked at
deploy time remains item #8's**, unchanged and still open. **Why**: it keeps U24's scope to its own state, does not
silently adopt another unit's deferred deliverable, and **does not widen #8** — U24 makes it *no worse*.

**B) U24 also delivers the missing CLI entrypoint**, discharging #8 for both sequences. *(Tempting — one runner for both,
and #8 closes. But it takes on `database`'s/composition's deliverable inside U24's scope, and the entrypoint would need to
run **two** sequences owned by **different** units — a coordination design #8 never specified.)*

**C) Defer entirely** — U24 defines the migration but nothing runs it in this scope. *(Honest; but U24's tests would then
have no path to a real schema, weakening its own verification.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 6 — Where does the drafting orchestration live, and how is it tested at tier-U?

U24 must drive `intake → rules-engine → outlier-model → memo-agent-core/memo-extensions` **through existing seams**. The
memo step needs an `LLMClient`; every prior unit tested such paths with an **injected offline double** (U4's `LLMClient`,
U19's `CapturingThinkingClient`, U21's recording fakes, U22's `DeclaredScoreEngine`).

**A) A U24 `CasePipeline` driving the frozen units, with every LLM-bearing dependency INJECTED; tier-U uses offline doubles
(RECOMMENDED).**
`CasePipeline` composes the frozen units in order and is handed its collaborators. At tier-U the memo step is driven by an
**injected offline double** — no key, no network, no live LLM — the **exact discipline all 23 units held**. `temperature=0`
stays **centrally fixed in the frozen adapters**; U24 neither sets nor overrides it (Q8-A).
**Why**: it is the established pattern, and it keeps U24's suite deterministic and CI-safe.

**B) U24 calls the frozen units directly from the store/service layer** (no distinct pipeline object). *(Fewer moving
parts; but it entangles persistence with orchestration and gives the LLM seam no single injection point.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 7 — Does U24 emit telemetry / a metric?

`observability` (U21) is frozen with **exactly five** `METRIC_DEFINITIONS`, and `deploy-config`'s five-panel no-drift scan
(plus U22's `NOMETRIC-1`) pins that number. U24 is the first genuinely new **runtime request path** since.

**A) NO new metric; U24 emits nothing into U21's frozen five (RECOMMENDED).**
A sixth metric would be **drift against a frozen topology** and would **break `deploy-config`'s five-panel scan** — the
same reasoning that settled U22's Q6-A. If U24 emits anything, it is its own domain state, not a Prometheus metric.
**Why**: it keeps two frozen units' load-bearing assertions green with zero negotiation.

**B) U24 emits through U21's existing injected trace/metric Protocols** without adding a definition. *(Arguably free — the
Protocols exist and take arbitrary steps. But the wiring is `OBS-SINK-DEFERRED`'s open half, so it would lean on an
undischarged deferral.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

## 4.5 Mandatory ambiguity-check (Q1–Q7 all A) — **NOT CLEAN: 2 folds RESOLVED + 1 GENUINE GAP → SURFACE-AND-STOP**

**Ran**: 2026-07-19 · **Result**: **NO FD artifact generated.** Checks (ii) and (iii) resolve; **check (i) surfaced a real
divergence from a frozen mechanism purpose-built for the reproducibility invariant.**

### ⛔ CASE-GAP-1 [check (i)] — **GENUINE GAP: Q2-A's JSON serialization diverges from the frozen CANON-SER precedent**

The check asked to *"confirm the migration file's actual DDL is consistent with what Q2-A commits to storing."*
**Measured on disk, I cannot confirm it — the frozen precedent uses a different mechanism, and the difference is
load-bearing.**

**`0001_initial_schema.sql`, verbatim — the frozen store persists the SAME TWO SHAPES Q2-A names:**
```sql
rule_results       BYTEA NOT NULL,  -- RuleResultReport as opaque CANON-SER bytes (BR-DB-10)
profile_canonical  BYTEA NOT NULL,  -- original ApplicantProfile as opaque CANON-SER bytes (BR-DB-10)
content_hash       VARCHAR NOT NULL -- sha256 of the canonical bytes (pre-replay tamper check)
```
**Not JSON — `BYTEA` CANON-SER bytes, plus a `content_hash` tamper check.**

**`backend/common/canon_ser.py`, verbatim — why that mechanism exists:**
> *"CANON-SER guarantees the §2.1 properties so **replay comparison and `content_hash` integrity checks are meaningful —
> the same logical content serializes to the same bytes on every run**: **P1** stable lexicographic key ordering (declared,
> never insertion/hash order) · **P2** `Decimal` as string, never IEEE float · **P3** canonical scalar forms … · **P4** no
> volatile fields injected."*

**⚑ Why this is a genuine gap and not a detail.** `model_dump_json()` **does not guarantee P1–P4**. The pending store holds
the artifacts that become a **committed, replayable decision**, and **Q8-A binds reproducibility as one of U24's five
invariants**. Three concrete consequences:
1. **Hash stability** — `memo_hash` and any tamper check depend on byte-stable serialization. JSON output that reorders
   keys or renders a `Decimal` as a float would break equality **silently on a later run**, not loudly at write time.
2. **A serialization seam across the commit boundary** — the pending store would hold **JSON** while `audit_record` holds
   **CANON-SER bytes** for **the very same two shapes**, so the commit path must convert, and *that conversion* becomes
   where replay fidelity is won or lost.
3. **`Decimal` is not incidental here** — money fields are `Decimal` throughout (`rules_engine` explicitly rejects `float`
   via `_reject_float`), which is precisely what CANON-SER's **P2** protects and what naive JSON is most likely to damage.

**⚑ My §4 Q2-A recommendation cited *"Precedent: `applicant_profile_snapshot` already persists a profile as a stored
artifact"* — that statement is TRUE but IMPRECISE, and I am correcting it here rather than letting it stand**: the
precedent persists it as **canonical bytes**, not JSON. The *intent* Q2-A gave (avoid duplicating frozen schemas in DDL) is
fully satisfied by CANON-SER too — `BYTEA` is equally opaque and duplicates nothing. **The two options differ only in the
serializer, and only one of them was designed for replay.**

**⇒ This needs your decision, not mine. Raised as Question 8. NO FD artifact generated.**

### ✅ CASE-Fold-1 [check (ii)] — RESOLVED **by disclosure**: WIRE-1 is genuinely silent on `failed`

**`MemoView.status` is a CLOSED two-value discriminator** — WIRE-1 §5 defines exactly `"ready | pending"`, with:
> *"**`status: "pending"`** → the pipeline has **not yet** produced a memo for this application."*

A `failed` application has produced no memo, so it **fits the literal wording** — but *"not **yet**"* implies it will
eventually be `ready`, which a failed case **will not**. ⇒ **WIRE-1 is silent on the failed case.** This is exactly the
situation the check anticipated: it must be **disclosed, not quietly decided**.

**Resolution consistent with the standing holds** (*"do not touch WIRE-1's contract text"*): **`failed` is an INTERNAL U24
lifecycle state; at the R4 wire boundary it projects to the only legal value, `pending`.** `ui-memo-view` keeps a defined
shape and nothing in the frozen contract is violated. **The imprecision is disclosed as a register item, not hidden.**
*(Amending WIRE-1 to add a third status is the honest long-term fix — and is **forbidden by this pass's holds**, exactly as
Q9-B's test relaxation was.)*

**⚑ NEW REGISTER ITEM #14 — `MEMOVIEW-FAILED-STATE-UNMODELLED`**

| Field | Value |
|---|---|
| **What** | WIRE-1's `MemoView.status` admits only `ready \| pending`. U24's `failed` terminal state has **no wire representation** and is projected to `pending`, which reads as *"not yet drafted"* rather than *"drafting failed"*. |
| **Why deferred** | Adding a third status value **amends WIRE-1's frozen contract text** — forbidden by Scope B's holds. Belongs to its own authorized change. |
| **Owner** | a **future authorized change** (a WIRE-1 contract amendment) |
| **Blocking?** | **Non-blocking** — the shape stays valid and the client still renders; the loss is diagnostic precision at the wire, not correctness. |

### ✅ CASE-Fold-2 [check (iii)] — RESOLVED: routing is **NOT** internal; U24 **must** invoke it explicitly

**Measured**: a grep of `memo_agent_core/orchestrator.py` for `borderline` / `route_borderline` / `ThinkingMode` /
`thinking` returns **ZERO hits**. The orchestrator does **not** route.

`memo_extensions/borderline_router.py` exposes a **free, pure function**:
```python
def route_borderline(rule_report, outlier_signal: OutlierSignal | None = None) -> ThinkingMode
```
— `EXTENDED` when the recommendation is `REFER`, **or** the outlier score is `>=` the cutoff, **or** any rule is within the
proximity margin; otherwise `STANDARD`. It holds **no client, no provider, no network** (a provider is *structurally
un-injectable* — there is no `client` parameter), and reads the outlier **by shape** through a U19-local Protocol.

⇒ **Concrete consequence for Q6-A's `CasePipeline`, to be pinned in the FD**: U24 must **explicitly** (a) call
`route_borderline(rule_report, outlier_result)` after the outlier step, and (b) hand the resulting `ThinkingMode` to the
provider adapter — U19's adapters take it as a **constructor argument**
(`OllamaAdapter(client, model=…, thinking_mode=…)`). **Routing is not free; it is a step U24 owns.** Note the outlier is
passed **by shape**, so U24 needs no new coupling. **No user decision required — but this materially shapes the pipeline,
so it is recorded rather than discovered at NFR Design.**

---

### Question 8 — How are `rule_results` and `applicant_profile` serialized in the pending store?

Raised by **CASE-GAP-1**. Q2-A's *intent* (no frozen schema duplicated in DDL; version stamps as first-class columns) is
**kept in every option** — only the serializer differs.

**A) CANON-SER `BYTEA` + a `content_hash`, mirroring the frozen precedent exactly (RECOMMENDED).**
The pending store uses `backend/common/canon_ser.py` — the **same single canonical utility** `intake` and `audit-store`
already share — with `rule_results` and `applicant_profile` as `BYTEA` and a `content_hash` tamper check, and the four
version stamps as scalar columns. **Why**: the artifacts crossing the commit boundary are then **byte-identical in both
stores**, so no conversion sits on the replay path; P1–P4 (stable ordering, `Decimal`-as-string, canonical scalars, no
volatile fields) hold **by construction**, protecting Q8-A's reproducibility invariant; and it **reuses the frozen shared
utility rather than introducing a second serialization discipline** into a system whose whole audit story rests on the
first. **Cost**: bytes are opaque to SQL inspection — the same trade the frozen store already accepted.

**B) JSON columns via `model_dump_json` / `model_validate_json`, as Q2-A originally stated.**
*(Human-readable and directly inspectable in the DB; but it introduces a **second serialization discipline** for the same
two shapes, puts a conversion step on the commit/replay path, and forfeits the P1–P4 guarantees the frozen mechanism exists
to provide — in the one store whose contents become a replayable audit record.)*

**C) JSON for `applicant_profile` (inspectable) + CANON-SER for `rule_results` (replay-critical).** *(A middle path; but
two mechanisms in one table is the least explicable option, and `applicant_profile` is itself replay-critical — the frozen
store canonicalises it too.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

## 4.6 Ambiguity-check RE-RUN (Q1–Q8) after Q8-A switched the encoding — **CLEAN**

**Ran**: 2026-07-19 · **Result**: **CLEAN — 2 folds resolved, no new gap. FD Part 2 generated.**

### ✅ CASE-Fold-3 [check (i)] — RESOLVED, and better than the question assumed: a FROZEN GENERIC ADAPTER ALREADY EXISTS

**`canon_ser` has NO shape coupling whatsoever.** Its signature is `canon_ser(value: Any) -> bytes`, and it is purely
**structural** — recursing over `None`/`bool`/`Enum`/`Decimal`/`datetime`/`date`/`int`/`str`/`list`/`tuple`/`dict`. There
is nothing shape-specific to un-pick. Companions `canon_deserialize(data: bytes) -> Any` and `content_hash(value: Any)`
are equally generic.

**⚑ One real subtlety — and it is ALREADY SOLVED by a frozen artifact.** `canon_ser` accepts **plain Python values, not
Pydantic models**: a `RuleResultReport` handed in directly would raise
`CanonSerError("type … is not canonically serializable")`. The model must first be reduced via `.model_dump(mode="python")`
— and **`mode="python"` is load-bearing**: `mode="json"` would pre-stringify `Decimal`s, so the `$dec` envelope would never
fire and **P2's type fidelity would be silently lost on the round-trip**.

**U24 does not need to know any of that, because the adapter already exists** — `backend/audit_store/canon_adapter.py`,
**generic over `BaseModel`**, written for **exactly these two shapes**:
```python
class CanonSerAdapter:
    @staticmethod
    def canonical_bytes(model: BaseModel) -> bytes: return canon_ser(model.model_dump(mode="python"))
    @staticmethod
    def content_hash(model: BaseModel) -> str:      return _content_hash(model.model_dump(mode="python"))
```
Its docstring states the intent verbatim: *"Normalizes a Pydantic model (the imported `RuleResultReport` or
`ApplicantProfile`) … **one convention for both** `rule_results` and `profile_canonical` … **no fork, no §2.1 change**."*
It is the same adapter `commit_service.py:122` already uses.
⇒ **U24 reuses the frozen `audit_store.CanonSerAdapter` BY SHAPE** — no new adapter, no re-declaration of the `mode="python"`
detail, and **byte-identical encoding on both sides of the commit boundary by construction**. *(Note there are two adapters
named `CanonSerAdapter`: `intake`'s is `ApplicantProfile`-specific; **audit-store's is the generic one U24 uses**.)*
**One constraint inherited**: CANON-SER **reserves `$`-prefixed dict keys** — U24 must not introduce any.

### ✅ CASE-Fold-4 [check (ii)] — RESOLVED: canonicalize at the transition that FINALIZES each shape; no interaction with routing

**Where canonicalization happens follows directly from Q4-A's transition boundary — it is not a free choice:**

| Transition | Shape finalized | Canonicalized + hashed |
|---|---|---|
| `submitted → profiled → evaluated` *(eager, one transaction)* | `ApplicantProfile`, then `RuleResultReport` | **both, at the end of that transaction** |
| `evaluated → drafted` *(separate trigger)* | `DecisionMemo` → `memo_hash`; `model_version` | the **four scalar stamps** land here |

**Canonicalization is NOT deferred to a single late point**, because the two rich shapes are finalized in the **eager**
transaction while the stamps arrive at the **drafting** transition — a single late point would mean holding un-persisted
domain objects across a trigger boundary, defeating the durability the pending store exists for. **`content_hash` is
computed at the same call site as `canonical_bytes`** (it is `sha256` over those same bytes — one adapter, two static
methods), so the hash can never drift from the bytes it attests.

**⚑ No interaction with `route_borderline` (check (iii)'s finding).** Routing sits in the **drafting** transition,
**downstream** of both canonicalized shapes: it *reads* `rule_report` + `outlier_result` and returns a `ThinkingMode` that
configures the adapter. It writes nothing and finalizes no persisted shape.
**And `ThinkingMode` itself need NOT be persisted**: `route_borderline` is a **pure deterministic function of
`(rule_report, outlier_signal)`**, both of which **are** persisted — so the routing decision is **exactly reproducible from
stored state**, satisfying Q8-A's reproducibility invariant **without** adding a column. *(Recorded so a future reader does
not mistake its absence for an oversight.)*

**⇒ Re-check CLEAN. FD Part 2 generated.**

---

## 5. Explicit HOLDS

- **No FD artifact until all `[Answer]` tags are filled**, followed by the **mandatory ambiguity-check**,
  **surfacing-and-stopping** on any genuine gap.
- **No code · no wiring · `backend/case_lifecycle/` NOT created · nothing under `backend/app/` touched** (the wiring pass
  comes only after U24's five stages).
- **WIRE-1's contract text NOT touched · Q1-B NOT resolved · `not_wired.py` NOT renamed · U23's test NOT edited · no
  frozen unit's internals touched** (`database`/U15 consumed **only** through its parameterized migration seam) · the
  **`audit_store` Docker-guard gap NOT touched** · **tier-B NOT authorized**.
- **The five invariants bind** (Q8-A): advisory-only/human-in-the-loop (satisfied by the frozen `DecisionCommitService`
  gate — the pending store holds **recommendations, never decisions**) · no LLM in the deterministic rules path ·
  `temperature=0` centrally fixed in the frozen adapters · bias-free · reproducibility (the version stamps
  `CommitContext` requires).

---

## 6. Next step (STOP here)

Fill the seven `[Answer]:` tags in §4. On your signal I will read the answers, run the **mandatory ambiguity-check**,
**embed the full Q&A in this plan file**, and generate **FD Part 2** (the three artifacts) — then present the standardized
2-option completion message. **No FD artifact is generated until the answers are in and checked.**
