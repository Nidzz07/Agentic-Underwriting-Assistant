# NFR Requirements — `rules-engine` (C2)

**Stage**: BUILD → NFR Requirements (per-unit) · cluster unit 2 (dependency order)
**Unit**: U3 `rules-engine` — the deterministic rulebook engine (pure Python, **zero LLM**)
**Depth**: comprehensive (invariant-bearing deterministic-core unit)
**Date**: 2026-07-05 · **Runtime**: Python **3.12 pinned** (build-wide, D6)
**Scope**: The unit's **testable non-functional targets**, built **ON the frozen, approved Functional
Design** — the C2 contract (`load_rulebook` / `evaluate` / `recommend`), the YAML `Rule` schema +
`input_fields` CON-BR1 mechanism + operator↔threshold §2.1 mapping, the tri-state `RuleResult`, the
`RuleResultReport` shape, the domain-confirmed boundaries, the `Decimal` derivations, the
fixed-precedence aggregation, and the deterministic `ConfidenceBands` are **settled and NOT
re-opened**. Every target below is a **pass/fail assertion** that becomes a pytest test at Code-Gen
(TDD, pytest-cov ≥ 90% per QA-6).

**How to read a target**: each `NFR-RULES-*` has an **ID**, a **statement**, a **measurable
assertion** (the pass/fail check), and **traceability**. "Blocking in `quality-gates`" means this unit
*authors* the test and *defines* the target; the `quality-gates` unit *aggregates* it as a blocking
gate — this unit does **not** re-implement the harness (reference-not-own). Two intentional
non-pass/fail items are marked: **NFR-RULES-PERF-1** (observed, not gated) and the tech-stack
confirmations (in `tech-stack-decisions.md`).

---

## 1. Reproducibility / determinism — CON-DET-1 (the dominant NFR; the replay dependency)

### NFR-RULES-DET-1 — determinism: byte-identical `evaluate` ×N (same order)
- **Statement**: `evaluate(profile, rulebook_version)` is a **pure function** — repeated runs on the
  **same input** produce a **byte-identical** `RuleResultReport`.
- **Measurable assertions** (pass/fail):
  - **Same-input ×N≥10** — run `evaluate` ≥10× on identical `(profile, rulebook_version)`; the
    canonically-serialized report is identical every run.
    `assert len({canon_report(evaluate(p, v)) for _ in range(10)}) == 1` (mirrors NFR-REPRO-1
    same-input×10).
  - **No non-determinism sources** — no wall-clock, no unseeded randomness, no dict-order reliance in
    `evaluate` / aggregation / confidence (asserted by construction + the ×N test).
- **Traceability**: CON-DET-1, NFR-REPRO-1, FD `business-logic-model.md §2`. **Blocking in
  `quality-gates`** (reproducibility suite).

### NFR-RULES-DET-2 — order-independence: permuted evaluation order → identical result
- **Statement**: the recommendation is a pure function of the **set** of `outcome_tier`
  contributions, **not** of rule evaluation order — a **distinct** guarantee from DET-1 (DET-1 = same
  order ×N; DET-2 = *different* order, same result).
- **Measurable assertions** (pass/fail):
  - **Seeded permutation equality** — for seeded permutations of the rulebook's rule order,
    `evaluate` yields the **same `recommendation` + `confidence`** and the **same canonical report**
    (the `rule_results` list is re-sorted to its fixed deterministic order, so the report is
    byte-identical). `assert canon_report(evaluate_ordered(perm)) == canon_report(evaluate_ordered(base))`.
  - **Hypothesis property** — over arbitrary permutations of the rule order, the canonical report is
    invariant (universal-quantifier: `∀ perm: result(perm) == result(base)`).
- **Traceability**: CON-DET-1, FD `business-rules.md §3` (order-independent aggregation),
  `business-logic-model.md §2`. **Blocking in `quality-gates`.**

### NFR-RULES-DEC-1 — `Decimal` derivation exactness (DR-DTI / DR-INCM)
- **Statement**: the engine-owned `dti_ratio` / `income_multiple` derivations are exact in `Decimal`
  (never float), quantized under the single shared context, and boundary-exact; a missing/uncomputable
  operand is handled deterministically as insufficient-info, never an error.
