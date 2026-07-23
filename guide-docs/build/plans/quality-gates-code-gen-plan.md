# Code Generation Plan (Part 1) — `quality-gates` (U13)

**Phase / Stage**: BUILD → Code Generation, **Part 1 (Planning) ONLY** (plan-then-generate; numbered `[Answer]` tags to fill). **NO code generated at this stage.**
**Loop position**: `quality-gates` (U13) — FD ✅ · NFR Requirements ✅ · NFR Design ✅ · Infrastructure Design **SKIPPED-logged** ✅ → **Code Generation Part 1 ← here** (the **last** stage for this unit).
**Unit**: U13 `quality-gates` · **Date**: 2026-07-08 · **Depth**: COMPREHENSIVE · **single verification authority** for CON-BR1 / CON-BR2·AC-1 / QA-3 / AC-5 · Stories **US-PLAT-3/4/5/6**.
**Status**: **Five `[Answer]` tags FILLED (all A); ambiguity-check CLEAN (three named checks resolved as folds CG-QG-Fold-1/2/3, §8A); Part 2 GENERATED + tests GREEN** — `backend/quality_gates/` (6 source modules + tests); **28 passed / 100% own-code coverage; full backend 801 passed / 3 skipped / 27 deselected local / 99.81% (828/3 CI); ui-shell frontend untouched.** This plan re-saved with the filled answers + resolved folds embedded (standing convention). STOPPED at the Code-Gen 2-option gate.

Built **ON** the frozen FD (BR-QG-1..9, module inventory, the four evidence-record shapes, the `CorpusLoader` boundary) + approved **NFR Requirements** (eleven `NFR-QG-*` targets, tiers U/S) + approved **NFR Design** (patterns P1–P9 + CollectedBlockingTestConvention; components C1–C9; folds QG-Fold-1..5 + NFR-QG-Fold-1/2/3 + ND-QG-Fold-1/2/3) — **re-opening none**. **TDD tests-first, leaf-first**, Python 3.12, mirroring `corpus_generator` / `secrets_config` / `auth_rbac`.

---

## 1. File tree (under `backend/quality_gates/` — realized per-unit convention)

```text
backend/quality_gates/
├── __init__.py
├── reports.py                 # C8 EvidenceReportBase + BiasSwapReport / ReproducibilityReport / RuleCoverageReport / CoverageGateReport
├── corpus_loader.py           # C1 CorpusLoader (from_file / from_records / profiles / manifest_version)
├── bias_swap_suite.py         # C3 BiasSwapGate (swap-invariance + AttributionCheck sub) -> BiasSwapReport
├── reproducibility_suite.py   # C4 ReproducibilityGate (x10 identity over evaluation_output) -> ReproducibilityReport
├── rule_coverage_report.py    # C5 RuleCoverageGate (coverage accumulation over RulebookLoader rule set) -> RuleCoverageReport
├── coverage_gate.py           # C6 CoverageWiringGate + C7 CoverageEvidenceGate (two DISTINCT producers, one report shape)
└── tests/
    ├── __init__.py
    ├── conftest.py            # stub corpus fixtures + injected fake engines (biased / non-deterministic) + fixture builders
    ├── fixtures/
    │   ├── controlled_rulebook/<version>.yaml   # P3a controlled 2-3-rule fixture rulebook (Q3)
    │   └── coverage_sample.json                 # C7 fixture coverage-data artifact (Q2)
    ├── test_reports.py                # EVIDENCE-1
    ├── test_corpus_loader.py          # LOADER-1
    ├── test_bias_swap_suite.py        # BIAS-1 (+ teeth), PROXY-1
    ├── test_reproducibility_suite.py  # REPRO-1 (+ teeth)
    ├── test_rule_coverage_report.py   # RULECOV-1 (+ P3a teeth)
    ├── test_coverage_gate.py          # COVWIRE-1 (+ teeth), COVEVID-1
    ├── test_reference_not_own.py      # REFNOTOWN-1 (C9 — AST/import scan + non-vacuous self-test)
    └── test_blocking_form.py          # BLOCKING-1 (C9 — static collected/not-skip/xfail meta-check)
```

