# NFR Requirements — `llm-judge` (U22, EPIC-6, Phase 2)

**Stage**: BUILD → NFR Requirements (per-unit), **Part 2 (Generation)** · **Unit**: U22 `llm-judge` · EPIC-6 · **Phase 2** ·
**Depth**: **standard** (`unit-of-work.md` L249 pin) · **Date**: 2026-07-19 · Story **US-PLAT-10** · QA-4 · AC-2 / AC-6 ·
FR-PROV-GATE-2.
**Built ON** the frozen FD (**`BR-JUDGE-1..11`**; the `GroundednessRubric`/`RubricDimension`/`JudgedSample`/`ReferenceMemo`/
`ProviderScopeTag`/`DimensionScore`/`SampleScore`/`EvalRunResult` domain model; the injected **`RubricEngine`** seam; the
**four mandatory fixture roles**; the **three disclosed register items**) — **re-opening none.**
Answers **Q1–Q3 (all A)** + the NFR-Req folds **NFR-JUDGE-Req-Fold-1..3** (plan §4.5).

**⚑ U22 is the LAST unit in the entire 23-unit decomposition.**

**Tiers**: **tier-U** = fast, deterministic, in CI — **no live LLM, no key, no network, no Docker** (U19's verbatim
taxonomy), **extended here to: no Node, no `npx`, no promptfoo shim import, no telemetry**. **tier-S** = offline smoke
(optional). **tier-B** = **NOT authorized and NOT required** for U22's completion (Q1-A / BR-JUDGE-9). **Every lint/scan
carries a detector self-test** so it can never pass vacuously.

> **No new dependency** (`tech-stack-decisions.md`): `promptfoo` is **already floored** (`requirements.txt` L49,
> `promptfoo>=0.1.0`) — **nothing is added**. But the installed pip package is a **thin Python shim around the Node.js
> promptfoo CLI**, and **the Node engine is ABSENT**. That is an **engine** gap, not a dependency gap, and it is the
> substance of **`PROMPTFOO-CLI-DEFERRED`**.

---

## 1. Finalized `NFR-JUDGE-*` targets — pass/fail assertion · acceptance · tier · rigor

### FULL RIGOR (HIGHEST) — the two LOAD-BEARING targets

#### ⚑ NFR-JUDGE-EXEMPT-1 — the Ollama exemption is explicit **and NON-VACUOUS** (BR-JUDGE-3) — **[LOAD-BEARING]**

> **⚑ Why this one is load-bearing, stated as a mechanism rather than an adjective.** A frozen U19 artifact
> (`backend/memo_extensions/tests/test_provgate.py`) **assigns this duty to `llm-judge` (U22) BY NAME** and **deliberately
> declines to assert it**: *"Ollama's ABSENCE from the groundedness/promptfoo target set (AC-6 / QA-4 / FR-PROV-GATE-2) is a
> **tooling-config fact owned by `llm-judge` (U22)**, recorded as an **explicit, documented exemption — never implicit, and
> not asserted here**."* ⇒ **If U22 does not assert it, NOTHING IN THE BUILD DOES.** And the natural way to "prove" an
> exclusion — run a set with nothing to exclude and observe that nothing was excluded — **passes vacuously**. The load-bearing
> mechanism is therefore **`exempt_count` as a positive witness**: the exemption is proven by something **present and
> counted**, never by an absence.

- **Assertion**: a `{gemini, claude, ollama}` sample set yields **`scored_count == 2`** **AND** **`exempt_count == 1`**
  **AND** the Ollama sample is **PRESENT in `sample_scores`** — retained and counted, **excluded from scoring and from
  `aggregate_score`**. **Exempt ≠ dropped.**
