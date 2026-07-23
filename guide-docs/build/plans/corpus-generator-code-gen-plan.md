# Code Generation Plan (Part 1) — `corpus-generator` (U14)

**Phase / Stage**: BUILD → Code Generation — **Part 1 (Planning) + Part 2 (EXECUTED)** (plan-then-generate; five `[Answer]` tags filled = all A)
**Loop position**: `corpus-generator` (U14) — FD ✅ · NFR Requirements ✅ · NFR Design ✅ · Infrastructure Design ✅ **SKIPPED-logged** · **Code Generation ✅ (Part 2 executed; at the 2-option gate).**
**Unit**: U14 `corpus-generator` · **Date**: 2026-07-07 · **Depth**: **COMPREHENSIVE** · owns **CON-BR3**, DATA-1/2/3, FR-PROV-4 · Story **US-PLAT-7**.
**Status**: **Part 2 GENERATED** — `backend/corpus_generator/**` (11 source modules + `build.py` + 12 test modules). Five `[Answer]` tags = **A** (below, §7). Ambiguity-check CLEAN (five realization clarity-folds; §11). **67 corpus tests / 100% own-code coverage; full backend 773 passed / 3 skipped [Docker-gated integration deselected locally; 800 in CI] / 99.80% ≥ 90% QA-6 PASS; frontend Vitest untouched.** STOPPED at the standardized 2-option gate.

Built **ON** the frozen FD (**eleven BR-CORP rules**, **four folds**, **five call-only dependencies** incl. `common.canon_ser`), the
approved **NFR Requirements** (**eleven `NFR-CORP-*` targets**, tiers **U/S/B**, folds **NFR-1/NFR-2**), and the approved **NFR Design**
(**8 patterns P1–P8**, **components C1–C8 + substrate**, **ND-Fold-1/ND-Fold-2**) — **re-opening none**. TDD tests-first, leaf-first,
Python 3.12, mirroring the realized per-unit convention of `database` / `auth_rbac` / `secrets_config`.

---

## 1. What Code-Gen produces (Part 2 preview) — realized per-unit convention

New Python backend package `backend/corpus_generator/` + its co-located test suite; a repo-root `corpus/` output dir is written **only**
by the out-of-band tier-B build (not created at Code-Gen). Proposed file tree:

```text
backend/corpus_generator/
  __init__.py
  config.py                     # C1 GenerationConfig (frozen Pydantic value object)
  records.py                    # CorpusRecord + CorpusManifest (frozen Pydantic output records)
  exceptions.py                 # CorpusGenerationError -> BudgetExhaustedError, SkewAuditError
  profile_factory.py            # C2 ProfileFactory (seeded; uses intake.derivations + intake.schema)
  labeling_oracle.py            # C3 LabelingOracle (wraps rules_engine.evaluate, call-only)
  rejection_sampler.py          # C4 RejectionSampler (pre-flight + runtime guards; threaded Random)
  skew_audit.py                 # C5 SkewAudit (two independent sub-checks, AND-ed at top)
  document_text_generator.py    # C6 DocumentTextGenerator (INJECTED LLMClient seam)
  manifest_builder.py           # C7 CorpusManifestBuilder / FreezeAdapter (canon_ser hash; intake projection)
  generator.py                  # C8 CorpusGenerator orchestrator (+ tier-S smoke entrypoint)
  build.py                      # tier-B OUT-OF-BAND entrypoint (real google-genai LLMClient wiring + GEMINI_API_KEY) — OMITTED from unit cov
  tests/
    __init__.py
    conftest.py                 # seeded fixtures, capturing LLM double, test-scoped config, synthetic distributions
    test_config.py
    test_records.py
    test_exceptions.py
    test_profile_factory.py     # DET-1, PROFILE-1, SEGREGATION-1
    test_labeling_oracle.py     # LABEL-1
    test_rejection_sampler.py   # BOUND-1 (pre-flight + runtime)
    test_skew_audit.py          # SKEW-BAND-1 + SKEW-EDGE-1 (independence)
    test_manifest_builder.py    # FREEZE-1 + HASH-1
    test_generator.py           # DET-1 (2-run byte-identity), LABEL-1 (all records), FREEZE-1, tier-S smoke
    test_reference_not_own.py   # REFNOTOWN-1 (AST scan + non-vacuous self-test) + DET-1 clock/random-absence
    test_pii.py                 # PII-1 (governance note + light structural)
```

