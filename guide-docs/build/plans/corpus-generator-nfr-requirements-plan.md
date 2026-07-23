# NFR Requirements Plan (Part 1) — `corpus-generator` (U14)

**Phase / Stage**: BUILD → NFR Requirements, **Part 1 (Planning)** (plan-then-generate; numbered `[Answer]` tags to fill)
**Loop position**: `corpus-generator` (U14) — FD ✅ **APPROVED (corrected)** → **NFR Requirements Part 1 ← here.**
**Unit**: U14 `corpus-generator` · **Date**: 2026-07-07 · **Depth**: **COMPREHENSIVE** (confirmed) · owns **CON-BR3**, DATA-1/2/3, FR-PROV-4 · Story **US-PLAT-7**.
**Status**: **Four `[Answer]` tags FILLED (all A); ambiguity-check CLEAN (2 named risks resolved as folds NFR-1/NFR-2, §5A); Part 2 GENERATED** (`nfr-requirements.md` + `tech-stack-decisions.md`). This plan re-saved with the filled answers + resolved folds embedded (standing convention).

Built **ON** the frozen FD — the **eleven BR-CORP rules**, the **four folds**, the **five call-only dependencies** (intake,
rules-engine, memo-agent-core, secrets-config, `common.canon_ser`), and the `CorpusManifest` / `CorpusRecord` / `GenerationConfig`
shapes (`guide-docs/build/corpus-generator/functional-design/`) — **re-opening none**. Each BR-CORP-1..11 maps to a **pass/fail
testable `NFR-CORP-*` target** at an explicit **test tier**.

---

## 1. What NFR Requirements produces (Part 2 preview)
- `nfr-requirements.md` — the finalized `NFR-CORP-*` targets (pass/fail assertions + acceptance criteria + tier + traceability to BR-CORP-* + Security-Guardrails table).
- `tech-stack-decisions.md` — the test/generation substrate decisions (Faker seeded, pytest unit tier, injected-LLM capturing double, `canon_ser`/intake/rules-engine seams) with no unjustified new dependency.

## 2. Test tiers (explicit — per Q7 offline vs out-of-band)
| Tier | Meaning | Runs in CI? |
|---|---|---|
| **U — unit / seeded-deterministic** | pure, offline: seeded `ProfileFactory`, the real (deterministic) engine oracle, `SkewAudit` logic driven by **synthetic** distributions, the injected LLM **mocked** (capturing double) | **Yes** |
| **S — offline end-to-end smoke** *(pending Q3)* | a tiny seeded end-to-end run (factory→derive→label→sample→gate→freeze) with the LLM **mocked** — asserts a valid manifest + gate behavior without a live key | **Yes (if adopted)** |
| **B — out-of-band build invocation** | the **real** full-corpus generation (live Gemini prose, 300+), small-batch-validate → full | **No (manual/build step)** |

> The ±3pp band and edge-case **audit logic** is exercised at **tier U** on **synthetic proportions/checklists** (no full corpus
> needed); the **enforcement on the real 300+ corpus** happens at **tier B** when the gate runs during generation. This resolves the
> small-CI-batch tension without weakening either assertion.

---

## 3. BR-CORP → draft `NFR-CORP-*` target map (every rule mapped; no orphan)

