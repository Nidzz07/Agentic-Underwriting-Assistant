# NFR Design Plan — `rules-engine` (C2)

**Phase / Stage**: BUILD → NFR Design (per-unit, plan-then-generate)
**Loop position**: cluster unit 2 · FD ✅ 2026-07-03 · NFR Requirements ✅ 2026-07-05 → **NFR Design
← here** → **Infrastructure Design (likely SKIP — pure-logic deterministic library, no untrusted
parsing → no sandbox NFR; confirmed + logged at that stage)** → **Code-Gen** (TDD ≥90%).
**Unit**: U3 `rules-engine` — the deterministic rulebook engine (pure Python, **zero LLM**).
**Depth**: comprehensive (invariant-bearing deterministic-core unit).
**Date**: 2026-07-05 · **Runtime**: Python **3.12 pinned** (D6).
**Status**: **Plan — awaiting `[Answer]:` tags.** No NFR Design artifacts generated yet. Stop after
this plan.

This plan follows `.project-guide-rule-details/build/nfr-design.md`. NFR Design is the **"how" for
each "what"** — it turns the approved **`NFR-RULES-*` targets** (the *what*) into concrete **design
patterns + logical components** (the *how*), built **ON the frozen FD and the approved NFR targets —
re-opening neither.** No code yet; that is Code-Gen.

---

## 1. Unit context (analyzed — Step 1) ✅

### 1.1 Inputs this stage builds on (frozen — not re-opened)
- **Frozen FD** (`guide-docs/build/rules-engine/functional-design/`): the C2 contract
  (`load_rulebook` / `evaluate` / `recommend`), the YAML `Rule` schema + `input_fields` mechanism +
  operator↔threshold §2.1 mapping, the tri-state `RuleResult`, the `RuleResultReport` shape, the
  domain-confirmed boundaries (age 18–65 incl., DTI ≤0.40, BMI 25/30), the `Decimal` DR-DTI/DR-INCM
  derivations, the fixed-precedence aggregation, the deterministic `ConfidenceBands`, and the §7
  schema-vs-data boundary (bulk 25–40-rule population deferred to Code-Gen).
- **Approved NFR Requirements** (`guide-docs/build/rules-engine/nfr-requirements/`): the 15
  `NFR-RULES-*` targets + `tech-stack-decisions.md` (RE-D1 pyyaml safe_load, RE-D2 Pydantic-v2
  load-validation, RE-D3 shared `decimal_context`, RE-D4 no-LLM interpreter, RE-D5 `RulebookCanonAdapter`,
  RE-D6 Python 3.12).

