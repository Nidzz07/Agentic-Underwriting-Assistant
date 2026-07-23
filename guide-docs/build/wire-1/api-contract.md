# WIRE-1 — Frontend↔Backend API Contract

**Kind**: Cross-unit **contract artifact** (NOT a per-unit-loop unit) · authored as a single lightweight contract-design pass · **Date**: 2026-07-08 · **Amended (additive)**: 2026-07-17 (WIRE1-Fold-4)
**Status**: **PINNED** — the hard checkpoint before `ui-queue`'s FD (and the other four UI view units) is satisfied. **The 2026-07-17 amendment is an ADDITION to this same pin (not a new contract version replacing it)**: it adds one optional field (`MemoView.outlier`) + one by-value enum (`FlagDirection`) for outlier data; the four scope items and R1–R7 are otherwise unchanged.
**Scope**: exactly four items — **(1)** endpoint/route list · **(2)** response envelope shape · **(3)** error shape · **(4)** Role delivery to the client — plus the **frozen enum-by-value wire map** (not remapped/re-cased), grounded in the five built response shapes **plus a sixth response shape added by the 2026-07-17 additive amendment (U18 `OutlierResult`, carried on R4 — WIRE1-Fold-4; no new scope item, no new route)**.
**Six answers (all A)**: A1 narrative markdown · A2 plain REST/JSON · A3 bare bodies + list wrapper + error envelope · A4 offset/limit pagination · A5 single error body + fixed status table · A6 `GET /session` role delivery, auth-handshake deferred.

**Not in scope (deferred, named-not-designed)**: the actual route **implementation** (`backend/app/main.py`) — the FastAPI composition root — lands later, covered by **integration tests in Build & Test** (unit-of-work.md §2). CORS origin allowlisting is a **runtime deploy concern → `deploy-config` (P2)** (WIRE1-Fold-3). The **auth handshake** mechanism (bearer/cookie/OIDC) is an **abstract seam, deferred** (A6). This contract pins **shapes**, not wiring.

---

## 1. Frozen enum wire map (serialize BY VALUE — four casings — NOT remapped/re-cased)

WIRE-1 transports these exact values; the client (ui-shell copy module, domain-entities §2.1) keys on them. **No re-casing, no remapping, no bare `DECLINE`.**

| Domain enum | Frozen source | Wire value(s) | Casing |
|---|---|---|---|
| **Recommendation** | `rules_engine.report_schema.Recommendation` | `APPROVE` · `REFER` · `DECLINE-RECOMMEND` | **UPPERCASE**, hyphenated `-RECOMMEND` suffix (FR-RULES-5) |
| **Confidence** | `rules_engine.report_schema.Confidence` | `High` · `Medium` · `Low` | **Title-case** |
| **Role** | `auth_rbac.roles.Role` | `underwriter` · `auditor` · `admin` | **lowercase** |
| **CommitAction** *(human gate action — distinct namespace)* | `audit_store.record_schema.CommitAction` | `approve` · `override` | **lowercase** |
| **FlagDirection** *(outlier flag tail — added by the 2026-07-17 amendment, §7 WIRE1-Fold-4)* | `outlier_model.schemas.FlagDirection` | `high` · `low` | **lowercase** |

> **Namespace-distinctness (binding)**: `CommitAction` `approve`/`override` (lowercase — the **human's** committed action) is a **different value space** from `Recommendation` `APPROVE`/`REFER`/`DECLINE-RECOMMEND` (UPPERCASE — the **system's** advisory output). The human **`override`** (disagree) must never be serialized as, or confused with, the system `DECLINE-RECOMMEND`.

---

## 2. Conventions (A2 · A3)

- **Plain REST over JSON/HTTP**; `Content-Type: application/json` request + response.
- **Success — bare resource body** (the resource object directly).
- **Success — collections** — a **list wrapper**: `{ "items": [ … ], "page": { "page": <int>, "size": <int>, "total": <int> } }` (A4 offset/limit; 1-based `page`).
- **Failure — a single canonical error envelope** (§4). Success responses carry no `error` key; error responses carry no resource body.
- **Advisory-only invariant (binding)**: the API **never finalizes a decision**. GET routes never mutate. A `Recommendation` is advisory output; **only** `POST …/commit` — an **explicit underwriter action** — creates a `CommittedDecision`. There is no auto-commit path.

---

## 3. Endpoint / route list (A1 · scope item 1)

