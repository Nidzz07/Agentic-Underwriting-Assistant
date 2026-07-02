# Unit of Work — Story Map

**Phase / Stage**: DISCOVER → Units Generation (Part 2 — Generation)
**Project Type**: Greenfield
**Date**: 2026-07-02
**Status**: Generated at the Units Generation completion gate — awaiting **Request Changes / Approve & Continue → BUILD**.

This artifact proves the **completion criterion**: **all 40 stories** in `stories.md §8` are
assigned to **exactly one** of the 23 units (`unit-of-work.md §3`). Per-epic totals must match
disk exactly: **INTAKE 4, RULES 5, OUT 3, MEMO 7, UI 7, PLAT 12, ADMIN 2 = 40**
(**30 Phase 1 / 10 Phase 2**). Applies **F5(b)** (§4) and states the **`database` story-less
status** explicitly (§3) so it does not read as a coverage gap.

---

## 1. Forward map — every story → exactly one unit

| # | Story | Phase | Epic | Owning unit |
|--:|---|:--:|---|---|
| 1 | US-INTAKE-1 | 1 | INTAKE | `intake` |
| 2 | US-INTAKE-2 | 1 | INTAKE | `intake` |
| 3 | US-INTAKE-3 | 1 | INTAKE | `intake` |
| 4 | US-INTAKE-4 | 1 | INTAKE | `document-sanitizer` |
| 5 | US-RULES-1 | 1 | RULES | `rules-engine` |
| 6 | US-RULES-2 | 1 | RULES | `rules-engine` |
| 7 | US-RULES-3 | 1 | RULES | `rules-engine` |
| 8 | US-RULES-4 | 1 | RULES | `rules-engine` |
| 9 | US-RULES-5 | 1 | RULES | `rules-engine` |
| 10 | US-OUT-1 | 2 | OUT | `outlier-model` |
| 11 | US-OUT-2 | 2 | OUT | `outlier-model` |
| 12 | US-OUT-3 | 2 | OUT | `outlier-model` |
| 13 | US-MEMO-1 | 1 | MEMO | `memo-agent-core` |
| 14 | US-MEMO-2 | 1 | MEMO | `memo-agent-core` |
| 15 | US-MEMO-3 | 1 | MEMO | `memo-agent-core` |
| 16 | US-MEMO-4 | 1 | MEMO | `memo-agent-core` |
| 17 | US-MEMO-5 | 2 | MEMO | `memo-extensions` |
| 18 | US-MEMO-6 | 2 | MEMO | `memo-extensions` |
| 19 | US-MEMO-7 | 2 | MEMO | `memo-extensions` |
| 20 | US-UI-1 | 1 | UI | `ui-queue` |
| 21 | US-UI-2 | 1 | UI | `ui-memo-view` |
| 22 | US-UI-3 | 2 | UI | `ui-outlier-view` |
| 23 | US-UI-4 | 1 | UI | `ui-approval-gate` |
| 24 | US-UI-5 | 1 | UI | `ui-override-form` |
| 25 | US-UI-6 | 1 | UI | `ui-history` |
| 26 | US-UI-7 | 1 | UI | `ui-shell` *(F1)* |
| 27 | US-PLAT-1 | 1 | PLAT | `auth-rbac` *(realized across C5 gate units — F5b, §4)* |
| 28 | US-PLAT-2 | 1 | PLAT | `audit-store` *(F2)* |
| 29 | US-PLAT-3 | 1 | PLAT | `quality-gates` |
| 30 | US-PLAT-4 | 1 | PLAT | `quality-gates` |
| 31 | US-PLAT-5 | 1 | PLAT | `quality-gates` |
| 32 | US-PLAT-6 | 1 | PLAT | `quality-gates` |
| 33 | US-PLAT-7 | 1 | PLAT | `corpus-generator` |
| 34 | US-PLAT-8 | 1 | PLAT | `audit-store` *(F3; `database` is the substrate, story-less)* |
| 35 | US-PLAT-9 | 2 | PLAT | `observability` |
| 36 | US-PLAT-10 | 2 | PLAT | `llm-judge` |
| 37 | US-PLAT-11 | 2 | PLAT | `deploy-config` |
| 38 | US-PLAT-12 | 1 | PLAT | `secrets-config` |
| 39 | US-ADMIN-1 | 1 | ADMIN | `admin-cli` |
| 40 | US-ADMIN-2 | 1 | ADMIN | `admin-cli` |

**Count = 40. Each story appears exactly once.** No orphan, no double-assignment.

---

## 2. Per-epic completion proof (must match `stories.md §8` on disk)

| Epic | Story IDs | Count | Owning unit(s) |
|---|---|:--:|---|
| **INTAKE** | US-INTAKE-1/2/3/4 | **4** | `intake` (3) + `document-sanitizer` (1) |
| **RULES** | US-RULES-1/2/3/4/5 | **5** | `rules-engine` (5) |
| **OUT** | US-OUT-1/2/3 | **3** | `outlier-model` (3) |
| **MEMO** | US-MEMO-1/2/3/4/5/6/7 | **7** | `memo-agent-core` (4) + `memo-extensions` (3) |
| **UI** | US-UI-1/2/3/4/5/6/7 | **7** | `ui-queue`/`ui-memo-view`/`ui-outlier-view`/`ui-approval-gate`/`ui-override-form`/`ui-history`/`ui-shell` (1 each) |
| **PLAT** | US-PLAT-1..12 | **12** | `auth-rbac`(1) + `audit-store`(2) + `quality-gates`(4) + `corpus-generator`(1) + `secrets-config`(1) + `observability`(1) + `llm-judge`(1) + `deploy-config`(1) |
| **ADMIN** | US-ADMIN-1/2 | **2** | `admin-cli` (2) |
| **TOTAL** | | **40** | |