`corpus/profiles.json` + `corpus/manifest.json` are **frozen output data** written by `build.py` at tier B — not authored at Code-Gen.

---

## 2. Component → module map (C1–C8 + exceptions + substrate → files)

| Component (NFR-Design) | Module | Realizes | Key holds |
|---|---|---|---|
| **C1 `GenerationConfig`** | `config.py` | DET-1 seed source; single source of `(target_split, tolerance_pp)` (ND-Fold-1) | frozen value object; `seed`, `target_split` `{APPROVE 0.40, REFER 0.35, "DECLINE-RECOMMEND" 0.25}`, `tolerance_pp=3`, `attempt_budget`, `min_profiles=300`, `rulebook_version`, `model_id` |
| **`CorpusRecord` / `CorpusManifest`** | `records.py` | the frozen output records (FD §4/§5) | `extra="forbid"`; `label`/`intended_class` are `Recommendation`; `profile` is `intake.ApplicantProfile` |
| **exception taxonomy** | `exceptions.py` | Q1-A NFR-Design §10 | `CorpusGenerationError` base → `BudgetExhaustedError` (P3), `SkewAuditError` (P4) |
| **C2 `ProfileFactory`** | `profile_factory.py` | DET-1, PROFILE-1, SEGREGATION-1 (demographic-independent source) | seeded `Random` + seeded `Faker`; derives via `intake.derivations`; synthetic `application_id`; segregated `Demographics` |
| **C3 `LabelingOracle`** | `labeling_oracle.py` | LABEL-1 | thin call-only wrapper over `rules_engine.RulesEngine.evaluate(...).recommendation`; no rule logic |
| **C4 `RejectionSampler`** | `rejection_sampler.py` | BOUND-1 | pre-flight feasibility guard (band lower-edge count `> attempt_budget` → `BudgetExhaustedError`, seed-independent) + runtime exhaustion guard (same exception); bounded loop |
| **C5 `SkewAudit`** | `skew_audit.py` | SKEW-BAND-1 + SKEW-EDGE-1 | `band_ok` (±3pp, reads C1's band) AND `edges_ok` (checklist) — **AND-ed only at top, never blended**; raises `SkewAuditError` |
| **C6 `DocumentTextGenerator`** | `document_text_generator.py` | FR-PROV-4, PII-1 | drives the **injected** `memo_agent_core.provider.LLMClient` seam; `temperature=0` central in `GeminiAdapter`; unit-covered with a capturing double |
| **C7 `CorpusManifestBuilder`/`FreezeAdapter`** | `manifest_builder.py` | FREEZE-1 + HASH-1 | `content_hash = common.canon_ser.content_hash(<list of {profile: profile.model_dump(mode="python"), label, edge_case_tags, documents_text}>)`; single `rulebook_version`; explicit include/exclude field-set |
| **C8 `CorpusGenerator`** | `generator.py` | DET-1 + all (composition) | drives construct→derive→label→sample→gate→prose→freeze; the tier-S smoke entrypoint |
| **test/structural substrate** | `tests/test_reference_not_own.py`, `tests/test_pii.py` | REFNOTOWN-1, HASH-1 (structural), PII-1 | AST no-local-reimpl scan + non-vacuous self-test; PII light structural |
| **tier-B entrypoint** | `build.py` | tier B (out-of-band) | real google-genai `LLMClient` + `secrets-config` `GEMINI_API_KEY`; **omitted** from unit coverage (Q5) |

---

## 3. TDD test → target map (every `NFR-CORP-*` at its NFR-pinned tier)

| Target | Tier | Test file(s) | Assertion (TDD, test-first) |
|---|---|---|---|
| **DET-1** | U | `test_generator.py`, `test_reference_not_own.py` | (a) **two runs**, same seed → **byte-identical** canonicalized `{profile, label, edge_case_tags}` (via `canon_ser` bytes, **excluding** `documents_text` per Q4/§6.5); (b) **structural** — no `datetime.now`/`date.today`/`time.*`, no unseeded `random.*` in the generation modules; (c) `generation_timestamp` excluded from compared content |
| **LABEL-1** | U | `test_labeling_oracle.py`, `test_generator.py` | for **every** record `record.label == evaluate(record.profile, manifest.rulebook_version).recommendation`; label set only from the oracle; `intended_class` never overrides |
| **BOUND-1** | U | `test_rejection_sampler.py` | (a) **happy path** — satisfiable target within budget → corpus, no raise; (b) **pre-flight pigeonhole guard** — per-class lower-edge count `> attempt_budget` raises `BudgetExhaustedError`, **parametrized over multiple seeds** to assert seed-independence; (c) **runtime-exhaustion guard** — feasible-on-paper config the seeded factory can't satisfy within budget raises `BudgetExhaustedError`; both provably **not a hang** (bounded loop) |
| **SKEW-BAND-1** | U (+B) | `test_skew_audit.py` | synthetic proportions: within band → pass; any class off by >3pp → `SkewAuditError`, **regardless of the edge-checklist state** (band-fail-despite-edges-ok — independence); band computation does not consult the checklist |
| **SKEW-EDGE-1** | U (+B) | `test_skew_audit.py` | synthetic checklist: all edges present → pass; **any one** absent → `SkewAuditError`, **even when the ±3pp band is satisfied** (edges-fail-despite-band-ok — never averaged); enumerated set fixed (thin-file; self-employed/irregular; age 18; age 65; BMI 25.00; BMI 30.00; DTI 40%; single-missing-document) |
| **FREEZE-1** | U | `test_manifest_builder.py`, `test_generator.py` | (a) **one** `rulebook_version` across the run == `manifest.rulebook_version`; (b) **structural** — reading the frozen corpus imports no generator, no LLM client; (c) `content_hash` pins the freeze |
| **HASH-1** | U (+structural) | `test_manifest_builder.py`, `test_reference_not_own.py` | (a) `manifest.content_hash` **reproduces** via `common.canon_ser.content_hash()` over the `{profile: profile.model_dump(mode="python"), label, edge_case_tags, documents_text}` composite list; (b) mutating a **provenance** field (`generation_timestamp`, …) → hash **unchanged**; mutating a **profile/label/tag/prose** field → hash **changes**; (c) **structural** — no local `hashlib`/serialization |
| **SEGREGATION-1** | U | `test_profile_factory.py` | build a profile + a copy differing **only** in `Demographics`; `evaluate` both → **same** `recommendation`; **explicit code comment**: this is corpus-generator's OWN layered-respect check, **NOT** `quality-gates`' bias-swap suite (CON-BR1 verification owner) |
| **REFNOTOWN-1** | U (structural) | `test_reference_not_own.py` | (a) **AST-style scan** across the five surfaces — no local `hashlib`/`canon_ser`, no local age/BMI derivation, no rule-eval, no non-injected temperature literal; (b) **non-vacuous self-test** — a planted synthetic local hasher / local derivation is flagged |
| **PROFILE-1** | U | `test_profile_factory.py` | (a) every profile round-trips through Pydantic (`extra="forbid"`); (b) `age_years_derived == intake.derivations.compute_age(dob, as_of)` and (height/weight present) `bmi_derived == compute_bmi(...)`; (c) `application_id == "corpus-<seed>-<index>"` (Q2) |
| **PII-1** | governance (+ light structural, U) | `test_pii.py` | governance note (synthetic-only) + **light structural** — the generation path reads no external-identifier source and makes no network read (only network = injected Gemini seam at tier B, mocked in CI) |
| **tier-S smoke** | S | `test_generator.py` | offline end-to-end on a **test-scoped `GenerationConfig`** (Q3), LLM **mocked** — exercises factory→derive→label→sample→gate→freeze + a valid manifest + the gate invoked; **never** asserts the real 40/35/25 band or full DATA-2 checklist; never masquerades as a real corpus (Fold NFR-1) |
| **tier-B full run** | B | `build.py` invocation (NOT CI) | the real 300+ corpus (live Gemini via `secrets-config` `GEMINI_API_KEY`), small-batch-validate → full; committed to `corpus/`; documented run instructions, **not a collected pytest test** (Q4) |

---

## 4. Leaf-first build order (TDD tests-first; matches the established convention)

- **Step 0 — Package scaffold**: `backend/corpus_generator/__init__.py` + `tests/__init__.py` + `tests/conftest.py`; add `--cov=backend/corpus_generator` to `pyproject.toml` `[tool.pytest.ini_options].addopts`; add the `build.py` (+ any real-client entrypoint) `omit` to `[tool.coverage.run]` per Q5. Touches no built unit; adds no new production dependency beyond the already-declared Faker + the five frozen seams.
- **Step 1 — C1 `config.py`** (`test_config.py`): frozen `GenerationConfig`; band params single-sourced.
- **Step 2 — `records.py`** (`test_records.py`): `CorpusRecord` + `CorpusManifest` frozen models.
- **Step 3 — `exceptions.py`** (`test_exceptions.py`): `CorpusGenerationError` → `BudgetExhaustedError`, `SkewAuditError`; subclass assertions.
- **Step 4 — C2 `profile_factory.py`** (`test_profile_factory.py`): seeded factory using `intake.derivations` + `intake.schema`; DET-1, PROFILE-1, SEGREGATION-1.
- **Step 5 — C3 `labeling_oracle.py`** (`test_labeling_oracle.py`): call-only `rules_engine.evaluate` wrapper; LABEL-1.
- **Step 6 — C4 `rejection_sampler.py`** (`test_rejection_sampler.py`): pre-flight (band lower-edge, reads C1) + runtime guards; BOUND-1.
- **Step 7 — C5 `skew_audit.py`** (`test_skew_audit.py`): two independent sub-checks AND-ed at top; SKEW-BAND-1 + SKEW-EDGE-1 independence.
- **Step 8 — C6 `document_text_generator.py`** (`test_document_text_generator.py`): injected `LLMClient` seam driven by a capturing double.
- **Step 9 — C7 `manifest_builder.py`** (`test_manifest_builder.py`): `canon_ser.content_hash` over the intake-projection composite; FREEZE-1 + HASH-1.
- **Step 10 — C8 `generator.py`** (`test_generator.py`): orchestrator composing C1–C7; DET-1 2-run byte-identity, LABEL-1 all-records, FREEZE-1, **tier-S smoke**.
- **Step 11 — structural/reference-not-own guards** (`test_reference_not_own.py`, `test_pii.py`): REFNOTOWN-1 AST scan + non-vacuous self-test; DET-1 clock/random-absence; PII-1 light structural.
- **Step 12 — `build.py`** tier-B out-of-band entrypoint (real google-genai `LLMClient` + `GEMINI_API_KEY`); omitted from unit cov; not run in CI.
- **Step 13 — Coverage gate**: full `pytest` run → QA-6 `--cov-fail-under=90` on `backend/corpus_generator`'s own code (tier U + S); confirm no regression of the existing backend suite; `ui-shell` frontend suite untouched.

---

## 5. HOLDS restated (binding through Code-Gen)

- **Reference-not-own** — no production code edited in any of the **five** call-only surfaces: `intake`, `rules-engine`, `memo-agent-core`, `secrets-config`, `common.canon_ser`.
- **No local re-implementation** — no local hasher/serialization (delegate to `common.canon_ser`), no local age/BMI derivation (delegate to `intake.derivations`), no rule-eval (delegate to `rules_engine.evaluate`), no second/non-injected temperature literal.
- **Label authority stays `rules-engine`** — the label is `evaluate(...).recommendation`; **no LLM in the label path** (the injected LLM produces document PROSE only, FR-PROV-4).
- **CON-BR1 verification stays `quality-gates`'** — SEGREGATION-1 is this unit's OWN layered-respect check only (explicit code comment); no bias-swap suite / swap pairs authored here.
- **Zero real PII** — synthetic Faker fields + build-authored Gemini prose over synthetic inputs; the unit finalizes no decision.
- **WIRE-1 untouched**; **tier B never runs in CI**; no other unit started; no LLM run at Code-Gen (the capturing double drives C6 offline).

---

## 6. Coverage / quality gate (QA-6) + suite integration

- **Root pytest integration** — `corpus_generator`'s **tier-U + tier-S** tests fold into the **existing root pytest run** (add `--cov=backend/corpus_generator` to `addopts`), exactly like `secrets_config` / `auth_rbac`. It is a **Python backend addition**, so it joins the single backend pytest suite (currently **733 passed / 3 skipped / 99.76%**).
- **No regression** — the run must keep the existing backend suite green (target: previous total + `corpus_generator`'s new tests, all passing; overall coverage stays ≥ the QA-6 bar). **`ui-shell`'s frontend Vitest suite is a separate runner/tree and is NOT touched** (no `frontend/` change).
- **QA-6 ≥ 90%** on `backend/corpus_generator`'s own counted code at tier U+S (`--cov-fail-under=90`). The tier-B `build.py` real-client entrypoint is **omitted** from unit coverage (Q5), like `pg_repository.py` / the `database` integration modules — all pure-logic C1–C8 modules stay counted and covered (C6 is unit-covered via the injected capturing double).
- **Markers** — tier-U/S tests are ordinary collected tests (no new marker needed if Q4-A). Any decision on a tier-B marker vs a plain non-test entrypoint is Q4.

---

## 7. Clarifying questions (fill each `[Answer]` tag; last option = Other)

Genuine **Code-Gen-only** choices — they do **not** re-open the FD, the `NFR-CORP-*` targets, the patterns/components, or the folds.

### Question 1 — On-disk serialization format of the frozen corpus (`corpus/profiles.json` + `corpus/manifest.json`)
How are the frozen files written, and how does that relate to the `content_hash`?
A) **`corpus/profiles.json`** = a single JSON **array** of `CorpusRecord` objects; **`corpus/manifest.json`** = the one `CorpusManifest`
   object. Files are written human-readably (`indent=2`, UTF-8, `Decimal`-as-string, sorted keys) via Pydantic `model_dump`/`json.dumps`.
   **Decoupled from the hash**: `content_hash` is computed over `common.canon_ser` **bytes** of the canonicalized composite (not the
   pretty-printed file bytes), so file readability never affects hash stability. **Recommended.**
B) **Per-record files** under `corpus/profiles/<application_id>.json` + `corpus/manifest.json`.
C) Other.