- **Acceptance**:
  - **(a) Positive teeth** — over `in_gate_samples()` **+** `exempt_witness_sample()` (a **three-sample composition**):
    all three assertions above hold together.
  - **(b) Detector self-test** — were the Ollama sample wrongly **scored**, `scored_count` would read **`3`** and the
    assertion **fails**. The detector is therefore non-vacuous by construction.
  - **(c) ⚑ The degenerate-configuration guard** — a set with **`exempt_count == 0`** is **FLAGGED as an invalid/degenerate
    verification configuration**, **never silently accepted as a passing run**. Driven by
    **`degenerate_all_in_gate_set()`** — a **genuinely separate third builder** (Req-Fold-1), **not** an alias of
    `in_gate_samples()`: **distinct `sample_id`s**, **no call into `in_gate_samples()`**, and a **self-asserting
    precondition** (`all(s.provider is not ProviderScopeTag.ollama)`) so the builder **fails at construction** rather than
    the guard silently going vacuous.
  - **(d) Scope of the guard** — this is a **fixture-set validity** assertion about **U22's own verification**, not a claim
    that a production run over a corpus lacking Ollama memos is invalid. It therefore **does not contradict INGATE-1**
    (Req-Fold-1): different function, different level.
- **Tier**: component (teeth) + structural guard. **Rigor**: **full (highest) — LOAD-BEARING**.

#### NFR-JUDGE-NOEDIT-1 / NOMETRIC-1 — U22 edits nothing it judges and emits no metric (BR-JUDGE-11) — **[LOAD-BEARING]**

> **Rigor note (Req-Fold-2)**: promoted from the plan §2 draft's hedged *"load-bearing-style"* to **full (highest)**, to
> conform to the frozen convention — **both** prior units carrying a NOEDIT target designated it outright
> (`NFR-OBS-NOEDIT-1` = full (highest); `NFR-DEP-NOEDIT-1` = **[LOAD-BEARING]**), each with a detector self-test. This
> **raises** rigor and restores `observability`'s exact pairing: one **structural** load-bearing target beside one
> **behavioural** one (there TRACE-1, here EXEMPT-1).

- **Assertion**: **(a)** every path U22 authors is **⊆ its own tree**; **no write** under any frozen `backend/<unit>/` tree
  or `backend/app/**`. **(b)** U22 declares **no** Prometheus metric and **no** dashboard panel — `observability`'s frozen
  **five** `METRIC_DEFINITIONS` and `deploy-config`'s `deploy/grafana-dashboard.json` stay **byte-unchanged**.
- **Acceptance**:
  - **(a) NOEDIT path scan** + **detector self-test** — a synthetic write to a frozen path **must** be flagged.
  - **(b) Static byte-unchanged check** — `backend/observability/metrics.py`'s `METRIC_DEFINITIONS` and
    `deploy/grafana-dashboard.json` are read **read-only** and asserted unchanged. **Neither unit's suite is re-run**
    (plan §3.3): a **static content check**, and **import-to-read ≠ edit** (ROUTES-1 / Q2-A).
  - **(c)** No U22 module declares a metric name ⇒ a sixth metric cannot drift in and break `deploy-config`'s five-panel
    no-drift scan.
- **Tier**: structural. **Rigor**: **full (highest) — LOAD-BEARING**.

### FULL RIGOR

#### NFR-JUDGE-THRESH-1 — the ≥ 4/5 gate, with the boundary asserted explicitly (BR-JUDGE-1)
- **Assertion**: aggregation and the gate are a **pure function** of the dimension scores. A sample **passes** when
  `aggregate >= threshold`; the **run** passes when the mean over **in-gate samples only** is `>= 4`.
- **Acceptance**: **(a)** **`aggregate == 4` PASSES** and **`aggregate == 3.99` FAILS**, with the **`>=` comparison asserted
  explicitly** so the boundary lands on the intended side (the boundary-value discipline the domain rules pin for
  thresholds). **(b)** `gate_passed` computed over the **in-gate mean**, with an exempt sample present and **provably not
  contributing** to it. **(c)** Determinism: fixed dimension scores ⇒ byte-reproducible `aggregate` / `passed` /
  `gate_passed`, dimension order following the rubric's **declared** order.
- **Tier**: component (teeth). **Rigor**: full.

#### NFR-JUDGE-INGATE-1 — Gemini + Claude are in-gate (BR-JUDGE-2 / FR-PROV-GATE-2)
- **Assertion**: `gemini`- and `claude`-tagged samples are **scored** and **counted** toward `aggregate_score` /
  `gate_passed`.
- **Acceptance**: over **`in_gate_samples()`** — `scored_count == 2`, both `in_gate == True`, both present in
  `sample_scores`. **Detector**: a sample wrongly filtered out drops the count ⇒ fails.
