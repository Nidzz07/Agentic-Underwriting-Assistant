# Functional Design Plan (Part 1) — `corpus-generator` (U14)

**Phase / Stage**: BUILD → Functional Design, **Part 1 (Planning)** (plan-then-generate; `[Answer]` tags **answered & locked** before this file was written)
**Loop position**: `corpus-generator` (U14) — **DISCOVER-carryover CLEAN** (no partial artifact; no `backend/corpus_generator/`; no `corpus/`) → **FD Part 1 ← here.**
**Unit**: U14 `corpus-generator` · **Date**: 2026-07-07 · **Depth**: **COMPREHENSIVE** (user-confirmed) · **Story**: US-PLAT-7 · owns **CON-BR3**, DATA-1/2/3, FR-PROV-4.
**Status**: **Plan written; STOP at this gate for user review. NO FD artifact generated** (`domain-entities.md` / `business-rules.md` / `business-logic-model.md` come in Part 2, on explicit go). No `backend/**` or `corpus/**` code created.

Build-time, seeded, versioned, **skew-audited** synthetic corpus (300+, ~40/35/25), frozen by a manifest. Built **ON** the frozen
contracts of four already-complete units — **consumed call-only / reference-not-own, none edited**. **No decision finalized; the
recommendation LABEL originates in `rules-engine` (CON-BR2), never here; the LLM is used only for build-time document PROSE (FR-PROV-4).**

---

## 1. Scope — owns / builds ON / does NOT own

### 1.1 Owns (CON-BR3 single source)
The **seeded + versioned + skew-audited** synthetic corpus and its **manifest freeze**: profile construction, engine-authoritative
labeling, the **blocking skew-audit gate** (before use), the Gemini build-time document-text path, and the frozen `corpus/` output.
US-PLAT-7 · DATA-1 (300+, ~40/35/25) · DATA-2 (all mandatory edge cases) · DATA-3 (seeded + manifest-versioned + skew-audited).

### 1.2 Builds ON — build-time dependency ledger (all **call-only / reference-not-own; no production code edited**)
| Dependency (built unit) | Consumed surface | Used for | Pattern precedent |
|---|---|---|---|
| **`intake`** | `intake.schema.ApplicantProfile` (+ `Demographics`, enums) **and** `intake.derivations.compute_age` / `compute_bmi` | the profile SHAPE + **single-sourced** derivation of `age_years_derived` / `bmi_derived` (boundary-exact 25.00/30.00, clock-free) — **Q8-A** | consume-a-shape (like every unit importing `report_schema`) + call-only derivation |
| **`rules-engine`** | `RulesEngine.evaluate(profile, rulebook_version) -> RuleResultReport` (+ `report_schema.Recommendation`) | the **label authority** — each profile's class = the engine's `recommendation` (CON-BR2) — **Q1-A** | mirrors audit-store `ReplayService` (evaluate as oracle, not re-implemented) |
| **`memo-agent-core`** | `provider.LLMClient` seam `generate(model, prompt, temperature) -> str` (injected; `temperature=0` central) | build-time **document PROSE** via the primary provider (Gemini) — **Q2-A / FR-PROV-4** | the `GeminiAdapter` injected-client / offline-testable pattern (TEMP0-1) |
| **`secrets-config`** | `GEMINI_API_KEY` | the out-of-band real-generation key (never in tests) — **Q2-A / SEC-3** | secrets single-source |

> **Note the dependency growth (explicit, per user):** the originally-listed deps were `memo-agent-core` + `secrets-config`;
> Q1-A adds **`rules-engine`** (evaluate oracle) and Q8-A adds **`intake`** (derivations only). Total build-time deps =
> **intake + rules-engine + memo-agent-core + secrets-config**, all **complete**, all **consumed call-only / reference-not-own,
> zero production code edited in any of them.**

### 1.3 Does NOT own (reference-not-own boundary — held closed)
- **CON-BR1 verification** (bias-swap delta=0) → **`quality-gates`** (U13). corpus-generator is a **layered-respect** point only:
  it populates the **already-segregated** `Demographics` sub-object (frozen schema: *"Never a rule/feature input"*) seeded-independently,
  and authors **no bias-swap suite and no pre-made swap pairs** (**Q6-A**).
