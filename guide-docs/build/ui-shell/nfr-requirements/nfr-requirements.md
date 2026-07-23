# NFR Requirements — `ui-shell` (`ui-common` / U10)

**Stage**: BUILD → NFR Requirements (per-unit) · shared shell / design-system unit
**Depth**: **lighter overall EXCEPT full rigor on the invariant / acceptance-criteria-bearing facets** (CON-BR4 language
facet, single-source copy, data-testid, no-TS).
**Unit**: U10 `ui-shell` — owns **CON-BR4 (language facet)**, FR-UI-3/4/5 · Story **US-UI-7** · **Date**: 2026-07-07.
**Built ON** the frozen FD (`domain-entities.md` / `business-rules.md` / `business-logic-model.md`, incl. the RoleGate
single-mechanism amendment) — **re-opening none of it**. Each `NFR-UI-*` target is a **pass/fail testable assertion**
traced to its FD rule (BR-UI-1..7). **Advisory-only; no LLM. Reference-not-own + WIRE-1 held as constraints, not new
scope** (the shell **fetches nothing real**).

---

## 0. Central testability principle

`ui-shell`'s invariant-bearing properties are testable **without a running backend or the WIRE-1 contract**, three ways:
1. **Build-failing lints + structural single-source checks** over the single-source modules (`shell/copy` +
   `FORBIDDEN_TERMS`) — COPY-1, ADVISORY-1, **GATE-1**, TESTID-1; each carries a **detector self-test** so it can never
   pass vacuously (the auth-rbac / secrets-config mechanism).
2. **Component-render assertions** (React Testing Library) — **COPY-1(b)** (badge label look-up) and **RBAC-1** (with a
   **stub `RoleContext.Provider`**).
3. **Structural / file-scan checks** — NOTS-1 (no `.ts`/`.tsx`), REFNOTOWN-1 (no backend import, no real fetch).

**No target tests a view's or a backend unit's internals, and none exercises the real wire** (WIRE-1 held — SCOPE-1) —
GATE-1 tests only `ui-shell`'s **copy-module vocabulary/namespace source**; the human-gate **render-context** attribution
is **U7-owned** (see GATE-1 delegation + SCOPE-1). The two FD folds are preserved: **ADVISORY-1 and GATE-1 share the ONE
`FORBIDDEN_TERMS` source** (no two word-lists); each check is **non-vacuous** (self-test).

---

## 1. Finalized `NFR-UI-*` targets (pass/fail; test tier stated)

### FULL RIGOR — invariant / acceptance-criteria-bearing

#### NFR-UI-COPY-1 — single-source copy; no inlined display string (BR-UI-1)
- **Assertion**: no view or shell primitive contains a Recommendation / Confidence / Role **display-label literal**
  outside `shell/copy`; every label is **imported** from it. The `RecommendationBadge`/`ConfidenceBadge` render their
  label by **look-up from the domain value**, never an inlined string.
- **Acceptance criteria**: (a) a **build-failing lint** flags any label literal outside `shell/copy`; (b) a component
  passing `value="DECLINE-RECOMMEND"` renders the canonical label sourced from `RECOMMENDATION_LABELS`; (c) **detector
  self-test** — a synthetic inlined label triggers the lint.
- **Test tier**: **structural / lint** (unit).

#### NFR-UI-ADVISORY-1 — advisory vocabulary, lexical lint over the single source (BR-UI-2)
- **Assertion**: for **system output**, "recommendation" is required and "decision" is forbidden; the decline label
  **preserves `-RECOMMEND`**; a **bare `"DECLINE"`** is forbidden — enforced by a **build-failing lint** over the **one**
  `FORBIDDEN_TERMS` source (**fold 1**: the same source GATE-1 uses).
- **Acceptance criteria**: (a) each enumerated forbidden token (bare `DECLINE`; `decision`/`approved`/`declined` as
  system output) **fails the build**; (b) the canonical labels (with `-RECOMMEND`, "recommendation") **pass**;
  (c) **detector self-test** — a synthetic violation is flagged (non-vacuous).
- **Test tier**: **structural / lint** (unit).

#### NFR-UI-GATE-1 — human-gate vocabulary/namespace source, distinct from system output (BR-UI-3, copy-module facet)
- **Assertion**: `ui-shell`'s **copy module** exposes the human `CommitAction` label namespace `{approve, override}`
  (`approve` = agree; `override` = disagree with a **mandatory non-blank reason**, `approve` requires **none** — matching
  `CommittedDecision.reason`) as a namespace **DISTINCT** from the system `Recommendation` labels; and the
  finalization/attribution vocabulary is drawn from the **SAME single `FORBIDDEN_TERMS` source** as ADVISORY-1 (**fold 1**
  preserved — one list, two checks: lexical vs contextual).
