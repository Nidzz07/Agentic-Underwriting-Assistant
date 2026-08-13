# Document Upload & Real Parsing — scoping plan

**Stage**: POST-BUILD → scoping/planning pass
**Status**: ✅ **DESIGN COMPLETE — Q1–Q14 all answered. Ambiguity-check RE-RUN against the complete set -> CLEAN,
with FOUR recorded constraints (§4.2). Execution plan written as a separate artifact:
`document-upload-code-gen-plan.md`.** Superseded status line, preserved: *"⛔ PLAN GATE — 12 questions open, none
pre-filled…"* · then *"NOT CLEAN: one BLOCKING finding (Fold A) and TWO new questions…"*. No code written, no
backend file touched, WIRE-1 untouched.
**Date**: 2026-08-02
**Predecessors**: `register-2-submission-path-plan.md` (**Q2(a)** deferred this pass and named six of its costs),
`register-2-code-gen-plan.md`, commits `d102c52` + `d43b661`
**Baselines**: backend **1691 / 0 / 44 / 5 / 99.64%** · frontend **778 / 152**

---

## 0. ⛔ Read this first — the goal is narrower than it sounds, and one finding proves it

### 0.1 Parsed document CONTENT reaches no profile field. None.

`pipeline.py:107-109` builds the gate's input as `form_fields` + the `DocumentEntry` **manifest**. The extracted
text goes into `free_texts` → sanitizer → `PipelineResult.sanitized_texts`, which **R10 discards**. And
`parse_worker.py:36` returns `"structured_fields": {}` — a **literal empty dict, always**.

⚑ **So uploading documents buys DOCUMENT-COMPLETENESS, not DOCUMENT-DERIVED DATA.** `DOCS-COMPLETE-1` reads
`documents_missing_count = max(expected - satisfied, 0)`, and `satisfied_count` counts **only `PARSED` entries**.
Three uploaded, parsed documents drive it to `0` and the rule passes. **That is real, and it is the whole of what
parsing changes today.**

### 0.2 ⛔ `incomplete=true` will SURVIVE a perfect three-document upload

`validation_gate.py:169-177` sets `incomplete` from **seven** clauses. Documents are one:

```python
incomplete = (bmi is None or debt is None or employment is None or smoking is None
              or not occupation or not health_flags
              or any(e.status is not DocStatus.PARSED for e in manifest.entries))
```

The current form collects **none** of the first six — register #2 deliberately scoped it to the 7 required fields.
**Adding documents fixes exactly one clause of seven.**

⚠️ **And one clause cannot be satisfied honestly at all**: `not health_flags` means **an applicant who reports no
health flags is marked incomplete**. A genuinely healthy applicant **cannot** reach `incomplete=false` under the
current frozen logic. **Per the scoping instruction this is a DISCLOSED LIMITATION, not something this pass
reopens `intake` to fix.** It is named in **Q11**.

### 0.3 What is therefore IN and OUT, stated before any question is asked

| | |
|---|---|
| **IN** | Attach real PDFs through the UI · parse them for real (`SubprocessParseWorker`, pdfplumber, the existing sandbox) · **`DOCS-COMPLETE-1` genuinely passes** when three parse · the optional form fields (**Q10**) |
| ⛔ **OUT** | **`structured_fields` extraction** — pulling income/employment out of a parsed PDF to fill or override form fields. **A separate, much larger pass** (**Q9**). |

---

## 1. Measured inventory

### 1.1 What already exists, and is more than expected

* **`SubprocessParseWorker` is complete and real.** Fresh ephemeral child per document, wall-clock kill (5 s),
  POSIX `RLIMIT_CPU` (5 s) + `RLIMIT_AS` (256 MB), data-only `IpcCodec` (no pickle, float refused), and **every**
  termination mode — timeout / CPU / OOM / crash / undecodable — converging on a deterministic `unparseable`.
* **`pdfplumber>=0.11.0`** is in `requirements.txt` and used by the worker.
* ⚑ **`python-multipart>=0.0.12` is ALSO in `requirements.txt` — and used NOWHERE.** A declared, unused
  dependency. The **library** for multipart is present; the **convention** is not.
* **`DOCS-COMPLETE-1` already exists** in both rulebook versions, already reads `documents_missing_count`, and is
  a `refer_trigger` (thin-file → REFER, never DECLINE). **No rules-engine change is needed.**
* **`IntakeGate` already refuses to be lied to**: `_build_manifest` downgrades a client-claimed
  `DocStatus.PRESENT` to `UNPARSEABLE` — *"never silently admit"*. A client cannot assert a document is fine.

### 1.2 ⛔ Five gaps, none of which existed as problems before this pass

1. **Nothing bounds subprocess concurrency.** `parser.py:84` spawns unconditionally. No semaphore, pool or queue.
2. **Nothing limits upload size or count.** No `413`, no byte cap, no per-submission document cap.
3. **The backend has never written a file.** This would be the first filesystem **write** in `backend/app/`.
   `test_no_write_route.py` polices transactions and domain seams; **nothing polices file I/O.**
4. ⚑ **The shared frontend transport cannot send a file.** `httpTransport.js` does `JSON.stringify(body)` and
   always sets `Content-Type: application/json`. A `FormData` body becomes `{}`. **That module is shared by all
   six seams** — not frozen, but a blast radius Q2(a)'s cost list never named.
5. ⚑ **The sanitization audit channel is unwired.** `SanitizationReportChannel`'s default sink is
   `lambda source_ref, report: None`. Harmless today (no documents ⇒ nothing to sanitize). **With user-uploaded
   PDFs it becomes the forensic record of prompt-injection attempts — and it goes nowhere.** PROJECT-BRIEF §10
   failure mode **#4** is *"prompt injection — malicious text in uploaded document"*. **This pass is the one that
   makes that failure mode reachable.** → **Q8.**

### 1.3 The six Q2(a) costs, re-verified

Five accurate as written; **#6 is partly paid** (the multipart library is already a dependency). **Two costs were
missing from the original list** — §1.2 items **4** and **5** above.

### 1.4 WIRE-1 today

