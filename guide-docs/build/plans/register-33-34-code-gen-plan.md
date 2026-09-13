# REGISTERS #33 + #34 (+ #35) — CODE GENERATION PLAN

**Status**: ✅ **COMPLETE AND GREEN — BOTH STAGES, ALL 11 STEPS, ALL 48 CHECKBOXES `[x]`, ZERO UNCHECKED.**
⛔ **TIER-U / TIER-I GREEN ONLY. LIVE VERIFICATION PENDING — §7 HAS NOT BEEN RUN.**
**Backend 1892 / 0 / 45 / 5 / 99.36% · frontend 823 / 155** (frontend an exact baseline match).
⛔ **#35 opened AND closed · #34 closed — TIER-U ONLY · #33 NOT closed** — register 34 → 35.
⚠️ **Nothing in this pass constitutes evidence that a real model returned parseable XML, or that a
re-draft succeeded against a real stack.** §7 is the only instrument that can move #33 or lift #34
above tier-U, and it carries ⛔ **two checks that have never once succeeded in this build's
history**. ⛔ **NOT COMMITTED.** HEAD `bd3875d`, nothing staged.
⚠️ **Superseded status line, preserved**: *"✅ COMPLETE AND GREEN — BOTH STAGES, ALL 11 STEPS, ALL 51 CHECKBOXES."*
⛔ **Corrected: the checkbox count is 48, not 51** — an overcount written at the close of stage 2 and
fixed here rather than left standing.
⚠️ **Superseded status line, preserved**: *"⚑ IN EXECUTION. STAGE 1 COMPLETE (steps 0–5); STAGE 2 IN PROGRESS (resumed at step 6.3)."*
⚠️ **Superseded status line, preserved**: *"⛔ PLAN ONLY — AT THE CODE-GEN GATE. NO CODE WRITTEN. NO FROZEN FILE TOUCHED."*
⛔ **That line went false on 2026-09-12 and was not corrected at the time** — the session that executed
stage 1 was cut off by a usage limit and logged nothing. **Two of the four authorized frozen files
(`orchestrator.py`, `telemetry.py`) ARE now modified**, plus five design docs and two new test files.
**Stage 1 measured +4, landing at 1841 — the prediction hit exactly**; coverage unmoved at 99.36%.
**Step 6.1's test exists and step 6.2's RED was reproduced and recorded 2026-09-12T12:09:05Z**
(`DECLINE-RECOMMEND: extracted 'DECLINE-RECOMMEND'`). ⚑ **Reconstruction entry**: `audit.md`
2026-09-12T12:09:05Z, which also records the one thing that is **lost and deliberately not
fabricated** — stop-gate 1's original RED observation. ⛔ **STILL NOT COMMITTED.**
**Created**: 2026-08-24
**Parents**: `register-33-34-combined-plan.md` (Q1–Q13 answered; ambiguity check §6 CLEAN)
· `register-33-34-reopening-authorization.md` — ✅ **SIGNED 2026-08-24, four files, changes (a)–(m)**
**Baseline**: HEAD `bd3875d` · nothing committed · backend **1837 / 0 / 45 / 5 / 99.36%** · frontend **823 / 155**
**Targets**: **#33** `MEMO-XML-CONTRACT-NEVER-REQUESTED` · **#34** `CHECKPOINT-POISONS-REDRAFT`
· **#35** (opened **and** closed by this pass, Q3b-A)

> ⚠️ **SUPERSEDED BY EXECUTION, PRESERVED AS WRITTEN**: *"⛔ NOTHING IN THIS FILE HAS BEEN EXECUTED.
> Every count below is a prediction, and this project's record on predictions is documented and poor
> in one direction: Fold-7 predicted +48 and measured +84; the live-LLM-drafting pass predicted +48
> and measured +63. ⚑ Both missed the same way — a plan bullet names an idea; the implementation
> needs several assertions to pin it. Stop-gate 9 therefore requires every variance to be reconciled
> with a stated cause, and ⛔ no test may be trimmed to hit a number."*
>
> ⛔ **IT MISSED THE SAME WAY, FOR THE SAME REASON, A THIRD TIME.** Predicted **+26** (→1863),
> measured **+55** (→**1892**). ⚑ **Its own diagnosis was correct in advance** — see **§0.4**'s table.

---

## 0. ⚑ Execution record — what actually happened

**Executed 2026-09-12** across two sessions. ⚠️ **Stage 1's session was cut off by a usage limit and
logged nothing**; its work was verified from disk and reconstructed at `audit.md`
2026-09-12T12:09:05Z. Stage 2 and the close are recorded at `audit.md` 2026-09-12T12:41:19Z.

### 0.1 ⛔ A STRUCTURAL GUARD FIRED — AND IT WAS NOT ONE OF THIS PLAN'S TEN STOP-GATES

At the §11 gate, **`test_frozen_untouched.py::TestNoFileIsAddedUnderAFrozenUnit::
test_no_frozen_unit_imports_the_composition_root` went RED.** Step 7.5's new test had placed
`from backend.app.offline_memo_double import _RULE_ID_PATTERN` inside
`backend/memo_agent_core/tests/test_prompt_builder.py` — ⛔ **a file in the FROZEN tree importing the
COMPOSITION ROOT.** The guard states the rule itself: *"The dependency arrow points ONE way:
app → units. A unit importing back would make the composition root a dependency of the things it
composes."*

⛔ **THE GUARD WAS RIGHT; THE NEW TEST WAS WRONG. THE GUARD WAS NOT TOUCHED.** The cross-unit
assertion moved to `backend/app/tests/test_offline_double_citation_invariant.py`, where importing
both directions is legitimate; `test_prompt_builder.py` retains only the unit-local property (the
placeholder carries an underscore and no hyphen). ⚑ **A second test came out of the fix**, exercising
both #35 defenses together: the worked example genuinely IS in the prompt, and the extractor
genuinely does not pick it up.

⚠️ **THE POINT WORTH KEEPING, AND IT IS NOT FLATTERING TO THIS PLAN.** ⛔ **This was NOT stop-gate 5.**
Stop-gate 5 (`memo_extensions` Scans 1 and 7) passed **cleanly**, exactly as §6.2 predicted — that
analysis was right. ⚑ **The violation was caught by a PRE-EXISTING guard in the app suite that is not
among this plan's ten numbered stop-gates at all.** This plan anticipated import trouble at the
`memo_extensions` boundary and cleared it; ⛔ **it did not anticipate the frozen unit's own TEST
directory having an import rule.** It held anyway — because someone had written that guard earlier,
for a different reason. **A plan's stop-gates are not the whole safety net, and this pass is the
evidence.**

