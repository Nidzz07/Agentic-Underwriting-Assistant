# Business Rules — `corpus-generator` (U14)

**Stage**: BUILD → Functional Design (per-unit) · build-time synthetic-corpus unit · **Depth**: comprehensive
**Unit**: U14 `corpus-generator` · **Date**: 2026-07-07 · owns **CON-BR3**, DATA-1/2/3, FR-PROV-4 · Story **US-PLAT-7**.
**Scope**: The **enforceable rules** the generator and its skew-audit gate obey. Each states its condition and, where checkable,
names the mechanism (landing at NFR / Code-Gen). **Deterministic, seeded, no LLM in the label path, no real PII.** Built exactly on
the eight locked answers + four folds — re-opening none.

---

## 1. Determinism & seeding

### BR-CORP-1 — Seeded determinism (CON-DET-1)
- **Condition**: every structured field of every profile is a **pure function of the fixed `seed`** (`GenerationConfig`). **No
  wall-clock is read, no unseeded randomness is used, no dict-ordering assumption is made.** The `generation_timestamp` is
  **recorded** in the manifest but is **never an input** to generation. Same seed + same deps → the same corpus.
- **Why**: CON-DET-1 / DATA-3; the reproducibility suite must run on trustworthy, regenerable data.
- **Checkable**: regenerate with the same seed → identical structured profiles + identical labels (LLM prose is separately
  **frozen**, BR-CORP-5); a determinism test asserts no clock/`random`-without-seed usage.

---

## 2. Labeling authority

### BR-CORP-2 — The engine is the label authority (CON-BR2)
- **Condition**: a profile's class is **exactly** `RulesEngine.evaluate(profile, rulebook_version).recommendation`
  (`APPROVE` / `REFER` / `DECLINE-RECOMMEND`). `corpus-generator` **assigns no label independently**; `intended_class` is a
  generation *target* / provenance only and is **never** authoritative.
- **Why**: CON-BR2 (the recommendation originates in `rules-engine`); a single labeling authority prevents corpus-vs-engine drift.
- **Checkable**: for every `CorpusRecord`, `record.label == evaluate(record.profile, manifest.rulebook_version).recommendation`.

### BR-CORP-3 — Bounded rejection-sampling; never loops (Fold 1)
- **Condition**: generation is **bounded rejection-sampling toward per-class quotas under a fixed seeded attempt budget** — a
  generated-and-labeled profile is **kept if its engine-label still needs filling** (its class is below the ±3pp band target),
  else **discarded**; if the **attempt budget is exhausted before the band is met, the build fails the skew-audit gate loudly**
  (BR-CORP-4). **No unbounded regeneration loop exists.**
- **Why**: Fold 1/3 — the engine is the label authority, so "intended class" is only a generation heuristic; termination is
  guaranteed by the fixed budget, and failure is loud, not silent.
- **Checkable**: an attempt counter bounded by `attempt_budget`; on exhaustion the gate raises (a test drives an impossible target
  to assert the loud failure, not a hang).

---

## 3. Skew-audit gate (CON-BR3 / DATA-3)

### BR-CORP-4 — Blocking skew-audit before use: ±3pp band AND edge-case checklist (conjunction; Fold 2)
- **Condition**: before the corpus is frozen/usable, the `SkewAudit` gate asserts **both**, independently:
  1. **Distribution band** — each class proportion is within **±3 percentage-points** of `{APPROVE 40, REFER 35,
     DECLINE-RECOMMEND 25}`; **and**
  2. **Edge-case checklist** — **every** DATA-2 mandatory edge case is **present** (thin-file; self-employed / irregular income;
     exact-threshold boundaries **age 18, age 65, BMI 25.00, BMI 30.00, DTI 40%**; single-missing-document). **No edge case is
     optional or averaged into the band.**
  A failure of **either** condition **fails the build loudly** (no partial/ungated corpus is emitted).
- **Why**: CON-BR3 ("skew-audited before use") + DATA-1/DATA-2/DATA-3; `corpus-generator` is the **single source** of the
  skew-audited corpus (quality-gates consumes it, does not re-own the audit).
- **Checkable**: the gate is a build-blocking assertion over the realized corpus; the manifest records `class_proportions`,
  `tolerance_pp = 3`, and the full `edge_case_checklist` (all true). Jointly satisfiable at open-N **"300+"** (the free bulk pads
  each class to band while every edge case is present; N grows if ever needed).

