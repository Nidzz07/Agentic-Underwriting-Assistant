# WIRE-1 — Frontend↔Backend API Contract

**Kind**: Cross-unit **contract artifact** (NOT a per-unit-loop unit) · authored as a single lightweight contract-design pass · **Date**: 2026-07-08 · **Amended (additive)**: 2026-07-17 (WIRE1-Fold-4) · **2026-07-25 (WIRE1-Fold-5 — authentication routes)** · **2026-08-02 (WIRE1-Fold-6 — the application-submission routes)** · **2026-08-03 (WIRE1-Fold-7 — document upload)**
**Status**: **PINNED** — the hard checkpoint before `ui-queue`'s FD (and the other four UI view units) is satisfied. **The 2026-07-17 amendment is an ADDITION to this same pin (not a new contract version replacing it)**: it adds one optional field (`MemoView.outlier`) + one by-value enum (`FlagDirection`) for outlier data; the four scope items and R1–R7 are otherwise unchanged.
**The 2026-07-25 amendment (WIRE1-Fold-5) is likewise an ADDITION to this same pin, not a new version**: it adds **two routes** (R8 `POST /login`, R9 `POST /logout`), **one success convention** (204 no-content, §2), **one request body** (§5), and **corrects the now-false "handshake deferred" statements** (§6 + this header). ⚑ **R1–R7 remain byte-unchanged in path, method, purpose, success body and Auth** — verified row-by-row at sign-off. See **§7.2**.
**The 2026-08-02 amendment (WIRE1-Fold-6) is likewise an ADDITION to this same pin, not a new version**: it adds **two routes** (R10 `POST /applications`, R11 `POST /applications/{application_id}/draft`) and **their request/response shapes** (§5). ⚑ **§1, §2, §4, §6 and §8 are UNTOUCHED**: no new WIRE-1 enum crosses the wire; both routes reuse §2's existing **bare resource body** success shape (no `201`, no `multipart/form-data`, no new convention); and all three failure modes are **already in §4's table** — `400 invalid_request` (whose row has named *"intake Pydantic reject"* since the 2026-07-08 pin), `401 unauthenticated`, `403 forbidden`. ⚑ **R1–R9 remain byte-unchanged in path, method, purpose, success body and Auth** — verified row-by-row at sign-off. See **§7.3**.
**The 2026-08-03 amendment (WIRE1-Fold-7) is likewise an ADDITION to this same pin, not a new version**: it lets **R10** *also* accept `multipart/form-data` **alongside its existing JSON body**, adds **one enum row** (§1 `DocType`), **one request convention** (§2), **one error row** (§4 `413`), and the request shape (§5). ⚑ **R10's ROW in §3 is byte-unchanged** — path, method, purpose, success body and Auth are all identical; only the note block beneath it is superseded. ⚑ **R1–R11 remain byte-unchanged**, verified row-by-row at sign-off. See **§7.4**.
**Scope**: exactly four items — **(1)** endpoint/route list · **(2)** response envelope shape · **(3)** error shape · **(4)** Role delivery to the client — plus the **frozen enum-by-value wire map** (not remapped/re-cased), grounded in the five built response shapes **plus a sixth response shape added by the 2026-07-17 additive amendment (U18 `OutlierResult`, carried on R4 — WIRE1-Fold-4; no new scope item, no new route)**.
**Six answers (all A)**: A1 narrative markdown · A2 plain REST/JSON · A3 bare bodies + list wrapper + error envelope · A4 offset/limit pagination · A5 single error body + fixed status table · A6 `GET /session` role delivery, auth-handshake deferred *(⚑ the "deferred" half is **SUPERSEDED by WIRE1-Fold-5** — the handshake is now realized; the role-delivery half stands unchanged)*.

**Not in scope (deferred, named-not-designed)**: the actual route **implementation** (`backend/app/main.py`) — the FastAPI composition root — lands later, covered by **integration tests in Build & Test** (unit-of-work.md §2). CORS origin allowlisting is a **runtime deploy concern → `deploy-config` (P2)** (WIRE1-Fold-3). ~~The **auth handshake** mechanism (bearer/cookie/OIDC) is an **abstract seam, deferred** (A6).~~ **⚑ SUPERSEDED 2026-07-25 (WIRE1-Fold-5) — retained struck-through, not deleted, per supersede-not-rewrite.** The handshake is **no longer deferred**: it is realized as an opaque server-side session delivered in an `HttpOnly`/`Secure`/`SameSite=Lax` cookie, issued by **R8** and revoked by **R9** (§3, §6). This contract pins **shapes**, not wiring.

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
| **DocType** *(uploaded document kind — added by the 2026-08-03 amendment, §7 WIRE1-Fold-7)* | `intake.schema.DocType` | `salary_slip` · `bank_statement` · `medical_questionnaire` | **lowercase** |

