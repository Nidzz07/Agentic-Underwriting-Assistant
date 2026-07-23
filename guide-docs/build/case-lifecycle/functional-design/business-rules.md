# Business Rules — `case-lifecycle` (U24, Scope B)

**Stage**: BUILD → per-unit loop → **Functional Design, Part 2 (Generation)** · **Depth**: **comprehensive** (Q1-A) ·
**Date**: 2026-07-19
**`BR-CASE-1..14`** — each **grounded** (traced to a frozen source or an answered question) and **checkable** (states how it
is verified, and at which tier). Built ON the frozen contracts — **re-opening none.**

---

## BR-CASE-1 — The lifecycle has **five states plus one internal terminal state**

`submitted → profiled → evaluated → drafted → committed`, with **`failed`** reachable from the drafting attempt.
**Each transition's artifact is produced by exactly one frozen unit** (`intake`/`sanitizer` → `rules-engine` →
`outlier-model` + `memo-agent-core`/`memo-extensions` → `audit-store`), so **U24 invents no domain computation**.

- **Grounded**: Scope B **Q2-A** · the frozen `ApplicationSummary` (*"null until a recommendation is drafted"*) ·
  `MemoView.status`.
- **Checkable** *(tier-U)*: a state-machine test asserts the legal transition set and that **every illegal transition is
  rejected**; each transition's artifact is produced by driving the corresponding frozen seam.

## BR-CASE-2 — Transitions are **legal-only and forward-only**; no state is skipped

`submitted → drafted` (skipping evaluation) and any backward move are **rejected**. A case never reaches `drafted` without
a `RuleResultReport`, because `CommitContext` requires one.

- **Grounded**: `CommitContext`'s required fields · the append-only/forward-only discipline (BR-DB-4's shape).
- **Checkable** *(tier-U)*: teeth over the illegal set, each asserted to raise.

## BR-CASE-3 — `submitted → profiled → evaluated` advances **EAGERLY in one transaction**

All three steps are **deterministic, LLM-free and fast** (parse/sanitize, then pure-Python rule evaluation), so submission
either lands at **`evaluated`** or **fails outright** — **a case is never left half-parsed**.

- **Grounded**: **Q4-A** · the *no-LLM-in-the-deterministic-rules-path* invariant.
- **Checkable** *(tier-U)*: after submission the state is `evaluated` and **both** canonical payloads are persisted; a
  failure mid-way leaves **no partial row** (transactional).

## BR-CASE-4 — `evaluated → drafted` requires a **separate explicit trigger**; R4 stays a pure read

The **one expensive, non-deterministic, LLM-bearing** step is the only one behind its own trigger. **R4 performs no
drafting** — it reports `status: pending` until a memo exists, `ready` once drafted.

- **Grounded**: **Q4-A** · WIRE1-Fold-2 (*"the sync-vs-async model is an implementation detail"*) · GET semantics.
- **Checkable** *(tier-U)*: calling the R4 read path **does not** invoke the pipeline (the injected double records **zero**
  calls); after the trigger, state is `drafted` and R4 reports `ready`.

## BR-CASE-5 — **`failed` is a terminal state**, so a stuck case is representable

A drafting failure moves the case to **`failed`** rather than leaving it parked at `evaluated` with no way to tell a
never-triggered case from a broken one.

- **Grounded**: **Q4-A** · SCOPEB-Fold-2 (the stuck-application risk).
- **Checkable** *(tier-U)*: a failing injected double drives the case to `failed`; the state is distinguishable from
  `evaluated`.

## BR-CASE-6 — ⛔ `failed` **projects to `pending`** at the wire, and the gap is **DISCLOSED**

WIRE-1's `status` admits only `ready | pending`. **`failed` is INTERNAL**; R4 emits `pending` — the only legal value.

- **Grounded**: WIRE-1 §5 (**closed** discriminator) · **CASE-Fold-1** · register **#14
  `MEMOVIEW-FAILED-STATE-UNMODELLED`** (owner: a future authorized **WIRE-1 amendment**; **non-blocking**).
- **Checkable** *(tier-U)*: a `failed` case yields a **contract-valid** `MemoView` with `status == "pending"`; **no U24
  artifact claims WIRE-1 models a failed state**. **WIRE-1's contract text is NOT amended.**

