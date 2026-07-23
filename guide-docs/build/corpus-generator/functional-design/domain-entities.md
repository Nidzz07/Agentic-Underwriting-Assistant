# Domain Entities — `corpus-generator` (U14)

**Stage**: BUILD → Functional Design (per-unit) · build-time synthetic-corpus unit · **Depth**: comprehensive
**Unit**: U14 `corpus-generator` · **Date**: 2026-07-07 · owns **CON-BR3**, DATA-1/2/3, FR-PROV-4 · Story **US-PLAT-7**.
**Scope**: The **build-time** modules that generate a seeded, versioned, **skew-audited** synthetic corpus (300+, ~40/35/25),
frozen by a manifest. A generator unit's "entities" are its **module/record inventory** (names + shapes) plus the **frozen output
records** (corpus profiles + manifest), not a live request path. **Pure Python + Faker + a build-time Gemini prose call.** The unit
**owns no business logic that affects a recommendation** — the LABEL originates in `rules-engine` (CON-BR2); the LLM produces only
document PROSE (FR-PROV-4). It **imports no production code it does not own** — four built units are consumed **call-only /
reference-not-own** (§2).

Built exactly on the **eight locked FD-plan answers (all A)** and the **four folds** in
`guide-docs/build/plans/corpus-generator-functional-design-plan.md` — re-opening none.

---

## 1. The build-time surface (what `corpus-generator` produces)

`corpus-generator` lives at **`backend/corpus_generator/`** (realized per-unit convention) and emits, on an **out-of-band build
invocation**, a **frozen corpus** under repo-root **`corpus/`**:

| Output | Location | Shape |
|---|---|---|
| **Corpus profiles** | `corpus/profiles.json` (or per-record) | a list of **`CorpusRecord`** — each a valid `intake.ApplicantProfile` + generated document text + the engine-assigned label (§5) |
| **Manifest** | `corpus/manifest.json` | one **`CorpusManifest`** — seed + versions + counts + edge-case checklist + content hash (§4) |

Consumers (**`outlier-model`** U18/P2, **`quality-gates`** U13/P1) **read the frozen artifact only** — they never re-invoke the
generator or Gemini (Q4 freeze-and-commit; DET-1 preserved for consumers).

---

## 2. Consumed frozen shapes (reference-not-own — call-only, none edited)

| Consumed surface | From unit | Used for | Answer |
|---|---|---|---|
| `intake.schema.ApplicantProfile` (+ `Demographics`, `DocumentManifest`, enums `EmploymentType`/`SmokingStatus`/`Gender`/`DocType`/`DocStatus`) | `intake` | the profile SHAPE every `CorpusRecord` conforms to | Q5/Q8 |
| `intake.derivations.compute_age(dob, as_of) -> int` · `compute_bmi(height_cm, weight_kg) -> Decimal` | `intake` | **single-sourced** derivation of `age_years_derived` / `bmi_derived` (clock-free, `Decimal`, boundary-exact 25.00/30.00) | Q8 |
| `rules_engine.engine.RulesEngine.evaluate(profile, rulebook_version) -> RuleResultReport` · `rules_engine.report_schema.Recommendation` | `rules-engine` | the **label authority** — the profile's class is `report.recommendation` (CON-BR2) | Q1 |
| `memo_agent_core.provider.LLMClient.generate(model, prompt, temperature) -> str` | `memo-agent-core` | the **injected** build-time Gemini prose seam (`temperature=0` central, offline-testable) | Q2 |
| `GEMINI_API_KEY` (via `secrets-config`) | `secrets-config` | the out-of-band real-generation key (never in tests; SEC-3) | Q2 |
| `common.canon_ser.content_hash(value) -> str` (+ `canon_ser`) | **shared `backend/common/`** (no unit owns it — the shared *location*; audit-store is the spec authority) | the **single** canonical-serialization + `content_hash` implementation the manifest's `content_hash` delegates to (§4, BR-CORP-11) — same status as its other consumers (intake / rules-engine / audit-store / memo-agent-core) | correction |

> **Reference-not-own (binding).** `corpus-generator` **imports these shapes/functions and calls them**; it **re-implements none**,
> **edits none**, and owns **no rule-evaluation logic** and **no LLM label path**. The `evaluate()`-as-oracle pattern mirrors
> audit-store's `ReplayService`.

---

## 3. Module / record inventory (names + shapes; JS-free Python)

| Entity / module | Kind | Responsibility | Consumes |
|---|---|---|---|
| **`GenerationConfig`** | value object (§6) | the fixed seed + generation parameters (target split, ±3pp tolerance, attempt budget, model id, `rulebook_version`) | — |
| **`ProfileFactory`** | module | seeded construction of **raw** inputs → a valid `ApplicantProfile` (derived fields via `intake.derivations`; synthetic `application_id`) | `intake.schema`, `intake.derivations` |
| **`LabelingOracle`** | module | wraps `RulesEngine.evaluate(profile, rulebook_version)` → the profile's authoritative `Recommendation` | `rules-engine` |
| **`DocumentTextGenerator`** | module | build-time salary-slip / bank-statement / medical-questionnaire **prose** via the injected `LLMClient` | `memo-agent-core` seam |
| **`SkewAudit`** | module | the **blocking gate**: **±3pp band on ~40/35/25 AND every DATA-2 edge case present** (conjunction; Fold 2) | — |
| **`CorpusGenerator`** | orchestrator | drives the seeded build: construct → derive → label → **bounded rejection-sample** under budget → skew-audit gate → prose → freeze | all of the above |
| **`CorpusRecord`** | output record (§5) | one corpus row: `ApplicantProfile` + document text + engine label + provenance | — |
| **`CorpusManifest`** | output record (§4) | the frozen manifest (Pydantic; §4) | — |