> **C2 InjectedEngine seam** is realized as the **constructor `engine` parameter** on C3/C4/C5 (mirroring `ReplayService(__init__(self, repository, engine))` exactly — ND-QG-Fold-2), **not** a production module (subject to **Q5**). **C9 StructuralGuard** is realized as the two structural **test** modules + a shared scan helper (subject to **Q4**), not counted toward production coverage.

---

## 2. Component → module map

| Component | Module | Realizes |
|---|---|---|
| **C8 EvidenceReportBase** (+ 4 report models) | `reports.py` | P9 (shared base: `passed`, excluded-from-equality provenance stamp, readable serialization); the four frozen report shapes |
| **C1 CorpusLoader** | `corpus_loader.py` | P6 (dual-source `from_file`/`from_records`; imports `corpus_generator.records.CorpusRecord`/`CorpusManifest` call-only) |
| **C2 InjectedEngine seam** | *(constructor param; Q5)* | P7 (duck-typed injected engine; real `RulesEngine` in prod, fakes in test — never routes through real `evaluate()` when faked) |
| **C3 BiasSwapGate** | `bias_swap_suite.py` | P1 (+ AttributionCheck sub); `model_copy` swap `{full_name, gender, city}`; `evaluation_output()` rule_results attribution; `pincode` N/A |
| **C4 ReproducibilityGate** | `reproducibility_suite.py` | P2 (×10 identical imported `evaluation_output()` projection) |
| **C5 RuleCoverageGate** | `rule_coverage_report.py` | P3 (+ P3a); `RulebookLoader.load_rulebook(manifest.rulebook_version)`; definite PASS/FAIL accumulation |
| **C6 CoverageWiringGate** | `coverage_gate.py` | P4 (`tomllib` read of `pyproject`; `--cov-fail-under` present + ≥90; **sets `passed`**) |
| **C7 CoverageEvidenceGate** | `coverage_gate.py` | P5 (fixture coverage-data artifact; `measured_pct` **informational, distinct code path**, never conflated with C6) |
| **C9 StructuralGuard / test substrate** | `tests/test_reference_not_own.py` + `tests/test_blocking_form.py` (+ helper) | P8 (AST/import scan, non-vacuous self-test) + BLOCKING-1 static meta-check |

---

## 3. TDD test → target map (every `NFR-QG-*` at its NFR-pinned tier)

