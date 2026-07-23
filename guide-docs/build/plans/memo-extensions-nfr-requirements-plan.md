# NFR Requirements — Plan (Part 1) — `memo-extensions` (U19, C4, **Phase 2**)

**Stage**: BUILD → per-unit loop → **NFR Requirements Part 1 (Plan)** · **Unit**: U19 `memo-extensions` · C4 · **Phase 2** · **Depth**: **comprehensive** (consistent with the FD depth decision) · **Date**: 2026-07-17
**Stories**: US-MEMO-5/6/7 · **Requirements**: FR-MEMO-5/6/7, FR-PROV-2/3/5, FR-PROV-GATE-1/2, CON-BR1, CON-BR2, CON-DET-1.
**Built ON** the **frozen FD** — `domain-entities.md` (the four-module inventory + method surfaces; the **`OutlierSignal`** structural Protocol; the two MCP tool surfaces; the **construction-time** thinking-mode mechanism), `business-rules.md` (**BR-MEXT-1..13**), `business-logic-model.md` (the route → construct → enrich → draft → validate lifecycle) — **re-opening none of it.** **FD APPROVED 2026-07-17 (option 2, Continue → NFR Requirements).**

**Status**: **PART 1 ANSWERED 2026-07-17 (Q1–Q4 all A, embedded §3) → ambiguity-check RUN (§3.5) → CLEAN (4 folds) → Part 2 GENERATED** (`nfr-requirements.md` + `tech-stack-decisions.md`). **STOPPED at the NFR Requirements 2-option completion gate.** Full Q&A embedded here per the standing convention. **No code; `backend/memo_extensions/` NOT created; `requirements.txt` NOT edited.**
**⚑ NEW named register item opened by Q4-A: `MCP-TRANSPORT-DEFERRED`** (§3.6) — so *"two MCP servers"* as a **stated brief deliverable** is **not quietly understood as fully done** when only the **handler layer + injected seam** exist at this stage.

---

## 1. Unit context

### 1.1 What this stage decides
The **pass/fail quality targets** (`NFR-MEXT-*`) attached to the frozen FD — **HOW** each **BR-MEXT-\*** is verified, at what **tier**, with what **rigor**. It decides **no functional behavior** (that is the frozen FD) and generates **no code**. U19's dominant NFRs are **determinism** (CON-DET-1 / BR-MEXT-1), **groundedness** (FR-MEMO-5 / BR-MEXT-6), and **frozen-boundary integrity** (BR-MEXT-11) — each already designed **by construction** in the FD; this stage pins the guards that **verify the construction held**.

### 1.2 Frozen FD carried in (NOT re-opened — targets attach to these)
- **BR-MEXT-1..13** — the checkable invariants (this NFR set is their pass/fail expression).
- The **four modules** under `backend/memo_extensions/` — `borderline_router.py` · `mcp_tools.py` · `provider_secondary.py` (Claude) · `provider_showcase.py` (Ollama) — the exact files the frozen layout `unit-of-work.md:70–71` names.
- The **U19-local `OutlierSignal`** structural Protocol = `{is_outlier, outlier_score}` — satisfied **by shape**, **never imported** (Fold-3).
- The **construction-time thinking-mode mechanism** (Fold-1) — incl. Gemini reaching its budget via the **injected `LLMClient`**, with the capability/config binding **already frozen-deferred by U4** to composition/deploy-config.
- The **MCP boundary**: **supplementary** · **read-only** · **demographic-free** — and the handed report as the **sole citable source** (Q7-A), enforced by the **frozen, unchanged `CitationValidator`**.
- **BR-MEXT-13** — the **negative scope rule** (no outlier data in prose), guarding the registered **`OUTLIER-IN-PROSE`** gap.

### 1.3 Governing requirements + tier convention (inherited, verified on disk)
- **Tiers**: **tier-U** = fast, deterministic, in CI — **the default path: no live LLM call, no network, no key, no Docker, no live MCP server**; **tier-S** = offline smoke (optional); **tier-B** = out-of-band real-corpus (**N/A to U19** — it never touches the corpus; **NOT authorized**).
- **The frozen no-live-LLM discipline**, verbatim from U4's `test_provider.py` header: *"No test constructs a real Gemini client, reads a key, or touches the network."* U19 inherits it for **Claude and Ollama**.
- **Injected/capturing doubles**: the **TEMP0-1 part i** precedent — *"a capturing test double records the outgoing request; no network, no key, no CI live call."*
- **Detector self-tests**: every structural scan carries one, so it can **never pass vacuously** (the CG-NFR-OUT-Fold-3 convention).
- **Docker/DB**: **avoidable and avoided** — U19's `audit-store` `R` edge is exercised through the **`decisions-tools` seam**, not a live Postgres (the `audit_store` Docker-guard gap is **untouched** and stays out of U19's path).

