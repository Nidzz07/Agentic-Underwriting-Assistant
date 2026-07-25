# Login & Signup — IMPLEMENTATION CODE-GENERATION PLAN

**Stage**: POST-BUILD → the implementation pass for **register #25 `PER-4-AUTHN-UNIMPLEMENTED`**.
**Status**: 🟡 **PLAN ONLY — NO CODE WRITTEN. NOTHING EXECUTED.** Stopped at the plan-file gate.
**Date**: 2026-07-25T10:42:13Z
**Design of record (settled, not re-litigated here)**: `login-signup-plan.md` (**Q1–Q13 answered**) ·
`frozen-assertion-relaxation-plan.md` (**Q1–Q3 answered**) · `frozen-assertion-relaxation-code-gen-plan.md`.
**Prerequisite, confirmed green and committed**: **Phase A** — `ceb32f6`, suite **1582 / 0 / 43 / 5 / 99.87%**.

---

## 0. Ground truth re-confirmed from disk before planning

| Checked | Result |
|---|---|
| `login-signup-plan.md` | **13/13 `[Answer]` tags filled**; no blanks |
| `frozen-assertion-relaxation-plan.md` | **3/3 filled**; Q1(c) duplicate-with-cross-check · Q2(a) three renames · Q3(a) structural |
| Relaxation code-gen §1 | **Phase A/B split confirmed**: Phase A green-throughout (done, committed); **Phase B = the 8 expected-value flips, executed INSIDE this pass, immediately before the code that satisfies them** |
| `backend/app/tests/_route_inventory.py` | On disk, declaring **seven** routes, **one** non-GET, **four** route modules — i.e. today's surface, exactly as Phase A intended |
| `backend/deploy_config/tests/_route_inventory.py` | Mirror present and in sync |
| `test_route_inventory_sync.py` | Present; reads both copies **as text**, `ast`-parsed, duplicate-checked |
| `test_no_write_route.py` | `_DECLARED_PATHS` / `_DECLARED_NON_GET` / `_NON_GET_PATHS` / `_DOMAIN_WRITE_MODULES` / `_DOMAIN_SEAMS` present; R-3 split live; **A-4 (`:239`/`:258`/`:275`) AST-identical to pre-Phase-A HEAD** |
| `test_routes.py` | R-1/R-2 reading the inventory; `test_route_modules_are_exactly_the_declared_inventory` renamed as recorded |
| **Two preserved-by-construction constraints** | **(1)** credential/session stores **outside `backend/app/`**; **(2)** login client **not** registered in `seams.js` |

**Three facts newly verified for this plan** (none were established by the prior plans):

* ⛔ **`admin-cli create-user` takes `user_id, subject, role` and NO credential** (`backend/admin_cli/cli.py:43-47`).
  It provisions the `app_user` row only. **A user created by it cannot log in.** This contradicts part of Q3(a)'s
  premise and is surfaced as **Q3** below, not glossed.
* ✅ **No test asserts `requirements.txt`'s contents.** Adding `argon2-cffi` breaks nothing. (`test_llm_client.py`'s
  only "requirements" hits are my own docstring prose.)
* ✅ **`test_coverage_gate.py` checks only that `--cov-fail-under` is present and ≥ 90** — it does **not** enumerate
  the `--cov=` package list. Adding a `--cov=` line for the new package is safe; **omitting** it would silently
  leave the new package outside QA-6, which is a quality decision, not a test failure.

---

## 1. What this pass delivers, and what it explicitly does not

