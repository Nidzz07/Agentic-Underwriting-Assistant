# Functional Design Plan (Part 1) — `llm-judge` (EPIC-6 / U22, Phase 2)

**Phase / Stage**: BUILD → per-unit loop → **Functional Design, Part 1 (Planning)** (plan-then-generate + `[Answer]:` tags)
**Loop position**: `llm-judge` (U22) — **the 1st of its stages**. **Unit**: U22 · EPIC-6 · **Phase 2** · **Date**: 2026-07-19
**Status**: **Plan — awaiting `[Answer]:` tags. NO FD artifact generated; no code; no files beyond this plan. Stop after this plan.**

**⚑ This is the LAST unit in the entire 23-unit decomposition.** Its completion closes the 6th of 6 Phase-2 units and the
full 23-unit build.

---

## 0. DISCOVER-carryover check (RAN — no carryover blocks this unit)

Re-read on disk, **re-derived none**:
- **`unit-of-work.md` L249** — the U22 definition (verbatim below).
- **`unit-of-work-dependency.md` L51 + L200** — U22's dependency edges + its cross-cutting classification.
- **`unit-of-work-story-map.md` L55/L107** — US-PLAT-10 → `llm-judge`, 1 story, exactly once (no orphan/double-assignment).
- **`stories.md`** — the US-PLAT-10 bullet criteria.
- **`requirements.md` L167/168/206/233/237** — FR-PROV-GATE-1/2, QA-4, AC-2, AC-6.
- **`PROJECT-BRIEF.md` L171/175/183-184/234** — the evals row, the LLM-as-judge ≥4/5 promptfoo rubric.

**No open DISCOVER carryover item blocks U22.** The accumulated register items (`Q1-B` divergence, R2–R5 unwired,
tier-B unauthorized, Docker-guard gap, `OUTLIER-IN-PROSE`, `MCP-TRANSPORT-DEFERRED`, `OBS-SINK-DEFERRED`,
`DEPLOY-MIGRATE-DEFERRED`) are **all either out of U22's scope or resolvable as named deferrals** — but **two of them bear
directly on this unit's scope and are raised as questions below**: **tier-B** (Q1) and the **live-LLM discipline** (Q4).

---

## 1. ⚑ Depth classification — **CHECKED, not assumed**

> **`unit-of-work.md` L249 (verbatim)**:
> `#### U22 — `llm-judge`  *(EPIC-6; Phase 2)* — promptfoo groundedness rubric ≥4/5 (Gemini+Claude; Ollama exempt). **US-PLAT-10.** QA-4, AC-2/6. *Depth: standard.*`

**The classification on disk is `standard`** — **not** comprehensive. For contrast, the two units immediately preceding it
carry *different* pinned depths, which is why this had to be read rather than inherited: `observability` (U21) is
*"comprehensive at Infrastructure Design (wiring-heavy)"* and `deploy-config` (U23) is *"comprehensive at Infrastructure
Design"*. **U22 carries neither annotation** — plain `standard`, with no stage-specific escalation.

**`unit-of-work.md` §4 (Carried-forward depth annotation)** makes depth *"a revisitable recommendation — not a locked
floor"*, and lists the *lighter* candidates as display-only UI and **pure-wiring units (`secrets-config`, `admin-cli`,
`deploy-config`, `observability`)** — **`llm-judge` is NOT in that lighter list**, and §4 also states *"the deterministic-core
and **quality** units"* stay comprehensive. `llm-judge` is a **quality unit** (QA-4/AC-2/AC-6). So there is a genuine tension
on disk between the **L249 pinned `standard`** and **§4's "quality units stay comprehensive"** — this is surfaced as **Q5**
rather than improvised.

**Depth RECOMMENDATION for this stage: `standard`** — per the explicit L249 pin, which is the more specific statement.
**Confirmable/overridable via Q5.**

---

## 2. The frozen contracts U22 builds **ON** (referenced, re-derived NONE)

### 2.1 What U22 owns (US-PLAT-10 / QA-4 / AC-2 / AC-6 / FR-PROV-GATE-2)
- **`requirements.md` L206 (QA-4)** — *"LLM-as-judge groundedness rubric (promptfoo, ≥ 4/5) on memo quality; memo wording
  anchored to a reference memo via few-shot for consistency (**not claimed bit-identical**). Applies to Gemini + Claude."*
- **`requirements.md` L237 (AC-6)** — *"LLM-as-judge score ≥ 4/5 (Gemini + Claude only; **Ollama exempt** as showcase-only)."*
- **`requirements.md` L233 (AC-2)** — *"Unexplained recommendations | 0 | Eval groundedness check."*
- **`requirements.md` L168 (FR-PROV-GATE-2)** — *"**Memo-quality** gates — groundedness ≥ 4/5 and memo calibration — apply to
  **Gemini (primary) + Claude (secondary)** only. **Ollama is exempt** (showcase-only)."*
  vs **L167 (FR-PROV-GATE-1)** — *"**Decision-level** gates — reproducibility (100%) and bias-swap (delta 0) — apply to **all**
  providers, because the decision is provider-independent (CON-BR2)."*
  ⇒ **`llm-judge` is precisely the unit that OWNS and EXECUTES the FR-PROV-GATE-2 memo-quality half.** FR-PROV-GATE-1's
  decision-level half is **already owned by `quality-gates` (U-P1)** — **not** re-opened here.