### 1.4 Guardrails held (underwriting-rules skill)
**#1 advisory-only** → CONTRACT-1 · **#2 human gate** (untouched; outside U19) → MCPRO-1 · **#3 no LLM in the deterministic path** → ROUTE-1 · **#4 temperature=0** → TEMP0-1 · **#5 reproducibility** → ROUTE-1/AGNOSTIC-1 · **#6 bias-free** → BIAS-1 · **#8 explainability** → GROUND-1.

---

## 2. NFR Requirements execution plan (checkboxes)
- [x] **P1. Unit context** (§1) — DONE (this plan).
- [x] **P2. Collect the four `[Answer]:` tags** (§3 — **Q1–Q4 all A**) + run the **mandatory ambiguity-check** (§3.5 — **CLEAN, 4 folds**) + open **`MCP-TRANSPORT-DEFERRED`** (§3.6).
- [x] **P3. Generate `nfr-requirements.md`** — the `NFR-MEXT-*` set with acceptance + tier + rigor + traceability + the Security-Guardrails compliance table.
- [x] **P4. Generate `tech-stack-decisions.md`** — the D-decisions (Claude/Ollama already floored **and installed** → **no new dependency**; **`MCP-TRANSPORT-DEFERRED`** recorded in full; the injected-double substrate for **both** `LLMClient` **and** the MCP transport seam).
- [ ] **P5. NFR Requirements 2-option completion gate — AWAITING USER.**

---

## 2.5 Draft `NFR-MEXT-*` target map (every BR-MEXT-\* → a pass/fail target; the user-named tests folded in)