**Delivers**: real authentication — a credential store, an Argon2id verifier, revocable server-side sessions
delivered as a hardened cookie, `POST /login` + `POST /logout`, and `current_identity()` resolving from the
session instead of the forgeable `X-User-Id` header. This is what closes §1.3 of the scoping plan: *"`X-User-Id:
<any known user_id>` **is** authentication."*

**Does NOT deliver**: MFA or breached-password checking (**Q4.2(ii)**, a disclosed narrowing) · self-service
signup (**Q3(a)** — admin-provisioned only) · OIDC/SSO (**OOS-3**, Phase 3) · any change to the RBAC model
(`auth-rbac` U11 stays frozen and untouched) · any change to R1's response **shape** (**Q6(a)**).

⚑ **#25 discharges only on delivered, verified behaviour.** Per the standing evidentiary rule (#18/#8 precedent),
a mechanism that is structurally complete but unverified against a **real running system** is **NARROWED, not
DISCHARGED**. This plan's §9 states exactly what would be required for a full discharge.

---

## 2. The new persistent state — `0003_auth.sql` (Q2a · Q5b · Q9a)

**Owner**: **U15 `database`** (Q9a). **Placement**: `backend/database/migrations/0003_auth.sql`, i.e. the next
file in U15's existing forward-only sequence, **after `0002_grants.sql`**.

**Why this placement is load-bearing, not incidental** — verified at the relaxation design's check (i):

* `migration_runner.py:69` discovers by glob `[0-9][0-9][0-9][0-9]_*.sql`, so `0003_auth.sql` is **picked up by
  the existing runner with no `backend/scripts/run_migrations.py` edit** — which is precisely why Q9(a) chose U15
  ownership over a separate sequence (a separate sequence would need that hardcoded two-sequence list edited, and
  failing to do so fails **silently at deploy** — register #8's exact, freshly-remediated failure mode).
* ⚑ **It lands owner-only BY CONSTRUCTION.** `0003` applies **after** `0002_grants.sql`, so the two audit roles
  already exist and receive **no grant on the new tables** — the migration contains **no `GRANT` and no
  `CREATE ROLE`**. This is exactly **CORE-RATIONALE-20**'s ratified posture for `app_user`, inherited rather than
  re-argued: *"the pending tables hold pre-commit drafts; `audit_reader` is scoped to the committed trail and
  gains nothing legitimate from reading them."* Credentials are a strictly stronger case.
* **No collision** with U24's sequence (`case_lifecycle/migrate.py:60-68` intersects live filename sets;
  `0003_auth.sql` ∩ `0001_case_lifecycle.sql` = ∅).
* **DATA-5 preserved**: `TIMESTAMPTZ` keeps the schema Postgres-specific so it cannot silently apply on SQLite.

### 2.1 Schema

```sql
-- user_credential — one row per user that HAS a password. Absence of a row means
-- "this user cannot log in", which is a legitimate state (e.g. provisioned, not yet activated).
CREATE TABLE user_credential (
    user_id         VARCHAR      NOT NULL,   -- PK + FK -> app_user.user_id
    password_hash   VARCHAR      NOT NULL,   -- argon2id ENCODED string: algorithm + params + salt + digest
    failed_attempts INTEGER      NOT NULL,   -- lockout counter (Q4.2-ii); reset to 0 on success
    locked_until    TIMESTAMPTZ  NULL,       -- NULL = not locked
    updated_at      TIMESTAMPTZ  NOT NULL,
    CONSTRAINT pk_user_credential PRIMARY KEY (user_id),
    CONSTRAINT fk_user_credential_app_user FOREIGN KEY (user_id) REFERENCES app_user (user_id)
);

-- user_session — one row per issued session. Server-side and therefore REVOCABLE (Q5b).
CREATE TABLE user_session (
    session_id VARCHAR      NOT NULL,   -- PK; the SHA-256 of the raw token, never the token itself
    user_id    VARCHAR      NOT NULL,   -- FK -> app_user.user_id
    created_at TIMESTAMPTZ  NOT NULL,
    expires_at TIMESTAMPTZ  NOT NULL,   -- absolute expiry; enforced server-side on every request
    revoked_at TIMESTAMPTZ  NULL,       -- set by logout; NULL = live
    CONSTRAINT pk_user_session PRIMARY KEY (session_id),
    CONSTRAINT fk_user_session_app_user FOREIGN KEY (user_id) REFERENCES app_user (user_id)
);