Pinned surface **R1–R11**. Amendments: **Fold-4** (outlier field) · **Fold-5** (R8/R9) · **Fold-6** (R10/R11,
2026-08-02). This would be **WIRE1-Fold-7 — the fourth amendment.** ⛔ Unlike Fold-6, it **cannot** avoid §2: §2
binds *"`Content-Type: application/json` request + response"*, and multipart contradicts it.

---

## 2. Open decisions — Q1–Q14 ALL ANSWERED (verbatim, 2026-08-02)

### Q1 — WIRE1-Fold-7's route shape ⚑ THE STRUCTURAL DECISION

- **(a) AMEND R10 to accept `multipart/form-data`.** Smallest surface; one route, one journey; the frontend already
  has a submit button to hang it on. ⛔ It changes a **pinned route's request media type one fold after pinning
  it**, and forces the shared-transport change onto the path every submission takes.
- **(b) A SECOND route — `POST /applications/{application_id}/documents`.** Keeps R10 JSON and untouched; makes
  upload a distinct, retryable step. ⛔ But documents must be present **at intake time** — the gate builds the
  manifest and assigns `application_id` on pass — so attaching later means **re-running intake**, which mints a
  **new** id. ⚑ Feasible because `IntakeGate(id_generator=…)` is injectable (`validation_gate.py:76`), so the
  existing id can be forced. Cost: a second intake run and a re-evaluation of an `evaluated` case.
- **(c) An UPLOAD route returning opaque handles**, referenced by R10's JSON body. Keeps R10 JSON, and gives
  temp-file lifetime an explicit owner with a named lifecycle. ⛔ Orphaned handles become the retention problem in
  a new costume, and it is the largest of the three.

**Recommendation: (a)**, on three grounds. **(i)** R10's request shape was designed for this — `documents` is
already in the body, explicitly so *"the seam's shape is already correct for when documents land later"*.
**(ii)** One journey, one route matches how a user thinks about submitting an application with attachments.
**(iii)** (b) and (c) both introduce a **second intake execution or a second lifecycle**, and this pass already
carries the filesystem, concurrency and retention problems — adding a state machine on top is the larger risk.
⚠️ Accept openly: R10 becomes the slowest route in the system (§Q3).

**[Answer]**: (a) — amend R10 to accept multipart/form-data. R10's request shape was already designed with this in mind (the empty documents list existing specifically so this follow-on's shape would already be correct). One journey, one route.

> ⚑ **CLARIFIED 2026-08-03, after the ambiguity-check's Constraint 4 — the answer above is preserved verbatim and
> its meaning is unchanged; only its precision is improved.** Option (a) as offered read *"AMEND R10 to accept
> `multipart/form-data`"*, which is **ambiguous between ADDING a media type and REPLACING one**. The confirmed
> reading is **ADD**:
>
> > **Amend R10 to ALSO accept `multipart/form-data`, ALONGSIDE its existing JSON shape — not as a replacement.**
>
> ⛔ **Multipart-only was never viable and this is why**: ~15 existing backend tests POST JSON to R10, and the
> frontend shipped at `d43b661` sends JSON. An application with **no documents** has no reason to pay multipart's
> cost. **Fold-7's §2 amendment must therefore read "JSON *or* multipart" for R10**, and the handler branches on
> `Content-Type`. ⚑ Recorded here rather than only in §4.2 because Q1 is where a future reader will look first,
> and the ambiguity was in Q1's own wording.

---

### Q2 — Which WIRE-1 sections does Fold-7 amend?

Grounded in Fold-6's audit-every-section discipline (which **shrank** that amendment by one section):

| § | Needed? |
|---|---|
| **§2** | ⛔ **YES** — a `multipart/form-data` request convention. Unavoidable. |
| **§4** | ⛔ **YES** — a **413** row. Fold-6 explicitly recorded *"no upload ⟹ no 413"*; that reverses. |
| **§5** | **YES** — R10's request shape: the `documents` part, and superseding *"MUST be `[]` under this fold"*. |
| **§3** | **The note block only.** The R10 **row** (path/method/success body/auth) is unchanged under Q1(a). |
| **§1** | ⚠️ **A real question.** Fold-6 argued intake's enums travel under *"intake's contract governs"*. But `DocType` would now be **client-authored**, which is different from R3 echoing it back. |
| **§7.4** | Always — the fold record. |

- **(a) §2 + §3-note + §4 + §5 + §7.4, and ADD a §1 row for `DocType`.** Most conservative; treats a
  client-authored enum as a wire enum.
- **(b) The same, WITHOUT a §1 row**, on Fold-6's precedent verbatim.
- **(c) Defer the §4 `413` by rejecting oversize uploads as `400 invalid_request`.** Fewer sections. ⛔ But 413 is
  the correct status and §4 is a *fixed status table*; misusing 400 to avoid an amendment is the kind of drift
  this project refuses elsewhere.

**Recommendation: (a).** The §1 row is cheap and the distinction is real — every other enum in §1 is one the
**server** emits; this would be the first the **client** asserts, and an unrecognised `doc_type` must have a
defined outcome. ⚑ Fold-6's own lesson was that *an amendment's blast radius is knowable only by auditing every
section* — and that audit made Fold-6 smaller. Here it makes Fold-7 one row larger, which is the same discipline
producing the opposite answer.

**[Answer]**: (a) — §2 + §3-note + §4 + §5 + §7.4, and add a §1 row for DocType. The distinction that this is the first client-authored enum (versus every other §1 enum being server-emitted) is real and worth the one extra row.

---

### Q3 — Synchronous parsing in R10, or not? ⚑ This partially re-opens Q3(a)

Three documents parse **serially** (`pipeline.py:77`), each up to 5 s wall ⇒ **~15 s worst case**. R10 is currently
the fast half of a two-phase flow chosen precisely to keep slow work off the submit button.

- **(a) SYNCHRONOUS — parse inside R10.** Simplest, and keeps `submit()` atomic: intake runs once, the manifest is
  correct, the case persists at `evaluated`. ⛔ R10 becomes the slowest route in the system.
