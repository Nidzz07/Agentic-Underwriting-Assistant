# FINDING — `seed_demo_cases.py` raises `TypeError` on construction

**Status**: 🔴 **REPORTED, NOT FIXED** — presented for a fix-now-or-defer decision
**Found**: 2026-07-23, incidentally, during tier-B Stage 1 (Step 4)
**Scope**: **separate from tier-B.** Nothing in tier-B caused it, depends on it, or is blocked by it.
**Location**: `backend/scripts/seed_demo_cases.py` — **TWO defects**, see §1 and §1b

> ## ⚑ REVISED 2026-07-23, after a fresh ground-truth re-confirmation
>
> The re-check found a **SECOND, INDEPENDENT DEFECT hiding behind the first**, and it **invalidates this memo's
> original "one-line fix" framing**. Both are confirmed by execution. **§1b is new; §4 and §5 are revised.**
>
> * **Line number moved**: the `RulebookLoader()` call is now at **line 154**, not 139 — this pass's own approved
>   C7 docstring edit shifted it. Same defect, same file.
> * **Defect 2**: even with defect 1 fixed, **every seeded case would land in `FAILED`**, never `drafted` — so the
>   script would still not do the one thing it exists to do.

---

## 1. What is broken

```python
# backend/scripts/seed_demo_cases.py:154  (inside _SeedSeams.__init__)
# (was :139 when first reported; this pass's own C7 docstring edit shifted it)
loader = RulebookLoader()
```

```python
# backend/rules_engine/loader.py:73  (frozen U3)
def __init__(self, rulebook_dir: str | Path) -> None:
```

`RulebookLoader.__init__` takes a **required** positional `rulebook_dir`. It has **no default**. Every other caller
in the build passes it explicitly — `corpus_generator/build.py`, `quality_gates`' conftest, `rules_engine`'s own
tests, and the new `backend/scripts/run_quality_gates.py`. **The seed script does not.**

### Confirmed by direct execution, not by reading

```
>>> RulebookLoader()
TypeError: RulebookLoader.__init__() missing 1 required positional argument: 'rulebook_dir'

>>> seed_demo_cases._SeedSeams()
TypeError: RulebookLoader.__init__() missing 1 required positional argument: 'rulebook_dir'
```

`_SeedSeams.__init__` fails on its **first statement**. Every path through the script constructs `_SeedSeams` —
both the offline default and the `--real-llm` path — so **`main()` cannot complete under any invocation.**

## 1b. ⚑ THE SECOND DEFECT — the offline double cites a rule id that does not exist

```python
# backend/scripts/seed_demo_cases.py  (_OfflineLLMClient.generate)
# Cites a rule that genuinely appears in the report, so citation validation passes for
# the right reason rather than being bypassed.
cited = "DTI-001" if "DTI-001" in prompt else ""
```

**There is no rule `DTI-001` in this build.** The rulebook at `1.0.0` contains eleven rules, and the DTI rule is
**`DTI-CEIL-1`**:

```
AGE-BAND-1  BMI-OBESE-1  DTI-CEIL-1  INCM-CEIL-1  SMOKE-STATUS-1  OCC-LOWRISK-1
MED-HEALTH-1  DOCS-COMPLETE-1  IRDAI-INCOME-FLOOR-1  IRDAI-COVER-POSITIVE-1  IRDAI-EMP-SALARIED-1
```

**So the comment's claim is FALSE.** `"DTI-001" in prompt` is **always False** (verified against the real
`PromptBuilder` output), the double always emits `<rule_id></rule_id>` — an **empty** citation — U4's
`CitationValidator` rejects it, the graph re-drafts to `MEMO_CITATION_RETRY_CAP = 2`, then **flags**, and
`LangGraphOrchestrator.run()` returns **`None`**.

### Verified end-to-end for all three demo cases

```
DEMO-0001: recommendation=REFER   memo=None -> BLOCKED -> case goes to FAILED
DEMO-0002: recommendation=REFER   memo=None -> BLOCKED -> case goes to FAILED
DEMO-0003: recommendation=REFER   memo=None -> BLOCKED -> case goes to FAILED
```

`CasePipeline.draft` (`pipeline.py:116`) then transitions the case to **`CaseState.FAILED`** and returns
`DraftOutcome(failure_reason="drafting produced no memo")`.

### ⛔ What this means — the script would not do what it exists to do

Its own docstring for `seed()`: *"draft all but the last so **BOTH R4 branches are reachable**."* With defect 2:

* **R4's `ready` branch is NEVER reachable** — no case ever reaches `drafted`.
* **R5's commit path is NEVER reachable** — there is no `drafted` recommendation to commit.
* Worse, the failure is **invisible at the wire**: register **#14** records that a `failed` case projects to
  `"pending"` on R4, and register **#16** that `ApplicationSummary` has **no status field at all**. So all seeded
  cases would appear **pending / indistinguishable from fresh** — a reviewer would see a plausible-looking queue
  and conclude the demo path worked.

**⚑ Therefore defect 1 is not "the bug" — it is the bug that has been HIDING defect 2.** Fixing only the
`RulebookLoader()` line yields a script that runs to completion, prints three `FAILED (drafting produced no memo)`
lines, and seeds a database in which **nothing is exercisable**.

## 2. Why it was never caught

**No test constructs `_SeedSeams` or imports `seed_demo_cases`.** A repo-wide grep returns only *docstring
mentions* from other modules (`app/dependencies.py:120`, `run_migrations.py:11`,
`reconcile_committing_cases.py:41`, `build_corpus.py:21`) — no import, no call, no test.

`backend/scripts/` is outside every `--cov=` target, so the module is **coverage-invisible** as well as untested.
It is an out-of-band script that has apparently **never been run to completion** since the line was written.

⚑ This is a **coverage-blind-spot** failure, not a logic error: the defect is a one-token omission that any single
execution would have caught instantly.

## 3. Which existing claims this invalidates

### (a) Register **#2**'s partial-discharge claim — `BUILD-COMPLETION-REPORT.md` §6.1-REVISED

> **"The API layer is exercisable after running the seed script."**

This is the **honest narrowed claim** that replaced the original *"end-to-end demo path"* wording, and it is
repeated in `guide-state.md`, `audit.md`, and `composition-root/scope-b-wiring-summary.md`. It is stated as
**verified**.

**It cannot have been verified by running the script**, because the script raises before it seeds anything. Either
it was verified some other way (by reasoning about the wiring rather than executing it), or it was not verified at
all. **Either way the claim needs correcting or genuinely re-verifying.**