- **⚑ Explicitly NOT re-derived**: **FR-PROV-GATE-1**'s decision-level gates (reproducibility 100%, bias-swap delta 0) apply
  to **all three** providers and remain **`quality-gates`' to own**. U22 single-sources **GATE-2 only**.
- **Tier**: component (teeth). **Rigor**: full.

#### NFR-JUDGE-EXEMPTSCOPE-1 — exempt from **memo-quality gates ONLY**, never "untested" (BR-JUDGE-4)
- **Assertion**: the exempt record carries an **explicit reason tag naming *memo-quality*** as the exemption's **scope**; no
  U22 artifact states or implies Ollama is untested.
- **Acceptance**: **(a)** the tag is present and names the scope. **(b)** a scan over every U22 artifact finds **no**
  "untested"-equivalent characterization of Ollama. **(c)** U19's decision-level assertions for Ollama (`temperature=0`,
  CON-BR2-TYPE — asserted directly in frozen `test_provgate.py`) are **REFERENCED, never re-derived**.
- **Tier**: structural + governance. **Rigor**: full.

#### NFR-JUDGE-ANCHOR-1 — anchoring-consistency has **paired** teeth (BR-JUDGE-5 / Q7-A)
- **Assertion**: the **close** fixture scores **high**; the **deliberately-divergent** fixture scores **low**, both against
  the single canonical `reference_memo()`.
- **Acceptance**: **(a)** the pair is driven by **`anchoring_pair()`**, which returns **close and divergent TOGETHER** so
  the pair **cannot be split** (Q1-A). **(b) Detector self-test** — a **single-fixture-only** configuration (close without
  divergent, or vice versa) is **FLAGGED as insufficient**: one fixture alone passes vacuously. **(c)** Per QA-4's *"not
  claimed bit-identical"*, this scores **style/structure adherence**, **not textual identity**. **(d)** The anchoring pair is
  **its own family, NOT overlapped** onto the provider-tagged samples (Q1-A), so a provider-scope edit cannot silently move
  the anchoring baseline.
- **Tier**: component (paired teeth) + detector self-test. **Rigor**: full.

#### NFR-JUDGE-ADVISORY-1 / NOVERDICT-1 — advisory-only; the judge never alters a recommendation (BR-JUDGE-7)
- **Assertion**: the judge **scores prose**. It emits **no** `Recommendation`, no verdict, and **no field capable of carrying
  one** — *"the judge changed the recommendation"* is **structurally unrepresentable**.
- **Acceptance**: **(a) Structural** — no U22 type declares a `Recommendation`-typed (or verdict-typed) field.
  **(b) Token scan** over every U22 artifact for a bare verdict token (`APPROVE` / `REFER` / `DECLINE`) used as a judge
  **output**, **+ detector self-test** (a synthetic verdict-emitting type or token **must** be flagged). **(c)** All rubric
  text, dimension descriptions, justifications and report copy use **"recommendation"** — never a bare "decision".
  **(d)** Only `memo.narrative_prose` (the **`L`** region) is judged; the `D`/`RO`/`M` regions are never scored — scoring
  them would re-open **CON-BR2-TYPE**.
- **Tier**: structural + token scan. **Rigor**: full.

#### NFR-JUDGE-NODEMO-1 — no demographic identifier anywhere (BR-JUDGE-10 / CON-BR1)
- **Assertion**: no demographic identifier enters any rubric input, dimension description, carried sample context,
  justification, report — **or the hand-authored reference memo**.
- **Acceptance**: a **demographic-token scan** over **every U22 artifact AND `reference_memo()`**, **+ detector self-test** —
  a **synthetic demographic token planted in a fixture IS flagged** (proving the scan is non-vacuous). Mirrors U4's
  `PromptBuilder`, which deliberately omits name/city/gender.
- **Tier**: structural + detector self-test. **Rigor**: full.

#### NFR-JUDGE-CLIDEFER-1 — the engine is injected; the real CLI is `PROMPTFOO-CLI-DEFERRED` (BR-JUDGE-8 / Q2-A / Fold-1)
- **Assertion**: scoring is reached **only** through the `RubricEngine` Protocol; at tier-U an **offline deterministic fake**
  drives **every** test. **No promptfoo import, no Node, no npx, no network, no telemetry, no key, no live LLM.**
