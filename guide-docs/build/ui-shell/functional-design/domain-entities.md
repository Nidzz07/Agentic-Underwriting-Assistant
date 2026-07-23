# Domain Entities — `ui-shell` (`ui-common` / U10)

**Stage**: BUILD → Functional Design (per-unit) · shared shell / design-system unit · **Depth**: standard
**Unit**: U10 `ui-shell` · **Date**: 2026-07-07 · owns **CON-BR4 (language facet)**, FR-UI-3/4/5 · Story **US-UI-7**.
**Scope**: The **shared design-system surface** — the modules/primitives every C5 view unit imports and conforms to. A UI
unit's "entities" are its **module/primitive inventory** (names + prop shapes), not data records. **React + Tailwind,
NO TypeScript** (FR-UI-5). **ui-shell owns NO business logic** — no rule eval, no authorization *decision*, no LLM, no
commit. It **imports no backend production code**; it consumes backend **shapes** by value (reference-not-own).

---

## 1. The design-system surface (what `ui-shell` exports)

`ui-shell` lives at `frontend/src/shell/` and is the **single source** of the app-wide UI conventions. It exports four
concerns; every C5 view (`ui-queue`, `ui-memo-view`, `ui-approval-gate`, `ui-override-form`, `ui-history`, and the
Phase-2 `ui-outlier-view`) **composes them and inherits the conventions** — nothing app-wide is redefined per view.

| Concern | Module | Owns |
|---|---|---|
| **Copy / strings** (§2) | `shell/copy` | the ONLY place Recommendation / Confidence / Role **display labels** + advisory vocabulary + the forbidden/required word-list are defined |
| **Primitives** (§3) | `shell/components` | presentational React components: page frame, panel/region, read-only-region wrapper, `RecommendationBadge`, `ConfidenceBadge`, `RoleGate` |
| **Design tokens** (§4) | `shell/tokens` | the single aesthetic source (color / spacing / typography), refined-minimalism direction; **values deferred** to NFR-Design / Code-Gen |
| **Role seam** (§5) | `shell/session` | an abstracted Role provider/context — RoleGate reads the current Role from it; fed later by the real session response per **WIRE-1** |

---

## 2. Copy / strings module (`shell/copy`) — the single source (Q1 + Q2)

The **only** place any Recommendation / Confidence / Role display string is defined. Views and primitives **import from
here; never inline** a string (BR-UI-1). The module keys on the **frozen backend enum values** (verified in the built
code) and maps each to a **display label** + the copy conventions.

### 2.1 Canonical wire map — enums serialize BY VALUE, four heterogeneous casings (WIRE-1 invariant)

The copy module keys on these exact values; the future wire contract (**WIRE-1**) **must not remap or re-case them**.

| Domain enum | Source (frozen `str, Enum`) | Wire value(s) | Casing |
|---|---|---|---|
| **Recommendation** | `rules_engine.report_schema.Recommendation` | `APPROVE`, `REFER`, `DECLINE-RECOMMEND` | **UPPERCASE**, hyphenated suffix (FR-RULES-5) |
| **Confidence** | `rules_engine.report_schema.Confidence` | `High`, `Medium`, `Low` | **Title-case** |
| **Role** | `auth_rbac.roles.Role` | `underwriter`, `auditor`, `admin` | **lowercase** |
| **CommitAction** *(human gate action — distinct namespace)* | `audit_store.record_schema.CommitAction` | `approve` / `override` | **lowercase** (both values); the **human's** committed action (`approve` = agree; `override` = disagree, mandatory non-blank reason), NOT system output |