CREATE INDEX ix_user_session_user_id ON user_session (user_id);
```

⚑ **`session_id` stores the SHA-256 of the raw token, never the raw token.** A database read therefore yields **no
usable session credential** — the same reasoning that makes `password_hash` a hash. SHA-256 (not Argon2) is
correct here because the token is high-entropy CSPRNG output, not a human-chosen secret, so slow hashing buys
nothing and costs latency on every authenticated request.

**Paired artifact**: `backend/database/migrations/checksums.json` gains a **third** entry. ⛔ **The two existing
entries must remain byte-identical** — U15's frozen migrations are never re-hashed.

---

## 3. The stores — authored OUTSIDE `backend/app/` (Q12a, the A-4-preserving constraint)

⚑ **This is the constraint that preserves A-4 without weakening it.** If the stores lived under `backend/app/`,
`.insert(` would appear there and `test_no_write_route.py:239` would fail — the composition root's stated
guarantee (*"every write goes through the frozen `DecisionCommitService`"*) would have to be relaxed. Authoring
them outside means the guarantee **survives this work completely intact**.

**Pattern to follow — U24 `case_lifecycle`** (named in Q12(a)): a package owning `store.py` (the Protocol + an
in-memory fake) and `repository.py` (the real Postgres adapter), constructed and injected at the composition
root, never importing `backend.app`.

**Package**: see **Q2** — the name is not settled by any prior plan.

| Module | Responsibility |
|---|---|
| `hashing.py` | Argon2id encode/verify (§4). Pure; no DB, no I/O. |
| `store.py` | `CredentialStore` + `SessionStore` Protocols + deterministic in-memory fakes for tier-U. |
| `repository.py` | The real Postgres adapters over an **injected** `sqlalchemy.Engine` (SEC-3: no credential VALUE here). Coverage-omitted like every other `pg_repository.py`. |
| `service.py` | `authenticate(user_id, password) -> SessionToken \| None` and `logout(token)`. Owns lockout, uniform failure, and session issuance/revocation. |
| `admin.py` | The credential-setting entrypoint (see **Q3**). |
| `tests/` | tier-U suite over the in-memory fakes. |

**Import direction stays one-way**: the package imports **nothing** from `backend.app`; the composition root
imports it. This mirrors U24 and keeps `test_frozen_untouched.py`'s import-direction guard satisfied — and,
verified at the relaxation design's §11.2, a new `backend/<pkg>/` does **not** perturb that file's
`PRODUCTION_FILES` (scoped to `backend/app` via `APP_ROOT.rglob`) nor its hardcoded `FROZEN_UNITS` set.

---

## 4. Argon2id (Q4.1a) and the non-negotiables (Q4)

**Dependency**: `argon2-cffi` added to `requirements.txt` (verified safe — no test asserts its contents).

**Properties, each to be asserted by a named test, not assumed:**

| Property | How it is achieved and proven |
|---|---|
| **Per-user salt** | `argon2-cffi` generates a random salt per hash and embeds it in the encoded string. Test: hashing the **same** password twice yields **different** encoded strings, and both verify. |
| **Constant-time verification** | Delegated to `argon2-cffi`'s `verify()`, which is designed for it. ⚑ **No hand-rolled comparison anywhere** — asserted structurally by scanning the module for `==` against a hash. |
| **Uniform failure** | Unknown user, no credential row, wrong password, and locked account **all** return the identical `401` envelope with the identical message and **indistinguishable timing behaviour** (a dummy verify runs on the unknown-user path so it is not a timing oracle). Test: the four paths produce byte-identical response bodies. |
| **No credential material anywhere it could leak** | Never in `AuditRecord`, never in Langfuse traces, never in Prometheus labels, never in logs, never in a WIRE-1 §4 error `message`/`detail`. Test: a structural scan asserting the password parameter name never reaches a logging call, plus a behavioural test that the 401 body contains neither the submitted password nor the stored hash. |
| **Lockout (Q4.2-ii)** | `failed_attempts` + `locked_until` on `user_credential`. Thresholds are **not settled by any prior plan** → **Q5**. |

⚑ **Explicitly NOT implemented, and disclosed by name** (Q4.2(ii)): **MFA** and **breached-password-list
checking**. Per Q11(c) this narrowing is recorded at **`requirements.md` §10 only**, naming both omissions
explicitly — that documentation edit is **step 8** of §8 below.

---

## 5. The routes — and the WIRE-1 amendment as its own gated sub-step (Q7a)

**New module**: `backend/app/routes/auth.py` — `POST /login`, `POST /logout`.

⚑ **`auth.py` must reference NONE of `_DOMAIN_SEAMS`** (`CasePipeline`, `PostgresCaseStore`,
`PendingCommitContextProvider`, `PostgresAuditRepository`, `DecisionCommitService`) — enforced by Phase A's
`test_no_non_get_route_but_the_commit_reaches_domain_state`. It touches the session/credential service only.
This is the *"being non-GET is necessary but never sufficient"* rule working as designed.

### ⛔ 5.1 STEP-GATED: the WIRE-1 §3 amendment requires sign-off BEFORE any route is added

**WIRE-1 has been held frozen for the entire build.** WIRE1-Fold-4 (2026-07-17) added a **field**; **no route has
ever been added to the pinned R1–R7 table.** This would be the first.

**The amendment, stated exactly so it can be signed off or refused as written:**

* **Additive only**: R1–R7 keep their paths, methods, bodies, auth requirements and status meanings **byte-unchanged**.
* **Adds two rows** to §3: `R8 POST /login` → `{user_id, password}` → **204 + `Set-Cookie`**, auth: *unauthenticated
  (this is the handshake)*; `R9 POST /logout` → no body → **204 + cookie cleared**, auth: *authenticated, any role*.
* **Adds no new error code** — 401 (`unauthenticated`) covers a failed login, and 429 is **not** introduced;
  lockout returns the **same uniform 401** (Q4's uniform-failure rule outranks status-code precision here, and
  saying "you are locked out" is itself an enumeration oracle).
* **§6 gains one sentence**: the handshake previously deferred as *"an abstract seam… Phase-1 may stub it"* is now
  realized as a session cookie. **R1's shape is unchanged (Q6a)** — this records how the identity arrives, which
  is exactly what §6 reserved.

**⚑ This sub-step produces no code and must be signed off on its own.** If it is refused, the pass stops here and
Q7(b)'s platform-gate alternative returns to the table.

---

## 6. Cookie delivery and the client (Q5b · Fold-3 · Q13a)

* **Cookie**: `HttpOnly`, `Secure`, `SameSite=Lax`, `Path=/`, no `Domain`, `Max-Age` = session TTL.
  `Secure`'s local-dev handling is **Q4** below (the `os.environ` behavioural-switch precedent from Fold-2).
* ✅ **`httpTransport.js` needs NO change** — and this is stronger than "a one-line change". Fold-3 established
  that `fetch` defaults to `credentials: 'same-origin'` and the topology already **is** same-origin
  (`main.jsx:25` `baseUrl: '/api'` + the Vercel rewrite + the Vite dev proxy), so **cookies are sent
  automatically**. A frozen-classified file is therefore **not touched at all**. ⚑ *This plan records the finding
  as "no change needed"; if implementation shows otherwise, that is a stop-gate, not a quiet one-line edit.*
* ✅ **The login client is NOT registered in `seams.js` (Q13a)** — it follows `sessionClient.js`'s non-seam
  precedent (*"a one-shot read, not a unit seam"*), so **`app.test.jsx:261`'s exact seam-key set stays green and
  the frontend never enters the relaxation scope**.
* **`X-User-Id`**: removed from the *server's* trust path (§7). Whether the header is also removed from
  `httpTransport.js` is **out of scope here** — it becomes inert once the server ignores it, and removing it
  touches a frozen-classified file for no behavioural gain.

---

## 7. R1 stays byte-unchanged in shape (Q6a)

`GET /session` continues to return `{user_id, role}` with the lowercase role value — **no re-case, no new field**.
`sessionClient.js`, `RoleContext`, `RoleProvider`, `useCurrentRole`, `RoleGate` and `AppFrame` need **zero** change.

**What changes is one function**: `backend/app/dependencies.py::current_identity()` resolves the caller from the
**session cookie** — look up the SHA-256 of the presented token in `user_session`, reject if absent/expired/revoked,
then read the role from `app_user` exactly as today (`to_role`, fail-closed to 401). ⚑ `dependencies.py:34` already
anticipated this: *"Replacing this with the real OIDC handshake **touches only this module**."*

⚑ **`AuditRecord.underwriter_id` becomes meaningful for the first time** — the CON-BR4 "WHO" ceases to be a
self-asserted string. That is the substance of what #25 fixes, and it is worth stating plainly rather than
leaving implicit.

---

## 8. Execution order — TDD, RED before GREEN

**Phase B is steps 1–2, exactly as the approved design requires** (relaxation code-gen §1: *"inside the login
pass, immediately before the code that satisfies them"*).

| Step | Action | Expected state |
|--:|---|---|
| **0** | Baseline `pytest backend` | **1582 / 0 / 43 / 5 / 99.87%** — else **STOP** |
| **1** | **WIRE-1 §3 amendment sign-off** (§5.1) | No code. **Gated — stop until signed off** |
| **2** | **PHASE B FLIP**: inventory → 9 routes / 3 non-GET / 5 route modules; U15 tests → 3 migrations | 🔴 **exactly 6 RED**: R-1, R-2, R-3a, R-5, R-6, R-7. R-4 green, R-8 skips (Docker), R-3b green. **Any other set ⇒ STOP** |
| **3** | `0003_auth.sql` + `checksums.json` third entry | R-6, R-7 → GREEN (R-8 remains CI-only) |
| **4** | **RED**: `hashing.py` tests (salt-varies, verify-round-trip, no hand-rolled compare) → then `hashing.py` | GREEN |
| **5** | **RED**: store/service tests over in-memory fakes — uniform failure across all four paths, lockout, session issue/expire/revoke → then `store.py`/`service.py` | GREEN |
| **6** | `repository.py` (real Postgres adapters, coverage-omitted) + `pyproject.toml` `--cov=` line | GREEN, coverage ≥ 90 |
| **7** | **RED**: composition-root tests — cookie attributes, `current_identity` from cookie, R1 shape unchanged → then `auth.py` + `dependencies.py` | R-1, R-2, R-3a, R-5 → **GREEN**; full suite green |
| **8** | Docs: WIRE-1 §3 amended text · `requirements.md` §10 SECURITY-12 narrowing (Q11c) · register #25 status | No test impact |
| **9** | Full suite + frontend suite | See §9 |

### Predicted test-count deltas — stated in advance

| Area | Δ | Basis |
|---|--:|---|
| `hashing.py` tests | **+5** | salt-varies · verify-true · verify-false · encoded-format · no-hand-rolled-compare scan |
| store/service tests | **+12** | 4 uniform-failure paths · lockout trip/reset/expiry (3) · session issue/lookup/expire/revoke (4) · token-stored-hashed |
| composition-root tests | **+7** | cookie attrs (3: HttpOnly/Secure/SameSite) · current_identity from cookie (2: valid, expired) · R1 shape unchanged · X-User-Id no longer trusted |
| `admin.py` / credential-setting | **+3** | set-password · overwrite · unknown-user |
| **Total predicted** | **+27 → 1609 passed** | skipped **43** unchanged · errors **exactly 5** unchanged |

⚑ **Coverage**: `repository.py` is coverage-omitted (the `pg_repository.py` precedent); everything else is pure
logic and must reach the same ≥90% bar. Predicted **≥99.8%**, not pinned to a decimal — **this is the one figure
this plan does NOT predict exactly**, and saying so is more honest than inventing a digit.

### Stop-gates

1. Step 0 baseline ≠ 1582/0/43/5/99.87%.
2. Step 1 not signed off → no route is written.
3. Step 2's RED set ≠ **exactly the 6 predicted**.
4. Any test outside the named set changes state.
5. **A-4 (`:239`/`:258`/`:275`) or `app.test.jsx:261` changes state** → **design-invalidating**; stop and re-authorize.
6. `errors` ≠ 5 or `skipped` ≠ 43 at any point.
7. Any credential value appears in a log, trace, error body, or `AuditRecord` in any test output.
8. `backend/scripts/`, `backend/app/llm_client.py`, or tier-B touched.

---

## 9. What would discharge #25 — and what would leave it NARROWED

**DISCHARGED** requires: a real login against a **real Postgres**, producing a session, driving R2–R7 with it, and
a commit whose `AuditRecord.underwriter_id` is the **authenticated** user. **NARROWED** is the honest outcome if
the work is structurally complete and tier-U-proven but never run against a live database — **the #18 and #8
precedent exactly**. This environment has **no Docker and no live Postgres**, so **NARROWED is the expected
outcome of this pass**, and the plan says so in advance rather than discovering it at the gate.

---

## 10. THE OPEN QUESTIONS

> Every `[Answer]` tag is **BLANK**. Nothing proceeds until all are filled, after which the **mandatory
> ambiguity-check** runs.

### Q1 — Is this a 25th UNIT with the full five-stage BUILD loop, or a remediation pass?

* **(a) — A remediation pass**, using this code-gen plan directly. The two approved plans already answered what
  FD/NFR/NFR-Design would produce: schema, hashing primitive, session mechanism, cookie policy, routes, security
  narrowing, and the frozen-assertion treatment (16 answered questions across two gated documents).
* **(b) — A 25th unit `authn` with the full loop** (FD → NFR Req → NFR Design → Infra → Code Gen), on the **Scope
  B / U24 precedent**: new domain state got a full loop precisely so the composition root would not invent it.

**Recommendation (grounded): (a).** U24's loop existed because its domain state was **un-designed** — Scope B's
own words: *"the pending-application lifecycle is un-designed domain state belonging in its own stage, not
smuggled into a wiring pass."* Here the state **is** designed, in two documents the user gated question-by-question.
Re-running the loop would re-litigate settled decisions, which this build has consistently treated as a cost, not
a virtue. ⚑ **But (b) is a legitimate call** if the security-critical nature of a credential store warrants the
full ceremony — in which case **this document becomes the Code-Generation stage of that loop** and the four
preceding stages must run first.

**[Answer]**: (a) — remediation pass, using this code-gen plan directly. The domain state here is designed across two gated documents with 16 answered questions, unlike U24's genuinely un-designed pending-application lifecycle. Re-running the full five-stage loop would re-litigate settled decisions rather than protect against un-designed ones.

---

### Q2 — What is the new package called?

* **(a) — `backend/authn/`** — the exact contrast with the frozen `backend/auth_rbac/` (authz). Reads as
  *authentication*, which is precisely what #25 says is missing.
* **(b) — `backend/auth_session/`** — names the session lifecycle; understates the credential half.
* **(c) — `backend/credentials/`** — names the credential half; understates sessions.
* **(d) — Extend `backend/auth_rbac/`** — ⛔ **not available**: U11 is frozen, and this would be a frozen-unit edit
  requiring its own authorization. Listed only to record that it was considered and why it is excluded.

**Recommendation (grounded): (a) `backend/authn/`.** The authn/authz split is the exact distinction #25 is about
— BR-AUTH-10 deferred *"authn"* while U11 delivered *"authz"*, and naming the package `authn` makes the previously
implicit boundary explicit in the tree itself. It also reads correctly beside `auth_rbac` without touching it.

**[Answer]**: (a) — backend/authn/. Makes the authn/authz boundary BR-AUTH-10 left implicit explicit in the tree, reads correctly alongside auth_rbac without touching it.

---

### Q3 — ⛔ How does an admin actually SET a password? (a gap in Q3(a)'s premise)

**The finding**: Q3(a) answered signup as *"admin-provisioning only… **already built via admin-cli
create-user**"*. Verified on disk, **`create-user` takes `user_id, subject, role` and no credential**
(`admin_cli/cli.py:43-47`). It creates the `app_user` row and nothing else. **A user it creates cannot log in.**
So Q3(a) is right that **user provisioning** exists, and wrong that **credential provisioning** does — that half
has no implementation anywhere.

* **(a) — A new entrypoint in the new package**, e.g. `python -m backend.authn.admin set-password <user_id>`,
  reading the password from a prompt/stdin (never `argv`, which leaks into shell history and process lists).
  ✅ **No frozen unit edited.** ✅ Credential handling stays in the package that owns hashing.
* **(b) — Reopen `admin-cli` (U17, FROZEN)** to add `set-password`. ⛔ A frozen-unit edit needing its own
  authorization, and it would put Argon2 hashing inside a unit whose FD says nothing about credentials.
* **(c) — `backend/scripts/`** ⛔ **explicitly off-limits** for this pass.

**Recommendation (grounded): (a).** It is the only option that adds the missing capability **without editing a
frozen unit**, and it keeps every line that touches a plaintext password inside the one package designed to handle
it. ⚑ Note the consequence honestly: the project then has **two** admin entrypoints (`admin-cli` for
role/rulebook, `authn.admin` for credentials). That is a real cost, disclosed rather than hidden; unifying them
later is a U17 reopening decision, not this pass's.

**[Answer]**: (a) — a new entrypoint inside the new backend/authn/ package (e.g. python -m backend.authn.admin set-password <user_id>, reading from stdin/prompt, never argv). No frozen-unit edit. Accept the disclosed cost of two admin entrypoints (admin-cli for role/rulebook, authn.admin for credentials) — unifying them later is its own future U17-reopening decision, not this pass's.

---

### Q4 — How is the cookie's `Secure` attribute handled in local development?

`Secure` cookies are not sent over `http://127.0.0.1`, so a hard-coded `Secure=True` breaks the local dev loop
that Phase A's sibling pass just made clickable.

* **(a) — `os.environ` behavioural switch, defaulting to SECURE.** `SESSION_COOKIE_SECURE` read directly via
  `os.environ`; **absent or anything other than `"false"` ⇒ `Secure=True`**. Local dev opts **out** explicitly.
  Uses the **Fold-2 precedent** verbatim: `llm_client.py:106-120` establishes that SEC-3's `os.environ` rejection
  *"is scoped to credentials and secret material specifically"* and that a **behavioural on/off switch is not a
  credential**. ✅ **C-B avoided** — frozen `Settings` stays at six fields.
* **(b) — A seventh `Settings` field.** ⛔ Edits **frozen U16**, and would additionally require the paired
  `.env.example` edit that `test_governance.py:92-94` enforces.
* **(c) — Always `Secure=True`**, and require local dev over HTTPS. ⛔ Breaks the just-delivered dev loop for no
  security gain in a synthetic-data demo.

**Recommendation (grounded): (a), with the fail-safe default.** The default must be **secure**, so that a
missing/misspelt env var yields the **safe** behaviour — a forgotten variable must never silently downgrade a
production cookie. Opting out is then a deliberate, greppable local act.

**[Answer]**: (a) — os.environ behavioural switch (SESSION_COOKIE_SECURE), defaulting to Secure=True, opt-out only via explicit "false". Fail-safe default: a missing or misspelled variable must never silently downgrade a production cookie. Uses the Fold-2 precedent — a behavioural switch is not a credential, so this doesn't touch frozen Settings.

---

### Q5 — Session lifetime and lockout thresholds

Q4.2(ii) mandated lockout but fixed **no numbers**; Q5(b) mandated server-side expiry but fixed **no TTL**. These
are policy, so they are asked rather than invented.

* **(a) — Session absolute TTL 8h · no idle timeout · lockout after 5 consecutive failures for 15 minutes.**
* **(b) — TTL 30m + sliding renewal · lockout 10 failures / 5 minutes.**
* **(c) — TTL 24h · lockout 3 failures / 60 minutes.**

**Recommendation (grounded): (a).** An 8-hour absolute TTL covers one underwriter working day without a
mid-review logout — and because sessions are **server-side and revocable** (Q5b), a long TTL is not the risk it
would be with a stateless JWT: `admin-cli set-role`, deactivation, or logout all take effect **immediately**.
**No idle timeout** keeps the first implementation simple and avoids a renewal path that would need its own
tests. **5 failures / 15 minutes** is the conventional balance — high enough not to lock out ordinary typos, low
enough to make online guessing useless against an Argon2id-hashed credential. ⚑ Whatever is chosen must be
**named constants in one module**, not literals scattered across the service.

**[Answer]**: (a) — 8h absolute session TTL, no idle timeout, lockout after 5 consecutive failures for 15 minutes. Long TTL is acceptable because sessions are server-side revocable, not stateless. Name these as constants in one module, not scattered literals, so they're a single reviewable location if the thresholds ever need revisiting.

---

## 11. Holds for this pass — verified, all currently upheld

| Hold | Status |
|---|---|
| **No code written; nothing executed** | ✅ This is a plan |
| `backend/app/routes/` untouched | ✅ Not read-modified; `auth.py` is **specified, not created** |
| `backend/app/llm_client.py`, `backend/scripts/`, tier-B untouched | ✅ |
| **A-4 and `app.test.jsx:261` preserved by construction** | ✅ The two constraints are restated as **hard gates** (stop-gate 5) |
| **WIRE-1 text unamended** | ✅ The amendment is **specified and GATED** (§5.1), not performed |
| U15's `0001`/`0002` and `checksums.json` untouched; **no migration written** | ✅ `0003_auth.sql` is specified only |
| U16's six-field `Settings` untouched | ✅ Q4(a) avoids C-B by design |
| `auth_rbac` (U11) and `admin_cli` (U17) untouched | ✅ Q2(d) and Q3(b) both **excluded**, with reasons recorded |
| `not_wired.py` not renamed (**#13 open**) | ✅ |
| `audit_store` Docker-guard gap untouched (5 errors stay 5) | ✅ |
| **#25 stays OPEN · no commit** | ✅ |

**Suite carried, not re-run**: backend **1582 / 0 / 43 / 5 / 99.87%** (committed at `ceb32f6`) · frontend
**687 / 137 / 0**.

---

**STOPPED AT THE PLAN-FILE GATE.** No code. No migration. No route. No WIRE-1 amendment performed. **#25 still
OPEN.** Five questions await answers, after which the mandatory ambiguity-check runs.

---

## 12. MANDATORY AMBIGUITY-CHECK — Q1–Q5 + everything settled in the two prior approved plans

**Run**: 2026-07-25 · **Result**: ✅ **CLEAN — 4 directed checks, 4 folds, no surface-and-stop.** Every finding
below was established by reading the asserting code, not inferred.

### ✅ Check (i) — does `backend/authn/admin.py` collide with `backend/scripts/` being off-limits? **CLEAN**

* **Nothing under `backend/` asserts what lives in `backend/scripts/`.** The only references anywhere are two
  prose docstrings (`dependencies.py:120`, `not_wired.py:251`). No test enumerates it, constrains it, or requires
  CLIs to live there.
* **`admin_cli` does NOT claim CLI exclusivity.** `admin_cli/tests/test_reference_not_own.py:123` asserts
  `{"role_gate.py", "app_user_writer.py", "pg_writer.py", "cli.py", "__main__.py"} <= names` — a **subset** check
  over **admin_cli's own** module names. It says nothing about other packages having entrypoints.
* `backend/authn/admin.py` is a new file in a new package and **touches `backend/scripts/` not at all**.

> **AUTHN-Fold-1 — follow `admin_cli`'s own structure.** `admin.py` stays **injection-pure** (takes an injected
> `Engine`, no `create_engine`, no `get_settings`), with a thin `__main__.py` doing the composition — exactly the
> `admin_cli/cli.py` + `admin_cli/__main__.py` split, and `__main__.py` coverage-omitted the same way. This keeps
> the credential path testable at tier-U with no DB and no secrets.

### ✅ Check (ii) — do 8h / no-idle / 5-failures-15-min collide with anything existing? **CLEAN — more strongly than expected**

A repo-wide scan of `backend/`, WIRE-1 and `requirements/` for
`lockout|rate.?limit|throttle|429|idle.?timeout|session.?(ttl|timeout|expiry)` returned **ZERO hits**.

⚑ **There is no existing rate-limiting, lockout, or session-lifetime mechanism or assumption anywhere in the
build.** No NFR pins a session lifetime; WIRE-1 §4's status table has no 429 and gains none (§5.1 already
decided lockout returns the **uniform 401**). The Q5(a) constants are genuinely new and unconstrained.

