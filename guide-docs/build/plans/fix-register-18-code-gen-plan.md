# Register #18 — CODE GENERATION PLAN (Part 1: the PLAN. No code.)

**Stage**: POST-BUILD → register-item remediation · **the FIRST production LLM path in this build**
**Status**: 🟡 **PLAN ONLY — NO CODE WRITTEN.** Stopped at the plan-file gate.
**Date**: 2026-07-21T15:58:44Z
**Scoping plan of record**: `fix-register-18-plan.md` — Q1–Q8 + Q1b/Q2b/Q3b/Q3c/Q4b/Q4c/Q5b/Q5c/Q6b/Q7b/Q7c
answered; §7 ambiguity check; **§7.2 Q9 + Confirm 1 + Confirm 2** answered and closed at §8.
**Discipline**: TDD, **leaf-first**, ambiguity-checked — the same as every prior pass in this build.

---

## ⚠️ 0. NOTHING REQUIRES ADDITIONAL AUTHORIZATION — but ONE thing must be seen before it appears in a diff

Unlike #19 (whose **B1** narrowed a load-bearing test and needed its own sign-off), **this pass narrows no
existing test and reopens no unit.** Q2(c) landed the new module in `backend/app/`, which is **not** a frozen-23
unit — it is the composition root, authored out-of-band and already `--cov`-counted.

> ### ⚑ D1 — `corpus_generator/build.py` becomes IMPORTABLE as a side effect of Step 1
>
> Q1(a) replaces `google-generativeai` with `google-genai` in `requirements.txt`. `build.py:32,37` imports
> `from google import genai` — imports that **cannot currently succeed** against the declared manifest. After
> Step 1 they can.
>
> **This is a real state change and it is named here rather than discovered in a diff.** It **does NOT authorize
> tier-B**: nothing in this pass runs `build.py`, no test collects it, it stays coverage-omitted
> (`pyproject.toml:104`), and its `--model-id` default is **not** changed. **The module merely stops being
> broken-by-manifest.** No sign-off is requested; the disclosure is the point.

**Everything else in this plan is determinate** and follows from the answered questions.

---

## 1. Change inventory

| # | File | Kind | Frozen? |
|---|---|---|---|
| 1 | `requirements.txt` | **−`google-generativeai>=0.8.0`** · **+`google-genai>=X.Y`** (Q1 / Q1b) | manifest |
| 2 | `backend/app/llm_client.py` | **NEW** — the flag-free injected **wrapper** + the guarded **factory** | composition root |
| 3 | `backend/app/tests/test_llm_client.py` | **NEW** — tier-U guardrail suite | composition root test |
| 4 | `backend/scripts/seed_demo_cases.py` | `--real-llm` opt-in · dual banner · call-count summary · model-id/version split | out-of-band script |
| 5 | `.env.example` | `ALLOW_REAL_LLM_CALLS` documented as a **non-secret behavioural switch** | config example |
| 6 | `guide-docs/build/composition-root/real-llm-verification.md` | **NEW** — Q7b(ii) manual out-of-band procedure | docs |
| 7 | `guide-docs/BUILD-COMPLETION-REPORT.md` | #18 outcome (Q8b, decided at the gate) · **NEW** reproducibility item (Q6) | docs |
| 8 | `guide-docs/audit.md` · `guide-state.md` | completion entries with live figures | docs |

**⛔ NOT TOUCHED, verified**: `backend/memo_agent_core/provider.py` (**the `LLMClient` Protocol is IMPLEMENTED,
NEVER MODIFIED**) · `backend/memo_extensions/**` (Q2 chose `backend/app/`; **no reopening**) · every other
frozen-23 unit's internals · `backend/app/dependencies.py` (**Q8 excluded composition-root wiring**) ·
`backend/app/routes/**` (**no new route**) · `guide-docs/build/wire-1/api-contract.md` · `not_wired.py`'s
**filename** · U23's frozen `NFR-DEP-ROUTES-1` · the `audit_store` Docker guard · `corpus_generator/build.py` ·
`pyproject.toml`'s `omit` list (**Confirm 1 — pragma, not omit**).

