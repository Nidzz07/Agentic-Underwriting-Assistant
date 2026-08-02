# Register #2 — The Real Application-Submission Path (scoping plan)

**Stage**: POST-BUILD → scoping/planning pass
**Status**: ✅ **DESIGN COMPLETE — all 10 questions answered. Ambiguity-check RE-RUN → CLEAN (§4.1), with a
SCOPE REDUCTION (Fold-6 does not amend §4). Execution plan written as a separate artifact:
`register-2-code-gen-plan.md`. AWAITING REVIEW — no code written, no backend file touched.** Superseded status line, preserved: *"⛔ PLAN GATE — 8 questions open, none pre-filled…"*
**Date**: 2026-08-01
**Predecessors**: `scope-b-wiring-plan.md` (where **Q11-A** scoped the claim), `frontend-backend-wiring-plan.md`,
`login-signup-plan.md` (the **Fold-5** precedent for a route-adding WIRE-1 amendment), commit `3a08dd8`

---

## 0. ⛔ Read this first — two findings that change the shape of the work

### 0.1 The intake unit has NEVER been wired. Anywhere.

Repo-wide scan: **`IntakePipeline` has zero call sites outside `backend/intake/` itself.** The seed script — the
only path that has ever created a case — **bypasses intake completely** (`seed_demo_cases.py:263`):

```python
def profile(self, raw): 
    """`raw` is already a validated profile here — the script builds them directly."""
    return raw
```

It hands `CasePipeline` a hardcoded `_demo_profile()`. **So U1 `intake` — pdfplumber parsing, the sanitizer, the PII
guard, the validation gate — has never run in any reachable path.** Same shape as `outlier_model` before the last
pass, but substantially larger.

⚑ **Consequence for framing**: *"replicate what the seed script does"* is the **wrong** brief. The seed script skips
the single biggest component a real submission path needs. **This pass wires a unit for the first time; it does not
mount an existing one.**

### 0.2 A submission route REVERSES a deliberate architectural decision

`seed_demo_cases.py:24-28` records why `CasePipeline` lives outside `backend/app/`:

> *"none of R2/R3/R4/R5 calls `submit()` or `draft()` … Keeping `CasePipeline` out of `backend/app/` means the
> LLM-bearing composition **never enters the request path**, which is what makes R4 side-effect-free **BY
> CONSTRUCTION** rather than by discipline (BR-CASE-4 / TRIGGER-1)."*

A submission route puts an LLM-bearing pipeline **into a request handler**. That is not a detail — it is the
inversion of a stated invariant. **Q3 exists to decide it deliberately.**

---

## 1. Measured inventory

### 1.1 Register #2's status and the Q11-A qualifier

**PARTLY DISCHARGED** — the register's only discharge, explicitly incomplete. Q11-A verbatim
(`scope-b-wiring-plan.md:736`):

> The honest claim is **"the API layer is exercisable after running a seed script."** Explicitly **NOT** *"the demo
> path is runnable end-to-end"* — option C would require an ingestion route needing **both** a WIRE-1 amendment
> **and** a frozen-test edit, neither permitted. **State precisely; do not let it drift toward the stronger claim.**

⚑ **Q11-A is not a narrower scoping of #2 — it is the record of what #2 still lacks.** Three named gaps:
**(i)** no ingestion route · **(ii)** no clickable UI · **(iii)** *(via §12.5 / Q12-C)* memo prose is **synthetic**.
**This pass can close (i) and (ii). (iii) belongs to register #18** — see **Q5**.

### 1.2 What the seed script does, end to end

| # | Step | Mechanism |
|---|---|---|
| 1 | migrations | `apply_all_migrations()` — U15's + U24's |
| 2 | fit the outlier model | `build_outlier_model()` — committed corpus, **~2.6 s**, fails loudly if absent |
| 3 | compose seams | rulebook loader · `RulesEngine` · `MemoAgentInputBuilder` · `LangGraphOrchestrator` + `GeminiAdapter` · **offline LLM double by default** |
| 4 | **build the profile** | ⛔ `_demo_profile()` — hardcoded. **No intake.** |
| 5 | submit | `submit()` → `profile()` (pass-through) → `evaluate()` → persist at `evaluated` |
| 6 | draft | `draft()` → `score_outlier()` → `route_borderline()` → `draft_memo()` → persist `PendingRecommendation` |

**Steps 5–6 are reusable as-is. Step 4 must be newly built through intake. Steps 1–3 become composition concerns.**

### 1.3 WIRE-1 today, and what an amendment costs

Pinned surface: **R1–R9**. **No ingestion route.** Prior amendments: **Fold-4** (2026-07-17, additive `outlier`
field) · **Fold-5** (2026-07-25, R8/R9). A submission route is **Fold-6 — the third amendment**.