**One adjacent item, named so it is not later misread**: **`NFR-AUTH-PERF-1`** is a **soft, observed-not-gated**
latency budget on **`authorize`** (in-memory matrix check + ≤1 role lookup). ⚑ **Argon2id is deliberately slow —
that is the point of an adaptive hash — but it sits on the LOGIN path, not on `authorize`.** `authorize` is
unchanged by this pass. So there is no conflict, and **login latency must not be reported as a regression of
NFR-AUTH-PERF-1**, which does not govern it.

### ✅ Check (iii) — is `SESSION_COOKIE_SECURE` consistent with how `ALLOW_REAL_LLM_CALLS` is tested? **CLEAN, with one REQUIRED constraint**

The two switches are **structurally the same pattern**, not an inconsistency:

| Switch | Literal required to LEAVE the safe default | Default (absent/misspelt) |
|---|---|---|
| `ALLOW_REAL_LLM_CALLS` | exact `"true"` to **enable** spend (`llm_client.py:120`; `"1"`, `"TRUE"`, `"True"`, `" true"` all refuse) | **safe** — refuse |
| `SESSION_COOKIE_SECURE` (Q4a) | exact `"false"` to **disable** `Secure` | **safe** — `Secure=True` |

Same shape — an **exact-match literal** is required to leave the safe state — with the polarity matched to each
switch's semantics. **`backend/conftest.py` does not touch `os.environ`** (it only auto-skips `posix_only`
markers), and the only env-touching conftests are `database`'s and `secrets_config`'s, each scoped to its own
package.