---

## 2. Design decisions already settled (do not re-derive)

| Decision | Value | Source |
|---|---|---|
| SDK | **`google-genai`**; `google-generativeai` **removed entirely** | Q1(a) |
| Version pin | **`>=` floor**, matching every other line's convention | Q1b |
| Location | **`backend/app/llm_client.py`** — reopens nothing | Q2(c) |
| **Shape** | ⚑ **TWO pieces**: flag-free injected **wrapper** + guarded **factory** | **Q9(A)** |
| Cap placement | **inside the wrapper** — so it covers retries and every future caller | Q5b |
| Flag placement | **inside the factory only** — the wrapper never reads it | **Q9(A)** |
| Flag source | **`os.environ`**, in the factory, **never** `Settings` (frozen) | **Confirm 2** |
| Key source | **`get_settings().GEMINI_API_KEY`** — exclusively; never `os.environ` | Q3(a) / Confirm 2 |
| Key failure | **fail closed at construction** | Q3b(i) |
| SDK import | ⚑ **LAZY, inside the factory — NEVER at module import** | check (ii), binding |
| Cap default | **20 calls / process**, overridable by explicit argument | Q5c |
| Coverage | **`# pragma: no cover` on network-bound lines only; NO `omit` entry** | **Confirm 1** |
| Temperature | **passed through untouched** — the wrapper sets/defaults nothing | Q6 |
| Model id | **non-floating, supplied at OUR construction site** | Q6 / Q4b |
| Seed default | **offline double stays the DEFAULT**; real path opt-in | Q4(b) |
| Real-API test | **manual out-of-band doc only** — no pytest marker, no `pyproject.toml` edit | Q7b(ii) |

**⚠️ Naming constraints, binding** (from §7.1 Constraint B, `test_frozen_untouched.py:39-42`): the new module must
**not** declare a top-level `Settings`, `AuditRecord`, `Role`, `to_role`, `AuthRBAC`, `ApiAuthGuard`,
`AuditService`, `PostgresAuditRepository`, or `PostgresUserRoleRepository`. It must also introduce **no**
`.insert(` / `.atomic(` / `.commit(` / `.put_application(` / `.put_recommendation(` / `CasePipeline` / `.draft(` /
`.submit(` / `AUDIT_WRITER_URL` token, all of which are scanned across **every** file under `backend/app/`.

> ### ⚑ ONE CONVENTIONAL DEFAULT TAKEN, NAMED SO IT IS REVERSIBLE AT THE GATE
> Q5(c) requires per-call logging, but **there is no logging precedent in this build** — a repo-wide scan finds
> **zero** production uses of `logging` or `structlog` (the latter is declared in `requirements.txt` and never
> imported). Rather than stop the pass for a decision this small, the plan takes the **conventional default**: a
> module-level `logging.getLogger(__name__)`, **no handler and no config**, which is **inert and silent by
> default** and never prints during tests. The alternative — `print()`, as `seed_demo_cases.py` uses — is
> rejected for a library module. **Named here so it is visible and can be overridden at this gate.**

---

## 3. The two-piece shape (Q9(A)) — stated precisely before any code

```
backend/app/llm_client.py

  class CappedGeminiClient:                      # the WRAPPER — flag-free, purely injected
      def __init__(self, sdk_client, *, max_calls: int = 20) -> None
      def generate(self, *, model: str, prompt: str, temperature: float) -> str
      # - satisfies the FROZEN LLMClient Protocol STRUCTURALLY (no import, no inheritance)
      # - counts EVERY call; raises once max_calls is exceeded
      # - passes `temperature` through UNTOUCHED — sets nothing, defaults nothing
      # - logs model id, prompt LENGTH, latency, running count — never prompt text, never a key
      # - __repr__ discloses NO key material (it holds no key at all — see below)
      @property
      def call_count(self) -> int

  def build_gemini_client(settings, *, model_id: str, max_calls: int = 20) -> CappedGeminiClient:
      # the FACTORY — the ONLY spend-capable path
      # 1. os.environ ALLOW_REAL_LLM_CALLS must be exactly "true"  -> else refuse (Confirm 2)
      # 2. key = settings.GEMINI_API_KEY, validated non-empty      -> fail closed (Q3b-i)
      # 3. LAZY `from google import genai` here, NEVER at module top  (binding)
      # 4. return CappedGeminiClient(genai.Client(api_key=key), max_calls=max_calls)
```