| Target | Test module | Positive | Negative / teeth | Tier |
|---|---|---|---|---|
| **BIAS-1** | `test_bias_swap_suite.py` | real engine over stub → `BiasSwapReport.delta_count == 0`, `passed` | **injected biased-fake engine** (recommendation depends on a demographic field) → `delta_count > 0`, `passed is False` | U |
| **PROXY-1** | `test_bias_swap_suite.py` | vary `occupation`/`income` → change attributable to the sanctioned rule via `evaluation_output()` `rule_results`; demographic swap alone → no change | assert `pincode` **absent** from `ApplicantProfile`/`Demographics` (N/A documented) | U |
| **REPRO-1** | `test_reproducibility_suite.py` | real engine ×10 → identical `evaluation_output()`, `reproducibility_pct == 100`, `passed` | **injected non-deterministic-fake engine** (varies by run) → `reproducibility_pct < 100`, `passed is False` | U |
| **RULECOV-1** | `test_rule_coverage_report.py` | stub exercising every rule of the **P3a controlled rulebook** to a definite PASS/FAIL → `coverage_pct == 100`, `passed` | **P3a controlled rulebook with one deliberately-unexercised rule** (operand absent → `NOT_EVALUATED`) → that rule in `uncovered_rule_ids`, `passed is False` | U |
| **COVWIRE-1** | `test_coverage_gate.py` | **real `pyproject.toml`** → `wiring_present`, `fail_under_configured == 90`, `passed` | fixture `pyproject` with `--cov-fail-under` **absent** or **< 90** → `passed is False` | U (structural) |
| **COVEVID-1** | `test_coverage_gate.py` | **fixture coverage-data artifact** → `CoverageGateReport.measured_pct` extracted, well-formed report | assert `measured_pct` is **informational** (does not set/affect `passed`); **distinct code path** from COVWIRE-1 | U |
| **LOADER-1** | `test_corpus_loader.py` | full gate suite green through `from_records` with **no committed `corpus/`** present | (registered gap) `from_file` exercised only when a tier-B corpus exists; its absence does not fail CI | U/S |
| **REFNOTOWN-1** | `test_reference_not_own.py` | AST/import scan of `backend/quality_gates/` finds **no** local rule-eval/hasher/derivation/second engine, no production edit of a consumed unit | **non-vacuous self-test** — a synthetic planted local re-implementation is flagged | U (structural) |
| **EVIDENCE-1** | `test_reports.py` | two runs on identical inputs → **field-equal** reports (Pydantic equality), provenance/`generated_at` excluded; readable JSON | (determinism) no content-hash step; base holds no gate logic | U |
| **BLOCKING-1** | `test_blocking_form.py` | **static AST/marker scan**: each gate test function is collected and carries **no** `skip`/`xfail` marker / `pytestmark` | woven per-gate (each gate's own teeth test fails on violation); **no pytest internals** imported | U (property + structural) |

**No orphan** — all eleven `NFR-QG-*` targets covered.

---

## 4. Leaf-first build order (TDD tests-first per step)

- **Step 0 — scaffold**: create `backend/quality_gates/__init__.py` + `tests/` scaffolding + `tests/fixtures/`; **add `"--cov=backend/quality_gates"` to `pyproject.toml` `[tool.pytest.ini_options].addopts`** (joining the existing nine `--cov` entries; `--cov-fail-under=90` already present). Touches **no** built unit; the addopts edit is config, not a consumed-surface production edit. *(This makes COVWIRE-1's own gate real: the wiring it asserts is the very `--cov-fail-under=90` line.)*
- **Step 1 — C8 `reports.py`** (leaf, no deps) → `test_reports.py` (EVIDENCE-1).
- **Step 2 — C1 `corpus_loader.py`** (imports `corpus_generator.records` call-only) → `test_corpus_loader.py` (LOADER-1).
- **Step 3 — C2 seam** (constructor-param convention + `conftest.py` fake engines; Q5) — no production module unless Q5-B.
- **Step 4 — C3 `bias_swap_suite.py`** (deps C1 + C2 + C8 + `intake` `model_copy` + `evaluation_output`) → `test_bias_swap_suite.py` (BIAS-1 + PROXY-1).
- **Step 5 — C4 `reproducibility_suite.py`** (deps C1 + C2 + C8 + `evaluation_output`) → `test_reproducibility_suite.py` (REPRO-1).
- **Step 6 — C5 `rule_coverage_report.py`** (deps C1 + C8 + `rules_engine.loader.RulebookLoader`) + P3a fixture rulebook → `test_rule_coverage_report.py` (RULECOV-1).
- **Step 7 — C6 CoverageWiringGate** (`coverage_gate.py`; deps C8 + stdlib `tomllib`) → `test_coverage_gate.py::COVWIRE-1`.
- **Step 8 — C7 CoverageEvidenceGate** (`coverage_gate.py`; deps C8; fixture coverage artifact) → `test_coverage_gate.py::COVEVID-1` (distinct code path).
- **Step 9 — C9 StructuralGuard** (`test_reference_not_own.py` REFNOTOWN-1 + `test_blocking_form.py` BLOCKING-1; scans everything above; Q4).
- **Step 10 — suite / coverage gate**: full root `pytest` run → QA-6 ≥90% on `backend/quality_gates`; confirm no regression (§6).

---

## 5. HOLDS (binding through Code-Gen)
- **No production code edited** in any of the five consumed surfaces — `rules-engine`, `corpus-generator`, `intake`, `audit-store`'s `ReplayService` pattern (reference only), `pyproject.toml` **read-only** by C6. *(The Step-0 `addopts` line is a coverage-scope config addition, not a consumed-surface production edit — the same mechanical addition each prior unit made.)*
- **No local** rule-eval / hasher / derivation / second engine (P8/REFNOTOWN-1, non-vacuous self-test).
- **Verification only** — no enforcement/definition of CON-BR1/CON-DET-1 (stays `rules-engine`/`outlier-model`); no re-own of memo's structural CON-BR2.
- **C6/C7 stay distinct producers** of one `CoverageGateReport`; `passed` from C6's wiring verdict, `measured_pct` from C7 informational — **never conflated** (ND-QG-Fold-1).
- **Injected fakes are duck-typed doubles** that **never route through the real `evaluate()`** (NFR-QG-Fold-1).
- **Zero real PII** (synthetic stub only). **WIRE-1 untouched.** **Tier-B run stays UNAUTHORIZED and out of scope** for this unit's Code-Gen (LOADER-1 proves CI green with no committed `corpus/`).
- **No LLM** anywhere. **No new dependency** (stdlib `tomllib`; pytest/coverage/Pydantic already present).

## 6. Coverage / quality gate
- **QA-6 ≥90%** on `backend/quality_gates`'s own code, folding into the **root** pytest run via the Step-0 `--cov=backend/quality_gates` addition.
- **No regression** — the current backend suite (800 passed / 3 skipped in Docker CI = 733 + 67; or the locally-visible 773 passed / 3 skipped with the 27 Docker-gated integration tests deselected) must stay green; the new quality_gates tests **add** to it. **ui-shell's frontend Vitest suite is untouched** (separate runner/tree).
- No production module needs a coverage `omit` (unlike `corpus_generator/build.py` — this unit has no tier-B/real-client entrypoint). If C2/C9 realization introduces any non-import-covered shim, it is called out at Part 2.

---

## 7. Clarifying questions (fill each `[Answer]` tag; last option = Other — Code-Gen-only choices, re-opening nothing)

### Question 1 — Evidence-report on-disk output path + format (US-PLAT-3/4/5 auditor artifact)
Where/how are the human-readable evidence reports emitted on disk?
A) The report models expose a **readable JSON serialization**; on-disk emission is to a **configurable `output_dir` parameter defaulting to a repo-level `reports/quality_gates/`** (git-ignored), **one JSON file per gate**; the **collected tests assert the in-memory report object** (not a committed on-disk path), keeping CI path-independent. **Recommended.**
B) Emit under `backend/quality_gates/reports/` (inside the package) / a different format (e.g. Markdown). C) Other.