| # | Method · Route | Purpose (UI unit) | Success body | Auth |
|--:|---|---|---|---|
| R1 | `GET /session` | current user identity + Role (scope item 4) | `{ "user_id": str, "role": <Role value> }` | authenticated |
| R2 | `GET /applications?page=&size=` | application queue (`ui-queue`) | list wrapper of **ApplicationSummary** | authenticated (any role) |
| R3 | `GET /applications/{application_id}` | one application's profile | **ApplicantProfile** | authenticated |
| R4 | `GET /applications/{application_id}/memo` | profile + report + memo (`ui-memo-view`) | **MemoView** (§5 — carries `status`) | authenticated |
| R5 | `POST /recommendations/{recommendation_id}/commit` | approve / override (`ui-approval-gate` / `ui-override-form`) | **CommittedDecision** | **`underwriter` only** (`RBAC_COMMIT`) |
| R6 | `GET /decisions?page=&size=` | decision history (`ui-history`) | list wrapper of **DecisionSummary** | authenticated |
| R7 | `GET /decisions/{decision_id}` | one committed decision | **AuditRecord** | authenticated |

> Commit is keyed by **`recommendation_id`** (the pending recommendation), matching `DecisionCommitService.commit(recommendation_id, underwriter_id, action, reason)`. R4's response carries the `recommendation_id` the client then commits (§5).

---

## 4. Error shape + HTTP-status mapping (A5 · scope item 3)

**Error body (every non-2xx):**
```json
{ "error": { "code": "string_slug", "message": "human-readable", "detail": { } } }
```
`detail` is optional (e.g. per-field validation errors). No secret VALUE ever appears in `message`/`detail`.

| HTTP | When | Example `code` |
|--:|---|---|
| **400** | malformed request / input validation (intake Pydantic reject, bad body) | `invalid_request` |
| **401** | unauthenticated (no/invalid session) | `unauthenticated` |
| **403** | authenticated but role-forbidden (e.g. `auditor` calling R5 commit) — auth-rbac `RBAC_COMMIT` | `forbidden` |
| **404** | no such application / recommendation / decision | `not_found` |
| **409** | commit-gate conflict — **override with a blank/missing reason** (BR-COMMIT-GATE), or an already-committed recommendation | `commit_conflict` |
| **422** | well-formed but unprocessable (e.g. action outside `{approve, override}`) | `unprocessable` |
| **500** | internal error | `internal_error` |

> **Advisory-only (restated)**: there is no status/route by which the API itself finalizes a decision — a `CommittedDecision` exists **only** as the result of R5 (explicit underwriter action).

---

## 5. Response shapes (grounded in the five built Pydantic schemas — not invented; **+ a sixth, U18 `OutlierResult`, added by the 2026-07-17 additive amendment — WIRE1-Fold-4**)

Field names/values mirror the frozen schemas; enum fields carry the §1 wire values verbatim.

