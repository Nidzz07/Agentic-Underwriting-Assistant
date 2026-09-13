# REGISTERS #33 + #34 — COMBINED SCOPING PLAN

**Status**: ✅ **ALL THIRTEEN QUESTIONS ANSWERED 2026-08-24** · ✅ **AMBIGUITY CHECK RUN — CLEAN (§6)**
⛔ **STILL NO CODE, NO BACKEND FILE TOUCHED.** Next artifact: the re-issued reopening authorization,
which requires its own separate signature before any code-generation plan is written.
**Created**: 2026-08-24 · **Answered**: 2026-08-24 · **Checked**: 2026-08-24
**Baseline**: HEAD `bd3875d` · nothing committed · backend **1837 / 0 / 45 / 5 / 99.36%** · frontend **823 / 155**
**Targets**: **#33** `MEMO-XML-CONTRACT-NEVER-REQUESTED` · **#34** `CHECKPOINT-POISONS-REDRAFT`
· ⛔ **and a THIRD live defect found while grounding this plan** (§1.5, Question 3)
**Companion artifact**: `register-33-34-reopening-authorization.md` — ⛔ **DRAFT, UNSIGNED**
**Parents**: `BUILD-COMPLETION-REPORT.md:1606-1674` (#33/#34 as opened) · `live-llm-drafting-plan.md` ·
`live-llm-drafting-code-gen-plan.md` §6 (the manual verification that surfaced both)

> ⚑ **SUPERSEDED 2026-08-24 — preserved because it was true for the whole of the question gate:**
> *"This document asks thirteen questions and answers none of them. Every `[Answer]:` tag is
> deliberately empty. Each question carries a grounded recommendation — grounded meaning it cites the
> file and line, or the reproduction, that its reasoning rests on — but a recommendation is an
> argument, not a decision. ⚠️ The recommendations were written by the same agent that will report
> agreement with them later; that is stated here so a future reader discounts it appropriately."*
>
> **All thirteen are now answered**, verbatim as given, at their `[Answer]:` tags. ⚠️ **Every headline
> letter matched the recommendation** — stated plainly rather than dressed up as independent
> convergence, since the recommendations were written by the same agent now reporting the agreement.
> ⚑ **The answers' real work was elsewhere**: they rejected four options *outright* by name (Q2's D,
> Q4's C, Q5's A and C, Q8's C) with reasons that go beyond the recommendations' own, and Q1's answer
> supplied a sharper statement of the two-part rationale than the recommendation did. ⛔ **The
> ambiguity check at §6 then found three things the answer set underspecified**, one of which
> — §6.1 — would have defeated Q2's own stated intent had it been left implicit.

---

## 0. ⚠️ Two premises this session was handed, and what testing them produced

Both were carried into this pass as settled. **One was strengthened; one is false.** They are stated
first because a plan that repeated the false one would assert a stop-gate that does not exist.

### 0.1 ⚠️ **FALSIFIED** — `memo_agent_core` is **NOT** coverage-gated at 100%

The premise was that `memo_agent_core` is gated at 100% by `pyproject.toml`'s `--cov=` configuration,
so any uncovered X3 branch "moves the 90% gate", a stop-gate breach. ⛔ **There is no per-unit gate
anywhere in this build.**

| What was checked | What is actually there |
|---|---|
| `pyproject.toml` `addopts` | **17 flat `--cov=<tree>` entries** and **exactly one** threshold — `--cov-fail-under=90` (`:82`) |
| How that threshold is computed | Over the **union** of all 17 trees — `TOTAL 4024` statements, currently **99.36%** |
| `quality_gates/coverage_gate.py` | `COV_FAIL_UNDER_MIN = 90` (`:26`); `passed = wiring_present and fail_under >= COV_FAIL_UNDER_MIN` (`:41`) — ⚑ **a meta-gate asserting the CONFIG declares a threshold ≥90, not a per-unit measurement** |
| `memo_agent_core`'s actual coverage | **100% on all 12 modules** — ⚑ **observed, not enforced** |

⛔ **The corrected consequence, which Question 11 is written against**: an uncovered X3 branch is **not
a stop-gate breach**. It is a real but smaller regression — a handful of statements against a 4024
statement denominator (~0.02 pp) with a **9.36 pp margin** above the gate. What it *would* cost is
`memo_agent_core`'s standing 100%, which is a **documented figure this build has never broken**, and
that is worth defending on its own terms rather than by invoking a gate that would not fire.

### 0.2 ⛔ **STRENGTHENED** — no FROZEN_UNITS member's source logic has ever been reopened

Confirmed **mechanically, from git history**, not by assertion:

| Frozen unit | Commits touching `backend/<unit>/` |
|---|--:|
| `intake` · `rules_engine` · **`memo_agent_core`** · `audit_store` · `auth_rbac` · `secrets_config` · `corpus_generator` · `quality_gates` · `admin_cli` · `common` | **1** each — `51935ac`, the original BUILD commit |
| `database` | **2** — `51935ac` + `d6a6876`, ⚑ **purely additive** (`0003_auth.sql` + one line of `checksums.json` + one line each in three **test** files; authorized at login/signup Q9(a)) |
| ⚑ `case_lifecycle` — **NOT a FROZEN_UNITS member** | **2** — `51935ac` + **`3a08dd8`**, the #27/#28 source fix |

⛔ **No `.py` source module under any frozen unit has ever been modified.** The one post-build
source-modifying commit belongs to the one unit that is *not* frozen. **This is developed in full in
the companion authorization document §2**, and is the reason that document exists as a separate
artifact rather than a section here.

---

## 1. Investigation findings — what the code actually does today

Every claim below was read from the tree at `bd3875d`, and every claim marked ⚑ **REPRODUCED** was
executed against the real modules in a scratchpad. ⛔ **No project file was touched to do any of it.**

### 1.1 #33 — the XML contract is enforced on the parse side and requested nowhere

`PromptBuilder.build` (`prompt_builder.py:31-50`) emits, in order: the system prompt, the read-only
recommendation and confidence, the rule report, the non-demographic applicant facts. ⛔ **No
output-format instruction, no schema, no element names, no example.** The two parsers are identical
in behaviour and asymmetric in shape:

| Parser | Location | Shape | Frozen? |
|---|---|---|---|
| `GeminiAdapter._parse_xml` | `memo_agent_core/provider.py:65-70` | **`@staticmethod` on the adapter class** | ⛔ **YES** |
| module-level `_parse_xml` | `memo_extensions/provider_secondary.py:47-55` | **module function**, shared by `ClaudeAdapter` **and** `OllamaAdapter` (`provider_showcase.py` imports it) | **No** |

Both are `ElementTree.fromstring(raw_xml)` with **zero tolerance** — no fence-stripping, no
preamble-skipping, no block extraction. ⚠️ **The asymmetry is load-bearing for X3**: one edit lands
inside a frozen class as a static method; the other lands on a module function that **two** adapters
share. They are not the same change written twice.

### 1.2 #34 — ⚑ **REPRODUCED, both with and without the checkpointer**

`orchestrator.py:137` compiles with `checkpointer=MemorySaver()` — explicit, not a default — and
`:155` uses **`application_id` as the `thread_id`**. Behind `@lru_cache(maxsize=1)`
(`dependencies.py:369`) that is one `MemorySaver` for the process's life.

⚑ **Run against the real `LangGraphOrchestrator`** (`langgraph 1.2.7` / `langgraph-checkpoint 4.1.1`):

| Configuration | Invoke #1 | Invoke #2 | Invoke #3 |
|---|---|---|---|
| **as it ships** (`MemorySaver`) | **memo** | ⛔ **`RuntimeError: recommendation/confidence are read-only channels (CON-BR2-STATE); no node may write them`** — preceded by the **identical 15-type deserialization-warning cluster** the user saw at §6 | — |
| **candidate C2** (no checkpointer) | **memo** | **memo** | **memo** |

⚑ Under C2 the provider is called **exactly once per invoke** and **`memo_hash` is byte-stable across
invokes** — a property Question 9 turns into an assertion.

### 1.3 ⛔ Nothing consumes the checkpointer — the C2 premise, verified negatively

A repo-wide grep finds **no** `get_state`, `update_state`, `get_state_history`, `.stream(`,
`astream`, or `interrupt` anywhere in the codebase. The **only** `MemorySaver` / `checkpointer` /
`thread_id` occurrences in production code are the **three inside `orchestrator.py` itself** (`:25`
import, `:137` compile, `:155` thread_id). ⛔ **No test anywhere references any of them** — the sole
hit under any `tests/` tree is a **docstring** at `observability/tests/test_trace.py:36`.

### 1.4 ⛔ Three false claims — now four — across 9 files and ~16 locations

The docstring at `orchestrator.py:4-6` reads *"Checkpointer **YES** (`MemorySaver`, in-process —
retry loop + durability + 100%-step tracing)"*. **Every one of those three justifications is false**,
and a fourth claim sits at `:11-13`. Full inventory:

| # | The claim | Locations | Status |
|---|---|---|---|
| **1** | *"LangGraph does not run the reducer on the initial input"* | `orchestrator.py:11-13`, `:48-51` | ⛔ **FALSE for a restored thread** — `BinaryOperatorAggregate.update()` bypasses the reducer only when the channel `is MISSING`; `from_checkpoint()` sets the value, so a restored channel takes the reducer branch. **This is #34's root cause.** |
| **2** | *"Langfuse 100%-step tracing via the checkpointer"* | `telemetry.py:7` · `observability/trace.py:6`, `:57`, `:64` · `observability/tests/test_trace.py:36` · `nfr-requirements.md:122` · `nfr-design-patterns.md:88` · `logical-components.md:20`, `:42` | ⛔ **FALSE, and more so than recorded** — ⚑ `TraceRecorder.on_step` is called by **five observability unit tests and by nothing else**. Never by `orchestrator.py`, never by any production module. It is not *"wired via a checkpointer that does not do it"*; **it is not wired at all** (consistent with OBS-SINK-DEFERRED). |
| **3** | *"bounded retry via the checkpointer"* | `tech-stack-decisions.md:13` · `business-logic-model.md:7`, `:64` | ⛔ **FALSE, independently** — ⚑ **REPRODUCED**: with **no checkpointer**, a bad-then-good provider produced **2 provider calls and a finalized memo**. The retry loop is a plain `add_conditional_edges` cycle (`orchestrator.py:130-134`) carrying `attempts` in state. |
| **4** | ⚠️ *"durability"* | `orchestrator.py:4-6` · `tech-stack-decisions.md:61` | ⛔ **FALSE** — `MemorySaver` is in-process and dies with the process; nothing reads a checkpoint back after a restart, and nothing reads one back **at all** (§1.3). ⚑ **This is a fourth claim, not among the three carried into this pass.** |

⚑ **Claim 3 is the load-bearing one for C2**: because the retry loop needs no checkpointer, removing
the checkpointer **cannot regress the one behaviour the docstring offers as its justification.**

⚠️ **A detail worth keeping, and it is exculpatory rather than damning.** `audit.md:760` records that
claim 1 was affirmatively tested at build time: *"verified LangGraph doesn't call the reducer on seed
but does on node-write."* **That was true for the no-checkpoint case that was exercised, and was
never exercised with a restored checkpoint.** ⛔ **The defect is an untested boundary, not an
unchecked assumption** — which is exactly what Question 9's regression test exists to close.

### 1.5 ⛔ **A THIRD LIVE DEFECT — found while grounding finding (b), and independent of both register items**

`_RULE_ID_PATTERN` (`offline_memo_double.py:46`) is `\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b`, and
`first_cited_rule_id` `.search()`es the **whole prompt**, left to right. `PromptBuilder.build` emits
`RECOMMENDATION (read-only): {value}` at `:36` — **before** the rule report at `:39-42`. And
`Recommendation.DECLINE_RECOMMEND = "DECLINE-RECOMMEND"` (`rules_engine/report_schema.py:28`)
**matches that regex.**

⚑ **REPRODUCED** against the real `PromptBuilder`, the real factories and the real `CitationValidator`:

| Recommendation | `first_cited_rule_id` returns | `CitationValidator` outcome | Result |
|---|---|---|---|
| `APPROVE` | `'R-AGE-1'` | `valid` | memo finalized |
| `REFER` | `'R-AGE-1'` | `valid` | memo finalized |
| ⛔ **`DECLINE-RECOMMEND`** | ⛔ **`'DECLINE-RECOMMEND'`** | ⛔ **`citation_failure`**, `offending=['DECLINE-RECOMMEND']` | ⛔ **memo BLOCKED → case FAILED** |

⛔ **Every DECLINE-RECOMMEND case that has ever gone through the offline double has silently landed in
`FAILED`** — after burning both citation-retry attempts — **for this build's entire history.**

⚠️ **Three things make this worse than its size suggests.**
1. ⛔ **Zero test coverage.** `grep` finds **no** `DECLINE-RECOMMEND` or `DECLINE_RECOMMEND` anywhere
   under `backend/app/tests/`. Every offline-double test uses an APPROVE or REFER fixture, so the
   defect is invisible to a green suite.
2. ⚑ **It is the `DTI-001` defect class, live, in the very file whose docstring records fixing it
   once** — `offline_memo_double.py:52-56`: *"the seed script's copy … originally cited a hardcoded
   `DTI-001` … so **every seeded case silently landed in `FAILED`**."* Same symptom, same file, a
   different cause, still shipping.
3. ⚠️ **It is duplicated.** `seed_demo_cases.py:118` carries `_first_cited_rule_id` with the same
   regex, and `offline_memo_double.py:28-32` explicitly records that the duplication is deliberate
   and that *"the two must stay behaviourally equivalent."*

⚑ **And the same grounding produced the token table Question 2 needs.** The real regex, run over 24
candidates:

| ⛔ **UNSAFE** (matches — would be mis-cited) | ✅ **SAFE** (does not match) |
|---|---|
| `EXAMPLE-RULE-ID` · `RULE-ID-HERE` · `XXX-000` · `FILL-IN` · `A-1` · `DTI-001` · `IRDAI-EMP-SALARIED-1` | `EXAMPLE_RULE_ID` (underscore) · `rule-id-here` · `example-rule-id` · `the-rule-id` (lowercase) |
| ⚠️ **`NOT-QUALITY-GATED`** and **`OFFLINE-DOUBLE-NOT-A-REAL-LLM`** — ⛔ **this build's own two stamp markers** | `Example-Rule` (mixed case) · `ABC` · `TODO` (unhyphenated) · `<rule_id>` (underscore) |

⚑ **The decisive structural point**: the element name **`<rule_id>` contains an underscore and is
inherently safe**, so a worked example's XML **tags** cost nothing. ⛔ **The hazard is solely the
placeholder VALUE placed inside them.**

⚠️ **And the stamp-marker row is a standing latent hazard worth naming**: if any future change ever
puts a `model_version` into a prompt, `NOT-QUALITY-GATED` becomes the first regex match and the same
defect reappears with a third cause.

### 1.6 ✅ The design-doc boundary is mechanically settled — the *decision* is not

`FROZEN_UNITS` (`test_frozen_untouched.py:21-24`) is a set of **`backend/<unit>/` directory names**.
`PRODUCTION_FILES` (`:16`) is `APP_ROOT.rglob("*.py")` rooted at **`backend/app/`**. ⛔ **Neither
reaches `guide-docs/` at all**, so `guide-docs/build/memo-agent-core/` is outside both boundaries and
needs **no reopening authority whatsoever.**

⚑ **But the precedent is not "mixed" — it resolves to a rule this project has already applied four
times, and the rule decides Question 7 on the merits rather than on taste:**

| Case | Design doc edited? | Why |
|---|---|---|
| `intake` (audit `:479-481`) | ✅ back-annotated `business-rules.md` | the built reason-precedence was not in the design |
| `rules-engine` (audit `:581-593`) | ✅ back-annotated `domain-entities.md §4.2` | ⚑ on the stated principle ***"FD back-annotated FIRST (design owns it)"***, and ⛔ **the user required disk verification before approving** |
| `auth-rbac` (audit `:971-982`) | ✅ back-annotated `domain-entities.md §2.5` | the read contract's shape changed; also disk-verified |
| ⚑ **`memo-agent-core` itself** (audit `:760`) | ⛔ **NO** | ***"No FD back-annotation needed (frozen signature preserved)"*** — Option B kept the frozen signature, so nothing in the design became false |

⛔ **The operative test is whether the design document would otherwise state something FALSE about the
built system.** ⚑ Note also that `intake`, `rules_engine` and `auth_rbac` are **all FROZEN_UNITS
members** — so editing a frozen unit's *design docs* is itself well-precedented, and is a
categorically lighter act than editing its *source*.

### 1.7 ⚠️ What the freeze actually is, stated once so no document overstates it

`test_frozen_untouched.py`'s own docstring (`:6-7`) says the suite asserts *"the half that is
checkable from inside the suite"* and that the **"no file edited" half is verified out-of-band by an
mtime scan**. ⛔ **So no frozen unit's edit-freeze is mechanically enforced — `memo_agent_core`
included.** This is the same admission `register-27-reopening-authorization.md` §2 makes about
`case_lifecycle`, and it means the authorization document is the only real control in **both** cases.
⚠️ **It does not weaken the reopening request; it is the reason the request must be exhaustive.**

---

## 2. Questions

Thirteen questions. **None is pre-filled.** Answer by putting a letter after each `[Answer]:` tag; if
no option fits, choose the last option and describe.

---

## Question 1
X1 adds an explicit XML output-format instruction to `PromptBuilder`. **What is its structure and
where in the prompt does it go?**

A) **Appended last, after the applicant facts** — a `REQUIRED OUTPUT FORMAT:` block naming the two
   elements and the exact nesting, placed at the very end of `build()`'s line list so it is the last
   thing the model reads before generating.
B) **Folded into `_SYSTEM_PROMPT`** (`prompt_builder.py:16-23`) — one more sentence in the existing
   system instruction, so format lives with the other standing constraints (advisory-only,
   cite-only-listed-rules) rather than as a separate block.
