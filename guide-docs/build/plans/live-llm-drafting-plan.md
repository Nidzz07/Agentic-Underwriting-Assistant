# LIVE LLM DRAFTING — SCOPING PLAN (Ollama first)

**Status**: ✅ **ALL TEN QUESTIONS ANSWERED 2026-08-16.** ⛔ **STILL NO CODE, NO BACKEND FILE TOUCHED.**
Next artifact: the **code-generation plan**, which requires its own separate approval.
**Created**: 2026-08-16 · **Answered**: 2026-08-16
**Baseline**: HEAD `bd3875d` · working tree clean · backend **1774 / 0 / 45 / 5 / 99.49%** · frontend **815 / 154**
**Register**: 31 tracked — 20 open · 7 closed/discharged · 4 narrowed (#3, #8, #18, #19)
**Target register item**: **#18 `NO-PRODUCTION-LLMCLIENT`** (NARROWED) — and, through it, **#2** gap **(iii)**

> ⚑ **SUPERSEDED 2026-08-16 — preserved because it was true for the whole of the question gate:**
> *"This document asks ten questions and answers none of them. Every `[Answer]:` tag is deliberately
> empty. Each question carries a grounded recommendation — grounded meaning it cites the file and
> line the reasoning rests on — but the recommendation is an argument, not a decision, and nothing
> below has been implemented."*
>
> **All ten are now answered**, verbatim as given, at their `[Answer]:` tags. ⚑ **Every headline
> letter matched the recommendation** — which is stated plainly rather than dressed up as
> independent convergence, since the recommendations were written by the same agent that is now
> reporting the agreement. **The answers did three things the recommendations did not**, and those
> are where the real decisions live: they resolved Q4's deliberately-open design fork, they took
> Q4's option D *in addition to* A, and they **declined** Q9's proposed register item on a stated
> argument. See **§4.1**. ⛔ **Nothing below has been implemented.** The answers are decisions about
> what to build, not a record of anything built.

---

## 0. Context

### 0.1 What this pass would be

Register **#18** has been the sole named blocker on **#2**'s full discharge since 2026-08-02. Its
gap **(iii)** — *synthetic memo prose* — is the last thing standing between this build and a memo
produced by an actual language model. Today every memo the request path produces comes from
`backend/app/offline_memo_double.py`, stamped `OFFLINE-DOUBLE-NOT-A-REAL-LLM`, and that stamp has
now been read back out of a real PostgreSQL in **three separate manual verifications** (register
#2's, document-upload's §9, and the outlier mount's §7). The stamp is doing exactly the job it was
built for. This pass would be the first time it changes.

The provider chosen to go first is **Ollama**, running locally, model
`llama3.1:8b-instruct-q4_K_M`. The user has installed it, confirmed the daemon is running, and
confirmed `curl http://localhost:11434` responds. That satisfies the system-level prerequisite;
**this plan assumes Ollama is reachable during scoping and design**, and defers proving a real
draft end-to-end to §10's manual verification.

⚑ The fixed quantization in the model tag is not incidental — it was chosen against register
**#22 `MEMO-PROSE-NOT-BIT-REPRODUCIBLE`**, and it bears directly on Question 5's stamp design.

### 0.2 ⚠️ Two documentation states a future reader should not be confused by

Neither is in scope for this pass. Both are named here so that a reader who checks them gets the
correct picture rather than a stale one.

**(a) The outlier-mount doc-state lag.** `guide-docs/guide-state.md`'s final entry and
`guide-docs/audit.md`'s `2026-08-13T17:01:28Z` entry both close with **"NOT COMMITTED"** /
**"NO COMMIT"** and assert HEAD is still `d43b661`. **That is no longer true.** Commit `bd3875d`
(2026-08-13 22:42:11 +0530) contains that pass — its own commit body enumerates S1–S5 by name. The
entries were written before the commit landed and were not revised after. ⚑ This is the same class
of gap this project has already recorded twice and handled the same way both times: the register #2
doc-state correction (`audit.md` 2026-08-02T16:41:52Z) and the document-upload deferred backfill.
**Acknowledged, not fixed here** — a documentation-sync task owns it.

**(b) `BUILD-COMPLETION-REPORT.md` is stale on the register, and it is stale about #18
specifically — which is why it is flagged in *this* plan rather than left to a general cleanup.**
That file's §5 is still headed *"The complete Deferred Decisions register — 20 items"*, and its
table contains **no rows for #26–#31**. Items #27, #28 and #29 exist only as appended
`REGISTER UPDATE` sections at the file's tail; ⛔ **#30 `INJECTION-SPAN-SINK-DEFERRED` and #31
`HEALTHFLAGS-COMPLETENESS-SURPRISE` appear nowhere in that file at all** (verified: `grep -c` for
both names returns **0**). Its running chronology tops out at *"Register now stands at 26 tracked"*;
the authoritative count — **31 tracked** — lives only in `guide-state.md:7248`.

⛔ **Why this matters here and not merely in general.** A reader opening the completion report to
check **#18**'s history gets its §5 row (line 158), which is accurate as far as it goes, and the
2026-07-22 *narrowing* entry — but **no indication that #18 has since become the sole named blocker
on #2**, which is a status change recorded only in `guide-state.md`. The file understates #18's
current significance to this build. **Not fixed in this pass** — a separate, future documentation-sync
task — but a reader of *this* plan should take `guide-state.md` as authoritative on #18, not the
completion report.

---

## 1. Investigation findings — what the code actually does today

Every claim below was read from the tree at `bd3875d`. File and line references are exact.

### 1.1 There are TWO client seams, not one, and they are not interchangeable

| Seam | Defined at | Signature | Drives |
|---|---|---|---|
| `LLMClient` | `memo_agent_core/provider.py:37` | `generate(*, model, prompt, temperature) -> str` | `GeminiAdapter` |
| `ThinkingLLMClient` | `memo_extensions/provider_secondary.py:34` | `generate(*, model, prompt, temperature, thinking) -> str` | `ClaudeAdapter`, `OllamaAdapter` |

⚑ **The split is deliberate and documented.** `provider_secondary.py:4-11` records the reason: the
frozen `memo_agent_core.LLMClient` seam is *"three kwargs, no thinking channel"* and *"is U4's
Gemini path, left completely UNTOUCHED"*, so U19 defined its own seam rather than amend a frozen
one. **`memo_agent_core` is in `FROZEN_UNITS`; `memo_extensions` is not.**

⚠️ `OllamaAdapter` (`provider_showcase.py:22-26`) imports `_PRODUCTION_TEMPERATURE`, `ThinkingLLMClient`
and `_parse_xml` — two of them **private names** — from `provider_secondary`. The two adapters are
structurally identical (`provider_showcase.py:48-55` vs `provider_secondary.py:78-85`).

### 1.2 The composition root conflates model-ID and model_version-stamp

`backend/app/dependencies.py:238-242`:

```python
self._orchestrator = LangGraphOrchestrator(
    GeminiAdapter(OfflineMemoLLMClient(), model=OFFLINE_MODEL_VERSION),
    rulebook=loader.load_rulebook(RULEBOOK_VERSION),
    model_version=OFFLINE_MODEL_VERSION,
)
```

`model=` is the **model ID** the adapter forwards to `client.generate(model=...)`; `model_version=`
is the **stamp** that is persisted and eventually shown to a human. Both are the single string
`"OFFLINE-DOUBLE-NOT-A-REAL-LLM"`. ⚑ **Harmless today and only today** — `OfflineMemoLLMClient.generate`
accepts `model` and ignores it (`offline_memo_double.py:72`). Against a real provider the ID must be
a resolvable model name and the stamp must be an honest provenance record; they cannot be the same
string.

⚑ **The correct split already exists in this repo**, in `backend/scripts/seed_demo_cases.py`:

```python
def __init__(self, llm_client=None, *, model: str = OFFLINE_MODEL_VERSION,
             model_version: str = OFFLINE_MODEL_VERSION, ...)      # :198-205
...
model_version = f"{REAL_MODEL_ID}+google-genai-{_google_genai_version()}"   # :407
seams = _SeedSeams(..., model=REAL_MODEL_ID, model_version=model_version)   # :408-412
```

`_SeedSeams`' own comment (`:214-216`) states it in terms: *"Default (no --real-llm): the offline
double, model + stamp = OFFLINE_MODEL_VERSION … Real path: … an explicit non-floating model id and
a real model_version stamp (Q4b split)."* **`_CompositionSeams` never received that split.**

### 1.3 ⛔ Nothing on the drafting path catches an exception — and there is no generic handler

Traced end to end:

| Layer | File:line | Exception handling |
|---|---|---|
| draft node | `memo_agent_core/orchestrator.py:93` | `output = self._provider.complete(...)` — **none** |
| orchestrator | `memo_agent_core/orchestrator.py:156` | `final = self._graph.invoke(...)` — **none** |
| pipeline | `case_lifecycle/pipeline.py:186` | `memo = self._seams.draft_memo(...)` — **none** |
| route R11 | `app/routes/submission.py:212` | `outcome = pipeline.draft(...)` — **none** |
| app | `app/main.py:98-100` | handlers for `WireError`, `RequestValidationError`, `StarletteHTTPException` — **no generic `Exception` handler** |

⛔ **Consequence.** A `ConnectionError` from an Ollama client escapes all five layers and is served
by Starlette's default error middleware as a **plain-text 500**, not the WIRE-1 §4 envelope. That
directly contradicts `main.py:97`'s own stated invariant: *"Every non-2xx leaves as the WIRE-1 §4
envelope — no route can emit a non-contract body."* **Today nothing can trigger it** — the offline
double cannot fail — which is precisely why the gap has never been visible.

⚑ **The `memo is None` branch does not cover this.** `pipeline.py:187-193` handles a *domain*
failure — drafting ran and produced nothing — and transitions the case to `FAILED`. An **uncaught
exception bypasses that transition entirely**: no row is written, the case stays `evaluated`, and
`DraftOutcome`'s contract (*"never raises for a domain failure"*, `pipeline.py:155`) is silent about
infrastructure failure because infrastructure failure was not previously reachable.

### 1.4 `case_seams()` is `lru_cache`d, and it is constructed on SUBMIT, not on DRAFT

`dependencies.py:318-326` — `@lru_cache(maxsize=1)`, one `_CompositionSeams` per process. Its
`__init__` runs on the **first request that needs the pipeline**, which is R10 `submit`, not R11
`draft`. Two consequences for any construction-time reachability check:

* ⛔ It would run during **submission** and, if it raised, would break the submit path over a
  drafting-only dependency.
* ⛔ It would run **exactly once per process**. Ollama going down after that first submit would
  never be re-noticed; Ollama being down at that moment would poison the cache for the process's
  whole life.

⚑ Contrast `outlier_model()` (`dependencies.py:299-315`), which is also `lru_cache`d but is
resolved **at call time inside `score_outlier`** (`:281`) precisely so construction stays cheap —
the comment at `:277-279` says so.

### 1.5 R11's concurrency shape, and the timeout that does not exist

`trigger_drafting` (`submission.py:180`) is a **plain `def`**, not `async def` — FastAPI therefore
runs it on a threadpool thread. ⚑ It is **not** wrapped in `run_bounded_parse`; that limiter
(`parse_concurrency.py`) is R10's, and exists for subprocess PDF parsing. **R11 has no concurrency
bound and no timeout.**

⛔ **The Ollama SDK defaults to NO timeout.** `ollama._client`'s `__init__` declares `timeout: Any = None`
and its docstring states it overrides httpx's default deliberately. Installed version: **`ollama 0.6.2`**,
and `ollama>=0.3.0` **is already declared in `requirements.txt:13`** — no new dependency is needed.

⚑ This cuts both ways and the direction is the opposite of the intuitive one: a **cold model load
of tens of seconds will NOT be cut off** (good), but a **hung daemon will hold a threadpool thread
forever** (bad). There is no upper bound on either side today.

### 1.6 `OLLAMA_HOST` needs no new plumbing at all

* `Settings` (`secrets_config/settings.py:23-38`) has exactly six required fields and
  `extra="ignore"` (`:30`). An `OLLAMA_HOST` in `.env` is **silently ignored**, not an error.
  `secrets_config` **is** in `FROZEN_UNITS` — adding a field reopens a frozen unit.
* ⚑ **`.env.example` already reserves the variable**, under *"Phase-2 RESERVED (memo-extensions /
  observability author these at their own FD; NOT required in Phase 1 — reserved-not-authored,
  BR-SEC-6)"*, commented out as `# OLLAMA_HOST=`.
* ⛔ **The SDK reads it without being asked**: `ollama._client` resolves
  `_parse_host(host or os.getenv('OLLAMA_HOST'))`, defaulting to localhost. Passing nothing is
  already correct behaviour.
* ⚑ **Two precedents exist for a behavioural env var read via `os.environ`**, and the closer one is
  in the very file a selector would live in: `dependencies.py:83-97` (`SESSION_COOKIE_SECURE`),
  whose comment argues *"Behavioural switch, NOT a credential — so reading it from `os.environ` is
  not a SEC-3 violation … Reading it here also avoids C-B: frozen `Settings` stays at exactly six
  fields."* The other is `llm_client.py:120` (`ALLOW_REAL_LLM_CALLS`).

### 1.7 ⛔ The `memo_extensions` import is NOT mechanically gated anywhere

This is the finding most likely to change how Question 8 is answered, so it is stated plainly.

* `test_frozen_untouched.py:21-24` — `FROZEN_UNITS` = `{intake, rules_engine, memo_agent_core,
  audit_store, auth_rbac, secrets_config, database, corpus_generator, quality_gates, admin_cli,
  common}`. **`memo_extensions` is not a member.** Neither are `case_lifecycle`, `outlier_model`,
  `observability`, `llm_judge` or `authn`.
* `test_frozen_untouched.py:19` — `COMPOSED_UNITS` = `{audit_store, auth_rbac, secrets_config}`.
  Only these three are *required* to be imported by `backend/app/`. Nothing requires or forbids
  `memo_extensions`.
* `test_no_write_route.py:100` — `_PIPELINE_MODULES` = `frozenset({"dependencies.py", "submission.py"})`,
  which governs references to `CasePipeline` / `.draft(` / `.submit(` (`:89`). **Orthogonal** to
  imports of `memo_extensions`.
* ⛔ **And `memo_extensions` is ALREADY in the production import graph**:
  `case_lifecycle/pipeline.py:38` does `from backend.memo_extensions.borderline_router import route_borderline`,
  called at `:184` on every draft. It is reached on the live path today.

⚑ So the honest framing is: this would be the **first import of `memo_extensions` from
`backend/app/`**, but it would be **neither the first production import of `memo_extensions`** nor
a violation of any mechanical guard. Whether it still deserves its own sign-off is Question 8, and
it is a **discipline** question, not a compliance one.

### 1.8 The Ollama quality-gate exemption is real, built, and tested

* `llm_judge/pipeline.py:35` — `IN_GATE_PROVIDERS`, with the comment *"Ollama is deliberately absent
  (memo-quality gates only)"*. `partition_by_scope` (`:44-47`) splits every sample; exempt samples
  are **retained** in `sample_scores` and counted in `exempt_count` (`:97-99`, `:144`), tagged
  `EXEMPT_REASON_MEMO_QUALITY` (`schemas.py:59-60`).
* `memo_extensions/tests/test_provgate.py` asserts the **decision-level** gates hold for Ollama —
  `temperature == 0` (`:30`) and `"recommendation" not in MemoDraftOutput.model_fields` (`:31`,
  CON-BR2-TYPE) — and its docstring states the boundary: *"exempt from memo-QUALITY gates only
  (groundedness/promptfoo), NEVER from the DECISION-LEVEL gates."*
* `PROJECT-BRIEF.md` §9 and its 2026-06-17 precedence note classify Ollama as
  **SHOWCASE — *"wired, NOT tested against acceptance criteria."*** The acceptance table (§6) sets
  *LLM-as-judge score ≥4/5 via promptfoo* as a criterion Ollama memos are exempt from by design.

### 1.9 Where the `model_version` stamp actually travels

`_CompositionSeams` → `LangGraphOrchestrator(model_version=)` → `DecisionMemo.model_version` →
`PendingRecommendation.model_version` (`case_lifecycle/schemas.py:58`, table
`pending_recommendation`, `0001_case_lifecycle.sql:38`) → at commit,
`audit_store/commit_service.py:128` → `AuditRecord.model_version` (`record_schema.py:50`) → table
`audit_record` (`0001_initial_schema.sql:21`) → R7 `GET /decisions/{id}` → UI
`frontend/src/history/components/ForensicTupleRegion.jsx:22`, testid `history-detail-model-version`.

⛔ **R4 `GET /applications/{id}/memo` does NOT carry `model_version`** — `projections.py`'s
`memo_view` (`:123`) never emits it (verified: zero occurrences of `model_version` in that file).
⚑ **Therefore the stamp is only visible in the UI after the case is COMMITTED**, in the history
view's forensic tuple. It is visible in `psql` immediately after drafting, from
`pending_recommendation`. This shapes §10's verification ordering and is easy to get wrong.

---

## 2. Questions

Ten questions. **None is pre-filled.** Answer by putting a letter after each `[Answer]:` tag; if no
option fits, choose the last option and describe.

---

## Question 1
The Ollama client class must be built from scratch. What is its scope, relative to
`CappedGeminiClient` (`app/llm_client.py:51-99`) and its guarded factory
`build_gemini_client` (`:102-129`)?

A) **Full mirror** — a `CappedOllamaClient` (injected SDK object, call counter, cap-exceeded
   refusal, length-only logging, `call_count` property, non-delegating `__repr__`) **plus** a
   guarded `build_ollama_client(*, model_id, max_calls)` factory holding the lazy `import ollama`.
   Retain a call cap, but document its reason as **runaway-loop containment, not spend**.
