# NFR Requirements Plan (Part 1) — `llm-judge` (EPIC-6 / U22, Phase 2)

**Phase / Stage**: BUILD → per-unit loop → **NFR Requirements, Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `llm-judge` (U22) · **FD ✅ (approved 2026-07-19)** → **NFR Requirements ← here (the 2nd of U22's 5 stages)**
**Unit**: U22 · EPIC-6 · **Phase 2** · **Date**: 2026-07-19 · **Depth**: **standard** (consistent with the FD decision, per
`unit-of-work.md` L249's explicit pin)
**Status**: **Plan — awaiting `[Answer]:` tags. NO NFR artifact generated; no code; no files beyond this plan.**

Built **ON** the frozen FD — **`BR-JUDGE-1..11`**, the `GroundednessRubric`/`RubricDimension`/`JudgedSample`/`ReferenceMemo`/
`ProviderScopeTag`/`DimensionScore`/`SampleScore`/`EvalRunResult` domain model, the **injected `RubricEngine` seam**, the
**four mandatory fixture roles**, and the **three disclosed register items** — **re-opening none of it**.

**⚑ U22 is the LAST unit in the entire 23-unit decomposition.**

---

## 1. Tier convention (inherited verbatim — not re-derived)

**tier-U** = fast, deterministic, in CI — **no live LLM call, no key, no network, no Docker** (U19's verbatim taxonomy),
**extended here to: no Node, no `npx`, no promptfoo shim import, no telemetry**. **tier-S** = offline smoke (optional).
**tier-B** = **NOT authorized** and **NOT required** for U22's completion (Q1-A / BR-JUDGE-9).
**Every lint/scan carries a detector self-test** so it can never pass vacuously (the established convention).

---

## 2. `BR-JUDGE-*` → draft `NFR-JUDGE-*` target map (all 11 mapped — NO ORPHAN)

| BR | Draft target | Tier / rigor | Pass/fail teeth |
|---|---|---|---|
| **BR-JUDGE-1** | **THRESH-1** | tier-U, **standard** | Aggregation + gate arithmetic is a **pure function**. Teeth: **`aggregate == 4` PASSES** and **`aggregate == 3.99` FAILS**, with the **`>=` comparison asserted explicitly** (the boundary-value discipline the domain skill pins for thresholds). Plus `gate_passed` over the in-gate mean. |
| **BR-JUDGE-2** | **INGATE-1** | tier-U, standard | A `{gemini, claude}` fixture set yields `scored_count == 2`, both `in_gate == True`, both present in `sample_scores`. **Detector**: a sample wrongly filtered out drops the count → fails. |
| **BR-JUDGE-3** | **⚑ EXEMPT-1 — LOAD-BEARING** | tier-U, **full-highest** | `{gemini, claude, ollama}` → `scored_count == 2` **AND** `exempt_count == 1` **AND** the Ollama sample **present** in `sample_scores`. **⚑ The degenerate-configuration guard**: an **all-in-gate fixture set yielding `exempt_count == 0` is FLAGGED as an invalid/degenerate test configuration — never silently accepted as a passing run.** **Detector self-test**: were the Ollama sample wrongly scored, `scored_count` reads `3` → fails. |
| **BR-JUDGE-4** | **EXEMPTSCOPE-1** | tier-U, standard | The exempt record carries an **explicit reason tag naming *memo-quality*** as the exemption's scope; a scan asserts **no U22 artifact states or implies Ollama is untested**. U19's decision-level assertions are **referenced, never re-derived**. |
| **BR-JUDGE-5** | **ANCHOR-1** | tier-U, **standard (paired)** | The **close** fixture scores **high**; the **divergent** fixture scores **low**. **⚑ Detector self-test**: a **single-fixture-only** configuration (close without divergent, or vice versa) is **FLAGGED as insufficient** — the pair is mandatory, because one fixture alone passes vacuously. |
| **BR-JUDGE-6** | **DISCLOSE-1** | **governance / documentation-presence** | See **§3.1** — this rule's entire content is *"this is honestly not implemented"*. Proposed: a **token/section-presence check** mirroring `deploy-config`'s **DOC-1**, plus a **negative assertion** that U22 claims no discharge. **No executable teeth** — and that is honest, not a gap. |
| **BR-JUDGE-7** | **ADVISORY-1 / NOVERDICT-1** | tier-U, **structural + token** | **(a) Structural**: no U22 type declares a `Recommendation`-typed (or verdict-typed) field ⇒ *"the judge changed the recommendation"* is **unrepresentable**. **(b) Token scan** over every U22 artifact for a bare verdict token (`APPROVE`/`REFER`/`DECLINE`) used as a judge **output**, with a **detector self-test** (a synthetic verdict-emitting type/token is flagged). |
| **BR-JUDGE-8** | **CLIDEFER-1** | tier-U (**absence**) + named deferral | **Distinct acceptance from BR-JUDGE-9** (Fold-1). tier-U teeth: the suite passes with **no promptfoo import, no Node, no npx, no network**; an **AST scan** asserts no U22 production module imports the promptfoo shim (detector self-test). **Discharge criteria (documented, not run)**: Node+npx present · CLI **pinned** · **telemetry opt-out** configured · adapter bound · **verified against the seeded fixtures**. **Needs NO corpus, NO tier-B, NO live key.** |
| **BR-JUDGE-9** | **EVALDEFER-1** | tier-U (**absence**) + named deferral | **Distinct acceptance from BR-JUDGE-8.** tier-U teeth: the whole suite passes with **tier-B unauthorized and the corpus absent**; `EvalRunResult.tier == "unit"`; **no test reads the real corpus**. **Discharge criteria (documented, not run)**: tier-B corpus authorized + built **AND** live Gemini+Claude keys **AND** ≥4/5 evaluated over real memos — **with CLIDEFER-1 discharged first** (the one-way prerequisite). |
| **BR-JUDGE-10** | **NODEMO-1** | tier-U, standard | Demographic-token scan over **every U22 artifact and the hand-authored reference memo**. **Detector self-test**: a synthetic demographic token planted in a fixture **is flagged** (proving the scan is non-vacuous). |
| **BR-JUDGE-11** | **NOEDIT-1 / NOMETRIC-1** | tier-U, **load-bearing-style** | **(a)** NOEDIT-style **path scan** — U22-authored paths ⊆ its own tree; **no write** under any frozen `backend/<unit>/` tree or `backend/app/**`; **detector self-test** (synthetic frozen-path write flagged). **(b)** **Static byte-unchanged check** — `observability`'s frozen five `METRIC_DEFINITIONS` and `deploy-config`'s `deploy/grafana-dashboard.json` read **read-only** and asserted unchanged; **U22 declares no metric name**. **Neither unit's suite is re-run** (a static content check, per the standing instruction). |

**Also carried (from the FD, not new)**: **AC-2** (*zero unexplained recommendations*) rides on THRESH-1 + the `groundedness`
dimension; **PERF** — U22 owns **no runtime SLO** (an out-of-band quality activity), proposed **observed-never-gated**, folded
into the governance target as prior units did.

---

## 3. The four called-out clarifications

### 3.1 What "testable" means for **BR-JUDGE-6** (`FEWSHOT-ANCHOR-UNIMPLEMENTED`)
A rule whose entire content is *"this is honestly not implemented"* **cannot** have executable teeth — there is no behaviour
to exercise. The **established precedent is `deploy-config`'s DOC-1**: a **token-set checklist** asserting the required
literal anchors are present in the doc, matching the **token set, not headings/prose**, with a **detector self-test** (a
removed token is flagged). Proposed for DISCLOSE-1, mirroring it:
- **(a) presence**: the register item **`FEWSHOT-ANCHOR-UNIMPLEMENTED`** appears by name in U22's artifacts with its owner
  (`memo-agent-core` / a future explicitly-authorized change) and its rationale;
- **(b) negative assertion**: **no U22 artifact or report field claims discharge** of the generation-side half;
- **(c) detector self-test**: removing the disclosure token **fails** the check.
⇒ **Governance/documentation-presence, not executable teeth** — and labelling it so is **honest**, exactly as
`deploy-config` labelled BUILD-1/BOOT-1's deploy-time halves *named-not-tested*.

### 3.2 BR-JUDGE-8 vs BR-JUDGE-9 — **separate acceptance criteria** (Fold-1 confirmed)
Their tier-U teeth are both **absence** proofs, but they assert **different absences** and their **discharge criteria are
disjoint**: CLIDEFER-1 is about **no engine present** (no Node/npx/import) and discharges **without any corpus**;
EVALDEFER-1 is about **no corpus read** (tier-B unauthorized) and discharges **only after** CLIDEFER-1. Modelling them as one
target would **erase the one-way prerequisite** that Fold-1 established. ⇒ **Two targets.**

### 3.3 BR-JUDGE-11's byte-unchanged check
A **static read-only content check** of `backend/observability/metrics.py`'s `METRIC_DEFINITIONS` and
`deploy/grafana-dashboard.json` — **no re-run of either unit's suite**, per the standing instruction. Reading a frozen file
to assert it is unchanged is **import-to-read ≠ edit** (settled by ROUTES-1 / Q2-A).

### 3.4 Fixture-role note feeding Q1
The FD pins **four mandatory fixture roles**, but they are **not four disjoint samples**: the **close/divergent anchoring
pair** may **overlap** the provider-tagged samples (e.g. the `gemini` sample could double as the *close* fixture) **or** be
additional. This is a real modelling choice with a real consequence for whether ANCHOR-1 and EXEMPT-1 can interfere — **Q1**.

---

## 4. Clarifying questions — fill each `[Answer]:` tag

> **I will not improvise on any of these.** Each is a genuine fork. **C/D "Other"** — describe after the tag.

---

### Question 1 — One shared fixture module, or dedicated non-overlapping fixtures per target?

**Grounding measured on disk**: **both** cited precedents use **ONE shared `fixtures.py` per unit** —
`backend/outlier_model/tests/fixtures.py` and `backend/memo_extensions/tests/fixtures.py` — **but each contains
deliberately-separate, purpose-built NAMED FAMILIES**. U18's module exposes `normal_corpus_profiles()`,
`typical_profile()`, **`missing_optional_profile()`**, **`swap_pair()`** (bias-swap only) and **`outlier_profile()`**
(threshold only) — one module, distinct families, **no family reused across targets whose failure modes differ**.

**A) ONE shared `fixtures.py` with deliberately-separate NAMED FAMILIES per target — the exact U18/U19 convention
(RECOMMENDED).**
A single module exposing distinct builders: `in_gate_samples()` (gemini + claude) · **`exempt_witness_sample()`** (the
Ollama sample — its own family, so EXEMPT-1 can never be weakened by another target's edits) · **`anchoring_pair()`**
(close + divergent, returned **together** so ANCHOR-1's pair cannot be split) · `reference_memo()` (the single canonical
exemplar) · `degenerate_all_in_gate_set()` (the **negative** fixture EXEMPT-1's degenerate-configuration guard needs).
**The anchoring pair is its own family, NOT overlapped onto the provider-tagged samples** — so a change made for a
provider-scope test cannot silently alter what "close" and "divergent" mean.

**B) Fully separate fixture modules per target** (e.g. `fixtures_exempt.py`, `fixtures_anchor.py`). *(Available; but it
diverges from the one-module convention every prior unit followed, and duplicates the shared builders.)*

**C) One shared module with the anchoring pair OVERLAPPED onto the provider-tagged samples** (the `gemini` sample doubles
as *close*). *(Available and fewer fixtures; but it couples ANCHOR-1 to INGATE-1/EXEMPT-1 — a provider-scope edit would
silently change the anchoring baseline. Rejected as the default for that reason.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 2 — Does the `RubricEngine` offline fake need an interop check against the real promptfoo output shape?

**⚑ The cited precedent is real, and I re-read it — but it differs in one decisive respect.**
`backend/memo_extensions/tests/test_signal.py` **does** carry an interop self-test:
`test_interop_by_value_u18_outlier_result_satisfies_protocol` — *"A real U18 `OutlierResult` **SHAPE**, constructed **BY
VALUE (never imported)**, carrying the extra prose/trace fields — still satisfies the narrow `OutlierSignal` Protocol"* —
with `assert isinstance(by_value, OutlierSignal)` **plus a non-vacuity assertion**
`assert not isinstance(object(), OutlierSignal)`.

**The decisive difference**: U19 could replicate U18's shape **by value** because **U18's `OutlierResult` is a FROZEN,
ON-DISK shape** — a known, verifiable target. **For U22 there is no such target**: the promptfoo CLI **is absent**, its
output shape is **external, version-dependent, and unpinned** (an `npx` run-time fetch). Replicating it "by value" would be
replicating an **assumed** shape, not a verified one — manufacturing **false confidence** that the seam is interop-proven.

**A) NO by-value interop check now; the fake proves the Protocol is satisfiable and NON-VACUOUS, and real-shape interop is
part of the `PROMPTFOO-CLI-DEFERRED` discharge (RECOMMENDED).**
U22 keeps the **half of the precedent that is honestly available**: `assert isinstance(fake, RubricEngine)` (satisfiable)
**and** `assert not isinstance(object(), RubricEngine)` (**non-vacuous** — the exact U19 assertion). It **omits** the
by-value replica, because the precedent's **precondition — a frozen on-disk shape to mirror — is absent**. **Real-shape
interop becomes an explicit, named criterion of CLIDEFER-1's discharge** ("the adapter satisfies `RubricEngine` against the
real CLI's actual output"). Honest: the seam is proven **satisfiable and discriminating**, and the unverifiable half is
**deferred by name** rather than faked.

**B) Add a by-value replica of promptfoo's documented output shape now** — mirror the published schema as a fixture and
assert it satisfies the Protocol. *(Available; but the shape is unpinned and unverifiable offline, so a green test would
attest to an **assumption**. If the real CLI's shape differs, the test passes while the interop is broken — worse than no
test.)*

**C) Defer the entire Protocol check** (not even satisfiability/non-vacuity at tier-U). *(Rejected — it discards the half
that IS honestly verifiable, and would let the seam pass vacuously.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 3 — What does "coverage" mean for this hybrid unit?

U22 is **not** `deploy-config`: it has **real production Python** (rubric definition, scope-filtering, aggregation,
threshold arithmetic, report assembly) — genuinely unit-coverable. But three of its rules (**BR-JUDGE-6, 8, 9**) are
**disclosure/deferral** content with **no production module**.

**Grounding measured on disk** (`pyproject.toml`): every pure-logic unit adds its own `--cov=backend/<unit>` with the
standing note *"No omit — the unit is pure logic, fully unit-coverable"*. **`observability` is the exact precedent for the
hybrid case**: it added **`--cov=backend/observability`** with *"No omit — the unit is pure logic, fully unit-coverable
(**no live-SDK/subprocess/network module at tier-U**)"* — **even though its live SDK binding was deferred
(`OBS-SINK-DEFERRED`)**. `deploy-config` added **no** line only because it had **no production `.py` at all`.

**A) Add `--cov=backend/llm_judge`, NO omit — following `observability` verbatim (RECOMMENDED).**
The deferred halves are **absent modules, not uncovered ones**: no promptfoo adapter and no live-run module is written at
this stage, so there is **nothing uncoverable to omit**. Every production line U22 ships is tier-U-reachable through the
injected fake. The global **`--cov-fail-under=90` holds unchanged**, and U22's tree is expected at **100%** like its
pure-logic siblings. **BR-JUDGE-6/8/9 are governance/deferral targets — their verification is the presence/absence scans,
which is orthogonal to line coverage** and is stated as such so the number is not mistaken for covering them.

**B) Add the `--cov` line with an `omit` for the deferral-related modules.** *(Rejected under A's reasoning — there are no
such modules to omit; adding a speculative omit would pre-authorize an uncovered module that does not exist.)*

**C) Add no `--cov` line** (the `deploy-config` treatment). *(Rejected — U22 has real production logic; omitting it would
leave genuine code outside QA-6, weakening the gate.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

## 4.5 Mandatory ambiguity-check (RAN against Q1-A / Q2-A / Q3-A + the frozen FD) — **CLEAN**

**Ran**: 2026-07-19 · **Result**: **CLEAN — 3 folds RESOLVED, no genuine gap, no surface-and-stop.** Checked against
`BR-JUDGE-1..11`, the frozen domain model, the `RubricEngine` seam, the four fixture roles, the three register items, and the
§2/§3 draft target map. **One correction to §2's draft rigor labelling** is carried by Fold-2 (below) — flagged, not silent.

---

### ⚑ NFR-JUDGE-Req-Fold-1 [check (i)] — RESOLVED: `degenerate_all_in_gate_set()` **must** be a genuinely separate third builder

**The question is real.** By *content* alone, "a sample set with no exempt sample" and "the in-gate family" are
co-satisfiable today — so aliasing `degenerate_all_in_gate_set()` to `in_gate_samples()` would be *currently* correct. It is
still **wrong**, for a reason that is structural rather than incidental:

**The two families are defined by DIFFERENT INVARIANTS that merely coincide right now.**

| Builder | Its declared invariant | Its role |
|---|---|---|
| `in_gate_samples()` | *"contains a `gemini` sample and a `claude` sample"* | INGATE-1's **positive** fixture |
| `degenerate_all_in_gate_set()` | *"contains NO exempt-tagged sample ⇒ `exempt_count == 0`"* | EXEMPT-1's **negative** fixture |

A builder whose contract is *"has gemini and claude"* says **nothing** about whether an exempt sample is absent — that
absence is incidental to it and load-bearing for the other. Q1-A's own stated principle (*"its own family, so EXEMPT-1 can
never be weakened by another target's edits"*) applies here **verbatim**, and U18's frozen precedent is the same shape:
`swap_pair()` is bias-only and `outlier_profile()` is threshold-only, **deliberately not reused** across targets whose
failure modes differ.

**⚑ The accidental-satisfaction risk the check asked about — and the mechanism that forecloses it.** Note first that
EXEMPT-1's **positive** fixture is itself a **third composition** (`in_gate_samples()` **+** `exempt_witness_sample()`), so
three set-level fixtures exist, not two. The anti-conflation mechanism, pinned here so Code-Gen cannot drift:
1. **Distinct `sample_id`s** — the degenerate set's samples carry their own ids, so the two sets are **never identity-equal**
   and no test can pass by reading the wrong one;
2. **A self-asserting builder** — `degenerate_all_in_gate_set()` asserts its **own precondition** internally
   (`all(s.provider is not ProviderScopeTag.ollama)`), so if a future edit ever introduced an exempt sample into it, the
   **builder** fails at construction rather than the guard silently becoming vacuous;
3. **No aliasing** — it does **not** call `in_gate_samples()`; a provider-scope edit therefore cannot move the negative
   fixture's meaning.

**⚑ And the two targets do not contradict each other**, which is the deeper form of the question: INGATE-1 asserts the
**scope-filter** scores both in-gate samples (true, and correct); EXEMPT-1's guard asserts the **run-validity check** flags a
set with `exempt_count == 0` as a **degenerate verification configuration**. Different function, different level — a
*fixture-set validity* assertion about U22's own verification, **not** a claim that a production run over a corpus lacking
Ollama memos is invalid. Both hold simultaneously. **No user decision needed.**

---

### ⚑ NFR-JUDGE-Req-Fold-2 [check (ii)] — RESOLVED: EXEMPT-1's designation is **correct**; the inconsistency is **next door**, at NOEDIT-1

**EXEMPT-1 alone at full-highest is NOT a labelling inconsistency.** Measured against the frozen precedents:
- **Count** — `observability` carried **two** full-highest (`NFR-OBS-NOEDIT-1` · `NFR-OBS-TRACE-1`); `deploy-config` carried
  **three** (`NOEDIT-1` · `SEC3-1` · `ROUTES-1`). **One or two per unit** is the band, and U22 is inside it.
- **Behavioural full-highest is precedented** — the objection *"full-highest is usually a structural scan"* does not hold:
  **`NFR-OBS-TRACE-1` is `component (teeth) + structural` at full (highest)**. `deploy-config`'s three are all scans only
  because it is a declarative unit with **no production Python to exercise**. U22 has real logic, so a behavioural
  load-bearing target is the *right* shape, and EXEMPT-1 additionally carries a structural clause (the degenerate-set guard)
  inside itself — the same hybrid TRACE-1 has.

**⚑ But the check surfaced a real inconsistency one target over.** §2 designates BR-JUDGE-11's target
**NOEDIT-1 / NOMETRIC-1** as *"load-bearing-**style**"* — a hedge that appears in **no** prior unit. Both units that carried
a NOEDIT target designated it outright: `NFR-OBS-NOEDIT-1` = **full (highest)**, `NFR-DEP-NOEDIT-1` = **[LOAD-BEARING]**,
each with a detector self-test. A hedged label at U22 — the unit with the **most** frozen trees adjacent to it — would be a
**downward** drift against a frozen convention.

**⇒ Correction carried into Part 2**: **NOEDIT-1 / NOMETRIC-1 is promoted to `full (highest)` · LOAD-BEARING.** This
restores `observability`'s **exact** pairing — one **structural** load-bearing target (NOEDIT) alongside one **behavioural**
load-bearing target (there TRACE-1, here EXEMPT-1) — which is precisely the paired-scan shape the check expected to find.
The change **raises** rigor and conforms to precedent; it is **flagged here, not applied silently**, and is reversible at the
stage gate. **No user decision needed to proceed.**

---

### ⚑ NFR-JUDGE-Req-Fold-3 [check (iii)] — RESOLVED: DISCLOSE-1 and CLIDEFER-1's deferred-interop half are **genuinely distinct**

Both are *"honestly disclose an undelivered thing"*, so the check is warranted. They separate on **four independent axes** —
this is **not** one gap under two rule numbers:

| | **BR-JUDGE-6 → DISCLOSE-1** | **BR-JUDGE-8 → CLIDEFER-1** (interop half, Q2-A) |
|---|---|---|
| **Content** | QA-4's **generation-side few-shot anchoring** is unimplemented **build-wide** (repo scan: zero hits) | the **real rubric engine is absent**, so its **output shape** cannot be interop-verified offline |
| **Owner** | **`memo-agent-core` (U4)** or a future explicitly-authorized change — **never U22's to discharge** | **U22 / whoever discharges the CLI item** — U22's own seam |
| **Direction of data flow** (Fold-3's axis) | exemplars **INTO** generation | engine output **OUT OF** scoring |
| **Dischargeability** | **structurally blocked** by the frozen-P1 guardrail — needs its own separate authorization | **merely not-yet-done** — install/pin Node CLI, bind adapter, verify on U22's seeded fixtures. **Touches no frozen unit.** |

The second row is decisive: **one is not U22's to fix at all; the other is U22's and is blocked only by an absent external
tool.** Collapsing them would erase that ownership distinction exactly as merging BR-JUDGE-8/9 would have erased Fold-1's
one-way prerequisite.

**⚑ One real interaction, pinned so Part 2 cannot let them drift together.** Because both are verified by
**presence checks over U22's artifacts**, their token sets could converge and let one satisfy the other. Mechanism:
- **DISCLOSE-1's** token set is keyed to the register name **`FEWSHOT-ANCHOR-UNIMPLEMENTED` + its U4 owner attribution**;
- **CLIDEFER-1's** record is keyed to its **five discharge criteria** (Node+npx · pinned CLI · telemetry opt-out · adapter
  bound · **real-shape interop verified** — the criterion Q2-A newly names);
- **each carries its own detector self-test**, and each self-test asserts the **other's** tokens being present does **not**
  mask its own token's removal. Non-interchangeable by construction.

**No user decision needed.** ⇒ **Ambiguity-check CLEAN. Part 2 generated.**

---

## 5. Explicit HOLDS for Part 2

- **No NFR artifact until all `[Answer]:` tags are filled**, followed by the **mandatory ambiguity-check**, **surfacing-and-
  stopping** on any genuine gap rather than improvising.
- **No code**; **no `backend/llm_judge/`**; **no promptfoo config**; **no live eval run**; **`requirements.txt` NOT edited**
  (promptfoo already floored); **`pyproject.toml` NOT edited at this stage** (Q3 decides the Code-Gen-time line).
- **The frozen FD re-opened NONE** — `BR-JUDGE-1..11`, the domain model, the `RubricEngine` seam, the four fixture roles and
  the three register items are **built ON, not revised**.
- **WIRE-1 untouched · the 17 frozen P1 units untouched (INCLUDING `memo-agent-core`) · `outlier-model` (U18) ·
  `memo-extensions` (U19) · `ui-outlier-view` (U20) · `observability` (U21) · `deploy-config` (U23) untouched · the CLOSED
  composition root untouched · tier-B NOT authorized · the `audit_store` Docker-guard gap untouched · no other unit
  started · the 23-unit decomposition unchanged.**
- **Domain invariants bind**: advisory-only wording; the judge never alters a recommendation; no LLM in the deterministic
  rules path; `temperature=0` centrally fixed in U19's frozen adapters (U22 neither sets nor overrides it); no demographic
  identifier anywhere.

---

## 6. Next step (STOP here)

Fill the three `[Answer]:` tags in §4. On your signal I will read the answers, run the mandatory ambiguity-check, **embed
the full Q&A in this plan file**, and generate **Part 2** — `nfr-requirements.md` (the finalized `NFR-JUDGE-*` targets with
acceptance/tier/rigor) + `tech-stack-decisions.md` — then present the standardized 2-option completion message.
**No NFR artifact is generated until the answers are in and checked.** This is the **2nd of U22's 5 stages**, and U22 is the
**LAST unit in the 23-unit decomposition**.