### 2.2 Dependency edges (`unit-of-work-dependency.md` L51, verbatim)
> `| `llm-judge` (2) | `memo-agent-core`, `memo-extensions`, `corpus-generator` `R` | scores memo groundedness (Gemini+Claude) |`

**`corpus-generator` carries the `R` annotation** — the **same** marker `outlier-model` (U18) carries on its corpus edge
(*"`outlier-model` (2) | `corpus-generator` `R`, `secrets-config` | reads **frozen** corpus by `corpus_version`"*). This is
the **direct precedent** that grounds **Q1**.

### 2.3 Cross-cutting classification (`unit-of-work-dependency.md` L200, verbatim)
> *"`observability`, `llm-judge`, `deploy-config` (all P2) **wrap the built system**."*

⇒ The frozen DISCOVER artifact **already classifies `llm-judge` as a wrap-the-built-system unit**, in the *same sentence* as
`observability` and `deploy-config`. **Q2** exists to confirm the one way U22 may differ from those two, not to re-open the
classification.

### 2.4 `memo-agent-core` (U4, FROZEN) — what U22 evaluates
Read on disk (`backend/memo_agent_core/schemas.py`), **not re-derived**:
- **`MemoDraftOutput`** — the LLM's structured output, declaring **only** `narrative_prose` + `cited_rule_ids`. Per the
  module docstring: **CON-BR2-TYPE** — it has **no** `recommendation`/`confidence` field, so *"the LLM changed the
  recommendation" is unrepresentable*.
- **`DecisionMemo`** — `frozen=True`, `extra="forbid"`; `.recommendation`/`.confidence` are injected **read-only** by
  `MemoAssembler` from the handed deterministic report.
- **`CitationValidationResult`** (`all_valid`, `offending_cited_ids`, `outcome` ∈ `valid`/`citation_failure`) — the frozen
  **hallucination guard** (`validate_citations`).
- **`MissingInformationItem`** / `MissingInfoSource` — the deterministic missing-info region (D) with a fixed total order.
⇒ **The groundedness rubric scores `narrative_prose` against the evidence the deterministic layer already produced.** The
frozen citation validator is a **separate, deterministic** guard — U22 **layers on** it, never replaces it.

### 2.5 `memo-extensions` (U19, FROZEN) — the providers under gate
Read on disk (`backend/memo_extensions/`): **`provider_secondary.py`** (`ClaudeAdapter`, Claude Opus 4.8, *tested*
secondary) and **`provider_showcase.py`** (`OllamaAdapter`, *showcase/wired-only*). **`temperature=0` is fixed CENTRALLY**
inside the adapter (`_PRODUCTION_TEMPERATURE: Final[int] = 0`), *"never a per-call / caller-controlled parameter"*.
U19's own tier taxonomy (verbatim, `nfr-requirements.md` L6): **tier-U** = *"no live LLM call, no key, no network, no Docker,
no live MCP server"*, extended to Claude and Ollama; **tier-S** = offline smoke; **tier-B** = N/A + NOT authorized.

### 2.6 `observability` (U21, FROZEN) — whether U22's own runs are traced
Read on disk (`backend/observability/__init__.py`): the unit is *"the **emit-only** telemetry SINK/WIRING unit… Defines the
**injected** trace/metric Protocols + the pure allowlist projection… **WITHOUT editing any frozen unit**… The LIVE
Langfuse/Prometheus SDK binding is **deferred** to composition/deploy-config (`OBS-SINK-DEFERRED`); this package builds the
injected Protocols + their **offline fakes** only."* The five frozen metrics are `DECISION_LATENCY`,
`DECISIONS_BY_RECOMMENDATION`, `RULE_EVALUATION_DURATION`, `LLM_CALL_ERRORS`, `OUTLIER_FLAG`.
⇒ **None of the five frozen metrics is an "eval-run" metric.** Whether U22 emits telemetry at all is therefore a real
question (**Q6**) — adding a sixth metric would be **drift against a frozen topology** that `deploy-config` just committed
a 1:1 dashboard against.

### 2.7 Domain invariants (from the underwriting-rules skill) that bind U22
**Advisory-only language**: the rubric, its prompts, and every artifact must say **"recommendation"**, never a bare
"decision"/verdict — and must never emit `APPROVE`/`REFER`/`DECLINE-RECOMMEND` as an *output of the judge*. **No LLM in the
deterministic rules path** — U22 sits **downstream of** the memo, never inside rule evaluation. **temperature=0** on any
production LLM call. **Bias-free**: no demographic identifier may enter a rubric prompt or a judge feature.

---

## 3. ⚑ Two findings surfaced on disk that the questions below turn on

