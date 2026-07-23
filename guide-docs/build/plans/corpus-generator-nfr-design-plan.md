# NFR Design Plan (Part 1) — `corpus-generator` (U14)

**Phase / Stage**: BUILD → NFR Design, **Part 1 (Planning)** (plan-then-generate; numbered `[Answer]` tags to fill)
**Loop position**: `corpus-generator` (U14) — FD ✅ · NFR Requirements ✅ **APPROVED** → **NFR Design Part 1 ← here.**
**Unit**: U14 `corpus-generator` · **Date**: 2026-07-07 · **Depth**: **COMPREHENSIVE** · owns **CON-BR3**, DATA-1/2/3, FR-PROV-4 · Story **US-PLAT-7**.
**Status**: **ANSWERED (all four `[Answer]: A`) · ambiguity-check CLEAN (two resolutions embedded as ND-Fold-1 / ND-Fold-2, §8A) · Part 2 GENERATED 2026-07-07** — `guide-docs/build/corpus-generator/nfr-design/nfr-design-patterns.md` (8 patterns + typed-exception taxonomy + validated pattern-integration Mermaid + text alt) and `logical-components.md` (C1–C8 + substrate + reference-not-own [five surfaces] + component→target coverage no-orphan + validated component-relationship Mermaid + text alt). Re-saved with answers + folds embedded (standing convention). STOPPED at the NFR-Design 2-option gate.

Built **ON** the frozen FD (**eleven BR-CORP rules**, **four folds**, **five call-only dependencies** incl. `common.canon_ser`) and
the approved **NFR Requirements** (**eleven `NFR-CORP-*` targets**, tiers **U/S/B**, **folds NFR-1/NFR-2**) — **re-opening none**. Each
`NFR-CORP-*` target maps to a **named design pattern** + a **logical component**, at the rigor of the other comprehensive units
(rules-engine / audit-store / memo-agent-core / database).

---

## 1. What NFR Design produces (Part 2 preview)
- `nfr-design-patterns.md` — one section per **pattern**, each structurally meeting its `NFR-CORP-*` target(s) + traceability + a
  **validated pattern-integration Mermaid** (7 rules + text alternative).
- `logical-components.md` — the **named components** + responsibilities + ownership + a **reference-not-own check** against the five
  call-only surfaces + a **component→target coverage** table (no orphan) + a **validated component-relationship Mermaid**.

---

## 2. Pattern → `NFR-CORP-*` target map (draft; one pattern per row)

| Pattern | Target(s) | Structural mechanism (draft) |
|---|---|---|
| **P1 SeededGenerationPattern** | DET-1 | ONE `random.Random(seed)` instance threaded through `ProfileFactory` + `RejectionSampler`; **Faker seeded from it**; **no global `random`, no wall-clock**; `generation_timestamp` recorded post-hoc, excluded from content |
| **P2 LabelingOraclePattern** | LABEL-1 | `LabelingOracle` wraps `rules_engine.evaluate()` **call-only**; the record `label` is assigned **only** from the oracle's return; **no other code path sets a label** |
| **P3 BoundedRejectionSamplingPattern** | BOUND-1 | keep-if-class-needed under `attempt_budget`; **pigeonhole precondition** (Q2) + a **named typed exception** (Q1) on exhaustion; loop bounded → no hang (Fold 1 / NFR-2) |
| **P4 ConjunctiveSkewAuditPattern** | SKEW-BAND-1 + SKEW-EDGE-1 | `SkewAudit` computes **two independent sub-checks** — band(±3pp) and edge-checklist — **AND-ed only at the top level, never blended into one score** (Fold 2); build-blocking (typed exception, Q1) |
| **P5 FreezeManifestPattern** | FREEZE-1 + HASH-1 | `CorpusManifestBuilder`/`FreezeAdapter` canonicalizes the `CorpusRecord` list (**explicit included vs excluded field-set**, Q3/Q4) and **delegates hashing to `common.canon_ser.content_hash`**; provenance excluded; single `rulebook_version`; frozen corpus is self-contained data |
| **P6 DemographicSwapInvariancePattern** | SEGREGATION-1 | swap the `Demographics` sub-object → **same engine label**; scoped as **this unit's OWN layered-respect check** — **NOT** owning/duplicating `quality-gates`' bias-swap suite |
| **P7 ReferenceNotOwnBoundaryPattern** | REFNOTOWN-1 + PROFILE-1 | the **five** call-only boundaries with **structural no-edit guards** (no local hasher/derivation/rule-eval/second-temperature); profile built via `ProfileFactory` using `intake.derivations`; Pydantic round-trip + derivation-equality |
| **P8 GovernancePIIPattern** | PII-1 | governance statement + **light-structural** (no external-identifier source; no non-mocked network read outside tier B) |

**No orphan** — all eleven `NFR-CORP-*` targets covered (FREEZE-1+HASH-1 share P5; SKEW-BAND-1+SKEW-EDGE-1 share P4).

---

## 3. Logical components (draft)