| Target | BR | Draft pass/fail assertion | Tier | Rigor |
|---|---|---|---|---|
| **NFR-CORP-DET-1** | BR-CORP-1 | **repeat-run byte-identity**: same seed → byte-identical structured profiles + labels across **N** runs (**Q1**); **structural**: no wall-clock (`datetime.now`/`date.today`) and no unseeded randomness in the generation path | U | full |
| **NFR-CORP-LABEL-1** | BR-CORP-2 | for **every** record, `record.label == evaluate(record.profile, manifest.rulebook_version).recommendation`; no independent label path exists | U | full |
| **NFR-CORP-BOUND-1** | BR-CORP-3 | **(a) happy path** — quotas filled within budget → corpus produced; **(b) loud-failure path** — an impossible target under a **deliberately tight budget** (**Q2**) exhausts the budget and the gate **raises** (asserted, **not a hang**) | U | full |
| **NFR-CORP-SKEW-BAND-1** | BR-CORP-4 (i) | `SkewAudit` **passes iff** each class proportion is within **±3pp** of 40/35/25; **build-blocking** on failure. **Independent** of the edge checklist (**not averaged**). Unit-tested on synthetic proportions (U) + enforced on the full corpus (B) | U (+B) | full |
| **NFR-CORP-SKEW-EDGE-1** | BR-CORP-4 (ii) | `SkewAudit` **passes iff** **every** DATA-2 edge case is present (thin-file; self-employed/irregular; age 18/65; BMI 25.00/30.00; DTI 40%; single-missing-document) — a **checklist, not averaged** into the band; **build-blocking** on any absence | U (+B) | full |
| **NFR-CORP-FREEZE-1** | BR-CORP-5/6 | `manifest.rulebook_version` **equals the version passed to every `evaluate()`** in the run; the frozen corpus is **self-contained data** (consumers need neither the generator nor an LLM); the freeze is pinned by `content_hash` | U | full |
| **NFR-CORP-SEGREGATION-1** | BR-CORP-7 | swapping the `Demographics` sub-object on an **otherwise-identical** profile leaves the **engine label unchanged**. **Ownership note (do not conflate)**: this is corpus-generator's **own layered-respect** check — **NOT** a substitute for, or re-implementation of, `quality-gates`' bias-swap suite (CON-BR1 verification owner) | U | full |
| **NFR-CORP-REFNOTOWN-1** | BR-CORP-8 | **structural**: the five surfaces (intake, rules-engine, memo-agent-core, secrets-config, `common.canon_ser`) are imported **call-only** and **none edited**; **no local** hasher, derivation, rule-eval, or second temperature setting | U (structural) | full |
| **NFR-CORP-PROFILE-1** | BR-CORP-9 | every emitted profile round-trips through Pydantic (valid, `frozen`, `extra="forbid"`); `age_years_derived`/`bmi_derived` **equal** `intake.derivations` output; `application_id` is the deterministic synthetic id | U | full |
| **NFR-CORP-PII-1** | BR-CORP-10 | **governance/review**: synthetic-only (Faker + prose); no real PII. *(Optional light structural: no external-identifier/network read in the generation path — see Q4.)* | governance (+opt structural) | soft |
| **NFR-CORP-HASH-1** | BR-CORP-11 | `manifest.content_hash == common.canon_ser.content_hash(<canonicalized CorpusRecord list>)`; changing a **provenance** field (`generation_timestamp`, …) does **NOT** change the hash; changing a **profile/label/tag** field **DOES**; **no local SHA/serialization helper** exists | U (+structural) | full |

**No orphan** — BR-CORP-1..11 each map to a target.

---

## 4. Clarifying questions (fill each `[Answer]` tag; last option = Other)

These decide **NFR-tier realization** — they do **not** re-open the FD, the BR-CORP rules, or the folds.

### Question 1 — Determinism repeat-count (NFR-CORP-DET-1)
How many repeat runs prove byte-identity?
A) **2 runs** — byte-identity is binary; a second identical run proves determinism. The ×10 *corpus-reproducibility* acceptance
   criterion (AC-1) is **`quality-gates`' scope**, not duplicated here. **Recommended.**
B) **×10** — align the generator's own determinism test with the project calibration convention (heavier; overlaps quality-gates).
C) Other.

[Answer]: A

### Question 2 — Loud-failure test: tight-budget value + impossible-target construction (NFR-CORP-BOUND-1)
How is the budget-exhaustion (loud-failure) path forced deterministically?
A) **Fixed tiny `attempt_budget` (e.g. 1) + an unsatisfiable per-class quota** — a test constructs a target the seeded factory
   cannot meet within the budget and asserts the `SkewAudit` gate **raises** (deterministic, no hang). Exact constant `budget=1`
   (or a small stated constant). **Recommended.**
B) A different construction (please specify).
C) Other.

[Answer]: A

### Question 3 — Automated smoke-check for the out-of-band full run (tier S)
Does the pipeline get an offline end-to-end smoke, or is the full run purely manual?
A) **Adopt tier S** — a tiny seeded end-to-end run with the **LLM mocked** (no key/network) exercises factory→derive→label→sample→
   gate→freeze and asserts a valid manifest + gate pass, **run in CI**; the **real** full-corpus (live Gemini, 300+) stays **tier B /
   out-of-band**. Catches integration breaks without a live LLM. **Recommended.**