**ApplicantProfile** — `intake.schema.ApplicantProfile` (verbatim; intake's contract governs).

**ApplicationSummary** (R2 list item — a thin projection for the queue): `{ "application_id": str, "recommendation_id": str | null, "recommendation": <Recommendation value> | null, "confidence": <Confidence value> | null }` (`null` until a recommendation is drafted — see `status` below).

**RuleResultReport** — `rules_engine.report_schema.RuleResultReport`: `{ rule_results[], recommendation, confidence, rulebook_version, content_hash, engine_version, decline_reasons[], refer_reasons[] }`.

**DecisionMemo** (three-region) — `memo_agent_core.schemas.DecisionMemo`: `{ narrative_prose, cited_rule_ids[], missing_information[], recommendation, confidence, memo_hash, model_version }`.

**OutlierResult** (added by the 2026-07-17 amendment — **WIRE1-Fold-4**) — `outlier_model.schemas.OutlierResult` (U18 / C3), carried **by value** on R4's `MemoView.outlier`:
```json
{
  "outlier_score": "float",
  "is_outlier": "bool",
  "flagged_features": [
    { "feature": "str", "z_score": "float", "shap_value": "float", "direction": "<FlagDirection value: high | low>" }
  ],
  "provenance": { "corpus_version": "str", "seed": "int", "outlier_model_version": "str" }
}
```
- Field names/values mirror the frozen U18 schema verbatim (re-declared by none). `flagged_features` **MAY be empty** (a normal applicant). `direction` carries the §1 `FlagDirection` wire value (`high`/`low`) by value. **No verdict/`Recommendation` field** — advisory-only, by construction (U18 `NFR-OUT-ADVISORY-1`). `provenance` carries versions + `seed` (non-PII, non-secret — U18 `NFR-OUT-SEC-1`), not applicant data.

**MemoView** (R4 — the combined view for `ui-memo-view`, with an explicit render state — **WIRE1-Fold-2**; the additive `outlier` field — **WIRE1-Fold-4**):
```json
{
  "application_id": "str",
  "recommendation_id": "str | null",
  "status": "ready | pending",
  "profile":  ApplicantProfile | null,
  "report":   RuleResultReport | null,
  "memo":     DecisionMemo | null,
  "outlier":  OutlierResult | null
}
```
- **`status: "ready"`** → `recommendation_id`, `profile`, `report`, `memo` are all present; `ui-memo-view` renders the memo.
- **`status: "pending"`** → the pipeline has not yet produced a memo for this application; `report`/`memo` are `null` (and `profile` may still be present once intake has parsed it). `ui-memo-view` has a **defined "not yet drafted" state** to render.
- **`outlier` (WIRE1-Fold-4, additive 2026-07-17)** → `OutlierResult | null`, carrying `outlier-model` (U18 / C3) `OutlierResult` **by value**, consumed by `ui-outlier-view` (U20) as another facet of the same case-detail view. It is **`null` when `status: "pending"`** *and* **`null` in Phase 1** (where `services.md` omits the `OUT` call, so a `ready` memo still carries `outlier: null`) — **populated only for a Phase-2 `ready` view**. Purely additive: the `status` discriminator continues to govern `profile`/`report`/`memo` only; existing `ui-memo-view` ignores the field. Advisory-only preserved — `OutlierResult` has **no verdict/`Recommendation` field** (it is advisory input, never a decision).
- The **sync-vs-async processing model** (whether the memo is computed on-view or pre-drafted) is an **implementation detail** deferred to Build & Test; the contract pins only the two client-visible shapes.

**Commit request body** (R5 — explicit approve/override, **WIRE1-Fold-1**):
```json
{ "action": "approve | override", "reason": "string (required, non-blank) iff action == override" }
```
- **`underwriter_id` is NOT in the body** — it is derived from the **authenticated session** (the same identity R1 returns). The backend re-checks `authorize(underwriter_id, RBAC_COMMIT)` independently of the API layer (AUTHZ-1), so a client cannot commit **as another user**.
- **`recommendation_id`** comes from the **path** (R5), matching the commit service's key.
- **`reason` is mandatory (non-blank) iff `action == override`** and ignored/optional on `approve` — mirroring `CommittedDecision.reason` (optional field, conditionally mandatory) and the frozen `BR-COMMIT-GATE` (`an override requires a non-blank reason`). A blank-reason override → **409** (§4).

**CommittedDecision** (R5 success) — `audit_store.record_schema.CommittedDecision`: `{ recommendation_id, underwriter_id, action, reason | null }`.

**DecisionSummary** (R6 list item): `{ "decision_id": str, "application_id": str, "recommendation_id": str, "action": <CommitAction value>, "timestamp": ISO-8601 }`.

**AuditRecord** (R7) — `audit_store.record_schema.AuditRecord`: `{ decision_id, application_id, recommendation_id, audit_tuple, applicant_profile_snapshot, committed_decision, status, supersedes_decision_id | null }`.

---

## 6. Role delivery to the client (A6 · scope item 4)

- **`GET /session` → `{ "user_id": str, "role": <Role value> }`**, where `role` is the **exact lowercase enum value** (`underwriter`/`auditor`/`admin`) — **no re-case**. `ui-shell`'s `shell/session` seam calls this on load and exposes `currentRole ∈ {underwriter, auditor, admin} | null` (null before the call resolves / unauthenticated → 401).
- **The auth *handshake* mechanism** (bearer token / session cookie / OIDC) is an **abstract seam, deferred** — Phase-1 may stub it; the `app_user.subject` OIDC seam already exists. WIRE-1 pins **how the Role reaches the client** (the shape), not the handshake.
- `role` is **chrome/labelling + client-side affordance only**; it is **not** an authorization datum. Backend authorization is re-enforced server-side (auth-rbac) on every protected route (e.g. R5 → 403 for non-`underwriter`).

---

## 7. Ambiguity-check resolutions (RUN 2026-07-08 — CLEAN, three folds)
Grounded on `commit_service.commit`/`_gate`, the built response schemas, and PROJECT-BRIEF's Vercel+Render split — all re-read on disk. No genuine gap → no STOP.
- **WIRE1-Fold-1 (check i)** — the commit body **explicitly** encodes `action ∈ {approve, override}` + `reason` (required-non-blank **iff** override), matching `BR-COMMIT-GATE`; `underwriter_id` is taken from the **authenticated session** (not the body — AUTHZ-1 backend re-check, prevents commit-as-another-user); `recommendation_id` from the path. Not merely implied — pinned in §5.
- **WIRE1-Fold-2 (check ii)** — R4 `MemoView` carries a **`status` discriminator** (`ready` | `pending`), so `ui-memo-view` always has a defined shape whether or not a memo has been drafted; the sync-vs-async model is an implementation detail (Build & Test).
- **WIRE1-Fold-3 (check iii)** — `Content-Type: application/json` is a **contract fact** (in scope, §2); **CORS origin allowlisting** is a **runtime deploy concern → `deploy-config` (P2)** (Vercel↔Render), named-not-designed here — correctly out of scope for the contract shape.

### 7.1 WIRE1-Fold-4 — additive amendment for outlier data (2026-07-17, ambiguity-check CLEAN)
**Trigger**: `ui-outlier-view` (U20) has no wire surface for outlier data — R1–R7 carried none — and `outlier-model` (U18 / C3) is now complete with its `OutlierResult`/`FlaggedFeature`/`OutlierProvenance` schema frozen. This amendment closes that prerequisite gap **additively**, on the existing pin.

**Decision — option (a): extend R4 `MemoView` with an additive, nullable `outlier: OutlierResult | null`** (not a new `R8` route). Grounded in: **(1)** `services.md`'s assembled end-state returns a **combined case-detail payload** (`API→UI: pending recommendation + memo + missing-information list`) with the outlier computed in the *same* pipeline pass as the memo (`API→OUT: score` → `OUT→API: OutlierResult` → `API→MEMO: draft … + outlier_result`), so it shares R4's existing `ready|pending` lifecycle rather than inventing a second one; **(2)** the minimal change to this pinned contract — a new optional field within existing scope item (1)/§5, **not** a new route in the pinned R1–R7 table; **(3)** `OutlierResult` carried **by value** from U18, advisory-only (no verdict field), so R4's advisory-only invariant is preserved (reinforced). The precedent for facets sharing one route exists (ui-approval-gate + ui-override-form share R5). Option (b) `R8 GET /applications/{id}/outlier` was considered and set aside (a second pinned route + second round-trip + duplicated pending/404 machinery for one case-detail screen); option (c) nesting inside `DecisionMemo` was rejected (it would edit a **frozen P1** schema).

**Semantics (binding)**: `outlier` is **`null` when `status: pending`** *and* **`null` in Phase 1** (`services.md` omits the `OUT` call, so a `ready` memo still carries `outlier: null`); **populated only for a Phase-2 `ready` view**. The `status` discriminator continues to govern `profile`/`report`/`memo` only. `FlagDirection` (`high`/`low`) added to the §1 enum wire map as the fifth by-value enum. **No envelope change** (R4 is a bare body), **no new error code** (absent/pending outlier is `null`; a missing application still 404s via existing R4).

**Holds**: no frozen P1 unit edited — `MemoView` is a WIRE-1-owned composite; `OutlierResult` is consumed **by value** from U18. R1–R7 route table, envelope (§2), error shape (§4), and role delivery (§6) are **byte-unchanged** except the additive R4 field + the new §1 `FlagDirection` row. This is an **addition to the existing WIRE-1 pin, not a new contract version**. **Implementation reconciliation deferred**: R4 is a `501` stub in the closed composition root (part of the open R2–R5-unwired item) — `backend/app/` is **not** touched by this amendment; the wire-up lands whenever R4 is actually wired (Build & Test / a future composition-root scope).

## 8. Holds
No frozen artifact edited (the five enums, the six response shapes (by value — incl. U18 `OutlierResult`, WIRE1-Fold-4), `commit_service`, ui-shell's wire map are consumed **by value/by shape**, none modified). Enum wire map preserved verbatim (no remap/re-case). Advisory-only invariant stated. Route **implementation** deferred to Build & Test; CORS + auth-handshake deferred (deploy-config P2 / abstract seam). **tier-B run NOT authorized; no unit started; `backend/app/main.py` NOT written.**
