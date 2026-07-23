# Tech-Stack Decisions — `corpus-generator` (U14)

**Stage**: BUILD → NFR Requirements (per-unit) · **Depth**: comprehensive (invariant-bearing build-time unit).
**Unit**: U14 `corpus-generator` · **Date**: 2026-07-07. Build-time synthetic-corpus generator (CON-BR3, DATA-1/2/3, FR-PROV-4).
**Principle**: name only what makes the `NFR-CORP-*` targets **checkable** and the generation **deterministic**; consume the five
frozen surfaces call-only; **introduce no unjustified new dependency**. **No LLM in the label path; no real PII.**

---

## Decisions

| # | Decision | Rationale / notes |
|---|---|---|
| **D1** | **Python 3.12 + pytest** (unit tier U) | The build-wide runtime + test runner (already pinned); the `NFR-CORP-*` unit targets run here, offline, in CI. |
| **D2** | **Faker (seeded) for structured fields** — **already a dependency** (`requirements.txt: faker>=30.0.0`) | Synthetic profile fields (names/cities/incomes/dates/etc.). **No new dependency.** Seeded for determinism (NFR-CORP-DET-1). |
| **D3** | **Seeded stdlib `random` for sampling** (no `numpy`) | Bounded rejection-sampling + quotas use a **seeded** `random.Random(seed)`; `numpy` is **not** pulled in (it is `outlier-model`'s P2 concern). Determinism via a single seeded generator (NFR-CORP-DET-1). |
| **D4** | **Injected Gemini seam = `memo_agent_core.provider.LLMClient`** | Build-time document **prose** via `generate(model, prompt, temperature) -> str`, `temperature=0` central (FR-PROV-4). **Injected** → a capturing double drives it offline in CI (no key/network); the real google-genai client is wired at the **tier-B** build step only. |
| **D5** | **`common.canon_ser.content_hash` for the manifest hash** | The **single** CANON-SER (BR-CORP-11 / NFR-CORP-HASH-1) — **no local hasher**. Provenance fields excluded (P4). |
| **D6** | **`rules_engine.evaluate` as the label oracle; `intake.derivations` + `intake.schema`** | Label authority (CON-BR2) + single-sourced age/BMI derivation + the profile shape — all **call-only, none edited** (NFR-CORP-LABEL-1 / PROFILE-1 / REFNOTOWN-1). |
| **D7** | **`SkewAudit` band/edge logic unit-tested on synthetic distributions** | The ±3pp band + DATA-2 checklist **logic** is verified at tier U with synthetic proportions/checklists — **no full corpus needed** in CI (NFR-CORP-SKEW-BAND-1/EDGE-1); enforcement on the real corpus is tier B. |
| **D8** | **Tier S offline end-to-end smoke — test-scoped `GenerationConfig`** | A tiny seeded run (LLM mocked) exercises the full pipeline + a valid manifest + the gate invoked (**Fold NFR-1**); uses a **test-scoped** config (small `min_profiles`, satisfiable target/edge-subset) and **never** asserts the real band or masquerades as the real corpus. |
| **D9** | **Tier B out-of-band full run** | The **real** corpus (live Gemini via `secrets-config` `GEMINI_API_KEY`, 300+, small-batch → full) is a **build invocation, not CI** (Q7). Output committed to repo-root `corpus/` + `manifest.json`. |
| **D10** | **PII light structural check** (Q4-A) | On top of the governance statement, a cheap structural check asserts the generation path reads **no external-identifier source** and makes **no network read** (NFR-CORP-PII-1). |
| **D11** | **Package `backend/corpus_generator/`; output `corpus/`** | The realized per-unit convention (confirmed) + the top-level frozen-corpus location (`unit-of-work.md`). |

---

## Deferred / referenced (not decided here)
- **Mock PDF documents** → deferred (FD Q5); consumers use structured profiles + document text.
- **Concrete Faker field distributions + prose prompt wording** → **Code-Gen** (still seeded, still deterministic).
- **`outlier-model` feature vector / `numpy` / SHAP** → `outlier-model` (U18, P2), **not** here.
- **The bias-swap suite / rule-coverage / reproducibility ×10** → `quality-gates` (U13); corpus-generator only *supports* them.

**No new dependency beyond the already-declared Faker + the shared/frozen seams (`canon_ser`, `intake`, `rules_engine`,
`memo_agent_core` `LLMClient`, `secrets_config`). No LLM in the label path; no real PII; no network in CI.**