### 0.2 ⚠️ An unpredicted interaction at step 6.5 — diagnosed BEFORE anything was edited

Two pre-existing tests in `test_submission_routes.py::TestTheOfflineDoubleAnnouncesItself` went RED
on #35's fix: they fed **synthetic bare prompts** carrying **neither marker**, so bounded extraction
correctly returned `""`. ⚑ **The production chain was traced first**: `orchestrator._draft_node` →
`PromptBuilder.build()` → `provider.complete` → `OfflineMemoLLMClient.generate` is the **only** path,
and it **always** emits both markers unconditionally. ⛔ **Stale fixtures asserting the contract this
pass deliberately removed — not a real break.** Re-shaped to real prompt form; ⚠️ **no assertion
weakened**, and #35 is now additionally pinned at that caller.

### 0.3 ⚑ An unpredicted bonus at step 8.5 — asserted, not assumed

`provider_showcase` imports the same `_parse_xml`, so ⛔ **`OllamaAdapter` gained X3 tolerance too —
all THREE adapters, not the two this plan named.** Both adapters are parametrized into the U19
tolerance tests rather than the consequence being left implicit.

### 0.4 ⛔ Variance — predicted +26, measured +55 (+29 over)

| Source | Tests | Why |
|---|---|---|
| `test_orchestrator_redraft.py` (new) | **4** | Q9-D's four layers — ⚑ **exactly as predicted** |
| `test_offline_double_citation_invariant.py` (new) | **11** | 3 `Recommendation` params + empty-report + **2 marker guards** + **3 mirror-equivalence params** + **2 placeholder / both-defenses** |
| `test_parse_tolerance.py` (new, U19) | **20** | 2 adapters × (no-op + **5 wrapper shapes** + still-raises + **2 shape-error cells**) + 2 sharing-identity tests |
| `test_provider.py` (extended) | **+14** | 9 X3 tolerance + 5 for (h) |
| `test_prompt_builder.py` (extended) | **+5** | (j)(k)(l) + constraints-not-weakened + block-is-last |
| `test_submission_routes.py` (extended) | **+1** | #35 pinned at the offline-double caller |
| **Total** | **= 55** | 1837 → **1892** |

⚑ **The cause is the one this plan named in advance, verbatim**: *"a plan bullet names an idea; the
implementation needs several assertions to pin it."* Three bullets did the damage — **parametrization**
(§8.1 listed six shapes; across **two** adapters that is 20), **both-ends bounding** (**two** guard
branches, not one), and **anti-drift** (the mirror and the shared helper are each only enforceable by
a test the plan named as a *property*). ⛔ **No test was trimmed to approach the number** (stop-gate 9).
⚠️ **Stage 1's +4 was EXACT** — the one stage whose test count Q9-D fixed **in advance**, which is
precisely the difference between a bullet naming a count and a bullet naming an idea.

### 0.5 Coverage — read per-module, not from the total

`memo_agent_core` **12/12 at 100%** (283 stmts / 28 branches, **0 missed, 0 partial**) ·
`memo_extensions` **5/5 at 100%** · `offline_memo_double.py` **20 / 0 / 4 / 0 = 100%**.
**Total 99.36% — identical to baseline, not merely close.** ⛔ Thresholds unedited (`git diff
pyproject.toml` empty; frontend config empty); ⛔ **no `# pragma: no cover` added anywhere.**
⚠️ **Variance on `offline_memo_double.py`, cause stated**: predicted *"13/13 or similar"* assuming
**one** guard; there are **two**, because a missing start marker and a missing end marker fail for
different reasons and ⛔ **an unbounded END is exactly what #35 was.**

### 0.6 ⛔ Stop-gate 7 — no fifth frozen file

Exactly four `memo_agent_core` production files modified: `orchestrator.py`, `prompt_builder.py`,
`provider.py`, `telemetry.py`. Test files under `memo_agent_core/tests/**` are covered by
authorization §3.5; every non-frozen file touched appears in §3.6's list.

---

## 1. What is decided, and what is not open

