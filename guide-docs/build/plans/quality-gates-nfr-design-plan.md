# NFR Design Plan (Part 1) — `quality-gates` (U13)

**Phase / Stage**: BUILD → NFR Design, **Part 1 (Planning)** (plan-then-generate; numbered `[Answer]` tags to fill)
**Loop position**: `quality-gates` (U13) — FD ✅ · NFR Requirements ✅ **APPROVED (Continue)** → **NFR Design Part 1 ← here.**
**Unit**: U13 `quality-gates` · **Date**: 2026-07-08 · **Depth**: **COMPREHENSIVE** (confirmed) · **single verification authority** for CON-BR1 / CON-BR2·AC-1 / QA-3 / AC-5 · Stories **US-PLAT-3/4/5/6**.
**Status**: **Four `[Answer]` tags FILLED (all A); ambiguity-check CLEAN (three named checks resolved as folds ND-QG-Fold-1/2/3, §8A); Part 2 GENERATED** (`nfr-design-patterns.md` + `logical-components.md`, each with a 7-rule-validated Mermaid + text alt). This plan re-saved with the filled answers + resolved folds embedded (standing convention). STOPPED at the NFR-Design 2-option gate.

Built **ON** the frozen FD (BR-QG-1..9, the module inventory + the **four evidence-record shapes** `BiasSwapReport`/`ReproducibilityReport`/`RuleCoverageReport`/`CoverageGateReport`, the **`CorpusLoader` boundary**) and the **approved NFR Requirements** (**eleven `NFR-QG-*` targets**, tiers U/S, the **eight FD/NFR folds** — QG-Fold-1..5 + NFR-QG-Fold-1/2/3) — **re-opening none**. Each `NFR-QG-*` target maps to a **named design pattern** + a **logical component**, mirroring the rigor of `rules-engine` / `audit-store` / `memo-agent-core` / `corpus-generator`.

---

## 1. What NFR Design produces (Part 2 preview — NOT generated yet)
- `nfr-design-patterns.md` — the named patterns (each meeting its `NFR-QG-*` target) + a validated **pattern-integration Mermaid** (7-rule + text alt) + a traceability table (no orphan).
- `logical-components.md` — the logical components (responsibility / ownership / reference-not-own check across all consumed surfaces) + a **component→target coverage** table (no orphan) + a validated **component-relationship Mermaid** (7-rule + text alt).

---

## 2. Pattern → target map (every `NFR-QG-*` mapped; no orphan)

