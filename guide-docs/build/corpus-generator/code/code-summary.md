# Code Generation — Summary — `corpus-generator` (U14)

**Stage**: BUILD → Code Generation (Part 2, executed) · build-time synthetic-corpus unit · **Depth**: COMPREHENSIVE
**Unit**: U14 `corpus-generator` · **Date**: 2026-07-07 · owns **CON-BR3**, DATA-1/2/3, FR-PROV-4 · Story **US-PLAT-7**.
**Realized ON** the frozen FD (11 BR-CORP rules, 4 folds, 5 call-only deps incl. `common.canon_ser`), the approved NFR Requirements
(11 `NFR-CORP-*` targets, tiers U/S/B, folds NFR-1/NFR-2), and the approved NFR Design (8 patterns P1–P8, components C1–C8 +
substrate, ND-Fold-1/ND-Fold-2) — **re-opening none**. TDD tests-first, leaf-first, Python 3.12; mirrors the realized per-unit
convention of `database` / `auth_rbac` / `secrets_config`.

---

## 1. Modules generated (`backend/corpus_generator/`)

| Module | Component | Realizes | Notes |
|---|---|---|---|
| `config.py` | **C1** `GenerationConfig` | DET-1 seed source; single band source (ND-Fold-1) | frozen Pydantic value object; `seed` / `target_split` `{APPROVE 0.40, REFER 0.35, "DECLINE-RECOMMEND" 0.25}` (keyed by `Recommendation` value) / `tolerance_pp=3` / `attempt_budget` / `min_profiles=300` / `rulebook_version` / `rulebook_dir` / `engine_version` / `model_id` / `required_edge_cases` (default = the fixed 8-item DATA-2 enumeration) |
| `records.py` | `CorpusRecord` / `CorpusManifest` | frozen output records (FD §4/§5) | `frozen=True`, `extra="forbid"`; `label`/`intended_class` are `Recommendation`; `profile` is `intake.ApplicantProfile` |
| `exceptions.py` | taxonomy | Q1-A / NFR-Design §10 | `CorpusGenerationError` → `BudgetExhaustedError` (P3), `SkewAuditError` (P4) |
| `profile_factory.py` | **C2** `ProfileFactory` | DET-1, PROFILE-1, SEGREGATION-1 | seeded `Random` + seeded `Faker`; derives via `intake.derivations`; synthetic `application_id` = `corpus-<seed>-<index>`; fixed clock-free `_AS_OF_ANCHOR`; segregated `Demographics` seeded-independently; class + edge recipes |
| `labeling_oracle.py` | **C3** `LabelingOracle` | LABEL-1 | thin call-only wrapper over `RulesEngine.evaluate(...).recommendation`; constructs `RulesEngine(RulebookLoader(dir), engine_version=...)` call-only (the ReplayService pattern) |
| `rejection_sampler.py` | **C4** `RejectionSampler` | BOUND-1 | pre-flight feasibility guard (band lower-edge count `> attempt_budget` → `BudgetExhaustedError`, seed-independent) + runtime exhaustion guard (same exception); bounded loop; engine is the authority |
| `skew_audit.py` | **C5** `SkewAudit` | SKEW-BAND-1 + SKEW-EDGE-1 | `band_ok` (±3pp, reads C1's band) **AND** `edges_ok` (checklist) — independent, AND-ed only at the top, never blended; `band_lower_edge_count` = the shared band-lower-edge arithmetic (ND-Fold-1); raises `SkewAuditError` |
| `document_text_generator.py` | **C6** `DocumentTextGenerator` | FR-PROV-4, PII-1 | drives the **injected** `memo_agent_core.provider.LLMClient` seam; single central `_PROSE_TEMPERATURE = 0`; `complete()` NOT reused; unit-covered via a capturing double |
| `manifest_builder.py` | **C7** `CorpusManifestBuilder`/`FreezeAdapter` | FREEZE-1 + HASH-1 | `content_hash = common.canon_ser.content_hash(<[{profile: model_dump("python"), label, edge_case_tags, documents_text}]>)` (single hasher, no local SHA); `determinism_projection` excludes `documents_text`; single `rulebook_version`; `corpus_to_json`/`manifest_to_json` human-readable (Q1-A, decoupled from the hash) |
| `generator.py` | **C8** `CorpusGenerator` | DET-1 + composition | orchestrates construct→derive→label→sample→gate→prose→freeze; ONE `random.Random(seed)` + seeded `Faker`; **injected** `generation_timestamp` (never a clock read); tier-S `smoke()` entrypoint |
| `build.py` | tier-B entrypoint | tier B (out-of-band) | real google-genai `LLMClient` + `secrets_config` `GEMINI_API_KEY`; writes `corpus/profiles.json` + `corpus/manifest.json`; **OMITTED** from unit coverage (Q5); never in CI |

**Test suite** (`backend/corpus_generator/tests/`): `conftest.py` (seeded fixtures, `CapturingLLMClient` offline double, `test_scoped_config` Fold NFR-1, real `oracle`) + 12 test modules.

---

## 2. Test → target map (every `NFR-CORP-*` at its NFR-pinned tier)

| Target | Tier | Test file(s) | Verified |
|---|---|---|---|
| **DET-1** | U | `test_generator.py`, `test_profile_factory.py`, `test_reference_not_own.py` | 2-run byte-identity over `{profile,label,edge_case_tags}` via `canon_ser` (excl. `documents_text`); factory byte-identity; structural clock/unseeded-random absence |
| **LABEL-1** | U | `test_labeling_oracle.py`, `test_generator.py` | every record `label == evaluate(profile, manifest.rulebook_version).recommendation` |
| **BOUND-1** | U | `test_rejection_sampler.py` | happy path; pre-flight pigeonhole raise **parametrized over 5 seeds** (seed-independent); runtime-exhaustion raise; both `BudgetExhaustedError`, bounded (not a hang) |
| **SKEW-BAND-1** | U (+B) | `test_skew_audit.py` | synthetic proportions in/out of band; independence — band fails despite all edges present; band does not consult the checklist |
| **SKEW-EDGE-1** | U (+B) | `test_skew_audit.py` | synthetic checklist; independence — a missing edge fails despite the band being satisfied (never averaged); fixed 8-item set |
| **FREEZE-1** | U | `test_manifest_builder.py`, `test_generator.py` | single `rulebook_version` == manifest's; manifest pins the freeze; all edges present |
| **HASH-1** | U (+structural) | `test_manifest_builder.py`, `test_reference_not_own.py` | hash reproduces via `common.canon_ser.content_hash`; provenance mutation → hash unchanged; content (prose/label/tag) mutation → hash changes; no local `hashlib` |
| **SEGREGATION-1** | U | `test_profile_factory.py` | Demographics-swap → same engine label; **explicit code comment**: OWN layered-respect check, NOT quality-gates' bias-swap suite |
| **REFNOTOWN-1** | U (structural) | `test_reference_not_own.py` | AST scan across the package (no local hasher/derivation/rule-eval/non-central temperature) + **non-vacuous self-test** (planted violations flagged); five surfaces imported call-only |
| **PROFILE-1** | U | `test_profile_factory.py` | Pydantic round-trip; `age_years_derived`/`bmi_derived` equal `intake.derivations`; `application_id == corpus-<seed>-<index>`; boundary-exact BMI 25.00/30.00, age 18/65 |
| **PII-1** | governance (+ structural, U) | `test_pii.py` | governance (synthetic-only) + light structural: no network import, no `os.environ`/`os.getenv` read in the generation path |
| **tier-S smoke** | S | `test_generator.py` | offline end-to-end on `test_scoped_config`, LLM mocked — wiring + valid manifest + **gate invoked** (spy); never asserts the real band (Fold NFR-1) |
| **tier-B full run** | B | `build.py` invocation (NOT CI) | documented `python -m backend.corpus_generator.build`; omitted from coverage; not a collected test (Q4) |

---

## 3. Results

- **corpus_generator suite: 67 passed**; **coverage 100%** on the unit's own code (325 stmts, 0 miss; branch 100%). `build.py` omitted (Q5).
- **Full backend suite: 773 passed / 3 skipped** with the 27 Docker-gated `integration` tests deselected (Docker not running locally; they run + pass in Linux CI). In a Docker-available CI the total is **800 passed / 3 skipped** (prior 733 + 67 new). **No regression.**
- **Overall coverage 99.80% ≥ 90% (QA-6 PASSED)** — up from the prior 99.76%.
- **Frontend Vitest (ui-shell) UNTOUCHED** — zero `frontend/` changes; separate runner/tree.

---

## 4. Realization notes (faithful; no frozen artifact re-opened)

Five determinate Code-Gen realizations, each forced by the frozen artifacts / answers / on-disk surfaces — none a user-facing
decision, none re-opening a frozen artifact (surfaced in the ambiguity-check as clarity-folds, no STOP):

1. **`LabelingOracle` engine construction** — `RulesEngine(RulebookLoader(rulebook_dir), engine_version=...)` built call-only, exactly
   as `audit-store`'s `ReplayService` + the rules-engine tests do; `rulebook_dir` → the repo's `backend/rules_engine/rulebook/`,
   representative version **`1.0.0`**. Reference-not-own preserved (public classes constructed, nothing edited).
2. **Fixed clock-free `_AS_OF_ANCHOR`** (`date(2026,1,1)`) for age derivation — never `date.today()`; DET-1 held; `GenerationConfig`
   frozen shape unchanged (a factory constant, not a config field).
3. **Injected `generation_timestamp`** — passed into `build_manifest` / `generate` (fixed in tests; `datetime.now(UTC)` only in the
   omitted `build.py`), mirroring rules-engine's injected `engine_version`; the generation path is clock-free (BR-CORP-1).
4. **Single central prose temperature** — `document_text_generator._PROSE_TEMPERATURE = 0`, passed as a Name (not a literal) to the
   injected `LLMClient.generate`; this is "the injected seam's central one" REFNOTOWN-1 explicitly permits (`complete()` NOT reused, Q2).
5. **`required_edge_cases` on `GenerationConfig`** — defaults to the fixed 8-item DATA-2 enumeration (the "fixed enumerated set" of
   SKEW-EDGE-1 for the real corpus); the `test_scoped_config` supplies a satisfiable subset per **Q3-A / Fold NFR-1** (already frozen,
   not a new decision). `documents_text` composite keys are `DocType` value strings so `canon_ser`'s str-key rule is satisfied.

## 5. Holds honored (binding through Code-Gen)
- No production code edited in any of the five call-only surfaces (`intake` / `rules_engine` / `memo_agent_core` / `secrets_config` /
  `common.canon_ser`) — REFNOTOWN-1 AST-verified + non-vacuous self-test.
- No local hasher / serialization / derivation / rule-eval / second-or-varying temperature.
- Label authority stays `rules-engine` (`evaluate().recommendation`); **no LLM in the label path** (LLM = document PROSE only, FR-PROV-4).
- SEGREGATION-1 is this unit's OWN layered-respect check only (explicit code comment); **CON-BR1 bias-swap suite stays `quality-gates`'**.
- Zero real PII (Faker + build-authored prose over synthetic inputs); no live LLM call anywhere in the suite (capturing double only).
- **WIRE-1 untouched**; **tier B never runs in CI**; no other unit started; `ui-shell` frontend Vitest suite untouched.
