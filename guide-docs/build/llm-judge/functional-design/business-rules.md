# Business Rules — `llm-judge` (EPIC-6 / U22, Phase 2)

**Stage**: BUILD → per-unit loop → **Functional Design, Part 2 (Generation)** · **Depth**: **standard** (Q5-A) ·
**Date**: 2026-07-19
**`BR-JUDGE-1..11`** — each **grounded** (traced to a frozen source) and **checkable** (states how it is verified, and at
which tier). Built ON the frozen U4 / U19 / U21 contracts — **re-opening none**.

---

## BR-JUDGE-1 — The groundedness gate is **≥ 4 of 5**

The rubric scores each in-gate sample on a **1–5** scale; a sample **passes** when its aggregate is **≥ 4**. The **run**
passes when the mean aggregate over **in-gate samples only** is **≥ 4**.

- **Grounded**: AC-6 (*"LLM-as-judge score ≥ 4/5"*) · QA-4 · `PROJECT-BRIEF.md` L175 · US-PLAT-10 bullet 1.
- **Checkable** *(tier-U)*: with fixture-declared dimension scores, aggregation and the pass/fail boundary are a **pure
  function** — including the **exact boundary cases** `aggregate == 4` (**pass**) and `aggregate == 3.99` (**fail**). The
  comparison is **`>=`**, stated explicitly so the boundary lands on the intended side.

---

## BR-JUDGE-2 — Memo-quality gating applies to **Gemini + Claude** (in-gate)

Samples tagged `gemini` or `claude` are **scored** and **counted** toward `aggregate_score` / `gate_passed`.

- **Grounded**: **FR-PROV-GATE-2** (`requirements.md` L168) · AC-6 (L237) · QA-4 (L206) · U19 `BR-MEXT-10`.
- **Checkable** *(tier-U)*: a fixture set containing both providers yields `scored_count == 2`; both appear in
  `sample_scores` with `in_gate == True`.
- **Explicitly NOT re-derived**: **FR-PROV-GATE-1**'s decision-level gates (reproducibility 100%, bias-swap delta 0) apply
  to **all three** providers and are **`quality-gates`' to own**. U22 **single-sources GATE-2 only**.

---

## BR-JUDGE-3 — **Ollama is exempt from memo-quality gates, and the exemption must be NON-VACUOUS**

An `ollama`-tagged sample is **present in the assembled sample set** and **retained in `sample_scores`**, but is
**excluded from scoring and from `aggregate_score`**, and is **counted in `exempt_count`**.

**⚑ The fixture set MUST contain at least one Ollama-sourced sample.** A fixture set of only in-gate samples would prove the
exclusion **vacuously** — nothing present to exclude.

- **Grounded**: **a frozen U19 artifact assigns this duty to U22 BY NAME** —
  `backend/memo_extensions/tests/test_provgate.py`, verbatim: *"Ollama's ABSENCE from the groundedness/promptfoo target set
  (AC-6 / QA-4 / FR-PROV-GATE-2) is a **tooling-config fact owned by `llm-judge` (U22)**, recorded as an **explicit,
  documented exemption — never implicit, and not asserted here**."* U19 **deliberately declined** to assert it. Also
  FR-PROV-GATE-2 · U19 `BR-MEXT-10`.
- **Checkable** *(tier-U, with real teeth — the SEC3-1 non-vacuity discipline)*: with a fixture set of
  `{gemini, claude, ollama}` → `scored_count == 2` **and** `exempt_count == 1` **and** the Ollama sample is **present** in
  `sample_scores`; **and** a **detector self-test** — were the Ollama sample wrongly scored, `scored_count` would read `3`
  and the assertion fails. **`exempt_count == 0` is itself a failure signal** (vacuous set).

---

## BR-JUDGE-4 — Ollama's exemption is from **memo-quality gates ONLY** — never from the decision-level gates

*"Exempt from scoring"* must **never** be recorded, rendered, or read as *"untested"*. Ollama **holds** `temperature=0` and
**CON-BR2-TYPE** identically.

- **Grounded**: U19 `BR-MEXT-10` (*"exempt from memo-quality gates; **held to decision-level gates**"*) ·
  `test_provgate.py` (*"'Wired-only' != untested code"*) · FR-PROV-GATE-1.
- **Checkable** *(tier-U)*: U22's exempt record carries an **explicit reason tag** naming *memo-quality* as the scope of the
  exemption; no artifact asserts or implies Ollama is untested. **U19 already asserts the decision-level gates for Ollama
  directly** — U22 **references, never re-derives** them.

---

## BR-JUDGE-5 — Anchoring-consistency is a **scored dimension**, compared against a **U22-owned reference memo**

`anchoring_consistency` scores whether a memo's **wording and structure** are consistent with the reference memo. Per QA-4
this is **"not claimed bit-identical"** — it scores **style/structure adherence**, not textual identity. **One canonical
reference** serves the whole fixture set; it is **not** a per-applicant content twin.