B) **Full mirror, minus the gate** — same client class and factory, but **no `ALLOW_REAL_LLM_CALLS`
   equivalent**, because a local daemon costs nothing and the flag's stated purpose is
   *"whether real spend is permitted"* (`llm_client.py:106`). Selection alone enables it.
C) **Client only, no factory** — construct `ollama.Client()` inline in `dependencies.py` and wrap
   it. Fewer moving parts, but breaks the established two-piece separation
   (`llm_client.py:3-4`: *"deliberately separated so the spend gate never touches the offline test
   surface"*).
D) Other (please describe after [Answer]: tag below)

> **Recommendation: A.** The cap is worth keeping even at zero cost, because the thing it actually
> bounds is not money — `llm_client.py:38-40` says it *"bounds real spend INCLUDING the memo
> agent's citation-retry loop, because the cap counts inside `generate`."* That retry loop is
> `orchestrator.py:118`'s `MEMO_CITATION_RETRY_CAP` path, and it is **provider-independent**. A
> small local model is *more* likely than Gemini to fail citation validation repeatedly, so the
> loop-bounding value goes **up**, not down, when the provider gets weaker. Keeping the factory
> (against C) preserves the property that the offline test surface never touches the construction
> path. ⚠️ The one thing A must not do is copy `ALLOW_REAL_LLM_CALLS`'s **wording** — see Q1's
> option B and Question 3; a flag whose message says *"permit real spend"* would be a false
> statement on a local daemon.

