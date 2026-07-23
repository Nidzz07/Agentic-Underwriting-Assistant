# NFR Requirements — Plan (Part 1) — `ui-outlier-view` (U20, C5, **Phase 2**)

**Stage**: BUILD → per-unit loop → **NFR Requirements Part 1 (Plan)** · **Unit**: U20 `ui-outlier-view` · C5 · **Phase 2** · **Depth**: **lighter (display)** · **Date**: 2026-07-17 · Story **US-UI-3** · FR-OUT-2.
**Built ON** the frozen FD (re-opening none): **BR-OUTV-1..10**; the component/prop inventory (`OutlierView`/`OutlierStateView`/`OutlierScoreRegion`/`FlaggedFeaturesRegion`); the **four-state render model** with the **field-derived `NOT_AVAILABLE`** state; the advisory-statistical framing (isolation-by-absence); the reference-not-own boundary + the forward-looking **OUTV-FD-Fold-2** note; the outlier-local copy incl. **`FLAG_DIRECTION_LABELS`**; the `outlier-<element>-<purpose>` testids. Answers **Q1–Q5 (A/A/A/B/A)** + folds **OUTV-FD-Fold-1..3** are the substrate.

**Status**: **Part 2 GENERATED — the THREE `[Answer]` tags (§4) are FILLED (Q1-A, Q2-A, Q3-A); ambiguity-check RUN → CLEAN (three folds, no surface-and-stop); the two NFR artifacts generated** under `guide-docs/build/ui-outlier-view/nfr-requirements/` (`nfr-requirements.md` [thirteen `NFR-OUTV-*`, STATE-1 + NOVERDICT-1 the load-bearing pair] · `tech-stack-decisions.md`). **STOPPED at the NFR Requirements 2-option completion gate** (1. Request Changes / 2. Continue → NFR Design). Full Q&A re-embedded (§4, standing convention).

### Part-2 ambiguity-check verdict (CLEAN — three folds, none improvised)
- **NFR-OUTV-Fold-B (check i)** — `NOVERDICT-1`'s rendered-absence half uses **RTL `queryBy*` returning null** over the **enumerated finite set** of `Recommendation`/`Confidence` wire values + shell labels (exact matching), with the **structural import-absence scan** as the primary robust guarantee — **not** a broad `textContent.includes(...)` substring sweep (the project's text-scan-false-positive caution applies).
- **NFR-OUTV-Fold-C (check ii)** — three distinct outlier fixtures — **`outlier: null`** (NOT_AVAILABLE) · **`outlier: {…, flagged_features: []}`** (EMPTY / READY-no-anomalies) · **`outlier: {…, flagged_features: […]}`** (READY-with-data) — fed through the single `fetchSeam` double (Fold-A). The `null`-vs-`{flagged_features:[]}` distinction is structurally unambiguous (falsy-null vs truthy-object); mirrors `ui-memo-view` NFR-MEMO-Fold-C.
- **NFR-OUTV-Fold-D (check iii)** — `PROV-1` uses **distinctive, collision-proof sentinels** for `seed` (a large tagged integer) + `corpus_version` (a tagged string) that cannot overlap any legitimately-rendered value, so the negative "sentinel absent" assertion is sound in both directions.

---

## 1. Tier convention (the lighter display-unit stack — frozen, inherited, no new toolchain)

Verified on disk (`frontend/package.json`: `vitest run`, `@testing-library/react`, `jsdom`; `ui-memo-view` `tech-stack-decisions.md` D3): the display-unit test tier is **Vitest + React Testing Library + jsdom**, **no live backend**, **R4 mocked via a single injected/capturing `fetchSeam` double** (the `ui-queue`/`ui-memo-view` prop-injection precedent — **NFR-OUTV-Fold-A**, single double). Structural/advisory conformance uses the **frozen ESLint lints** (`advisory-vocabulary`, `no-inline-label`) registered on `src/outlierView/**`, plus AST/source structural checks — the `ui-memo-view` `NFR-MEMO-ADVISORY-1`/`COPY-1` mechanism. **No new dependency** beyond the established React/Tailwind/Vitest/RTL/jsdom/ESLint substrate. **No TypeScript** (FR-UI-5). Each `NFR-OUTV-*` is a **pass/fail testable assertion** traced to its `BR-OUTV-*`.

