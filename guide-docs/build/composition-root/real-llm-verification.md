# Real-LLM Verification — MANUAL, OUT-OF-BAND procedure (register #18, Q7b-ii)

**Status**: human-run only. ⛔ **NOT a pytest test. No marker. No `pyproject.toml` edit. Never
collected by CI. Zero possibility of a CI run spending money.**

**Why manual**: this is the FIRST code path in the build that can spend real money. Every tier-U
and tier-I test runs offline by construction. The real Gemini path is reachable **only** through
this deliberate, two-gated procedure — it is verified by a human, out of band, exactly like the
tier-B `corpus_generator/build.py` entrypoint.

---

## ⚠️ This spends real money

Running this procedure issues **real Gemini API calls** against your `GEMINI_API_KEY` and **will
incur real charges**. Order of magnitude: **a few Gemini-2.5-flash calls per case** (one draft
plus up to `MEMO_CITATION_RETRY_CAP` = 2 citation retries), so `--cases 1` is typically **1–3
calls**, i.e. a **fraction of a US cent** at current flash pricing. The wrapper's hard call cap
(`--max-llm-calls`, default 20) bounds the blast radius even if something loops.

Do **not** run this in CI, in a shared job, or unattended.

---

## The two independent gates (both required)

A real call cannot happen unless **both** hold — one typo cannot enable spend:

1. **CLI opt-in**: pass `--real-llm` to the seed script.
2. **Environment switch**: `ALLOW_REAL_LLM_CALLS=true` (exact string `true`, checked inside
   `build_gemini_client`). `1`, `yes`, `TRUE`, `true ` — all still **refuse, fail-closed**.

Plus the standing key gate: `GEMINI_API_KEY` must be a non-empty secret (validated by
`secrets-config` at `Settings()` construction, and again structurally in the factory).

---

## Procedure

Run from the repo root, against a database you have already provisioned (the seed script applies
migrations itself).

```bash
# 1. Ensure the real SDK is installed (it is NOT installed for the offline suite).
pip install -r requirements.txt          # declares google-genai>=1.0.0

# 2. Provide the real key via the environment (SEC-3: never a literal, never committed).
export GEMINI_API_KEY="<your real key>"
export DATABASE_URL="postgresql://.../..."   # a real, reachable Postgres

# 3. Arm the SECOND gate — exact string "true".
export ALLOW_REAL_LLM_CALLS=true

# 4. Seed ONE case on the real path.
python -m backend.scripts.seed_demo_cases --cases 1 --real-llm
```

### Expected output

* The **red banner**: `DEMO SEED — ⚠️  REAL LLM CALLS — THIS WILL SPEND MONEY`, naming the pinned
  `model=` id, the call `cap`, and the `stamp=` (`<model-id>+google-genai-<sdk-version>`).
* One seeded case reported `submitted -> evaluated (left pending)` (with `--cases 1` the single
  case is left pending; use `--cases 2` to also exercise a `drafted` case).
* A closing line: `💸 REAL LLM calls made this run: N (cap 20).`

### What to confirm

1. **A genuine memo was produced** — inspect the drafted case's memo via `GET
   /applications/{id}/memo` (after seeding ≥2 cases so one is `drafted`). The prose must read as
   real model output, **not** the `_OfflineLLMClient` placeholder text.
2. **The stamp is real and falsifiable** — the committed/pending record's `model_version` is
   `gemini-2.5-flash-001+google-genai-<sdk-version>`, **not** `OFFLINE-DOUBLE-NOT-A-REAL-LLM`.
3. **The recommendation is unchanged by the LLM** — it still comes from the deterministic rules
   engine (CON-BR2-TYPE). The memo prose is advisory only.
4. **The model id resolves.** ⚑ `gemini-2.5-flash-001` is pinned as a **non-floating** id (Q6).
   If the live API rejects it, list available ids and adjust `REAL_MODEL_ID` in
   `seed_demo_cases.py` to the current non-floating equivalent — do **not** fall back to the
   floating `gemini-2.5-flash` alias, which would defeat the reproducibility-narrowing (Q6/#18a).

### Guardrails to observe while running

* **Cap fires on overrun**: `--cases 30` with the default cap raises `LLMCallCapExceeded` partway
  through — spend is bounded, by design (Q5b, the cap lives in the wrapper and counts retries).
* **Refusal without the env gate**: `--real-llm` with `ALLOW_REAL_LLM_CALLS` unset (or not exactly
  `true`) raises `RealLLMCallsNotEnabled` **before any network call**.
* **No key logged**: the wrapper logs `prompt_len`, never prompt text, never the key; its `repr`
  discloses no key material; it holds no key at all (the key reaches `genai.Client` only inside the
  factory). ⚑ Honest limit: this covers **our** code — the SDK's own exceptions may embed request
  context, which is not ours to promise.

---

## Reproducibility note (register #18a)

`temperature=0` makes sampling greedy but **does not** make memo prose bit-reproducible across
provider-side model changes. The **decision path** remains 100% reproducible (structurally, via
CON-BR2-TYPE — the model cannot alter the recommendation); **memo prose is not claimable
bit-exactly** under a real LLM. Pinning a non-floating model id narrows this; it does not close
it. See the register.
