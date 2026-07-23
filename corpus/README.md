# `corpus/` — tier-B Stage 1 evidence artifact

**Generated**: 2026-07-23 · **Stage**: tier-B **Stage 1** (`guide-docs/build/plans/tier-b-stage1-code-gen-plan.md`)
**Produced by**: `python -m backend.scripts.build_corpus --out corpus` (**offline mode — the default**)
**Register item**: **#3 `tier-B corpus run`**

---

## ⚠️ WHAT THIS IS — read before citing it

| Component | Status |
|---|---|
| `profiles.json` → each record's **`profile`** | ✅ **GENUINE.** Real `ApplicantProfile` values, seeded and deterministic, labeled by the **real deterministic `RulesEngine`** (`label` is the engine's authoritative recommendation, never a generation target). |
| `profiles.json` → each record's **`documents_text`** | ⛔ **PLACEHOLDER.** Produced by a **deterministic offline double**, **NOT by a language model**. Every entry is the same fixed placeholder sentence. **It is not realistic document text and must never be read, quoted, or evaluated as model-authored content.** |
| `manifest.json` → `model_version` | Stamped **`OFFLINE-DOUBLE-NOT-A-REAL-LLM`** — deliberately unmistakable wherever it travels. |

**No LLM call was made to produce this corpus. No money was spent.**

---

## Why the prose is a placeholder — a deliberate, recorded decision

tier-B **Stage 1** authorized corpus generation. The real-prose run (Step 9 of the code-gen plan) was **deliberately
deferred**, not skipped by oversight, on evidence produced at Step 6:

* **All four blocking quality gates read only `record.profile`. None reads `documents_text`.** So the gate results
  below are **identical** to what a real-prose corpus would produce — real prose would not change them.
* The prose therefore has **no consumer** until tier-B **Stage 2/3** (memo drafting + LLM-as-judge evaluation) is
  authorized, which it currently is **not**.
* Generating it now would mean paying for an artifact that sits unused and would likely need **regenerating against
  a then-current model** anyway — register **#22**'s model-drift concern applied forward.

**Real-prose generation is deferred to whenever Stage 2/3 is actually taken up, so the spend and the consumption
happen together.**

---

## ⚑ Why committing this artifact is EVIDENTIARY, not the Q7(a) unfalsifiability argument

The authorization plan's **Q7(a)** argued for committing the corpus because *a real-prose corpus is **not**
bit-identically regenerable* (its prose comes from a live model), so an uncommitted one would effectively cease to
exist on a clean checkout and every downstream claim would become unfalsifiable.

**That argument does NOT apply to this artifact, and is not being claimed for it.** This corpus **is**
deterministically regenerable: three independent offline runs produced the **identical**
`content_hash 57821891ba502e2e213c096bf3b0f5d3ab9e60107b13b687753b437bb7290525`. Anyone can reproduce it byte-for-byte
with the command at the top of this file.

It is committed as **evidentiary record-keeping** — the specific artifact against which AC-1, AC-3 and AC-4 were
measured — **not** because it would otherwise be unrecoverable. Q7(a)'s original reasoning is preserved for the
real-prose corpus it was written about.

---

## What was verified against this corpus (`gate-reports/`)

Run by `python -m backend.scripts.run_quality_gates --corpus corpus --reports corpus/gate-reports`.
**Zero model calls.**

| Gate | Result | Criterion |
|---|---|---|
| `bias-swap.json` | **`delta_count: 0`** over 300 profiles | **AC-3** — bias-swap delta 0 |
| `reproducibility.json` | **`reproducibility_pct: 100.0`** over 300 profiles × 10 runs | **AC-1** — 100% reproducibility |
| `rule-coverage.json` | **`coverage_pct: 100.0`**, `total_rules: 11`, rulebook `1.0.0` | **AC-4** — rule coverage |
| `coverage-wiring.json` | `wiring_present: true`, `fail_under_configured: 90` | **AC-5** wiring |

### ⛔ SCOPE OF THESE RESULTS — stated plainly

**These gates verify the DECISION PATH over real applicant profiles. They say NOTHING about document prose or memo
quality.** No gate reads `documents_text`; no gate involves an LLM. In particular:

* They are **not** evidence about **AC-6** (the ≥4/5 LLM-as-judge groundedness score), which remains
  **completely unverified** — see register **#10 `JUDGE-EVAL-DEFERRED`**.
* They are **not** evidence that the document text is realistic, useful, or model-authored. It is not.

### ⚑ Note on AC-4's "100%"

`total_rules: 11` — the rulebook at version `1.0.0` contains **eleven** rules. **`PROJECT-BRIEF.md` §3 Component 2
specifies "25-40 underwriting rules."** So **AC-4's 100% means 100% of the 11 rules that exist**, not of the 25-40
originally scoped. The gate is honest about what it measures; the gap is between the rulebook (frozen unit U3) and
the brief, and **predates tier-B entirely**. Recorded here so this figure is never read as broader than it is.

---

## Regenerating

```bash
# byte-identical to the committed artifact (zero cost, no key, no network, no SDK)
python -m backend.scripts.build_corpus --out corpus

# re-verify the four gates (zero model calls)
python -m backend.scripts.run_quality_gates --corpus corpus --reports corpus/gate-reports
```

The real-prose corpus, when Stage 2/3 is authorized, is produced by the **opt-in, billable** path — which requires
**both** `--real-llm` **and** `ALLOW_REAL_LLM_CALLS=true`, plus an explicit non-floating `--model-id` and an explicit
`--max-llm-calls`. It will **not** reproduce this `content_hash`, by construction.