- **Grounded**: QA-4 (`requirements.md` L206) · US-PLAT-10 bullet 3 (`stories.md` L622) · **Q7-A** · **CG-JUDGE-Fold-3**.
- **Checkable** *(tier-U, with real teeth)*: a **close** fixture scores **high**; a **deliberately-divergent** fixture
  scores **low**. The pair is mandatory — a single close fixture would pass vacuously.

---

## BR-JUDGE-6 — ⛔ The **generation-side** few-shot anchoring is **NOT delivered here** — `FEWSHOT-ANCHOR-UNIMPLEMENTED`

QA-4's anchoring clause has **two halves**. U22 delivers the **scoring** half (BR-JUDGE-5). The **generation** half —
supplying few-shot exemplars to the memo prompt so the draft is anchored **at draft time** — is **NOT implemented anywhere
in the build** and is **NOT implemented here**.

- **Grounded / measured**: a repo-wide scan of `backend/**/*.py` for `few.?shot|reference_memo|reference memo` returns
  **ZERO HITS**. U4's frozen `PromptBuilder` builds the prompt from `MemoAgentInput` **and nothing else** — no reference
  memo, no exemplars. The clause exists only in `requirements.md` L206 and `stories.md` L622.
- **Why not here**: anchoring at draft time requires passing exemplars **INTO** U4's `PromptBuilder` — **editing a frozen P1
  unit**, which the standing guardrails forbid and which **Q2-A** (read-only/downstream) excludes. **Q7-C** (authorize the
  U4 edit) was **rejected**: it would be a first-of-its-kind frozen-P1 edit at the final unit of the build and **needs its
  own separate, deliberate authorization**, not a fold inside this FD.
- **Register**: recorded by name as **`FEWSHOT-ANCHOR-UNIMPLEMENTED`**, owned by **`memo-agent-core` (U4)** or a future
  explicitly-authorized change. **Disclosed, never silently dropped** — the `DEPLOY-MIGRATE-DEFERRED` / AC-7 honesty pattern.
- **Checkable**: U22 claims **no** discharge of the generation half in any artifact or report field.

---

## BR-JUDGE-7 — The judge is **advisory-only** and **never alters a recommendation**

The judge **scores prose**. It emits **no** `Recommendation`, no verdict, and no field capable of carrying one. All rubric
text, dimension descriptions, justifications and report copy use **"recommendation"** — never a bare "decision".

- **Grounded**: the advisory-only invariant · **CON-BR2-TYPE** (`MemoDraftOutput` declares no `recommendation`/`confidence`;
  `DecisionMemo` is `frozen`) · ADVISORY-1 · U4's `PromptBuilder` system prompt.
- **Checkable** *(tier-U)*: **structural** — no U22 type declares a `Recommendation`-typed field, so *"the judge changed the
  recommendation"* is **unrepresentable**; plus a **token scan** over every U22 artifact for a bare verdict token
  (`APPROVE`/`REFER`/`DECLINE`) used as a judge **output**, with a **detector self-test**.

---

## BR-JUDGE-8 — The rubric engine is **injected**; the real promptfoo CLI is **`PROMPTFOO-CLI-DEFERRED`**

Scoring is reached **only** through the `RubricEngine` Protocol. At **tier-U** an **offline deterministic fake** drives every
test — **no Node, no npx, no network, no telemetry, no key, no live LLM**.

- **Grounded**: **Q3-A** · the U21 injected-Protocol precedent · the `MCP-TRANSPORT-DEFERRED` shape.
- **⚑ Disclosed facts about the real engine** (measured on disk): `promptfoo>=0.1.0` **is already floored** in
  `requirements.txt` (**nothing new is added**), **but** the installed pip package (0.1.4) is a **thin Python shim around
  the Node.js/TypeScript promptfoo CLI** (*"requires Node.js and npx"*; falls back to `npx`); **the Node engine is ABSENT**;
  invoking it would **`npx`-fetch an unpinned package over the network at run time**; and the shim pulls **`posthog`
  telemetry** (7.21.3) — a BFSI concern, so **telemetry opt-out is documented** as part of the discharge.
- **Discharge conditions** *(distinct — Fold-1)*: Node + npx present · CLI **pinned** · telemetry opt-out configured ·
  adapter bound · **verified against the seeded fixtures**. **Requires NO corpus, NO tier-B, NO live provider key.**
- **Checkable** *(tier-U)*: every test passes with **no promptfoo import and no Node present**; a scan asserts no U22
  production module imports the promptfoo shim.

---

## BR-JUDGE-9 — The real evaluation run is **`JUDGE-EVAL-DEFERRED`**; tier-B is **not required** for U22's completion

U22 is **built and verified at tier-U on a seeded fixture set**. The **real ≥4/5 gate over the tier-B corpus** is a
**named, separately-authorized run**.