---

## 4. Freeze & manifest (Q4 / Fold 4)

### BR-CORP-5 — Freeze-and-commit; consumers never re-call Gemini
- **Condition**: the generated corpus (JSON profiles + document text) is **committed** under `corpus/` and pinned by a
  `CorpusManifest` (`domain-entities.md §4`). Downstream consumers (`outlier-model`, `quality-gates`) **read the frozen artifact
  only** — they **never re-invoke the generator or Gemini**. Reproducibility holds for consumers even though LLM prose is not
  guaranteed byte-identical across model/time.
- **Why**: DATA-3 (manifest-versioned) + CON-DET-1 for consumers; LLM text is not byte-stable, so it is frozen, not regenerated.
- **Checkable**: `content_hash` over the frozen corpus matches the manifest; no consumer imports the generator or an LLM client.

### BR-CORP-6 — Single, unambiguous `rulebook_version` (Fold 4)
- **Condition**: the manifest records the **single** `rulebook_version` semver (+ `engine_version`, provider `model_version`) the
  corpus was labeled against. A future production-rulebook version (the deferred 25–40-rule set) is a **new** version → a
  **deliberate, tracked regeneration**, never an in-place relabel.
- **Why**: mirrors `rules-engine`'s append-only/replay contract.
- **Checkable**: `manifest.rulebook_version` equals the version passed to every `evaluate()` call in the run.

---

## 5. Demographic segregation (CON-BR1 layered-respect)

### BR-CORP-7 — Demographics present-but-separable; no bias-swap suite here (Q6)
- **Condition**: demographic identifiers (name / gender / city) are generated **seeded-independently** and populated **only** into
  the profile's **already-segregated `Demographics` sub-object** (frozen schema: *"Never a rule/feature input"*). They **never**
  influence the financial/medical fields or the `label`. `corpus-generator` authors **no bias-swap suite and no pre-made swap pairs**.
- **Why**: CON-BR1 is **verified** by `quality-gates` (delta = 0) and **enforced** in the feature vector by `outlier-model`;
  `corpus-generator` is a **layered-respect** point only (defense-in-depth), not a co-owner of the invariant.
- **Checkable**: swapping the `Demographics` sub-object across otherwise-identical profiles leaves the engine `label` unchanged
  (a property the corpus must uphold; the *suite* that asserts it lives in `quality-gates`).

---

## 6. Reference-not-own & PII

### BR-CORP-8 — Call-only build-time dependencies; injected LLM; no LLM in the label path (Q1/Q2/Q8)
- **Condition**: the four build-time deps — `intake` (derivations + schema), `rules-engine` (`evaluate`), `memo-agent-core`
  (`LLMClient` seam), `secrets-config` (`GEMINI_API_KEY`) — are **consumed call-only / reference-not-own; none is edited**. The
  Gemini path is **injected** (`temperature=0` fixed centrally in the adapter; offline-testable). The **LLM produces document PROSE
  only** (FR-PROV-4) — it is **never** in the label path (labels come from `rules-engine`, BR-CORP-2).
- **Why**: reference-not-own; CON-BR2; FR-PROV-4; TEMP0-1 discipline (temperature=0, offline-testable).
- **Checkable**: a structural check finds no production edit in the deps and no LLM call on the labeling path; a capturing double
  proves the prose path is offline-testable.

### BR-CORP-9 — Every profile is a valid `ApplicantProfile`; derivations single-sourced (Q8)
- **Condition**: every emitted profile is a valid **frozen** `intake.ApplicantProfile` (`extra="forbid"`), with
  `age_years_derived` / `bmi_derived` computed via **`intake.derivations`** (no re-implementation), and a **deterministic synthetic
  `application_id`** (`corpus-<seed>-<index>`).
- **Why**: Q8 — single-sourced derivation avoids age/BMI drift vs intake; boundary-exact (25.00 / 30.00) is essential for DATA-2.
- **Checkable**: profile construction round-trips through Pydantic validation; derived fields equal `intake.derivations` output.

### BR-CORP-10 — Zero real PII; advisory boundary
- **Condition**: **all** data is synthetic (Faker structured fields + Gemini prose); **no real PII** at any stage. The unit
  **finalizes no decision** and **runs no LLM in the label path**.
- **Why**: technical constraint (synthetic/mock only); advisory-only architecture.
- **Checkable**: review + the offline test posture; no external identifier source.