[Answer]: A

### Question 2 — Deterministic synthetic `application_id` format confirmation
Confirm the exact id string (verified valid against `intake.schema.ApplicantProfile` at Part 2).
A) **`application_id = f"corpus-{seed}-{index}"`**, `index` = **0-based** sequential position over **KEPT** records (not attempts),
   plain decimal (no zero-padding), matching FD BR-CORP-9. **Recommended.**
B) Zero-padded index and/or an embedded class tag (e.g. `corpus-<seed>-<class>-<index>`).
C) Other.

[Answer]: A

### Question 3 — Tier-S test-scoped `GenerationConfig` values (Fold NFR-1)
How are the tiny-N smoke config values chosen so the pipeline + gate are exercised without asserting the real band?
A) A dedicated `test_scoped_config()` fixture in `conftest.py` with a **small `min_profiles`** (e.g. 9), an `attempt_budget`
   generously above the pigeonhole bound, and a **satisfiable target/edge-subset** sized to what the tiny N can meet — asserts wiring +
   a valid manifest + the gate invoked, **never** the real 40/35/25 band or full DATA-2 checklist. `min_profiles=300` governs the real
   tier-B corpus only. **Recommended.**
B) Reuse the real config with only `min_profiles` lowered.
C) Other.

[Answer]: A