⛔ **Plus a frozen-test edit, exactly as Q11-A predicted.** `deploy_config/tests/test_routes.py` asserts
**exact-set equality** over the deployed `(path, method)` set (`NFR-DEP-ROUTES-1`, labelled *"LOAD-BEARING —
full-highest"*), reading `_route_inventory.py`, cross-checked by `app/tests/test_route_inventory_sync.py` and
`test_no_write_route.py`.

### 1.4 What intake actually accepts

```python
IntakePipeline.process(form_fields: dict[str, Any], documents: list[DocumentInput]) -> PipelineResult
DocumentInput(doc_type: DocType, source_path: Optional[str])
PipelineResult(outcome: ApplicantProfile | RejectedIntake, sanitized_texts: [...])
```

⛔ **`source_path` is a filesystem path, not bytes.** `SubprocessParseWorker` spawns a **subprocess** under
CPU/memory/timeout limits (5 s · 5 CPU-s · 256 MB) that reads the file **from disk**. `pdfplumber>=0.11.0` is in
`requirements.txt`. **An upload route therefore cannot hand bytes to intake** — it must land the file, invoke a
subprocess, and clean up. **Q2.**

### 1.5 ⚑ `CaseSeams.profile` is duck-typed — which makes U24 cheap

`pipeline.py:76` — `def profile(self, raw: object) -> object: ...`. **Untyped, both ends.** An intake-backed seam
satisfies it **without any change to `case_lifecycle`**. That is the strongest single argument that this pass may
need **no U24 reopening at all** (**Q7**).

⚠️ **But `RejectedIntake` has nowhere to go.** `submit()` returns `PendingApplication` — **it has no failure
channel** (unlike `draft()`, which returns `DraftOutcome`). The same asymmetry register #27 turned on. **Q8.**

### 1.6 The outlier model is a composition problem now

`build_outlier_model()` is called **only** in the seed script's `main()`. **~2.6 s per fit is fine once per script
run and unacceptable per HTTP request.** Something must hold a fitted model for the process lifetime — a concern
`backend/app/` has never had. **Q4**, and it collides with the **unresolved** question of whether `corpus/` ships to
the deployed backend (outlier plan §7 item 2).

### 1.7 The frontend has nothing pre-built

Existing units: `queue` · `memoView` · `approvalGate` · `overrideForm` · `outlierView` (built, **unmounted**) ·
`history` · `login` · `shell`. **There is no submission view.** ⚑ Unlike the outlier mount pass — which had a
complete frozen unit with 158 passing tests waiting — **this is a new UI unit designed and built from scratch**.
**Q6.**

---

## 2. Open decisions — answer inline, none pre-filled

### Q1 — WIRE1-Fold-6's scope, and how the frozen-test edit is gated

A new route (call it **R10**) is unavoidable if submission happens over HTTP.

**Sections Fold-6 touches**: **§3** route list (R10) · **§5** request body + success shape · **§2** conventions —
**only if** a `201 Created` or `multipart/form-data` convention is introduced, both of which would be new · **§4**
error mapping (validation rejection; `413` if uploads) · **§7** a new `### 7.3 WIRE1-Fold-6` subsection · the
**header** · **§1** only if a new enum reaches the wire.

- **(a) Amend additively in Fold-5's exact shape, with the frozen-test edit as its OWN gated sub-step requiring
  separate written sign-off. — RECOMMENDED.** Fold-5 is the proven precedent: R1–R7 were verified **byte-unchanged
  row-by-row at sign-off**, the amendment was declared purely additive, and superseded text was struck through
  rather than deleted. ⚑ Gating the `test_routes.py` / `_route_inventory.py` / cross-check edit **separately** is
  the important half: that assertion is labelled **LOAD-BEARING — full-highest**, it is the only mechanical guard
  on the deployed route surface, and it must be **deliberately widened, never quietly**. Two gates, two signatures.
- **(b) One combined amendment+test gate.** Fewer stops. But it lets a frozen load-bearing assertion change ride
  along inside a contract amendment, which is precisely the coupling the project has avoided three times.
- **(c) Amend WIRE-1 now, defer the route implementation to a later pass.** Contract-first, and legitimate — but a
  pinned route nobody serves is a worse artifact than no route.
- **(d) Avoid the amendment: submit via an existing route** (e.g. overloading R5) or keep ingestion out-of-band.
  ⛔ Rejected: it would misuse a pinned commit route, and out-of-band ingestion is exactly the state Q11-A says is
  *not* end-to-end.

**[Answer]**: (a) — amend WIRE-1 additively in Fold-5's exact shape, with the frozen-test edit (test_routes.py + _route_inventory.py + the cross-checks) as its own separately-gated sub-step requiring its own written sign-off. Two gates, two signatures — the load-bearing route-surface assertion must be widened deliberately, never bundled into the contract amendment.

---

### Q2 — what does the submission accept? ⚑ The largest hidden-cost driver

Intake supports **both** structured `form_fields` and parsed `documents`. What the **route** accepts is a separate,
much bigger decision — and it determines whether the frontend is a form or an upload pipeline (**Q6**).

**⛔ The honest cost of the document path**, stated in full rather than discovered later:

1. **Bytes → disk.** The subprocess worker reads a **path**. Uploads must be written to temp storage before intake
   runs. That is new: no route in this system has ever touched the filesystem.
2. **Temp-storage lifetime.** Who deletes the file, and when — on success, on failure, on crash? A leaked PDF of an
   applicant's financials is a **PII retention** issue, not just housekeeping (and `pii_guard` exists precisely
   because this project takes that seriously).
3. **Size and count limits.** None exist today. Without them an upload route is a trivial resource-exhaustion
   target. This means a `413` mapping and therefore a **§4** amendment.
4. **Subprocess concurrency.** 5 s timeout · 5 CPU-s · 256 MB **per document**. Under concurrent submissions this
   multiplies with nothing bounding it — a capacity question the deployed backend has never faced.
5. **Deployment.** Render's filesystem is ephemeral and the container's memory is finite; the subprocess model
   needs verifying there, not just locally.
6. **`multipart/form-data`** is a new request convention (**§2**), and the frontend needs real file-upload handling,
   progress, and error states.

- **(a) STRUCTURED-ONLY for this pass; documents named as a deliberate follow-on. — RECOMMENDED.** It closes
  Q11-A's gaps (i) and (ii) — a genuine end-to-end HTTP journey and a clickable UI — while deferring **six**
  distinct infrastructure problems that have nothing to do with #2's actual claim. ⚑ It still **wires intake for the
  first time**: `process(form_fields, documents=[])` runs the sanitizer, the PII guard and the validation gate — the
  parse step simply has nothing to parse. **The unit gets exercised; only the PDF path waits.** And the brief's
  pdfplumber requirement is deferred, not denied.
