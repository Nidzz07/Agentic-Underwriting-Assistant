# Tech-Stack Decisions — `llm-judge` (U22, EPIC-6, Phase 2)

**Stage**: BUILD → NFR Requirements (per-unit), **Part 2 (Generation)** · **Unit**: U22 `llm-judge` · EPIC-6 · **Phase 2** ·
**Depth**: **standard** · **Date**: 2026-07-19.
**Built ON** the frozen FD + the eleven `NFR-JUDGE-*` targets — **re-opening none**. Answers **Q1–Q3 (all A)** + folds
**NFR-JUDGE-Req-Fold-1..3**.

> **HEADLINE: NO NEW DEPENDENCY.** `promptfoo` is **already floored** in `requirements.txt` (L49, `promptfoo>=0.1.0`), so the
> pip-layer no-new-dependency streak is **INTACT** and **`requirements.txt` is NOT edited**.
> **⚑ But this is NOT a clean "already floored, nothing to decide."** The installed pip package is a **thin Python SHIM
> around the Node.js/TypeScript promptfoo CLI**, and **the Node engine — the thing that actually judges — is ABSENT.**
> That is an **ENGINE gap, not a dependency gap**, and it is the entire substance of **`PROMPTFOO-CLI-DEFERRED`**.

---

## 1. Dependency verification (measured on disk, not assumed)

| Library | `requirements.txt` | Installed | Role at U22 |
|---|---|---|---|
| `promptfoo` | **`>=0.1.0` (floored, L49)** | **0.1.4 — the PYTHON SHIM only** | the **deferred** real rubric engine, behind the injected `RubricEngine` Protocol. **NOT imported by any U22 production module.** |
| **the promptfoo Node CLI** | **n/a (not a pip artifact)** | **⛔ ABSENT** | **the actual engine.** Reached only via `npx`. **The gap.** |
| `pytest` / `pytest-cov` | floored + installed | INSTALLED | tier-U runner + the QA-6 coverage gate (the sibling-unit convention) |

**`requirements.txt` is NOT edited. U22 adds no library.**

### 1.1 ⚑ The shim-vs-engine distinction, recorded in full

| Fact | Measured evidence | Consequence for U22 |
|---|---|---|
| The pip package is a **shim, not the engine** | `pip show -f promptfoo` (0.1.4): *"requires Node.js and npx"*; `cli.py` uses `shutil.which("node")` / `which("npx")` / `subprocess`, *"falling back to `npx`"* | Importing it buys **no scoring capability** — only a subprocess launcher. |
| The **Node engine is ABSENT** | `frontend/node_modules/promptfoo` not present; the `venv\Scripts\promptfoo.exe` on PATH is **the shim** | There is **nothing to bind** an adapter to at this stage. |
| Invoking it would **fetch an unpinned package over the network at run time** | the `npx` fallback path | **Violates tier-U** (no network) **and** supply-chain hygiene (unpinned) ⇒ **CLI pinning is a discharge criterion**. |
| The shim pulls **`posthog` telemetry (7.21.3)** | transitive dependency of the installed shim | A **BFSI concern** ⇒ **telemetry opt-out is a discharge criterion**. |
| Its **output shape is external, version-dependent and unpinned** | no on-disk, frozen artifact to mirror | **Grounds Q2-A** — see JUDGE-D4. |

**Shape of the decision**: the same as **`MCP-TRANSPORT-DEFERRED`** — a genuine, disclosed external-tool decision rather than
a silent assumption. *(Contrast `observability`'s `OBS-SINK-DEFERRED`, where both SDKs were floored **and installed** and only
the **wiring** was deferred. Here the engine itself is missing — a strictly larger gap, and named as such.)*

---

## 2. Decisions (JUDGE-D1..JUDGE-D9)

- **JUDGE-D1 — tier-U runner: `pytest`.** No new dependency. Matches every prior backend unit. **tier-U** = no live LLM, no
  key, no network, no Docker — **extended at U22 to: no Node, no `npx`, no promptfoo shim import, no telemetry.**

- **JUDGE-D2 — ONE shared `tests/fixtures.py` with FIVE deliberately-separate NAMED FAMILIES (Q1-A).** The exact
  **U18/U19 convention**, measured on disk: both `backend/outlier_model/tests/fixtures.py` and
  `backend/memo_extensions/tests/fixtures.py` are **one module per unit** holding **purpose-built families that are not
  reused across targets whose failure modes differ** (U18: `normal_corpus_profiles()` · `typical_profile()` ·
  `missing_optional_profile()` · **`swap_pair()`** [bias-only] · **`outlier_profile()`** [threshold-only]).

  | Family | Serves | Why it is its own family |
  |---|---|---|
  | `in_gate_samples()` | INGATE-1 | the `gemini` + `claude` provider-tagged in-gate pair |
  | **`exempt_witness_sample()`** | **EXEMPT-1 (positive)** | **its own family, so EXEMPT-1 can never be weakened by another target's edits** |
  | **`degenerate_all_in_gate_set()`** | **EXEMPT-1 (negative guard)** | **a genuinely separate builder — see JUDGE-D3** |
  | **`anchoring_pair()`** | ANCHOR-1 | **returns close + divergent TOGETHER so the pair cannot be split** |
  | `reference_memo()` | ANCHOR-1 · NODEMO-1 | the **single canonical** style/structure exemplar |

  **⚑ The anchoring pair is NOT overlapped onto the provider-tagged samples.** Overlapping (option C) was rejected because a
  change made for a **provider-scope** test would then **silently alter what "close" and "divergent" mean** — coupling
  ANCHOR-1 to INGATE-1/EXEMPT-1.

