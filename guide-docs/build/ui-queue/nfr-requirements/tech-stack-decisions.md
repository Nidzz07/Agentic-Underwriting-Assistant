# Tech-Stack Decisions — `ui-queue` (U5)

**Stage**: BUILD → NFR Requirements (per-unit) · **Depth**: lighter (display) + async-state addendum · **Unit**: U5
`ui-queue` · **Date**: 2026-07-09. The **first UI unit that actually fetches** (WIRE-1 R2, mocked in tests).
**Principle**: **inherit** ui-shell's frozen substrate unchanged; name only what makes the `NFR-QUEUE-*` targets
**checkable**; keep aesthetic values + bundler/deploy topology **deferred**. **No LLM. No live backend** (R2 doubled).

---

## Decisions

| # | Decision | Rationale / notes |
|---|---|---|
| **D1 (inherited)** | **React + Tailwind CSS** | The pinned UI stack (FR-UI-5). `ui-queue` lives at `frontend/src/queue/`, composing frozen `ui-shell` primitives. |
| **D2 (inherited)** | **Plain JS/JSX — NO TypeScript** | FR-UI-5; enforced by **NFR-QUEUE-NOTS-1** (no `.ts`/`.tsx`, no `tsconfig`). |
| **D3 (inherited)** | **Vitest + React Testing Library + jsdom** | Drives the component targets (PENDING-1, ERROR-1, PAGINATION-1, VIEWONLY-1 render, the four per-state renders + the consolidated transition test of FETCH-1). Same runner as ui-shell — no new toolchain. |
| **D4 (inherited)** | **ESLint over the single `FORBIDDEN_TERMS` source** | Backs COPY-1 / NAMESPACE-1 / TESTID-1 lints — **reuses** ui-shell's one word-list (no second list); each lint ships a **detector self-test** (non-vacuous). Mechanism **reused, not modified**. |
| **D5 (inherited)** | **File / import scan in CI** | NFR-QUEUE-NOTS-1 (no `.ts`/`.tsx`), SELECT-1 (no router import), VIEWONLY-1 (no `RoleGate` import), PERF-1 (no unbounded fetch path). Cheap structural checks. |
| **D6 (NEW) — R2 fetch-double: injected/capturing function** | **Q1-A.** `QueueView` receives its fetch function via **prop/context**; production wires the real R2 fetch at the composition root, tests inject a **capturing double** that **records the requested page** and returns programmed responses. **One** double construction for the whole suite (**NFR-QUEUE-Fold-1**) — each test programs it (resolve non-empty → `ready`; `items:[]`/`total:0` → `empty`; reject/error-envelope → `error`) and reads the recorded page only where asserted (RETRY-1, the page transition). Makes RETRY-1's "page N, not 1" assertion clean **and** avoids a second mock pattern. |
| **D7 (NEW) — state-management mechanics: deferred to Code-Gen** | The queue holds `{ state, page, items, error }`; the **concrete hook/store shape**, retry debounce, and request cancellation are **Code-Gen** mechanics (per **Fold-B**). NFR pins only the **testable behavior** (states + position-preserving Retry), not the mechanism. |
| **D8 (inherited)** | **Node LTS + npm toolchain** | Frontend build toolchain is a Code-Gen detail; the **bundler/dev-server (Vite) + Vercel deploy topology stay DEFERRED** → `deploy-config` (P2) / confirmed at Infra Design (likely SKIP for `ui-queue`). |
| **D9 (NEW) — deferred display values** | **skeleton-row count** (Q2-A), **default page `size`** (N2), and **aesthetic token values** (inherited from ui-shell tokens) are **visual/tuning values deferred** to NFR-Design / Code-Gen — recorded as targets/shapes, not specified. |
| **D10 (inherited)** | **No new backend/runtime dependency; no LLM; no real network in tests** | The queue composes frozen **value shapes** and fetches R2 through the double; the R2 **route implementation** is WIRE-1/Build & Test, **not** authored here. |

---

## Deferred / referenced (not decided here)
- **Bundler / dev-server (Vite or equivalent) + Vercel deploy topology** → `deploy-config` (P2) / Infrastructure Design
  (likely a logged SKIP for `ui-queue`, confirmed after NFR).
- **WIRE-1 R2 route implementation** (`backend/app/main.py`) → Build & Test integration (not this unit).
- **State-management mechanics** (hook/store, debounce, cancellation) → Code-Gen (D7 / Fold-B).
- **Concrete display values** (skeleton-row count, default page `size`, aesthetic token values) → NFR-Design / Code-Gen.

**No new dependency beyond the standard React/Tailwind/Vitest/RTL/jsdom/ESLint substrate already established by `ui-shell`;
no LLM anywhere in `ui-queue`; no live backend (R2 doubled).**