**Decided** (Q1–Q13 + §6's five resolutions + the signed authorization): C2 removes the checkpointer ·
X3 is **subtractive-only** tolerance in **both** parsers · X1 adds a system-prompt sentence **and** an
appended format block with an `EXAMPLE_RULE_ID` placeholder · #35's extraction is bounded at **both**
ends · the shared helper lives in `provider.py` · Q9-D's four-layer regression test · two stages ·
100% held on `memo_agent_core`, `memo_extensions` and `offline_memo_double.py` · X2 deferred with a
register row **and** a note at each parser · all eight design-doc statements back-annotated,
disk-verified.

⛔ **There are NO open gates in this plan.** The reopening is signed; the design questions are answered.
⚑ **This is deliberately unlike `live-llm-drafting-code-gen-plan.md`, which carried two open gates (G1,
G2) into execution.** Everything here was settled upstream, which is why this plan is stages and
stop-gates only.

### 1.1 ⚠️ One thing this plan must not let a reader assume

**#33's fix cannot be proven by this pass's test suite.** X1 changes what is *asked of a model*, and
⛔ **no unit test can verify that a model complies.** The suite can prove the prompt *contains* the
instruction, that the parser *tolerates* what a model plausibly returns, and that nothing regressed.
⚑ **Only §7's live verification can show a real memo.** **#33 is not closed by a green suite**, and
§8 says so.

---

## 2. Stage 1 — #34 / candidate C2

**Register**: #34. **Authorization changes**: **(a)–(e)** + **(m)**. **Files**: `orchestrator.py`
(changed), `telemetry.py` (docstring only), `memo_agent_core/tests/test_orchestrator_redraft.py`
(**new**), plus Q7-A's design-doc back-annotations.

⚑ **Why (m) and the back-annotations land HERE and not in stage 2**: they are false *because of C2*.
Deferring them would leave stage 1 green with the tree asserting a mechanism it no longer has.

### Step 0 — ⛔ THE REOPENING IS APPLIED

The signed authorization takes effect. ⚠️ **Before any edit**: confirm `git status` shows the expected
8 modified / 13 untracked and HEAD `bd3875d`, and record the four frozen files' mtimes — §2.3 of the
authorization notes the freeze is verified out-of-band by mtime scan, so the *before* reading is the
only baseline that exists.

- [x] **0.1** Baseline confirmed; frozen-file mtimes recorded.

### Step 1 — the regression test, written FIRST and observed RED

**File**: `backend/memo_agent_core/tests/test_orchestrator_redraft.py` (**new**).

⚑ **RED-first across the change, not after it.** The test is written against today's tree, where
⛔ **it must FAIL on invoke #2 with the `RuntimeError`** — the reproduction §1.2 of the parent plan
already observed. **That failure IS the bug**, and seeing it is the only proof the test is not vacuous.

Q9-D's four layers, each a separate assertion:

| Layer | Assertion | What it kills |
|---|---|---|
| **(i)** | Both invokes return a **non-`None` `DecisionMemo`** with a valid citation | A test that only asserts "no exception" |
| **(ii)** | `orchestrator._graph.checkpointer is None` | ⛔ A future reintroduction re-masked by a guard elsewhere — **the `3a08dd8` failure mode** |
| **(iii)** | `memo1.memo_hash == memo2.memo_hash` | A re-draft that succeeds but produces a different memo |
| **(iv)** | ⛔ The provider's **call count increments** on invoke #2 | ⚑ **The strawman: an implementation memoizing by `application_id` satisfies (i)+(ii)+(iii)** |

⚠️ **Two construction requirements**, both from §6.3 / the parent plan §1.4: the test builds its **own**
`LangGraphOrchestrator` (never via `case_seams()`, or `@lru_cache(maxsize=1)` leaks state between
tests), and it uses the **existing** `FakeProvider` fixture — ⛔ **no XML, no real client**, which is
what makes stage 1 independent of #33.

- [x] **1.1** Test written. ⛔ **Observed RED on invoke #2 with the exact `RuntimeError`.** Record the message.
- [x] **1.2** ⛔ **STOP-GATE 1** — if it passes on arrival, the harness is wrong. **STOP.**

### Step 2 — (a) + (b): remove the checkpointer

- [x] **2.1** `orchestrator.py:137` — `graph.compile(checkpointer=MemorySaver())` → `graph.compile()`.
- [x] **2.2** `orchestrator.py:25` — remove `from langgraph.checkpoint.memory import MemorySaver`.
- [x] **2.3** Re-run Step 1's test. ⛔ **Observed GREEN, all four layers.**
- [x] **2.4** ⚑ Run the **whole** `memo_agent_core` suite. ⛔ **Expect zero failures** — the parent plan
      §5 verified no test anywhere references the checkpointer, and
      `test_read_only_channel_reducer_raises_on_write` calls `_reject_channel_write` **directly**.
      ⚠️ **A failure here would mean the negative verification was wrong. STOP and report.**

⛔ **`run()`'s `thread_id` config at `:155` is NOT removed** (authorization §3.1). It is inert; leaving
it keeps the diff minimal.

### Step 3 — (c)(d)(e)(m): the four false claims, in source

- [x] **3.1** `orchestrator.py:4-6` — the module docstring. ⛔ **All three justifications are false and
      the correction must say so, not go silent**: *retry loop* (⚑ reproduced working without a
      checkpointer), *durability* (in-process; nothing reads a checkpoint back at all), *100%-step
      tracing* (⚑ `TraceRecorder.on_step` has no production caller).
- [x] **3.2** `orchestrator.py:11-13` — the CON-BR2-STATE seeding claim. ⚠️ **The correction must
      preserve what is still true** (no node returns those keys, so the recommendation cannot change
      inside the graph) **and record why the old claim was believed**: `audit.md:760` shows it was
      affirmatively tested — for the no-checkpoint case, the only one exercised.
- [x] **3.3** `orchestrator.py:48-51` — `_reject_channel_write`'s own docstring. ⚑ **The most
      consequential of the three**: it is what a reader consults when this error fires.
- [x] **3.4** `telemetry.py:7` — change **(m)**. ⛔ **Docstring only.** `MemoTelemetryEvent`'s fields and
      the OBS-1 allowlist are untouched; 18 statements at 100% before and after.

⛔ **`_reject_channel_write`'s BEHAVIOUR is not touched** — only its account of when it can fire.

### Step 4 — Q7-A: back-annotate all eight, then prove it on disk

⚑ **Design owns it** — the `rules-engine` principle (`audit.md:584`), *"FD back-annotated FIRST"*.
⚠️ **Not frozen** (authorization §4.1): `guide-docs/` is outside `FROZEN_UNITS` and `PRODUCTION_FILES`.

| # | File · line | The false clause |
|---|---|---|
| 1 | `nfr-design/logical-components.md:20` | *"**checkpointer YES** / interrupt NO"* |
| 2 | `nfr-design/logical-components.md:42` | *"Langfuse tracing … **Wired externally via the checkpointer**"* |
| 3 | `nfr-design/nfr-design-patterns.md:88` | *"Langfuse 100%-step tracing **via the checkpointer**"* |
| 4 | `nfr-requirements/nfr-requirements.md:122` | *"Langfuse 100%-step tracing **via the checkpointer**"* |
| 5 | `nfr-requirements/tech-stack-decisions.md:13` | *"NFR-MEMO-CITE-FAILURE (**bounded retry via the checkpointer**)"* |
| 6 | `nfr-requirements/tech-stack-decisions.md:61` | *"Langfuse 100%-step tracing … **via the checkpointer**"* |
| 7 | `functional-design/business-logic-model.md:7` | *"the **checkpointer**/interrupt pattern"* |
| 8 | `functional-design/business-logic-model.md:64` | *"## 2. Immutable-recommendation state + the **checkpointer**/interrupt pattern"* |

Each gets a dated `BACK-ANNOTATION` marker naming this pass and #34, in the `domain-entities.md §4.2`
shape. ⚠️ **Rows 2, 3, 4 and 6 carry the Langfuse claim, which was false BEFORE C2** — the
back-annotation must say so, and must **not** imply C2 caused it (§6.4).

- [x] **4.1** All eight back-annotated.
- [x] **4.2** ⛔ **STOP-GATE 2 — disk verification, not a summary.** `grep -n "checkpointer"` across
      `guide-docs/build/memo-agent-core/`; every surviving hit must be inside a back-annotation marker.
      ⚑ **The `rules-engine` precedent required exactly this before approval** (`audit.md:591-593`).

### Step 5 — stage 1 gate

- [x] **5.1** Full backend suite. **Predicted: 1837 → 1841.**
- [x] **5.2** ⛔ `memo_agent_core` **at 100%, all 12 modules** — read the per-module rows, not the total.
- [x] **5.3** Coverage threshold **unedited**; no `# pragma: no cover` added.
- [x] **5.4** Variance reconciled with a stated cause (stop-gate 9).

⚑ **Predicted +4** — one test per Q9-D layer. ⚠️ **This is the prediction most likely to be low**, for
the documented reason: layer (i) alone plausibly needs two assertions (memo returned, citation valid),
and the RED-first harness may need its own non-vacuity pin.

---

## 3. Stage 2 — #33 (X1 + X3) and #35, together

**Registers**: #33, #35. **Authorization changes**: **(f)–(l)**. **Files**: `provider.py`,
`prompt_builder.py`, `memo_extensions/provider_secondary.py`, `app/offline_memo_double.py`,
`scripts/seed_demo_cases.py`, their tests, and `BUILD-COMPLETION-REPORT.md`.

⚑ **Why together** (Q10-C): X1 puts a new token into a prompt whose extraction function is
known-broken. ⛔ **Landing X1 before #35's fix would be actively unsafe**, and the interaction is what
the stage's own tests must cover.

### Step 6 — #35 FIRST, RED-first, and its test is the one that has never existed

⚠️ **#35 is fixed BEFORE X1 is added**, so the extraction is already sound when the worked example
arrives.

- [x] **6.1** Write the citation-invariant test **parametrized over every `Recommendation` value**
      (`APPROVE`, `REFER`, `DECLINE_RECOMMEND`) **plus the ⛔ EMPTY-rule-report case** — ⚑ **the cell
      §6.1's table used to expose that single-ended anchoring leaks the worked example.** Assert
      `first_cited_rule_id(PromptBuilder().build(ai))` is a **member of the handed report's rule ids**,
      or `""` when the report is empty.
- [x] **6.2** ⛔ **Observed RED on `DECLINE-RECOMMEND`**, returning `'DECLINE-RECOMMEND'`. ⚑ **That
      failure is #35**, reproduced by the suite for the first time in this build's history.
      ⚑ **OBSERVED 2026-09-12**, verbatim: `AssertionError: DECLINE-RECOMMEND: extracted
      'DECLINE-RECOMMEND', which is not one of the citable rule ids ['R-AGE-1', 'R-DTI-1'] — a
      fabricated citation`. ⚠️ The other three parametrizations passed — **`APPROVE`/`REFER` by luck
      (no hyphen in their values), not by correctness**, which is the reason for parametrizing.
- [x] **6.3** Fix `offline_memo_double.py`'s `first_cited_rule_id` — ⛔ **bounded at BOTH ends** (§6.1,
      approved at sign-off): search only between the `RULE REPORT (the only citable rules):` marker and
      the `APPLICANT FACTS (non-demographic):` marker. ⚠️ **Marker absent → return `""`** (the guard
      branch that must be covered, §6.3).
