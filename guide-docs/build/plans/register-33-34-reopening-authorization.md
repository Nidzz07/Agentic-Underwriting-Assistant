# `memo_agent_core` — ⛔ **FIRST AUTHORIZED REOPENING OF A FROZEN UNIT'S SOURCE LOGIC** (request)

**Artifact type**: standalone reopening authorization — **not** an execution plan, **not** a code-gen plan
**Status**: ✅ **APPROVED 2026-08-24 (§6). `memo_agent_core`'s FIRST reopening is authorized as scoped
in §3 — four files, thirteen changes (a)–(m) plus §3.5's tests, nothing beyond.** Execution proceeds
via a separate code-gen plan, with the reopening as **step 0**. ⛔ **NO FROZEN FILE TOUCHED YET.**
Superseded status lines, preserved: *"⛔ RE-ISSUED 2026-08-24 WITH §3 FINALIZED. AWAITING EXPLICIT
WRITTEN SIGN-OFF."* · *"⛔ AWAITING EXPLICIT WRITTEN SIGN-OFF … §3's file list is contingent on
Question 6 … presented for review, not for signature in its current state."*
**Date**: 2026-08-24 (drafted) · **Re-issued**: 2026-08-24 (§3 finalized against the answers)
**Approved design**: `register-33-34-combined-plan.md` — ✅ **all thirteen questions answered**
(**Q1-C · Q2-A · Q3a-A · Q3b-A · Q4-A · Q5-B · Q6-C · Q7-A · Q8-B · Q9-D · Q10-C · Q11-C · Q12-C ·
Q13-A**), ambiguity check **CLEAN** (§6), with three resolutions folded in below (§6.1, §6.2, §6.3)
**Procedural precedent**: `register-27-reopening-authorization.md` — U24's fourth reopening; the shape
of this document (standalone approval, exhaustive file list, applied as step 0 of a separate execution pass)
⛔ **Class precedent: NONE. See §2 — this is a first.**

> ✅ **RESOLVED AT SIGN-OFF — the four-file scope was put to the approver explicitly and approved.**
> *"Confirmed — the file list is four, not three. … My original direction was based on an incomplete
> framing, not the correct scope."* The section below is **preserved as written** because it is the
> record of what was surfaced and why. ⚑ **Preserved text follows:**
>
> ⚠️ **ONE THING CHANGED FROM WHAT THE APPROVING DIRECTION EXPECTED, AND IT IS STATED FIRST BECAUSE IT
> AFFECTS THIS DOCUMENT'S HEADLINE CLAIM.** The direction asked that §3 be finalized *"confirming file
> list stays at exactly three files, per Q6=C."* ⛔ **It does not stay at three — it is FOUR.**
> **Q8-B** independently authorizes correcting `telemetry.py`'s docstring, and `telemetry.py` is a
> `backend/memo_agent_core/` file. ⚑ **The two answers do not contradict**: Q6's options enumerated
> only the files carrying *code* changes, and Q8 is the question that governs docstrings.
> ⚠️ **`telemetry.py` is a ZERO-STATEMENT entry** — one docstring line, no behaviour, no coverage
> effect (§3.4). **See the combined plan §6.7.** ⛔ **This document is written with four files
> because writing it with three would silently override an explicitly-answered question. If three is
> preferred, strike §3.4 at signature — but as a decision, not an inference.**

---

## 1. What is being requested

Authorization to modify **four files inside `backend/memo_agent_core/`**, a **FROZEN_UNITS member**, to
remediate register **#33 `MEMO-XML-CONTRACT-NEVER-REQUESTED`** and **#34 `CHECKPOINT-POISONS-REDRAFT`**,
both opened 2026-08-19 (`BUILD-COMPLETION-REPORT.md:1606-1674`) and both **blocking**: #33 blocks live
drafting on **every** provider; #34 blocks re-drafting on any application within a process lifetime.

