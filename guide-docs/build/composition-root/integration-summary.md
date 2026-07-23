# Composition-Root Integration Pass — Completion Summary (Scope A)

**Nature**: an **OUT-OF-BAND INTEGRATION PASS** — an explicitly-logged **deviation**, **NOT a numbered unit** (`unit-of-work.md:104-108`: the composition root is *"not a 24th unit of work"*). The **23-unit decomposition is unchanged**. **Date**: 2026-07-16 · **Scope**: **A — backed slice only** · Q1–Q5 answered; plan `guide-docs/build/plans/composition-root-integration-plan.md`.

**Result**: **backend 960 passed / 31 skipped** (was 850/31 — **+110, additive**), coverage **99.83%** (was 99.82%), `backend/app` **100% every file**. **Frontend 524 passed / 117 files** (was 486/114 — **+38, additive**), `src/app` **100% every metric**, **ESLint clean**. **No frozen unit touched** (mtime-verified). **5 pre-existing Docker errors unchanged.**

---

## 1. What was built

### Backend — `backend/app/` (the FastAPI composition root)

| Module | Role | Cov |
|---|---|---|
| `main.py` | `create_app()` + module-level `app`; registers R1/R6/R7 + the R2–R5 markers; composition only, no domain logic | 100% |
| `dependencies.py` | the **two-engine binding**, frozen-unit construction, the **`X-User-Id` stub identity**, **`READ_AUDIT` enforcement** | 100% |
| `errors.py` | the WIRE-1 §4 envelope + the frozen status→code table + handlers on **every** non-2xx | 100% |
| `projections.py` | `AuditRecord` → §5 `DecisionSummary` / list wrapper; **in-app pagination** | 100% |
| `routes/session.py` · `routes/decisions.py` · `routes/not_wired.py` | R1 · R6+R7 · R2–R5 markers | 100% |

### Frontend — `frontend/src/app/` (author-only; **not browser-runnable**, Decision 5)

| Module | Role | Cov |
|---|---|---|
| `httpTransport.js` | the **real transport** satisfying the duck-typed contract **every frozen seam already expects** — no seam modified | 100% |
| `seams.js` | all **five** frozen units' seams over the one real transport | 100% |
| `sessionClient.js` | R1 → the `RoleContext` value shape; **fail-closes to `null`** | 100% |
| `App.jsx` | composes frozen `AppFrame` + `HistoryView`; **no router** (Decision 6 N/A) | 100% |

**Shared-config extensions** (no frozen unit touched): `pyproject.toml` `--cov=backend/app` (**gate unchanged**); `vitest.config.js` + `eslint.config.js` add `src/app` (**thresholds unchanged**).

---

## 2. Route binding — as delivered

| Route | Status | Bound to | Engine |
|---|---|---|---|
| **R1** `GET /session` | ✅ **REAL** | `PostgresUserRoleRepository.get_role` → `to_role` | `DATABASE_URL` |
| **R2/R3/R4** | ⛔ **501 `not_implemented`** | *no pending-application store exists* | — |
| **R5** `POST …/commit` | ⛔ **501 `not_implemented`** | *only a **test-fake** `CommitContextProvider` exists* | — |
| **R6** `GET /decisions` | ✅ **REAL** | `AuditService.browse_history()` → §5 projection + in-app pagination | `AUDIT_READER_URL` |
| **R7** `GET /decisions/{id}` | ✅ **REAL** | `AuditService.get()`; `None` → 404 `not_found` | `AUDIT_READER_URL` |

> **WIRE-1 additive amendment 2026-07-17 (WIRE1-Fold-4)**: R4's `MemoView` shape gained an additive `outlier: OutlierResult | null` field (U18 outlier data). **No effect on this Scope-A slice** — R4 remains a `501 not_implemented` stub here; the wire-up (and this field) reconcile whenever R4 is actually backed. **`backend/app/` not touched by that amendment.**

**Two-engine least-privilege binding derived from the frozen `0002_grants.sql`, not chosen**: `audit_reader`/`audit_writer` hold grants on the **audit tables only** — **neither can read `app_user`** — so R1 must use the owner engine and R6/R7 the SELECT-only reader (SEC-4). **No writer engine is ever constructed.**

