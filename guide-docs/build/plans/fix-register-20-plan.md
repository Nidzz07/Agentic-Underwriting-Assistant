# Register Item #20 — `PENDING-TABLES-NO-EXPLICIT-GRANTS` · SCOPING PLAN

**Stage**: POST-BUILD → register-item remediation · the third item taken up after **SCOPE B CLOSED**
(after **#19 NARROWED** and **#18 NARROWED**).
**Status**: 🟡 **SCOPING / PLANNING ONLY — NO CODE, NO MIGRATION CHANGE GENERATED.** Stopped at the plan-file gate.
**Date**: 2026-07-22T16:46:43Z
**Origin**: register item **#20**, opened by the **Scope B in-place composition-root wiring pass**
(`guide-docs/build/composition-root/scope-b-wiring-summary.md` §5 #20; `BUILD-COMPLETION-REPORT.md` §5 #20)
and deliberately recorded there as an **open observation, not a decision** — per **Scope B Q8a**, *"inventing a
grant is a security decision the composition root must not make alone."*
**Owner recorded in the register**: **U24 / a security review.** This pass is that review, begun.

**Register severity, quoted, not softened**: *"**Non-blocking** — the chosen engine binding works and is
least-privilege-consistent. Recorded for review."* (Register #20 is the register's **least severe** open item —
the opposite end from #19's *"most serious"*. This plan is scoped accordingly, per the task's own note that #20
*"may not need a full code-gen plan if the answer turns out to be 'this is correct as-is, document it as
deliberate.'"*)

---

## 0. What this document is and is not

* **IS**: a scoping plan. Ground truth, the framing correction, and **four open questions** for the user to answer.
* **IS NOT**: a fix, a design, a migration, or an authorization. **No code is generated. No migration is written.
  No unit is reopened.** Whether *any* change is required at all is **Q2**, and the answer is the user's.

**Every `[Answer]` tag below is BLANK. None is pre-filled.** Recommendations are given where grounded and are
explicitly marked as recommendations, never as decisions.

---

## 1. Ground truth — re-established from disk, not from any summary

Five checkpoints were re-verified against the actual current files. **All five confirm the gap exactly as
located.** One divergence *from the register's framing* was found and is reported in §1.6 rather than absorbed —
it **narrows** the open question rather than widening it.

### 1.1 `backend/case_lifecycle/migrations/0001_case_lifecycle.sql` — ✅ CONFIRMED

| Property | On disk |
|---|---|
| Creates `pending_application` | ✅ L19–29 (PK `application_id`) |
| Creates `pending_recommendation` | ✅ L33–45 (PK `recommendation_id`, FK → `pending_application`) |
| Any `GRANT` statement | ❌ **NONE** |
| Any `CREATE ROLE` statement | ❌ **NONE** |
| An **explicit** header statement of the no-grants posture | ✅ **YES** — L9–11, tagged **MIGSCOPE-1 / CASE-Req-Fold-1** |

The header (L9–11), quoted verbatim:

> `-- ⚑ NO GRANTS HERE (MIGSCOPE-1 / CASE-Req-Fold-1): U24's store is reached via the`
> `-- DATABASE_URL owner engine and grants to NO U15-owned role. That is what keeps the tier-I`
> `-- test self-contained — it needs neither 0001_initial_schema.sql nor 0002_grants.sql applied.`

**The pending tables are owner-only by default. Confirmed exactly.**

### 1.2 `backend/database/migrations/0002_grants.sql` — ✅ CONFIRMED (the frozen precedent)

| Role | Created here | Grants |
|---|---|---|
| `audit_writer` | ✅ `CREATE ROLE … LOGIN PASSWORD '${AUDIT_WRITER_PASSWORD}'` | **INSERT, SELECT on `audit_record`, `applicant_profile_snapshot` — those two tables only** |
| `audit_reader` | ✅ `CREATE ROLE … LOGIN PASSWORD '${AUDIT_READER_PASSWORD}'` | **SELECT on `audit_record`, `applicant_profile_snapshot` — those two tables only** |

⚑ **Nothing is granted on `app_user`, and nothing on the pending tables** (which do not exist in U15's sequence).
These are the **only two `CREATE ROLE` statements in the entire build.** The "owner" is whatever `DATABASE_URL`
authenticates as (the schema owner) — **there is no explicit owner role**; it is the migration/admin identity
described in `database`'s Infrastructure Design §5 (`infrastructure-design.md:149`).

### 1.3 `backend/app/dependencies.py` — ✅ CONFIRMED (the access pattern, exactly)

| Route(s) | Dependency | Engine | Role |
|---|---|---|---|
| R1 (`app_user` read) | `get_user_role_repository` | `app_engine()` | **owner / `DATABASE_URL`** |
| **R2–R5 (pending-state reads)** | `get_case_store` → `PostgresCaseStore(app_engine())` | **`app_engine()`** | **owner / `DATABASE_URL`** |
| R5 (the audit **WRITE**) | `get_commit_service` → `PostgresAuditRepository(writer_engine())` | `writer_engine()` | `audit_writer` |
| R6/R7 (audit reads) | `get_audit_service` → `PostgresAuditRepository(reader_engine())` | `reader_engine()` | `audit_reader` |

⚑ **The case store is bound to `app_engine()` (owner) — `dependencies.py:119–121`**, exactly as register #20's
`dependencies.py:22` docstring claims. **Cross-checked and true.** ⚑ **Decisively: neither `reader_engine()` nor
`writer_engine()` is ever passed to the case store, and `get_case_store` never receives an audit engine.** The
audit roles touch `audit_record` + `applicant_profile_snapshot` and nothing else, in code, today.

### 1.4 A grant-posture test already exists and PASSES — ✅ CONFIRMED

`backend/case_lifecycle/tests/test_migscope.py::test_u24s_migration_grants_to_no_u15_role` (L36–44):

```python
def test_u24s_migration_grants_to_no_u15_role():
    """⚑ The condition that keeps the tier-I test self-contained."""
    raw = (CASE_MIGRATIONS_DIR / "0001_case_lifecycle.sql").read_text(encoding="utf-8")
    sql = sg.sql_without_comments(raw)      # ⚑ a comment saying "NO GRANTS" is not a GRANT
    upper = sql.upper()
    assert "GRANT" not in upper
    assert "CREATE ROLE" not in upper
    assert "audit_writer" not in sql
    assert "audit_reader" not in sql
```

⚑ **This is the load-bearing finding for Q2.** The no-grants posture is **not** merely present in the SQL — it is
**asserted by a passing tier-U test that strips comments first** (so the reassuring header comment is explicitly
*not* mistaken for the guarantee). It is tied to the named requirement **NFR-CASE-MIGSCOPE-1 (P-CASE-11)** and
business rule **BR-CASE-12**, and folded requirement **CASE-Req-Fold-1 / CASE-D4**. **The posture is implemented,
documented, tested, and traceable — it is not an accident, and it is not silently present.**

### 1.5 The roles the pending tables sit inside — ✅ CONFIRMED, plus the decisive precedent

The complete role model created by `0001_initial_schema.sql` + `0002_grants.sql`:

| Principal | What it is | Grants on `audit_record`/`snapshot` | Grants on `app_user` | Grants on pending tables |
|---|---|---|---|---|
| owner (`DATABASE_URL`) | schema owner / migration+admin identity | owns all | owns all | owns all |
| `audit_writer` | the ONE write role (R5) | INSERT+SELECT | **none** | **none** |
| `audit_reader` | the SEC-4 read-only auditor (R6/R7) | SELECT | **none** | **none** |

> ### ⚑ FIND — `app_user` is ITSELF owner-only, and this is the direct in-build precedent
> `app_user` (the auth-rbac identity skeleton, a **table**, `0001_initial_schema.sql:51`) carries **no audit-role
> grant of any kind**. It is owner-only, and it is reached **exactly** the way the pending tables are —
> `get_user_role_repository` → `PostgresUserRoleRepository(app_engine())` (`dependencies.py:96–98`). The
> `dependencies.py` header states the reason plainly: *"``audit_reader``/``audit_writer`` hold grants on
> ``audit_record`` + ``applicant_profile_snapshot`` ONLY — **neither can read ``app_user``**."*
> **The pending tables are not an anomaly. They sit inside the SAME owner-only posture the build already applies to
> its other non-audit table**, established at U15 and never questioned. #20 asks whether that posture is *correct
> for the pending tables specifically* — but it is emphatically not *novel*.

Parallel corroboration: `database`'s own Infrastructure Design already lists *"whether `auth-rbac` wants its OWN
dedicated PostgreSQL DB role scoped to `app_user`"* as an **explicitly deferred future consideration**
(`infrastructure-design.md:196`). Per-unit dedicated least-privilege roles were treated as **post-Phase-1** work
across the whole build — never a Phase-1 gap. #20 is the case-lifecycle counterpart of that same deferral.

### 1.6 ⚠️ DIVERGENCE FROM THE REGISTER'S FRAMING — reported, not absorbed

The register (both `BUILD-COMPLETION-REPORT.md` §5 #20 and `scope-b-wiring-summary.md` §5 #20) frames #20 as:

> *"Whether this is **deliberate least privilege** or an **unreviewed gap** in U24's migration is **NOT decided**…
> recorded as an **open observation** for review, deliberately undecided (Q8a)."*

**On disk, that framing is half right and half stale, and the difference changes what this pass is actually
deciding:**

| The register implies | On disk |
|---|---|
| The no-grants posture might be an **unreviewed gap** | It is **reviewed and deliberate at the migration level** — documented in the header, asserted by a passing test (§1.4), tied to a named NFR/BR |
| The **security question** is wide open | The **implementation** is settled; what is genuinely un-stated is one specific thing (below) |

⚑ **The genuinely-open residual, stated precisely — and it is NARROWER than "undecided":**

The posture's **documented rationale is migration self-containment** — *"keeps the tier-I test self-contained; it
needs neither `0001_initial_schema.sql` nor `0002_grants.sql` applied"* (CASE-Req-Fold-1 / CASE-D4). That is a
**test-isolation / migration-scope** justification. It is a *true* and *sufficient* reason for U24's migration to
grant to no **U15-owned** role — but it is **not** the same statement as an affirmative **access-model security
judgment**: *"the `audit_reader` and `audit_writer` roles have no legitimate need to read or write pre-commit
draft state, so owner-only is the correct security posture."*

**Owner-only fell out of a migration-scope decision. It was never separately argued as a security posture.** That
— and *only* that — is what #20 has left genuinely open. **The question is therefore not "is there a gap in the
SQL?" (there is not) but "was the security reasoning ever stated, or only the migration-scope reasoning?" (only
the latter).** This reframing is the substance of Q1 and Q2.

---

## 2. The design tension, stated precisely

There is **no functional tension** here — nothing is broken, no route fails, no test is red. This is the
register's calmest item. The tension is entirely one of **disclosure discipline**, and it has exactly the shape
this project has repeatedly insisted on naming:

> **A correctness property (owner-only pending access) exists and is enforced, but the *reason it is correct* was
> recorded under a different, narrower justification (migration self-containment) than the one a security reviewer
> would look for (access-model least privilege). The property is right; the rationale on record is incomplete.**

This is the **inverse** of #18 and #19. Those were *"a real functional gap, disclosed, needing a real fix."* #20
is *"a real functional posture that is already correct, whose **security rationale** was never written down as
such."* The likely resolution is therefore **documentation, not code** — but that must be **confirmed from the
access patterns, not assumed**, which is Q1's job.

**Two constraints bound every option and must be stated up front, because they were verified on disk and they
rule out the naive fixes:**

* ⚑ **C-A — `0001_case_lifecycle.sql` is CHECKSUM-LOCKED.** `case_lifecycle/migrations/checksums.json` pins its
  sha256 (`391e974c…`). **Editing even a comment in that file changes its hash and breaks the manifest** (and the
  U24 immutability discipline that MIGNAME-1/the checksum manifest enforce). **So "just add the security rationale
  as a comment in the migration" is NOT available** — the disclosure, wherever it lands, **cannot land in the
  frozen migration file.** This is a real finding, not a stylistic preference.
* ⚑ **C-B — granting `audit_writer`/`audit_reader` on the pending tables would BREAK MIGSCOPE-1's self-containment
  property.** CASE-Req-Fold-1 holds *only because* U24's migration grants to no U15-owned role: that is what lets
  the tier-I test run against U24's sequence alone, without `0002_grants.sql`. Adding an audit-role grant would
  make U24's migration **depend on those roles existing**, re-coupling it to U15's sequence and breaking the
  containment the passing test asserts. **So the specific "fix" of granting the existing audit roles on the
  pending tables is not merely unneeded — it is actively contraindicated** (independent of whether it is
  authorized). A *new, dedicated* role would avoid this, but is a larger decision — see Q3.

---

## 3. THE OPEN QUESTIONS

> **Instructions**: write your choice after each `[Answer]:` tag. Multiple letters are fine where the options
> compose. **Nothing proceeds until every tag is filled.** Once answered, the full Q&A is embedded back into this
> document and the mandatory ambiguity-check runs before anything else happens.

---

### Q1 — Is owner-only access to the pending tables actually correct, given what those tables hold?

**What the tables hold (§1.1, `0001_case_lifecycle.sql`):** `pending_application` and `pending_recommendation`
hold **pre-commit, not-yet-audited state** — the applicant profile, the draft memo, the rule-results and outlier
bytes, and version stamps, for a case that is `submitted`/`profiled`/`evaluated`/`drafted`/`committing`/`failed`
but **not yet `committed`**. These are **drafts**. The **audit trail proper** — the immutable record of a
*committed* decision — lives in `audit_record` + `applicant_profile_snapshot`, which is a **separate write, on a
separate engine, at the commit boundary.**

**The two audit roles, judged against their actual wired contracts (not a default assumption):**

- **`audit_reader`** is the **SEC-4 read-only auditor** role. Its entire purpose (`0002_grants.sql` header;
  `dependencies.py` `get_audit_service`) is to let **R6/R7 browse *committed* decisions**. Pending state is, by
  definition, **the state that has not yet entered the audit trail**. Granting `audit_reader` read access to
  drafts would **broaden the auditor's surface beyond the committed record it is scoped to** — which cuts
  *against* SEC-4's least-privilege intent, not for it. **No wired access pattern gives `audit_reader` any reason
  to read pending state**, and one can be argued to be actively undesirable.
- **`audit_writer`** is used by **exactly one caller** — the frozen `DecisionCommitService`, to **INSERT a
  committed `AuditRecord`** (`commit_service.py`, verified frozen and hook-free during the #19 pass). Its grant is
  **INSERT+SELECT on the two audit tables only.** The commit's *assembly inputs* (the pending profile/memo/stamps)
  are gathered by `PendingCommitContextProvider` **on the owner engine** (`get_commit_context_provider` →
  `get_case_store` → `app_engine()`) and **passed in** to the service. **`audit_writer` never reads or writes
  pending state, and structurally does not need to** — the provider hands it a finished `CommitContext`. **No
  wired access pattern gives `audit_writer` any reason to touch pending state.**

**Options:**

- **(a) — Owner-only is CORRECT.** The pending tables hold pre-commit drafts; the audit roles are scoped to the
  *committed* audit trail; neither audit role has a wired or contractual reason to read or write drafts; and the
  one path that must read pending state at commit time (the context provider) already does so **on the owner
  engine** and passes assembled inputs into the frozen service. Owner-only is **least-privilege-consistent** and
  matches the `app_user` precedent (§1.5) exactly.
- **(b) — Owner-only is INCORRECT / incomplete**, i.e. some role *should* hold a grant on the pending tables that
  it does not. **To choose this, name the specific role and the specific wired (or operationally required) access
  pattern that owner-only blocks today.** ⚑ On the evidence in §1.3, **no such pattern exists** — every pending
  read in the running system already goes through the owner engine by design.

**Recommendation (grounded): (a).** The argument is made **from the access patterns actually wired in R2–R5 and
the frozen `DecisionCommitService`'s own contract**, not from a default: (1) the audit roles are scoped to the
committed trail, and pending state is pre-audit by construction; (2) no wired caller reaches the pending tables
through a non-owner engine; (3) the sole commit-time pending read is on the owner engine and feeds assembled
inputs into the frozen service; (4) it matches the `app_user` owner-only precedent the build already treats as
correct. **Owner-only is not a gap — it is the least-privilege-consistent posture.** ⚑ *This is a recommendation,
not a decision; Q1 is the security judgment the register asked a reviewer to make, and it is the user's to
ratify.*

**[Answer]**: (a) — owner-only is correct. The argument from the actual wired access patterns is sound: audit_reader is scoped to the committed trail (R6/R7), and granting it visibility into pre-commit drafts would broaden its surface beyond what SEC-4's least-privilege intent actually calls for, not serve it. audit_writer has exactly one caller (the frozen DecisionCommitService), which receives fully-assembled CommitContext inputs from the provider — it never touches pending state directly, structurally. No wired caller anywhere in R2-R5 reaches the pending tables through a non-owner engine. This is also consistent with the standing app_user precedent, which the build has already treated as correct in the identical shape. Owner-only is the least-privilege-consistent posture, not a gap.

---

### Q2 — If owner-only is correct, is any code change needed at all — or is this purely a documentation/disclosure gap?

**Conditional on Q1(a).** If owner-only is correct, then **the SQL, the engine binding, and the passing test are
all already right** — there is nothing to *fix* in behaviour. The only thing #20 identified that is genuinely
absent is the **affirmative access-model rationale** (§1.6): the posture is on record as *migration
self-containment*, never as *"the audit roles have no business reading drafts, therefore owner-only."*

**The distinction the task asks to draw explicitly — "add a migration" vs. "write down why no migration is
needed":**

- **"Add a migration"** would mean changing the *behaviour* of the grant model — a new `GRANT` on the pending
  tables. Under Q1(a) this is **not warranted** (nothing needs the grant) and, for the *existing* audit roles, is
  **contraindicated by C-B** (it breaks MIGSCOPE-1 self-containment). This is Q3's territory and, under Q1(a),
  Q3's answer is "no."
- **"Write down why no migration is needed"** means recording the **security rationale** for owner-only in a
  durable location, so the next reviewer meets a *decision* rather than an *absence* — closing #20 as a disclosure
  item. **This changes no behaviour and touches no migration.**

**Where the disclosure would land (options are not mutually exclusive; C-A forbids the migration file):**

- **(a) — Documentation-only, no code touched at all.** Record the Q1 rationale in **(i)** this plan's answered
  form + **(ii)** the register (`BUILD-COMPLETION-REPORT.md` update section, on the #18/#19 precedent) + **(iii)**
  `guide-state.md` + `audit.md`. `dependencies.py`'s existing "OPEN OBSERVATION (register #20)… **NOT decided
  here**" block (L22–26) is left as the historical record and **superseded** by the register update, exactly as
  past entries were superseded rather than rewritten. **No file under `backend/` is modified.** ✅ Satisfies every
  hold trivially.
- **(b) — Documentation + a one-line upgrade of the `dependencies.py` header.** As (a), **plus** editing the
  `dependencies.py` register-#20 note from *"NOT decided here"* to *"decided: deliberate owner-only least
  privilege — see register #20 resolution."* ⚠️ This **is** a source edit (to a composition-root module, **not** a
  frozen-23 unit and **not** a migration, so it violates no stated hold) — but it is a real change to a file with
  its own tests. **If chosen, it must be treated as a (tiny) code change with a verification step**, not a free
  documentation edit. Worth it because the disclosure then lives **where the consequence lives** (the engine
  binding), which is this project's stated disclosure preference.
- **(c) — Documentation + strengthen the *test's* docstring.** As (a), plus adding the security rationale to
  `test_migscope.py::test_u24s_migration_grants_to_no_u15_role`'s docstring (U24's **own** test — editable, not
  frozen; not checksummed). ⚠️ Same caveat as (b): it is a source edit needing a green-run confirmation, though a
  docstring-only change cannot change behaviour.

**Recommendation (grounded): (a), optionally composed with (b).** (a) alone fully discharges the disclosure gap
with **zero code risk** and trivially satisfies every hold — and under this project's discipline, a documented
decision in the register + guide-state + audit trail is a *real* resolution, not a lesser one. (b) is a
worthwhile **small** addition because it plants the ratified decision at `dependencies.py:22`, the exact spot a
future maintainer reads the engine binding — but it crosses from "documentation" into "a source edit with a
verification step," so it should be **chosen deliberately**, and if chosen it makes this a *minimal* code-gen
pass rather than a pure-docs pass. **(c) is optional polish**; the test already enforces the posture, so its
docstring is the least load-bearing of the three. ⚑ **Note the meta-point: even under (b)/(c) there is NO
migration and NO behaviour change — the grant model on disk is already what Q1 concludes it should be.**

**[Answer]**: (a) composed with (b) — documentation-only as the primary resolution (recording the Q1 rationale in this plan, the register, guide-state.md, and audit.md), plus the small dependencies.py header upgrade from "NOT decided here" to a statement citing the ratified decision and register #20's resolution. I'm choosing to include (b) because the disclosure should live where a future maintainer will actually encounter the consequence — the engine binding itself — not only in a separate planning document they might never open. Treat (b) as the minimal, verified source edit it genuinely is: confirm the full suite stays green after the docstring change, with zero behavioral difference, before considering it done.

---

### Q3 — If additional grants ARE found warranted, what is the required mechanism (and why it is its own decision)?

**Conditional on Q1(b)** — reachable **only** if Q1 concludes a role genuinely needs a pending-table grant it
lacks. This question exists so the mechanism is understood **before** anyone is tempted to add a grant "just in
case," and so the cost of doing so is visible.

**If — and only if — a real gap is found**, adding a grant is **not** a matter of editing anything that exists:

- **(a) — A NEW forward-only migration in `case_lifecycle/migrations/`**, e.g. `0002_case_lifecycle_grants.sql`,
  following the **exact discipline the #19 fix and U24's own sequence already hold**:
  * **Forward-only, immutable-once-published** — a change is a *new higher-numbered file*, **never** an edit to
    `0001_case_lifecycle.sql` (which C-A confirms is checksum-locked anyway).
  * **Collision-guarded** — it flows through `apply_case_migrations()`, which runs
    `assert_no_collision_with_database()` **first** (`migrate.py:71–79`). The bare filename
    `0002_case_lifecycle_grants.sql` does **not** collide with U15's `0002_grants.sql` (different bare names), so
    the guard passes — but the guard *is* the mechanism that must be honored, not bypassed.
  * **Checksummed** — a new `checksums.json` entry for the new file (the manifest is U24's own, editable; adding a
    *new* key is not editing the *existing* `0001` key).
  * **Its own authorization** — logged to `audit.md`/`guide-state.md` **before any code**, exactly as U24's two
    prior reopenings were, and distinct from them.
- ⚑ **What such a migration must NOT do (C-B):** grant to the **existing** `audit_writer`/`audit_reader` roles.
  Doing so re-couples U24's migration to U15's role sequence and **breaks MIGSCOPE-1 self-containment** — the
  passing `test_migscope.py` guarantee. If a real operational need for pending-state visibility ever arises (e.g.
  an **admin / operational-visibility** role browsing stuck `committing` cases — cf. #21's reconciliation script),
  it would almost certainly be a **NEW, dedicated role**, not one of the two audit roles — which is an even
  clearer "its own decision, its own authorization, its own migration" case, and one that also touches
  `secrets-config` (a new role-scoped URL) and `deploy-config` (env wiring), i.e. **well beyond #20's scope.**

**Recommendation (grounded):** **Not applicable unless Q1 selects (b).** If it does, **(a) is the only compliant
mechanism**, and any grant must target a **new dedicated role**, never `audit_writer`/`audit_reader` (C-B). ⚑
**This is explicitly flagged as speculative-until-justified**: on the §1.3 evidence there is no such access
pattern today, so absent a concrete named need from Q1(b), **no migration should be written** — adding a grant
"for future operational visibility" with no present consumer is exactly the speculative security change the Scope
B Q8a caution was written to prevent.

**[Answer]**: N/A — not reachable, since Q1 selected (a). No migration is written. Record explicitly that this question was considered and correctly not triggered, so a future reader doesn't wonder whether it was skipped rather than resolved.

---

### Q4 — How is #20's outcome recorded, whichever way it resolves?

**This plan states both possible outcomes and their evidentiary bar before concluding either — it does not assume
the recommended one.**

- **Outcome A — DISCHARGED as a documentation/disclosure item** *(reachable under Q1(a) + Q2(a)/(b)/(c))*.
  #20's defect was that owner-only's **security rationale** was never stated as such. Writing it down **removes
  that defect entirely** — there is no surviving residual, because the posture was already behaviourally correct
  and tested. This is therefore a **genuine full discharge**, unlike #18/#19 (which each left a real residual and
  so were *narrowed*). ⚑ **Evidentiary bar for claiming DISCHARGED:** (1) Q1 ratified as (a) with the access-
  pattern argument on record; (2) the security rationale durably recorded in the register + `guide-state.md` +
  `audit.md` (and, if Q2(b)/(c), at `dependencies.py`/the test); (3) the existing passing `test_migscope`
  guarantee and the `app_user` precedent (§1.5) cited as the standing enforcement — **no new test is required
  because the posture is already asserted.** If all three hold, #20 is closed **DISCHARGED**, and it becomes the
  register's **first clean full discharge** (#2 was only *partly* discharged).
- **Outcome B — REMAINS OPEN as an item requiring an actual migration** *(reachable only under Q1(b))*.
  If a real gap is found — a named role with a legitimate, wired-or-operationally-required pending-state access
  that owner-only blocks — then #20 is **not** a documentation item: it needs a new forward-only migration (Q3(a))
  under its own authorization and its own code-gen plan. ⚑ **Evidentiary bar for claiming a real gap:** a
  **concrete access pattern**, named and grounded in disk (a route, a service contract, or a stated operational
  procedure), that (i) must read or write pending state, (ii) must do so under a **non-owner** role, and (iii)
  cannot be served by the existing owner-engine binding. **On today's disk that bar is not met** (§1.3) — but Q1
  is the user's to decide, so the outcome is stated for completeness.

**Recommendation (grounded): Outcome A**, on the strength of §1.3–§1.5 (no non-owner pending access is wired or
contractually needed; the `app_user` precedent; the posture already tested). ⚑ **But per this project's standing
discipline, the outcome is decided ON THE EVIDENCE at the answer gate, not pre-committed here** — if Q1 surfaces a
concrete access pattern this plan did not find, Outcome B is correct and #20 stays open with a migration owed.
**#20 must not be marked closed on the *assumption* of Outcome A; it is marked closed only once the Q1 argument is
ratified and the rationale is actually written down.**

**[Answer]**: Outcome A — DISCHARGED as a documentation/disclosure item, on the evidentiary bar you laid out: Q1 ratified as (a) with the access-pattern argument now on record; the rationale durably written into the register, guide-state.md, audit.md, and dependencies.py per Q2; and the existing passing test_migscope guarantee plus the app_user precedent cited as the standing enforcement, with no new test required since the posture was already asserted before this pass began. This becomes the register's first clean full discharge, distinct from #2's partial discharge and #18/#19's narrowing — state that distinction explicitly when recording the closure, since it's a meaningfully different outcome shape from anything else in the register so far.

---

## 4. Holds for this pass — verified, all currently upheld

| Hold | Status at plan time |
|---|---|
| No edit to U15's frozen `0001_initial_schema.sql` or `0002_grants.sql` | ✅ Untouched — this pass reads them as the precedent, edits neither |
| No edit to U24's frozen `0001_case_lifecycle.sql` (and it is **checksum-locked**, C-A) | ✅ Untouched — any disclosure lands elsewhere; any grant (if warranted) is a **new** file |
| A new U24 migration, IF warranted, is forward-only + collision-guarded (the #19-fix discipline) | ✅ Not written; mechanism specified in Q3 for the conditional case only |
| No edit to any other frozen-23 unit's internals | ✅ Untouched |
| WIRE-1's contract text **not amended** | ✅ Untouched — #20 does not touch the wire contract at all |
| `not_wired.py` **not renamed** | ✅ Untouched — register #13 stays open |
| U23's frozen test **not edited** | ✅ Untouched — no route added, no filename set changed |
| The `audit_store` Docker-guard gap **untouched** — 5 errors stay exactly 5 | ✅ Untouched — nothing here touches `audit_store` or its tests |
| **tier-B not authorized** | ✅ Not invoked — #20 needs neither corpus nor LLM |
| **No new route** under `backend/app/routes/` | ✅ None proposed — #20 is a grant/disclosure question, not a routing one |
| **No code or migration generated in this pass** | ✅ **Zero code written. Zero files under `backend/` touched.** Only `guide-docs/` (this plan + the start-of-work log) |

**Test state carried forward, NOT re-run by this pass**: backend **1549 passed / 0 failed / 40 skipped / 5
pre-existing `audit_store` Docker-absence errors**, coverage **99.87%**. **Nothing was executed or modified under
`backend/`.**

---

## 5. What happens after the answers

1. Answers recorded verbatim in `audit.md`; **the full Q&A embedded back into this document** (§3 becomes the
   answered record).
2. **The mandatory ambiguity-check runs** against the answer set — surface-and-stop if not clean, per the standing
   discipline. *(Given the scope, the most likely check is confirming Q2's chosen disclosure locations and whether
   Q2(b)/(c)'s source edits are in or out — a much smaller surface than #18/#19.)*
3. **If Q1(a) + Q2 documentation-only** (the likely path): there is **no code-gen plan and no reopening** — the
   resolution is a documentation pass. #20 is closed **DISCHARGED** per Q4 Outcome A, with the rationale written
   into the register + `guide-state.md` + `audit.md` (and, if Q2(b)/(c), a small verified source edit).
4. **If Q2 includes a source edit (b)/(c)**: a **minimal** change plan with an explicit before/after and a
   green-run verification is written and separately approved before the edit is made.
5. **If Q1(b)**: a U24 migration authorization is logged **before any code**, followed by a full forward-only,
   collision-guarded, checksummed code-gen plan (Q3(a)) under its own approval; #20 stays **OPEN** until that
   ships. Register updated to reflect the migration owed.

---

**STOPPED AT THE PLAN-FILE GATE.** No code. No migration. No reopening. No register status change. The next
decision is the user's.

---

## 6. MANDATORY AMBIGUITY-CHECK — run against the Q1–Q4 answer set + §1 ground truth

**Run**: 2026-07-22 · **Result**: **directed checks (i) and (iii) CLEAN; directed check (ii) literal-clean but
surfaced one ADJACENT GAP → SURFACED-AND-STOPPED → resolved by the user (update both files).** No answer was
improvised; the one gap that could not be resolved without a scope decision was stopped on.

### ✅ Directed check (i) — the `dependencies.py` edit vs. the `backend/app/` scanner tests: CLEAN

Both scanners are **AST-based**, so a docstring-only edit is provably inert:

* `test_no_write_route.py` runs `strip_comments_and_docstrings` (AST) **before every content assertion**. The
  entire register-#20 note is the **module docstring** → fully stripped. Its `AUDIT_WRITER_URL`-count assertion
  counts **code** occurrences only (**1**, in `writer_engine()`); a docstring edit cannot change it. Its
  `AUDIT_WRITER_PASSWORD not in stripped` holds (docstring stripped anyway).
* `test_frozen_untouched.py::test_the_app_owns_no_persistence_of_its_own` scans **RAW** source for exactly
  `{"CREATE TABLE", "__tablename__", "declarative_base", "sa.Table("}` — **the new prose avoids all four.**
* `test_engine_binding.py` is purely behavioural (monkeypatched `create_engine`) — docstring-invariant.
* No test asserts the literal `"NOT decided"` string (grep confirmed: only `dependencies.py` and the reconcile
  script contained it, no test file).

### ✅ Directed check (iii) — closure-wording consistency across the three docs: CLEAN

Satisfied by authoring **CORE-RATIONALE-20** as a single identical block in `BUILD-COMPLETION-REPORT.md`,
`guide-state.md`, `audit.md`, and (in condensed form) the two in-code notes.

### ⚠️ Directed check (ii) — #20 closure vs. #21 / the reconciliation script: LITERAL-CLEAN, one ADJACENT GAP surfaced

**The literal question is clean.** #20's closure **ratifies owner-only**, which is exactly the access pattern
`reconcile_committing_cases.py` already relies on (it reads pending state on the owner engine *because* #20). It
asserts **nothing** about #21's cross-store crash-window atomicity — access-control and cross-store atomicity are
**orthogonal** concerns. Closing #20 verifies nothing unverified about #21.

**⛔ But the check surfaced an adjacent gap the plan's §1 and the original scoping both MISSED.** A grep for
in-code `#20` references returned **TWO** source files, not one:

| File | Line | Claim before this pass |
|---|---|---|
| `backend/app/dependencies.py` | 22 | *"OPEN OBSERVATION … NOT decided here"* |
| `backend/scripts/reconcile_committing_cases.py` | 44 | *"register #20, left open and undecided here"* |

**The plan's §1 ground-truth pass identified only the first.** Closing #20 as DISCHARGED while leaving the second
untouched would make the codebase **contradict itself the moment the closure landed** — one file saying "decided",
another "undecided" — exactly the cross-artifact drift directed check (iii) exists to catch, but between two
**source** files.

**SURFACED-AND-STOPPED**, rather than (a) improvising a second edit beyond the scoped single `dependencies.py`
edit, or (b) silently shipping the contradiction. **User decision: update both files** (same character of edit —
docstring-only, test-neutral, non-frozen, outside every scan root). Line 133's `# owner — register #20` pointer
stays as-is (accurate regardless of #20's status).

**⚑ Recorded as a disclosed process finding** (the #19-vacuous-fixture / #18-Q9-collision precedent): the plan's
ground-truth pass was **incomplete on this one point**, and the ambiguity-check is what caught it. It is written
into all three closure documents, not smoothed over.

---

## 7. Resolution — #20 DISCHARGED (documentation-only)

**Both edits made** (pure docstring/comment, zero behaviour, all four forbidden substrings avoided):

* `dependencies.py` header: *"OPEN OBSERVATION … NOT decided here"* → *"RESOLVED (register #20, DISCHARGED) …
  deliberately owner-only least privilege."*
* `reconcile_committing_cases.py:44`: *"left open and undecided here"* → *"RESOLVED as deliberate owner-only least
  privilege."*

**Full backend suite, live: 1549 passed / 0 failed / 40 skipped / 5 errors (same `audit_store` Docker-absence
names) / 99.87% coverage — BYTE-FOR-BYTE IDENTICAL to the pre-#20 baseline.** No migration, no reopening, no new
test.

**Outcome: #20 DISCHARGED — the register's FIRST clean full discharge** (Q4 Outcome A). Distinct from #2 (partly
discharged) and #18/#19 (narrowed, each with a surviving residual as a new item). **#20 leaves no residual and
opens no new item.**

**Register now: 22 tracked — 18 open · 2 discharged (#2 partly, #20 fully) · 2 narrowed (#18, #19).** ⚑ Count
reconciliation: #20 was one of the prior 19 open, so discharging it drops open **19 → 18** (18+2+2 = 22 tracked,
total preserved); a "19 open + #20 discharged" reading double-counts #20 to 23.

**STOPPED for user review of both diffs and the closure documentation before approval.**