⚑ **And defect 2 makes the claim WORSE, not merely unverified.** Even after defect 1 is fixed, the script seeds
**only `FAILED` cases** — so **R4's `ready` branch and R5's commit path are never reachable**, and the claim
*"the API layer is exercisable"* would remain **false in substance**, not just unproven. Only R2, R3, R6 and R7
would serve anything, and R2/R3 would show cases that are silently failed (registers #14 and #16).

⚑ Note precisely what is and is not in doubt: **the seven WIRE-1 routes themselves are unaffected** — they are
independently unit-tested and their wiring is proven by U24's and the composition root's own suites. What is in
doubt is only the **seeding step** that makes those routes serve data, and therefore the *"exercisable"* half of
the claim.

### (b) Register **#18**'s `--real-llm` path is **unreachable**

`#18` is **NARROWED** on the basis that *"a production `LLMClient` now exists and a real memo is producible **in
principle** via the opt-in path."* That opt-in path is `seed_demo_cases.py --real-llm`, which constructs
`_SeedSeams(real_client, ...)` — and therefore **raises before any model call.**

**This does not falsify #18's NARROWED status**, and should not be over-read:

* `backend/app/llm_client.py` itself is **correct, tested (17 tier-U tests) and reachable** — `build_corpus.py`
  now constructs it through `build_gemini_client` successfully.
* The chain `CaseSeams.draft_memo → LangGraphOrchestrator → GeminiAdapter → CappedGeminiClient` is intact.
* What is broken is the **seed script's own construction**, upstream of all of it.

But #18's residual was *"the manual real-API verification has NOT been run end-to-end"* — and this finding explains
**why it could not have been**, and means the documented procedure in `real-llm-verification.md` **would fail at
step one** if attempted today. #18's residual is therefore **larger than recorded**: not merely "not yet run", but
"**not currently runnable**".

### (c) Not affected

* **tier-B Stage 1** — `build_corpus.py` and `run_quality_gates.py` construct `RulebookLoader` correctly and are
  fully green (15 tier-U tests). The committed `corpus/` and its four gate reports are unaffected.
* **The full test suite** — unchanged, because nothing imports this module.
* **Any frozen unit** — `RulebookLoader` is correct; the caller is wrong.

## 4. The fix, characterised (NOT applied) — ⚑ REVISED: it is TWO fixes, not one

**Defect 1** — one line: pass the rulebook directory, exactly as `run_quality_gates.py:RULEBOOK_DIR` and
`corpus_generator/build.py:_default_rulebook_dir()` already do —
`Path(__file__).resolve().parents[1] / "rules_engine" / "rulebook"`.

**Verified sufficient for construction**: with that line corrected, the whole in-memory chain builds and runs —
`RulebookLoader` -> `RulesEngine` -> `load_rulebook` -> `MemoAgentInputBuilder` -> `GeminiAdapter` ->
`LangGraphOrchestrator`, then `_demo_profile` -> `evaluate` (returns `REFER`) -> `draft_memo`. Nothing else in the
constructor is broken.

**Defect 2** — one line: the offline double must cite a rule id that **actually exists in the report**. The
robust form is to stop hardcoding any id and derive it from the prompt (or from the report), rather than
substituting `DTI-CEIL-1` for `DTI-001` and leaving the same brittle pattern in place. ⚑ **The accompanying
comment must be corrected too** — it currently asserts a property the code does not have, which is how the defect
survived review.

⚑ **Neither fix alone is sufficient.** Defect 1 alone yields a script that runs and seeds only `FAILED` cases.
Defect 2 alone is unreachable. **They are a pair.**

⚑ **A fix still would not close this.** The script would then need to be **actually run to completion** against a
real Postgres to substantiate #2's *"exercisable"* claim — which needs Docker or a live database, neither
available in the environment where this was found. **Fixing the lines and re-asserting the claim without executing
it would repeat the original error exactly.**

### Why this was invisible: the shared root cause

Both defects are **unexecuted-code** defects in a module that is **untested, uncollected, coverage-invisible, and
never run**. Neither is subtle; either would have been caught by **one execution** or by **one test that
constructs `_SeedSeams` and asserts a memo is produced**. The absence of that single test is the actual gap.

## 5. Decision required

### ⚑ 5a. The FLOOR — independent of what happens to the code

**Two recorded claims are currently overstated and should be corrected regardless of which code option is chosen:**

1. **`BUILD-COMPLETION-REPORT.md` §6.1-REVISED** — *"The API layer is exercisable after running the seed script"*
   (repeated in `guide-state.md`, `audit.md`, `scope-b-wiring-summary.md`). Correct to state that the seed script
   **has never been successfully run**, and that with both defects present it seeds **only failed cases**.
2. **#18's residual wording** — currently *"the manual real-API verification has not been run"*. Correct to
   *"**not currently runnable** — the `--real-llm` path raises before any model call."*

**This is the floor because a disclosure record that asserts something is *exercisable* when it raises `TypeError`
on its first statement has an integrity problem independent of the code.** Per this build's supersede-not-rewrite
discipline, the original wording is preserved and superseded, never edited in place.

### 5b. The CODE decision — four options

| Option | What it means |
|---|---|
| **(a) Fix both defects now; verify later** | Apply both one-line fixes + a **tier-U test that constructs `_SeedSeams` and asserts a memo is actually produced** (closing the blind spot permanently, and catching defect 2's class). Leaves #2's claim still unverified until someone runs the script against a real DB. |
| **(b) Fix both now; verify now** | (a) plus actually running the script end-to-end against Postgres, genuinely substantiating or refuting #2's claim. **Needs Docker or a live DB — neither available here.** |
| **(c) Defer the code entirely** | Open as a new register item and do **5a only** — correct the two claims now, in documentation, touching no code. |
| **(d) Correct the claims now; fix the code in its own pass** | 5a immediately; the code fix scoped separately with its own gate. |

**Recommendation — stated as two separate judgements, as requested:**

* **On the claims (5a): do it now, unconditionally.** This is not really a choice — the statements are wrong on
  disk today, and every further pass builds on them.
* **On the code (5b): (a).** Both fixes are one line each and fully understood; the tier-U construction test is
  the piece that actually matters, because it converts an unexecuted script into one with a standing guard, and it
  is what would have caught **both** defects. **(b) is unavailable here** (no Docker/DB). **(c) leaves a known-broken
  script on disk with no owner.** **(d) is defensible** if you would rather keep this pass documentation-only —
  the difference between (a) and (d) is only *when*, and both are honest.

⚑ **Whichever is chosen, the real-database verification remains outstanding** and should be tracked as a residual
on the #8 precedent (written-but-unexecuted proof recorded as a residual rather than claimed) — **not** quietly
folded into a "fixed" claim.

**No code has been changed. No claim has been rewritten. Awaiting a decision.**
