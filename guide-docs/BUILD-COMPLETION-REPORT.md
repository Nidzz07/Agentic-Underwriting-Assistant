# BUILD COMPLETION REPORT — Agentic Underwriting Assistant

**Report type**: read-only retrospective synthesis · **Date**: 2026-07-19
**Scope**: a summary of what exists on disk at the close of the GUIDE-AI-SDP BUILD phase. **This report creates no code,
re-opens no unit, re-derives no frozen decision, and starts no work.**

**Verification method**: every factual claim below was checked against `guide-docs/audit.md`, `guide-docs/guide-state.md`,
the `guide-docs/build/` directory tree, `guide-docs/discover/application-design/unit-of-work.md`, and the live test suites —
**not** reconstructed from conversation summaries. Two live runs were performed for this report (`pytest backend`,
`npm run test`); both are read-only. **Discrepancies found are flagged in §7.**

---

## 1. Executive summary

**The system**: a BFSI **Agentic Underwriting Assistant** (`PROJECT-BRIEF.md`) — ingests loan/insurance applications with
supporting documents, evaluates them against a **versioned deterministic rulebook** (pure Python, zero LLM), compares
applicants against a synthetic corpus using **ML outlier detection**, and drafts an **audit-ready decision memo** for human
underwriter review. Architectural invariants: **advisory-only** (the system never finalises a decision), **deterministic
core**, **full auditability**, **bias-free by design**, **human-in-the-loop as a hard constraint**.

**The methodology**: **GUIDE-AI-SDP** — a DISCOVER → BUILD → DEPLOY workflow with a per-unit BUILD loop of five stages
(Functional Design → NFR Requirements → NFR Design → Infrastructure Design → Code Generation), each stage gated by explicit
written user approval, each with a plan-then-generate split and a mandatory ambiguity-check before generation.

**Final scale (measured 2026-07-19):**

| Metric | Value |
|---|---|
| Units complete | **23 of 23** (17 Phase-1 + 6 Phase-2) |
| Backend tests | **1308 passed / 31 skipped / 5 pre-existing `audit_store` Docker-absence errors** |
| Frontend tests | **682 passed / 137 test files** (verified live for this report) |
| Backend coverage | **99.86%** — `--cov-fail-under=90` **held** |
| Infrastructure Design | **3 real passes · 20 logged, rule-justified skips** |
| Open register items | **20** (see §5) — ⚑ *was 12 at this report's original writing; folded to the true count 2026-07-21* |

---

## 2. Unit-by-unit ledger

All 23 units completed their applicable stages: **Functional Design ✓ · NFR Requirements ✓ · NFR Design ✓ · Infrastructure
Design (real pass or logged skip) ✓ · Code Generation ✓**.