### BR-CORP-11 — `content_hash` via the shared CANON-SER; no second hasher (cross-unit contract)
- **Condition**: `CorpusManifest.content_hash` is computed by the **single shared CANON-SER** — `common.canon_ser.content_hash()`
  (SHA-256 over `canon_ser` canonical bytes) — **not** a re-declared or divergent hashing implementation. It is applied over the
  **canonicalized frozen corpus content**: the structured `CorpusRecord` list (`profile` + `label` + `edge_case_tags` +
  `documents_text`). The manifest's own **provenance fields are EXCLUDED** from the hash (`generation_timestamp`, `content_hash`
  itself, and the version/count metadata) — exactly as `engine_version`/timestamp are excluded from audit-store's replay-equality
  projection (CANON-SER **P4**: no volatile fields). The LLM-generated `documents_text` is a **JSON-native `str`** to `canon_ser`, so
  it canonicalizes **in the same pass** as the structured fields — **no separate raw-bytes path and no blended mechanism** (canon_ser
  accepts `str` as a JSON-native scalar).
- **Why**: CANON-SER is the **one** canonical-serialization/`content_hash` implementation every hashing unit delegates to
  (intake's `ApplicantProfileSnapshot`, rules-engine's `RuleResultReport`, audit-store's persisted hashes, memo-agent-core's
  `memo_hash`) — *"CANON-SER is referenced, not re-declared."* A second hasher here would risk a divergent, drift-prone corpus hash.
- **Reference-not-own**: `common.canon_ser` is a shared `backend/common/` surface (**no unit owns it**; audit-store is the spec
  authority) consumed **call-only, not edited** — a fifth consumed surface alongside the four unit deps.
- **Checkable**: the manifest hash equals `common.canon_ser.content_hash(<canonicalized CorpusRecord list>)`; a structural check
  finds **no** local SHA/serialization helper in `corpus-generator`; excluded provenance fields do not change the hash.

---

## 7. Rule index

| Rule | Condition summary | Traces |
|---|---|---|
| BR-CORP-1 | seeded determinism; clock-free; timestamp recorded not input | CON-DET-1, DATA-3 |
| BR-CORP-2 | class = engine `evaluate().recommendation`; no independent label | CON-BR2 |
| BR-CORP-3 | bounded rejection-sampling; fixed budget; gate-fail-loud; never loops | Fold 1/3 |
| BR-CORP-4 | blocking skew-audit: ±3pp band AND edge-case checklist (conjunction) | CON-BR3, DATA-1/2/3, Fold 2 |
| BR-CORP-5 | freeze-and-commit; consumers never re-call Gemini | DATA-3, Q4 |
| BR-CORP-6 | single unambiguous `rulebook_version`; future version = tracked regeneration | Fold 4 |
| BR-CORP-7 | demographics present-but-separable; no bias-swap suite here | CON-BR1 (layered), Q6 |
| BR-CORP-8 | call-only deps; injected LLM; no LLM in the label path | reference-not-own, CON-BR2, FR-PROV-4 |
| BR-CORP-9 | valid `ApplicantProfile`; derivations via `intake.derivations`; synthetic id | Q8, DATA-2 |
| BR-CORP-10 | zero real PII; no decision finalized | tech constraints, advisory-only |
| BR-CORP-11 | `content_hash` via shared CANON-SER (no second hasher); prose is JSON-native `str`; provenance excluded (P4) | CANON-SER cross-unit contract, DATA-3 |

---

## 8. Security-Guardrails compliance (enabled extension)

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A (referenced)** | The unit generates data; it validates no *application* input (that is `intake`'s SEC-2). Emitted profiles are Pydantic-valid (BR-CORP-9). |
| Prompt-injection defense | **N/A** | The Gemini prose call uses build-authored prompts over synthetic data; no untrusted external document is parsed here (SEC-1 is `document-sanitizer`'s). |
| Secrets management | **Compliant (referenced)** | `GEMINI_API_KEY` is read via `secrets-config` (SEC-3); no secret literal in the unit (BR-CORP-8). |
| Read-only DB access for audit role | **N/A** | The unit persists to `corpus/` files, not the audit DB. |
| Audit logging | **N/A** | The build provenance is the manifest, not the runtime audit trail (that is `audit-store`'s SEC-5). |
| **No real PII / synthetic-only** | **Compliant (owns it)** | BR-CORP-10 — Faker + synthetic prose; zero real PII. |

No blocking finding.
