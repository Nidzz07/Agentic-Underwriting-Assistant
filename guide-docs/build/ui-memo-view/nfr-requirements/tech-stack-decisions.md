# Tech-Stack Decisions — `ui-memo-view` (U6)

**Stage**: BUILD → NFR Requirements (per-unit) · **Depth**: lighter (display) + fetch-lifecycle addendum + three-region
read-only-separation addendum · **Unit**: U6 `ui-memo-view` · **Date**: 2026-07-09. The **second UI unit that actually
fetches** (WIRE-1 R4, mocked in tests) and the **first** to render the DecisionMemo three-region shape.
**Principle**: **inherit** ui-shell's frozen substrate (and ui-queue's applied convention) unchanged; name only what makes
the `NFR-MEMO-*` targets **checkable**; keep aesthetic values + bundler/deploy topology **deferred**. **No LLM. No live
backend** (R4 doubled). Q1–Q7 all **A**.

---

## Decisions

| # | Decision | Rationale / notes |
|---|---|---|
| **D1 (inherited)** | **React + Tailwind CSS** | The pinned UI stack (FR-UI-5). `ui-memo-view` lives at `frontend/src/memoView/`, composing frozen `ui-shell` primitives (incl. **first use** of `ReadOnlyRegion`). |
| **D2 (inherited)** | **Plain JS/JSX — NO TypeScript** | FR-UI-5; enforced by **NFR-MEMO-NOTS-1** (no `.ts`/`.tsx`, no `tsconfig`). |
| **D3 (inherited)** | **Vitest + React Testing Library + jsdom** | Drives the component targets (SEPARATION-1, ERROR-1, PENDING-1, LISTORDER-1, VIEWONLY-1 render, the four per-state renders + the consolidated transition test of FETCH-1). Same runner as ui-shell/ui-queue — no new toolchain. |
| **D4 (inherited)** | **ESLint over the single `FORBIDDEN_TERMS` source** | Backs COPY-1 / ADVISORY-1 / NAMESPACE-1 / TESTID-1 lints — **reuses** ui-shell's one word-list (no second list); each lint ships a **detector self-test** (non-vacuous). Mechanism **reused, not modified**: a **new `eslint.config.js` block** registers `no-inline-label` + `advisory-vocabulary` on `src/memoView/**` (mirroring the queue block) + a `memo-testid-convention` rule (mirroring `queue-testid-convention`). **No `src/shell` file modified.** |
| **D5 (inherited)** | **File / import scan in CI (StructuralGuard convention)** | NFR-MEMO-NOTS-1 (no `.ts`/`.tsx`), VIEWONLY-1 (no `RoleGate` import, **no router import**, no commit affordance), PERF-1 (single-resource, no unbounded fetch path). Mirrors ui-queue's `nots` / `noRoleGateImport` / `noRouterImport` / `boundedFetch` StructuralGuard scans — **as a convention, not an import**. |
| **D6 (NEW) — R4 fetch-double: injected/capturing function via prop (Q1-A)** | `MemoView` receives its fetch function as a **prop** (`fetchSeam`, per the FD's own local memo fetchSeam, Q6-A); production wires the real R4 fetch at the composition root, tests inject a **capturing double** that **records the requested `applicationId`** and returns programmed responses. **One** double construction for the whole suite (**NFR-MEMO-Fold-A**, ui-queue Fold-1 precedent) — each test programs it (`status:"ready"` → `ready`; `status:"pending"` → `pending`; reject/error-envelope → `error`) and reads the recorded id only where asserted (ERROR-1 Retry, the transition test's retry leg). Makes ERROR-1's "same `applicationId`, not a different id" assertion (Q4-A) clean **and** avoids a second mock pattern. |
| **D7 (NEW) — DOM-containment separation-teeth in jsdom (Q2-A / NFR-MEMO-Fold-B)** | SEPARATION-1 (the load-bearing target) proves CON-BR2-TYPE structurally via **`Node.contains()` + scoped `within()` queries** — jsdom implements `Node.contains()` for **arbitrary-depth** descendants (and returns `false` for a sibling's subtree), so `!narrative.contains(readonly)` / `!readonly.contains(narrative)` + `within(readonly).getByTestId('memo-recommendation')` present + `within(narrative).queryByTestId('memo-recommendation')` null is a **sound sibling non-containment** assertion, not just parent-child. **Real teeth** (fails if the recommendation were nested under the narrative), not testid-presence-only. |
| **D8 (NEW) — discriminator + list-order teeth need two distinct ready fixtures (Q3-A / NFR-MEMO-Fold-C)** | PENDING-1's teeth needs an **empty-lists** `status:"ready"` memo (proving `ready ≠ pending` isn't an emptiness heuristic; also exercises BR-MEMO-9's empty-list neutral-copy branch); LISTORDER-1's teeth needs a **populated, deliberately non-sorted** `status:"ready"` memo (proving no client re-sort). **Two complementary fixtures, no shared one** — Code-Gen builds both deliberately. The **reverse** case (`status:"pending"` with a non-null memo) is a **WIRE-1 contract violation** and is **not** fabricated. |
| **D9 (NEW) — state-management mechanics: deferred to Code-Gen** | `MemoView` holds `{ state, view, error }`; the **concrete hook/store shape**, retry debounce, and request cancellation are **Code-Gen** mechanics. NFR pins only the **testable behavior** (the four states + same-resource Retry), not the mechanism. |
| **D10 (inherited)** | **Node LTS + npm toolchain** | Frontend build toolchain is a Code-Gen detail; the **bundler/dev-server (Vite) + Vercel deploy topology stay DEFERRED** → `deploy-config` (P2) / confirmed at Infra Design (likely SKIP for `ui-memo-view`). |
| **D11 (NEW) — deferred display values** | **aesthetic token values** (inherited from ui-shell tokens), the **minimal profile-header field set** (`ProfileContextHeader` — which `ApplicantProfile` fields to show), and **loading-placeholder markup** are **visual/tuning values deferred** to NFR-Design / Code-Gen — recorded as targets/shapes, not specified. |
| **D12 (inherited)** | **No new backend/runtime dependency; no LLM; no real network in tests** | The memo view composes frozen **value shapes** (WIRE-1 `MemoView` / memo-agent-core `DecisionMemo`) and fetches R4 through the double; the R4 **route implementation** is WIRE-1/Build & Test, **not** authored here. It **imports no `ui-queue` code** — that unit's fetchSeam/StructuralGuard/testid-lint are **mirrored as a convention**. |

---

## Deferred / referenced (not decided here)
- **Bundler / dev-server (Vite or equivalent) + Vercel deploy topology** → `deploy-config` (P2) / Infrastructure Design
  (likely a logged SKIP for `ui-memo-view`, confirmed after NFR).
- **WIRE-1 R4 route implementation** (`backend/app/main.py`) → Build & Test integration (not this unit).
- **State-management mechanics** (hook/store, retry debounce, cancellation) → Code-Gen (D9).
- **Concrete display values** (aesthetic token values, the minimal profile-header field set, loading-placeholder markup)
  → NFR-Design / Code-Gen (D11).
- **`narrative_prose` advisory conformance** → **memo-agent-core** (CON-BR2, backend, at draft time) — **out of scope**
  for this view by the BR-MEMO-2 governance boundary (nfr-requirements.md §0).

**No new dependency beyond the standard React/Tailwind/Vitest/RTL/jsdom/ESLint substrate already established by `ui-shell`
and applied by `ui-queue`; no LLM anywhere in `ui-memo-view`; no live backend (R4 doubled); no `src/shell` edit and no
`ui-queue` import.**