| Target | Attaches to | Acceptance (pass/fail) | Tier | Rigor |
|---|---|---|---|---|
| **NFR-MEXT-ROUTE-1** *(load-bearing)* | BR-MEXT-1 | **(a) purity teeth** — `route_borderline` is a **pure function**: same `(report, signal)` → identical `ThinkingMode` across N≥2 calls; no state retained. **(b) structural/AST scan** — **zero** LLM / provider / adapter / network / `requests` / `httpx` / client imports **anywhere** under `borderline_router.py`, **+ detector self-test** (a synthetic LLM-client import line is flagged). **(c) trigger teeth** — a **REFER** report routes `EXTENDED`; rule-proximity within margin ⇒ `EXTENDED`; outside ⇒ `STANDARD`. **(d) boundary teeth** — a value **exactly at** `RULE_PROXIMITY_MARGIN` / **exactly at** `OUTLIER_SCORE_CUTOFF` lands on the intended side, with the comparison (`<=` vs `<`) explicit. **(e) constants** — exactly one module-level literal per trigger, **parameterized off the named constant** (never a hardcoded number — the NFR-OUT-THRESHOLD-1 / Q3-A precedent, so calibration is a one-constant edit). | structural + component (teeth) | **full (highest)** |
| **NFR-MEXT-FROZEN-1** *(load-bearing)* | BR-MEXT-11 | **(a) extend-don't-modify scan** — U19's only `backend.*` imports are `memo_agent_core`, `rules_engine`, `audit_store` (its **three frozen edges**); **no file under `backend/memo_agent_core/` is modified** (+ detector self-test). **(b) the two frozen U4 tests as a U19-owned regression guard** — that `route_borderline` **still raises `NotImplementedError`** and that U4's `provider` namespace **still contains no Claude/Ollama/MCP name**. **Mechanization is Q1.** **(c) adapters live outside U4's namespace** — `dir(memo_agent_core.provider)` contains **none** of U19's adapter names. | structural + component | **full (highest)** |
| **NFR-MEXT-SIGNAL-1** | BR-MEXT-2 | **(a) by-shape teeth** — a **U19-local fake** satisfying `OutlierSignal` structurally drives **every** routing test (**no U18 import in tests either**). **(b) interop self-test** — a **real U18 `OutlierResult` constructed BY VALUE (not by import)** is shown to **satisfy the Protocol structurally**, proving the frozen `component-methods.md:73` contract is honored without an edge. **(c) None-degrades teeth** — `route_borderline(report, None)` equals the **rule-proximity-only** result over that report (FR-MEMO-7). **(d) scan** — **no `outlier_model` import** under `backend/memo_extensions/` (+ self-test). | component + structural | full |
| **NFR-MEXT-AGNOSTIC-1** | BR-MEXT-3 | the **identical** `(report, signal)` yields the **identical** `ThinkingMode` under **all three** provider selections; the router's source references **no** adapter/provider name (scan); an **Ollama** adapter constructed with `EXTENDED` **still completes** (degrades) rather than raising. | component + structural | full |
| **NFR-MEXT-THINK-1** | BR-MEXT-4 | **(a) frozen-signature assertion applied to EACH new adapter** — `params == ["self","prompt","schema"]` **exactly** (U4's own assertion, extended to Claude + Ollama); each `isinstance(...)` the `runtime_checkable` `ProviderAbstraction`. **(b) capturing-double teeth, OFFLINE** — an adapter constructed with **`EXTENDED`** produces a **thinking-configured** outgoing request; constructed with **`STANDARD`** it does **not** — **no network, no key, no live call**. **(c)** the mode is **construction-time only** — it appears in **no** `complete` signature. | component (offline doubles) + structural | full |
| **NFR-MEXT-TEMP0-1** | BR-MEXT-5 | the capturing double records **`temperature == 0`** on **every** call from **every** adapter (Claude **and** Ollama), in **BOTH** thinking modes (the TEMP0-1 part i pattern extended); **no** adapter's `complete` exposes a `temperature` parameter (part ii). **Extended thinking never implies a non-zero temperature.** | component (offline doubles) + structural | full |
| **NFR-MEXT-GROUND-1** *(load-bearing)* | BR-MEXT-6 | **(a) the direct retrieval-miss test** — a memo citing a rule that **exists in the `Rulebook` but is ABSENT from the handed `RuleResultReport`** (i.e. **exactly what MCP can describe**) → the **frozen `CitationValidator`** returns **`citation_failure`** with that id in `offending_cited_ids`. **(b)** `citation_validator.py` is **unmodified** (scan). **(c)** the supplementary section is **explicitly marked non-citable** in the composed prompt; **no U19 code path appends to `cited_rule_ids`** (scan + self-test). | component (teeth) + structural | full |
| **NFR-MEXT-MISS-1** | BR-MEXT-8 | with **both** MCP servers **unavailable** (failing/timing-out/empty doubles), drafting still yields a **valid `MemoDraftOutput`** whose citations **pass** the frozen validator; the failure path adds **no** content to the prompt; the miss is **observable** (surfaced for U21), **not silent**. **A miss never blocks and never relaxes GROUND-1.** | component (teeth) | full |
| **NFR-MEXT-MCPRO-1** | BR-MEXT-7 | **neither** server exposes a write/mutate/commit method (surface scan); **no** `DecisionCommitService` / write-transport / session-write import under `mcp_tools.py` (+ detector self-test); both edges exercised **read-only**. | structural | full |
| **NFR-MEXT-BIAS-1** | BR-MEXT-9 | **(a) structural scan** — **no** `full_name` / `gender` / `city` / `.demographics` reference in any `mcp_tools.py` return path (+ detector self-test). **(b) swap teeth** — identical financials with **swapped name/gender/city** → **byte-identical** supplementary context. **Scope of the swap teeth is Q3.** `quality-gates` remains the **external** CON-BR1 delta verifier. | structural + component (teeth) | full |
| **NFR-MEXT-CONTRACT-1** | BR-MEXT-12 | structural — **no** U19 module declares a Pydantic model, and **none** declares/emits a `Recommendation` field or value (+ self-test); `MemoDraftOutput` / `DecisionMemo` **unmodified**; **QA-5** (*"the LLM cannot change a recommendation"*) holds for **Claude and Ollama** exactly as for Gemini; no "decision"-as-verdict wording in U19 strings. | structural | full |
| **NFR-MEXT-SCOPE-1** | BR-MEXT-13 | structural — **zero** references to `flagged_features` / `shap_value` / `provenance` **anywhere** under `backend/memo_extensions/` (+ **mandatory detector self-test** feeding a synthetic `result.flagged_features` read and asserting it is **flagged**); the composed prompt's supplementary section contains **no** outlier content; `MemoAgentInput` **unmodified**. **The `OutlierSignal` minimal surface is itself the guard.** | structural | full |
| **NFR-MEXT-PROVGATE-1** | BR-MEXT-10 | **(a)** the **Ollama** adapter **is** unit-tested offline (constructed; `temperature=0` asserted; structured output parsed) — *"wired-only" ≠ untested code*. **(b)** `temperature=0` + **CON-BR2-TYPE** hold for it **identically**. **(c) governance** — its **absence from any groundedness/promptfoo target set is a Code-Gen/tooling-config fact of `llm-judge` (U22), NOT a code fact needing a test here** (per the user's direction); recorded as a documented exemption, never implicit. | component + governance | full (a/b) · governance (c) |
| **NFR-MEXT-PERF-1** | (adapter/MCP cost) | **observed / soft, non-gating** — no hard SLO, consistent with **every** prior unit's soft-perf posture. No live call is timed (there are none at tier-U). | observed / soft | soft |
| **NFR-MEXT-SEC-1** | (skill guardrails) | governance — the Security-Guardrails compliance table (prompt-injection posture, secrets via `secrets-config`, read-only edges, no PII/secret in error paths, advisory-only). | governance | N/A |

**No orphan**: BR-MEXT-1→ROUTE-1 · 2→SIGNAL-1 · 3→AGNOSTIC-1 · 4→THINK-1 · 5→TEMP0-1 · 6→GROUND-1 · 7→MCPRO-1 · 8→MISS-1 · 9→BIAS-1 · 10→PROVGATE-1 · 11→FROZEN-1 · 12→CONTRACT-1 · 13→SCOPE-1. PERF-1 / SEC-1 cover the cost + governance concerns.

---

## 3. Clarifying questions (fill each `[Answer]:`; full text, lettered options)

> Four questions. **Q1–Q3 are the ones you named; Q4 is a genuine on-disk finding surfaced during planning** (not improvised — see its verified evidence). Fill these; I then run the mandatory ambiguity-check, then Part 2 **on explicit approval**. **No ambiguity will be improvised — flagged and stopped.**

### Q1 — How should BR-MEXT-11's "re-run the two frozen U4 tests as a regression guard" be **mechanized**?

**Context.** BR-MEXT-11 is load-bearing: U19 **extends** U4 and **modifies nothing**, and **two frozen P1 tests already enforce that** — `test_route_borderline_is_a_not_wired_stub` and `test_only_gemini_adapter_is_present_no_claude_ollama_mcp`. You asked for a U19-owned guard that re-runs them so a future accidental modification is caught **in U19's context**. The mechanization matters because **importing another unit's TEST file is itself a reference-not-own concern** — and the project has a settled precedent for exactly this tension: **U18 "mirrored — never imported —" `quality_gates/corpus_loader.py`**, and **U20 "never imported" U18, mirroring its nine feature names by value**.

**The distinction that makes this resolvable**: importing U4's **test file** is a cross-unit *test* dependency (unprecedented, brittle to a U4 test rename, and double-collected by pytest). Importing U4's **production module** (`memo_agent_core.provider`) is **U19's own frozen edge** — it already does so to implement the Protocol. Both assertions can be re-made from the **production** symbols alone.

- **(A) MIRROR the assertions locally, importing only U4's PRODUCTION module** — U19's suite imports `from backend.memo_agent_core.provider import route_borderline` and `import backend.memo_agent_core.provider as provider_module` (**both already U19's legitimate edge**) and re-asserts the two facts itself: `route_borderline()` **raises `NotImplementedError`**, and `dir(provider_module)` contains **no** Claude/Ollama/MCP name. **No U4 test file is imported; no test is double-collected; a U4 test rename cannot break U19.** **(Recommended)** — it is the exact **mirror-don't-import** discipline U18 and U20 already established, it keeps the guard **inside U19's own suite** (failing in U19's context, as you asked), and it depends only on the **production contract** U19 legitimately consumes.
- **(B) IMPORT and re-invoke the two named U4 test functions.** Maximum fidelity — literally the same assertions, no drift possible. But it creates a **cross-unit test-file import** (unprecedented in this project), **double-collects** those tests, and couples U19's suite to U4's **test-function names** — a rename in a frozen unit's test file would break U19, which inverts the dependency direction.
- **(C) DON'T add the guard — rely on U4's own suite in CI.** Has real merit and should be stated honestly: the full backend suite (**1011 passed / 31 skipped**) **already runs both tests**, so a modification to U4 **is already caught** — (A) is strictly a **duplicate signal**. The counter-argument is that (A)'s duplicate is **cheap, local, and self-documenting**: it states U19's dependency **as an executable assertion** rather than an assumption, which is the point of a regression guard at a unit boundary.

**[Answer]**: **A** — **mirror the assertions locally, importing only U4's production module** (`memo_agent_core.provider`, **already U19's legitimate edge**), re-asserting that **`route_borderline()` raises `NotImplementedError`** and that **`dir(provider_module)` contains no Claude/Ollama/MCP name**. **No U4 test file imported, no double-collection, no coupling to U4's test-function names.**

> **Ambiguity-check upgrade (NFR-MEXT-Fold-1, §3.5)**: (A) turns out to be **strictly stronger than the "duplicate signal"** framing in option (C) — it catches a **namespace-pollution** class U4's own test **can miss**. Details in §3.5. A

### Q2 — Do the two MCP servers get a **live protocol implementation** under test, or an **injected/fake transport** the way `LLMClient` is injected?

**Context.** The FD pins *"two read-only servers"* (`services.md:46`). The frozen precedent is unambiguous about live infrastructure in tests — U4's `test_provider.py` header states verbatim: *"**No test constructs a real Gemini client, reads a key, or touches the network.**"* — and the **real** client is *"wrapped to this minimal `LLMClient` seam **at composition time** (a deploy-config/secrets concern)."*

**A design nuance worth pinning explicitly**: U19 owns the **server side** here, so there are really **two separable layers** — the **tool-handler functions** (pure: read a `Rulebook` / decision records → return a demographic-free projection) and the **MCP protocol transport** that exposes them. The handlers are testable **directly, with no protocol involved at all**; only the transport would need a live server. **This interacts with Q4** (there is **no MCP library floored or installed**).

- **(A) INJECTED / FAKE transport; tool HANDLERS tested directly — no live MCP server at tier-U.** The handlers are exercised as **pure functions** against fixture `Rulebook` / decision records (this is where **every** BR-MEXT-6/7/8/9 tooth actually lives), and the MCP transport is an **injected seam** with a fake — **mirroring `LLMClient` exactly**. The **real protocol wiring lands at composition/deploy-config**, precisely where U4 **already** frozen-deferred the real Gemini client. **(Recommended)** — it is the established seam discipline, keeps tier-U with **no network/no server**, and puts every U19 invariant under test **without** a protocol in the loop.
- **(B) LIVE MCP protocol implementation exercised in CI** — spin up the two servers and drive them over the real protocol. Highest fidelity to *"servers"*, but introduces **live infrastructure into tier-U** (contradicting the frozen no-network discipline), needs an **MCP dependency** (Q4), and would be this project's **first CI-live-service test** outside the Docker-guarded `audit-store` integration path.
- **(C) (A) for tier-U + a tier-S OFFLINE SMOKE against a real local MCP server, non-gating.** Keeps CI clean and adds one fidelity signal; costs an optional path plus the Q4 dependency, and the smoke is **not** where any invariant is verified.

**[Answer]**: **A** — **injected/fake transport; tool handlers tested directly with no live MCP server at tier-U.** The handlers are **pure functions** against fixture `Rulebook`/decision records — **where every BR-MEXT-6/7/8/9 tooth actually lives** — and the transport is an **injected seam with a fake, mirroring `LLMClient` exactly**. **Real protocol wiring deferred to composition/deploy-config, precisely where U4 already deferred the real Gemini client.**

### Q3 — Does BR-MEXT-9's **swap test** cover **both** MCP servers independently, or does one shared harness suffice?

**Context.** Both surfaces are demographic-free by the **same** mechanism, so a shared harness is tempting. **But there is a real asymmetry in the frozen FD** that decides whether a shared harness would be **vacuous on one side** — and this project has an explicit **"no vacuous pass"** discipline (the mandatory detector self-test on every structural scan):

- **`decisions-tools`** reads **committed decision records about other applicants** — it is the **only** surface carrying **applicant-derived data**, and therefore **the only place a demographic can actually leak**. A swap test here has **real teeth**.
- **`rulebook-tools`** (`describe_rules(rule_ids) -> list[RuleDescription]`) takes **rule ids** and returns **rule descriptions**. It **never takes an applicant** — so a name/gender/city swap has **nothing to swap**. A swap test against it is **not merely weak; it is barely constructible**, and would pass **vacuously**.

- **(A) ASYMMETRIC, matched to where the risk actually is** — **`decisions-tools` gets the full swap teeth** (identical financials, swapped name/gender/city → **byte-identical** supplementary context), while **`rulebook-tools` gets a STRONGER structural assertion**: it **takes no applicant input at all**, so it **cannot** leak a demographic **by construction** — plus the shared demographic-reference scan over **both** modules. **(Recommended)** — it puts the teeth where a leak is possible and replaces a vacuous swap with a **by-construction** argument, which is **strictly stronger** than a test that cannot fail. This is the same shape as U18's *"structurally unnameable"* reasoning (BR-OUT-1).
- **(B) ONE shared parameterized harness over BOTH surfaces** — uniform and cheap, and would catch future drift if `rulebook-tools` ever grew an applicant-shaped parameter. But **today it is vacuous on the `rulebook-tools` half** (nothing to swap), which is exactly the false-confidence the detector-self-test convention exists to prevent.
- **(C) FULLY INDEPENDENT full swap tests per server** — most thorough-looking, but duplicates (A)'s meaningful half and **still cannot fail** on the `rulebook-tools` side.

**[Answer]**: **A** — **asymmetric, matched to where the risk actually is.** **`decisions-tools` gets full swap teeth** (identical financials, swapped name/gender/city → **byte-identical** supplementary context). **`rulebook-tools` gets a stronger structural assertion instead**: it **takes no applicant input at all**, so it **cannot leak a demographic by construction** — **strictly stronger than a test that cannot fail**. Plus a **shared demographic-reference scan over both modules**.

> **Ambiguity-check sharpening (NFR-MEXT-Fold-3, §3.5)**: the `decisions-tools` swap teeth attach to the **OUTPUT projection** — seeded decision records differing **only** in demographics must yield a **byte-identical** projection — because that is where `decisions-tools`' leak risk **actually lives** (it reads *stored* records; the demographics are in the **data**, not the caller). The **input** side is covered by the **same by-construction argument** as `rulebook-tools`. This **sharpens** A, contradicting nothing. A

### Q4 — **[GENUINE ON-DISK FINDING — not one you named]** There is **no MCP library floored or installed**. Does U19 add the project's first new runtime dependency, or defer the protocol to composition?

**Verified this session, not assumed:**
- `requirements.txt` floors **`anthropic>=0.40.0`** and **`ollama>=0.3.0`** — so **US-MEMO-7's two adapters need NO new dependency**. Confirmed **installed**: `anthropic 0.116.0`, `ollama 0.6.2`, `langchain-anthropic 1.4.8`.
- **`grep -in "mcp" requirements.txt` → NO match.** **`import mcp` → NOT INSTALLED.** So **US-MEMO-5's MCP half has no floored library**, while every other U19 need is already satisfied.
- Suggestive frozen detail: U4's frozen test asserts `"mcp" not in _top_level_imports(provider_module)` — the **name** was anticipated, but **no package was ever floored**.
- Relevant precedent: **U20 held a hard "no new dependency" line**; **U18's tech-stack-decisions closes with "No new dependencies"**. **U19 would be the first unit to break that streak** — which is a decision worth making deliberately, not by import.

This is a **tech-stack decision Part 2 must record**, and it is **entangled with Q2**: under **Q2-A**, the tool **handlers** need **no MCP library at all** (they are pure functions over `Rulebook`/decision records), and only the **transport** would.

- **(A) DEFER the MCP protocol/SDK to composition/deploy-config; U19 adds NO new dependency.** U19 builds the **tool-handler layer** + an **injected transport seam**; the actual MCP protocol binding is a **composition/deploy-config concern** — **exactly where U4 already frozen-deferred the real google-genai client** (*"wrapped to this minimal `LLMClient` seam at composition time (a deploy-config/secrets concern)"*). **Every BR-MEXT-6/7/8/9 invariant is fully verified at tier-U with no MCP package present.** **(Recommended if Q2=A)** — it keeps the no-new-dependency streak, mirrors the frozen deferral pattern precisely, and adds nothing U19's own invariants need.
- **(B) FLOOR an MCP SDK now** (e.g. add `mcp>=x.y` to `requirements.txt`) and build against it. Highest fidelity to *"two MCP servers"* as a deliverable; costs the project's **first new runtime dependency since the floor was set**, and pulls a protocol into a unit whose invariants **do not depend on it**.
- **(C) FLAG as a decomposition/tech-stack gap and STOP** — on the argument that FR-MEMO-5 + PROJECT-BRIEF §9 promise **MCP servers** as a real deliverable, so "handlers only, protocol deferred" may under-deliver US-MEMO-5, and the missing floor may be an oversight worth an explicit decision before any U19 code exists.

**[Answer]**: **A** — **defer the MCP protocol/SDK to composition/deploy-config; U19 adds no new dependency.** U19 builds the **tool-handler layer + an injected transport seam**; the actual MCP protocol binding is a **composition/deploy-config concern**, mirroring **exactly where U4 already deferred the real client**. **Every BR-MEXT-6/7/8/9 invariant is fully verified at tier-U with no MCP package present.** This **preserves the no-new-dependency streak U18 and U20 both held**, and is **consistent with Q2-A** (the handlers need no MCP library at all).

**Because Q4-A touches PROJECT-BRIEF's literal *"MCP servers"* deliverable language, it is logged as its own named register item — `MCP-TRANSPORT-DEFERRED` (§3.6) — exactly as `OUTLIER-IN-PROSE` was.**

---

## 3.5 MANDATORY AMBIGUITY-CHECK — RUN 2026-07-17 against Q1–Q4 (all A) + the frozen FD + the frozen contracts → **CLEAN (4 folds; no surface-and-stop)**

Checked against: **BR-MEXT-1..13**; the four-module inventory; the **`OutlierSignal`** Protocol; the **MCP boundary** (supplementary / read-only / demographic-free); the frozen `provider.py` + `citation_validator.py` + `prompt_builder.py` + `tests/test_provider.py`; `unit-of-work-dependency.md:48`; the underwriting-rules skill. **Every fold resolves against a frozen artifact or an established precedent — none improvised.**

### NFR-MEXT-Fold-1 — Q1-A is **strictly stronger** than option (C)'s "duplicate signal", and the reason is concrete
Option (C) argued U4's own suite already runs both tests, making a U19 mirror redundant. **That is not quite true, and the gap is exactly the bug class the guard exists for.** `test_only_gemini_adapter_is_present_no_claude_ollama_mcp` inspects **`dir(provider_module)`** — a **live namespace**, evaluated **in whatever import state the test session happens to be in**. U4's own test lives in a module that imports **only U4**; under pytest's default collection order (`memo_agent_core` **before** `memo_extensions`), U19's modules may **not yet be imported** when it executes — so a **module-level namespace pollution originating in U19** (e.g. an accidental `provider_module.ClaudeAdapter = ...` monkeypatch at import time) **would not be caught by U4's own test**. The **U19-owned mirror runs in a module that definitely imports U19's adapters**, so it **does** catch it. **Conclusion: (A) is not a duplicate — it is strictly stronger in the one context that matters.** Folded into **NFR-MEXT-FROZEN-1**.

### NFR-MEXT-Fold-2 — under Q2-A + Q4-A, what exactly is the *"server"* that BR-MEXT-7's read-only scan attaches to?
`unit-of-work.md:238` / `services.md:46` say *"two read-only **servers**"*, but Q4-A defers the **protocol transport**. So *"server"* at this stage = **the tool-handler surface** (`mcp_tools.py`), with the transport an injected seam. **Resolution**: **NFR-MEXT-MCPRO-1's read-only scan attaches to the handler module** — **where a write could actually be written** — so the invariant is verified **at full strength with no protocol present**; a transport binding **cannot introduce a write the handlers do not expose**. This is the **exact shape of U4's own deferral** (the `LLMClient` seam is tested; the real client is composed later). **The deliverable-language consequence is registered as `MCP-TRANSPORT-DEFERRED` (§3.6) rather than absorbed silently.**

### NFR-MEXT-Fold-3 — Q3-A's swap teeth attach to the **OUTPUT projection**, not the caller (a sharpening, not a contradiction)
Q3-A says *"identical financials, swapped name/gender/city → byte-identical supplementary context"*. **Where does `decisions-tools`' leak risk actually live?** It reads **stored committed decision records about other applicants** — the demographics are in **the data it returns**, not in the caller's request. So the teeth must be: **seed the fake decision-record source with records differing ONLY in demographics → assert the returned projection is byte-identical**, which **directly proves the projection drops demographics** (the real BR-MEXT-9 guarantee). The **input** side is then covered by the **same by-construction argument Q3-A applies to `rulebook-tools`**: the query type **carries no demographic field**, so a demographic **cannot enter either surface**. **Both halves are non-vacuous; neither needs a decision.** Folded into **NFR-MEXT-BIAS-1**.

### NFR-MEXT-Fold-4 — "U4 is unmodified" must be verified **behaviorally**, not by a file-hash/mtime pin
The §2.5 draft said FROZEN-1 asserts *"no file under `backend/memo_agent_core/` is modified"*. **Mechanizing that as a content-hash or mtime pin would be wrong**: mtime is meaningless across a git checkout, and a hash pin would **false-fail the day U4 is ever legitimately amended** (e.g. if `OUTLIER-IN-PROSE` is one day resolved toward a U4 amendment **with the hold explicitly lifted**) — turning a guard into an obstacle. **No prior unit did this**; session-level mtime verification has always been a **reviewer/agent check, never a test**. **Resolution**: FROZEN-1 verifies the frozen boundary by **(i)** the two **behavioral** mirror assertions (Q1-A) and **(ii)** an **import-discipline scan** (U19's only `backend.*` imports are its three frozen edges) — both fail loudly on a **real** violation and stay green through a **deliberate** future amendment. Folded into **NFR-MEXT-FROZEN-1**.

**Verdict: CLEAN.** No genuine gap requires a decision. Folds 1 and 3 **strengthen** the answers; Folds 2 and 4 **pin mechanization** that would otherwise have been improvised at Code-Gen. → **Part 2 generated.**

---

## 3.6 ⚑ REGISTER ENTRY — `MCP-TRANSPORT-DEFERRED` (NEW named open item, opened 2026-07-17 by Q4-A)

> **Logged, not silently absorbed** — the same treatment as **`OUTLIER-IN-PROSE`** and the composition-root's **Q1-B divergence**. Its purpose is precise: **so *"two MCP servers"* as a stated PROJECT-BRIEF deliverable is NOT quietly understood as fully done when only the handler layer + injected seam exist at this stage.**

| Field | Value |
|---|---|
| **Name** | **`MCP-TRANSPORT-DEFERRED`** — the live MCP **protocol/transport** binding for `rulebook-tools` + `decisions-tools` |
| **Status** | **OPEN — deferred to composition / deploy-config (U23).** Not built, not floored, not tested at tier-U. |
| **Opened** | 2026-07-17, at U19's NFR Requirements Part 1, by the **Q4-A** resolution |
| **What U19 DOES deliver** | The **tool-handler layer** (pure functions over `Rulebook` / decision records) **+ an injected transport seam** with a fake. **All of BR-MEXT-6/7/8/9 is verified at full strength at tier-U.** |
| **What is NOT delivered yet** | The **live MCP protocol binding** — the handlers exposed **over MCP** to a real client. |
| **⚠️ Explicitly NON-BLOCKING for U19** | **This blocks NONE of U19's own invariants.** BR-MEXT-6 (sole citable source), BR-MEXT-7 (read-only), BR-MEXT-8 (non-fatal miss) and BR-MEXT-9 (demographic-free) are **each fully testable without the transport** (NFR-MEXT-Fold-2). **Only the live-protocol deliverable itself is outstanding.** |
| **Future options** | (a) floor an MCP SDK + bind the transport in **deploy-config (U23)**; (b) a dedicated later pass; (c) Phase 3. |

**The evidence, cited so a future reader need NOT re-derive it:**

| # | Evidence | Verified |
|---|---|---|
| 1 | **No MCP library is floored** — `grep -in "mcp" requirements.txt` → **NO match** | on disk, 2026-07-17 |
| 2 | **No MCP library is installed** — `import mcp` → **NOT INSTALLED** (while `anthropic 0.116.0` / `ollama 0.6.2` / `langchain-anthropic 1.4.8` **are** installed — so **provider breadth needs nothing new**) | on disk, 2026-07-17 |
| 3 | **Anticipated-but-unfloored** — U4's frozen `test_provider.py` asserts `"mcp" not in _top_level_imports(provider_module)`: **the name was anticipated, but no package was ever floored** | frozen test, read-only |
| 4 | **The composition-deferral precedent** — frozen `provider.py`: the real client *"is wrapped to this minimal `LLMClient` seam **at composition time** (a deploy-config/secrets concern)"*. U19's transport deferral is **the same shape**, not a new pattern | frozen `provider.py` |
| 5 | **The no-new-dependency streak** — U18's `tech-stack-decisions.md` closes with *"No new dependencies"*; U20 held the same hard line. U19 would be the **first** to break it — a decision worth making **deliberately, not by import** | frozen artifacts |
| 6 | **The deliverable language this protects** — PROJECT-BRIEF §3 C4 (*"MCP servers expose rulebook and decisions DB as tools"*) + §9; FR-MEMO-5; US-MEMO-5 | brief / requirements |

---

## 4. HOLDS (binding on Part 2)

- **`memo-agent-core` (U4, frozen P1) NOT modified** — imported/composed only. The two frozen U4 tests **must stay green** (BR-MEXT-11 / NFR-MEXT-FROZEN-1); U4's `route_borderline` stub **stays not-wired**.
- **`outlier-model` (U18) NOT touched and NOT imported** — reached only as a **handed-in `OutlierSignal`**; the interop self-test constructs `OutlierResult` **by value, never by import**.
- **`ui-outlier-view` (U20), WIRE-1, the closed composition root, all 17 frozen P1 units — NOT touched.**
- **No live LLM call, no key, no network** at tier-U (the frozen U4 discipline, extended to Claude + Ollama). **No live Docker/DB** — the `audit-store` edge is exercised through the `decisions-tools` seam.
- **tier-B NOT authorized** (and **N/A** — U19 never touches the corpus); the **`audit_store` Docker-guard gap NOT touched**; **no other unit started**; the **23-unit decomposition unchanged**.
- **`OUTLIER-IN-PROSE` stays OPEN and out of scope** (BR-MEXT-13 / NFR-MEXT-SCOPE-1) — not reopened, not absorbed.
- **The frozen FD (BR-MEXT-1..13 + the module inventory + `OutlierSignal` + the MCP boundary) is the substrate — targets attach to it, re-opening none.**
- **No NFR artifact, no code** until the four answers are filled, the ambiguity-check runs, and Part 2 is explicitly authorized.

## 5. Gate

- [x] **(1)** **Q1–Q4 answered — all A**; full question text + answers embedded (§3) per the standing convention.
- [x] **(2)** Mandatory **ambiguity-check RUN** (§3.5) → **CLEAN**, 4 folds, no surface-and-stop.
- [x] **(3)** **`MCP-TRANSPORT-DEFERRED`** opened as a **named register item** (§3.6) with its **six evidence rows** and its **explicit non-blocking scope**.
- [x] **(4)** **Part 2 GENERATED** — `guide-docs/build/memo-extensions/nfr-requirements/nfr-requirements.md` + `tech-stack-decisions.md`.
- [ ] **(5)** **NFR Requirements 2-option completion gate — AWAITING USER.** (1. Request Changes / 2. Continue to Next Stage → **NFR Design**.)

**STOPPED — no code, nothing under `backend/memo_extensions/`, `requirements.txt` NOT edited.** NFR Design does **not** begin until the gate is answered.