- **(b) DOCUMENTS (PDF upload) — the full pipeline.** The most faithful to the brief's *"pdfplumber + Pydantic"*
  framing and the only option that exercises `SubprocessParseWorker` for real. ⛔ But it brings all six costs above
  into a pass whose subject is a *drafting trigger*, and any one of them could dominate the schedule.
- **(c) BOTH, in one pass.** Complete. Largest scope, and couples a straightforward form to an upload pipeline —
  the same "two unrelated failure modes in one diff" the outlier pass rejected.
- **(d) Documents FIRST, structured later.** Rejected: it front-loads every hard problem and delivers no clickable
  path until the last of them is solved.

**[Answer]**: (a) — structured-only for this pass, with documents/PDF upload named explicitly as a deliberate follow-on. This closes Q11-A's gaps (i) and (ii), still wires intake for the first time (sanitizer, PII guard, validation gate all run), and defers the six real infrastructure costs of the upload pipeline to their own future pass.

**[Answer — accept an empty `documents` list?]**: And yes to the follow-up: the route should explicitly accept an empty documents list, so the seam's shape is already correct for when documents land later.

---

### Q3 — ⛔ Synchronous drafting in the request, or not? **The architectural question.**

`draft()` is **LLM-bearing**. Calling it inside a handler makes submission latency = rules + outlier scoring + an
LLM round-trip, and **reverses** the decision quoted in §0.2.

- **(a) TWO-PHASE — submission is synchronous through `submit()` only (intake → rules → persist at `evaluated`),
  and returns fast; drafting is triggered separately. — RECOMMENDED.** Four grounds, each structural rather than
  stylistic. **(i)** It **preserves the existing invariant exactly**: `submit()` is already documented as *"LLM-free
  throughout"* and atomic, so the LLM-bearing half never enters *this* handler. **(ii)** ⚑ **The system is already
  shaped for it** — R4's `status: pending | ready` discriminator exists precisely because a case can exist before
  its memo does, and `case_to_memo_view_state` maps `evaluated → "pending"`. A two-phase flow renders correctly
  **today, with no frontend change beyond the new view**. **(iii)** It keeps a slow, failure-prone, spend-capable
  call off the user's submit button. **(iv)** It leaves the drafting trigger's mechanism (**a second route, a
  background task, or a queue**) as a **separately decidable** question rather than baking the hardest one in now.
  ⚠️ Its cost: the user submits and sees `pending` — the demo needs a second action, so "end-to-end in one click"
  becomes "end-to-end in two".
- **(b) SYNCHRONOUS — one route does intake → rules → outlier → memo → persist, returning the drafted case.** The
  best demo: one click, a finished memo. ⛔ But it puts an LLM call in a request handler, so submission inherits the
  model's latency and failure modes; a timeout leaves a case at `evaluated` with the user told nothing; and under
  Q5's real-LLM option **every submission spends money synchronously**. It also makes the stated
  "LLM never enters the request path" invariant **false**, which would need recording as a deliberate reversal.
- **(c) BACKGROUND TASK** (FastAPI `BackgroundTasks`) — submission returns fast and drafting runs after the
  response. Feels like (b), costs like (a). ⛔ But it introduces **fire-and-forget work with no retry, no
  visibility, and no failure surface**; a crash mid-draft leaves a case at `evaluated` with nothing recording why.
  ⚑ Note the precedent: register **#19**'s `committing` state exists *because* this project treats
  crash-in-the-middle as a real, reconcilable condition rather than an unlikely one.
- **(d) A REAL QUEUE** (worker + broker). The correct production answer, and the only one that gives retry,
  back-pressure and observability. ⛔ Enormous for this stage: new infrastructure, new deployment surface, new
  failure modes — and `render.yaml` currently describes a single web service.