**`ui-history` (U9) now works end-to-end against a real backend, and nothing else does.** That is the point of Scope A.

---

## 3. 🔴 RECORDED DIVERGENCE — UNRESOLVED, deliberately carried (Q1-B)

**`READ_AUDIT` on R6/R7 vs WIRE-1 §3's "authenticated (any role)".**

| Side | Says | `admin` on R6/R7 |
|---|---|---|
| **WIRE-1 §3** (frozen contract) | R6/R7 are **"authenticated"** — any role | **200** |
| **`auth_rbac.PERMISSION_MATRIX`** (frozen policy) | `READ_AUDIT` = underwriter + auditor; **admin excluded** | **403** |

**Applied (Q1-B)**: enforce `READ_AUDIT` **verbatim** via the frozen `ApiAuthGuard` — **applying an already-frozen policy, not deciding to override it**. auth-rbac is the single-sourced RBAC authority; the server is always the real gate. **WIRE-1 is NOT amended.**

**Genuinely two-sided, not a one-sided oversight**: the frozen **`ui-history` FD (BR-HIST-7)** independently hit the **mirror** of this and **sided with WIRE-1** — declining `RoleGate can="read"` because it "would cosmetically exclude `admin`… a UI/contract divergence from R6/R7's any-authenticated". **So the frozen client assumes any-authenticated while the server enforces `READ_AUDIT`.** For `admin` the UI would render a history surface the server answers **403**. *(Blast radius today is nil — BR-HIST-7 itself notes "admin has no UI journey anyway" — but the divergence is real.)*