## 2. Draft `NFR-OUTV-*` target map (every BR-OUTV-* mapped; no orphan)

| Target | Traces | Acceptance (pass/fail) | Tier |
|---|---|---|---|
| **NFR-OUTV-STATE-1** *(LOAD-BEARING — state-derivation correctness)* | BR-OUTV-3 | The four states `{LOADING, READY, NOT_AVAILABLE, ERROR}` render correctly; **teeth**: `NOT_AVAILABLE` is reached **only** from a **2xx resolution with `outlier===null`** (both a `pending` body **and** a Phase-1 `ready` body with `outlier:null`), and a **fetch failure never** yields `NOT_AVAILABLE` (it yields `ERROR`). The discriminator reads the **`outlier` field**, not `status` — a `ready` body with `outlier:null` still ⇒ `NOT_AVAILABLE`. Mirrors the rigor of `ui-queue`'s array-length-vs-status and `ui-memo-view`'s `PENDING-1` status-discriminator. | component (RTL) |
| **NFR-OUTV-NOVERDICT-1** *(advisory, load-bearing — see Q1)* | BR-OUTV-2 | **no `Recommendation` namespace in rendered output**: (a) structural — no `RecommendationBadge`/`ConfidenceBadge` import in `outlierView/**`; (b) rendered — RTL over a populated `READY` fixture asserts no `Recommendation` wire value (`APPROVE`/`REFER`/`DECLINE-RECOMMEND`) and no shell recommendation/confidence label appears in the DOM. *(Q1: whether this is its own target vs folded into SCOPE-1/ADVISORY-1.)* | structural + component |
| **NFR-OUTV-ADVISORY-1** | BR-OUTV-2/5 | the frozen `advisory-vocabulary` + `no-inline-label` lints are **registered + green** on `src/outlierView/**` (static-source scope only — never lints runtime data); a synthetic forbidden-term insertion fails the lint (non-vacuity). | structural (lint) |
| **NFR-OUTV-COPY-1** | BR-OUTV-5 | single-source copy — no inlined `shell/copy` display label; **`FLAG_DIRECTION_LABELS`** maps `high`/`low` to **statistical-position** phrases (above/below the typical range), keyed by value, **no** severity/verdict word; no value collides with a shell label or a `FORBIDDEN_TERMS.systemOutput` token. | structural + component |
| **NFR-OUTV-EMPTY-1** *(see Q2)* | BR-OUTV-3/6 | a `READY` fixture with `outlier` present but `flagged_features: []` (a normal applicant, valid score) renders the neutral **"no anomalous features"** message + a valid score, and is **distinct from `NOT_AVAILABLE`** (analyzed-with-no-anomalies ≠ not-analyzed). *(Q2: whether this is its own target vs a parameterized case of STATE-1.)* | component (RTL) |
| **NFR-OUTV-LISTORDER-1** | BR-OUTV-6 | RTL over a **deliberately non-sorted** `flagged_features` fixture — rendered row order **equals** the input order; no comparator/`.sort()` in the view source. Mirrors `ui-memo-view` `LISTORDER-1`. | component + structural |
| **NFR-OUTV-ERROR-1** | BR-OUTV-7 | a non-2xx / transport failure renders `error.message` (visible) + `error.code` (hidden testid) + a **Retry** that re-fetches R4 for the **same** `applicationId`; `error.detail` **never** rendered raw. | component |
| **NFR-OUTV-VIEWONLY-1** | BR-OUTV-4 | no `RoleGate`, no router import, no commit/`POST`, no outward mutating event; `shell/session` available but **not gated on**. | structural + component |
| **NFR-OUTV-PROV-1** *(see Q3)* | BR-OUTV-9 | **negative teeth**: `seed` and `corpus_version` **never** appear in rendered output (over a `READY` fixture whose provenance carries recognizable sentinel values); the optional `outlier_model_version` footnote tested per the single chosen realization. *(Q3: test both present/absent configs, or one chosen behavior.)* | component (negative) |
| **NFR-OUTV-TESTID-1** | BR-OUTV-8 | every state container + flag row + score/`is_outlier`/error elements carry `outlier-<element>-<purpose>` testids; the `outlier-testid-convention` lint is green. | structural + component |
| **NFR-OUTV-SCOPE-1** | BR-OUTV-10 | structural scan: **no import** of `outlier-model`, `ui-memo-view`, `ui-queue`, any other sibling view, or any backend module in `outlierView/**`; the only imports are `ui-shell` + the injected `fetchSeam` + React/Tailwind; + a detector self-test (non-vacuity). | structural |
| **NFR-OUTV-FETCH-1** | BR-OUTV-1/3 | R4 fetched via the **single injected `fetchSeam` double** (Fold-A); the four-state machine is exercised end-to-end (loading → each terminal state); the double captures the R4 call (same-`applicationId` on Retry). | component |
| **NFR-OUTV-NOTS-1** | FR-UI-5 | no `.ts`/`.tsx` under `outlierView/`; JS/JSX only. | structural |