| Pattern | Meets target(s) | Mechanism (design, not code) |
|---|---|---|
| **P1 · DemographicSwapInvariancePattern** (+ **AttributionCheck** sub-pattern) | NFR-QG-BIAS-1, NFR-QG-PROXY-1 | swap `{full_name, gender, city}` via `ApplicantProfile.model_copy(update={"demographics": ...})` on otherwise-identical profiles → assert engine `recommendation` unchanged (`delta_count == 0`). **AttributionCheck** sub-pattern varies `occupation`/`income` and reads `evaluation_output()` `rule_results` to attribute any change to the **sanctioned rule** (occupation-risk / affordability), never a demographic proxy; `pincode` asserted N/A. **Teeth** via the injected biased-fake engine (P7). |
| **P2 · RepeatRunIdentityPattern** | NFR-QG-REPRO-1 | run `evaluate(p, v)` **×10** per profile, project each via the **imported `evaluation_output()`**, assert all 10 projections **field-identical** (`reproducibility_pct == 100`). **Teeth** via the injected non-deterministic-fake engine (P7). Seeded-outlier deferred P2 (documented). |
| **P3 · CoverageAccumulationPattern** | NFR-QG-RULECOV-1 | load the rule-ID set via `RulebookLoader.load_rulebook(manifest.rulebook_version)`; iterate `evaluate()` over the corpus; accumulate, per `rule_id`, whether a **definite PASS/FAIL** was observed; `uncovered_rule_ids` empty ⇒ `coverage_pct == 100`. **Teeth** via the controlled fixture rulebook (P3a below) with a deliberately-unexercised rule. |
| **P3a · ControlledFixtureRulebookMechanism** (part of P3) | NFR-QG-RULECOV-1 teeth | a small hand-authored 2–3-rule YAML loaded via the **real `RulebookLoader`** (its Pydantic `Rulebook` schema **is** the validator — NFR-QG-Fold-2; **no bespoke validator**); distinct from production `1.0.0`. |
| **P4 · StructuralWiringMetaAssertionPattern** | NFR-QG-COVWIRE-1 | read `pyproject.toml` via stdlib **`tomllib`**; assert `addopts` contains `--cov-fail-under` present **and** value ≥ 90 (`wiring_present and fail_under_configured >= 90`). The **binding** gate's wiring check — **not** an enforcer. |
| **P5 · CoverageEvidenceExtractionPattern** | NFR-QG-COVEVID-1 | read a **fixture coverage-data artifact** (`coverage.json`/`.coverage`), extract + format `measured_pct` into the report — **informational, distinct code path from P4, never conflated** (QG-Fold-3 / NFR-QG-Fold-3). |
| **P6 · CorpusLoaderDualSourcePattern** | NFR-QG-LOADER-1 | `CorpusLoader.from_file(path)` (frozen `corpus/profiles.json` via `CorpusRecord.model_validate`) **or** `from_records(records)` (in-memory stub); `profiles()` / `manifest_version()`. CI green on `from_records` with **no committed `corpus/`**; `from_file` is the tier-B path. |
| **P7 · InjectedEngineSeamPattern** *(cross-cutting enabler)* | enables NFR-QG-BIAS-1 / REPRO-1 / BLOCKING-1 teeth | each engine-driven gate takes an **injected engine** — the frozen `ReplayService(__init__(self, repository, engine))` pattern (`self._engine.evaluate(...)`). Production injects the real `RulesEngine`; tests inject **duck-typed fakes**; the real `evaluate()` is **never routed through** when a fake is injected (NFR-QG-Fold-1). |
| **P8 · NoLocalReimplementationGuardPattern** | NFR-QG-REFNOTOWN-1 | an **AST / import scan** over `backend/quality_gates/` asserting no local rule-eval / hasher / derivation / second engine, no production edit of a consumed unit, and **non-vacuous self-test** (a synthetic local re-implementation is flagged). Mirrors the `auth-rbac` / `corpus-generator` precedent. |
| **P9 · DeterministicReportPattern** | NFR-QG-EVIDENCE-1 | each evidence record is a **pure function of `(corpus, rulebook, engine)`** on a shared base — same inputs → **field-equal** report (Pydantic equality), any `generated_at`/provenance **excluded** from equality; **human-readable** serialization; **no content-hash** step. |
| **(cross-cutting) CollectedBlockingTestConvention** *(pending Q1)* | NFR-QG-BLOCKING-1 | each gate's collected pytest test (positive + negative/teeth) **fails the build** on violation and is **not** `skip`/`xfail`. **Q1 decides**: a **property woven into P1–P5** (recommended) vs a **separate ninth pattern**. |

**No orphan** — all eleven `NFR-QG-*` targets are met (BIAS-1→P1; PROXY-1→P1 sub; REPRO-1→P2; RULECOV-1→P3/P3a; COVWIRE-1→P4; COVEVID-1→P5; LOADER-1→P6; REFNOTOWN-1→P8; EVIDENCE-1→P9; BLOCKING-1→cross-cutting via P1–P5 [Q1]; P7 is the cross-cutting enabler for the teeth of BIAS-1/REPRO-1/BLOCKING-1).

---

## 3. Logical components (responsibility · ownership · reference-not-own)