C) **Both** — a short binding sentence in `_SYSTEM_PROMPT` ("respond with XML only, no prose outside
   the tags") **and** a `REQUIRED OUTPUT FORMAT:` block appended last carrying the structure.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: C.** ⚑ **The two halves do different jobs and the reproduction shows why.** The
> §6 failure was not a malformed XML document — it was a **well-formed Markdown memo** beginning
> `**ADVISORY MEMO**`. The model was not confused about structure; it was never told that prose was
> the wrong container. That is a **standing behavioural constraint**, which is exactly what
> `_SYSTEM_PROMPT` already carries for the other two ("Always use the word 'recommendation'"; "Cite
> ONLY rule ids…"). ⚠️ **But a system-prompt sentence alone gives the model no element names**, and
> the parser reads `narrative_prose` and `./cited_rule_ids/rule_id` by exact path
> (`provider.py:67-69`) — a model that invents `<memo_text>` produces well-formed XML that parses to
> an **empty prose string and zero citations**, which then fails `CitationValidator` and presents as
> *"drafting produced no memo"*. ⛔ **That failure is worse than the current one because it is
> silent**, so the exact element names must appear somewhere concrete. ⚑ **Placement of the block
> last is not cosmetic** — it interacts with Question 2 (see §1.5: everything before the rule report
> is a citation-regex hazard) and with recency, since format instructions are best honoured closest
> to generation. **A is the acceptable reduced-scope fallback if C is judged to be two changes where
> one would do.**

[Answer]: C — both a binding sentence in _SYSTEM_PROMPT and a REQUIRED OUTPUT FORMAT block appended last. The two do different jobs: the system prompt sentence prevents prose entirely; the appended block gives exact element names so a "compliant but wrong-shaped" XML document doesn't parse to silence.

---

## Question 2
⛔ **The worked example is a live correctness hazard, not a styling detail** (§1.5). **What token
shape does the example's `<rule_id>` placeholder use, and where is the example placed?**

A) **Underscore placeholder, block placed last** — `<rule_id>EXAMPLE_RULE_ID</rule_id>`, in the
   `REQUIRED OUTPUT FORMAT:` block appended after the applicant facts. ⚑ Safe on **both** axes: the
   token cannot match the regex, **and** it sits after the rule report anyway.
B) **Lowercase placeholder, block placed last** — `<rule_id>rule-id-here</rule_id>`. Also safe on
   both axes; reads more like documentation and less like a constant.
C) **Reuse a REAL rule id from the handed report** — the example cites an id that is genuinely in
   this applicant's report, so even if the model copies the example verbatim the citation validates.
D) **Placement alone** — keep any token shape, rely solely on the block being after the rule report,
   since `first_cited_rule_id` returns the **first** match and a real rule id will always precede it.
E) Other (please describe after [Answer]: tag below)

> **Recommendation: A, and ⛔ D should be rejected outright.** ⚠️ **D is the option that looks
> sufficient and is not.** It is true that `.search()` returns the first match and that the rule
> report precedes the appended block — **but §1.5 proves the premise is already broken**: for a
> DECLINE case the first match today is `DECLINE-RECOMMEND`, emitted at `:36`, **before** the rule
> report. D would make the example's safety depend on an ordering property that **is currently
> false**, and would couple X1's correctness to Question 3's fix landing. ⛔ **Two independent
> defences, neither relying on the other, is the correct shape for a hazard this cheap to avoid.**
>
> ⚑ **A over B on one concrete ground**: `EXAMPLE_RULE_ID` shares its **underscore** convention with
> the element names the model must emit (`narrative_prose`, `cited_rule_ids`, `rule_id`), so it reads
> as part of the template rather than as prose to be echoed. Both are regex-safe (§1.5's table).
> ⛔ **C is the option to argue about and the recommendation is against it**: an example citing a
> genuinely valid id makes the *example* correct but teaches the model that **that specific rule** is
> the one to cite, biasing citation selection toward whichever rule the template picked — which
> corrupts the thing `CitationValidator` exists to check. ⚠️ **Whatever is chosen, it needs a test
> that pins it**: an assertion that `first_cited_rule_id(PromptBuilder().build(...))` is a member of
> the handed report's rule ids, for **every** `Recommendation` value. Without that, the next person
> to edit the template reintroduces this by hand.

[Answer]: A — EXAMPLE_RULE_ID (underscore), block placed last. Reject D outright per your own reasoning — placement-alone relies on an ordering premise §1.5 already proved broken (DECLINE-RECOMMEND precedes the rule report today). Two independent defenses, neither depending on the other.

---

## Question 3
⛔ **THE THIRD DEFECT (§1.5) — every DECLINE-RECOMMEND case silently lands in `FAILED` today.** This
is live, pre-existing, and independent of both #33 and #34. **What is the fix, and is it its own
register item?**

**3a — the fix shape:**

A) **Anchor extraction to the rule-report section** — `first_cited_rule_id` searches only the text
   after the `RULE REPORT (the only citable rules):` marker, so nothing emitted before it can ever
   be picked up, whatever it looks like.
B) **Exclude the `Recommendation` enum values** — subtract `{r.value for r in Recommendation}` from
   the match set, so `DECLINE-RECOMMEND` specifically can never be returned.
C) **Narrow the regex** — require a trailing numeric segment or otherwise tighten the pattern so
   `DECLINE-RECOMMEND` falls outside it.
D) **Validate against the handed report** — the double takes the report's rule ids and returns the
   first match **that is a member of them**, `""` otherwise.
E) Other (please describe after [Answer]: tag below)

> **Recommendation: A, with D as the stronger-but-larger alternative.** ⛔ **B and C are both
> fixes-by-enumeration and both fail the same way**: they patch the one token that is known to
> collide. ⚠️ **§1.5's table shows the collision class is wider than one token** —
> `NOT-QUALITY-GATED` and `OFFLINE-DOUBLE-NOT-A-REAL-LLM`, this build's own stamps, match identically,
> and C would additionally reject `IRDAI-EMP-SALARIED-1`, a **real** rule-id shape. ⚑ **A fixes the
> class**: the function's *name* is `first_cited_rule_id`, its docstring says *"the first rule id
> appearing in the prompt"*, and the prompt's own line — *"RULE REPORT (**the only citable rules**)"*
> — already declares where citable rules live. A makes the implementation match the sentence the
> prompt already prints. ⚑ **It also composes with Question 2 for free**: with A, the worked example's
> token shape stops mattering for this path entirely, giving the second independent defence.
>
> ⚠️ **D is genuinely stronger and is not recommended only because of what it changes.** D would make
> the double structurally incapable of emitting an invalid citation — but it changes the double from
> *"discover what the prompt cites"* to *"agree with the report by construction"*, which ⛔ **weakens
> `CitationValidator` as a test instrument**: every offline-path assertion that citation validation
> works would become tautological. The double's own docstring (`:52-56`) says the discovery behaviour
> exists so validation passes *"for the RIGHT reason rather than by coincidence"* — **D trades that
> away.** ⚠️ **Whichever is chosen, the duplicate at `seed_demo_cases.py:118` must move with it**
> (`offline_memo_double.py:28-32`: *"the two must stay behaviourally equivalent"*), and the fix needs
> a test **parametrized over every `Recommendation` value** — the absence of exactly that test is why
> this shipped.

**3b — register item, or absorbed into this pass?**

A) **Open it as register #35**, fix it in this pass, close it on the same evidence.
B) **Open it as #35, document only** — fix it in a later pass, as #33/#34 were.
C) **No register item** — fix it inside this pass and record it in the close-out only.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: A. The case for and against, stated fairly.**
>
> ⛔ **For a register item.** It meets every criterion the last four opened items met: **pre-existing**
> (present since `51935ac`), **independent** of this pass's causal chain, **blocking** for a real
> user journey (no decline case can ever be drafted offline), and ⛔ **it was invisible to a green
> 1837-test suite**, which is precisely the property `#26`, `#27` and `#33`/`#34` were each opened to
> record. ⚑ **The strongest argument is the precedent it would otherwise break**: #33 and #34 were
> opened *specifically* so a future reader could not read the causal chain as one bug. Folding a
> **third**, differently-caused defect into #33's fix pass without its own row does exactly the
> conflation those two items were written to prevent.
>
> ⚠️ **Against.** It is small, its fix is a few lines, and it touches the same file family as #33 —
> so a reader might reasonably see one register row where the pass produced one coherent change.
> ⛔ **This argument is real but it is an argument about effort, not about accuracy**, and this
> project has repeatedly chosen accuracy: `#29` was split out of `#28` for exactly this reason, and
> `#24` was *"OPENED **and** DISCHARGED in one pass"* (`guide-state.md:806`) — ⚑ **so opening an item
> and closing it in the same pass is established here and costs nothing.**
>
> ⚠️ **B is recommended against on a specific ground**: unlike #33 and #34, this fix has **no design
> fork**. 3a is a choice among four mechanisms with a clear winner, not a tradeoff needing its own
> scoping pass. Deferring it would leave a known, reproduced, user-visible defect open for no
> deliberative benefit.

[Answer 3a]: A — anchor extraction to the rule-report section. Fixes the class, not one token, and composes with Q2 for free (the worked example's token shape stops mattering for this path once extraction is properly scoped).

[Answer 3b]: A — open register #35, fix and close in this pass, on the same evidence. This is a real, pre-existing, independently-caused defect and deserves its own row per the same discipline #29 was split from #28 for. The #24 precedent (opened and discharged in one pass) means this costs nothing procedurally.

---

## Question 4
X3 makes both parsers tolerant. ⛔ **Where exactly is the boundary between recoverable near-XML and
what must still fail loudly?**

A) **Fence + preamble stripping only** — strip Markdown code fences (```` ```xml ```` … ```` ``` ````)
   and any text before the first `<memo>` / after the last `</memo>`, then parse. Anything that still
   fails `fromstring` raises as it does today.
B) **A + element-name tolerance** — additionally accept a small set of near-miss element names
   (`<memo_text>` for `<narrative_prose>`, etc.) mapped back to the schema.
C) **A + regex extraction fallback** — if no parseable XML block is found, pull `narrative_prose` and
   `rule_id` values out with regexes, so a memo is produced from partially-structured output.
D) **No tolerance at all** — rely on X1 alone; a model that ignores an explicit instruction and a
   worked example should fail loudly rather than be guessed at.
E) Other (please describe after [Answer]: tag below)