**[Answer]**: (a) — two-phase: submission is synchronous through submit() only (intake → rules → persist at evaluated) and returns fast; drafting is triggered separately. This preserves the "LLM never enters the request path" invariant exactly, the system is already shaped for it (R4's pending|ready discriminator), and it keeps the slow/spend-capable LLM call off the submit button.

**[Answer — what triggers drafting?]**: a second explicit route (R11, widening Fold-6 to add both R10 and R11) triggered by a UI action on the pending case — this keeps drafting deliberate and visible rather than fire-and-forget, and mirrors how the rest of the system exposes state transitions as explicit actions. Confirm in the plan that R11 is part of the same Fold-6 amendment, not a separate later one.

---

### Q4 — where does the fitted outlier model live?

~2.6 s per fit. **Per request is not an option.** Today it is fitted once in the seed script's `main()`.

- **(a) Fit ONCE at application startup and hold it for the process lifetime, behind the same lazy-`lru_cache`
  pattern the three engines already use. — RECOMMENDED.** It matches an **established composition-root idiom**
  (`app_engine()`, `writer_engine()`, `get_settings()` are all lazy + cached), it costs one ~2.6 s hit on the first
  submission rather than on every one, and it adds **no new artifact type**. ⚠️ Two consequences to accept openly:
  the first submission after a cold start is slow, and **the deployed backend must then have `corpus/` present** —
  which is the **unresolved** question already carried forward from the outlier pass (`render.yaml` neither places
  nor verifies it). Choosing (a) **converts that open question into a hard deployment dependency**, and it should
  be answered in this pass rather than inherited again.
- **(b) Eager fit at startup** (not lazy) — no slow first request, but every boot pays 2.6 s and a missing corpus
  fails at **startup**, taking the whole service down rather than one route. Arguably better (fail fast, loudly);
  arguably worse (a corpus problem kills login too).
- **(c) A precomputed, persisted model artifact** loaded at startup. No fit cost at all. ⛔ Adds a binary artifact,
  a build step, a versioning question, and a **staleness risk against `corpus_version`** — the provenance triple
  exists to make a score replayable, and a stale pickle silently breaks that.
- **(d) No outlier on the submission path** — draft with `outlier=None`, as every case did before the last pass.
  Smallest change. ⛔ But it means a real submission produces a case **worse** than a seeded one, immediately after
  a pass whose whole point was making outlier data real.

**[Answer]**: (a) — fit once at application startup, held for the process lifetime via the same lazy lru_cache pattern the three engines already use.

**[Answer — does `corpus/` ship to the deployed backend?]**: YES, corpus/ ships to the deployed backend — resolve the carried-forward question here, in this pass, as a hard dependency. The deployment pass must place and verify corpus/profiles.json on Render, and outlier scoring depending on it is now an explicit, documented deployment requirement rather than a silent assumption.

---

### Q5 — offline double or real LLM — and **the sequencing decision with #18**

Today `build_gemini_client` is reachable only from two **out-of-band scripts**, behind two gates (`--real-llm` +
`ALLOW_REAL_LLM_CALLS=true`) and a per-process cap.

⛔ **A route changes the risk class.** Script spend is opt-in, out-of-band and human-initiated. Route spend is
reachable **by any authenticated user over HTTP** — so this becomes a **spend-exposure and rate-limiting** question,
not a fidelity one.

**And the sequencing matters as much as the choice:**

- **(a) OFFLINE double on this path; #2 closes Q11-A's (i) and (ii); (iii) stays open and is named. — RECOMMENDED.**
  It is free, safe, deterministic, and needs no new gate. ⚑ It is also **honest by construction**: every memo is
  stamped `OFFLINE-DOUBLE-NOT-A-REAL-LLM`, visible in the API response, the database and any audit record — so a
  synthetic memo **cannot be mistaken** for a real one. The end-to-end path becomes demonstrable **now**, and #18
  upgrades the prose later **without touching this pass's structure** (the seam is already injected). **#2's
  remaining gap is then exactly one clearly-named item.**
- **(b) REAL LLM on this path, gated as the scripts are.** #2 lands complete — Q11-A's (i), (ii) **and** (iii) all
  closed at once. ⛔ But it puts spend behind an HTTP route with no rate limit, no per-user cap and no abuse story,
  and it makes this pass depend on #18's unresolved work.
- **(c) SEQUENCE #18 FIRST, then #2.** #2 arrives complete and never demos synthetic prose. ⛔ It blocks the entire
  end-to-end path behind a separate, independently-sized body of work — and #18 has been open since 2026-07-20
  without being scheduled.
- **(d) Offline by default with a real-LLM opt-in on the route** (a request flag or an env gate). Flexible. ⛔ A
  per-request spend switch is a **larger** abuse surface than a process-level flag, and it puts the spend decision
  in the caller's hands rather than the operator's.

**[Answer]**: (a) — offline double on this path. #2 closes Q11-A's (i) and (ii); (iii) (synthetic prose) stays explicitly named as register #18's territory. Free, safe, deterministic, honest by construction (every memo stamped OFFLINE-DOUBLE-NOT-A-REAL-LLM), and the seam is already injected so #18 upgrades the prose later without touching this pass's structure. We do #2 first, then #18 — sequencing confirmed.

---

### Q6 — the frontend submission view

⚑ **Nothing is pre-built.** Unlike the outlier mount pass (a complete frozen unit with 158 passing tests waiting),
this is a **new UI unit**: components, copy, seam, testids, error/empty/loading states, and its own tests. Its shape
follows **Q2** almost entirely.

- **(a) A new `submission/` unit mirroring the existing units' structure exactly** — `SubmissionView.jsx`,
  `components/`, `copy.js`, `fetchSeam.js`, `testids.js`, `__tests__/` — mounted behind the login gate, registering
  a **seventh** `seams.js` key. **— RECOMMENDED.** It follows the six existing units' established shape, so it is
  reviewable against known precedent rather than novel. ⚑ It also inherits the **already-answered Q4(a)** from the
  outlier plan: adding a seam key means superseding `app.test.jsx`'s exact-key assertion — ⚠️ **and note the
  outlier mount pass will do the same to the same assertion**, so whichever lands second must expect it.
- **(b) Extend an existing view** (e.g. the queue) with a submission affordance. Less new surface. ⛔ But it widens
  a frozen unit's responsibility and breaks the one-unit-one-concern shape every other view follows.
- **(c) A minimal unstyled form**, deferring the full unit. Fastest to a demo. ⛔ Inconsistent with six polished
  peers, and "temporary" UI reliably becomes permanent.
- **(d) Defer the frontend entirely** — ship R10 and demo with `curl`. Legitimate as a staging step, and it keeps
  this pass backend-only. ⛔ But Q11-A names **"not a clickable UI"** as an explicit gap, so #2 cannot close
  without it.

**[Answer]**: (a) — a new submission/ frontend unit mirroring the six existing units' structure exactly, mounted behind the login gate, registering a seventh seams.js key. Note explicitly in the plan the double-supersession of app.test.jsx's exact-key assertion (this pass + the deferred outlier mount), so whichever lands second expects a seven-key set.

---

### Q7 — which frozen units need reopening?

| Unit | Assessment |
|---|---|
| **`case_lifecycle` (U24)** | ⚑ **Probably NONE.** `CaseSeams.profile(raw: object) -> object` is **duck-typed at both ends**, so an intake-backed seam satisfies it with no U24 change. `submit()`/`draft()` already do exactly what a submission path needs. **Contingent on Q8** — a rejected intake may need a channel `submit()` does not have. |
| **`intake` (U1)** | ⚑ **Depends entirely on Q2.** Under **structured-only**, `process(form_fields, documents=[])` is called **as-is — no reopening**. Under **documents**, the `source_path`-only seam may need a bytes-or-path variant → **a reopening**. |
| **`deploy_config` (U23)** | ⛔ **YES** — `test_routes.py` + `_route_inventory.py`, the load-bearing exact-set assertion. **Gated separately per Q1.** |
| Others | None expected. |

- **(a) Authorize NOTHING up front; scope each reopening separately if and when the design forces it, following
  the #27 discipline (standalone authorization naming exact files, applied as step 0). — RECOMMENDED.** ⚑ The
  investigation shows the two most likely reopenings are **avoidable** (U24 by duck-typing, U1 by choosing Q2(a)),
  so pre-authorizing would grant scope that may never be needed — and a reopening's file list must never expand by
  inference. **Only U23's is certain**, and Q1(a) already gives it its own gate.
- **(b) Pre-authorize U24 + U1 now** so execution never stalls. Fewer interruptions; grants scope on speculation.
- **(c) Pre-authorize U23 only** (certain), leave the rest to (a). ⚑ Effectively identical to (a) given Q1(a)
  already gates U23 — worth stating so the two are not double-counted.
- **(d) Forbid all reopening; design around every frozen boundary.** ⛔ Impossible — R10 cannot exist without U23's
  route assertion changing.

**[Answer]**: (a) — authorize nothing up front; scope each reopening separately if and when the design forces it, following the #27 discipline (standalone authorization naming exact files, applied as step 0). Only U23's route-assertion edit is certain, and Q1(a) already gates it. U24 is avoided by duck-typing and U1 by Q2(a)'s structured-only choice, so neither should be pre-authorized on speculation.

---

### Q8 — where does a REJECTED intake surface? *(surfaced by §1.5)*

`IntakePipeline` returns `ApplicantProfile | RejectedIntake`. **`submit()` returns `PendingApplication` and has no
failure channel** — the same asymmetry register #27 turned on (`draft()` has `DraftOutcome`; `submit()` has
nothing). An applicant failing the validation gate is an **expected, ordinary outcome**, not an exception.