- **The feature vector** (demographic-excluded) → **`outlier-model`** (U18, P2).
- **Rule-coverage / reproducibility verification** → **`quality-gates`** (the corpus is rich enough to *support* those gates; it does not *verify* them).
- **No rule-evaluation LOGIC** re-implemented (consumes `evaluate()`); **no decision finalized**; **no LLM in the label path**
  (LLM = document prose only); **no real PII** (Faker + synthetic prose).

---

## 2. Locked decisions (the eight answered `[Answer]` tags — authoritative; not re-opened at Part 2)

| # | Decision (locked = **A**) | One-line meaning |
|---|---|---|
| **Q1** | Label authority = **construct-to-target + rules-engine verifying oracle**, refined to **bounded rejection-sampling** (see Fold 1) | class = `evaluate(...).recommendation`; intended class is only a generation *target* |
| **Q2** | Build-time Gemini prose via the **reused `LLMClient` seam** (injected, `temperature=0` central, offline-testable) | `complete()` (memo-shaped) is **not** reused |
| **Q3** | corpus-generator **owns a blocking build-time skew-audit gate**: **±3pp band** on ~40/35/25 **+** every DATA-2 edge case present | band and edge-checklist are **independent** conditions |
| **Q4** | **Freeze-and-commit**: corpus + manifest committed; consumers read the frozen artifact, **never re-call Gemini** | reproducibility for consumers despite non-byte-stable LLM text |
| **Q5** | Output = **JSON `ApplicantProfile`-conformant profiles + generated document TEXT**; **mock PDFs DEFERRED** | resolves the Brief §4 vs US-PLAT-7 tension toward text now |
| **Q6** | Demographics **present-but-separable** (already a segregated sub-object); **no bias-swap suite / no swap pairs here** | pairing/swap stays `quality-gates` |
| **Q7** | **Offline-testable** (injected seams; Gemini mocked in CI); full corpus = **out-of-band build invocation** (real key, not CI) | small-batch validate → full corpus (US-PLAT-7) |
| **Q8** | Mint the profile by **reusing `intake.derivations`** (compute_age/compute_bmi) + direct construct + **deterministic synthetic `application_id`** | single-sourced derivation → no age/BMI drift; adds the intake dep |

### 2A. Full question text + filled answers (durable record — self-contained, no chat needed)

> **Standing convention (adopted 2026-07-07):** every plan file embeds its numbered `[Answer]` questions **with the filled
> letter answers** and the resolved **folds** verbatim, so the plan stands as a complete durable record on disk.

**Q1 — Label authority: how is each profile's APPROVE/REFER/DECLINE-RECOMMEND class assigned?**
A) **Construct-to-target + rules-engine as the verifying oracle (hybrid)** — deterministically construct seeded profiles aimed at a
   target class, then run the **frozen rules-engine** on each; its actual recommendation is the stored label, and a mismatch
   (constructed-intent ≠ engine output) forces regeneration. Keeps the corpus label consistent with the one recommendation authority
   (CON-BR2). **Consequence to accept: adds a build-time dependency on `rules-engine`** (built) beyond the originally-listed deps. **Recommended.**
B) Generate-then-classify (pure rejection sampling on engine output — no construction intent).
C) Construct-to-label only, **no** engine run (simplest; risks corpus-label ≠ engine-output drift — not recommended).
**[Answer]: A** *(refined by Fold 1 — the "mismatch forces regeneration" clause is superseded by bounded rejection-sampling)*

**Q2 — Build-time Gemini text seam (document prose)**
A) **Reuse memo-agent-core's `LLMClient` seam** (`generate(model, prompt, temperature)->str`) via an **injected** client —
   `temperature=0` central, model_version recorded in the manifest (FR-PROV-4), offline-testable with a capturing double
   (no network/key in tests). Does **not** reuse `complete()` (memo-shaped, wrong output). **Recommended.**
B) Define a **new build-time text-generation adapter** owned by corpus-generator (own seam, same central-temperature + injected-client discipline).
C) Other.
**[Answer]: A**

**Q3 — Skew-audit ownership + tolerance**
A) **corpus-generator owns a blocking build-time skew-audit gate** — asserts the ~40/35/25 split within a **stated ± tolerance band**
   and that **every DATA-2 edge case is present**, "before use" (CON-BR3/DATA-3); quality-gates later *consumes* the frozen corpus but
   does not re-own this audit. **Recommended.**