### 3.1 promptfoo IS floored — but the floored package is a **shim**, not the engine
- **`requirements.txt` L49** — `promptfoo>=0.1.0` is **already floored**. ⇒ At the pip layer, **the "no new dependency
  unless flagged" streak is INTACT**; U22 introduces nothing new to `requirements.txt`.
- **But `pip show -f promptfoo` (v0.1.4 installed) reads**: *"**Python wrapper for the promptfoo CLI** … This package
  provides a Python interface to the promptfoo **TypeScript** CLI tool. **It requires Node.js and npx to be installed**."*
  Its `cli.py` is *"a **thin wrapper** around the promptfoo **Node.js** CLI … executes a global promptfoo binary when
  available, **falling back to `npx`**"* (`shutil.which("node")` / `shutil.which("npx")` / `subprocess`).
- **The actual evaluation engine — the Node promptfoo CLI — is ABSENT** (`frontend/node_modules/promptfoo` not present; the
  `venv\Scripts\promptfoo.exe` on PATH is the **shim**, not the engine). On invocation the shim would **`npx`-fetch the real
  CLI at run time — i.e. a network fetch of an unpinned package**.
- The shim also pulls **`posthog` (7.21.3, installed)** and ships a `telemetry.py` — i.e. **outbound analytics** in a BFSI
  system.
⇒ This is **not** a clean "already floored, nothing to decide". It is a **genuine, disclosable dependency decision** — the
same shape as `MCP-TRANSPORT-DEFERRED` for U19. Raised as **Q3**; **not improvised**.

### 3.2 The `outlier-model` (U18) fixture precedent is exact
`outlier-model`'s frozen `code-summary.md`/`business-logic-model.md`: *"Every test runs seeded + deterministic at **tier-U**
on in-memory fixtures"*; **`CorpusSource`** is a **dual-source seam** — **`from_records`** (tier-U/S fixture) vs
**`from_file`** (tier-B frozen `corpus/`), *"by `corpus_version`"*; and *"**tier-B NOT authorized (not required)**"*;
*"No test … exercises the real tier-B corpus."* ⇒ A unit with an `R` corpus edge has **already** been built, fully
unit-tested, and completed **without tier-B ever running**. Grounds **Q1**.

---

## 4. Proposed FD scope (what Part 2 WOULD produce — pending answers)

Per the `standard` depth pin (Q5) and the prior units' FD shape, **three artifacts** at
`guide-docs/build/llm-judge/functional-design/`:
1. **`domain-entities.md`** — the judge's data contracts: the **rubric definition**, a **judged-sample** record, the
   **groundedness score** value object (≥4/5 threshold), the **eval-run result/report**, and the **provider-scope tag**
   (Gemini+Claude in-gate / Ollama exempt). Explicit **reference-not-own** list: `DecisionMemo`/`MemoDraftOutput`/
   `CitationValidationResult` (U4), the provider adapters (U19), `CorpusRecord`/`CorpusManifest` (corpus-generator, `R`).
2. **`business-rules.md`** — **`BR-JUDGE-1..N`**, including: the ≥4/5 threshold; **Gemini+Claude in-gate, Ollama exempt**
   (FR-PROV-GATE-2, single-sourced — *not* re-deriving FR-PROV-GATE-1); the **few-shot reference-memo anchoring**
   (consistency, **not** bit-identical — QA-4's exact wording); **advisory-only** rubric language; **no demographic input**;
   **the judge never alters a recommendation** (it scores prose only — the CON-BR2-TYPE boundary held).
3. **`business-logic-model.md`** — the eval lifecycle (**assemble sample set → run rubric → score → aggregate → report
   pass/fail vs ≥4/5**), the **tier split** (what runs at tier-U vs what is deferred to a live/authorized run), and the
   **seam** by which the rubric engine is injected (so tier-U needs no live LLM and no Node CLI).

**NOT in scope at FD**: any code; any `backend/llm_judge/` package; any promptfoo config file; any live eval run; any edit
to U4/U19/U21/U23 or the composition root.

---

## 5. Clarifying questions — fill each `[Answer]:` tag

> Answer with the letter (e.g. `[Answer]: A`). For **C/D "Other"**, describe after the tag. **I will not improvise on any of
> these** — each is a genuine fork with a real consequence, not a formality.

---

### Question 1 — What exactly does `llm-judge` evaluate, and against what corpus? (the tier-B dependency)

`unit-of-work-dependency.md` L51 gives U22 an **`R` (read-only reference)** edge to `corpus-generator` — the *same* marker
`outlier-model` (U18) carries. **tier-B (the real 300+ synthetic corpus run) has never been authorized.** Does U22's scope
*depend* on tier-B running first?

**A) Build + unit-test against a SEEDED FIXTURE SET; defer the real evaluation run as its own separately-authorized step —
exactly the `outlier-model` precedent (RECOMMENDED).**
U22 owns a **dual-source seam** mirroring U18's `CorpusSource.from_records` / `.from_file`: at **tier-U** the judge scores a
small, **seeded, in-repo fixture set** of `DecisionMemo`-shaped samples (hand-authored, deterministic, no live LLM, no
network, no Node CLI); the **real ≥4/5 gate over the tier-B corpus** is a **named, deferred, separately-authorized run**
(proposed register name **`JUDGE-EVAL-DEFERRED`**), documented but never executed here. **tier-B stays unauthorized and is
NOT required for U22 to be complete** — precisely as U18 completed. The rubric logic, the threshold arithmetic, the
provider-scoping (Gemini+Claude in / Ollama exempt), the aggregation, and the report shape are **all fully verifiable at
tier-U** on fixtures.