### 1.2 What NFR Design produces (the "how")
For **each** approved target, a **design pattern** + the **logical components** that realize it:
| Target(s) (the "what") | Pattern to design (the "how") |
|---|---|
| NFR-RULES-DET-1 / -DET-2 | The **pure-function `evaluate()` + order-independent aggregation pattern**: fixed canonical rule iteration (list byte-stability) + set-based aggregation (permutation invariance) — both DET-1 (same-order ×N) and DET-2 (permuted) structurally guaranteed. |
| NFR-RULES-DEC-1 | The **Decimal-derivation pattern**: DR-DTI/DR-INCM pure, single shared `decimal_context`; **operand-missing → `not_evaluated` → `refer_trigger` by construction (guard before any division — no divide path)**. |
| NFR-RULES-CANON-1 | The **`RulebookCanonAdapter` pattern**: normalize `Rulebook` → canon_ser's existing value space (declared set→sorted-list) → **unchanged** shared util. |
| NFR-RULES-BR1-1 / -BR1-2 / -SCHEMA-1 | The **load-time rejection pattern** (Pydantic-v2 load-validation = the single structural gate) **+** the **independent namespace-exclusion pattern** (resolution namespace built without demographics). |
| NFR-RULES-AUDIT-1 / -2 / -3 | The **deterministic `content_hash` pattern** + **append-only immutable versioning pattern** + the **forensic-not-equality projection** (report separates evaluation-output from provenance; projection = audit-store's). |
| NFR-RULES-AGG-1 | The **fixed-precedence aggregation pattern** (DECLINE > REFER > APPROVE, order-independent; `incomplete`/`not_evaluated` → REFER-never-DECLINE). |
| NFR-RULES-CONF-1 | The **deterministic confidence-banding pattern** (fixed versioned constants, proximity function, no LLM). |
| NFR-RULES-OBS-1 | The **allowlist `TelemetryEmitter` pattern** (structural demographic exclusion — no free-text/profile-value field; the intake precedent). |
| NFR-RULES-PERF-1 | The **observed-only instrumentation** (emit `evaluate` timing via the seam; no hard bound — no untrusted parsing). |

### 1.3 Guardrails held (skill)
- **No LLM anywhere** in the engine (CON-BR2); **CON-DET-1** (pure `evaluate`, order-independent
  aggregation, `Decimal` not float, no wall-clock/unseeded-random/dict-order); **CON-BR1** (demographics
  structurally unreachable — load-time reject + namespace exclusion, and never in telemetry);
  **CON-AUDIT-1** (immutable versions, `content_hash` verifiable, forensic-not-equality); advisory-only
  (`-RECOMMEND`); thin-file → REFER never DECLINE.

### 1.4 Ownership boundaries (reference-not-own — carried from NFR Requirements)
- Shared **CANON-SER** = audit-store §2.1 via `backend/common/canon_ser.py` (used through the
  `RulebookCanonAdapter`, **unchanged**); single **`Decimal` context** = `backend/common/decimal_context`;
  observability **stack** = `observability` (this unit emits only); CON-DET-1 / CON-BR1 **verification**
  = `quality-gates`; replay **orchestration + comparison** = `audit-store` ReplayService; secrets =
  `secrets-config`; cloud infra = `deploy-config` (**Infrastructure Design likely SKIPPED** — no
  untrusted parsing, no independent cloud topology).

---

## 2. NFR Design execution plan (checkboxes — Step 2)

Artifacts generated **after** answers + ambiguity-check (per nfr-design.md Step 6) →
`guide-docs/build/rules-engine/nfr-design/` → `nfr-design-patterns.md`, `logical-components.md`.
Mermaid diagrams **required** (validated against the 7 rules + text alternative).

- [x] **P1. Analyze NFR Requirements + the frozen FD** (§1 above — done).
- [x] **P2. Collect `[Answer]:` tags** (§3); run the ambiguity-check. **DONE 2026-07-05 — all 11
  answered A; ambiguity-check CLEAN (no clarification file). One binding sharpening folded into
  generation: DET-2 completeness — ALL order-derived report list fields (`rule_results`,
  `decline_reasons`, `refer_reasons`) use the one fixed canonical order (by `rule_id`), not iteration
  order.**
- [x] **P3. `nfr-design-patterns.md`** — the design pattern for each `NFR-RULES-*` target (§1.2): the
  pure-function + order-independent-aggregation pattern, the Decimal-derivation pattern, the
  `RulebookCanonAdapter` pattern, the load-time-rejection + namespace-exclusion patterns, the
  `content_hash` + append-only + forensic-not-equality patterns, the fixed-precedence aggregation
  pattern, the confidence-banding pattern, the allowlist `TelemetryEmitter` pattern. Each pattern
  traces to its target + states how the assertion is **structurally** met. Mermaid pattern-integration
  diagram (validated + text alternative). **DONE 2026-07-05 — 8 pattern sections (§1 determinism incl.
  the DET-2 all-list-fields sharpening, §2 Decimal guard-before-divide, §3 RulebookCanonAdapter, §4
  load-reject + independent namespace exclusion, §5 content_hash + append-only, §6 aggregation +
  forensic-not-equality, §7 confidence, §8 telemetry/perf) + §9 traceability + §10 validated
  pattern-integration Mermaid + text alternative.**
- [x] **P4. `logical-components.md`** — the logical components the patterns introduce (§4 below) with
  responsibilities + relationships, **consistent with the FD entities** — logical only, no code.
  Mermaid component-relationship diagram (validated + text alternative). **DONE 2026-07-05 — 9-component
  inventory + §2 ownership table (no component owns a reference-not-own concern) + §3 validated
  component-relationship Mermaid (LR, two subgraphs) + text alternative + §4 consistency check.**
- [x] **P5. Consistency + ownership check** — **DONE** — both artifacts build on the frozen FD +
  approved targets (re-open neither); reference-not-own held throughout; every pattern maps to a target
  it makes structurally achievable; schema-vs-data 25–40-rule authoring stays deferred to Code-Gen.
- [~] **P6. Guardrail compliance pass + present the standardized 2-option completion message** —
  **2-option message PRESENTED 2026-07-05; awaiting Request Changes / Continue → Infrastructure Design
  (likely SKIP) → Code-Gen.** (Do NOT advance until Continue.)

---

## 3. Clarifying questions (Step 3 — fill each `[Answer]:` tag)

Letter choice after each `[Answer]:` tag; if none fit, choose the last option (Other) and describe.
These decide **design patterns** — they do **not** re-open the FD or the approved NFR targets.

### A. Determinism: pure-function `evaluate()` + order-independent aggregation (DET-1 / DET-2)

## Question 1 — `evaluate()` purity + deterministic rule iteration
How is `evaluate` structured so it is a pure function and the `rule_results` list is byte-stable?

A) **Pure function + fixed canonical iteration order.** `evaluate(profile, rulebook_version)` has **no
   I/O, no wall-clock, no unseeded randomness, no dict-order reliance**. Rules are iterated in a **fixed
   canonical order** (e.g. sorted by `rule_id`) **only** to make the emitted `rule_results` **list**
   byte-stable; the order does **not** affect the outcome (aggregation is set-based, Q2). Structurally
   gives **DET-1** (same input, same order, ×N → byte-identical).