B) Delegate the skew-audit to quality-gates (not recommended — CON-BR3 single-sources it here).
**[Answer]: A** — confirmed: **± band = ±3 percentage-points** on the ~40/35/25 split, stated in the manifest; **every DATA-2 mandatory
edge case must be present regardless of the aggregate band** (no edge case is optional or averaged away).

**Q4 — Manifest contents + freeze mechanism**
A) **Freeze-and-commit**: the generated corpus (JSON profiles + document text) is **committed** under `corpus/` and pinned by a
   **manifest** = { seed, corpus_version, provider+model_version, per-class counts, DATA-2 edge-case checklist, profile_count,
   content hash, rulebook_version used for labeling, generation_timestamp (recorded) }. Downstream consumers **read the frozen artifact,
   never re-call Gemini** — so reproducibility holds even though LLM text isn't guaranteed byte-identical across model/time. **Recommended.**
B) Regenerate-on-demand from seed (rejected — LLM text is not byte-stable; would break CON-DET-1 for consumers).
**[Answer]: A**

**Q5 — Corpus output format + mock PDFs**
A) **JSON `ApplicantProfile`-conformant profiles + generated document TEXT**, frozen in `corpus/`; **mock PDF binaries DEFERRED**
   (intake's pdfplumber path is exercised by intake's own fixtures; outlier-model/quality-gates consume structured profiles + text).
   Resolves the Brief §4 "mock PDF" vs US-PLAT-7 "document text" tension toward text now. **Recommended.**
B) Also emit mock PDF documents in this unit now.
**[Answer]: A**

**Q6 — Demographic fields (CON-BR1 layered respect) + bias-swap pairing**
A) Profiles carry demographic identifiers (name/gender/city) as **present-but-separable** fields (so outlier-model can exclude them and
   quality-gates can swap them), with corpus-generator's obligation being only that **demographics never influence the label or
   financial fields**. corpus-generator does **not** author the bias-swap suite or emit pre-made swap pairs — **pairing/swapping stays
   quality-gates'** (CON-BR1 verification owner). **Recommended.**
B) corpus-generator also emits ready-made bias-swap pairs (same financials, swapped demographics) to feed quality-gates.
**[Answer]: A**

**Q7 — Offline testability + small-batch validation**
A) The unit is **offline-testable** — seeded deterministic structured-field generation (Faker) + the **injected** text seam mocked
   (capturing double, no live Gemini in CI, mirroring memo-agent-core TEMP0-1). The **small-batch validation then full corpus**
   (US-PLAT-7) is an **out-of-band build invocation** (real key, not run in CI); tests assert the generator/audit logic, not a live LLM. **Recommended.**
B) Other.
**[Answer]: A**

**Q8 — How does corpus-generator mint a valid `ApplicantProfile` (derived fields + `application_id`) outside the intake gate?**
A) **Reuse intake's derivation functions (reference-not-own), construct the profile directly, mint deterministic synthetic
   `application_id`s** — corpus-generator seeds the *raw* inputs (dob, as_of_date, height, weight, income, …) and calls **intake's
   `derivations` seam** (`compute_age` / `compute_bmi`) to compute `age_years_derived` / `bmi_derived` exactly as intake would
   (no re-implementation → no age/BMI-rounding drift), and assigns seeded IDs like `corpus-<seed>-<index>`. **Consequence to accept:
   adds a build-time dependency on `intake`** (already built) — same call-only, no-edit pattern as Q1's rules-engine oracle. **Recommended.**
B) **Generate raw inputs and run the full intake pipeline** (validation gate + derivation) to emit the profile — maximal fidelity
   (also exercises SEC-2), but heavier and couples corpus generation to the whole intake pipeline, not just derivation.
C) **Re-implement age/BMI derivation inside corpus-generator** — rejected (a second derivation source → drift risk vs intake; violates reference-not-own).
**[Answer]: A**

## 3. Folds (locked; carried into Part 2 as authoritative mechanisms)

- **Fold 1 — Q1 bounded-retry refinement (authoritative Q1 mechanism):** *"bounded rejection-sampling toward per-class quotas under
  a **fixed seeded attempt budget**; a profile is kept if its **engine-label** still needs filling, else discarded; if the budget is
  exhausted before the band is met, the build **fails the skew-audit gate loudly (never loops)**."* Deterministic, seeded, terminating.