- **Measurable assertions** (pass/fail):
  - **Decimal 4dp `ROUND_HALF_UP`** via `backend/common/decimal_context` — no float on any
    threshold-compared value (by construction + type).
  - **Boundary-exact** — `dti_ratio == Decimal("0.40")` → **pass**; `Decimal("0.4001")` → **fail**;
    `income_multiple == ceiling` → **pass** (ceiling is the versioned rulebook threshold).
    `assert dti_rule(profile_at_0_40).status == "pass"` etc.
  - **Operand-missing / zero-income** — `verifiable_income_annual` absent/`0` (or debt absent) ⇒ the
    rule is **`not_evaluated`** with a **`refer_trigger`** contribution and `actual_value == null` —
    **never** a divide error, a fabricated ratio, or a silent pass.
    `assert dti_rule(missing_income).status == "not_evaluated" and tier == "refer_trigger"`.
- **Traceability**: CON-DET-1, FR-RULES-2, FD `business-rules.md §2` (DR-DTI/DR-INCM). **Blocking in
  `quality-gates`.**

### NFR-RULES-CANON-1 — rulebook canonicalization = shared CANON-SER via a `RulebookCanonAdapter`
- **Statement**: the rulebook's canonical form (the basis of `content_hash`, NFR-RULES-AUDIT-1) is
  produced by a **rules-engine-side `RulebookCanonAdapter`** that **normalizes the `Rulebook` into the
  EXISTING `backend/common/canon_ser.py` value space, then calls the UNCHANGED shared utility** — the
  **`CanonSerAdapter` precedent** (intake). **One canonicalization convention, no fork, no §2.1 change.**
  *(Sharpening 1.)*
- **Measurable assertions** (pass/fail):
  - **Adapter normalization is total + declared** — every rule-set shape maps into canon_ser's value
    space: **`set`-threshold → a declared-sorted `list`** (sorted by **canonical string form**, a
    deterministic total order), **`DecimalRange` → a dict of `Decimal`+`bool`**, **enum → `.value`**,
    **`ScalarLiteral` → native scalar**. `assert canon_rulebook(rb)` succeeds for every valid rulebook
    and never passes a raw `set` to `canon_ser`.
  - **Byte-stability + set-order invariance** — the same logical rulebook → the **same canonical
    bytes** on every run, **regardless of set insertion order** (the declared sort makes set ordering
    deterministic). `assert canon_rulebook(rb_set_order_A) == canon_rulebook(rb_set_order_B)`.
  - **No shared-spec change** — `backend/common/canon_ser.py` and audit-store §2.1 are **unchanged**;
    the adapter lives in rules-engine. audit-store is unaffected (it never canonicalizes a rulebook,
    never passes a set). *(If a native-`set` branch on the shared util is ever preferred instead, that
    is a conscious backward-compatible shared-code decision to LOG — the adapter path avoids it.)*
- **Traceability**: CON-DET-1, CON-AUDIT-1, audit-store §2.1 (the single spec), intake
  `CanonSerAdapter` precedent. **Blocking in `quality-gates`** (jointly with the replay suite).

---

## 2. Bias-exclusion robustness — CON-BR1 (structural, load-time; belt-and-suspenders)

### NFR-RULES-BR1-1 — load-time rejection (universal-quantifier property)
- **Statement**: `load_rulebook` **rejects at load** any rule whose `input_fields` names a demographic
  path **or** any field outside the allowlist namespace — a malformed/adversarial rulebook **fails to
  load**, it does not silently resolve to nothing.
- **Measurable assertions** (pass/fail):
  - **Hypothesis universal-quantifier** — `∀` rule naming a demographic path (`demographics.*`,
    name/gender/city) **or** an unknown/out-of-allowlist field, `load_rulebook` **raises** a load error
    (the rulebook does not load). `assert raises(RulebookLoadError): load_rulebook(rb_with_bad_field)`
    over generated bad fields.
- **Traceability**: CON-BR1, FD `business-logic-model.md §4` (load-time schema validation), US-RULES-5.
  **Blocking in `quality-gates`** (feeds bias-swap; delta-verification stays single-sourced there).

### NFR-RULES-BR1-2 — namespace exclusion (independent structural guard)
- **Statement**: **independently of the load check**, the operand-resolution namespace built from a
  profile **never contains a demographic field** — a rule could not reach a demographic **even if the
  load-check were bypassed** (belt-and-suspenders, structural).
- **Measurable assertions** (pass/fail):
  - `assert not any(dem in build_namespace(profile) for dem in {"demographics", "full_name", "gender", "city"})`.
  - The namespace contains **only** the demographic-excluded fields + the engine-derived `dti_ratio` /
    `income_multiple`.