> **Namespace-distinctness (binding)**: `CommitAction` `approve`/`override` (lowercase — the **human's** committed action) is a **different value space** from `Recommendation` `APPROVE`/`REFER`/`DECLINE-RECOMMEND` (UPPERCASE — the **system's** advisory output). The human **`override`** (disagree) must never be serialized as, or confused with, the system `DECLINE-RECOMMEND`.

> ⚑ **`DocType` is the FIRST enum in this table the CLIENT asserts rather than the server emits** (added 2026-08-03, WIRE1-Fold-7). Every row above travels server→client; this one travels client→server, as a multipart part name. That asymmetry is why it earns a row at all: an unrecognised value must have a defined outcome, and it does — **400 `invalid_request`**, never a silent drop. ⚑ The values are `intake`'s own, consumed **by value**; this contract re-declares nothing.

---

## 2. Conventions (A2 · A3)

- **Plain REST over JSON/HTTP**; `Content-Type: application/json` request + response.
- **Success — bare resource body** (the resource object directly).
- **Success — collections** — a **list wrapper**: `{ "items": [ … ], "page": { "page": <int>, "size": <int>, "total": <int> } }` (A4 offset/limit; 1-based `page`).
- **Success — no content (added 2026-07-25, WIRE1-Fold-5)** — a **state-changing route that returns no resource** responds **`204 No Content`** with an **empty body and no `Content-Type`**. ⚑ **Purely additive**: it introduces a third success shape alongside the two above and **changes neither of them**; every existing route keeps the shape it already had. The `Content-Type: application/json` rule above governs responses **that carry a body**, which a 204 by definition does not. Used by **R8** and **R9** only.
- **Request — `multipart/form-data` (added 2026-08-03, WIRE1-Fold-7)** — **R10 only**, and **only as an ALTERNATIVE to its JSON body, never as a replacement**. A submission carrying **no documents** stays plain JSON exactly as before; a submission carrying documents sends `multipart/form-data` with one `form_fields` part (a JSON string) and up to three file parts named by `DocType`. ⚑ **Purely additive**: the `Content-Type: application/json` rule above continues to govern **every other request in the contract**, and R10's JSON path is **unchanged in shape, status and error mapping**. ⛔ **No other route accepts multipart.**
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
| **R8** | `POST /login` | authenticate + issue a session (`authn`) | **204 No Content** + `Set-Cookie` (§2, §6) | **unauthenticated** — this route *is* the handshake |
| **R9** | `POST /logout` | revoke the current session (`authn`) | **204 No Content** + cookie cleared | authenticated (any role) |
| **R10** | `POST /applications` | submit a new application — intake → rules → persist at `evaluated` (`ui-submission`) | **SubmissionAccepted** (§5) | **`underwriter` only** (`RBAC_COMMIT`) |
| **R11** | `POST /applications/{application_id}/draft` | trigger drafting for a pending case (`ui-submission`) | **DraftTriggerResult** (§5) | **`underwriter` only** (`RBAC_COMMIT`) |

> ⚑ **R8/R9 added 2026-07-25 (WIRE1-Fold-5). R1–R7 above are BYTE-UNCHANGED** — path, method, purpose, success body and Auth all identical to the 2026-07-08 pin, verified row-by-row at sign-off.
> **R8 request body**: `{ "user_id": str, "password": str }` (§5). **Failure**: a **uniform `401`** for *every* rejection — unknown user, no credential row, wrong password, **and locked-out** — because distinguishing them is a user-enumeration oracle; `400` for a malformed body. **No new error code and no `429`** is introduced (§4 unchanged).
> **R9**: no request body; `401` if no valid session. Revocation is server-side, so a revoked session stops working **immediately** rather than at expiry.
> ⚑ **R8 is the contract's first unauthenticated route.** This is additive: no existing row's Auth value changes, and the word *"authenticated"* in R1–R7 keeps its exact meaning — only the previously **unspecified** mechanism behind it becomes specified.

