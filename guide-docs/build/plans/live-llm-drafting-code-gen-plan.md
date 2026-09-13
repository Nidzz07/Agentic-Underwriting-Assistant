# LIVE LLM DRAFTING — CODE GENERATION PLAN (Ollama, opt-in)

**Status**: ⛔ **PLAN ONLY — AT THE CODE-GEN GATE. NO CODE WRITTEN. NO BACKEND FILE TOUCHED.**
**Created**: 2026-08-16
**Parent**: `live-llm-drafting-plan.md` (Q1–Q10 answered; ambiguity check §4; re-check §5)
· `live-llm-drafting-clarification-questions.md` (both answered)
**Baseline**: HEAD `bd3875d` · clean · backend **1774 / 0 / 45 / 5 / 99.49%** · frontend **815 / 154**
**Target**: register **#18** gap (iii) — for the **showcase** provider only (Q6)

> ⛔ **NOTHING IN THIS FILE HAS BEEN EXECUTED.** Every count below is a **prediction**, and this
> project's record on predictions is mixed and documented as such — Fold-7 predicted +48 and
> measured **+84**. Stop-gate 8 therefore requires every variance to be reconciled **with a stated
> cause**, and ⛔ **no test may be trimmed to hit a number.**

---

## 1. What is decided, and what is still open

**Decided** (Q1–Q10 + both clarifications): `OllamaAdapter` via `ThinkingLLMClient` · a
`CappedOllamaClient` mirroring `CappedGeminiClient` with a **per-draft** cap · `os.environ` selector
failing safe to the offline double · fail-loud per draft inside the WIRE-1 envelope at **500** ·
model-ID/stamp split with a three-part stamp · Gemini deferred · timeout + `CapacityLimiter` +
`async def` R11 · the `memo_extensions` import gated and guarded · **Ollama opt-in, not default** ·
full-chain manual verification plus a reproducibility probe.

**Open — and each is a named gate below, not an assumption**: **G1** the `memo_extensions` import
authorization · **G2** where Q9's *"visible"* non-quality-gated marking goes.

### 1.1 ⚑ One honest reframing of the cap, discovered while writing this plan

`MEMO_CITATION_RETRY_CAP = 2` (`memo_agent_core/constants.py:18`), and `orchestrator.py:118`
re-drafts only while `attempts < cap` — so **the citation-retry loop is already structurally bounded
at 2 model calls per draft.** ⛔ **The per-draft cap therefore does not prevent a runaway that is
currently possible; it is defence-in-depth against a future re-entry path that is not bounded.**
That is a weaker and more accurate claim than *"runaway-loop containment"* as a primary control, and
it is recorded here rather than left implied, because a reader who assumes the cap is load-bearing
would mis-tune it. ⚑ It also sets the number: **`MAX_CALLS_PER_DRAFT = 4`** is comfortable headroom
over a structural maximum of 2, and any breach means something re-entered that should not have.

---

## 2. The two gates

