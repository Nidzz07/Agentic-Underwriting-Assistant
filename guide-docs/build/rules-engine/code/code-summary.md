# Code Summary — `rules-engine` (C2) · BUILD → Code Generation (Part 2)

**Unit**: U3 `rules-engine` — the deterministic rulebook engine (pure Python, **zero LLM**).
**Date**: 2026-07-05 · **Runtime**: Python **3.12** (pinned, D6).
**Result**: **174 rules-engine tests pass; source coverage 100%** (full backend suite **386 passed /
3 skipped / 99.62%**, QA-6 ≥90% gate reached). App code at `backend/rules_engine/` (never `guide-docs/`).
Implements the frozen FD + approved `NFR-RULES-*` targets + NFR patterns + 9 components — **re-opening none**.

**Update 2026-07-05 (gap resolved, option (a)):** the two non-scalar categories are now authored via
**derived scalar operands** (`health_flag_count`, `documents_missing_count`) added to `DerivationFunctions`
+ the allowlist + namespace, **back-annotated into the frozen FD** (`domain-entities.md §4.2`). The
evaluator stays **scalar-only** (not extended). **All 9 categories now rule-exercised** — the minimal
representative rulebook is complete. See §5.

---

## 1. Modules generated (`backend/rules_engine/`)

| Module | Component | Role |
|---|---|---|
| `report_schema.py` | (data leaf) | Frozen `RuleResult` / `RuleResultReport` + shared enums (`Operator`/`RuleCategory`/`OutcomeTier`/`RuleStatus`/`Recommendation`/`Confidence`) + `DecimalRange`; float-rejecting `Number`. |
| `rulebook_schema.py` | (data leaf) | `Rule`/`Rulebook`/`ConfidenceBands` (Pydantic v2) + load validators — single-sourced `ALLOWED_INPUT_FIELDS` (BR1-1), operator↔threshold shape (SCHEMA-1). |
| `canon_adapter.py` | RulebookCanonAdapter | Normalize → **unchanged** shared `canon_ser`; `content_hash` (set→sorted-list, DecimalRange→dict, enum→.value). |
| `derivations.py` | DerivationFunctions | DR-DTI / DR-INCM `Decimal` 4dp `ROUND_HALF_UP`, **guard-before-divide**. |
| `namespace.py` | NamespaceBuilder | Demographic-excluded operand namespace + derived operands (BR1-2). |
| `loader.py` | RulebookLoader | `pyyaml safe_load` → validate → freeze → hash-verify → versioned cache; append-only. |
| `evaluator.py` | RuleEvaluator | Pure per-rule tri-state evaluation, fixed canonical order by `rule_id`, boundary-exact. |
| `aggregator.py` | Aggregator | Set-reduction precedence (DECLINE>REFER>APPROVE); thin-file→REFER; reason lists. |
| `confidence.py` | ConfidenceBander | Deterministic High/Med/Low over fixed versioned `ConfidenceBands`. |
| `report.py` | ReportBuilder | Assemble report — all list fields canonical order (DET-2); `evaluation_output` projection (AUDIT-3). |
| `engine.py` | RulesEngine | `load_rulebook` + pure `evaluate(profile, rulebook_version)`; **injected** `engine_version`. |
| `telemetry.py` | TelemetryEmitter | Allowlist schema (OBS-1 — no profile/demographic/free-text field); observed-only timing (PERF-1). |
| `rulebook/1.0.0.yaml`, `1.1.0.yaml` | (data) | Representative rulebook — 2 versions, all 7 operators, all 3 tiers, set-thresholds, 7 scalar/enum categories. |

Shared, **reference-not-own** (imported, never edited/re-declared): `backend/common/canon_ser.py`,
`backend/common/decimal_context.py`, intake's `ApplicantProfile` (`backend/intake/schema.py`).

## 2. Tests → target map (`backend/rules_engine/tests/`)