- **Acceptance criteria** (all authorable in `ui-shell`, **no view/gate render**): (a) the copy module defines the
  `CommitAction` labels `{approve, override}`, asserted **≠** `RECOMMENDATION_LABELS` — and specifically the human
  `override` label asserted **≠** the system `DECLINE-RECOMMEND` label; (b) GATE-1's contextual check reads the **SAME
  `FORBIDDEN_TERMS`** source object as ADVISORY-1 (fold 1), verified **structurally** (one source object, both
  consumers); (c) **detector self-test** — a synthetic collision (a `CommitAction` label equal to a `Recommendation`
  label, or a second divergent word-list) is **flagged** (non-vacuous).
- **Delegation (recorded explicitly)**: the **render-context attribution** — "finalization-implying framing renders only
  within the human-gate component, attributed to the human" — is **owned and tested by `ui-approval-gate` (U7)**, which
  composes the shell and owns the gate component. It is **NOT tested in `ui-shell`** (consistent with SCOPE-1 +
  reference-not-own between UI units). `ui-shell` provides the enforceable **vocabulary/namespace SOURCE** that makes
  U7's attribution test possible.
- **Test tier**: **structural / unit** (over the copy module).

#### NFR-UI-TESTID-1 — `data-testid` convention (BR-UI-5)
- **Assertion**: every interactive / assertion-relevant shell primitive exposes a **stable `data-testid`** per the
  documented naming convention (`domain-entities.md §6`).
- **Acceptance criteria**: (a) a lint/test asserts the convention holds across shell primitives; (b) **detector
  self-test** — a primitive missing/misnaming its testid is flagged.
- **Test tier**: **structural / component** (unit).

#### NFR-UI-NOTS-1 — no TypeScript (BR-UI-6)
- **Assertion**: the unit is **plain JS/JSX + React + Tailwind** — **no `.ts`/`.tsx`, no TS config/toolchain**.
- **Acceptance criteria**: a file-scan over the `ui-shell` tree finds **zero** `.ts`/`.tsx` files and **no** TS config
  (`tsconfig*.json`); CI fails if any appear.
- **Test tier**: **structural** (unit).

### MEDIUM RIGOR — invariant coverage

#### NFR-UI-RBAC-1 — RoleGate cosmetic only; no authorization decision (BR-UI-4)
- **Assertion**: `RoleGate` renders/hides/disables purely on the **injected `RoleContext` value** (via `useCurrentRole()`)
  and calls **no** authorization function; it owns no security decision (real boundary = `auth-rbac` `authorize` +
  `DecisionCommitService`, SEC-4).
- **Acceptance criteria**: (a) with a **stub `RoleContext.Provider`** set to `underwriter`, an `act` affordance renders;
  set to `auditor`, it is hidden/disabled; (b) a static check asserts `RoleGate` imports **no** authz/backend module and
  invokes no `authorize`-style call.
- **Test tier**: **component + structural** (unit).

### LIGHTER / SOFT — recorded, not over-specified

#### NFR-UI-REFNOTOWN-1 — reference-not-own + WIRE-1 held (BR-UI-7) *(light structural guard)*
- **Assertion**: `ui-shell` **imports no backend production module** (cross-language: no Python/`backend/*` import) and
  makes **no real network fetch** — it **fetches nothing real** (WIRE-1 held); Role/Recommendation/Confidence are
  consumed as **value shapes** only.
- **Acceptance criteria**: a structural scan finds no `import` from a backend path and no `fetch`/`axios` call to a real
  endpoint in the shell (stubs/seams only). Realizes the held constraint checkably; **designs no wire contract**.
- **Test tier**: **structural** (unit).

#### NFR-UI-AESTHETIC-1 — refined-minimalism direction; token VALUES deferred *(soft)*
- **Statement**: the aesthetic **direction** is pinned (refined-minimalism; distinctive-but-professional type; restrained
  palette; **no** Inter/Roboto/Arial default, **no** purple-gradient cliché). Concrete **token values**
  (fonts/colors/spacing) are **deferred to NFR-Design / Code-Gen** — recorded here as a **shape/target**, not specified.
- **Test tier**: **N/A (deferred design decision)**.

#### NFR-UI-PERF-1 / NFR-UI-A11Y-1 — soft, observed
- **PERF-1**: shell primitives are presentational; **render latency + bundle size are observed, non-gating** (no SLO).
- **A11Y-1**: interactive primitives should be **semantic + keyboard-focusable** and carry accessible labels (aligned
  with NFR-EXPLAIN-1) — a **soft target**; detailed a11y verification lands with the view units / NFR-Design.