B) Iterate in the rulebook's authored (file) order (rejected — fragile to authoring/dict order; not a
   declared canonical order).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — pure function + fixed canonical iteration order. evaluate(profile, rulebook_version) has no I/O, no wall-clock, no unseeded randomness, no dict-order reliance; rules iterated in a fixed canonical order (sorted by rule_id) ONLY to make the emitted rule_results list byte-stable — order does not affect outcome (aggregation is set-based, Q2). Structurally gives DET-1.

## Question 2 — Order-independent aggregation mechanism (DET-2)
How is permuted-order invariance structurally guaranteed (a **distinct** guarantee from DET-1)?

A) **Set-based reduction + re-sorted output.** Aggregation is a **pure reduction over the multiset/set
   of `outcome_tier` contributions** under fixed precedence (Q9) — it never depends on iteration order.
   The `rule_results` list is **re-sorted to the fixed canonical order** (Q1) **before** the report is
   built, so a **permuted** evaluation order produces a **byte-identical** canonical report. This makes
   **DET-2** (permuted-order → identical) structural, independent of DET-1. The permutation/Hypothesis
   test asserts it.
B) Rely on rules always arriving pre-sorted (rejected — doesn't prove order-independence; a permutation
   would then differ).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — set-based reduction + re-sorted output. Aggregation is a pure reduction over the multiset/set of outcome_tier contributions under fixed precedence, never dependent on iteration order; the rule_results list is re-sorted to the fixed canonical order before the report is built, so a permuted evaluation order produces a byte-identical canonical report. DET-2 structural, independent of DET-1.

### B. Decimal-derivation pattern (DEC-1)

## Question 3 — DR-DTI / DR-INCM derivation + operand-missing handling
How are the derivations kept exact and how is operand-missing handled by construction?