⚑ **A third defect — register #35, to be opened by this pass (Q3b-A) — is remediated alongside them
but requires NO frozen-unit authority**: its fix lands in `backend/app/offline_memo_double.py` and
`backend/scripts/seed_demo_cases.py`, neither of which is frozen (§3.6).

**This document authorizes the reopening only.** The execution/code-gen plan is a **separate**
artifact, written **after** this is signed off.

✅ **Both prerequisites named in the drafted version were met, and the document is now SIGNED** (§6):
the thirteen questions are answered, the ambiguity check is clean, and the four-file scope was
confirmed explicitly. ⛔ **What remains is the code-generation plan's own separate approval.**

---

## 2. ⛔ Prior reopenings — and why this is **NOT** the fifth

⚠️ **This section exists because the obvious framing is wrong, and the wrong framing would understate
what is being asked for.**

This project has authorized **four** prior reopenings. **All four were `case_lifecycle` (U24)**:

| # | Reopening | Unit | Reason |
|---|---|---|---|
| 1 | `list_application_ids()` | `case_lifecycle` | no enumeration primitive existed (Scope B wiring, Q1-A) |
| 2 | `memo_from_canonical()` | `case_lifecycle` | no memo rehydration existed anywhere in the build |
| 3 | the two-step commit claim | `case_lifecycle` | register **#19**'s fix |
| 4 | `pipeline.py` / `repository.py` / `fixtures.py` | `case_lifecycle` | registers **#27** + **#28** |

⛔ **`case_lifecycle` is NOT a member of `FROZEN_UNITS`.** `test_frozen_untouched.py:21-24` defines it as
a set of exactly **eleven** `backend/<unit>/` directory names:

```python
FROZEN_UNITS = {
    "intake", "rules_engine", "memo_agent_core", "audit_store", "auth_rbac",
    "secrets_config", "database", "corpus_generator", "quality_gates", "admin_cli", "common",
}
```

⚑ **`memo_agent_core` is a member. `case_lifecycle` is not.** `register-27-reopening-authorization.md` §2
states this in writing, and this document adopts its finding verbatim:

> ⚑ **Honesty note.** `case_lifecycle` is **NOT** in `test_frozen_untouched.py`'s `FROZEN_UNITS` set — that
> guard covers the original eleven units. **U24's frozen status is a project-convention and authorization
> discipline, not a mechanically enforced one.** No test will fail if this authorization is exceeded.
> **This document is the only real control**, which is why its file list is exhaustive and why anything
> outside it must come back for a fresh request.

### 2.1 ⛔ The distinction, stated so it cannot be conflated

**The four prior reopenings supply a PROCEDURAL shape and NOT a class precedent. These are different
claims.**

| | What the prior reopenings establish | What they do **not** establish |
|---|---|---|
| ✅ **Procedural** | The **shape** to copy: a standalone authorization, written and signed **before** any code; an **exhaustive** file list; **named reasons per change**; applied as **step 0** of a separate execution pass | — |
| ⛔ **Class** | — | ⛔ **That a FROZEN_UNITS member's source logic has ever been reopened.** It has not. **This would be the first.** |

⚠️ **A future reader must not read this document as "the fifth reopening."** It is the **first of its
kind** and the **fifth by procedure**.

### 2.2 ⚑ The claim is proven by git history, not asserted

`git log` over each frozen unit's tree, at `bd3875d`:

| Unit | Commits | Detail |
|---|--:|---|
| `intake` · `rules_engine` · **`memo_agent_core`** · `audit_store` · `auth_rbac` · `secrets_config` · `corpus_generator` · `quality_gates` · `admin_cli` · `common` | **1** each | `51935ac` — *"BUILD phase: 24 units, frontend, deploy config, and the full design record"*. ⛔ **Never modified since.** |
| `database` | **2** | `51935ac` + `d6a6876`. ⚑ **Purely additive**: `0003_auth.sql` (new file) + one line of `checksums.json` + one line each in **three test files**. ⛔ **No `.py` source module modified.** Authorized at login/signup **Q9(a)**. |
| ⚑ **`case_lifecycle`** — *not frozen* | **2** | `51935ac` + **`3a08dd8`** — the #27/#28 **source** fix, i.e. the fourth reopening. |