### ⛔ G1 — the `memo_extensions` import (Q8)
**Subject**: `backend/app/dependencies.py` importing `backend.memo_extensions.provider_showcase`.
**Required before**: Stage 3.
**Text the authorization must use** (Q8's own instruction — the gate must not overclaim):

> This is the **first import of `memo_extensions` from `backend/app/`**. It is **not** the first
> production import of `memo_extensions` — `case_lifecycle/pipeline.py:38` already imports
> `borderline_router` and calls it on every draft (`:184`). `memo_extensions` is **not** in
> `FROZEN_UNITS` and **no existing guard forbids this import**; the gate exists as discipline, and
> the guard created in Stage 1 exists so the *next* such import meets an assertion rather than
> nothing.

### ⛔ G2 — where Q9's visible marking goes (§5.4)
**Required before**: Stage 6. **Options**: **A** stamp-only (cheapest; ⚠️ probably does *not*
satisfy Q9's *"not just via the stamp"*) · **B** a new wire field (⛔ a fifth WIRE-1 Fold + its own
gate) · **D** stamp marker **+** a `memoView` badge derived from it (**recommended** — no Fold,
because §4.0(i) established `memo.model_version` is already on R4).
**Stage 6 below is written for D.** If G2 selects A, Stage 6 loses its frontend half; if B, this
pass gains a Fold gate and should be re-planned.

---

## 3. Stages

Six stages. ⚑ **Stages 1–4 are the pass; Stage 5 is documentation; Stage 6 is gated.** Order is
chosen so that each guard exists **before** the code it constrains, per Fold-7's G2 discipline.

### Stage 1 — the guard, created empty and RED-first

**Files**: `backend/app/tests/test_no_write_route.py` (changed).

1. Add `_MEMO_EXTENSIONS_IMPORT_MODULES_FROM_APP: frozenset[str] = frozenset()` beside the file's
   two existing allowlists, with a comment stating the `APP_ROOT`-only scope explicitly and naming
   `case_lifecycle/pipeline.py:38` as **outside** it.
2. Add the assertion: within `PRODUCTION_FILES`, the set of modules importing `backend.memo_extensions`
   **equals** the allowlist. ⚑ **Exact-set equality, not a skip-list** — the `_PIPELINE_MODULES`
   shape, so both a new importer *and* a named module quietly dropping the import fail.
3. Add the non-vacuity detector: a synthetic source string containing the import is shown to fail
   the same predicate. ⛔ Without it, an empty allowlist over zero importers asserts nothing.

**RED/GREEN**: ✅ **GREEN on arrival** — and deliberately so. The RED arrives in **Stage 3**, when
`dependencies.py` first imports and the guard refuses it. That is the *"first encounter is a
failure"* discipline, applied across a stage boundary.

**Predicted: +2 backend tests.**

---

### Stage 2 — `backend/app/ollama_client.py`

**Files**: `backend/app/ollama_client.py` (**new**), `backend/app/tests/test_ollama_client.py` (**new**).

1. `class OllamaUnreachable(RuntimeError)` — message names the **resolved host**; never a key.
2. `class OllamaCallCapExceeded(RuntimeError)` — message names the cap **and that it is per-draft**,
   so it can never be read as an availability problem (§5.3).
3. `MAX_CALLS_PER_DRAFT: int = 4`, with §1.1's reasoning at the constant.
4. `DRAFT_TIMEOUT_SECONDS: float = 120.0`, with the cold-load reasoning at the constant.
5. `class CappedOllamaClient` — satisfies `ThinkingLLMClient` **structurally** (no import, no
   inheritance), i.e. `generate(*, model, prompt, temperature, thinking) -> str`:
   * counter in a **`threading.local()`** (§5.2), **reset by an explicit `begin_draft()`** — never
     lazily initialized, because threadpool threads are reused;
   * `temperature` passed through **untouched** (TEMP0-1 lives in the adapter, not here);
   * `thinking` accepted and mapped to the SDK's options; ⚑ if the model ignores it the adapter
     still **completes** — `provider_showcase.py:11-13`'s stated degrade-at-the-adapter behaviour;
   * logs **prompt length only**, never prompt text;
   * wraps the SDK's `RequestError`/`ResponseError`/connection failures into `OllamaUnreachable`,
     carrying the resolved host (Q3's hybrid);
   * `call_count` property + a non-delegating `__repr__`.
6. `build_ollama_client(*, model_id, max_calls, timeout)` — the guarded factory, sole holder of the
   lazy `import ollama`. ⛔ **No `ALLOW_REAL_LLM_CALLS` equivalent** (Q1 B's reasoning): a local
   daemon is not spend, and copying that flag's *"permit real spend"* wording would be false.

**RED-before-GREEN** — every test written and observed failing first:
`generate` returns parsed text · temperature passthrough · thinking passthrough both ways · cap
refuses at 5th call **within one draft** · ⛔ **cap RESETS after `begin_draft()`** (the whole point
of the clarification) · ⛔ **two threads keep INDEPENDENT counters** (§5.2's race, pinned) · ⛔ **a
reused thread starts at zero** (the reset-vs-lazy-init invariant) · unreachable host →
`OllamaUnreachable` naming the host · log line carries length not text · `__repr__` leaks nothing ·
factory passes `timeout` · factory imports lazily (module import needs no daemon).

**Predicted: +16 backend tests.**

---

### Stage 3 — the selector, the model/stamp split, and the import that trips G1's guard

**Files**: `backend/app/dependencies.py` (changed), `backend/app/tests/test_no_write_route.py`
(changed — allowlist), `backend/app/tests/test_dependencies_provider.py` (**new**).

1. `MEMO_PROVIDER_ENV = "MEMO_PROVIDER"` beside `SESSION_COOKIE_SECURE_ENV`, same
   behavioural-switch-not-a-credential comment, ⛔ **fail-safe: only the exact literal `"ollama"`
   selects live; absent, misspelt or anything else → the offline double.**
2. `OLLAMA_MODEL_ID = "llama3.1:8b-instruct-q4_K_M"` as a named constant.
3. `_CompositionSeams.__init__` parameterized `(*, provider=None, model=None, model_version=None)`,
   mirroring `_SeedSeams` (`seed_demo_cases.py:198-205`) — ⛔ **defaults reproduce today's behaviour
   byte-for-byte**, so every existing construction is unaffected.
4. `build_ollama_stamp(model_id, digest, sdk_version) -> str` — the three-part stamp (Q5 C), digest
   truncated to **12 chars**, with the *"pins the weights, not the sampling stack; narrows #22, does
   not close it"* note **at the function**, not only in this plan.
5. The Ollama branch: `OllamaAdapter(CappedOllamaClient(...), model=OLLAMA_MODEL_ID, thinking_mode=...)`.
   ⛔ **THIS IS THE LINE THAT TRIPS STAGE 1'S GUARD.** Observe it RED, then add `"dependencies.py"`
   to `_MEMO_EXTENSIONS_IMPORT_MODULES_FROM_APP` and observe GREEN.
6. `draft_memo` calls `client.begin_draft()` **before** `self._orchestrator.run(...)` — the
   per-draft boundary (§5.2). ⚑ Guarded so the offline double, which has no such method, is
   unaffected.
7. `ollama.show()` for the digest, called **once at construction** (not per draft) and **failing
   soft** — a digest lookup failure must degrade the stamp, never break drafting.

**RED-before-GREEN**: unset env → offline double (fail-safe) · `"Ollama"`/`"OLLAMA"`/`"true"`/junk →
offline double (exact-literal) · `"ollama"` → `OllamaAdapter` · ⛔ **model ID and stamp are
DIFFERENT strings** (the §1.2 conflation, pinned so it cannot return) · stamp contains all three
parts · digest truncated to 12 · digest-lookup failure still yields a usable stamp · `begin_draft`
called exactly once per `draft_memo` · offline path untouched · **G1 guard RED then GREEN**.

**Predicted: +14 backend tests.**

---

### Stage 4 — R11: `async def`, the bound, the timeout, the catch

**Files**: `backend/app/draft_concurrency.py` (**new**), `backend/app/routes/submission.py` (changed),
`backend/app/tests/test_draft_concurrency.py` (**new**), `backend/app/tests/test_submission_routes.py`
(changed).

1. `draft_concurrency.py` mirroring `parse_concurrency.py` **including its recorded reasoning**:
   `MAX_CONCURRENT_DRAFTS: int = 1` (⚑ **one**, because a single local daemon serializes anyway —
   and the constant's comment must state that ⛔ **correctness does NOT depend on this value**,
   §5.2), `@lru_cache` `draft_limiter()`, `async def run_bounded_draft(...)`.
2. ⛔ **STOP-GATE 4A — convert R11 to `async def` and offload ALL THREE blocking calls**:
   `pipeline.read` at `:209`, `pipeline.draft` at `:212`, `pipeline.read` at `:216`. §4.2 found
   that offloading only the draft leaves two blocking DB round-trips on the event loop **and no
   existing test would catch it**. Mirror R10's discipline, not merely its `async` keyword.
3. The optional liveness pre-check (Q4 D) — ⚑ **also offloaded**, or it reintroduces on the loop
   exactly what 4A removes. Failure → `OllamaUnreachable`, same path as any other.
4. `try/except (OllamaUnreachable, OllamaCallCapExceeded)` → `WireError(INTERNAL_ERROR, <distinct
   message>, detail={...})`. ⛔ **Named types only — never a bare `except Exception`** (§5.3).

**RED-before-GREEN**: unreachable Ollama → **500 in the WIRE-1 envelope**, not a plain-text 500 (the
§1.3 gap, closed) · cap-exceeded → **500 with a MATERIALLY DIFFERENT message** · ⛔ **the two
messages are asserted DIFFERENT from each other** (without this, §5.3 is decorative) · the offline
path is byte-unchanged · ⛔ **the event loop stays responsive during a slow draft** (4A's
non-vacuity — a `GET /session` 401 mid-draft, the stronger probe document-upload §9 discovered) ·
limiter serializes · limiter survives two event loops (the Fold-7 lesson) · timeout passed through ·
a permit is released on the exception path.

**Predicted: +14 backend tests.**

---

### Stage 5 — the register item (Q4), documentation only

**Files**: `guide-docs/` only.

Open **#32 `UNCAUGHT-EXCEPTION-ESCAPES-ENVELOPE`**: `main.py:97` asserts *"Every non-2xx leaves as
the WIRE-1 §4 envelope — no route can emit a non-contract body"*, but only three handlers are
registered (`:98-100`) and **nothing mechanically enforces it against an uncaught exception on any
route.** Stage 4 closes the **one reachable path** (R11); the **general capability** remains.
⚑ Exactly the **#28 → #29** split shape, cited as precedent in the item itself.

**Predicted: 0 tests.** ⚠️ Register **31 → 32 tracked**.

---

### Stage 6 — Q9's visible marking ⛔ **GATED ON G2; written for option D**

**Files**: `backend/app/dependencies.py` (stamp prefix), `frontend/src/memoView/` (badge + copy + tests).

1. The stamp gains a leading `NOT-QUALITY-GATED` component.
2. `memoView` renders a visible badge when `memo.model_version` carries it, with copy stating the
   memo came from a provider **exempt from the memo-quality gates** (groundedness/promptfoo) while
   **holding every decision-level gate** — the `provider_showcase.py:6-9` distinction, in the UI.
3. ⛔ **No WIRE-1 change** — it reads `memo.model_version`, already on R4 (§4.0(i)).

**RED-before-GREEN**: badge absent for the offline double · present for Ollama · copy does **not**
say the memo is untested or wrong (the exemption is scoped to memo-quality, and the UI must not
overclaim it) · stamp round-trips through `psql` and R4 with the prefix intact.

**Predicted: +2 backend, +4 frontend.**

---

## 4. Predicted deltas

| Stage | Backend | Frontend | Notes |
|---|--:|--:|---|
| 1 guard | **+2** | — | green on arrival; RED lands in stage 3 |
| 2 client | **+16** | — | largest; 3 of them pin §5.2's race |
| 3 seams | **+14** | — | trips and then satisfies G1's guard |
| 4 R11 | **+14** | — | includes 4A's loop-responsiveness non-vacuity |
| 5 register | **0** | — | documentation |
| 6 marking (G2) | **+2** | **+4** | drops to 0/0 if G2 selects A |
| **Total** | **+48** | **+4** | |

**Predicted end state**: backend **1822 / 0 / 45 / 5**, frontend **819 / 154**.

⚠️ **Coverage**: `ollama_client.py`'s real-SDK construction path takes `# pragma: no cover` on the
`llm_client.py:132` precedent (**not** a `pyproject.toml` omit); every refusal, cap and wrapping
path stays covered. The 90% gate must pass **unedited** — ⛔ **editing a coverage threshold is a
stop-gate breach.**

---

## 5. Stop-gates

| # | Condition | Action |
|---|---|---|
| **1** | Any new test passes on arrival without having been observed RED | ⛔ **STOP** — vacuity |
| **2** | Stage 3's import does **not** turn G1's guard RED | ⛔ **STOP** — the guard is vacuous |
| **3** | A bare `except Exception` appears on the drafting path | ⛔ **STOP** — §5.3 |
| **4A** | R11 converted to `async def` with **any** blocking call left un-offloaded | ⛔ **STOP** — §4.2 |
| **5** | The cap is found to be shared across concurrent drafts | ⛔ **STOP** — §5.2's race is live |
| **6** | Correctness is found to depend on `MAX_CONCURRENT_DRAFTS`'s value | ⛔ **STOP** — §5.2 |
| **7** | Any frozen unit is touched, or `case_lifecycle` is edited | ⛔ **STOP** — no reopening is authorized |
| **8** | A coverage threshold is edited, or WIRE-1 is amended | ⛔ **STOP** |
| **9** | Measured deltas differ from §4 | ⚠️ **Reconcile with a stated cause; never trim a test** |

---

## 6. Manual verification (Q10 C) — **§6 runs only after all six stages are green**

⚑ **Incorporating §4.0(i)'s correction**: `curl` confirms the stamp **one step earlier than
originally assumed** — on **R4, pre-commit**, at `memo.model_version` — not only via `psql`.

1. ⛔ **Submit fresh through the browser and draft from the accepted panel.** A reloaded or seeded
   case has **no UI draft affordance** (register #2's standing residual); forgetting this reads a
   working design as broken.
2. ⚠️ **Expect the first draft to be slow, and do not investigate it**: the ~2.6 s lazy corpus fit
   (`dependencies.py:306-309`) **and** the cold model load stack.
3. `psql` — `pending_recommendation.model_version` carries all three stamp parts.
4. ⚑ **`curl` R4** — `memo.model_version` matches `psql` exactly, **before any commit**.
5. ⛔ **Read the prose.** It must be genuinely model-written — **not** the `PLACEHOLDER MEMO` text.
6. ⛔ **Verify the cited rule ID is REAL**, present in the rulebook — not merely non-empty. A
   hallucinated-but-plausible ID fails `CitationValidator` and surfaces as *"drafting produced no
   memo"* → 500, which is the `DTI-001` failure (`offline_memo_double.py:52-56`) with a new cause.
7. Commit; `psql` `audit_record.model_version`; `curl` R7; confirm the UI history forensic tuple at
   `history-detail-model-version`; confirm Stage 6's badge if G2 selected D.
8. **The reproducibility probe** — draft the same profile twice, compare prose. ⛔ **Recorded as an
   OBSERVATION against register #22, never as a determinism claim**: one repetition is not
   `PROJECT-BRIEF` §5.1's *"same input × 10 runs"*, and **differing prose is a FINDING about #22,
   not a failure of this pass.**
9. **Failure modes**: stop Ollama → 500 **in the envelope** naming the host; then confirm the
   cap message is **different** from it.
10. ⛔ **Confirm the fail-safe**: unset `MEMO_PROVIDER`, restart, draft → the **offline double**,
    stamped `OFFLINE-DOUBLE-NOT-A-REAL-LLM`. Ollama is **opt-in** (Q9 C), and this is the check
    that proves it.

---

## 7. Holds this pass asserts

⛔ **No frozen unit touched** — nothing under `intake/`, `rules_engine/`, `memo_agent_core/`,
`audit_store/`, `auth_rbac/`, `secrets_config/`, `database/`, `common/` · ⛔ **`case_lifecycle/` NOT
edited** — no fifth U24 reopening · ⛔ **WIRE-1 UNAMENDED** — no Fold (unless G2 selects B, which
re-plans the pass) · no migration · no `.sql` · no `checksums.json` · no `render.yaml` ·
**coverage thresholds unedited on both sides** · `PROJECT-BRIEF.md` unchanged.

## 8. ⚠️ What this pass explicitly does NOT do

* ⛔ **Does not close register #18.** It moves the **showcase** half only. Gemini's production client
  stays **unproven through the request path** (Q6 A) — and the close-out must say which half moved.
* ⛔ **Does not make Ollama the default** (Q9 C). An unconfigured deployment still serves the
  offline double.
* ⛔ **Does not bring Ollama into `IN_GATE_PROVIDERS`.** The memo-quality exemption stands.
* ⛔ **Does not close register #22.** The digest narrows it; the sampling stack is unpinned.
* ⚠️ **Does not fix the two documentation states** at the parent plan's §0.2.
