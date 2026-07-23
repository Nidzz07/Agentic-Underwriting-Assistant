# Domain Entities — `llm-judge` (EPIC-6 / U22, Phase 2)

**Stage**: BUILD → per-unit loop → **Functional Design, Part 2 (Generation)** · **Depth**: **standard** (Q5-A, per
`unit-of-work.md` L249's explicit pin) · **Date**: 2026-07-19
**Built ON** the frozen `memo-agent-core` (U4), `memo-extensions` (U19), `observability` (U21) and `corpus-generator` (`R`)
contracts — **re-opening none**. Answers **Q1–Q7 (all A)**; folds **CG-JUDGE-Fold-1..3**; gap **CG-JUDGE-GAP-1** disclosed.

**⚑ U22 is the LAST unit in the 23-unit decomposition** — the 6th and final Phase-2 unit.

---

## 1. Scope

`llm-judge` owns the **memo-quality half of the provider gate** (FR-PROV-GATE-2): an **LLM-as-judge groundedness rubric**
scoring drafted memo prose at **≥ 4/5**, applied to **Gemini (primary) + Claude (secondary)**, with **Ollama exempt**
(showcase-only). It is a **wrap-the-built-system** unit (`unit-of-work-dependency.md` L200) — a **read-only consumer of
frozen output shapes**, strictly downstream, **editing no unit it observes** (Q2-A).

**It does NOT own**: FR-PROV-GATE-1's decision-level gates (reproducibility, bias-swap) — those are **`quality-gates`'**;
memo *generation* — that is U4's; the memo *hallucination guard* (`validate_citations`) — that is U4's deterministic guard,
which U22 **layers on**, never replaces.

---

## 2. The rubric definition — `GroundednessRubric`

The rubric is a **declarative value object**: a fixed, ordered set of **scored dimensions**, each scored on the **1–5
integer scale** that AC-6's *"≥ 4/5"* presupposes.

| Field | Type | Meaning |
|---|---|---|
| `rubric_id` | `str` | Stable identifier of this rubric revision. |
| `dimensions` | `list[RubricDimension]` | The ordered scored dimensions (§2.1). **Declared order IS the deterministic report order.** |
| `threshold` | `int` | The pass mark. **`4`** — AC-6 / QA-4 *"≥ 4/5"*. |
| `scale_max` | `int` | **`5`**. |

### 2.1 `RubricDimension` — the scored dimensions

| Field | Type | Meaning |
|---|---|---|
| `dimension_id` | `str` | Stable id, e.g. `groundedness`, `anchoring_consistency`. |
| `description` | `str` | The judge-facing criterion text. **Advisory-only wording; no demographic reference.** |
| `weight` | `int` | Contribution to the aggregate (equal by default — no hidden weighting). |

**The dimension set (standard depth — two dimensions, both with teeth):**

1. **`groundedness`** *(the AC-2 / AC-6 core)* — is every claim in `narrative_prose` **supported by the handed rule report**,
   and is **every cited rule id actually present** in it? This is the *"zero unexplained recommendations"* criterion (AC-2).
   It **complements** U4's deterministic `validate_citations`: that guard answers *"is this id real?"*; the rubric answers
   *"is the prose actually grounded in the evidence?"*.
2. **`anchoring_consistency`** *(Q7-A)* — is the memo's **wording and structure consistent with the reference memo**?
   Per QA-4, consistency is *"**not claimed bit-identical**"* — so this scores **style/structure adherence**, not textual
   identity. **Scored against a U22-owned reference memo fixture (§4), never against a per-applicant twin** (Fold-3).

> **⛔ Honest-scope note (CG-JUDGE-GAP-1 / `FEWSHOT-ANCHOR-UNIMPLEMENTED`).** QA-4's clause has **two halves**. U22 delivers
> the **scoring** half (`anchoring_consistency`). The **generation** half — supplying few-shot exemplars to the memo prompt so
> the draft is *anchored at draft time* — is **NOT implemented anywhere in the build** (repo-wide scan: **zero hits**; U4's
> frozen `PromptBuilder` carries no reference memo and no exemplars) and **cannot** be implemented here without editing the
> frozen U4. It is disclosed by name on the register. **U22 does not claim to discharge it.**

---

## 3. `JudgedSample` — one memo submitted for scoring

| Field | Type | Meaning |
|---|---|---|
| `sample_id` | `str` | Stable identifier within an eval run. |
| `memo` | `DecisionMemo` | **Reference-not-own** — the frozen U4 shape, **imported read-only**. |
| `rule_report` | `RuleResultReport` | **Reference-not-own** — the frozen grounding source the memo must be anchored to. |
| `provider` | `ProviderScopeTag` | Which provider drafted this memo (§5) — **drives in-gate vs exempt**. |

**Only `memo.narrative_prose` (the `L` region) is judged.** The `D` (`missing_information`), `RO`
(`recommendation`/`confidence`) and `M` (`memo_hash`/`model_version`) regions are deterministic or injected and are
**never scored** — scoring them would re-open **CON-BR2-TYPE**.

---

## 4. `ReferenceMemo` — the anchoring comparison target (Fold-3)

A **U22-owned, hand-authored fixture**: one canonical `DecisionMemo`-shaped exemplar that `anchoring_consistency` scores
against.

| Property | Resolution |
|---|---|
| **Where it lives** | **U22's own fixture module.** **NOT** added to `backend/memo_agent_core/tests/` — that would edit a frozen unit. |
| **Why hand-authored** | No shared/golden memo fixture exists to reuse (U4's tests construct `DecisionMemo` ad-hoc inline; its test tree has no `fixtures.py`). |
| **⚑ Why it needs NO U4 change** | It is a **scoring comparison TARGET held by the judge**, **not** a prompt INPUT. **U4 never sees it.** Feeding exemplars *into* `PromptBuilder` is the forbidden `FEWSHOT-ANCHOR-UNIMPLEMENTED` half; comparing *against* one downstream is U22's own. **The two halves separate cleanly by direction of data flow.** |
| **How it is built** | Via the **imported frozen `DecisionMemo` schema** — instantiating a frozen model is **using** it, not modifying it (import-to-read ≠ edit; ROUTES-1 / Q2-A). |
| **Constraints it inherits** | **Advisory-only wording** (*"recommendation"*, never a bare verdict) and **no demographic identifier** — mirroring U4's `PromptBuilder`, which deliberately omits name/city/gender. |
| **Cardinality** | **One** canonical reference serves the whole fixture set — it is a **style/structure exemplar**, not a per-applicant content twin (QA-4: *"not claimed bit-identical"*). |

---

## 5. `ProviderScopeTag` — the FR-PROV-GATE-2 boundary

A fixed enum tagging each sample's drafting provider, and the **single place** the in-gate/exempt decision is represented.

| Value | Gate status | Grounding |
|---|---|---|
| `gemini` | **IN-GATE** (primary) | FR-PROV-GATE-2 / AC-6 / QA-4 |
| `claude` | **IN-GATE** (secondary, tested) | FR-PROV-GATE-2 / AC-6 / QA-4 |
| `ollama` | **EXEMPT from memo-quality gates ONLY** | FR-PROV-GATE-2; U19 `BR-MEXT-10` |

> **⚑ The exemption is a duty ASSIGNED to U22 by name.** `backend/memo_extensions/tests/test_provgate.py` (frozen, verbatim):
> *"Ollama's ABSENCE from the groundedness/promptfoo target set … is a **tooling-config fact owned by `llm-judge` (U22)**,
> recorded as an **explicit, documented exemption — never implicit, and not asserted here**."* U19 deliberately declined to
> assert it. ⇒ U22 must make it **explicit and non-vacuous** (Fold-2 / `business-rules.md` BR-JUDGE-3).
>
> **Boundary preserved**: Ollama is exempt from **memo-quality** gates *only*. It **still holds the decision-level gates**
> (`temperature=0`, CON-BR2-TYPE) — U19 asserts these for it directly. *"Exempt from scoring"* must **never** be recorded or
> read as *"untested"*.

---

## 6. `DimensionScore` / `SampleScore` — the scoring value objects

**`DimensionScore`** — `dimension_id: str` · `score: int` (**1–5**) · `justification: str` (the judge's stated reason;
**advisory-only wording, no demographic reference**).

**`SampleScore`** — `sample_id: str` · `provider: ProviderScopeTag` · `dimension_scores: list[DimensionScore]` ·
`aggregate: float` (mean of dimension scores) · `passed: bool` (`aggregate >= threshold`) · `in_gate: bool`.

**Determinism**: dimension order follows the rubric's **declared** order; aggregation is a **pure function** of the
dimension scores. Given fixed judge scores, the aggregate, `passed` and the whole report are **byte-reproducible** — which
is what makes the deterministic half fully testable at **tier-U** with no live call (Q4-A).

---

## 7. `EvalRunResult` — the run report artifact

| Field | Type | Meaning |
|---|---|---|
| `rubric_id` | `str` | Which rubric revision produced this. |
| `sample_scores` | `list[SampleScore]` | **All** samples, in deterministic order — **including exempt ones**. |
| `scored_count` | `int` | Count of **in-gate** samples actually scored. |
| `exempt_count` | `int` | Count of samples **present but excluded** from scoring — **the non-vacuity witness** (Fold-2). |
| `aggregate_score` | `float` | Mean aggregate over **in-gate samples only**. |
| `gate_passed` | `bool` | `aggregate_score >= 4`. |
| `tier` | `EvalTier` | `unit` (fixtures) or `live` (the deferred authorized run). |

**⚑ `exempt_count` is load-bearing.** Exempt samples are **retained in `sample_scores` and counted**, never dropped. A run
whose fixture set contained only in-gate samples would report `exempt_count == 0` — which is exactly the **vacuous**
outcome BR-JUDGE-3 forbids.

**Q6-A**: this report is the **only** thing U22 emits. **No Prometheus metric, no new panel** — a sixth would be drift
against `observability`'s frozen five and would break `deploy-config`'s five-panel no-drift scan.

---

## 8. `RubricEngine` — the injected seam (Q3-A)

A **Protocol** (the U21 injected-Protocol pattern), not a concrete binding:

```text
RubricEngine.score(sample: JudgedSample, rubric: GroundednessRubric) -> list[DimensionScore]
```

| Implementation | Tier | Notes |
|---|---|---|
| **Offline deterministic fake** | **tier-U** | Returns fixed, fixture-declared scores. **No Node, no npx, no network, no telemetry, no key, no live LLM.** Drives every tier-U test. |
| **Real promptfoo CLI adapter** | **deferred** | **`PROMPTFOO-CLI-DEFERRED`** — see `business-rules.md` BR-JUDGE-8. |

**This seam is what lets Q4-A hold**: the deterministic half (assembly, scope filtering, aggregation, threshold, report) is
**fully exercised at tier-U**; only the *act of judging* sits behind the seam.

---

## 9. Reference-not-own (explicit)

**Imported read-only, never edited, never re-derived:**

| Shape / artifact | Owner | Use here |
|---|---|---|
| `DecisionMemo`, `MemoDraftOutput`, `CitationValidationResult`, `MissingInformationItem` | **`memo-agent-core` (U4, frozen)** | Read the memo under judgment; construct the reference fixture. **`PromptBuilder` NOT touched.** |
| `RuleResultReport`, `Recommendation`, `Confidence` | **`rules-engine` (frozen)** | The grounding source; the read-only injected values. |
| `ApplicantProfile` | **`intake` (frozen)** | Sample context only — **no demographic field enters any rubric input**. |
| `ClaudeAdapter`, `OllamaAdapter` + the `ProviderAbstraction` seam | **`memo-extensions` (U19, frozen)** | Driven through their **existing** seam; `temperature=0` stays **centrally** fixed in the adapters. |
| `CorpusRecord`, `CorpusManifest` | **`corpus-generator` (`R`)** | **Deferred** — reached only in the live run (`JUDGE-EVAL-DEFERRED`). **tier-B NOT authorized, NOT required for U22's completion** (Q1-A). |
| trace/metric Protocols, the frozen five metrics | **`observability` (U21, frozen)** | **Referenced to justify NON-wiring** (Q6-A). No metric added. |

**Owned by U22 (new here):** `GroundednessRubric` · `RubricDimension` · `JudgedSample` · `ReferenceMemo` (fixture) ·
`ProviderScopeTag` · `DimensionScore` · `SampleScore` · `EvalRunResult` · `EvalTier` · the `RubricEngine` Protocol.

**U22 introduces no change to any frozen shape** — it composes existing ones and adds its own.