- **(a) Handle rejection in the ROUTE, before `submit()` is ever called: run intake in the handler, and on
  `RejectedIntake` return a 4xx carrying `reason_category` / `field_errors` / `missing_items` — never entering the
  pipeline. — RECOMMENDED.** `RejectedIntake` already carries exactly the fields a form needs to show per-field
  errors, so the UI gets a genuinely useful response. ⚑ **Reopens no frozen unit**: the composition root decides,
  U24 never sees a rejected case, and no half-created row exists. It also keeps `submit()`'s contract intact.
- **(b) Give `submit()` an outcome type** mirroring `DraftOutcome`. Symmetric and arguably where it belongs. ⛔ A
  U24 reopening for a case the pipeline should arguably never be handed.
- **(c) Persist rejected intakes** as a `failed`-like row for audit. Attractive for traceability. ⛔ Needs a schema
  and state the machine does not have, i.e. a migration — and it would store rejected applicants' data, which is a
  **retention decision**, not a technical one.
- **(d) Raise an exception and let the global error handler map it.** Simplest. ⛔ Rejection is a **domain outcome**,
  not an error; this loses `field_errors` and the project has consistently refused this shape (Q4-A).

**[Answer]**: (a) — handle rejection in the route, before submit() is ever called: run intake in the handler, and on RejectedIntake return a 4xx carrying reason_category/field_errors/missing_items, never entering the pipeline. Reopens no frozen unit, keeps submit()'s contract intact, no half-created row, and gives the form a genuinely useful per-field error response.

---

## 3. Mandatory ambiguity-check — combined Q1–Q8 answer set

**Answer set**: Q1(a) · Q2(a)+empty-documents · Q3(a)+R11 · Q4(a)+corpus-ships · Q5(a)+#2-then-#18 · Q6(a) ·
Q7(a) · Q8(a).

**Result: ⛔ NOT CLEAN. One BLOCKING finding, and TWO new questions are surfaced (Q9, Q10).** Two of the three
directed checks came back with real objections; the third came back clean.

### ⛔ Fold A (DIRECTED, BLOCKING) — an existing test forbids the pipeline in `backend/app/` **by name**

The §0.2 invariant is **not merely documented — it is mechanically enforced**, and both R10 and R11 violate it.
`backend/app/tests/test_no_write_route.py::test_the_read_routes_invoke_no_pipeline_step` scans **every production
file under `backend/app/`** and asserts:

```python
assert "CasePipeline" not in code, path
assert ".draft(" not in code, path
assert ".submit(" not in code, path
```

Its docstring: *"⚑ BR-CASE-4 / TRIGGER-1 — no GET may trigger drafting. Structural, not behavioural: `CasePipeline`
is not imported or constructed anywhere in this package, so a read CANNOT reach `draft()` even by mistake."*

⚑ **The guard is BROADER than its name.** It says *"read routes"*, but it scans **all** production source, not GET
handlers — so it forbids the pipeline **anywhere** in the composition root. **R10 (`submit()`) and R11 (`draft()`)
each break it directly, and both need `CasePipeline` imported.**

⚑ **There are TWO overlapping guards on `CasePipeline`, and only one has an exemption mechanism.** The
`_DOMAIN_SEAMS` scan (`:73-79`) also lists `CasePipeline`, but it **exempts** modules in
`_DOMAIN_WRITE_MODULES = frozenset({"not_wired.py"})`. The blocking assertion has **no such escape hatch**.