> ⚑ **The wrapper never holds the key.** The key reaches `genai.Client(...)` inside the factory and the wrapper
> receives an **already-constructed SDK object**. This makes Q3c's non-disclosure guarantee **structural rather
> than behavioural** — the wrapper cannot leak what it does not have — and is a strictly stronger property than
> the question asked for. It is called out because it is a *design consequence* of Q9(A), not an extra decision.

---

## 4. TDD, leaf-first execution order

Leaf-first = **manifest → wrapper → factory → seed script → docs**. Each step is **RED → GREEN**, tests written
before implementation, suite green before the next step.

### Step 1 — `requirements.txt` (the leaf, Q1)

- [ ] **GREEN**: replace `google-generativeai>=0.8.0` with `google-genai>=X.Y` — exact floor pinned at
      implementation time against the current stable release (Q1b), `>=` per the file's convention
- [ ] **VERIFY**: repo-wide scan confirms **zero** imports of `google.generativeai` remain (already true today —
      re-confirmed, not assumed)
- [ ] **VERIFY**: `pip install -r requirements.txt` resolves
- [ ] ⚑ **DISCLOSE (D1)**: `corpus_generator/build.py` becomes importable. **Not run. Not collected. Still
      coverage-omitted. Its `--model-id` default is NOT changed.** Tier-B remains unauthorized.

### Step 2 — the wrapper `CappedGeminiClient` (the code leaf)

- [ ] **RED** — `test_llm_client.py`, all against a **hand-written fake SDK object**, **no key, no network, and
      `google-genai` need not even be installed**:

| # | Test | Asserts |
|---|---|---|
| 1 | `test_it_satisfies_the_frozen_llmclient_protocol` | ⚑ `isinstance(wrapper, LLMClient)` — the **test** imports the frozen Protocol (`runtime_checkable`); **production does not**. Conformance proven without coupling. |
| 2 | `test_it_passes_temperature_through_untouched` | fake records `temperature`; wrapper **sets and defaults nothing** |
| 3 | `test_it_passes_the_model_id_through_untouched` | fake records `model` |
| 4 | `test_it_returns_the_sdk_response_text` | the raw string reaches the caller unaltered |
| 5 | `test_it_counts_every_call` | `call_count` increments per `generate()` |
| 6 | `test_it_refuses_beyond_the_cap` | call `max_calls` times OK; call **`max_calls + 1`** raises |
| 7 | `test_the_cap_default_is_20` | Q5c's default pinned as a test, not a memory |
| 8 | **`test_the_cap_counts_retries_not_just_drafts`** | ⛔ **THE TOOTH — see below** |
| 9 | `test_its_repr_discloses_no_key_material` | Q3c |
| 10 | `test_it_logs_prompt_length_never_prompt_text` | caplog: length present, prompt body **absent** |

> ### ⛔ Test 8 — the cap-counts-retries tooth (the one that makes Q5b non-vacuous)
> A cap that counted only *drafts* would silently under-count, because the memo agent **re-enters the client on a
> citation failure** (`MEMO_CITATION_RETRY_CAP`, `memo_agent_core/orchestrator.py`). The test therefore drives
> the **real `LangGraphOrchestrator`** through the **real `GeminiAdapter`** over our wrapper over a fake SDK
> object that returns **citation-invalid XML**, forcing the retry loop, then asserts
> **`wrapper.call_count > 1` for a single `draft`** — and that the cap fires mid-retry when set low enough.
> ⚑ **A spy on `generate` alone would pass while the retry path went uncounted; this cannot.** Same reasoning as
> #19's *"`commit()` never invoked"* spy assertion.