- **Grounded**: **Q1-A** · **Q4-A** · the **`outlier-model` (U18) precedent** — its `CorpusSource` is a **dual-source seam**
  (`from_records` fixture / `from_file` tier-B corpus, by `corpus_version`), *"tier-B NOT authorized (not required)"*, and it
  **completed** that way · the `corpus-generator` `R` edge (`unit-of-work-dependency.md` L51).
- **Discharge conditions** *(distinct from BR-JUDGE-8 — Fold-1)*: **tier-B corpus authorized + built** **AND** live
  Gemini + Claude keys **AND** the ≥4/5 gate actually evaluated over real memos. **Prerequisite:
  `PROMPTFOO-CLI-DEFERRED` discharged first** (a rubric engine must exist to run).
- **⚑ Why two items, not one**: the dependency is **one-way**. `PROMPTFOO-CLI-DEFERRED` is dischargeable **without** the
  corpus (verify the real engine on fixtures); `JUDGE-EVAL-DEFERRED` is **not** dischargeable without an engine. Same
  asymmetry as `OBS-SINK-DEFERRED`'s deployment/code split.
- **Checkable** *(tier-U)*: the whole suite passes with **tier-B unauthorized and the corpus absent**; `EvalRunResult.tier`
  reads `unit`; no test reads the real corpus.

---

## BR-JUDGE-10 — **No demographic identifier** enters any rubric input, prompt, justification or report

Not in the rubric text, the dimension descriptions, the judged sample's carried context, the reference memo, the
justifications, or the report.

- **Grounded**: the bias-free invariant · CON-BR1 · U4's `PromptBuilder`, which **deliberately omits** name/city/gender
  (*"Demographics … are intentionally omitted (bias-free)"*).
- **Checkable** *(tier-U)*: a **demographic-token scan** over every U22 artifact and over the hand-authored reference memo,
  with a **detector self-test** (a synthetic memo carrying a demographic token is **flagged**).

---

## BR-JUDGE-11 — U22 **edits nothing it judges**, and emits **no new metric**

`llm-judge` **wraps the built system**: it imports frozen shapes read-only, drives frozen adapters through their existing
seam, and **writes into no frozen tree**. It adds **no** Prometheus metric and **no** dashboard panel.

- **Grounded**: **Q2-A** · **Q6-A** · `unit-of-work-dependency.md` L200 (*"`observability`, `llm-judge`, `deploy-config`
  (all P2) **wrap the built system**"*) · U21's frozen five metrics · `deploy-config`'s five-panel **no-drift** scan.
- **Checkable** *(tier-U)*: a **NOEDIT-style path scan** — U22-authored paths ⊆ its own tree; **no write** under any frozen
  `backend/<unit>/` tree or `backend/app/**`; **detector self-test** (a synthetic frozen-path write is flagged). Plus: U22
  declares **no** metric name, so `observability`'s five and `deploy-config`'s dashboard stay **byte-unchanged**.

---

## Traceability — no orphan

| Rule | Traces to | Tier |
|---|---|---|
| BR-JUDGE-1 | AC-6 · QA-4 · US-PLAT-10 b1 · Brief L175 | U |
| BR-JUDGE-2 | FR-PROV-GATE-2 · AC-6 · QA-4 · US-PLAT-10 b2 | U |
| BR-JUDGE-3 | FR-PROV-GATE-2 · U19 `test_provgate.py` (assigned by name) · `BR-MEXT-10` | U (non-vacuous) |
| BR-JUDGE-4 | FR-PROV-GATE-1 · `BR-MEXT-10` | U (referenced) |
| BR-JUDGE-5 | QA-4 · US-PLAT-10 b3 · Q7-A · Fold-3 | U (paired fixtures) |
| BR-JUDGE-6 | QA-4 (undischarged half) · CG-JUDGE-GAP-1 | disclosure |
| BR-JUDGE-7 | advisory-only · CON-BR2-TYPE · ADVISORY-1 | U (structural) |
| BR-JUDGE-8 | Q3-A · Fold-1 | U + deferral |
| BR-JUDGE-9 | Q1-A · Q4-A · U18 precedent · `R` edge | U + deferral |
| BR-JUDGE-10 | bias-free · CON-BR1 | U (detector) |
| BR-JUDGE-11 | Q2-A · Q6-A · L200 · U21/U23 frozen | U (NOEDIT) |

**AC-2** (*zero unexplained recommendations*) is carried by **BR-JUDGE-1 + BR-JUDGE-5**'s `groundedness` dimension.
**Every `BR-JUDGE-*` is checkable at tier-U**; the only undischarged items are the **three named, disclosed** register
entries — `PROMPTFOO-CLI-DEFERRED`, `JUDGE-EVAL-DEFERRED`, `FEWSHOT-ANCHOR-UNIMPLEMENTED`.