> ⚑ **R10/R11 added 2026-08-02 (WIRE1-Fold-6). R1–R9 above are BYTE-UNCHANGED** — path, method, purpose, success body and Auth all identical, verified row-by-row at sign-off.
> **Two phases, deliberately.** R10 is **LLM-free**: intake → rules → persist at `evaluated`, returning a case whose R4 `status` is **`pending`**. R11 is the **separate, explicit** trigger that drafts the memo and moves it to `ready`. ⚑ **No GET gains a write path**, so R4 stays side-effect-free and §2's advisory-only invariant is untouched: neither route creates a `CommittedDecision`, which remains R5's sole preserve.
> **R10 request body**: `{ "form_fields": {…}, "documents": [] }` (§5). **`documents` MUST be empty under this fold** — PDF upload is a named follow-on, so no `multipart/form-data` and no `413` are introduced. **Failure**: `400 invalid_request` when intake rejects, carrying `RejectedIntake`'s `reason_category` / `field_errors` / `missing_items` in the error envelope's **existing** `detail` (§4).
>
> ⚑ **SUPERSEDED 2026-08-03 (WIRE1-Fold-7).** The Fold-6 sentence above is retained verbatim, not deleted. *"`documents` MUST be empty under this fold — PDF upload is a named follow-on"* — **that follow-on is this fold.** R10 now accepts up to **three** documents, one per `DocType`, as `multipart/form-data` (§2, §5). ⛔ **R10's ROW ABOVE IS BYTE-UNCHANGED — a media type is not a route.**
> **Failures added by Fold-7**: a file over the per-file cap, or a request over the total cap → **413** `payload_too_large`; an unknown `doc_type`, a fourth document, or two parts of the same `doc_type` → **400** `invalid_request`. ⚑ **A document that fails to PARSE is NOT an error** — it is recorded `unparseable` in the manifest and the application still persists, because a thin file is a **REFER**, never a rejection.
> **R11**: no request body; `404 not_found` for an unknown `application_id`. ⚑ **Re-triggering an already-drafted case is NOT an error** — `200` with `outcome: "skipped"`, mirroring `DraftOutcome.skipped`, so a repeat click is idempotent rather than a failure.
> ⚑ **Both routes are `underwriter`-only, gated on the EXISTING `RBAC_COMMIT` rbac_action.** The vocabulary is closed inside the frozen `auth_rbac` unit, so no new permission is minted here; `RBAC_COMMIT` is precisely the underwriter-only slice of `PERMISSION_MATRIX`. ⚠️ **Recorded rather than smoothed over**: the action's value is `"commit"`, so it now gates three operations, only one of which commits. Splitting it into a distinct action is a **frozen-unit reopening**, deliberately not taken in this fold.

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
| **413** | upload exceeds the per-file or per-request size cap (WIRE1-Fold-7) | `payload_too_large` |
| **422** | well-formed but unprocessable (e.g. action outside `{approve, override}`) | `unprocessable` |
| **500** | internal error | `internal_error` |

> ⛔ **The 413 cap is enforced by a STREAMING BYTE COUNTER, not by `Content-Length`** (WIRE1-Fold-7). A client may understate `Content-Length` or omit it entirely; the header is used only as a cheap early reject and **is not the control**. The counter refuses mid-stream, so **no oversized body is ever fully received and none is ever written to disk**.

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

**Login request body** (R8 — added 2026-07-25, **WIRE1-Fold-5**):
```json
{ "user_id": "string", "password": "string" }
```
- Documented **here** rather than in §3 because §3's table has **no request column** — the same placement the **R5 commit request body** already uses. Purely additive; no existing §5 shape changes.
- **The password is never stored, logged, traced, echoed, or placed in any `AuditRecord`.** It is verified against an **Argon2id** hash and discarded. No §4 error `message`/`detail` may contain it (SEC-3 already forbids secret VALUES there).
- **Success carries no body** — the session arrives as a `Set-Cookie` (§2 no-content, §6). The client then reads its identity from **R1**, whose shape is **unchanged**.
- **R9 has no request body**; the session is identified by the cookie alone.