> **Namespace-distinctness note**: the human `CommitAction` values `approve` / `override` (lowercase) are a **different
> value space and namespace** from the system `Recommendation` values `APPROVE` / `REFER` / `DECLINE-RECOMMEND`
> (UPPERCASE). In particular the human **`override`** (disagree) must **never** be rendered as, or confused with, the
> system **`DECLINE-RECOMMEND`** — they are different concepts (a human's disagreement vs a system advisory). The copy
> module keeps these **two label namespaces separate** so a system recommendation can never be mistaken for the human's
> committed action — the concrete anchor for the Q3 human-vs-system separation (see `business-rules.md` BR-UI-3,
> `business-logic-model.md §4`).

### 2.2 Copy module contents (shapes; no visual values here)

| Export | Shape | Notes |
|---|---|---|
| `RECOMMENDATION_LABELS` | `{ APPROVE, REFER, "DECLINE-RECOMMEND" } → display string` | the `-RECOMMEND` suffix is **preserved** in the decline label; **never** a bare "DECLINE" |
| `CONFIDENCE_LABELS` | `{ High, Medium, Low } → display string` | — |
| `ROLE_LABELS` | `{ underwriter, auditor, admin } → display string` | for chrome/labelling only; not an authorization datum |
| `ADVISORY_VOCABULARY` | the required term (**"recommendation"**) + system-output phrasings | "decision" is **reserved** for the human's committed action (CON-BR4) |
| `FORBIDDEN_TERMS` | word-list backing the Q2 lint **and** the Q3 gate-attribution test | ONE co-located source (fold) — e.g. a bare `"DECLINE"`, or "decision"/"approved"/"declined" used as **system** output |

---

## 3. Shell primitives (`shell/components`) — presentational only

Every primitive is **presentational**: it receives a domain **value** as a prop and renders using tokens + copy. **No
primitive defines a display string** — the badge looks up its label from `shell/copy` (BR-UI-1 fold). Every
interactive / assertion-relevant primitive exposes a stable **`data-testid`** (FR-UI-3, §6).

| Primitive | Prop shape (JS/JSX — no TS) | Behavior |
|---|---|---|
| `AppFrame` | `{ children, user }` | page shell / layout chrome; hosts the Role context provider (§5) |
| `Panel` / `Region` | `{ title, children, testid }` | a bordered content region; layout primitive |
| `ReadOnlyRegion` | `{ children, testid }` | wraps read-only memo regions (recommendation / confidence) so views frame them as **read-only** (memo-agent-core three-region shape) |
| `RecommendationBadge` | `{ value, testid }` where `value ∈ {APPROVE, REFER, "DECLINE-RECOMMEND"}` | **looks up** its label from `RECOMMENDATION_LABELS`; applies a token style per value; **inlines no string** |
| `ConfidenceBadge` | `{ value, testid }` where `value ∈ {High, Medium, Low}` | looks up label from `CONFIDENCE_LABELS` |
| `RoleGate` | `{ can, children, fallback }` — `can ∈ {"act","read"}` | **cosmetic** show/hide/disable of an affordance; reads the current Role **internally** via `useCurrentRole()` from `RoleContext` (§5) — **no `role` prop**; owns **NO authorization decision** (§5, BR-UI-4). Tests inject by wrapping in a stub `RoleContext.Provider`. |

---

## 4. Design tokens (`shell/tokens`) — single aesthetic source, values deferred

The single source of the app's aesthetic, expressed as **CSS / Tailwind theme variables** so no view redefines
color/type/spacing. **Direction is pinned; concrete values are a later (NFR-Design / Code-Gen) decision.**

- **Direction (pinned, §1.3 of the plan)**: **refined-minimalism** — legible, trustworthy-professional, restraint over
  spectacle; a distinctive-but-professional type pairing (**not** Inter/Roboto/Arial defaults); a restrained palette
  (**no** purple-gradient cliché). Reconciled from the frontend-design skill's refined branch, **not** its maximalist
  default. Appropriate to a **BFSI audit-grade** surface.
- **Token categories (shapes now; values later)**: `color` (surface / text / border / status-accent per recommendation),
  `typography` (display + body families, scale), `spacing`, `radius`, `elevation`.
- The status-accent colors are **keyed by the same Recommendation values** as the copy module — one value space,
  two facets (label in `shell/copy`, accent in `shell/tokens`).

---

## 5. Role provider / session seam (`shell/session`) — abstracted (reference-not-own, WIRE-1)

- `RoleGate` reads the **current Role** from an **abstracted provider/context** (`RoleContext` + a `useCurrentRole()`
  hook), **not** from any hard-wired fetch. The seam's shape: `currentRole ∈ {underwriter, auditor, admin} | null`.
- **RoleGate does NOT define the wire retrieval.** How the real session/auth response delivers the current user's Role to
  this context is owned by **WIRE-1** (the FastAPI composition-root api-contract artifact), which **must be pinned before
  `ui-queue`'s FD** (`business-logic-model.md §5`). Until then the context is fed by a **test/stub provider** only.
- The Role is consumed as a **value shape**; **no `auth_rbac` Python is imported** into the React codebase (the first
  cross-language reference-not-own boundary — Python enum → React via API JSON, never a code import).
- **RBAC here is cosmetic** (defense-in-depth): the **real** boundary stays `auth-rbac`'s backend `authorize` +
  audit-store's `DecisionCommitService` re-check (SEC-4). The server rejects an unauthorized action even if the UI guard
  were bypassed (BR-UI-4).

---

## 6. `data-testid` convention (FR-UI-3)

- Every interactive / assertion-relevant shell primitive accepts and renders a **stable `data-testid`** following a
  documented naming convention (e.g. `shell-<primitive>-<purpose>`). Views pass a testid where they assert.
- **Checkable** (BR-UI-5): a lint/test asserts the convention holds for shell primitives; enforced at NFR/Code-Gen.

---

## 7. Boundary — what `ui-shell` does NOT own

- **No view screens** — no queue / memo / gate / override / history screen lives here (those are U5–U9).
- **No authorization decision** — that is `auth-rbac` (SEC-4); the shell's RoleGate is cosmetic (§5, BR-UI-4).
- **No commit / gate logic** — that is `audit-store`'s `DecisionCommitService`.
- **No rule evaluation, no LLM, no memo drafting** — pure presentation + conventions.
- **No wire contract** — endpoints / envelope / session-role delivery are **WIRE-1** (composition-root), not authored
  here; the shell fetches nothing real (`business-logic-model.md §3/§5`).