- [ ] **GREEN**: implement the wrapper. **No `google.genai` import anywhere in it** — it is SDK-agnostic by
      construction and merely calls the object it was handed
- [ ] ⚑ **NO `# pragma: no cover` in the wrapper** — every line is genuinely reachable with a fake

### Step 3 — the factory `build_gemini_client` (Q9(A))

- [ ] **RED** — the guard tests, still with **no key and no network**:

| # | Test | Asserts |
|---|---|---|
| 11 | `test_it_refuses_without_the_env_flag` | `ALLOW_REAL_LLM_CALLS` unset ⇒ raises; **monkeypatched env, never the real one** |
| 12 | `test_it_refuses_when_the_flag_is_not_exactly_true` | `"1"`, `"yes"`, `"TRUE "` ⇒ still refuses (**exact match, fail-closed**) |
| 13 | `test_it_fails_closed_on_an_empty_or_whitespace_key` | Q3b(i) — the structurally-invalid case `Settings` alone would not catch |
| 14 | `test_the_refusal_message_contains_no_key_material` | Q3c — the second half of the non-disclosure guarantee |
| 15 | `test_the_wrapper_constructor_needs_no_flag` | ⛔ **Q9(A)'s whole point**: constructing the wrapper with a fake **works with the flag unset** — the offline suite never touches a spend flag |
| 16 | `test_the_module_imports_without_the_sdk_installed` | ⚑ import `backend.app.llm_client` succeeds regardless — **proves the lazy import** |