| Component | Responsibility | Owns / references |
|---|---|---|
| **C1 · CorpusLoader** | dual-source profile supply (`from_file` / `from_records`, `profiles`, `manifest_version`) — the tier-U/S-vs-tier-B seam | **owns**; **references** `corpus_generator.records.CorpusRecord`/`CorpusManifest` (call-only import) |
| **C2 · InjectedEngine seam** | the injection point for the engine (real `RulesEngine` in prod; duck-typed fakes in test) | **owns** the seam; **references** `rules_engine.RulesEngine.evaluate` (call-only, ReplayService pattern) |
| **C3 · BiasSwapGate** | swap-invariance + attribution check → `BiasSwapReport` | **owns**; **references** `intake.ApplicantProfile`/`Demographics` (`model_copy`), `evaluation_output()` |
| **C4 · ReproducibilityGate** | ×10 identity over `evaluation_output()` → `ReproducibilityReport` | **owns**; **references** `evaluation_output()` (imported projection) |
| **C5 · RuleCoverageGate** | coverage accumulation over the `RulebookLoader`-loaded rule set → `RuleCoverageReport` | **owns**; **references** `rules_engine.loader.RulebookLoader` (real loader; P3a) |
| **C6 · CoverageWiringGate** | structural `pyproject --cov-fail-under=90` wiring meta-assertion (tomllib) → `CoverageGateReport` (wiring fields) | **owns**; **references** `pyproject.toml` (read-only) |
| **C7 · CoverageEvidenceGate** | coverage-% extraction from the fixture coverage-data artifact → `CoverageGateReport` (`measured_pct`) | **owns**; **references** a coverage-data artifact (read-only). **Distinct producer from C6 — same report shape, never conflated** |
| **C8 · EvidenceReportBase** | the shared report base (common `passed`, provenance stamp excluded-from-equality, readable serialization) the four report models extend | **owns** (P9) |
| **C9 · StructuralGuard / test substrate** | the reference-not-own AST/import scan (REFNOTOWN-1) + the collected-not-skip/xfail meta-check (BLOCKING-1 structural part); non-vacuous self-test | **owns**; scans `backend/quality_gates/` + the consumed-surface imports |

---

## 4. Reference-not-own check (all consumed surfaces — call-only, none edited)

| Surface | How consumed | Edited? |
|---|---|---|
| `rules_engine` — `RulesEngine.evaluate`, `report.evaluation_output`, `loader.RulebookLoader` | injected engine (C2) + imported projection (C4) + real loader (C5/P3a) | **No** |
| `corpus_generator` — `CorpusRecord` / `CorpusManifest` | `CorpusLoader` deserialize / accept (C1) | **No** |
| `intake` — `ApplicantProfile` / `Demographics` | `model_copy` demographic swap (C3) | **No** |
| `audit_store` — `ReplayService` | **pattern reference only** (load + injected-`evaluate()` + compare `evaluation_output()`) — not necessarily imported, not re-implemented | **No** |
| `pyproject.toml` — `--cov-fail-under=90` | read-only via `tomllib` (C6) | **No** |

> **Verification only** — no enforcement/definition of CON-BR1/CON-DET-1 (stays `rules-engine`/`outlier-model`); no re-own of memo CON-BR2. No local rule-eval / hasher / derivation / second engine (P8 self-tested).

---

## 5. Component → target coverage (no orphan)

| Target | Component(s) | Pattern(s) |
|---|---|---|
| NFR-QG-BIAS-1 | C3 (+C2) | P1 (+P7) |
| NFR-QG-PROXY-1 | C3 | P1 sub (AttributionCheck) |
| NFR-QG-REPRO-1 | C4 (+C2) | P2 (+P7) |
| NFR-QG-RULECOV-1 | C5 | P3 / P3a |
| NFR-QG-COVWIRE-1 | C6 | P4 |
| NFR-QG-COVEVID-1 | C7 | P5 |
| NFR-QG-LOADER-1 | C1 | P6 |
| NFR-QG-REFNOTOWN-1 | C9 | P8 |
| NFR-QG-EVIDENCE-1 | C8 | P9 |
| NFR-QG-BLOCKING-1 | C3/C4/C5/C6/C7 (+C9 structural) | cross-cutting (Q1) |

All eleven targets covered; C2 (InjectedEngine seam) and C8 (EvidenceReportBase) are shared enablers (not orphans — they realize the teeth + determinism properties across gates).

---

