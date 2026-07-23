# Business Rules — `audit-store` (EPIC-6 / U12)

**Stage**: BUILD → Functional Design (per-unit) · cluster-FD-first unit 3 of 4
**Unit**: U12 `audit-store` (the CON-BR4 write-gate, append-only persistence, replay-as-detection,
auditor read-only surface)
**Date**: 2026-07-03
**Scope**: The `DecisionCommitService` write-gate predicate, append-only enforcement, the
persisted-on-committed-decision rule, the replay match/mismatch rules, and the OOS-7 `active`-only
rule. Every rule states its condition explicitly. Technology-agnostic.

**Invariants held**: CON-BR4 (decision-write gate — single backend source), CON-AUDIT-1 (6-tuple +
replay + append-only), SEC-4 (auditor read-only), SEC-5 (audit logging), CON-BR1 (storage ≠
influence), CON-DET-1 (replay determinism boundary), DATA-4/DATA-5.

---

## 1. `DecisionCommitService` write-gate — the CON-BR4 predicate (Flag 1)

`commit(recommendation_id, underwriter_id, action, reason=None) -> CommittedDecision`. The gate is
the **single backend write-gate** (single-sourced in `audit-store`; the UI facets U7/U8 merely
consume it). It **rejects** a commit unless **all** hold — stated as one precise predicate:

### BR-COMMIT-GATE (reject iff any clause is true)
```
REJECT the commit  iff
    underwriter_id is missing/empty
 OR action is missing
 OR action not in {approve, override}             # action is a CLOSED enum - no other value can commit
 OR (action == override AND trim(reason) == "")   # trim-then-empty - spaces/tabs-only reason rejected, not just null
```

- **`underwriter_id` always mandatory** (WHO) — a missing/empty id is rejected.
- **`action` is a CLOSED enum `{approve, override}`** (WHAT) — always mandatory; **any value outside
  the set (or a missing action) is rejected** — nothing else can commit. `approve` = agree,
  `override` = disagree.
- **`reason` mandatory on `override`** (WHY) — the check is **trim-then-empty**: the reason is
  trimmed of leading/trailing whitespace and rejected if empty, so a **spaces/tabs-only** reason is
  rejected, **not just `null`** (an override cannot commit with a blank rationale).
- **On `approve`**, no separate free-text is required: the **`action=approve` + the endorsed
  `recommendation_id`** is the **rationale-of-record** — a named underwriter took responsibility for
  endorsing a specific recommendation. **No committed decision is ever unaccountable.**

> **Why this does NOT weaken CON-BR4**: every accepted commit carries `underwriter_id` (WHO) + a
> recorded `action` (WHAT) + the endorsed/overridden recommendation; disagreement additionally
> carries a non-blank `reason` (WHY). There is **no path** to a committed decision with no
> accountable rationale — CON-BR4's "reject any write lacking `underwriter_id` + reason" is
> satisfied (free-text reason on override; structured action-of-record on approve).

### BR-AUTHZ-RECHECK (defense-in-depth, SEC-4)
The gate **independently re-checks the committer holds the underwriter role** at the backend
boundary — it does **not** rely on the API-layer RBAC. A **read-only auditor is rejected at the
service** even if the API/UI control were bypassed. Two enforcement points (API layer **and** here);
the service is the last line (`services.md §5`).

---

## 2. Persist-on-committed-decision (CON-AUDIT-1) — atomic

### BR-PERSIST-ATOMIC
- The `AuditRecord` write is **triggered by `commit`** (the human gate) and is **atomic with the
  commit** — commit and audit-tuple persistence are **one atomic operation**. **No committed
  decision exists without its persisted `AuditRecord`** (and vice-versa).
- Persistence happens on **every committed decision** — **not** on every recommendation. A **pending
  recommendation that is never committed produces no `AuditRecord`** (it may leave an observability
  trace, but not a CON-AUDIT-1 audit record).
- The assembled record carries the full 6-tuple + the **`ApplicantProfileSnapshot`** (the original
  validated profile, `domain-entities.md §4`) + the commit linkage + the OOS-7 seam
  (`status=active`).

---

## 3. Append-only enforcement (CON-AUDIT-1 / SEC-5) — structural (Flag 4)

### BR-APPEND-ONLY
- Committed `AuditRecord`s are **append-only by construction**: **no `UPDATE`, no `DELETE`** on a
  committed record. Enforced at **two layers**:
  1. **Service layer** — no mutation API exists (only insert + read).
  2. **DB-role level** — the write role may **`INSERT` only**; the auditor role is **read-only**
     (SEC-4). No role can update/delete a committed record.

### BR-STATUS-WRITE-ONCE (seam ↔ append-only consistency, Flag 4)
- `status` is **written once as `active`** and **never updated in place**.
- A record's **`superseded`-ness is DERIVED**, not stored-mutable: a record is effectively
  superseded **iff** a newer `AuditRecord` references it via `supersedes_decision_id` (read-time
  projection). So **Phase-3 supersession is a pure APPEND** (a new record), and **no `active →
  superseded` in-place flip ever occurs** — the OOS-7 seam and append-only are consistent.