[Answer]: A

### Question 2 — Fixture construction for C6/C7 tests (COVWIRE-1 / COVEVID-1)
How are the wiring and coverage-data fixtures built?
A) **COVWIRE-1**: the positive case reads the **real `pyproject.toml`** (asserts `--cov-fail-under=90` present in the `addopts` list); the teeth cases write a **temp `pyproject.toml`** (`tmp_path`) with `addopts` variants — one **omitting** `--cov-fail-under`, one with `--cov-fail-under=85`. **COVEVID-1**: a **fixture `coverage_sample.json`** in coverage.py's JSON shape (`{"totals": {"percent_covered": <float>, ...}}`) drives `measured_pct` extraction. **Recommended.**
B) A different fixture construction (e.g. parse `.coverage` SQLite directly / mock the coverage API). C) Other.

[Answer]: A

### Question 3 — P3a controlled fixture rulebook YAML shape + rule_ids (RULECOV-1 teeth)
What is the 2–3-rule fixture, and how is one rule left uncovered?
A) A **3-rule** test-scoped YAML (`rulebook_version: "qg-test-0.0.1"`, `content_hash: ""` [loader recomputes], `confidence_bands`) loaded via the **real `RulebookLoader`** (validates: allowlisted `input_fields`, quoted thresholds, operator/threshold shape): `t_dti` (`dti_ratio` `lte` `"0.40"`), `t_age` (`age_years_derived` `gte` `"18"`), and **`t_uncovered`** whose operand is **deliberately absent** in the stub profiles (e.g. a rule on an operand the stub omits → engine returns `NOT_EVALUATED` for every record → uncovered). The positive stub populates the operands `t_dti`/`t_age` need; the teeth stub leaves `t_uncovered`'s operand absent. **Recommended.**
B) A 2-rule fixture / a different uncovered-rule construction. C) Other.

[Answer]: A

### Question 4 — C9 static-scan mechanism (REFNOTOWN-1 + BLOCKING-1)
How does the StructuralGuard scan `backend/quality_gates/`?
A) The **stdlib `ast` module** — parse each source/test module, walk `Import`/`ImportFrom` + `FunctionDef`/`ClassDef` nodes to assert no local rule-eval/hasher/derivation/second-engine (REFNOTOWN-1) and no `skip`/`xfail`/`pytestmark` decorator on gate test functions + they are collected (BLOCKING-1) — **no pytest internals**; mirrors the `auth_rbac`/`corpus_generator` `test_reference_not_own.py` precedent; a planted synthetic re-implementation self-tests non-vacuity. **Recommended.**
B) A lighter **regex/import-string** scan (no full AST). C) Other.