A) **Pure derivations under the single shared context + guard-before-divide.** `dti_ratio` /
   `income_multiple` are **pure functions** using the shared `backend/common/decimal_context` (4dp
   `ROUND_HALF_UP`, `Decimal` never float). A **precondition guard** checks operand presence /
   non-zero income **before** any division — if it fails, the rule is emitted `not_evaluated` +
   `refer_trigger` with `actual_value == null` and **no division is ever attempted** (no divide-by-zero
   path exists structurally). Exposed in the resolution namespace so a rule can name them.
B) Compute then catch a divide error (rejected — relies on exception-catching, not a structural guard;
   risks a fabricated/partial value).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — pure derivations under the single shared context + guard-before-divide. dti_ratio/income_multiple are pure functions using backend/common/decimal_context (4dp ROUND_HALF_UP, Decimal never float); a precondition guard checks operand presence/non-zero income BEFORE any division — if it fails, the rule is emitted not_evaluated + refer_trigger with actual_value == null and no division is ever attempted (no divide-by-zero path exists structurally).

### C. Canonicalization pattern (CANON-1)

## Question 4 — `RulebookCanonAdapter` structure
How is the rulebook canonicalized for `content_hash` without touching the shared util?

A) **Adapter → existing value space → unchanged shared `canon_ser`.** A rules-engine
   `RulebookCanonAdapter` reduces the `Rulebook` to canon_ser's **existing** value space —
   **`set`-threshold → declared-sorted `list`** (sorted by **canonical string form**, a deterministic
   total order), **`DecimalRange` → dict of `Decimal`+`bool`**, **enum → `.value`**, **`ScalarLiteral`
   → native scalar** — then calls the **UNCHANGED** `backend/common/canon_ser.py`; `content_hash =
   sha256(canonical bytes)`. **No `canon_ser.py`/§2.1 change; audit-store unaffected.** (The
   `CanonSerAdapter` precedent from intake.)
B) Add a native `set` branch to the shared `canon_ser.py` (deferred — a shared-code change; the adapter
   path avoids it; would be a conscious, logged decision, not the default).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — adapter → existing value space → unchanged shared canon_ser. RulebookCanonAdapter reduces the Rulebook to canon_ser's existing value space (set-threshold → declared-sorted list by canonical string form; DecimalRange → dict of Decimal+bool; enum → .value; ScalarLiteral → native scalar) then calls the UNCHANGED backend/common/canon_ser.py; content_hash = sha256(canonical bytes). No canon_ser.py/§2.1 change; audit-store unaffected. The CanonSerAdapter precedent.

### D. CON-BR1: load-time rejection + independent namespace exclusion (BR1-1 / BR1-2 / SCHEMA-1)

## Question 5 — Load-time rejection pattern (the structural gate)
Where and how are demographic/unknown-field and operator↔threshold violations rejected?

A) **Pydantic-v2 load-validation on the `Rule`/`Rulebook` schema = the single structural gate.**
   `load_rulebook` validates every rule at load: (i) each `input_fields` entry must resolve in the
   **allowlist namespace** (a demographic path or unknown field → **reject**, BR1-1); (ii) the
   `threshold` shape must match the `operator` (§2.1 → **reject**, SCHEMA-1). A malformed/adversarial
   rulebook **fails to load** (raises a load error) — it never reaches `evaluate`. The allowlist is
   **single-sourced** (one declared set of resolvable field names).
B) Validate lazily during evaluation (rejected — a bad rule could partially run; not "fails to load").
C) Other (please describe after [Answer]: tag below)

[Answer]: A — Pydantic-v2 load-validation on the Rule/Rulebook schema = the single structural gate. load_rulebook validates every rule at load: (i) each input_fields entry must resolve in the allowlist namespace (demographic path or unknown field → reject, BR1-1); (ii) threshold shape must match operator (§2.1 → reject, SCHEMA-1). A malformed/adversarial rulebook fails to load (raises), never reaches evaluate. Allowlist single-sourced.

## Question 6 — Independent namespace-exclusion pattern (belt-and-suspenders)
How is demographic-unreachability guaranteed **independently** of the load check?