**B) U22's scope genuinely REQUIRES tier-B first** — the unit cannot be meaningfully designed or completed until the real
corpus exists, so U22 blocks on a tier-B authorization decision. *(Available, but it would make U22 the first unit in the
build to hard-block on tier-B, and it contradicts the U18 precedent where an `R` corpus edge was satisfied by fixtures.)*

**C) Narrow U22 to rubric-definition-only** — define the rubric as a declarative artifact with **no** executing scorer at
all, deferring **all** execution. *(Available; but it likely under-delivers US-PLAT-10, which asks for a rubric that
**scores** memo quality.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 2 — Is `llm-judge` another "wrap the built system" unit, or does judging output quality change its relationship to U4/U19?

`unit-of-work-dependency.md` **L200** already states: *"`observability`, `llm-judge`, `deploy-config` (all P2) **wrap the
built system**."* So the classification is frozen. The real question is whether **judging U4/U19's output quality** implies
any coupling that `observability`/`deploy-config` did not have.

**A) YES — the same wrap-the-built-system relationship, editing none of them; the ONLY difference is that U22 reads their
OUTPUT (a `DecisionMemo`) rather than their EMISSIONS or their PACKAGING (RECOMMENDED).**
U22 is a **read-only consumer of frozen output shapes**, exactly as `observability` was an emit-only sink and
`deploy-config` a packager. It **imports `DecisionMemo`/`MemoDraftOutput` read-only** (import-to-read ≠ edit, the ROUTES-1
precedent) and **drives the frozen provider adapters through their existing seam** — **editing U4 and U19 not at all**. A
**`NOEDIT`-style scan** enforces this, as in U21/U23. The judge is **strictly downstream**: it never feeds back into memo
generation, never alters a recommendation (CON-BR2-TYPE holds structurally), and never enters the deterministic rules path.

**B) NO — judging quality requires a tighter coupling** (e.g. U22 needs a hook or callback inside the memo pipeline, or
needs to re-run generation itself). *(Available; but this would require touching the frozen U4 orchestrator — which the
guardrails forbid — so it would need an explicit authorization.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 3 — How does promptfoo fit the "no new dependency unless flagged" discipline? (see §3.1)

**The facts on disk**: `promptfoo>=0.1.0` **IS already floored** in `requirements.txt` L49 (so the pip-layer streak is
intact), but the installed package (0.1.4) is a **thin Python shim that shells out to the Node.js promptfoo CLI via
`npx`**; **the Node engine is NOT installed**; invoking it would **`npx`-fetch an unpinned package over the network at run
time**; and the shim pulls **`posthog` telemetry**.

**A) Treat the Node CLI as a DEFERRED, EXPLICITLY-DISCLOSED external dependency — design the rubric engine behind an
INJECTED SEAM so tier-U never needs promptfoo at all (RECOMMENDED).**
U22 defines a **`RubricEngine` Protocol** (the U21 injected-Protocol pattern, verbatim in spirit). At **tier-U** an
**offline deterministic fake** drives every test — **no Node, no `npx`, no network, no telemetry**. The **real promptfoo
CLI binding** is a **named deferral** (proposed **`PROMPTFOO-CLI-DEFERRED`**) discharged only in the separately-authorized
live eval run, alongside **explicit disclosure** of (i) the Node/`npx` requirement, (ii) the unpinned run-time fetch, and
(iii) the **posthog telemetry** — with telemetry **opt-out documented** as a BFSI concern. **This is the same shape as
`MCP-TRANSPORT-DEFERRED`**: the handler layer is built and fully tested; the live protocol binding is deferred. `promptfoo`
stays floored in `requirements.txt`; **nothing new is added**.

**B) Install/pin the Node promptfoo CLI now** (add it to `frontend/package.json` or a new tool manifest) so the real engine
is present in-repo. *(Available; but it introduces a **new** Node dependency + a telemetry-bearing toolchain, breaking the
streak that has held every unit — and it would be the first non-flagged new dependency in the build.)*