| Target / invariant | Test(s) |
|---|---|
| **DET-1** (same-order ×N byte-identical) | `test_evaluator::test_det1_byte_identical_across_ten_runs`, `test_engine::test_det1_same_order_byte_identical_across_ten_runs` |
| **DET-2** (permuted → byte-identical whole report) | `test_report::test_det2_whole_report_byte_identity_under_any_permutation`, `test_engine::test_det2_reversed_rule_authoring_yields_identical_report` |
| **DEC-1** (Decimal, guard-before-divide) | `test_derivations::*` |
| **CANON-1** (set-order-invariant hash) | `test_canon_adapter::test_set_threshold_order_invariant`, `test_rulebook_data::test_has_a_set_threshold_rule` |
| **BR1-1** load-reject ∀ (Hypothesis) | `test_loader::test_forall_out_of_allowlist_field_rejected_at_load`, `test_rulebook_schema::*` |
| **BR1-2** namespace exclusion | `test_namespace::test_demographics_never_in_namespace` |
| **SCHEMA-1** operator↔threshold reject | `test_loader::test_load_rejects_operator_threshold_mismatch` |
| **AUDIT-1** deterministic hash + tamper-verify | `test_loader::test_build_tamper_mismatch_rejected`, `test_rulebook_data::test_both_versions_load_with_distinct_hash` |
| **AUDIT-2** append-only immutable | `test_loader::test_append_only_two_versions_both_loadable_distinct_hash`, `test_loaded_rulebook_is_frozen_immutable` |
| **AUDIT-3** forensic-not-equality projection | `test_report::test_engine_version_difference_is_equal_under_output_projection` |
| **BND-1** boundary exactness | `test_evaluator::test_age_boundary_inclusive` / `test_bmi_25_is_overweight_not_normal` / `test_dti_ceiling_exact` |
| **AGG-1** order-independent + thin-file→REFER | `test_aggregator::test_recommendation_and_reasons_are_permutation_invariant` / `test_incomplete_*` |
| **CONF-1** deterministic banding | `test_confidence::test_confidence_is_permutation_invariant` / `test_deterministic_across_ten_runs` |
| **OBS-1** allowlist telemetry (demographic-free) | `test_telemetry::test_only_str_leaves_are_rulebook_metadata` / `test_telemetry_bytes_carry_no_applicant_free_text` |
| **PERF-1** observed-not-gated | `test_telemetry::test_perf_timing_observed_not_gated` |
| End-to-end APPROVE/REFER/DECLINE | `test_engine::*`, `test_rulebook_data::test_*_profile_*` |

## 3. Sharpenings folded in (from the Part-1 ambiguity-check)
1. **`engine_version` INJECTED** via `RulesEngine.__init__` — never git/file-I/O inside `evaluate()` (DET-1 purity).
2. **All 7 operators** exercised (`test_evaluator::test_all_seven_operators_exercised` + rulebook `test_all_seven_operators_present`).
3. **≥2 rulebook versions** (`1.0.0` + `1.1.0`) — append-only, distinct hash, both loadable.
4. **All 3 recommendation tiers** reachable end-to-end (APPROVE / REFER / DECLINE-RECOMMEND).
5. **≥1 set-threshold (`in`) rule** — CANON-1 set-order path exercised end-to-end.

## 4. Realization notes (faithful to the frozen design — flagged, not silent)
- **`rulebook_schema.Rule.threshold` given `union_mode="left_to_right"`** (a 1-line Step-2 correction): a YAML
  string bound (`"0.40"`) now coerces to `Decimal` (`Number` tried first) per FD §2.1, instead of Pydantic
  smart-union keeping it a `str`. No field/shape/behavior change; Step-2 tests still pass. Needed once YAML
  string thresholds were introduced at Step 6.
- **Authoring convention (frozen evaluator §2):** a rule's `operator`/`threshold` encodes the **acceptable**
  condition → PASS; the `outcome` tier is contributed on **FAIL**. So "obese is bad" is authored as the
  acceptable `bmi < 30` (obese fails → refer), not `bmi >= 30`. All representative rules follow this.

## 5. ✅ Gap resolved (option (a) — derived scalar operands; evaluator NOT extended)
`medical_health` (`health_flags`, a **list**) and `document_completeness` (`documents`, a **`DocumentManifest`
object**) were not authorable under the frozen scalar/enum evaluator. Resolved per the approved direction by
adding **two derived SCALAR operands** (back-annotated into the frozen FD `domain-entities.md §4.2`), computed
by `DerivationFunctions` alongside `dti_ratio`/`income_multiple`, exposed in the namespace, added to the
single-sourced `ALLOWED_INPUT_FIELDS`:

| Derived operand | Type | Derivation | Authored rule (acceptable→PASS) |
|---|---|---|---|
| `health_flag_count` | `int` | `len(health_flags)` | `MED-HEALTH-1`: `health_flag_count lte 0` → `refer_trigger` (any flag → REFER). |
| `documents_missing_count` | `int` | `max(expected_count − satisfied_count, 0)` | `DOCS-COMPLETE-1`: `documents_missing_count lte 0` → `refer_trigger` (thin-file → REFER, never DECLINE). |

**`int` over `bool`**: an `int` authors directly with the frozen numeric operators (`lte`/`eq` + `Decimal`
threshold); a `bool` would need a §2.1 change or the awkward `in {true}` idiom. **Evaluator unchanged**
(scalar-only holds); pure deterministic `int` derivations, **no new divide path**. BR1-1 load-reject + BR1-2
namespace-exclusion still hold (the 2 new fields are in-allowlist; a demographic path still rejects — the
Hypothesis ∀ and the extended namespace-exclusion test confirm it). **All 9 categories now rule-exercised**
(`test_rulebook_data::test_all_nine_categories_present`). The full 25–40-rule population remains the deferred
data-authoring pass.

## 6. N/A step-categories (justified — plan Q6)
API layer (FastAPI orchestrator), Repository/persistence (`audit-store` + `database`), Frontend, DB migrations,
replay orchestration (`audit-store` ReplayService). This unit generates **business logic + tests + this summary** only.