- **Acceptance**:
  - **(a) Absence teeth** — the whole suite passes with none of the above present.
  - **(b) AST scan** — **no U22 production module imports the promptfoo shim**, **+ detector self-test**.
  - **(c) ⚑ Protocol satisfiability AND non-vacuity (Q2-A)** — `assert isinstance(fake, RubricEngine)` **and**
    `assert not isinstance(object(), RubricEngine)` — **the exact U19 non-vacuity assertion** (`test_signal.py`).
  - **(d) ⚑ NO by-value interop replica now, and this is deliberate (Q2-A).** U19 could replicate U18's `OutlierResult`
    **by value** because that shape is **FROZEN and ON-DISK** — a verifiable target. **For U22 no such target exists**: the
    promptfoo CLI is **absent** and its output shape is **external, version-dependent and unpinned** (an `npx` run-time
    fetch). A by-value replica would attest to an **assumption** — it would pass green while the real interop was broken,
    which is **worse than no test**. ⇒ U22 keeps the **honestly-available half** and **defers the unverifiable half by
    name**.
  - **(e) Discharge criteria** *(documented, NOT run — five)*: Node + npx present · CLI **pinned** · **telemetry opt-out**
    configured · adapter bound · **⚑ real-shape interop verified against the seeded fixtures** (the criterion Q2-A newly
    names). **Requires NO corpus, NO tier-B, NO live provider key.**
- **Tier**: tier-U (**absence** + Protocol teeth) + named deferral. **Rigor**: full.

#### NFR-JUDGE-EVALDEFER-1 — the real ≥4/5 run is `JUDGE-EVAL-DEFERRED` (BR-JUDGE-9 / Q1-A / Fold-1)
- **Assertion**: U22 is **built and verified at tier-U on a seeded fixture set**. **tier-B is NOT authorized and NOT
  required** for U22's completion.
- **Acceptance**: **(a)** the whole suite passes with **tier-B unauthorized and the corpus absent**. **(b)**
  `EvalRunResult.tier` reads **`unit`**. **(c)** **No test reads the real corpus.** **(d) Discharge criteria** *(documented,
  NOT run)*: tier-B corpus authorized + built **AND** live Gemini + Claude keys **AND** ≥ 4/5 actually evaluated over real
  memos — **with `PROMPTFOO-CLI-DEFERRED` discharged FIRST** (the one-way prerequisite).
- **⚑ Distinct from CLIDEFER-1 (Fold-1)**: both are absence proofs, but they assert **different absences** — *no engine
  present* vs *no corpus read* — with **disjoint discharge criteria**. Merging them would **erase the one-way
  prerequisite**. Precedent: `outlier-model` (U18) completed with an `R` corpus edge and *"tier-B NOT authorized (not
  required)"*.
- **Tier**: tier-U (**absence**) + named deferral. **Rigor**: full.

### GOVERNANCE / DOCUMENTATION-PRESENCE

#### NFR-JUDGE-DISCLOSE-1 — `FEWSHOT-ANCHOR-UNIMPLEMENTED` is disclosed by name (BR-JUDGE-6)
- **Assertion**: QA-4's **generation-side** few-shot anchoring is **NOT implemented anywhere in the build** and is **NOT
  implemented here**; U22 **claims no discharge** of it.
- **⚑ What "testable" means here, honestly**: a rule whose entire content is *"this is honestly not implemented"* **has no
  behaviour to exercise** and therefore **cannot** have executable teeth. The established precedent is `deploy-config`'s
  **DOC-1** — a **token-set checklist** matching **tokens, not headings or prose**, with a detector self-test.
- **Acceptance** (mirroring DOC-1): **(a) presence** — the register name **`FEWSHOT-ANCHOR-UNIMPLEMENTED`** appears in U22's
  artifacts **with its owner** (`memo-agent-core` (U4) or a future explicitly-authorized change) **and its rationale**;
  **(b) negative assertion** — **no U22 artifact or report field claims discharge** of the generation-side half;
  **(c) detector self-test** — **removing the disclosure token FAILS** the check.