- [x] **6.4** Mirror it in `scripts/seed_demo_cases.py:118` — ⚑ *"the two must stay behaviourally
      equivalent"* (`offline_memo_double.py:28-32`). ⚠️ **`backend/scripts/` is in no `--cov=` entry**,
      so this is **tested but not measured** — pre-existing and correct, not an omission.
      ⚑ **Markers kept byte-identical** across the two copies, and equivalence is now **enforced by a
      test** parametrized over every `Recommendation` — ⛔ previously *nothing* enforced it.
- [x] **6.5** Observed GREEN on all four parametrizations.
      ⛔ **AND AN UNPREDICTED INTERACTION — TWO PRE-EXISTING TESTS WENT RED (variance, cause stated).**
      `test_submission_routes.py::TestTheOfflineDoubleAnnouncesItself` fed **synthetic bare prompts**
      (`"... rule DTI-CEIL-1 evaluated ..."`, `"rule AGE-BAND-1 passed"`) carrying **neither marker**,
      so bounded extraction correctly returned `""`. ⚑ **Diagnosed before editing anything**: the
      production chain is `orchestrator._draft_node` → `PromptBuilder.build()` →
      `provider.complete` → `OfflineMemoLLMClient.generate`, a **single** path whose prompt **always**
      carries both markers (emitted unconditionally). ⛔ **Stale fixtures asserting the removed
      unbounded contract — not a real break.** Fixtures re-shaped to real prompt form; ⚠️ **no
      assertion weakened**, and a **new** test (`test_it_does_not_cite_the_RECOMMENDATION_itself`)
      pins #35 at this caller too. In scope as step 6's *"their tests"*.
- [x] **6.6** ⛔ `offline_memo_double.py` **still at 100%** (11/11 → 13/13 or similar). §6.3's approved
      ⚑ **MEASURED: 20 stmts / 0 miss / 4 branch / 0 partial = 100%.** ⚠️ **Variance from the
      predicted "13/13", cause stated**: the plan's figure assumed **one** guard; the implementation
      has **two** (start-marker absent, end-marker absent) because they fail for different reasons and
      ⛔ **an unbounded end is exactly what #35 was**. Two guards + two marker constants + `region_start`
      = +9 statements, not +2, and **4 branch arcs all covered** by the two new guard tests.
      scope extension.

### Step 7 — X1: (j)(k)(l) in `prompt_builder.py`

- [x] **7.1** **(j)** A binding sentence in `_SYSTEM_PROMPT` (`:16-23`) — ⚑ Q1-C's first half: *prevents
      prose entirely*. ⚠️ Must not weaken the three existing constraints.
- [x] **7.2** **(k)** A `REQUIRED OUTPUT FORMAT:` block appended **last** in `build()` — ⚑ Q1-C's second
      half: **exact element names**, because the parser reads `narrative_prose` and
      `./cited_rule_ids/rule_id` by exact path and a well-formed document with other names ⛔ **parses
      to silence**.
