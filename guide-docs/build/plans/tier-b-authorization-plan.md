# TIER-B AUTHORIZATION — SCOPING PLAN

**Register items addressed together**: **#3** `tier-B corpus run` · **#9** `PROMPTFOO-CLI-DEFERRED` ·
**#10** `JUDGE-EVAL-DEFERRED` · **#18** `NO-PRODUCTION-LLMCLIENT` (NARROWED) · **#22**
`MEMO-PROSE-NOT-BIT-REPRODUCIBLE`
**Date**: 2026-07-23 · **Status**: 🟡 **SCOPING / PLANNING ONLY — no code, no API call, no spend, no corpus**
**Predecessors** (the discipline model): `fix-register-19-plan.md` · `fix-register-18-plan.md` ·
`fix-register-20-plan.md` · `fix-register-8-plan.md`

---

## 0. What this document is, and is not

**Is**: a ground-truth report and a set of **genuinely open decisions**, each written in full with lettered
options and — where the evidence grounds one — a recommendation. **Every `[Answer]` tag below is BLANK. None is
pre-filled. None is improvised.**

**Is not**: an authorization, a design, or an implementation. **No code was generated. No API call was made. No
money was spent. No corpus was generated.** Nothing in this pass touched `ALLOW_REAL_LLM_CALLS`, the call cap, or
any frozen artifact.