## BR-CASE-7 — The two rich shapes are stored as **CANON-SER `BYTEA` + `content_hash`**, never JSON

`ApplicantProfile` and `RuleResultReport` are persisted exactly as the frozen schema persists them.

- **Grounded**: **Q8-A** · `0001_initial_schema.sql` (`rule_results BYTEA` / `profile_canonical BYTEA` / `content_hash`) ·
  `canon_ser.py`'s **P1–P4** guarantees · **CASE-GAP-1**.
- **⚑ Why**: JSON guarantees **none** of P1–P4, so a reordered key or a `Decimal` rendered as a float would break hash
  equality **silently on a later run**. CANON-SER makes the **pending and committed sides byte-identical**, removing any
  conversion from the replay path.
- **Checkable** *(tier-U)*: a **round-trip** `serialize → deserialize → serialize` is **byte-identical**; `Decimal` and
  `date` return **as themselves**; `content_hash` is stable across runs; a mutated byte **fails** the hash check.

## BR-CASE-8 — Canonicalization **reuses the frozen `CanonSerAdapter`**; U24 forks nothing

U24 calls **`audit_store.CanonSerAdapter`** (`canonical_bytes` / `content_hash`, generic over `BaseModel`) — the same
adapter `commit_service.py` already uses.

- **Grounded**: **CASE-Fold-3** · the adapter's own docstring (*"one convention for both … **no fork, no §2.1 change**"*).
- **⚑ Why it matters**: `canon_ser` takes **plain values, not models**, and the reduction **must** be
  `.model_dump(mode="python")` — `mode="json"` would pre-stringify `Decimal`s so the `$dec` envelope never fires, **silently
  losing P2 type fidelity**. The frozen adapter already encodes this; U24 must not re-derive it.
- **Checkable** *(tier-U)*: a scan asserts **no U24 module calls `canon_ser` directly** or re-implements the reduction;
  `$`-prefixed keys appear nowhere in U24's data.

## BR-CASE-9 — Canonicalization happens **at the transition that finalizes each shape**

The two rich shapes are canonicalized **in the eager transaction**; the four stamps land at **drafting**. `content_hash` is
computed **at the same call site** as the bytes it attests.

- **Grounded**: **CASE-Fold-4** · BR-CASE-3/4's transaction boundary.
- **Checkable** *(tier-U)*: after submission both payloads **and** their hashes are persisted; the hash always matches its
  stored bytes.

## BR-CASE-10 — `route_borderline` is an **explicit U24 pipeline step**

U24 calls `route_borderline(rule_report, outlier_result)` and hands the resulting **`ThinkingMode`** to the provider
adapter (a **constructor argument**).

- **Grounded**: **CASE-Fold-2** — measured: the orchestrator has **zero** borderline/routing references; the router is a
  **free, pure function** with **no client parameter**.
- **⚑ `ThinkingMode` is NOT persisted**: it is a pure deterministic function of `(rule_report, outlier_signal)`, both of
  which **are** persisted ⇒ **exactly reproducible from stored state**. Its absence is a decision, not an oversight.
- **Checkable** *(tier-U)*: a `REFER` report yields `EXTENDED` and the adapter receives it; re-deriving the mode from
  stored state reproduces the same value.

## BR-CASE-11 — U24's migrations are **namespaced and collision-guarded**

U24 owns its own `migrations/` + `checksums.json`, run through the **frozen parameterized** runner/verifier;
**`database` (U15) is NOT edited**.

- **Grounded**: **Q3-A** · **SCOPEB-Fold-1** (the tracking table is keyed by **bare `filename` PK**; the glob is
  `[0-9][0-9][0-9][0-9]_*.sql`).
- **⚑ The hazard**: an identically-named file across the two sequences would be **silently skipped as already-applied — a
  no-op, not an error**. A **startup collision assertion fails loudly** instead.
- **Checkable** *(tier-U)*: filenames are disjoint from U15's; a **synthetic colliding name is flagged** (detector
  self-test); `verify_checksums` passes against U24's own manifest.

## BR-CASE-12 — Migration invocation is **in-process and confined to U24's own sequence**

