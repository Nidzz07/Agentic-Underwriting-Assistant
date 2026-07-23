# `GUIDE-DOCS-BUILD-GITIGNORED` — SCOPING PLAN

**Decision 2**, taken up after the seed-script defect closed · **Date**: 2026-07-23
**Status**: 🟡 **SCOPING / PLANNING ONLY — no `.gitignore` edit, no `git add`, no commit**
**Predecessors**: `tier-b-authorization-plan.md` §7 (where this was first surfaced) · the
`fix-register-*` scoping discipline

---

## 0. ⚑ THE FINDING IS MUCH LARGER THAN THE `.gitignore` RULE

This was surfaced as *"`guide-docs/build/` is untracked because of a frontend-intended `build/` rule."* **That is
true, and it is a subset of the real problem.** Fresh ground truth:

> **Only 81 files are tracked in the entire repository, and `backend/` has ZERO tracked files.**
> The last commit is **`2edaba4` — the DISCOVER-phase close**. **The entire BUILD phase — all application code,
> the frontend, deploy config, and all BUILD documentation — is uncommitted.**

The `.gitignore` rule explains why **one part** of that could not be committed even if someone tried. It does not
explain the rest.

**⚑ The two problems are DISTINCT and must not be conflated**, because a fix for one silently fails to address
the other:

| | Problem | Size | Would `git add -A` capture it? |
|---|---|---|---|
| **(A)** | **Never committed** — untracked but **not ignored** | **650 files, 4.0 MB** | ✅ **Yes** |
| **(B)** | **Actively ignored** — caught by `.gitignore:19`'s unanchored `build/` | **311 files, 5.9 MB** | ⛔ **NO — silently skipped** |

**(B) is the dangerous one.** Anyone "fixing" this with `git add -A` would commit 650 files, see a clean-looking
`git status`, and **still be missing the entire BUILD design record** — with no error and no warning.

---

## 1. Ground truth — verified fresh from disk

### 1.1 What is tracked today — 81 files

```
 34  .claude/
 21  .project-guide-rule-details/     (but NOT its build/ subdirectory - see 1.4)
 20  guide-docs/                      (DISCOVER only, + audit.md + guide-state.md)
  1  each: PROJECT-BRIEF.md  CLAUDE.md  requirements.txt  .gitignore
       guide-ai-sdp  "unhappy paths.png"
```

`git ls-files backend/` → **0**. `git ls-files guide-docs/build/` → **0**.

### 1.2 Problem (A) — untracked but NOT ignored: 650 files, 4.0 MB

```
406  backend/          228  frontend/           7  corpus/          3  deploy/
  1  each: testresults.txt  render.yaml  pyproject.toml  .python-version
            .env.example    guide-docs/BUILD-COMPLETION-REPORT.md
```

**`backend/` is NOT ignored** — `git check-ignore backend/app/main.py` returns nothing. It was simply **never
added**. Ordinary `git add` reaches all of it.

### 1.3 Problem (B) — actively ignored by `.gitignore:19`

```
# Node / frontend
node_modules/
dist/
build/          <-- line 19: UNANCHORED, matches ANY directory named "build" at ANY depth
```

| Path caught | Files | Size | What it is |
|---|---|---|---|
| `guide-docs/build/` | **305** | **5.8 MB** | Every BUILD-phase artifact: 24 unit directories (`functional-design/`, `nfr-requirements/`, `nfr-design/`, `infrastructure-design/`, `code/`) **+ all ~110 files in `plans/`**, including every `fix-register-*` plan, both tier-B plans, and **this document** |
| `.project-guide-rule-details/build/` | **6** | **60 KB** | ⚑ **A SECOND VICTIM, newly found** — the methodology's **own BUILD-phase rule files**: `functional-design.md`, `nfr-requirements.md`, `nfr-design.md`, `infrastructure-design.md`, `code-generation.md`, `build-and-test.md` — the very files **`CLAUDE.md` instructs the workflow to load** |

Confirmed: `git check-ignore -v guide-docs/build/plans/x.md` → `.gitignore:19:build/`.

### 1.4 ⚑ DECISIVE — the `build/` rule protects NOTHING that exists

* `frontend/vite.config.js:11` sets **`outDir: 'dist'`**.
* **`dist/` already has its own rule at `.gitignore:18`.**
* A filesystem sweep finds **no `build/` or `dist/` output directory anywhere** — the only two `build` directories
  on disk are the two documentation directories in 1.3.

**So the rule has never protected anything and currently protects nothing. It is pure collateral damage.** This
materially lowers the risk of changing it — there is no build output relying on it.