- **(b) Parse in a BACKGROUND task, persist the case first.** Fast submit. ⛔ The case would persist with all
  documents `missing`, then need **re-evaluation** after parsing — a second write and a second rules run, and
  Q3(c) already rejected fire-and-forget for having *"no retry, no visibility, and no failure surface"*.
- **(c) A THIRD phase — submit, upload, then draft.** Honest about the cost. ⛔ Three user actions for one
  application, and it needs Q1(b)/(c)'s re-intake machinery.

**Recommendation: (a)**, with the latency disclosed in the UI rather than engineered away. ⚑ It preserves the
property that matters — **`submit()` stays LLM-free and atomic**, and the manifest is right the first time.
Q3(a)'s invariant was *"no LLM in the request path"*, **not** *"the request path is fast"*; parsing is CPU-bounded,
sandboxed and killable in a way an LLM call is not. ⚠️ But this makes **Q4 load-bearing** — 15 s of held
threadpool worker per submission is exactly the capacity problem.

**[Answer]**: (a) — synchronous parsing inside R10, with the latency disclosed in the UI rather than engineered away. Preserves submit()'s atomicity and correctness; parsing is CPU-bounded and killable, unlike an LLM call, so the original "no LLM in the request path" invariant is preserved even though the request gets slower.

---

### Q4 — ⛔ Concurrency bounding. Nothing exists; something must be designed.