- **Traceability**: CON-BR1, FD `business-logic-model.md §4` (namespace exclusion, enforcement point 1).
  **Blocking in `quality-gates`.**

### NFR-RULES-SCHEMA-1 — operator↔threshold-shape validation at load
- **Statement**: `load_rulebook` **rejects** any rule whose `threshold` shape does not match its
  `operator` (FD §2.1) — no operator-threshold mismatch reaches evaluation.
- **Measurable assertions** (pass/fail):
  - `assert raises: load_rulebook(rule with operator="between" and a scalar Decimal threshold)`;
    likewise a categorical `in` with a `Decimal` threshold, a numeric bound as a bare `eq`, etc.
- **Traceability**: FR-RULES-3, FD `domain-entities.md §2.1`. **Blocking in `quality-gates`.**

---

## 3. Replay verifiability & versioning — CON-AUDIT-1 / FR-RULES-6

### NFR-RULES-AUDIT-1 — deterministic `content_hash`
- **Statement**: `content_hash` is a **deterministic** function of the canonicalized rule set
  (NFR-RULES-CANON-1) — **same rules → same hash; any rule change → a different hash** (tamper-evidence).
- **Measurable assertions** (pass/fail):
  - `assert content_hash(rb) == content_hash(rb)` (stable) **and** `content_hash(rb) != content_hash(rb_one_rule_changed)`.
  - `rulebook_version` (semver) + `content_hash` together are **sufficient + verifiable** to reconstruct
    the exact ruleset (the replay handle).