⚑ **R5's `underwriter_id` note above is UNCHANGED and becomes stronger.** *"Derived from the authenticated session (the same identity R1 returns)"* was aspirational while identity was a stub header; under WIRE1-Fold-5 it is **literally true** — the CON-BR4 "WHO" in every committed decision is now an authenticated subject.

**DecisionSummary** (R6 list item): `{ "decision_id": str, "application_id": str, "recommendation_id": str, "action": <CommitAction value>, "timestamp": ISO-8601 }`.

**AuditRecord** (R7) — `audit_store.record_schema.AuditRecord`: `{ decision_id, application_id, recommendation_id, audit_tuple, applicant_profile_snapshot, committed_decision, status, supersedes_decision_id | null }`.

**Submission request body** (R10 — added 2026-08-02, **WIRE1-Fold-6**):
```json
{
  "form_fields": {
    "date_of_birth": "YYYY-MM-DD",
    "as_of_date": "YYYY-MM-DD",
    "verifiable_income_annual": "decimal string",
    "requested_cover_amount": "decimal string",
    "full_name": "string",
    "gender": "<intake Gender value>",
    "city": "string",
    "height_cm": "decimal string | null",
    "weight_kg": "decimal string | null",
    "existing_debt_obligations_annual": "decimal string | null",
    "employment_type": "<intake EmploymentType value> | null",
    "smoking_status": "<intake SmokingStatus value> | null",
    "occupation": "string | null",
    "health_flags": ["string"],
    "free_text_fields": { "<source_ref>": "string" }
  },
  "documents": []
}
```
- `form_fields` is passed **verbatim** to `intake.pipeline.IntakePipeline.process(form_fields, documents)`. **Its key vocabulary is `intake`'s, not WIRE-1's** — this contract pins the envelope; `intake`'s own `IntakeGate` governs which keys are required, exactly as §5's `ApplicantProfile` entry already defers (*"verbatim; intake's contract governs"*). Documented **here** rather than in §3 because §3 has **no request column** — the same placement the **R5 commit body** and the **R8 login body** already use.
- ⛔ **Money values are decimal STRINGS, never JSON floats.** `intake`'s gate refuses a float outright (**BR-TYP-1** — *"float not permitted; use a decimal string"*), which surfaces as a `400`.
- ⚑ **SUPERSEDED 2026-08-03 (WIRE1-Fold-7). The Fold-6 bullet is retained VERBATIM AND IN FULL:**

  > ⚑ **`documents` MUST be `[]` under this fold.** The key is present so the seam's shape is already correct when upload lands; a non-empty list is a `400`. **Consequence, stated here so it is not discovered later**: with no document supplied, `intake` marks all three expected documents `missing`, so **every Fold-6 submission yields `ApplicantProfile.incomplete = true`** and the rules engine routes it accordingly. That is intake's designed behaviour (*"reject only what is structurally unrecoverable; everything merely incomplete becomes a valid profile that rules-engine routes to REFER"*), **not a defect** — and it is why document upload is a named follow-on rather than an optional extra.

  **Upload has landed — the first sentence is superseded. ⛔ THE CONSEQUENCE CLAUSE IS NOT: it remains TRUE.**
  Three parsed documents clear the *documents* clause of `intake`'s completeness test, but that test has
  **seven** clauses and documents are **one**. An application can carry three parsed documents and still be
  `incomplete = true`. **Fold-7 makes `DOCS-COMPLETE-1` passable; it does not make an application complete.**

  **R10 now accepts TWO request encodings, and the JSON one is UNCHANGED:**

  **(1) `application/json`** — exactly as Fold-6 pinned it, `documents` remaining `[]`. **Byte-unchanged in shape, status and error mapping.** A submission carrying no documents uses this and pays nothing for multipart.

  **(2) `multipart/form-data`** — for a submission carrying documents:

  | Part | Content | Required |
  |---|---|---|
  | `form_fields` | the **same JSON object** as (1)'s `form_fields`, sent as a string | yes |
  | `salary_slip` · `bank_statement` · `medical_questionnaire` | one PDF each; the part name **is** the `DocType` value (§1) | no — any subset, including none |

  - ⛔ **At most ONE part per `DocType`.** A duplicate is **400**, never last-wins: silently discarding a document an applicant believed they had supplied is the worst available outcome.
  - ⚑ **A supplied document that cannot be parsed is recorded `unparseable`** and the application still persists. `DOCS-COMPLETE-1` counts only `parsed` entries, so an unparseable document affects the **recommendation**, not the **acceptance**.
  - ⛔ **RETENTION (BINDING).** An uploaded document exists on disk **only for the duration of the request that carried it**, under an application-owned temp root, and is deleted on **every** exit path — success, rejection, parse failure and unhandled error alike. **A file surviving an abnormal termination (a crash, an OOM kill, a deploy) is removed by a sweep at the next startup.** ⚑ **No uploaded document is persisted and none is written to the database** — only the derived `DocumentEntry` manifest and its content hash.