**Offline testability (Q7)**: `ProfileFactory` (seeded Faker), `LabelingOracle` (real engine, deterministic), and `SkewAudit` are
fully testable with **no network**; `DocumentTextGenerator` takes the `LLMClient` as an **injected** dependency, so a capturing
test double drives it offline (no key, no live Gemini). The **full-corpus generation is an out-of-band build step**, not a CI test.

---

## 4. `CorpusManifest` — the freeze record (Q4 + Fold 4)

The manifest **pins** the frozen corpus so any consumer reads a reproducible artifact and any regeneration is deliberate.

| Field | Type | Meaning |
|---|---|---|
| `seed` | int | the fixed seed driving all structured-field generation (DET-1) |
| `corpus_version` | str | the corpus artifact's own semver/tag |
| `rulebook_version` | str | the **single** `rules-engine` rulebook semver the corpus was **labeled** against (Fold 4) |
| `engine_version` | str | the injected `rules-engine` `engine_version` (build id) used for labeling |
| `provider` | str | the primary provider — `"gemini"` (FR-PROV-4) |
| `model_version` | str | the exact Gemini model id used for document prose |
| `class_counts` | object | `{ APPROVE, REFER, "DECLINE-RECOMMEND" }` → integer counts |
| `class_proportions` | object | the realized proportions (audited within ±3pp of 40/35/25) |
| `tolerance_pp` | number | the band half-width = **3** (percentage-points) |
| `edge_case_checklist` | object | each DATA-2 mandatory edge case → present true/false (**all must be true**) |
| `profile_count` | int | total profiles (≥ 300) |
| `content_hash` | str | SHA-256 via the **shared CANON-SER** — `common.canon_ser.content_hash()` (**not** a re-declared hasher; BR-CORP-11) — over the **canonicalized frozen corpus content**: the structured `CorpusRecord` list (`profile` + `label` + `edge_case_tags` + `documents_text`). The manifest's own **provenance fields are EXCLUDED** (`generation_timestamp`, `content_hash` itself, and the version/count metadata), mirroring CANON-SER **P4** (no volatile fields) and audit-store excluding `engine_version`/timestamp from its replay-equality projection. Document `documents_text` prose is a **JSON-native `str`** to `canon_ser`, so it is canonicalized **in the same pass** as the structured fields — **no separate raw-bytes path, no blended mechanism** |
| `generation_timestamp` | str | recorded provenance timestamp (**recorded, never an input to generation** — DET-1) |

> **Fold 4**: `rulebook_version` is unambiguous — a single semver over an immutable, append-only, self-declaring `{version}.yaml`.
> The corpus is labeled against the **current active (representative) rulebook version**; a future production-rulebook version →
> a **deliberate, tracked regeneration** (mirrors the replay contract), never silent drift.

---

## 5. `CorpusRecord` — one frozen corpus row

| Field | Type | Notes |
|---|---|---|
| `profile` | `intake.ApplicantProfile` | valid, frozen (`extra="forbid"`); derived fields via `intake.derivations`; synthetic `application_id` (`corpus-<seed>-<index>`) |
| `documents_text` | object | generated prose per `DocType` (`salary_slip` / `bank_statement` / `medical_questionnaire`) — Gemini build-time output (frozen) |
| `label` | `Recommendation` | the **engine-assigned** class (`APPROVE` / `REFER` / `DECLINE-RECOMMEND`) — CON-BR2; never assigned independently |
| `intended_class` | `Recommendation` | the generation *target* only (provenance) — **not** authoritative; the stored `label` always wins (Fold 1/3) |
| `edge_case_tags` | list[str] | which DATA-2 edge case(s) this record satisfies (feeds the `SkewAudit` checklist) |

**Demographic separability (Q6 / CON-BR1 layered-respect)**: demographics live in the profile's **already-segregated
`Demographics` sub-object** (frozen schema: *"Never a rule/feature input"*), generated **seeded-independently** and **never**
influencing the financial/medical fields or the `label`. `corpus-generator` authors **no bias-swap suite and no swap pairs** —
pairing/swapping is `quality-gates`' (CON-BR1 verification owner).

---

## 6. `GenerationConfig` — the seeded parameters (DET-1)

| Field | Meaning |
|---|---|
| `seed` | fixed seed for Faker + all sampling (pure function of the seed; no wall-clock, no unseeded randomness) |
| `target_split` | `{ APPROVE: 0.40, REFER: 0.35, "DECLINE-RECOMMEND": 0.25 }` |
| `tolerance_pp` | `3` — the ±3pp band half-width (Q3) |
| `attempt_budget` | the **fixed seeded** maximum generation attempts (Fold 1 termination bound) |
| `min_profiles` | `300` (open upper bound — "300+") |
| `rulebook_version` | the rulebook semver labeling runs against |
| `model_id` | the Gemini model id for prose (recorded in the manifest) |

---

## 7. Boundary — what `corpus-generator` does NOT own

- **No recommendation logic** — the class is the engine's output (CON-BR2); no rule evaluation is re-implemented.
- **No decision finalization** — advisory/consumer artifact only; the human gate is `audit-store`/`ui-approval-gate`.
- **No CON-BR1 verification** — the bias-swap suite (delta=0) is `quality-gates`; corpus-generator only respects segregation.
- **No feature vector** — `outlier-model` (P2) owns the demographic-excluded vector.
- **No rule-coverage / reproducibility verification** — `quality-gates` owns those; the corpus is rich enough to *support* them.
- **No live LLM in tests, no LLM in the label path, no real PII** — Faker + a build-time (mocked-in-CI) Gemini prose call only.
- **No mock PDF binaries** (Q5 — deferred); **no bundler / deploy** concern (backend build-time unit; WIRE-1 untouched).
