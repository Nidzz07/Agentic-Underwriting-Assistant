# Tech-Stack Decisions — `ui-shell` (`ui-common` / U10)

**Stage**: BUILD → NFR Requirements (per-unit) · **Depth**: lighter (display-only shared surface).
**Unit**: U10 `ui-shell` · **Date**: 2026-07-07. The **FIRST frontend/React unit** (track switch from Python).
**Principle**: name only what makes the `NFR-UI-*` targets **checkable**; keep bundler/deploy topology + aesthetic
values **deferred**. **No LLM. Reference-not-own + WIRE-1 held** (fetches nothing real).

---

## Decisions

| # | Decision | Rationale / notes |
|---|---|---|
| **D1** | **React + Tailwind CSS** | The pinned UI stack (brief / FR-UI-5). `ui-shell` lives at `frontend/src/shell/`. |
| **D2** | **Plain JS/JSX — NO TypeScript** | FR-UI-5 (pinned). Enforced by **NFR-UI-NOTS-1** (no `.ts`/`.tsx`, no `tsconfig`). |
| **D3** | **Test runner + component testing: Vitest + React Testing Library + jsdom** | JS-native (no TS toolchain); RTL drives the **component** targets **COPY-1(b)** (badge label look-up) and **RBAC-1** (with a **stub `RoleContext.Provider`**). GATE-1 is now **structural** (copy-module vocabulary/namespace source) and **does not need RTL**. Standard, lightweight; no heavy new scope. |
| **D4** | **Lint mechanism: ESLint with a rule over the single `FORBIDDEN_TERMS` source** | Backs the **build-failing** lints (COPY-1, ADVISORY-1, TESTID-1) — one word-list, two checks (fold 1). Each lint ships a **detector self-test** (fold 2, non-vacuous). |
| **D5** | **no-TS + reference-not-own enforcement: file/import scan in CI** | NFR-UI-NOTS-1 (file-scan) + NFR-UI-REFNOTOWN-1 (no backend import, no real fetch). Cheap structural checks. |
| **D6** | **Node LTS + npm toolchain** | Frontend build toolchain is a **Code-Gen** tech-stack detail, **not cloud infra**. The **bundler/dev-server (e.g. Vite) and Vercel deploy topology are DEFERRED** — `deploy-config` (P2) / confirmed at Infra Design (likely SKIP). |
| **D7** | **Aesthetic tokens: direction pinned, VALUES deferred** | Refined-minimalism (NFR-UI-AESTHETIC-1); concrete fonts/colors/spacing decided at **NFR-Design / Code-Gen**. |
| **D8** | **No new backend/runtime dependency; no LLM; no real network** | The shell composes frozen **value shapes**; the wire contract is **WIRE-1** (composition-root), pinned **before `ui-queue`'s FD** — **not** authored here. |

---

## Deferred / referenced (not decided here)
- **Bundler / dev-server (Vite or equivalent) + Vercel deploy topology** → `deploy-config` (P2) / Infrastructure Design
  (likely a logged SKIP for `ui-shell`, confirmed after NFR).
- **WIRE-1 api/serialization contract** (endpoints, envelope, error shape, session-role delivery) → composition-root
  `api-contract` artifact, **hard checkpoint before `ui-queue`'s FD** (Deferred Decisions register).
- **Concrete aesthetic token values** → NFR-Design / Code-Gen.

**No new dependency beyond the standard React/Tailwind/Vitest/RTL/ESLint substrate; no LLM anywhere in `ui-shell`.**
