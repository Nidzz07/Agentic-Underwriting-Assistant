# Outlier Wiring Plan — closing register #17, and correcting what #17 says

**Stage**: POST-BUILD → scoping/planning pass
**Status**: ✅ **PLAN COMPLETE — all 8 questions answered (Q1–Q7 embedded, then Q8 surfaced by the check and
answered). Ambiguity-check CLEAN (5 folds). Backend-only execution plan written (§5), 14 steps, predicted 1615 →
1621.** Superseded status line, preserved: *"⛔ PLAN GATE — 7 questions open, none pre-filled. No code written. No
backend file touched."* — true at the time it was written, false once the answers landed.
**Date**: 2026-07-26
**Predecessors**: `frontend-backend-wiring-plan.md` (Q5(c) excluded outlier), `override-wiring-plan.md` (the mounting pattern this would follow), commit `17a626c`

---

## 0. ⛔ Read this first — the premise this pass was scoped on is false

The override pass was "mount an already-working thing." **This is not that.** The investigation found that register
#17's central factual claim does not hold for the running system, and that its stated owner is mis-attributed.
Both findings change the shape of the work, and neither should be discovered mid-execution.

**#17 says**: *"`PendingRecommendation.outlier_canonical` **persists real outlier data** … The data exists; the
frozen contract forbids sending it."*

**Measured on disk**: there is **no outlier data anywhere in the system**, and the contract is not the first thing
stopping it — it is the *last*.

---

## 1. Measured inventory — verified this session, not inferred

### 1.1 ⚑ FOUR stacked barriers. #17 describes only the last two.

| # | Barrier | Evidence |
|---|---|---|
| **1** | **Nothing computes an outlier score in any API-reachable path.** The only production `score_outlier` returns `None`. | `backend/scripts/seed_demo_cases.py:214` |
| **2** | **Therefore `outlier_canonical` is NULL for every persisted case** — the pipeline stores it only `if outlier is not None`. | `backend/case_lifecycle/pipeline.py:133-135` |
| **3** | R4's projection hardcodes `"outlier": None` regardless of what is stored. | `backend/app/projections.py:138` |
| **4** | WIRE-1 binds `outlier` null **in Phase 1**. | `api-contract.md:177` |
| **5** | ⛔ **`OutlierResult` CANNOT BE PERSISTED AT ALL.** `CanonSerAdapter.canonical_bytes` rejects IEEE float (`CanonSerError: float is not permitted; use Decimal (CON-DET-1)`), and `outlier_score` / `z_score` / `shap_value` are all `float`. **Found during execution, 2026-08-01 — see §4.1.** | `common/canon_ser.py:57` vs `outlier_model/schemas.py` |

The Phase-1 return is deliberate and documented, not an oversight:

```python
def score_outlier(self, profile):
    """⚑ Phase 1 emits no outlier (services.md omits the OUT call), and WIRE1-Fold-4
    binds R4's outlier to null regardless. Returning None is the honest Phase-1
    behaviour, not a stub standing in for something that should be here."""
    return None
```

⚑ **`backend/app/` never imports `outlier_model` at all** — verified by repo scan; the only occurrences are prose in
`projections.py`. The API layer has no reference to the outlier capability in any form.

**What #17 actually describes** is U24's schema *capability* — `PendingRecommendation` **can** carry
`outlier_canonical`. That is true. **"The data exists" is not.** A reader relying on #17 would conclude the work is
"unblock the projection"; it is not.

### 1.2 The model and the corpus both genuinely work — the gap is neither

* **`backend/outlier_model/`: 51 tests pass** — determinism, swap-invariance (bias), no-demographic-read, SHAP
  attribution, threshold, provenance, imputation, no-global-RNG.
* **The corpus is real and committed**: `corpus/profiles.json` — **300 profiles**, `120/105/75` (band delta
  **0.00pp**), **all 8 DATA-2 edge cases present**, DET-1 proven by three runs producing identical
  `content_hash 57821891…`, `seed 42`, `corpus_version 1.0.0`.
* **Public surface**: `OutlierModel.fit(...) -> FittedOutlierModel`, then `.score(profile) -> OutlierResult`
  (`outlier_score`, `is_outlier`, `flagged_features[]`, `provenance`). Advisory-only by construction — **no verdict
  field**, which is what keeps R4's advisory-only invariant intact.