**Infra column key** — `SKIP` = assessed at the stage and logged with explicit rule justification under **CLAUDE.md**
*"Skip IF: No infrastructure changes / Infrastructure already defined"* **+ `execution-plan.md:200`**'s *Lighter /
minimal-footprint* classing (*"pure-logic units … have little independent infra; `admin-cli` has none; `ui-*` is static
hosting on Vercel"*). `REAL` = a comprehensive non-skip pass (§4).

### Phase 1 — 17 units

| # | Unit | Infra | Delivers |
|---|---|---|---|
| U1 | `intake` | SKIP | Turns an application form + documents into one validated, typed `ApplicantProfile`, or rejects at the Pydantic gate. |
| U2 | `document-sanitizer` | SKIP | Neutralises prompt-injection text so hidden instructions never reach the LLM (SEC-1). **⚑ Co-built inside `intake`** — see §7.1. |
| U3 | `rules-engine` | SKIP | Evaluates the profile against a versioned rulebook in **pure Python, zero LLM**; produces the recommendation + per-rule report. |
| U4 | `memo-agent-core` | SKIP | Drafts the audit-ready, rule-cited memo — **prose only**, never touching the recommendation (CON-BR2-TYPE). |
| U5 | `ui-queue` | SKIP | The application queue (display). |
| U6 | `ui-memo-view` | SKIP | Memo view with rule citations, confidence, missing-info list. |
| U7 | `ui-approval-gate` | SKIP | The human approval-gate UI facet (backend enforcement single-sourced in `audit-store`). |
| U8 | `ui-override-form` | SKIP | Override-with-mandatory-reason UI facet (invariant-bearing). |
| U9 | `ui-history` | SKIP | Decision-history browse; links to the audit tuple. |
| U10 | `ui-shell` | SKIP | The UI-wide invariant — advisory-only copy conventions + the `data-testid` contract. |
| U11 | `auth-rbac` | SKIP | Canonical role/permission model + backend enforcement at both points. |
| U12 | `audit-store` | SKIP | Decision-write + audit + replay boundary; owns `DecisionCommitService` (rejects writes lacking underwriter action). |
| U13 | `quality-gates` | SKIP | The four blocking gates as one CI/pytest harness (bias-swap delta 0, reproducibility, rule coverage, code coverage). |
| U14 | `corpus-generator` | SKIP | Build-time seeded, versioned, skew-audited synthetic corpus (300+, 40/35/25), frozen by a manifest. |
| U15 | `database` | **REAL** | Shared PostgreSQL schema + migrations (no SQLite — DATA-5). |
| U16 | `secrets-config` | SKIP | Provider/service keys via env/secrets; build fails on a hardcoded secret (SEC-3). |
| U17 | `admin-cli` | SKIP | Out-of-band rulebook-version + user/role/provider-config management (no admin UI). |

### Phase 2 — 6 units (in completion order)

| # | Unit | Infra | Delivers |
|---|---|---|---|
| U18 | `outlier-model` | SKIP | Compares an applicant against the seeded corpus and explains anomalies, **without demographic identifiers**. |
| U20 | `ui-outlier-view` | SKIP | Outlier flags + SHAP in the memo view; conforms to the `ui-shell` contract. |
| U19 | `memo-extensions` | SKIP | Extends the memo agent with grounding + routing + provider breadth (Claude/Ollama adapters, MCP tools). |
| U21 | `observability` | **REAL** | Langfuse traces (100% of steps) + Prometheus/Grafana (5 metrics). |
| U23 | `deploy-config` | **REAL** | Validation deploy on Render + Vercel, free-tier. |
| U22 | `llm-judge` | SKIP | promptfoo groundedness rubric ≥4/5 (Gemini+Claude in-gate; Ollama exempt). **The 23rd and final unit.** |

> **Note on ordering**: Phase-2 units completed **U18 → U20 → U19 → U21 → U23 → U22**, not in numeric order. This is
> consistent throughout `guide-state.md` and `audit.md`.

---

## 3. The Infrastructure Design record

**20 of 23 units logged a SKIP; 3 took a real, comprehensive pass.** The distinction was not incidental: the
`unit-of-work.md` annotation *"comprehensive at Infrastructure Design"* appears **exactly three times** — L218
(`database`), L248 (`observability`), L250 (`deploy-config`) — and maps **1:1** onto the three units with an
`infrastructure-design/` directory on disk. Every skip was assessed **at the stage** and logged with rule justification;
none was silent or pre-assumed.

---

## 4. The three real Infrastructure Design passes

Each of these designed a **deployed, running service topology** — qualitatively different from the 20 skips, which were
pure-logic or display units that provision nothing.

**`database` (U15) — the first non-skip.** Designed Postgres provisioning **per tier**, the **grant-DDL execution**
mechanism (a pinned placeholder-substitution scheme for the writer/reader role split), connection and pooling
configuration, and **migration execution per environment**. It also placed the `DbUrlGuard` and fixed the `secrets-config`
contract as **shapes only, never values** — establishing `AUDIT_WRITER_URL` / `AUDIT_READER_URL` as *required*, not
optional. This is the pass that made the append-only, role-separated audit store physically realisable.

**`observability` (U21) — the second.** Designed the **live Langfuse binding** at composition level (the real callback
attaching to U4's frozen graph checkpointer), the Prometheus **`/metrics` mount + scrape**, the **single Grafana dashboard
topology**, and **`secrets-config` key delivery** for both sinks. It also explicitly designed **AC-7's deploy-time
100%-trace audit** as a split: what is verifiable at tier-U versus what can only be audited against a running system. The
code-side halves it left unbound are `OBS-SINK-DEFERRED`.

**`deploy-config` (U23) — the third.** Designed the **Render backend service**, the **Vercel frontend project**, and — the
load-bearing decision — **frontend↔backend connectivity via a Vercel rewrite/proxy**, chosen specifically so the deployed
topology requires **no CORS change in the backend** and therefore **never touches the closed composition root**. Also: the
DB-provisioning reference + **migration release step**, the env-manifest topology (**shapes only**), the observability
deployment half, and an **honest partial-deploy deploy doc** recording which routes are live versus `501`.

---

## 5. The complete Deferred Decisions register — 20 items

> ⚑ **FOLD NOTE — 2026-07-21.** This section recorded **12** items when this report was first written. That figure was
> **already stale at the time**: **#13** and **#14** had been opened later (in the Scope B plan and U24's `states.py`)
> and were **never folded back in** — the register was *14 in substance, 12 in this document*, a disclosed
> documentation lag. The **Scope B wiring pass** then opened **six more** (#15–#20), which likewise existed only as
> declarations in code.
>
> **All eight (#13–#20) are folded in below**, at the same rigor as #1–#12. **Items #1–#12 are preserved byte-for-byte
> and unaltered.** The register now stands at **20**, which is the true current count.
>
> ⚑ **One item has been DISCHARGED — see the note directly beneath the table regarding #2.**

All twenty verified present in `guide-state.md` and `audit.md`. **"Blocking"** below means: does this prevent the system
being *usable as built today*?

| # | Item | What it is | Why deferred, not resolved | Owner | Blocking? |
|---|---|---|---|---|---|
| 1 | **Composition root — Q1-B divergence** | A divergence between the composition root's realized scope and an earlier option-B intent. | The root was **deliberately closed** at its integration pass; reopening it was never authorized. | composition root / user authorization | **Non-blocking** for what is wired; contributes to #2. |
| 2 | **R2–R5 unwired** (R4 a `501` stub) | Four of seven WIRE-1 routes are registered as `501 not_implemented`: no pending-application store, no pre-commit profile store, no drafting trigger, only a test-fake commit context. | Each needs a store or trigger no unit was scoped to own; wiring them would have required reopening the closed root. | composition root / a future wiring unit | **⚑ BLOCKING for the end-to-end demo path** (see §6). |
| 3 | **tier-B corpus run** | The real 300+ synthetic corpus has **never been generated or run against**. | Never authorized. Confirmed **not applicable to any unit** across the whole build — every unit completed at tier-U on seeded fixtures. | user authorization | **Non-blocking** for unit-level correctness; **blocking** for real-corpus quality verification. |
| 4 | **`audit_store` Docker-guard gap** | 5 integration tests error without Docker; 31 tests skip. | A hygiene gap in the guard, not a correctness defect. **Stable at exactly 31 skips + 5 errors across every unit** since first identified. | `audit-store` / CI config | **Non-blocking** — the affected paths are covered by unit-tier tests. |
| 5 | **`OUTLIER-IN-PROSE`** | The outlier signal is not surfaced in memo prose. | Surfaced during Phase 2; **never assigned an owner**. | **unassigned** | **Non-blocking**. |
| 6 | **`MCP-TRANSPORT-DEFERRED`** | The MCP protocol/SDK transport binding for the memo agent's tools. | Would have introduced a new dependency; the tools work through an injected seam without it. | `memo-extensions` / composition | **Non-blocking**. |
| 7 | **`OBS-SINK-DEFERRED`** | The **live code-attachment half** of Langfuse/Prometheus/Grafana. | The deployment half **is** realized as committed config (§4); the code binding is composition's, and both SDKs are already floored + installed. | composition / `deploy-config` | **Non-blocking** — no tier-U invariant depends on it. |
| 8 | **`DEPLOY-MIGRATE-DEFERRED`** | `render.yaml`'s `preDeployCommand` references a migration runner with **no CLI entrypoint** (`backend/database/migrate.py` absent). | The runnable entrypoint is `database`'s/composition's deliverable, not `deploy-config`'s. Carried on the AC-7 *provisioned-for-not-discharged* pattern. | `database` / composition | **Non-blocking** at build time; **blocking for an actual deploy**. |
| 9 | **`PROMPTFOO-CLI-DEFERRED`** | The real promptfoo engine. The pip package is a **thin shim around the Node CLI**, and **the Node engine is absent**; invoking it would `npx`-fetch an **unpinned** package at run time and pulls `posthog` telemetry. | Unacceptable at tier-U and in a BFSI system. The engine sits behind an injected Protocol with an offline fake. **5 discharge criteria** recorded in code. | `llm-judge` (U22) | **Non-blocking** — the deterministic half is fully verified without it. |
| 10 | **`JUDGE-EVAL-DEFERRED`** | The real ≥4/5 groundedness gate evaluated over the tier-B corpus. | Needs tier-B **and** live keys **and** a working engine. **One-way prerequisite**: requires #9 discharged first. | `llm-judge` (U22) | **Non-blocking** for U22's completion; **blocking** for AC-6 verification. |
| 11 | **`FEWSHOT-ANCHOR-UNIMPLEMENTED`** | QA-4's **generation-side** few-shot anchoring — supplying exemplars to the memo prompt at draft time. Repo-wide scan: **zero hits**. | Implementing it requires passing exemplars **into** a **frozen P1 unit's** `PromptBuilder` — forbidden without its own separate authorization. | **`memo-agent-core` (U4)** or a future explicitly-authorized change — **never `llm-judge`'s to discharge** | **Non-blocking**; leaves QA-4 half-realized (§6). |
| 12 | **`testresults.txt` append-vs-overwrite** | The file is overwritten per unit rather than appended, losing per-unit history. | Housekeeping; never escalated. | housekeeping | **Non-blocking**. |
| 13 | **`NOTWIRED-FILENAME-STALE`** | `backend/app/routes/not_wired.py` is named for markers it no longer holds. ⚑ **REALIZED by the Scope B wiring pass**: the file now holds **four WIRED routes on the primary user journey** under a name asserting the opposite. | Renaming it breaks U23's frozen `NFR-DEP-ROUTES-1`, which asserts **exact-set equality** over filenames in that directory. **The rename and the test relaxation are a MATCHED PAIR** requiring their own authorization; neither half is valid alone. | `deploy-config` (U23) + composition root, **as one change** | **Non-blocking** for behaviour. A **real readability cost**: a maintainer tracing the memo-view flow lands in a file called `not_wired.py` that is entirely wired. |
| 14 | **`MEMOVIEW-FAILED-STATE-UNMODELLED`** | WIRE-1 §5's `MemoView.status` is a **closed two-value discriminator** (`ready`\|`pending`). U24's internal `failed` state has **no wire representation**, so it projects to `pending` — but *"has not **yet** produced a memo"* implies it eventually will, which a failed case never will. | Adding a third status **amends WIRE-1's contract text**, forbidden without its own authorization. `failed` remains internally distinguishable (FAILED-1); only the wire projection is lossy. ⚑ **Blast radius WIDENED by the wiring pass**: with R4 live, failed cases now render as `pending` **to a real client**, not just in theory. | a future authorized WIRE-1 amendment | **Non-blocking** — the loss is diagnostic precision at the wire, not correctness. Compounded by #16. |
| 15 | **`R2-N+1-AMPLIFIED`** | R2 enumerates all application ids, then **per row** performs a `get_application` **+ a CANON-SER rehydration + a `recommendation_for_application`** — materially worse than R6's CR-Fold-4 N+1, which has no per-row rehydration. Declared at `backend/app/routes/not_wired.py:100`. | The accepted cost of reusing the existing `paginate` projection verbatim and keeping pagination in-app (Q4b). Optimizing means pushing `limit`/`offset` **into U24**, a separate change with its own reopening cost. **Disclosed rather than optimized**, deliberately. | composition root / a future U24 `limit`-`offset` change | **Non-blocking.** Harmless at Phase-1 volumes; one bounded page still crosses the wire. |
| 16 | **`APPSUMMARY-FAILED-INDISTINGUISHABLE`** | WIRE-1's `ApplicationSummary` has **no `status` field at all**, so a `failed` case is **indistinguishable from a fresh one** in the R2 queue. Declared at `backend/app/projections.py:95`. | Rows are deliberately **not** filtered by state: filtering silently would be an **undisclosed domain decision taken inside the composition root** (Q4d-iii), which the whole pass was careful to avoid. Adding a status field amends WIRE-1. | a future WIRE-1 amendment (pairs with #14) | **Non-blocking** for correctness; a **real diagnostic-precision loss** for a queue user. |
| 17 | **`OUTLIER-DATA-EXISTS-CONTRACT-FORBIDS`** | `PendingRecommendation.outlier_canonical` **persists real outlier data**, but WIRE1-Fold-4 binds `outlier: null` in Phase 1 **even for a `ready` view**. The data exists; the frozen contract forbids sending it. Declared at `backend/app/projections.py:138`. | Emitting it would be an **unauthorized contract change**. WIRE-1 was honored and the mismatch **disclosed rather than quietly resolved** (Q5b) — *"the data exists but the contract forbids it"* is exactly what should be reconciled deliberately later, not silently now. | a future WIRE-1 amendment | **Non-blocking.** A deliberate contract-fidelity choice. |
| 18 | **`NO-PRODUCTION-LLMCLIENT`** (**B4**) | **No production `LLMClient` implementation exists anywhere in the repo.** `memo_agent_core/provider.py` names it as deferred to composition — *"the real google-genai client is wrapped to this at composition"* — and **composition closed without supplying it**. ⚑ **Compounding**: `requirements.txt` declares **`google-generativeai`** (legacy SDK) while the code imports `from google import genai` (the **new `google-genai` SDK**) — **different distributions**, and `google-genai` is **declared nowhere**. Declared at `backend/scripts/seed_demo_cases.py:6`. | The only real adapter (`corpus_generator/build.py::_GeminiLLMClient`) is a **tier-B out-of-band entrypoint**, and **tier-B is not authorized**. Building a new one needs a **new dependency**, a live `GEMINI_API_KEY`, real network and real spend. The seed script therefore uses a **disclosed deterministic offline double** (Q12-C). ⚑ **The build closed with a deferred seam absent from its own register** — the same failure mode as the `CaseSeams` blocker. | composition / `deploy-config` (secrets) | **Non-blocking** for the wired API layer and the seeded demo. **⛔ BLOCKING for any real memo generation** — no genuine LLM-drafted memo can be produced by this system today. |
| 19 | **`COMMITTED-TRANSITION-NEVER-PERFORMED`** (**G2**) | `drafted → committed` is declared legal in U24's `LEGAL_TRANSITIONS` and `COMMITTED` is terminal, but **no code performs it**. ⚑ Consequences: WIRE-1 §4's *"already-committed recommendation → 409"* is **UNENFORCED**; the same `recommendation_id` can be committed **repeatedly**, writing a **duplicate `AuditRecord` each time**; and a committed case still reports `status: "ready"` on R4 **forever**. Declared at `backend/app/routes/not_wired.py:209`. | Deliberately **not** fixed in the wiring pass (Q6d-ii) **even though U24 was already reopened twice** — the fix straddles the **commit boundary (COMMITBOUND-1)**, sits outside the frozen service's transaction, and must not be folded into a wiring pass as a convenience. A route-level pre-check was **rejected** as duplicating enforcement. | U24 + `audit-store`, **needing its own commit-boundary review** | **⛔ THE MOST SERIOUS OPEN ITEM.** Non-blocking for the wiring's correctness, but **double-commit is a genuine BFSI-relevant defect** and must be treated as such. |
| 20 | **`PENDING-TABLES-NO-EXPLICIT-GRANTS`** | U24's `0001_case_lifecycle.sql` creates `pending_application`/`pending_recommendation` **without granting any audit role on them** — they are **owner-only by default**. That is *why* the case store binds to the owner (`DATABASE_URL`) engine rather than the audit reader. Declared at `backend/app/dependencies.py:22`. | Whether this is **deliberate least privilege** or an **unreviewed gap** in U24's migration is **explicitly NOT decided** (Q8a) — the wiring pass recorded it as an open observation rather than silently ruling either way, since inventing a grant is a security decision the composition root must not make alone. | U24 / a security review | **Non-blocking** — the chosen engine binding works and is least-privilege-consistent. Recorded for review. |

> ⚑ **ITEM #2 IS DISCHARGED — the only discharge in the register's history.**
> **#2 `R2–R5 unwired`** was closed by the **Scope B in-place composition-root wiring pass** (2026-07-20). All seven
> WIRE-1 routes are now live. Its row above is **preserved verbatim as the historical record** of why it was opened;
> it no longer describes the system. ⚑ **Its blocking claim — *"BLOCKING for the end-to-end demo path"* — is now
> only PARTLY discharged**: the routes are wired and serve real data, but per **Q11-A** the honest claim is
> *"the API layer is exercisable **after running the seed script**"*, **not** a self-contained end-to-end HTTP
> journey (that needs an ingestion route, requiring both a WIRE-1 amendment and a frozen-test edit) and **not** a
> clickable UI. See `guide-docs/build/composition-root/scope-b-wiring-summary.md`.
>
> **Net open count: 19 open + 1 discharged = 20 tracked.**

Items **9, 10, 11** are additionally realized **in code** as `backend/llm_judge/engine.py::DEFERRED_REGISTER`, each
carrying `discharged=False` and machine-checked by U22's suite.

Items **13–20** are likewise realized **in code** as named declarations at the exact locations cited above — each
sits in the docstring of the module whose behaviour it qualifies, so a maintainer meets the disclosure **where the
consequence lives** rather than only in this report.

---

## 6. Known limitations of the current build — stated plainly

> ⚑ **6.1 IS SUPERSEDED — 2026-07-21.** The paragraph below described the build **before** the Scope B wiring pass.
> **R2–R5 are no longer `501` markers; all seven WIRE-1 routes are live** and serve real data from U24's pending
> store. It is **preserved verbatim** as the historical statement of the gap that motivated Scope B. **For the current
> position, read 6.1-REVISED immediately after it.**

**[Historical, superseded]** *6.1 The core demo path is not runnable end-to-end. Only **R1 `GET /session`**, **R6 `GET
/decisions`** and **R7 `GET /decisions/{id}`** are live. **R2–R5 are registered as `501 not_implemented`** — verified on
disk in `backend/app/main.py`, which documents each: no pending-application store (R2), no pre-commit profile store
(R3), no store and no drafting trigger (R4), and only a test-fake context provider (R5). **A user cannot today submit an
application, have a memo drafted, and commit a decision through the running system.** The units that would each do this
work are built and unit-tested; they are not wired together behind live routes.*

**6.1-REVISED — the current position (2026-07-21).** **All seven WIRE-1 routes are live.** `case-lifecycle` (U24)
supplied the pending-application store, and the Scope B wiring pass wired R2–R5 **in place**, requiring **two
explicitly-authorized reopenings of U24** (`list_application_ids()`, because no enumeration primitive existed; and
`memo_from_canonical()`, because no memo rehydration existed anywhere in the build).

⚑ **The honest scope claim is deliberately narrower than "end-to-end"**:

> **"The API layer is exercisable after running the seed script."**

* ✅ R2–R7 serve **real data** over HTTP once `backend/scripts/seed_demo_cases.py` has run.
* ❌ **Not** a self-contained HTTP journey — WIRE-1 pins exactly seven routes and contains **no ingestion route**;
  adding one needs **both** a WIRE-1 amendment **and** an edit to U23's frozen test. Ingestion is therefore
  out-of-band, in the seed script.
* ❌ **Not** a clickable browser UI — the frontend was untouched (Q10-A) and remains not browser-runnable.
* ⚠️ **Seeded memo prose is SYNTHETIC** — a deterministic offline double, **not a real model call**, because **no
  production `LLMClient` exists** (register **#18**). No genuine LLM-drafted memo can be produced today.
* ⛔ **Double-commit is possible** — register **#19**; nothing performs the `drafted → committed` transition.

Full disclosure: **`guide-docs/build/composition-root/scope-b-wiring-summary.md`**.

**6.2 tier-B has never run, so two headline quality gates are unverified against real data.** Every unit completed at
tier-U against seeded fixtures. Consequently: the **≥4/5 LLM-as-judge groundedness gate (AC-6)** has **never been evaluated
over real drafted memos**, and the **synthetic corpus itself has never been generated**. The **≥90% code-coverage gate
(QA-6) IS genuinely verified** — it is measured on every run and currently holds at **99.86%** — but coverage is a
code-level measure and should not be read as evidence about model output quality. *(Note: the brief for this report paired
"≥90%" with tier-B; on disk these are separable — coverage is verified, the ≥4/5 judge gate is not. Recorded in §7.2.)*

**6.3 QA-4's few-shot anchoring is only half-realized.** `llm-judge` delivers the **scoring** half — an
`anchoring_consistency` rubric dimension with paired close/divergent fixtures. The **generation** half — anchoring the memo
at draft time via exemplars — **is not implemented anywhere in the build**, and cannot be without editing a frozen P1 unit.
It is disclosed by name rather than silently dropped.

**6.4 An honest note on what the ANCHOR-1 tests prove.** Because the tier-U rubric engine is an offline fake returning
fixture-**declared** scores, U22's anchoring tests prove the **paired-fixture plumbing and the unsplittable-pair
safeguard** — not that a real judge scores divergence lower. That narrowing is recorded as a first-class part of the
pattern, and real-shape discrimination is a named discharge criterion of #9.

---

## 7. Discrepancies found on disk — flagged as requested

**7.1 `document-sanitizer` (U2) has no `guide-docs/build/` directory of its own — and this is correct, not an omission.**
The `build/` tree contains **22 unit directories for 23 units**. U2 was **co-built inside `intake` (U1)**: its code lives
at `backend/intake/sanitizer/` (`normalizer.py`, `pattern_registry.py`, `sanitizer.py`, `report_channel.py`), and
`intake`'s code summary is titled **"Code Summary — `intake` + `document-sanitizer`"**. `guide-state.md` records it
verbatim as *"document-sanitizer (co-built in intake)"*. **No contradiction** — recorded here only because the directory
count would otherwise look like a missing unit.

**7.2 One framing correction to the report brief.** The brief stated that tier-B never running leaves *"the ≥90%/≥4/5
quality gates unverified against the real corpus."* On disk these two are **separable**: the **≥90% coverage gate is
verified and currently holds at 99.86%** (it does not depend on tier-B at all), while the **≥4/5 judge gate is genuinely
unverified**. Corrected in §6.2 rather than restated.

**7.3 Nothing else contradicted the build record.** Specifically re-verified for this report: the backend suite
(**1308 / 31 / 5** — matches), the frontend suite (**682 passed / 137 files** — live run matches the recorded figure
exactly), the **three** `infrastructure-design/` directories, R2–R5's `501` status, all **12** register item names present
in both `audit.md` and `guide-state.md`, and the 23-unit list in `unit-of-work.md`.

> ⚑ **7.3 is a DATED VERIFICATION RECORD, left unaltered.** Every figure above was true **when this report was
> written**, and rewriting a verification statement after the fact would destroy its value as evidence. Three of its
> facts have since changed and are superseded elsewhere in this document, **not** by editing the record:
> * backend suite **1308 / 31 / 5** → **1492 / 37 / 5** (live run 2026-07-21; the 5 `audit_store` Docker errors
>   **unchanged**; zero regression) — see `testresults.txt`
> * **R2–R5's `501` status** → all seven routes **live** — see **6.1-REVISED**
> * **12 register items** → **20** — see the **§5 fold note**
>
> The frontend figure (**682 / 137**) is **not** restated as current: the frontend was untouched and **not re-run**.

---

## 8. Categories of follow-on work available

**Named, not recommended. Nothing here is prioritised, sequenced, or implied to be next — and several require an
authorization decision that is the user's alone.**

**(a) Completing the composition root's remaining route wiring** — R2–R5, and with them the end-to-end demo path (§6.1).
Touches the currently **closed** composition root, and relates to the open Q1-B divergence (#1).

**(b) Authorizing and running tier-B** — generating the real 300+ synthetic corpus and running the quality gates against
it. Prerequisite for discharging #10, and the only route to verifying AC-6 against real memos.

**(c) Discharging the named technical deferrals** — `OBS-SINK-DEFERRED` (#7, the live sink code attachment),
`DEPLOY-MIGRATE-DEFERRED` (#8, the migration CLI entrypoint), `PROMPTFOO-CLI-DEFERRED` (#9, pinning the Node CLI +
telemetry opt-out + binding the adapter), `MCP-TRANSPORT-DEFERRED` (#6). Each has its own owner and, for #9, five
explicitly recorded discharge criteria. **#10 depends on #9** (one-way).

**(d) The one item requiring a frozen-P1 exception** — `FEWSHOT-ANCHOR-UNIMPLEMENTED` (#11). Implementing it means editing
`memo-agent-core`'s `PromptBuilder`, which would be the **first frozen-P1 edit in the build** and needs its own separate,
deliberate authorization decision.

**(e) Housekeeping** — the `testresults.txt` append-vs-overwrite question (#12) and assigning an owner to
`OUTLIER-IN-PROSE` (#5), which remains the only register item with **no owner named**.

---

*End of report. This document is a synthesis only — no unit was started, no frozen artifact was modified, no deferral was
discharged, and tier-B remains unauthorized.*

---

# ⚑ REGISTER UPDATE — 2026-07-21 · item #19 NARROWED · new item #21 opened

**This section supersedes §5's row for #19. That row is preserved verbatim above as the historical record of the
defect as first disclosed; it no longer describes the system.**

## #19 `COMMITTED-TRANSITION-NEVER-PERFORMED` — **NARROWED, NOT DISCHARGED**

Fixed by **U24's THIRD authorized reopening** (`fix-register-19-code-gen-plan.md`), the register's first item to be
remediated rather than merely re-disclosed. The commit is now **two-step**: a compare-and-swap claim
(`drafted → committing`) **before** the frozen `DecisionCommitService.commit()`, and a finalize
(`committing → committed`) **after** it returns; every rejection **releases** the claim.

**What is now genuinely true** — ✅ **duplicate `AuditRecord`s are ELIMINATED**, by a Postgres row-level write lock,
proven at tier-I with two real concurrent connections (not a race narrowed by timing) · ✅ **WIRE-1 §4's
already-committed 409 is genuinely enforced, including under concurrent access** · ✅ a committed case no longer
reports `status: "ready"` on R4 · ✅ an ordinary rejection (blank-reason override, unauthorized caller) leaves the
case **re-committable**.

**⛔ Why it is NOT marked discharged.** The fix does **not** achieve cross-store atomicity, and no wording will make
it so: `audit_record` and the pending store are **two transactional boundaries on two engines**, and merging them
would require editing a frozen unit. The surviving window is real and is tracked as **#21**.

## #21 `COMMITTING-CRASH-WINDOW` — **NEW**

| | |
|---|---|
| **What it is** | A crash **between** the frozen service's audit write and U24's `finalize_commit` leaves the case in `committing`: the `AuditRecord` exists, the case does not yet show `committed`. |
| **Why it exists** | The direct consequence of two separately-owned transactional boundaries. `commit()` has **no post-write hook**, so the finalize cannot be inside its transaction. Eliminating this window entirely would need 2PC or an outbox — both requiring a frozen-unit edit. |
| **Why this shape was CHOSEN** | The alternative (claim *after* the write) yields the **worse** residual: a case marked `committed` with **no audit record**, and since `COMMITTED` is terminal, a **lost, un-retryable human decision** — which cuts directly against the brief's full-auditability invariant. `committing` is **explicit, non-terminal, detectable and reversible**. |
| **Mitigation, shipped** | `backend/scripts/reconcile_committing_cases.py` — **read-only**. Lists stranded cases and names the determinate action: `recommendation_id` present in `audit_record` → advance to `committed`; absent → revert to `drafted` for retry. It **performs neither** — that is an operator decision. |
| **Location** | `backend/case_lifecycle/states.py` · `backend/app/routes/not_wired.py` (R5's docstring) |
| **Owner** | composition / U24 — a future 2PC-or-outbox change, which would need a frozen-unit authorization |
| **Blocking?** | **Non-blocking.** Crash-only, narrow, detectable and reconcilable — replacing an unbounded, always-reachable defect. |

**Also updated**: **#14 `MEMOVIEW-FAILED-STATE-UNMODELLED` WIDENED** — `COMMITTING` is a **second** internal state
with no wire representation, projecting to `"pending"`, so a mid-commit case is indistinguishable at the wire from an
undrafted one. Disclosed, **not** silently absorbed; WIRE-1's text **not amended**; **no discharge claimed**.

**Register now stands at 21 tracked items: 19 open · 1 discharged (#2, partly) · 1 narrowed (#19).**

---

# ⚑ REGISTER UPDATE — 2026-07-21T17:04:30Z · item #18 NARROWED · new item #22 opened

**This section supersedes §5's row for #18. That row is preserved verbatim above as the historical record of the
defect as first disclosed; it no longer describes the system.**

Fixed by `fix-register-18-code-gen-plan.md` — the register's **second** item remediated rather than
re-disclosed (after #19), and the **first production LLM path in the entire build**. A new composition-root
module `backend/app/llm_client.py` supplies the two-piece shape (Q9-A): a flag-free, purely-injected
`CappedGeminiClient` **wrapper** + a guarded `build_gemini_client` **factory**. `requirements.txt` now declares
`google-genai>=1.0.0` (legacy `google-generativeai` removed). The seed script gains an opt-in `--real-llm` path,
gated independently by `ALLOW_REAL_LLM_CALLS=true`; the offline double stays the byte-for-byte default.

## #18 `NO-PRODUCTION-LLMCLIENT` (B4) — **NARROWED, NOT DISCHARGED**

**What is now genuinely true** — ✅ **a production `LLMClient` implementation EXISTS** for the first time; the
chain `CaseSeams.draft_memo → LangGraphOrchestrator → GeminiAdapter → CappedGeminiClient` is **complete** ·
✅ the manifest is **self-consistent** (`google-genai` declared, imports match, legacy SDK gone) · ✅ **spend
cannot occur by accident** — two independent gates (`--real-llm` **and** `ALLOW_REAL_LLM_CALLS=true`) plus a
**hard call cap that counts retries**, proven by the tier-U tooth test (real orchestrator + real adapter over the
wrapper, `call_count > 1` for one draft; cap fires mid-retry) · ✅ **the offline path is untouched and remains the
default** — the full suite runs with **no key, no network, no SDK installed, and no spend flag set** (1549 passed
/ 40 skipped / 5 errors, `ALLOW_REAL_LLM_CALLS` unset; +17 offline tests, zero regression).

**⛔ Why it is NOT marked discharged.** Q8b instructs the outcome be decided **on evidence actually produced**,
and two things fall short of *"a genuine LLM-drafted memo can be produced by this system"*:
1. **The manual real-API verification has NOT been run end-to-end.** No live `GEMINI_API_KEY`, no network, and
   `google-genai` is not installed in this environment. The real path is **unit-proven and structurally complete**,
   but **no real memo has actually been produced and confirmed**. The procedure is documented
   (`guide-docs/build/composition-root/real-llm-verification.md`) for a human to run out of band.
2. **The pinned model id `gemini-2.5-flash-001` is not confirmed to resolve** against the live API (it is a
   deliberate non-floating pin per Q6; the verification doc says to confirm/adjust it against `models.list`,
   never falling back to the floating alias).

So the item is **genuinely improved** — the blocker *"no production `LLMClient` exists"* is resolved, and a real
memo is producible **in principle** via the opt-in path — but **claiming DISCHARGED would overclaim** exactly the
end-to-end confirmation that has not been performed. **NARROWED**, on the #19 precedent, is the honest outcome.

## #22 `MEMO-PROSE-NOT-BIT-REPRODUCIBLE` (#18a) — **NEW**

| | |
|---|---|
| **What it is** | AC-1 requires *"identical input → identical output, 100%"*, with `temperature=0` as the stated mechanism. `temperature=0` makes sampling **greedy**, which is **not** the same as bit-reproducible: outputs can still differ across provider-side model updates, serving-stack non-determinism, and tokenizer/safety changes. |
| **What is protected regardless** | The **recommendation** is produced by the deterministic rules engine, **never** by the LLM (CON-BR2-TYPE — `MemoDraftOutput` carries only `narrative_prose` + `cited_rule_ids`, so the model **structurally cannot** change the recommendation). AC-1's 100% claim **holds for the DECISION path**; it is **not claimable bit-exactly for MEMO PROSE** under a real LLM, even at `temperature=0`. |
| **Mitigation, shipped** | The real path pins a **non-floating** model id (`REAL_MODEL_ID`, not the `gemini-2.5-flash` alias) and stamps `model_version = <model-id>+google-genai-<sdk-version>` (Q6b) so drift is bounded and any replay is falsifiable. **Narrows** the window; does **not** close it. |
| **Location** | `backend/scripts/seed_demo_cases.py` (REAL_MODEL_ID) · `real-llm-verification.md` |
| **Owner** | composition / a future WIRE-1-or-AC-1 clarification |
| **Blocking?** | **Non-blocking.** Prose-level only; the decision path is bit-reproducible by construction. |

**D1 disclosed (not requiring sign-off)**: `corpus_generator/build.py` becomes importable **in principle** by the
manifest fix, but stays **unrun, uncollected, coverage-omitted, `--model-id` default unchanged** — and
`google-genai` is not installed here, so it remains non-importable in this environment regardless. **Tier-B stays
unauthorized.**

**Register now stands at 22 tracked items: 19 open · 1 discharged (#2, partly) · 2 narrowed (#18, #19).**

---

# ⚑ REGISTER UPDATE — 2026-07-22T17:19:09Z · item #20 DISCHARGED (the register's FIRST clean full discharge)

**This section supersedes §5's row for #20 (and the Scope-B summary's row #20). Those rows are
preserved verbatim above as the historical record of the observation as first disclosed; they no
longer describe the system.**

Resolved by `fix-register-20-plan.md` (Q1–Q4 answered) — the **third** item taken up after Scope B
closed (after #19 and #18, both NARROWED), and the **FIRST DISCHARGED CLEANLY** rather than narrowed
or merely re-disclosed. This is a **documentation/disclosure resolution: no code behaviour changed,
no migration was written, no unit was reopened.**

## #20 `PENDING-TABLES-NO-EXPLICIT-GRANTS` — **DISCHARGED**

**The core rationale, ratified (Q1(a)) — CORE-RATIONALE-20, identical across this report,
`guide-state.md`, `audit.md`, and the two in-code notes:**

> Owner-only access to the pending tables (`pending_application`, `pending_recommendation`) is
> **deliberate least privilege, not an unreviewed gap.** The pending tables hold pre-commit,
> not-yet-audited drafts. `audit_reader` is scoped to the committed audit trail (R6/R7) and gains
> nothing legitimate from reading drafts — doing so would broaden its surface against SEC-4's
> least-privilege intent. `audit_writer` has exactly one caller, the frozen `DecisionCommitService`,
> which receives fully-assembled `CommitContext` inputs from the owner-engine provider and never
> touches pending state directly. No wired caller in R2–R5 reaches the pending tables through a
> non-owner engine. This is the same owner-only posture the build already applies to `app_user`, and
> it is enforced by the passing tier-U test
> `test_migscope.py::test_u24s_migration_grants_to_no_u15_role` (NFR-CASE-MIGSCOPE-1 / BR-CASE-12).
> No new test and no migration are required; the posture was already correct and asserted. #20's only
> genuine defect was that this correctness had been recorded under a *migration-self-containment*
> rationale (CASE-Req-Fold-1) and never as an affirmative *access-model security* judgment — now
> stated.

**Outcome shape — distinct from everything else in the register (Q4 Outcome A):** #20 is the
register's **first clean full discharge.** Unlike **#2** (discharged only *partly* — routes wired but
not an end-to-end journey), and unlike **#18 / #19** (each NARROWED, each leaving a real residual
tracked as a *new* item — #22, #21), **#20 leaves NO residual**: the posture was already behaviourally
correct and tested; its only defect was that the *security* rationale had never been stated as such.
Writing it down removes the defect entirely. **No new register item is opened.**

**What was actually changed — two docstring-only edits, zero behaviour:**
- `backend/app/dependencies.py` header note: *"OPEN OBSERVATION … NOT decided here"* → *"RESOLVED
  (register #20, DISCHARGED) … deliberately owner-only least privilege."*
- `backend/scripts/reconcile_committing_cases.py:44`: *"register #20, left open and undecided here"* →
  *"register #20, RESOLVED as deliberate owner-only least privilege."*

Both are pure docstring/comment changes — docstring-stripped by the `backend/app/` AST scanners
(`test_no_write_route.py`), or outside every structural-scan root (`backend/scripts/`), and touching
none of the four raw-source-scanned substrings. **Full backend suite byte-for-byte identical to the
pre-#20 baseline: 1549 passed / 0 failed / 40 skipped / 5 errors (same names) / 99.87% coverage.** No
migration, no new test (the posture was already asserted by `test_migscope.py`). Line 133's
`# owner — register #20` pointer stays as-is — it remains accurate regardless of #20's status.

**⚑ Disclosed process finding (recorded, not smoothed over — the #19-vacuous-fixture / #18-Q9-collision
precedent):** the scoping plan's ground-truth pass (§1) identified **only one** in-code #20 reference
(`dependencies.py:22`) and **missed a second** (`reconcile_committing_cases.py:44`), which asserted the
same *"undecided"* claim and would have **contradicted the closure the moment it landed**. It was
caught **only by the mandatory ambiguity-check's directed check (ii)**, surfaced-and-stopped on, and
resolved by the user's decision to update both files. Executed without the ambiguity-check, the
codebase would have shipped a self-contradiction. **Recorded as evidence the ambiguity-check earns its
place.**

**Register now stands at 22 tracked items: 18 open · 2 discharged (#2 partly, #20 fully) · 2 narrowed
(#18, #19).** ⚑ **Count reconciliation:** the pre-#20 figure was *"19 open"*; #20 was one of those 19,
so discharging it drops open to **18** (18 + 2 + 2 = 22), preserving the tracked total. (The closing
instruction wrote *"19 open"* alongside *"#20 fully-discharged"*, which double-counts #20 to 23;
corrected here to **18 open**.)

**HOLDS upheld:** U15's frozen `0001_initial_schema.sql` / `0002_grants.sql` untouched · U24's
checksum-locked `0001_case_lifecycle.sql` untouched · **no new migration written** · no other
frozen-23 internal edited · WIRE-1 text unamended · `not_wired.py` not renamed · U23's frozen test
unedited · `audit_store` Docker-guard gap untouched (5 errors stay exactly 5) · tier-B not authorized
· no new route under `backend/app/routes/`.

---

# ⚑ REGISTER UPDATE — 2026-07-22T18:24:22Z · item #8 NARROWED (entrypoint built + tier-U-proven; tier-I written but not executed here)

**This section supersedes §5's row for #8 and §8(c)'s mention of it. Those are preserved verbatim
above as the historical record of the gap as first disclosed; they no longer describe the system.**

Resolved-in-code by `fix-register-8-code-gen-plan.md` (Q1–Q6 answered; ambiguity-check clean with one
surfaced adjacent finding folded in). The **fourth** item taken up after Scope B closed (after #19
NARROWED, #18 NARROWED, #20 DISCHARGED), and the register's **third NARROWED** outcome.

## #8 `DEPLOY-MIGRATE-DEFERRED` — **NARROWED, NOT DISCHARGED**

**The missing artifact now EXISTS.** `backend/scripts/run_migrations.py` is the runnable deploy-time CLI
entrypoint `render.yaml`'s `preDeployCommand` invokes. It is a **cross-unit orchestrator** (Q1-B —
deliberately in `backend/scripts/`, not inside frozen `backend/database/`, so no frozen unit's package
imports a later one): built from `get_settings().DATABASE_URL` (the owner engine), it applies **both**
forward-only sequences in one invocation — `database` (U15) via a plain `MigrationRunner`, then
`case_lifecycle` (U24) via `apply_case_migrations()` (which runs the production collision guard FIRST —
C-C, never a bare runner on U24's dir). **Hardcoded, explicitly named** (Q3-A — no dynamic discovery, which
C-C would make hazardous). **Idempotent** by construction (skip-if-applied, inherited from the frozen
runners) and **fail-loud** (Q4-A — any error is a non-zero exit that blocks the release step before
traffic; rendered SQL is never logged, SEC-3).

**What is now genuinely true** — ✅ a single command applies both migration sequences in the correct order,
guard-first · ✅ `render.yaml`'s `preDeployCommand` names an entrypoint that **exists on disk** for the
first time (deploy-config's committed config is now correct) · ✅ the orchestration contract is
**tier-U-proven** by 7 tests (engine-from-settings; U15-before-U24; U24-via-`apply_case_migrations`-exactly-
once; **MigrationRunner constructor-arg spy proving `CASE_MIGRATIONS_DIR` is never handed to the wrong
runner**; fail-loud propagation AND `engine.dispose()`-via-`finally` on **each** half separately; no rendered
SQL in output) · ✅ a **tier-I integration test is written** (both sequences materialize on a fresh
`postgres:16`; the `applied_migrations` table records all three files; a second run applies nothing) using
the `_docker_available()` **ping-guard verbatim**, so Docker-absence is a **clean SKIP, never a sixth error**
(observed: 3 skipped, errors stay exactly 5).

**⛔ Why it is NOT marked DISCHARGED.** Per the plan's §7 evidentiary rule (and on the #18 precedent): the
tier-I proof — the only thing that shows the entrypoint applies a real schema against a real database — has
**NOT been executed** in this environment, which has **no Docker**; it **skipped**. No CI run and no local
Docker run has confirmed it green anywhere observable to this pass. And the **actual Render release step has
not been run end-to-end** (no live deploy). The entrypoint is **structurally complete and tier-U-proven**,
and a correct migration IS producible **in principle** — but claiming DISCHARGED would overclaim exactly the
real-database confirmation that has not been performed. **NARROWED** is the honest outcome; the evidentiary
bar is "confirmed to run against a real database," not code quality.

**The residual (tracked on #8 itself, no new item opened — the #18-manual-verification precedent):** the
tier-I integration test is **written but unexecuted here** (CI-gated), and the **live Render release step is
not run**. It discharges to fully DISCHARGED the moment the tier-I test is confirmed green under Docker (CI,
which the suite mandates integration tests run in, or a local Docker run) — no code change required, only
execution-confirmation. Because the residual is a not-yet-executed *proof of already-written code* (not a
missing capability), it is recorded on #8 rather than spawned as a new register item.

**Adjacent doc-consistency finding, surfaced and resolved (the #20 directed-check precedent):** pointing
`preDeployCommand` at the now-existing entrypoint would have left two prose locations asserting the
opposite. Both updated as part of this pass: `render.yaml`'s own comment (within the Q5 edit), and —
**explicitly approved at the plan gate as beyond the literal Q5 answer** — `deploy/README.md`'s MIGRATION
section ("Until it exists…" → the entrypoint now exists). Both test-neutral (`test_doc.py`'s five marker
tokens intact; no test asserts either prose). The historical `database` Infra-Design §3.4 and §5 #8 row are
**superseded here, not rewritten in place.**

**Verification — full backend suite, live, EXACT match to the plan's advance predictions:** **1556 passed /
0 failed / 43 skipped / 5 errors (same `audit_store` Docker-absence names) / 99.87% coverage.** Δ from the
pre-#8 baseline: **+7 passed** (tier-U), **+3 skipped** (tier-I, Docker-absent), **errors unchanged at 5**,
**coverage unchanged** (`backend/scripts` is not a `--cov` target, so `run_migrations.py` is
coverage-invisible — test-covered by tier-U + tier-I, never counted in the 99.87%; stated honestly, not read
as "covered").

**Register now stands at 22 tracked — 17 open · 2 discharged (#2 partly, #20 fully) · 3 narrowed (#8, #18,
#19).** ⚑ Count reconciliation: #8 was one of the prior 18 open, so narrowing it drops open **18 → 17** and
raises narrowed **2 → 3** (17 + 2 + 3 = 22, tracked total preserved); no new item opened.

**HOLDS upheld:** U15's `0001_initial_schema.sql`/`0002_grants.sql` untouched · U24's checksum-locked
`0001_case_lifecycle.sql` untouched · frozen `MigrationRunner`/`verify_checksums` **called, never edited** ·
no other frozen-23 unit internal or **test** edited (U23's `deploy_config/tests/*` untouched — 41 pass; the
edits are to `render.yaml` config + `deploy/README.md` doc, both non-frozen, distinct from the tests) ·
WIRE-1 text unamended · `not_wired.py` not renamed · `audit_store` Docker-guard gap untouched (5 errors stay
exactly 5) · tier-B not authorized · no new route under `backend/app/routes/`.

---

# ⚑ REGISTER UPDATE — 2026-07-23 · item #3 NARROWED · new item #23 opened · tier-B **Stage 1** closed

**This section supersedes §5's row for #3 and §8(b)'s mention of it. Those are preserved verbatim above as the
historical record of the gap as first disclosed; they no longer describe the system.**

Resolved-in-part by `tier-b-authorization-plan.md` (Q1–Q12 answered; Q2/Q8/Q9 deferred) and
`tier-b-stage1-code-gen-plan.md` (Steps 0–6 + revised close-out). The **fifth** item taken up after Scope B closed
(after #19 NARROWED, #18 NARROWED, #20 DISCHARGED, #8 NARROWED), the register's **fourth NARROWED** outcome, and the
**first pass to address five register items at once** (#3, #9, #10, #18, #22).

## #3 `tier-B corpus run` — **NARROWED, NOT DISCHARGED**

**A 300-profile corpus now EXISTS** at `corpus/` — the first in the build's history — and **the four blocking
quality gates have been run against it**, which had also never happened (a repo-wide scan confirmed U13's gates had
**no production caller** anywhere).

**What is now genuinely true** — ✅ `corpus/profiles.json` + `corpus/manifest.json` are committed, with **300
profiles** at **120/105/75 = 0.4000/0.3500/0.2500**, i.e. **band delta 0.00pp** on all three classes against the
±3pp tolerance, and **all 8 DATA-2 edge cases present** · ✅ **DET-1 proven at full scale** — three independent runs
produced the identical `content_hash 57821891ba502e2e213c096bf3b0f5d3ab9e60107b13b687753b437bb7290525` · ✅ the
**±3pp band and the 8-edge checklist were satisfied by an actual run for the first time** (they had only ever been
satisfied by `SkewAudit` unit tests over *synthetic* counts — the N=300 pipeline had **never been run, even
offline**) · ✅ **AC-3 bias-swap `delta_count` 0**, **AC-1 reproducibility 100.0%** (300 × 10 runs), **AC-4 rule
coverage 100.0%**, coverage-wiring pass — all four **blocking** gates green over real profiles · ✅ a **guarded**
corpus entrypoint exists (`backend/scripts/build_corpus.py`) that routes real spend exclusively through #18's
`build_gemini_client`, closing the gap where U14's `build.py` was reachable with nothing but a key.

### ⛔ Why it is NOT DISCHARGED — decided on the register's ACTUAL wording

#3's recorded subject is *"the **real** 300+ synthetic corpus has **never been generated or run against**"*, and
its blocking claim is *"**blocking** for real-corpus **quality verification**."* Measured against that text, **two
distinct residuals survive**:

1. **The document prose is NOT real.** The committed corpus carries **placeholder, offline-generated
   `documents_text`**, stamped `model_version = OFFLINE-DOUBLE-NOT-A-REAL-LLM`. The **profiles** are genuine,
   seeded, deterministic and engine-labeled; the **prose** is not model-authored. So *"the real corpus"* is
   **half-satisfied**: real profiles, placeholder prose.
2. **AC-6 remains completely unaddressed.** The ≥4/5 LLM-as-judge groundedness gate has still **never been
   evaluated**, and *"real-corpus quality verification"* in #3's blocking clause spans it. Structurally this is
   **#10 `JUDGE-EVAL-DEFERRED`**'s subject, gated one-way behind **#9 `PROMPTFOO-CLI-DEFERRED`** — **both untouched
   by this pass, both `discharged=False`.**

**The real-prose run was DELIBERATELY DEFERRED, not skipped by oversight.** Step 9 of the code-gen plan was
authorized and ready; it was **not run** on evidence produced at Step 6 — see the boxed finding below.

### ⚑ THE DECISIVE FINDING — why the spend was deferred

> **All four blocking gates consume only `CorpusLoader.profiles(records)` — i.e. `record.profile`. NO gate reads
> `documents_text`.** Therefore the gate results above are **identical to what a real-prose corpus would produce**;
> real prose would not change a single one of them.
>
> The prose consequently has **no consumer** until tier-B **Stage 2/3** (memo drafting + judge evaluation) is
> authorized — which it is **not**. Generating it now would pay for an artifact that sits unused and would likely
> need **regenerating against a then-current model** anyway (**register #22**'s drift concern applied forward).
> Real-prose generation is deferred so that **the spend and the consumption happen together**.

**⚑ NO API CALL WAS MADE AND NO MONEY WAS SPENT AT ANY POINT IN THIS PASS.**

### ⛔ Scope of the four gate reports — stated plainly, not to be over-read

`corpus/gate-reports/` verifies the **DECISION PATH over real applicant profiles**. It is **NOT** a claim about
**document prose or memo quality** — no gate reads `documents_text` and no gate involves an LLM. In particular it
is **not** evidence about **AC-6**, which remains entirely unverified.

### ⚑ Why committing this artifact is EVIDENTIARY, not Q7(a)'s unfalsifiability argument

Q7(a) argued for committing the corpus because a **real-prose** corpus is *not* bit-identically regenerable, so an
uncommitted one would effectively cease to exist on a clean checkout and every downstream claim would become
unfalsifiable. **That argument does not apply to this artifact and is not claimed for it**: this corpus **is**
deterministically regenerable (proven — three runs, one hash), reproducible by anyone with
`python -m backend.scripts.build_corpus --out corpus`. It is committed as **evidentiary record-keeping** — the
specific artifact against which AC-1/AC-3/AC-4 were measured. Q7(a)'s reasoning stands, unchanged, for the
real-prose corpus it was written about.

### ⚑ Disclosed note — AC-4's "100%" is 100% of ELEVEN rules

`rule-coverage.json` reports `total_rules: 11`. The rulebook at `1.0.0` contains eleven rules (`AGE-BAND-1`,
`BMI-OBESE-1`, `DTI-CEIL-1`, `INCM-CEIL-1`, `SMOKE-STATUS-1`, `OCC-LOWRISK-1`, `MED-HEALTH-1`, `DOCS-COMPLETE-1`,
`IRDAI-INCOME-FLOOR-1`, `IRDAI-COVER-POSITIVE-1`, `IRDAI-EMP-SALARIED-1`). **`PROJECT-BRIEF.md` §3 Component 2
specifies "25-40 underwriting rules."** So **AC-4's 100% is 100% of the 11 rules that exist**, not of the 25-40
originally scoped. The gate is honest about what it measures; the gap is between the rulebook (**frozen U3**) and
the brief, **predates tier-B entirely**, and is **out of scope for correction here**. Recorded so this figure is
never later misread.

## #23 `U22-DISCHARGE-UNRECORDABLE-IN-CODE` — **NEW**

| | |
|---|---|
| **What it is** | U22's `DEFERRED_REGISTER` carries `discharged: bool = False` on a **frozen** dataclass, and **three frozen tests hard-assert it stays False** — `test_governance.py::test_the_three_register_items_are_named_owner_attributed_and_undischarged`, `test_clidefer.py::test_the_cli_deferral_is_disclosed_with_its_five_discharge_criteria`, `test_clidefer.py::test_no_register_item_claims_discharge`. **U22's design supplies NO mechanism to flip the field.** |
| **Why it matters** | When #9 or #10 is eventually discharged on its merits, **that fact cannot be recorded in code** without editing three frozen U22 tests. Register edit + frozen-test relaxation are a **MATCHED PAIR** — neither half valid alone — structurally identical to **#13 `NOTWIRED-FILENAME-STALE`**. |
| **Why it is opened NOW** | The constraint is **real today**, independent of any discharge: it was discovered during this pass's ground-truth reconstruction, and leaving it undisclosed would mean a future pass rediscovering it mid-flight. Opened per the authorization plan's **Q11a(c)** — spawn a residual rather than overclaim (the #21/#22 precedent). |
| **Owner** | `llm-judge` (U22) + whoever discharges #9/#10, **as one authorized change** |
| **Blocking?** | **Non-blocking.** No behaviour depends on it. It is a **recording-fidelity** constraint that will bite exactly once, at the moment of a real discharge. |

## What Stage 1 did NOT establish — restated so nothing is over-read

* **AC-6 (≥4/5 LLM-as-judge)** — **completely unverified.** Untouched.
* **#9 `PROMPTFOO-CLI-DEFERRED`** and **#10 `JUDGE-EVAL-DEFERRED`** — **untouched**, both `discharged=False`. Q2 and
  Q8/Q9 were **explicitly deferred**, not answered.
* **#18** — **not discharged.** ⚑ And see the separate finding below, which **enlarges** its residual.
* **#22** — unaffected and **inherited**: a real-prose corpus would carry the same non-reproducibility, which is
  precisely why the deferred run is expected to produce a *different* `content_hash`.
* **Stages 2 and 3 remain NOT AUTHORIZED.**

## ⚑ SEPARATE FINDING, reported not fixed — `seed_demo_cases.py` raises on construction

Discovered incidentally at Step 4 and **deliberately not fixed** (the approved C7 scope was the line-97 docstring
only). `backend/scripts/seed_demo_cases.py:139` calls `RulebookLoader()` with **no argument**; the constructor
requires `rulebook_dir`. **Confirmed by direct execution** — both `RulebookLoader()` and `_SeedSeams()` raise
`TypeError`. No test constructs `_SeedSeams` or imports the module, so it was never caught.

**It bears on two existing claims** and needs a decision:
* **#2's partial discharge** — §6.1-REVISED's *"the API layer is exercisable **after running the seed script**"*
  **cannot have been verified by running the script.** (The seven WIRE-1 routes themselves are unaffected and
  independently tested; only the *seeding* step, and therefore the *"exercisable"* half, is in doubt.)
* **#18's residual** is **larger than recorded** — the `--real-llm` opt-in path is currently **unreachable**, so the
  documented `real-llm-verification.md` procedure would fail at step one. (`backend/app/llm_client.py` itself is
  correct and reachable — `build_corpus.py` constructs it successfully.)

Full write-up, with four decision options: **`guide-docs/build/composition-root/seed-script-defect-finding.md`**.

## Verification — full backend suite, live

**1571 passed / 0 failed / 43 skipped / 5 errors (same `audit_store` Docker-absence names) / 99.87% coverage** —
**EXACT match to the code-gen plan's advance predictions.** Δ from the pre-Stage-1 baseline (1556/0/43/5/99.87%,
re-confirmed live at Step 0): **+15 passed** (9 tier-U for `build_corpus.py`, 6 for `run_quality_gates.py`),
**skipped unchanged**, **errors unchanged at exactly 5**, **coverage unchanged** — `backend/scripts` is not a
`--cov` target, so both new modules are **coverage-invisible: test-covered, never counted** (stated honestly, not
read as "covered"). Adding the new top-level `corpus/` directory perturbed **nothing**, as the ambiguity-check
predicted.

**Register now stands at 23 tracked — 16 open · 2 discharged (#2 partly, #20 fully) · 4 narrowed (#3, #8, #18,
#19) · 1 new (#23).** ⚑ Count reconciliation: #3 was one of the prior 17 open, so narrowing it drops open **17 →
16** and raises narrowed **3 → 4**; **#23 is new and open**, so open goes **16 → 17** and the tracked total **22 →
23** (17 + 2 + 4 = 23).

**HOLDS upheld:** `corpus_generator/build.py` **completely untouched** (unused, coverage-omitted, superseded-not-
deleted) · `max_calls=20` default in `backend/app/llm_client.py` **unchanged** · **no frozen-23 unit internal or
test edited** · U22's `DEFERRED_REGISTER` and its three frozen tests untouched · WIRE-1 unamended · `not_wired.py`
not renamed · U23's frozen test unedited · `audit_store` Docker-guard gap untouched (**5 errors stay exactly 5**) ·
no new route under `backend/app/routes/` · **Stages 2 and 3 not authorized** · **#18's spend guardrails neither
weakened nor bypassed** · **no API call, no money spent, no real-prose corpus generated** · `seed_demo_cases.py`'s
constructor defect **reported, not fixed**.

---

# ⚑ CLAIM CORRECTION — 2026-07-23 · two recorded claims were OVERSTATED · seed-script defects fixed

**This section supersedes §6.1-REVISED's *"exercisable"* clause and the #18-NARROWED residual wording in the
2026-07-21T17:04:30Z update. Both are preserved verbatim above as the historical record; neither is edited in
place. Nothing else in either section changes.**

Two defects were found in `backend/scripts/seed_demo_cases.py` during tier-B Stage 1 and are **now fixed**; two
recorded claims that rested on that script were **overstated** and are corrected here.

## 1. The two defects (both confirmed by execution, both now fixed)

| # | Defect | Effect |
|---|---|---|
| **1** | `RulebookLoader()` called with **no argument** (`seed_demo_cases.py:154`); the constructor takes a **required** `rulebook_dir` | `_SeedSeams.__init__` raised **`TypeError` on its first statement**. `main()` **could not complete under any invocation.** |
| **2** | The offline double hardcoded `cited = "DTI-001" …`; **there is no rule `DTI-001` in this build** (the DTI rule is `DTI-CEIL-1`) | The condition was **always False**, so the double emitted an **empty** `<rule_id>`, U4's `CitationValidator` rejected it, the graph retried to `MEMO_CITATION_RETRY_CAP` and **flagged**. **Every seeded case would have landed in `FAILED`, never `drafted`.** |

⚑ **Defect 1 was hiding defect 2.** Fixing only the constructor would have produced a script that ran to
completion and seeded a database in which **nothing was exercisable** — and the failure would have been
**invisible at the wire**, because a `failed` case projects to `"pending"` on R4 (register **#14**) and
`ApplicationSummary` carries no status field at all (register **#16**).

⚑ **Root cause — the same for both**: an **untested, uncollected, coverage-invisible** module that had **never
been run to completion**. Neither defect is subtle; either would have been caught by one execution.

## 2. ⛔ CORRECTION 1 — §6.1-REVISED's *"exercisable"* claim

> **Recorded claim**: *"The API layer is exercisable after running the seed script."*
> (§6.1-REVISED, echoed in `guide-state.md`, `audit.md`, `scope-b-wiring-summary.md`.)

**That claim was overstated and cannot have been verified by running the script**, which raised `TypeError` before
seeding anything. **It was worse than merely unverified**: with defect 2 present it would have remained **false in
substance** even after defect 1 was fixed — only R2/R3/R6/R7 would have served anything, and R2/R3 would have
shown silently-failed cases.

**The corrected, current claim:**

> **The demo path is proven at tier-U to reach `drafted`, with R4 reporting `ready`. The seed script has NOT been
> confirmed to run end-to-end against a real Postgres — that verification remains outstanding.**

⚑ **What was never in doubt**: the **seven WIRE-1 routes themselves**. They are independently unit-tested and
their wiring is proven by U24's and the composition root's own suites. Only the **seeding step** — and therefore
the *"exercisable"* half of the claim — was affected.

## 3. ⛔ CORRECTION 2 — #18's residual wording

> **Recorded**: *"The manual real-API verification has **NOT been run** end-to-end."*

**Corrected to**: *"The manual real-API verification is **NOT CURRENTLY RUNNABLE**"* — the `--real-llm` opt-in path
constructs `_SeedSeams(real_client, …)` and therefore **raised before any model call**, so the documented procedure
in `real-llm-verification.md` **would have failed at step one** if attempted. Not merely *not yet done*: *not
possible*.

**With the fix, the path is reachable again** — but **#18 remains NARROWED**, unchanged. The real-API verification
is **still not run** (no live key, no network, `google-genai` not installed here), and this correction changes only
the accuracy of *why*, never the status.

⚑ **`backend/app/llm_client.py` itself was never implicated** — it is correct, has 17 passing tier-U tests, and
`build_corpus.py` constructs it through `build_gemini_client` successfully.

## 4. What the fix is, and — plainly — what it does NOT establish

**Changed** (all in `backend/scripts/`, non-frozen): the constructor call now passes `rulebook_dir()`; the offline
double **discovers** the rule id from the prompt rather than hardcoding one, so it **cannot drift out of step with
the rulebook again**; and a new `backend/scripts/tests/test_seed_demo_cases.py` adds **7 tier-U tests**.

**⚑ The test is the actual fix.** The load-bearing one —
`test_drafting_a_demo_case_produces_a_memo_rather_than_blocking` — **fails under either defect**: defect 1 makes it
raise, defect 2 makes drafting return `None`. `test_the_demo_path_reaches_drafted_and_r4_reports_ready` drives the
real `CasePipeline` over U24's `InMemoryCaseStore` and asserts `state == DRAFTED` and R4 `== "ready"`.

**⛔ PROVEN AT TIER-U ONLY. A real Postgres run has NOT confirmed this end-to-end.** There is no Docker and no live
database in this environment. Per the **#8 precedent**, that is recorded as an **outstanding residual** — built and
tier-U-proven, live confirmation pending — and is **not** folded into the "fixed" claim.

**Chain re-verified for a third defect** (traced, not assumed — since defect 2 was itself found hiding behind
defect 1): past `DRAFTED`, `case_to_memo_view_state` → `ready`; `MemoCanonAdapter.memo_from_canonical` rehydrates
(recommendation `REFER`, cited `['DTI-CEIL-1']`); `claim_for_commit` → **WON**, state → `committing`; a **second**
claim → **LOST** (register #19's duplicate guard genuinely working); `finalize_commit` → `committed`; R4 then
`pending` (register **#14**'s already-disclosed lossy projection, not a new defect). **No third logic defect.**
⚑ The frozen `DecisionCommitService.commit()` audit-write is **not** exercised by this trace — it needs the audit
repository and a DB, and is part of the same outstanding residual.

## 5. ⚑ THIRD FINDING — environmental, PRE-EXISTING, reported NOT fixed

On a Windows **cp1252** console the script's banner `print()` raises
**`UnicodeEncodeError: 'charmap' codec can't encode characters`** — the banners at lines 326/333 contain `—` and
`⚠️`. Confirmed: with `PYTHONIOENCODING=utf-8` the script proceeds correctly past the banner and fails only at
`get_settings()` for absent DB credentials, which is **correct fail-closed behaviour**.

* **Pre-existing** — the emoji banners were authored in register #18's pass, **not** by this fix.
* **Not a logic defect** and **not present on Linux/CI/Render**, which are UTF-8.
* **Out of the approved scope** for this pass (two one-line fixes + the test), so **reported, not fixed.**

## 6. Verification

**Full backend suite, live: 1578 passed / 0 failed / 43 skipped / 5 errors (same `audit_store` Docker-absence
names) / 99.87% coverage.** Δ from the post-Stage-1 baseline (1571/0/43/5/99.87%): **+7 passed**, skipped
unchanged, **errors exactly 5**, coverage unchanged — `backend/scripts` is not a `--cov` target, so the fixed
module stays **coverage-invisible: test-covered, never counted**.

**Register unchanged at 23 tracked** — 17 open · 2 discharged · 4 narrowed. **No register item is opened or closed
by this correction**: the two defects were **never register items** (they were undiscovered), and #2 and #18 keep
their existing statuses — only their *wording* is corrected. The outstanding real-Postgres verification is tracked
as a residual on the **#2 claim** above, on the #8 precedent.

**HOLDS upheld:** no frozen-23 unit internal or test edited (`RulebookLoader` is **called correctly, never
modified**) · U22's `DEFERRED_REGISTER` and its three frozen tests untouched · WIRE-1 text unamended ·
`not_wired.py` not renamed · U23's frozen test unedited · `audit_store` Docker-guard gap untouched (**5 errors stay
exactly 5**) · no new route · **Stages 2 and 3 not authorized** · #18's spend guardrails neither weakened nor
bypassed (`max_calls=20` default unchanged; the `--real-llm` path still requires both gates) · **no API call, no
money spent**.

---

# ⚑ REGISTER UPDATE — 2026-07-23T07:55:16Z · item #24 OPENED **and** DISCHARGED in one pass

Resolved by `guide-docs/build/plans/repo-tracking-gap-plan.md` (Q1–Q6 answered). Opened and closed in the same
pass per **Q6(a)** — the register has consistently tracked **disclosure and reproducibility** gaps, not only
behavioural defects (**#12** housekeeping, **#13** a stale filename are both precedents), so the correction gets a
citable permanent record without leaving a perpetually-open item for something genuinely finished.

## #24 `REPO-TRACKING-GAP` (surfaced as `GUIDE-DOCS-BUILD-GITIGNORED`) — **DISCHARGED**

**⚑ The item as surfaced UNDERSTATED the problem, and the scoping pass says so plainly.** It was reported as
*"`guide-docs/build/` is untracked because of a frontend-intended `build/` rule."* True — and a **subset**. Fresh
ground truth found that **only 81 files were tracked in the entire repository and `backend/` had ZERO**; the last
commit was **`2edaba4`, the DISCOVER-phase close**. **The entire BUILD phase was uncommitted.**

**Two DISTINCT problems**, and conflating them was the trap:

| | Problem | Size | Would `git add -A` have caught it? |
|---|---|---|---|
| **(A)** | Never committed — untracked but **not ignored** | 650 files | ✅ yes |
| **(B)** | **Actively ignored** by `.gitignore:19`'s unanchored `build/` | 311 files | ⛔ **NO — silently** |

**(B) was the dangerous half**: a `git add -A` "fix" would have committed 650 files, shown a clean `git status`,
and **still omitted the entire BUILD design record**, with no error and no warning.

**⚑ Second victim, newly found**: `.project-guide-rule-details/build/` (6 files) — the workflow's **own BUILD-phase
rule files, which `CLAUDE.md` instructs the workflow to load**. Its 21 siblings were already tracked, so the
directory was **half-committed**.

**⚑ The rule protected nothing**: `frontend/vite.config.js` sets `outDir: 'dist'`, and `dist/` already had its own
rule. No `build/` output directory existed anywhere.

### What was done — two commits, per Q4(b)

* **`b8d184a`** — `.gitignore` **alone**: `build/` → **`frontend/build/`** (Q2-b), with a comment recording *why*
  so a future "cleanup" cannot silently revert it; plus `testresults.txt` ignored (Q5-b); plus the pre-existing,
  previously-uncommitted `!.env.example` negation from U16's pass.
* **`51935ac`** — the BUILD phase: **966 files** (961 A / 4 M / 1 D) — `backend/` 406 · `guide-docs/` 310 ·
  `frontend/` 228 · `corpus/` 7 · `.project-guide-rule-details/build/` 6 · `deploy/` 3 · `pyproject.toml`,
  `render.yaml`, `.python-version`, `.env.example`.

⚑ **Deliberately NOT a reconstructed per-unit commit sequence** (Q4 rejected option (d)): the work happened across
many sessions and was never committed as it went, so synthesising a plausible-looking history would misrepresent
when things actually occurred — against the audit-trail discipline this build has held throughout. **One honest
"state at close of BUILD" commit is the truthful record.**

### Ambiguity-check — three directed checks, all CLEAN

* **(i)** `guide-docs/build/` and `.project-guide-rule-details/build/` **freed**; `frontend/build/assets/app.js`
  **still ignored** (`.gitignore:24`); `frontend/dist/index.html` still ignored (`.gitignore:18`). Before/after
  captured with `git check-ignore -v`.
* **(ii)** U16's `test_governance.py` — the **only** test reading `.gitignore` — **7/7 pass**; `.env` still
  ignored and still untracked.
* **(iii)** ⚑ **the one that mattered — no over-un-ignoring.** All ten probed paths stay ignored: `.env`, `venv/`,
  `frontend/node_modules/`, `__pycache__/`, `.coverage`, `.pytest_cache/`, `.hypothesis/`, `backend/.coverage`,
  `dist/`, `node_modules/`. **Nothing became stageable as a side effect.**

**Git identity, confirmed before staging**: `Nidhi Dhyani <nsdhyani22@gmail.com>`, branch **`main`**.
⚑ Committed **directly to `main`**, as every prior commit in this repository was, per explicit instruction.

### Verification — all four checks RUN, including the load-bearing one

1. ✅ `git check-ignore -v guide-docs/build/plans/x.md` → **no match**.
2. ✅ `git status --porcelain` → **empty**; `git ls-files` → **1041** (predicted ≈1040).
3. ✅ ⚑ **THE CLEAN-CHECKOUT TEST RAN AND PASSED — it was NOT skipped.** `git clone --no-hardlinks` to a temp
   directory produced: `backend/` **406**, `guide-docs/build/` **306**, `.project-guide-rule-details/build/`
   **6**, `corpus/` **7**, `frontend/` **228**, `deploy/` **3**; the clone's tracked count **1041 — exact match**.
   Load-bearing files spot-checked present (`BUILD-COMPLETION-REPORT.md`, both tier-B plans, U22's `engine.py`,
   `build_corpus.py`, `corpus/manifest.json`, the workflow rule files, `.env.example`), and **`.env` and
   `node_modules/` confirmed ABSENT** from the clone. **This is the check that actually tested the broken
   property**, and it is genuinely green — no downgrade to "verified by the other three only" is needed.
4. ✅ **Full suite unchanged: 1578 passed / 0 failed / 43 skipped / 5 errors (same `audit_store` names) /
   99.87%** — exactly as predicted; no code changed.

### ⚑ What this does NOT do

**It does not discharge register #12** (`testresults.txt` append-vs-overwrite). Ignoring that file stops future
diff churn; **#12 is about losing per-unit history**, which is untouched. **#12 stays OPEN**, exactly as the Q5(b)
answer required be stated explicitly.

**Register now stands at 24 tracked — 17 open · 3 discharged (#2 partly, #20 fully, #24 fully) · 4 narrowed (#3,
#8, #18, #19).** ⚑ Count: **#24 is new and immediately discharged**, so open is **unchanged at 17**, discharged
**2 → 3**, tracked **23 → 24** (17 + 3 + 4 = 24).

**HOLDS upheld:** no frozen-23 unit internal or test edited · U22's `DEFERRED_REGISTER` and its three frozen tests
untouched · WIRE-1 unamended · `not_wired.py` not renamed · U23's frozen test unedited · `audit_store`
Docker-guard gap untouched (**5 errors stay exactly 5**) · **tier-B Stages 2 and 3 not authorized** · #18's spend
guardrails untouched · **no API call, no money spent** · no file moved, renamed or deleted beyond the
pre-existing `unhappy paths.png` deletion, which is disclosed in the commit message.