⛔ **Precise claim, at exactly the strength the evidence supports**: **no `.py` source module under any
FROZEN_UNITS member has ever been modified.** ⚠️ **A frozen unit's tree has been written into once**
(`d6a6876`, additive, authorized) — so the claim is about **source logic**, not about the tree being
untouched. **The one post-build source-modifying commit belongs to the one unit that is not frozen.**

### 2.3 ⚠️ What the freeze actually is — stated so this document does not overstate its own significance

`test_frozen_untouched.py`'s own docstring (`:6-7`) says the suite asserts *"the half that is checkable
from inside the suite"* and that ⛔ **the "no file edited" half is verified out-of-band by an mtime scan**,
reported at the gate. Its five assertions check that `backend/app/` re-declares no frozen symbol, that the
three `COMPOSED_UNITS` are imported, that `backend/app/` owns no persistence, that `backend/app/` is the
only tree it owns, and that no frozen unit imports back into `backend/app/`. ⛔ **None of them detects an
edit to a frozen unit's source.**

⚑ **So `memo_agent_core`'s freeze is the same kind of control `case_lifecycle`'s is: authorization
discipline, not mechanical enforcement.** ⚠️ **This does not make the reopening smaller — it makes this
document load-bearing.** Nothing will fail if §3 is exceeded. **§3 is the control.**

---

## 3. ⛔ FROZEN files this reopening covers — exhaustive and FINAL

✅ **Finalized against the answered questions.** Four files, **thirteen changes (a)–(m)**, nothing beyond.

### 3.1 `backend/memo_agent_core/orchestrator.py` — register **#34** (Q6-C, Q8-B)

| Change | Where | Authority | Why |
|---|---|---|---|
| **(a)** `graph.compile(checkpointer=MemorySaver())` → `graph.compile()` | `_build_graph`, `:137` | **#34**, **Q6-C**, candidate **C2** | ⛔ **The root cause.** A restored channel is not `MISSING`, so seeding takes the reducer branch and `_reject_channel_write` fires on the **seed**. ⚑ **Reproduced both ways**: with the checkpointer, invoke #2 raises; without it, invokes #1–#3 each return a memo. |
| **(b)** Remove `from langgraph.checkpoint.memory import MemorySaver` | `:25` | consequence of (a) | An unused import of the removed mechanism. ⚑ Removes one **covered** statement — see §5's coverage row. |
| **(c)** Correct the module docstring's checkpointer claims | `:4-6` | **#34**, **Q8-B** | ⛔ **All three stated justifications are false**: *"retry loop"* (⚑ reproduced working **without** a checkpointer), *"durability"* (`MemorySaver` is in-process and nothing reads a checkpoint back **at all**), *"100%-step tracing"* (⚑ `TraceRecorder.on_step` has **no production caller**). |
| **(d)** Correct the CON-BR2-STATE seeding claim | `:11-13` | **#34**, **Q8-B** | *"LangGraph does not run the reducer on the initial input"* is true **only** for a thread with no checkpoint. ⚑ `audit.md:760` records this was affirmatively tested at build time — **for the no-checkpoint case, which was the only one exercised.** |
| **(e)** Correct the same claim in `_reject_channel_write`'s docstring | `:48-51` | **#34**, **Q8-B** | The identical false premise, restated at the reducer itself. ⚠️ **This is the docstring a future reader consults when this error fires**, so it is the most consequential of the three. |

⛔ **`_reject_channel_write`'s BEHAVIOUR is NOT touched.** It still raises on any node write; CON-BR2-STATE
is unchanged in substance. ⚑ **Only its docstring's account of *when* it can fire is corrected.**