> **Recommendation: A, and ⛔ C should be rejected.** ⚑ **A is bounded by a property that makes it
> safe to reason about: it is purely *subtractive*.** It removes wrapper text and then hands the
> result to the **same** `ElementTree.fromstring` with the **same** element paths. It cannot invent a
> citation, cannot alter prose, and cannot turn a failure into a wrong answer — **the worst case is
> that it strips nothing and the parse fails exactly as today.** That property is what lets a
> tolerant parser live inside a frozen unit at all.
>
> ⛔ **C breaks that property and breaks it in the one place this system cannot afford.** A regex
> that pulls `rule_id`-looking tokens out of unstructured prose is ⚑ **the §1.5 defect, generalized
> and moved onto the live path** — the build has now been bitten twice by "extract an identifier by
> pattern from free text" (`DTI-001`, and `DECLINE-RECOMMEND`). ⛔ **A hallucinated-but-plausible id
> extracted by regex is a citation the system cannot distinguish from a real one**, and `PROJECT-BRIEF`
> §5.5's *"zero unexplained recommendations"* is the guarantee it would be spending.
>
> ⚠️ **B is defensible and is recommended against on evidence.** The observed failure was Markdown
> prose, **not** mis-named elements — so B guesses at a failure mode that has not been seen, and each
> alias is a permanent contract the parser must honour. ⚑ **If a real element-name miss is observed
> later, B is a small additive follow-on**; adding it now is speculative. ⚠️ **D deserves a fair
> hearing** — it is honest, and X1 may well be sufficient — but ⛔ the ⚑ **specific, cheap, already-
> witnessed** failure it declines to absorb is a model wrapping correct XML in ```` ```xml ```` fences,
> which is the single most common instruction-following deviation for local instruct models. A costs
> a few lines and one branch to cover it.

[Answer]: A — fence/preamble stripping only, purely subtractive. Reject C outright — regex-extracting values from unstructured prose is exactly the DTI-001/DECLINE-RECOMMEND defect class generalized onto the live path, and this system cannot distinguish a hallucinated-but-plausible extracted citation from a real one.

---

## Question 5
⚠️ **The two parsers are not the same edit** (§1.1): one is a `@staticmethod` inside frozen
`GeminiAdapter`; the other is a module-level function two adapters share. **How is X3 applied to
both without duplicating the tolerance logic?**

A) **Duplicate deliberately** — implement the stripping independently in each file, with a comment in
   each naming the other and stating they must stay behaviourally equivalent. ⚑ The
   `offline_memo_double.py` / `seed_demo_cases.py` precedent (`:28-32`).
B) **`memo_extensions` imports from `memo_agent_core`** — put the helper in the frozen unit and have
   `provider_secondary.py` import it. ⚑ It already imports from `memo_agent_core.schemas`.
C) **Put the shared helper in `backend/common/`** — the existing shared-utility home, imported by
   both. ⛔ But `common` is itself a FROZEN_UNITS member, so this **widens the reopening to a second
   frozen unit**.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: B.** ⛔ **C is the option to reject first**: it would take a reopening that is
> already a project first (§0.2) and make it a **two-unit** first, for a helper neither unit's design
> assigns to `common`. ⚑ **B costs no new structural precedent** — `provider_secondary.py:28` already
> does `from backend.memo_agent_core.schemas import MemoDraftOutput, ThinkingMode`, so the import
> direction (`memo_extensions` → `memo_agent_core`) is **established and one-way**, and adding one
> more name to an existing arrow is the smallest possible change. It also puts the helper **where the
> frozen parser that needs it lives**, so the frozen unit is self-contained.
>
> ⚠️ **A's precedent is real but its cited case argues against it.** The `offline_memo_double` /
> `seed_demo_cases` duplication is documented as a ⛔ **"DISCLOSED COST"** and a *"named follow-on,
> not an oversight"* (`:28-32`) — and ⚑ **§1.5 is that duplication coming due**: the citation defect
> now has to be fixed in two places. **Choosing A here would knowingly create a second instance of a
> debt the first instance is currently billing us for.** ⚠️ **A's one genuine merit**, which should be
> weighed: it keeps `memo_extensions` able to change its tolerance without a frozen-unit reopening.
> ⛔ **If that autonomy is wanted, say so under D** — it is a legitimate preference, not an error.

[Answer]: B — the shared helper lives in memo_agent_core, imported by memo_extensions, using the arrow that already exists (provider_secondary.py already imports from memo_agent_core.schemas). Reject C — it would widen the reopening to a second frozen unit (common/) for no design reason. Reject A's duplication — the offline_memo_double/seed_demo_cases duplication is already a disclosed cost coming due via Q3's fix; don't knowingly create a second instance of the same debt.

---

## Question 6
**What exactly does the reopening of `memo_agent_core` cover?** (The companion authorization document
is written against whichever answer this receives.)

A) **`orchestrator.py` only** — `graph.compile()` with no checkpointer, the import removed, the
   docstrings corrected. #33's parser tolerance is applied **only** to the non-frozen
   `provider_secondary.py`, leaving Gemini's frozen parser intolerant.
B) **`orchestrator.py` + `provider.py`** — C2 **and** X3's tolerance in the frozen parser, so both
   providers behave identically.
C) **`orchestrator.py` + `provider.py` + `prompt_builder.py`** — B, plus X1's output-format
   instruction and worked example, which is **the only place the prompt is built.**
D) Other (please describe after [Answer]: tag below)

> **Recommendation: C — and the recommendation is that the scope is not actually a choice.** ⛔ **X1
> has no non-frozen implementation.** `PromptBuilder` (`memo_agent_core/prompt_builder.py`) is the
> sole prompt construction site; `orchestrator.py:92` calls `self._prompt_builder.build(...)` and
> nothing else assembles a prompt anywhere in the build. **Requesting X1 while excluding
> `prompt_builder.py` would be requesting a change with no place to put it.**
>
> ⛔ **A is the option that must be rejected explicitly rather than by omission**, because it looks
> like prudent minimalism and would silently defeat the pass's own stated purpose. Under A the
> **Gemini** path — ⚑ `PROJECT-BRIEF` §9's **PRIMARY** provider, and the one that is **quality-gated**
> while Ollama is exempt — keeps a zero-tolerance parser while the showcase provider gets a tolerant
> one. ⚠️ **That is the exact asymmetry `#33`'s own row warns about**: *"#18 gap (iii) cannot move for
> EITHER provider until #33 is closed."* **A closes it for the exempt provider only.**
>
> ⚑ **Three files, three named reasons, nothing beyond** is the shape `register-27-reopening-authorization.md`
> §3 established and the shape the companion document uses. ⚠️ **The honest cost of C, stated plainly**:
> it is **three** frozen source files in the **first** reopening of a frozen unit's source logic in
> this project's history, which is a large first. **That is an argument for scrutinising each of the
> three, not for cutting one that the design requires.**

[Answer]: C — all three files (orchestrator.py, provider.py, prompt_builder.py). Confirmed this isn't really a choice: X1 has no non-frozen implementation, since PromptBuilder is the sole prompt-construction site. Option A would leave Gemini — the quality-gated PRIMARY provider — intolerant while the exempt showcase provider gets tolerance, which is the exact asymmetry #33's own row warns against.

---

## Question 7
⚠️ C2 makes **eight statements false** across five design documents under
`guide-docs/build/memo-agent-core/` (§1.4). Those documents are ⛔ **mechanically outside every frozen
boundary** (§1.6) and need no reopening authority. **Are they corrected, and how?**

A) **Back-annotate all of them**, in the `rules-engine` / `auth-rbac` shape — the false clause struck
   and replaced, with a dated `BACK-ANNOTATION` marker naming this pass and the register items.
B) **Back-annotate only the two claims C2 makes newly false** (`checkpointer YES`, `bounded retry via
   the checkpointer`), leaving the Langfuse-tracing claims — which were **already** false before this
   pass — for a separate documentation-sync task.
C) **Correct nothing** — the documents record the design as approved at the time; a `REGISTER UPDATE`
   in `BUILD-COMPLETION-REPORT.md` is the appropriate place for what changed since.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: A.** ⚑ **§1.6 found the rule rather than a preference, and it decides this.** The
> project back-annotated three times (`intake`, `rules-engine`, `auth-rbac`) and **declined once —
> in `memo_agent_core` itself** — and the discriminator is consistent every time: **back-annotate
> when the design document would otherwise state something false.** `audit.md:760` is explicit that
> nothing was written because *"the frozen signature [was] preserved"*. ⛔ **C2 does not preserve
> anything; it deletes the mechanism four documents name by role.** ⚑ **And the `rules-engine`
> precedent adds a procedural requirement worth carrying**: the user required the back-annotation be
> **verified on disk** before approving (`audit.md:591-593`), so this pass should present grep
> evidence, not a summary.
>
> ⚠️ **B is the interesting answer and is recommended against on the specific ground that it
> preserves a falsehood it has already identified.** Its logic is sound — Langfuse-via-checkpointer
> was false *before* C2, so it is not this pass's defect. ⛔ **But this pass is the one that
> discovered it, reproduced it, and is editing the same lines**; leaving `logical-components.md:42`
> reading *"wired externally via the checkpointer"* **after removing the checkpointer** produces a
> document that is now false for **two** reasons instead of one. ⚑ **The honest form of B, if B is
> chosen, is to correct the C2 claims and add a one-line dated note at each Langfuse location saying
> the claim is known-false and owned by a named follow-on** — silence would be worse than either.
>
> ⛔ **C should be rejected.** The register records *what changed*; the design documents state *what
> the system is*. ⚠️ These are read by different people for different reasons, and a design doc that
> says `checkpointer YES` about a system with no checkpointer will mislead the next reader
> regardless of how complete the register is.