[Answer]: A — full mirror of CappedGeminiClient's shape, including the call cap, whose purpose is reframed as runaway citation-retry-loop containment (provider-independent, and arguably MORE valuable against a weaker local model), not spend control.

---

## Question 2
There are two client seams (§1.1). `GeminiAdapter` takes `LLMClient` (3 kwargs); `OllamaAdapter`
takes `ThinkingLLMClient` (4 kwargs, `+thinking`). Which does this pass wire, and does the switch
span both paths?

A) **`ThinkingLLMClient` + `OllamaAdapter` only.** Build one 4-kwarg client, construct
   `OllamaAdapter`, leave `GeminiAdapter` and the `LLMClient` seam exactly as they are. Requires
   importing `memo_extensions` from `backend/app/` (Question 8).
B) **`LLMClient` + `GeminiAdapter` only.** Build a 3-kwarg client that talks to Ollama and hand it
   to the existing `GeminiAdapter`, changing only the injected object. Touches no new package and
   raises no import question at all.
C) **Both seams, one pass.** Build a 4-kwarg client for `OllamaAdapter` *and* keep a 3-kwarg path so
   Gemini and Ollama are both live-selectable through the same mechanism.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: A.** B is genuinely tempting — it is the smallest possible change and sidesteps
> Question 8 entirely — but it is **dishonest in a way this project has consistently refused**: it
> would route every live memo through a class literally named `GeminiAdapter`, whose docstring
> (`provider.py:46`) calls it *"P1 provider adapter"*, while no Gemini is involved. It would also
> silently discard the thinking channel, making `route_borderline`'s `EXTENDED` decision
> (`pipeline.py:184`) a computation with no effect — the exact *"disconnection assumed away"* shape
> register #30 was opened for. ⚑ **`OllamaAdapter` already exists, is already unit-tested
> (`test_provgate.py:17`), and is already the right class**; the only reason not to use it is the
> import question, which §1.7 shows is a discipline choice rather than a barrier. C is real scope
> creep: Gemini's live path is Question 6's subject and bundling it here would make one gate carry
> two providers.

[Answer]: A — ThinkingLLMClient + OllamaAdapter only. Routing Ollama through GeminiAdapter would be dishonest (a class literally named for Gemini serving no Gemini) and would silently discard the thinking channel, making route_borderline's EXTENDED decision inert — exactly the “disconnection assumed away” shape register #30 exists to name. Accept the memo_extensions import consequence; that's Q8's gate.

---

## Question 3
What is the exact shape of the provider selector, and how is `OLLAMA_HOST` sourced?

A) **Env var read at composition time via `os.environ`, `OLLAMA_HOST` not read by us at all.** A
   named constant in `dependencies.py` (e.g. `MEMO_PROVIDER_ENV = "MEMO_PROVIDER"`), read inside
   `_CompositionSeams.__init__`, **fail-safe to the offline double** on absent/unrecognised values;
   only an exact literal (`"ollama"`) selects the live provider. `OLLAMA_HOST` is left entirely to
   the SDK's own `os.getenv` (§1.6), and `.env.example`'s reserved line is uncommented with a note.
B) **Env var read at composition time, `OLLAMA_HOST` read explicitly by us** and passed to
   `ollama.Client(host=...)`, so the resolved host is visible in our own logs and failure messages
   rather than buried in the SDK.
C) **Add `MEMO_PROVIDER` / `OLLAMA_HOST` as fields on `Settings`** — the SEC-3 single source, at the
   cost of reopening frozen `secrets_config` and moving it off exactly six fields.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: A.** C is the only option that reopens a frozen unit, and it does so for a
> **non-credential**: a localhost URL for an unauthenticated daemon is not secret material, which is
> the precise scope `dependencies.py:84-86` and `llm_client.py:109-114` both draw around SEC-3.
> ⚑ The `SESSION_COOKIE_SECURE` precedent (`dependencies.py:83-97`) is exact — same file, same
> `os.environ` read, same explicitly-stated reason (*"avoids C-B: frozen `Settings` stays at exactly
> six fields"*) — and its **fail-safe polarity discipline** should be copied verbatim: *"only the
> exact literal … so a forgotten variable can never silently downgrade production."* Here that means
> **absent ⇒ offline double**, so an unset variable can never accidentally put a real model in front
> of a user. ⚠️ B's motivation is legitimate and it is the one part of A worth reconsidering: if
> Question 4 selects a design with a diagnostic failure message, that message is much more useful
> if it can name the host it tried. **A with B's logging is a defensible hybrid — say so under
> "Other" if that is the intent.**

[Answer]: A, with B's diagnostic logging folded in as a hybrid — env var read via os.environ at composition time, fail-safe to the offline double on any absent/unrecognized value (only the exact literal “ollama” selects live), OLLAMA_HOST left to the SDK's own os.getenv resolution, but the resolved host logged at the point of failure so a diagnostic message can name what it tried to reach. No secrets_config reopening.

---

## Question 4
Ollama is unreachable or not running. What is the designed behaviour? ⚠️ Read §1.3 and §1.4 before
answering — the current code has **no** exception handling on this path and `case_seams()` is
`lru_cache`d.

A) **Fail loudly, per draft, inside the WIRE-1 envelope.** No reachability check at construction.
   Catch the connection failure at the drafting boundary and map it to a WIRE-1 §4 error — a **503**
   if the contract can carry one, else the existing **500** — so the case does **not** silently
   become `FAILED` and the operator gets a diagnosable body rather than Starlette's plain-text 500.