> **AUTHN-Fold-2 — REQUIRED, or the suite is non-hermetic.** A developer with `SESSION_COOKIE_SECURE=false`
> exported in their shell would silently exercise the insecure branch in tests that do not monkeypatch it.
> `secrets_config/tests/conftest.py` solves precisely this for its six keys — *"so a real shell-set variable can
> never leak into or mask a case"*. **`backend/authn/tests/conftest.py` MUST clear `SESSION_COOKIE_SECURE`
> before every test**, and every test that cares must set it explicitly, on the `ALLOW_REAL_LLM_CALLS`
> discipline.

### ✅ Check (iv) — does `backend/authn/` collide with an expected-module allowlist, as `case_lifecycle` did? **CLEAN**

* **`test_frozen_untouched.py:21` `FROZEN_UNITS`** is a hardcoded **11-name** set of Phase-1 units. It **already
  excludes** `case_lifecycle`, `outlier_model`, `memo_extensions`, `observability`, `llm_judge` and
  `deploy_config`. Its loop skips directories not listed, so **adding `authn` breaks nothing**.
* **`structural.py::is_under_frozen`** returns `True` for `backend/authn/...` (any `backend/<x>/` except
  `deploy_config`). **Harmless**: `test_noedit.py` only checks **U23's own artifacts** against that classifier.
  ⚑ **`case_lifecycle` has had exactly this property since Scope B with no breakage — the precedent is direct.**