**No orphan**: BR-OUTV-1→FETCH-1; 2→NOVERDICT-1+ADVISORY-1; 3→STATE-1(+EMPTY-1); 4→VIEWONLY-1; 5→COPY-1+ADVISORY-1; 6→LISTORDER-1+EMPTY-1; 7→ERROR-1; 8→TESTID-1; 9→PROV-1; 10→SCOPE-1; FR-UI-5→NOTS-1. **Load-bearing**: **STATE-1** (the field-derived `NOT_AVAILABLE` correctness) + the advisory cluster (**NOVERDICT-1**/ADVISORY-1).

## 3. Security-Guardrails posture (display unit)
Read-only presentational view — **no secret**, **no LLM/prompt**, **no persistence/write**, **no PII authored** (renders advisory statistical signals from an already-validated R4 body). Input validation is the backend's (R4); the view **never** renders `error.detail` raw (BR-OUTV-7) and **never** renders `seed`/`corpus_version` (BR-OUTV-9). Advisory-only + bias-free framing is the load-bearing display concern (NOVERDICT-1/ADVISORY-1). **No blocking finding anticipated** (finalized in Part 2's compliance table).

## 4. Clarifying questions (`[Answer]` tags — LEFT BLANK; lettered; full text below)

> Fill these; I then run the ambiguity-check against the answers + the frozen FD (BR-OUTV-1..10) + the `ui-memo-view` NFR precedent + the `ui-shell` lint substrate, then Part 2 (`nfr-requirements.md` + `tech-stack-decisions.md`) **on your explicit go**. **No improvising on any ambiguity — flag and stop.**

### Q1 — Does BR-OUTV-2's "renders no `Recommendation` namespace" need its own dedicated target?
- **A.** **Yes — a dedicated `NFR-OUTV-NOVERDICT-1`**, distinct from `NFR-OUTV-SCOPE-1` (imports) and `NFR-OUTV-ADVISORY-1` (lint). It asserts a **positive absence in rendered output**: (a) structural — no `RecommendationBadge`/`ConfidenceBadge` import; **and** (b) rendered — RTL over a populated `READY` fixture asserts no `Recommendation` wire value / no recommendation-confidence label appears in the DOM. *(Recommended — the "no verdict in what the user sees" claim is the load-bearing advisory guarantee (BR-OUTV-2), and a rendered-output absence is a different assertion from an import-boundary scan (SCOPE-1) or a source lint (ADVISORY-1); this mirrors how `ui-memo-view` kept `SEPARATION-1` [render structure] separate from `ADVISORY-1`/`COPY-1` [lint] and reference-not-own.)*
- **B.** **No — fold it into `SCOPE-1` + `ADVISORY-1`** (no dedicated target). *(Leaner, but conflates an import-boundary claim + a source-lint claim with a rendered-output absence claim; the load-bearing advisory guarantee loses its own teeth.)*
- **C.** Other (describe).