- [x] **7.3** **(l)** The placeholder is ⛔ **`EXAMPLE_RULE_ID`** — underscore. ⚑ The regex sweep
      confirmed `EXAMPLE-RULE-ID`, `RULE-ID-HERE`, `XXX-000`, `FILL-IN` all **match** and would be
      mis-cited; `EXAMPLE_RULE_ID` does not. ⚑ `<rule_id>` itself is inherently safe (underscore).
- [x] **7.4** ⛔ **Re-run Step 6.1's test unchanged.** ⚑ **This is the interaction Q10-C staged these
      together for**: with double-ended anchoring the example is outside the search region entirely, and
      with `EXAMPLE_RULE_ID` it could not match even if it were not. **Both defenses independent (§6.1).**
- [x] **7.5** Add a test that the prompt **contains** the format instruction and the element names.
      ⚠️ **This is the honest limit of what a unit test can assert about X1** (§1.1).
- [x] **7.6** ⛔ **STOP-GATE 3** — if Step 6.1's test goes RED here, the example leaked. **STOP.**

⛔ **The two section markers are now LOAD-BEARING** (authorization §3.3): they bound #35's extraction
region and must not be reworded without changing `offline_memo_double.py` in the same commit.

### Step 8 — X3: (f)(g)(i) in `provider.py`, then `provider_secondary.py`

- [x] **8.1** Write the tolerance tests first, in both units. ⚑ **No test anywhere currently references
      `_parse_xml` directly** (verified) — these are the **first** direct exercise of parse behaviour.
      Cases: ```` ```xml ````-fenced valid XML · bare ```` ``` ````-fenced · conversational preamble
      before `<memo>` · trailing text after `</memo>` · ⛔ **genuine prose with no XML at all → still
      raises** · already-clean XML unchanged (the no-op path).
- [x] **8.2** Observed RED.
- [x] **8.3** **(g)** The shared helper as a module-level function in **`provider.py`** — ⚑ §6.2's
      resolution; ⛔ **a new module would be a FIFTH frozen file.** **Subtractive only** (Q4-A): strip
      fences, strip outside the outermost `<memo>`, hand the result to the **same** `fromstring`.
      ⛔ **No regex extraction of values — explicitly rejected by Q4-A.**
- [x] **8.4** **(f)** `GeminiAdapter._parse_xml` calls it.
- [x] **8.5** `memo_extensions/provider_secondary.py`'s module-level `_parse_xml` imports and calls it.
      ✅ **§6.2 verified both import scans pass unchanged** — Scan 1 is scoped to `borderline_router.py`;
      Scan 7 allows unit root `memo_agent_core`. ⚠️ **If Scan 7 goes RED, the analysis was wrong. STOP.**
- [x] **8.6** **(i)** The X2 deferral note at each parser (Q12-C).
- [x] **8.7** Observed GREEN both units.
      ⚑ **STOP-GATE 5 CLEAR — §6.2's analysis was right.** `memo_extensions` **101 passed**, with
      **Scan 1 and Scan 7 green**: Scan 7 allows the `memo_agent_core` root, Scan 1 is scoped to
      `borderline_router.py`. ⚑ **Unpredicted bonus, stated rather than buried**: `provider_showcase`
      imports the same `_parse_xml`, so ⛔ **`OllamaAdapter` gained tolerance too — all THREE
      adapters, not the two the plan named.** Asserted rather than assumed (both adapters are
      parametrized). ⚠️ **Two tests pin the SHARING, not just the behaviour** — a future copy-paste
      of the helper into U19 would keep every behavioural test green while re-creating the drift.

### Step 9 — (h): the silent-empty path

- [x] **9.1** Test first: a **well-formed** document with **wrong element names** (e.g. `<memo_text>`)
      currently yields `prose=""`, `cited=[]` and ⛔ **no exception** — surfacing downstream as *"drafting
      produced no memo"*. Observed RED against the desired named error.
- [x] **9.2** **(h)** Raise a named, diagnosable error when the parsed document contains **neither**
      expected element. ⚠️ **Must remain distinguishable from a model that genuinely cited nothing** —
      that is the whole point (Q13-A).
- [x] **9.3** Observed GREEN. ⚑ **199 passed across both units.** ⚠️ **Q13-A's boundary is pinned by
      its OWN tests, in both units**: an empty `<cited_rule_ids/>` beside real prose is NOT a shape
      error — it is a model that genuinely cited nothing, which ⛔ **`CitationValidator` must block
      on the merits.** Collapsing the two would destroy the distinction (h) exists to draw. The
      error is a `ValueError`, **explicitly not a `ParseError`** (asserted), so *"not XML"* and
      *"XML of the wrong shape"* stay different types. ⚑ Both the helper and the error type are
      **imported** by U19, never redefined — asserted by identity, not by behaviour. ⚑ **X1 is what makes this reachable**: it converts a loud failure
      (not-XML) into a quiet one (wrong-names) unless this lands with it.

### Step 10 — #35's register row, and #33's status

- [x] **10.1** Open **#35** in `BUILD-COMPLETION-REPORT.md` — ⚑ **at stage 2, with its fix** (§6.5,
      approved). The `#24` shape: opened **and** closed in one pass. Must record: pre-existing since
      `51935ac`; **every DECLINE-RECOMMEND case silently landed in `FAILED`**; **zero test coverage**;
      ⚠️ **the same defect class as `DTI-001`, in the file whose docstring records fixing it once**;
      and the duplicate at `seed_demo_cases.py:118`.
- [x] **10.2** ⛔ **Register 34 → 35 tracked.** ⚠️ `guide-state.md` is now stale **by three**; ⛔ **still
      not corrected here** — flagged, per standing direction.
- [x] **10.3** #33: record what the suite proves and what it does **not** (§1.1, §8). ⛔ **Not closed.**
- [x] **10.4** #34: closed on stage 1's evidence, ⚠️ **tier-U only** — no live re-draft yet.
      ⚑ **Row written, and it also records what the closure's evidence is MISSING**: stage 1's
      original stop-gate-1 RED was never logged and is **not reconstructed**. ⚠️ The post-condition
      is independently verified; **that proves the fix works, not that the test once failed.**