[Answer]: A — back-annotate all eight false statements across the five design documents, verified on disk (grep evidence, not a summary), per the rules-engine precedent requiring disk verification before approval. The operative rule this project has applied four times is: back-annotate when the document would otherwise state something false. C2 makes eight things false; silence is not acceptable given that rule.

---

## Question 8
⚠️ Beyond the design docs, the false claims also sit in **production docstrings and one test
docstring** (§1.4): `orchestrator.py:4-6`, `:11-13`, `:48-51` · `telemetry.py:7` ·
`observability/trace.py:6`, `:57`, `:64` · `observability/tests/test_trace.py:36`. **Which are in
scope?**

A) **`orchestrator.py`'s three only** — they are inside the file being reopened and describe the
   thing being removed. `telemetry.py` and `observability/` are separate units and separate passes.
B) **`orchestrator.py` + `telemetry.py`** — both are `memo_agent_core`; `telemetry.py:7` would
   otherwise reference a checkpointer that no longer exists in its own unit.
C) **All four files** — including `observability/`, since §1.3 established `on_step` is not wired to
   anything and the docstrings misdescribe it in a way this pass has now disproved.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: B.** ⚑ **A draws the line at the wrong place by one file.** `telemetry.py` is
> `backend/memo_agent_core/telemetry.py` — **the same unit, the same reopening** — and after C2 its
> line 7 (*"by `observability` (reference-not-own) via the graph checkpointer"*) would name a
> mechanism that **no longer exists in the file's own package.** ⛔ **Leaving a dangling reference
> inside the very unit being reopened is the kind of residue a reopening is supposed to prevent**,
> and it costs one line.
>
> ⛔ **C is scope creep, and specifically the kind this project has refused by name.** `observability`
> is a **different unit** with its **own** design record, and ⚠️ **its docstrings are wrong about
> something this pass did not cause**: `on_step` is unwired because of **OBS-SINK-DEFERRED**, a
> standing deferral, not because of the checkpointer. ⚑ **Correcting them properly means engaging
> with that deferral**, which is a separate piece of work with its own owner. **The right treatment
> is to record the finding** — that `TraceRecorder.on_step` has **no production caller at all**, which
> is stronger than what OBS-SINK-DEFERRED currently says — **and let the item that owns it act.**
> ⚠️ **If Question 3b opens a register item, this finding is a natural second candidate for one**; it
> is at minimum a close-out note, and ⛔ **it must not be silently dropped**, which is the failure
> `#30` and `#31` were opened late to record (`live-llm-drafting-plan.md:665-668`).

[Answer]: B — orchestrator.py's three docstring locations plus telemetry.py (same unit, same reopening, would otherwise leave a dangling reference to a removed mechanism inside the very unit being reopened). Reject C — observability/ is a different unit with its own owner (OBS-SINK-DEFERRED); record the finding that on_step has no production caller at all, but let the item that owns it act.

---

## Question 9
⛔ **The #34 regression test.** It must assert a **returned memo**, not merely the absence of an
exception, and it must pin **which mechanism** provides correctness — so a future change elsewhere
cannot silently re-mask the bug the way `3a08dd8` incidentally did. **What is its exact shape?**

A) **Two invokes, assert a memo both times** — build one `LangGraphOrchestrator`, run the same
   `MemoAgentInput` twice, assert both return a non-`None` `DecisionMemo` with a valid citation.
B) **A + a structural assertion on the compiled graph** — additionally assert the compiled graph has
   **no checkpointer** (e.g. its `checkpointer` attribute is falsy), so the test fails if one is ever
   reintroduced, whatever the behavioural outcome.
C) **A + B + a memo-equivalence assertion** — additionally assert the two invokes produce **equal
   `memo_hash`**, pinning that a re-draft is not merely successful but produces the same memo.
D) **A + B + C + a non-vacuity guard** — additionally assert that the second invoke actually **called
   the provider again** (a call-count assertion), so the test cannot pass against an implementation
   that silently returns a cached first result.
E) Other (please describe after [Answer]: tag below)

> **Recommendation: D. Each layer answers a specific way the weaker versions can go quietly wrong,
> and three of the four are grounded in this build's own recorded history.**
>
> ⛔ **A alone is insufficient for exactly the reason the question names.** A two-invoke behavioural
> test passes under **any** implementation that does not raise — including a future one that
> reintroduces a checkpointer but happens to be re-masked by a guard moved somewhere else. ⚑ **That
> is not hypothetical: it is what `3a08dd8` did.** `#34`'s own row records that #27's pass moved a
> legality check above `draft_memo` *"for entirely unrelated reasons"* and ⛔ **"INCIDENTALLY closed
> the only then-reachable route"* — for **four months**, with a fully green suite. **B is the layer
> that makes the mechanism itself the assertion**, so correctness stops depending on a guard
> somewhere else staying where it is.
>
> ⚑ **C is cheap and was verified available**: the reproduction confirmed `memo_hash` is **byte-stable
> across invokes** under C2. ⚠️ It also pins something the register cares about independently —
> `PROJECT-BRIEF` §5.1's reproducibility claim — at the one place a re-draft can be observed offline.
>
> ⛔ **D is the layer this project's own recent history says not to skip.** The live-LLM-drafting pass
> found **two tests that passed against a broken design** (`audit.md:7738-7756`), and the lesson
> recorded there was that the discriminating assertion is the one that fails against a **strawman**.
> ⚑ **The strawman here is concrete**: an implementation that memoizes by `application_id` and returns
> the first memo would satisfy A, B **and** C — same memo, no exception, no checkpointer — while
> having reintroduced a *different* form of the same "second draft is not a real draft" defect. **A
> provider call-count assertion is the one line that kills it.**
>
> ⚠️ **One caveat to state in the test itself**: it must build its **own** orchestrator, not reach
> through `case_seams()`, or `@lru_cache(maxsize=1)` will leak state between tests — the same shape
> §1.4 of the parent plan flagged about construction-time probes.

[Answer]: D — all four layers: memo returned both invokes, structural no-checkpointer assertion, memo_hash equality, and the non-vacuity call-count guard. The strawman argument is decisive — a future implementation that memoizes by application_id would satisfy A+B+C while reintroducing a different form of the same defect; only the call-count assertion catches it.

---

## Question 10
#33 and #34 have **independent root causes and independent fixes**, and #34's regression test was
confirmed reproducible **without** #33 being fixed (§1.2). **Are they staged and gated separately, or
implemented together in one stage?**

A) **Separate stages, separate gates** — #34 (C2) first as its own stage with its own green run, then
   #33 (X1+X3), then Question 3's defect. Three stages, three verification points.
B) **One stage** — all three changes land together, one green run, one gate.
C) **Two stages** — #34 alone first (it is a two-line change with a self-contained test), then #33
   and Question 3's defect together (they share `prompt_builder.py` and the citation path).
D) Other (please describe after [Answer]: tag below)

> **Recommendation: C.** ⚑ **The staging should follow the dependency structure, and the dependency
> structure is asymmetric.**
>
> ⛔ **#34 is genuinely independent and genuinely verifiable alone.** The reproduction ran C2 against
> a **fake provider** and got three successful invokes with **no XML involved at all** — so its
> regression test needs nothing from #33. ⚑ **It is also the smallest, highest-confidence change in
> the pass** (one `compile()` argument, one import) with the **strongest** evidence behind it, and
> landing it first means the frozen-unit reopening's riskiest-sounding element is proven green before
> anything subtler is layered on.
>
> ⚑ **#33 and Question 3's defect belong together for a concrete reason, not a thematic one**: they
> **interact through the same function**. Question 2's recommendation makes the worked example
> regex-safe; Question 3a's recommendation anchors extraction to the rule-report section. ⛔ **Landing
> X1 while Question 3's fix is still outstanding would put a new token into a prompt whose extraction
> function is known-broken** — and if Question 2 chose D (placement alone), it would be actively
> unsafe. **Fixing extraction and adding the example in one stage means the stage's own tests cover
> the interaction.**
>
> ⚠️ **A's extra split is not wrong, just unpaid-for**: separating #33 from Question 3's defect buys a
> third verification point over two changes that must be verified together anyway. ⛔ **B is
> recommended against** — it merges a frozen-unit removal, a frozen-unit prompt change, a two-file
> parser change and a live-defect fix into **one** variance reconciliation, which is exactly the
> condition under which the live-LLM-drafting pass's `+48 → +63` miss became hard to attribute.

[Answer]: C — two stages: #34 (C2) alone first, since it's genuinely independent and was reproduced with a fake provider needing no XML at all; then #33 + Q3's defect together, since they interact through the same function (prompt_builder.py) and must be verified together anyway.

---

## Question 11
⚠️ **Coverage** (§0.1, and note the premise this replaces). There is **one global
`--cov-fail-under=90`** and **no per-unit gate**; `memo_agent_core` is at **100% observed, not
enforced**. X3 and Question 3's fix each add branches. **What constraint does this pass adopt?**

A) **Hold `memo_agent_core` at 100%** — every new branch fully covered, verified by reading the
   per-module coverage rows, and treated as a **self-imposed** stop-gate for this pass.
B) **Hold the global gate only** — cover what is reasonable; the binding constraint is the 90%
   threshold, which has 9.36 pp of margin.
