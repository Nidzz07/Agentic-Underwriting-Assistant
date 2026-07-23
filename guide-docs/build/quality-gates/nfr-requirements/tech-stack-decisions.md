# Tech-Stack Decisions — `quality-gates` (U13)

**Stage**: BUILD → NFR Requirements (per-unit) · **Depth**: comprehensive (single verification authority for four blocking gates).
**Unit**: U13 `quality-gates` · **Date**: 2026-07-08. The four blocking verification gates (CON-BR1 bias-swap / CON-BR2·AC-1 reproducibility / QA-3 rule-coverage / AC-5 code-coverage).
**Principle**: name only what makes the `NFR-QG-*` targets **checkable**; consume the frozen surfaces **call-only** (verification only, reference-not-own); **introduce no new dependency**; **no LLM; no real PII; no network**.

---

## Decisions

| # | Decision | Rationale / notes |
|---|---|---|
| **D1** | **Python 3.12 + pytest** (unit tier U/S) | The backend-wide runtime + test runner (already pinned across nine units); the `NFR-QG-*` targets run here, offline, in CI. |
| **D2** | **Tests fold into the ROOT pytest run** — `--cov=backend/quality_gates` joins `addopts` (Q4-A) | The gate tests join the existing backend suite (the 800-passed Docker-CI total = prior 733 + corpus-generator 67); **no separate runner**, **no new dependency**; the frontend Vitest suite is **untouched**. QA-6 ≥90% applies to `backend/quality_gates`'s own code. |
| **D3** | **Injected engine (duck-typed) = `rules_engine.RulesEngine`, ReplayService pattern** | The gates take an **injected engine** (frozen `ReplayService(__init__(self, repository, engine))` pattern — `self._engine.evaluate(...)`). Production runs inject the real engine; tests inject **fakes** (NFR-QG-Fold-1). Call-only, `rules-engine` **not edited** (NFR-QG-REFNOTOWN-1). |
| **D4** | **Injected fake engines — biased + non-deterministic doubles** (Q1-A) | The non-vacuous "teeth" for NFR-QG-BIAS-1 / REPRO-1 / BLOCKING-1: a **biased** fake (recommendation depends on a demographic field) and a **non-deterministic** fake (output varies by run) are **duck-typed test doubles** with their own `.evaluate()`; injected in place of the real engine, so **the real `evaluate()` is never routed through** (NFR-QG-Fold-1). |
| **D5** | **Imported `rules_engine.report.evaluation_output` as the equality projection** | The **single-sourced** projection (the same ReplayService uses) — reproducibility ×10 identity, bias-swap delta, per-rule coverage rows. **No local re-derivation** (QG-Fold-4 / NFR-QG-REFNOTOWN-1). |
| **D6** | **Real `rules_engine.loader.RulebookLoader` for the controlled test rulebook** (Q2-A) | The rule-coverage logic test loads a **small hand-authored 2–3-rule fixture rulebook** from a fixture/temp path via the **real loader** — whose Pydantic `Rulebook` schema **validates the fixture itself** (malformed → `RulebookLoadError`); **no bespoke validation** (NFR-QG-Fold-2). Distinct from production `1.0.0`; thresholds quoted-as-strings, `input_fields` in the financial/medical/lifestyle allowlist. |
| **D7** | **In-memory stub corpus via `CorpusLoader.from_records`** (Q4-A) | Fixtures are **hand-crafted in-memory `CorpusRecord`/profile lists** (tiny, controlled — Faker not required though available). CI passes with **no committed `corpus/`** (NFR-QG-LOADER-1). `corpus_generator.records.CorpusRecord`/`CorpusManifest` imported call-only. |
| **D8** | **`intake.schema.ApplicantProfile`/`Demographics` + `model_copy` for demographic swaps** | The bias-swap suite swaps `{full_name, gender, city}` via `profile.model_copy(update={"demographics": ...})` (frozen-safe — QG-Fold-5); `pincode` asserted absent (NFR-QG-PROXY-1). Call-only, **not edited**. |
| **D9** | **Report determinism via direct Pydantic model equality** (Q3-A) | NFR-QG-EVIDENCE-1 asserts same-inputs → **field-by-field-equal** report objects (provenance/`generated_at` excluded); a light human-readability (readable-JSON) check. **No content-hash step** — the reports are small structured objects (NFR-QG-Fold-3). |
| **D10** | **`coverage_gate` reads `pyproject.toml` via stdlib `tomllib`; % evidence from the coverage data artifact** | COVWIRE-1 asserts `--cov-fail-under` present + ≥90 (structural, stdlib only); COVEVID-1 extracts `measured_pct` from a **fixture coverage-data artifact** (`coverage.json`/`.coverage`) — **separate** code path, informational, **not** an enforcer (QG-Fold-3 / NFR-QG-Fold-3). Binding enforcement stays `pyproject`'s. |
| **D11** | **Structural guards for reference-not-own** (AST/import scan, self-tested) | NFR-QG-REFNOTOWN-1 / BLOCKING-1: a structural check confirms no local rule-eval/hasher/derivation/second-engine in `backend/quality_gates/`, no production edit of a consumed unit, and that gate tests are **collected** (not `skip`/`xfail`); the guard is **non-vacuous** (self-test flags a synthetic local re-implementation). Mirrors the `auth-rbac`/`corpus-generator` no-forbidden-imports mechanism. |
| **D12** | **Package `backend/quality_gates/`** (Q6-A) | The realized per-unit convention (matching `corpus_generator`/`secrets_config`); folds into the root pytest run; auditor evidence reports under a reports output path (exact path a Code-Gen detail). |

---

## Deferred / referenced (not decided here)
- **`audit-store` `ReplayService`** → consumed as a **pattern reference** (load + injected-`evaluate()` + compare `evaluation_output()`), not necessarily imported; **not re-implemented**.
- **The real full-corpus acceptance runs** (bias-swap delta=0 over the actual 300+ corpus, 100% rule coverage over the real rulebook) → **tier-B, out-of-band, not CI, NOT authorized here, not a Code-Gen blocker** (QG-Fold-1 / BR-QG-6).
- **Seeded-outlier determinism** (`outlier-model` seeded reproducibility) → **deferred to `outlier-model` (U18, P2)**; folded into reproducibility when it lands (QG-Fold-4).
- **Concrete stub-corpus contents + evidence-report exact field wording + reports output path** → **Code-Gen** (still deterministic, still human-readable).

**No new dependency** beyond the already-declared backend stack (pytest, coverage, Pydantic v2) + stdlib `tomllib`, and the frozen call-only seams (`rules_engine` `evaluate`/`evaluation_output`/`RulebookLoader`, `corpus_generator` records, `intake` schema, `audit_store` `ReplayService` pattern). **No LLM; no real PII; no network; WIRE-1 untouched.**