⚑ **Register reconciled: 34 → 35 tracked — 22 open · 9 closed/discharged · 4 narrowed.** #35 opens
and closes (+1 tracked, +1 closed), #34 closes (−1 open, +1 closed), #33 stays open.
⚠️ **A finding recorded in #35's row that outlives this pass**: `offline_memo_double.py` stood at
**11/11 statements, 100% — and was still wrong.** ⛔ **The coverage measured the lines, not the
inputs**; no test had ever fed it a `DECLINE-RECOMMEND` prompt.

### Step 11 — stage 2 gate

- [x] **11.1** Full backend suite. **Predicted: 1841 → 1863.**
      ⚑ **MEASURED: 1892 passed / 0 failed / 45 skipped / 5 errors / 99.36%.** Frontend **823 / 155**.
- [x] **11.2** ⛔ 100% held on `memo_agent_core` (12), `memo_extensions` (5), **and
      `offline_memo_double.py`** — per-module rows, not the total.
- [x] **11.3** Thresholds unedited; no `# pragma: no cover` on a reachable branch.
      ⚑ **Verified**: `git diff pyproject.toml` **empty**; frontend coverage config **empty**; ⛔ **no
      `# pragma: no cover` added anywhere by this pass** (diff-checked, plus the three new files).
- [x] **11.4** Frontend **823 / 155 unchanged** — ⚑ nothing in this pass touches the frontend.
      ⚑ **MEASURED: 823 passed / 155 files — EXACT baseline match, zero delta.**
- [x] **11.5** Variance reconciled with a stated cause.
      ⛔ **VARIANCE: predicted +26 (→1863), measured +55 (→1892) — +29 OVER, and in the direction
      this plan named in advance.** ⚑ **Delta BY NAME, and it accounts for all 55:**

      | Source | Tests | Why |
      |---|---|---|
      | `test_orchestrator_redraft.py` (new) | **4** | Q9-D's four layers — **exactly as predicted** |
      | `test_offline_double_citation_invariant.py` (new) | **11** | 3 `Recommendation` params + empty-report + **2 marker guards** + **3 mirror-equivalence params** + **2 placeholder/both-defenses** |
      | `test_parse_tolerance.py` (new, U19) | **20** | 2 adapters × (no-op + **5 wrapper shapes** + still-raises + **2 shape-error cells**) + 2 sharing-identity tests |
      | `test_provider.py` (extended) | **14** | 9 X3 tolerance + 5 for (h) |
      | `test_prompt_builder.py` (extended) | **5** | (j)(k)(l) + constraints-not-weakened + **block-is-last** |
      | `test_submission_routes.py` (extended) | **1** | #35 pinned at the offline-double caller |
      | | **= 55** | |

      ⚑ **THE CAUSE IS THE ONE THE PLAN PREDICTED, VERBATIM**: *"a plan bullet names an idea; the
      implementation needs several assertions to pin it."* Three bullets did the damage:
      **(1) parametrization** — 8.1 said *"cases:"* and listed six shapes; run across **two**
      adapters that is 20, not 6. **(2) both-ends bounding** needed **two** guard branches, not one.
      **(3) anti-drift** — the mirror and the shared helper are each only enforceable by a test that
      the plan named as a property, not as a test.
      ⛔ **NO TEST WAS TRIMMED TO APPROACH THE PREDICTED NUMBER** (stop-gate 9). ⚠️ **Stage 1's +4 was
      exact** — the one stage whose test count Q9-D fixed *in advance*, which is precisely the
      difference between a bullet that names a count and a bullet that names an idea.

---

## 4. Predicted deltas

| Stage | Step | Backend | Notes |
|---|---|--:|---|
| 1 | Q9-D regression test | **+4** | one per layer; ⚠️ **most likely to run low** |
| 2 | #35 citation invariant | **+4** | 3 `Recommendation` values + the empty-report case |
| 2 | X1 prompt assertions | **+2** | instruction present; element names present |
| 2 | X3 tolerance × 2 units | **+12** | 6 cases each: fenced ×2, preamble, trailing, still-raises, no-op |
| 2 | (h) named error | **+2** | wrong-names raises; genuinely-empty citations still distinguishable |
| 2 | (g) helper direct tests | **+2** | subtractive no-op; idempotence |
| **Total** | | **+26** | **1837 → 1863** |

⚠️ **Frontend: 0.** ⛔ **Coverage**: `memo_agent_core` **100%**, `memo_extensions` **100%**,
`offline_memo_double.py` **100%**; global expected to **rise** slightly (new fully-covered statements
against a 99.36% base). ⛔ **Editing a threshold is a stop-gate breach.**

⚑ **Stated plainly**: on this project's record — **+48→+84**, **+48→+63** — **+26 is more likely to be
low than high.** Variance is reconciled, never trimmed.

---

## 5. Stop-gates

| # | Condition | Action |
|---|---|---|
| **1** | Step 1's regression test passes on arrival | ⛔ **STOP** — vacuous harness |
| **2** | A `checkpointer` hit survives outside a back-annotation marker | ⛔ **STOP** — Step 4.2 |
| **3** | Step 6.1's test goes RED after X1 lands | ⛔ **STOP** — the worked example leaked |
| **4** | Any existing `memo_agent_core` test fails at Step 2.4 | ⛔ **STOP** — the negative verification was wrong |
| **5** | `memo_extensions` Scan 7 goes RED at Step 8.5 | ⛔ **STOP** — §6.2's analysis was wrong |
| **6** | A regex-extraction fallback appears in either parser | ⛔ **STOP** — Q4-A's explicit rejection |
| **7** | A **fifth** `memo_agent_core` file is touched, or any other frozen unit | ⛔ **STOP** — outside the signed authorization |
| **8** | A coverage threshold is edited, or `# pragma: no cover` added to a reachable branch | ⛔ **STOP** |
| **9** | Measured deltas differ from §4 | ⚠️ **Reconcile with a stated cause; never trim a test** |
| **10** | `case_lifecycle/` edited, or WIRE-1 amended | ⛔ **STOP** — no such authorization exists |

---

## 6. ⛔ Holds this pass asserts