### Question 4 — Test integration into the root pytest run + tier-B handling
Do `corpus_generator`'s tests join the root run, and does tier B need a marker?
A) **Tier-U + tier-S fold into the ROOT pytest run** (`--cov=backend/corpus_generator` in `addopts`), like `secrets_config`/`auth_rbac`.
   **Tier B is NOT a collected pytest test** — it's the standalone out-of-band `build.py` entrypoint (real Gemini, heavy full corpus),
   invoked manually / in a dedicated build job, **never in CI**; so **no new marker is needed** (the CI-safe end-to-end assertion is
   tier-S with the LLM mocked, already collected). **Recommended.**
B) Add a new deselected-by-default marker (e.g. `corpus_build`) for a tier-B pytest test.
C) Other.

[Answer]: A

### Question 5 — Coverage omit for the tier-B real-client entrypoint
Which module(s), if any, are omitted from unit coverage (paralleling `pg_repository.py` / the `database` integration modules)?
A) **Omit `*/corpus_generator/build.py`** (the real google-genai `LLMClient` + `GEMINI_API_KEY` wiring + full-corpus run) from
   `[tool.coverage.run].omit` — exercised only out-of-band, like `pg_repository.py`. **All** pure-logic modules (C1–C8 core,
   `exceptions`, `records`, `skew_audit`, `rejection_sampler`, `profile_factory`, `manifest_builder`, `document_text_generator` with the
   injected double) stay **counted and unit-covered to ≥90%**. **Recommended.**