**C) Drop promptfoo entirely** and implement the rubric with an in-house scorer. *(Available; but PROJECT-BRIEF L175/L184
and QA-4/AC-6 name **promptfoo** explicitly, so this diverges from a stated requirement and would need to be recorded as a
divergence like `Q1-B`.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 4 — Does the judge need LIVE LLM calls to function, and how is that reconciled with the tier-U discipline?

`llm-judge` is judging LLM output quality, so an "LLM-as-judge" is by definition an LLM call. Every prior unit held
**tier-U = "no live LLM call, no key, no network"** (U19's verbatim taxonomy). **Is U22 the first unit where that discipline
genuinely cannot hold at some tier?**

**A) The discipline HOLDS at tier-U; the live judging is deferred to a separately-authorized run — the same shape as tier-B
corpus generation and AC-7's trace audit (RECOMMENDED).**
Split the unit cleanly into **two halves**: **(i)** the **deterministic half** — rubric definition, threshold arithmetic
(≥4/5), provider-scope enforcement (Gemini+Claude in-gate, **Ollama exempt**), sample assembly, score aggregation, report
shape, and pass/fail — **all pure, all fully tested at tier-U against fixed judge-score fixtures with no live call**; and
**(ii)** the **live-judging half** — the actual LLM scoring pass — reached **only** through the injected `RubricEngine` seam
and **deferred** to the authorized run (`JUDGE-EVAL-DEFERRED`). ⇒ **U22 is NOT the first unit to break the discipline**;
it is the third to *name* a deferred live step (`corpus-generator`'s tier-B, `observability`'s AC-7, now this). Any live
call, when it eventually runs, uses **temperature=0** per the domain invariant.

**B) U22 genuinely cannot hold tier-U** — accept that a live LLM call (key + network) is required for the unit to be
meaningfully tested, and authorize that as a first-in-build exception. *(Available; but it would break a discipline that has
held across all 22 completed units, and would need explicit authorization.)*

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 5 — Depth confirmation (the L249 pin vs §4's "quality units stay comprehensive")

**Checked, not assumed** (§1): `unit-of-work.md` **L249 pins `Depth: standard`**, while **§4** says depth is *"a revisitable
recommendation — not a locked floor"*, lists the *lighter* candidates as display-only UI + pure-wiring units (**`llm-judge`
is NOT among them**), and states *"the deterministic-core and **quality** units"* stay comprehensive — and `llm-judge` **is**
a quality unit (QA-4/AC-2/AC-6). Genuine tension on disk; not improvised.

**A) `standard` — honour the explicit L249 pin (RECOMMENDED).**
The per-unit pin is the more specific statement, and §4's escalation clause is permissive ("can be given comprehensive
depth"), not mandatory. `standard` yields the three FD artifacts in §4 above without the extra comprehensive apparatus.

**B) `comprehensive`** — escalate under §4, on the grounds that `llm-judge` is a quality unit owning an acceptance criterion
(AC-6) and the FR-PROV-GATE-2 boundary. §4 explicitly permits this **without amending `unit-of-work.md` or
`execution-plan.md`**.

**C) Other (describe after `[Answer]:`)**

[Answer]: A

---

### Question 6 — Are `llm-judge`'s own evaluation runs traced/measured by `observability`?

The user flagged U22's eval runs as *"a candidate for being traced/measured"*. But `observability` (U21) is **frozen** with
**exactly five metrics**, and `deploy-config` (U23) **just committed a Grafana dashboard pinned 1:1 to those five, with a
scan asserting no sixth panel and no drift**. None of the five is an eval-run metric.

**A) NO new metric; U22 is NOT wired into the frozen five (RECOMMENDED).**
Adding an eval metric would be **drift against a frozen topology** and would **break `deploy-config`'s just-passing
five-panel no-drift scan**. U22's eval runs are an **out-of-band quality activity**, not a production request path — the
same reasoning by which `quality-gates` (U-P1) is not a traced production step. If U22 emits anything, it emits **its own
report artifact**, not a Prometheus metric. Recorded explicitly so the omission is **honest, not an oversight**.

**B) YES — wire U22 into observability**, accepting a 6th metric/panel and the consequent updates to `observability` and
`deploy-config`. *(Available; but both are **frozen**, and the guardrails forbid touching U21/U23 — so this would require
explicit re-opening authorization.)*

**C) Defer the decision** — name it as an open seam (e.g. `JUDGE-TRACE-DEFERRED`) without designing it now.

**D) Other (describe after `[Answer]:`)**

[Answer]: A

---

## 5.5 Mandatory ambiguity-check (RAN against the six answers + the frozen substrate) → **⚑ NOT CLEAN — 2 folds RESOLVED + 1 GENUINE GAP → SURFACE-AND-STOP**

**Answers as given (verbatim intent)**: **Q1-A** seeded fixture set mirroring `outlier-model`; the real run a named
separately-authorized `JUDGE-EVAL-DEFERRED`; tier-B stays unauthorized and is not required for completion. **Q2-A** same
wrap-the-built-system relationship as U21/U23, editing neither U4 nor U19; read-only consumer of frozen output shapes
(import-to-read ≠ edit); drives the frozen adapters through their existing seam; strictly downstream, never feeding back
into memo generation nor altering a recommendation. **Q3-A** Node CLI a deferred, explicitly-disclosed external dependency;
rubric engine behind an injected `RubricEngine` Protocol with an offline deterministic fake at tier-U (no Node, no npx, no
network, no telemetry); real binding a named `PROMPTFOO-CLI-DEFERRED` disclosing the npx unpinned-fetch + posthog
telemetry; `promptfoo` stays floored, nothing new added. **Q4-A** tier-U discipline holds — deterministic half fully tested
on fixtures, live-judging half deferred; U22 the third unit to *name* a deferred live step, not the first to break the
discipline. **Q5-A** `standard` depth per the specific L249 pin. **Q6-A** no new metric; not wired into observability's
frozen five; own report artifact only.