- **⚑ Distinct from CLIDEFER-1 (Req-Fold-3)** — these are **not one gap under two numbers**. They differ on **content**
  (unimplemented generation mechanism vs absent scoring engine), **owner** (**U4 / future-authorized — never U22's to
  discharge** vs **U22's own seam**), **direction of data flow** (exemplars **INTO** generation vs engine output **OUT OF**
  scoring — Fold-3's axis), and **dischargeability** (**structurally blocked** by the frozen-P1 guardrail vs **merely
  not-yet-done**, touching no frozen unit). **Anti-conflation mechanism**: DISCLOSE-1's token set is keyed to the register
  name **+ U4 owner attribution**; CLIDEFER-1's is keyed to its **five discharge criteria**; **each detector self-test
  asserts the other's tokens do NOT mask its own token's removal.**
- **⇒ Labelled governance/documentation-presence, NOT executable teeth — and labelling it so is HONEST, not a gap**, exactly
  as `deploy-config` labelled BUILD-1/BOOT-1's deploy-time halves *named-not-tested*.
- **Tier**: governance / documentation-presence + detector self-test. **Rigor**: governance (structural teeth on presence).

### SOFT / OBSERVED

#### NFR-JUDGE-PERF-1 — evaluation cost observed, never gated
- **Assertion / Acceptance**: **U22 owns no runtime SLO** — memo-quality evaluation is an **out-of-band quality activity**,
  not a request-path concern. **No hard SLO** (the uniform prior-unit posture); nothing to time at tier-U (the engine is an
  offline fake). Real per-run cost belongs to the deferred authorized run. **No U22 test asserts a timing failure.**
- **Tier**: observed / soft. **Rigor**: soft.

### GOVERNANCE

