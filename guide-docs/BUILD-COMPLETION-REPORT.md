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
| 17 | **`OUTLIER-DATA-EXISTS-CONTRACT-FORBIDS`** ✅ **CLOSED 2026-08-13** ⚑ **SUPERSEDED — see #17-C** ⛔ **CLOSED ON BOTH HALVES.** The **technical** half closed 2026-08-01 (a real score computed, persisted at 464 canonical bytes, served on the wire — see 17-C). The **frontend** half closed 2026-08-13: `OutlierView` mounted at the composition root (`seams.js` seventh key, `App.jsx` selection branch) and **observed rendering that real data on screen**, cross-checked digit-for-digit against `curl`'s R4 body (user-run; `audit.md` 2026-08-13T17:01:28Z). ⚑ **The closure is of the ITEM, not an endorsement of its title** — 17-C stands as the standing correction and is **not deleted**. ⚠️ It does **not** mean "the system is in Phase 2" (only the Phase-2-OUT slice), does **not** settle the corpus-deployment question, and does **not** touch **#5 `OUTLIER-IN-PROSE`**. | **ORIGINAL TEXT, PRESERVED VERBATIM:** `PendingRecommendation.outlier_canonical` **persists real outlier data**, but WIRE1-Fold-4 binds `outlier: null` in Phase 1 **even for a `ready` view**. The data exists; the frozen contract forbids sending it. Declared at `backend/app/projections.py:138`. | Emitting it would be an **unauthorized contract change**. WIRE-1 was honored and the mismatch **disclosed rather than quietly resolved** (Q5b) — *"the data exists but the contract forbids it"* is exactly what should be reconciled deliberately later, not silently now. | a future WIRE-1 amendment | **Non-blocking.** A deliberate contract-fidelity choice. |
| **17-C** | **`OUTLIER-CORRECTION`** — the correction to #17, not a new gap | ⛔ **#17'S TWO LOAD-BEARING CLAIMS WERE BOTH FALSE, and its owner was mis-attributed.** **(1)** *"persists real outlier data"* — **it did not.** Nothing computed a score in any API-reachable path (`seed_demo_cases.py`'s `score_outlier` returned `None`), so `outlier_canonical` was **NULL for every row ever written**. **(2)** *"the frozen contract forbids sending it"* — **it does not.** WIRE-1 binds `outlier` null *in Phase 1* and explicitly provides for it being *"populated only for a Phase-2 `ready` view"*; populating it is **contract-COMPLIANT**. ⚑ **#17 described 2 of 5 barriers**: (1) nothing scored, (2) therefore nothing stored, (3) `projections.py` hardcoded null, (4) WIRE-1's Phase-1 binding, and — found only by executing it — **(5) `CanonSerAdapter.canonical_bytes` REJECTS IEEE float (`CanonSerError`, CON-DET-1) while every numeric field of `OutlierResult` is a float, so a real score could not be persisted at all.** | **RESOLVED 2026-08-01** by the Phase-2-OUT slice: the seed script fits the committed corpus and scores; the score is stored as a **Decimal-quantized projection** (`backend/app/outlier_canonical.py`, 12 dp, named constant) because CANON-SER refuses float; `projections.py` dequantizes for a `ready` view. ⚑ **No frozen unit reopened. No WIRE-1 amendment** — none was needed, and the belief that one was is the misattribution being corrected here. ⛔ **The quantization is a projection of the model's float output — NOT a claim that the ML computation is bit-for-bit reproducible across library versions.** CANON-SER guarantees the persisted *representation*, not floating-point computation, which nothing in this stack promises. | ~~a future WIRE-1 amendment~~ → **corrected owner: implementing Phase-2-OUT** (done) | **Non-blocking.** ✅ **LIVE EVIDENCE PRODUCED 2026-08-01** — supersedes this cell's earlier text, *"Live evidence (re-seed → `psql` → `curl` → determinism spot-check) is **NOT YET RUN** — until it is, this is proven at tier-U/I only."* All six Step 13 checks passed against a real local PostgreSQL (user-run; see `audit.md` 2026-08-01T14:54:07Z): `psql` shows `outlier_canonical` **non-null, 464 bytes** on DEMO-0001/0002 — **the first outlier data ever persisted by this system**; `curl` R4 returns a complete `OutlierResult` (`outlier_score=0.567032896281`, `is_outlier=true`, **two explained flags** carrying `z_score`/`shap_value`/`direction`, full provenance `{1.0.0, 42, …}`); a never-drafted case still returns `outlier: null`; **two independent seeds produced byte-identical values across every field** (reproducibility §6, live for the first time); and a missing corpus **fails loudly by name** rather than degrading to null. ⚑ The score differs from the plan's `0.667071302659` because that reference is `corpus/profiles.json[0]`, a **different profile** — **not** a determinism drift, and **not** stop-gate 8. ⛔ **#17's TECHNICAL gap is closed. Its FRONTEND half is NOT** — the mount pass stays deferred per Q1(a) (`seams.js` still has five keys, `OutlierView` still unmounted), and **#27** `DUPLICATE-PENDING-RECOMMENDATION-ROWS` is open and unrelated. |
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

---

# ⚑ REGISTER UPDATE — 2026-07-25T10:42:13Z · item #25 OPENED (a scope gap, not a deferral — the register's first)

**Opened by**: the login/signup scoping pass's ground-truth reconstruction
(`guide-docs/build/plans/login-signup-plan.md` §1.4). **Opened only — NOT resolved.** Designing its fix is a
separate act, scoped in that plan and gated on the user's answers.

## #25 `PER-4-AUTHN-UNIMPLEMENTED` — **NEW, OPEN**