### 1.5 Constraints on editing `.gitignore` — narrow, and satisfied

`backend/secrets_config/tests/test_governance.py` (**frozen U16**) is the only test that reads `.gitignore`:

* `test_gitignore_lists_dotenv` — requires the literal line **`.env`** to be present. **Unaffected** by anchoring
  or removing `build/`.
* `test_dotenv_not_git_tracked` — runs `git ls-files .env`, must return empty. **Unaffected.**

**No test asserts anything about `build/`, `dist/`, or `node_modules/`.**

### 1.6 Safety of a bulk add — verified, no landmines

| Concern | Status |
|---|---|
| `.env` | ✅ **ignored** (`git check-ignore .env` confirms) |
| `frontend/node_modules` | ✅ **ignored** — **0** of the 228 frontend files are under it |
| `venv/`, `__pycache__/`, `.coverage`, `.pytest_cache/`, `.hypothesis/` | ✅ all ignored |
| Secret-shaped files (`*.pem`, `*.key`, `*.env`) | ✅ **none** in the untracked set (the `secrets_config/` hits are the unit's own **source files**, not secrets) |
| Total size | **4.0 MB (A)** + **5.9 MB (B)** ≈ **10 MB** — unremarkable for a git repo; **no LFS needed** |

---

## 2. Why this matters, stated without inflation

The project's stated invariants are **full auditability** and **replayability**. Its methodology treats each
stage's artifacts as first-class deliverables gated by explicit written approval. Today:

* **A clean checkout of this repository yields the DISCOVER phase and nothing else** — no application code, no
  tests, no BUILD design record, no register.
* **Every claim this build has carefully qualified** — the register, the NARROWED/DISCHARGED distinctions, the
  supersede-not-rewrite discipline — **lives in files git does not know about.**
* The **BUILD-phase rule files defining the workflow itself** are ignored (1.3), so the methodology is only
  half-committed.

⚑ **Stated fairly**: nothing is *lost* — every file is on disk and intact. This is a **version-control and
reproducibility gap**, not data loss, and **no behaviour depends on it**. It is **non-blocking** in exactly the
sense the register uses that word.

---

## 3. THE OPEN QUESTIONS

> **Every `[Answer]` tag is BLANK. Recommendations are given where the evidence grounds one.**

---

### Q1 — Scope: fix the ignore rule only, or also commit the BUILD phase?

§0 established these are separable. **A fix to (B) alone leaves 650 files still uncommitted; a fix to (A) alone
silently misses 311 files.**

* **(a) Both, in one pass** — correct the `build/` rule, then commit everything (A + B) together.
* **(b) (B) only** — correct the rule now; leave committing as its own later decision. Smallest change; but the
  repo stays in a state where a clean checkout has no BUILD phase.
* **(c) (A) only** — commit what is committable now, leave the rule for later. ⚠️ **Actively harmful**: it
  produces a repo that *looks* complete (`git status` clean) while missing the entire BUILD design record. **The
  worst of the four.**
* **(d) Both, but as two separately-gated passes** — rule first, verify, then commit as its own reviewed step.

**Recommendation: (d).** (a) and (d) reach the same end state; (d) separates a **1-line config change** from a
**~960-file commit**, so each is reviewable on its own terms and the rule fix can be verified (by `git
check-ignore` and `git status`) *before* anything is staged. **(c) is explicitly not recommended** for the reason
given. **(b) is a defensible stopping point** if you want the rule corrected without deciding the commit question
today.

**[Answer]**: (d) — both problems addressed, but as two separately-gated passes: correct the .gitignore rule first, verify it with git check-ignore and git status, then treat committing everything as its own separate, reviewed step. Do not do (c) — a partial fix that only commits what's currently reachable would look complete while still hiding the entire BUILD record, which is worse than the current honestly-broken state.

---

### Q2 — How is the `build/` rule corrected?

§1.4 established it protects nothing that exists, so all three options are low-risk. They differ in intent.

* **(a) Delete the `build/` line entirely.** Vite writes to `dist/`, already covered at line 18. Simplest, and
  removes a rule with no current purpose. Risk: a future tool configured to output to `build/` would be committed
  — a real but easily-corrected future concern.
* **(b) Anchor it to the frontend** — replace `build/` with `frontend/build/`. Preserves the rule's **original
  intent** exactly, keeps protection if the frontend build output ever moves, and stops matching documentation
  directories at any depth.
* **(c) Keep `build/` and add negations** — `!guide-docs/build/` and `!.project-guide-rule-details/build/`.
  ⚠️ **Fragile**: git negation of a directory whose *parent* is excluded is a well-known footgun, requires
  care to re-include nested contents, and it would need a new negation each time another `build/` directory
  appears. **Most complex, least robust.**

**Recommendation: (b).** It is the only option that **preserves the rule's stated intent** (it sits under the
`# Node / frontend` heading beside `node_modules/`) while eliminating the collateral damage, and it needs no
negation machinery. **(a) is a reasonable simplification** given `dist/` already covers the real output path —
choose it if you'd rather delete a dead rule than anchor it. **(c) is not recommended.**