C) **A, plus hold `memo_extensions` at its current level too** — since Question 5 may put the shared
   helper's callers in both units.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: C, stated with the corrected premise rather than the one this pass was handed.**
> ⛔ **The honest framing first**: an uncovered X3 branch would **not** breach any gate. It would cost
> a few statements against a 4024-statement denominator (~0.02 pp) with 9.36 pp of headroom. **Anyone
> claiming otherwise — including this plan's own earlier premise — is overstating the mechanism.**
>
> ⚑ **The real argument for A/C is different and, stated accurately, stronger.** `memo_agent_core`'s
> 100% is a figure this build has **carried since `51935ac` and never broken**, recorded at
> `audit.md:760` (*"12 source modules ALL 100% covered"*). ⚠️ **The branches X3 adds are precisely the
> ones that must not go uncovered**: the fence-stripped path, the preamble-stripped path, and the
> still-fails path are the **entire** behavioural content of the change, and an uncovered one is an
> untested tolerance rule. ⛔ **This build has just been bitten by exactly that** — #33 exists because
> *"no test feeds realistic model prose to `_parse_xml`"* (`BUILD-COMPLETION-REPORT.md:1641`). Adding
> tolerance without covering each branch would repeat the defect at one remove.
>
> ⚑ **C over A on Question 5's account**: if B is chosen there, the helper lives in `memo_agent_core`
> but is *called* from `memo_extensions`, so a coverage claim scoped to one unit would miss the other
> caller. ⚠️ **Whichever is chosen, one thing is non-negotiable and is a real stop-gate**: ⛔ **no
> coverage threshold may be edited, and no `# pragma: no cover` may be added to a reachable branch.**
> That is the stop-gate the parent pass held (its §5 gate 8) and the one that genuinely exists.

[Answer]: C — hold both memo_agent_core and memo_extensions at their current coverage levels as a self-imposed discipline, on the corrected premise (no mechanical gate, but a 100% figure this build has never broken and the branches being added are the entire behavioral content of the fix). No threshold edits, no pragma: no cover on reachable branches — that remains the real stop-gate.

---

## Question 12
Candidate **X2** (true structured output — `response_schema` on Gemini, `format=` on Ollama) is
**deferred, not dropped**. **How is the deferral recorded?**

A) **A register item** — its own row, naming what it would buy and why it was not taken now.
B) **A section in this plan's close-out** only — recorded in `audit.md` / `guide-state.md`.
C) **A register item AND a note at each parser** — so someone reading `_parse_xml` sees that a
   stronger mechanism exists and was consciously deferred.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: C.** ⚑ **The reason X2 must be recorded loudly is that its cost is routinely
> underestimated, including in the framing that produced this pass.** X2 is **not** a config
> addition. Both providers' structured-output modes are **JSON-schema** based —
> `response_schema` / `response_mime_type` on `google-genai`, `format=<json schema>` on `ollama` —
> so taking X2 means the model emits **JSON**, which means ⛔ **`_parse_xml` is replaced, not
> configured**, in **both** adapters, plus the offline double's hardcoded XML string, plus every
> test that asserts on XML. ⚠️ **That is a wire-format migration of the memo path**, and it collides
> with `PROJECT-BRIEF` §3's *"Structured XML output → Pydantic validation"* and §9's *"Tool use with
> structured XML outputs"* — ⛔ **so X2 additionally requires a `PROJECT-BRIEF` amendment**, which
> nothing in this pass's scope authorizes.
>
> ⚑ **That is exactly why A alone is insufficient and C is recommended.** A register row is read by
> someone auditing the register; ⚠️ **the person who needs this is the one reading `_parse_xml` and
> wondering why tolerance was hand-rolled instead of the SDK being asked for a schema.** A two-line
> note at each parser answers that at the point of confusion. ⛔ **B alone should be rejected**: it is
> the exact shape `live-llm-drafting-plan.md:665-668` records as having failed twice — *"registers #30
> and #31 were both opened **late**, as re-opened promises — the answers that created them named the
> instrument and the instrument was never picked up."*

[Answer]: C — a register item AND a note at each parser. The register row is for auditors; the inline note is for whoever reads _parse_xml later and wonders why tolerance was hand-rolled instead of asking the SDK for a real schema. Don't repeat the #30/#31 "named the instrument, never picked up" failure.

---

## Question 13
⚠️ **`_parse_xml`'s silent-empty behaviour, surfaced by Question 1's reasoning and not currently
tracked by any register item.** Both parsers use `root.find("narrative_prose")` and
`root.findall("./cited_rule_ids/rule_id")`; on a **well-formed** XML document with **different**
element names, `prose` becomes `""` and `cited` becomes `[]` — ⛔ **no exception, an empty memo, and a
`CitationValidator` failure that presents as *"drafting produced no memo"*.** Is this in scope?

A) **In scope** — add a structural check that raises a **named, diagnosable** error when the parsed
   document contains neither expected element, so a schema mismatch is distinguishable from a model
   that genuinely cited nothing.
B) **Out of scope, record it** — a register item or close-out note; X1's explicit element names make
   it much less likely, and it has never been observed.
C) **Out of scope, silent** — it is a hypothetical, and #33's fix addresses the cause.
D) Other (please describe after [Answer]: tag below)

> **Recommendation: A.** ⚑ **The reason to take it now is that X1 is what makes it reachable.** Today
> the model returns prose and `fromstring` raises immediately — ⛔ **a loud, unambiguous failure.**
> After X1, a model that has been **told** to emit XML will emit XML, and the remaining failure mode
> shifts from *"not XML"* to *"XML with the wrong names"* — ⚠️ **which is the silent one.** **X1
> converts a loud failure into a quiet one unless A is taken with it.**
>
> ⛔ **And "presents as *drafting produced no memo*" is precisely the misdirection this pass exists to
> stop repeating.** `#34`'s row spends a full line on its error message *"actively misdirect[ing]"*,
> and `offline_memo_double.py:52-56` records `DTI-001` producing the same phrase from a different
> cause. ⚑ **Three different causes now funnel into one uninformative operator-facing message** —
> `DTI-001`, §1.5's `DECLINE-RECOMMEND`, and this. **A named error at the parse boundary separates
> "the model gave us the wrong shape" from "the model cited nothing", which no current signal does.**
>
> ⚠️ **The fair case for B**: it is one more change inside a frozen unit in a reopening that is
> already this project's first, and it addresses something never observed. ⛔ **The counter is that it
> is the same file, the same function and the same edit session as X3** — it is a few lines inside a
> change already authorized — **and deferring it means the next pass reopens a frozen unit again for
> it.** ⚑ **If A is chosen, the authorization's §3 file list does not grow**; only the per-file change
> list does. ⚠️ **If B is chosen, it should say plainly that X1 made the failure quieter**, so the
> tradeoff is recorded rather than inherited.

[Answer]: A — in scope. X1 converts a loud failure (not-XML-at-all) into a potentially silent one (well-formed-XML-wrong-names) unless this lands in the same stage. Same file, same function, same edit session as X3 — deferring it just means reopening the frozen unit again later for a few lines.

---

## 3. Stop gate

✅ **GATE 1 SATISFIED** — all thirteen answered 2026-08-24, ambiguity check run and **CLEAN** (§6).
⛔ **GATE 2 OUTSTANDING** — the companion `register-33-34-reopening-authorization.md` must be
**signed off in writing** before any code-generation plan is written.

Two gates, in this order, and they are **not** interchangeable:

1. ⛔ **This document's thirteen answers**, followed by an **ambiguity check** across the complete
   answer set, in the shape `live-llm-drafting-plan.md` §4/§5 used. ⚑ **The check is not a formality
   here** — Questions 2, 3, 5, 6, 10 and 11 interact pairwise, and §4.3 of the parent plan is the
   precedent for a check that found a genuine blocking contradiction after every headline answer
   looked clean.
2. ⛔ **The reopening authorization signed**, as a **standalone** artifact, **before** the
   code-generation plan is written — the `register-27` shape (*"design approved standalone, applied
   as step 0 of its own execution pass"*).

Only then: a **code-generation plan** with numbered steps and checkboxes, for its own separate
approval, per `CLAUDE.md`'s two-part Code Generation rule.

### Holds asserted for this document

⛔ **No backend file touched** · no code written · no test modified · no frozen unit touched ·
`case_lifecycle/` not edited · WIRE-1 unamended · `PROJECT-BRIEF.md` unchanged · every reproduction
in §1 ran in a scratchpad against imported modules · **NO COMMIT.**

---

## 4. ⚠️ Documentation states a future reader should not be confused by

**Named, not fixed** — each has an owner elsewhere.

**(a) ⛔ `guide-state.md`'s register count is stale by two.** `guide-state.md:7454` reads
***"REGISTER NOW STANDS AT 32 TRACKED — 21 open"***. The authoritative figure is
`BUILD-COMPLETION-REPORT.md:1668` — ***34 tracked — 23 open · 7 closed/discharged · 4 narrowed***.
⚑ The `guide-state.md` figure was correct when written and went stale when #33 and #34 opened; the
#33/#34 entry says so explicitly. ⛔ **Deliberately not corrected here**, per the standing direction
that this pass flags rather than fixes it. ⚠️ **If Question 3b opens #35, the count moves again** —
whichever pass corrects it should reconcile from the authoritative source, not from either stale
figure.

**(b) The two states carried from `live-llm-drafting-plan.md` §0.2 are still unfixed** — the
outlier-mount entry's stale *"HEAD is `d43b661`"* / *"NOT COMMITTED"*, and
`BUILD-COMPLETION-REPORT.md`'s §5 register table still headed *"20 items"* with no rows for #26–#31.
**A documentation-sync task owns both.**

**(c) ⚠️ `uw.txt` is untracked and holds a live session token** from the §6 manual verification.
Harmless where it is; ⛔ **must not be committed.**

---

## 5. ⚠️ What this pass explicitly does NOT do

* ⛔ **Does not close register #18.** Gap (iii) moves only on a **live** memo produced through the
  request path; this pass makes that possible and does not itself demonstrate it.
* ⛔ **Does not close #22.** Nothing here touches the sampling stack.
* ⛔ **Does not fix #32.** The envelope capability is untouched; #32's row already records that a
  generic handler is not obviously the right fix.
* ⛔ **Does not take X2** (Question 12) — a wire-format migration requiring a `PROJECT-BRIEF`
  amendment.
* ⛔ **Does not correct `observability/`'s docstrings** (Question 8's recommendation) — a different
  unit, owned by OBS-SINK-DEFERRED.