⚠️ Disclosed: the corpus manifest records `"model_version": "OFFLINE-DOUBLE-NOT-A-REAL-LLM"` — profiles came from
the deterministic offline double (register #18's consequence), not a real LLM. Structurally valid for scoring;
recorded so no one later reads the corpus as LLM-authored.

**So the gap is not the model, and not the corpus. It is that nothing connects them to anything.**

### 1.3 ⚑ WIRE-1 likely needs NO amendment — #17's owner appears mis-attributed

#17 names the owner as *"a future WIRE-1 amendment."* WIRE-1's own binding text (`api-contract.md:177`):

> `outlier` is **`null` when `status: pending`** *and* **`null` in Phase 1** … ; **populated only for a Phase-2
> `ready` view**.

**Populating outlier data for a Phase-2 ready view is contract-COMPLIANT, not a contract change.** WIRE-1
anticipated and specified this case. What is required is **implementing Phase 2**, not amending the contract.

⚑ If this reading holds, the standing "do not touch WIRE-1" constraint is **not engaged by this work at all** — a
materially different pass than #17's text implies. **Q2 and Q3 exist to settle this deliberately rather than let a
scoping pass quietly reinterpret a pinned contract.**

### 1.4 The frontend unit is complete — and was designed for exactly today's state

**158 tests across 20 files, all passing.** Components, copy, seam, testids, role-invariance, error/empty/transition
states — the same completeness `overrideForm` had.

⚑ `OutlierView.jsx:18-20` records that the state discriminator is the **`outlier` field**, deliberately **not** R4's
`status`, because *"a Phase-1 `status:\"ready\"` body can STILL carry `outlier: null`"*. **Mounted today it would
render `NOT_AVAILABLE` permanently** — correct, honest, and exactly the "renders permanently empty" outcome the
original wiring pass cited when excluding it.

### 1.5 ⚑ `seams.js` needs a SIXTH key — the deferred Q4(b) cost, coming due

Unlike override (already registered, zero seam cost), **outlier is NOT in `seams.js`**. Adding it breaks a
currently-green exact-key assertion — `app.test.jsx:547-550`:

```js
it('wires all five units seams', () => {
  expect(Object.keys(seams).sort()).toEqual(['commit', 'history', 'memo', 'override', 'queue']);
});
```

This is **precisely the Q4(b) edit the original wiring pass declined** ("Breaks the existing `wires all five units
seams` test (exact-key equality) — a test edit, gated by Q6"). It is a **known, disclosed cost**, named here in
advance so it is not met as a surprise mid-execution. It is a genuine test change requiring explicit
acknowledgement — not merely an addition. **Q4.**

### 1.6 The API has no drafting trigger — which is where the real difficulty sits

Drafting happens **only** in `backend/scripts/seed_demo_cases.py` (`CasePipeline` is constructed nowhere else
outside tests). The API exposes reads plus R5's commit; **no route drafts a case**. That is register **#2**'s
residual, not a new finding — but it determines where outlier scoring can be wired at all, and it means **any fix
must touch a backend file**. **Q1 and Q5.**

### 1.7 The minimal technical path, stated concretely

1. Fit a `FittedOutlierModel` from the committed corpus (`CorpusSource.from_file('corpus/profiles.json')`).
2. Have the drafting path's `score_outlier` return `model.score(profile)` instead of `None`.
3. Re-seed, so `outlier_canonical` is populated for real cases.
4. Unblock `projections.py:138` to emit the stored `OutlierResult` for a `ready` view.
5. Register the sixth seam and mount `OutlierView` (Q4).

**Steps 1–4 are backend. Step 5 is the only part resembling the override pass.**

---

## 2. Open decisions — answer inline, none pre-filled

### Q1 — one combined pass, or a backend remediation pass FIRST?

The backend work (§1.7 steps 1–4) is a real remediation: it touches the seed script, requires re-seeding a
database, and changes what R4 emits. The mount is trivial afterward. Precedent shape: the CRLF checksum issue, the
migration entrypoint (`__main__.py`), and #19 were each handled as their own focused backend fixes before anything
consumed them.

- **(a) Backend remediation pass FIRST, mounting as a separate follow-on. — RECOMMENDED.** Three grounds, each
  measured rather than stylistic: **(i)** mounting before the backend works reproduces exactly the
  "permanently empty surface" outcome the original wiring pass rejected — and this time knowingly, which is worse;
  **(ii)** the backend change is where all the risk is (re-seeding, a corpus dependency at runtime, a projection
  change), and bundling it with a test-breaking seams edit means two unrelated failure modes in one diff;
  **(iii)** it mirrors the shape this project has used for every backend gap so far, and the override pass showed
  how cheap the mount is *once the backend is proven*. ⚑ It also means the mount pass gets a **real** manual
  verification (an actual score rendered) instead of asserting an empty state.
- **(b) One combined pass** — backend fix + mount + tests together. Fewer gates, one diff, one verification. But it
  couples a backend remediation to a frontend test-contract change, and if the backend proves harder than §1.7
  suggests, the frontend work is stranded mid-pass.
- **(c) Backend pass only; defer the mount indefinitely.** Closes the real gap and leaves the UI decision open.
  Honest, but leaves a fully-built, fully-tested unit unmounted for a third pass running.
- **(d) Frontend mount first (rendering `NOT_AVAILABLE`), backend later.** Rejected on the wiring pass's own
  recorded reasoning: a surface that can only ever be empty implies a capability that does not exist.

**[Answer]**: (a) — backend remediation pass first, mounting as a separate follow-on. Mounting before the backend works would knowingly reproduce the exact "permanently empty surface" outcome the original wiring pass rejected, and bundling a real backend fix with a test-breaking seams edit puts two unrelated failure modes in one diff.

---

### Q2 — what does "Phase 2" mean as a scoping boundary for THIS work?

"Phase 2" comes from `services.md`, where it bundles **`OutlierService` (C3)** *and* **`ObservabilityService`
(Langfuse traces + Prometheus/Grafana)**. ⚑ **This pass must not silently absorb an undefined boundary** — "we are
now in Phase 2" could later be read as claiming observability work that was never done.

- **(a) Define a NAMED MINIMAL SLICE — "Phase-2-OUT" — and claim only that: an API-reachable path that computes a
  real `OutlierResult` and persists it, plus R4 emitting it for a `ready` view. Explicitly NOT ObservabilityService,
  NOT Langfuse, NOT Prometheus/Grafana, and NOT a drafting trigger in the API. — RECOMMENDED.** It is the smallest
  slice that satisfies WIRE-1's "Phase-2 `ready` view" precondition, and naming it prevents a future reader from
  inferring the rest of Phase 2 shipped. The claim recorded would be precise: *"the OUT call is no longer omitted"*,
  not *"the system is in Phase 2."*
- **(b) Declare full Phase 2 in scope.** Honest to `services.md`'s own grouping, but drags observability into an
  outlier pass — a large, unrelated body of work.
- **(c) Avoid the term "Phase" entirely**; describe the change purely as "R4 now emits stored outlier data."
  Sidesteps the ambiguity but loses the link to WIRE-1's binding text, which is phrased in phases — and that link
  is what makes the change contract-compliant rather than a contract change.
- **(d) Treat the phase boundary as a WIRE-1 question and amend the contract to say so.** Rejected unless Q3
  concludes WIRE-1 genuinely blocks this; §1.3 indicates it does not.

**[Answer]**: (a) — a named minimal slice, "Phase-2-OUT": an API-reachable path computing and persisting a real OutlierResult, plus R4 emitting it for a ready view. Explicitly not ObservabilityService, Langfuse, Prometheus/Grafana, or an API drafting trigger. Record the claim precisely as "the OUT call is no longer omitted," not "the system is in Phase 2."

---

### Q3 — should register #17's TEXT be corrected?

#17 has **two defects**: its premise (*"the data exists"*) is false for the running system (§1.1), and its owner
(*"a future WIRE-1 amendment"*) appears wrong (§1.3). A future reader relying on it would mis-scope the work in
both directions — thinking it smaller than it is, and thinking it requires a contract change it likely does not.

- **(a) Correct #17 in place via supersession — preserve the original row verbatim as the historical record, add a
  correction stating the four-barrier structure and the corrected owner. — RECOMMENDED.** Exactly the discipline
  used for `httpTransport.js`'s AUTH docstring, `seams.js`'s backing table, the `app.test.jsx` rename, and every
  prior register correction: **supersede, never rewrite; the old text stays readable.** One accurate item is better
  than two partial ones, and the register is already at 26.
- **(b) Leave #17 untouched and open a NEW item** for the missing scoring path (barriers 1–2), letting #17 continue
  to describe barriers 3–4 only. Arguably more faithful — the two gaps have different owners — but it leaves a
  standing item whose premise is **false as written**, which is the thing worth fixing.
- **(c) Both — correct #17's premise AND split barriers 1–2 into their own item.** Most precise; costs a 27th
  register item and some overlap between the two entries.
- **(d) Leave it; record the correction only in this plan.** Rejected: plans are not the register, and the false
  premise would survive in the document people actually consult.

**[Answer]**: (a) — correct #17 in place via supersession, preserving the original row verbatim as the historical record, with a correction stating the four-barrier structure and the corrected owner. Same discipline as every other correction in this project.

---

### Q4 — the `seams.js` sixth key and the five-key assertion (§1.5)

Applies when mounting happens (this pass under Q1(b), a later pass under Q1(a)).

- **(a) Add `outlier` as the sixth key and supersede the assertion to `['commit','history','memo','outlier','override','queue']`, with a comment recording the old five-key set and why it changed. — RECOMMENDED.** Supersede-not-rewrite,
  the pattern used three times already in this file. The assertion keeps its teeth — exact-key equality, just over
  the correct set — and nothing is deleted or loosened. ⚑ Requires explicit acknowledgement that a **currently-green
  test is being changed**, which is why it is a question and not a footnote.
- **(b) Relax the assertion to a subset check** (`toContain`). Rejected: it would stop catching an accidentally
  dropped or misnamed seam, which is the whole point of exact-key equality.
- **(c) Register the sixth seam WITHOUT mounting the view.** Breaks the test for no user-visible gain.
- **(d) Defer entirely — do not register outlier this pass.** Correct under Q1(a)/(c), where mounting is out of
  scope; then this question simply moves to the mount pass rather than being answered now.

**[Answer]**: (a) — add outlier as the sixth key, supersede the exact-key assertion to the six-key set with a comment recording the old five-key set and why it changed. This applies at the mount pass, per Q1(a)'s sequencing — note this now so it's not treated as a surprise when that pass begins.

---

### Q5 — WHERE does outlier scoring get wired?

Constrained by §1.6: drafting happens only in the seed script, so that is the only place a score can currently be
computed for a real case.

- **(a) Wire it in `seed_demo_cases.py`'s seams — fit once at startup from the committed corpus, return
  `model.score(profile)`. — RECOMMENDED.** It is the only production drafting path that exists; it is a
  **script**, not the API surface, so the blast radius is contained; and it needs no new route. The honest
  description of the result: *"seeded cases now carry real outlier data"* — which is what R4 then serves.
- **(b) Build a real `OutlierService` in `backend/app/` and inject it via `dependencies.py`.** Architecturally
  tidier, but the API **has nothing that drafts**, so the service would have no caller — machinery with no path to
  it.
- **(c) (a) now, (b) later when a drafting trigger exists** (register #2 territory). Compatible with (a); records
  the intent without building unreachable machinery.
- **(d) Score lazily inside R4 on read.** Rejected on two grounds: it would make a GET compute an ML score per
  request, and the score would not be persisted — breaking replay/auditability, which the brief treats as
  non-negotiable.

**[Answer]**: (a) — wire scoring in seed_demo_cases.py's seams, fitting once at startup from the committed corpus. It's the only production drafting path that exists, contained blast radius, no new route needed.

---

### Q6 — the corpus as a RUNTIME dependency

Scoring requires fitting against `corpus/profiles.json` (committed, 615KB). Today the corpus is a **build/test-time**
artifact; using it at seed time makes it a runtime input. `CorpusSource` was explicitly built to impose **no hard
`corpus/` dependency** (BR-OUT-8 / NFR-OUT-CORPUS-1).

- **(a) Fit at seed time from the committed corpus file, and fail LOUDLY with a clear message if it is absent.
  — RECOMMENDED.** The corpus is committed, so the path exists in any checkout; and a loud failure is the honest
  behaviour for a seed script whose whole job is producing complete demo data. ⚑ It does **not** violate BR-OUT-8:
  that binds `outlier_model` (which still needs no corpus present), not a caller that chooses to supply one.
- **(b) Fit at seed time, but fall back to `outlier=None` if the corpus is missing.** Preserves today's behaviour
  as a graceful degrade — but silently reproduces the exact defect this pass exists to fix, and would be very hard
  to notice.
- **(c) Precompute and persist a fitted model artifact**, loaded at seed time. Avoids refitting; adds a binary
  artifact, a versioning question, and a staleness risk against `corpus_version`.
- **(d) Defer — decide when deployment (Render) is addressed.** ⚑ Worth noting regardless: whether `corpus/` ships
  to the deployed backend is a **real** open question this plan does not answer, and (a) does not settle it.

**[Answer]**: (a) — fit at seed time from the committed corpus file, fail loudly if absent. The corpus is committed and present in any checkout; a loud failure is the honest behavior for a script whose job is producing complete demo data. Note explicitly, per your flag: whether corpus/ ships to the deployed backend remains a real open question this pass does not answer, and should be carried forward to the eventual deployment pass rather than forgotten.

---

### Q7 — verification depth for the backend half

The standard this project has set (Step 7 / Step 10 / Step 12) is evidence from a real database, not a passing test.

- **(a) Full: re-seed against real Postgres → `psql` read-back confirming `outlier_canonical` is NON-NULL → `curl`
  R4 confirming a real `OutlierResult` on the wire (score, `is_outlier`, flagged features with SHAP values,
  provenance) → determinism spot-check that re-scoring the same profile yields an identical score. — RECOMMENDED.**
  The determinism check matters more here than anywhere else in the build: **reproducibility is an acceptance
  criterion (100%, §6)** and an outlier score is the one number in the system produced by a fitted ML model. It
  would be the first live evidence that seeded randomness holds end-to-end.
- **(b) Full minus the determinism spot-check.** Cheaper; leaves the one genuinely new risk unmeasured.
- **(c) `psql` read-back only**, no wire check. Proves persistence, not that R4 serves it.
- **(d) Automated tests only.** Rejected on this project's record: the 204 defect and the override gaps were both
  found by manual verification and by nothing else.

**[Answer]**: (a) — full verification: re-seed against real Postgres, psql read-back confirming outlier_canonical is non-null, curl R4 confirming a real OutlierResult on the wire, and a determinism spot-check re-scoring the same profile for an identical score. Reproducibility is a 100% acceptance criterion and this is the one number in the system produced by a fitted ML model — worth confirming properly.

---

## 3. Mandatory ambiguity-check — combined answer set

**Answer set**: Q1(a) · Q2(a) · Q3(a) · Q4(a) · Q5(a) · Q6(a) · Q7(a). Every finding below was **measured on disk
or executed this session**, not inferred.

**Internal consistency, checked first**: Q1(a) defers all frontend work, which makes Q4(a) a *recorded forward
commitment* rather than this pass's work — no conflict, and it is carried in §5 so the mount pass inherits it.
Q5(a) and Q6(a) both land in `seed_demo_cases.py` and interact — that interaction is Folds A and B, and it is the
one place the answer set needed reconciling. Q2(a)'s named slice bounds exactly what Q7(a) must verify. **No answer
contradicts another.**

**Result: CLEAN on the seven answered questions — 5 folds resolved — but ⛔ ONE NEW QUESTION IS SURFACED (Q8).**
It concerns whether a frozen unit must be reopened, which is not something a fold may decide.

### ⚑ Fold A (DIRECTED) — does "fit once at startup" behave across repeated seed-script runs?

**Yes, and determinism is confirmed by execution, not by reading the code.**

`seed_demo_cases.py` is a one-shot CLI (`python -m backend.scripts.seed_demo_cases --cases 3`), so "startup" means
**once per invocation**; re-running refits from scratch. That is safe, because the fit is deterministic by
construction *and* in fact:

* `OutlierModel.fit` uses `RandomState(manifest.seed)` — an **explicit local instance**, seed single-sourced from
  `CorpusManifest`, with `random_state=rng` injected into `IsolationForest` and the **global `np.random` never
  touched** (`model.py:113-121`).
* **Measured this session** against the committed corpus: two *independent* fits scored the same profile at
  `0.667071302659` — **byte-identical to 12 decimal places** — and re-scoring on one model was identical too.

**Measured cost** (300 profiles, this machine):

| Operation | Time |
|---|---|
| corpus load + parse | **0.164 s** |
| fit #1 | **2.701 s** |
| fit #2 | **2.507 s** |

⚠️ **~2.6 s per fit is NOT free, and that is the finding.** For a one-shot seeding run it is irrelevant. **Inside
`_SeedSeams.__init__` it is not** — see Fold B, where six existing tests construct that class.

### ⛔ Fold B (DIRECTED) — could Q6(a)'s loud failure break anything relying on the seed script?

**Deployment: no. Tests: YES — and naively implemented it would re-open a previously-fixed defect.**

* **`render.yaml` does NOT invoke the seed script.** Its only release step is
  `preDeployCommand: python -m backend.scripts.run_migrations`. **Deployment is unaffected** by any change here.
* **But `backend/scripts/tests/test_seed_demo_cases.py` constructs `_SeedSeams()` in SIX tests**, and one
  (`test_the_demo_path_reaches_drafted_and_r4_reports_ready`) builds a `CasePipeline` and calls `draft()`.

If corpus-fitting were placed **inside `_SeedSeams.__init__`** with a fail-loud on a missing corpus, three separate
problems follow, all avoidable:

1. ⚑ **It re-opens the exact defect class that file exists to catch.** `test_seed_seams_constructs_without_raising`
   was written because `__init__` once raised `TypeError` **on its first statement**, so `main()` "could not
   complete under ANY invocation". Adding a new hard failure mode to that same constructor is inviting the same
   defect back under a new name.
2. **~2.6 s × 6 constructions ≈ +16 s** on the backend suite, for tests whose subject is not outlier scoring.
3. `test_the_offline_default_path_needs_no_sdk_no_key_and_no_network` asserts the default path needs nothing
   external. A **mandatory** file read does not literally violate "no SDK, no key, no network", but it sits close
   enough to that test's subject that it should not be introduced silently.

**RESOLUTION — inject the fitted model; do not fit in the constructor.** `_SeedSeams` already takes an **injected
`llm_client`** with an offline default; the outlier model follows that established shape:

* `_SeedSeams(..., outlier_model=None)` — when `None`, `score_outlier` returns `None` exactly as today, so all six
  existing tests keep **byte-identical current behaviour, need no corpus, and pay no fit cost**;
* `main()` builds the fitted model from the committed corpus and **injects** it — and that is where Q6(a)'s
  **loud failure** belongs, because that is the path whose job is producing complete demo data.

This honours Q5(a) ("fit once at startup from the committed corpus") and Q6(a) ("fail loudly if absent") **exactly
as answered**, while confining both to the entrypoint rather than the constructor. **Zero existing tests change.**

### Fold C — the R4 projection change is small, but it needs a deserializer that does not yet exist

`pipeline.py:134` stores `CanonSerAdapter.canonical_bytes(outlier)` — **serialization already works** (the method
is generic over `BaseModel`). **Deserialization does not exist**: `audit_store/canon_adapter.py` exposes only
`profile_from_canonical` and `report_from_canonical`, and `memo_from_canonical` lives separately in
`case_lifecycle/memo_adapter.py`. **There is no `outlier_from_canonical` anywhere.** Where it should live is
**Q8** — it is the one decision in this set that could require reopening a frozen unit.

### Fold D — Q2(a)'s named slice is enforceable, not just aspirational

"Phase-2-OUT" excludes `ObservabilityService`. Verified this is a real boundary and not a fiction: `render.yaml`
already declares `LANGFUSE_*` as **"Phase-2 reserved (set-not-consumed by U23)"**, so observability has its own
declared, untouched surface. This pass reads none of those variables and adds no tracing. The recorded claim will
be *"the OUT call is no longer omitted"* — never *"the system is in Phase 2."*

### Fold E — Q7(a)'s determinism spot-check has a defined pass condition

Because Fold A already measured it, the manual check is not open-ended: **re-scoring the same profile must yield
the identical `outlier_score`**, and a re-seed must reproduce the same stored value. The reference value observed
this session for `corpus/profiles.json[0]` is `0.667071302659` with `provenance.corpus_version=1.0.0`, `seed=42`.
⚑ Anything else means seeded randomness is not holding, which would be a **blocking** finding against acceptance
criterion §6 (reproducibility 100%).

---

## 4. ✅ NEW QUESTION SURFACED BY THE CHECK — **ANSWERED**

### Q8 — where does `outlier_from_canonical` live? (Fold C)

R4 must turn `outlier_canonical` bytes back into an `OutlierResult`. No such deserializer exists. The three
candidate homes differ in **whether a frozen unit must be reopened**, which is why this cannot be a fold.

- **(a) Deserialize in the composition root — `backend/app/projections.py` — via `OutlierResult.model_validate_json(...)`, importing the schema by value from `outlier_model`. — RECOMMENDED.** `backend/app/` is the composition
  root and is **not frozen**; it is the layer whose job is exactly this translation, and it already imports across
  units. WIRE-1 specifies `OutlierResult` is carried **"by value" from U18**, so a by-value schema import is the
  contract's own framing. ⚑ **Reopens no frozen unit and needs no authorization** — the only option with that
  property.
- **(b) Add `outlier_from_canonical` to `audit_store/canon_adapter.py`.** Symmetric with the two existing
  `*_from_canonical` methods. ⛔ `audit_store` is **frozen** — this needs an authorized reopening for one method.
- **(c) Add a new adapter in `case_lifecycle`, mirroring `memo_adapter.py`'s precedent.** Strong precedent: that
  file exists precisely so a memo could be deserialized without touching `audit_store`. ⛔ But `case_lifecycle`
  (U24) is also frozen and has already been reopened three times; this would be the **fourth**.
- **(d) Have `PostgresCaseStore` return a decoded `OutlierResult`** instead of bytes. Rejected: it changes a
  repository's return shape, touching U24 **and** every existing caller.

**[Answer]**: (a) — deserialize in the composition root, backend/app/projections.py, via OutlierResult.model_validate_json(...), importing the schema by value from outlier_model. This reopens no frozen unit and needs no authorization, and WIRE-1 already frames OutlierResult as carried "by value" from U18, so this is the contract's own framing, not a new decision.

---

## 4.1 ⛔ BARRIER #5, found during execution — and its named resolution

**Discovered at step 8 on 2026-08-01, not at planning time.** ⚑ **Fold C's central claim was
FALSE.** It stated: *"`pipeline.py:134` stores `CanonSerAdapter.canonical_bytes(outlier)` —
**serialization already works** (the method is generic over `BaseModel`)."* It is generic over
`BaseModel` **structurally**, but CANON-SER's **P2** invariant forbids the field *type*
`OutlierResult` is built from. Fold C treated deserialization as the only gap. **Serialization is
also a gap, and it is the harder one.** Reproduced two ways before anything was decided:

| Level | Result |
|---|---|
| `CanonSerAdapter.canonical_bytes(OutlierResult(...))` | `CanonSerError: float is not permitted; use Decimal (CON-DET-1)` |
| `CasePipeline.draft()` with a real fitted model injected | **`DRAFT RAISES: CanonSerError`** — the case never reaches `drafted` |

The conflict is architectural, not incidental: **U18 emits floats by nature** (IsolationForest
scores, SHAP attributions, z-scores) while **CANON-SER forbids float by design**, because binary
float is not portably reproducible and the audit chain's whole value is byte-reproducibility.

### RESOLUTION — the Decimal-quantized projection seam (user decision, 2026-08-01)

`score_outlier` returns a **`QuantizedOutlierResult`** — a Decimal-typed projection of
`OutlierResult`, with `outlier_score` and every `z_score` / `shap_value` quantized to a **single
named precision constant** (`OUTLIER_QUANT_DECIMAL_PLACES = 12`, matching the precision Fold A/E
actually observed). `projections.py` dequantizes on read, so the wire keeps the float shape
`outlierView` already expects.

⚑ **Why this and not the alternatives**: it is the **only** option that reopens **no frozen
unit**. `CaseSeams.score_outlier` is typed `Optional[object]` and U24 serializes whatever it is
handed, so the projection travels U24's existing path untouched. Relaxing CANON-SER would
reopen frozen `common/` **and** deliberately break CON-DET-1; converting inside U24's pipeline
or switching that field to plain JSON would each reopen U24 (its 4th reopening).

### ⛔ WHAT THIS DOES **NOT** CLAIM — state it wherever this is described

**This is a quantized projection of the model's float output. It is NOT a claim that the
underlying ML computation is bit-for-bit reproducible across library versions.** CANON-SER's
guarantee applies to the **persisted representation** — the same logical value serializes to the
same bytes — and to nothing else. Floating-point computation itself is reproducible only within a
pinned `(sklearn, numpy, platform)` combination, which is why `OUTLIER_MODEL_VERSION` bundles the
sklearn version in the first place. **No part of this stack promises cross-version FP identity,
and quantization must never be read as supplying it.** What quantization buys is exactly this: two
runs that compute the same score persist identical bytes, and a stored score reads back
unambiguously. ⚑ Round-trip losslessness is claimed **AT the named precision**, not against the
raw float — a float carrying more than 12 significant decimals is deliberately narrowed, and that
narrowing is the point, not a defect.

---

## 5. Execution plan — backend only (the mount pass is DEFERRED per Q1(a))

⚑ **Contingent on Q8.** The step table assumes **Q8(a)**; under (b) or (c) an authorized frozen-unit reopening
must precede step 4 and the predicted deltas change.

**Baselines**: backend **1615 passed / 0 failed / 43 skipped / 5 Docker-absence errors / 99.63%**; frontend
**723 / 147 / 0** — ⚑ **frontend is not touched by this pass at all** and must end unchanged.

**Predicted backend delta: ~~+6 tests → 1621~~ → SUPERSEDED 2026-08-01: +13 tests → 1628.**
The original +6 preserved as the record of what was predicted before barrier #5 was known. The
revision has two causes, both stated rather than absorbed: **barrier #5 costs +4** (T7–T10, §4.1),
and **T5 turned out to be four assertions, not one** (score, explained flags, provenance triple,
advisory-only shape) — a plan estimate that was too coarse, not a scope change. Per step:

| # | Step | File | RED first? | Δ |
|---|---|---|---|---|
| 1 | Confirm both baselines before touching anything | — | n/a | 0 |
| 2 | **T1** `_SeedSeams with no injected model scores None — today's behaviour, pinned` (Fold B's safety net: proves the six existing tests' path is untouched) | `scripts/tests/` | ✅ RED | +1 |
| 3 | **T2** `an injected fitted model makes score_outlier return a real OutlierResult` | `scripts/tests/` | ✅ RED | +1 |
| 4 | Add the `outlier_model=None` injection param + real `score_outlier` | `scripts/seed_demo_cases.py` | → turns T1/T2 green | 0 |
| 5 | **T3** `main() fails LOUDLY and by name when the corpus file is absent` (Q6(a)) | `scripts/tests/` | ✅ RED | +1 |
| 6 | **T4** `main() builds and injects a fitted model from the committed corpus` | `scripts/tests/` | ✅ RED | +1 |
| 7 | Build + inject the model in `main()`; loud failure on a missing corpus | `scripts/seed_demo_cases.py` | → turns T3/T4 green | 0 |
| **7a** | ⛔ **BARRIER #5 (§4.1).** **T7** `quantize() yields Decimal at the named precision` | `app/tests/test_outlier_canonical.py` | ✅ RED | +1 |
| **7b** | **T8** `quantize → canonical_bytes → canon_deserialize → dequantize is lossless AT the named precision` | same | ✅ RED | +1 |
| **7c** | **T9** `re-scoring the same profile yields the identical quantized value` (Fold E extended through quantization) | same | ✅ RED | +1 |
| **7d** | Implement the projection seam — named precision constant, `quantize`, `dequantize` | `app/outlier_canonical.py` (NEW) | → turns T7–T9 green | 0 |
| **7e** | **T10** `score_outlier returns the projection AND CasePipeline.draft() persists it` — the barrier-#5 regression test | `scripts/tests/` | ✅ RED | +1 |
| **7f** | Return the projection from `score_outlier`; **re-inject** in `main()` (this was reverted on 2026-08-01 to restore the demo path) | `scripts/seed_demo_cases.py` | → turns T10 **+ T3/T4** green | 0 |
| 8 | **T5** `R4 emits a stored OutlierResult for a ready view` (Q2(a)'s slice) | `app/tests/` | ✅ RED | +1 |
| 9 | **T6** `R4 still emits outlier:null when nothing was scored` (the pending / never-scored path stays correct) | `app/tests/` | ✅ RED | +1 |
| 10 | Unblock `projections.py:138` per **Q8** | `app/projections.py` | → turns T5/T6 green | 0 |
| 11 | Full backend suite; confirm **1621 / 0 / 43 / 5**, coverage ≥ threshold; **frontend re-run, expect 723 unchanged** | — | n/a | — |
| 12 | Per **Q3(a)**: supersede #17's text — original row preserved verbatim, correction stating the four barriers and the corrected owner | `BUILD-COMPLETION-REPORT.md` | n/a | 0 |
| 13 | **Manual live verification — USER-RUN** (§5.1) | — | n/a | — |
| 14 | Docs: `guide-state.md` + one `audit.md` entry | docs | n/a | — |

**Files touched: 3** — `backend/scripts/seed_demo_cases.py`, `backend/scripts/tests/test_seed_demo_cases.py`,
`backend/app/projections.py` (+ a new/extended test file under `backend/app/tests/`), plus docs. ⚑ **No frontend
file. No WIRE-1 change** (§1.3 — Phase-2 population is contract-compliant). **No frozen unit under Q8(a).**

### Named stop-gates — halt and report, do not work around

1. **Any of T1–T6 green on arrival** → the test is vacuous. ⚑ Highest risk is **T1**, which pins *current*
   behaviour and could pass trivially; it must be shown red by temporarily removing the `None` guard.
2. **Any of the six existing `_SeedSeams()` tests changes state.** Fold B's whole design is that they stay
   byte-identical. If one moves, the injection approach is wrong — stop, do not adjust the test.
3. **Backend suite ≠ 1628** (superseded from 1621 by §4.1 — see the delta note above), or the 43 skips / 5 Docker
   errors move. Report the corrected figure with its cause **before** proceeding; never adjust tests to hit the
   prediction (the 712 → 716 precedent).
4. **Frontend count ≠ 723.** This pass must not touch it at all.
5. **Coverage threshold weakened, or any threshold number edited.** Forbidden.
6. **Any frozen unit appears in `git status`** (`audit_store/`, `case_lifecycle/`, `outlier_model/`, any
   `frontend/src/<unit>/`) — under Q8(a) none should. Stop immediately.
7. **WIRE-1's `api-contract.md` appears in `git status`.** Stop.
8. **Fit time regresses materially above the measured ~2.6 s**, or the reference score
   `0.667071302659` changes → seeded determinism is not holding. **Blocking** (acceptance criterion §6).
9. **`corpus/` turns out to be needed by any test that previously passed without it.** Stop and re-open Fold B.
10. **Any commit.** Not authorized in this pass.

### §5.1 Step 13 — manual verification, user-run (Q7(a) in full)

**Preconditions**: local Postgres up, migrations applied, `corpus/profiles.json` present.

1. **Re-seed**: `python -m backend.scripts.seed_demo_cases --cases 3` → completes without error; note the ~2.6 s
   fit is expected and one-off.
2. ⚑ **`psql` read-back — `outlier_canonical` is NON-NULL**:
   ```sql
   SELECT recommendation_id, (outlier_canonical IS NOT NULL) AS has_outlier,
          octet_length(outlier_canonical) AS bytes
   FROM pending_recommendation ORDER BY recommendation_id;
   ```
   Expect **`has_outlier = true`** with a non-zero length. **This will be the first outlier data ever persisted by
   this system.**
3. **`curl` R4** on a drafted case → the body's `outlier` is a **real `OutlierResult`**, not null: an
   `outlier_score`, `is_outlier`, `flagged_features[]` each carrying a `z_score`, a **`shap_value`** and a
   `direction` of `high`/`low`, and `provenance` = `{corpus_version, seed, outlier_model_version}`.
4. **Confirm a `pending` case still returns `outlier: null`** — the null path must survive (T6's live counterpart).
5. ⚑ **Determinism spot-check** (Fold E): re-run the seed against a clean database and confirm the **same profile
   yields the identical `outlier_score`**. Reference from this session: `0.667071302659`,
   `corpus_version 1.0.0`, `seed 42`. **Any divergence is blocking.**
6. **Loud-failure check**: temporarily rename `corpus/profiles.json`, re-run the seed → it must fail **loudly and
   by name** ("corpus not found at …"), not silently seed `outlier: null`. Restore the file afterwards.

**Stop-gate**: if step 2 shows NULL, if step 3's `outlier` is null on a drafted case, if step 4's pending case
carries a non-null outlier, or if step 5 diverges — **stop and report** before any doc update or commit.

---

## 6. Holds for this pass

| Hold | Status at the plan gate |
|---|---|
| No backend file touched | ✅ Read-only throughout. `outlier_model` tests were **run** (51 passed), nothing edited. |
| WIRE-1 untouched | ✅ Read-only. §1.3 argues no amendment is needed — **that is a finding to be ratified by Q2/Q3, not an action taken.** |
| No frozen `ui-shell` component or view unit edited | ✅ `outlierView/` read only. |
| No code written | ✅ Files written: **1** — this plan. |
| No commit | ✅ User's call. |
| Register status unchanged | ✅ 26 tracked — 18 open / 4 discharged / 4 narrowed. **#17 unchanged pending Q3.** |

---

## 7. Carried forward — do not lose these

1. ⚑ **The mount pass (deferred by Q1(a))** inherits **Q4(a)** already answered: add `outlier` as the sixth
   `seams.js` key and supersede the exact-key assertion at `app.test.jsx:547-550` to the six-key set, recording the
   old set and why it changed. **Answered in advance so it is not met as a surprise.**
2. ⚑ **Whether `corpus/` ships to the deployed backend is UNRESOLVED** (Q6's flagged residual). `render.yaml`'s
   build step is `pip install -r requirements.txt` and its only release step is `run_migrations` — **nothing
   currently places or verifies `corpus/` on the deployed host**, and seeding is not part of deployment at all.
   **Carry to the eventual deployment pass.** This plan does not answer it and must not be read as having done so.
3. ✅ **Q8 — ANSWERED (a)**: deserialize in `backend/app/projections.py` via `OutlierResult.model_validate_json(...)`,
   importing the schema by value from `outlier_model`. It was the only decision that could have required reopening a
   frozen unit; **(a) reopens none**, so stop-gate 6 stands unchanged and §5's step table holds as written.

---

## 8. What closing #17 would and would not deliver

**Would**: the first real `OutlierResult` persisted and served by this system; R4 finally carrying the field
WIRE1-Fold-4 added on 2026-07-17; and — under a later mount — the brief's Component 3 (*"outlier detection with
SHAP-style feature importance"*) demonstrated in a browser rather than only in unit tests.

**Would not**: discharge **#2** (still no drafting trigger in the API) · discharge **#3** (the corpus remains
offline-double-generated) · touch **#18** (no production `LLMClient`) · address whether `corpus/` ships to the
deployed backend (Q6(d)) · make the system "Phase 2" in `services.md`'s full sense (Q2).