- **Test tier**: **observed / soft**.

#### NFR-UI-SCOPE-1 — scoped exclusions *(GOVERNANCE / EXCLUSION STATEMENT — not a runtime test)*
- **Statement**: the `NFR-UI-*` set tests **only** `ui-shell`'s own conventions (copy single-source, advisory vocabulary,
  the human-gate **vocabulary/namespace source**, RBAC cosmetics, testid, no-TS, reference-not-own). It does **NOT** test
  the C5 **view** units' internals, any **backend** unit's internals, or the **WIRE-1** api-contract (owned by the
  composition-root, pinned **before `ui-queue`'s FD**). Enforced by review.
- **U7 boundary (GATE-1 consistency)**: the human-gate **render-context attribution** ("finalization framing renders only
  within the human-gate component") is **owned and tested by `ui-approval-gate` (U7)**, not `ui-shell` — `ui-shell` owns
  only the enforceable **vocabulary/namespace SOURCE** (GATE-1). This makes SCOPE-1 and GATE-1 **consistent** (no target
  renders a view/gate).
- **Test tier**: **N/A (governance statement)**.

---

## 2. Traceability (target → FD rule → invariant → tier → rigor)

| Target | FD rule | Invariant | Tier | Rigor |
|---|---|---|---|---|
| NFR-UI-COPY-1 | BR-UI-1 | CON-BR4 single-source copy | lint | full |
| NFR-UI-ADVISORY-1 | BR-UI-2 | CON-BR4 advisory vocabulary / FR-RULES-5 | lint | full |
| NFR-UI-GATE-1 | BR-UI-3 | human-gate vocabulary/namespace source (hard-constraint #2; render-context attribution → U7) | structural / unit | full |
| NFR-UI-TESTID-1 | BR-UI-5 | FR-UI-3 | lint / component | full |
| NFR-UI-NOTS-1 | BR-UI-6 | FR-UI-5 | structural | full |
| NFR-UI-RBAC-1 | BR-UI-4 | SEC-4 cosmetic facet / reference-not-own | component / structural | medium |
| NFR-UI-REFNOTOWN-1 | BR-UI-7 | reference-not-own / WIRE-1 held | structural | soft |
| NFR-UI-AESTHETIC-1 | — | refined-minimalism (values deferred) | N/A | soft |
| NFR-UI-PERF-1 | — | soft budget | observed | soft |
| NFR-UI-A11Y-1 | — | accessibility (NFR-EXPLAIN-1 aligned) | observed | soft |
| NFR-UI-SCOPE-1 | BR-UI-7 | reference-not-own / WIRE-1 boundary | N/A | governance |

**No orphaned FD rule**: BR-UI-1..7 each map to a target.

---

## 3. Security-Guardrails compliance (enabled extension)

| Control | Status | Rationale |
|---|---|---|
| Input validation | **N/A (referenced)** | The shell fetches nothing real (REFNOTOWN-1); application-input validation is `intake`'s SEC-2. |
| Prompt-injection defense | **N/A** | No LLM/prompt path in `ui-shell`. |
| Secrets management | **N/A** | No secret handled; env/keys are `secrets-config`'s SEC-3. |
| Read-only DB access for audit role | **N/A (referenced)** | The auditor read-only distinction is surfaced **cosmetically** (RBAC-1); enforcement is `auth-rbac` + `audit-store` (SEC-4). |
| Audit logging | **N/A** | The shell persists nothing. |
| **Least-privilege UI framing (advisory-only + human-gate)** | **Compliant (owns the CON-BR4 language facet)** | COPY-1 / ADVISORY-1 / GATE-1 make the advisory + human-gate framing **build-checkable**. |

No blocking finding.

---

## 4. Settled items held (not re-opened)
- The **frozen FD** (BR-UI-1..7 + the design-system surface, incl. the RoleGate single-mechanism amendment) is the
  substrate — NFR builds testable targets **on** it.
- **Reference-not-own (cross-language)** + **WIRE-1** — held; realized checkably as **NFR-UI-REFNOTOWN-1** (imports no
  backend, fetches nothing real); **no wire/serialization work here**. WIRE-1 stays owned by the composition-root,
  pinned **before `ui-queue`'s FD**.
- **Aesthetic token VALUES** deferred to NFR-Design / Code-Gen (AESTHETIC-1). **Perf / bundle** observed, non-gating.
- **Infrastructure Design** for `ui-shell` **not pre-committed** — likely a logged SKIP (source-level shell; Vercel
  topology is `deploy-config` P2) — confirmed at that stage after NFR. Settled non-edits stay closed:
  `PROJECT-BRIEF.md`, `user-journey.md`, every built unit's code/design.