`[Answer]:` A

### Q2 — Does the empty-`flagged_features` case (a normal applicant) need its own explicit target?
- **A.** **Yes — a dedicated `NFR-OUTV-EMPTY-1`.** RTL over a `READY` fixture with `outlier` present but `flagged_features: []` (valid score, no anomalies) renders the neutral **"no anomalous features"** message + a valid score, and is **asserted distinct from `NOT_AVAILABLE`** ("analyzed, no anomalies found" ≠ "not analyzed"). *(Recommended — the two are a **meaningfully different, advisory-correctness-bearing** distinction the underwriter must not misread, even though both are the `READY`/absent-null enum path; the frozen units gave empty-list its own rendered case [`ui-queue` empty, `ui-memo-view` empty citations/missing-info].)*
- **B.** **No — a parameterized sub-case of `STATE-1`/`COMPOSE`** (no separate target). *(Leaner; but the "empty-flags ≠ not-available" distinction is exactly the kind of state-conflation this project has given load-bearing teeth elsewhere.)*
- **C.** Other (describe).

`[Answer]:` A

### Q3 — The optional `outlier_model_version` footnote (Q5-A) — test both configs, or one chosen behavior?
- **A.** **Code-Gen decides ONCE; the NFR set tests only the chosen behavior + the hard invariant.** `NFR-OUTV-PROV-1` **always** gates the invariant that holds either way (**`seed`/`corpus_version` never rendered**); the footnote is a single Code-Gen realization — if included, one test asserts **only** `outlier_model_version` shows (never `seed`/`corpus_version`); if omitted, only the negative invariant is tested. *(Recommended — "optional" is Code-Gen realization latitude, **not** a runtime toggle; testing both present/absent configs would test a configurability the unit has no requirement for.)*
- **B.** **Test both "present" and "absent" configurations** (treat the footnote as a configurable prop with coverage for each). *(More coverage, but pins a configurability that is not a requirement.)*
- **C.** **Pin only the negative invariant now** (`seed`/`corpus_version` never rendered); defer the footnote-presence decision entirely to NFR-Design/Code-Gen, testing it only once realized. *(Closest to A; differs only in when the footnote decision is recorded.)*
- **D.** Other (describe).

`[Answer]:` A

---

## 5. HOLDS (binding through Part 2)
- **No NFR artifact generated in Part 1**; `guide-docs/build/ui-outlier-view/nfr-requirements/` NOT created; no code; no `frontend/src/outlierView/`.
- **Re-opening none of the frozen FD** (BR-OUTV-1..10 + the four-state model + the folds); **WIRE-1 consumed by shape, not touched**; **`outlier-model` (U18) reached only via R4, never imported**; **`ui-shell`/`ui-memo-view` composed/mirrored, never edited**; **no sibling-view or backend import**.
- The **17 frozen P1 units + the closed composition root UNTOUCHED**; **tier-B NOT authorized**; the **`audit_store` Docker-guard gap** untouched; **no other unit started**; the 23-unit decomposition unchanged.

## 6. Gate
**Part 1 (Plan) WRITTEN — STOPPED at the plan-file gate.** The three `[Answer]` tags (Q1–Q3) are **BLANK**. On the filled answers: run the mandatory **ambiguity-check** against the answers + the frozen FD (BR-OUTV-1..10) + the `ui-memo-view` NFR precedent + the `ui-shell` lint substrate — **surface-and-stop on any genuine gap, do not improvise** — then, **on the explicit go**, generate Part 2 (`nfr-requirements.md` + `tech-stack-decisions.md`). **Depth: lighter.** NO NFR artifact generated in Part 1. WIRE-1 · `outlier-model` (U18) · `ui-shell`/`ui-memo-view` · the 17 frozen P1 units · the closed composition root UNTOUCHED; tier-B NOT authorized; the `audit_store` Docker-guard gap untouched; no other unit started; the 23-unit decomposition unchanged.
