# Code Generation Plan (Part 1) — `llm-judge` (EPIC-6 / U22, Phase 2)

**Phase / Stage**: BUILD → per-unit loop → **Code Generation, Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `llm-judge` (U22) · FD ✅ → NFR Requirements ✅ → NFR Design ✅ → **Infrastructure Design ⏭️ SKIPPED
(logged, rule-justified — the 20th skip)** → **Code Generation ← here (the 5th and LAST of U22's stages)**
**Unit**: U22 · EPIC-6 · **Phase 2** · **Date**: 2026-07-19 · **Depth**: comprehensive (per `execution-plan.md` L202; TDD per QA-6)
**Status**: **ANSWERED (Q1–Q5 all A) · ambiguity-check CLEAN (§6.5) · Part 2 GENERATED.** 114 tests green · `backend/llm_judge` at 100% · backend **1308 passed / 31 skipped / 5 pre-existing Docker errors**.

Built **ON** the frozen FD (`BR-JUDGE-1..11`), the approved **NFR Requirements** (eleven `NFR-JUDGE-*`), the approved
**NFR Design** (`P-JUDGE-1..14` · `C-JUDGE-1..5`) and the **logged Infrastructure Design SKIP** — **re-opening NONE.**

> **⚑ U22's Code Generation is the LAST stage of the entire 23-unit decomposition. Its approval closes the build.**

**Live baseline measured this session (not cited from memory)**: `pytest backend --collect-only` → **1230 tests collected**,
reconciling exactly with the recorded **1194 passed / 31 skipped / 5 pre-existing `audit_store` Docker-absence errors**
(1194 + 31 + 5 = 1230). U22 is **purely additive**; this baseline must not regress.

---

## 1. Component → module map (concrete files under `backend/llm_judge/`)

**Layout is PINNED by the approved NFR Design** (`EXPECTED_PRODUCTION_MODULES = {"rubric.py", "schemas.py", "pipeline.py",
"engine.py"}`) and matches the **measured sibling convention** — flat modules, no subpackages
(`outlier_model`, `memo_extensions`, `observability` all flat).

| Component | Files | Contents |
|---|---|---|
| **C-JUDGE-1** | `backend/llm_judge/schemas.py` · `backend/llm_judge/rubric.py` | `ProviderScopeTag` · `EvalTier` · `RubricDimension` · `GroundednessRubric` · `JudgedSample` · `DimensionScore` · `SampleScore` · `EvalRunResult` — **frozen dataclasses, NO `Recommendation`-typed field anywhere** (P-JUDGE-10: the verdict is *unrepresentable*); `exempt_count` a **required** field (P-JUDGE-1); `dimensions` an **ordered tuple** (P-JUDGE-8 determinism) |
| **C-JUDGE-2** | `backend/llm_judge/pipeline.py` | `partition_by_scope()` · **`is_nonvacuous_exemption_set()`** · `aggregate_sample()` · `run_eval()` |
| **C-JUDGE-3** | `backend/llm_judge/engine.py` | the **`RubricEngine` Protocol** (production). **⚑ `DeclaredScoreEngine` fake NEVER in production** — see **Q1** |
| **C-JUDGE-4** | `backend/llm_judge/tests/fixtures.py` | the **five named families**: `in_gate_samples()` · `exempt_witness_sample()` · **`degenerate_all_in_gate_set()`** (genuinely separate, self-asserting) · **`anchoring_pair()`** (tuple ⇒ unsplittable) · `reference_memo()` |
| **C-JUDGE-5** | `backend/llm_judge/tests/structural.py` + `tests/test_structural_guard.py` | the **six scans**, each with a **detector self-test**; `production_py_files()` **EXCLUDING `tests/`**; `EXPECTED_PRODUCTION_MODULES` non-vacuity guard |

Plus `backend/llm_judge/__init__.py` and `backend/llm_judge/tests/__init__.py` (sibling convention).

### 1.1 Header-comment deliverables — **explicit on ALL FOUR production modules**
Per the standing rule **"header comments document; they never enforce"**, each production module carries a module docstring
stating: *holds no LLM · edits no frozen unit · declares no verdict · reaches no network/Node/npx at tier-U*. **These are
documentation only** — every one of those properties is **independently enforced** by a C-JUDGE-5 scan with a detector
self-test. **No test asserts on docstring text** *(except DISCLOSE-1's token checklist, whose subject is the disclosure
itself — see Q3)*.

---

## 2. TDD test → target map (every `NFR-JUDGE-*` at its NFR-pinned tier)

**TDD per QA-6**: each test is written **before** the production code it exercises, in the leaf-first order of §3.

### The two LOAD-BEARING pairs — **full-highest rigor**

| Target | Pattern | Teeth | Detector self-test |
|---|---|---|---|
| **EXEMPT-1** *(positive)* | **P-JUDGE-1** | over `in_gate_samples() + exempt_witness_sample()` (the **three-sample composition**): `scored_count == 2` **∧** `exempt_count == 1` **∧** the Ollama sample **present in `sample_scores`** | a wrongly-**scored** Ollama sample makes `scored_count` read **`3`** ⇒ fails |
| **EXEMPT-1** *(degenerate guard)* | **P-JUDGE-2** | `is_nonvacuous_exemption_set(degenerate_all_in_gate_set())` is **`False`**; over the three-sample composition it is **`True`** | the builder's **own precondition** `all(s.provider is not ProviderScopeTag.ollama)` fails at construction if an exempt sample ever enters |
| **NOEDIT-1** | **P-JUDGE-3** | authored paths ⊆ `ALLOWED_U22_PREFIXES` **and disjoint from** `FROZEN_PREFIXES` (every frozen `backend/<unit>/` + `backend/app/**`) | a synthetic authored path under a frozen tree **is flagged** |
| **NOMETRIC-1** | **P-JUDGE-4** | **(a) PRIMARY — provenance scan**: no U22 module declares a metric name / `MetricDefinition`. **(b) CORROBORATING — property read**: `len(METRIC_DEFINITIONS) == 5` + the five names by value; `len(panels) == 5` + **no nested `panels` key** + exprs == the frozen five | a synthetic `MetricDefinition(...)` in a U22 module **is flagged** |

**⚑ NOMETRIC-1(b) reads `backend/observability/metrics.py` and `deploy/grafana-dashboard.json` READ-ONLY. NEITHER UNIT'S
SUITE IS RE-RUN** — a static content check (import-to-read ≠ edit). The technique is `deploy_config/tests/test_scope.py`'s,
**reused not reinvented** (ND-Fold-3); the no-nested-`panels` assertion is U22's one addition, so future row-nesting **fails
loudly** rather than silently under-counting.

### The remaining targets

| Target | Teeth |
|---|---|
| **THRESH-1** | **`aggregate == 4` PASSES** and **`aggregate == 3.99` FAILS**, with the **`>=` asserted explicitly**; `gate_passed` over the **in-gate mean** with an exempt sample present and **provably not contributing**; determinism (fixed scores ⇒ byte-reproducible, declared dimension order) |
| **INGATE-1** | over `in_gate_samples()`: `scored_count == 2`, both `in_gate == True`, both in `sample_scores`. **GATE-1 remains `quality-gates`'** — not re-derived |
| **EXEMPTSCOPE-1** | the exempt record carries an explicit reason tag naming ***memo-quality*** as the scope; a scan finds **no "untested"-equivalent** characterization of Ollama in any U22 artifact; U19's decision-level assertions **REFERENCED, never re-derived** |
| **ANCHOR-1** | **honestly scoped per Q2-A**: `anchoring_pair()` returns both **together**; the close sample lands with a **higher `aggregate`** than the divergent one; a **single-fixture-only** configuration is **flagged as insufficient**. **⚑ Proves the paired-fixture PLUMBING and the UNSPLITTABILITY safeguard — NOT engine-side discrimination**, which is a named `PROMPTFOO-CLI-DEFERRED` criterion |
| **CLIDEFER-1** | `assert isinstance(fake, RubricEngine)` **∧** `assert not isinstance(object(), RubricEngine)` (**satisfiable + non-vacuous**, U19's exact assertion). **⚑ NO by-value interop replica** — the pattern's precondition (a frozen on-disk shape to mirror) is **absent**. AST scan: **no production import of the promptfoo shim** (+ detector). Suite passes with **no Node/npx/network/telemetry/key** |
| **EVALDEFER-1** | the suite passes with **tier-B unauthorized and the corpus absent**; `EvalRunResult.tier` reads **`unit`**; **no test reads the real corpus** |
| **DISCLOSE-1** | **token checklist** (U23 DOC-1 lineage): the `FEWSHOT-ANCHOR-UNIMPLEMENTED` name **+ U4 owner attribution + rationale**; **negative assertion** — no discharge claimed. **⚑ ANTI-CONFLATION self-test**: CLIDEFER-1's tokens being present does **NOT** mask removal of DISCLOSE-1's own token, **and vice versa** |
| **NODEMO-1** | demographic-token scan over every U22 artifact **AND `reference_memo()`**; **detector self-test** — a **planted** demographic token **is flagged** |
| **ADVISORY-1 / NOVERDICT-1** | **structural**: no U22 type declares a `Recommendation`/verdict-typed field. **+ token scan** for a bare `APPROVE`/`REFER`/`DECLINE` used as a judge **output** (+ detector). Only `narrative_prose` (the `L` region) judged |
| **PERF-1** | **observed, never gated** — no U22 test asserts a timing failure; U22 owns **no runtime SLO** |
| **SEC-1** | governance — review + the C-JUDGE-5 scans; the three register items **named, owner-attributed, none discharged** |

**No orphan**: all eleven `NFR-JUDGE-*` + PERF-1 + SEC-1 have teeth above.

---

## 3. Leaf-first build order (TDD at each step)

1. **C-JUDGE-1 — the domain model** (`schemas.py`, `rubric.py`). **No dependencies.** Tests first: ADVISORY-1's structural
   no-verdict-field assertion; the `exempt_count`-required and ordered-`dimensions` shape assertions.
2. **C-JUDGE-4 — the fixtures substrate** (`tests/fixtures.py`). Depends on the domain model **and read-only frozen U4
   shapes** (`DecisionMemo`, `RuleResultReport`). The five families, with `degenerate_all_in_gate_set()`'s self-asserting
   precondition and `anchoring_pair()`'s tuple return.
3. **C-JUDGE-3 — the engine seam** (`engine.py` Protocol + the tests-only fake). CLIDEFER-1's satisfiable/non-vacuous teeth
   land here.
4. **C-JUDGE-2 — the eval pipeline** (`pipeline.py`). Depends on 1–3. THRESH-1 · INGATE-1 · EXEMPTSCOPE-1 · EXEMPT-1 (both
   halves) · ANCHOR-1 · EVALDEFER-1 teeth.
5. **C-JUDGE-5 — the StructuralGuard scans** (`tests/structural.py`, `tests/test_structural_guard.py`). **Scans the
   COMPLETED production tree**, so it must come last. NOEDIT-1 · NOMETRIC-1 · CLIDEFER-1's AST half · NODEMO-1 ·
   ADVISORY-1's token half · DISCLOSE-1.
6. **Coverage gate** — add the `--cov` line (Q5), run the full backend suite, confirm no regression.

---

## 4. Coverage / quality gate

- **`--cov=backend/llm_judge`, NO omit** (Q3-A of NFR Requirements, following **`observability`'s precedent verbatim**):
  the deferred halves are **absent modules, not uncovered ones**, so there is nothing to omit.
- **Global `--cov-fail-under=90` UNCHANGED.** U22's own tree expected at **100%**, like its pure-logic siblings.
- **⚑ Stated so the number is not misread**: BR-JUDGE-6/8/9's verification is the **presence/absence scans**, which is
  **orthogonal to line coverage**. A 100% figure must **not** be read as covering them.
- **No regression**: the **1230-test baseline** (1194 passed / 31 skipped / **5 pre-existing `audit_store` Docker errors**)
  must hold, with U22's new tests added on top. **The 5 Docker errors and 31 skips must stay exactly unchanged** — U22 adds
  neither.

---

## 5. Explicit HOLDS

- **No frozen unit edited.** `memo-agent-core`'s `DecisionMemo`/`RuleResultReport`/`PromptBuilder` **read-only**, its **test
  tree never touched**; `memo-extensions`' provider adapters **driven through their existing seam, never edited**
  (`temperature=0` stays centrally fixed **in those frozen adapters**); `observability`'s `METRIC_DEFINITIONS` and
  `deploy-config`'s `grafana-dashboard.json` **read read-only** for the corroborating check — **neither suite re-run**.
- **No new dependency.** `promptfoo` stays **floored**; **no engine import in production**; **`requirements.txt` NOT
  edited**. The only `pyproject.toml` edit is the single `--cov` line (Q5).
- **The three register items disclosed by name, NONE discharged**: `PROMPTFOO-CLI-DEFERRED` · `JUDGE-EVAL-DEFERRED` ·
  `FEWSHOT-ANCHOR-UNIMPLEMENTED`.
- **Untouched**: **WIRE-1** · the **17 frozen P1 units (INCLUDING `memo-agent-core`)** · `outlier-model` (U18) ·
  `memo-extensions` (U19) · `ui-outlier-view` (U20) · `observability` (U21) · `deploy-config` (U23) · the **CLOSED
  composition root** · the **`audit_store` Docker-guard gap** · **no other unit started** · the **23-unit decomposition**.
- **tier-B N/A and NOT authorized.**
- **Domain invariants bind**: advisory-only wording; the judge never alters a recommendation; no LLM in the deterministic
  rules path; no demographic identifier anywhere.

---

## 6. Clarifying questions — fill each `[Answer]:` tag

> **Code-Gen-only choices.** None re-opens a frozen or approved decision. **C/D "Other"** — describe after the tag.

---

### Question 1 — Where does the `DeclaredScoreEngine` fake live?

**⚑ Measured on disk, and it contradicts a parenthetical in my own NFR Design.** `logical-components.md` wrote
*"(`tests/fakes.py`)"* — but **NO unit in the build has a `tests/fakes.py`**. Every fake class lives in that unit's
**`tests/fixtures.py`**: `CapturingThinkingClient`, `FakeDecisionRecordSource`, `FailingDecisionRecordSource`,
`FakeOutlierSignal`, `ByValueOutlierResult` (U19) · `RecordingTraceSink`, `RecordingMetricExporter` (U21).

**A) In `tests/fixtures.py`, alongside the five families — matching the measured convention (RECOMMENDED).**
Zero new files; the fake sits beside the fixtures it echoes scores for; identical to U19/U21. The NFR Design's binding
requirement — **the fake is NEVER in production**, so CLIDEFER-1's scan has a clean production set — is satisfied either
way, since `tests/` is excluded from every production scan. The `fakes.py` parenthetical was **illustrative, not
load-bearing**; following the on-disk convention is the more faithful reading.

**B) A separate `tests/fakes.py`.** *(Available; but it would be the **only** such file in the build, diverging from a
convention every sibling follows, for no gain.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 2 — `sample_id` convention guaranteeing `degenerate_all_in_gate_set()` and `in_gate_samples()` are never identity-equal

Req-Fold-1 requires **distinct `sample_id`s** so the two sets can never be confused. The exact convention is open.

**A) Distinct literal PREFIXES + an explicit disjointness test (RECOMMENDED).**
`in_gate_samples()` → `"ingate-gemini-1"`, `"ingate-claude-1"` · `exempt_witness_sample()` → `"exempt-ollama-1"` ·
`degenerate_all_in_gate_set()` → `"degen-1"`, `"degen-2"` · `anchoring_pair()` → `"anchor-close-1"`,
`"anchor-divergent-1"` · plus a **dedicated test asserting the id sets are DISJOINT** — so the separation is **asserted,
not merely intended**. Fully deterministic (no RNG, no wall-clock — the U18 fixture discipline).

**B) A shared prefix with a numeric offset** (`sample-1..2` vs `sample-3..4`). *(Available; but adjacency invites a future
edit to renumber into a collision, and the ids no longer say what family they belong to.)*

