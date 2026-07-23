# NFR Requirements — `corpus-generator` (U14)

**Stage**: BUILD → NFR Requirements (per-unit) · build-time synthetic-corpus unit · **Depth**: **COMPREHENSIVE**
**Unit**: U14 `corpus-generator` · **Date**: 2026-07-07 · owns **CON-BR3**, DATA-1/2/3, FR-PROV-4 · Story **US-PLAT-7**.
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md` — the **eleven BR-CORP rules**,
the **four folds**, the **five call-only dependencies** incl. `common.canon_ser`, the `CorpusManifest`/`CorpusRecord`/
`GenerationConfig` shapes) — **re-opening none**. Each `NFR-CORP-*` target is a **pass/fail testable assertion** traced to its
BR-CORP rule. Four NFR-tier answers (all **A**) + two resolved folds (NFR-1/NFR-2) locked in the plan.

---

## 0. Central testability principle (tiers + folds)

`corpus-generator` is verified across three tiers (plan §2):
- **U — unit / seeded-deterministic** (CI): seeded `ProfileFactory`, the real deterministic engine oracle, `SkewAudit` logic driven
  by **synthetic** distributions/checklists, the injected LLM **mocked** (capturing double). This is where every invariant target
  actually proves out.
- **S — offline end-to-end smoke** (CI): a tiny **test-scoped-config** run (LLM mocked) exercising factory→derive→label→sample→gate→
  freeze — asserts wiring + a valid manifest + the gate is invoked. **Fold NFR-1**: it does **NOT** assert the real 40/35/25 band or
  the full DATA-2 checklist, and **never masquerades as a real corpus** (`min_profiles = 300` governs the real **tier-B** corpus only).
- **B — out-of-band build invocation** (not CI): the **real** full corpus (live Gemini prose, 300+, small-batch → full).

**Folds preserved:** Fold 1 (bounded rejection-sampling), Fold 2 (±3pp band **AND** edge checklist are **independent, conjunctive**),
Fold 3 (engine is label authority; termination bound), Fold 4 (single `rulebook_version`), **Fold NFR-1** (tier S = wiring smoke),
**Fold NFR-2** (BOUND-1 loud-failure is seed-independent via pigeonhole `quota > budget`).

---

## 1. Finalized `NFR-CORP-*` targets (pass/fail; tier stated)

### FULL RIGOR — invariant / acceptance-criteria-bearing

#### NFR-CORP-DET-1 — seeded determinism, byte-identical (BR-CORP-1)
- **Assertion**: same `seed` + same deps → **byte-identical** structured corpus content (profile + label + `edge_case_tags`); no
  wall-clock and no unseeded randomness in the generation path.
- **Acceptance criteria**: (a) **2 runs** (Q1) with the same seed produce byte-identical canonicalized content (compared via
  `canon_ser` bytes); (b) **structural** — no `datetime.now`/`date.today`/`time.*` and no `random` without a seeded generator in the
  generation modules; (c) `generation_timestamp` is recorded in the manifest but **excluded** from the compared content (P4).
- **Tier**: **U**.

#### NFR-CORP-LABEL-1 — engine is the label authority (BR-CORP-2)
- **Assertion**: for **every** record, `record.label == evaluate(record.profile, manifest.rulebook_version).recommendation`.
- **Acceptance criteria**: (a) recomputing the engine label for every record equals the stored `label`; (b) **structural** — the
  `label` is set **only** from the oracle (no independent label path); (c) `intended_class` never overrides `label`.
- **Tier**: **U**.

#### NFR-CORP-BOUND-1 — bounded termination; loud failure, never a hang (BR-CORP-3, Fold 1 + Fold NFR-2)
- **Assertion**: generation is bounded; the happy path completes within budget; an impossible target **raises loudly**.
- **Acceptance criteria**: (a) **happy path** — a satisfiable target within `attempt_budget` → a corpus is produced, no raise;
  (b) **loud-failure path** — a per-class **required count strictly greater than `attempt_budget`** (**pigeonhole**; e.g.
  `attempt_budget = 1`, require ≥ 2 of a class) causes the run to **raise a typed error** (`SkewAudit`/budget-exhaustion), asserted
  **seed-independently** (quota > budget is unreachable for any seed — **Fold NFR-2**), and provably **not a hang** (the attempt loop
  is bounded by `attempt_budget`).
- **Tier**: **U**.

#### NFR-CORP-SKEW-BAND-1 — ±3pp distribution band, build-blocking (BR-CORP-4 i, Fold 2)
- **Assertion**: `SkewAudit` **passes iff** each class proportion is within **±3 percentage-points** of `{APPROVE 40, REFER 35,
  DECLINE-RECOMMEND 25}`; build-blocking on failure; **independent** of the edge checklist.
- **Acceptance criteria**: (a) **tier U** — feeding `SkewAudit` **synthetic** proportions: within band → pass; any class off by
  > 3pp → **fail** (raises/returns fail), **regardless** of the edge checklist state (independence); (b) the band computation does
  **not** consult the edge checklist (not averaged); (c) **tier B** — the gate runs on the real 300+ corpus during generation.
- **Tier**: **U (+B)**.

#### NFR-CORP-SKEW-EDGE-1 — DATA-2 edge-case checklist, build-blocking (BR-CORP-4 ii, Fold 2)
- **Assertion**: `SkewAudit` **passes iff** **every** DATA-2 mandatory edge case is present — a **checklist, not averaged** into the
  band; build-blocking on any absence.
- **Acceptance criteria**: (a) **tier U** — a synthetic checklist with all edges present → pass; **any one** edge absent → **fail**,
  even when the ±3pp band is satisfied (**never averaged away**); (b) the enumerated set is **thin-file; self-employed/irregular
  income; age 18; age 65; BMI 25.00; BMI 30.00; DTI 40%; single-missing-document**; (c) **tier B** enforcement on the real corpus.
- **Tier**: **U (+B)**.

#### NFR-CORP-FREEZE-1 — freeze + single `rulebook_version` (BR-CORP-5/6, Fold 4)
- **Assertion**: `manifest.rulebook_version` **equals the version passed to every `evaluate()`** in the run; the frozen corpus is
  **self-contained data**; the freeze is pinned by `content_hash`.
- **Acceptance criteria**: (a) every `evaluate()` call in a run uses **one** `rulebook_version` = the manifest's (a run cannot mix
  versions); (b) **structural** — reading the frozen corpus imports **no** generator and **no** LLM client (consumers read data
  only); (c) `content_hash` pins the freeze (ties to NFR-CORP-HASH-1).
- **Tier**: **U**.

#### NFR-CORP-SEGREGATION-1 — demographic-swap label invariance (BR-CORP-7)
- **Assertion**: swapping the `Demographics` sub-object on an **otherwise-identical** profile leaves the **engine label unchanged**.
- **Acceptance criteria**: (a) build a profile + a copy differing **only** in `Demographics`; `evaluate` both → **same**
  `recommendation`; (b) **ownership note (not conflated)** — this is corpus-generator's **own layered-respect** check; it is **NOT**
  a substitute for, or a re-implementation of, `quality-gates`' bias-swap suite (the CON-BR1 verification owner, delta = 0 across the
  corpus).
- **Tier**: **U**.

#### NFR-CORP-REFNOTOWN-1 — reference-not-own; no local re-implementation (BR-CORP-8)
- **Assertion**: the **five** surfaces (`intake`, `rules-engine`, `memo-agent-core`, `secrets-config`, `common.canon_ser`) are
  imported **call-only** and **none edited**; corpus-generator defines **no local** hasher, derivation, rule-eval, or second
  temperature.
- **Acceptance criteria**: (a) a **structural** test — the unit imports those surfaces but contains **no** local `hashlib`/SHA or
  local `canon_ser`, **no** local age/BMI derivation, **no** rule evaluation, **no** temperature literal other than the injected
  seam's central one; (b) **non-vacuous self-test** — a synthetic local hasher / local derivation is flagged.
- **Tier**: **U (structural)**.

#### NFR-CORP-PROFILE-1 — valid profile; derivation equality (BR-CORP-9)
- **Assertion**: every emitted profile is a valid **frozen** `ApplicantProfile` (`extra="forbid"`); derived fields equal
  `intake.derivations`; `application_id` is the deterministic synthetic id.
- **Acceptance criteria**: (a) every profile constructs/round-trips through Pydantic without error; (b)
  `age_years_derived == intake.derivations.compute_age(dob, as_of)` and (when height/weight present)
  `bmi_derived == compute_bmi(height_cm, weight_kg)`; (c) `application_id == "corpus-<seed>-<index>"` deterministically.
- **Tier**: **U**.

#### NFR-CORP-HASH-1 — `content_hash` via shared CANON-SER; provenance excluded (BR-CORP-11)
- **Assertion**: `manifest.content_hash == common.canon_ser.content_hash(<canonicalized CorpusRecord list>)`; **provenance fields
  excluded**; **no local SHA/serialization**.
- **Acceptance criteria**: (a) the manifest hash **reproduces** via `common.canon_ser.content_hash()` over the canonicalized
  `CorpusRecord` list (`profile` + `label` + `edge_case_tags` + `documents_text`); (b) mutating a **provenance** field
  (`generation_timestamp`, …) leaves the hash **unchanged**; mutating a **profile/label/tag** field **changes** it; (c)
  **structural** — no local `hashlib`/serialization in corpus-generator (ties to NFR-CORP-REFNOTOWN-1).
- **Tier**: **U (+structural)**.

### SOFT — governance

#### NFR-CORP-PII-1 — zero real PII (BR-CORP-10, Q4)
- **Statement**: all data is synthetic (Faker structured fields + build-authored Gemini prose over synthetic inputs); **no real PII**.
- **Acceptance criteria**: (a) **governance** — synthetic-only by construction; (b) **light structural** (Q4-A) — the generation path
  reads **no external-identifier source** and makes **no network read** (the only network is the injected Gemini seam at tier B,
  **mocked** in CI).
- **Tier**: **governance (+ light structural, U)**.

---

## 2. Traceability (target → BR-CORP → tier → rigor)

| Target | BR-CORP | Tier | Rigor |
|---|---|---|---|
| NFR-CORP-DET-1 | 1 | U | full |
| NFR-CORP-LABEL-1 | 2 | U | full |
| NFR-CORP-BOUND-1 | 3 | U | full |
| NFR-CORP-SKEW-BAND-1 | 4 (i) | U (+B) | full |
| NFR-CORP-SKEW-EDGE-1 | 4 (ii) | U (+B) | full |
| NFR-CORP-FREEZE-1 | 5/6 | U | full |
| NFR-CORP-SEGREGATION-1 | 7 | U | full |
| NFR-CORP-REFNOTOWN-1 | 8 | U (structural) | full |
| NFR-CORP-PROFILE-1 | 9 | U | full |
| NFR-CORP-HASH-1 | 11 | U (+structural) | full |
| NFR-CORP-PII-1 | 10 | governance (+ structural) | soft |

**No orphan** — BR-CORP-1..11 each map to a target (BR-CORP-5 and 6 share NFR-CORP-FREEZE-1).

---

## 3. Security-Guardrails compliance (enabled extension)

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A (referenced)** | The unit generates data; emitted profiles are Pydantic-valid (NFR-CORP-PROFILE-1). Application-input validation is `intake`'s SEC-2. |
| Prompt-injection defense | **N/A** | The Gemini prose call uses build-authored prompts over synthetic data; no untrusted external document is parsed here (SEC-1 is `document-sanitizer`'s). |
| Secrets management | **Compliant (referenced)** | `GEMINI_API_KEY` via `secrets-config` (SEC-3); no secret literal (NFR-CORP-REFNOTOWN-1); mocked in CI. |
| Read-only DB access for audit role | **N/A** | The unit writes `corpus/` files, not the audit DB. |
| Audit logging | **N/A** | Build provenance is the manifest, not the runtime audit trail (SEC-5 is `audit-store`'s). |
| **No real PII / synthetic-only** | **Compliant (owns it)** | **NFR-CORP-PII-1** — Faker + synthetic prose; governance + light structural (no external-identifier/network read). |

No blocking finding.

---

## 4. Settled items held (not re-opened)
- The **frozen FD** (BR-CORP-1..11, the five call-only deps incl. `common.canon_ser`, the manifest/record/config shapes) is the
  substrate — NFR builds testable targets **on** it.
- **CON-BR1 verification stays `quality-gates`'** — NFR-CORP-SEGREGATION-1 is corpus-generator's **own layered-respect** check, not
  that suite. **CON-BR2** label authority = `rules-engine`. **No LLM in the label path; no real PII; WIRE-1 untouched** (backend
  build-time unit).
- **The real full-corpus run is tier B / out-of-band** (Q7); tier S is a wiring smoke on a **test-scoped config** (Fold NFR-1).
  **Mock PDFs remain deferred** (FD Q5). Settled non-edits stay closed: `PROJECT-BRIEF.md`, `user-journey.md`, every built unit's
  code/design.