A) **A `NamespaceBuilder` that constructs the resolution namespace from the allowlist ONLY.** The
   operand namespace handed to the evaluator is built from **only** the demographic-excluded profile
   fields (+ derived `dti_ratio` / `income_multiple`); the `demographics` sub-object is **never**
   placed in it. So even a **hypothetically-loaded** bad rule could not resolve a demographic (no
   resolvable target) — structural, **independent** of Q5's load gate. Both guards tested separately.
B) Rely solely on the load check (rejected — single point; not belt-and-suspenders).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — a NamespaceBuilder that constructs the resolution namespace from the allowlist ONLY. The operand namespace is built from only the demographic-excluded profile fields (+ derived dti_ratio/income_multiple); the demographics sub-object is never placed in it. Even a hypothetically-loaded bad rule could not resolve a demographic (no resolvable target) — structural, independent of Q5's load gate. Both guards tested separately.

### E. Replay: content_hash + append-only + forensic-not-equality (AUDIT-1 / -2 / -3)

## Question 7 — `content_hash` + append-only immutable versioning pattern
How are hash-determinism and append-only immutability structurally realized?

A) **Frozen immutable `Rulebook` + hash over the canonical bytes + versioned store.**
   `load_rulebook(version)` builds an **immutable (frozen)** `Rulebook`; `content_hash =
   sha256(RulebookCanonAdapter bytes)` (Q4) — same rules → same hash, any change → different. Versions
   live in an **append-only** versioned store (a published version's source is **never mutated**; a
   change is a new semver + new file/entry); old versions remain loadable. Load **verifies** the
   recomputed `content_hash` matches the recorded one (tamper-evidence).
B) Mutable rulebook object + hash recomputed ad hoc (rejected — mutation risk; not append-only).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — frozen immutable Rulebook + hash over the canonical bytes + versioned store. load_rulebook(version) builds an immutable (frozen) Rulebook; content_hash = sha256(RulebookCanonAdapter bytes) (Q4); versions in an append-only versioned store (a published version's source never mutated; a change is a new semver + new entry); old versions remain loadable; load verifies the recomputed content_hash matches the recorded one (tamper-evidence).

## Question 8 — Forensic-not-equality: how the report SUPPORTS audit-store's projection
Replay comparison is `audit-store`'s (reference-not-own). How does rules-engine's report support the
forensic-not-equality projection **without owning the comparison**?

A) **Clean field separation in the report + audit-store owns the projection.** The `RuleResultReport`
   cleanly separates the **evaluation-output** fields (per-rule rows + `recommendation` + `confidence`
   — the replay **equality set**) from the **provenance** fields (`rulebook_version` + `content_hash` +
   `engine_version` — forensic/verification). `audit-store`'s `ReplayService` owns the match/mismatch
   **comparison** and applies the projection (excluding provenance) — **exactly its §2.1/§3.1
   projection**. rules-engine provides only pure re-evaluation + the separable report shape; it has **no
   concept of replay**. (Matches AUDIT-3 field-for-field.)
B) rules-engine performs the replay comparison itself (rejected — replay orchestration is audit-store's).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — clean field separation in the report + audit-store owns the projection. The RuleResultReport cleanly separates evaluation-output fields (per-rule rows + recommendation + confidence — the replay equality set) from provenance fields (rulebook_version + content_hash + engine_version — forensic/verification); audit-store's ReplayService owns the match/mismatch comparison and applies the projection (excluding provenance) — exactly its §2.1/§3.1 projection. rules-engine provides only pure re-evaluation + the separable report shape; it has no concept of replay.

### F. Aggregation pattern (AGG-1)

## Question 9 — Fixed-precedence aggregation pattern
How is DECLINE > REFER > APPROVE realized order-independently, with incomplete → REFER-never-DECLINE?

A) **A pure reduction over the `outcome_tier` set under fixed precedence.** `recommend(results,
   incomplete)` = **DECLINE-RECOMMEND** if any `decline_fail`; else **REFER** if any `refer_trigger`
   (including the `incomplete` insufficient-info trigger and every `not_evaluated` → `refer_trigger`);
   else **APPROVE**. **`incomplete` / `not_evaluated` contribute only `refer_trigger`, never
   `decline_fail`** → thin-file lands REFER, never DECLINE. `decline_reasons` / `refer_reasons` collect
   the driving rule_ids. Pure, order-independent (feeds DET-2).