## 6. Mermaid (generated + 7-rule-validated at Part 2 — consistent with the other comprehensive units)
Two diagrams, each with a text alternative, produced in Part 2 (mirroring `corpus-generator` / `audit-store`, which presented their Mermaids in the Part-2 artifacts):
- **pattern-integration** (in `nfr-design-patterns.md`) — CorpusLoader → InjectedEngine seam → the four gates → EvidenceReportBase / collected tests; P4/P5 distinct coverage paths.
- **component-relationship** (in `logical-components.md`) — C1..C9 wiring.
Both validated against the 7 rules (alphanumeric node IDs, every label double-quoted, no forbidden characters, balanced blocks) before write, with a text alternative always included.

---

## 7. Clarifying questions (fill each `[Answer]` tag; last option = Other)

These decide **NFR-Design pattern/component realization** — they do **not** re-open the FD, the BR-QG rules, the eleven `NFR-QG-*` targets, the seven locked answers, or the eight folds.

### Question 1 — BLOCKING-1: cross-cutting property vs a separate ninth pattern
Is the collected-test-with-teeth structure a **property of the four gate patterns**, or its **own pattern**?
A) **Cross-cutting property** — each gate pattern (P1–P5) **includes** its own collected pytest test (positive + negative/teeth), so NFR-QG-BLOCKING-1 is realized **within** those patterns; a light shared **`CollectedBlockingTestConvention`** documents the *not-`skip`/not-`xfail` + collected + fails-on-violation* discipline (and C9 adds a structural meta-check that the gate tests are collected), **without** being a standalone ninth pattern. No genuine separate mechanism is needed. **Recommended.**
B) **A separate ninth pattern** (`BlockingFormPattern`) owning the collected/teeth discipline centrally — heavier, risks duplicating each gate's own test structure.
C) Other.

[Answer]: A

### Question 2 — InjectedEngine seam realization (P7 / C2)
How is the injected engine threaded through the engine-driven gates?
A) **A thin injection point** — each engine-driven gate takes the engine (or an `evaluate` callable) as a **constructor parameter**, mirroring `ReplayService(__init__(self, repository, engine))` exactly; production passes the real `RulesEngine`, tests pass duck-typed fakes. **No wrapper/adapter class** beyond the injection point (duck-typed, Pythonic, matches the frozen precedent). **Recommended.**
B) **A formal `EngineSeam` adapter class** wrapping `RulesEngine` behind an interface — more ceremony than the frozen ReplayService precedent uses.
C) Other.

[Answer]: A

### Question 3 — EvidenceReportBase: shared base vs independent report models (P9 / C8)
How do the four evidence-record shapes get their determinism/human-readability property?
A) **A shared `EvidenceReportBase`** (common `passed` + an excluded-from-equality provenance stamp + a readable serialization) that `BiasSwapReport` / `ReproducibilityReport` / `RuleCoverageReport` / `CoverageGateReport` **extend** — determinism + field-equality + provenance-exclusion are properties of the base, inherited once. **Recommended.**
B) **Four fully-independent report models** with the determinism property repeated in each — more duplication, easier to drift.
C) Other.

[Answer]: A

### Question 4 — Structural substrate granularity (C9 / P8)
Where do the structural meta-checks live?
A) **One `StructuralGuard` / test-substrate component (C9)** houses the reference-not-own AST/import scan (REFNOTOWN-1) **and** the collected-not-`skip`/`xfail` meta-check (BLOCKING-1 structural part), **distinct** from `CoverageWiringGate` (C6, which owns the `pyproject` `tomllib` read); each is independently checkable but they share the structural-test substrate + the non-vacuous self-test discipline. **Recommended.**
B) **Fully separate modules** for each structural check with no shared substrate — more scattering, harder to keep the self-test non-vacuous.
C) Other.

[Answer]: A

---