* No test enumerates top-level `backend/` packages.

> **AUTHN-Fold-3 — close the guard gap rather than inherit it.** Because `authn` will not be in `FROZEN_UNITS`,
> `test_no_frozen_unit_imports_the_composition_root` will **not** cover it. `authn` must assert its **own**
> one-way import direction (no `backend.app` import) in its own suite. `case_lifecycle` carries this same gap;
> this pass closes it for `authn` rather than replicating it.

> **AUTHN-Fold-4 — coverage wiring, on U24's exact precedent.** U24 names its real adapter **`repository.py`**
> and adds an **explicit** omit line `*/case_lifecycle/repository.py` (`pyproject.toml:121`) — it does **not**
> rely on the `*/pg_repository.py` glob. `authn` follows suit: `--cov=backend/authn` **plus**
> `omit = "*/authn/repository.py"` and `"*/authn/__main__.py"`. Omitting the `--cov=` line entirely would leave
> the package outside QA-6 — silently, since `test_coverage_gate.py` does not enumerate the list.

### Verdict

**CLEAN.** No further ambiguity. Proceeding to the full TDD-ordered execution steps.

---

## 13. FULL TDD-ORDERED EXECUTION STEPS

> ⚑ **Nothing below has been executed.** This section is the plan of record for the implementation pass and stops
> at its own gate.

