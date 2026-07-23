# Register #18 — production `LLMClient` · CODE SUMMARY

**Stage**: POST-BUILD → register-item remediation · the **FIRST production LLM path in this build**
**Scoping plan**: `guide-docs/build/plans/fix-register-18-plan.md` · **Code-gen plan**:
`guide-docs/build/plans/fix-register-18-code-gen-plan.md`
**Discipline**: TDD, leaf-first, RED→GREEN, ambiguity-checked — as every prior pass.

---

## 1. What was built — the two-piece shape (Q9-A)

`backend/app/llm_client.py` — a new module in the composition root (reopens **no** frozen unit;
the location both frozen docstrings in `memo_agent_core/provider.py` name — *"wrapped to this at
composition"*):

| Piece | Owns | Flag-aware? | Holds the key? | SDK import? |
|---|---|---|---|---|
| `CappedGeminiClient` (**wrapper**) | the call cap (counts retries), temperature pass-through, per-call logging, `repr` non-disclosure | **no** — purely injected | **no** — receives an already-constructed SDK object | **none** — SDK-agnostic |
| `build_gemini_client` (**factory**) | the `ALLOW_REAL_LLM_CALLS` gate, the `get_settings()` key read, the lazy `google.genai` import | **yes** — the ONLY spend-capable path | reads it, passes it to `genai.Client`, keeps nothing | **lazy**, inside the function |

⚑ **Structural non-disclosure (stronger than Q3c asked).** The key reaches `genai.Client(...)`
**inside the factory**; the wrapper receives an already-constructed SDK object, so **the wrapper
cannot leak what it does not have.** Proven by `test_the_wrapper_structurally_holds_no_key` (its
constructor has no key parameter at all), *in addition to* the behavioural `repr`/refusal-message
tests (Q3c).

The wrapper satisfies the frozen `memo_agent_core.LLMClient` seam **structurally** — the test
imports the `runtime_checkable` Protocol; production does not. `provider.py` is **not touched**.

## 2. The cap counts retries — the tooth (test 8)

`test_the_cap_counts_retries_not_just_drafts` drives the **real** `LangGraphOrchestrator` through
the **real** `GeminiAdapter` over the wrapper over a fake SDK returning citation-invalid XML,
forcing the `MEMO_CITATION_RETRY_CAP` loop, then asserts `call_count == 2 > 1` for a single draft
— and that the cap fires **mid-retry** when set to 1. A spy on `generate()` alone would pass while
the retry path went uncounted; this cannot. Same reasoning as #19's *"commit() never invoked"*.

## 3. Spend safety — two independent gates + a hard cap

Real spend requires **both** `--real-llm` (seed CLI) **and** `ALLOW_REAL_LLM_CALLS=true` (env,
exact match, checked in the factory). Absent either → fail closed, **before any network call**.
The wrapper's cap (default 20, `--max-llm-calls` override) bounds the blast radius including the
citation-retry loop, because the cap lives **inside the wrapper** (Q5b).

## 4. Coverage — pragma, not omit (Confirm 1)

`llm_client.py` is **fully covered except the real-spend construction** (the lazy `google.genai`
import + `genai.Client(...)` + wrapper construction), which carries `# pragma: no cover` following
the `not_wired.py:127` precedent — **no new `pyproject.toml` omit entry**. The flag check, key
validation and refusal paths stay **genuinely tested** (tests 11–14).

> ⚑ **Disclosed refinement of the code-gen plan's Confirm-1 wording.** The plan said *"pragma the
> `genai.Client(...)` line only"*. With the injected-seam design (Q9-A), the lazy import, the
> `genai.Client(...)` call **and** its wrapper-construction/return all live on the same real-spend
> path that **no offline test drives** (by design — no test touches the spend flag/SDK). They are
> therefore pragma'd as one contiguous network-bound region (a delegating `return` line + a private
> `_capped_client_over_real_genai` helper), consistent with Confirm 1's own *"network-bound
> line(s)"* (plural). This is broader than *"one line"* but **narrower than an `omit` entry**, and
> the invariant the confirmation protects — flag/key/refusal genuinely covered — holds exactly.

## 5. The `os.environ` flag (Confirm 2)

`ALLOW_REAL_LLM_CALLS` is read from `os.environ` **in the factory**, never via `Settings` (frozen)
and never in `dependencies.py`. The factory docstring states why this is **not** a SEC-3 violation:
`dependencies.py`'s `os.environ` rejection is scoped to **credentials**; this is a **behavioural
on/off switch, not a credential**, and is never read alongside `GEMINI_API_KEY` (which stays
exclusively `get_settings()`). Documented as a non-secret switch in `.env.example`, separated from
the credential block.

## 6. Seed script (Q4) — offline default preserved byte-for-byte

`backend/scripts/seed_demo_cases.py`:
* Default (no `--real-llm`): `_OfflineLLMClient` **unchanged**, model + stamp `OFFLINE_MODEL_VERSION`,
  the synthetic-placeholder banner **verbatim**, the placeholder reminder footer **verbatim**. The
  `_OfflineLLMClient` class and its warning docstring are **kept byte-for-byte** (Q4 non-negotiable).
* `--real-llm`: the real `CappedGeminiClient` via the factory; an explicit **non-floating** model id
  (`gemini-2.5-flash-001`, Q6) passed to `GeminiAdapter` (frozen U4's default **not** changed); the
  `model_version` stamp split off as `<model-id>+google-genai-<sdk-version>` (Q4b); a distinct
  **"REAL LLM CALLS — THIS WILL SPEND MONEY"** banner; a real-call-count exit summary.

The module docstring's stale *"no production `LLMClient` anywhere"* claim was rewritten (register
#18 now NARROWED, real path reachable via `--real-llm`).

## 7. Manual real-API verification (Q7b-ii)

`guide-docs/build/composition-root/real-llm-verification.md` — a human-run, out-of-band procedure.
**Not a pytest test, no marker, no `pyproject.toml` edit, never collected, zero CI-spend risk.**

## 8. D1 — disclosed, tier-B NOT authorized

`requirements.txt` now declares `google-genai>=1.0.0` (legacy `google-generativeai` removed; zero
production imports of it remained). This makes `corpus_generator/build.py` importable **in
principle** — but it is **unrun, uncollected, coverage-omitted, `--model-id` default unchanged**,
and `google-genai` is not even installed in the offline environment, so `build.py` stays
non-importable here regardless. **Tier-B remains unauthorized.**

## 9. Holds upheld

`memo_agent_core/provider.py`'s `LLMClient` Protocol **IMPLEMENTED, NEVER MODIFIED** ·
`memo_extensions/` **untouched** · every other frozen-23 unit's internals **untouched** · WIRE-1's
text **not amended** · `not_wired.py` **not renamed** (#13 stays open) · U23's frozen test **not
edited** · `audit_store` Docker-guard gap **untouched (5 stays 5)** · **no new route** ·
`dependencies.py` **not wired** (Q8 — the LLM-bearing composition stays out of the request path;
Scope B's Q3-D side-effect-free-by-construction property survives) · **tier-B not authorized**.