### ✅ CG-JUDGE-Fold-1 [check (i)] — `JUDGE-EVAL-DEFERRED` and `PROMPTFOO-CLI-DEFERRED` are **GENUINELY SEPARABLE**: **TWO distinct register items with DIFFERENT discharge conditions and a one-way prerequisite edge** — *not* the same deferral described twice.
The naive reading (*"the live run needs both the real corpus and the real CLI simultaneously, so it is one item"*) is
**refuted by asymmetry**: **`PROMPTFOO-CLI-DEFERRED` is independently dischargeable WITHOUT the corpus and WITHOUT tier-B** —
install/pin the Node CLI, configure telemetry opt-out, bind the `RubricEngine` adapter to it, and verify it end-to-end
**against the seeded fixture set from Q1-A**. That is a real, independently valuable state (*"the real engine works, driven
on fixtures"*) reachable while tier-B remains unauthorized. The converse does **not** hold: `JUDGE-EVAL-DEFERRED` cannot
discharge without a working rubric engine (Q3-C's in-house scorer was rejected), so it **depends on**
`PROMPTFOO-CLI-DEFERRED`. ⇒ **Two items, one directed edge**:
- **`PROMPTFOO-CLI-DEFERRED`** — discharges on: Node+npx present, CLI **pinned**, telemetry opt-out configured, adapter
  bound, **verified on fixtures**. **Needs no corpus, no tier-B, no live provider key.**
- **`JUDGE-EVAL-DEFERRED`** — discharges on: **tier-B corpus authorized + built** **AND** live Gemini+Claude keys **AND**
  the ≥4/5 gate actually evaluated over real memos. **Prerequisite: `PROMPTFOO-CLI-DEFERRED` discharged first.**
**Precedent**: `OBS-SINK-DEFERRED` split exactly this way (deployment half realizable by `deploy-config` while the code
half stayed composition's). Resolves against frozen facts — **no user decision needed**.

### ✅ CG-JUDGE-Fold-2 [check (iii)] — the Ollama exemption **REQUIRES an Ollama-sourced fixture with real teeth**; this is **not** an analogy to U19 — a **frozen U19 artifact explicitly ASSIGNS this duty to U22**.
`backend/memo_extensions/tests/test_provgate.py` docstring (**verbatim, on disk**):
> *"**Governance note (NOT a code test)**: Ollama's ABSENCE from the groundedness/promptfoo target set (AC-6 / QA-4 /
> FR-PROV-GATE-2) is a **tooling-config fact owned by `llm-judge` (U22)**, recorded as an **explicit, documented
> exemption — never implicit, and not asserted here**."*

So U19 **deliberately declined** to assert the exemption and **handed it to U22 by name**, with the standard *"never
implicit"*. ⇒ A fixture set containing **only** Gemini+Claude samples would prove the exclusion **VACUOUSLY** (nothing
present to exclude). **The fixture set MUST include at least one Ollama-sourced sample that is PRESENT in the assembled
sample set but DEMONSTRABLY EXCLUDED from the scored/aggregated set** — the **non-vacuity** discipline already established
by SEC3-1's permit-side detector self-test and every `detector self-test` in the build. U19 also fixes the **boundary**:
Ollama is exempt from **memo-quality** gates *only*, and **still holds the decision-level gates** (`temperature=0`,
CON-BR2-TYPE) — so the fixture must exclude it from **scoring**, never characterise it as untested. Resolves against a
frozen artifact — **no user decision needed**.

### ⛔ CG-JUDGE-GAP-1 [check (ii)] — **GENUINE GAP — SURFACING AND STOPPING.** QA-4's few-shot reference-memo anchoring is **NOT IMPLEMENTED ANYWHERE IN THE CODEBASE**, and U22 **cannot** implement it without editing the frozen U4 — which the guardrails forbid.
**Measured on disk, not inferred**: a repo-wide scan of `backend/**/*.py` for `few.?shot|reference_memo|reference memo`
returns **ZERO HITS**. U4's frozen `PromptBuilder` (`backend/memo_agent_core/prompt_builder.py`, read in full) builds the
prompt from `MemoAgentInput` **and nothing else** — system prompt + read-only recommendation + read-only confidence + the
rule report + non-demographic applicant facts. **There is no reference memo and there are no few-shot exemplars.** The
clause appears **only** as an unrealized requirement, in exactly two places: `requirements.md` **L206** (QA-4) and
`stories.md` **L622** (US-PLAT-10's third bullet).

**Why this is a genuine fork and not something to improvise**: *"memo wording **anchored** to a reference memo **via
few-shot**"* is a **GENERATION-side** mechanism — few-shot exemplars are supplied to the model **when the memo is drafted**.
That is U4's `PromptBuilder`. But **Q2-A** (just answered) fixes U22 as **strictly downstream, read-only, editing neither
U4 nor U19**, and the standing guardrails forbid touching the 17 frozen P1 units. ⇒ **U22 structurally cannot discharge the
generation-side half of QA-4.** Two coherent readings exist and they lead to **materially different FD artifacts**:
- **Reading 1 — U22 scores anchoring-CONSISTENCY as a rubric dimension.** The judge scores *"is this memo's wording
  consistent with the reference memo?"* as one scored dimension. Exercisable at tier-U (a close fixture scores high, a
  deliberately-divergent one scores low → real teeth). **But this does not make the generator few-shot-anchored** — it only
  *measures* consistency that nothing is currently producing, so QA-4's generation clause stays unimplemented.
- **Reading 2 — the anchoring clause is wholly OUT of U22's scope.** U22 scores **groundedness** only (the ≥4/5 rubric,
  AC-6/AC-2), and the few-shot anchoring is recorded as an **unimplemented requirement** belonging to U4 / a future
  authorized change — a **new register item** (proposed **`FEWSHOT-ANCHOR-UNIMPLEMENTED`**).