- **Fold 2 — (i) ±3pp band vs mandatory edge cases:** the skew-audit is a **conjunction** — (a) each class proportion within **±3pp**
  of 40/35/25 **AND** (b) a DATA-2 **edge-case-presence checklist** (never averaged, never traded against the band). Jointly satisfiable
  at open-N **"300+"** (the free bulk pads each class to band while every edge case is present; N grows if ever needed).
- **Fold 3 — (ii) termination bound:** because the **engine is the label authority**, "intended class" is only a generation target and
  the **stored label is always the engine's output** → generation is bounded rejection-sampling (Fold 1); no infinite loop, gate-fails-loud.
- **Fold 4 — (iii) manifest `rulebook_version` unambiguity:** `evaluate()` takes a single `rulebook_version` semver over an immutable,
  append-only, self-declaring `{version}.yaml`; the manifest records that one semver (+ `engine_version` + provider `model_version`).
  The corpus is labeled against the **current active (representative) rulebook version**; a future production-rulebook version →
  **deliberate, tracked regeneration** (mirrors the replay contract), not silent drift.

---

## 4. Planned FD Part 2 artifacts (structure only — NOT generated yet)

### 4.1 `domain-entities.md` — module / entity inventory (comprehensive)
| Entity / module | Responsibility | Consumes |
|---|---|---|
| **`CorpusGenerator`** (orchestrator) | drives the seeded build: construct → derive → label → rejection-sample under budget → skew-audit gate → prose → freeze | all four deps |
| **`ProfileFactory`** | seeded construction of **raw** inputs (dob, as_of_date, height, weight, income, cover, debt, employment, smoking, occupation, health_flags, documents, demographics) + build a valid `ApplicantProfile` | `intake.derivations`, `intake.schema` |
| **`LabelingOracle`** | wraps `RulesEngine.evaluate(profile, rulebook_version)` → the profile's authoritative `Recommendation` | `rules-engine` |
| **`DocumentTextGenerator`** | build-time salary-slip / bank-statement / medical-questionnaire **prose** via the injected `LLMClient` (Gemini) | `memo-agent-core` seam, `GEMINI_API_KEY` |
| **`SkewAudit`** | the blocking gate: ±3pp band **AND** DATA-2 edge-case checklist | — |
| **`CorpusManifest`** (Pydantic) | the frozen manifest schema (fields in §4.3) | — |
| **`CorpusRecord`** | one corpus row: `ApplicantProfile` + generated document text + engine label + provenance | — |
| **seed / config** | the fixed seed + generation parameters (target split, tolerance, attempt budget, model id) | — |

### 4.2 `business-rules.md` — enforceable rules (draft index for Part 2)
- **BR-CORP-1** Seeded determinism (DET-1): every structured field is a pure function of the fixed seed; no wall-clock / unseeded randomness.
- **BR-CORP-2** Engine label authority (CON-BR2): class = `evaluate(...).recommendation`; corpus-generator assigns no label independently.
- **BR-CORP-3** Bounded rejection-sampling (Fold 1): per-class quotas, fixed seeded attempt budget, discard-if-full, gate-fail-on-exhaustion, never loops.
- **BR-CORP-4** Skew-audit gate (CON-BR3/DATA-3): blocking **before use**; ±3pp band **AND** every DATA-2 edge case present; loud build failure otherwise.
- **BR-CORP-5** Manifest freeze (Q4/DATA-3): corpus + manifest committed; consumers read the frozen artifact, never re-call Gemini.
- **BR-CORP-6** Demographic segregation respect (CON-BR1 layered): demographics seeded-independently into the segregated sub-object; never influence financials/label; **no** bias-swap suite / swap pairs here.
- **BR-CORP-7** Zero real PII: all data synthetic (Faker + Gemini prose); no real identifiers.
- **BR-CORP-8** Reference-not-own build-time deps (Q1/Q2/Q8): the four deps consumed call-only; no production code edited; Gemini path injected + offline-testable (`temperature=0` central; FR-PROV-4 primary=Gemini).
- **BR-CORP-9** Profile validity: every emitted profile is a valid frozen `ApplicantProfile` (`extra="forbid"`), derived fields via `intake.derivations`, deterministic synthetic `application_id`.
- **BR-CORP-10** Boundary: no rule-evaluation logic re-implemented; no decision finalized; no LLM in the label path.
- Plus a **Security-Guardrails** compliance table (Input validation / prompt-injection / read-only-DB / audit-logging = **N/A**; **Secrets management** = referenced (`GEMINI_API_KEY`, SEC-3); **no real PII** = compliant).