- **JUDGE-D3 — `degenerate_all_in_gate_set()` is a genuinely SEPARATE third builder, not an alias (Req-Fold-1).**
  `in_gate_samples()`'s invariant is *"contains gemini and claude"*; the degenerate set's invariant is *"contains NO
  exempt-tagged sample ⇒ `exempt_count == 0`"*. These **coincide today but are not the same contract** — the absence is
  incidental to one and **load-bearing** for the other. Three mechanisms foreclose accidental satisfaction:
  **(1) distinct `sample_id`s** (the two sets are never identity-equal); **(2) a self-asserting precondition** inside the
  builder (`all(s.provider is not ProviderScopeTag.ollama)`) so a future edit **fails at construction** rather than making
  the guard vacuous; **(3) no aliasing** — it does not call `in_gate_samples()`.
  Note also that **EXEMPT-1's positive fixture is a third composition** (`in_gate_samples()` + `exempt_witness_sample()`), so
  **three** set-level fixtures exist, not two.

- **JUDGE-D4 — the `RubricEngine` fake proves satisfiability + NON-VACUITY, and NOTHING MORE (Q2-A).**
  `assert isinstance(fake, RubricEngine)` **and** `assert not isinstance(object(), RubricEngine)` — **the exact U19
  non-vacuity assertion** (`memo_extensions/tests/test_signal.py`).
  **⚑ NO by-value interop replica, deliberately.** U19's `test_interop_by_value_u18_outlier_result_satisfies_protocol`
  replicated U18's `OutlierResult` **by value** — legitimate **because that shape is FROZEN and ON-DISK**, a verifiable
  target. **U22 has no such target**: the CLI is absent and its output shape is unpinned. A by-value replica would attest to
  an **assumption** — passing green while the real interop was broken, **worse than no test**. ⇒ **real-shape interop
  becomes an explicit, named criterion of `PROMPTFOO-CLI-DEFERRED`'s discharge**, not something faked now.

- **JUDGE-D5 — `--cov=backend/llm_judge`, NO omit (Q3-A) — following `observability` verbatim.**
  Measured in `pyproject.toml`: every pure-logic unit adds `--cov=backend/<unit>` with *"No omit — the unit is pure logic,
  fully unit-coverable"*. **`observability` is the exact hybrid precedent** — it added `--cov=backend/observability` with
  *"No omit … (**no live-SDK/subprocess/network module at tier-U**)"* **even though its live SDK binding was deferred
  (`OBS-SINK-DEFERRED`)**. `deploy-config` added **no** line **only because it had no production `.py` at all**.
  - **The deferred halves are ABSENT modules, not uncovered ones** — no promptfoo adapter and no live-run module is written
    at this stage, so **there is nothing uncoverable to omit**. Adding a speculative `omit` (option B) would **pre-authorize
    an uncovered module that does not exist**.
  - **Every production line U22 ships is tier-U-reachable through the injected fake.** The global
    **`--cov-fail-under=90` holds UNCHANGED**; U22's tree is expected at **100%**, like its pure-logic siblings.
  - **⚑ Stated so the number is not misread**: **BR-JUDGE-6/8/9 are governance/deferral targets — their verification is the
    presence/absence scans, which is ORTHOGONAL to line coverage.** A 100% figure must **not** be read as covering them.
  - **`pyproject.toml` is NOT edited at this stage** — the line lands at **Code-Gen**.

- **JUDGE-D6 — the rubric, scope-filter, aggregation, threshold and report are PURE PYTHON.** No RNG, no wall-clock, no
  external call. Dimension order follows the rubric's **declared** order ⇒ **byte-reproducible** given fixed dimension
  scores. This is what makes the deterministic half **fully** verifiable offline.

- **JUDGE-D7 — the reference memo is built via the IMPORTED FROZEN `DecisionMemo` schema.** Instantiating a frozen model is
  **using** it, not modifying it (**import-to-read ≠ edit**; ROUTES-1 / Q2-A). It lives in **U22's own fixture module** —
  **never** added to `backend/memo_agent_core/tests/`, which would be a frozen-unit edit. It inherits **advisory-only
  wording** and **no demographic identifier**.