U24 applies **only** its own migrations. **How they run at deploy time remains `DEPLOY-MIGRATE-DEFERRED` (#8) — unchanged,
still open, NOT adopted.**

- **Grounded**: **Q5-A** · register #8.
- **Checkable** *(tier-U)*: U24's runner is constructed with **its own** `migrations_dir`; a scan asserts U24 **never**
  passes `database`'s default directory and **authors no CLI entrypoint**.

## BR-CASE-13 — The **commit boundary is the frozen service's**, never re-implemented

`PendingCommitContextProvider` supplies **context only**. The CON-BR4 gate and the **independent** authz re-check run
**inside** `DecisionCommitService.commit()`.

- **Grounded**: **Q5-A of Scope B** · `commit_service.py`'s ordered enforcement (gate **before** assembly).
- **⚑ Advisory-only / human-in-the-loop**: the pending store holds **recommendations, never decisions**; a
  `CommittedDecision` exists **only** as R5's result.
- **Checkable** *(tier-U)*: a **structural scan** asserts **no U24 module implements a gate, an authz check, or a write to
  `audit_record`**; the provider returns a `CommitContext` and **nothing more**.

## BR-CASE-14 — U24 emits **no new metric**

- **Grounded**: **Q7-A** · `observability`'s frozen **five** `METRIC_DEFINITIONS` · `deploy-config`'s five-panel no-drift
  scan · U22's `NOMETRIC-1`.
- **Checkable** *(tier-U)*: a scan asserts **no U24 module declares a metric name or `MetricDefinition`**; U21's five and
  U23's dashboard stay **byte-unchanged** (**read-only; neither suite re-run**).

---

## The five inherited invariants, restated for U24

| # | Invariant | How U24 holds it |
|---|---|---|
| 1 | **Advisory-only / human-in-the-loop** | BR-CASE-13 — the pending store holds **recommendations, never decisions**; the frozen gate runs inside `commit()`. U24 declares **no** verdict field of its own. |
| 2 | **No LLM in the deterministic rules path** | BR-CASE-3 — `profiled`/`evaluated` are LLM-free by construction; the LLM sits **only** in `evaluated → drafted`, strictly after rule evaluation. |
| 3 | **`temperature=0` on production LLM calls** | **Centrally fixed inside U19's frozen adapters.** U24 **neither sets nor overrides it** and constructs no provider client of its own. |
| 4 | **Bias-free** | No demographic attribute enters rule evaluation, the outlier features, or any prompt. `ApplicantProfile` is persisted **as a frozen shape, not widened**. |
| 5 | **Reproducibility** | BR-CASE-7/9 — CANON-SER's **P1–P4** + `content_hash`, plus the four version stamps `CommitContext` requires, kept as **first-class scalar columns**. `ThinkingMode` is re-derivable (BR-CASE-10). |

---

## Traceability — no orphan

| Rule | Traces to | Tier |
|---|---|---|
| BR-CASE-1 | Q2-A · `ApplicationSummary` · `MemoView` | U |
| BR-CASE-2 | `CommitContext` required fields | U |
| BR-CASE-3 | Q4-A · invariant #2 | U |
| BR-CASE-4 | Q4-A · WIRE1-Fold-2 | U |
| BR-CASE-5 | Q4-A · SCOPEB-Fold-2 | U |
| BR-CASE-6 | WIRE-1 §5 · CASE-Fold-1 · **register #14** | U + disclosure |
| BR-CASE-7 | Q8-A · `0001_initial_schema.sql` · CANON-SER P1–P4 · CASE-GAP-1 | U |
| BR-CASE-8 | CASE-Fold-3 · the frozen adapter | U (structural) |
| BR-CASE-9 | CASE-Fold-4 | U |
| BR-CASE-10 | CASE-Fold-2 · `borderline_router.py` | U |
| BR-CASE-11 | Q3-A · SCOPEB-Fold-1 | U (detector) |
| BR-CASE-12 | Q5-A · register #8 | U (structural) |
| BR-CASE-13 | Scope B Q5-A · `commit_service.py` | U (structural) |
| BR-CASE-14 | Q7-A · U21/U23 frozen | U (structural) |

**Every `BR-CASE-*` is checkable at tier-U.** The only undischarged items U24 touches are the **named, disclosed** register
entries — **#8 `DEPLOY-MIGRATE-DEFERRED`** (unchanged) and **#14 `MEMOVIEW-FAILED-STATE-UNMODELLED`** (new). **U24 claims
no discharge of either.**