B) **No tier S** — CI runs only per-module unit tests; the full end-to-end is purely manual/out-of-band.
C) Other.

[Answer]: A

### Question 4 — Test/generation substrate + PII structural check (tech-stack)
Confirm the substrate and whether PII gets a structural check.
A) **Faker (seeded)** for structured fields + the **injected Gemini seam** (capturing double in CI) for prose + **pytest** unit tier;
   `SkewAudit` band/edge logic unit-tested on **synthetic** distributions; **no new heavy dependency** beyond Faker. **NFR-CORP-PII-1
   adds a light structural check** (no external-identifier source / no network read in the generation path) on top of the governance
   statement. **Recommended.**
B) Same substrate but **PII stays governance-only** (no structural check).
C) Other.

[Answer]: A

---

## 5. Carried FD folds (referenced, not re-derived — the substrate NFR builds on)
1. **Fold 1** — Q1 bounded rejection-sampling (fixed seeded budget; keep-if-needed else discard; gate-fail-loud; never loops) → drives **NFR-CORP-BOUND-1**.
2. **Fold 2** — ±3pp band **AND** edge-checklist are **independent, conjunctive** → **two separate** targets **NFR-CORP-SKEW-BAND-1** + **NFR-CORP-SKEW-EDGE-1**.
3. **Fold 3** — termination bound (engine is label authority; intended class is only a target) → **NFR-CORP-BOUND-1 / LABEL-1**.
4. **Fold 4** — single `rulebook_version` semver; future version = tracked regeneration → **NFR-CORP-FREEZE-1**.

### 5A. Newly-resolved NFR-tier folds (ambiguity-check — both named risks CLEAN)
5. **Fold NFR-1 — tier S is a wiring smoke, not a corpus validator** *(risk i)*: tier S uses a **test-scoped `GenerationConfig`**
   (small `min_profiles`, a satisfiable target/tolerance and edge-subset) to exercise pipeline wiring (factory→derive→label→sample→
   gate→freeze) + a **valid manifest** + the gate being **invoked** (happy path). It does **NOT** assert the real 40/35/25 ±3pp band
   or the full DATA-2 checklist — those are **NFR-CORP-SKEW-BAND-1 / SKEW-EDGE-1** at tier U (synthetic distributions) + tier B
   (enforcement on the real corpus). `GenerationConfig.min_profiles = 300` governs the **real tier-B** corpus only; tier S never
   masquerades as a real corpus (its manifest is test-scoped, not committed as the real `corpus/`).
6. **Fold NFR-2 — BOUND-1 loud-failure is seed-independent (pigeonhole)** *(risk ii)*: the impossible target is a per-class
   **required count strictly greater than `attempt_budget`** (e.g. `budget = 1`, require ≥ 2 of a class). Because you can keep at
   most `budget` profiles, quota > budget is **unreachable for every seed** — so budget exhaustion and the loud raise are
   **seed-independent** and can never coincidentally pass. This refines Q2-A's "unsatisfiable quota" to a **pigeonhole** guarantee.

## 6. Settled items held (not re-opened)
The frozen FD (BR-CORP-1..11, the five call-only deps incl. `common.canon_ser`, the manifest/record/config shapes) is the substrate —
NFR builds testable targets **on** it. **CON-BR1 verification stays `quality-gates`'** (NFR-CORP-SEGREGATION-1 is corpus-generator's
own layered-respect check, not that suite). **CON-BR2** label authority = `rules-engine`. **No LLM in the label path; no real PII;
WIRE-1 untouched** (backend build-time unit). Out-of-band full-corpus run per Q7. No other unit started.

## 7. Next step (STOP here)
Fill the four `[Answer]` tags. On your signal I will run the mandatory ambiguity-check (surface-and-stop on any genuine gap), then —
if clean — generate **Part 2** (`nfr-requirements.md` + `tech-stack-decisions.md`) and, per the standing convention, **re-save THIS
plan file with the filled answers + any resolved folds embedded**. Then the standardized NFR-Requirements 2-option gate. **No NFR
artifact is generated until the answers are in and checked.**