**C) Generated UUIDs.** *(Rejected — non-deterministic, breaking the seeded/fixed-value fixture discipline every prior unit
holds.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 3 — Where do DISCLOSE-1's and CLIDEFER-1's token literals LIVE, and what are they?

DISCLOSE-1 is a **token checklist** (U23 DOC-1 lineage). U23 scanned a real committed deliverable (`deploy/README.md`).
U22's equivalent home is open — and it matters, because the tokens must be **in-tree and scannable** without coupling the
unit's test tree to `guide-docs/`.

**A) A `DEFERRED_REGISTER` constant in `engine.py`, scanned by the checklist test (RECOMMENDED).**
A module-level tuple of records, each carrying **item name · owner · rationale · `discharged: False`**:
`("FEWSHOT-ANCHOR-UNIMPLEMENTED", "memo-agent-core (U4) or a future explicitly-authorized change", <rationale>, False)` ·
`("PROMPTFOO-CLI-DEFERRED", "llm-judge (U22)", <5 discharge criteria>, False)` ·
`("JUDGE-EVAL-DEFERRED", "llm-judge (U22)", <criteria + the one-way prerequisite>, False)`.
**Why**: in-tree, **greppable**, **line-coverable** (so it counts toward the 100% tree), a **structured** subject for the
negative "no discharge claimed" assertion (`discharged is False`, not prose-matching), and it keeps the tokens **out of
`guide-docs/`** so the test tree stays self-contained. **Anti-conflation** is clean: DISCLOSE-1's checklist keys on the
**register name + owner** field, CLIDEFER-1's on the **five discharge criteria** field, and each detector self-test asserts
the other's tokens present do **not** mask its own removal.