**⚑ Why this plan is deliberately UNBUNDLED.** Every prior register item resolved after Scope B (#19, #18, #20,
#8) was a *single* defect with a *single* owner, and 4–6 questions sufficed. **tier-B is categorically different**:
it is an entire testing tier that was deliberately never run across the whole build, it spans five register items,
and it is **the first real-money path at scale** (≈1,500–1,800 live model calls, vs the 20-call cap that is the
build's current ceiling). Sub-decisions a smaller item would fold into a "reasonable default" are therefore
surfaced here as their **own numbered questions** — twelve of them. That is intentional conservatism, not padding.

---

## 1. Ground truth — re-established from disk, not from any summary

Every claim below was verified by reading the actual file or running a read-only check in this environment. Where
disk **diverges from the register**, it is flagged **⚑ DIVERGENCE** and stated plainly.

### 1.1 `backend/corpus_generator/build.py` — ✅ CONFIRMED exactly as the register describes

95 lines. `main()` parses `--seed 42 · --out corpus · --rulebook-version 1.0.0 · --engine-version corpus-build-1 ·
--model-id gemini-2.5-flash · --min-profiles 300 · --attempt-budget 100000`, reads the key via
`secrets_config.get_settings()` (SEC-3, never a literal), constructs `_GeminiLLMClient` → `CorpusGenerator`, and
writes `corpus/profiles.json` + `corpus/manifest.json`.

* **It has never been run.** `corpus/` **does not exist** on disk (`ls -d corpus` → *No such file or directory*).
* **It is coverage-omitted** — `pyproject.toml` `[tool.coverage.run] omit` contains `*/corpus_generator/build.py`.
* **It is excluded by name from two structural scans** — `tests/test_pii.py:15` and
  `tests/test_reference_not_own.py:16`, both `_EXCLUDED_FILES = {"build.py"}`.
* **It cannot run in this environment today.** `python -c "import google.genai"` → **`ModuleNotFoundError`**
  (confirmed live), even though `requirements.txt` now declares `google-genai>=1.0.0` (#18's manifest fix). #22's
  D1 note predicted exactly this: *"importable in principle … `google-genai` is not installed here, so it remains
  non-importable in this environment regardless."* **Confirmed.**

**⚑ DIVERGENCE A — the model-id default contradicts #22's own mitigation.** `build.py:57` defaults `--model-id`
to **`gemini-2.5-flash`** — a **floating alias**. `generator.py:107` passes it as `model_version=config.model_id`
into `build_manifest`, so it is **stamped into the frozen `CorpusManifest.model_version`**. #22's shipped
mitigation is precisely the opposite: `seed_demo_cases.py`'s `REAL_MODEL_ID = "gemini-2.5-flash-001"`, chosen
*"so provider-side model drift is bounded and the audit stamp is falsifiable"*, with an explicit instruction
*"never falling back to the floating alias."* **A tier-B corpus run at today's defaults would freeze a floating
alias into the corpus's permanent provenance record.** This is Q5.

**⚑ DIVERGENCE B — `_GeminiLLMClient` is outside #18's guardrails entirely.** `build.py:28-44`:

```
class _GeminiLLMClient:
    def __init__(self, api_key: str) -> None:
        from google import genai
        self._client = genai.Client(api_key=api_key)
    def generate(self, *, model, prompt, temperature) -> str: ...
```

**No call cap. No `ALLOW_REAL_LLM_CALLS` gate. No logging. It takes the raw API key.** #18's two-gate design
(`--real-llm` **and** `ALLOW_REAL_LLM_CALLS=true`, plus a hard cap counting retries) protects *only*
`seed_demo_cases.py`. **`build.py` is reachable with nothing but a key present.** This is Q3 and Q4.

**⚑ DIVERGENCE C — the corpus artifact's disposition was never decided.** `.gitignore` has **no `corpus/`
entry**. A generated corpus (300 profiles × 3 LLM-authored prose documents + a manifest) is therefore
**committable by default**, and nothing in the build has ever decided whether it should be. This is Q7.

### 1.2 What *"tier-B is not authorized"* has meant operationally — ⚑ **THERE IS NO FLAG**

A repo-wide scan finds **31 tier-B references in Python**. **Every single one is a docstring, comment, or test
name.** There is:

* **no** `TIER_B_AUTHORIZED` constant, module, or setting;
* **no** environment variable gate (`ALLOW_REAL_LLM_CALLS` gates *only* `build_gemini_client`, which `build.py`
  never calls);
* **no** runtime check anywhere that consults anything about tier-B.

**tier-B has been unauthorized purely and only because nobody has ever typed the command.** The only enforcement
in the build is **negative and indirect**: the coverage omit, the two `_EXCLUDED_FILES` scan exclusions, and U22's
`test_promptfoo_is_never_imported_into_the_running_test_process`.

**Two consequences, both load-bearing for this plan.** (i) Authorizing tier-B requires **no un-gating** — there is
nothing to switch on. (ii) Symmetrically, **nothing prevents an accidental full-scale run** except the absent SDK;
once `pip install google-genai` happens for any reason, `python -m backend.corpus_generator.build` is one command
away from ~900 uncapped billable calls. That asymmetry is itself an argument for Q3.

### 1.3 The two real-API clients — ⚑ **independent, and neither supersedes the other**

| | `CappedGeminiClient` + `build_gemini_client` (#18) | `_GeminiLLMClient` (U14 `build.py`) |
|---|---|---|
| Location | `backend/app/llm_client.py` (composition root) | `backend/corpus_generator/build.py` (frozen unit) |
| Holds the key? | **No** — takes an already-constructed SDK client | **Yes** — takes the raw `api_key` |
| Call cap | **Yes**, hard, counts retries, raises `LLMCallCapExceeded` | **None** |
| `ALLOW_REAL_LLM_CALLS` | **Yes**, exact `"true"`, in the factory | **None** |
| Logging | prompt **length** only, never text, never key | **None** |
| Satisfies | `memo_agent_core.LLMClient` structurally | `memo_agent_core.LLMClient` structurally |

Both lazily `from google import genai` and both call `models.generate_content`. **Neither imports or references
the other.** They are two independent implementations of the same frozen seam that now coexist.

**Can `build.py` simply use #18's client?** Not without crossing a boundary the build has consistently defended:
`backend/corpus_generator` is listed in `llm_judge/tests/structural.py`'s `FROZEN_PREFIXES` and in
`app/tests/test_frozen_untouched.py`'s frozen-unit set, and the direction **frozen unit → composition root
(`backend/app/`)** is exactly what `test_no_frozen_unit_imports_the_composition_root` exists to prevent. So the
duplication **cannot be resolved by a one-line import**. It is a real decision — Q4.

### 1.4 What tier-B must produce, and who consumes it

**The corpus output half is settled and consistent — this genuinely works.** `build.py` writes
`corpus/profiles.json` (a JSON array of `CorpusRecord`) + `corpus/manifest.json`. **Three independent readers
already expect exactly that shape**: `quality_gates/corpus_loader.py::from_file`,
`outlier_model/corpus_source.py::from_file`, and their tests — each doing
`[CorpusRecord.model_validate(row) for row in json.loads(...)]`. Nothing needs to change for the corpus to be
consumable by the gates and by U18.

**⚑ The judge half does NOT work. `EvalTier.LIVE` has no consumer.**

* `EvalTier.LIVE` appears in **exactly two places repo-wide**: its own enum member (`schemas.py:54`) and
  `EvalRunResult.tier`'s default (`schemas.py:135`). `run_eval(..., tier=…)` takes it as a parameter and **stamps
  it into the report**. **Nothing branches on it.** No production caller passes it — the only callers are 15 test
  functions, all defaulting to `UNIT`.
* **There is no llm-judge entrypoint of any kind** — no `build.py`, no script, no CLI. `llm_judge/__init__.py` is
  *"deliberately empty of re-exports … nothing in the build imports it."*
* **⚑ The shapes do not connect.** `CorpusRecord` = `profile + documents_text + label + intended_class +
  edge_case_tags`. `JudgedSample` = `memo: DecisionMemo + rule_report: RuleResultReport + provider`. **Nothing in
  the build converts one into the other.** A tier-B judge run needs a corpus → `RulesEngine.evaluate()` →
  `LangGraphOrchestrator.run()` → `JudgedSample` assembly that **exists nowhere**. The closest precedent is
  `seed_demo_cases.py::_SeedSeams`, which does the profile → report → memo chain — but writes to **Postgres**, not
  to a judgeable in-memory sample list.

**Nor is there any gate entrypoint.** A grep for `BiasSwapGate|ReproducibilityGate|RuleCoverageGate|
CoverageWiringGate` outside `backend/quality_gates/` returns **nothing**. The four gates are classes exercised
only by their own tests. Running them over a real corpus also needs an entrypoint that does not exist. This is Q8.

### 1.5 Cost and scale — itemized from the code, ⚑ and **3× larger than the register's framing implies**

| Stage | Calls | Evidence |
|---|---|---|
| **Corpus prose** | **3 × N** | `document_text_generator.py:25` `_DOC_TYPES` has **three** entries (salary slip, bank statement, medical questionnaire); `generate_for()` loops them, **one `generate()` per doc type per profile**. |
| Rejection sampling | **0** | `rejection_sampler.py` runs pure-Python (`ProfileFactory` + `LabelingOracle` → `RulesEngine`) **before** the prose loop in `generator.py:92`. **Discarded attempts cost nothing.** A genuinely good property. |
| **Memo drafting** | **1–2 per memo** | `orchestrator.py:118` re-drafts while `attempts < MEMO_CITATION_RETRY_CAP`; `constants.py:18` `= 2`. So 1 call, or 2 if the first draft's citations fail. |
| **Judge scoring** | **≈1 per sample** | Undesigned. `RubricEngine.score(sample, rubric) -> list[DimensionScore]` is per-sample, so one call scoring both dimensions is the natural shape; a per-dimension implementation would be 2×. |
| **Four quality gates** | **0** | ⚑ **All four are LLM-FREE** — see below. |

**Full designed scale (N = 300):**

```
corpus prose      300 profiles x 3 docs                     =   900 calls
memo drafting     300 memos x 1-2 (citation retry)          =   300 - 600 calls
judge scoring     300 samples x 1 (2 dimensions per call)   =   300 calls
                                                              --------------
                                                    TOTAL   = 1,500 - 1,800 real, billable calls
```

**Against #18's guardrail: the cap default is 20.** Full tier-B is **75–90×** that, and the cap is
**per-client-instance** (`self._count` on one `CappedGeminiClient`), so it does not aggregate across the three
stages even if each used the capped client. **#18's guardrails were sized for the seed script's 2–3 demo cases
and are structurally inadequate at this scale.** That is Q3 — and per the HOLDS, changing them requires its own
justification, not a quiet bump.

**⚑ DECISIVE, and it cuts the *other* way — all four blocking gates are LLM-FREE.** Verified by reading each:

* `BiasSwapGate` — swaps `{full_name, gender, city}` and compares `evaluation_output()` from the injected
  **rules engine**. No LLM.
* `ReproducibilityGate` — runs `engine.evaluate(profile, version)` **×10** and compares the
  `evaluation_output()` projection. No LLM. Its own docstring: *"asserted on the **deterministic engine output**,
  not LLM wording."*
* `RuleCoverageGate` — accumulates definite PASS/FAIL per `rule_id` over the corpus via `engine.evaluate()`. No LLM.
* `CoverageWiringGate` — reads `pyproject.toml` with `tomllib`. No LLM.

**So: once a corpus exists, running all four blocking gates against real data costs ZERO additional model calls.**
Two of PROJECT-BRIEF §6's headline criteria — **bias-swap delta 0** and **reproducibility 100%** — become
verifiable against real data for the price of the corpus alone. **This materially changes the shape of the
authorization decision** and is the strongest argument for the separability in Q1.

### 1.6 ⚑ FINDING 1 — #9's stated blockers now have concrete mechanisms (the register's rationale is partly stale)

The register's rationale for `PROMPTFOO-CLI-DEFERRED` (`engine.py:65-72`) asserts three things. **Checked live in
this environment:**

| Register claim | Verified today | Verdict |
|---|---|---|
| *"the Node engine is ABSENT"* | **`node v22.17.1`** and **`npx 11.16.0`** are present | ⚑ **STALE HERE.** Discharge criterion 1 (*"Node and npx present"*) is **already satisfied** in this environment. The global `promptfoo` **CLI** is still absent (`npm ls -g` → only `node-red`, `npm`; `which promptfoo` resolves to the **venv pip shim**, not a Node binary). |
| *"would `npx`-fetch an **unpinned** package at run time"* | `promptfoo/cli.py` (shim **0.1.4**, installed) builds `[npx, "-y", f"promptfoo@{version}"]` where `version = os.environ.get("PROMPTFOO_VERSION", "latest")` | ⚑ **A PINNING MECHANISM EXISTS.** `PROMPTFOO_VERSION=<exact>` pins the fetch; `npm install -g promptfoo@<exact>` bypasses npx entirely (the shim prefers a found global binary over npx). Criterion 2 is **addressable**. |
| *"pulls `posthog` telemetry"* | `promptfoo/telemetry.py` `_disabled` returns True on `PROMPTFOO_DISABLE_TELEMETRY` **or** `IS_TESTING`; the PostHog client is constructed **lazily** and only when not disabled | ⚑ **AN OPT-OUT EXISTS** and is the same env var the TypeScript project honours. Criterion 3 is **addressable**. **Honest caveat**: `posthog` is imported at `telemetry.py` module scope (and **is installed here**, v7.21.3), so the *dependency* is present regardless — only the *network emission* is suppressed. |

**Criteria 4 and 5 remain genuinely open**: *"the real adapter bound to the `RubricEngine` Protocol"* and
*"real-shape interop verified against the seeded fixtures."* Criterion 5 is precisely what `test_clidefer.py`'s
§2 refuses to fake — *"a replica would attest to an ASSUMPTION and pass green while the real interop was broken."*

**This does not make promptfoo the right route.** It makes **both routes real, grounded choices** — which is why
Q2 is the single most consequential question in this plan.

### 1.7 ⚑ FINDING 2 — a hard structural blocker the brief's framing did not anticipate

**(a) U22's frozen tests hard-assert `discharged is False`, and U22's design supplies NO mechanism to flip it.**

Three separate frozen tests assert it:

* `test_governance.py::test_the_three_register_items_are_named_owner_attributed_and_undischarged` —
  `assert item.discharged is False` for **every** item in `DEFERRED_REGISTER`;
* `test_clidefer.py::test_the_cli_deferral_is_disclosed_with_its_five_discharge_criteria` —
  `assert item.discharged is False`;
* `test_clidefer.py::test_no_register_item_claims_discharge` —
  `assert all(item.discharged is False for item in DEFERRED_REGISTER)`.

The task brief's HOLD anticipated *"updating their discharged status through whatever mechanism U22's own design
specifies."* **On disk there is no such mechanism.** `DeferredItem` is a `frozen=True` dataclass with
`discharged: bool = False`; the only way to record a discharge in code is to change that literal, **which breaks
three frozen U22 tests**. Discharging #9 or #10 *in code* is therefore a **MATCHED PAIR** — register edit +
frozen-test edit, neither half valid alone — structurally identical to **#13 `NOTWIRED-FILENAME-STALE`**, which
the build has kept open for exactly this reason. This is Q11, and it is why "the gate passed" and "the register
says discharged" are **two different decisions**.

**(b) A real `RubricEngine` adapter cannot live inside `backend/llm_judge/`.** Four frozen scans forbid it:

| Frozen test | What it forbids |
|---|---|
| `test_governance.py::test_u22_adds_no_new_dependency_beyond_the_standard_library_and_frozen_units` | production import roots **⊆ `{backend, dataclasses, enum, typing, __future__}`** — so no `json`, no `os`, no `subprocess`, nothing |
| `test_governance.py::test_no_production_module_opens_a_network_connection_or_spawns_a_process` | `requests, httpx, urllib, socket, subprocess, aiohttp` |
| `test_governance.py::test_no_u22_module_reads_a_secret_or_an_environment_variable` | `api_key, secret_key, sk-, os.environ, getenv` — across **production AND tests** |
| `test_clidefer.py::test_no_production_module_imports_the_promptfoo_shim` | `FORBIDDEN_PRODUCTION_IMPORTS = {"promptfoo"}` |

Both scans enumerate via `UNIT_DIR.rglob("*.py")`, so **any new file placed under `backend/llm_judge/` is
automatically enrolled**. **The adapter must land outside the unit** — the exact shape #18 took
(`backend/app/llm_client.py`) and #8 took (`backend/scripts/run_migrations.py`). `backend/scripts/` is already
confirmed (by #8's ambiguity-check) to sit outside every structural file-set scan **and** outside every `--cov=`
target. This bounds Q2 and Q8.

### 1.8 The Claude side of the in-gate set — ⚑ a second missing production client

`pipeline.py:36` `IN_GATE_PROVIDERS = {GEMINI, CLAUDE}`. AC-6's aggregate is computed over **in-gate** samples.
But:

* `ClaudeAdapter` (`memo_extensions/provider_secondary.py:58`) drives a **different seam** —
  `ThinkingLLMClient.generate(*, model, prompt, temperature, thinking)` — **not** the frozen
  `memo_agent_core.LLMClient`. **No production implementation of `ThinkingLLMClient` exists anywhere.** #18
  supplied a Gemini client for the *other* seam.
* `secrets_config/settings.py`'s `Settings` declares **six** required fields — `DATABASE_URL`,
  `AUDIT_WRITER_URL`, `AUDIT_READER_URL`, `AUDIT_WRITER_PASSWORD`, `AUDIT_READER_PASSWORD`, `GEMINI_API_KEY`.
  **There is no `ANTHROPIC_API_KEY` field at all**; `.env.example` lists it commented-out under *"Phase-2
  RESERVED"*. Adding one reopens **frozen U16**.

So a Claude-inclusive tier-B needs **a second production client for a second Protocol plus a frozen-unit
reopening**. That is Q12, and it is a much larger ask than it first appears.

### 1.9 Current test state — carried forward, **not re-run this pass**

**1556 passed / 0 failed / 43 skipped / 5 errors** (the same `audit_store` Docker-absence names) **/ 99.87%
coverage.** Register: **22 tracked — 17 open · 2 discharged (#2 partly, #20 fully) · 3 narrowed (#8, #18, #19).**

---

## 2. The design tension, stated precisely

**tier-B is the only route to two things the project promised and has never verified**: AC-6's ≥4/5 LLM-as-judge
score over *real drafted memos*, and PROJECT-BRIEF §4's *"synthetic dataset: 300+ applicant profiles"* actually
existing. Deliverable §7.2 (*"eval suite — labeled test set, accuracy/groundedness metrics, LLM-as-judge rubric
via promptfoo"*) and §7.8 (*"rule coverage report — every rule exercised"*) both point here.

**Against that**: tier-B is the first real-money path at scale, the guardrails that exist were sized for 20 calls,
the one entrypoint that exists is outside those guardrails and stamps a floating model id, the judge half has no
entrypoint and no shape bridge, and discharging the two register items it targets collides with three frozen
tests.

**Four constraints bound every option below**:

* **C-1 — nothing may be added inside `backend/llm_judge/`.** §1.7(b). Any adapter or entrypoint lands outside.
* **C-2 — `build.py` cannot import the composition root.** §1.3. The two-client duplication has no free fix.
* **C-3 — the four blocking gates are free once a corpus exists.** §1.5. Corpus generation and judge evaluation
  are **separable purchases**, not one indivisible one.
* **C-4 — `discharged=False` is frozen-test-enforced.** §1.7(a). A passing gate does **not** automatically become
  a discharged register item.

---

## 3. THE OPEN QUESTIONS

> **Every `[Answer]` tag below is deliberately BLANK.** Recommendations are given where the disk evidence grounds
> one, and withheld where it does not. Nothing here is decided.

---

### Q1 — What exactly gets authorized, and in what order? Are these separable authorizations?

The brief asks whether corpus generation, a real judge engine, and a live evaluation run are separable. **They
are — and §1.5's finding that the four gates are LLM-free makes the separation unusually clean.** Three candidate
packages:

* **STAGE 1 — corpus generation only.** Run `build.py` (or a guarded equivalent) to produce
  `corpus/profiles.json` + `corpus/manifest.json`. Cost: **3 × N calls**. Then run the four blocking gates over
  the real corpus at **zero additional call cost**. Addresses **#3**. Verifies **AC-3 (bias-swap delta 0)**,
  **AC-1 (reproducibility ×10)** and **AC-4 (rule coverage 100%)** against real data for the first time.
  Touches **#9 and #10 not at all.**
* **STAGE 2 — a real rubric engine.** Bind a real `RubricEngine` (route chosen in Q2). Addresses **#9**.
  Independently valuable: #9's discharge criteria include *"real-shape interop verified"*, which is provable on
  the **existing seeded fixtures** with **no corpus at all** — `test_evaldefer.py` already asserts this
  asymmetry (*"`PROMPTFOO-CLI-DEFERRED` discharges without any corpus"*).
* **STAGE 3 — the live evaluation run.** Draft real memos over the corpus and score them. Addresses **#10**,
  verifies **AC-6**. **Requires both Stage 1 and Stage 2** — this is the register's recorded one-way
  prerequisite, and it is genuine, not bureaucratic: without Stage 1 there is nothing to draft from, without
  Stage 2 there is nothing to score with.

**Options:**

* **(a)** Authorize **Stage 1 only** now. Generate the corpus, run the four free gates, record results, and
  return to Q2/Q3 for Stages 2–3 as a **separate later decision** with Stage 1's actual observed cost in hand.
* **(b)** Authorize **Stage 1 + Stage 2** now (corpus + a real engine bound and interop-verified), deferring the
  full evaluation run.
* **(c)** Authorize **all three stages** as one package, with the full spend approved up front.
* **(d)** Authorize **Stage 2 only** first (a real engine proven against the existing seeded fixtures, zero
  corpus, minimal spend) — front-loading the highest technical risk (Q2) at the lowest cost, then decide on the
  corpus afterwards.

**Recommendation: (a), unless Q6 selects a pilot, in which case (a) applied to the pilot.** Three grounded
reasons. (i) **Stage 1 buys the most verified acceptance criteria per rupee spent** — three of §6's seven, for
the price of the corpus alone (C-3). (ii) **It is the only stage with a working consumer already on disk** — the
three `from_file` readers (§1.4); Stages 2 and 3 both need code that does not exist. (iii) **It de-risks the
estimate** — the ≈1,500–1,800 figure in §1.5 is derived from code, not measured; Stage 1's actual token spend is
the only honest input to deciding whether Stage 3 is affordable. **Counter-argument, stated fairly**: (d) has a
real case — Q2 is the hardest technical question here and could be settled for a handful of calls, and if the
route-around-promptfoo option proves unworkable, that changes what Stage 1 is even *for*.

**[Answer]**: (a) — authorize Stage 1 only (corpus generation), then run the four LLM-free blocking gates over the real corpus at zero additional call cost. Stages 2 and 3 return as a separate later decision with Stage 1's actual observed spend in hand. The reasoning holds: Stage 1 buys three of the seven acceptance criteria for the price of the corpus alone, it's the only stage with working consumers already on disk, and it converts the derived 1,500-1,800 estimate into a measured number before anything larger is committed.

---

### Q2 — ⚑ The #9 promptfoo problem: use promptfoo, or route around it entirely?

**The single most consequential technical question in this pass.** §1.6 established that three of #9's five
discharge criteria now have concrete mechanisms; §1.7(b) established that **whichever route is chosen, the
adapter cannot live inside `backend/llm_judge/`**.

* **(a) Bind the real promptfoo CLI**, pinned via `PROMPTFOO_VERSION=<exact>` (or `npm install -g
  promptfoo@<exact>`), with `PROMPTFOO_DISABLE_TELEMETRY=1`, behind an adapter placed **outside**
  `backend/llm_judge/` that implements `RubricEngine.score()` by shelling out and parsing the CLI's output.
  **For**: this is what PROJECT-BRIEF §7.2 and §9's *"Evals"* row literally name, and it discharges #9 **on its
  own recorded criteria**, all five, including *real-shape interop verified*. **Against**: it introduces a Node
  toolchain, an external output shape that is *"external, version-dependent and unpinned"* (U22's own words), a
  `subprocess` boundary in a BFSI system, and the `posthog` dependency stays installed even with emission
  suppressed. It also makes the eval depend on promptfoo's own provider configuration — a **second** place API
  keys and model ids are configured, outside `secrets_config`.
* **(b) Route around promptfoo entirely** — implement `RubricEngine.score()` directly against
  `llm_judge.rubric.GROUNDEDNESS_RUBRIC`, using a real `LLMClient` (#18's `CappedGeminiClient`) as the judging
  model: build a judge prompt from the rubric's two `RubricDimension.description` strings, call the model, parse
  `list[DimensionScore]`. **For**: no Node, no npx, no subprocess, no telemetry, no second config surface; it
  reuses the **guarded, capped, gated** client #18 built for exactly this class of problem; `RubricEngine` is
  *"the ONE substitutable point in the unit"* and was designed to be substituted; and it keeps the whole eval
  inside Python where `secrets_config` is the single key path. **Against**: it **cannot discharge #9 on #9's own
  criteria** — those criteria are written *about promptfoo specifically* (pinned CLI, telemetry opt-out,
  real-shape interop against the CLI). Choosing (b) means #9 is resolved by **making itself moot**, which is a
  **narrowing or a re-framing, not a discharge**, and must be recorded as such (see Q11). It also weakens the
  literal reading of deliverable §7.2 (*"via promptfoo"*).
* **(c) Both** — implement (b) as the primary engine and (a) as a secondary cross-check, comparing the two
  engines' scores on the same samples. **For**: the comparison is itself evidence about judge reliability, and it
  discharges #9 on its own criteria *while* keeping the production path promptfoo-free. **Against**: roughly
  double the implementation and double the judging spend, for a project already at scale-risk.
* **(d) Neither yet** — defer Q2 until Stage 1's corpus exists, and decide the engine route with real memos in
  hand.

**Recommendation: (b), with the discharge consequence stated explicitly and accepted up front.** Grounded in four
disk facts. (i) **U22's design already points here**: `RubricEngine` is a `runtime_checkable` Protocol described
as *"the ONE substitutable point"*, and `engine.py`'s header names *"no promptfoo shim imported"* as a
**property to preserve**, not a temporary state. (ii) **The BFSI argument that rejected promptfoo at tier-U has
not changed** — an unpinned-by-default external CLI with telemetry, in a system whose whole thesis is
determinism and auditability, is exactly what U22 declined; `PROMPTFOO_VERSION` pinning makes it *possible*, not
*good*. (iii) **#18 already built the right shape** — a capped, flag-gated, key-safe client that satisfies the
seam; route (b) reuses it and inherits its guardrails, where route (a) opens a second, unguarded spend path
through promptfoo's own provider config. (iv) **C-1 applies either way**, so (a)'s "it's what the brief says"
advantage does not extend to it being structurally simpler — both need an out-of-unit adapter.
**⚑ The cost of (b), stated plainly and not minimised**: choosing it means **#9 is never discharged on its
recorded criteria**. Deliverable §7.2's *"via promptfoo"* becomes unmet-as-literally-written, and that must be
disclosed in the deliverable, not quietly reinterpreted. If discharging #9 exactly as written matters more than
the architectural objection, **(a) is the correct answer and this recommendation should be overridden.**

**[Answer]**: ⚑ **DEFERRED-PENDING-STAGE-2-AUTHORIZATION — NOT ANSWERED IN THIS PASS.** Verbatim: *"Deferred — not answered in this pass. Since Q1 authorizes Stage 1 only, Q2 (the promptfoo-vs-route-around decision) is not yet needed and should not be pre-committed. Record it explicitly as deferred-pending-Stage-2-authorization rather than answered, so the reasoning in your recommendation stays available and un-stale for when it's actually live. I note your recommendation of (b) with its honest cost stated — that #9 would then never discharge on its own recorded criteria — and I want that tradeoff decided with Stage 1's results visible, not before."*

> **The recommendation above is PRESERVED INTACT and is not superseded, not weakened, and not to be re-derived.** When Stage 2 authorization is taken up, this question is live exactly as written, with §1.6's and §1.7(b)'s ground truth still standing.

---

### Q3 — Spend guardrails at tier-B scale: are #18's adequate, raised, or replaced?

Per the HOLDS, this pass **has not touched** `ALLOW_REAL_LLM_CALLS` or the cap. The facts: the cap defaults to
**20**, is **per-client-instance**, lives inside `CappedGeminiClient`, and **does not cover `build.py` at all**
(§1.1 Divergence B). Full tier-B is **1,500–1,800 calls** (§1.5).

* **(a) Raise `--max-llm-calls` for the run** and otherwise keep #18's design as-is. Simple; but it leaves
  `build.py`'s uncapped path untouched, so the largest single stage (900 calls) stays **entirely ungoverned**.
* **(b) Extend #18's existing guardrails to cover the corpus path** — i.e. whatever Q4 decides about the
  two-client duplication also brings the cap and the `ALLOW_REAL_LLM_CALLS` gate to corpus generation, with a
  per-stage cap set deliberately (e.g. corpus ≈ 3N + headroom; drafting ≈ 2N; judging ≈ N + headroom) rather than
  one global number.
* **(c) Design a separate, larger-scale guardrail** appropriate to a batch run — e.g. a *budget* abstraction
  (max calls **and** an estimated-token or estimated-cost ceiling), a **dry-run mode** that counts the calls a run
  *would* make without issuing any, and a **resumable checkpoint** so a run that trips the ceiling does not throw
  away the calls already paid for. Strictly more work; strictly more appropriate to the scale.
* **(d) A per-stage explicit override with no new mechanism** — each stage invoked with its own cap passed
  explicitly on the command line, no defaults changed anywhere, so the number is a conscious act every time.

**Recommendation: (b) plus the dry-run element of (c), and explicitly NOT (a).** Reasons: (i) **(a) is
unacceptable on its own** — it governs the smallest stage and leaves the 900-call stage uncapped, which is
precisely the asymmetry §1.2 flagged; (ii) **a dry-run counter is cheap and high-value here** — the
1,500–1,800 estimate is *derived*, and the sampler's keep/discard behaviour means the exact profile count is
seed-dependent (§1.5 note), so a zero-cost count-what-I-would-call pass converts an estimate into a number
**before** any money is spent; (iii) **per-stage caps beat one global cap** because the three stages have
genuinely different shapes and a single number either strangles corpus generation or fails to constrain judging.
**Withheld**: whether the full (c) budget/resume machinery is warranted depends on Q6's scale answer — at pilot
scale it is over-engineering, at full scale it is arguably the minimum. **Explicitly noted**: any change here
weakens nothing only if the gate stays *exactly* `ALLOW_REAL_LLM_CALLS == "true"` and caps move **up by explicit
argument, never by changing a default**.

**[Answer]**: (b) plus the dry-run element of (c), and explicitly not (a). Extend #18's guardrails to cover the corpus path via whatever Q4 decides, with a per-stage cap set deliberately rather than one global number, and add a zero-cost dry-run counter that reports exactly how many calls a run would make before any are issued. The gate stays exactly ALLOW_REAL_LLM_CALLS == "true"; caps move up only by explicit argument, never by changing a default. Given Q1 scopes this to Stage 1, only the corpus-stage cap needs setting now.

> ⚑ **Ambiguity-check constraint (vi), binding on implementation**: `secrets_config/tests/test_governance.py::test_env_example_matches_settings_fields` asserts `.env.example`'s **active** keys equal `Settings.model_fields` **exactly**. Any new Stage-1 switch must therefore be a **CLI argument** (the `--max-llm-calls` precedent) or a **commented** `.env.example` line (the `ALLOW_REAL_LLM_CALLS` precedent) — **never a new active key**, which would break a frozen U16 test.

---

### Q4 — The two-client duplication: resolve it, and if so how and when?

§1.3: `CappedGeminiClient` (guarded) and `_GeminiLLMClient` (unguarded) both implement the same frozen seam.
§1.3 also established `build.py` **cannot** import `backend/app/` without inverting the frozen-unit → composition
direction.

* **(a) Leave both, unchanged.** Honest about the duplication, changes nothing, and accepts that the corpus stage
  runs **unguarded**. Requires Q3 to accept an ungoverned 900-call stage — which the Q3 recommendation rejects.
* **(b) Write a new tier-B corpus entrypoint outside both trees** (e.g. `backend/scripts/build_corpus.py`) that
  constructs `CappedGeminiClient` via `build_gemini_client` and injects it into `CorpusGenerator` — which
  **already takes `llm_client` as a constructor parameter**, so no frozen unit changes at all. `build.py` is
  then left **exactly as-is**, unused, still coverage-omitted, and disclosed as superseded-but-not-deleted (the
  build's established supersede-not-rewrite discipline). `backend/scripts/` is confirmed outside every structural
  scan and outside `--cov` (#8's ambiguity-check).
* **(c) Reopen U14 and edit `build.py`** to use the guarded client. Requires resolving C-2 (the import direction),
  i.e. either moving the guarded client somewhere both can reach, or duplicating the guard logic. **Reopens a
  frozen unit** for something (b) achieves without one.
* **(d) Defer** — decide only after Q1 settles whether corpus generation is authorized at all.

**Recommendation: (b).** It is the same move #18 and #8 both made — put the cross-cutting orchestrator in
`backend/scripts/`, reference frozen units call-only, edit none of them. It is the *only* option that brings the
900-call stage under #18's guardrails **without** reopening a frozen unit or inverting an import direction, and
it works because `CorpusGenerator.__init__` was designed with `llm_client` injected. It also resolves Divergence
A for free (the new entrypoint can pass a non-floating `--model-id` default — see Q5) without editing `build.py`.
**Stated honestly**: (b) leaves a **second, still-unguarded entrypoint on disk**. That is a real cost and must be
disclosed, not glossed — though it is strictly no worse than today, and (a) leaves the same file *plus* no
guarded alternative.

**[Answer]**: (b) — a new tier-B corpus entrypoint under backend/scripts/ that constructs CappedGeminiClient via build_gemini_client and injects it into CorpusGenerator (which already takes llm_client as a constructor parameter, so no frozen unit changes). build.py is left exactly as-is, unused, coverage-omitted, and disclosed as superseded-but-not-deleted. Record honestly that this leaves a second unguarded entrypoint on disk — that's a real cost, strictly no worse than today, but it must be disclosed rather than glossed.

---

### Q5 — The model-id divergence: which model id does a tier-B corpus stamp?

§1.1 Divergence A: `build.py` defaults to the **floating alias** `gemini-2.5-flash`, stamped permanently into
`CorpusManifest.model_version`; #22's shipped mitigation pins **`gemini-2.5-flash-001`** and says *"never falling
back to the floating alias."*

* **(a) Pin to `gemini-2.5-flash-001`** (#22's exact `REAL_MODEL_ID`), consistent with the seed script, and
  confirm it resolves against `models.list` before the run — the procedure `real-llm-verification.md` already
  documents.
* **(b) Confirm the currently-served dated id first** (via a `models.list` call, which is essentially free) and
  pin to whatever that returns, which may or may not be `-001`.
* **(c) Accept the floating alias** for the corpus specifically, on the argument that the corpus is *synthetic
  document prose* and not an auditable decision artifact.
* **(d) Pin, and additionally record the SDK version** in the manifest the way #22's seed-script stamp does
  (`<model-id>+google-genai-<sdk-version>`) — noting that `CorpusManifest.model_version` is a plain `str`, so
  this needs no schema change to a frozen unit.

**Recommendation: (b) then (d).** (b) because **#18 is NARROWED specifically because `gemini-2.5-flash-001` is
unconfirmed against the live API** — pinning to an unverified id is the exact failure #18 declined to claim past;
a `models.list` call settles it at negligible cost and would *also* contribute to #18's outstanding verification.
(d) because the corpus manifest is a **freeze record** whose entire purpose is making the corpus reproducible and
falsifiable, and #22's argument (greedy ≠ bit-reproducible; bound the drift, stamp the provenance) applies to
corpus prose at least as strongly as to memo prose. **(c) is not recommended**: `documents_text` is inside the
manifest's `content_hash`, so prose drift changes the corpus's identity — a floating alias makes that drift
untraceable.

**[Answer]**: (b) then (d) — confirm the currently-served dated model id via a models.list call first (essentially free, and it also contributes to #18's outstanding verification), pin to whatever that returns, and stamp the manifest with model-id + SDK version per #22's precedent. Do not accept the floating alias: documents_text is inside the manifest's content_hash, so prose drift changes the corpus's identity and a floating alias makes that drift untraceable.

---

### Q6 — Corpus scale: full 300+ immediately, or a pilot first?

PROJECT-BRIEF §4 specifies **300+ profiles at ~40/35/25**. `GenerationConfig.min_profiles` defaults to 300;
`skew_audit` enforces the band **±3pp** *and* the **8-item DATA-2 edge-case checklist**, conjunctively, as a
**blocking gate before freeze**.

* **(a) Full 300 immediately.** ≈900 calls for the corpus. Produces the artifact the brief actually specifies;
  the skew audit and edge checklist are only meaningful at real scale.
* **(b) A ~30-profile pilot first** (a tenth), to validate the pipeline end-to-end for ≈90 calls, then the full
  run. ⚑ **Verify before choosing this**: at `min_profiles=30` the per-class targets become 12/11/7 (largest
  remainder), and **phase A always emits the 8 required edge records first** — so a pilot is feasible on paper,
  but the **±3pp band is much harder to hit at N=30** (one profile is 3.3pp), and `required_edge_cases` may need
  the test-scoped subset the config explicitly permits (`config.py:16`: *"a **test-scoped** config may pass a
  satisfiable subset … the real tier-B corpus uses the default"*). **A pilot may therefore fail the skew audit
  for reasons that have nothing to do with the pipeline being broken** — which would be a misleading signal.
* **(c) A "shape pilot"** — run the full pipeline at N=300 with the **offline capturing double** (the one the
  tier-S `smoke()` path already uses), producing a **structurally complete corpus with placeholder prose at zero
  cost**, to validate freeze/manifest/hash/skew/edge-checklist and every downstream reader **before** spending on
  real prose. Then the real run is a pure prose swap.
* **(d) Full run, but with the dry-run counter from Q3 first**, so the exact call count is known before spending.

**Recommendation: (c), then (a) — and explicitly not (b) as the first step.** (c) is the strongest option on
disk: `CorpusGenerator.smoke()` and the `CapturingLLMClient` double **already exist**, the four gates and all
three `from_file` readers can be exercised against a full-size corpus for **zero calls**, and every failure mode
that is *not* about prose quality (skew band, edge checklist, hash stability, JSON round-trip, gate wiring,
`--cov` neutrality, file size) surfaces before any money moves. (b)'s ±3pp problem at N=30 is a genuine trap: a
pilot failing its skew audit would look like a broken pipeline when it is really an under-powered sample. If a
*paid* pilot is still wanted after (c), it should be sized by the band arithmetic, not by "a tenth". **Withheld**:
whether (d)'s counter is a prerequisite or a nice-to-have depends on Q3.

**[Answer]**: (c) then (a) — run the full N=300 pipeline with the offline capturing double first, at zero cost, to validate freeze/manifest/hash/skew-band/edge-checklist and every downstream reader; then the real run as a pure prose swap. Explicitly not (b): your ±3pp arithmetic at N=30 is convincing, and a pilot failing its skew audit for sample-size reasons would be a genuinely misleading signal.

> ⚑ **Ambiguity-check finding (v), MATERIAL — this answer is stronger than the recommendation knew.** Verified on disk: the `real_config` (N=300) fixture is used **only** to construct the `oracle` fixture. **No test anywhere calls `generate()` at N=300** — every generator test uses `test_scoped_config` (N=9, tolerance 50pp, a 2-edge subset). **The full-scale pipeline has NEVER been run at N=300, even offline**, so the ±3pp band and the full 8-edge DATA-2 checklist have never been satisfied by an actual run, only by `SkewAudit` unit tests over synthetic counts. The shape-pilot is therefore a **genuine experiment that may legitimately fail** (`SkewAuditError` / `BudgetExhaustedError`) — the code-gen plan must define that failure branch rather than predict success.

---

### Q7 — What happens to the corpus artifact once it exists?

§1.1 Divergence C: `.gitignore` has **no `corpus/` entry**, so the artifact is committable by default and nothing
has decided whether it should be. Rough size: 300 records × (a full `ApplicantProfile` + **three** LLM-authored
prose documents) + a manifest — plausibly **several MB of JSON**.

* **(a) Commit it.** Makes the corpus **frozen, versioned, reviewable and reproducible-by-inspection**, which is
  what `CorpusManifest`'s `content_hash` and the word *"frozen"* throughout U14 imply. Consistent with the
  brief's replayability and auditability principles. Costs repo size, and every regeneration is a large diff.
* **(b) Gitignore it**, treating the corpus as a build artifact regenerated from `seed` + `manifest`. Keeps the
  repo lean. ⚑ **But regeneration is not actually deterministic across time**: the *profiles* are seeded and
  reproducible, while the **prose is LLM-generated** and subject to exactly #22's drift — so a regenerated corpus
  may have a **different `content_hash`**, and "reproducible from the seed" would be **false for the prose half**.
* **(c) Commit the manifest only**, gitignore `profiles.json`. Small diff, permanent provenance record — but the
  manifest alone cannot reconstruct the corpus, so it documents an artifact nobody else can obtain.
* **(d) Commit it under Git LFS** or an equivalent, if size is the binding objection.

**Recommendation: (a), with the size measured at Q6(c)'s zero-cost dry run before finalising.** The decisive
argument is (b)'s hidden flaw: **the corpus is not regenerable bit-identically**, because its prose comes from a
real model — the same #22 finding, applied to U14. An artifact that cannot be regenerated and is not committed is
an artifact that **effectively ceases to exist** the moment the working directory is cleaned, and every
downstream claim ("the gates passed over the real corpus") becomes unfalsifiable. That directly contradicts the
project's full-auditability invariant. **If size turns out to be prohibitive**, (d) is the fallback; (c) is the
weakest option and is not recommended.

**[Answer]**: (a) — commit the corpus, with size measured at Q6(c)'s zero-cost run before finalizing. Your argument is decisive: the corpus is not bit-identically regenerable because its prose comes from a real model (the same #22 finding applied to U14), so an uncommitted corpus effectively ceases to exist on a clean checkout and every downstream claim becomes unfalsifiable. If size proves prohibitive, (d) Git LFS is the fallback; (c) manifest-only is not acceptable.

> ⚑ **Ambiguity-check (vi) confirms this needs NO `.gitignore` edit**: `git check-ignore corpus/profiles.json` returns **not ignored** — the `build/` rule matches only directories named `build`, and no rule matches `corpus/`. `secrets_config/tests/test_governance.py::test_gitignore_lists_dotenv` is therefore untouched.

---

### Q8 — Where does the tier-B evaluation entrypoint live, and what exactly does it do?

§1.4: there is **no llm-judge entrypoint, no gate entrypoint, and no `CorpusRecord` → `JudgedSample` bridge**.
C-1 forbids putting any of it inside `backend/llm_judge/`.

The missing chain, stated precisely:
`CorpusRecord.profile` → `RulesEngine.evaluate()` → `RuleResultReport` → `MemoAgentInputBuilder.build()` →
`LangGraphOrchestrator.run()` → `DecisionMemo` → `JudgedSample(memo, rule_report, provider)` → `run_eval(...,
engine, tier=EvalTier.LIVE)` → `EvalRunResult`.

* **(a) One script under `backend/scripts/`** (e.g. `run_tier_b_eval.py`) doing the whole chain, mirroring
  `seed_demo_cases.py::_SeedSeams` — which **already performs the profile → report → memo half** — but assembling
  `JudgedSample`s **in memory** and writing an `EvalRunResult` report to disk, instead of writing to Postgres.
* **(b) Two scripts** — one that drafts memos over the corpus and freezes them to disk (`memos.json`), one that
  loads and judges them. **For**: the drafting spend (300–600 calls) is preserved across judge re-runs, so
  iterating on the rubric or the engine costs only the judging calls; and a crash in judging does not waste the
  drafting spend. **Against**: a second on-disk artifact with its own shape, versioning and Q7-style disposition
  question.
* **(c) Extend `seed_demo_cases.py`** with a corpus-driven mode. **Against**: it is a *demo seed* script with a
  Postgres dependency and a very loud placeholder-memo contract; overloading it muddies both purposes.
* **(d) Defer** the entrypoint question until Q1/Q2 settle, since its shape depends on both.

**Recommendation: (b), with the Q7 disposition question applied to the intermediate memo artifact too.**
Grounded in the cost structure: drafting is the **second-largest spend** (300–600 calls) and is **completely
independent of the judge engine**. If Q2's engine choice, the judge prompt, or the rubric needs a second attempt
— which is likely, since neither has ever been exercised against a real model — (a) forces re-paying for drafting
every time, while (b) makes iteration cost only the judging calls. Freezing drafted memos also makes the eval
**re-runnable and auditable**, which is the same argument that makes the corpus worth freezing. **Withheld**: the
exact on-disk shape of the memo artifact — `DecisionMemo` is a frozen U4 Pydantic model and round-trips cleanly,
but whether the artifact stores bare memos or `(memo, rule_report, provider)` triples is a design detail that
belongs in the code-gen plan, not here.

**[Answer]**: ⚑ **DEFERRED-PENDING-STAGE-2-AUTHORIZATION — NOT ANSWERED IN THIS PASS.** Verbatim: *"Deferred — not answered in this pass, for the same reason as Q2. The evaluation entrypoint is Stage 2/3 territory and its shape depends on Q2's engine choice. Record as deferred-pending-Stage-2-authorization. Your (b) two-script recommendation and its cost-structure reasoning should be preserved verbatim for when it's live."*

> **The (b) recommendation and its cost-structure reasoning above are PRESERVED VERBATIM and remain live for the Stage-2 pass.** ⚑ Note that Stage 1 **does** build a `backend/scripts/` corpus entrypoint (Q4-b) and a gate-runner path (Q10 floor) — neither of which pre-commits this question, because the *evaluation* entrypoint (memo drafting + judging) is a distinct artifact that Stage 1 does not create.

---

### Q9 — How many corpus entries actually get drafted and judged?

Nothing requires the judged sample set to equal the corpus. The corpus is sized for **statistical** purposes
(outlier detection, rule coverage, skew); the judge gate is an **aggregate mean over in-gate samples** with a
`>= 4` threshold (`pipeline.py::meets_threshold`).

* **(a) All of it** — draft and judge every corpus entry. 300–600 + 300 calls. Maximum evidence; maximum spend.
* **(b) A stratified subsample** — e.g. 60 entries drawn proportionally across APPROVE / REFER /
  DECLINE-RECOMMEND **and** deliberately including all 8 DATA-2 edge cases, since edge cases are where
  groundedness is most likely to fail. ≈60–120 + 60 calls. ⚑ **Note**: `run_eval` takes whatever sample list it
  is handed and computes the mean — so a subsample produces a **statistically valid but narrower** claim, which
  must be stated as such in the report (*"AC-6 measured over a stratified 60-sample subset"*, never *"over the
  corpus"*).
* **(c) Edge cases only** — the 8 DATA-2 records plus a small control group. Cheapest; deliberately adversarial;
  but a mean over a hard-case-only set is **not** what AC-6 describes and would understate the system.
* **(d) A tiered approach** — (b) first; escalate to (a) only if the subsample lands near the 4.0 boundary where
  a larger sample would actually change the verdict.

**Recommendation: (d), with (b)'s stratification.** Two grounded reasons. (i) **The threshold is a mean, so
precision matters only near the boundary** — a subsample scoring 4.6 or 3.2 will not flip at N=300, and paying
5× for a decimal place is poor value; a subsample scoring 4.05 genuinely warrants the full run. (ii)
**Stratification is not optional here** — `rejection_sampler` phase A always emits the 8 edge records first, so
they are identifiable in the corpus, and omitting them would produce a flattering-but-unrepresentative score,
which cuts against this project's consistent preference for honest findings. **Non-negotiable regardless of the
answer**: whatever sample set is used must be **named and counted in the report**, and the AC-6 claim must be
scoped to it exactly.

**[Answer]**: ⚑ **DEFERRED-PENDING-STAGE-2-AUTHORIZATION — NOT ANSWERED IN THIS PASS.** Verbatim: *"Deferred — Stage 3 territory, not needed for Stage 1. Preserve the (d)-with-(b)-stratification recommendation and the non-negotiable point that whatever sample set is used must be named and counted in the report with the AC-6 claim scoped to it exactly."*

> **PRESERVED**: the (d)-with-(b)-stratification recommendation, and the **non-negotiable** requirement that whatever sample set is used be **named and counted in the report**, with the AC-6 claim **scoped to it exactly**.

---

### Q10 — Reproducibility and bias-swap at tier-B, given #22

The brief asks how §5.1's 100%-reproducibility and §5.2's bias-swap-delta-0 interact with #22's disclosed
memo-prose non-reproducibility. **§1.5 resolves most of this, and the answer is better than the question
assumes:**

**All four blocking gates are LLM-free.** `ReproducibilityGate` compares `evaluation_output()` projections across
10 runs of the **deterministic rules engine**; `BiasSwapGate` swaps `{full_name, gender, city}` and compares the
**engine recommendation**. Neither touches `narrative_prose`. **So running the real bias-swap and reproducibility
suites over the real corpus cannot surface #22's prose non-determinism — structurally, not by luck.** #22's own
framing (*"AC-1's 100% claim holds for the DECISION path; it is not claimable bit-exactly for MEMO PROSE"*) is
therefore **exactly right**, and the gates already measure the half that is claimable.

The genuinely open question is whether tier-B **additionally** runs a **prose-level** invariance check.

* **(a) Run the four existing gates over the real corpus, and nothing more.** #22 stays an accepted, disclosed,
  prose-scoped limitation. AC-1 and AC-3 are verified on the decision path, honestly scoped. Zero extra calls.
* **(b) Additionally run a prose-level bias-swap** — draft memos for both the original and demographic-swapped
  profiles and compare the prose. **Doubles the drafting spend.** ⚑ **And this is the risk the brief anticipated,
  confirmed real**: at `temperature=0` the prose will still differ across two calls for reasons that are ordinary
  LLM non-determinism, **and the swapped profile's prose legitimately differs anyway because the memo prompt
  contains the profile**. A naive diff would report a "bias delta" that is nothing of the kind. **If (b) is
  chosen, the comparison must be on a bias-relevant projection** (e.g. cited rule ids, or the recommendation the
  prose asserts) **and never on raw prose text** — otherwise it manufactures a false positive on the project's
  most reputationally sensitive gate.
* **(c) Additionally run a prose-level *reproducibility* probe** — draft the same memo N times and record how
  much the prose actually varies. Costs N× a small sample. **For**: it converts #22 from a reasoned prediction
  into a **measured** finding, which is strictly more honest and is exactly the kind of evidence this project has
  preferred. **Against**: it can only ever confirm the limitation, never remove it.
* **(d) (a) + (c)**, and explicitly not (b).

**Recommendation: (d).** (a) is the mandatory floor — it verifies AC-1 and AC-3 on the path where the claim
actually holds, for zero extra calls. (c) is cheap (a handful of calls on 2–3 samples) and turns #22 from
*"we reason this is true"* into *"we measured it and here is the variance"* — the same evidentiary upgrade #8 and
#18 were held to. **(b) is actively not recommended** unless it is scoped to a bias-relevant projection: as the
brief suspected, a raw-prose bias-swap at tier-B is the most likely way this entire exercise produces a
misleading result, and §5.2's *"any delta found = blocking bug, not a warning"* means a false positive there is
expensive. **The existing `BiasSwapGate` already discharges §5.2 correctly**, on the recommendation, which is
what §5.2 actually specifies (*"Decision recommendation must not change"*).

**[Answer]**: (d) — run the four existing gates over the real corpus (mandatory floor, zero extra calls, verifies AC-1 and AC-3 on the path where the claim actually holds), plus (c) the prose-level reproducibility probe when Stage 2/3 is authorized, since that converts #22 from a reasoned prediction into a measured finding. Explicitly not (b): your analysis of the false-positive risk on a raw-prose bias-swap is correct and that gate is too reputationally sensitive to manufacture a spurious delta on. Note that the (c) half is Stage-3-dependent; only the (a) floor applies to this authorization.

> **Scope split, recorded**: the **(a) floor is IN Stage 1**; the **(c) prose-reproducibility probe is DEFERRED to Stage 2/3** with the rest of the eval work. **(b) is rejected outright**, not deferred.

---

### Q11 — What do success and failure look like, and how is each recorded?

⚑ **C-4 makes this harder than it first appears.** §1.7(a): three frozen U22 tests hard-assert
`discharged is False`, and **U22's design provides no mechanism to flip it**. So *"the gate passed"* and *"the
register item is discharged"* are **two separate decisions**, and the second one collides with frozen tests.

**Sub-question 11a — how is a PASS recorded?**

* **(a) Documentation-only**, on the **#20 precedent** — record the result in `BUILD-COMPLETION-REPORT.md`,
  `guide-state.md` and `audit.md` as a register **UPDATE** section, leaving `DEFERRED_REGISTER`'s
  `discharged=False` **untouched** and disclosing plainly *why* (the frozen-test constraint), so the code and the
  documents do not contradict each other.
* **(b) Flip `discharged=True` and edit the three frozen tests** as an explicitly-authorized **matched pair** —
  the #13 shape. Makes the code self-describing; **requires editing frozen U22 tests**, which the standing HOLDS
  forbid without its own separate authorization.
* **(c) Defer the code-side flip** to a future authorized pass, doing (a) now and recording the matched pair as a
  **new register item** (the "#9/#10 discharge cannot be recorded in code" gap), on the #21/#22 precedent of
  spawning a residual rather than overclaiming.

**Sub-question 11b — what happens if the ≥4/5 gate does NOT pass?** The brief is explicit that this is not an
emergency, and the project's record supports that.

* **(a) Record the failing score as a first-class finding** — report the actual aggregate, the per-dimension
  breakdown, and the sample set — and **change nothing else**. AC-6 is recorded as **measured and not met**,
  which is strictly more informative than never having measured it.
* **(b) Record it and immediately iterate on the memo prompt** to raise the score. ⚑ **Note the collision**: the
  memo prompt is built by **U4's frozen `PromptBuilder`**, so this is a **frozen-P1 edit** — the same
  authorization #11 `FEWSHOT-ANCHOR-UNIMPLEMENTED` has been waiting on. It is not available as a quick fix.
* **(c) Record it and iterate on the *judge* side** (the rubric prompt, the engine's parsing) — legitimate if
  the failure is diagnosed as a **judging artifact** rather than a memo-quality problem, but requires the
  diagnosis to be made and stated honestly, not assumed.

**Recommendation: 11a → (c); 11b → (a).**
For **11a**, (c) is the only option consistent with both the HOLDS and the build's disclosure discipline: it
records the real outcome now, does not edit a frozen test, and does not leave a silent contradiction between a
passing gate and a `discharged=False` field — it names the gap as its own tracked item, exactly as #21 and #22
were spawned rather than absorbed.
For **11b**, (a) is strongly grounded in this project's own record: **#8 and #18 were both held to NARROWED
rather than DISCHARGED** specifically because the evidence fell short, and #22 was opened rather than smoothed
over. A failing AC-6 score measured over real memos is **more valuable than an unmeasured one**, and the
temptation to tune prompts until the number clears 4.0 is exactly the inflation this build has consistently
refused. ⚑ **Stated in advance, before any number exists**: whatever the score turns out to be, it is reported as
measured. **(b) is unavailable anyway** without a frozen-P1 authorization; if a fix is genuinely warranted after
diagnosis, it is its own scoping pass with its own gate.

**[Answer]**: 11a → (c); 11b → (a). For 11a: document the outcome now on the #20 precedent, leave DEFERRED_REGISTER's discharged=False untouched, disclose plainly why (the frozen-test constraint), and open the "#9/#10 discharge cannot be recorded in code" gap as its own new register item — the #21/#22 precedent of spawning a residual rather than overclaiming. For 11b: whatever the score turns out to be, it is reported as measured, stated in advance before any number exists. (b) is unavailable anyway without a frozen-P1 authorization.

> **Stage-1 scope note**: **11a applies to this authorization** — Stage 1's outcome for **#3** is recorded documentation-only, and the new "discharge-cannot-be-recorded-in-code" register item is opened as part of it. **11b concerns the AC-6 score, which Stage 1 does not measure**, so it binds the Stage-2/3 pass; it is recorded here **in advance, before any number exists**, exactly as the answer requires.

---

### Q12 — Provider breadth: Gemini only, or Gemini + Claude?

`IN_GATE_PROVIDERS = {GEMINI, CLAUDE}` and AC-6's aggregate spans in-gate samples. But §1.8 established that a
Claude-inclusive run needs **two things that do not exist**: a production implementation of
`ThinkingLLMClient` (a **different Protocol** from the one #18 implemented), and an `ANTHROPIC_API_KEY` field on
**frozen U16's `Settings`**, which currently declares six fields and does not include it.

* **(a) Gemini only.** Uses #18's existing, guarded, capped client. **Reopens nothing.** The eval report records
  `scored_count` over Gemini samples and states the scope honestly: *"AC-6 measured on the primary provider
  (Gemini); the secondary (Claude) is in-gate by design but was not exercised at tier-B."* Consistent with
  PROJECT-BRIEF §9's *"PRIMARY = Gemini … SECONDARY = Claude (tested fallback)"*, where "tested" refers to U19's
  offline adapter tests.
* **(b) Gemini + Claude.** Fuller AC-6 coverage and genuinely exercises the vendor-independence claim (§9's
  *"Model switch … Vendor independence proof"*). **Requires** a second production client for
  `ThinkingLLMClient`, an `ANTHROPIC_API_KEY` on frozen `Settings` (**a frozen-unit reopening**), a second API
  account and key, and **roughly doubles** the drafting spend for in-gate samples.
* **(c) Gemini now, Claude as a separately-scoped later pass**, so the vendor-independence claim is not dropped
  — just sequenced behind its own authorization.
* **(d) Gemini + a small Ollama exempt set**, to make `exempt_count` a **non-zero positive witness** over real
  data. ⚑ **Note**: `is_nonvacuous_exemption_set` is documented as *"a SET property, not a test-configuration
  opinion … nothing in production calls it as a gate"*, so a Gemini-only run with `exempt_count == 0` is
  **legitimate**, not a defect — but a run that includes an exempt sample demonstrates the partition working over
  real data.

**Recommendation: (c).** (b)'s cost is understated by the brief's framing: it is not "add a second provider", it
is *a second production client for a second Protocol, plus reopening frozen U16, plus a second vendor account,
plus double the drafting spend* — a scope comparable to register #18's entire pass, folded in as a side effect.
(a) is the correct content for **this** authorization; (c) is (a) with the Claude gap explicitly kept on the
books rather than quietly dropped, so §9's vendor-independence claim stays honest. **(d) is a reasonable
low-cost addition** if an Ollama endpoint happens to be available locally (it costs nothing per call), but it is
independent of the main decision and should not gate it.

**[Answer]**: (c) — Gemini only for this authorization, with the Claude gap explicitly kept on the books as a separately-scoped later pass rather than quietly dropped, so §9's vendor-independence claim stays honest. Your cost analysis is right that (b) is not "add a second provider" but a second production client for a second Protocol plus reopening frozen U16 plus a second vendor account — comparable in scope to #18's entire pass. (d) Ollama is a reasonable low-cost addition if an endpoint happens to be available locally, but it should not gate this.

---

## 4. HOLDS for this pass — all currently upheld

| Hold | Status |
|---|---|
| Scoping only — **no code generated** | ✅ upheld — no file under `backend/` or `frontend/` written or edited |
| **No API call, no money spent, no corpus generated** | ✅ upheld — the only external checks were read-only local ones (`node --version`, `npx --version`, `npm ls -g`, `import` probes); **`corpus/` still does not exist** |
| No edit to any frozen-23 unit's internals | ✅ upheld |
| **No edit to U22's frozen `DEFERRED_REGISTER` entries** | ✅ upheld — read only; §1.7(a) reports the flip constraint, changes nothing |
| WIRE-1's contract text not amended | ✅ upheld |
| `not_wired.py` not renamed | ✅ upheld (#13 stays open) |
| U23's frozen test not edited | ✅ upheld |
| `audit_store` Docker-guard gap untouched — **5 errors stay exactly 5** | ✅ upheld — suite not re-run this pass; state carried forward |
| No new route under `backend/app/routes/` | ✅ upheld |
| **#18's spend guardrails neither weakened nor bypassed by this pass** | ✅ upheld — `ALLOW_REAL_LLM_CALLS` never set, cap never changed; **any change is Q3's own decision with its own justification** |

**Carried forward, not re-run**: **1556 passed / 0 failed / 43 skipped / 5 errors / 99.87%**.
**Register unchanged at 22 tracked** — 17 open · 2 discharged (#2 partly, #20 fully) · 3 narrowed (#8, #18, #19).

---

## 5. What happens after the answers

1. **Mandatory ambiguity-check** against the answer set and §1's ground truth, on the #20 / #8 precedent — with
   at least these **directed checks**, each traced against actual disk content, not assumed:
   * **(i)** Does anything the answers imply land inside `backend/llm_judge/` and trip one of the four scans in
     §1.7(b)? (C-1.)
   * **(ii)** Does a new `corpus/` directory or a new `backend/scripts/` module perturb `--cov`, any structural
     file-set scan, the skip count, or **the 5 `audit_store` errors**? (`backend/scripts` was cleared by #8;
     `corpus/` is a **new top-level directory** and has **not** been cleared by any prior pass — this must be
     checked, not inherited.)
   * **(iii)** Does the Q4 entrypoint's construction of `CappedGeminiClient` collide with `test_llm_client.py`'s
     17 tests or with the offline-default guarantee (**the full suite must still run with no key, no network, no
     SDK and the flag unset**)?
   * **(iv)** Are there **other in-code assertions about tier-B** beyond the ones §1.2 found, that a real run
     would contradict? (The **#20 second-reference miss** is the precedent: one directed check caught a
     contradiction the ground-truth pass missed.)
2. **A separate code-gen plan** (`tier-b-authorization-code-gen-plan.md`) — component inventory, TDD leaf-first
   order, RED-before-GREEN, **advance predictions for pass/skip/error/coverage counts**, an explicit **dry-run /
   cost-confirmation step before any billable call**, and an explicit **DISCHARGED-vs-NARROWED-vs-documentation-
   only** section per Q11.
3. **A second, explicit spend gate** at the moment of the first real call — the dry-run count and the
   per-stage caps confirmed against the estimate in §1.5 **before** any money moves.
4. **Register update** per Q11's answer, superseding — never rewriting — the historical §5 rows for #3, #9, #10.

**⚑ This document authorizes nothing. STOPPING at the plan-file gate.**

---

## 6. MANDATORY AMBIGUITY-CHECK — RUN against the Q1–Q12 answer set + §1 ground truth

**Six directed checks** — the four this plan's §5 anticipated, plus **(v)** and **(vi)** requested at the answer
gate. Every one traced against **actual disk content**, never assumed. **Result: CLEAN — with two findings
SURFACED (not absorbed) and two implementation constraints discovered.**

### (i) Does anything the answers imply land inside `backend/llm_judge/`, or trip a sibling unit's scan? — ✅ **CLEAN**

Q1(a) scopes this authorization to **Stage 1 only**, which touches U22 **not at all**. Q4(b) places the corpus
entrypoint in `backend/scripts/`, already cleared by #8's ambiguity-check as outside every structural file-set
scan **and** outside every `--cov=` target. Sibling scans re-verified for the gate-runner path:

* `quality_gates/tests/test_reference_not_own.py` scans `_SRC_DIR.glob("*.py")` where `_SRC_DIR =
  backend/quality_gates` — **a `backend/scripts/` runner is outside it.**
* `quality_gates/tests/test_blocking_form.py`'s `_GATE_TEST_MODULES` is a **fixed four-name list**
  (`test_bias_swap_suite.py`, `test_reproducibility_suite.py`, `test_rule_coverage_report.py`,
  `test_coverage_gate.py`) — nothing new is auto-enrolled.

⚑ **Constraint recorded for implementation**: BLOCKING-1 flags any `@skip`/`@xfail` decorator or module-level
`pytestmark` on a listed gate test module. **The real-corpus gate run must therefore be a SCRIPT, not a
corpus-presence-skipped pytest test added to that list.** Q10's floor is satisfied by a runner under
`backend/scripts/`, which sidesteps this entirely.

### (ii) Does a new top-level `corpus/` perturb `--cov`, any file-set scan, the skips, or **the 5 `audit_store` errors**? — ✅ **CLEAN, verified not inherited**

This directory has been cleared by **no prior pass**, so every element was checked fresh:

* **pytest collection** — `pyproject.toml` `testpaths = ["backend"]`. `corpus/` is outside it and contains **no
  `.py`**. Not collected.
* **Coverage** — `--cov=` names 17 specific **packages**; `corpus/` is data. **Coverage-invisible.**
* **Repo-root enumeration** — a grep for `REPO_ROOT.iterdir` / `.glob(` / `.rglob(` on a root path across
  `backend/` returns **nothing**. **No test enumerates repo-root children.**
* **U23's artifact scan** — `deploy_config/tests/structural.py`'s `U23_ARTIFACTS` is a **fixed explicit list**
  of eight paths; `corpus/` is not among them and nothing globs for more.
* ⚑ **The two "no `corpus/`" tests were read in full, and both use `tmp_path`, NOT the repo root.**
  `outlier_model/tests/test_corpus_source.py::test_default_path_needs_no_corpus_file(tmp_path)` asserts
  `not list(tmp_path.iterdir())` — **the pytest temp dir being empty**, not the repo's `corpus/`.
  `quality_gates/tests/test_corpus_loader.py` likewise writes its own `tmp_path/profiles.json`. **A real
  `corpus/` at repo root breaks neither.** This is precisely the assumption that had to be checked rather than
  inherited.

**Conclusion: skips unchanged, and the 5 `audit_store` Docker-absence errors stay exactly 5.**

### (iii) Does the Q4 entrypoint collide with `test_llm_client.py` or the offline-default guarantee? — ✅ **CLEAN**

All **17** tests target `backend/app/llm_client.py` itself and use `monkeypatch` for the flag (per-test isolated).
Two constraints, both compatible with Q3's answer as written:

* `test_the_cap_default_is_20` pins the **default** — Q3's *"caps move up only by explicit argument, never by
  changing a default"* is exactly what keeps this green. The new entrypoint passes `max_calls=` **explicitly**.
* `test_the_module_imports_without_the_sdk_installed` — the new entrypoint must likewise **not import
  `google.genai` at module scope**; it inherits the lazy import inside `build_gemini_client`.

**Offline-default guarantee preserved**: the entrypoint is opt-in and out-of-band, never collected, so the full
suite still runs with **no key, no network, no SDK, and the flag unset**.

### (iv) Other in-code assertions about tier-B that a real Stage-1 run would contradict? — ⚑ **ONE ACTIONABLE FINDING + FOUR FROZEN STALENESS LOCATIONS** (the #20 / #8 precedent firing again)

**Verified first: none of these substrings is asserted by any test.** A grep for `not authorized` / `NOT
authorized` across `test_*.py` returns **no assertion lines** — `test_evaldefer.py` asserts on
`discharge_criteria`, `test_clidefer.py` on the *promptfoo* rationale's `npx`/`unpinned`/`telemetry` tokens, and
`test_governance.py` on `DOCUMENTATION ONLY` / `never enforcement`. **So these are prose-stale, not
test-breaking.**

**⚑ ACTIONABLE — non-frozen, editable, would contradict the change the moment it lands:**

* **`backend/scripts/seed_demo_cases.py:97`** — *"the only real adapter (`corpus_generator/build.py`) is a
  **tier-B entrypoint that is not authorized**."* After Q1(a) + Q4(b) this is **doubly false**: tier-B corpus
  generation is authorized, **and** `build.py` is no longer the only real adapter (a guarded
  `backend/scripts/` entrypoint exists, and `backend/app/llm_client.py` already superseded the claim in part).
  `backend/scripts/` is **non-frozen** — this is exactly the `render.yaml`-comment / `reconcile_committing_
  cases.py:44` shape. **SURFACED, NOT ABSORBED** — folded into the Stage-1 code-gen plan as **explicitly-flagged
  scope for plan-gate approval**, beyond the literal text of any answer.

**FROZEN — must NOT be edited (standing HOLDS); handled by supersede-not-rewrite:**

| Location | Text that goes stale |
|---|---|
| `llm_judge/engine.py:88` (inside `JUDGE_EVAL_DEFERRED.rationale`) | *"tier-B is NOT authorized and is NOT required for U22's completion"* |
| `llm_judge/schemas.py:52` (`EvalTier` docstring) | *"tier-B NOT authorized, NOT required for U22's completion"* |
| `llm_judge/tests/test_governance.py:7` · `test_evaldefer.py:4` | *"the tier-B corpus (NOT authorized)"* |
| `case_lifecycle/tests/test_governance.py:6` | *"the tier-B corpus (NOT authorized)"* |

⚑ **A precise nuance, stated rather than overstated.** After Stage 1, the accurate position is **"tier-B corpus
generation is authorized; tier-B judge evaluation is NOT"**. So `JUDGE_EVAL_DEFERRED`'s claim remains
**substantially true for its own subject (#10)** — only the blanket phrase *"tier-B is NOT authorized"* becomes
imprecise. **This is mild staleness, not a contradiction**, and it is disclosed in the register update rather
than corrected in frozen code.

### (v) Can the Q6(c) offline shape-pilot actually run today with `google-genai` absent? — ✅ **CLEAN on the SDK question, ⚑ with a MATERIAL new finding**

**Verified LIVE, not assumed** — a read-only import probe in this environment:

```
CorpusGenerator + BiasSwapGate + ReproducibilityGate + RuleCoverageGate + CoverageWiringGate
  -> imports OK        'google.genai' in sys.modules: False
```

**The capturing-double path genuinely needs no SDK.** `CorpusGenerator` takes `llm_client` as a constructor
parameter and `memo_agent_core.provider` does not import the SDK at module scope — confirmed by the whole suite
already running green with `google-genai` absent.

⚑ **MATERIAL FINDING — the full-scale pipeline has NEVER been run at N=300, even offline.** The `real_config`
fixture (N=300, ±3pp, all 8 DATA-2 edges) is used **only** to construct the `oracle` fixture; **no test calls
`generate()` at N=300.** Every generator test uses `test_scoped_config` (N=9, `tolerance_pp=50`, a **two-edge**
subset), whose own docstring says it *"NEVER asserts the real 40/35/25 band or the full DATA-2 checklist."* So
the ±3pp band and the 8-edge checklist have **only ever been satisfied by `SkewAudit` unit tests over synthetic
counts**, never by an actual generation run.

**Consequence, folded into the code-gen plan**: the shape-pilot is a **genuine experiment with a real failure
mode** (`SkewAuditError` if the band is unmet, `BudgetExhaustedError` if `attempt_budget` is exhausted). The plan
**must not predict success** — it must define the failure branch. This makes Q6(c) **more** valuable than its
recommendation credited: it is the cheapest possible place to discover a genuine pipeline limit, at **zero
spend**.

⚑ **Second constraint**: `CapturingLLMClient` lives in `backend/corpus_generator/tests/conftest.py`. A
`backend/scripts/` entrypoint must **define its own local offline double** (the
`seed_demo_cases.py::_OfflineLLMClient` precedent) rather than import a frozen unit's `conftest`.

### (vi) Does committing the corpus interact with `.gitignore`'s `build/` rule, or any repo-size / file-count assertion? — ✅ **CLEAN, with one adjacent constraint**

* **`corpus/` is NOT gitignored.** `git check-ignore -v corpus/profiles.json` → **not ignored** (non-zero exit).
  The `build/` rule matches only directories **named** `build`. **Q7(a) requires NO `.gitignore` edit at all**,
  so `secrets_config/tests/test_governance.py::test_gitignore_lists_dotenv` (which asserts `.env` is a line in
  `.gitignore`) is **untouched**, as is `test_dotenv_not_git_tracked`.
* **No repo-size or file-count assertion exists anywhere.** A grep for `st_size` / `getsize` /
  `len(list(...glob` across `backend/` returns only `profile_count` **manifest-field** references — a corpus
  property, not a repo-filesystem assertion.
* ⚑ **ADJACENT CONSTRAINT DISCOVERED (binding, recorded on Q3 above)**:
  `secrets_config/tests/test_governance.py::test_env_example_matches_settings_fields` asserts `.env.example`'s
  **active** keys **exactly equal** `Settings.model_fields`. `ALLOW_REAL_LLM_CALLS` passes today **only because
  it is commented out**. **Any new Stage-1 switch must be a CLI argument or a commented line — never a new
  active `.env.example` key**, which would break a frozen U16 test.

### Ambiguity-check verdict

**CLEAN.** No blocker. Two findings **surfaced and not absorbed** — the `seed_demo_cases.py:97` doc-staleness
(flagged for plan-gate approval) and the never-run-at-N=300 discovery (which reshapes the shape-pilot's framing
from validation to experiment). Two implementation constraints discovered — **no new active `.env.example`
key**, and **a locally-defined offline double**. Both are carried into the Stage-1 code-gen plan.

---

## 7. ⚑ INCIDENTAL FINDING — a CANDIDATE NEW REGISTER ITEM, deliberately NOT fixed in this pass

**This is a real and entirely separate problem from tier-B.** Surfaced during this pass's git checks; recorded
here for a decision **after tier-B Stage 1 completes**, per instruction. **No fix attempted, no `.gitignore`
edit made.**

### `GUIDE-DOCS-BUILD-GITIGNORED` — every BUILD-phase artifact is invisible to git

| | |
|---|---|
| **What it is** | `.gitignore:19`'s **`build/`** rule — written under the `# Node / frontend` heading alongside `node_modules/` and `dist/`, and plainly **intended for frontend build output** — is an **unanchored directory pattern**, so it matches **`guide-docs/build/` at any depth**. Confirmed: `git check-ignore -v guide-docs/build/plans/x.md` → **`.gitignore:19:build/`**. `git ls-files guide-docs/build/plans/` returns **nothing**. |
| **Blast radius** | **The entire BUILD phase of the project.** All 24 unit directories under `guide-docs/build/` — every `functional-design/`, `nfr-requirements/`, `nfr-design/`, `infrastructure-design/` and `code/code-summary.md` — plus **all 100+ files in `guide-docs/build/plans/`**, including every `fix-register-*` plan and **this document**. The DISCOVER phase (`guide-docs/discover/`), `guide-state.md` and `audit.md` are **unaffected** — they are tracked, which is why the gap has never been visible in `git status`. |
| **Why it matters** | The GUIDE-AI-SDP methodology treats these as **first-class deliverables** and the project's audit trail treats them as evidence. A clean checkout of this repository reproduces **the code and the DISCOVER phase but none of the BUILD design record** — every approval gate, every plan, every code summary, every NFR target. For a project whose thesis is full auditability, that is a material gap. |
| **Why it is NOT fixed here** | (1) **Out of scope** — it has nothing to do with tier-B, and folding an unrelated repo-wide change into a spend authorization is exactly the bundling this build has consistently refused. (2) **It is not risk-free**: `secrets_config/tests/test_governance.py` reads `.gitignore` and runs `git ls-files`, so the change needs its own verification pass. (3) **The correct fix is a real decision, not a default** — anchor the rule (`/frontend/build/` or `dist/`-only), or add a negation (`!guide-docs/build/`), or move the docs; and separately, whether to retroactively commit ~100 existing files is its own call. |
| **Suggested owner** | repo hygiene / housekeeping — adjacent to register **#12** (`testresults.txt` append-vs-overwrite), the register's other housekeeping item |
| **Blocking?** | **Non-blocking** for behaviour — no test reads these files and no code imports them. A **real reproducibility and audit-trail gap**, not a correctness defect. |

**Recommended disposition**: open as a **new register item after Stage 1 closes**, so the register count changes
once for tier-B and once for this, rather than entangling the two. **No action taken in this pass.**
