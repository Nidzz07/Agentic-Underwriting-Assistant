# TIER-B STAGE 1 — CODE GENERATION PLAN

**Authorized by**: `tier-b-authorization-plan.md`, **Q1(a) — Stage 1 ONLY**
**Answers realized**: Q1(a) · Q3(b)+dry-run · Q4(b) · Q5(b)→(d) · Q6(c)→(a) · Q7(a) · Q10(a)-floor · Q11a(c) · Q12(c)
**Deferred, NOT realized here**: **Q2**, **Q8**, **Q9** (DEFERRED-PENDING-STAGE-2-AUTHORIZATION) · Q10's (c) probe
**Register items touched**: **#3** (the subject) · **#18** (partial contribution via Q5b) · **#22** (inherited, disclosed)
**Register items NOT touched**: **#9**, **#10** — Stages 2 and 3 are **NOT authorized**
**Date**: 2026-07-23 · **Status**: 🟡 **PLAN ONLY — no code generated, no API call, no spend, no corpus**
**Ambiguity-check**: **RUN and CLEAN** — six directed checks, `tier-b-authorization-plan.md` §6

---

## 0. Scope fence — what this plan is allowed to do

**IN**: a guarded corpus entrypoint under `backend/scripts/`; a four-gate runner under `backend/scripts/`; their
tier-U tests; a zero-cost offline shape-pilot; a zero-cost dry-run cost confirmation; the model-id confirmation;
**one** real corpus generation run; the four-gate run over it; the corpus commit; the register update.

**OUT — explicitly**: no memo drafting, no judge evaluation, no `RubricEngine` adapter, no promptfoo decision, no
`EvalTier.LIVE` consumer, no prose-level reproducibility probe, no Claude/Ollama path. **Stages 2 and 3 are not
authorized and nothing here anticipates them beyond leaving the corpus where they would read it.**

---

## 1. Component inventory

| # | Component | Path | Kind | Coverage |
|---|---|---|---|---|
| **C1** | Guarded tier-B corpus entrypoint | `backend/scripts/build_corpus.py` | **NEW** production script | **invisible** — `backend/scripts` is not a `--cov=` target |
| **C2** | Four-gate runner over a frozen corpus | `backend/scripts/run_quality_gates.py` | **NEW** production script | **invisible** — same |
| **C3** | C1's tier-U contract tests | `backend/scripts/tests/test_build_corpus.py` | **NEW**, 9 tests | counted as passes |
| **C4** | C2's tier-U contract tests | `backend/scripts/tests/test_run_quality_gates.py` | **NEW**, 6 tests | counted as passes |
| **C5** | The frozen corpus artifact | `corpus/profiles.json` + `corpus/manifest.json` | **NEW** data, committed (Q7-a) | n/a — no `.py` |
| **C6** | Gate evidence reports | `corpus/gate-reports/*.json` | **NEW** data | n/a |
| **C7** | ⚑ **FLAGGED** — adjacent doc-staleness fix | `backend/scripts/seed_demo_cases.py:97` docstring | edit, **non-frozen** | docstring only |
| **C8** | Register + state + audit updates | `BUILD-COMPLETION-REPORT.md`, `guide-state.md`, `audit.md` | doc | n/a |