### 13.0 ⚑ SUPERSESSION — the §8 delta prediction is revised by the folds

**§8's table is superseded by §13.2. It is preserved above as the pre-ambiguity-check estimate.** Fold-3 adds one
test (the import-direction guard). **Revised total: +28 → 1610 passed**, not +27 → 1609.

### 13.1 The steps

| # | Step | Kind | Gate |
|--:|---|---|---|
| **0** | `pytest backend` baseline | verify | **1582 / 0 / 43 / 5 / 99.87%** — else **STOP** |
| **1** | ⛔ **WIRE-1 §3 amendment sign-off** (§5.1) — two additive rows, no new error code, §6 sentence | **GATED** | **No code until signed off.** Refusal ⇒ pass stops, Q7(b) returns |
| **2** | **PHASE B FLIP** — both `_route_inventory.py` copies → 9 routes / 3 non-GET / 5 modules; U15's three migration assertions → 3 files | 🔴 RED | **exactly 6 RED**: R-1, R-2, R-3a, R-5, R-6, R-7. R-4 green · R-8 skips (Docker) · R-3b green. **Any other set ⇒ STOP** |
| **3** | `0003_auth.sql` + `checksums.json` third entry | GREEN | R-6, R-7 → green. R-8 **CI-only**, never claimed locally |
| **4** | **RED** `authn/tests/test_hashing.py` → then `authn/hashing.py` | RED→GREEN | **+5** |
| **5** | **RED** `authn/tests/test_store.py` + `test_service.py` (in-memory fakes) → then `store.py`, `service.py`, `constants.py` | RED→GREEN | **+12** |
| **6** | **RED** `authn/tests/test_import_direction.py` (Fold-3) + `conftest.py` clearing `SESSION_COOKIE_SECURE` (Fold-2) | RED→GREEN | **+1** |
| **7** | `authn/repository.py` + `__main__.py`; `pyproject.toml` `--cov=` + two omit lines (Fold-4) | GREEN | coverage ≥ 90 |
| **8** | **RED** `authn/tests/test_admin.py` → then `authn/admin.py` (injection-pure, stdin-read, Fold-1) | RED→GREEN | **+3** |
| **9** | **RED** composition-root tests (cookie attrs · `current_identity` from cookie · R1 shape unchanged · `X-User-Id` no longer trusted) → then `backend/app/routes/auth.py` + `dependencies.py` | RED→GREEN | **+7**; R-1, R-2, R-3a, R-5 → **GREEN** |
| **10** | Docs: WIRE-1 §3 amended text · `requirements.md` §10 SECURITY-12 narrowing naming **MFA** and **breached-password-list checking** (Q11c) · register #25 → **NARROWED** with residual | none | no test impact |
| **11** | Full backend suite + `npm test` | verify | **1610 / 0 / 43 / 5 / ≥99.8%**; frontend **687 / 137 / 0 unchanged** |