**Either way, an unimplemented acceptance-adjacent requirement has been discovered** — QA-4 is only **half** realizable by
U22 as scoped. **This is exactly the "flag and stop, do not improvise" condition.** Deciding it silently would either
invent a generation-side change to a frozen unit or quietly drop a stated requirement. **NO FD artifact generated.
Escalated as Q7 below.**

---

## 5.6 ⛔ Question 7 (NEW — raised by CG-JUDGE-GAP-1; blocks Part 2)

### Question 7 — How is QA-4's few-shot reference-memo anchoring handled, given it is unimplemented and U22 cannot implement it?

**Facts**: repo-wide scan → **zero** few-shot/reference-memo implementation; U4's `PromptBuilder` is frozen and has none;
the clause exists only in `requirements.md` L206 + `stories.md` L622; Q2-A fixes U22 as read-only/downstream; the
guardrails forbid editing U4.

**A) U22 scores anchoring-CONSISTENCY as one rubric dimension; the GENERATION-side few-shot mechanism is recorded as a new
open register item `FEWSHOT-ANCHOR-UNIMPLEMENTED`, owned by U4 / a future authorized change (RECOMMENDED).**
Keeps U22's scope honest and additive: the rubric gains a *consistency-to-reference* dimension fully testable at tier-U
(close fixture → high, divergent fixture → low, giving it teeth), while the **unimplemented generation half is disclosed
by name** rather than silently dropped — the same honesty pattern as `DEPLOY-MIGRATE-DEFERRED` and AC-7. QA-4 is then
**explicitly half-discharged**, with the remaining half visible on the register.

**B) The anchoring clause is wholly OUT of U22's scope** — U22 scores groundedness only (AC-6/AC-2); the entire anchoring
clause becomes `FEWSHOT-ANCHOR-UNIMPLEMENTED` against U4. *(Cleanest scope boundary; but US-PLAT-10's third bullet then has
no owner at all in the completed build.)*

**C) Authorize U22 to add the few-shot anchoring to U4's `PromptBuilder`** — explicitly re-opening a frozen P1 unit.
*(Available only with an explicit override; it contradicts the standing guardrails and Q2-A, and would be the first frozen-P1
edit in the build.)*

**D) Other (describe after `[Answer]:`)**

[Answer]: A — U22 scores anchoring-consistency as one rubric dimension (fully testable at tier-U: a close fixture scores
high, a deliberately-divergent one scores low, giving it real teeth), while the generation-side few-shot mechanism itself is
recorded as a new, honestly-disclosed open register item **`FEWSHOT-ANCHOR-UNIMPLEMENTED`**, owned by `memo-agent-core` (U4)
or a future explicitly-authorized change — **never silently dropped, never implemented here**. This keeps U22's scope honest
and additive, consistent with the `DEPLOY-MIGRATE-DEFERRED` and AC-7 pattern of disclosing a real gap by name rather than
either overclaiming discharge or erasing a stated requirement from the register.
**Rationale for A over B**: B would leave **US-PLAT-10's third bullet with no owner anywhere in the completed 23-unit
build**. Under A the consistency-scoring half is **real, tested, and delivers genuine value** (catching wording drift
against a reference), even though it does **not** retroactively make `memo-agent-core`'s generation few-shot-anchored.
**C is correctly rejected** — reopening a frozen P1 unit at the very last unit of the build would be a first-of-its-kind
violation of the standing guardrails and needs its **own separate, deliberate authorization decision** if ever pursued, not
something folded into this FD.

---

## 5.7 Ambiguity-check RE-RUN (against Q7-A + Q1–Q6 + Fold-1 + Fold-2) → **CLEAN (1 new fold; no surface-and-stop)**