B) **Fall back to the offline double** when Ollama is unreachable, so drafting always succeeds.
C) **Refuse to select at composition time** — probe Ollama in `_CompositionSeams.__init__` and fall
   back to the offline double (or raise) based on the result.
D) **A, plus a lightweight per-draft pre-check** — a cheap liveness call before the drafting call,
   so the failure is attributed to *"Ollama is not running"* rather than surfacing as a generic
   client exception from deep inside the graph.
E) Other (please describe after [Answer]: tag below)

> **Recommendation: A, and ⛔ C should be rejected outright.** §1.4 is decisive against C:
> `case_seams()` is `@lru_cache(maxsize=1)` and is constructed on the **first submit**, not the
> first draft — so a construction-time probe would (i) run during **submission**, which has no
> business depending on the LLM, and (ii) be cached for the process's entire life, so an Ollama
> restart is never noticed and an Ollama outage at that one moment poisons every later draft. ⚑ The
> established idiom for exactly this is right next door: `outlier_model()` is `lru_cache`d but
> **resolved at call time inside `score_outlier`** (`dependencies.py:281`, comment at `:277-279`),
> specifically so construction stays cheap.
>
> ⛔ **B is the option to argue about, and the recommendation is against it.** A silent fallback
> means a user can be shown a `PLACEHOLDER MEMO … NOT BY A LANGUAGE MODEL` while believing the live
> provider is running. The stamp would still be honest — that is what it is for — but the *system*
> would have chosen to degrade without saying so, and this build has refused that shape before by
> name: Q6(b)'s *"silent `outlier=null` fallback was refused"* in favour of a loud
> `FileNotFoundError` (guide-state, register #2 entry). ⚠️ **A has a real cost that must be accepted
> openly**: with no Ollama, drafting simply does not work, and the demo path stops. That is the
> correct trade only if it is stated.
>
> ⚑ **Whatever is chosen, §1.3's gap must be closed by this pass**, because this pass is what makes
> it reachable. Today an uncaught `ConnectionError` produces a **plain-text 500 that violates
> `main.py:97`'s own stated invariant**. A genuine open sub-question the answer should address: does
> the catch belong in **`submission.py`** (route-local, no frozen unit touched, but only covers R11)
> or as a **generic `Exception` handler in `main.py`** (covers every route, restores the stated
> invariant globally, but is a broader change than this pass strictly needs)? **D** is worth taking
> if and only if the diagnostic gain justifies an extra round-trip per draft; note it does **not**
> remove the need for the catch, since the daemon can die between the pre-check and the call.

[Answer]: A — fail loudly per draft, inside the WIRE-1 envelope. C is rejected outright per the lru_cache timing argument. B (silent offline fallback) is rejected — it would let a user believe a live provider is running when it silently isn't, which this project has refused before (Q6(b)'s corpus fallback). On the design fork the recommendation left open: catch locally in submission.py for this pass (matching Q2's R11-specific scope), not a generic main.py Exception handler — that's a larger, separate change. Open a small register item noting main.py:97's stated “no route can emit a non-contract body” invariant has no mechanical enforcement against uncaught exceptions across ALL routes (not just R11) — a real, disclosed gap, not fixed in this pass. Take D's per-draft liveness pre-check as well, for diagnostic clarity, understood as a nicety on top of the catch, not a replacement for it.

---

## Question 5
`_CompositionSeams` conflates model-ID and `model_version`-stamp (§1.2). How is that fixed, and what
does the Ollama stamp carry?

A) **Mirror `_SeedSeams` exactly**: parameterise `_CompositionSeams.__init__` with `model=` and
   `model_version=`, and stamp `f"{model_id}+ollama-python-{version('ollama')}"` — i.e. the
   **SDK** version, byte-for-byte the shape `seed_demo_cases.py:407` already uses for Gemini.
B) **Mirror the split, but stamp the SERVER not the SDK** — carry the Ollama **server/model**
   identity (via `ollama.show()`'s model digest, or the daemon's version), on the grounds that what
   produced the prose is the server and the model weights, not the Python wrapper.
C) **Mirror the split, and stamp BOTH** — model ID + model digest + SDK version, the fullest
   provenance triple this seam can express.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: B, leaning C — and this is the question where register #22 does real work.**
> A is the safest by precedent, and precedent is not nothing: `_SeedSeams`' Gemini stamp is
> SDK-versioned and this would match it exactly. ⛔ **But the Gemini case and the Ollama case are not
> analogous.** With Gemini, `gemini-2.5-flash` is a server-side moving target and the SDK version is
> about all the client can honestly attest to. With Ollama, the **weights are local, pinned, and
> content-addressable** — the user chose `llama3.1:8b-instruct-q4_K_M` *specifically for its fixed
> quantization*, and `ollama.show()` can return a **digest** over exactly those bytes. ⚑ Stamping
> `ollama-python-0.6.2` would record the version of the thing that **did not** generate the prose
> while omitting the one identifier that pins what did.
>
> Register **#22 `MEMO-PROSE-NOT-BIT-REPRODUCIBLE`** is the reason this matters rather than being
> pedantry: the digest is the strongest reproducibility anchor available anywhere in this build's
> LLM path, and it is available **only** for the local provider. ⚠️ Two honest limits to state
> wherever the stamp is documented: a digest pins the **weights**, not the sampling stack, so it
> **narrows #22 and does not close it** — the same distinction `outlier_canonical.py` already draws
> (*"guarantees the persisted representation, not floating-point computation"*, `dependencies.py:272-275`);
> and `show()` is an extra call whose failure must not break drafting. ⛔ **C is stronger than B and
> costs one string** — the only argument against it is `audit_record.model_version`'s readability as
> a `VARCHAR` a human reads in the history view. **If the stamp would exceed comfortable display
> length in `ForensicTupleRegion.jsx:22`, prefer B; otherwise C.**

[Answer]: C — stamp all three: model ID, a model digest via ollama.show(), and the SDK version. If the combined string would be uncomfortably long for ForensicTupleRegion.jsx's display, truncate the digest to a short form (e.g., first 12 characters, git-short-hash style) rather than dropping a component. Document explicitly, per the recommendation, that the digest pins the weights, not the sampling stack — narrows register #22, does not close it.

---

## Question 6
Gemini's guardrails (`CappedGeminiClient`, `build_gemini_client`) have **never run through R11** —
only through `seed_demo_cases.py --real-llm`, and their real-spend paths carry `# pragma: no cover`
(`llm_client.py:129`, `:132`). Does this pass prove them end-to-end through the live route?

A) **Defer.** Ollama is the default; wire and prove Ollama only. Record explicitly that Gemini
   remains **unproven through the request path**, and leave #18's Gemini-specific gaps open.
B) **Close both.** Wire Gemini as a second selectable provider in the same pass and prove both live,
   fully discharging #18.
C) **Wire Gemini, prove it only if it costs nothing** — make it selectable, but require only the
   refusal paths (gate off, empty key) to be exercised live, not a real billed call.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: A.** ⚑ B would make a **billed API call a prerequisite for this pass passing** —
> it needs a live `GEMINI_API_KEY`, real network and real spend, which is the exact combination
> `BUILD-COMPLETION-REPORT.md:158` names as why #18 opened in the first place. Bundling that into
> the pass that first makes *any* live provider work means a Gemini billing problem blocks an Ollama
> deliverable. C is a fair middle and its refusal-path testing has genuine value, but ⚠️ it invites a
> specific misreading this project has been careful about: *"Gemini is wired and its guards were
> tested"* would be true of the **refusals** and false of the **success path**, and the two are
> easily conflated in a later summary.
>
> ⛔ **A carries one obligation.** If #18 is described as *progressed* after this pass, the
> description must say **which half** — a live Ollama memo closes gap (iii) for the **showcase**
> provider and does **not** make Gemini's production client proven. ⚑ Note the sharp asymmetry
> Question 9 then inherits: **the provider being proven live is the one exempt from the quality
> gates, and the one that is quality-gated remains unproven live.**