⛔ **`run()`'s `thread_id` config (`:155`) is NOT removed.** With no checkpointer it is inert, and leaving
it costs nothing while keeping the diff minimal. ⚠️ **If review prefers it removed, that is an amendment
to this table, not an inference from it.**

### 3.2 `backend/memo_agent_core/provider.py` — register **#33** (Q4-A, Q5-B, Q12-C, Q13-A)

| Change | Where | Authority | Why |
|---|---|---|---|
| **(f)** Tolerant pre-parse in `GeminiAdapter._parse_xml` | `:65-70` | **#33**, **Q4-A**, candidate **X3** | ⛔ **Zero tolerance today.** ⚑ **Q4-A scopes this to SUBTRACTIVE ONLY** — strip Markdown fences, strip text outside the outermost `<memo>` — then the **same** parse against the **same** element paths. ⛔ **Its worst case is that it strips nothing and fails exactly as today.** ⚠️ **The regex-extraction fallback is explicitly REJECTED by Q4-A** and must not appear. |
| **(g)** Module-level shared stripping helper, imported by `memo_extensions` | new module-level function in **this file** | **Q5-B** + combined plan **§6.2** | ⚑ **§6.2 resolved the fork the answer left open**: Q5-B says *"in `memo_agent_core`"* but not in which module. ⛔ **A new module would be a FIFTH frozen file**; `provider.py` is already in this list and is the home of the parser it serves. ✅ **§6.2 verified both `memo_extensions` import scans pass unchanged** — Scan 1 is scoped to `borderline_router.py` only; Scan 7 allows unit root `memo_agent_core`. |
| **(h)** Named, diagnosable error when a well-formed document contains **neither** expected element | `:67-69` | **Q13-A** | ⛔ **X1 makes this reachable.** Today a prose answer raises loudly; after X1 the residual failure becomes *"XML with the wrong names"*, which parses to `prose=""`, `cited=[]` and surfaces as *"drafting produced no memo"* — ⚠️ **the same uninformative message `DTI-001` and #35 already produce. Three causes, one message.** |
| **(i)** Deferral note recording that candidate **X2** was consciously not taken | at `_parse_xml` | **Q12-C** | ⚑ For the reader of `_parse_xml` who wonders why tolerance was hand-rolled instead of asking the SDK for a schema. ⚠️ **X2 is a JSON wire-format migration requiring a `PROJECT-BRIEF` §3/§9 amendment** — not a config flag. |

⛔ **`GeminiAdapter.complete`'s signature, `_PRODUCTION_TEMPERATURE`, and the `LLMClient` Protocol are NOT
touched.** TEMP0-1 and the injected-seam shape are unchanged.

### 3.3 `backend/memo_agent_core/prompt_builder.py` — register **#33** (Q1-C, Q2-A)

| Change | Where | Authority | Why |
|---|---|---|---|
| **(j)** Binding output-format sentence in `_SYSTEM_PROMPT` | `:16-23` | **#33**, **Q1-C**, candidate **X1** | ⛔ **The root cause of #33.** ⚑ **Confirmed by probing the live daemon with the exact prompt this file produces**: the model returned a well-formed **Markdown** memo beginning `**ADVISORY MEMO**`. **The model behaved correctly; it was never told to emit XML.** ⚑ Q1-C's reasoning: this half **prevents prose entirely**. |
| **(k)** `REQUIRED OUTPUT FORMAT:` block appended **last** in `build()`, naming the exact element names | `:34-50` | **#33**, **Q1-C** | ⚑ Q1-C's second half: the parser reads `narrative_prose` and `./cited_rule_ids/rule_id` by **exact path**, so an instruction without names admits a well-formed document that ⛔ **parses to silence**. |
| **(l)** ⛔ The worked example's `<rule_id>` placeholder is **`EXAMPLE_RULE_ID`** | within (k) | **Q2-A** | ⚠️ **A live correctness hazard, not styling.** `offline_memo_double.py:46`'s regex matches `EXAMPLE-RULE-ID`, `RULE-ID-HERE`, `XXX-000`, `FILL-IN` — ⛔ **and this build's own `NOT-QUALITY-GATED` and `OFFLINE-DOUBLE-NOT-A-REAL-LLM` stamps.** It does **not** match `EXAMPLE_RULE_ID`. ⚑ **The element name `<rule_id>` is inherently safe (underscore); the hazard is solely the placeholder VALUE.** |