B) Sequential first-match-wins over an ordered rule list (rejected — order-dependent; not a set reduction).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — a pure reduction over the outcome_tier set under fixed precedence. recommend(results, incomplete) = DECLINE-RECOMMEND if any decline_fail; else REFER if any refer_trigger (including the incomplete insufficient-info trigger and every not_evaluated → refer_trigger); else APPROVE. incomplete/not_evaluated contribute only refer_trigger, never decline_fail → thin-file lands REFER never DECLINE. decline_reasons/refer_reasons collect driving rule_ids. Pure, order-independent (feeds DET-2).

### G. Confidence pattern (CONF-1)

## Question 10 — Deterministic confidence-banding pattern
How is confidence banded deterministically, never by the LLM?

A) **A pure `ConfidenceBander` over fixed versioned constants.** Confidence = a pure function of (a)
   the **normalized proximity** of each numeric `actual_value` to its nearest threshold and (b) profile
   completeness, banded via the **fixed `ConfidenceBands` constants carried in the versioned rulebook**
   (`high_margin` / `low_margin`). **No randomness, no wall-clock**; a margin change is a **new rulebook
   version** (replay-stable). **Produced in rules-engine, never the LLM** (CON-BR2). Read-only input to
   the memo.
B) A heuristic tuned at runtime / outside the versioned constants (rejected — not replay-stable).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — a pure ConfidenceBander over fixed versioned constants. Confidence = a pure function of (a) normalized proximity of each numeric actual_value to its nearest threshold and (b) profile completeness, banded via the fixed ConfidenceBands constants carried in the versioned rulebook (high_margin/low_margin). No randomness, no wall-clock; a margin change is a new rulebook version (replay-stable). Produced in rules-engine, never the LLM (CON-BR2). Read-only input to the memo.

### H. Observability pattern (OBS-1)

## Question 11 — Allowlist `TelemetryEmitter` pattern (demographic-free by construction)
How is demographic content structurally excluded from telemetry (not merely omitted)?

A) **An allowlist `TelemetryEmitter` (the intake precedent).** A **Pydantic allowlist schema** of typed
   non-text fields — `rule_id` (rulebook metadata), enums (`recommendation` / `confidence` /
   aggregation-tier / per-rule `status`), **int** counts (per-`recommendation`, fired / `not_evaluated`)
   + derivation timing — and **NO applicant-profile-derived field, no free-text / `str` field** that
   could carry a demographic value. Span text / demographics are **structurally unrepresentable** (no
   field to hold them). Emit-only; the `observability` unit wires it. A **schema-level assertion** proves
   no profile/demographic/free-text field exists (mirrors intake NFR-INT-FORENSIC(b)).
B) Emit rich events and filter demographics out before sending (rejected — relies on a filter, not a
   structural allowlist).
C) Other (please describe after [Answer]: tag below)

[Answer]: A — an allowlist TelemetryEmitter (the intake precedent). A Pydantic allowlist schema of typed non-text fields — rule_id, enums (recommendation/confidence/aggregation-tier/per-rule status), int counts + derivation timing — and NO applicant-profile-derived field, no free-text/str field that could carry a demographic value. Demographics structurally unrepresentable (no field to hold them). Emit-only; observability wires it. Schema-level assertion proves no profile/demographic/free-text field exists (mirrors intake NFR-INT-FORENSIC(b)).

---

## 4. Logical components to be designed (P4 — named now for the plan of record)

Consistent with the FD entities; **logical only** (module split is a Code-Gen concern):