[Answer]: A — defer Gemini entirely. Do not bundle a billed API call as a prerequisite for this pass. State explicitly in whatever closes this pass which half of #18 moved (Ollama/showcase proven live; Gemini/production remains unproven live) so it can't be misread as full closure.

---

## Question 7
R11 is a sync `def` on FastAPI's threadpool, with **no timeout on either side** and an SDK that
defaults to **no timeout at all** (§1.5). A cold model load can take tens of seconds. What bounds it?

A) **Client-side timeout only** — pass an explicit generous `timeout` to `ollama.Client(...)`
   (comfortably above a cold load, e.g. 120 s), leaving R11's threadpool shape untouched.
B) **Client-side timeout + a concurrency bound**, reusing `parse_concurrency.py`'s
   `anyio.CapacityLimiter` idiom so N concurrent drafts cannot pin N threadpool threads against one
   single-threaded local daemon.
C) **No timeout** — accept unbounded waits, matching today's behaviour and the SDK's own default.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: B, with A as the acceptable minimum.** ⛔ C is the status quo and the status quo
> is a **thread leak waiting to happen**: `ollama._client` sets `timeout: Any = None`, explicitly
> overriding httpx's default, so a hung daemon holds a FastAPI threadpool thread **forever** — and
> that pool is shared with **R10's JSON submissions** (`submission.py:169`), so enough stuck drafts
> starve submission itself. ⚑ The timeout must be **generous, not tight** — the failure mode to
> avoid is killing a legitimate cold load, which is exactly the misdiagnosis `document-upload`'s §9
> step 8 was rewritten to prevent (*"the original would have read the design working correctly as a
> failure"*).
>
> B's extra half is worth its cost because ⚑ **a local Ollama daemon is a far scarcer resource than
> a cloud API**: `MAX_CONCURRENT_PARSES = 2` exists for exactly this reasoning applied to
> subprocesses, and `anyio.CapacityLimiter` is already the established primitive here — including
> the recorded reason it was chosen over `asyncio.Semaphore` (*"bound to a different event loop"*,
> guide-state's Fold-7 deviation 2). ⚠️ A real caveat against B: R11 is a **sync** `def`, so the
> limiter cannot be acquired the way `run_bounded_parse` does it from an `async` caller. Choosing B
> means either converting R11 to `async def` + `run_in_threadpool` (mirroring R10) or using a
> thread-appropriate primitive — **a genuine design fork the answer should name, not leave implied.**

[Answer]: B — client-side timeout (generous, e.g. 120s, tuned to comfortably exceed a cold load) plus a concurrency bound via anyio.CapacityLimiter, matching parse_concurrency.py's established idiom. Take the design fork explicitly: convert R11 to async def + run_in_threadpool to acquire the limiter, mirroring R10's shape, rather than reaching for a thread-inappropriate primitive.

---

## Question 8
This would be the first import of `memo_extensions` from `backend/app/`. ⚠️ §1.7 found it is **not
mechanically gated anywhere**, and that `case_lifecycle/pipeline.py:38` **already imports it on the
live path**. Does it still get its own explicit sign-off gate?

A) **Yes — its own gate, signed off in writing before any import is added**, same discipline as
   WIRE1-Fold-6's G1/G2/G3 and Fold-7's G2, on the ground that *"not mechanically forbidden"* has
   never been this project's standard for a structural first.
B) **Yes, and additionally create the missing guard** — add `memo_extensions` to an explicit
   allowlist in `test_no_write_route.py` or `test_frozen_untouched.py` so the import direction is
   mechanically pinned from now on, created **before** the import that needs it (Fold-7's G2 shape:
   *"the guard is created BEFORE the first module that writes, so that module's first encounter
   with it is a FAILURE"*).
C) **No separate gate** — it is not a frozen unit, no guard forbids it, and it is already in the
   production import graph via `case_lifecycle`. Note it in the plan and proceed.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: B.** ⚑ The finding that no guard exists is an argument **for** B rather than for
> C, and this project has taken that exact turn before: Fold C found `test_no_write_route.py` *"had
> no opinion about file I/O at all"*, and the response was to **create** `_FILESYSTEM_WRITE_MODULES`
> rather than to conclude that filesystem writes were fine. That guard now has *"exactly one
> member"* and the discipline is recorded as *"the inverse of register #2's G3 — there a guard
> existed and was narrowed; here a guard did not exist and was created."* This is the same shape a
> third time.
>
> ⚠️ **Where C's argument has genuine force, stated fairly**: `memo_extensions` is **not** frozen, it
> is **already** imported by `case_lifecycle/pipeline.py:38`, and calling this *"the first import"*
> without that qualifier would be **inaccurate** — the accurate claim is *"the first from
> `backend/app/`."* ⛔ Any gate written under A or B must state it that way, or it documents a
> premise that is false. B's cost is one small guard and one deliberately-RED first run; the benefit
> is that the next module reaching into `memo_extensions` from the composition root meets an
> assertion instead of nothing.

[Answer]: B — yes, its own explicit sign-off gate, AND create the missing guard (an explicit allowlist in test_no_write_route.py or test_frozen_untouched.py), created before the import that needs it, same RED-first discipline as Fold-7's G2. State the gate's justification accurately: this is the first import of memo_extensions from backend/app/ specifically, not the first production import overall (case_lifecycle already does it) — don't let the gate's own text overclaim.

---

## Question 9
⛔ **The precedence reversal.** `PROJECT-BRIEF.md` §9 classes Ollama as **SHOWCASE — *"wired, NOT
tested against acceptance criteria"*** — and `llm_judge/pipeline.py:35` excludes it from
`IN_GATE_PROVIDERS` **by design**. Making it the default **LIVE** provider means real users see
memos from the one provider deliberately never subjected to groundedness or promptfoo judging. How
is that resolved?

A) **Proceed, with the exemption made loudly visible at the surface** — accept Ollama as the live
   default, and require the memo to be visibly marked as coming from a non-quality-gated provider
   (a stamp convention and/or UI copy), so no reader can mistake it for a gated memo.
B) **Proceed, and narrow the exemption instead** — bring Ollama into `IN_GATE_PROVIDERS` for
   groundedness at least, on the ground that *"exempt because showcase"* stops being defensible the
   moment it is the default.
C) **Do not make it the default.** Wire Ollama as explicitly opt-in, keep the offline double as the
   default, so the never-gated provider is only ever reachable by deliberate selection.
D) **Proceed unchanged** — the decision-level gates (temperature=0, CON-BR2-TYPE, bias-swap,
   reproducibility) all hold for Ollama, the recommendation itself is LLM-free, and the system is
   advisory-only with a human gate, so memo-quality exemption is an acceptable residual.
E) Other (please describe after [Answer]: tag below)