### 13.2 Predicted deltas, stated in advance

| Area | Δ | Cumulative |
|---|--:|--:|
| Step 4 — hashing (salt-varies · verify-true · verify-false · encoded-format · no-hand-rolled-compare) | **+5** | 1587 |
| Step 5 — store/service (4 uniform-failure paths · lockout trip/reset/expiry · session issue/lookup/expire/revoke · token-stored-hashed) | **+12** | 1599 |
| Step 6 — import-direction guard (Fold-3) | **+1** | 1600 |
| Step 8 — admin entrypoint (set · overwrite · unknown-user) | **+3** | 1603 |
| Step 9 — composition root (3 cookie attrs · 2 identity-from-cookie · R1 shape · `X-User-Id` untrusted) | **+7** | **1610** |

**Skipped stays 43. Errors stay exactly 5** (same `audit_store` Docker-absence names).
⚑ **Coverage is predicted `≥99.8%`, NOT a pinned decimal** — `repository.py` and `__main__.py` are omitted, the
rest is pure logic, and inventing a digit would be false precision.

### 13.3 Stop-gates (superseding §8's list, extended by the folds)

1. Step 0 baseline ≠ **1582 / 0 / 43 / 5 / 99.87%**.
2. Step 1 not signed off → **no route written**.
3. Step 2's RED set ≠ **exactly the 6 predicted**.
4. Any test outside the named set changes state.
5. ⛔ **A-4 (`:239`/`:258`/`:275`) or `app.test.jsx:261` changes state** → **design-invalidating**; stop and
   re-authorize.
6. `errors` ≠ 5 or `skipped` ≠ 43 at any point.
7. Any credential value appears in a log, trace, error body, or `AuditRecord` in any test output.
8. `backend/scripts/`, `backend/app/llm_client.py`, or tier-B touched.
9. **NEW (Fold-2)**: any `authn` test passes or fails differently depending on the developer's shell environment.
10. **NEW (Fold-3)**: `backend/authn/` imports anything from `backend.app`.
11. **NEW**: `httpTransport.js` turns out to need a change after all (Fold-3 of the scoping plan predicted **no
    change**) — that is a stop-gate, not a quiet one-line edit.

---

**STOPPED AT THE EXECUTION-PLAN GATE.** No code. No migration. No route. **WIRE-1 unamended** (step 1 is the
gate). **#25 still OPEN.** Awaiting approval to execute.