⛔ **`_SYSTEM_PROMPT`'s existing three constraints are NOT weakened** — advisory-only language, the
read-only recommendation, and cite-only-listed-rules stay exactly as written. ⛔ **The deliberate
exclusion of demographics (`:48`) is NOT touched** — bias-free-by-design is unchanged. ⛔ **The two
section markers `RULE REPORT (the only citable rules):` and `APPLICANT FACTS (non-demographic):` become
LOAD-BEARING** under §6.1's resolution (they bound #35's extraction region) and **must not be reworded**
without updating `offline_memo_double.py` in the same change.

### 3.4 ⚠️ `backend/memo_agent_core/telemetry.py` — **DOCSTRING ONLY** (Q8-B)

⛔ **This is the fourth file, and the one the approving direction did not expect.** See the banner
above and combined plan **§6.7**.

| Change | Where | Authority | Why |
|---|---|---|---|
| **(m)** Correct *"Langfuse 100%-step tracing is wired by `observability` (reference-not-own) **via the graph checkpointer**"* | `:7` | **Q8-B** | ⛔ After (a) there is no graph checkpointer, so this line would name a removed mechanism **inside its own unit**. ⚑ Q8-B's stated reasoning: *"would otherwise leave a dangling reference to a removed mechanism inside the very unit being reopened."* |

⚑ **ZERO statements. Zero behaviour. Zero coverage effect.** `telemetry.py` is 18 statements at 100%
and stays 18 statements at 100%. ⛔ **Nothing but the docstring is touched** — `MemoTelemetryEvent`'s
field set and the emit-only allowlist (OBS-1) are untouched.

### 3.5 `backend/memo_agent_core/tests/**` — new and extended tier-U tests (Q9-D, Q11-C)

⚠️ **New test files under a frozen tree are part of the reopening**, exactly as `register-27`'s change
**(f)** treated them.

| Change | Authority | Why |
|---|---|---|
| **#34's regression test — all four Q9-D layers** | **Q9-D** | ⛔ (i) a **memo returned on both invokes**, not merely no exception; (ii) a **structural** assertion that the compiled graph has no checkpointer — ✅ **verified available**: `compiled.checkpointer` is `None` when compiled without one in `langgraph 1.2.7`; (iii) **`memo_hash` equality** across invokes; (iv) ⛔ **a provider call-count non-vacuity guard** — ⚑ **the layer that kills the strawman**, an implementation memoizing by `application_id` would satisfy (i)+(ii)+(iii) while reintroducing the defect in another form. |
| **Tests for (f)–(l)** | **Q4-A · Q11-C · Q13-A** | Every X3 branch — fence-stripped, preamble-stripped, still-fails, and (h)'s named error — must be covered (§5's coverage row). ⚠️ **The test must build its OWN orchestrator**, never reach through `case_seams()`, or `@lru_cache(maxsize=1)` leaks state between tests. |
| ⛔ **A prompt/citation invariant test parametrized over EVERY `Recommendation` value** | **Q2-A · Q3a-A · §6.1** | ⚑ **The absence of exactly this test is why #35 shipped.** It must include the ⛔ **empty-rule-report** case — **the cell §6.1's table used to expose that single-ended anchoring leaks the worked example.** |

### 3.6 Files touched that are **NOT** frozen — listed for completeness, **not authorized here**