* ⚠️ **Does not correct `guide-state.md`'s register count** (§4(a)).
* ⛔ **Does not commit.**

---

## 6. Ambiguity check against the complete answer set — **2026-08-24**

✅ **RESULT: CLEAN. No contradiction between any two answers.** ⚠️ **Three underspecifications were
found and are RESOLVED BY DESIGN below; two further interactions are recorded rather than resolved.**
⛔ **One of the three — §6.1 — is not cosmetic: left implicit, it would have defeated the stated
intent of Q2's own answer.**

⚑ Every check below was **executed**, not argued. The harnesses ran in a scratchpad against imported
project modules; ⛔ **no project file was touched to run them.**

### 6.1 ⛔ Check 1 — Q2 × Q3a: do both defenses genuinely need to coexist?

**The question asked**: does anchoring extraction to the rule-report section (Q3a-A) fully neutralize
the need for Q2-A's regex-safe token, or do both do real work?

⚑ **Executed.** The real `PromptBuilder` output, plus the Q1(C) format block appended last, across
`APPROVE` / `DECLINE-RECOMMEND` × populated / empty rule report × safe / unsafe placeholder token.
Three extraction implementations compared: **today's** (unanchored), **single-ended** (anchor the
start at the `RULE REPORT` marker only), **double-ended** (bound the region between the `RULE REPORT`
and `APPLICANT FACTS` markers).

| Recommendation | Rule report | Example token | today | single-ended | double-ended |
|---|---|---|---|---|---|
| APPROVE | populated | safe `EXAMPLE_RULE_ID` | `R-AGE-1` | `R-AGE-1` | `R-AGE-1` |
| APPROVE | populated | **unsafe** `EXAMPLE-RULE-ID` | `R-AGE-1` | `R-AGE-1` | `R-AGE-1` |
| APPROVE | **EMPTY** | safe | `''` | `''` | `''` |
| APPROVE | **EMPTY** | **unsafe** | ⛔ `EXAMPLE-RULE-ID` | ⛔ **`EXAMPLE-RULE-ID`** | ✅ `''` |
| DECLINE-RECOMMEND | populated | safe | ⛔ `DECLINE-RECOMMEND` | ✅ `R-AGE-1` | ✅ `R-AGE-1` |
| DECLINE-RECOMMEND | populated | **unsafe** | ⛔ `DECLINE-RECOMMEND` | ✅ `R-AGE-1` | ✅ `R-AGE-1` |
| DECLINE-RECOMMEND | **EMPTY** | safe | ⛔ `DECLINE-RECOMMEND` | ✅ `''` | ✅ `''` |
| DECLINE-RECOMMEND | **EMPTY** | **unsafe** | ⛔ `DECLINE-RECOMMEND` | ⛔ **`EXAMPLE-RULE-ID`** | ✅ `''` |

**✅ ANSWER TO THE QUESTION AS ASKED: both defenses genuinely do real work, and neither is
redundant.** Read the two ⛔ cells in the *single-ended* column against the two ⛔ `DECLINE-RECOMMEND`
cells in the *today* column: ⚑ **each defense covers exactly the cases the other misses.** Q3a covers
everything **before** the rule report — which Q2 cannot reach. Q2's token shape covers the appended
block when the rule report is **empty** — which single-ended anchoring cannot reach.

⛔ **BUT THAT IS ALSO THE PROBLEM, AND IT IS THE FINDING.** Q2's answer states the intent explicitly:
***"Two independent defenses, neither depending on the other."*** ⚠️ **Under the single-ended reading
they are NOT independent — they are complementary, each load-bearing for a different case, with no
overlap at all.** Removing either one leaves a live hole. That is strictly weaker than what Q2's
answer asked for, and it fails for the same structural reason Q2 rejected option D: ⚑ **it makes
correctness depend on where things sit in the prompt.**

**⚑ RESOLVED BY DESIGN — the anchor is bounded at BOTH ends**: extraction searches only the region
between the `RULE REPORT (the only citable rules):` marker and the `APPLICANT FACTS (non-demographic):`
marker. The double-ended column is **correct in every cell, at every token shape.** Then:

* **Defense 1 (Q3a)**: extraction cannot see the worked example **at all** — not because of ordering,
  but because the example is outside the searched region by construction.
* **Defense 2 (Q2)**: even if a future edit widened the region, the token still cannot match.

⛔ **These are now genuinely independent, which is what Q2's answer asked for and what the
single-ended reading does not deliver.** ⚑ **This is a refinement of Q3a-A, not a departure from it**
— the answer's own words are *"anchor extraction to the rule-report **section**"*, and a section has
two boundaries. **Non-blocking**; recorded here so the code-gen plan carries the bounded form and a
test pins the empty-report case, which is the cell that exposed it.

### 6.2 ✅ Check 2 — Q5 × Q6: does B's helper placement implicitly require a fourth file?

**The question asked**: is Q5-B (shared helper in `memo_agent_core`, imported by `memo_extensions`)
consistent with Q6-C's three-file scope, or does it smuggle in a fourth?

**✅ CLEAN — and the check found two guards neither answer mentioned, both of which pass unchanged.**
`memo_extensions` runs **eight AST/import scans**; two are relevant, and ⚑ **they differ in
granularity in exactly the way that matters here**:

| Scan | Where | Granularity | Scope | Verdict on `from backend.memo_agent_core.provider import …` |
|---|---|---|---|---|
| **Scan 1** — router allow-list | `test_structural_guard.py:39-54` | ⛔ **full module path** — `_ROUTER_ALLOWED` contains `backend.memo_agent_core.schemas` but **NOT** `…provider` | ⚑ **`ROUTER_MODULE` only** (`structural.py:27` = `borderline_router.py`) | ✅ **Not reached** — `provider_secondary.py` is outside this scan's scope |
| **Scan 7** — unit-edge rule | `test_structural_guard.py:200-212` | **unit root** — `_ALLOWED_BACKEND_ROOTS = {memo_agent_core, rules_engine, audit_store}` | **all four** production modules | ✅ **PASSES** — `backend_edge_roots()` maps it to root `memo_agent_core`, which is allowed |

⚠️ **Had Scan 1's full-path allow-list covered `provider_secondary.py`, Q5-B would have turned it RED
and required a guard edit.** It does not — `Scan 1 ⊂ Scan 7` by construction (the file's own docstring,
`:5-6`). ⛔ **So Q5-B needs no guard edit and no new allowlist entry.**

**⚑ RESOLVED BY DESIGN — one fork the answers did not name.** Q5-B says the helper lives *"in
`memo_agent_core`"* but not **in which module**. A new module (e.g. `memo_agent_core/xml_tolerance.py`)
would be a **fourth frozen file** and would contradict Q6-C's three-file answer. ⛔ **The helper
therefore goes in `provider.py`** — already file #2, already the home of the parser it serves, and the
choice that keeps §3 at exactly three files. ⚑ Precedent for the resulting import is exact:
`provider_showcase.py:22` already imports **two private names** (`_PRODUCTION_TEMPERATURE`,
`_parse_xml`) across a module boundary, so a private helper crossing units is the established idiom
here, not a new one.

### 6.3 ✅ Check 3 — Q10 × Q11: is there an awkward intermediate coverage state?

**The question asked**: does the two-stage split leave coverage in a bad state between stage 1 and
stage 2?

**✅ CLEAN — there is no intermediate dip, and the reason is structural.** ⚑ Stage 1 (C2) is
**net-subtractive** in statements:

| Stage-1 change | Coverage effect |
|---|---|
| `graph.compile(checkpointer=MemorySaver())` → `graph.compile()` | **None** — same statement, still executed |
| Remove `from langgraph.checkpoint.memory import MemorySaver` (`:25`) | Removes **one covered** statement — ratio unchanged |
| Docstring corrections (`:4-6`, `:11-13`, `:48-51`) | **None** — not statements |
| Q9's regression test | **Adds** covered lines |

⚑ **And no currently-covered line becomes unreachable.** The one candidate is
`_reject_channel_write`'s `raise` — but `test_read_only_channel_reducer_raises_on_write` calls it
**directly** (`BUILD-COMPLETION-REPORT.md:1659`), not through the graph, so it stays covered after C2.
⛔ **`memo_agent_core` therefore holds 100% at the stage-1 gate**, which is the state Q11-C requires.

**⚠️ RESOLVED BY DESIGN — but the check found a real gap in Q11-C's SCOPE.** Q11-C names
`memo_agent_core` and `memo_extensions`. ⛔ **It does not name `backend/app/offline_memo_double.py`** —
which is exactly where Q3a's fix lands, and which is **currently at 100% (11/11 statements)**. Q3a's
bounded anchor adds at least one guard branch (marker absent → `""`). Left outside the discipline, the
fix that closes #35 would knock a 100% module off 100%.