> **Recommendation: C, with A's marking as a required companion — and the tension is real, not
> dissolvable.** ⛔ **D is the answer to resist**, precisely because every clause in it is *true*.
> The rules engine is LLM-free (`PROJECT-BRIEF` §11.1), `CON-BR2-TYPE` means the model **cannot**
> represent a recommendation change (`test_provgate.py:31`), `temperature=0` holds
> (`provider_showcase.py:52`), and nothing is decided without an underwriter. All of that bounds the
> **decision**. ⚑ **None of it bounds the PROSE**, and prose is the entire deliverable here — the
> memo is what a human reads before exercising the approval gate. *"LLM-as-judge score ≥4/5"*
> (`PROJECT-BRIEF` §6) exists to bound exactly that, and Ollama is exempt from it.
>
> C is recommended because it is **the only option that changes nothing about the exemption's
> premise**. `PROJECT-BRIEF` §9's *"wired, not tested against acceptance criteria"* stays literally
> true of an opt-in showcase provider; it becomes strained the moment "showcase" is what everyone
> gets by default. ⚑ This also composes with Question 3's fail-safe polarity at zero extra cost:
> **absent env var ⇒ offline double** already *is* opt-in. Under C the live memo remains fully
> reachable for demonstration and for §10's verification — it just is not what an unconfigured
> deployment serves.
>
> ⚠️ **B is the intellectually cleanest answer and is being recommended against on scope, not
> merit.** Bringing Ollama in-gate would require a real judged corpus run against the ≥4/5 threshold
> — `JUDGE-EVAL-DEFERRED` is still open — and would very likely **fail** for an 8B quantized local
> model, which would then block this pass on a result that is not a defect. ⛔ **A alone is
> insufficient**: marking is necessary under any of A/B/C but does not by itself resolve making the
> ungated provider the default. **If the answer is A or D, that is a legitimate call — but it should
> be recorded as a deliberate, reasoned narrowing of `PROJECT-BRIEF` §9's showcase classification,
> with a register item opened, rather than left as a side effect of a wiring pass.**

[Answer]: C — do not make Ollama the default; wire it as explicitly opt-in, with the offline double remaining the default. Pair this with A's requirement: when Ollama IS selected and used, mark the output as coming from a non-quality-gated provider, visibly, not just via the existing honest model_version stamp. Since this choice does NOT narrow PROJECT-BRIEF §9's showcase classification (opt-in-showcase is exactly what §9 already describes), no register item is needed for the classification itself — but log the decision in whatever closes this pass so it's traceable as a deliberate choice, not a default that happened to land this way.

---

## Question 10
The manual verification plan. ⚠️ Two constraints shape it: the drafting trigger exists in the UI
**only in the accepted panel immediately after submitting** (register #2's standing residual — *"a
pending case reached any other way … has no UI draft affordance"*), and **`model_version` is not on
R4** (§1.9) — it reaches the UI only in the history view's forensic tuple, **after commit**. What is
the scope?

A) **Full chain, submit → draft → commit → history.** Submit fresh through the browser; draft from
   the accepted panel; read `pending_recommendation.model_version` in `psql`; commit; read
   `audit_record.model_version` in `psql`; confirm the same string on R7 via `curl`; confirm it
   rendered at `history-detail-model-version` in the UI. Plus: confirm the prose is genuinely
   model-generated (not the placeholder), confirm citation validation passed against a **real**
   rule ID, and exercise the Question 4 failure mode by stopping Ollama and re-drafting.
B) **Draft only, no commit** — submit, draft, verify the stamp and prose in `psql` and `curl`. Skip
   commit and the UI, since the drafting path is what changed.
C) **Full chain plus a reproducibility probe** — everything in A, and additionally draft the *same*
   profile twice to observe whether `temperature=0` plus a pinned quantization actually yields
   identical prose, recording the result **as an observation against register #22, not as a claim**.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: C.** ⛔ B is too narrow for a specific structural reason rather than a general
> preference: **`model_version` never appears on R4**, so a draft-only walkthrough **cannot see the
> stamp in the UI at all** and would verify the honest-stamp requirement in `psql` only. The whole
> point of the stamp is that it survives to a human reading a committed decision — that is the
> journey `ForensicTupleRegion.jsx:22` exists for, and only a commit reaches it.
>
> C's extra probe is recommended because ⚑ **this pass creates the first opportunity in this build's
> history to observe register #22 empirically.** Until now every memo came from a deterministic
> string, so #22 has been a *concern* with no evidence either way. Two drafts of one profile against
> pinned local weights at `temperature=0` is a cheap, genuinely informative observation. ⛔ **It must
> be recorded as an observation, not a determinism claim** — a single repetition is not the
> *"same input × 10 runs"* calibration `PROJECT-BRIEF` §5.1 specifies, and if the prose **does**
> differ that is a **finding about #22, not a failure of this pass.**
>
> ⚑ Three practical notes for whoever writes §10 out in full. **(i)** The draft must be triggered
> **fresh post-submission** — register #2's residual means a reloaded or seeded case has no UI
> affordance, and a walkthrough that forgets this will read a working design as broken, the exact
> failure `document-upload` §9 step 8 was rewritten to prevent. **(ii)** The **first** live draft
> also pays the ~2.6 s lazy corpus fit (`dependencies.py:306-309`) **plus** a cold model load — the
> two costs stack, and the combined first-draft latency should be **expected, not investigated**.
> **(iii)** Verify the citation is a **real rule ID from the rulebook**, not merely non-empty:
> `offline_memo_double.py:52-56` records that the seed script's original double cited a hardcoded
> `DTI-001` *"a rule id that does not exist in this build"*, so **every seeded case silently landed
> in `FAILED`** — a real model can reintroduce that failure by hallucinating a plausible-looking ID,
> and `CitationValidator` refusing it would present as *"drafting produced no memo"* → **500**.

[Answer]: C — full chain (submit → draft → commit → history) plus the two-draft reproducibility probe, recorded explicitly as an observation against register #22, not a determinism claim. Incorporate all three practical notes: trigger drafting fresh post-submission (not on a reloaded/seeded case), expect the first draft to pay both the corpus-fit AND cold-model-load costs stacked together, and specifically verify the cited rule ID is real (not a hallucinated-but-plausible one that would silently fail citation validation the way the original seed double's hardcoded DTI-001 did).

---

## 3. Stop gate

⛔ **NOTHING PROCEEDS UNTIL ALL TEN ANSWERS ARE PROVIDED.**

On answers, the next artifact is a **code-generation plan** with explicit numbered steps and
checkboxes, presented for its own separate approval before any code is written — per
`CLAUDE.md`'s Code Generation two-part rule. In particular:

* ⛔ **No backend file is edited before that second approval.**
* ⛔ **Question 8's gate (if A or B) is signed off separately** from the code-gen plan, before the
  import exists.
* ⛔ **Question 9's outcome, if it narrows `PROJECT-BRIEF` §9's showcase classification, is recorded
  as a register item** rather than absorbed into a wiring pass's close-out. ⚑ Registers #30 and #31
  were both opened **late**, as *"re-opened promises — the answers that created them named the
  instrument and the instrument was never picked up."* This plan names the instrument here so that
  does not happen a third time.

### Holds asserted for this document

⛔ **No backend file touched** · no code written · no test run modified · `PROJECT-BRIEF.md`
unchanged · `guide-state.md` / `audit.md` / `BUILD-COMPLETION-REPORT.md` unchanged by this file ·
working tree otherwise clean at `bd3875d`.

---

## 4. Ambiguity check against the complete answer set — **2026-08-16**

⛔ **RESULT: NOT CLEAN. One genuine contradiction found, and it blocks the code-gen plan.**
Two of the three named interactions resolve cleanly; the third does not. Two corrections to this
document's **own earlier findings** were also forced by the check and are recorded first, because
one of them was an error in §1.9 that would otherwise have propagated into the verification plan.

### 4.0 ⚠️ TWO CORRECTIONS TO THIS DOCUMENT, made before the check's own results

**(i) ⛔ §1.9 WAS WRONG. R4 *does* carry `model_version`.** §1.9 claimed *"R4 `GET /applications/{id}/memo`
does NOT carry `model_version`"*, citing zero occurrences of that string in `projections.py`. **The
grep was right and the conclusion was wrong.** `projections.py:184` emits
`"memo": memo.model_dump(mode="json")`, and `DecisionMemo.model_version` is a required field
(`memo_agent_core/schemas.py:108`), listed in WIRE-1 §5's own `DecisionMemo` shape. **The stamp
therefore travels on R4, nested at `memo.model_version`, immediately after drafting and before any
commit.** ⚑ The half of §1.9 that survives is the **UI** half: no `memoView` component renders it
(verified — zero matches in `frontend/src/memoView/` outside `__tests__/`), so on screen it still
appears only in the history forensic tuple at `ForensicTupleRegion.jsx:22`, post-commit. **Q10's
answer (C, full chain) is unaffected and remains correct** — but the reason given for rejecting
option B was partly wrong, and `curl` can now confirm the stamp one step earlier than §10 assumed.