B) No omit — count everything (would force live-Gemini wiring into unit coverage).
C) Other.

[Answer]: A

---

## 8. Carried folds (referenced, not re-derived)
FD **Fold 1** (bounded rejection-sampling) · **Fold 2** (band AND edge, independent) · **Fold 3** (engine label authority / termination)
· **Fold 4** (single `rulebook_version`). NFR **Fold NFR-1** (tier S = wiring smoke, test-scoped config) · **Fold NFR-2** (pigeonhole
seed-independent raise). NFR-Design **ND-Fold-1** (shared band arithmetic; pre-flight uses the band LOWER EDGE from C1's single
`(target_split, tolerance_pp)`) · **ND-Fold-2** (`CanonSerAdapter` is part of the `intake` surface; five-surface count preserved;
`common.canon_ser` is the single hasher).

## 9. Settled items held (not re-opened)
Frozen FD (BR-CORP-1..11, five call-only deps, manifest/record/config shapes) + approved `NFR-CORP-*` targets/tiers/folds + approved
patterns/components are the substrate — Code-Gen realizes them, re-opening none. **CON-BR1 verification stays `quality-gates`'.**
**CON-BR2** label authority = `rules-engine`. **No LLM in the label path; no real PII; WIRE-1 untouched.** Tier-B out-of-band full run;
mock PDFs deferred. No other unit started.