⚑ **Whichever is chosen, add a comment** recording *why*, so the next person doesn't "tidy" it back to `build/`.

**[Answer]**: (b) — anchor the rule to frontend/build/, replacing the unanchored build/ line. This preserves the rule's original stated intent (it sits under "# Node / frontend" beside node_modules/) while eliminating the collateral match against any build/ directory at any depth. Add a comment explaining why, so a future "cleanup" doesn't revert it to the unanchored form.

---

### Q3 — Is `.project-guide-rule-details/build/` in scope?

⚑ **Newly found in this pass** (§1.3) — the 6 BUILD-phase rule files `CLAUDE.md` instructs the workflow to load.
Its 21 sibling files under `.project-guide-rule-details/` **are already tracked**, so the directory is currently
**half-committed**.

* **(a) Yes — same fix, same pass.** Q2(a) and Q2(b) both un-ignore it automatically; it then needs adding.
* **(b) Yes to un-ignoring, no to committing** — treat the methodology's files as vendored content tracked
  separately from project work.
* **(c) Out of scope** — leave it ignored and decide separately.

**Recommendation: (a).** The directory is **already 21/27 committed**, so excluding the remaining 6 is an
inconsistency, not a policy. Committing them makes the workflow that produced this build **reproducible from the
repo** — which is the same argument that makes the BUILD docs worth committing. **(c) is hard to justify**: it
leaves a known-ignored directory that the workflow actively reads.

**[Answer]**: (a) — same fix, same pass. .project-guide-rule-details/build/ is already 21/27 tracked; leaving the remaining 6 files ignored is an inconsistency, not a policy, and those are the files CLAUDE.md instructs the workflow to load. Un-ignore and commit them alongside everything else.

---

### Q4 — If committing (Q1 a/d): one commit, or several?

≈**960 files**, ≈**10 MB**.

* **(a) One commit** — *"BUILD phase: 24 units, docs, register."* Simple, honest, one boundary.
* **(b) Two commits** — (i) the `.gitignore` correction; (ii) everything else. Makes the rule change reviewable in
  isolation and visible in history as a deliberate act.
* **(c) Several, by area** — e.g. `.gitignore` · `backend/` · `frontend/` · `guide-docs/build/` · config +
  artifacts. More navigable history; more staging work.
* **(d) Per-unit commits reconstructing build order.** ⚠️ **Not recommended** — it would **fabricate a history
  that did not happen**, which cuts directly against this project's audit-trail discipline. Recording ~960 files
  as one honest "this is the state at close of BUILD" commit is **more truthful** than a synthesised sequence.

**Recommendation: (b), or (c) if you want a more navigable history.** (b) pairs naturally with Q1(d). **(d) is
explicitly not recommended** for the honesty reason above.

**[Answer]**: (b) — two commits: one for the .gitignore correction alone (reviewable in isolation, visible in history as a deliberate act), one for everything else. Explicitly not (d) — fabricating a per-unit commit sequence that didn't actually happen in real time would misrepresent this project's own history, directly against the audit-trail discipline this build has held throughout.

---

### Q5 — What about `corpus/`, `testresults.txt`, and `.env.example`?

Three files in the untracked set have prior decisions or open questions attached:

* **`corpus/` (7 files, 604 KB)** — **already decided**: tier-B Stage 1's Q7(a) committed it as the evidence
  artifact, with `corpus/README.md` labelling it. It is untracked only because **nothing has been committed at
  all**. Including it simply executes a decision already made.
* **`testresults.txt`** — the subject of **register #12** (`append-vs-overwrite`). Committing it does not resolve
  #12; it just tracks a file that is overwritten per run. ⚠️ **Committing a per-run-overwritten file makes every
  future run a spurious diff.**
* **`.env.example`** — **must be committed**: it is placeholder-only by design, and frozen U16's
  `test_env_example_is_committed_and_placeholder_only` asserts it **exists**. `.gitignore` already has an explicit
  `!.env.example` negation for exactly this purpose.