| ID | Component | Responsibility | Backs |
|---|---|---|---|
| **C1** | **`GenerationConfig`** | value object — `seed`, `target_split`, `tolerance_pp=3`, `attempt_budget`, `min_profiles`, `rulebook_version`, `model_id` | DET-1, BOUND-1, SKEW-* |
| **C2** | **`ProfileFactory`** | seeded raw-input construction → valid `ApplicantProfile` (via `intake.derivations` + synthetic `application_id`) | DET-1, PROFILE-1 |
| **C3** | **`LabelingOracle`** | wraps `rules_engine.evaluate(profile, rulebook_version)` → `Recommendation` (call-only) | LABEL-1 |
| **C4** | **`RejectionSampler`** | bounded rejection-sampling toward per-class quotas under `attempt_budget`; pigeonhole precondition; raises the typed exception on exhaustion | BOUND-1 |
| **C5** | **`SkewAudit`** | two independent sub-checks (band + edge-checklist), AND-ed at top; build-blocking | SKEW-BAND-1, SKEW-EDGE-1 |
| **C6** | **`DocumentTextGenerator`** | build-time prose via the **injected** `LLMClient` (Gemini; mocked in CI) | FR-PROV-4 (+ PII-1) |
| **C7** | **`CorpusManifestBuilder` / `FreezeAdapter`** | canonicalize the `CorpusRecord` list + `common.canon_ser.content_hash`; build + freeze the manifest (single `rulebook_version`) | FREEZE-1, HASH-1 |
| **C8** | **`CorpusGenerator`** (orchestrator) | drives factory→derive→label→sample→gate→prose→freeze; the tier-S smoke entrypoint; holds the reference-not-own boundary | DET-1, all (composition) |
| — | **test/structural substrate** | no-edit/no-local-reimpl guards (REFNOTOWN-1/HASH-1), PII structural check, SkewAudit synthetic-input tests | REFNOTOWN-1, PII-1 |

---

## 4. Reference-not-own check (the five call-only surfaces — none edited)

| Surface | Owner | corpus-generator | Guard |
|---|---|---|---|
| `intake.schema.ApplicantProfile` + `intake.derivations` | `intake` | **calls** (profile shape + age/BMI) | no local derivation |
| `rules_engine.evaluate` + `Recommendation` | `rules-engine` | **calls** (label oracle) | no local rule-eval |
| `memo_agent_core.provider.LLMClient` | `memo-agent-core` | **drives** (injected prose seam) | no second temperature; injected |
| `GEMINI_API_KEY` (`secrets-config`) | `secrets-config` | **reads** (tier B) | no secret literal |
| `common.canon_ser` (`content_hash`) | shared `backend/common/` (no unit owns; audit-store spec authority) | **calls** (manifest hash) | **no local hasher/serialization** |

Not owned here: CON-BR1 bias-swap suite / feature vector (`quality-gates` / `outlier-model`), rule-eval logic, decision finalization.

---

## 5. Component → target coverage (no orphan — finalized at Part 2)
DET-1→C1/C2/C8 · LABEL-1→C3 · BOUND-1→C4(+C1) · SKEW-BAND-1→C5 · SKEW-EDGE-1→C5 · FREEZE-1→C7 · HASH-1→C7 · SEGREGATION-1→C2/C3 (swap+re-evaluate) · REFNOTOWN-1→C8+substrate · PROFILE-1→C2 · PII-1→C6+substrate. **All eleven covered.**

## 6. Mermaid (Part 2)
Both artifacts will carry a **7-rule-validated Mermaid** + text alternative (pattern-integration in `nfr-design-patterns.md`;
component-relationship in `logical-components.md`), consistent with database / memo-agent-core / rules-engine.

---

## 7. Clarifying questions (fill each `[Answer]` tag; last option = Other)
Genuine **pattern-decision** opens — they do **not** re-open the FD, the NFR-CORP targets, or the folds.

### Question 1 — Typed-exception taxonomy (P3 / P4 build-blocking)
How are the build-blocking failures raised?
A) **One unit base exception `CorpusGenerationError` with two subclasses** — `BudgetExhaustedError` (P3, budget exhaustion) and
   `SkewAuditError` (P4, band or edge-checklist failure). Named, typed, catchable; tests assert the specific subclass. **Recommended.**
B) A **single** `CorpusGenerationError` for both (less granular).
C) Other.

[Answer]: A

### Question 2 — Pigeonhole precondition realization (P3 / BOUND-1 / Fold NFR-2)
How is the pigeonhole guarantee structured?
A) **Pre-flight feasibility guard + runtime exhaustion guard** — a structural pre-flight check raises immediately when the config is
   infeasible (a per-class required count **> `attempt_budget`**, i.e. `quota > budget`), **before any sampling** (seed-independent by
   construction — Fold NFR-2); a runtime budget-exhaustion guard still raises for a feasible-on-paper config the seeded factory can't
   satisfy within budget. Both raise `BudgetExhaustedError`. **Recommended** (makes the guarantee structurally checkable, as asked).
B) **Runtime-exhaustion only** — no pre-flight; the loop runs to `attempt_budget` then raises (matches BOUND-1 AC literally; less explicit).
C) Other.