**The arithmetic.** Per document: `RLIMIT_AS` **256 MB**. FastAPI runs sync handlers in a threadpool (**40**
workers by default), so **40 concurrent parses are structurally possible**. Meanwhile the process already holds
uvicorn **plus** the fitted IsolationForest/SHAP model (register #2 stage 3, resident for the process lifetime).

⚠️ **Render's free plan is documented at 512 MB. I have NOT measured it and it must be confirmed at deploy time.**
If it is 512 MB, **two concurrent parses can exceed the instance.**

- **(a) A process-wide semaphore bounding concurrent parses** (e.g. 1–2), acquired in the composition root around
  the intake call. Small, explicit, one named constant. ⛔ Under load, requests **queue**, so p99 latency degrades
  rather than the instance dying — a deliberate trade.
- **(b) Cap the FastAPI threadpool instead.** One line. ⛔ Throttles **every** route, including cheap reads, to
  protect one.
- **(c) A real work queue** (worker + broker). The correct production answer. ⛔ Enormous; `render.yaml` describes
  a single web service, and Q3(d) rejected this same shape for drafting.
- **(d) Nothing — rely on the free tier's low traffic.** ⛔ Rejected on its face: an unbounded 256 MB × N is a
  trivial resource-exhaustion target on an **authenticated but not rate-limited** route.

**Recommendation: (a)**, with the bound as a **named constant** and a test asserting the semaphore is actually
acquired. ⚑ It is the only option that bounds **the thing that is actually unbounded** (memory per parse) without
new infrastructure or collateral damage to other routes. ⚠️ It also converts a crash into a wait, which is the
right direction for a free-tier demo.

**[Answer]**: (a) — a process-wide semaphore bounding concurrent parses (1-2), as a named constant, with a test asserting it's actually acquired. Converts a crash into a queue wait, which is the right direction for a free-tier deployment.

---

### Q5 — ⛔ Temp-file location, and who deletes it. **The retention question.**

`pdfplumber.open()` needs a **real path**, so bytes must land on disk. Four windows:

| Window | Answerable in-process? |
|---|---|
| Parse succeeds | ✅ `try/finally` |
| Parse fails / times out | ✅ `finally` still runs |
| Handler raises between write and parse | ✅ if `finally` wraps the **write**, not the parse |
| ⛔ **Process killed mid-request** (OOM, deploy, free-tier spin-down) | ❌ **No `finally` runs. The file survives.** |

⚑ **Three project-specific aggravations**: this would be the **only** filesystem write in the backend and nothing
guards it; the file is **raw applicant PII** (a salary slip) and `pii_guard` is a *build-time scanner over
committed artifacts*, blind to a runtime temp file; and **Render free-tier spin-down is routine**, so the "crash"
case is the *normal* case there.

- **(a) `tempfile.TemporaryDirectory()` per request, deleted in a `finally`, PLUS a startup sweep** of the parent
  temp root for orphans older than a threshold. Covers all four windows including the kill.
- **(b) Per-request temp dir only, no sweep.** Simpler; accepts that a hard kill leaks a PII-bearing file until
  the container is replaced. ⚑ On an ephemeral filesystem the container **is** replaced — the leak's lifetime is
  bounded by the instance's, which may be an acceptable and *statable* property.
- **(c) An in-memory filesystem** (`tmpfs`/`/dev/shm`) so nothing touches durable storage. Strongest retention
  story. ⛔ Consumes the **same RAM** Q4 is rationing, and is platform-specific.
- **(d) Never write to disk — give `intake` a bytes-accepting worker.** Eliminates the question entirely. ⛔
  **Reopens frozen `intake` (U1)** — the one reopening this pass can otherwise avoid — and pdfplumber still needs
  a file-like object the subprocess can reach across the process boundary.

**Recommendation: (a).** The sweep is ~15 lines and is the only thing that answers the window that has no
in-process answer. ⚑ **Name the retention property explicitly in code and in WIRE-1's fold record** — *"an
uploaded document exists on disk only for the duration of one request, and a startup sweep removes any survivor
of an abnormal termination"* — so it is a stated guarantee rather than an emergent behaviour.

**[Answer]**: (a) — tempfile.TemporaryDirectory() per request deleted in a finally, PLUS a startup sweep for orphans from abnormal termination. State the retention guarantee explicitly in code and in the WIRE-1 fold record, not just as emergent behavior.

---

### Q6 — Size and count limits

None exist. Without them the route is a trivial exhaustion target.

- **(a) A per-file byte cap AND a per-submission count cap, both named constants, enforced BEFORE anything
  touches disk**, mapping to **413**. ⚑ Enforcing pre-disk matters: a 2 GB upload must be refused while streaming,
  not after landing.
- **(b) A total-payload cap only.** Simpler. ⛔ Permits 500 tiny files, each spawning a subprocess.
- **(c) Rely on the reverse proxy's default body limit.** ⛔ Invisible, platform-specific, untestable, and yields
  a non-WIRE-1 error body.

**Recommendation: (a)**, with the count cap set to **exactly the three `DocType` members**. ⚑ `_EXPECTED_DOCS` is
already exactly three and `DocType` is a closed enum, so a fourth document has nowhere to go — the cap is
**derived from the domain**, not invented. ⚠️ Decide whether two files of the same `doc_type` is a 400 or
last-wins; my instinct is 400, because silently discarding an uploaded document is the worst option.

**[Answer]**: (a) — a per-file byte cap AND a per-submission count cap (derived from the domain: exactly 3, matching DocType's closed enum), both enforced before anything touches disk, mapping to 413. On the same-doc-type duplicate question: 400, not last-wins — silently discarding an uploaded document is the worst option.

---

### Q7 — The frontend upload UI, and the shared-transport change

⛔ **`httpTransport.js` must change**: it `JSON.stringify`s every body and always sets
`Content-Type: application/json`. `FormData` must pass through **untouched**, with **no** Content-Type set (the
browser must supply the multipart boundary). **That module is shared by all six seams.**

- **(a) Teach `httpTransport` to detect `FormData` and pass it through**, plus a `submission/` file-input
  component with per-document states (selected / uploading / parsed / unparseable). ⚑ One transport change,
  additive, guarded by a test that the JSON path is byte-unchanged.
- **(b) A SEPARATE upload transport** used only by the submission seam. Zero risk to the other five. ⛔ Two
  transports means two places auth, base-url and error normalization must agree.
- **(c) Bypass the seam and use `fetch` directly in the component.** ⛔ Violates the unit convention every other
  unit follows, and `structure.test.js` already asserts the submission unit calls no `fetch` of its own.

**Recommendation: (a).** The change is ~5 lines and strictly additive; the alternative duplicates a module whose
whole purpose is being the single client-side wire boundary. ⚑ Per-document status must be **visible** — a
document that fails to parse produces a `refer` outcome the user should be able to see and understand, not a
silent downgrade.

**[Answer]**: (a) — teach httpTransport.js to detect FormData and pass it through untouched (no Content-Type set), guarded by a test that the existing JSON path stays byte-unchanged. Per-document status (selected/uploading/parsed/unparseable) must be visible to the user, not silently downgraded.

---

### Q8 — ⛔ The sanitization audit channel is unwired. Wire it, or defer it?

`SanitizationReportChannel`'s default sink is `lambda source_ref, report: None`. It holds `original_span`
**verbatim** — deliberately, as the forensic record — and is documented as *"the SOLE carrier of span text …
DISJOINT by construction from the telemetry seam and any log sink"*.

⚑ **Today this is harmless: no documents means nothing to sanitize.** This pass changes that. It makes
PROJECT-BRIEF §10's failure mode **#4** (*prompt injection in an uploaded document*) reachable for the first time,
and the artifact that would evidence it is discarded.

- **(a) Wire a real sink in this pass.** The neutralization is already correct; only the record is missing. ⛔ But
  the sink's natural destination is `audit-store` — a **frozen** unit — and the report contains **verbatim
  attacker-supplied text plus applicant PII**, so persisting it is itself a retention decision (Q5 again, but
  durable).
- **(b) Defer, and record it as a named register item.** Keeps this pass's scope on upload + parsing. ⛔ The pass
  that creates the risk would then also be the pass that declines to evidence it.
- **(c) A middle course: emit COUNTS to telemetry now** (which is already wired and already carries counts/enums
  only), and defer the verbatim-span sink. ⚑ *"Injection attempts were neutralized on this application"* becomes
  visible without persisting attacker text or PII anywhere new.

**Recommendation: (c).** It closes the invisibility without opening a durable-retention question inside a pass
already carrying one, and it touches no frozen unit — the telemetry seam is already injected and already emits
`neutralization_count`. ⚠️ **(a) remains the right end state** and should be opened as a register item regardless
of which is chosen, so the verbatim channel's disconnection is tracked rather than assumed.

**[Answer]**: (c) — emit counts to the already-wired telemetry seam now (neutralization_count, no verbatim text, no PII), defer the durable verbatim-span sink. Open a register item for (a) as the correct eventual end state, so the disconnection is tracked rather than assumed away.

---

### Q9 — `structured_fields` extraction: confirm OUT of scope

`parse_worker.py:36` returns `"structured_fields": {}` — always. Extracting income from a salary slip would need
real extraction logic **plus** a policy decision about whether document-derived values override form-entered ones,
**plus** an audit story for which value a decision was based on.

⚑ **The scoping instruction already stated this is OUT.** Recorded as a question so the decision is on the record
in the artifact rather than only in conversation.

- **(a) OUT of scope; named explicitly as a future pass.**
- **(b) IN scope for one field** (e.g. income from a salary slip) as a proof of concept.
- **(c) IN scope fully.**

**Recommendation: (a).** ⛔ **(b) is the dangerous one**: a single extracted field still requires the whole
override-policy and provenance decision, and answering it *"just for income"* would set that policy by accident.

**[Answer]**: (a) — confirmed OUT of scope, named explicitly as a future pass. Agreed with your reasoning that even one field would force the override-policy and provenance decision by accident.

---

### Q10 — The optional form fields: confirm IN scope

Per §0.2, documents fix **one of seven** `incomplete` clauses. The optional intake fields — `height_cm`,
`weight_kg` (⇒ `bmi_derived`), `existing_debt_obligations_annual`, `employment_type`, `smoking_status`,
`occupation`, `health_flags` — are collected by nothing today.

⚑ **The scoping instruction already stated this rides along IN this pass, if cheap.** It is cheap: the intake gate
already reads every one of them; only the form needs to ask.

- **(a) IN — add all six/seven as genuinely optional inputs.**
- **(b) IN, but only those needed to demonstrate a completable application.**
- **(c) OUT — its own pass.**

**Recommendation: (a).** The gate reads them already, so the cost is form surface and tests, not logic. ⚠️ They
must be **truly optional** — the disabled-until-valid affordance must continue to key on the **seven required**
fields only, or an optional field would become mandatory by UI accident.

**[Answer]**: (a) — all six/seven optional fields added as genuinely optional inputs, since the gate already reads them and the cost is form surface, not logic. Confirm explicitly in the plan that the disabled-until-valid affordance keys only on the seven originally-required fields, so an optional field can never become accidentally mandatory.

---

### Q11 — ⛔ The `health_flags` limitation: disclose, or work around?

`not health_flags` ⇒ **an applicant reporting no health flags is `incomplete`**. A genuinely healthy applicant
**cannot** reach `incomplete=false`. This is frozen `intake` behaviour.

⚑ **The scoping instruction directs DISCLOSURE, not a fix** — `validation_gate.py` is not to be reopened here.
Recorded as a question only to settle **where** the disclosure lives and **how loudly**.

- **(a) Disclose in the plan, in the form's copy, AND open a register item** so the constraint is tracked rather
  than remembered.
- **(b) Disclose in code comments and the plan only.**
- **(c) Work around it in the UI** — e.g. an explicit *"no health flags reported"* choice that submits a sentinel
  value. ⛔ **Rejected on its face**: it would put a fabricated clinical assertion into an applicant's profile to
  satisfy a completeness check. **Never.**

**Recommendation: (a).** ⚑ A register item is the right instrument: the limitation is real, it is not this pass's
to fix, and *"documents parse but the case is still incomplete"* is exactly the kind of surprise a future reader
deserves to find written down.

**[Answer]**: (a) — disclose in the plan, in the form's copy, AND open a register item. This is a real, user-facing surprise ("I attached everything and I'm still marked incomplete") and deserves to be findable, not just commented in code.

---

### Q12 — Staging. ⚠️ My instinct is this is LARGER than register #2's four stages.

Register #2 needed four stages for a **structured-only** path with no filesystem, no concurrency and no retention
question. This pass has all three, plus a frontend change to a **shared** module.

- **(a) SIX stages**: **1** Fold-7 (§2/§3-note/§4/§5/§1/§7.4) + the route-set/allowlist edits — ⛔ gated like
  Fold-6's three gates · **2** limits + the temp-file lifecycle + the sweep, **backend, no route change yet** ·
  **3** concurrency bounding, independently testable · **4** R10 multipart + real parsing wired · **5** frontend:
  transport + upload UI + optional fields · **6** manual verification + close-out.
- **(b) FOUR stages**, mirroring register #2 (contract → backend → composition → frontend).
- **(c) TWO passes** — backend-only upload+parsing first, ship and verify it by `curl`; the UI as its own pass.

**Recommendation: (a).** ⚑ Stages **2** and **3** are the ones register #2 had no analogue for, and they are the
**risky** ones — a retention bug and a capacity bug are both invisible to a green suite. Giving each its own stage
means each is independently reviewable and independently revertable. ⚠️ Note stage **2** is testable with **no
route at all**, which makes it the natural place to start and the easiest thing to get right in isolation.

**[Answer]**: (a) — six stages, with stages 2 (temp-file lifecycle + sweep) and 3 (concurrency bounding) each independently testable and reviewable with no route required, exactly as you reasoned — a retention bug and a capacity bug are both invisible to a green suite and deserve their own gates.

---

## 3. Mandatory ambiguity-check — RUN 2026-08-02 against Q1–Q12

**Answer set**: Q1(a) · Q2(a) · Q3(a) · Q4(a) · Q5(a) · Q6(a) · Q7(a) · Q8(c) · Q9(a) · Q10(a) · Q11(a) · Q12(a).

**Result: ⛔ NOT CLEAN. One BLOCKING finding, and TWO new questions are surfaced (Q13, Q14).** All three directed
checks were run against the **installed** framework source and the repository, not from recall. One came back
blocking, one came back clean-with-a-constraint, one confirmed the gap it asked about.

### ⛔ Fold A (DIRECTED, BLOCKING) — the framework consumes the whole upload BEFORE authorization runs, and imposes NO file-size limit

Measured in `venv/Lib/site-packages/` — **fastapi 0.139.0 / starlette 1.3.1**:

| Fact | Evidence |
|---|---|
| The body is read **before** dependencies are solved | `fastapi/routing.py:422` `body = await request.form()` … `:473` `solved_result = await solve_dependencies(...)` |
| File parts have **NO size cap** | `starlette/formparsers.py:181-188` — `max_part_size` is checked **only** `if self._current_part.file is None`. **File parts stream unbounded.** |
| Files land on **real disk** above 1 MB | `formparsers.py:147,230` — `SpooledTemporaryFile(max_size=spool_max_size)`, `spool_max_size = 1MB` |
| The knobs are **not tunable per route** | FastAPI calls `request.form()` with **no arguments**, so starlette's `max_files=1000` / `max_fields=1000` / `max_part_size=1MB` defaults apply and cannot be lowered at the route |

⛔ **Three answers cannot be implemented as literally worded.**

1. **Q6's *"enforced BEFORE anything touches disk"* is UNACHIEVABLE** with FastAPI `UploadFile` parameters. Any
   real PDF exceeds 1 MB, so it is **already written to a starlette-owned temp file before the handler exists**. A
   cap checked in the handler runs *after* the bytes have landed.
2. **Q5's per-request `TemporaryDirectory` is the SECOND temp artifact, not the first.** Starlette's spool file is
   the first, is created earlier, and is owned by the framework (closed via `file_stack.push_async_callback`). ⚑
   **The retention guarantee must cover BOTH, and the startup sweep must know about both locations** — otherwise
   it sweeps the directory we control and leaves the one we do not.
3. **Q4's semaphore bounds PARSING, not UPLOAD BUFFERING.** It is acquired around the intake call — long after
   the bytes are on disk. Concurrent large uploads exhaust disk and memory **before any semaphore is reached**.

⚠️ **And it weakens — without breaking — the property register #2 paid for.** C4's spy still records **zero**
intake calls on a 403, so **that test stays green and its claim stays true**. But the property it was standing in
for — *"a wrong-role caller causes no work"* — becomes **false**: the server performs the heaviest I/O of the
entire request, unbounded, before issuing the 403. ⛔ **On a route with no rate limit, that is an
unauthenticated-adjacent resource-exhaustion vector**, and it is exactly the class of thing Q10 of register #2
existed to prevent.

**RESOLUTION DIRECTION**: the bytes must be bounded and the caller authorized **before** `request.form()` is
allowed to consume the stream — which means something upstream of the route handler. ⛔ **Which mechanism is a
decision, not a fold — Q13.**

### ✅ Fold B (DIRECTED) — the startup sweep does NOT conflict with the laziness finding, but it is CONSTRAINED

* `backend/app/main.py` has **no `lifespan`, no `on_event`, no startup hook of any kind** — this pass would
  introduce the first.
* Register #2's guard is `test_create_app_does_not_fit_the_model`, which asserts only that **no model fit**
  happens. A sweep is not a fit, so **the letter of the test is safe**.
* ⚑ But the *documented* property is stronger — *"`create_app()` still constructs nothing and reads no
  setting"*. **The sweep must therefore be a `lifespan` startup hook, NOT anything in `create_app()`'s body.**
* ⚠️ Every `conftest.py` fixture enters `with TestClient(app)`, which **runs lifespan**. So the sweep executes in
  every one. A `listdir` of an empty directory is negligible, so this is not a cost problem — but it **is** the
  first eager filesystem side effect at app startup, and it will run several times per test session.
* ⛔ **The sweep MUST be failure-tolerant.** A sweep that raises — an unreadable directory, a permissions error on
  Render — would take the whole application down at boot. **That is strictly worse than the leaked file it
  exists to remove.** Fail-open with a log, never fail-closed.

**No new question. Q5(a) stands, with these three constraints written into it.**

### ⛔ Fold C (DIRECTED) — `test_no_write_route.py` has NO opinion about file I/O, and this pass is what makes that matter

`grep -c "open(\|write_bytes\|write_text\|mkdir\|tempfile\|shutil\|os\.remove\|unlink"` over that file → **0**.

Its assertions cover `.insert(` / `.atomic(` / `.commit(` / the three claim methods / `AUDIT_WRITER_URL` /
`create_engine` / the domain seams. **Not one of them concerns the filesystem.** So a new module writing applicant
PDFs to disk would pass every structural guard in the composition root **silently**.

⚑ **This is the same shape as register #2's Fold A, one level over.** There, the guard existed and was too broad.
Here, **the guard does not exist at all** — and the thing it would guard is *raw applicant PII on disk*, which is
a higher-stakes subject than the transaction boundaries the file currently polices.

⚑ **The precedent for the fix already exists in that same file**: `_PIPELINE_MODULES`, added by Fold-6, is an
**exact set** naming which modules may reference the pipeline. A `_FILESYSTEM_WRITE_MODULES` set of identical
shape would name which module may touch the filesystem, and fail when a second one appears.

⛔ **But whether that guard is its own separately-gated sign-off — as G3 was for the TRIGGER-1 narrowing — is a
decision, not a fold — Q14.**

### ✅ Fold D — Q8(c)'s telemetry route reopens no frozen unit

`TelemetryEmitter` is injected into `IntakePipeline` and already emits `neutralization_count` on the
`SANITIZE` event (`pipeline.py:104-105`). Q8(c) therefore needs **no `intake` change at all** — only a real
emitter at the composition root instead of the default. ⚑ Confirms Q8(c) is the option that touches nothing
frozen, which was its main argument.

### ✅ Fold E — Q10's optional fields reopen nothing, and the affordance constraint is real

Every optional field named in Q10 is **already read** by `validation_gate._evaluate` (`height_cm`, `weight_kg`,
`existing_debt_obligations_annual`, `employment_type`, `smoking_status`, `occupation`, `health_flags`). The gate
needs no change; only the form must ask. ⚑ **Q10's stated constraint is confirmed necessary**: the
disabled-until-valid affordance keys on `REQUIRED_FIELDS`, so the optional fields must **not** be added to that
tuple — or an optional field silently becomes mandatory. A test should pin `REQUIRED_FIELDS` at exactly the
original seven.

---

## 4. NEW QUESTIONS SURFACED BY THE CHECK — ANSWERED

### Q13 — How are bytes bounded and the caller authorized BEFORE the upload is consumed? (Fold A)

- **(a) An ASGI middleware in front of the route** that rejects on `Content-Length` over the cap **and** resolves
  the session/role, before the request ever reaches FastAPI's body-reading. ⚑ It is the only layer that sits
  **upstream of `request.form()`**. ⛔ But it duplicates authentication outside `require_underwriter`, which is
  precisely the "two places decide authorization" shape this project has refused elsewhere — unless it is framed
  as a **cheap pre-filter that denies early and never grants**, with the real gate unchanged behind it.
- **(b) Drop `UploadFile` parameters and consume `request.stream()` by hand** in the handler, enforcing the byte
  cap as chunks arrive and writing straight into our own temp dir. ⚑ Gives exact control of both limits and
  retention, and **eliminates starlette's spool file entirely** — one temp artifact instead of two. ⛔ Hand-rolled
  multipart parsing is genuinely hard to get right, and `Depends` ordering still puts auth after the handler
  begins… though the handler can check auth **before** reading the stream.
- **(c) Rely on `Content-Length` alone, checked in a dependency ordered before the body param.** ⛔ Does not work:
  `request.form()` at `routing.py:422` runs before **any** dependency, so no `Depends` can pre-empt it. Recorded
  because it is the obvious answer and it is wrong.
- **(d) Accept the limitation**: cap in the handler, tolerate the buffered write, document it. ⛔ It makes Q6's
  central promise false and leaves an unbounded upload path on a rate-limitless route.

**Recommendation: (b)**, with **(a)** as a thin `Content-Length` fast-reject only — no authentication in the
middleware. Grounds: (b) is the only option that makes Q6's *"before anything touches disk"* **literally true**,
and it **removes** the second temp artifact Fold A found, which simplifies Q5 rather than complicating it. Pairing
it with a `Content-Length` pre-reject gives an early, cheap 413 without moving any authorization decision out of
`require_underwriter`. ⚠️ The cost is real and must be stated: **this pass would hand-roll multipart handling**,
and that deserves its own stage and its own adversarial tests.

**[Answer]**: (b) — drop UploadFile parameters and consume request.stream() by hand in the handler, enforcing the byte cap as chunks arrive and writing directly into our own controlled temp dir. Paired with (a) as a thin Content-Length fast-reject only — no authentication logic in the middleware, just an early cheap 413 for obviously-oversized requests. This is the only combination that makes Q6's "before anything touches disk" literally true and eliminates the second, framework-owned temp artifact entirely, which simplifies Q5 rather than adding a second thing to sweep.

Accept the disclosed cost explicitly: hand-rolled multipart parsing is genuinely hard to get right and deserves its own stage with real adversarial tests (malformed boundaries, truncated streams, a part with no filename, oversized Content-Length that lies about actual body size, etc.) — don't treat this as a small addition to an existing stage.

---

### Q14 — Does the new filesystem guard get its own gated sign-off? (Fold C)

- **(a) Yes — a THIRD gate, alongside the Fold-7 contract amendment and the route-set edit**, mirroring register
  #2's G1/G2/G3 exactly. The guard would be an exact-set `_FILESYSTEM_WRITE_MODULES` assertion plus a
  demonstrated non-vacuity proof (a synthetic module writing a file must fail it). ⚑ Register #2's G3 established
  that a load-bearing structural guard is widened **deliberately, never quietly** — and this one is being
  **created**, which is a larger act than widening.
- **(b) Yes to the guard, no to the separate gate** — fold it into the route-set gate. Fewer stops. ⛔ Exactly the
  bundling Q1(a) of register #2 rejected.
- **(c) Add the guard at the end, once the module exists.** ⛔ Then it is written to fit the code rather than to
  constrain it, which is how a guard becomes a tautology.
- **(d) No guard.** ⛔ Rejected: it would leave *raw applicant PII on disk* as the only capability in
  `backend/app/` with no structural check, in a package where transaction boundaries, engine construction, domain
  seams and pipeline reachability are all mechanically policed.

**Recommendation: (a).** ⚑ Write the guard **BEFORE** the writing module exists, so the first thing the new module
does is fail it — the strongest available proof that the guard bites, and the same RED-first discipline every
other assertion in that file was created under.

**[Answer]**: (a) — a third gated sign-off, mirroring register #2's G1/G2/G3 exactly, with the guard written and its non-vacuity proven BEFORE the writing module exists, so the module's first real test is failing against a guard already in place. This is the same RED-first discipline used throughout this project, applied to a guard that's being created rather than widened — which is the larger act, not the smaller one.

---

## 4.2 ✅ Ambiguity-check RE-RUN against the complete Q1–Q14 set — **CLEAN**, with FOUR recorded constraints

**Answer set**: Q1(a) · Q2(a) · Q3(a) · Q4(a) · Q5(a) · Q6(a) · Q7(a) · Q8(c) · Q9(a) · Q10(a) · Q11(a) ·
Q12(a) · **Q13(b)+(a)-as-fast-reject** · **Q14(a)**.

**Result: CLEAN. Fold A's blocking finding is RESOLVED — and resolved by MEASUREMENT, not by argument. No new
question is surfaced. Four constraints are recorded, each of which the execution plan must encode.**

### ✅ Re-check 1 (DIRECTED) — Q13(b) RESTORES the auth-before-work property. Proven, not asserted.

The directed question was whether Q13(b) genuinely restores the ordering Fold A found degraded, or merely moves
the problem. **Measured with a throwaway probe against the installed fastapi 0.139.0 / starlette 1.3.1**, a
5 MB multipart upload against two handlers that declare **no body parameter**:

```
DENIED  -> status=403  events=['AUTH']                      <- ZERO bytes read
ALLOWED -> status=413  events=['AUTH-OK', 'HANDLER-BODY']   <- cap fires on the first chunk
```

⚑ **The mechanism, and why it is structural rather than incidental.** `fastapi/routing.py:419-422` reads the body
**only** `if body_field:` — and `body_field` is populated **only** when the dependant declares a body parameter.
A handler taking `Request` and `Depends(...)` alone therefore has `body_field is None`, so **line 422 never
executes**. The ordering becomes:

1. `solve_dependencies` → `require_underwriter` → **403 raised here**, and
2. the handler body — the only place `request.stream()` is ever touched — **never runs**.

**So the property is not merely restored, it is restored BY CONSTRUCTION**: the stream is unreachable until after
authorization, because the only code that reads it is downstream of the dependency that refuses. ⚑ This is
strictly **stronger** than the position before Fold A: R10 today is protected by *FastAPI resolving `Depends`
before the handler body*; under Q13(b) it is protected by that **plus** the framework never touching the body at
all. **A wrong-role caller now causes literally zero I/O**, which is what register #2's C4 spy was standing in
for and could not itself enforce.

⚠️ **One property the probe also establishes**: the 413 fires on the **first chunk that crosses the cap**, so a
lying `Content-Length` is caught by the streaming counter regardless. **The middleware fast-reject is an
optimization, NOT the security control** — that distinction must be written into the code, or a later reader will
assume the middleware is load-bearing and weaken the handler check.

### ⛔ CONSTRAINT 1 — the handler must be `async def`, and the intake call MUST be offloaded

`request.stream()` is an async generator, so the handler becomes `async def`. ⛔ **But `IntakePipeline.process` →
`SubprocessParseWorker.parse` → `subprocess.run` is fully BLOCKING**, and FastAPI runs `async def` handlers **on
the event loop**, not in the threadpool. Calling intake directly from the async handler would **block the entire
event loop for up to ~15 s**, freezing every other request in the process — health checks included.

**Required shape**: `async def` handler reads and caps the stream → writes the temp files → hands the blocking
intake+submit work to `starlette.concurrency.run_in_threadpool`. ⚑ Every **other** route in the app is `def` and
is already threadpooled by FastAPI; R10 becomes the first handler that must arrange this for itself, and the
first place where getting it wrong degrades the whole process rather than one request.

### ⛔ CONSTRAINT 2 — Q4's semaphore must be an `asyncio.Semaphore`, acquired in the async handler

Q4(a) said "process-wide semaphore". Under Constraint 1 the type matters: a `threading.Semaphore` awaited from
the async handler would **block the event loop while waiting**, and one acquired inside the threadpool function
would **hold a threadpool worker** for the duration of the wait. An `asyncio.Semaphore` acquired in the handler
around `run_in_threadpool` parks the waiter on the event loop at near-zero cost. ⚑ **Q4(a) stands; its
implementation is now specified rather than left open.**

### ⛔ CONSTRAINT 3 — `form_fields` loses Pydantic validation and must be validated by hand

Dropping the body parameter also drops `SubmissionRequest`. R10's `form_fields` currently arrives as a validated
Pydantic model; under Q13(b) it arrives as a multipart part the handler decodes itself. ⚑ **The 400 path changes
shape**: today a malformed body is caught by FastAPI's `RequestValidationError` handler; under Q13(b) the handler
must produce the same WIRE-1 §4 envelope itself. ⚠️ **The existing test that pins a malformed body → 400 must
keep passing**, and it becomes an assertion about hand-written code rather than about the framework.

### ⛔ CONSTRAINT 4 — R10 must accept **BOTH** JSON and multipart, and this is forced, not chosen

Q1(a) says *"amend R10 to accept multipart"*. It does **not** say "multipart only" — and multipart-only is
**not viable**:

* **~15 existing backend tests POST JSON to R10** (`test_submission_routes.py`'s `submit()` helper and every test
  built on it), and
* **the shipped frontend sends JSON** — `submission/fetchSeam.js` builds `{form_fields, documents: []}`, already
  committed at `d43b661` and verified in a browser.

Making R10 multipart-only would break both for no gain: an application with **no documents** has no reason to
pay multipart's cost. **Required shape**: the handler branches on `Content-Type` — JSON keeps the existing path
byte-for-byte, multipart takes the new streaming path. ⚑ **Fold-7's §2 amendment must therefore say
"JSON *or* multipart" for R10**, not "multipart".

⚠️ **If multipart-only is actually wanted, say so** — it costs ~15 test rewrites plus a frontend change, and it
is a different answer to Q1 than the one recorded.

### ✅ Re-check 2 — Q14's guard and Q13(b)'s streaming write compose cleanly

Q14(a) creates `_FILESYSTEM_WRITE_MODULES` **before** the writing module exists. Q13(b) means exactly **one**
module writes files (the handler's temp-file helper), and starlette's spool file — the artifact we would not have
owned — **is eliminated**. ⚑ **So the guard's exact set has exactly one member, and Q13(b) is what makes that
true**: under the rejected `UploadFile` approach the framework would have been writing files outside any set the
guard could name. The two answers reinforce each other rather than merely coexisting.

### ✅ Re-check 3 — Q5's sweep now has ONE directory to sweep, not two

Fold A found that Q5's per-request `TemporaryDirectory` was the *second* temp artifact. **Q13(b) removes the
first.** The sweep's target is now a single, app-owned root whose layout the app defines — which is what makes a
sweep meaningful at all, since sweeping a directory the framework manages would have been both unsafe and
racy against concurrent requests.

### ✅ What the re-check did NOT find

* **No frozen-unit reopening.** `intake` is used as-is (a path is handed to `SubprocessParseWorker`); the rules
  engine needs nothing; U24 stays duck-typed; hand-rolled streaming lives in `backend/app/`.
* **No conflict with `submit()`'s atomicity** — parsing completes before `submit()` is called.
* **No new register item beyond the two Q8 and Q11 already open by their own answers.**

---

## 5. Frozen units — expected reopenings

| Unit | Assessment |
|---|---|
| **`intake` (U1)** | ⚑ **NONE under Q5(a)/(b)/(c)** — `SubprocessParseWorker` already takes a path, so writing a temp file uses U1 **as-is**. ⛔ **Q5(d) would reopen it**, and so would wiring the sanitization sink under Q8(a). **This is the pivotal choice.** |
| **`rules_engine`** | ✅ **NONE.** `DOCS-COMPLETE-1` exists and already reads `documents_missing_count`. |
| **`case_lifecycle` (U24)** | ✅ None expected — duck-typed, as in register #2. |
| **`deploy_config` (U23)** | ⚠️ **Likely** — the route inventory if Q1(b)/(c) adds a route, and possibly `render.yaml` for temp storage. |
| **`common`** | ✅ None. |

---

## 6. Holds for this pass

| Hold | Status at the plan gate |
|---|---|
| No backend file touched | ✅ Read-only throughout. |
| WIRE-1 untouched | ✅ Read-only. Fold-7 is **proposed, not drafted**. |
| No frozen unit edited | ✅ No reopening requested yet. |
| No code written | ✅ Files written: **1** — this plan. |
| No commit | ✅ User's call. |
| Register unchanged | ✅ **29 tracked. #2 partly discharged.** |

---

## 7. Carried forward — do not lose these

1. ⛔ **`corpus/` on Render is STILL an open deployment action** — created by register #2, declared at
   `outlier_composition.CORPUS_ON_RENDER`, **not yet implemented**. This pass adds a **second** filesystem
   dependency of a **different kind**: writable, not merely readable. **The deployment pass now owes two things.**
2. ⚠️ **Register #2's residual inside gap (ii)** — a pending case has no UI draft affordance outside the
   immediately-post-submit flow. **Unrelated to this pass, still open.**
3. ⚑ **`python-multipart` is a declared, unused dependency.** If Q1 lands anywhere but (a)… it is used either way.
   Recorded because an unused dependency that suddenly becomes load-bearing deserves a version pin review.
4. ⚑ **The Render free-tier memory figure (512 MB) is DOCUMENTED, NOT MEASURED.** Q4's arithmetic depends on it.
   **Confirm at deploy time.**