**Aggregate 4 + 5 + 3 + 7 + 7 + 12 + 2 = 40 ✓** — matches per-epic, not just in aggregate.

---

## 3. Reverse map — unit → stories (incl. the story-less unit)

| Unit | Phase | Stories owned | Count |
|---|:--:|---|:--:|
| `intake` | 1 | US-INTAKE-1/2/3 | 3 |
| `document-sanitizer` | 1 | US-INTAKE-4 | 1 |
| `rules-engine` | 1 | US-RULES-1/2/3/4/5 | 5 |
| `memo-agent-core` | 1 | US-MEMO-1/2/3/4 | 4 |
| `ui-queue` | 1 | US-UI-1 | 1 |
| `ui-memo-view` | 1 | US-UI-2 | 1 |
| `ui-approval-gate` | 1 | US-UI-4 | 1 |
| `ui-override-form` | 1 | US-UI-5 | 1 |
| `ui-history` | 1 | US-UI-6 | 1 |
| `ui-shell` | 1 | US-UI-7 | 1 |
| `auth-rbac` | 1 | US-PLAT-1 | 1 |
| `audit-store` | 1 | US-PLAT-2, US-PLAT-8 | 2 |
| `quality-gates` | 1 | US-PLAT-3/4/5/6 | 4 |
| `corpus-generator` | 1 | US-PLAT-7 | 1 |
| **`database`** | 1 | **— (STORY-LESS by design)** | **0** |
| `secrets-config` | 1 | US-PLAT-12 | 1 |
| `admin-cli` | 1 | US-ADMIN-1, US-ADMIN-2 | 2 |
| `outlier-model` | 2 | US-OUT-1/2/3 | 3 |
| `memo-extensions` | 2 | US-MEMO-5/6/7 | 3 |
| `ui-outlier-view` | 2 | US-UI-3 | 1 |
| `observability` | 2 | US-PLAT-9 | 1 |
| `llm-judge` | 2 | US-PLAT-10 | 1 |
| `deploy-config` | 2 | US-PLAT-11 | 1 |
| **Sum** | | | **40** |

> **`database` is story-less by design — this is not a coverage gap.** It is shared PostgreSQL
> infrastructure (schema + migrations, DATA-5) depended on by `audit-store`, `auth-rbac`,
> `rules-engine`, and `admin-cli`. Its persistence behaviour is **exercised through
> US-PLAT-8** (owned by `audit-store`) and US-PLAT-2. The completion criterion constrains
> **stories → units** (every story has exactly one owner), **not units → stories** — a unit may
> legitimately own zero stories. Likewise `provider-abstraction` is a **module** of
> `memo-agent-core` (not a unit) and carries no story of its own, which is normal for a module.

---

## 4. Realization vs assignment (F5b) — cross-unit behaviours that are NOT second assignments

Some stories are **owned by one unit** but **observably realized across others**. This is
realization, not double-assignment — the "exactly once" ownership in §1/§2 still holds.

- **US-PLAT-1 (RBAC separation) → owned by `auth-rbac`.** Its UI-observable behaviour
  ("an auditor attempting any write/approve is denied") is **realized across** `auth-rbac`
  (canonical model + backend enforcement) **and the C5 gate units** `ui-approval-gate` /
  `ui-override-form` (which hide/disable the commit control for auditors as a thin consuming
  facet). The **story is assigned once** (`auth-rbac`); the C5 facet is realization. **(F5b)**
- **US-PLAT-2 (auditor read-only audit trail) → owned by `audit-store`.** Realized via the
  `auth-rbac` read-only DB role (SEC-4) and the `ui-history` browse view — consuming facets,
  not co-owners. **(F2)**
- **US-UI-4 / US-UI-5 (approval gate / override) → owned by `ui-approval-gate` /
  `ui-override-form`.** The **backend CON-BR4 write enforcement** (reject records lacking
  `underwriter_id`+`reason`) is **single-sourced in `audit-store`/DecisionCommitService** — the
  UI units consume that one backend gate rather than each re-implementing the invariant
  (keeps CON-BR4 single-sourced; `unit-of-work.md §5`).
- **US-UI-7 (advisory copy + data-testid) → owned by `ui-shell`.** Every C5 view unit (incl.
  the Phase-2 `ui-outlier-view`) **conforms to** the `ui-shell` contract — realization of a
  shared convention, not a re-assignment. **(F1)**

---

## 5. Phase-split proof (30 Phase 1 / 10 Phase 2)

| Phase | Stories | Count |
|:--:|---|:--:|
| **1** | INTAKE 4 · RULES 5 · MEMO 4 (US-MEMO-1/2/3/4) · UI 6 (US-UI-1/2/4/5/6/7) · PLAT 9 (US-PLAT-1/2/3/4/5/6/7/8/12) · ADMIN 2 | **30** |
| **2** | OUT 3 · MEMO 3 (US-MEMO-5/6/7) · UI 1 (US-UI-3) · PLAT 3 (US-PLAT-9/10/11) | **10** |
| | **Total** | **40** |

Matches `stories.md §8` (30 P1 / 10 P2). **Phase-safe:** every Phase-1 unit owns only Phase-1
stories and every Phase-2 unit owns only Phase-2 stories — no grouped unit mixes phases
(`unit-of-work-dependency.md §3` proves no P1→P2 dependency back-edge), so the BUILD loop runs
all 17 Phase-1 units before any of the 6 Phase-2 units.

---

*End of unit-of-work-story-map.md. 40/40 stories assigned exactly once; per-epic 4/5/3/7/7/12/2;
30 P1 / 10 P2; `database` story-less by design. Stop at the Units Generation completion gate.*