[Answer]: A

### Question 3 — `CorpusRecord` canonicalization projection (P5 / HASH-1)
How is each `CorpusRecord` reduced to a `canon_ser`-serializable structure for `content_hash`?
A) **Reuse intake's `CanonSerAdapter` projection convention** for the profile sub-part (`profile.model_dump(mode="python")` — the
   blessed profile→canon projection) wrapped in the composite record `{ profile, label, edge_case_tags, documents_text }`, then
   `common.canon_ser.content_hash(<list>)`. **`canon_ser` stays the single hasher**; the profile projection is single-sourced with
   intake (extends the intake consumed surface, call-only). **Recommended.**
B) **Inline `profile.model_dump(mode="python")`** in corpus-generator (identical call; does not import `CanonSerAdapter`) + the same
   composite + `canon_ser.content_hash`. Avoids extending the intake surface; the trivial `model_dump` is not a serialization convention.
C) Other.

[Answer]: A

### Question 4 — `content_hash` field-set vs DET-1 comparison-set (P5 / HASH-1 vs DET-1)
Which fields go into the freeze `content_hash`, and does it differ from DET-1's determinism-comparison set?
A) **`content_hash` INCLUDES `documents_text`** (freeze/tamper-evidence over **all committed content**: `profile` + `label` +
   `edge_case_tags` + `documents_text`), while **DET-1's byte-identity comparison EXCLUDES `documents_text`** (frozen LLM prose is
   not part of the **seeded-generation** determinism; only the structured `profile`+`label`+`edge_case_tags` are). Both **exclude**
   the manifest provenance (`generation_timestamp`, `content_hash` itself, version/count metadata) per P4. The two field-sets differ
   **by design** and I'll state both explicitly. **Recommended.**
B) Make the two sets identical (e.g., exclude `documents_text` from `content_hash` too — weaker freeze integrity; not recommended).
C) Other.

[Answer]: A

---

## 8. Carried folds (referenced, not re-derived)
FD **Fold 1** (bounded rejection-sampling) → P3 · **Fold 2** (band AND edge, independent) → P4 · **Fold 3** (engine label authority /
termination) → P2/P3 · **Fold 4** (single `rulebook_version`) → P5. NFR **Fold NFR-1** (tier S = wiring smoke, test-scoped config) →
C8 smoke entrypoint · **Fold NFR-2** (pigeonhole seed-independent raise) → P3 (Q2).

## 8A. NFR-Design folds resolved at the ambiguity-check (answers all A; no frozen artifact re-opened)
- **ND-Fold-1 — Shared band arithmetic; pre-flight quota uses the band LOWER EDGE (check (i) / Q2 / P3 ↔ P4).** The pre-flight
  feasibility guard's per-class "required count" is the band **lower edge** `ceil(min_profiles × (target_prop − tolerance_pp/100))`,
  read from the **single** `(target_split, tolerance_pp)` on `GenerationConfig` (C1) — **not** `min_profiles × class_proportion` (the
  band **center**, which would be *unsound* and false-raise on band-feasible configs). `SkewAudit`'s band check reads the **same**
  `(target_split, tolerance_pp)`; **one band definition, two uses**, so the pre-flight and the final band check **cannot independently
  disagree**. Answers the user's check (i): the guard needs the **full target distribution + tolerance band**, and the two arithmetics
  are the **same single-sourced** definition. Fold NFR-2's coarse `quota > budget` pigeonhole is the special case.
- **ND-Fold-2 — `CanonSerAdapter` is part of the already-listed `intake` surface, not a sixth (check (ii) / Q3 / P5 / P7).**
  `CanonSerAdapter` lives in `backend/intake/` → consuming its projection **convention** `profile.model_dump(mode="python")` is
  consuming the already-listed `intake` surface (#1). corpus-generator reuses the convention to build the composite `CorpusRecord`
  projection; `common.canon_ser.content_hash` (surface #5) remains the **single** hasher. The **five-surface** count is preserved.
  Answers the user's check (ii): **not** a sixth surface.

## 9. Settled items held (not re-opened)
Frozen FD (BR-CORP-1..11, five call-only deps, manifest/record/config shapes) + approved `NFR-CORP-*` targets/tiers/folds are the
substrate — patterns/components realize them, re-opening none. **CON-BR1 verification stays `quality-gates`'** (P6 is the own
layered-respect check). **CON-BR2** label authority = `rules-engine`. **No LLM in the label path; no real PII; WIRE-1 untouched.**
Tier-B out-of-band full run; mock PDFs deferred. No other unit started.

## 10. Next step (STOP here)
Fill the four `[Answer]` tags. On your signal I run the mandatory ambiguity-check (surface-and-stop on any genuine gap), then — if
clean — generate **Part 2** (`nfr-design-patterns.md` + `logical-components.md`, validated Mermaid + text alternatives) and re-save
THIS plan file with the filled answers + any resolved folds embedded (standing convention). Then the standardized NFR-Design 2-option
gate. **No NFR-Design artifact is generated until the answers are in and checked.**