**The discipline extends to `offline_memo_double.py`.** ⚑ Verified as coherent: `memo_agent_core`
(12 modules), `memo_extensions` (5 modules) and `offline_memo_double.py` are **all currently at 100%**,
so this is a bar that is met today, not one being invented. ⚠️ **Stated for contrast so the boundary is
not misread as arbitrary**: `backend/app/` as a whole is **not** at 100% — `dependencies.py` 98%,
`ollama_client.py` 94%, `multipart_reader.py` 95% — so the discipline is scoped to **modules that are
at 100% and are being edited by this pass**, not to a tree.

⚑ **One consequence recorded so it is not later mistaken for an omission**: the mirror fix in
`backend/scripts/seed_demo_cases.py` (`:118`) gets **no coverage credit at all** — `backend/scripts/`
appears in **no** `--cov=` entry. ⛔ **Its tests still run** (`testpaths = ["backend"]` collects
`backend/scripts/tests/`), so the fix is *tested* but not *measured*. **That is pre-existing and
correct**, and `register-27-reopening-authorization.md` §3.4 already classifies that tree the same way.

### 6.4 ⚠️ Check 4 — Q7 × Q8: a transient asymmetry, recorded not resolved

⛔ **Not a contradiction — the boundary is unit ownership, and it is coherent.** But it produces a
state worth naming before it is discovered later and read as an oversight.

Q7-A back-annotates the **Langfuse-via-checkpointer** claim where it appears in **memo-agent-core's
design docs** (`logical-components.md:42`, `nfr-design-patterns.md:88`, `nfr-requirements.md:122`).
Q8-B declines to correct the **same claim** in **`observability/`'s source docstrings**
(`trace.py:6`, `:57`, `:64`).

⚠️ **So on completion, this build will say two different things about one mechanism**: memo-agent-core's
design record will state tracing is **not** wired via the checkpointer; `observability/trace.py` will
still describe `on_step` as *"the graph-checkpointer callback adapter"*.

⚑ **This is the correct call and the reason is ownership, not convenience.** `observability` is a
different unit with its own design record, and ⛔ **its docstrings are wrong about something this pass
did not cause** — `on_step` is unwired because of **OBS-SINK-DEFERRED**, a standing deferral.
Correcting them properly means engaging that deferral. ⛔ **What must not happen is silent drift**, so
the finding this pass contributes — ⚑ **`TraceRecorder.on_step` has NO production caller at all,
which is stronger than what OBS-SINK-DEFERRED currently records** — is carried into the close-out as a
named, owned observation. **Recorded, not resolved. Non-blocking.**

### 6.5 ⚠️ Check 5 — Q3b × Q10: when does #35's register row get written?

Q3b-A opens **#35** and closes it **in this pass**; Q10-C puts its fix in **stage 2**. ⚠️ **The
answers do not say when the row is written**, and the two obvious readings differ:

* Write it at **stage 1** → the register shows an open item the pass has not yet reached, and the
  stage-1 gate reports a count that is momentarily accurate-but-misleading.
* Write it at **stage 2, alongside its fix** → the register never shows an item this pass has not
  acted on.

**⚑ RESOLVED BY DESIGN — stage 2, with the fix**, on the `#24` precedent Q3b itself cites
(*"OPENED **and** DISCHARGED in one pass"*, `guide-state.md:806`), where the opening and the discharge
are one bookkeeping act. ⚠️ **Consequence for §4(a), stated so the next pass does not double-count**:
this pass moves the authoritative register from **34 → 35 tracked**, and `guide-state.md`'s
**"32 tracked"** will then be stale **by three**. ⛔ **Whoever reconciles it must count from
`BUILD-COMPLETION-REPORT.md`, not from either stale figure.**

### 6.7 ⛔ Check 6 — Q8 × Q6: **the frozen file list is FOUR, not three**

⚠️ **This was not one of the three interactions flagged for checking. It was found while writing §3
of the authorization against the actual answers, and it changes that document's headline scope
claim — so it is recorded here rather than absorbed silently.**

**Q6-C's answer names three files**: `orchestrator.py`, `provider.py`, `prompt_builder.py`.
**Q8-B's answer names a fourth**: *"orchestrator.py's three docstring locations **plus telemetry.py**."*

⛔ **`telemetry.py` is `backend/memo_agent_core/telemetry.py` — a file inside the frozen unit.**
Its line 7 reads *"Langfuse 100%-step tracing is wired by `observability` (reference-not-own) **via the
graph checkpointer**"* — a claim C2 makes false, inside the very unit being reopened, which is
precisely the reasoning Q8-B gave for including it.

**⚑ THE TWO ANSWERS DO NOT CONTRADICT EACH OTHER.** Q6's four options enumerated only the files
carrying **code** changes (C2, X3, X1) — its option list never contemplated a docstring-only file,
and Q8 is the question that governs docstrings. ⛔ **But the arithmetic consequence is real and must
not be glossed**: the reopening covers **four frozen source files**, not three.

| File | Changes | Statements affected |
|---|---|---|
| `orchestrator.py` | C2 + three docstring corrections | 1 removed, 1 modified |
| `provider.py` | X3 tolerance + shared helper + Q13 named error + Q12 note | additive |
| `prompt_builder.py` | X1 instruction + worked example | additive |
| ⚠️ **`telemetry.py`** | ⛔ **docstring line 7 only** | ⚑ **ZERO — no statement changes, no behaviour change, no coverage effect** |

⚠️ **RECORDED, NOT RESOLVED — this is the one item that needs an explicit confirmation at the
signature gate rather than a design resolution here.** The direction that produced these answers
asked for the authorization to be finalized *"confirming file list stays at exactly three files, per
Q6=C."* ⛔ **It does not stay at three.** The honest options are:

* **(i) Four files** — accept `telemetry.py` as a docstring-only entry, on Q8-B's stated reasoning.
  ⚑ **Recommended**: it is zero statements, zero behaviour, and excluding it leaves a dangling
  reference to a removed mechanism *inside the reopened unit* — the exact residue Q8-B was answered
  to prevent.
* **(ii) Three files** — drop `telemetry.py`, contradicting Q8-B, and hand its one line to a
  documentation-sync task.

⛔ **The authorization is re-issued under (i) with `telemetry.py` as §3.4, marked docstring-only**,
because writing it under (ii) would silently override an explicitly-answered question. ⚠️ **If (ii)
is preferred, that is a one-line amendment at signature — but it must be a decision, not an
inference.**

### 6.6 Summary

| Check | Result | Blocking? |
|---|---|---|
| §6.1 Q2 × Q3a | ✅ **Both defenses do real work** — ⚠️ but single-ended anchoring makes them *complementary*, not *independent*, failing Q2's stated intent → ⚑ **RESOLVED: bound the anchor at BOTH ends** | **No** |
| §6.2 Q5 × Q6 | ✅ **Clean** — Scan 1 out of scope, Scan 7 passes at unit-root granularity; ⚑ **RESOLVED: the helper goes in `provider.py`**, adding no file | **No** |
| §6.3 Q10 × Q11 | ✅ **No intermediate dip** (stage 1 is net-subtractive); ⚠️ ⚑ **RESOLVED: the coverage discipline extends to `offline_memo_double.py`**, currently 100% and edited by Q3a | **No** |
| §6.4 Q7 × Q8 | ⚠️ **Transient documented asymmetry** — correct by unit ownership; **recorded, not resolved** | **No** |
| §6.5 Q3b × Q10 | ⚠️ **Underspecified** — ⚑ **RESOLVED: #35's row is written at stage 2 with its fix**; register goes 34 → 35 | **No** |
| ⛔ **§6.7 Q8 × Q6** | ⛔ **The frozen file list is FOUR, not three** — `telemetry.py` (docstring-only, zero statements). **Answers do not contradict; the stated expectation does.** ⚠️ **Needs explicit confirmation at signature** | ⚠️ **Not blocking, but NOT auto-resolvable** |

✅ **CLEAN ENOUGH TO PROCEED.** ⛔ **No contradiction between any two answers** — every interaction
above resolves, and the one arithmetic surprise (§6.7) is a mismatch between the answers and a
*stated expectation about* them, not between two answers. Three underspecifications have
well-precedented resolutions; two interactions are recorded; ⚠️ **one (§6.7) needs an explicit yes/no
at the signature gate.** ⚑ **None is hidden**: every resolution above is vetoable at the reopening
authorization's signature gate or at the code-generation plan's own approval gate.

⚠️ **The one that would have cost something if missed is §6.1.** Q2's answer asked for *"two
independent defenses, neither depending on the other"*, and ⛔ **the literal single-ended reading of
Q3a would have delivered two mutually-dependent ones** — each covering the other's blind spot, with
no redundancy anywhere. **The empty-rule-report cell is what exposed it, and it is the cell the
code-gen plan must test.**

⚠️ **And the one worth noting about the check itself**: §6.7 was **not** among the three interactions
nominated for checking, and the three that were nominated all came back clean or cheaply resolvable.
⛔ **It surfaced only when §3 of the authorization was written out file-by-file against the actual
answers** — which is an argument for writing the artifact rather than reasoning about it abstractly,
and is recorded so the next check does the same.

➡️ **Next artifact**: `register-33-34-reopening-authorization.md`, **re-issued with §3 finalized**
against these answers — ⛔ **awaiting signature.**