- [ ] **GREEN**: implement the factory
      - `os.environ.get("ALLOW_REAL_LLM_CALLS") == "true"` — **exact**, fail-closed
      - key **exclusively** via `get_settings().GEMINI_API_KEY`; **never** `os.environ`
      - ⚑ **LAZY** `from google import genai` **inside the function body** (binding, per check (ii);
        `build.py:32`'s precedent)
      - ⚑ **Confirm 2 docstring, mandatory and explicit**: why `os.environ` here is **not** a SEC-3 violation —
        *`dependencies.py`'s rejection of `os.environ` is scoped to **credentials and secret material**; this is a
        **behavioural on/off switch controlling whether real spend is permitted**, not a credential, and it must
        **never** be conflated with or read alongside `GEMINI_API_KEY`'s retrieval path, which stays **exclusively**
        through `get_settings()`.*
      - ⚑ **Confirm 1**: `# pragma: no cover` on **the `genai.Client(...)` construction line(s) only** — following
        `not_wired.py:127`'s precedent exactly. **The flag check, the key validation and the refusal paths are NOT
        pragma'd — they stay genuinely covered.** **No `omit` entry added to `pyproject.toml`.**
- [ ] ⚑ **Docstring must state Q3c's honest limit**: this guarantees **our** code never discloses the key; it
      **cannot** guarantee the SDK's own exceptions never embed request context. **State the limit, do not imply a
      stronger guarantee than can be delivered.**

### Step 4 — `backend/app/`'s existing scanners (verification, not edit)

- [ ] **VERIFY (no edit)**: `test_no_write_route.py` and `test_frozen_untouched.py` both build `PRODUCTION_FILES`
      via `APP_ROOT.rglob("*.py")` — the new module is **auto-enrolled**. Confirm all eight assertion families
      still pass **unmodified**: `.insert(` · `.atomic(` · `.commit(` · `.put_application(` · `.put_recommendation(`
      · `CasePipeline` · `.draft(` · `.submit(` · `AUDIT_WRITER_URL` · `AUDIT_WRITER_PASSWORD` ·
      `DictCommitContextProvider` all legitimately absent
- [ ] **VERIFY (no edit)**: `test_frozen_untouched.py`'s `owned == {"app"}` still holds
- [ ] ⛔ **If ANY existing assertion needs modification, STOP and report it as a finding.** §7.1 predicts **none
      will**. **A required edit here would be a prediction miss, not a chore.**

### Step 5 — the seed script (Q4(b) / Q4c / Q4b)

- [ ] **GREEN** — `--real-llm` flag, **default FALSE**:
      - flag absent ⇒ `_OfflineLLMClient()` **exactly as today**, zero config, zero cost, **banner unchanged**
      - flag present ⇒ `build_gemini_client(...)`, which **independently** requires `ALLOW_REAL_LLM_CALLS=true`
        (**two independent gates**, per Q4)
- [ ] **GREEN** — ⚑ **model-id / version-stamp SPLIT** (the §1.7 FIND, Q4b):
      - real path: `model` = an **explicit non-floating model id**; `model_version` = **model id + SDK version**
        (Q6b's minimum), assembled at the construction site
      - ⛔ **`GeminiAdapter`'s default is NOT changed** — the id is passed as an argument. Editing frozen U4 is
        forbidden.
      - offline path: `OFFLINE_MODEL_VERSION` behaviour **unchanged**
- [ ] **GREEN** — Q4c dual banner:
      - offline: the existing **"⚠️ MEMOS ARE SYNTHETIC PLACEHOLDERS"** banner, **verbatim and unchanged**
      - real: a **visually distinct "⚠️ REAL LLM CALLS — THIS WILL SPEND MONEY"** banner naming the model id and
        the cap
      - real: an **exit summary printing the real-call count** (`wrapper.call_count`)
- [ ] **GREEN** — update the module docstring: register **#18**'s status changes; the *"no production `LLMClient`
      anywhere in this build"* claim **becomes false and must be rewritten**, not left standing
- [ ] ⚑ **The `_OfflineLLMClient` class and its warning docstring are KEPT, not deleted** — Q4's non-negotiable

### Step 6 — the manual real-API procedure (Q7b(ii))

- [ ] **NEW** `guide-docs/build/composition-root/real-llm-verification.md` — a **human-run, documented procedure**:
      export the key, set `ALLOW_REAL_LLM_CALLS=true`, run `seed_demo_cases.py --cases 1 --real-llm`, inspect the
      memo, confirm the stamps
- [ ] ⛔ **NOT a pytest test. No new marker. NO `pyproject.toml` edit. Never collected. Zero possibility of a CI
      run spending money.** (Q7b(ii))
- [ ] Must state the expected **cost order of magnitude** and that it spends **real money**

### Step 7 — full-suite verification

- [ ] `pytest backend` — ⚑ **PREDICTIONS STATED IN ADVANCE** (the #19 discipline):

| Metric | Baseline (post-#19) | Predicted | Why |
|---|---|---|---|
| passed | **1532** | **1532 + 16** | the 16 new tier-U tests in Steps 2–3 |
| failed | **0** | **0** | — |
| skipped | **40** | ⛔ **40 — UNCHANGED, +0** | **this pass adds NO tier-I test and NO Docker-dependent test.** Q7b(ii) is a **document**, not a test. **Every new test runs offline, always.** |
| errors | **5** | ⛔ **5 — EXACTLY 5, unchanged and confirmed BY NAME** | standing hold |
| coverage | **99.87%** | **≥90% gate held** | new module fully covered except the pragma'd SDK-construction line |
| `EXPECTED_PRODUCTION_MODULES` | **8** | **8 — unchanged** | that scan is scoped to `case_lifecycle/` (`tests/structural.py:26`); a `backend/app/` module **cannot** affect it — verified, not assumed |

- [ ] ⛔ **Any deviation from the above is a finding to REPORT, not to absorb.**
- [ ] `python -m compileall` over `app` + `scripts` exits **0**
- [ ] ⚑ **Confirm the offline suite still passes with `ALLOW_REAL_LLM_CALLS` UNSET** — the single most important
      regression check in this pass, and the whole reason Q9 landed on (A)

### Step 8 — documentation and the register

- [ ] `.env.example` — `ALLOW_REAL_LLM_CALLS` documented under a **new non-secret section**, clearly separated
      from the credential block so it is never mistaken for one (Confirm 2)
- [ ] **NEW register item — Q6's reproducibility gap**, stated exactly as Q6 requires: *AC-1's 100%
      reproducibility claim holds for the **decision path**, structurally guaranteed by **CON-BR2-TYPE** (the model
      cannot alter the recommendation), but **cannot be claimed bit-exactly for memo prose under a real LLM, even
      at `temperature=0`**.* With owner and the pinned-model-id mitigation.
- [ ] **Register #18 outcome — DECIDED AT THE GATE ON EVIDENCE, NOT PROMISED HERE** (Q8b). The expectation is
      **DISCHARGED**; ⛔ **that expectation must be tested against what the implementation actually delivers, per
      Q8b's own instruction, and NARROWED chosen instead if anything falls short.**
- [ ] `guide-docs/build/composition-root/` code summary — the two-piece shape and D1's disclosure
- [ ] `audit.md` + `guide-state.md` — completion entries with **live figures**

---

## 5. What this fix will and will not guarantee — the honest claim

**WILL**: ✅ **A production `LLMClient` implementation exists** — the chain
`CaseSeams.draft_memo → LangGraphOrchestrator → GeminiAdapter → LLMClient` is **complete for the first time** ·
✅ **a genuine LLM-drafted memo can be produced**, via the opt-in seed path · ✅ the manifest is **self-consistent**
(`google-genai` declared, imports match, the legacy SDK gone) · ✅ **spend cannot occur by accident** — two
independent gates (`--real-llm` **and** `ALLOW_REAL_LLM_CALLS=true`) plus a **hard call cap that counts retries** ·
✅ **the offline path is untouched and remains the default** — the full suite still runs with **no key, no network,
no SDK installed, and no spend flag set**.

**WILL NOT**: ⛔ **make memo prose bit-reproducible.** `temperature=0` makes sampling greedy — **not
deterministic across provider-side model changes.** AC-1's 100% claim holds for the **decision path** (structurally,
via **CON-BR2-TYPE** — `MemoDraftOutput` carries only `narrative_prose` + `cited_rule_ids`, so **the model cannot
change the recommendation**) and **is not claimable bit-exactly for prose**. Pinning a non-floating model id
**narrows** this; it does not close it. **A new register item records exactly that.**
⛔ **Not wire the client into the live request path** — Q8 excluded it. `dependencies.py` is unchanged, no route is
added, and Scope B's Q3-D property (*R4 side-effect-free **by construction***) **survives intact**. A real memo is
producible **by the out-of-band seed script**, **not** by an HTTP call.
⛔ **Not authorize tier-B.** `corpus_generator/build.py` becomes **importable** (D1) and remains **unrun,
uncollected, coverage-omitted, and unauthorized**.
⛔ **Not guarantee the SDK's own exceptions never embed request context** (Q3c's stated limit). **Our** code is
tested never to disclose the key. **The SDK's internals are not ours to promise.**

---

## 6. Holds — all upheld

`memo_agent_core/provider.py`'s **`LLMClient` Protocol IMPLEMENTED, NEVER MODIFIED** · `memo_extensions/`
**untouched — NOT reopened** · every other frozen-23 unit's internals **untouched** · WIRE-1's text **not
amended** · `not_wired.py` **not renamed** (register #13 stays open) · U23's frozen test **not edited** ·
`audit_store` Docker-guard gap **untouched (5 stays exactly 5)** · **tier-B not authorized** (D1 disclosed) ·
**no new route** under `backend/app/routes/` · **`dependencies.py` not wired** (Q8) · register **#20** left open
and undecided.

---

**STOPPED AT THE PLAN-FILE GATE. No code written.** Implementation begins only after this plan is approved.