### ✅ CG-JUDGE-Fold-3 [the Q7-A reference-memo question] — anchoring-consistency scoring **DOES** require a reference memo; it is a **U22-OWNED, HAND-AUTHORED TIER-U FIXTURE**, and it requires **NO change to U4**.
**The question is real**: you cannot score *"is this memo's wording consistent with the reference?"* without a reference to
compare against. Resolved on three grounded points:

1. **Nothing exists to reuse — and reuse would be forbidden anyway.** Scanned on disk: there is **no shared/golden memo
   fixture** in the build. `backend/memo_agent_core/tests/` has **no `fixtures.py`** (unlike `memo_extensions`, which does);
   U4's tests construct `DecisionMemo` **ad-hoc inline** (`test_schemas.py` L44, `test_memo_hash_adapter.py` L38).
   ⇒ U22 **hand-authors its own** reference memo as fixture data. Critically, it **must NOT be added into U4's test tree** —
   that would be **editing a frozen unit**. It lives in **U22's own fixture module**.
2. **⚑ The decisive distinction — comparison TARGET vs prompt INPUT.** The reference memo is a **scoring comparison target
   held by the judge**; it is **NOT** fed into the memo-generation prompt. **U4 never sees it.** Few-shot anchoring (the
   unimplemented `FEWSHOT-ANCHOR-UNIMPLEMENTED` half) would require passing exemplars **INTO** `PromptBuilder` at draft
   time — *that* is the U4 edit the guardrails forbid, and it is exactly what Q7-A does **not** do. ⇒ **Q7-A is structurally
   compatible with Q2-A (read-only/downstream) and with the frozen-P1 guardrail.** The two halves of QA-4 are cleanly
   separated by *direction of data flow*: **into generation = U4's, forbidden here**; **out of generation into scoring =
   U22's, delivered here**.
3. **Construction is import-to-read, not edit.** The reference memo is built **via the imported frozen `DecisionMemo`
   schema** (fields read on disk: `narrative_prose` **L** · `cited_rule_ids` **L** · `missing_information` **D** ·
   `recommendation` **RO** · `confidence` **RO** · `memo_hash` **M** · `model_version` **M**). Instantiating a frozen
   Pydantic model is **using** it, not modifying it — the same import-to-read ≠ edit principle already settled by ROUTES-1
   and Q2-A.

**Two constraints the reference memo inherits (stated so Part 2 cannot drift)**:
- **Scope of comparison**: the judge scores the **`narrative_prose` (L) region only** — the sole LLM-authored prose. The
  **D / RO / M** regions are deterministic or injected and are **never judged** (judging them would re-open CON-BR2-TYPE).
- **Nature of the comparison**: QA-4 says *"anchored … for consistency (**not claimed bit-identical**)"* ⇒ the reference is
  a **STYLE/STRUCTURE exemplar**, not a per-applicant content twin. **One canonical reference memo** serves the fixture set;
  it is **not** required to match each sample's applicant or rule report. This is what makes the dimension coherent for a
  fixture set spanning different applicants.
- The hand-authored reference must itself obey the unit's own rules: **advisory-only wording** (*"recommendation"*, never a
  bare verdict) and **no demographic identifier** — mirroring U4's `PromptBuilder`, which deliberately omits name/city/gender.

**No frozen contract re-opened; no frozen edit; no user decision needed. → Proceed to generate Part 2.**

---

## 6. Explicit HOLDS for Part 2

- **No FD artifact until every `[Answer]:` above is filled**, followed by the **mandatory ambiguity-check** (grounded in the
  frozen U4/U19/U21/U23 contracts + the actual on-disk promptfoo/corpus facts), **surfacing-and-stopping** on any genuine
  gap rather than improvising.
- **No code**; **no `backend/llm_judge/` package**; **no promptfoo config**; **no live eval run**; **no `requirements.txt`
  edit** (promptfoo already floored — §3.1).
- **WIRE-1 untouched · the 17 frozen P1 units untouched · `outlier-model` (U18) · `memo-extensions` (U19) ·
  `ui-outlier-view` (U20) · `observability` (U21) · `deploy-config` (U23) — all now frozen — untouched · the CLOSED
  composition root untouched · tier-B NOT authorized · the `audit_store` Docker-guard gap untouched · no other unit
  started · the 23-unit decomposition unchanged.**
- **Domain invariants bind**: advisory-only wording ("recommendation", never a bare verdict); the judge **never** alters a
  recommendation (CON-BR2-TYPE); **no LLM in the deterministic rules path**; **temperature=0** on any production call; **no
  demographic identifier** in any rubric prompt or judge input.
- **FR-PROV-GATE-2 is single-sourced here**; **FR-PROV-GATE-1 stays `quality-gates`'** — not re-derived.

---

## 7. Next step (STOP here)

Fill the six `[Answer]:` tags in §5. On your signal I will read the answers, run the mandatory ambiguity-check, **embed the
full Q&A in this plan file**, and generate **Part 2** — the FD artifacts named in §4 — then present the standardized
2-option completion message (1. Request Changes / 2. Continue to Next Stage). **No FD artifact is generated until the
answers are in and checked.** This is the **1st of U22's stages**, and U22 is the **LAST unit in the 23-unit decomposition**.