**B) A dedicated `backend/llm_judge/register.py` module.** *(Available; but it adds a 5th production module holding only
constants, and `EXPECTED_PRODUCTION_MODULES` is already pinned at four by the approved NFR Design.)*

**C) Module docstrings only (prose, not a constant).** *(Available and closest to U23's doc-scan; but prose-matching is
exactly what DOC-1 avoided — U23 matched **tokens, not headings or prose** — and a docstring is not a structured subject
for the `discharged is False` assertion.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 4 — Test-file organization

**Measured sibling convention**: one test file **per target/concern**, named `test_<concern>.py`, plus `fixtures.py`,
`structural.py`, `test_structural_guard.py`, `__init__.py` (U21 has 12 such files; U19 has 14; U18 has 15).

**A) One test file per target, mirroring the convention (RECOMMENDED).**
`test_threshold.py` (THRESH-1) · `test_ingate.py` (INGATE-1) · **`test_exempt.py`** (EXEMPT-1 **both halves — kept together
so the pair's complementarity is visible in one place, while remaining two distinct mechanisms**) · `test_exempt_scope.py`
(EXEMPTSCOPE-1) · `test_anchor.py` (ANCHOR-1) · `test_clidefer.py` · `test_evaldefer.py` · `test_disclose.py` ·
`test_nodemo.py` · `test_advisory.py` · `test_noedit.py` · `test_nometric.py` · `test_perf_observed.py` (the exact sibling
filename) · `test_governance.py` (SEC-1) · `test_structural_guard.py` (the six scans' detector self-tests) — plus
`fixtures.py` · `structural.py` · `__init__.py`.

**B) Grouped by rigor** (one `test_load_bearing.py` + one `test_standard.py`). *(Rejected — it hides the target→file
mapping every sibling makes obvious, and buries the two load-bearing pairs among others.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 5 — `pyproject.toml` `--cov` line placement, and the `__init__.py` export surface

**Measured**: each unit's line is appended **in build order**, immediately before `--cov-report=term-missing`, with a
standing comment block above it.

**A) Append after `--cov=backend/observability`, before `--cov-report=term-missing`, with the standing comment; `__init__.py`
left EMPTY (RECOMMENDED).**
The comment mirrors observability's wording: *"No omit — the unit is pure logic, fully unit-coverable (no
promptfoo/Node/subprocess/network module at tier-U)"*, noting the `--cov-fail-under` gate is **UNCHANGED**.
**Empty `__init__.py`**: **nothing in the build imports `llm_judge`** — it is the last unit, wraps the built system, and
**no unit depends on it** — so an export surface would be speculative API. Tests import concrete modules directly, as
siblings do.

