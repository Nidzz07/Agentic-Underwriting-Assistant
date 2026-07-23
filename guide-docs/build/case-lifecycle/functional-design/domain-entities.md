# Domain Entities — `case-lifecycle` (U24, Scope B)

**Stage**: BUILD → per-unit loop → **Functional Design, Part 2 (Generation)** · **Unit**: U24 · **Scope B** ·
**Depth**: **comprehensive** (Q1-A) · **Date**: 2026-07-19
**Built ON** the Scope B scoping answers **Q1–Q9** and U24's FD answers **Q1–Q8**, plus folds **SCOPEB-Fold-1..4** and
**CASE-Fold-1..4** — **re-opening none.**

**⚑ U24 is the FIRST unit added after the original 23-unit decomposition completed.** It owns the **pending (pre-commit)**
half of the underwriting case; the **committed** half remains `audit-store`'s, untouched.

---

## 1. Scope

`case-lifecycle` owns the **un-designed domain state** Scope A refused to invent: the **pending-application /
pending-recommendation lifecycle** that R2–R5 read and write. It **drives** the frozen pipeline through existing seams and
**persists** what a commit will later need — then hands off to the frozen `DecisionCommitService` at the boundary.

**It does NOT own**: memo *generation* (U4's) · rule *evaluation* (U3's) · outlier *scoring* (U18's) · borderline *routing
logic* (U19's — U24 **invokes** it, see §6) · the *committed* record, its authz gate, or its atomic write (U12's) · route
*binding* (the composition root's, in a later wiring pass) · the frontend (Q7-A, backend-only).

---

## 2. `CaseState` — the five states + one internal terminal state

```text
submitted → profiled → evaluated → drafted → committed
                                 ↘ failed          (internal only)
```

| State | Meaning | Produced by (frozen unit) |
|---|---|---|
| `submitted` | the case exists; nothing parsed yet | — (U24 creates the row) |
| `profiled` | a validated, sanitised `ApplicantProfile` exists | **`intake` (U1) + `document-sanitizer` (U2)** |
| `evaluated` | a `RuleResultReport` (+ `Recommendation`, `Confidence`) exists | **`rules-engine` (U3)** |
| `drafted` | a `DecisionMemo` (+ `OutlierResult`) exists; a **recommendation is ready for review** | **`outlier-model` (U18)** + **`memo-agent-core` (U4)** / **`memo-extensions` (U19)** |
| `committed` | an underwriter acted; an `audit_record` row exists | **`audit-store` (U12)** — **U24 does not write this** |
| **`failed`** | drafting failed; the case is **parked and representable**, not silently stuck | U24 (terminal) |

**⚑ The boundary is sharp and already frozen**: everything **up to and including `drafted`** is **pending state U24 owns**.
**`committed` is `audit_record`**, reachable **only** through `DecisionCommitService`. **R2/R3/R4 read pending state; R5 is
the one transition that crosses the boundary.**

### 2.1 ⛔ `failed` has NO wire representation — disclosed, not hidden (CASE-Fold-1 / register #14)

WIRE-1's `MemoView.status` is a **closed two-value discriminator** — `ready | pending` — and defines `pending` as *"the
pipeline has **not yet** produced a memo."* A failed case fits the **literal** wording but not the *"not **yet**"*.
**WIRE-1 is genuinely silent on this case.**

**Resolution**: `failed` is **INTERNAL to U24**; at the R4 wire boundary it **projects to `pending`**, the only legal
value. Nothing frozen is violated and `ui-memo-view` keeps a defined shape. **The imprecision is disclosed as register item
`MEMOVIEW-FAILED-STATE-UNMODELLED`** (owner: a future authorized **WIRE-1 amendment**; **non-blocking** — the loss is
diagnostic precision at the wire, not correctness). **WIRE-1's contract text is NOT amended here.**

---

## 3. `PendingApplication` — the case record

| Field | Type | Notes |
|---|---|---|
| `application_id` | `str` | PK — the case id, the key R2/R3/R4 address |
| `state` | `CaseState` | the §2 state; **`failed` never leaves U24 un-projected** |
| `profile_canonical` | `bytes` | **CANON-SER bytes** of `ApplicantProfile` (Q8-A) |
| `profile_content_hash` | `str` | `sha256` over those bytes — tamper/drift check |
| `rule_results_canonical` | `bytes \| null` | **CANON-SER bytes** of `RuleResultReport`; `null` before `evaluated` |
| `rule_results_content_hash` | `str \| null` | as above |
| `rulebook_version` | `str \| null` | **stamp** — first-class scalar (Q2-A) |
| `engine_version` | `str \| null` | **stamp** |

**Why bytes, not JSON (Q8-A / CASE-GAP-1)**: the frozen `0001_initial_schema.sql` stores **these same two shapes** as
`BYTEA` CANON-SER + a `content_hash`, because CANON-SER guarantees **P1** stable key order · **P2** `Decimal`-as-string,
never float · **P3** canonical scalars · **P4** no volatile fields — *"the same logical content serializes to the same
bytes on every run."* JSON guarantees none of these. Using CANON-SER makes the pending and committed sides
**byte-identical**, so **no conversion sits on the replay path** and drift fails **loudly at write time**, not silently at
replay.

---

## 4. `PendingRecommendation` — what a commit will need

Created at `drafted`. **Its contents are already specified by a frozen shape**: it must be sufficient to reconstruct a
`CommitContext` **exactly**.

| Field | Type | Reconstructs |
|---|---|---|
| `recommendation_id` | `str` | PK — **the key R5 commits by** |
| `application_id` | `str` | FK → `PendingApplication` |
| `memo_canonical` | `bytes` | the `DecisionMemo` (CANON-SER) — R4's `memo` |
| `outlier_canonical` | `bytes \| null` | the `OutlierResult` (CANON-SER) — R4's `outlier` |
| `memo_hash` | `str` | **stamp** → `CommitContext.memo_hash` |
| `model_version` | `str` | **stamp** → `CommitContext.model_version` |
| `engine_version` | `str` | **stamp** → `CommitContext.engine_version` |
| `rulebook_version` | `str` | **stamp** → `CommitContext.rulebook_version` |

`CommitContext.rule_results` and `.applicant_profile` are rehydrated from the **`PendingApplication`** (§3) — the two rich
shapes live in one place, not duplicated.

---

## 5. `PendingCommitContextProvider` — the real seam implementation

The frozen `CommitContextProvider` Protocol is `get(recommendation_id) -> CommitContext`. Today **only
`DictCommitContextProvider`** implements it — labelled by `audit-store` itself a *"Test/fake provider."* **U24 supplies the
real one.**

```text
PendingCommitContextProvider.get(recommendation_id) -> CommitContext
    1. load PendingRecommendation by recommendation_id      (unknown -> raise, R5 maps to 404)
    2. load its PendingApplication
    3. rehydrate rule_results + applicant_profile           (frozen CanonSerAdapter, by shape)
    4. return CommitContext(rule_results=…, memo_hash=…, model_version=…,
                            engine_version=…, rulebook_version=…, applicant_profile=…)
```

**⚑ It supplies context ONLY.** It performs **no** authorization, **no** gate check and **no** write — those run **inside**
the frozen `DecisionCommitService.commit()` (CON-BR4 gate **before** assembly, then an **independent** authz re-check).
**U24 never re-implements the human-in-the-loop enforcement; it composes with it.**

---

## 6. `CasePipeline` — driving the frozen units (Q6-A)

Ordered composition through **existing seams**, editing none:

```text
intake(+sanitizer) -> ApplicantProfile
rules_engine       -> RuleResultReport
outlier_model      -> OutlierResult
route_borderline(rule_report, outlier_result) -> ThinkingMode      # ⚑ U24 MUST call this
memo adapter(thinking_mode=…) + LangGraphOrchestrator.run(MemoAgentInput) -> DecisionMemo | None
```

**⚑ `route_borderline` is NOT internal to the orchestrator (CASE-Fold-2).** Measured: the orchestrator contains **zero**
references to borderline/routing/`ThinkingMode`. `route_borderline` is a **free, pure function** in `memo-extensions`
holding **no client, no provider, no network** (a provider is *structurally un-injectable* — it has no `client`
parameter), reading the outlier **by shape**. ⇒ **U24 owns this step explicitly**: call it, then hand the resulting
`ThinkingMode` to the provider adapter, which takes it as a **constructor argument**.

**`ThinkingMode` is deliberately NOT persisted**: it is a pure deterministic function of `(rule_report, outlier_signal)`,
both of which **are** persisted — so it is **exactly reproducible from stored state**. Its absence is a decision, not an
oversight.

**tier-U**: every LLM-bearing dependency is **injected**; tier-U drives **offline doubles** — no key, no network, no live
LLM — the discipline all 23 prior units held. **`temperature=0` stays centrally fixed in the frozen adapters; U24 neither
sets nor overrides it.**

---

## 7. `CaseMigrationSequence` — U24's own, run through the frozen seam (Q3-A / Q5-A)

U24 owns `migrations/` + its own `checksums.json`, executed by the **frozen parameterized**
`MigrationRunner(engine, migrations_dir=<U24's>)` and verified by `verify_checksums(migrations_dir=…, manifest_path=…)`.
**`database` (U15) is NOT edited** — the seam is used as designed.

**Two constraints from SCOPEB-Fold-1, binding:**
1. **Distinctly descriptive filenames.** The shared `applied_migrations` table is keyed by **bare `filename` (PK)**, so an
   identically-named file across the two sequences would be seen as **already applied and SILENTLY SKIPPED — a no-op, not
   an error**. The runner globs `[0-9][0-9][0-9][0-9]_*.sql`, so a `u24_` **prefix would not match** — the namespace lives
   in the **descriptive part** (e.g. `0001_case_lifecycle.sql`).
2. **A startup collision assertion** fails **loudly** if U24's filenames ever intersect U15's. *(A naming convention alone
   is a promise; the assertion is the enforcement.)*

**Invocation** (Q5-A): U24 exposes an **in-process** call applying **only its own** sequence. **How it runs at deploy time
remains `DEPLOY-MIGRATE-DEFERRED` (#8) — unchanged, still open, NOT adopted here.**

---

## 8. Reference-not-own — every frozen artifact U24 consumes

| Artifact | Owner | How consumed |
|---|---|---|
| `ApplicantProfile`, the sanitizer | `intake`/`document-sanitizer` (U1/U2) | **driven through existing seams**; shape imported read-only |
| `RuleResultReport` · `Recommendation` · `Confidence` | `rules-engine` (U3) | read-only; evaluation driven, never re-implemented |
| `OutlierResult` | `outlier-model` (U18) | read-only; **advisory, no verdict field** |
| `MemoAgentInput` · `DecisionMemo` · `LangGraphOrchestrator.run()` | `memo-agent-core` (U4) | driven through its existing seam; **`PromptBuilder` NOT touched** |
| **`route_borderline` · `ThinkingMode`** | `memo-extensions` (U19) | **⚑ invoked explicitly** (§6); pure function, read-only |
| provider adapters (`ClaudeAdapter`, `OllamaAdapter`) | `memo-extensions` (U19) | constructed with an injected client + `thinking_mode`; **`temperature=0` stays centrally fixed inside them** |
| **`CanonSerAdapter`** (`canonical_bytes` / `content_hash`, generic over `BaseModel`) | **`audit-store` (U12)** | **⚑ reused BY SHAPE** — no new adapter, no fork of §2.1 |
| **`canon_ser` / `canon_deserialize` / `content_hash`** | **`common`** (spec authority `audit-store`) | reached **through** the adapter above; `$`-prefixed keys **reserved** |
| `CommitContext` · `CommitContextProvider` · `DecisionCommitService` · `CommittedDecision` | `audit-store` (U12) | **composed with**; U24 implements the Protocol, **never the enforcement** |
| `MigrationRunner` · `verify_checksums` | `database` (U15) | **parameterized seam only** (§7) |
| `Role` · `to_role` · `AuthRBAC` · `RBAC_COMMIT` | `auth-rbac` (U11) | applied, **never re-decided**; **Q1-B NOT resolved** |
| `MemoView` · `ApplicationSummary` · the R1–R7 table | **WIRE-1** | **satisfied exactly; contract text NOT touched** |

**Owned by U24 (new here):** `CaseState` · `PendingApplication` · `PendingRecommendation` ·
`PendingCommitContextProvider` · `CasePipeline` · `CaseMigrationSequence`.

**U24 introduces no change to any frozen shape, adds no metric (Q7-A), and authors nothing under `backend/app/`.**