- **Phase 1/2**: `status` is always `active`; `supersedes_decision_id` is always null; the
  supersession write path is **not built** (OOS-7).

---

## 4. Auditor read-only surface (US-PLAT-2, SEC-4 / SEC-5)

### BR-AUDIT-READ
- `AuditService` exposes **read-only** queries — **get decision by `decision_id`**, **browse
  decision history** (by `application_id` or across cases) — backed by a **read-only DB role**
  (SEC-4).
- An auditor can open any past decision — the **full 6-tuple** (`rulebook_version`, `rule_results`,
  `timestamp`, `model_version`, `memo_hash`, `engine_version`) + the replay outcome — but **cannot
  modify any record** (BR-APPEND-ONLY + read-only role). This is the **US-PLAT-2** surface the C5
  `ui-history` / `ui-memo-view` consume.
- **Write blocking is enforced at the backend** (BR-AUTHZ-RECHECK + read-only role), **not** merely
  hidden in the UI.

---

## 5. Replay match/mismatch rules (replay-as-detection — G4 / OOS-8; Flag 3)

`ReplayService.replay(decision_id)` re-derives a fresh `RuleResultReport` and compares it to the
recorded `rule_results`. Orchestration logic → `business-logic-model.md §4`; the **comparison rules**:

### BR-REPLAY-EQUALITY (what decides match vs mismatch)
- **The verdict is decided by equality of the DETERMINISTIC EVALUATION-OUTPUT PROJECTION only** —
  the per-rule rows **+** `recommendation` **+** `confidence`, over the single **CANON-SER**
  convention (`domain-entities.md §2.1`). The provenance fields carried **inside** the stored
  `rule_results` (`rulebook_version` / `content_hash` / `engine_version`) are **excluded from the
  projection** — the stored report embeds them, but they are **not** compared.
- **Excluded from the equality set** (so they can never cause a **false** mismatch):
  `timestamp`, `underwriter_id`, `reason`, `memo_hash` (recorded metadata, re-read not re-derived).
- **`rulebook_version`** is the **load key** (a fixed input to replay), not a compared output.
- **`engine_version` and `content_hash` are FORENSIC/diagnostic — NOT equality triggers** (Flag 3).
  They are recorded and **surfaced to EXPLAIN** a mismatch (engine code drift vs rulebook byte-drift
  vs a genuine regression). **An engine refactor / new git SHA must NOT mass-flag** historical
  decisions as reproducibility failures — that is precisely why `engine_version` is a *distinguisher*,
  not a trigger.

### BR-REPLAY-VERDICT
- **Match** (canonical output equal) → **reproducibility VERIFIED** (decision reproduced).
- **Mismatch** → a **BLOCKING reproducibility failure**, surfaced read-only, **plus a forensic
  delta** (which rule/field diverged, recorded-vs-re-derived, and whether `engine_version` /
  `content_hash` differ). **Detection is in scope now**; the **incident-handling workflow is Phase 3
  (OOS-8)**. Replay is a **detection** mechanism — **not assumed to pass**.
- **Mismatch never mutates the record** (BR-APPEND-ONLY) — it flags, it does not re-write.

### BR-REPLAY-NO-MEMO
- Replay **re-evaluates `rule_results` only** (pure `evaluate()`, deterministic). It **never
  re-drafts the memo** (no LLM in replay) and **never re-commits**. Memo integrity is verified
  **separately** by **`memo_hash`** comparison (recorded vs recomputed hash of the stored memo).

---

## 6. Rule → requirement / invariant traceability

| Rule group | Satisfies |
|---|---|
| §1 BR-COMMIT-GATE | **CON-BR4** (write-gate; underwriter_id + reason), US-PLAT-8 |
| §1 BR-AUTHZ-RECHECK | **SEC-4** (defense-in-depth authz), `services.md §5` |
| §2 BR-PERSIST-ATOMIC | **CON-AUDIT-1** (persist per committed decision), US-PLAT-8 |
| §3 BR-APPEND-ONLY, BR-STATUS-WRITE-ONCE | **CON-AUDIT-1** (append-only), **SEC-5**, OOS-7 seam consistency |
| §4 BR-AUDIT-READ | **US-PLAT-2**, **SEC-4/SEC-5** (read-only auditor) |
| §5 BR-REPLAY-* | **CON-AUDIT-1** (replay), reviewer **G4**, **OOS-8** (detection now, workflow Phase 3) |
| `ApplicantProfileSnapshot` (domain-entities §4) | replay self-containment (Flag 2); **CON-BR1** storage ≠ influence; **DATA-4** |

**Advisory-only note**: the persisted human `action` is the one place **"decision"** is correct
(the human's committed choice). The system's own output stays a **recommendation** throughout.

---

*End of business-rules.md. Commit + replay pipeline logic → `business-logic-model.md`; schema →
`domain-entities.md`.*