⛔ **Exactly four frozen files** — `orchestrator.py`, `provider.py`, `prompt_builder.py`,
`telemetry.py`, plus `memo_agent_core/tests/` — **and no other frozen unit**: nothing under `intake/`,
`rules_engine/`, `audit_store/`, `auth_rbac/`, `secrets_config/`, `database/`, `corpus_generator/`,
`quality_gates/`, `admin_cli/`, ⚠️ **`common/`** · ⛔ **`case_lifecycle/` NOT edited — no fifth U24
reopening** · ⛔ **WIRE-1 UNAMENDED — no Fold** · no migration · no `.sql` · no `checksums.json` ·
no `render.yaml` · **coverage thresholds unedited** · `PROJECT-BRIEF.md` unchanged · **frontend
untouched** · **NO COMMIT.**

---

## 7. Manual verification — ⛔ USER-RUN, runs only after both stages are green

✅ **Both stages are green** (backend 1892 / 0 / 45 / 5 / 99.36%; frontend 823 / 155), so this
section is now live. ⛔ **NOT YET RUN.**

⚑ **This walkthrough MERGES two chains that must now be confirmed together**: this pass's §7 (the
**#34** and **#35** checks) and the live-LLM-drafting pass's own **§6** (the full live-Ollama chain,
never completed — it is the run that *found* #33 and #34 and stopped at attempt 2). ⚠️ **They are
merged rather than run separately because #33's fix is what makes the #34 check reachable at all**:
until a draft can succeed, there is no first draft to repeat.

⛔ **TWO STEPS HAVE NEVER ONCE SUCCEEDED IN THIS BUILD'S HISTORY** — **Step 9** (drafting the same
application twice) and **Step 11** (drafting a `DECLINE-RECOMMEND` case through the offline double).
⚑ **Everything before them is prerequisite; those two are the point.**

### 7.0 Prerequisites — confirm all five before starting

| # | Check | Expected |
|---|---|---|
| P1 | A real local **PostgreSQL** is up and `.env` carries real values for the six required vars | `Settings()` constructs at startup (fail-closed otherwise) |
| P2 | **Ollama daemon** running: `ollama list` | ⚠️ must include **`llama3.1:8b-instruct-q4_K_M`** — the exact `OLLAMA_MODEL_ID` in `dependencies.py:131`. A different tag will not be selected |
| P3 | Repo state | HEAD `bd3875d`, **nothing committed** — this pass is uncommitted working tree |
| P4 | Backend launch, **from the repo root** | `MEMO_PROVIDER=ollama python -m uvicorn backend.app.main:app --port 8000` |
| P5 | Frontend, in `frontend/` | `npm run dev` → Vite on **5173**, proxying `/api` → `127.0.0.1:8000` with `/api` **stripped** |

⚠️ **`MEMO_PROVIDER` is read from `os.environ` at composition** (`dependencies.py:124-136`), and the
orchestrator is built behind `@lru_cache(maxsize=1)` — ⛔ **changing it requires a backend RESTART,
never just a new request.**

⚑ **A `curl` session cookie** (R8): `curl -c uw.txt -X POST localhost:8000/login -H "Content-Type:
application/json" -d '{"user_id":"<uw>","password":"<pw>"}'` → **204**. Reuse with `-b uw.txt`.
⚠️ Route numbers below: **R4** = `GET /applications/{id}/memo` · **R7** = `GET /decisions/{id}` ·
**R10** = `POST /applications` · **R11** = `POST /applications/{id}/draft`.

---

### Part A — the live-Ollama drafting chain (register **#33**)