| | |
|---|---|
| **What it is** | **PER-4 — an in-scope Phase-1 requirement — was never built.** `requirements.md:78`: *"Authentication = **basic login with role-based access (JWT/session)**. RBAC MUST enforce the PER-1/PER-2 separation in the UI."* What exists instead is a stub: `VITE_USER_ID` → `X-User-Id` → an `app_user` lookup (`dependencies.py:160-175`), with **no credential verification of any kind**. **US-PLAT-1 (Phase 1) is half-delivered against its own acceptance criteria**: its Gherkin `Then` clauses (auditor denied, underwriter retains act capability) are built and tested; its `Given` clause — *"Given JWT/session authentication with roles underwriter and auditor"* — is **unsatisfied**. |
| **Why it went unrecorded** | ⚑ **A silent scope-widening in `auth-rbac`'s FD.** **BR-AUTH-10** (`guide-docs/build/auth-rbac/functional-design/business-rules.md`) defers the authentication flow with the justification *"**authn is out of Phase-1 scope**"*. **That justification is not supported by the requirements record.** What DISCOVER put out of Phase-1 scope was **OOS-3 — *full SSO/OAuth federated identity*** (`requirements.md:62`, *"Phase 3 — Future Release"*). Requirements Q6 **rejected option A (no real auth)** and **rejected option C (full SSO)**, selecting **B, basic login (JWT/session)**, which became PER-4 and was phase-tagged **Phase 1** via US-PLAT-1. Between Requirements Analysis and the auth-rbac FD, *"authn deferred"* widened from *"federated SSO deferred"* to *"all authentication deferred."* **No artifact surfaces, questions, or approves that widening** — it appears in BR-AUTH-10 as an already-settled premise, and every downstream artifact inherits it in good faith: `unit-of-work.md:182` (U11 lists PER-4/5 among its invariants while covering only the authz half) → `domain-entities.md:150-151` (*"**Not** an authentication (authn) design"*) → WIRE-1 A6 / §6:137 (*"abstract seam, deferred… Phase-1 may stub it"*) → `dependencies.py:31-34` (the `X-User-Id` stub). **Each step is individually defensible; the sum is an in-scope requirement silently dropped.** |
| **Citation chain (verbatim sources)** | `requirement-verification-questions.md` Q6 `[Answer]: B` · `requirements.md:78` (PER-4) · `requirements.md:79` (PER-5) · `requirements.md:62` (OOS-3 — *federated* only) · `personas.md:21` (*"Authenticated UI user (JWT/session)"*) · `user-journey.md:46` (*"1. Login with JWT/session; RBAC routes the user by role (PER-4)"*) · `stories.md` US-PLAT-1 (Phase 1, Traces PER-4/PER-5/SEC-4) · `unit-of-work.md:177-183` · `business-rules.md` BR-AUTH-10 · `business-logic-model.md:103` · `domain-entities.md:150-151` · `wire-1/api-contract.md:8,137` · `backend/app/dependencies.py:31-34,160-175` |
| **What is NOT claimed** | **`auth-rbac` (U11) is not defective.** Its authorization model is correct, single-sourced, enforced at both points, and tested. #25 is about the **authentication** half that PER-4 required and no unit ever owned — not about the authz half that U11 built well. Nor is any prior pass at fault for relying on the stub: every one of them disclosed it accurately as a stub. |
| **Severity — stated on the register's own scale** | **Non-blocking for the system as built and demonstrated today** (the stub works; the demo path runs; every test is green). **⛔ BLOCKING for any multi-user or publicly-reachable deployment**, and it **materially qualifies two headline claims**: **(1) SEC-4's segregation of duties is not adversarially enforceable** — the underwriter/auditor separation holds against mistakes, not against anyone who edits a header; **(2) `AuditRecord.underwriter_id` — the CON-BR4 "WHO" in every committed decision — is an unauthenticated, self-asserted string.** WIRE-1 §5:122 keeps `underwriter_id` out of the request body *precisely so* *"a client cannot commit **as another user**"*; with a forgeable header that protection is nominal. For a build whose stated invariant is **full auditability**, the audit trail's actor field currently has no authentication behind it. ⚑ On severity this sits alongside **#19** (*"a genuine BFSI-relevant defect"*) rather than with the housekeeping items — it is **not** a disclosure-only gap. |
| **Also engaged (recorded, not resolved)** | The **Security Guardrails** extension is `Enabled (scoped)` (`guide-state.md:25-30`) and the recorded scope **excludes `SECURITY-12: Authentication and Credential Management`** — a scope fixed at Requirements Analysis under the *same* unsupported assumption. Any fix forces a second decision on whether that scope widens; per **CLAUDE.md**, an applicable enabled extension rule that is unmet is a **blocking finding**, and SECURITY-12 includes *"**MFA MUST be supported for administrative accounts**"*. Scoped as **Q4.2** in the login/signup plan. |
| **Structural blocker on any fix (recorded here so it is not rediscovered)** | **Four frozen assertions across two units** would fail on any new route: `deploy_config/tests/test_routes.py:36` (exact-set equality over the seven WIRE-1 routes, *"LOAD-BEARING — full-highest"*, **app-level — binds wherever the router file lives**) · `:41` (exact filename set under `backend/app/routes/`) · `app/tests/test_no_write_route.py:107` (exactly one non-GET route) · `:239` (no direct writes under `backend/app/`; a signup INSERT breaks the composition root's stated *"every write goes through the frozen `DecisionCommitService`"* guarantee, `dependencies.py:15-20`). **Same MATCHED-PAIR shape as #13, but four assertions across two units instead of one.** |
| **Owner** | A future **authorized authentication pass** + an **`auth-rbac` (U11) scope reconciliation** (BR-AUTH-10 to be **superseded, never rewritten in place**), **as one authorization** |
| **Blocking?** | **Non-blocking today · ⛔ BLOCKING for any exposed or multi-user deployment.** See severity above. |

⚑ **A new outcome shape for this register.** Every prior item recorded a **deferral that was disclosed when it was
taken** (#2–#24) or a **rationale that was never written down** (#20). **#25 is the first item where the build's
own requirements record and its shipped behaviour disagree, and the disagreement was never disclosed at all.**
That distinction is recorded deliberately: the register's existing items are evidence the disclosure discipline
worked; #25 is evidence of the one place it did not, and it was found by a ground-truth pass rather than by the
gates.

**Register now stands at 25 tracked — 18 open · 3 discharged (#2 partly, #20 fully, #24 fully) · 4 narrowed
(#3, #8, #18, #19).** ⚑ Count reconciliation: **#25 is new and open**, so open goes **17 → 18**, discharged and
narrowed are unchanged, and tracked goes **24 → 25** (18 + 3 + 4 = 25).

**HOLDS upheld:** no frozen-23-or-24 unit internal or test edited · **BR-AUTH-10 not edited** (cited only; its
supersession is future authorized work) · WIRE-1 text unamended · `not_wired.py` not renamed · U23's frozen test
unedited · U15's migrations and U16's six-field `Settings` untouched · `audit_store` Docker-guard gap untouched
(**5 errors stay exactly 5**) · tier-B not authorized, not touched · `backend/` and `frontend/` **not written to
at all** · **no code generated** · **#25 opened, NOT resolved**.

---

# ⚑ REGISTER CORRECTION — 2026-07-25T10:42:13Z · #25's structural-blocker figure SUPERSEDED (4-across-2 → **8-across-3**)

**This section supersedes the *"Structural blocker on any fix"* row of #25's table above. That row is preserved
verbatim as the historical record of what was believed when #25 was opened; it is NOT rewritten in place.**
**#25's status is UNCHANGED — it remains OPEN and unresolved.** Only the blocker's *measurement* is corrected.

## What was wrong

#25 recorded the blocker as **"four frozen assertions across two units"**. That was **twice** understated. The
figure was corrected once to *"seven across three"* (still wrong in **membership**) and then, by an exhaustive
sweep, to the ratified figure below. Both errors were caught by the **mandatory ambiguity-check**, not by the
ground-truth passes that produced them.

## ⚑ The ratified figure (`login-signup-plan.md` Q12(a), Q13(a) — use this wording verbatim)

> **The relaxation scope is 8 assertions across 3 units — U23 (2: `deploy_config/tests/test_routes.py:36`,
> `:41`), the composition root (3: `backend/app/tests/test_no_write_route.py:107`, `:116`, `:122`), and U15
> `database` (3: `database/tests/test_migration_runner.py:75`, `test_migration_checksum.py:114`,
> `test_migration_apply.py:56` — the last **CI-only**, being Docker-gated), plus a `checksums.json` manifest
> entry. TWO further items are PRESERVED BY DESIGN CONSTRAINT rather than weakened:
> `test_no_write_route.py:239` (A-4), via authoring the credential/session stores OUTSIDE `backend/app/` on the
> U24 `PostgresCaseStore` pattern; and `frontend/src/app/__tests__/app.test.jsx:261`, via the `sessionClient.js`
> non-seam precedent.**

**Net corrections from the originally-recorded row**: **+`test_no_write_route.py:116`** (fails **twice**, for
`/login` and `/logout`) · **+`test_no_write_route.py:122`** (exact seven-path set) · **+U15's three** (triggered
by Q9(a)'s `0003_auth.sql`) · **−A-4** (needs **no** relaxation — it passes under the store-placement constraint).

## Why the first figure was wrong, stated plainly

**U15 was not in scope when #25 was opened** — the migration only enters once Q2(a)/Q9(a) put credentials in a
new `database`-owned migration, which was decided after. **That half is a legitimate consequence of a later
decision, not an error.** The composition-root half **was** an error: `:116` and `:122` sit in a file the
ground-truth pass had already read, and were missed because that pass enumerated the assertions it already knew
about rather than sweeping by change-type.

## ⚑ Disclosed process finding — recorded, not smoothed over

On the **#20 directed-check** and **#19-vacuous-fixture** precedent: **the plan's own §2 under-counted twice**,
and **the ambiguity-check caught both**. What finally worked was **changing the method** — enumerating every
exact-set/exact-count assertion in the repository perturbable by the three implied changes (**+2 routes, +1
migration file, +2 tables**) and classifying each as *breaks* or *survives* **with a reason** — rather than
re-checking the same list harder. Ten near-miss assertions were swept and confirmed **surviving**, each with its
reason recorded (`login-signup-plan.md` §11.3), so no future pass re-derives them.

**Caution for future passes, recorded as the lesson**: *a ground-truth pass that enumerates what it already knows
about is not a sweep.*

**Register still 25 tracked — 18 open · 3 discharged (#2 partly, #20 fully, #24 fully) · 4 narrowed (#3, #8, #18,
#19).** ⚑ **No count changes**: this corrects a measurement inside an existing open item, opens nothing, and
closes nothing.

**HOLDS upheld:** no frozen-23-or-24 unit internal or **test** edited — **all eight assertions are untouched on
disk** · WIRE-1 unamended · `backend/app/routes/` untouched, no route added · U15's migrations and
`checksums.json` untouched, **no migration written** · U16's six-field `Settings` untouched · `not_wired.py` not
renamed (#13 stays open) · `audit_store` Docker-guard gap untouched (**5 stays 5**) · tier-B not authorized ·
`backend/` and `frontend/` **not written to at all** · **no code generated** · **#25 remains OPEN**.

---

# ⚑ REGISTER NOTE — 2026-07-25T10:42:13Z · #18 — one recorded non-discharge reason is NO LONGER FACTUALLY ACCURATE (status UNCHANGED)

**This is a FACTUAL ANNOTATION, not a status change.** **#18 `NO-PRODUCTION-LLMCLIENT` remains NARROWED, NOT
DISCHARGED.** No discharge is claimed, nothing is superseded, and **no view is offered** on whether the real-API
verification should now be attempted — that is the user's decision.

## What changed in the world, not in the code

The 2026-07-21T17:04:30Z update recorded #18's first non-discharge reason as:

> *"**The manual real-API verification has NOT been run end-to-end.** No live `GEMINI_API_KEY`, no network, and
> **`google-genai` is not installed in this environment**."*

⚑ **The final clause is no longer true.** `google-genai` **is now installed** in the project venv
(`venv/Lib/site-packages/google/genai/`). This is a **legitimate, expected state**: `requirements.txt:8` declares
**`google-genai>=1.0.0`** — added by #18's own pass — so a plain `pip install -r requirements.txt` produces
exactly it.

## What is UNCHANGED, and why #18 does not move

* **The other recorded reasons stand**: **no live `GEMINI_API_KEY`** and **no network**, so the manual real-API
  verification (`guide-docs/build/composition-root/real-llm-verification.md`) **has still not been run**.
* **The second non-discharge reason is untouched**: the pinned model id `gemini-2.5-flash-001` is **still not
  confirmed to resolve** against the live API.
* **No real memo has been produced and confirmed.** The evidentiary bar recorded at #18's narrowing — *"decided
  on evidence actually produced"* — is **not met**, and an installed SDK is not evidence of a completed
  verification.
* **#18's spend guardrails are untouched**: `--real-llm` **and** `ALLOW_REAL_LLM_CALLS=true` are both still
  required, and `max_calls=20` is unchanged. **No API call was made and no money was spent by the pass that
  recorded this note.**

## How it surfaced — and the test-quality defect it exposed

The SDK's presence broke `backend/app/tests/test_llm_client.py::test_the_module_imports_without_the_sdk_installed`,
which asserted `find_spec("google.genai") is None` and reasoned that a successful import therefore **proved** the
SDK import was lazy. That inference held **only while the SDK was absent** — the test had encoded an
**environmental precondition as an invariant**, putting the manifest and the test in direct contradiction (the
manifest declares the SDK a dependency; the test asserted its absence).

⚑ **Worse than merely failing**: with the SDK present the old technique **could not prove the property at all** —
a successful import no longer discriminates lazy from eager — so it would have been **vacuous** had the
precondition merely been relaxed rather than the technique replaced.

**Corrected in its own scoped pass** (logged separately in `audit.md`): the test now asserts the property
**structurally by AST** — no `google`-rooted import outside a function body, and a lazy import must exist —
which is **environment-independent** and is what the test always actually wanted to prove. **`llm_client.py`
itself was never implicated and was not touched.**

**Register unchanged at 25 tracked — 18 open · 3 discharged (#2 partly, #20 fully, #24 fully) · 4 narrowed (#3,
#8, #18, #19).** No item opened, closed, narrowed or discharged by this note.

---

# ⚑ REGISTER UPDATE — 2026-07-25 · item #26 OPENED (a PRE-EXISTING defect, surfaced by the login/signup pass's commit verification)

**Opened by**: the per-commit verification at the close of the login/signup implementation pass. Each of that
pass's four code commits was checked out into an **isolated worktree** and run there, rather than trusting a
working-tree run — and every fresh checkout showed **two failures the working tree does not have**.

⚑ **Opened only — NOT fixed.** The likely remedy is a **repo-wide** change and is explicitly withheld pending its
own authorization (below).

## #26 `CRLF-CHECKSUM-MANIFEST-FRAGILE` — **NEW, OPEN**

| | |
|---|---|
| **What it is** | The **migration checksum manifests are environment-dependent, not content-dependent.** `core.autocrlf=true` with **no `.gitattributes`** anywhere in the repository, so git rewrites `.sql` line endings **on checkout**. A manifest whose sha256 was computed against **LF** bytes therefore does not match the **CRLF** bytes a fresh clone materialises, and checksum verification fails. |
| **The two failing tests** | `backend/case_lifecycle/tests/test_migname.py::test_verify_checksums_passes_against_u24s_own_manifest` · `backend/database/tests/test_migration_checksum.py::test_committed_manifest_matches_committed_migrations` |
| **Proven by bytes, not inferred** | `0001_initial_schema.sql` — manifest `848f6eec…` · **working tree** `848f6eec…` (**0** CRLF pairs) ✅ · **fresh checkout** `14fdf782…` (**57** CRLF pairs) ❌. Same file, same commit, two different digests. |
| ⚑ **PREDATES this pass — confirmed, not assumed** | Reproduced at **`ceb32f6`** (the Phase A close, **before any login/signup work existed**), where **both tests fail identically**. **Nothing in this pass caused it.** |
| ⚑ **Affects U24's manifest equally** | `test_migname` guards **U24's own `case_lifecycle/migrations/checksums.json`** — a file this pass never touched. The defect is in the **mechanism**, not in any one manifest, and it has been latent since U24 shipped. |
| **The new entry inherits it identically** | `0003_auth.sql`'s digest was computed against **LF** bytes, exactly as the two existing entries were. It is **consistent with them and consistently fragile** — no better, no worse. |
| **Why CI has never caught it** | **Linux defaults to `core.autocrlf=false`**, so a CI checkout materialises LF and the digests match. The failure is reachable **only** on a platform that translates line endings — i.e. a Windows contributor cloning fresh. The guard silently does not hold where it is most likely to be exercised by a newcomer. |
| **Why it matters** | These manifests are the **integrity mechanism for the frozen migrations** — the thing that would catch a silent edit to `0001_initial_schema.sql`. A guard that passes or fails according to the *checkout platform* rather than the *file contents* is not doing the job it is relied on for, in either direction: it can fail on an untouched file, and its passing on one machine says nothing about another. |
| **Likely fix — NAMED, EXPLICITLY NOT APPLIED** | A **`.gitattributes`** pinning line endings — minimally `*.sql text eol=lf`, or more broadly `* text=auto eol=lf` — so checked-out bytes are identical on every platform. ⛔ **Not applied here.** Even the narrow form changes how git materialises files repo-wide and would re-normalise existing checkouts; the broad form touches **every text file in the repository**. That is a repo-wide change requiring its **own authorization**, exactly like the `.gitignore` correction that became **#24**. ⚑ Note also that a fix must decide whether the **manifests are re-computed** or the **checkout is normalised** — those are different remedies with different blast radii, and choosing between them is part of the decision, not a detail. |
| **Owner** | `database` (U15) + `case_lifecycle` (U24) + repo configuration, **as one change** |
| **Blocking?** | **Non-blocking.** CI is green, the deployed path is unaffected (Linux), and no behaviour is wrong. It is a **guard-reliability** defect: the integrity check is weaker and less portable than it appears. |

### ⚑ Structural kinship — the second instance of this shape in a single session

**#26 is the same defect shape as `test_the_module_imports_without_the_sdk_installed`**, corrected earlier in this
same session (commit `86e2725`): **a test whose outcome depends on the ENVIRONMENT rather than on the property it
claims to check.**

* That one asserted `find_spec("google.genai") is None` and inferred laziness from the SDK's **absence** — sound
  only while the SDK was absent, and it broke the moment `requirements.txt` made it present.
* This one asserts a digest match and inherits the **checkout platform's** line-ending policy — sound only while
  every checkout uses LF.

Both are green in one environment and red in another **with no change to the code under test**. The earlier one
was fixed by re-expressing the assertion **structurally** (an AST scan, environment-independent); the analogous
move here is to make the **bytes** environment-independent via `.gitattributes` rather than to weaken the digest
check. **Recording the kinship so the pattern is recognised the third time it appears rather than re-diagnosed
from scratch.**

### ⚑ Follow-up correction to commit `d6a6876`'s message — appended here, NOT rewritten in git history

`d6a6876` ("feat(database): add 0003_auth.sql") states:

> *"The two existing entries are **BYTE-IDENTICAL** -- verified programmatically before writing, not assumed."*

**The claim is true but under-qualified, and #26 is exactly why.** The verification compared the two existing
digests **before and after** adding the third entry, in **this working tree**, where the `.sql` files carry **LF**.
It establishes that this pass **did not recompute or alter** those two entries — which was the property being
guarded, and that property genuinely holds.

It does **not** establish that those digests match the file bytes **universally**. On a fresh CRLF checkout they
match nothing, as #26 documents. ⚑ **"Verified programmatically" should be read as "verified against this
working tree's bytes", not "verified as correct on every platform."**

**Git history is not rewritten** — the commit message stands as written, and this entry is the correction, per
the standing supersede-not-rewrite discipline.

**Register now stands at 26 tracked — 18 open · 3 discharged (#2 partly, #20 fully, #24 fully) · 5 narrowed
(#3, #8, #18, #19, #25).** ⚑ Count reconciliation: the login/signup pass moved **#25 from open to narrowed**
(open 18 → 17, narrowed 4 → 5, tracked unchanged at 25); **#26 is new and open**, so open goes **17 → 18** and
tracked **25 → 26** (18 + 3 + 5 = 26).

**HOLDS**: **no `.gitattributes` added** · **no manifest recomputed** · **no `.sql` file touched** · no test
edited · no git history rewritten · working tree clean at `d72ffe4` · suite **1610 / 0 / 43 / 5 / 99.70%**
unchanged.

---

# ⚑ REGISTER UPDATE — 2026-07-25 · item #26 OPENED (a PRE-EXISTING defect, surfaced by the login/signup pass's commit verification)

**Opened by**: the per-commit verification at the close of the login/signup implementation pass. Each of that
pass's four code commits was checked out into an **isolated worktree** and run there, rather than trusting a
working-tree run — and every fresh checkout showed **two failures the working tree does not have**.

⚑ **Opened only — NOT fixed.** The likely remedy is a **repo-wide** change and is explicitly withheld pending its
own authorization (below).

## #26 `CRLF-CHECKSUM-MANIFEST-FRAGILE` — **NEW, OPEN**

| | |
|---|---|
| **What it is** | The **migration checksum manifests are environment-dependent, not content-dependent.** `core.autocrlf=true` with **no `.gitattributes`** anywhere in the repository, so git rewrites `.sql` line endings **on checkout**. A manifest whose sha256 was computed against **LF** bytes therefore does not match the **CRLF** bytes a fresh clone materialises, and checksum verification fails. |
| **The two failing tests** | `backend/case_lifecycle/tests/test_migname.py::test_verify_checksums_passes_against_u24s_own_manifest` · `backend/database/tests/test_migration_checksum.py::test_committed_manifest_matches_committed_migrations` |
| **Proven by bytes, not inferred** | `0001_initial_schema.sql` — manifest `848f6eec…` · **working tree** `848f6eec…` (**0** CRLF pairs) ✅ · **fresh checkout** `14fdf782…` (**57** CRLF pairs) ❌. Same file, same commit, two different digests. |
| ⚑ **PREDATES this pass — confirmed, not assumed** | Reproduced at **`ceb32f6`** (the Phase A close, **before any login/signup work existed**), where **both tests fail identically**. **Nothing in this pass caused it.** |
| ⚑ **Affects U24's manifest equally** | `test_migname` guards **U24's own `case_lifecycle/migrations/checksums.json`** — a file this pass never touched. The defect is in the **mechanism**, not in any one manifest, and it has been latent since U24 shipped. |
| **The new entry inherits it identically** | `0003_auth.sql`'s digest was computed against **LF** bytes, exactly as the two existing entries were. It is **consistent with them and consistently fragile** — no better, no worse. |
| **Why CI has never caught it** | **Linux defaults to `core.autocrlf=false`**, so a CI checkout materialises LF and the digests match. The failure is reachable **only** on a platform that translates line endings — i.e. a Windows contributor cloning fresh. The guard silently does not hold where it is most likely to be exercised by a newcomer. |
| **Why it matters** | These manifests are the **integrity mechanism for the frozen migrations** — the thing that would catch a silent edit to `0001_initial_schema.sql`. A guard that passes or fails according to the *checkout platform* rather than the *file contents* is not doing the job it is relied on for, in either direction: it can fail on an untouched file, and its passing on one machine says nothing about another. |
| **Likely fix — NAMED, EXPLICITLY NOT APPLIED** | A **`.gitattributes`** pinning line endings — minimally `*.sql text eol=lf`, or more broadly `* text=auto eol=lf` — so checked-out bytes are identical on every platform. ⛔ **Not applied here.** Even the narrow form changes how git materialises files repo-wide and would re-normalise existing checkouts; the broad form touches **every text file in the repository**. That is a repo-wide change requiring its **own authorization**, exactly like the `.gitignore` correction that became **#24**. ⚑ Note also that a fix must decide whether the **manifests are re-computed** or the **checkout is normalised** — those are different remedies with different blast radii, and choosing between them is part of the decision, not a detail. |
| **Owner** | `database` (U15) + `case_lifecycle` (U24) + repo configuration, **as one change** |
| **Blocking?** | **Non-blocking.** CI is green, the deployed path is unaffected (Linux), and no behaviour is wrong. It is a **guard-reliability** defect: the integrity check is weaker and less portable than it appears. |

### ⚑ Structural kinship — the second instance of this shape in a single session

**#26 is the same defect shape as `test_the_module_imports_without_the_sdk_installed`**, corrected earlier in this
same session (commit `86e2725`): **a test whose outcome depends on the ENVIRONMENT rather than on the property it
claims to check.**

* That one asserted `find_spec("google.genai") is None` and inferred laziness from the SDK's **absence** — sound
  only while the SDK was absent, and it broke the moment `requirements.txt` made it present.
* This one asserts a digest match and inherits the **checkout platform's** line-ending policy — sound only while
  every checkout uses LF.

Both are green in one environment and red in another **with no change to the code under test**. The earlier one
was fixed by re-expressing the assertion **structurally** (an AST scan, environment-independent); the analogous
move here is to make the **bytes** environment-independent via `.gitattributes` rather than to weaken the digest
check. **Recording the kinship so the pattern is recognised the third time it appears rather than re-diagnosed
from scratch.**

### ⚑ Follow-up correction to commit `d6a6876`'s message — appended here, NOT rewritten in git history

`d6a6876` ("feat(database): add 0003_auth.sql") states:

> *"The two existing entries are **BYTE-IDENTICAL** -- verified programmatically before writing, not assumed."*

**The claim is true but under-qualified, and #26 is exactly why.** The verification compared the two existing
digests **before and after** adding the third entry, in **this working tree**, where the `.sql` files carry **LF**.
It establishes that this pass **did not recompute or alter** those two entries — which was the property being
guarded, and that property genuinely holds.

It does **not** establish that those digests match the file bytes **universally**. On a fresh CRLF checkout they
match nothing, as #26 documents. ⚑ **"Verified programmatically" should be read as "verified against this
working tree's bytes", not "verified as correct on every platform."**

**Git history is not rewritten** — the commit message stands as written, and this entry is the correction, per
the standing supersede-not-rewrite discipline.

**Register now stands at 26 tracked — 18 open · 3 discharged (#2 partly, #20 fully, #24 fully) · 5 narrowed
(#3, #8, #18, #19, #25).** ⚑ Count reconciliation: the login/signup pass moved **#25 from open to narrowed**
(open 18 → 17, narrowed 4 → 5, tracked unchanged at 25); **#26 is new and open**, so open goes **17 → 18** and
tracked **25 → 26** (18 + 3 + 5 = 26).

**HOLDS**: **no `.gitattributes` added** · **no manifest recomputed** · **no `.sql` file touched** · no test
edited · no git history rewritten · working tree clean at `d72ffe4` · suite **1610 / 0 / 43 / 5 / 99.70%**
unchanged.

---

# ⚑ REGISTER UPDATE — 2026-07-26T07:37:32Z · item #25 **DISCHARGED** — the first NARROWED → fully DISCHARGED in the register's history

**This section supersedes #25's NARROWED status recorded at the close of the login/signup implementation pass.
That record is preserved verbatim as the historical statement of what was and was not proven at the time; it no
longer describes the system.**

## #25 `PER-4-AUTHN-UNIMPLEMENTED` — **DISCHARGED**

**The bar was set publicly, in advance, and has now been met in full.** From
`login-signup-code-gen-plan.md` §9 and commit **`5e454f2`**'s message, verbatim:

> *"a real login against a real Postgres, **driving R2–R7 with that session**, and **a commit whose
> `AuditRecord.underwriter_id` is the authenticated user**."*

⚑ **Discharged because the evidence meets that bar — not because time passed or the item became tiresome.** The
same discipline that kept #25 NARROWED one turn earlier, when the commit-path step was missing, requires
discharging it now that the step has been performed. **A bar that only ever ratchets in one direction is not a
bar.**

### The evidentiary basis — cited, not summarised

**Manual end-to-end verification by the user via `curl` and `psql` against a real local PostgreSQL**
(audit.md entry of 2026-07-26T07:37:32Z; events ~07:29–07:35 the same day):

| # | Evidence | What it settles |
|--:|---|---|
| 1 | Login as `demo-underwriter` → **204 + `Set-Cookie`**; session resolves with `role=underwriter` | R8 issues a real session; R1 reads it; the role comes from `app_user` |
| 2 | Commit of `REC-DEMO-0002-25a195b9` **through the session cookie** → `{"recommendation_id":"REC-DEMO-0002-25a195b9","underwriter_id":"demo-underwriter","action":"approve","reason":null}` | ⚑ **The load-bearing result.** `underwriter_id` was **never sent by the client** — WIRE-1 §5 forbids it in the body — so it was **derived server-side from the authenticated session** |
| 3 | **Direct `psql` against `audit_record`**: `decision_id 7d29fa12-eecf-4abc-9b1f-0ce59679eb1f`, `underwriter_id=demo-underwriter`, `action=approve` | The **persisted row**, not a projection of it. The CON-BR4 "WHO" is an authenticated subject **on disk** |
| 4 | Negative control (a): re-committing the same recommendation → **409 `commit_conflict`** | Register **#19**'s two-step claim guard is live against a real database |
| 5 | Negative control (b): committing with **no session cookie** → **401**, not 403 | The commit path is gated by **authentication**, not merely authorization — a caller without a session cannot reach it at all |

### ⚑ The single most persuasive artifact — a before/after in one table

The same `psql` query surfaced an **older row from the pre-fix era**:

| decision_id | application_id | underwriter_id | timestamp |
|---|---|---|---|
| `f67dc658-6e7e-438a-80cf-96315d2cad76` | DEMO-0001 | **`demo-user-1`** | 2026-07-23 |
| `7d29fa12-eecf-4abc-9b1f-0ce59679eb1f` | DEMO-0002 | **`demo-underwriter`** | 2026-07-26 |

The **2026-07-23** row was written under the **`X-User-Id` header** mechanism — the forgeable stub #25 was opened
about, where *any caller who knew a `user_id` was that user*. The **2026-07-26** row was written under the
**session-derived** mechanism. **Both sit in the same `audit_record` table, and the defect and its remedy are
visible side by side in a single query.** No test could have produced that; only a real database with real
history could. It is the cleanest evidence in the register.

### Why this is a FULL discharge and not another narrowing

Measured against **#25's own recorded wording**, not a generous paraphrase:

* Its subject — *"PER-4 — an in-scope Phase-1 requirement — was never built"* — **is satisfied**: it is built and
  field-verified.
* Its severity rationale — *"`AuditRecord.underwriter_id` … is an unauthenticated, self-asserted string … the
  audit trail's actor field currently has no authentication behind it"* — **is refuted by evidence 2 and 3**, on
  the persisted row itself.
* Its blocking claim — *"⛔ BLOCKING for any exposed or multi-user deployment"* — **is discharged**: lockout,
  uniform failure, server-side revocation, absolute expiry and session-gated commit are all confirmed working.
* **US-PLAT-1's Gherkin `Given`** — *"Given JWT/session authentication with roles underwriter and auditor"* — the
  clause #25 recorded as unsatisfied, **is now satisfied**; its `Then` clauses were already built and tested.

⚑ **A new outcome shape for this register.** #25 is the **first item to go NARROWED → fully DISCHARGED**. #20 and
#24 were discharged without ever being narrowed; #2 is only *partly* discharged; #3, #8, #18 and #19 remain
narrowed. **A narrowing is therefore not a terminal state** — it is an honest interim label that a later,
sufficient body of evidence can retire. That precedent is worth having.

### ⛔ What this discharge explicitly does NOT claim

Stated so the discharge is precise rather than expansive. **None of these is a residual of #25** — each is a
distinct matter, and none was ever part of the bar:

1. **There is no login UI.** A user cannot log in through a browser: this pass delivered routes, not a form
   (Q13(a) deliberately kept the login client out of `seams.js`). PER-4's *"in the UI"* phrasing is satisfied in
   the sense #25 recorded — the RBAC separation is enforced and the role reaches the client unchanged — but the
   **browser login journey does not exist**. Whether that warrants its own register item is the **user's call**;
   none is opened here.
2. **The `SESSION_COOKIE_SECURE=false` opt-out branch has never been exercised in a real run.** The fail-safe
   default was; its opt-out was not. That branch is what the local dev loop needs, since Vite serves over
   `http://`.
3. **`httpTransport.js` remains unproven against a real browser.** Fold-3's *"no change needed"* prediction
   (resting on `fetch`'s `credentials: 'same-origin'` default) is still unverified by any run.
4. **`test_migration_apply.py:56` has still never executed anywhere observable** (Docker-gated). The manual
   walkthrough necessarily applied `0003_auth.sql` for login to work at all — stronger evidence than the test
   would have given — but the assertion itself remains unrun.
5. **#26 `CRLF-CHECKSUM-MANIFEST-FRAGILE`** is untouched and remains open.

**Register now stands at 26 tracked — 18 open · 4 discharged (#2 partly, #20 fully, #24 fully, #25 fully) ·
4 narrowed (#3, #8, #18, #19).** ⚑ Count reconciliation: #25 moves **narrowed → discharged**, so narrowed drops
**5 → 4** and discharged rises **3 → 4**; open is **unchanged at 18** and the tracked total is **unchanged at 26**
(18 + 4 + 4 = 26).

**HOLDS**: **no code touched** · no test edited or run · no migration touched · no commit · the login/signup
implementation and the `__main__.py` fix remain **uncommitted** in the working tree, exactly as left.

---

# ⚑ REGISTER UPDATE — 2026-07-26T14:02:44Z · **NO ITEM CHANGES STATUS** · #19's evidence tier upgraded

**This section adds evidence; it supersedes nothing.** It is recorded because the override wiring pass produced the
first live-database exercise of a path #19 already claimed, and because *"no item changed"* is itself a finding that
must be stated with reasons rather than left as silence.

## The evidence — Step 12, user-run against a real local PostgreSQL

Performed by the **user** via **browser, `curl`, and `psql`** at approximate times (~13:5X UTC, 2026-07-26).
**Not observed by the agent**; recorded from the user's report with their identifiers. Three firsts:

1. **`action=override` committed through the browser** (DEMO-0001) with reason *"Manual review required due to
   income discrepancy"* typed in the UI. `AuditRecord` **`a7b67ca8-00a6-4d1d-8e88-a3254c25b0c6`** —
   `underwriter_id=demo-underwriter` (**server-derived**), `action=override`, `reason` = the exact text, **non-null**.
   ⚑ **The first override commit, and the first non-null `reason`, ever persisted in this project.**
2. **Blank-reason rejection over live HTTP** — `curl` on `REC-DEMO-0002-25a195b9`, `reason="   "` → **409
   `commit_conflict`**. ⚑ **The first live-database exercise of BR-COMMIT-GATE's blank-reason rejection.** The UI
   cannot produce this request (the affordance is disabled by construction), so the bypass was deliberate.
3. **Claim-release confirmed** — an immediate valid `approve` re-commit returned **200**, proving the rejected
   override released its claim rather than stranding the case in `committing`.

## Why NO item is discharged or narrowed — each candidate, explicitly

### #19 `COMMITTED-TRANSITION-NEVER-PERFORMED` — **NARROWED, unchanged. Evidence tier upgraded.**

⚑ The decisive detail is in **#19's own record above**, whose "what is now genuinely true" list already includes:

> ✅ an ordinary rejection (**blank-reason override**, unauthorized caller) leaves the case **re-committable**.

Findings **2 + 3** exercise **precisely that bullet, using precisely that blank-reason override** — for the first
time **over live HTTP against a real database**, through the production route rather than a tier-I harness.

**That is an evidence upgrade, not a status change.** #19's recorded non-discharge reason is **cross-store
atomicity**, stated as something *"no wording will make it so"* — and nothing here touches it. **Evidence accrues;
status moves only when the item's own recorded wording is satisfied.**

### #21 `COMMITTING-CRASH-WINDOW` — **OPEN, untouched, and structurally unreachable by this evidence**

#21's window sits **between the frozen service's audit write and U24's `finalize_commit`**. A blank-reason override
is refused by the CON-BR4 gate at **step 1 of `commit()`** — **before** the audit write at step 5. The release path
therefore **never enters #21's window**. This evidence **could not have tested #21 even in principle**, and no
partial credit is claimed for it.

### #13 `NOTWIRED-FILENAME-STALE` — **OPEN, unchanged**

The override pass renamed a frontend test whose name had outlived what it described — the **same class** of defect,
handled in **#13's shape** (superseded in place, old name preserved, reason recorded). But it is a **different
artifact**: #13 is `backend/app/routes/not_wired.py`, a backend file the pass was forbidden to touch. **Citing #13
as precedent is not progress against #13.**

### #2 `R2–R5 unwired` — ⛔ **STILL PARTLY DISCHARGED. Gaps (i) and (ii) CLOSED on live evidence; (iii) OPEN.**

⚑ **UPDATED 2026-08-02 by the register-#2 submission-path pass (WIRE1-Fold-6).** The prior entry is preserved
verbatim below because its reasoning was correct at the time and explains why the qualifier survived so long.

> **SUPERSEDED, preserved**: *"**PARTLY DISCHARGED, unchanged. The strongest remaining candidate.** R5's `override`
> action was **the last route-action never exercised end-to-end**, and it now has been… But #2's residual is
> recorded as *'the end-to-end claim remains scoped per **Q11-A**'* — **a scoping qualifier this pass did not
> re-adjudicate.** Moving a register status on an unread qualifier is exactly what this project forbids. ⚑ **Flagged
> for a future deliberate pass**, not resolved by side effect."*

**That future deliberate pass has now run, and it DID re-adjudicate the qualifier.** Q11-A named three gaps; two are
closed and one is not.

| Q11-A gap | Status | Evidence |
|---|---|---|
| **(i)** no ingestion route | ✅ **CLOSED** | **R10** `POST /applications` + **R11** `POST /applications/{id}/draft`, added by **WIRE1-Fold-6** (R1–R9 verified byte-unchanged at sign-off) and exercised live. |
| **(ii)** not a clickable UI | ✅ **CLOSED for the submit → draft → commit journey** | Submitted in a browser as `demo-underwriter`; `APP-c60445dfd820458295b33849ac8bef7c` drafted and committed through the existing approval gate. ⚠️ **A residual inside this gap is named below.** |
| **(iii)** memo prose is synthetic | ⛔ **OPEN — deliberately, by Q5(a)** | `model_version=OFFLINE-DOUBLE-NOT-A-REAL-LLM`, **read back out of the database** in live check 6. **This is register #18's territory.** |

⛔ **THEREFORE #2 IS NOT FULLY DISCHARGED, AND MUST NOT BE DESCRIBED AS SUCH.** Q5(a) chose the offline double
knowingly — *"free, safe, deterministic … honest by construction"* — over putting an unrated, unrate-limited spend
path behind an HTTP route. **The sequencing was #2 first, then #18**, and the stamp exists precisely so a synthetic
memo cannot be mistaken for a real one anywhere it travels: the API response, the database, and any `AuditRecord` it
is committed into. **A claim of full discharge would be stronger than the evidence supports.**

### ⚑ What the live evidence actually establishes (2026-08-02, user-run; reconstruction, not observation)

1. ⛔ **`engine_version=composition-root-1`** on the persisted case. The seed script stamps `seed-script-1`. **That
   single field is the mechanical proof that U1 `intake` executed in a reachable path for the first time in this
   build's history** — sanitizer, PII guard and SEC-2 validation gate all ran, and the 786 `profile_canonical` bytes
   describe an applicant **the system did not invent**.
2. ⛔ **`AuditRecord 9d39d4e1-9c1a-48c5-99a7-bd362f472b96`**, `application_id=APP-c60445dfd820458295b33849ac8bef7c`,
   `underwriter_id=demo-underwriter`. **The first audit record in this project's history whose lineage traces to an
   application a human submitted through a browser.**
3. **The first outlier score computed for an applicant the system did not invent** — `0.691335220069`, three
   SHAP-explained flags, full provenance triple, 598 persisted bytes.
4. **Rejection**: `requested cover amount = 0` → 400, *"requested cover must be > 0"* rendered **beside the correct
   field**, other values preserved, **no row created**.
5. **Authorization**: auditor 403 on R10 in the UI (no row created) and 403 on R11 by `curl`, the application
   **undisturbed**. ⚑ The R11 attempt landed on an already-`committed` case and was refused **at the role gate**,
   never reaching `draft()` — so the refusal is attributable to authorization alone, not confounded with register
   **#28**'s terminal-state guard.

### ⚠️ THE RESIDUAL INSIDE GAP (ii) — named, not absorbed

**The drafting trigger exists only in the submission view's accepted panel, immediately after submitting.** A pending
case reached any other way — a page reload, *"Submit another application"*, or a seeded `DEMO-*` row — **has no UI
draft affordance anywhere**: the queue offers selection, memo, approve and override, but no trigger.

⚑ **R11 itself is complete and correct**, and the journey this pass exists to demonstrate is clickable end to end.
What is narrower than it sounds is the claim *"the UI can draft any pending case"* — it cannot. **Closing this means
a draft affordance on a pending queue row: a future pass, named here so it is not discovered by someone assuming
otherwise.**

⚑ **Two further limits, carried forward rather than left implicit**: `queueEpoch` refreshes the queue on **submit**,
not on **draft**, so a drafted row's recommendation column stays empty until the next submission or a reload; and
under **Q2(a)** no document can be supplied, so **every** submission through this path yields
`ApplicantProfile.incomplete = true` with all three expected documents `missing`. Both are designed behaviour,
observed live, and recorded so neither is later read as a defect.

### ⛔ A HARD DEPLOYMENT DEPENDENCY THIS PASS CREATED

**`corpus/profiles.json` and `corpus/manifest.json` must be present on the deployed backend.** Outlier scoring is now
reachable over HTTP, so the corpus stopped being a seed-script convenience the moment R11 shipped. If absent, drafting
raises `FileNotFoundError` **by design** — there is no `outlier=null` fallback (Q6(b), refused). Declared as a named,
greppable constant at **`backend/app/outlier_composition.py::CORPUS_ON_RENDER`** and asserted by a test, so it cannot
be deleted silently. ⛔ **`render.yaml` is untouched: placing and verifying the corpus is the deployment pass's work.**

### #14 · #17 — unchanged

**#14** `MEMOVIEW-FAILED-STATE-UNMODELLED`: the `COMMITTING → "pending"` wire projection is untouched.
**#17**: outlier remains unregistered and unmounted — now the **only** case `seams.js`'s exclusion rationale still
describes, the rest of that docstring having been corrected as false in this pass.

> ⛔ **SUPERSEDED 2026-08-13 (outlier mount). The paragraph above is preserved verbatim and was true when written.**
> **#17 is now CLOSED**: the outlier seam **is** registered (`seams.js`, seventh key) and `OutlierView` **is**
> mounted in `App.jsx`'s selection branch, verified live. ⚑ With it, `seams.js`'s exclusion rationale describes
> **no remaining case at all** — its last one — and **there is no unmounted unit left in this build.** The
> superseded comment is preserved in `seams.js` itself rather than deleted. See the #17 row above and
> `guide-state.md`'s outlier-mount entry.

## Count

**Register remains 26 tracked items: 18 open · 4 discharged (#2 partly, #20, #24, #25) · 4 narrowed (#3, #8, #18,
#19).** No change to any figure.

⚑ **What DID change is outside the register**: the brief's **Component 5** requirement — *"override with mandatory
reason field"* — and **§5.6 human-in-the-loop** are now **demonstrated end-to-end on a real database** rather than
asserted from unit tests. Frontend suite **723 / 147 / 0 / 99.82%**. **No commit.**

---

# ⚑ REGISTER UPDATE — 2026-08-01 · item #27 OPENED (a PRE-EXISTING defect, surfaced by the outlier pass's Step 13 verification)

**Opened by**: the user's manual Step 13 verification of the outlier wiring pass, against a real local Postgres.
`psql` confirmed outlier data **was** correctly persisted (`REC-DEMO-0001-bd9e8e6a`, `outlier_canonical` 464 bytes,
`has_outlier = t`) — but `curl GET /applications/DEMO-0001/memo` returned **`outlier: null`** and a **different,
older** `recommendation_id` (`REC-DEMO-0001-6748165d`). `DEMO-0001` was found to hold **FOUR** recommendation rows
accumulated across sessions.

⚑ **Opened only — NOT fixed.** The fix requires reopening frozen `case_lifecycle` (U24) and is withheld.

## #27 `DUPLICATE-PENDING-RECOMMENDATION-ROWS` — ~~**NEW, OPEN**~~ → ✅ **CLOSED 2026-08-01 ON LIVE EVIDENCE**

> ⚑ **Status superseded in place** (original: *"NEW, OPEN"*). Fixed by **U24's FOURTH authorized reopening**
> (`register-27-reopening-authorization.md`, approved 2026-08-01) and **verified against a real local PostgreSQL**
> by the user — see `audit.md` 2026-08-01T16:54:50Z. **Both** of the two defects below are addressed:
>
> * **(i) the unordered lookup** → `_recommendation_row` now issues `ORDER BY recommendation_id LIMIT 1`
>   (change (d)). ⚠️ **This buys DETERMINISM, NOT CHRONOLOGY** — `recommendation_id` carries a random uuid
>   suffix, so it returns a *stable* row, **not** the *newest*. Selecting a genuine "current" row would need a
>   timestamp/sequence column, i.e. a migration, deliberately out of scope. **No claim is made that the "right"
>   row is chosen — only that the same row is chosen every time.**
> * **(ii) the unbounded accumulation** → `submit()` now returns a case unchanged once it has progressed beyond
>   `evaluated` (change (a)), so `draft()`'s guard fires and no second row is inserted.
>
> **Live evidence (user-run, real Postgres)**: reset → **seeded three times in sequence** → runs 2–3 reported
> **`skipped (already drafted)`**, no `FAILED` and no crash → **exactly 1 recommendation row per application** →
> R4 served the single unambiguous recommendation (`REC-DEMO-0001-101871ca`) with full outlier data attached.
>
> ⛔ **NOT claimed**: existing duplicate rows in any deployed database are **not** cleaned up by this fix — that
> remains an operator action. And the general weakness behind #28 (below) is **not** closed.

| | |
|---|---|
| **What it is** | **Two separable defects that compound.** An application may accumulate unboundedly many `pending_recommendation` rows, and the lookup that resolves *"the"* recommendation for an application picks among them **arbitrarily**. |
| ⛔ **Defect (i) — unordered, unlimited lookup over a non-unique column** | `PostgresCaseStore._recommendation_row` (`repository.py:145-149`) issues `SELECT … FROM pending_recommendation WHERE application_id = ?` with **no `ORDER BY` and no `LIMIT`**, then takes `.first()` **in Python**. `application_id` carries **no uniqueness guarantee** — `0001_case_lifecycle.sql` gives it only a **non-unique** `ix_pending_recommendation_application_id` (the PK is `recommendation_id`). **The row served is therefore undefined by SQL semantics.** ⚑ It is **NOT** "the earliest row by ascending PK": the observed oldest-row behaviour is an artifact of Postgres seq-scanning an insert-only table in heap order. A `VACUUM FULL`, an index-only plan, or any row update could change which row is served — **with no code change and no error**. |
| ⛔ **Defect (ii) — a non-idempotent writer paired with a state-resetting upsert** | `put_recommendation` (`repository.py:132`) is a **plain `INSERT`**, while its partner in the same atomic block, `put_application` (`repository.py:84`), is an `INSERT … ON CONFLICT DO UPDATE`. **One half of the transaction is re-run-safe and the other is not.** |
| ⚑ **How the re-draft guard is DEFEATED** | A guard exists and is correct: `pipeline.py:138` runs `assert_legal(application.state, CaseState.DRAFTED)`, and **`(DRAFTED, DRAFTED)` is absent from `LEGAL_TRANSITIONS`** — so re-drafting a drafted case raises. It never fires, because the seed script calls `submit()` first and `put_application`'s conflict clause **includes `state` in its `set_`** (`repository.py:98`), resetting `DRAFTED → EVALUATED`. `(EVALUATED, DRAFTED)` is legal, the guard passes, and a new row lands. **Every seed run = +1 recommendation row, permanently.** |
| **Blast radius — wider than R4** | `recommendation_for_application` is called by **R4** (`not_wired.py:172`), **R2's queue** (`not_wired.py:129` — so queue rows also show an arbitrary `recommendation_id` per application), and **`backend/scripts/reconcile_committing_cases.py:101`**, where a reconciliation step may act on an arbitrarily-chosen row. |
| ⚑ **PREDATES this pass and is UNRELATED to it — confirmed, not assumed** | None of the implicated code was touched by the outlier pass: `_recommendation_row`, `put_recommendation`, `put_application`, `submit`, and `LEGAL_TRANSITIONS` are all unmodified (`git status`). The accumulation itself long predates the pass — the four rows came from repeated testing **across earlier sessions**. |
| ⚑ **Why it surfaced only NOW** | Until this pass, **every** `pending_recommendation` row had `outlier_canonical = NULL`. Serving an arbitrary one of four otherwise-indistinguishable rows had **no observable consequence**. The outlier pass gave the rows a field that differs between them, which made an always-present defect visible for the first time. **The outlier feature itself is working correctly** — the newest row carries real, correctly-quantized, correctly-persisted outlier data. |
| ⛔ **Why NO TEST caught it — the doubles structurally mask it** | Both in-memory stores — `case_lifecycle/tests/fixtures.py:183` and `app/tests/factories.py:213` — implement the lookup as `for rec in self._recommendations.values(): if rec.application_id == application_id: return rec`. They are keyed by **`recommendation_id`** and iterate an **insertion-ordered dict**, so they are **deterministic where Postgres is not** and always return the **first inserted**. The doubles do not merely fail to catch this — they **actively mask it**, and they are keyed differently from the real query they stand in for. ⚑ **A test-double fidelity gap**, reachable only against a real database. |
| **Is multi-row intentional?** | **The schema permits it; nothing consumes it as history.** There is **no timestamp, no version, no `is_current`, and no ordering column** on `pending_recommendation` — so the rows cannot be ordered even in principle. Combined with the deliberate upsert on `put_application` (added for re-seed idempotence) against the plain `INSERT` on `put_recommendation`, the evidence reads as **oversight, not a designed immutable-history model**. |
| **Likely fix — NAMED, EXPLICITLY NOT APPLIED** | Candidates, each with a different blast radius: **(1)** add `ORDER BY` + `LIMIT 1` to `_recommendation_row` — but *nothing exists to order by*, so this requires a new column first; **(2)** make `put_recommendation` an upsert keyed on `application_id` — requires a UNIQUE constraint that does not exist, and forecloses history; **(3)** add a `created_at`/sequence column and serve the latest — a migration plus a lookup change; **(4)** stop `submit()` from resetting `state` on conflict, so the existing re-draft guard actually fires. ⛔ **None applied.** All of (1)–(4) touch **frozen `case_lifecycle` (U24)**, which has already been reopened three times, and (3) additionally needs a new forward migration. Choosing among them is a design decision about whether a recommendation is **replaceable** or **historical** — that question is unanswered and is part of the fix, not a detail of it. |
| **Owner** | `case_lifecycle` (U24) — repository + pipeline + possibly a new migration, **as one authorized reopening** |
| **Blocking?** | **Non-blocking for correctness of any single-seed database**, and non-blocking for the outlier pass, whose feature is confirmed working. ⛔ **But it is blocking for verification hygiene**: any manual check against a repeatedly-seeded database may read a stale row and report a false negative — which is exactly what happened here. **Verify on a freshly-reset database until this is fixed.** |

### ⚑ Verification guidance while #27 stands

⛔ **R4 cannot be addressed by `recommendation_id`.** The full route surface is
`GET /applications`, `GET /applications/{application_id}`, `GET /applications/{application_id}/memo`,
`GET /decisions`, `GET /decisions/{decision_id}`, `GET /session`, `POST /login`, `POST /logout`,
`POST /recommendations/{recommendation_id}/commit`. **R4 takes `application_id` only**, so "curl the specific
recommendation_id instead" is not available as a workaround.

**Therefore**: reset the database, re-run migrations, and **seed exactly once** before any wire verification. Each
application then holds exactly one recommendation and the unordered lookup is unambiguous. Keep `psql` as the
authority on what was persisted; treat `curl` as the wire check **only** on a single-seed database.

---

---

# ⚑ REGISTER UPDATE — 2026-08-01 · item #28 OPENED (a PRE-EXISTING defect, split from #27 per the remediation plan's Q2(a))

**Opened by**: the register #27 scoping investigation. While tracing #27's duplicate rows to their cause, the same
unguarded upsert was found to permit a **strictly more serious** defect that #27's text does not describe. Q2(a)
directed it be **split rather than folded**, because it is a different character of defect: an **illegal write to a
terminal case's state**, not a read-resolution ambiguity.

## #28 `TERMINAL-STATE-RESURRECTION` — **NEW, ✅ CLOSED 2026-08-01 ON LIVE EVIDENCE** (closure condition satisfied — see below)

| | |
|---|---|
| **What it is** | ⛔ **A terminal `COMMITTED` case was silently reset to `EVALUATED` by an ordinary re-submission**, and thereby became re-draftable **after it had already been committed to the audit trail**. `CasePipeline.submit()` built a fresh `PendingApplication` at `EVALUATED` and handed it to `put_application`, whose upsert `set_` includes `state` — so re-submitting **overwrote whatever state the row had reached**, with no transition check of any kind. |
| **Measured, not inferred** | Executed against the real pipeline 2026-08-01: `state before re-submit: COMMITTED` · `is terminal: True` · **`state AFTER re-submit: EVALUATED`**. |
| **Why it is more severe than #27** | #27 is a **read**-side ambiguity — the wrong row is served, but nothing incorrect is written. #28 is a **write**-side state-machine breach: a case the machine calls **terminal** is moved out of that state, and a decision already recorded in `audit_record` can be superseded by a fresh draft. ⚑ Reachability differs too: #27 needs duplicate rows to manifest; **#28 needs only one re-submission of any committed case.** |
| ⚑ **The general weakness behind it** | **`TERMINAL_STATES` (`states.py:94`) is referenced ONLY by tests about itself** — `test_states.py` and `test_failed.py`. **No production code path consults it.** `put_application` applies no transition guard, and `submit()`'s two `assert_legal` calls are **static** (constant-to-constant assertions about the transition table), never about the current row's state. |
| **Same root cause as #27** | Both follow from the unguarded state-writing upsert. One fix (`submit()`'s guard) closes both — which is exactly why splitting them was necessary: a single closed item would have hidden the more serious half inside the less serious one's framing. |
| **Fix** | **U24's FOURTH authorized reopening**, change **(a)**: `submit()` now reads the existing application first and, if it has **progressed beyond `evaluated`**, returns it **unchanged**. ⚑ The guard is in `submit()` and **not** in `put_application`, which must remain state-writing for `draft()`'s `evaluated -> drafted`, `_transition`'s `evaluated -> failed`, and register #19's CAS inside both test doubles. |
| ⛔ **What the fix does NOT close** | **The general hole stays open.** Change (a) closes the **one reachable path** (`submit()`); it does **not** make `TERMINAL_STATES` enforced, and `put_application` remains capable of writing any state to any row. A future caller could reintroduce the same class of defect. **No claim is made otherwise.** |
| **Owner** | `case_lifecycle` (U24) |
| **Blocking?** | **Was non-blocking in practice** (no operator had knowingly re-seeded a committed case), but **audit-integrity in character** — which is why it was split out and classified above #27 rather than folded into it. |

### Closure — ✅ **CONDITION SATISFIED 2026-08-01. CLOSED ON LIVE EVIDENCE.**

**Closed in the same pass that opened it**, which is permissible **only** because both the fix and its live
verification land here: tier-U proof is `case_lifecycle/tests/test_resubmit.py::test_submitting_a_committed_application_does_not_resurrect_it`
(observed RED first — `EVALUATED is not COMMITTED` — then green), and the live proof is the manual verification
step 5 against real Postgres.

⛔ **The stated condition was: "If the live verification is not run, #28 REMAINS OPEN."** ✅ **It was run**
(user-run, real local PostgreSQL, ~16:49–16:54; see `audit.md` 2026-08-01T16:54:50Z), and it passed:

> DEMO-0001 was **committed via R5 (200 OK)**, then the seed script was re-run. It reported
> **`skipped (already committed; not re-drafted)`** — ⚑ naming the **committed** terminal reason specifically,
> distinct from DEMO-0002's ordinary drafted-skip — and **`psql` confirmed `state=committed`, unchanged.**
> **Before this fix that exact sequence silently reset the application to `evaluated`, making an
> already-committed case re-draftable.**

Register **#19 re-confirmed in the same run**: a repeat commit on the same recommendation returned **409
`commit_conflict`** — not a duplicate, not a crash — so the CAS claim is unaffected by this change.

⛔ **STILL NOT CLOSED — the general hole. NOW TRACKED AS ITS OWN ITEM: #29 `TERMINAL-STATE-UNENFORCED`.**
`TERMINAL_STATES` remains consulted by **no production code path**, and `put_application` remains capable of
writing any state to any row. Change (a) closed the **one reachable path** (`submit()`), **not the underlying
capability**. A future caller could reintroduce the same class of defect, and **nothing mechanical would catch
it**. ⚑ Promoted out of this closure text into **#29** so it stays independently triageable rather than being
read as resolved alongside #28 — **#28 is the demonstration; #29 is the capability.**

---

---

# ⚑ REGISTER UPDATE — 2026-08-01 · item #29 OPENED (a RECORDED RESIDUAL of the #27/#28 fix, not a new discovery)

**Opened by**: the register #27/#28 remediation pass, at its close. ⚑ **This is not a newly-found defect.** It is
the **general capability** that made **#28** possible, deliberately promoted out of #28's closure text into its own
item so it stays independently triageable rather than being read as resolved alongside the specific path that was
fixed.

## #29 `TERMINAL-STATE-UNENFORCED` — **NEW, OPEN**

| | |
|---|---|
| **What it is** | ⛔ **Nothing in production enforces the state machine's terminal states.** `TERMINAL_STATES` (`states.py:94`) is declared — `frozenset({COMMITTED, FAILED})`, documented as *"Terminal states — no transition leaves them"* — but it is referenced **only by tests about itself** (`test_states.py`, `test_failed.py`). **No production code path consults it anywhere in the build.** |
| **The capability that follows** | `PostgresCaseStore.put_application` is an `INSERT … ON CONFLICT DO UPDATE` whose `set_` includes `state`, and it applies **no transition guard of any kind**. It can therefore **write any state to any row**, including moving a row *out of* a terminal state, with no error and no trace. |
| ⚑ **Why the guards that exist do not cover it** | `CasePipeline.submit()`'s two `assert_legal` calls are **static** — constant-to-constant assertions about the transition *table*, never about the *current row's* state. `draft()` and `_transition()` do check the live state, but they are callers; **the store primitive they all write through checks nothing.** |
| **Cross-reference — #28 is the demonstration** | **#28 `TERMINAL-STATE-RESURRECTION`** is the one *reachable* exploitation of this capability that was found and fixed: `submit()` reset a terminal `COMMITTED` case to `EVALUATED`, making a case already written to the audit trail re-draftable. ⚑ **#28's fix (change (a)) closed that one path by guarding `submit()`. It did NOT remove the underlying capability** — `put_application` is unchanged and can still do exactly the same thing for any future caller. |
| ⚑ **Why `put_application` was deliberately NOT changed** | It is the **sole state-writing primitive** for `draft()`'s `evaluated -> drafted`, `_transition()`'s `evaluated -> failed`, **and register #19's compare-and-swap inside both in-memory test doubles**. Making it refuse or validate transitions would have broken all three, and the doubles' breakage would have been **invisible at tier-I** (the real `_swap_state` issues its own `UPDATE` and does not route through `put_application`). Guarding the one caller was the correct minimal fix; **closing the general hole is a larger, separate decision.** |
| **What would be needed to close it** | Candidates, none chosen: **(1)** a transition guard inside `put_application` — must exempt or re-route register #19's CAS, and would move state-machine knowledge into the SQL shim, which its own docstring says *"only executes SQL"*; **(2)** split the primitive into a state-writing and a non-state-writing form, widening the change to `store.py`'s Protocol, `repository.py` and both doubles; **(3)** a database-level constraint or trigger — a migration, and therefore an entanglement with register **#26**. ⛔ **All three touch frozen `case_lifecycle` and require their own authorized reopening** (this pass's was U24's fourth). |
| **Detectability** | ⚠️ **None.** `case_lifecycle` is absent from `test_frozen_untouched.py`'s `FROZEN_UNITS`, and no test asserts anything about terminal-state enforcement in production code. A future caller reintroducing #28's defect **would not be caught by any mechanical guard** — only by review. |
| **Owner** | `case_lifecycle` (U24) — a fifth authorized reopening, if taken up |
| **Blocking?** | **Non-blocking, but real.** ⚑ **No other reachable path is currently known to exploit it**: `submit()` was the only caller that wrote a state without checking the live row, and it is now guarded. This is a **latent capability**, not an active defect — recorded so that it is triaged deliberately if a new caller ever writes through `put_application`, rather than rediscovered the way #28 was. |

⚑ **Recorded rather than fixed, deliberately.** The #27/#28 pass was authorized for exactly four frozen files and
six named changes; closing this would have exceeded that scope. Promoting it to its own item is the alternative to
either silently widening an approved reopening or letting the residual disappear inside a closed item's text.

---

---

# ⚑ REGISTER UPDATE — 2026-08-16 · item #32 OPENED (a RECORDED RESIDUAL of the live-LLM-drafting fix, not a new discovery)

**Opened by**: the live-LLM-drafting pass (Ollama, opt-in), at its Stage 5. ⚑ **This is not a newly
found defect.** It is the **general capability** that made the R11 gap possible, deliberately
promoted out of that fix's text into its own item so it stays independently triageable rather than
being read as resolved alongside the specific route that was closed.

⚑ **The shape is deliberately the #28 → #29 one**, and is recorded as such: **#28 was the
demonstration, #29 the capability.** Here the R11 catch is the demonstration and **#32 is the
capability.**

## #32 `UNCAUGHT-EXCEPTION-ESCAPES-ENVELOPE` — **NEW, OPEN**

| | |
|---|---|
| **What it is** | ⛔ **`main.py:97` asserts an invariant that nothing enforces.** The comment above the handler registrations reads *"Every non-2xx leaves as the WIRE-1 §4 envelope — no route can emit a non-contract body."* But `create_app` registers exactly **three** handlers (`main.py:98-100`) — `WireError`, `RequestValidationError`, `StarletteHTTPException` — and **no generic `Exception` handler**. Any other exception escaping a handler is served by Starlette's default error middleware as a **plain-text 500**, which is not the §4 envelope. |
| **How it was found** | By tracing the live-drafting path before wiring a real provider: `orchestrator.py:93` → `:156` → `pipeline.py:186` → `submission.py:212` → `main.py:98-100`, **five layers with no exception handling at any of them**. ⚑ It had been **unreachable in practice**, and for a precise reason — the offline double (`offline_memo_double.py`) returns a fixed string and **cannot fail**. The first real provider is what makes it reachable. |
| **What this pass DID close** | The **one reachable path**: R11 now catches `OllamaUnreachable` and `OllamaCallCapExceeded` **by name** and maps each to a distinct §4-enveloped 500. ⛔ **It did NOT install a generic handler**, per the pass's Q4 answer — *"catch locally in submission.py for this pass … not a generic main.py Exception handler — that's a larger, separate change."* |
| **The capability that remains** | **Every other route** — R1–R9, plus R10 — is still capable of emitting a non-contract body if any exception escapes it. Nothing structural prevents it and nothing tests for it. A future provider, driver, or serialization error on any route reintroduces the same class of defect. |
| ⚠️ **Why a generic handler is not obviously the right fix** | A blanket `Exception` handler makes **every** unexpected error a 500 with a contract body — which is the stated invariant, but also **hides genuine programming errors behind a polite envelope**, and would have swallowed the `ValueError` that `test_a_NON_ollama_exception_is_NOT_swallowed_by_the_catch` deliberately lets escape. ⛔ The right fix likely pairs a generic handler with a **re-raise in test/debug mode**, which is a decision about observability posture, not a one-line addition. |
| **Detectability** | ⚠️ **Partial, and newly so.** No test asserts the invariant across all routes. The pass added `test_an_unreachable_daemon_is_a_500_IN_THE_WIRE1_ENVELOPE` and its sibling, which pin the property **for R11 only**. A route-wide guard — the shape `_PIPELINE_MODULES` and `_FILESYSTEM_WRITE_MODULES` use — does not exist for this. |
| **Owner** | composition root (`backend/app/main.py` + `errors.py`) |
| **Blocking?** | **Non-blocking, but real, and it will get more real.** ⚑ **No other reachable path is currently known to exploit it** — every route's failure modes today go through `WireError` or framework validation. This is a **latent capability**, recorded so it is triaged deliberately when the next fallible dependency lands (Gemini's live path, per register #18's remaining half, is the obvious next candidate) rather than rediscovered the way the drafting path's was. |

⚑ **Recorded rather than fixed, deliberately, and the precedent is explicit.** The live-drafting pass
was authorized for a named scope, and its own Q4 answer drew this boundary in writing before any
code was written. Promoting the residual to its own item is the alternative to either silently
widening an approved scope or letting it disappear inside a closed fix's text — the same reasoning
`#29` records for `put_application`.

**Register now stands at 32 tracked — 21 open · 7 closed/discharged · 4 narrowed (#3, #8, #18, #19).**

---

# ⚑ REGISTER UPDATE — 2026-08-19 · items #33 and #34 OPENED (two PRE-EXISTING defects, surfaced by the live-LLM-drafting pass's §6 manual verification)

**Opened by**: the **USER**, running §6's manual verification against a real local Ollama daemon
(`llama3.1:8b-instruct-q4_K_M`) on application `APP-a930950b04b0496aa87dfa909d30b3e2`. ⛔ **Neither is
a defect this pass introduced.** Both predate it and are recorded as such below; what the pass did was
supply the **first fallible provider in this build's history**, which is what made each reachable.

⚑ **THE CAUSAL CHAIN, NAMED EXPLICITLY SO IT IS NEVER CONFLATED — this is the #28 → #29 shape, with
one capability and TWO distinct causes.** The two failures the user observed were *sequential on the
same application*, which makes them easy to read as one bug. They are not.

| | Role | Item |
|---|---|---|
| **The capability** | An uncaught exception on any route escapes as a plain-text 500, outside the WIRE-1 §4 envelope | **#32** `UNCAUGHT-EXCEPTION-ESCAPES-ENVELOPE` |
| **Cause 1** (attempt 1) | The model was never asked for XML, so the parse of its Markdown answer raised | **#33** `MEMO-XML-CONTRACT-NEVER-REQUESTED` |
| **Cause 2** (attempt 2) | The retry re-invoked a checkpointed LangGraph thread keyed by `application_id`, which raised | **#34** `CHECKPOINT-POISONS-REDRAFT` |

⛔ **Fixing #32 fixes NEITHER #33 NOR #34.** A generic handler would convert both into tidy enveloped
500s — a well-formatted report that the memo still cannot be drafted, and that the application still
cannot be re-drafted. ⚑ Conversely, #33 and #34 are **independent of each other**: each has its own
root cause, its own owner, and its own fix, and either can be fixed without the other. **They are
linked only by sequence — #33's uncaught exception is what left the case in a state where #34 became
reachable.** A future reader must not treat any one of the three as covering another.

## #33 `MEMO-XML-CONTRACT-NEVER-REQUESTED` — **NEW, OPEN**

| | |
|---|---|
| **What it is** | ⛔ **The XML output contract is enforced on the PARSE side only. Nothing anywhere asks the model to produce XML.** `PromptBuilder.build` (`prompt_builder.py:31-50`) emits the system instruction, the read-only recommendation/confidence, the rule report and the applicant facts — **and no output-format instruction, no XML schema, no element names, no example**. Meanwhile `_parse_xml` calls `ElementTree.fromstring(raw_xml)` with **zero tolerance**: no fence-stripping, no preamble-skipping, no block extraction. |
| ⛔ **Provider-independent — confirmed on BOTH adapters** | The identical zero-tolerance parse exists twice: `memo_agent_core/provider.py:64-70` (`GeminiAdapter._parse_xml`) and `memo_extensions/provider_secondary.py:47-55` (the module-level `_parse_xml` that `ClaudeAdapter` **and** `OllamaAdapter` share). Neither client call requests a structured output: `CappedGeminiClient.generate` passes `config={"temperature": temperature}` only (`llm_client.py:76-80`) — **no `response_mime_type`, no `response_schema`** — and `CappedOllamaClient.generate` passes `options={"temperature": temperature}` only (`ollama_client.py:149-155`), with no `format=` argument. ⚑ **This is not an Ollama defect and not a small-model defect.** |
| **How it was found** | §6's manual verification, attempt 1: a genuine Ollama call completed and `_parse_xml` raised `ParseError: not well-formed (invalid token): line 1, column 0`. ⚑ **Confirmed first-hand by probing the live daemon with the exact prompt `PromptBuilder` produces**: at `temperature=0` the model returned a well-formed **Markdown** memo beginning `**ADVISORY MEMO**` — first three characters `'**A'`, which is precisely what produces "invalid token: line 1, column 0". ⛔ **The model behaved correctly.** It was asked for "a concise, audit-ready ADVISORY memo" and wrote one; it was never told to emit XML. |
| ⚠️ **Why no amount of parser tolerance fixes this alone** | The failure is **not** markdown code-fencing around XML, and **not** a conversational preamble before the tags — the two quirks a defensive parser would strip. **There is no XML in the output at all.** A tolerant parser has nothing to find. |
| **Why it was never visible** | `offline_memo_double.py:79-84` returns a **hardcoded, always-valid** XML string. Every memo this build has ever produced through the request path came from it. The XML contract has therefore been satisfied by a fixture, never by a model. |
| ⛔ **Blocking, and it blocks BOTH providers** | **This is why no live memo has ever been successfully produced by either Gemini or Ollama.** Live drafting cannot succeed on any provider until this is closed. |
| ⚑ **Cross-reference: register #18 `NO-PRODUCTION-LLMCLIENT`** | #18's remaining half — Gemini's production client, **unproven through the request path** (Q6 A) — **would hit this identically on its first real call.** The Gemini path's `# pragma: no cover` real-spend branches have never executed against a live model, so nothing has ever exercised `GeminiAdapter._parse_xml` on real model output either. ⚠️ **#18 gap (iii) cannot move for EITHER provider until #33 is closed.** |
| **Detectability** | ⛔ **None today.** No test asserts that the prompt requests a parseable format, and no test feeds realistic model prose to `_parse_xml`. Every adapter test injects a double that returns valid XML by construction — which is exactly why a defect in the *request* side is invisible to a suite that only ever exercises the *parse* side. |
| **Owner** | `backend/memo_agent_core/prompt_builder.py` (frozen unit) and/or the two client wrappers (`app/llm_client.py`, `app/ollama_client.py`) — ⚠️ **the choice of owner IS the design decision**, see the fix candidates. |
| **Blocking?** | ⛔ **YES — blocking for live drafting on any provider.** |

## #34 `CHECKPOINT-POISONS-REDRAFT` — **NEW, OPEN**

| | |
|---|---|
| **What it is** | ⛔ **`LangGraphOrchestrator` compiles its graph with `checkpointer=MemorySaver()` (`orchestrator.py:137`) and uses the `application_id` AS the LangGraph `thread_id` (`orchestrator.py:155`).** One orchestrator is built at `dependencies.py:369` behind `@lru_cache(maxsize=1)`, so **one `MemorySaver` lives for the whole server process**. Any **second** `invoke` on an `application_id` that already has a checkpoint raises `RuntimeError: recommendation/confidence are read-only channels (CON-BR2-STATE); no node may write them`. |
| **The mechanism, exactly** | `orchestrator.py:11-13` states the load-bearing assumption: *"Seeding at invoke is allowed (LangGraph does not run the reducer on the initial input)."* ⚑ **That is true only for a thread with NO checkpoint.** In `langgraph 1.2.7`: `BinaryOperatorAggregate.update()` bypasses the reducer only when `self.value is MISSING` (an empty channel), while `from_checkpoint()` sets `empty.value = checkpoint` — so a **restored** channel is not MISSING, seeding takes the reducer branch, and `_reject_channel_write` fires. |
| ⛔ **The hypothesis it disproves** | This is **not** a stale or partial checkpoint left by a *failed* attempt. **Reproduced both ways**: a first attempt that **fully succeeds** poisons the thread identically to one that fails. The rule is simply **"any completed invoke leaves a checkpoint; any second invoke on that `thread_id` raises."** The Ollama failure corrupted nothing — it merely created the first-ever occasion to invoke twice on one `application_id`. |
| ⛔ **It violates `CasePipeline.draft()`'s own stated contract** | `pipeline.py:155` declares the method *"never raises for a domain failure"*, and `DraftOutcome.skipped` exists (register #27, change (c)) precisely so that *"RE-TRIGGERING IS IDEMPOTENT, NOT A FAILURE"* (`submission.py` R11 docstring). ⛔ **A retry that raises an unrelated `RuntimeError` breaks both promises at once.** |
| ⚠️ **The error message actively misdirects** | It names **CON-BR2-STATE** and reads as a governance violation — as though a node had written to a read-only channel. ⛔ **No node wrote anything.** Nothing violated CON-BR2-STATE; the reducer fired on the *seed*, not on a node return. An operator or auditor reading this traceback would reasonably conclude the recommendation-immutability guarantee had been breached, which is **false** — the most expensive possible misreading in a system whose core claim is that the recommendation cannot change. |
| **Scope of the damage** | ⚠️ **Per-process, not permanent.** `MemorySaver` is in-memory: a server restart clears every checkpoint, and nothing else does — there is **no eviction, no TTL, no clear path**. So the accurate statement is *"that application cannot be drafted again until the process is bounced."* ⛔ **Unbounded growth**: one checkpoint accumulates per application drafted, for the life of the process. |
| **How it was found** | §6's manual verification, attempt 2 — retrying the same `APP-a930950b04b0496aa87dfa909d30b3e2` after #33's failure, preceded by a cluster of checkpoint-deserialization warnings for `backend.intake.schema.Gender` / `DocType` / `DocStatus` and several `rules_engine` / `memo_agent_core` types. ⚑ **Reproduced first-hand in-memory against the real orchestrator, emitting the identical warning cluster and the identical `RuntimeError`.** |
| ⛔ **PRE-EXISTING since the original build — and the git history is the finding** | `orchestrator.py` is **untouched by the live-LLM-drafting pass**, and `git log --follow` dates both the checkpointer and `thread_id=application_id` to **`51935ac`, the original BUILD-phase commit.** ⚑ **In `51935ac` this was reachable by a much shorter route**: `pipeline.draft()` called `draft_memo` at `:116` and only reached `assert_legal` at `:138` — **the legality guard sat BELOW the LLM call**, so any repeat draft would have invoked the orchestrator twice and raised. ⛔ **Register #27's pass (`3a08dd8`) moved that guard above `draft_memo` for entirely unrelated reasons** (dead-code revival + not spending money on a memo the refusal discards) **and in doing so INCIDENTALLY closed the only then-reachable route to this bug.** That reordering is why it was never observed — not any property of the design. |
| **What re-opened the route** | ⚑ #33's uncaught `ParseError` propagates out of `draft_memo`, **bypassing the `memo is None` → `FAILED` transition entirely** (`pipeline.py:187-193`). The case therefore stays `evaluated`, so `is_legal(evaluated → DRAFTED)` at `pipeline.py:173` is **still true** on the retry, `draft_memo` runs a second time, and the orchestrator is invoked twice on one `thread_id`. ⛔ **This is the sole linkage between #33 and #34** — sequence, not shared cause. |
| ⚑ **Cross-reference: register #32** | #32 is **the capability that lets this escape as a plain-text 500**. The R11 catch names `OllamaUnreachable` and `OllamaCallCapExceeded` only; a bare `RuntimeError` is neither (⚠️ note `OllamaCallCapExceeded` *is* a `RuntimeError` subclass, but the catch is by the named type, so a plain `RuntimeError` is correctly **not** caught). ⛔ **#32's own row predicted exactly this**: *"A future provider, driver, or serialization error on any route reintroduces the same class of defect."* It did — twice, in one sitting. |
| **Detectability** | ⛔ **None today.** A repo-wide grep finds **no test anywhere** referencing `thread_id`, `MemorySaver` or graph checkpointing in relation to the orchestrator. Every orchestrator test builds a **fresh** `LangGraphOrchestrator` (hence a fresh `MemorySaver`) and calls `run()` **exactly once**. ⚠️ `test_read_only_channel_reducer_raises_on_write` calls `_reject_channel_write` **directly** — so the reducer's raise is pinned in isolation, while **the condition under which the graph actually calls it has never been exercised.** |
| **Owner** | `backend/memo_agent_core/orchestrator.py` — ⛔ **a FROZEN unit** (`memo_agent_core` is in `FROZEN_UNITS`), which is the central constraint on every fix candidate. |
| **Blocking?** | ⛔ **YES for re-drafting, and it will become blocking for normal operation the moment #33 is fixed and a case can legitimately be drafted more than once per process.** |

⛔ **Recorded rather than fixed, deliberately.** Two blocking, independent findings with real design
tradeoffs — one of which touches a frozen unit — are not an ad hoc patch on an already-large
six-stage pass. **They get their own scoping pass**, on the same reasoning `#27`/`#28` were split
from their remediation and `#32` from the fix that surfaced it.

**Register now stands at 34 tracked — 23 open · 7 closed/discharged · 4 narrowed (#3, #8, #18, #19).**
⚠️ **This supersedes the "32 tracked — 21 open" figure** recorded at this file's #32 entry and at
`guide-state.md:7454`; both were correct when written. ⚑ The breakdown remains **derived from the
running tallies**, not from a re-enumeration of all 34 rows — stated so a future reader knows which
it is, exactly as the #32 entry stated it.

---

# ⚑ REGISTER UPDATE — 2026-09-12 · item #35 OPENED **and** CLOSED · **#34 CLOSED (tier-U)** · ⛔ **#33 NOT CLOSED** — the registers #33/#34 code-gen pass, stages 1 and 2

**Pass**: `register-33-34-code-gen-plan.md`, executed against the signed
`register-33-34-reopening-authorization.md` — ⛔ **this project's FIRST authorized reopening of a
frozen unit's source logic.** Four files, changes (a)–(m). HEAD `bd3875d`; **not committed.**

⚠️ **Stage 1 was executed by a session that was cut off by a usage limit and logged nothing.** Its
work was verified from disk and reconstructed at `audit.md` 2026-09-12T12:09:05Z, which is also
explicit about the one artefact that is **lost and deliberately not fabricated** — stop-gate 1's
original RED observation.

---

## #35 `OFFLINE-DOUBLE-CITES-THE-RECOMMENDATION` — **NEW, OPENED AND CLOSED IN THIS PASS**

⚑ **The `#24` shape**: opened and closed in one act, because the fix landed with the discovery.
⚠️ **Opened at STAGE 2 rather than at scoping** (§6.5, approved at sign-off) so the row could be
written alongside its fix rather than as a promise.

| | |
|---|---|
| **What it is** | ⛔ **`offline_memo_double.first_cited_rule_id` searched the WHOLE prompt for a rule id.** `PromptBuilder.build()` writes `RECOMMENDATION (read-only): <value>` **above** the rule report, and `Recommendation.DECLINE_RECOMMEND.value` is `"DECLINE-RECOMMEND"` — which the module's rule-id regex `\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b` **matches**. So the extracted "citation" was the recommendation itself. |
| ⛔ **The consequence, and why it was invisible** | `CitationValidator` correctly rejected the fabricated id — it is not in the handed report — so the memo was blocked and ⛔ **every `DECLINE-RECOMMEND` case through the offline double silently landed in `FAILED`.** ⚠️ **No error, no log line, no test.** The case simply never produced a memo. |
| ⚠️ **`APPROVE` and `REFER` escaped by LUCK, not correctness** | Their enum values contain **no hyphen**, so the regex — which requires one — could not match them. ⛔ **A single hyphen in a future recommendation value would have reproduced this**, which is why the regression test is parametrized over **every** `Recommendation` value rather than the one that broke. |
| ⛔ **Zero test coverage of the failing path** | `offline_memo_double.py` stood at **11/11 statements, 100%** — ⚠️ **and was still wrong.** ⛔ **This is the finding worth carrying forward**: the module was fully line-covered, and no test ever fed it a `DECLINE-RECOMMEND` prompt. **100% line coverage measured the lines, not the inputs.** |
| ⚑ **THE SAME DEFECT CLASS AS `DTI-001` — in the file whose own docstring records fixing it once** | `first_cited_rule_id`'s docstring describes DEFECT FIX 2: a hardcoded `DTI-001` that does not exist in this build, which made every emitted `<rule_id>` empty so *"every seeded case silently landed in `FAILED`"*. ⛔ **#35 is that defect again — same file, same symptom, same silence — with a *discovered* wrong id instead of a *hardcoded* wrong id.** ⚠️ The fix that produced the docstring addressed the instance, not the class: **nothing asserted that what came out was a rule id from the handed report.** That invariant is now a test. |
| **Pre-existing since** | ⛔ **`51935ac`, the original BUILD-phase commit** — the same commit that carries #34. Untouched by the live-LLM-drafting pass. |
| **The duplicate** | ⚠️ `backend/scripts/seed_demo_cases.py:118` carries a **second copy** of this double, disclosed deliberately at `offline_memo_double.py:28-32` (*"the two must stay behaviourally equivalent; if they drift, this one governs the request path"*). ⛔ **It had the identical defect and is fixed identically.** ⚑ Equivalence is now **enforced by a test** parametrized over every `Recommendation` — previously **nothing** enforced it. ⚠️ `backend/scripts/` is in no `--cov=` entry, so the mirror is **tested but not measured**; pre-existing and correct, not an omission. |
| **How it was found** | ⚑ The grounding pass for the #33/#34 scoping plan (finding A), **before** any code was written — while checking whether X1's future worked example could be mis-extracted. ⛔ **The live defect was found by looking for a hypothetical one.** |
| ✅ **The fix** | **Extraction is bounded at BOTH ends** (§6.1, approved at sign-off): it searches only between the `RULE REPORT (the only citable rules):` and `APPLICANT FACTS (non-demographic):` markers. ⚠️ **A missing marker returns `""`** rather than falling back to a whole-prompt search — failing closed, because a prompt of an unknown shape cannot be reasoned about and guessing would fabricate a citation. |
| ⚑ **Why BOTH ends, when one would fix the observed bug** | A start bound alone stops the recommendation leak but leaves the region running to the end of the prompt — so X1's `REQUIRED OUTPUT FORMAT` block, appended **after** the applicant facts, would fall inside it and its worked example would be cited instead. ⛔ **Bounding both ends keeps that out INDEPENDENTLY of the `EXAMPLE_RULE_ID` placeholder's underscore**, which is the second defense. **Neither depends on the other** — which is what Q2 required and what single-ended anchoring would have quietly broken. |
| **Detectability now** | ✅ A citation-invariant test **parametrized over every `Recommendation` value plus the empty-rule-report case**, asserting the extracted id is a member of the handed report's ids or `""`. ⚑ **The empty-report cell is not padding** — it is the cell that exposes single-ended anchoring. Plus both marker-guard branches, and the mirror-equivalence test. |
| **Owner** | `backend/app/offline_memo_double.py` (governs the request path) · `backend/scripts/seed_demo_cases.py` (mirror). ⚑ **Neither is a frozen unit** — #35's fix needed no part of the reopening authorization. |
| ✅ **Status** | **CLOSED.** ⚑ **Observed RED first** (2026-09-12): `AssertionError: DECLINE-RECOMMEND: extracted 'DECLINE-RECOMMEND', which is not one of the citable rule ids ['R-AGE-1', 'R-DTI-1'] — a fabricated citation`, then GREEN on all four parametrizations after the fix. ⛔ **Closed at tier-U.** ⚠️ §7 step 6 — drafting a `DECLINE-RECOMMEND` case through the offline double — has **never once succeeded in this build's history** and has not been run. |

---

## #34 `CHECKPOINT-POISONS-REDRAFT` — ✅ **CLOSED (tier-U only)**

| | |
|---|---|
| ✅ **The fix** | Candidate **C2**: `graph.compile(checkpointer=MemorySaver())` → `graph.compile()`, and the `MemorySaver` import removed. ⛔ **The checkpointer is gone, not guarded** — a guard would have left the mechanism in place for the `3a08dd8` failure mode to re-mask. |
| ⛔ **All three justifications for the checkpointer were FALSE, and the docstrings now say so rather than going silent** | *retry loop* — the `add_conditional_edges` cycle is plain graph state; ⚑ **reproduced working with no checkpointer at all** (bad-then-good provider → 2 calls, memo finalized). *durability* — `MemorySaver` is in-process, and ⛔ **nothing anywhere ever read a checkpoint back**: no `get_state`, `update_state`, `get_state_history`, `.stream`, `astream` or `interrupt` exists in this repository. *100%-step tracing* — ⛔ tracing was **never** wired through the checkpointer; `observability.TraceRecorder.on_step` has **no production caller at all**. ⚠️ **That last claim was false BEFORE C2** and is owned by OBS-SINK-DEFERRED, not by this pass. |
| ⚠️ **A narrower CON-BR2-STATE claim, preserved rather than deleted** | `orchestrator.py:11-13` said *"LangGraph does not run the reducer on the initial input."* ⚑ **True only for a thread whose channels are `MISSING`.** It was affirmatively tested at build time (`audit.md:760`) — but that test compiled its graph **without** a checkpointer, so **the no-checkpoint case was the only one ever exercised.** ⛔ **What CON-BR2-STATE actually rests on is unchanged and still true**: no node returns those keys, so the recommendation cannot change inside the graph. |
| **Regression protection** | Q9-D's **four independent layers**, each killing a different wrong implementation: (i) a real citation-valid memo on **both** invokes; (ii) ⛔ `_graph.checkpointer is None` — the **structural** pin against a reintroduction re-masked by a guard elsewhere; (iii) identical `memo_hash`; (iv) ⛔ **the provider call count increments** — which kills the memoizer strawman that satisfies (i)+(ii)+(iii) while reintroducing the defect in another form. |
| **Design record** | ✅ **All eight false design-doc statements back-annotated** across five files under six dated markers, **disk-verified by grep**: 18 surviving `checkpointer` hits, every one inside a back-annotation. ⚠️ Four of the eight carry the Langfuse claim, and each back-annotation states it was false **BEFORE** C2 rather than implying C2 caused it. |
| ⚠️ **CLOSED AT TIER-U ONLY** | ⛔ **No live re-draft has been performed.** The suite proves the graph has no checkpointer and that two in-process invokes both succeed. §7 step 5 — drafting the same application twice against a real stack — **has never once succeeded in this build's history** and has not been run. |
| ⛔ **What is LOST from this closure's evidence** | Stage 1's original stop-gate-1 RED observation — the exact `RuntimeError` on invoke #2 — was **never logged** by the interrupted session. It is **not reconstructed**, because regenerating it would mean reverting working code. ⚑ The post-condition is independently verified (the test exists, is non-vacuous by construction, and is green); ⚠️ **that proves the fix works, not that the test once failed.** |

---

## #33 `MEMO-XML-CONTRACT-NEVER-REQUESTED` — ⛔ **STILL OPEN. NOT CLOSED BY THIS PASS.**

✅ **What landed**: **(j)** a binding sentence in `_SYSTEM_PROMPT` requiring XML and nothing else,
appended **after** — never substituted for — the four pre-existing constraints; **(k)** a
`REQUIRED OUTPUT FORMAT:` block appended **last** in `build()`, naming the **exact** element names
the parser reads by path; **(l)** the `EXAMPLE_RULE_ID` placeholder, underscored so it cannot match
the rule-id regex; **(f)(g)** shared **subtractive** parse tolerance — fences, preambles, trailing
commentary — in **both** parsers, imported rather than copied; **(h)** a named
`MemoDocumentShapeError` for well-formed XML of the wrong shape.

⛔ **WHY THIS IS NOT A CLOSURE, STATED PLAINLY.** X1 changes **what is asked of a model**, and
⛔ **no unit test can verify that a model complies.** The suite proves the instruction is *present*,
that the parser *tolerates* what a model plausibly returns, and that nothing regressed. ⚠️ **A green
suite is not evidence that a real model now returns parseable XML.** ⚑ **Only §7's live verification
can show a real memo**, and it has not been run.

⚑ **What the suite DOES now prove, which nothing did before**: parse behaviour is exercised **at
all**. ⛔ **Before this pass no test anywhere referenced `_parse_xml`** — which is exactly how #33
reached a live call undetected.

⚠️ **Two things (h) deliberately does NOT do.** It does **not** fire when a model genuinely cites
nothing — prose plus an empty `<cited_rule_ids/>` is a legitimate draft for `CitationValidator` to
block **on the merits**, and collapsing those two cases would destroy the distinction (h) exists to
draw. And it is a `ValueError`, **not** a `ParseError`: *"not XML"* and *"XML of the wrong shape"*
stay different failures with different types.

⚑ **Cross-reference: #18 gap (iii) has NOT moved.** Gemini's production client remains unproven
through the request path. ⚠️ **X3 makes both providers more likely to survive a first real call; it
does not constitute evidence that either has made one.**

---

## Register reconciliation

⛔ **REGISTER NOW STANDS AT 35 TRACKED — 22 open · 9 closed/discharged · 4 narrowed (#3, #8, #18, #19).**

Movement in this pass: **#35 opens and closes** (tracked 34 → 35; closed +1). **#34 closes**
(open −1, closed +1). **#33 stays open.** So open goes **23 → 22** and closed/discharged **7 → 9**
(22 + 9 + 4 = 35).

⚠️ **This supersedes the "34 tracked — 23 open" figure** recorded at this file's #33/#34 entry;
it was correct when written. ⚑ The breakdown remains **derived from the running tallies**, not from
a re-enumeration of all 35 rows — stated so a future reader knows which it is, exactly as the #32
and #34 entries stated it.

⛔ **`guide-state.md` IS NOW STALE BY THREE** — it still reads *"32 tracked — 21 open"*. ⚠️ **Left
uncorrected here, deliberately and per standing direction**, and flagged rather than silently
carried: a documentation-sync task owns it, together with the two other known documentation states
(the outlier-mount entry's stale *"HEAD is `d43b661`"* / *"NOT COMMITTED"*, and this file's §5
register table still headed *"20 items"* with no rows for #26–#31).

---

# ⚑ REGISTER #33 / #34 / #35 — **FINAL EXECUTION STATE** (supersedes the counts in the entry above)

⚠️ **The entry above was written mid-execution, before the §11 gate.** Its substance stands; its
**numbers and its account of what the gates caught are superseded here.** ⛔ **Nothing below claims
live verification.**

## ⛔ TIER-U / TIER-I GREEN ONLY — LIVE VERIFICATION PENDING

| | |
|---|---|
| **Backend** | **1892 passed · 0 failed · 45 skipped · 5 errors · 99.36%** (the 5 errors are the standing `audit_store` Docker-absence set, unchanged by name) |
| **Frontend** | **823 / 155** — ⚑ an **exact** baseline match; nothing in this pass touches the frontend |
| **Plan** | **All 48 checkboxes `[x]`, zero unchecked**, both stages, all 11 steps |
| **Coverage** | `memo_agent_core` **12/12 at 100%** · `memo_extensions` **5/5 at 100%** · `offline_memo_double.py` **20/0/4/0 = 100%** · total **99.36%, identical to baseline**. ⛔ Thresholds unedited; **no `# pragma: no cover` added anywhere** |
| **Git** | HEAD `bd3875d` · nothing staged · ⛔ **NOT COMMITTED** |
| ⛔ **§7 manual verification** | **NOT RUN.** ⚠️ **No claim anywhere in this pass rests on live evidence.** |

⛔ **WHAT A GREEN SUITE HERE DOES NOT MEAN.** It is **not** evidence that a real model returned
parseable XML, **not** evidence that a re-draft succeeded against a real stack, and **not** evidence
that a `DECLINE-RECOMMEND` case produced a memo end to end. ⚑ **All three are §7's job**, and §7
carries ⛔ **two checks that have never once succeeded in this build's history.**

## ⛔ A structural guard fired — and it was NOT one of the plan's ten stop-gates

At the §11 gate, **`test_frozen_untouched.py::test_no_frozen_unit_imports_the_composition_root`**
went RED: step 7.5's new test had placed `from backend.app.offline_memo_double import
_RULE_ID_PATTERN` inside `backend/memo_agent_core/tests/test_prompt_builder.py` — ⛔ **a file in the
FROZEN tree importing the COMPOSITION ROOT**, against the guard's stated rule that *"the dependency
arrow points ONE way: app → units."*

✅ **Resolution: the test moved; the guard was not touched.** The cross-unit assertion now lives on
the app side where importing both directions is legitimate, and the frozen-tree test keeps only the
unit-local property. ⚑ A further test came out of the fix, exercising **both** #35 defenses at once.

⚠️ **THE PART WORTH CARRYING FORWARD.** ⛔ **This was not stop-gate 5.** Stop-gate 5
(`memo_extensions` Scans 1 and 7) passed **cleanly** — §6.2's analysis of the frozen edge was
correct. ⚑ **The violation was caught by a PRE-EXISTING guard that is not among the plan's ten
numbered stop-gates at all.** The plan anticipated import trouble at the `memo_extensions` boundary
and cleared it; ⛔ **it did not anticipate the frozen unit's own TEST directory having an import
rule.** It held because someone had written that guard earlier, for an unrelated reason.
**A plan's stop-gates are not the whole safety net.**

## ⛔ Variance — predicted +26 (→1863), measured +55 (→1892)

| Source | Tests |
|---|---|
| `test_orchestrator_redraft.py` (new) | **4** — ⚑ **exactly as predicted** |
| `test_offline_double_citation_invariant.py` (new) | **11** |
| `test_parse_tolerance.py` (new, U19) | **20** |
| `test_provider.py` (extended) | **+14** |
| `test_prompt_builder.py` (extended) | **+5** |
| `test_submission_routes.py` (extended) | **+1** |
| **Total** | **+55** |

⚑ **The plan diagnosed its own miss in advance**: *"a plan bullet names an idea; the implementation
needs several assertions to pin it."* Parametrization did most of it — §8.1 listed six shapes, and
across **two** adapters that is 20. ⛔ **No test was trimmed to approach the number.** ⚠️ **Stage 1's
+4 was exact** — the one stage whose count Q9-D fixed upstream rather than leaving to implementation.
⚑ **This is the THIRD consecutive pass to miss low for this same reason** (Fold-7 +48→+84;
live-LLM-drafting +48→+63), which makes it a property of how these plans are written, not bad luck.

## Status of each item, restated at final state

| Item | Status |
|---|---|
| **#35** `OFFLINE-DOUBLE-CITES-THE-RECOMMENDATION` | ✅ **CLOSED — tier-U.** Observed RED first, then green on all four parametrizations plus both marker guards. ⚠️ §7 step 6 has **never once succeeded** and has not been run. |
| **#34** `CHECKPOINT-POISONS-REDRAFT` | ✅ **CLOSED — ⚠️ TIER-U ONLY.** The graph structurally has no checkpointer and two in-process invokes both succeed. ⛔ **No live re-draft.** §7 step 5 has **never once succeeded** and has not been run. ⚠️ Its evidence is also **missing stage 1's original stop-gate-1 RED**, never logged and deliberately not reconstructed. |
| **#33** `MEMO-XML-CONTRACT-NEVER-REQUESTED` | ⛔ **OPEN. NOT CLOSED BY THIS PASS.** X1 changes what is *asked* of a model and ⛔ **no unit test can verify a model complies.** ⚑ What is new: parse behaviour is exercised **at all** — before this pass **no test anywhere referenced `_parse_xml`**, which is how #33 reached a live call undetected. |
| **#18** `NO-PRODUCTION-LLMCLIENT` gap (iii) | ⛔ **HAS NOT MOVED.** ⚠️ X3 makes both providers more likely to survive a first real call; **that is not evidence either has made one.** |
| **#22** `MEMO-PROSE-NOT-BIT-REPRODUCIBLE` | **OPEN, untouched.** §7's two-draft probe is an **observation**; differing prose is a finding about #22, not a failure of this pass. |

⛔ **REGISTER STANDS AT 35 TRACKED — 22 open · 9 closed/discharged · 4 narrowed (#3, #8, #18, #19).**
⚑ Derived from the running tallies, not from a re-enumeration of all 35 rows — stated so a future
reader knows which it is.

⛔ **`guide-state.md` REMAINS STALE BY THREE** (*"32 tracked — 21 open"*). ⚠️ **Flagged, not corrected
here**, per standing direction; a documentation-sync task owns it alongside the outlier-mount entry's
stale *"HEAD is `d43b661`"* and this file's §5 table still headed *"20 items"*.

⚑ **The durable lesson from #35, recorded because it generalizes past this pass**:
`offline_memo_double.py` stood at **11/11 statements, 100% — and was still wrong.**
⛔ **The coverage measured the LINES, not the INPUTS.** No test had ever handed it a
`DECLINE-RECOMMEND` prompt. ⚠️ A unit at 100% is not a unit that has been asked the right questions.

---

# ✅ REGISTER UPDATE — 2026-09-12 · **§7 LIVE VERIFICATION COMPLETE** · **#33 CLOSED ON LIVE EVIDENCE** · **#35 LIVE-CONFIRMED** · ⚠️ **#34 NOT UPGRADED — the evidence does not reach it** · **#22 now has measured negative evidence**

**Performed by the USER** via browser, `curl` and `psql` against a **real local PostgreSQL** and a
**real local Ollama daemon** (`llama3.1:8b-instruct-q4_K_M`). ⚠️ **Not observed by this agent**;
values are as reported. Full walkthrough and verbatim report: `audit.md` 2026-09-12T18:15:54Z.
⛔ **Still NOT COMMITTED** — HEAD `bd3875d`.

---

## ✅ #33 `MEMO-XML-CONTRACT-NEVER-REQUESTED` — **CLOSED ON LIVE EVIDENCE**

⚑ **This is the first time in this project's history that a real language model's memo prose has
reached the screen**, and ⛔ **#33 is the one item of the three that a test suite structurally could
NOT have closed** — the code-gen plan's §1.1 said so before execution: *"X1 changes what is asked of
a model, and no unit test can verify that a model complies."*

| | |
|---|---|
| **Application** | `APP-47bb6f55edec4eca86294d317a0c6883`, submitted fresh through the browser and drafted from the accepted panel |
| ✅ **The prose** | **Genuinely model-written** — ⛔ **not** the `PLACEHOLDER MEMO` text — and it synthesized all **seven** actual rule failures coherently |
| ✅ **The citations** | **Seven, all REAL rulebook ids matching the actual `rule_results`**: `AGE-BAND-1`, `BMI-OBESE-1`, `DOCS-COMPLETE-1`, `DTI-CEIL-1`, `IRDAI-EMP-SALARIED-1`, `OCC-LOWRISK-1`, `SMOKE-STATUS-1`. ⛔ **No hallucinated id. No leaked `EXAMPLE_RULE_ID`.** Both X1 defenses held live. |
| ✅ **The stamp** | `NOT-QUALITY-GATED+llama3.1:8b-instruct-q4_K_M+digest-unavailable+ollama-python-0.6.2`, **byte-identical** between `psql` (`pending_recommendation`) and **`curl` R4, pre-commit** — confirming §4.0(i)'s correction that the stamp is verifiable one step earlier than assumed |
| ⚠️ **What closure does NOT assert** | One successful call is **not** a compliance guarantee. The honest claim is *"a real model produced valid, correctly-cited XML through the full request path"* — ⛔ **not** *"the model always complies."* |

---

## ⚠️ #34 `CHECKPOINT-POISONS-REDRAFT` — ⛔ **NOT UPGRADED. STILL TIER-U FOR THE FIX ITSELF.**

⛔ **An upgrade to LIVE-CONFIRMED was requested and is DECLINED on evidentiary grounds** — recorded
as not-reached rather than performed-with-a-caveat, because a false entry in this register is
exactly what the project's verification discipline exists to prevent.

| | |
|---|---|
| **What was run** | Re-drafted `APP-47bb6f55…` a second time via `POST /applications/{id}/draft` |
| **Result** | `{"status": "ready", "outcome": "skipped"}` — clean, no exception, no `RuntimeError` |
| ⛔ **Why this does NOT reach #34** | `pipeline.draft()` places the `is_legal` guard at its **TOP**, above `draft_memo` (`pipeline.py:173`, U24's fourth reopening change (b)). **`skipped` means the guard short-circuited and `draft_memo` was NEVER CALLED** — the orchestrator was **never invoked a second time**, so ⛔ **the checkpointer path was never reached.** |
| ⚠️ **Why Part D does not close it either** | There was a **backend RESTART between steps 13 and 15**, and `MemorySaver` is **in-process** — a restart clears every checkpoint, so a post-restart draft cannot demonstrate the fix. |
| ⚑ **This is the shape #34's OWN row already predicted** | *"`3a08dd8` moved that guard above `draft_memo` … and in doing so INCIDENTALLY closed the only then-reachable route to this bug."* ⛔ **Now that #33 is fixed, drafting SUCCEEDS, the case reaches `DRAFTED`, and the HTTP path can no longer reach a double-invoke at all.** |
| ✅ **What IS live-confirmed** | **The ROUTE IS CLOSED.** In normal operation no HTTP caller can invoke the orchestrator twice on one `application_id`. ⚑ Part B also genuinely confirms **register #27's idempotency contract** live — *"RE-TRIGGERING IS IDEMPOTENT, NOT A FAILURE"* — a real and worthwhile result, but **a different claim.** |
| ⚠️ **What remains TIER-U ONLY** | That a double invoke **no longer raises**. Proven by `test_orchestrator_redraft.py`'s four layers, which invoke the orchestrator twice **in-process** and so do reach the path the live run did not. |

### ⚑ The run that WOULD close #34 live — derived from the state table, not guessed

`LEGAL_TRANSITIONS` (`case_lifecycle/states.py:81-85`) contains `(EVALUATED, DRAFTED)` but **not**
`(DRAFTED, DRAFTED)` and **not** `(FAILED, DRAFTED)`. ⛔ **So the only live route to a second
`draft_memo` on one application is a first attempt that leaves the case in `EVALUATED` — one that
raises BEFORE any transition.** ⚑ An Ollama outage does exactly that, and Part D step 13 produced
it. **The missing run is two draft attempts on one application in ONE process, with NO restart:**

1. `MEMO_PROVIDER=ollama`, Ollama **down** → draft → enveloped error; case stays `evaluated`.
2. Start Ollama **without bouncing the backend**.
3. Draft the **same** application again → ⛔ **the orchestrator is invoked a SECOND time on the same
   `thread_id`, in the same process.** Under C2 it must return a memo.

⚠️ **Until that runs, #34's row reads: fix tier-U proven, route live-confirmed closed.**

---

## ✅ #35 `OFFLINE-DOUBLE-CITES-THE-RECOMMENDATION` — **LIVE-CONFIRMED**

| | |
|---|---|
| **What was run** | Backend restarted with `MEMO_PROVIDER` **unset**; a profile engineered to trigger `DECLINE-RECOMMEND` (income `1000000`, existing debt `500000` → **DTI `0.5000` > the `0.40` ceiling**, failing `DTI-CEIL-1`) submitted and drafted |
| ✅ **Result** | `report.recommendation = DECLINE-RECOMMEND` · `memo.cited_rule_ids = ["AGE-BAND-1"]` · `status = ready` · ⛔ **no `FAILED` state** |
| ⛔ **What this proves** | **Every prior `DECLINE-RECOMMEND` case in this build's history would have landed in `FAILED` here — silently, with no error and no log line.** This one produced a memo. |
| ⚠️ **A nuance recorded so no future reader misreads it** | `first_cited_rule_id` returns the **first rule id in the report region**, and `AGE-BAND-1` is the **first rule in rulebook `1.0.0`** — ⛔ **not necessarily the FAILING rule** (`DTI-CEIL-1` was the `decline_fail`). ⚑ **That is correct behaviour for a placeholder double**, whose only obligation is to cite a **real id from the handed report**. The invariant held exactly. **What matters is what it is NOT: the literal string `DECLINE-RECOMMEND`.** |

---

## ⛔ #22 `MEMO-PROSE-NOT-BIT-REPRODUCIBLE` — **OPEN, AND NOW WITH MEASURED NEGATIVE EVIDENCE**

⚑ **This pass converts #22 from a theoretical concern into a finding.** Two drafts of an **identical
profile** (`APP-47bb6f55…` and `APP-38148504…`) produced:

- ✅ **the same rules cited, the same structure, the same conclusion** — and
- ⛔ **prose differing at the WORD LEVEL, and a DIFFERING `memo_hash`.**

⛔ **`temperature=0` PLUS pinned local weights do NOT yield byte-identical prose.** ⚠️ Consistent
with what the live-LLM-drafting pass already recorded: **the digest pins the weights, not the
sampling stack.** ⛔ **#22 REMAINS OPEN, and this evidence makes it HARDER to close, not easier.**
⚠️ It is **one repetition** — `PROJECT-BRIEF` §5.1's *"same input × 10 runs"* **still has not been
run**, and this observation does not substitute for it.

---

## Also recorded

| Item | Status after this verification |
|---|---|
| **#18** `NO-PRODUCTION-LLMCLIENT` | ⚑ **Gap (iii) MOVES — for the SHOWCASE/Ollama half ONLY.** A production `LLMClient` has now produced a real memo through the request path. ⛔ **Gemini's production client remains COMPLETELY UNPROVEN LIVE** — its `# pragma: no cover` real-spend branches have never executed and `GeminiAdapter._parse_xml` has never seen real model output. ⚠️ **#18 stays NARROWED, not closed**; no summary may describe it as progressed without naming which half. |
| **#32** `UNCAUGHT-EXCEPTION-ESCAPES-ENVELOPE` | ⛔ **UNTOUCHED.** The Ollama outage produced a **clean WIRE-1 envelope** naming the host with actionable guidance — ⛔ not a bare plain-text 500 — so #32's capability **did not fire on this route**. ⚠️ The R11 catch names the two Ollama types explicitly; **every other route retains the capability**, exactly as #32's row states. |
| **#27** `DraftOutcome.skipped` contract | ✅ **Confirmed live** by Part B's `skipped` — *"RE-TRIGGERING IS IDEMPOTENT, NOT A FAILURE."* ⚑ Recorded here because it is what Part B actually demonstrated. |
| **Fail-safe (Q9 C)** | ✅ **Held.** `MEMO_PROVIDER` unset → the offline double, stamped `OFFLINE-DOUBLE-NOT-A-REAL-LLM`. **An unconfigured deployment never silently reaches a live model.** |

---

⛔ **REGISTER NOW STANDS AT 35 TRACKED — 21 open · 10 closed/discharged · 4 narrowed (#3, #8, #18, #19).**

Movement: **#33 closes** (open 22 → 21, closed 9 → 10). ⚠️ **#34 and #35 were already counted closed
at stage 2**; this entry changes **#35's evidence tier** (tier-U → live-confirmed) and ⛔ **changes
neither the tier nor the count for #34**. ⚑ Derived from the running tallies, not from a
re-enumeration of all 35 rows — stated so a future reader knows which it is.

⚠️ **This supersedes the "35 tracked — 22 open · 9 closed" figure** recorded at this file's stage-2
entry, which was correct when written. ✅ **`guide-state.md`'s long-stale *"32 tracked — 21 open"* is
CORRECTED in this same pass**, reconciled against this file as the authoritative source.

---

# ✅ REGISTER UPDATE — 2026-09-12 · **#34 UPGRADED TIER-U → LIVE-CONFIRMED** — the derived closing run was executed and passed

⚑ **This section supersedes the `⚠️ #34 CHECKPOINT-POISONS-REDRAFT — NOT UPGRADED` row above**
(this file's §7 live-verification entry). ⛔ **That row is preserved, not rewritten** — it was
correct when written, and the run it specified has now been performed. **The count does not move:**
#34 was already counted **closed** at stage 2; what changes is its **evidence tier**, exactly as the
§7 entry changed #35's.

⚠️ **Epistemic status, stated first and different from every prior manual verification in this
file**: this run was **executed and observed first-hand by the agent**, not performed by the user and
reconstructed into the record. Detail: `audit.md` **2026-09-12T20:37:14Z**.

---

## ✅ #34 `CHECKPOINT-POISONS-REDRAFT` — **LIVE-CONFIRMED**

The run is exactly the one derived from `LEGAL_TRANSITIONS` in the section above — ⚑ **derived, not
guessed**, and then executed unchanged.

| | |
|---|---|
| **Harness** | Real `create_app()` · real local PostgreSQL · real cached `case_seams()` (`@lru_cache(maxsize=1)`) · real `POST /applications` and `POST /applications/{id}/draft` · auth stubbed via `dependency_overrides[require_underwriter]` (approved for this run) · ⛔ **ONE Python process throughout** |
| **Step 1 — Ollama DOWN** | `APP-7ab67ab52f2c46d098c7c4ff879192c3` submitted → `state=evaluated`. Draft #1 → **HTTP 500**, clean WIRE-1 envelope, `code=internal_error`, `detail.cause=provider_unreachable`, message naming the host and both operator remedies. ⛔ **`state` STILL `evaluated`** — the precondition the whole route depends on. |
| **Step 2 — daemon started, process NOT restarted** | `subprocess.Popen(['ollama','serve'])` from inside the same interpreter. ⚑ **Identity proven on BOTH objects**: `id(case_seams())` = `2905167156368` before **and** after; `id(seams._orchestrator)` = `2905163604784` before **and** after. ⛔ **The same `LangGraphOrchestrator` instance served both drafts.** `graph.checkpointer` read `None` at both points, live, on the real object. |
| ✅ **Step 3 — THE #34 CONDITION** | Draft #2 on the **same** application, **same process**, **same `thread_id`** → **HTTP 200** `{"status":"ready","outcome":"drafted"}`, `state=drafted`, **132.5 s**. Persisted: `REC-APP-7ab67ab52f2c46d098c7c4ff879192c3-bb19e6d8` · `model_version=NOT-QUALITY-GATED+llama3.1:8b-instruct-q4_K_M+digest-unavailable+ollama-python-0.6.2` · `memo_hash=735b93f31bb51ad6e3f2cfa0c26e1712952c5597d31fb930965aa4484c179b38` |
| ⛔ **What did NOT happen** | **No `RuntimeError`. No `CON-BR2-STATE`. No deserialization-warning cluster.** |
| ⚑ **The discriminator the §7 entry named** | **`outcome` is `drafted`, NOT `skipped`.** `skipped` meant the legality guard short-circuited **above** `draft_memo` and the orchestrator was never re-entered. `drafted` means `draft_memo` **ran** — the orchestrator **was** invoked a second time on that `thread_id` and **returned a memo**. ⛔ **That is #34's condition, and nothing weaker.** |

### ⚠️ One disclosed override — named before any claim is built on the run

Two earlier attempts with **nothing overridden** both died at **121 s** with `httpx ReadTimeout`.
⛔ **Neither was the #34 error.** Cause established **by measurement, not inference**: this host has
**no Ollama-supported GPU** (integrated *AMD Radeon(TM) Graphics*; `/api/ps` reports
`size_vram: 0`), so generation is **CPU-only at 4.92 tok/s measured** (200 tokens in 40.66 s).

The passing run raised **only the provider's HTTP read timeout**, 120 s → 900 s, by patching
`backend.app.dependencies.build_ollama_client` to a `functools.partial` **in the harness script**.
⛔ **NO PROJECT FILE WAS EDITED; `DRAFT_TIMEOUT_SECONDS` is unchanged on disk.**

⚑ **Why this cannot weaken the #34 claim, stated structurally rather than asserted**: #34 fires at
the **SEED of invoke #2** — before any node runs and before any provider call. A read timeout occurs
**inside** the provider call, i.e. **after** seeding has already succeeded. The override changed
**how long the model was allowed to talk**, and nothing about the checkpointer, the orchestrator,
`case_seams()`'s caching, the `thread_id`, R11, or the pipeline — **all exactly as shipped.**

⚑ **The two timed-out runs are themselves evidence, and they carry NO override.** Both reached a
**121-second provider call on invoke #2**; ⛔ **under the pre-C2 code that call would never have been
made**, because the seed would have raised in milliseconds. What they could not show is the **memo**,
which is what this item's closing condition demands. **Both are recorded; neither is discarded.**

---

## ⛔ A NEW FINDING THIS RUN EXPOSED — reported for a decision, NOT opened as an item

`ollama_client.py:49-60`'s own docstring asserts *"120 s is comfortably above a cold load and still
finite."* ⚠️ **That claim is FALSIFIED on this hardware.** The observed end-to-end draft is
**132.5 s** with the model already resident and the weights already in the OS page cache — so
⛔ **no real draft can complete through R11 at the shipped timeout on a CPU-only host.**

⚑ It is a **provider-performance** finding, **entirely separate from #34**, and it does **not**
affect the offline double, which is what an unconfigured deployment serves. ⛔ **No register item is
opened here** — this project opens items on explicit direction, and filing one unilaterally would be
the same overreach the §7 entry declined when it refused to record an unearned upgrade.

---

## Register after this update

⛔ **REGISTER STANDS AT 35 TRACKED — 21 open · 10 closed/discharged · 4 narrowed (#3, #8, #18, #19).**

⚑ **UNCHANGED FROM THE SECTION ABOVE, AND THAT IS THE POINT.** #34 was already counted **closed** at
stage 2; this update moves its **evidence tier only** (tier-U → live-confirmed). ⚠️ **No tally moves,
so nothing here supersedes the previous count** — it is restated for a reader who arrives at this
section first.

**Not claimed by this run**: ⛔ **#18 gap (iii) does NOT move** — this used the **Ollama showcase**
provider; **Gemini's production client remains completely unproven live.** · ⛔ **#22 untouched and
still open**, with the negative evidence recorded above; `PROJECT-BRIEF` §5.1's *"same input × 10
runs"* **still has not been run.** · ⛔ **#32 untouched.** · ⛔ **NO COMMIT** — HEAD `bd3875d`,
nothing staged.

---