**RESOLUTION DIRECTION**: narrow the claim the way this same file has already been narrowed **twice** (Scope A →
Scope B → register #19), each time preserving the old text and replacing it with something **strictly more
specific and still falsifiable** — e.g. *"no **GET** route imports or invokes the pipeline; it is reachable only
from the two explicit POST routes R10/R11"*, giving the second guard the same exemption shape the first already
has. ⛔ **But whether that edit is a THIRD separately-gated sign-off is a decision, not a fold — Q9.**

⚠️ **This also qualifies Q7(a).** `test_no_write_route.py` lives under `backend/app/tests/`, so it is **not frozen**
and needs **no reopening**. But it is load-bearing in exactly the way `test_routes.py` is, and Q1(a)'s
"two gates, two signatures" reasoning applies to it with equal force.

### ⛔ Fold B (DIRECTED) — R11's auth is genuinely undecided, and the default is wrong

R11 changes state (`evaluated -> drafted`), spends compute, and — under a future Q5(b) — could spend money. The
existing routes split two ways: **R2/R3/R4/R6/R7** are *"authenticated (any role)"*; **R5** is
**`underwriter` only**, enforced by a dedicated `require_commit` dependency added precisely because a write needed
more than authentication.

⚑ **R11 is a write with a cost.** Defaulting it to "any authenticated role" would let an **auditor** — a read-only
role by design (SEC-4) — trigger drafting. That is a role-model decision the plan has not made, and it cannot be
inferred from R10's answer. **Q10.**

### ✅ Fold C (DIRECTED) — the startup fit does NOT slow the suite, and nothing asserts otherwise

Answering the directed question directly:

* **`lru_cache(maxsize=1)` is the established idiom** — `app_engine()`, `reader_engine()` and `writer_engine()`
  all use it (`dependencies.py:98/104/111`). Q4(a) adds a fourth of exactly the same shape, so it introduces **no
  new pattern**.
* ⚑ **It is LAZY, so `create_app()` still constructs nothing.** The ~2.6 s fit happens on **first use**, not at
  import or app construction — so the **four** `create_app()` call sites in `app/tests/conftest.py` pay nothing.
* **Cost to the suite: ~2.6 s ONCE per process**, not per test, because the cache is module-level. Contrast the
  #27 investigation's finding, where the concern was ~2.6 s × N *constructions*; the `lru_cache` shape is what
  makes that not recur here.
* **No test asserts `create_app()` is cheap or constructs nothing** — searched; none exists. So there is nothing
  to break.
* ⚠️ **One caveat worth stating**: it would be ~2.6 s on the first test that exercises the submission route, which
  is fine — but if a future change made the fit **eager** (Q4(b)), it would become 2.6 s × every `create_app()`.
  **The laziness is load-bearing, not incidental.**

### ✅ Fold D — Q8 + Q4 add NO filesystem work to `backend/app/`, *because of* Q2(a)

The directed question was whether "intake in the handler" plus "fit at startup" put heavy or filesystem-touching
work into the composition root.

* **Intake**: under **Q2(a)** the route calls `process(form_fields, documents=[])`. With an empty document list the
  loop that would invoke `SubprocessParseWorker` **never executes** — so there is **no subprocess, no temp file, no
  filesystem access**. The sanitizer, PII guard and validation gate are pure in-memory work. ⚑ **Q2(a) is what
  makes Q8(a) safe**; under Q2(b) this fold would have come back very differently.
* **The outlier fit**: reads `corpus/profiles.json` **once per process**, at first use. That is a filesystem read
  in `backend/app/` — new, but bounded, read-only, and no different in kind from `RulebookLoader` reading the
  rulebook.
* **Frozen tests**: the `_DOMAIN_SEAMS` scan does **not** list `IntakePipeline` or `OutlierModel`, and the
  `create_engine` / `PostgresCaseStore(` / `get_settings(` construction prohibition (`:283`) is scoped to the
  **routes module** and satisfied by injecting through `dependencies.py` as every other collaborator already is.
* ⚑ **R4 stays side-effect-free.** Under **Q3(a)** drafting is a separate POST; no GET gains a write path. The
  invariant's *substance* survives — only the over-broad *wording* of the guard in Fold A needs narrowing.

### ✅ Fold E — R10 + R11 as one Fold-6 compose cleanly with the two-phase flow

Confirming the point Q3's answer asked to be stated: **R11 belongs to the SAME Fold-6 amendment, not a later one.**
Grounds: the two-phase flow is **incoherent with only one of them** — R10 alone creates cases nothing can draft,
and R11 alone has nothing to draft. Fold-5 is the precedent for a **single amendment adding two routes** (R8 + R9),
which were likewise only meaningful as a pair. §3's route list, §5's shapes and §7.3's fold note all take both rows
at once, and `_route_inventory.py` is updated **once** rather than twice.

---

## 4. ⛔ NEW QUESTIONS SURFACED BY THE CHECK — answer before the execution plan

### Q9 — how is the TRIGGER-1 guard narrowed, and is it a third gated sign-off? (Fold A)

- **(a) Narrow it in the file's own established shape — preserve the current claim verbatim, replace it with
  "no GET route imports or invokes the pipeline; it is reachable ONLY from R10/R11" using the `_DOMAIN_WRITE_MODULES`
  exemption pattern that already exists in the same file — AND gate that edit with its own written sign-off, as a
  THIRD gate alongside Fold-6 and `test_routes.py`. — RECOMMENDED.** The narrowing mechanism is not invented: this
  file has been narrowed twice already, each time strictly-more-specific and still falsifiable, with the old text
  kept. The separate gate follows Q1(a)'s own reasoning — a load-bearing structural guard must be widened
  deliberately, and this one is the **only** mechanical enforcement of the §0.2 invariant.
- **(b) Narrow it, but fold the edit into the Fold-6 gate.** One fewer stop. ⛔ Exactly the bundling Q1(a) rejected,
  applied to a guard that is arguably more load-bearing than the route set.
- **(c) Exempt R10/R11's module via `_DOMAIN_WRITE_MODULES` only**, leaving the assertion's text unchanged. Minimal
  diff. ⛔ But the assertion's *docstring* would then be false — it claims the pipeline is "not imported anywhere in
  this package" — and a guard whose prose lies is how register #17's premise survived.
- **(d) Delete the assertion.** ⛔ Rejected on the file's own recorded reasoning: deletion was considered and
  refused **twice**, because it would leave the file asserting nothing.

**[Answer]**: (a) — narrow the TRIGGER-1 guard in the file's own established shape, preserving the current claim verbatim and replacing it with a version stating the pipeline is reachable only from R10/R11, using the existing _DOMAIN_WRITE_MODULES exemption pattern. Gate this as its own third sign-off, alongside the Fold-6 contract amendment and the test_routes.py route-set edit. This guard is the only mechanical enforcement of the §0.2 invariant and deserves the same deliberate-widening treatment as the route-set assertion.

---

### Q10 — R11's authorization: who may trigger drafting? (Fold B)

- **(a) `underwriter` only, via a dedicated dependency mirroring `require_commit`. — RECOMMENDED.** Drafting is a
  **state-changing, resource-consuming** action, and R5 already establishes that writes get their own role gate
  rather than bare authentication. ⚑ It also keeps the **auditor** role read-only, which SEC-4 treats as a security
  property rather than a convention — an auditor able to trigger LLM drafting would quietly break that.
- **(b) Any authenticated role**, matching R2/R3/R4. Simplest, consistent with the read routes. ⛔ But R11 is not a
  read, and this hands a spend-capable trigger to a role defined as read-only.
- **(c) `underwriter` OR `admin`.** Operationally convenient. Needs the role model checked — admin's powers are
  defined elsewhere and should not be widened casually here.
- **(d) Defer — ship R10 now, R11's auth later.** ⛔ Incoherent with Q3(a): without R11 nothing can draft, so the
  two-phase flow has no second phase.

⚑ **Note this also affects R10.** Who may *submit*? The same question, and the answers may legitimately differ — a
submission might reasonably be broader than a drafting trigger. **Answer both.**

**[Answer — R11 (draft trigger)]**: (a) — underwriter only, via a dedicated dependency mirroring require_commit. Drafting is state-changing and resource-consuming (an LLM call), and R5 already establishes that writes get their own role gate. This also keeps the auditor role's read-only property intact per SEC-4.

**[Answer — R10 (submission)]**: (a) — underwriter only as well, for consistency and because submission is also the entry point to a resource-consuming pipeline (intake + rules evaluation). Keep both routes under the same auth model for this pass; if there's a legitimate future reason to broaden R10 to any authenticated role (e.g. a different persona submitting applications), that's a separate, deliberate decision — not assumed here.

---

## 4.1 ✅ Ambiguity-check RE-RUN against the complete Q1–Q10 set — **CLEAN**

**Answer set**: Q1(a) · Q2(a) · Q3(a)+R11 · Q4(a)+corpus-ships · Q5(a) · Q6(a) · Q7(a) · Q8(a) · **Q9(a)** ·
**Q10(a)/(a)**.

**Result: CLEAN. Both blocking folds are resolved, no new question is surfaced, and one directed re-check produced
a SCOPE REDUCTION.** The execution plan can be written.

### ✅ Re-check 1 — the three gates do NOT overlap, but the reason is subtle and must be stated

The concern is real on its face: **`test_no_write_route.py` appears in both gate 2 and gate 3.** It is not a
conflict, because the two gates touch it in **different ways**:

| Gate | What it EDITS | Effect on `test_no_write_route.py` |
|---|---|---|
| **2 — route set** | `backend/app/tests/_route_inventory.py` **and** `backend/deploy_config/tests/_route_inventory.py` (two copies, held identical by `test_route_inventory_sync.py`) | ⚑ **NONE — it is not edited.** It *reads* `ROUTE_INVENTORY` (`:57`, `_DECLARED_PATHS` at `:63`), so R10/R11 propagate **automatically** |
| **3 — TRIGGER-1** | `test_no_write_route.py`, **one assertion only** (`test_the_read_routes_invoke_no_pipeline_step`) | the narrowing itself |

⚑ **So gate 2 edits inventories; gate 3 edits an assertion. The file is read-affected by gate 2 and edited only by
gate 3.** That is a clean split — but it would be easy to mis-stage, so the execution plan states it explicitly.

⚑ **Two details gate 2 must not miss**, both discovered here rather than at execution:

1. **There are TWO `_route_inventory.py` files** — `app/tests/` (the **authoritative** copy) and
   `deploy_config/tests/` (the **mirror**). Editing one and not the other fails `test_route_inventory_sync.py`
   loudly, by design. **Gate 2 edits both.**
2. **R10/R11 are POSTs, so each needs a `NON_GET_ALLOWLIST` entry with its stated reason** — the inventory's own
   docstring requires it: *"Each non-GET entry carries the reason it is permitted to be non-GET — a GET-only
   surface is the default and the exceptions are enumerated, never implied."*

**No duplication, no conflict, and the staging is unambiguous once stated this way.**

### ✅ Re-check 2 — auth and rejection are cleanly ordered and cleanly distinguishable

**Ordering is by construction, not by discipline.** FastAPI resolves `Depends(...)` **before** the handler body
runs, so `require_underwriter` fires before any intake code executes. A caller with the wrong role therefore
**never reaches intake** — no wasted work, and no possibility of a rejection message leaking to an unauthorized
caller.

**The three failure modes are already three distinct codes in WIRE-1 §4 — none invented here:**

| Situation | Status | `code` | Source |
|---|---|---|---|
| no / invalid session | **401** | `unauthenticated` | §4, existing |
| authenticated, wrong role | **403** | `forbidden` | §4, existing — *"e.g. `auditor` calling R5 commit"* |
| intake rejected the application | **400** | `invalid_request` | §4, existing |

⚑ **THE FINDING — WIRE-1 §4 ALREADY ANTICIPATED Q8.** Its 400 row reads verbatim: *"malformed request / input
validation **(intake Pydantic reject**, bad body)"*, and the error body's `detail` field is documented as
*"optional (e.g. **per-field validation errors**)"* — which is **exactly** `RejectedIntake`'s
`field_errors` / `missing_items` / `reason_category`. **The contract has had a home for a rejected intake since
2026-07-08**, drafted before any ingestion route existed.

### ⚑ SCOPE REDUCTION — Fold-6 does NOT need to amend §4

§1.3 and Q1 both listed **§4** as a section Fold-6 would touch (error mapping; a `413` for uploads). Under the
settled answer set **neither applies**:

* **Q2(a)** means no upload — **no `413`**, and no `multipart/form-data`;
* rejection maps to **400**, already in the table;
* auth failures map to **401/403**, already in the table.

**Fold-6's real surface is therefore: §3 (two route rows) · §5 (request/response shapes) · §7.3 (the fold note) ·
the header — and §2 ONLY if a `201 Created` convention is chosen over reusing the existing bare-body 200.**
⚑ **One fewer amended section than scoped**, recorded because a smaller contract amendment is easier to verify
byte-for-byte at sign-off, which is the whole point of Fold-5's precedent.

---

## 5. Staged execution outline — CONTINGENT on Q9/Q10

⚠️ **Outlined, not committed to.** Q9 changes stage 1's gate count and Q10 changes stage 2's shape. Deltas are
**rough** — a real per-step prediction belongs in the execution plan, after these answers.

| Stage | Content | Gates | Predicted Δ | Independently committable? |
|---|---|---|---|---|
| **1** | **WIRE1-Fold-6** (R10 + R11; §2/§3/§4/§5/§7 + header) · `test_routes.py` + `_route_inventory.py` + cross-checks · **the Q9 narrowing** | ⛔ **THREE** sign-offs (contract · route-set · TRIGGER-1) | ~0 new tests; existing assertions **change** | ⚠️ **No** — routes declared but unserved. Land with stage 2. |
| **2** | Backend: R10 + R11 handlers · intake wiring · `RejectedIntake` → 4xx (Q8) · DI in `dependencies.py` | standard | **+15…25** | ✅ **Yes** — the API becomes exercisable by `curl`, honestly claimable without a UI |
| **3** | Outlier-model composition — the fourth `lru_cache`, corpus as a declared runtime dependency | standard | **+4…8** | ✅ **Yes** — small, self-contained |
| **4** | Frontend `submission/` unit + the 7th seam key + `app.test.jsx` supersession | standard | **+25…40** frontend | ✅ **Yes** — the clickable path, closing Q11-A (ii) |
| **5** | **Manual verification (USER-RUN)** — §6 | — | — | n/a |
| **6** | Register/doc close-out: #2's remaining gap restated, `corpus/`-on-Render recorded as a hard dependency | — | — | ✅ Yes |

⚑ **Stages 2, 3 and 4 are each independently committable and independently verifiable** — the shape the outlier
pass proved works. **Stage 1 is not**, because a pinned-but-unserved route is a worse artifact than no route; it
should land in the same commit as stage 2.

⚑ **Stage 3 could precede stage 2** — the outlier composition has no dependency on the routes existing. Sequencing
it first would de-risk the corpus/deployment question before any route work begins.

---

## 6. Manual verification plan (drafted; depth to be confirmed once Q2/Q3 are answered)

Matching the project's established standard — evidence from a real database, user-run.

1. **Reset** the pending tables (⛔ never drop — the `CREATE ROLE` and audit-evidence hazards).
2. **Submit through the UI** as an authenticated underwriter; the case appears in the R2 queue.
3. **`psql`**: a `pending_application` row exists with `state=evaluated`, real `profile_canonical` bytes, and —
   critically — **a profile that came through intake**, not a hardcoded fixture.
4. **R4** renders the case (`status: pending` under Q3(a); `ready` under Q3(b)).
5. **Drafting** (per Q3's answer) produces a memo and, per Q4, a real `OutlierResult`.
6. **Commit** through the existing approval gate → an `AuditRecord` whose lineage traces to a **user-submitted**
   application. ⚑ **This is the first time the audit trail would record a case the system did not invent.**
7. **Rejection path** (Q8): submit a deliberately invalid application → per-field errors, **no row created**.

---

## 7. Holds for this pass

| Hold | Status at the plan gate |
|---|---|
| No backend file touched | ✅ Read-only throughout. |
| WIRE-1 untouched | ✅ Read-only. Fold-6 is **proposed, not drafted**. |
| No frozen unit edited | ✅ No reopening requested yet (**Q7**). |
| No code written | ✅ Files written: **1** — this plan. |
| No commit | ✅ User's call. |
| Register unchanged | ✅ **29 tracked. #2 still partly discharged.** |

---

## 8. Carried forward — do not lose these

1. ⛔ **Q11-A's gap (iii) — synthetic memo prose — is register #18's**, and this pass must not be described as
   closing it unless **Q5(b)/(c)** is chosen. State the residual precisely or not at all.
2. ⚑ **`corpus/` shipping to the deployed backend is STILL unresolved** and **Q4(a) would force it**. It has been
   carried since the outlier pass; this is the pass that should answer it.
3. ⚑ **The `seams.js` exact-key assertion will be superseded TWICE** — once by the deferred outlier mount pass
   (**Q4(a)** of `outlier-wiring-plan.md`, already answered) and once by **Q6(a)** here. Whichever lands second
   inherits a **seven**-key set, not six.
4. **`seed_demo_cases.py` may become largely redundant** once a real submission path exists. ⚠️ Deleting it would
   remove the only path that exercises the `--real-llm` seam — **decide deliberately, do not let it rot.**

---

## 9. What closing #2 would and would not deliver

**Would**: the first application the system did not invent itself; the first exercise of U1 `intake` in any
reachable path; a clickable end-to-end journey from submission to committed decision; and Q11-A's gaps **(i)** and
**(ii)** closed.

**Would not**: discharge **#18** (memo prose stays synthetic under Q5(a)) · discharge **#3** (the corpus remains
offline-double-generated) · close **#29** (`TERMINAL_STATES` still unenforced) · address **#26** · mount the outlier
view (still deferred by the outlier plan's Q1(a)) · deliver PDF parsing under **Q2(a)**.