#### NFR-JUDGE-SEC-1 — scoped exclusions *(not a runtime test)*
- **Statement**: this set tests **only** `llm-judge`'s behavior. It does **not** test other units, the WIRE-1 routes,
  FR-PROV-GATE-1's decision-level gates (**`quality-gates`'**), memo *generation* (**U4's**), the memo hallucination guard
  `validate_citations` (**U4's deterministic guard, which U22 layers on and never replaces**), the real promptfoo engine
  (**deferred**), or the tier-B corpus (**NOT authorized**). U22 **consumes frozen shapes read-only** and introduces **no
  write path**. Enforced by review + the structural scans above.
- **Tier**: N/A (governance).

---

## 2. Traceability — target → `BR-JUDGE` / requirement → tier → rigor (**NO ORPHAN**)

| Target | BR-JUDGE / requirement | Tier | Rigor |
|---|---|---|---|
| **NFR-JUDGE-EXEMPT-1** | **BR-JUDGE-3** · FR-PROV-GATE-2 · U19 `test_provgate.py` (assigned **by name**) · `BR-MEXT-10` · Fold-2 | component + structural | **full (highest) — LOAD-BEARING** |
| **NFR-JUDGE-NOEDIT-1 / NOMETRIC-1** | **BR-JUDGE-11** · Q2-A · Q6-A · `unit-of-work-dependency.md` L200 · U21's frozen five · U23's no-drift scan | structural | **full (highest) — LOAD-BEARING** |
| NFR-JUDGE-THRESH-1 | BR-JUDGE-1 · **AC-6** · QA-4 · US-PLAT-10 b1 · Brief L175 | component (teeth) | full |
| NFR-JUDGE-INGATE-1 | BR-JUDGE-2 · **FR-PROV-GATE-2** · AC-6 · US-PLAT-10 b2 | component (teeth) | full |
| NFR-JUDGE-EXEMPTSCOPE-1 | BR-JUDGE-4 · FR-PROV-GATE-1 (**referenced**) · `BR-MEXT-10` | structural + governance | full |
| NFR-JUDGE-ANCHOR-1 | BR-JUDGE-5 · QA-4 · US-PLAT-10 b3 · Q7-A · Fold-3 | component (paired) + detector | full |
| NFR-JUDGE-ADVISORY-1 / NOVERDICT-1 | BR-JUDGE-7 · advisory-only · **CON-BR2-TYPE** · ADVISORY-1 | structural + token scan | full |
| NFR-JUDGE-CLIDEFER-1 | BR-JUDGE-8 · Q3-A · **Q2-A** · Fold-1 | tier-U (absence + Protocol) + deferral | full |
| NFR-JUDGE-EVALDEFER-1 | BR-JUDGE-9 · Q1-A · Q4-A · U18 precedent · the `R` edge | tier-U (absence) + deferral | full |
| NFR-JUDGE-NODEMO-1 | BR-JUDGE-10 · bias-free · **CON-BR1** | structural + detector | full |
| NFR-JUDGE-DISCLOSE-1 | BR-JUDGE-6 · QA-4 (undischarged half) · CG-JUDGE-GAP-1 · U23 DOC-1 pattern | governance / doc-presence | governance |
| NFR-JUDGE-PERF-1 | (soft perf — U22 owns no runtime SLO) | observed | soft |
| NFR-JUDGE-SEC-1 | governance | N/A | governance |

**No orphaned `BR-JUDGE` rule** — 1→THRESH-1 · 2→INGATE-1 · 3→**EXEMPT-1** · 4→EXEMPTSCOPE-1 · 5→ANCHOR-1 · 6→DISCLOSE-1 ·
7→ADVISORY-1/NOVERDICT-1 · 8→CLIDEFER-1 · 9→EVALDEFER-1 · 10→NODEMO-1 · 11→**NOEDIT-1/NOMETRIC-1**. PERF-1 / SEC-1 cover
cost + governance (carried, not new).

**Story / AC coverage**: **US-PLAT-10** → THRESH-1 (b1) + INGATE-1/EXEMPT-1/EXEMPTSCOPE-1 (b2) + ANCHOR-1 (b3).
**AC-6** (*LLM-as-judge ≥ 4/5*) → THRESH-1 (deterministic half) + EVALDEFER-1 (the deferred live half, **named**).
**AC-2** (*zero unexplained recommendations*) → THRESH-1 + ANCHOR-1 via the **`groundedness`** dimension.
**QA-4** → ANCHOR-1 (the **scoring** half, delivered) + **DISCLOSE-1** (the **generation** half, **disclosed as
unimplemented**) — the two halves separating cleanly by **direction of data flow**.

**Fixture-role → target map (Q1-A, five named families in one shared module)**:
`in_gate_samples()` → INGATE-1 · `exempt_witness_sample()` → EXEMPT-1 (positive) · `degenerate_all_in_gate_set()` →
EXEMPT-1 (negative guard, **separate builder** per Req-Fold-1) · `anchoring_pair()` → ANCHOR-1 (**returned together**) ·
`reference_memo()` → ANCHOR-1 + NODEMO-1.

---

## 3. Security-Guardrails extension — compliance (enabled extension)

`llm-judge` **adds an evaluation harness over already-built units** — a read-only consumer of frozen output shapes with no
write path, no route, and no new emission. The controls are assessed against **exactly** those additions.

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A** | U22 has no application-input surface; it consumes already-typed frozen `DecisionMemo` / `RuleResultReport` values. |
| Prompt-injection defense | **Compliant (deferred surface, disclosed)** | At tier-U **no prompt is built and no LLM runs** (offline fake). The real engine would introduce a judge-prompt surface — that surface arrives **only** with `PROMPTFOO-CLI-DEFERRED`, and is named, not silently assumed safe. |
| Secrets management | **Compliant (referenced)** | Provider keys are **`secrets-config`'s** (SEC-3); **no key is read at tier-U**. U22 hardcodes none and reads none. |
| **Supply-chain / external-tool hygiene** | **Compliant — disclosed** | The promptfoo shim would **`npx`-fetch an unpinned package over the network at run time** and pulls **`posthog` telemetry (7.21.3)** — a BFSI concern. Disclosed in full; **CLI pinning + telemetry opt-out are explicit discharge criteria** (CLIDEFER-1(e)). **No Node/npx/network/telemetry at tier-U.** |
| Read-only / no write path | **Compliant (load-bearing)** | **NOEDIT-1** — U22 persists nothing, reaches no DB, adds no route. Paths ⊆ its own tree; **import-to-read ≠ edit**. |
| Audit logging | **N/A (evaluator, not persister)** | U22 emits its own `EvalRunResult` report artifact; it persists no decision record. |
| Error hygiene (no secret/PII leak) | **Compliant** | No secret present at tier-U to leak; **NODEMO-1** keeps every justification and report field demographic-free. |
| **Bias-free by design (CON-BR1)** | **Compliant (load-bearing)** | **NODEMO-1** — scanned across every artifact **and the hand-authored reference memo**, with a **planted-token detector self-test**. |
| Reproducibility (CON-DET-1) | **Compliant** | Aggregation is a **pure function**; fixtures are seeded and fixed; **no RNG, no wall-clock**. `temperature=0` stays **centrally fixed in U19's frozen adapters** — U22 neither sets nor overrides it. |
| **Advisory-only (human-in-the-loop)** | **Compliant (load-bearing)** | **ADVISORY-1/NOVERDICT-1** — no `Recommendation`-typed field exists, so *"the judge changed the recommendation"* is **structurally unrepresentable**. U22 is **strictly downstream**; nothing feeds back into generation. |
| No LLM in the deterministic rules path | **Compliant** | U22 sits **downstream of the drafted memo**, never inside rule evaluation. |
| Full explainability | **Compliant** | Every `DimensionScore` carries a **`justification`**; the `groundedness` dimension **is** AC-2's *"zero unexplained recommendations"* criterion, layered on U4's deterministic `validate_citations` (**never replacing it**). |
| **Deliverable transparency** | **Compliant (registered ×3)** | **`PROMPTFOO-CLI-DEFERRED`** · **`JUDGE-EVAL-DEFERRED`** · **`FEWSHOT-ANCHOR-UNIMPLEMENTED`** — all three **named, owner-attributed, and disclosed**, never quietly assumed done. **⚑ U22 claims no discharge of any of them.** |

**No blocking finding.** Every applicable guardrail is compliant; the N/A determinations are stated with rationale above.

---

## 4. Settled items held (not re-opened)

- The **frozen FD** (`BR-JUDGE-1..11` + the domain model + the `RubricEngine` seam + the four fixture roles + the three
  register items) is the substrate. **CG-JUDGE-Fold-1..3** and **CG-JUDGE-GAP-1** stand as resolved/disclosed.
- **Q1-A** — **one shared `fixtures.py`** with **five deliberately-separate named families** (the exact U18/U19 convention);
  the **anchoring pair is NOT overlapped** onto the provider-tagged samples; **Req-Fold-1** pins
  `degenerate_all_in_gate_set()` as a **genuinely separate, self-asserting third builder**.
- **Q2-A** — **no by-value interop replica**; satisfiability **+** non-vacuity only; **real-shape interop is a named
  CLIDEFER-1 discharge criterion**. **Req-Fold-3** keeps DISCLOSE-1 and CLIDEFER-1 non-interchangeable.
- **Q3-A** — **`--cov=backend/llm_judge`, NO omit** (`observability` precedent verbatim); the global
  **`--cov-fail-under=90` holds unchanged**; **BR-JUDGE-6/8/9's verification is the presence/absence scans, orthogonal to
  line coverage** — the number must **not** be read as covering them. See `tech-stack-decisions.md`.
- **Req-Fold-2** — **NOEDIT-1/NOMETRIC-1 promoted to full (highest) / LOAD-BEARING**, conforming to the frozen NOEDIT
  convention and restoring the structural+behavioural load-bearing pairing.
- **Deferred to NFR Design / Code-Gen**: the exact module layout under `backend/llm_judge/`; the fake engine's precise
  surface; the exact scan token sets (DISCLOSE-1's and CLIDEFER-1's, finalized there); the `pyproject.toml` `--cov` line's
  placement and note wording.
- **Deferred by name (NOT discharged here)**: **`PROMPTFOO-CLI-DEFERRED`** · **`JUDGE-EVAL-DEFERRED`** ·
  **`FEWSHOT-ANCHOR-UNIMPLEMENTED`**.
- **Untouched**: **WIRE-1** · the **17 frozen P1 units (INCLUDING `memo-agent-core`)** · `outlier-model` (U18) ·
  `memo-extensions` (U19) · `ui-outlier-view` (U20) · `observability` (U21) · `deploy-config` (U23) · the **CLOSED
  composition root** · **tier-B (NOT authorized)** · the **`audit_store` Docker-guard gap** (31 skips + 5 Docker errors to
  stay unchanged) · the **23-unit decomposition**.