**Status: UNRESOLVED.** Carried for a future **deliberate** reconciliation (**Option C**: enforce `READ_AUDIT` **and** amend WIRE-1 §3's wording to "authenticated, `READ_AUDIT`-permitted"). **This pass does not resolve it and must not be read as having done so.** `test_authz_read_audit.py` encodes the consequence explicitly, so if reconciliation later lands on WIRE-1's reading, that test is what must change — visibly, not silently.

## 4. 🟡 RECORDED ADDITIVE EXTENSION (Q2-A)

**`501 not_implemented` ADDITIVELY extends WIRE-1 §4's status table — it is not a modification.** It **replaces and contradicts no frozen status**; all seven (400/401/403/404/409/422/500) keep their exact meanings; the envelope shape is unchanged. It names a state the frozen table has no word for: *"route defined by the contract, deliberately not wired in this deployment"* — distinct from `not_found` so R7's 404 is never confusable with "unwired".

## 5. 🟢 RECORDED HONEST-BEHAVIOR NOTES

- **R6 ordering (Q3-A)**: **no frozen artifact pins R6's order.** R6 emits `browse()`'s **`decision_id`** order — the **honest current behavior, not a designed guarantee**. `ui-history` re-sorts nothing (BR-HIST-5), so `decision_id` order is what an auditor sees; it is **not newest-first**. Asserted explicitly (`test_pagination.py::TestOrderingIsBrowsesDecisionIdOrder`), including that it is *not* chronological — the consequence is documented, not hidden. A timestamp sort would have required touching frozen `audit-store`.
- **CR-Fold-4 — in-app pagination is N+1 by construction**: `browse()` selects all ids then `_load_one`s each, so the server **materializes every record to serve one page**. The accepted cost of Decision 4 (keep `audit-store` frozen). Harmless at Phase-1 volumes; the client-side PERF-1 bound still holds — one bounded page crosses the wire.
- **Q5-A — `GEMINI_API_KEY` is required but unused**: frozen `Settings` is fail-closed with all six fields required, so the Scope-A app cannot boot without it despite wiring no LLM. A dummy value satisfies it. Reading `os.environ` directly would bypass SEC-3's single source; making the field optional would edit a frozen unit. Both rejected.

## 6. 🟡 CR-Fold-7 — the one conflict the answers themselves created

Q2-A directs that **R2–R5** each return the marker; **R5 is a POST** — so honoring Q2-A **necessarily registers one POST route**, colliding with the literal reading of *"no write route is registered"*. The two cannot both hold literally. **There is exactly one reading under which both are satisfiable**, and it is the one the hold's own reason-clause points at (*"since R5 stays unwired"*): the guarantee is about **write CAPABILITY**, not HTTP verbs. Asserted as the **stronger** property in `test_no_write_route.py`:

1. the **only** non-GET route is the R5 marker (read from `app.openapi()["paths"]`);
2. its handler **raises as its first statement** — AST-asserted — touching no service, reading no body;
3. **no writer engine** is ever constructed (`AUDIT_WRITER_URL` never read);
4. **no `DecisionCommitService`**, **no `CommitContextProvider`** (real or fake) exists under `backend/app/`;
5. no repository write method (`.insert(` / `.atomic(` / `.commit(`) is called anywhere.

A verb count would pass while a real commit path sat behind a POST; this cannot. **Surfaced, not absorbed** — the literal reading (drop the R5 marker, leave R5 unregistered) remains available on request.

---

## 7. Test → target map (110 backend + 38 frontend, all additive)

| Target | Tests |
|---|---|
| **INT-WIRE-1** *(load-bearing)* | `test_wire1_shapes.py` — R1/R6/R7 against the **contract's text**: exact field sets, enums by value and **never re-cased** (`APPROVE`/`High`/`approve`), R6 omits the recommendation, R7's full 6-tuple |
| **INT-ERR-1** | `test_error_envelope.py` — §4 envelope on **every** non-2xx incl. unknown paths; frozen table honored; malformed query → **400** (not the framework's 422); **no caller value ever echoed** |
| **INT-AUTH-1** | `test_auth_stub.py` — known user → role; missing/blank/unknown/blank-role → **401**; **a claimed role cannot elevate** (role comes from `app_user`, never the request) |
| **INT-AUTHZ-1** | `test_authz_read_audit.py` — matrix read as the source; underwriter+auditor 200; **admin 403**; 401 precedes 403; denial leaks no data |
| **INT-PAGE-1 / INT-PROJ-1** | `test_pagination.py` — 1-based slicing, `total` = full count, past-the-end → empty (not an error), projection drops no id, ordering asserted honestly |
| **INT-NOTWIRED-1** | `test_not_wired.py` — all four uniform; **never confusable with `not_found`**; never 500s; role-independent |
| **INT-FAITHFUL-1** | `test_no_write_route.py` — the five CR-Fold-7 assertions + comment-stripper self-tests |
| **INT-FROZEN-1** | `test_frozen_untouched.py` — app re-declares no frozen symbol, owns no persistence, **import direction one-way** |
| **INT-ENGINE-1** | `test_engine_binding.py` — engine-per-route, cached, **writer URL never read**, Settings the single source — **no live DB** |
| **INT-FE-1** | `httpTransport` (13) · `sessionClient` (15) · `app` (10) — incl. frozen seams over the real transport, the **production default-fetch path**, and the Q1-B 403 rendering through ui-history's ordinary error state |

---

## 8. Holds upheld

- **All 17 frozen units imported/composed, never edited** — **mtime-verified**: only `backend/app/**`, `frontend/src/app/**`, `pyproject.toml`, `vitest.config.js`, `eslint.config.js` touched. No file under any frozen `backend/<unit>/` or `frontend/src/<unit>/` tree.
- **WIRE-1 §4/§5 honored exactly**, verified via FastAPI **TestClient**. **Advisory-only + INV-FAITHFUL preserved** (§6).
- **No regression**: backend **850→960** (+110), 31 skipped unchanged, 5 pre-existing Docker errors unchanged; frontend **486→524** (+38); all six frozen frontend trees at their baselines.
- **Invented no domain state** — no pending store, no ingestion route, no `CommitContextProvider`, no migration `0003`. `audit-store` + `database` stay frozen.
- **No P2 unit started. tier-B NOT authorized. `audit_store` Docker-guard gap untouched. `execution-plan.md` untouched. The 23-unit decomposition unchanged — this is not a 24th unit.**

## 9. What this does NOT resolve (stated plainly)

The **core underwriting path (queue → memo → commit) remains unwired**; R2–R5 stay unbacked because the pending-application/recommendation lifecycle is **un-designed domain state**, which belongs in its own stage (Scope B/C), not smuggled into a wiring pass. The frontend **cannot run in a browser** — no bundler; `deploy-config` (U23, P2) owns that and was deliberately not pulled forward. **Build & Test still cannot run until all 23 units complete.** The **Q1-B divergence remains open.**