## 8. Carried folds (referenced, not re-derived — the substrate NFR-Design builds on)
**FD folds:** QG-Fold-1 (`CorpusLoader` dual-source) → P6/C1 · QG-Fold-2 (rule-coverage at `manifest.rulebook_version`, definite PASS/FAIL) → P3 · QG-Fold-3 (`coverage_gate` wiring meta-assert + separate % evidence, binding stays `pyproject`'s) → **P4 + P5 distinct** · QG-Fold-4 (imported `evaluation_output()`; outlier deferred P2) → P2/P8 · QG-Fold-5 (`model_copy` swap `{full_name, gender, city}`, proxy over occupation+income, `pincode` N/A) → P1.
**NFR folds:** NFR-QG-Fold-1 (injected-fake isolation — real `evaluate()` never routed through) → **P7/C2** · NFR-QG-Fold-2 (real `RulebookLoader` validates the fixture; no bespoke validator) → **P3a** · NFR-QG-Fold-3 (COVEVID-1 rigor = full; % informational) → **P5**.

### 8A. Newly-resolved NFR-Design folds (ambiguity-check — three named checks CLEAN, no genuine gap, no STOP)

Ran against the four answers (all A) + the frozen FD + approved NFR-Req + the patterns. No user-facing decision the substrate + answers don't determine. Three determinate realizations:

- **ND-QG-Fold-1 — the shared `EvidenceReportBase` does NOT couple `CoverageGateReport`'s dual-producer nature** *(check i)*: `EvidenceReportBase` (C8) carries **only** cross-cutting shape/property concerns (`passed`, an excluded-from-equality provenance stamp, a readable serialization) and **no** coverage/pyproject logic. `CoverageGateReport` extends it, but `passed` is set **solely** by C6's wiring meta-assertion (P4) while `measured_pct` is written **separately** by C7 (P5) and is **informational, excluded from `passed`**. Base concerns are **orthogonal** to which producer writes which fields — the P4/P5 separation (QG-Fold-3) is preserved.
- **ND-QG-Fold-2 — the thin injection point needs no formal Protocol at design level** *(check ii)*: mirroring the frozen `ReplayService(__init__(self, repository, engine))` exactly, the engine is an **untyped constructor parameter** with a **documented duck-typed contract** (`engine.evaluate(profile, rulebook_version) -> report`). A `typing.Protocol` is an **optional Code-Gen nicety**, not a design requirement and not needed to keep the fake contract clear (docstring + single call site suffice, as ReplayService).
- **ND-QG-Fold-3 — C9's BLOCKING-1 meta-check uses static analysis, not pytest internals; no conflict with P8** *(check iii)*: the collected-not-`skip`/`xfail` meta-check is a **static AST/marker scan** of the gate test modules (optionally pytest's **public** `--collect-only`), importing **no** pytest internals. P8's no-local-reimplementation scope is the **five consumed production surfaces**, **orthogonal** to the test framework's own facilities — no conflict.

## 9. Settled items held (not re-opened)
The frozen FD + approved NFR-Req (BR-QG-1..9, the eleven `NFR-QG-*` targets, the four evidence-record shapes, the `CorpusLoader` boundary, the eight folds) is the substrate — NFR-Design builds patterns/components **on** it. **Verification only** — no enforcement/definition of CON-BR1/CON-DET-1; no re-own of memo CON-BR2. **Reference-not-own** — the five surfaces call-only, none edited; injected fakes are duck-typed doubles (P7), never routed through real `evaluate()`. **Registered corpus-gap honored** — every own-logic pattern is tier-U/S over the stub; **tier-B is an external precondition, not a Code-Gen target/blocker**; **the tier-B run is NOT authorized here**. **No LLM; no real PII; no new dependency (stdlib `tomllib` only); WIRE-1 untouched; no other unit started.**

## 10. Next step (STOP here — DONE)
Four answers filled (all A); ambiguity-check **CLEAN** (ND-QG-Fold-1/2/3, §8A); **Part 2 GENERATED** — `guide-docs/build/quality-gates/nfr-design/nfr-design-patterns.md` (P1–P9 + the CollectedBlockingTestConvention, each meeting its `NFR-QG-*` target, §0 folds, §12 pattern-integration Mermaid 7-rule-validated + text alt, §13 traceability no-orphan, §14 Security-Guardrails table) and `logical-components.md` (C1–C9 responsibilities/ownership, §2 reference-not-own across all five surfaces none-edited, §3 component→target coverage no-orphan, §4 component-relationship Mermaid 7-rule-validated + text alt, §5 test substrate). This plan re-saved (standing convention). **STOPPED at the standardized NFR-Design 2-option gate (1. Request Changes / 2. Continue → Infrastructure Design)** — did not advance. **WIRE-1 untouched; tier-B run NOT authorized; no other unit started.**