| File | Change | Frozen? |
|---|---|---|
| `backend/memo_extensions/provider_secondary.py` | X3 tolerance in the shared module-level `_parse_xml` (`:47-55`) serving **both** adapters, importing (g)'s helper; plus Q12-C's deferral note | **No** — `memo_extensions` is not in `FROZEN_UNITS` |
| `backend/app/offline_memo_double.py` | ⛔ **#35's fix** — `first_cited_rule_id` bounded to the rule-report region at **BOTH** ends (§6.1) | **No** — the composition root |
| `backend/scripts/seed_demo_cases.py` | the same fix to `_first_cited_rule_id` (`:118`) — ⚑ *"the two must stay behaviourally equivalent"* (`offline_memo_double.py:28-32`) | **No** — a script, ⚠️ **outside every `--cov=` root**, so tested but not measured |
| `guide-docs/**` | this document, the plan, **#35's register row (written at stage 2, §6.5)**, `audit.md`, `guide-state.md`, and ⚠️ **Q7-A's back-annotation of all eight false statements across five design documents** | **No** — ⚑ see §4.1 |

---

## 4. What this authorization does **NOT** cover

Anything not listed in §3 requires a **fresh request**. Explicitly excluded:

- ⛔ **No other frozen unit.** `intake/`, `rules_engine/`, `audit_store/`, `auth_rbac/`,
  `secrets_config/`, `database/`, `corpus_generator/`, `quality_gates/`, `admin_cli/` and — ⚠️
  **specifically** — **`common/`** are untouched. ⚑ **Q5-B is what keeps `common/` out**: Q5-C would
  have required it and was rejected for exactly this reason.
- ⛔ **No fifth `memo_agent_core` file.** `schemas.py`, `assembler.py`, `citation_validator.py`,
  `constants.py`, `input_builder.py`, `memo_hash_adapter.py`, `missing_info.py` are untouched.
  ⚑ **§6.2's resolution — the helper goes in `provider.py` — is what prevents a fifth.**
- ⛔ **`case_lifecycle/` is NOT touched.** ⚑ **There is no fifth U24 reopening in this pass.**
- ⛔ **No behavioural change to `_reject_channel_write`.** CON-BR2-STATE stands exactly as built.
- ⛔ **No change to `MEMO_CITATION_RETRY_CAP` or the retry topology.** ⚑ **Reproduced**: the
  `add_conditional_edges` cycle works with no checkpointer — 2 provider calls, finalized memo.
- ⛔ **No candidate X2** (Q12-C). No `response_schema`, no `format=`, no JSON. ⚠️ A **wire-format
  migration** requiring a `PROJECT-BRIEF` §3/§9 amendment.