- **Traceability**: CON-AUDIT-1, FR-RULES-6, FD `business-logic-model.md §3`. **Blocking in
  `quality-gates`** (jointly with audit-store's replay suite).

### NFR-RULES-AUDIT-2 — immutable, append-only versioning
- **Statement**: a published rulebook version is **never edited in place** — a change is a **new
  version** (new semver + new `content_hash`); old versions are retained and remain loadable.
- **Measurable assertions** (pass/fail):
  - `assert load_rulebook("1.0.0") is byte-stable across calls` (immutable frozen set).
  - `assert load_rulebook(old_version)` still resolves after a new version exists, and the two are
    distinct frozen sets with distinct `content_hash`.
- **Traceability**: CON-AUDIT-1, FR-RULES-6, FD `business-logic-model.md §3`, skill (never mutate a
  published rule version). **Blocking in `quality-gates`.**

### NFR-RULES-AUDIT-3 — forensic-not-equality split (matches audit-store's replay projection)
- **Statement**: on replay, `rulebook_version` + `content_hash` + `engine_version` are
  **forensic/verification** fields — they are **NOT** part of the replay **equality set**. The equality
  set is the **evaluation-output projection**: per-rule rows (`rule_id`/`status`/`actual_value`/
  `operator`/`threshold`/`outcome_tier`) + `recommendation` + `confidence`. This is **exactly**
  audit-store's replay projection (its FD §2.1/§3.1) — the same field treated the same way in both
  units, so an `engine_version` (git-SHA) change alone is **not** a false replay mismatch.
- **Measurable assertions** (pass/fail):
  - `assert replay_equality_set(report)` excludes `rulebook_version` / `content_hash` / `engine_version`
    and includes exactly the per-rule rows + `recommendation` + `confidence`.
  - A report differing **only** in `engine_version` compares **equal** under the projection;
    `content_hash` is used for **verification** (byte-identity of the loaded rulebook), not output equality.
- **Traceability**: CON-AUDIT-1, audit-store `domain-entities.md §2.1/§3.1` (projection authority),
  FD `business-logic-model.md §5`. **Blocking in `quality-gates`** (joint replay suite with audit-store).

---

## 4. Boundary exactness — FR-RULES-3 (the exact-threshold discipline)

### NFR-RULES-BND-1 — domain-confirmed boundaries land on the intended side
- **Statement**: each domain-confirmed boundary is a first-class assertion; each `RuleResult` records
  the **exact `actual_value` + the explicit `operator`**.
- **Measurable assertions** (pass/fail):
  - **Age eligibility** — `18` → eligible, `65` → eligible (both inclusive); `17` / `66` → not.
  - **DTI** — `dti_ratio == 0.40` → **pass**; `0.4001` → **fail**.
  - **BMI** — `25.00` → **overweight** (not normal); `30.00` → **obese**.
  - Each fired `RuleResult` carries the exact value + the operator (`<=` vs `<`) it was compared with.
    `assert result.actual_value == Decimal("0.40") and result.operator == "lte" and result.status == "pass"`.
- **Traceability**: FR-RULES-3, US-RULES-2, FD `business-rules.md §1` (boundary table), skill
  (boundary behaviour is first-class). **Blocking in `quality-gates`.**

---

## 5. Aggregation & insufficient-info — FR-RULES-5 / CON-BR2

### NFR-RULES-AGG-1 — order-independent precedence + single-notioned insufficient-info REFER
- **Statement**: the recommendation is a pure function of the `outcome_tier` **set** under fixed
  precedence **DECLINE > REFER > APPROVE**; insufficient information routes to **REFER**, never a hard
  DECLINE (thin-file preserved).
- **Measurable assertions** (pass/fail):
  - **Precedence** — any `decline_fail` ⇒ **DECLINE-RECOMMEND** (decline dominates, even if also
    incomplete); else any `refer_trigger` ⇒ **REFER**; else all pass ⇒ **APPROVE**. The `-RECOMMEND`
    suffix is mandatory (FR-RULES-5).
  - **Order-independent** — the aggregate is invariant under rule-order permutation (shares the
    NFR-RULES-DET-2 permutation harness). `assert aggregate(shuffle(tiers)) == aggregate(tiers)`.
  - **Insufficient-info → REFER, never DECLINE** — `profile.incomplete == true` contributes a distinct
    insufficient-info `refer_trigger`; a `not_evaluated` rule contributes a `refer_trigger`; neither
    ever contributes `decline_fail`. `assert recommend(incomplete_only) == "REFER"` (never
    "DECLINE-RECOMMEND").
  - **Explainability** — `decline_reasons` / `refer_reasons` name exactly the driving rule(s).
- **Traceability**: FR-RULES-5, US-RULES-3, CON-BR2, FR-INTAKE-3 (thin-file → REFER), FD
  `business-rules.md §3/§3.1`. **Blocking in `quality-gates`.**

---

## 6. Deterministic confidence — CON-DET-1 / CON-BR2

### NFR-RULES-CONF-1 — replay-stable deterministic confidence banding
- **Statement**: `confidence ∈ {High, Medium, Low}` is a **pure function** of value-proximity +
  completeness using the **fixed `ConfidenceBands` constants** carried in the versioned rulebook —
  **produced in rules-engine, never by the LLM** (CON-BR2).
- **Measurable assertions** (pass/fail):
  - **Replay-stable** — same input + `rulebook_version` → **identical `confidence` ×N** (no randomness,
    no wall-clock). `assert len({evaluate(p, v).confidence for _ in range(10)}) == 1`.
  - **Versioned constants** — the bands are fixed constants **in the rulebook version**; a margin
    change is itself a **new version** (replay under the original stays exact).
  - **Sole-origin** — confidence is set by this unit; no LLM path can produce or alter it.
- **Traceability**: CON-DET-1, CON-BR2 (reviewer G2), FD `business-rules.md §4`. **Blocking in
  `quality-gates`** (reproducibility suite).

---

## 7. Performance — scoped soft budget (observed, NOT gated)

### NFR-RULES-PERF-1 — `evaluate()` soft budget
- **Statement**: a **soft, observed** latency budget for `evaluate()` over the full **25–40-rule** set
  on a typical synthetic profile — **not an SLA, not a blocking gate**.
- **Measurable assertions / commitments**:
  - **Observed p-target** — a documented best-effort target for `evaluate()` (in-memory, pure-Python),
    **recorded via emitted timing** (NFR-RULES-OBS-1), **not** a breach-failing check.
  - **No hard timeout** — unlike intake's sandbox, this unit does **no untrusted parsing**; it operates
    on already-validated data, so **no hard timeout bound is needed or defined**.
  - **Priority order** — correctness + determinism + explainability **take precedence over speed** (skill).
- **Traceability**: Brief §6, skill (explainability/consistency over speed). **Observed, not blocking.**
  *(Intentional non-pass/fail exception.)*

---

## 8. Observability — EMIT-ONLY, demographic-free (CON-BR1 extends to telemetry)

### NFR-RULES-OBS-1 — emit-only via an allowlist schema that structurally excludes demographic content
- **Statement**: rules-engine **emits** structured signals for the `observability` unit to wire; it
  does **NOT** own the Langfuse/Prometheus/Grafana stack. The emit schema **structurally cannot carry a
  demographic value** — the **same mechanism as intake's no-free-text `TelemetryEmitter`** (an allowlist
  Pydantic schema of typed non-text fields), not a convention to omit.
