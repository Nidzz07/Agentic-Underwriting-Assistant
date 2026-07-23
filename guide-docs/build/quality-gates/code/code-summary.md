# Code Summary — `quality-gates` (U13)

**Stage**: BUILD → Code Generation (per-unit) · the four blocking verification gates · **Depth**: COMPREHENSIVE
**Unit**: U13 `quality-gates` · **Date**: 2026-07-08 · **single verification authority** for CON-BR1 / CON-BR2·AC-1 / QA-3 / AC-5 · Stories **US-PLAT-3/4/5/6**.
**Generated** TDD tests-first, leaf-first, exactly per the approved Code-Gen plan (§4 Steps 0→10), on the five filled answers (all A) + ambiguity-check folds CG-QG-Fold-1/2/3. **Verification only; reference-not-own; no LLM; no real PII; no new dependency (stdlib `tomllib`).**

---

## 1. Modules produced (`backend/quality_gates/`)

| File | Component | Realizes |
|---|---|---|
| `__init__.py` | — | package doc |
| `reports.py` | **C8** EvidenceReportBase + `SwapRecord` + `BiasSwapReport`/`ReproducibilityReport`/`RuleCoverageReport`/`CoverageGateReport` | P9 · EVIDENCE-1 (determinism: provenance is not a model field; readable JSON; `emit()` artifact) |
| `corpus_loader.py` | **C1** CorpusLoader | P6 · LOADER-1 (`from_file`/`from_records`/`profiles`/`manifest_version`; `corpus_generator.records` call-only) |
| `bias_swap_suite.py` | **C3** BiasSwapGate (+ `swapped_demographics`, `changed_rules`) | P1 · BIAS-1 + PROXY-1 (`model_copy` swap `{full_name,gender,city}`; `evaluation_output()` attribution) |
| `reproducibility_suite.py` | **C4** ReproducibilityGate | P2 · REPRO-1 (×10 imported `evaluation_output()` identity) |
| `rule_coverage_report.py` | **C5** RuleCoverageGate | P3 · RULECOV-1 (`RulebookLoader` rule set at `manifest.rulebook_version`; definite PASS/FAIL) |
| `coverage_gate.py` | **C6** CoverageWiringGate + **C7** CoverageEvidenceGate | P4 + P5 · COVWIRE-1 (`tomllib` `--cov-fail-under`≥90, sets `passed`) + COVEVID-1 (fixture coverage `measured_pct`, informational, **distinct path**) |

- **C2 InjectedEngine seam** = the constructor `engine` parameter on C3/C4/C5 (no module — Q5-A; mirrors `ReplayService(__init__(self, repository, engine))`; duck-typed fakes never route through the real `evaluate()`).
- **C9 StructuralGuard** = `tests/_structural.py` (stdlib `ast` scans, Q4-A) + `tests/test_reference_not_own.py` (REFNOTOWN-1) + `tests/test_blocking_form.py` (BLOCKING-1) — in `tests/` (omitted from coverage like every `*/tests/*`).

**Tests** (`backend/quality_gates/tests/`): `conftest.py` (stub corpus + real/fixture engines + biased & non-deterministic duck-typed fakes), `fixtures/controlled_rulebook/qg-test-0.0.1.yaml` (P3a), `fixtures/coverage_sample.json` (C7), 8 test modules.

## 2. Test → target map (all eleven `NFR-QG-*`, positive + teeth, no orphan)

| Target | Positive | Teeth |
|---|---|---|
| BIAS-1 | real engine over stub → `delta_count==0`, `passed` | injected **biased** fake → `delta_count>0`, fail |
| PROXY-1 | occupation change attributes to `OCC-LOWRISK-1` only; demographic-only swap → no rule change | `pincode` asserted absent from schema |
| REPRO-1 | real engine ×10 → 100% identical | injected **non-deterministic** fake → <100%, fail |
| RULECOV-1 | complete stub → 100% over the P3a rulebook | teeth stub (bmi absent) → `T-BMI-UNCOVERED-1` NOT_EVALUATED → uncovered, fail |
| COVWIRE-1 | real `pyproject.toml` → wiring present + `==90`, `passed` | temp pyproject absent / `85` / valueless → fail |
| COVEVID-1 | fixture `coverage_sample.json` → `measured_pct` extracted | asserts distinct path (no pyproject read; wiring fields unset) |
| LOADER-1 | `from_records` green with no committed `corpus/`; `from_file` round-trip | — |
| REFNOTOWN-1 | AST scan of every source module → no local re-implementation | planted `import hashlib` + `def evaluate` flagged |
| EVIDENCE-1 | two runs → field-equal report; readable JSON; `emit()` writes artifact | provenance envelope only at serialize time |
| BLOCKING-1 | gate tests collected + no `skip`/`xfail` marker | planted `@pytest.mark.skip` / `pytestmark` flagged |

## 3. Results

- **`quality_gates`: 28 tests passed · 100% coverage on every own module** (reports/corpus_loader/bias_swap_suite/reproducibility_suite/rule_coverage_report/coverage_gate = 170 stmts, 0 miss) — **QA-6 ≥90% PASSED**.
- **Full backend: 801 passed / 3 skipped / 27 deselected locally (Docker-gated integration deselected) · total coverage 99.81% ≥ 90%.** With Docker (CI): **828 passed / 3 skipped** (800 prior + 28). **No regression** — the 773 prior-local-passing tests all still pass; +28 new.
- **`ui-shell` frontend Vitest suite UNTOUCHED** (zero `frontend/` files changed; separate runner/tree — 47 passed / 100% carried forward).
- **Only edit to an existing file:** `pyproject.toml` `addopts += "--cov=backend/quality_gates"` (coverage-scope config; the `--cov-fail-under=90` line COVWIRE-1 asserts is unchanged — CG-QG-Fold-1: the `--cov=` path entry is orthogonal to the `--cov-fail-under` token).

## 4. Realization notes / folds applied
- **CG-QG-Fold-1** — `_extract_fail_under` parses only the `--cov-fail-under` token; the Step-0 `--cov=backend/quality_gates` entry is never matched (no circular self-reference).
- **CG-QG-Fold-2** — the "operand absent" applies **only to the teeth stub** (bmi absent → `NOT_EVALUATED`); the positive stub populates all three fixture rules → 100%.
- **CG-QG-Fold-3** — the auditor artifact is realized in Code-Gen (`EvidenceReportBase.emit()` → readable JSON, exercised via `tmp_path`); gate-pass tests assert the in-memory object for path-independence. Default `output_dir` = repo-level `reports/quality_gates/` (Q1-A; runtime emission, git-ignored).

## 5. Holds honored
No production code edited in any of the five consumed surfaces (`rules-engine`, `corpus-generator`, `intake`, `audit-store`'s ReplayService pattern [reference only], `pyproject.toml` read-only by C6). No local rule-eval/hasher/derivation/second engine (REFNOTOWN-1 green). Verification-only — no enforcement/definition of CON-BR1/CON-DET-1; no re-own of memo CON-BR2. C6/C7 distinct producers, never conflated. Injected fakes duck-typed, never route through real `evaluate()`. Zero real PII (synthetic stub). No LLM. **WIRE-1 untouched; tier-B run NOT authorized and out of scope.**