- ⛔ **No regex-extraction fallback in either parser** (Q4-A's explicit rejection).
- ⛔ **No WIRE-1 change, no Fold.** No route, status code, or response shape is altered.
- ⛔ **No migration, no schema change, no `.sql`, no `checksums.json`.** Therefore **no new entanglement
  with register #26.**
- ⛔ **No coverage threshold edited, and no `# pragma: no cover` on a reachable branch** (Q11-C).
- ⛔ **No `observability/` change** (Q8-B's explicit rejection of C) — a different unit, owned by
  **OBS-SINK-DEFERRED**. ⚠️ **See §4.2 for the asymmetry this deliberately leaves.**
- ⛔ **#33, #34 and #35 are NOT closed by this authorization** — only by the executed fix **plus**
  verification, which for #33 means a real memo produced live through the request path.

### 4.1 ⚑ Why `guide-docs/build/memo-agent-core/` needs **no** authority from this document

* `FROZEN_UNITS` is a set of **`backend/<unit>/` directory names** (`test_frozen_untouched.py:21-24`).
* `PRODUCTION_FILES` is `APP_ROOT.rglob("*.py")` where `APP_ROOT` is **`backend/app/`** (`:14`, `:16`).

⛔ **Neither reaches `guide-docs/` at all.** Q7-A's back-annotation is an ordinary documentation edit
needing **no reopening authority**. ⚑ **It is nevertheless a real decision with a clean precedent**:
this project back-annotated `intake`, `rules-engine` and `auth-rbac` design docs (**all three
FROZEN_UNITS members**) and **declined** to for `memo_agent_core` itself when *"the frozen signature
[was] preserved"* (`audit.md:760`). **The operative test is whether the document would otherwise state
something false** — and C2 makes **eight** statements false across five documents. ⚠️ **Q7-A requires
disk verification (grep evidence, not a summary) before approval**, per the `rules-engine` precedent
at `audit.md:591-593`.

### 4.2 ⚠️ The asymmetry Q8-B deliberately leaves — named, not discovered later

On completion this build will say two different things about one mechanism: memo-agent-core's design
record and `telemetry.py` will state tracing is **not** wired via the checkpointer, while
`observability/trace.py:6,57,64` will still describe `on_step` as *"the graph-checkpointer callback
adapter."* ⛔ **This is correct by unit ownership** — `observability` has its own design record and its
docstrings are wrong about something **this pass did not cause** (OBS-SINK-DEFERRED). ⚑ **The finding
this pass contributes is stronger than what that deferral currently records: `TraceRecorder.on_step`
has NO production caller at all.** Carried to the close-out as a named, owned observation so it is not
silently dropped — the failure `#30` and `#31` were opened late to record.

---

## 5. Risk assessment

| Risk | Assessment |
|---|---|
| **Anything consumes the checkpointer** | ✅ **No.** ⚑ Repo-wide grep: **no** `get_state`, `update_state`, `get_state_history`, `.stream(`, `astream` or `interrupt` anywhere. The only `MemorySaver`/`checkpointer`/`thread_id` references in production code are the **three inside `orchestrator.py` itself**. **No test references any of them.** |
| **Tracing regresses** | ✅ **Cannot.** ⚑ `TraceRecorder.on_step` is called by **five observability unit tests and nothing else**. ⛔ **Tracing was never connected through the checkpointer**, so removing it regresses nothing. |
| **The retry loop regresses** | ✅ **Reproduced with no checkpointer**: bad-then-good provider → **2 provider calls, finalized memo.** The cycle is plain `add_conditional_edges` state. |
| **CON-BR2-STATE weakens** | ✅ **Untouched.** ⚑ The change removes the condition under which the reducer fired on a **SEED** — i.e. it removes **false** positives, not real ones. ⚠️ **Q9-D's structural assertion is what pins this**, or the removal is indistinguishable from a weakening. |
| **X3 masks a real failure** | ⚠️ **Bounded by design.** Q4-A is **subtractive only**; ⛔ **its worst case is that it strips nothing and fails exactly as today.** The citation-inventing fallback is explicitly rejected. |
| **Existing tests pin the behaviour being changed** | ⚑ **No test anywhere references the checkpointer, `MemorySaver` or `thread_id`**; every orchestrator test builds a fresh instance and calls `run()` **exactly once**. ⚠️ `test_read_only_channel_reducer_raises_on_write` calls `_reject_channel_write` **directly**, so it is unaffected by (a) and stays green. Expect **additions**. |
| **Coverage** | ⚠️ **Corrected from the premise this pass was handed.** ⛔ There is **one global `--cov-fail-under=90`** and **no per-unit gate**; `memo_agent_core`'s 100% is **observed, not enforced**. ⚑ **§6.3 verified stage 1 is net-subtractive — no intermediate dip.** Q11-C holds `memo_agent_core` + `memo_extensions` + ⚠️ **`offline_memo_double.py`** (§6.3's scope extension; currently 11/11 at 100% and edited by #35's fix). |
| **A fifth file creeps in** | ✅ **Closed by §6.2** — the shared helper goes in `provider.py`, not a new module. ⚠️ **This was a live risk**: Q5-B named the unit but not the module. |
| **Overreach** | ⛔ **NOT mechanically detectable** (§2.3) — no test fails if §3 is exceeded. Mitigated by §3's exhaustive list and a `git status` + `git diff --stat` review at the execution gate. ⚑ **Identical to `register-27`'s §5 mitigation.** |
| ⚠️ **Precedent** | ⛔ **The risk with no technical mitigation.** Approving the first reopening of a frozen unit's source logic makes the second easier to ask for. **The mitigation is that this document says so in §2, names the count, and is exhaustive** — so a future request must argue on its own merits rather than cite this one as routine. |

---

## 6. Sign-off

✅ **SIGNED 2026-08-24.** Both prerequisites were met at signature: the thirteen questions are answered
(`register-33-34-combined-plan.md` §2) and the ambiguity check is **CLEAN** (§6, with resolutions at
§6.1, §6.2, §6.3 folded into §3 above).

Authorization was requested — and is granted — for **exactly** the four frozen files in §3, for
**exactly** changes **(a)–(m)** plus §3.5's tests, on the design approved in
`register-33-34-combined-plan.md`.

⚑ **The one item that required explicit confirmation rather than silent acceptance** (combined plan
§6.7) — ⛔ **that the file list is FOUR, not the three the approving direction anticipated** — **was
surfaced before signature and answered directly.** `telemetry.py` (§3.4) is a **docstring-only,
zero-statement** entry required by **Q8-B**, and the approver confirmed Q6's options *"never
contemplated a docstring-only file."*

- [x] **APPROVED — four files** — `memo_agent_core`'s first reopening is authorized as scoped above,
      including §3.4's docstring-only entry. Proceed to write the execution/code-gen plan as a separate
      artifact; the reopening is applied as **step 0** of that pass.
- [ ] **APPROVED — three files** — as above but **§3.4 is struck**; `telemetry.py:7` is handed to a
      documentation-sync task, knowingly leaving a dangling reference inside the reopened unit.
- [ ] **APPROVED WITH CHANGES** — note them here: ______________________
- [ ] **DECLINED** — #33, #34 and #35 remain open; the design stands as a recorded, unexecuted deliverable.

**Signed**: Nidhi Dhyani (approved in writing, this session)  **Date**: 2026-08-24

**Approval text, verbatim**: *"Confirmed — the file list is four, not three. Q8=B genuinely authorizes
telemetry.py's docstring correction independently of Q6, and Q6's options simply never contemplated a
docstring-only file. My original direction was based on an incomplete framing, not the correct scope.
Sign off on four files. … AUTHORIZATION SIGN-OFF: APPROVED — four files, exactly as finalized in §3 of
the re-issued register-33-34-reopening-authorization.md (orchestrator.py, provider.py,
prompt_builder.py, telemetry.py), for exactly the thirteen changes (a)-(m) plus §3.5's tests named
there, and nothing beyond that list."*

### ⚑ Four ambiguity-check items expressly approved at sign-off

Recorded here because each modifies how §3 is executed, and a reopening's terms must not move by
inference afterwards:

| Item | Disposition at sign-off |
|---|---|
| **§6.1** — double-ended anchoring | ✅ **APPROVED.** *"bind the rule-report section at both ends, so correctness no longer depends on prompt ordering under any report state, exactly as Q2's original 'two independent defenses, neither depending on the other' required."* Governs §3.3's load-bearing-marker hold and §3.6's `offline_memo_double.py` fix. |
| **§6.3** — coverage-scope extension | ✅ **APPROVED.** `backend/app/offline_memo_double.py` joins the 100% discipline, *"since it's where #35 lands and is already at 100%."* |
| **§6.4** — the `observability/` asymmetry | ✅ **ACCEPTED as recorded-not-resolved**, *"correct by unit ownership, and does not block this authorization."* |
| **§6.5** — #35's row timing | ✅ **APPROVED.** Written at **stage 2** alongside its fix; register **34 → 35**; ⚠️ `guide-state.md` becomes stale **by three**, not two. |

⛔ **No file under `backend/memo_agent_core/` is touched until the execution plan is separately
reviewed.** ✅ **This document's gate is now closed; the code-gen plan's gate is not.**