## 10. Next step (STOP here)
Fill the five `[Answer]` tags. On your signal I run the mandatory ambiguity-check (surface-and-stop on any genuine gap), then — if clean
— generate **Part 2** (TDD tests-first, leaf-first: `backend/corpus_generator/**` + the co-located test suite), run the full backend
pytest suite + QA-6 coverage gate, write `guide-docs/build/corpus-generator/code/code-summary.md`, and re-save THIS plan file with the
filled answers + any resolved folds embedded (standing convention). Then the standardized Code-Gen 2-option gate. **No code is generated
until the answers are in and checked.**

---

## 11. Ambiguity-check result + Part 2 execution (2026-07-07) — CLEAN, five realization clarity-folds

The mandatory ambiguity-check ran against the five `[Answer]: A` tags + the frozen FD (11 BR-CORP, 4 folds, 5 call-only deps) + the
approved NFR Requirements (11 `NFR-CORP-*`, folds NFR-1/NFR-2) + the approved NFR Design (P1–P8, C1–C8, ND-Fold-1/ND-Fold-2), and the
five call-only surfaces re-read on disk (`intake.schema`/`derivations`/`CanonSerAdapter`, `rules_engine.engine.evaluate`+`report_schema`,
`memo_agent_core.provider.LLMClient`, `secrets_config.settings.GEMINI_API_KEY`, `common.canon_ser.content_hash`). **No genuine gap**
(no user-facing decision that the frozen artifacts + answers + disk don't determine). Five determinate realizations recorded as
**clarity-folds** (no STOP; none re-opens a frozen artifact):

- **CG-Fold-1 — `LabelingOracle` engine construction.** `RulesEngine(RulebookLoader(rulebook_dir), engine_version=...)` built call-only
  (the `audit-store` `ReplayService` pattern); `rulebook_dir` → the repo's `backend/rules_engine/rulebook/`, representative version
  **`1.0.0`**. Reference-not-own preserved (public classes constructed, nothing edited). `GenerationConfig` gains `rulebook_dir` +
  `engine_version` construction seams (operational params, not a semantic re-opening — mirrors rules-engine's injected `engine_version`).
- **CG-Fold-2 — Fixed clock-free `_AS_OF_ANCHOR`** (`date(2026,1,1)`) for age derivation — never `date.today()`; DET-1 held; a factory
  constant, `GenerationConfig` frozen shape unchanged.
- **CG-Fold-3 — Injected `generation_timestamp`** into `build_manifest`/`generate` (fixed in tests; `datetime.now(UTC)` only in the
  coverage-omitted `build.py`); the generation path is clock-free (BR-CORP-1), mirroring the injected `engine_version`.
- **CG-Fold-4 — Single central prose temperature** `document_text_generator._PROSE_TEMPERATURE = 0`, passed as a Name (not a literal) to
  the injected `LLMClient.generate` — "the injected seam's central one" REFNOTOWN-1 explicitly permits (`complete()` NOT reused, Q2).
- **CG-Fold-5 — `required_edge_cases` on `GenerationConfig`** defaults to the fixed 8-item DATA-2 enumeration (SKEW-EDGE-1's "fixed
  enumerated set" for the real corpus); the `test_scoped_config` supplies a satisfiable subset per **Q3-A / Fold NFR-1** (already frozen,
  not a new decision). `documents_text` composite keys are `DocType` value strings so `canon_ser`'s str-key rule holds.

**Part 2 generated** (TDD tests-first, leaf-first, exactly per §4, Steps 0→13): 11 source modules (`config`/`records`/`exceptions`/
`profile_factory`/`labeling_oracle`/`rejection_sampler`/`skew_audit`/`document_text_generator`/`manifest_builder`/`generator` + the
tier-B `build.py`) + `pyproject.toml` (`--cov=backend/corpus_generator` in addopts; `*/corpus_generator/build.py` in `omit`) + 12 test
modules. **Result: 67 corpus tests passed, 100% own-code coverage** (build.py omitted, Q5); **full backend 773 passed / 3 skipped**
(27 Docker-gated `integration` tests deselected locally — Docker not running; **800 passed / 3 skipped in Docker CI** = prior 733 + 67);
**overall 99.80% ≥ 90% (QA-6 PASS)**; **frontend Vitest (ui-shell) untouched.** See `build/corpus-generator/code/code-summary.md`.