[Answer]: A

### Question 5 — C2 InjectedEngine seam realization (production module vs constructor-param only)
Does the seam get a dedicated production module?
A) **No dedicated module** — the seam is the **constructor `engine` parameter** on C3/C4/C5 with the duck-typed contract (`engine.evaluate(profile, rulebook_version) -> report`) **documented in each gate's docstring** (mirrors `ReplayService` exactly, ND-QG-Fold-2); the fake doubles (biased / non-deterministic) live in `tests/conftest.py`. **No `typing.Protocol`** (deferred nicety, not needed). **Recommended.**
B) A small `engine_seam.py` with a documented `Protocol`/type alias for self-documentation. C) Other.

[Answer]: A

---

## 8. Carried folds (referenced, not re-derived)
QG-Fold-1..5 (CorpusLoader dual-source · rule-coverage at `manifest.rulebook_version` · coverage wiring-meta + separate % evidence · imported `evaluation_output()` + outlier P2 · `model_copy` swap-set) + NFR-QG-Fold-1/2/3 (injected-fake isolation · real-loader-validates-the-fixture · COVEVID rigor full) + ND-QG-Fold-1/2/3 (shared base does not couple dual-producer · no Protocol required · static meta-check not pytest-internals). All map to the modules/tests above.

## 8A. Ambiguity-check resolutions (three named checks CLEAN — folds, no genuine gap, no STOP)
Grounded on the frozen surfaces on disk (engine/report/report_schema/loader/intake schema/rulebook 1.0.0/corpus records) before ruling:
- **CG-QG-Fold-1** *(check i)* — `coverage_gate._extract_fail_under` parses **only** the `--cov-fail-under` token; the Step-0 `--cov=backend/quality_gates` entry is a separate `--cov=` path string **never matched**, so the addopts addition and COVWIRE-1's assertion cannot create a circular/confusing self-reference.
- **CG-QG-Fold-2** *(check ii)* — the "operand absent" applies **only to the teeth stub**: the positive stub populates all three fixture rules' operands → 100% coverage; the teeth stub leaves `height/weight` (hence `bmi_derived`) absent so `T-BMI-UNCOVERED-1` → `NOT_EVALUATED` for every record → uncovered. Two distinct stubs; the operand is never accidentally shared.
- **CG-QG-Fold-3** *(check iii)* — the "auditor read-only artifact" (US-PLAT-3/4/5) **is** realized in Code-Gen: `EvidenceReportBase.emit()` writes readable JSON to a configurable `output_dir` (default repo-level `reports/quality_gates/`), exercised via a `tmp_path` test; the gate-pass tests assert the **in-memory** object for CI path-independence. Real report-file emission is a runtime action, not deferred code.

## 9. Next step (STOP here — DONE)
Five answers filled (all A); ambiguity-check **CLEAN** (CG-QG-Fold-1/2/3); **Part 2 GENERATED + GREEN** — `backend/quality_gates/` (`reports.py` C8, `corpus_loader.py` C1, `bias_swap_suite.py` C3, `reproducibility_suite.py` C4, `rule_coverage_report.py` C5, `coverage_gate.py` C6+C7; C2 = constructor param; C9 = `tests/` structural substrate) + 8 test modules + P3a fixture rulebook + coverage fixture. **28 passed / 100% own-code coverage; full backend 801 passed / 3 skipped / 27 deselected local / 99.81% (828/3 CI); no regression; ui-shell frontend untouched.** Wrote `guide-docs/build/quality-gates/code/code-summary.md`; refreshed `testresults.txt`. Only existing-file edit: `pyproject.toml` addopts += `--cov=backend/quality_gates`. **STOPPED at the standardized Code-Gen 2-option gate (1. Request Changes / 2. Continue to Next Stage)** — did not advance. **WIRE-1 untouched; tier-B run NOT authorized; no other unit started.**