* **(a)** Commit all three.
* **(b)** Commit `corpus/` and `.env.example`; **gitignore `testresults.txt`** and note it against #12.
* **(c)** Commit `.env.example` only; defer `corpus/` and `testresults.txt`.

**Recommendation: (b).** `corpus/` and `.env.example` are settled. `testresults.txt` is a **generated per-run
artifact** — tracking it guarantees noise in every future diff, and ignoring it is the conventional treatment.
⚑ **Note honestly**: ignoring it does **not** discharge register **#12**, which is about losing per-unit history;
it just stops the churn. #12 stays open either way.

**[Answer]**: (b) — commit corpus/ (already decided at tier-B Stage 1's Q7-a) and .env.example (required by frozen U16's test); gitignore testresults.txt as a per-run-generated artifact. State explicitly in the commit or its accompanying note that ignoring testresults.txt does not discharge register #12 — that item is about losing per-unit history, not about diff noise, and it stays open regardless of this decision.

---

### Q6 — Does this become a register item, and how is it verified?

* **(a) Open it as a register item, then close it in the same pass** — consistent with the register being the
  project's disclosure ledger; gives the fix a permanent, citable record.
* **(b) Fix it without a register item** — it is repo hygiene, not a system defect, and no behaviour depends on
  it. Record it in `guide-state.md` / `audit.md` only.
* **(c) Open it and leave it open** until a clean-checkout verification has actually been performed.

**Recommendation: (a).** The register has consistently tracked **disclosure and reproducibility** gaps, not just
behavioural defects — **#12** (`testresults.txt` housekeeping) and **#13** (a stale filename) are both precedents
for something non-behavioural. Opening and closing it in one pass gives the correction a citable record without
leaving a permanent open item for something genuinely finished.

**Verification, whichever is chosen** — three checks, all cheap and decisive:
1. `git check-ignore -v guide-docs/build/plans/x.md` → **no match** (the rule no longer catches it).
2. `git status --porcelain` → **empty** after the commit, **and** `git ls-files | wc -l` ≈ **1,040**.
3. ⚑ **The real proof — a clean-checkout test**: `git clone` (or `git archive`) to a temp directory and confirm
   `backend/`, `guide-docs/build/` and `.project-guide-rule-details/build/` are all present. **This is the only
   check that actually tests the property that was broken**, and it is why (c) is a legitimate choice if that
   test cannot be run here.
4. **Full suite re-run** — expected **unchanged at 1578 / 0 / 43 / 5 / 99.87%** (no code changes; `.gitignore` is
   read by exactly two U16 tests, both unaffected per §1.5).

**[Answer]**: (a) — open the register item and close it in the same pass, giving the correction a citable, permanent record consistent with how #12 and #13 already track non-behavioral disclosure/reproducibility gaps. Run all four verification checks, and treat the clean-checkout test as the load-bearing one — if it can't actually be run in this environment, say so plainly and record the item as verified-by-the-other-three-checks-only, not silently upgraded to fully verified.

---

## 4. Holds for this pass — all upheld

**No `.gitignore` edit made · no `git add` · no commit · no file moved or deleted.**
No frozen-23 unit internal or test edited · U22's `DEFERRED_REGISTER` and its frozen tests untouched · WIRE-1
unamended · `not_wired.py` not renamed · U23's frozen test unedited · `audit_store` Docker-guard gap untouched
(**5 errors stay exactly 5**) · **tier-B Stages 2 and 3 not authorized** · #18's spend guardrails untouched ·
**no API call, no money spent**.

**Carried forward, not re-run**: **1578 passed / 0 failed / 43 skipped / 5 errors / 99.87%.**
**Register unchanged at 23 tracked** — 17 open · 2 discharged · 4 narrowed.

---

## 5. After the answers

1. **Ambiguity-check** — at minimum: (i) confirm the chosen Q2 form **actually** stops matching both directories
   (`git check-ignore` before/after) and **still** matches any real frontend build output; (ii) confirm U16's two
   `.gitignore`/`git ls-files` tests stay green; (iii) confirm no **ignored** path (`.env`, `venv/`,
   `node_modules/`, `__pycache__/`) becomes stageable as a side effect — **the one genuinely risky failure mode
   here is over-un-ignoring**, and it must be checked, not assumed.
2. **Execution**, gated per Q1's answer.
3. **Verification** per Q6, including the clean-checkout test if available.
4. **Register + `guide-state.md` + `audit.md`** updated per Q6.

**⚑ This document authorizes nothing. STOPPING at the plan-file gate.**