- **JUDGE-D8 — no new emission (Q6-A).** U22's `EvalRunResult` report artifact is its **only** output. **No Prometheus
  metric, no dashboard panel** — a sixth would be drift against `observability`'s frozen **five** `METRIC_DEFINITIONS` and
  would break `deploy-config`'s five-panel no-drift scan. Both are checked **statically, read-only, without re-running
  either unit's suite**.

- **JUDGE-D9 — module layout OPEN.** Sized to the lifecycle's concerns (rubric definition · sample assembly ·
  scope-filtering · aggregation/threshold · report) plus the `RubricEngine` Protocol and the offline fake. Exact module names
  finalized at **NFR Design / Code-Gen**. No frozen file-count constraint.

---

## 3. The three registered items (recorded, NOT discharged)

### 3.1 `PROMPTFOO-CLI-DEFERRED` — **OPEN**
- **DELIVERED (U22, tier-U)**: the **`RubricEngine` Protocol** + an **offline deterministic fake** driving **every** tier-U
  test, proven **satisfiable and non-vacuous** (JUDGE-D4).
- **NOT delivered**: the real promptfoo CLI adapter — **the Node engine is absent**.
- **Discharge criteria (five, documented — NOT run)**: **(1)** Node + npx present · **(2)** CLI **pinned** (no unpinned
  `npx` run-time fetch) · **(3)** **telemetry opt-out** configured (the `posthog` concern) · **(4)** adapter bound ·
  **(5) ⚑ real-shape interop verified against the seeded fixtures** (the criterion Q2-A newly names).
- **Requires**: **NO corpus · NO tier-B · NO live provider key.** Independently dischargeable.
- **⚠️ NON-BLOCKING**: **no U22 tier-U invariant depends on it** — THRESH-1 / INGATE-1 / EXEMPT-1 / EXEMPTSCOPE-1 / ANCHOR-1
  are each fully verified with **no engine present**.

### 3.2 `JUDGE-EVAL-DEFERRED` — **OPEN**
- **NOT delivered**: the real **≥ 4/5 gate evaluated over the tier-B corpus**. `EvalRunResult.tier` reads **`unit`**.
- **Discharge criteria**: tier-B corpus **authorized + built** **AND** live Gemini + Claude keys **AND** ≥ 4/5 actually
  evaluated over real memos — **with `PROMPTFOO-CLI-DEFERRED` discharged FIRST**.
- **⚑ Distinct from 3.1 (Fold-1), one-way**: the CLI item discharges **without** the corpus; this one **cannot** discharge
  without an engine. Merging them would erase the prerequisite. **Precedent**: `outlier-model` (U18) completed with an `R`
  corpus edge and *"tier-B NOT authorized (not required)"*.

### 3.3 `FEWSHOT-ANCHOR-UNIMPLEMENTED` — **OPEN**
- **NOT delivered, and NOT U22's to deliver**: QA-4's **generation-side** few-shot anchoring — supplying exemplars to the
  memo prompt so the draft is anchored **at draft time**. **Measured: a repo-wide scan of `backend/**/*.py` for
  `few.?shot|reference_memo|reference memo` returns ZERO HITS**; U4's frozen `PromptBuilder` carries no reference memo and no
  exemplars.
- **Owner**: **`memo-agent-core` (U4)** or a future **explicitly-authorized** change. Implementing it here would require
  **editing a frozen P1 unit** — forbidden by the standing guardrails and excluded by Q2-A.
- **⚑ Distinct from 3.1 (Req-Fold-3)**: different **content**, different **owner**, opposite **direction of data flow**
  (exemplars **INTO** generation vs engine output **OUT OF** scoring), and different **dischargeability** (**structurally
  blocked** vs **merely not-yet-done**). **U22 claims no discharge.**

---

## 4. Held

- **No new dependency**; **`requirements.txt` NOT edited**; **`pyproject.toml` NOT edited at this stage** (the `--cov` line
  lands at Code-Gen). **No code**; **`backend/llm_judge/` does not exist yet** (verified absent).
- **The frozen FD re-opened NONE** — `BR-JUDGE-1..11`, the domain model, the `RubricEngine` seam, the four fixture roles and
  the three register items are **built ON, not revised**.
- **Domain invariants bind**: **advisory-only** wording; the judge **never alters a recommendation**; **no LLM in the
  deterministic rules path**; **`temperature=0` stays centrally fixed in U19's frozen adapters** (U22 neither sets nor
  overrides it); **no demographic identifier anywhere**.
- **Untouched**: **WIRE-1** · the **17 frozen P1 units (INCLUDING `memo-agent-core`)** · `outlier-model` (U18) ·
  `memo-extensions` (U19) · `ui-outlier-view` (U20) · `observability` (U21) · `deploy-config` (U23) · the **CLOSED
  composition root** · **tier-B (NOT authorized)** · the **`audit_store` Docker-guard gap** (31 skips + 5 Docker errors to
  stay unchanged) · **no other unit started** · the **23-unit decomposition unchanged**.