**(ii) Q4's open 503-vs-500 sub-question resolves to 500, on the contract rather than on taste.**
WIRE-1 §4's status table (`api-contract.md:88-97`) is **400 / 401 / 403 / 404 / 409 / 413 / 422 /
500**, mirrored exactly by `errors.py:29-38` plus the additive `501`. ⛔ **There is no 503 and adding
one would be a fifth WIRE-1 Fold** — a contract amendment with its own gate. Q4's answer explicitly
scopes this pass away from *"larger, separate change[s]"*, so **`INTERNAL_ERROR` (500) it is**, which
is also what `submission.py:214` already raises for a drafting failure. **No Fold. No new gate.**

### 4.1 What the answers decided beyond the recommendations

Every headline letter matched. **Three things the answers did that the recommendations did not**,
recorded because these are the actual decisions:

1. **Q4 resolved the deliberately-open design fork** — the catch is **route-local in `submission.py`**,
   not a generic `main.py` handler, and the *general* gap is to be **recorded as a register item**
   rather than fixed. ⚑ This is the project's established shape: close the reachable path, promote
   the underlying capability to its own item (exactly how **#29** was split out of **#28**).
2. **Q4 took option D *in addition to* A**, explicitly as *"a nicety on top of the catch, not a
   replacement for it."*
3. ⛔ **Q9 DECLINED the recommended register item**, on the stated argument that opt-in-showcase
   *"is exactly what §9 already describes"* and therefore narrows nothing. ⚑ **The argument is
   sound and is accepted**: §9's classification is *"wired, NOT tested against acceptance
   criteria"*, and an opt-in provider satisfies that literally. The decision is to be **logged in
   the pass's close-out** instead, which is what makes it traceable without inventing a register
   item for a non-change.

### 4.2 Check 1 — Q4's route-local catch × Q7's `async def` conversion: ✅ **COMPOSE, with a named scope expansion**

They compose. Exceptions raised on a worker thread propagate normally to the awaiting caller, so a
`try/except` around the awaited bounded draft catches an Ollama failure exactly as it would today.

⚠️ **But Q7's conversion is a THREE-call change, not a one-call change, and the plan must say so.**
`trigger_drafting` currently runs **entirely** on a threadpool thread because it is a plain `def`,
which is why its **two synchronous `pipeline.read()` calls** (`submission.py:209` and `:216`) are
harmless today. Converting to `async def` moves the function body onto the **event loop**, and those
two calls are blocking SQLAlchemy round-trips through `PostgresCaseStore`. ⛔ **Offloading only the
draft would leave two blocking DB calls on the loop** — a regression that **no existing test would
catch**, since `TestClient` would still pass, merely with the loop stalled.

⚑ The precedent settles the correct shape: **R10 is `async def` and offloads *everything* blocking**
(`run_in_threadpool(_intake_and_submit, …)` at `:169`, `run_bounded_parse(…)` at `:160`). Mirroring
R10 means mirroring that discipline, not just its `async` keyword. ⚠️ The same applies to Q4's
option-D liveness pre-check: if it performs network I/O it must be offloaded too, or it
reintroduces on the loop precisely what the conversion was meant to keep off it.

**Resolvable without a decision** — it is an underspecification the check surfaced, not a conflict
between answers. It becomes a named step and a stop-gate in the code-gen plan.

### 4.3 Check 2 — Q1's retained call cap × Q4's fail-loud design: ⛔ **GENUINE CONTRADICTION — BLOCKING**

**The envelope half is fine.** `LLMCallCapExceeded` is a `RuntimeError` raised inside `generate()`
(`llm_client.py:66-69`) and propagates through the identical five layers as a `ConnectionError`, so
Q4's catch must cover **both** or the gap it exists to close stays half-open. That is a design
detail, not a contradiction, and the answer to it is *"same envelope, and the catch must not be
narrowed to connection errors alone."*

⛔ **The contradiction is between Q1's stated PURPOSE and Q1's chosen MECHANISM.**

Q1's answer reframes the cap as **"runaway citation-retry-loop containment (provider-independent),
not spend control."** But the mechanism it adopts wholesale from `CappedGeminiClient` is a
**per-instance, monotonic counter that is never reset** (`llm_client.py:60-70`: `self._count = 0` at
construction, `self._count += 1` per call, refuse at `max_calls`). Combine that with where the client
will live — inside `_CompositionSeams`, behind `@lru_cache(maxsize=1)` (`dependencies.py:318`) — and
the result is **one counter for the entire life of the server process**.

⚑ **That mechanism is per-process BUDGET, which is a spend-control semantic — the exact framing Q1's
answer said it was moving away from.** Runaway-loop containment is inherently **per-draft**: it
should bound how many times *one* drafting attempt may re-enter the model, and it should reset when
the next draft begins.

⛔ **The practical consequence is not theoretical.** At `max_calls=20`, with the citation-retry loop
able to consume several calls per draft (`orchestrator.py:118`, `MEMO_CITATION_RETRY_CAP`), a
long-lived server permanently stops drafting after roughly **five to twenty drafts** and returns
500s until restarted — with no way to reset short of a process bounce. ⚑ **The shape was safe in
`CappedGeminiClient` because its only caller was `seed_demo_cases.py`, a short-lived script where
"per-process" ≈ "per-run".** Moving it behind a cached seam in a long-running FastAPI app changes
what it means, and Q1's answer did not anticipate that because Q1 was framed on the seed-script
precedent.

⚠️ **Q10's own verification plan would plausibly hit this** — it drafts, re-drafts for the
reproducibility probe, and exercises the failure path, all in one server process.

**This requires a decision and is asked as Clarification Question 1** (see
`live-llm-drafting-clarification-questions.md`). It is not resolvable by inference: each option is
defensible and they produce materially different runtime behaviour.

### 4.4 Check 3 — Q8's new guard × `case_lifecycle`'s existing `memo_extensions` import: ✅ **CLEAN, with a naming requirement**

⛔ **No conflict, and nothing about `case_lifecycle` needs to be accounted for or duplicated —
structurally, not merely by convention.** Both candidate guard files define their scan set
identically:

```python
PRODUCTION_FILES = sorted(p for p in APP_ROOT.rglob("*.py") if "tests" not in p.parts)
```

(`test_no_write_route.py:140`, `test_frozen_untouched.py:16`.) The set is rooted at **`APP_ROOT`**,
i.e. `backend/app/` only. `case_lifecycle/pipeline.py` is outside it and is therefore **invisible to
any allowlist added there** — the guard *cannot* see that import even if someone tried to make it.
✅ Confirms Q8's own instruction that the gate's text must say *"the first import from `backend/app/`"*.

⚑ **`test_no_write_route.py` is the right home**, not `test_frozen_untouched.py`: it already hosts
two allowlists of exactly this shape — `_PIPELINE_MODULES` (`:100`) and `_FILESYSTEM_WRITE_MODULES`
(`:115`) — with the established `frozenset({...})` idiom and the recorded convention that two
differently-scoped claims must not be merged into one constant (`:96-99`).

⚠️ **One requirement, and it is exactly the failure this file has recorded before.** The guard's
name must carry its scope. A bare `_MEMO_EXTENSIONS_IMPORT_MODULES` reads as *"the modules that may
import memo_extensions"* — a claim **broader than what it checks**, since it is blind to every tree
outside `backend/app/`. ⛔ That is the defect the TRIGGER-1 narrowing was written to fix: *"the old
guard was ALSO BROADER THAN ITS OWN NAME — it said 'the read routes' but scanned every production
file."* The name (or an adjacent comment carrying the same weight) must state the `backend/app/`
scope so it cannot go stale into an overclaim.

### 4.5 Summary

| Check | Result | Blocking? |
|---|---|---|
| §4.0(i) R4 carries `model_version` after all | **Correction to this document** | No — Q10 stands |
| §4.0(ii) 503 vs 500 | **Resolved to 500 on the contract** — no Fold, no gate | No |
| §4.2 Q4 catch × Q7 async conversion | **Compose**; conversion is a 3-call change | No — becomes a stop-gate |
| §4.3 Q1 cap × Q4 fail-loud | ⛔ **CONTRADICTION** — purpose vs mechanism | ⛔ **YES** |
| §4.4 Q8 guard × `case_lifecycle` | **Clean**; naming requirement only | No |

⛔ **The code-generation plan is NOT written until §4.3 is answered.** Writing a staged plan on an
unresolved premise would produce stages whose content was decided by inference — which is the
"invented intermediate state" this project has refused before (register #2's commit-boundary
reasoning: *"the design plan's §5 three-way split would have required … producing commits whose
exact content was never run"*).

---

## 5. Ambiguity RE-CHECK against the corrected, complete answer set — **2026-08-16**

⚑ **Scope**: the ten Q-answers **plus** the two clarification answers (per-draft cap; guard home and
name), **plus** the two §4.0 corrections. Result summarized at §5.5.

### 5.1 The four items carried in from §4 — all now closed

| Item | Status |
|---|---|
| §4.0(i) R4 carries `model_version` | ✅ **CONFIRMED AS THE FINAL FINDING** and folded into the code-gen plan's manual-verification section. `curl` on R4 confirms the stamp **immediately after drafting, pre-commit**, at `memo.model_version`. The UI half is unchanged: no `memoView` component renders it today, so on screen it is history-only, post-commit. |
| §4.0(ii) 503 vs 500 | ✅ **CLOSED AS FINAL — 500 `internal_error`, no 503.** WIRE-1 §4's table (`api-contract.md:88-97`) has no 503; adding one would be a **fifth Fold** with its own gate, which Q4 scopes away. Recorded as answered, not left open. |
| §4.2 Q4 catch × Q7 async conversion | ✅ **CLOSED** — becomes **STOP-GATE 4A**: offload **all three** blocking calls, not just the LLM one. |
| §4.4 Q8 guard × `case_lifecycle` | ✅ **CLOSED** — `test_no_write_route.py`, name `_MEMO_EXTENSIONS_IMPORT_MODULES_FROM_APP`. ⚑ Leading underscore added to match the file's two existing allowlists (`_PIPELINE_MODULES`, `_FILESYSTEM_WRITE_MODULES`); the scope-carrying suffix is exactly as directed. |

### 5.2 ⛔ ONE NEW INTERACTION, created by the clarification answer itself — RESOLVED BY DESIGN

**The per-draft cap (Clarification A) and the concurrency bound (Q7 B) collide on shared mutable
state.** Neither answer is wrong; the combination is new.

The clarification answer suggests the counter *"be explicitly reset at the start of each `draft()`
call."* ⚠️ **A naive reset is a race.** With `CapacityLimiter(n>1)`, two drafts run concurrently on
two threadpool threads and — because the orchestrator, adapter and client are built **once** in
`_CompositionSeams.__init__` and cached behind `@lru_cache(maxsize=1)` — **they share one client
instance.** Draft B entering and zeroing the counter would wipe draft A's count mid-flight, so the
cap would bound nothing precisely when load makes it matter.

⛔ **And the reset cannot go in `CasePipeline.draft()`** — that is `case_lifecycle`, and touching it
needs an authorized reopening (this would be U24's fifth). ⚑ **It does not need to**:
`_CompositionSeams.draft_memo` (`dependencies.py:283-286`) is called **exactly once per draft**
(`pipeline.py:186`), lives in `backend/app/`, is not frozen, and is therefore the natural per-draft
boundary — reachable with **no reopening at all**.

**Resolution — a `threading.local()` counter, reset at `draft_memo` entry.** ⚑ The premise that makes
this exactly right: under Q7's design the **entire** `pipeline.draft` is handed to
`anyio.to_thread.run_sync` as one callable, so a draft — including every citation retry inside the
graph — runs start-to-finish on **one worker thread**. Thread-local is therefore **precisely
per-draft**, at any limiter value.

⛔ **The rejected alternative, and why it is rejected on principle rather than preference.** Setting
the draft limiter to **1** would serialize drafts and make a naive reset safe — but it would make
**correctness depend on the value of a tuning constant**. Someone later raising the bound for
throughput would silently reintroduce the race with nothing failing. That is exactly the drift
`parse_concurrency.py:14-18` was written against: *"Two separate mechanisms … can drift apart; a
later edit could offload without acquiring, and nothing would notice until production."*
**The bound is a performance knob; it must never also be a correctness guarantee.**

⚠️ **Two invariants this design depends on, both to be pinned by tests rather than assumed**:
(1) threads are **pooled and reused**, so the counter must be **reset at entry**, never merely
lazily initialized; (2) a draft must not be split across threads — if the orchestrator were ever
made async or partially offloaded, thread-local would stop meaning per-draft. Both get an explicit
test and a comment at the constant.

### 5.3 ✅ Distinguishable failures — confirmed contract-compatible, no Fold

Two exception types, two messages, one status:

| Condition | Exception | Status / code | Message names the operator action |
|---|---|---|---|
| daemon unreachable | `OllamaUnreachable` | 500 `internal_error` | the resolved host — *start Ollama* |
| per-draft cap hit | `OllamaCallCapExceeded` | 500 `internal_error` | the cap and that it is per-draft — *not* an availability problem |

⚑ **Contract-compatible without amendment.** WIRE-1 §4 specifies `message` only as
*"human-readable"* and `detail` as an optional object; `errors.py:47` builds `detail` as an open
dict. So a machine-readable discriminator may ride in `detail` **without a Fold**. ⛔ **The catch
must be written against the two named types, never a bare `except Exception`** — a bare catch would
re-merge exactly what this separation exists to keep apart, and would additionally swallow genuine
programming errors as *"Ollama problems."*

### 5.4 ⚠️ ONE ITEM THE ANSWERS UNDERSPECIFY — carried to a gate, not resolved unilaterally

**Q9 requires the live output be marked as non-quality-gated *"visibly, not just via the existing
honest `model_version` stamp."*** The re-check finds that **every surface satisfying both halves of
that sentence costs something the answers have not authorized**:

| Where the marking could go | Cost |
|---|---|
| **A** — inside the `model_version` string | **Zero.** Travels everywhere, already rendered at `ForensicTupleRegion.jsx:22`. ⚠️ **But it is the stamp**, which Q9's wording excludes. |
| **B** — a new field on the wire (e.g. on `MemoView`) | ⛔ **A fifth WIRE-1 Fold** + its own gate + a frontend change. |
| **D** — stamp carries the marker **and** `memoView` renders a badge derived from it | **No Fold** (uses `memo.model_version`, already on R4 per §4.0(i)) + one frontend unit change. |

⚑ **D is recommended**, because §4.0(i)'s correction is what makes it cheap: the stamp is *already*
on R4, so the frontend can render a visible badge from data the contract already carries. It
satisfies *"visibly"* with a rendered element rather than a string a reader must decode, and
satisfies *"not just the stamp"* because there is an actual UI affordance. ⚠️ **Stated plainly: A
alone probably does NOT satisfy Q9's wording**, and is offered only as the reduced-scope fallback.

⛔ **This is STOP-GATE G2 in the code-gen plan.** It is not resolved here because B and D differ by a
WIRE-1 amendment and a frontend stage — a scope difference the answers did not authorize either way.

### 5.5 Result

| Check | Result | Blocking? |
|---|---|---|
| §5.1 all four §4 carry-ins | **Closed** | No |
| §5.2 per-draft cap × concurrency bound | ⚠️ **New interaction — RESOLVED BY DESIGN** (thread-local, reset at `draft_memo`) | No |
| §5.3 distinguishable failures | **Confirmed, no Fold** | No |
| §5.4 Q9's visible marking | ⚠️ **Underspecified — carried to STOP-GATE G2** | No — the plan is written with D and a gate |

✅ **CLEAN ENOUGH TO PROCEED.** No contradiction remains. The one new interaction has a
well-precedented resolution; the one underspecified item is carried to a named gate inside the
code-gen plan rather than decided silently. ⚑ **Neither is hidden**: §5.2's design and §5.4's
recommendation are both vetoable at the code-gen plan's own approval gate.

➡️ **Code-generation plan: `live-llm-drafting-code-gen-plan.md`.**