### 4.3 `business-logic-model.md` — flow + manifest + boundary + self-check
- The **build-time generation flow** (validated Mermaid + text alt): `seed → ProfileFactory raw inputs → intake.derivations (age/BMI) →
  ApplicantProfile → LabelingOracle (engine) → bounded rejection-sample toward per-class quotas under budget → SkewAudit gate
  (±3pp AND edge checklist) → DocumentTextGenerator (Gemini prose) → freeze corpus + manifest`.
- **Manifest fields** (Q4/Fold 4): `seed`, `corpus_version`, `rulebook_version`, `engine_version`, provider `model_version`,
  per-class counts, tolerance (±3pp), DATA-2 edge-case checklist, `profile_count`, corpus content hash, `generation_timestamp` (recorded).
- **Termination argument** (Fold 1/3); **FD ↔ later-stage boundary** (NFR/Code-Gen: offline test substrate; the out-of-band full-corpus
  run; consumers `outlier-model` + `quality-gates` read the frozen artifact); **consumer/dependency map**; **invariant self-check**
  (CON-BR3, CON-BR1 layered-respect, CON-BR2, DET-1, DATA-1/2/3, FR-PROV-4, no-real-PII, US-PLAT-7 ACs).

---

## 5. Invariant → mechanism coverage (comprehensive; verified no orphan at Part 2)
| Invariant / requirement | Owner here? | Mechanism (Part 2) |
|---|---|---|
| **CON-BR3** seeded + versioned + skew-audited | ✅ single source | BR-CORP-1/4/5 |
| **CON-BR2** engine produces the recommendation | consumes | BR-CORP-2 (label = engine output) |
| **CON-BR1** no demographic proxy | layered-respect (verify = quality-gates) | BR-CORP-6 (segregated demographics; no swap suite here) |
| **CON-DET-1** determinism | ✅ (build-time) | BR-CORP-1/3 (seeded, bounded, clock-free derivations) |
| **DATA-1** 300+, ~40/35/25 | ✅ | BR-CORP-4 (±3pp band) |
| **DATA-2** all mandatory edge cases | ✅ | BR-CORP-4 (edge checklist) |
| **DATA-3** seeded + manifest + skew-audited | ✅ | BR-CORP-1/4/5 |
| **FR-PROV-4** Gemini build-time doc text, frozen | ✅ | BR-CORP-8 + manifest freeze |
| No real PII | ✅ | BR-CORP-7 |
| US-PLAT-7 ACs | ✅ | small-batch→full (Q7), all above |

---

## 6. Proposed layout (plan-level proposal — confirm at the gate)
- Module package: **`backend/corpus_generator/`** (following the realized per-unit convention `backend/<unit>/`, not the design-time
  `services/` sketch in `unit-of-work.md`; consistent with the seven built units).
- Frozen corpus data: **`corpus/`** at repo root (per `unit-of-work.md` line 100) — committed JSON profiles + document text + `manifest.json`.
- (Both are **proposals for your confirmation at this plan gate**, not silent locks.)

## 7. Settled items held (not re-opened)
Frozen `ApplicantProfile` / `Demographics` / `Recommendation` / the `LLMClient` seam / `intake.derivations` / `GEMINI_API_KEY` are the
substrate — consumed, never edited. WIRE-1 untouched (backend build-time unit; no UI). `deploy-config` P2 unchanged. The full production
rulebook (25–40 rules) stays deferred; the corpus labels against the current active rulebook version (Fold 4). No other unit started.

## 8. Next step (STOP here)
Review this plan + the restated locks/folds. On your explicit go I will run **no further ambiguity-check** (already closed) and generate
**Part 2** — `domain-entities.md`, `business-rules.md`, `business-logic-model.md` (validated Mermaid + text alternatives) at comprehensive
depth — then present the FD 2-option completion gate. **No FD artifact is generated until you approve this plan.**