1. ⛔ **Submit a FRESH application through the browser, then draft it from the accepted panel.**
   ⚠️ **A reloaded or seeded case has NO UI draft affordance** (register #2's standing residual) —
   forgetting this reads a working design as broken. **Record the `application_id`.**
2. ⚠️ **Expect the first draft to be SLOW, and do not investigate it.** Two unrelated cold costs
   stack: the **~2.6 s lazy corpus fit** (`dependencies.py:306-309`) **and** the cold Ollama model
   load. ⛔ **A tight timeout here would read a working design as broken.**
3. ⛔ **THE #33 CHECK — read the prose.** It must be **genuinely model-written**, ⛔ **not** the
   `PLACEHOLDER MEMO - GENERATED OFFLINE, NOT BY A LANGUAGE MODEL` text. ⚑ **This is the first time
   in this build's history that a real model's memo prose would reach the screen.**
4. ⛔ **Verify the cited rule ID is REAL** — present in rulebook **1.0.0** (the active version,
   `dependencies.py:248`), ⚠️ **not merely non-empty.** A hallucinated-but-plausible id fails
   `CitationValidator` and surfaces as *"drafting produced no memo"* → 500 — ⚑ **the `DTI-001`
   failure with a new cause.**
5. **`psql`** — `pending_recommendation.model_version` carries all three stamp parts
   (`ollama:llama3.1:8b-instruct-q4_K_M:<12-char digest>`). ⚠️ A `digest-unavailable` tail is
   **tolerated by design**, not a failure.
6. ⚑ **`curl` R4, pre-commit** — `GET /applications/{id}/memo` → `memo.model_version` matches
   `psql` **exactly**, **before any commit**. ⚠️ This is §4.0(i)'s correction: the stamp is
   confirmable **one step earlier** than originally assumed.
7. **Commit through the UI**, then: `psql` `audit_record.model_version` · **`curl` R7**
   (`GET /decisions/{decision_id}`) · confirm the UI history forensic tuple at
   `history-detail-model-version` · confirm the **provider badge**.
8. **The reproducibility probe** — draft the same *profile* twice and compare prose.
   ⛔ **Recorded as an OBSERVATION against register #22, NEVER as a determinism claim**: one
   repetition is not `PROJECT-BRIEF` §5.1's *"same input × 10 runs"*, and ⚠️ **differing prose is a
   FINDING about #22, not a failure of this pass.**

---

### Part B — ⛔ **THE #34 CHECK** (has never once succeeded)

9. ⛔ **Draft the SAME application from Step 1 a SECOND time.**
   - ✅ **PASS**: it returns a **memo**.
   - ⛔ **FAIL**: `RuntimeError: recommendation/confidence are read-only channels (CON-BR2-STATE);
     no node may write them`.
   - ⚠️ **If it fails, the message ACTIVELY MISDIRECTS.** It names CON-BR2-STATE and reads as a
     governance breach — ⛔ **nothing of the sort has happened.** Per `orchestrator.py:48-51`'s new
     diagnostic: **if `current == update` and no node returns those keys, suspect a REINTRODUCED
     CHECKPOINTER**, not a CON-BR2-STATE violation.
   - ⚑ **Why this is now expected to pass**: the graph is compiled bare (`graph.compile()`), so a
     second invoke on the same `application_id` thread has no checkpoint to restore.
   - ⚠️ **The honest scope of a pass**: it lifts #34 from **tier-U** to live-confirmed. It does
     **not** make the memo prose reproducible — that is #22, Step 8.

---

### Part C — ⛔ **THE #35 CHECK** (has never once succeeded)

⚠️ **This step runs on the OFFLINE DOUBLE, not Ollama** — #35 lives in `offline_memo_double.py`.

10. **Stop the backend. Restart it with `MEMO_PROVIDER` UNSET.** ⛔ A restart is mandatory
    (`@lru_cache(maxsize=1)`).
11. ⛔ **Submit a FRESH application whose evaluation yields `DECLINE-RECOMMEND`, and draft it.**
    ⚑ **A profile that triggers exactly one `decline_fail`, so the citation is unambiguous** —
    `DTI-CEIL-1` (acceptable = `dti <= 0.40`, and `dti = existing_debt / income`):

    | Field | Value | Effect |
    |---|---|---|
    | `verifiable_income_annual` | **1000000** | ✅ clears `IRDAI-INCOME-FLOOR-1` (≥ 120000) |
    | `existing_debt_obligations_annual` | **500000** | ⛔ **`dti = 0.5000 > 0.40` → `DTI-CEIL-1` FAILS → `decline_fail`** |
    | `requested_cover_amount` | **5000000** | > 0, and 5× income so `INCM-CEIL-1` (≤ 12×) passes |
    | age (via DOB) | **in 18–65** | clears `AGE-BAND-1` |

    ⚑ **Any one `decline_fail` dominates the aggregation** (`aggregator.py`: *"any `decline_fail` ⇒
    DECLINE-RECOMMEND"*), so the recommendation will be `DECLINE-RECOMMEND` regardless of how many
    `refer_trigger`s also fire.
    - ✅ **PASS**: it **produces a memo**, and the cited rule id is a **real rulebook id** —
      expected **`DTI-CEIL-1`**.
    - ⛔ **FAIL**: the case lands in **`FAILED`** with no memo, and/or the cited id is the literal
      string **`DECLINE-RECOMMEND`** — ⚑ **that is #35 exactly, and it is what used to happen every
      single time, silently, with no error and no log line.**
12. ⛔ **Confirm the `EXAMPLE_RULE_ID` placeholder did NOT leak.** The drafted memo's citation must
    **never** be `EXAMPLE_RULE_ID`. ⚑ Two independent defenses should each prevent it — the prompt's
    format block sits **after** the `APPLICANT FACTS` marker (outside the search region), **and** the
    underscore makes it unmatchable by the rule-id regex. ⚠️ **A leak here would mean BOTH failed.**

---

### Part D — failure modes and the fail-safe

13. **Restart with `MEMO_PROVIDER=ollama`, then STOP the Ollama daemon and draft.**
    ✅ Expect a **500 IN THE ENVELOPE** naming the host (`could not reach the Ollama daemon at
    http://127.0.0.1:11434: …`), ⛔ **not a bare plain-text 500** (that would be register **#32**).
14. **Confirm the cap message is DIFFERENT from the unreachable message** — `OllamaCallCapExceeded`
    must read as *"the application declining to re-enter the model"*, ⚑ **never as an outage.**
    ⚠️ The two are deliberately separate named types; collapsing them is the defect the split exists
    to prevent.
15. ⛔ **THE FAIL-SAFE — unset `MEMO_PROVIDER`, restart, draft.** It must fall back to the **offline
    double**, stamped `OFFLINE-DOUBLE-NOT-A-REAL-LLM`. ⚑ **Ollama is OPT-IN (Q9 C), and this is the
    check that proves an unconfigured deployment never silently reaches a model.**

---

### 7.1 What to record — ⛔ and what a pass does NOT entitle anyone to claim

**Record per step**: pass/fail, the `application_id`, the exact cited rule id, the full
`model_version` string, and **verbatim** any error text.

| If this passes | Then this is true | ⛔ And this is STILL NOT true |
|---|---|---|
| Steps 3–4 | A real model produced a parseable, correctly-cited memo | **#33 is closeable** — ⚠️ but one successful call is not a compliance guarantee; state it as *"first live memo"*, not *"the model always complies"* |
| Step 9 | **#34 lifts from tier-U to live-confirmed** | Memo prose is **not** thereby reproducible — that is **#22** |
| Step 11 | **#35 lifts from tier-U to live-confirmed** | Nothing about the Gemini path — ⛔ **#18 gap (iii) does NOT move**; the showcase provider is not the production client |
| Step 8 | An **observation** about #22 | ⛔ Differing prose is a **finding about #22**, not a failure of this pass |
| All 15 | The wiring is proven end-to-end | ⛔ **`PROJECT-BRIEF` §5.1's "same input × 10 runs" has still not been run** |

⛔ **If any step fails, STOP and report it rather than adjusting the run to get past it.** ⚑ The two
never-succeeded steps are exactly the ones where a workaround would destroy the evidence.

---
## 8. ⚠️ What this pass explicitly does NOT do

* ⛔ **Does not close #33 on a green suite.** ⚑ **No unit test can prove a model complies with an
  instruction** (§1.1). Only §7 steps 3–4 can. **A green suite means the ask is present and the parser
  is tolerant — not that live drafting works.**
* ⚠️ **Closes #34 at tier-U only** until §7 step 5 runs.
* ⛔ **Does not close #18.** Gap (iii) moves only on a live memo through the request path.
* ⛔ **Does not close #22** — nothing touches the sampling stack.
* ⛔ **Does not fix #32** — the envelope capability is untouched.
* ⛔ **Does not take X2** — a JSON wire-format migration needing a `PROJECT-BRIEF` §3/§9 amendment.
* ⛔ **Does not correct `observability/`'s docstrings** (§6.4) — recorded, owned by OBS-SINK-DEFERRED.
  ⚑ The finding it contributes — **`TraceRecorder.on_step` has no production caller at all** — goes to
  the close-out.
* ⚠️ **Does not correct `guide-state.md`'s register count** — which this pass makes stale **by three**.
* ⛔ **Does not commit.**