**B) Same placement, but `__init__.py` re-exports the public domain model.** *(Available; but it publishes an API with no
consumer, and every symbol would need a re-export test to stay at 100%.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

## 6.5 Mandatory ambiguity-check (RAN against Q1–Q5 all A + the frozen FD + approved NFR-Req + approved NFR Design + the logged Infra SKIP) — **CLEAN**

**Ran**: 2026-07-19 · **Result**: **CLEAN — 3 folds RESOLVED, no genuine gap, no surface-and-stop.**

### ⚑ CG-JUDGE-Fold-1 [the called-out check] — RESOLVED: disclosed clarification, **left un-retro-edited**, exactly as ND-Fold-1 was

**The Q1 correction does NOT require a matching correction to the approved `logical-components.md`.** The disposition is
**identical in kind to the ND-Fold-1 / ANCHOR-1 disclosure**, and for a sharper reason:

- **What is BINDING in the approved artifact is honored exactly.** `logical-components.md` states the requirement as
  *"the fake lives in `tests/`, **NEVER** in production — so **no production module can depend on it**, and CLIDEFER-1's
  scan has a **clean production set** to scan."* **`tests/fixtures.py` IS in `tests/`.** Every binding clause holds.
- **The `(tests/fakes.py)` parenthetical is load-bearing on NOTHING.** Verified: `EXPECTED_PRODUCTION_MODULES` names only
  the **four production modules** (`rubric.py`, `schemas.py`, `pipeline.py`, `engine.py`) — **no `fakes.py`**; and
  C-JUDGE-5's scan **excludes `tests/` wholesale**, so **no scan, target, or pattern references the filename at all.**
  It is an illustrative file name, not a contract.
- ⇒ **Same disposition as ND-Fold-1**: a **Code-Gen-stage clarification of an illustrative (non-binding) detail** in an
  approved artifact, **left un-retro-edited** (approved artifacts are built ON, not revised), with the discrepancy
  **disclosed explicitly in `code-summary.md`**. **No user decision needed.**

### ⚑ CG-JUDGE-Fold-2 — RESOLVED: ADVISORY-1's **token** scan must be PRODUCTION-ONLY, and that is FORCED, not convenient

**Discovered by reading the frozen U4 schema**: `DecisionMemo.recommendation: Recommendation` is a **REQUIRED** field.
Therefore **`reference_memo()` and every judged-sample fixture MUST construct a verdict value** (e.g. `Recommendation.REFER`)
— a verdict token will **necessarily** appear in `tests/fixtures.py`. That is **the memo UNDER JUDGMENT — judge INPUT**, and
the approved NFR text **already draws exactly this line**: it forbids a bare verdict token *"used as a judge **OUTPUT**"*.
⇒ **The token half scans PRODUCTION modules only**; the **structural half** — *no U22-owned type declares a
`Recommendation`-typed field* — carries the real teeth and is **unaffected by fixture content**. Documented in
`code-summary.md` so the scope reads as forced by a frozen shape, not chosen for convenience.

### ⚑ CG-JUDGE-Fold-3 — RESOLVED: NODEMO-1's scope is DELIBERATELY ASYMMETRIC to ADVISORY-1's

**NODEMO-1 must scan `tests/fixtures.py` too** — because the FD explicitly requires **the hand-authored reference memo** be
demographic-free — whereas **ADVISORY-1's token scan must exclude it** (Fold-2). The asymmetry is **deliberate and
documented**, not sloppy scoping: the two scans have different subjects.
**Additionally, a by-construction strength worth recording**: `JudgedSample` carries **`memo` + `rule_report` + `provider`
only** — the FD's §3 field table lists **no `ApplicantProfile`** — so **no demographic field can structurally enter a judged
sample at all**. The scan is the belt; the absent field is the braces. **No user decision needed.**

**⇒ Ambiguity-check CLEAN. Part 2 generated.**

---

## 7. Next step (STOP here)

Fill the five `[Answer]:` tags in §6. On your signal I will read the answers, run the **mandatory ambiguity-check**,
**embed the full Q&A in this plan file**, and generate **Part 2** — the production modules, the test suite, the coverage
line, a live full-suite run, and `guide-docs/build/llm-judge/code/code-summary.md` — then present the standardized 2-option
completion message.
**NO CODE is generated until the answers are in and checked.** This is the **5th and LAST of U22's stages**, and its
approval **closes the final unit in the entire 23-unit decomposition**.