| Component | Responsibility | Realizes pattern |
|---|---|---|
| **`RulebookLoader`** (+ Pydantic-v2 validator) | `load_rulebook(version)` → load YAML (safe_load), **validate at load** (CON-BR1 allowlist + operator↔threshold §2.1 reject), **freeze** an immutable `Rulebook` | Q5 (BR1-1/SCHEMA-1), Q7 (AUDIT-2) |
| **`RulebookCanonAdapter`** | Normalize `Rulebook` → canon_ser value space → **unchanged** shared `canon_ser`; compute `content_hash` | Q4 (CANON-1, AUDIT-1) |
| **`NamespaceBuilder`** | Build the demographic-excluded operand namespace (+ derived `dti_ratio` / `income_multiple`) | Q6 (BR1-2) |
| **`DerivationFunctions`** (DR-DTI / DR-INCM) | Pure `Decimal` derivations via the shared context; guard-before-divide → `not_evaluated`/`refer_trigger` | Q3 (DEC-1) |
| **`RuleEvaluator`** (the `evaluate()` interpreter) | Pure, fixed-order iteration; resolve operands from `input_fields` only; apply operator vs threshold; emit tri-state `RuleResult` | Q1 (DET-1) |
| **`Aggregator`** | Pure set-reduction under fixed precedence (DECLINE>REFER>APPROVE); order-independent; incomplete→REFER | Q2/Q9 (DET-2, AGG-1) |
| **`ConfidenceBander`** | Pure banding on fixed versioned `ConfidenceBands` constants | Q10 (CONF-1) |
| **`ReportBuilder`** | Assemble `RuleResultReport` with **clean output-vs-provenance separation** (supports audit-store's projection) | Q8 (AUDIT-3) |
| **`TelemetryEmitter`** | Allowlist schema (ids/enums/counts/timing), **no profile/demographic/free-text field**; emit-only | Q11 (OBS-1, PERF-1 timing) |

---

## 5. Constraints & settled items held (not re-opened)
- **Frozen FD + approved NFR targets** are the inputs — NFR Design adds patterns/components, re-opens
  **neither** the C2 contract / YAML schema / tri-state `RuleResult` / `RuleResultReport` / boundaries /
  derivations / aggregation / confidence **nor** the `NFR-RULES-*` assertions.
- **Schema-vs-data boundary honored**: the bulk 25–40-rule **data authoring stays deferred to Code-Gen**
  (FD §7). NFR Design designs the **engine + loader/validator/adapter** patterns, not the rule data.
- **Ownership reference-not-own**: shared **CANON-SER** (audit-store §2.1, via the adapter, **unchanged**)
  / shared **`decimal_context`** / observability **stack** / `quality-gates` **verification** /
  `audit-store` **replay-orchestration** / secrets — owned elsewhere. **Infrastructure Design likely
  SKIP** (confirmed + logged at that stage — no untrusted parsing, no independent cloud topology).
- **No LLM anywhere** (CON-BR2); advisory-only (`-RECOMMEND`); Python **3.12 pinned**.
- Three settled non-edits stay closed: `PROJECT-BRIEF.md`, OOS-7 README/case-study doc commitment,
  `user-journey.md`.

---

## 6. Loop position confirmation
**NFR Design (← here) → Infrastructure Design (likely SKIP — pure-logic, no untrusted parsing → no
sandbox NFR, no independent cloud topology; confirmed + logged at that stage) → Code-Gen** (TDD ≥90%,
per-unit). Same per-unit sequence intake followed.

---

## 7. Next step (STOP here)
Fill the eleven `[Answer]:` tags above. On your signal, I will read the answers, run the ambiguity-
check (adding a clarification file only if needed), then generate the NFR Design artifacts
(`nfr-design-patterns.md`, `logical-components.md`, with validated Mermaid + text alternatives) and
present the standardized 2-option completion message. **No NFR Design artifacts or code are generated
until the answers are in and checked.**