- **Measurable assertions** (pass/fail):
  - **Allowlist schema** — emitted events carry **only** rulebook-metadata (`rule_id`), enums
    (`recommendation`, `confidence`, aggregation-tier, per-rule `status`), and **int counts**
    (per-`recommendation`, per-rule fired / `not_evaluated`) + derivation timing (int). **No
    applicant-profile-derived value, no demographic field, no free-text/`str` field** that could hold
    one. `assert emitted_signals ⊆ {rule_ids, enums, ints}` and the emitter schema has **no free-text /
    profile-value field** (schema-level assertion, mirroring intake NFR-INT-FORENSIC(b)).
  - **No LLM** — there is no LLM in this path; nothing to trace on that axis.
  - **Reference-not-own** — this unit does not implement the observability stack; it exposes the signals.
- **Traceability**: CON-BR1 (extends to telemetry), NFR-OBS-1/2 (scope boundary only), intake
  `TelemetryEmitter` precedent. Stack owned by `observability`.

---

## 9. Traceability & ownership summary

| NFR ID | Invariant / Req | Test lives (authored) | Aggregated / owned |
|---|---|---|---|
| NFR-RULES-DET-1 | CON-DET-1, NFR-REPRO-1 | this unit (same-order ×N) | `quality-gates` (reproducibility) |
| NFR-RULES-DET-2 | CON-DET-1 (order-independence) | this unit (permutation + Hypothesis) | `quality-gates` (blocking) |
| NFR-RULES-DEC-1 | CON-DET-1, FR-RULES-2 | this unit (boundary + operand-missing) | `quality-gates` (blocking) |
| NFR-RULES-CANON-1 | CON-DET-1, CON-AUDIT-1 | this unit (`RulebookCanonAdapter`) | `quality-gates` (joint replay) |
| NFR-RULES-BR1-1 | CON-BR1 (load-time) | this unit (universal-quantifier) | `quality-gates` (bias-swap) |
| NFR-RULES-BR1-2 | CON-BR1 (namespace) | this unit (independent guard) | `quality-gates` (bias-swap) |
| NFR-RULES-SCHEMA-1 | FR-RULES-3 (§2.1) | this unit (load-validation) | `quality-gates` (blocking) |
| NFR-RULES-AUDIT-1 | CON-AUDIT-1, FR-RULES-6 | this unit (+ audit-store) | `quality-gates` (joint replay) |
| NFR-RULES-AUDIT-2 | CON-AUDIT-1, FR-RULES-6 | this unit (append-only) | `quality-gates` (blocking) |
| NFR-RULES-AUDIT-3 | CON-AUDIT-1 | this unit + audit-store (projection) | `quality-gates` (joint replay) |
| NFR-RULES-BND-1 | FR-RULES-3, US-RULES-2 | this unit (boundary suite) | `quality-gates` (blocking) |
| NFR-RULES-AGG-1 | FR-RULES-5, CON-BR2 | this unit (precedence + thin-file) | `quality-gates` (blocking) |
| NFR-RULES-CONF-1 | CON-DET-1, CON-BR2 | this unit (×N confidence) | `quality-gates` (reproducibility) |
| NFR-RULES-PERF-1 | Brief §6 | this unit (emitted timing) | observed (soft) |
| NFR-RULES-OBS-1 | CON-BR1, NFR-OBS-1/2 (scope) | this unit (allowlist schema) | `observability` (stack) |

**Ownership held (reference-not-own)**: shared **CANON-SER** = audit-store §2.1 via
`backend/common/canon_ser.py` (used through the `RulebookCanonAdapter`, unchanged); the single
**`Decimal` context** = `backend/common/decimal_context`; observability **stack** = `observability`;
CON-DET-1 / CON-BR1 **verification** (reproducibility + bias-swap) = `quality-gates`; replay
**orchestration** (match/mismatch) = `audit-store` ReplayService; secrets = `secrets-config`.
**Infrastructure Design is expected to be SKIPPED** for this unit (pure-logic; no untrusted parsing →
no sandbox NFR; no independent cloud topology) — that call is made and logged when the stage is reached.
**No LLM anywhere in this unit** (CON-BR2). Runtime **Python 3.12 pinned** (D6).

---

*End of nfr-requirements.md. Tech choices + the canonicalization-adapter decision →
`tech-stack-decisions.md`.*