- `free_text_fields` is the only free prose accepted; it passes the **sanitizer** and **PII guard** before the gate sees it.
- **`application_id` is NOT in the body** — it is **system-assigned by `IntakeGate` on gate pass** (a `RejectedIntake` never receives one), the same shape as R5's server-derived `underwriter_id`. A client cannot choose its own application id.

**SubmissionAccepted** (R10 success — added 2026-08-02, **WIRE1-Fold-6**):
```json
{ "application_id": "str", "status": "pending" }
```
- A **bare resource body** at **`200`** — §2's existing success shape, unchanged. ⚑ **No `201` convention is introduced**, deliberately: it would amend §2, and the smaller amendment is the one that can be verified byte-for-byte at sign-off.
- `status` carries the **same `ready | pending` discriminator R4 already defines**, not a second lifecycle vocabulary. It is **`pending`** on every successful R10 — the case is persisted at `evaluated` and has no memo yet. The client then reads R2/R4 as it already does.

**DraftTriggerResult** (R11 success — added 2026-08-02, **WIRE1-Fold-6**):
```json
{ "application_id": "str", "status": "ready | pending", "outcome": "drafted | skipped" }
```
- A **bare resource body** at **`200`**. `status` is again R4's discriminator; `outcome` distinguishes the two success paths, mirroring `case_lifecycle.DraftOutcome`'s own `skipped` **field** (register #27's fix) rather than parsing prose.
- **`drafted`** → a memo was produced this call; `status` is `ready`. **`skipped`** → the case was already drafted, or already committed, so nothing was attempted; `status` reflects the case as it stands. ⚑ **Re-triggering is therefore idempotent and NOT an error** — the property `DraftOutcome.skipped` exists to express.
- ⛔ **A genuine drafting FAILURE is NOT modelled here — a recorded limitation, not an omission.** When drafting runs and produces no memo, `case_lifecycle` moves the case to `failed`, and **`failed` has no wire representation**: `case_to_memo_view_state` maps it to `"pending"` (**register #14 `MEMOVIEW-FAILED-STATE-UNMODELLED`**, open). This fold maps a genuine drafting failure to the **existing `500 internal_error`** (§4, unchanged) and **declares only the two outcomes it can honestly express**. Adding a third status value would widen R4's discriminator and pre-empt #14's own resolution — **out of scope, and left to #14.**

---

## 6. Role delivery to the client (A6 · scope item 4)

- **`GET /session` → `{ "user_id": str, "role": <Role value> }`**, where `role` is the **exact lowercase enum value** (`underwriter`/`auditor`/`admin`) — **no re-case**. `ui-shell`'s `shell/session` seam calls this on load and exposes `currentRole ∈ {underwriter, auditor, admin} | null` (null before the call resolves / unauthenticated → 401).
- ~~**The auth *handshake* mechanism** (bearer token / session cookie / OIDC) is an **abstract seam, deferred** — Phase-1 may stub it; the `app_user.subject` OIDC seam already exists.~~ WIRE-1 pins **how the Role reaches the client** (the shape), not the handshake.
  > ⚑ **SUPERSEDED 2026-07-25 (WIRE1-Fold-5). The struck text is retained verbatim, not deleted** — supersede-not-rewrite. **The handshake is NO LONGER DEFERRED.** It is realized as an **opaque, server-side session token** (never a JWT, never a signed cookie), stored as its **SHA-256** so a database read yields no usable credential, delivered in an **`HttpOnly` · `Secure` · `SameSite=Lax`** cookie, **issued by R8** and **revoked by R9**.
  > **This is the reserved seam being USED AS DESIGNED, not a change of pin**: the struck bullet named *"session cookie"* as one of the anticipated mechanisms, and **§4's `401` row has read *"unauthenticated (no/invalid **session**)"* since the original 2026-07-08 pin.**
  > ⚑ **R1's shape is BYTE-UNCHANGED** (`{user_id, role}`, lowercase, no re-case). `sessionClient.js`, `RoleContext`, `RoleProvider`, `useCurrentRole`, `RoleGate` and `AppFrame` require **zero** change — only the server's `current_identity()` changes, resolving from the cookie instead of the `X-User-Id` stub.
  > **Sessions are revocable**: expiry is enforced **server-side on every request**, so a role change or logout takes effect **immediately** rather than at token expiry. The `app_user.subject` OIDC seam **remains reserved and unused** — full SSO stays **OOS-3 / Phase 3**.
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

### 7.2 WIRE1-Fold-5 — additive amendment for authentication routes (2026-07-25, sign-off in three rounds)

**Trigger**: register **#25 `PER-4-AUTHN-UNIMPLEMENTED`** — **PER-4** (*"Authentication = basic login with role-based access (JWT/session)"*) was answered **IN** at Requirements Analysis and phase-tagged **Phase 1** via **US-PLAT-1**, but was never built. What shipped instead was a stub: `X-User-Id` resolved against `app_user`, with **no credential verification of any kind**, so **any caller who knows a `user_id` is that user**. Closing that requires a real handshake, which requires routes, which requires this amendment.

**Decision — additive, across four substantive sections plus this record**: **§2** gains a third success convention (**204 no-content**); **§3** gains **R8**/**R9**; **§5** gains the **login request body** (placed there because §3 has no request column — the **R5 precedent**); **§6** and the header's *"deferred"* statements are **superseded** as now-false. **R1–R7 are byte-unchanged**, verified row-by-row.

**⚑ Why the section set grew twice during sign-off — recorded, not smoothed over.** The amendment was first presented as **§3 only**, then **§2+§3**, and finally **§2+§3+§5+§6**. Each expansion was found by an audit the *user explicitly demanded* before granting sign-off, and each was **surfaced and stopped on** rather than absorbed:
1. **§2 surfaced** because the planned `204` fits **neither** of §2's two success shapes and contradicts its `Content-Type` sentence as written.
2. **§5 surfaced** because §5 **documents request bodies** (the R5 commit body) and §3 has **no request column** — the earlier side-by-side had implicitly added one, which would have been a **structural** change to §3.
3. **§6 + the header surfaced** because *"the handshake … is an abstract seam, **deferred**"* becomes **FALSE** the moment the cookie ships — **register #13's exact defect shape** (a pinned text asserting what it no longer means).
**The lesson, recorded**: *an amendment's blast radius is not knowable from the section you intend to edit; it is knowable only by auditing every section against the change.*

**Semantics (binding)**: the **uniform 401** on R8 covers unknown-user, no-credential, wrong-password **and locked-out** alike — distinguishing them is a **user-enumeration oracle**. **No `429`** and **no new error code**: §4 is **unchanged**. Lockout, session TTL and cookie policy are **implementation** concerns, pinned in `login-signup-code-gen-plan.md`, not in this contract — WIRE-1 pins **shapes**.

**Holds**: **§1**'s enum wire map **untouched** (R8 carries plain strings; a 204 has no body, so no enum crosses the wire) · **§4** status table **untouched** · **§8** untouched · the **advisory-only invariant preserved** — R8/R9 create no `CommittedDecision` and touch no underwriting state, **structurally enforced** by `test_no_non_get_route_but_the_commit_reaches_domain_state`, which forbids any route module but the commit handler from referencing the domain seams. **This is an ADDITION to the existing pin, not a new contract version.**

### 7.3 WIRE1-Fold-6 — additive amendment for the application-submission routes (2026-08-02)

**Trigger**: register **#2**'s standing qualifier **Q11-A** — *"the API layer is exercisable **after running a seed script**"*, explicitly **not** *"the demo path is runnable end-to-end"*. Two of Q11-A's three named gaps — **(i) no ingestion route** and **(ii) no clickable UI** — cannot be closed without a route by which an application enters the system. ⚑ **`intake` (U1) has never been wired in any reachable path**: the seed script hands `CasePipeline` a hardcoded profile and skips the unit entirely. This amendment is what makes the project's first component reachable over HTTP.

**Decision — two routes in ONE fold, additively**: **§3** gains **R10** and **R11**; **§5** gains the **submission request body**, **SubmissionAccepted** and **DraftTriggerResult**; **§7** gains this record; the **header** records the amendment. **R1–R9 are byte-unchanged**, verified row-by-row.

**⚑ Why R10 and R11 are ONE amendment, not two.** The two-phase flow is **incoherent with only one of them**: R10 alone creates cases nothing can draft; R11 alone has nothing to draft. **Fold-5 is the precedent** for a single amendment adding two routes (R8 + R9), likewise meaningful only as a pair.

**⚑ Why the section set is SMALLER than first scoped — recorded, because Fold-5's lesson was the opposite.** Fold-5's blast radius grew twice during sign-off; here it **shrank once**, and for a reason worth writing down. **§4 was scoped as an amended section** (error mapping for rejection; a `413` for uploads) and turns out **not to need amending at all**: structured-only removes the upload and with it the `413`, and **§4's `400` row has read *"malformed request / input validation (intake Pydantic reject, bad body)"* since the original 2026-07-08 pin**, with `detail` documented as *"optional (e.g. per-field validation errors)"* — **exactly** `RejectedIntake`'s `field_errors` / `missing_items` / `reason_category`. **The contract has had a home for a rejected intake since before any ingestion route was contemplated.** The lesson generalizes Fold-5's: *an amendment's blast radius is knowable only by auditing every section — and the audit can shrink it as well as grow it.*

**Semantics (binding)**:
1. **Two phases.** R10 is **LLM-free** (intake → rules → persist at `evaluated`); R11 is the separate, explicit, LLM-bearing drafting trigger. §5's `MemoView` note stands: the contract pins the client-visible shapes; the two-phase model is how they are produced.
2. **Advisory-only preserved.** Neither route creates a `CommittedDecision`; **R5 remains the only route by which one comes into existence**. Both new routes are non-GET, and **no GET gains a write path** — R4 stays side-effect-free.
3. **`underwriter` only, on the existing `RBAC_COMMIT` action.** Both routes change state and consume resources; R5's row already establishes that a write gets its own role gate rather than bare authentication, and this keeps the **`auditor`** role read-only, which **SEC-4** treats as a security property. ⚠️ `RBAC_COMMIT`'s value is `"commit"` and it now gates three operations; minting a distinct action would reopen the frozen `auth_rbac` unit and is deliberately not done here.
4. **No new error code and no new status.** 400 / 401 / 403 / 404 / 500 all already exist in §4.
5. ⛔ **A `failed` case still has no wire representation** — register **#14** is untouched, and this fold explicitly declines to widen R4's `ready | pending` discriminator on its behalf.

**Holds**: **§1** enum wire map **untouched** — and this was audited, not assumed. R10's body carries `intake`'s own enum values (`Gender`, `EmploymentType`, `SmokingStatus`) **inside the intake-governed `form_fields` object**, and §1 has **never** listed intake's enums even though **R3 has transported them since the original pin** (`ApplicantProfile` carries `demographics.gender`, `employment_type`, `smoking_status`, `documents.entries[].doc_type`/`status`). §1 lists the enums **WIRE-1 itself composes**; intake's travel under *"intake's contract governs"*. Fold-6 introduces no new class of thing, so it mints no §1 row. · **§2** conventions **untouched** (both routes reuse the bare-body 200) · **§4** status table **untouched** · **§6** role delivery **untouched** · **§8** untouched. No frozen artifact edited — intake's schema is consumed **by shape**, `DraftOutcome`'s `skipped` **by value**. **This is an ADDITION to the existing pin, not a new contract version.**

### 7.4 WIRE1-Fold-7 — additive amendment for document upload (2026-08-03)

**Trigger**: register **#2**'s **Q2(a)**, which chose structured-only submission and named this pass as its
deliberate follow-on, listing six costs it was deferring: bytes-to-disk, temp-storage lifetime as a PII retention
issue, missing size limits, unbounded subprocess concurrency, Render's ephemeral filesystem, and
`multipart/form-data` as a new request convention. ⚑ **All six are paid here.** Register #2 shipped a submission
path on which **every** application was permanently `documents_missing_count = 3`, because no document could be
supplied. This fold is what lets `DOCS-COMPLETE-1` actually pass.

**Decision — additive, across five substantive sections plus this record**: **§1** gains a `DocType` row; **§2**
gains a `multipart/form-data` **request** convention; **§3**'s R10 **note** is superseded (**the row is not**);
**§4** gains a **413** row; **§5** gains R10's second request encoding. **R1–R11 are byte-unchanged**, verified
row-by-row at sign-off.

**⛔ WHY R10 SPEAKS BOTH ENCODINGS — forced, not chosen.** The scoping answer read *"amend R10 to accept
multipart"*, which is ambiguous between **adding** a media type and **replacing** one. Multipart-only was never
viable: **~15 existing backend tests POST JSON to R10**, and the **frontend shipped at `d43b661` sends JSON**.
Beyond the cost of breaking both, it would be wrong on its own terms — an application carrying **no documents**
has no reason to pay multipart's overhead. So R10 branches on `Content-Type`, and **its JSON path is unchanged in
shape, status and error mapping**. ⚑ Found by the ambiguity-check as *Constraint 4*, and recorded in the scoping
plan's Q1 as well as here, because Q1's own wording is where the ambiguity lived.

**⚑ WHY `DocType` EARNS A §1 ROW when Fold-6 argued intake's enums do not.** Fold-6 declined to add rows for
`Gender`/`EmploymentType`/`SmokingStatus` on the grounds that *"intake's contract governs"* and that R3 had been
echoing them back since the original pin. **`DocType` is different in kind: it is the first enum in §1 that the
CLIENT asserts rather than the server emits.** A value the server produces cannot be unrecognised; a value the
client sends can, and must therefore have a defined outcome — **400 `invalid_request`**, never a silent drop.
⚑ Fold-6's own lesson was that an amendment's blast radius is knowable only by auditing every section; that audit
made Fold-6 **smaller** and makes Fold-7 **one row larger**. Same discipline, opposite result.

**Semantics (binding)**:

1. **Two encodings, one route.** JSON when no documents; `multipart/form-data` when documents are attached. No
   other route in the contract accepts multipart.
2. ⛔ **The 413 cap is a STREAMING BYTE COUNTER, not `Content-Length`.** The header may be understated or absent
   and is used only as a cheap early reject; **it is not the control**. The counter refuses mid-stream, so an
   oversized body is never fully received and **never lands on disk**.
3. ⛔ **RETENTION.** An uploaded document exists on disk **only for the duration of its request**, under an
   application-owned temp root, deleted on every exit path; a survivor of abnormal termination is removed by a
   **startup sweep**. **No uploaded document is persisted; none reaches the database.** Only the derived manifest
   entry and its content hash do.
4. ⚑ **UNPARSEABLE IS NOT REJECTED.** A supplied document that fails to parse is recorded `unparseable` and the
   application still persists. It changes the **recommendation** (a thin file is a REFER), never the
   **acceptance**. A 5xx here would be wrong: the applicant did nothing invalid.
5. **At most one part per `DocType`**; a duplicate is **400**, never last-wins.
6. ⛔ **This fold does NOT make an application "complete".** `ApplicantProfile.incomplete` is set by **seven**
   clauses in intake's gate and documents are **one** of them. Three parsed documents satisfy
   `DOCS-COMPLETE-1`; they do not by themselves clear `incomplete`. Stated here because the opposite is the
   natural assumption and it is wrong.
7. ⛔ **No document CONTENT reaches any profile field.** The parse yields a manifest entry and a content hash;
   extracting values from a document — and the override-policy and provenance decisions that would come with it —
   is **explicitly out of scope** and named as a future pass.

**Holds**: **§3**'s R10 **row byte-unchanged** (a media type is not a route) · **§6** role delivery **untouched** ·
**§8** untouched · the **advisory-only invariant preserved** — R10 creates no `CommittedDecision`, and R5 remains
the only route that does · no frozen artifact edited (`intake`'s `DocType` and `DocumentEntry` are consumed **by
value**) · R1–R11 byte-unchanged. **This is an ADDITION to the existing pin, not a new contract version.**

---

## 8. Holds
No frozen artifact edited (the five enums, the six response shapes (by value — incl. U18 `OutlierResult`, WIRE1-Fold-4), `commit_service`, ui-shell's wire map are consumed **by value/by shape**, none modified). Enum wire map preserved verbatim (no remap/re-case). Advisory-only invariant stated. Route **implementation** deferred to Build & Test; CORS + auth-handshake deferred (deploy-config P2 / abstract seam). **tier-B run NOT authorized; no unit started; `backend/app/main.py` NOT written.**