**Scaffolding already present** (created by #8): `backend/scripts/__init__.py`, `backend/scripts/tests/__init__.py`.
**No new dependency is declared.** `google-genai>=1.0.0` is **already in `requirements.txt`** (#18) — it is merely
**not installed in this environment** (§4 Step 8 prerequisite).

**⚑ C7 is explicitly flagged as beyond the literal text of any Q1–Q12 answer.** It is the ambiguity-check's
actionable finding (§6(iv) of the authorization plan) and requires **explicit approval at this plan's gate**,
exactly as `deploy/README.md` did in #8's pass.

---

## 2. C1 — `backend/scripts/build_corpus.py` (Q4-b, Q3, Q5, Q6)

**Three modes, safest by default.** Mirrors `seed_demo_cases.py`'s established shape (offline default, `--real-llm`
opt-in, explicit cap argument, loud banner).

| Mode | Flag | Cost | What it does |
|---|---|---|---|
| **dry-run** | `--dry-run` | **ZERO** | Runs the sampler + skew audit (**pure Python**), then reports the exact call count `3 × len(sampled)` and exits **without generating any prose and without writing any file**. |
| **offline** (DEFAULT) | *(none)* | **ZERO** | Full pipeline with a **locally-defined offline double**; writes to `--out`. This is Q6(c)'s shape-pilot. |
| **real** | `--real-llm` | **BILLABLE** | Constructs `CappedGeminiClient` via `build_gemini_client(settings, model_id=…, max_calls=…)` and injects it into `CorpusGenerator`. |

**Guardrail contract (Q3-b), stated precisely:**

* The real path goes **exclusively** through `build_gemini_client`, so it inherits **both** #18 gates —
  `ALLOW_REAL_LLM_CALLS == "true"` **exactly**, and the non-empty-key fail-closed check.
* **Two independent opt-ins**, the seed-script pattern: the `--real-llm` flag **and** the environment gate.
* `--max-llm-calls` is **REQUIRED on the real path** (no default) and passed **explicitly** to
  `build_gemini_client`. ⚑ **The `max_calls=20` default in `backend/app/llm_client.py` is NOT changed** —
  `test_the_cap_default_is_20` stays green (ambiguity-check (iii)).
* **The corpus-stage cap is set deliberately**, from the dry-run's measured count plus headroom — **not** a round
  number and **not** a global default.
* ⚑ **No new active `.env.example` key** — every switch is a **CLI argument** (ambiguity-check (vi); a new active
  key would break frozen U16's `test_env_example_matches_settings_fields`).

**Model-id contract (Q5):** `--model-id` is **REQUIRED on the real path with no default**, and the script
**refuses a known floating alias** (`gemini-2.5-flash` bare). The manifest stamp follows #22's precedent —
`model_version = "<model-id>+google-genai-<sdk-version>"`, which needs **no frozen-unit change** because
`CorpusManifest.model_version` is a plain `str`. ⚑ Because `GenerationConfig.model_id` feeds **both** the SDK call
and the stamp, the stamp is assembled by passing the composed string where the manifest builder reads it; the
exact mechanism is a Step-2 implementation detail, and if it cannot be done **without touching a frozen unit**,
the fallback is to stamp the bare pinned id and **disclose the SDK version alongside in the run record** rather
than force a frozen edit.

**Offline double**: defined **locally in C1** (the `seed_demo_cases.py::_OfflineLLMClient` precedent). ⚑ It does
**not** import `CapturingLLMClient` from `backend/corpus_generator/tests/conftest.py` — a production script must
not depend on a frozen unit's test tree (ambiguity-check (v)).

**SEC-3**: the key is read only inside `build_gemini_client` off `get_settings()`; C1 never holds, logs or prints
key material, and never prints a prompt.

---

## 3. C2 — `backend/scripts/run_quality_gates.py` (Q10's floor)

Runs **all four blocking gates over a frozen corpus**. **Zero LLM calls** — this is §1.5's finding realized.

```
CorpusLoader.from_file(corpus/profiles.json)        -> list[CorpusRecord]
CorpusLoader.profiles(records)                      -> list[ApplicantProfile]
CorpusManifest.model_validate(corpus/manifest.json) -> manifest        # see gap note
rulebook_version = CorpusLoader.manifest_version(manifest)             # QG-Fold-2

BiasSwapGate(engine).run(profiles, rulebook_version)          -> BiasSwapReport
ReproducibilityGate(engine).run(profiles, rulebook_version)   -> ReproducibilityReport   # runs=10 default
RuleCoverageGate(engine, loader).run(profiles, rulebook_version) -> RuleCoverageReport
CoverageWiringGate(pyproject.toml).run()                      -> CoverageGateReport
```

**⚑ Gap found and named, not silently patched**: `CorpusLoader` has `from_file` (profiles) and
`manifest_version(manifest)` — but **no manifest-file loader**. C2 therefore parses `manifest.json` itself via
`CorpusManifest.model_validate(json.loads(...))`. This is legitimate: C2 sits **outside** `backend/quality_gates/`,
so QG's REFNOTOWN scan (`_SRC_DIR.glob("*.py")`) does not apply, and it re-implements nothing — it calls the frozen
Pydantic model. **Recorded so it is a visible choice, not an accident.**

**Blocking form**: any gate reporting `passed is False` → **non-zero exit**, fail-loud (the `run_migrations.py`
precedent). ⚑ **C2 is a SCRIPT, not a pytest test** — deliberately, per ambiguity-check (i): adding a
corpus-presence-skipped test to `quality_gates/tests/` would be flagged by **BLOCKING-1**
(`test_blocking_form.py` forbids `@skip`/`@xfail` on its four listed modules).

**Evidence**: each gate's report is written via its `to_json(generated_at=…)` envelope to `corpus/gate-reports/`.
The provenance stamp is a **serialization envelope, never a model field** (EVIDENCE-1), so reports stay
field-equal across runs.

---

## 4. Execution steps — TDD leaf-first, RED before GREEN, **cost gates explicit**

> **Steps 0–6 and 7 cost NOTHING.** The **first** billable call is at **Step 9**, behind **two** explicit stops.

| Step | What | Cost | Gate |
|---|---|---|---|
| **0** | Scaffolding check; **confirm the live baseline** `1556 / 0 / 43 / 5 / 99.87%` before any change | none | — |
| **1** | **RED** — write C3's 9 tier-U tests; confirm they fail at import (`build_corpus` absent) | none | — |
| **2** | **GREEN** — implement C1; all 9 pass | none | — |
| **3** | **RED** — write C4's 6 tier-U tests; confirm they fail | none | — |
| **4** | **GREEN** — implement C2; all 6 pass | none | — |
| **5** | **Full suite**; reconcile against §5's advance predictions | none | **any divergence is a FINDING, not a number to correct** |
| **6** | ⚑ **OFFLINE SHAPE-PILOT** — `python -m backend.scripts.build_corpus --out .tmp-corpus` at **N=300** | **ZERO** | **A GENUINE EXPERIMENT — see §6** |
| **7** | ⚑ **DRY-RUN COST CONFIRMATION** — `--dry-run`; reports the exact billable call count | **ZERO** | ⛔ **STOP — user confirms the number and the cap before proceeding** |
| **8** | Install `google-genai`; **`models.list`** to confirm the served dated model id (Q5-b) | **~free metadata call** | ⛔ **STOP — first network call; needs its own confirmation** |
| **9** | ⚑ **THE REAL RUN** — `--real-llm --model-id <confirmed> --max-llm-calls <from Step 7>` with `ALLOW_REAL_LLM_CALLS=true` | **BILLABLE** | only after 7 **and** 8 confirmed |
| **10** | **Four-gate run** over the real corpus (C2) | **ZERO** | — |
| **11** | Corpus commit per Q7-a, with the size measured at Step 6 | none | LFS fallback if prohibitive |
| **12** | ⚑ **FLAGGED** C7 — `seed_demo_cases.py:97` docstring | none | **plan-gate approval required** |
| **13** | Register update per Q11a + the new register item + full suite re-run | none | — |

**Step 8 prerequisite, named explicitly**: `google-genai` is **declared in `requirements.txt` but NOT installed
here** (verified live). Installing it is an **environment change**, not a code change, and it makes
`corpus_generator/build.py` — the **unguarded** entrypoint Q4(b) deliberately leaves in place — importable for the
first time. **That is the disclosed cost of Q4(b) and is restated here at the moment it becomes real.**

---

## 5. Advance predictions — stated BEFORE execution

| Metric | Baseline (carried, Step 0 re-confirms) | **Predicted after Step 5** | Why |
|---|---|---|---|
| Passed | 1556 | **1571** | **+15** tier-U (9 C3 + 6 C4) |
| Failed | 0 | **0** | — |
| Skipped | 43 | **43** | no new skip-guarded test; C2 is a script, not a test |
| **Errors** | **5** | **5** | ⚑ same `audit_store` Docker-absence names — **nothing here touches that guard** |
| Coverage | 99.87% | **99.87%** | `backend/scripts` is **not** a `--cov=` target — C1/C2 are coverage-invisible, exactly like `run_migrations.py` |

**After Step 13** (no further code): **1571 / 0 / 43 / 5 / 99.87%**, unchanged from Step 5.

⚑ **Honest note on the coverage figure**: C1 and C2 are **test-covered but never counted**. The 99.87% must not be
read as covering them — the same statement #8 made about `run_migrations.py`.

**Reconciliation rule**: at Step 5 and Step 13 the **live** numbers are compared to the above. **Any divergence is
reported as a finding and explained — never silently corrected.**

---

## 6. ⚑ Step 6 is an EXPERIMENT, not a validation — the failure branch, defined in advance

The ambiguity-check established that **the N=300 pipeline has never been run, even offline**: `real_config` (N=300,
±3pp, all 8 DATA-2 edges) builds only the `oracle` fixture, and every generator test uses `test_scoped_config`
(N=9, `tolerance_pp=50`, a two-edge subset) whose docstring states it *"NEVER asserts the real 40/35/25 band or the
full DATA-2 checklist."* **The band and the checklist have only ever been satisfied by `SkewAudit` unit tests over
synthetic counts.**

**So Step 6 may legitimately fail. This plan does not predict success.**

| Outcome | Meaning | Action |
|---|---|---|
| **Succeeds** | The pipeline genuinely produces 300 profiles inside ±3pp with all 8 edges | Proceed to Step 7. Record the profile count, class split, edge checklist, wall-clock and **file size** (Q7's input). |
| **`SkewAuditError`** | The seeded factory cannot hit ±3pp at N=300 | ⛔ **STOP.** A **real finding about U14**, discovered at **zero cost**. Do **not** widen `tolerance_pp` to make it pass — that would be tuning the gate to the result. Report, and return for a decision. |
| **`BudgetExhaustedError`** | `attempt_budget=100_000` insufficient | ⛔ **STOP and report.** Raising the budget is cheap and legitimate (sampling is free), but it is a **decision**, not an implementation detail. |
| **Runs unreasonably long** | The sampler drives the real rules engine per attempt | Report the measured time. Not a failure, but it bounds Step 9's feasibility. |

**In every failure case the correct response is to report, not to adjust a threshold until it passes.** This is the
Q11b principle applied before there is any number to be tempted by.

---

## 7. ⚑ What Stage 1 WILL and WILL NOT establish

### WILL establish

* **#3** — the 300+ synthetic corpus **exists for the first time**, frozen with a manifest and a content hash.
* **AC-3 · bias-swap delta 0** — measured over the **real** corpus, **zero extra LLM calls**.
* **AC-1 · reproducibility ×10** — measured over the real corpus, **on the decision path**, where the claim holds.
* **AC-4 · rule coverage** — measured over the real corpus. ⚑ **This may come back as less than 100%**, which is a
  genuine finding about the rulebook or the corpus and is **reported as measured** (Q11b's principle).
* **Whether the designed N=300 pipeline actually works** — the ±3pp band and 8-edge checklist, never before run.
* **A measured real-call count and actual spend**, replacing §1.5's derived 1,500–1,800 estimate for Stage 2/3.
* **Partial contribution to #18** — Step 8's `models.list` resolves *"the pinned model id is not confirmed to
  resolve against the live API"*, one of #18's two named residuals. ⚑ **It does not discharge #18** — the other
  residual (a real memo produced end-to-end) is **Stage 3**, not this.

### WILL NOT establish

* **AC-6 · the ≥4/5 LLM-as-judge score** — Stage 3. **Untouched. Still unverified.**
* **#9 `PROMPTFOO-CLI-DEFERRED`** — untouched; Q2 deferred. `discharged=False` stands.
* **#10 `JUDGE-EVAL-DEFERRED`** — untouched. Its *"tier-B corpus authorized and built"* criterion becomes
  satisfiable, but its other three criteria do **not**, and **#9 remains the one-way prerequisite**.
* **#18 discharged** — see above; a partial contribution only.
* **#22** — **unaffected, and inherited.** ⚑ The corpus's `documents_text` is **LLM-generated and inside the
  manifest's `content_hash`**, so the **corpus is subject to exactly the same non-reproducibility as memo prose**.
  Stage 1 does **not** make the corpus bit-regenerable — **which is precisely why Q7(a) commits it.** This must be
  stated in the register update, not left implicit.
* **Anything about memo quality.** Stage 1 generates **document prose for synthetic applicants**, not memos.
* **The end-to-end demo path**, the UI, or any Stage-2/3 capability.

---

## 8. Recording the outcome (Q11a-c)

**Documentation-only, on the #20 precedent.**

* **`DEFERRED_REGISTER`'s `discharged=False` is NOT touched**, and U22's three asserting tests are **not edited**.
  The reason is disclosed plainly: **U22's design provides no mechanism to flip it**, and doing so is a matched
  pair (register + frozen test) requiring its own authorization.
* **A NEW register item is opened** for that gap — *"the #9/#10 discharge cannot be recorded in code"* — on the
  #21/#22 precedent of spawning a residual rather than overclaiming.
* **#3's outcome** is recorded as a register **UPDATE** section. **DISCHARGED vs NARROWED is decided on evidence at
  Step 13**, not assumed here: the register's own words are *"blocking for real-corpus quality verification"*, and
  Stage 1 verifies the **three LLM-free gates** but **not AC-6** — so **NARROWED is the likely honest outcome**,
  with the residual being the unverified judge gate. **Not pre-decided.**
* **Four frozen prose locations go mildly stale** (`llm_judge/engine.py:88`, `llm_judge/schemas.py:52`,
  `llm_judge/tests/test_governance.py:7`, `case_lifecycle/tests/test_governance.py:6`). **None is edited** —
  handled by **supersede-not-rewrite**, with the precise position stated: *"tier-B corpus generation authorized;
  tier-B judge evaluation NOT authorized."* Verified: **no test asserts any of these substrings.**
* **`GUIDE-DOCS-BUILD-GITIGNORED`** (authorization plan §7) is opened as a **separate** candidate item **after**
  Stage 1 closes, so the register count moves once for tier-B and once for it.

---

## 9. HOLDS for the implementation pass

| Hold | How it is kept |
|---|---|
| No frozen-23 unit internals edited | C1/C2 live in `backend/scripts/`; `CorpusGenerator` takes `llm_client` **injected**; every frozen surface is **call-only** |
| **U22's `DEFERRED_REGISTER` and its frozen tests untouched** | Stage 1 does not import `backend.llm_judge` **at all** |
| WIRE-1 text unamended · `not_wired.py` not renamed · U23's frozen test unedited | nothing in this plan reaches them |
| **`audit_store` Docker-guard gap untouched — 5 errors stay exactly 5** | no new Docker-gated test; ambiguity-check (ii) confirmed `corpus/` perturbs nothing |
| No new route under `backend/app/routes/` | none added |
| **#18's spend guardrails not weakened or bypassed** | the real path goes **only** through `build_gemini_client`; the `max_calls=20` **default is unchanged**; caps rise **only by explicit argument** |
| **Stages 2 and 3 not authorized** | no memo drafting, no judge engine, no `RubricEngine` adapter, no `EvalTier.LIVE` consumer |
| `corpus_generator/build.py` not edited | left **exactly as-is**, unused, coverage-omitted, disclosed as superseded-not-deleted |
| No new dependency declared | `google-genai` already in `requirements.txt`; Step 8 is an **install**, not a manifest change |

---

## 10. Open items requiring approval AT THIS GATE

1. **C7** — the flagged `seed_demo_cases.py:97` docstring edit (**beyond the literal text of any answer**; the #8
   `deploy/README.md` precedent). Approve or exclude.
2. **Step 8's `pip install google-genai`** — an environment change that also makes the unguarded
   `corpus_generator/build.py` importable for the first time. Acknowledge.
3. **Confirmation that Steps 7 and 8 are genuine STOPS** — the implementation pass will halt at each and wait,
   rather than proceeding on the strength of this plan's approval.

**⚑ NO CODE GENERATED. NO API CALL. NO SPEND. NO CORPUS. STOPPING at the plan-file gate.**
