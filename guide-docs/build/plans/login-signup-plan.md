# Login & Signup — SCOPING PLAN

**Stage**: POST-BUILD → scope-gap remediation · the **sixth** item taken up after **SCOPE B CLOSED**
(after **#19 NARROWED**, **#18 NARROWED**, **#20 DISCHARGED**, **#8 NARROWED**, **#3 NARROWED / tier-B Stage 1**,
and the frontend↔backend wiring pass).
**Status**: 🟡 **SCOPING / PLANNING ONLY — NO CODE, NO SCHEMA, NO ROUTE, NO CONTRACT AMENDMENT GENERATED.**
Stopped at the plan-file gate.
**Date**: 2026-07-25T10:42:13Z
**Origin**: a new-session scoping request ("login & signup"), whose ground-truth pass surfaced a previously
**untracked** scope gap — now opened as register item **#25 `PER-4-AUTHN-UNIMPLEMENTED`**
(`BUILD-COMPLETION-REPORT.md`, register update 2026-07-25T10:42:13Z).
**Owner recorded in the register**: **a future authorized authentication pass + `auth-rbac` (U11) scope
reconciliation.** This plan is the scoping half of that pass, begun.

---

## 0. What this document is and is not

* **IS**: a scoping plan. Ground truth from disk, the structural blocker, and **eight open questions** for the
  user to answer.
* **IS NOT**: a design, a fix, a schema, a route, a WIRE-1 amendment, or an authorization. **No code is
  generated. No frozen file is touched. WIRE-1 is not amended. No frozen test is relaxed.**
* **IS NOT** the resolution of **#25**. Opening that item and designing its fix are deliberately separate acts;
  this plan scopes the fix, and **#25 stays OPEN** regardless of what is answered below.

**⚑ ANSWERED 2026-07-25 — all eight `[Answer]` tags are now filled with the user's verbatim answers (§4).** The
questions, options and recommendations below are preserved **byte-for-byte as authored before the answers**, so
the record shows what was asked and recommended, not a reconstruction. *(Original note, retained: "Every
`[Answer]` tag below is BLANK. None is pre-filled.")* Recommendations are given where grounded and are
explicitly marked as recommendations, never as decisions. Where the evidence genuinely does not settle a
question, that is said rather than papered over.

---

## 1. Ground truth — re-established from disk, not from any summary

### 1.1 What identity/auth exists today — the complete mechanism, four links

| # | Location | What happens |
|---|---|---|
| 1 | `frontend/.env.local` → `frontend/src/main.jsx:23` | `import.meta.env.VITE_USER_ID` — a **build/dev-time** Vite env var (currently `demo-underwriter`). |
| 2 | `frontend/src/app/httpTransport.js:42` | `...(userId ? { [USER_ID_HEADER]: userId } : {})` — attaches `X-User-Id` to every request; absent value ⇒ no header. |
| 3 | `backend/app/dependencies.py:160-175` | `current_identity()`: blank/missing header → **401**. Else `SELECT role FROM app_user WHERE user_id = :user_id` (`auth_rbac/pg_repository.py:21`) on the **owner** engine → `to_role()` (`roles.py:57-70`, exact-match, fail-closes) → `None` → **401**. Else `Identity(user_id, role)`. |
| 4 | `backend/app/routes/session.py:22-24` → `sessionClient.js:44` → `App.jsx:52` → `AppFrame.jsx:8` → `RoleGate.jsx` | R1 returns `{user_id, role}`; client fail-closes to `null`; the role is **cosmetic only**. |

Two properties, easy to conflate, kept separate here:

* **The ROLE is never trusted from the client** — `dependencies.py:168`: *"No role value is ever trusted from
  the header itself — only the user id is, and the ROLE comes from `app_user`."* The RBAC half is genuinely
  enforced server-side, twice (route guard + the independent re-check inside the frozen
  `DecisionCommitService.commit()`).
* **The IDENTITY is trusted from the client, entirely.** There is no verification step to bypass — there is no
  verification step.

### 1.2 What does NOT exist — repo-wide scan, verified not assumed

Regex sweep over `.md/.py/.js/.jsx/.yaml/.sql/.json` for
`login|sign ?up|password|bcrypt|argon2|scrypt|pbkdf2|jwt|oauth|oidc|bearer token|session cookie|credential`:

| Absent | Evidence |
|---|---|
| **Password authentication of any kind** | `app_user` has exactly three columns (`0001_initial_schema.sql:51-57`): `user_id`, `subject`, `role`. **No password, hash, salt, or credential column.** The only `PASSWORD` literals in `backend/` are **Postgres role** passwords (`0002_grants.sql:16,19`) and throwaway testcontainer fixtures. |
| **JWT** | Zero occurrences in any production file. Only DISCOVER-phase requirement prose and unrelated tooling rule-files. |
| **Session tokens / cookies / `Authorization` header** | `dependencies.py:31-34`: the stub is *"deliberately NOT `Authorization: Bearer`, which would imply a token semantic (validation, issuer, expiry) that does not exist."* |
| **A sessions table, or any session state** | `GET /session` issues nothing and stores nothing. It reads the header, looks up the role, echoes both. A session-shaped name over a pure identity reflection. |
| **Any middleware** | `add_middleware`: zero hits across `backend/` (independently confirmed, `guide-state.md:4771`). |
| **Signup / registration / user-creation / logout route** | The route surface is exactly seven (WIRE-1 R1–R7), pinned by a frozen test (§3). |
| **A login UI** | Confirmed by the wiring pass's own ground truth, `guide-state.md:4762`: *"A **login UI** is absent; an identity **concept** is not."* |

### 1.3 The security position, stated without hedging

`X-User-Id: <any existing user_id>` **is** authentication. Three consequences, none previously recorded:

1. **SEC-4's segregation of duties is not adversarially enforceable today.** The underwriter/auditor separation
   holds against mistakes and a well-behaved client; it does not hold against anyone who edits a header.
2. **`AuditRecord.underwriter_id` — the CON-BR4 "WHO" in every committed decision — is an unauthenticated,
   self-asserted string.** WIRE-1 §5:122 forbids `underwriter_id` in the request body *precisely so* "a client
   cannot commit **as another user**" — with a forgeable header, that protection is nominal. For a system whose
   headline claim is **100% auditability**, the audit trail's actor field currently has no authentication behind
   it.
3. **In a deployed Vercel build, identity is baked into the bundle at build time** (`main.jsx:23` resolves
   `import.meta.env` at build). Every visitor to a deployment is the same user.

The build record is consistently honest that the header is a **stub**. It is nowhere honest that **PER-4 was
supposed to have replaced it** — which is §1.4.

### 1.4 ⚑ THE SCOPE GAP — login was scoped IN and silently dropped (register #25)

**Answered IN at Requirements Analysis.** `requirement-verification-questions.md` Q6 — *"What
authentication/authorization model should the Underwriter UI use?"*, options A (no real auth) / B / C (full SSO):

> **[Answer]: B — basic login with role-based access (JWT/session).** REASON: RBAC is what actually enforces the
> Q5 role separation (the auditor cannot edit what they audit), which is the part this project genuinely needs.
> Full SSO/OAuth is federated identity that depends on a company IdP and adds demo friction with no
> acceptance-criterion payoff; it belongs with the eventual enterprise/production handover, not this build. Auth
> layer will be structured so an OIDC provider can slot in later.

The answer **rejects A** (no real auth) and **rejects C** (full SSO), selecting the middle. It became a
requirement — `requirements.md:78`:

> | **PER-4** | Authentication = **basic login with role-based access (JWT/session)**. RBAC MUST enforce the PER-1/PER-2 separation in the UI (underwriter vs auditor). | Q6 (B) |

Only the **federated** half was deferred — `requirements.md:62`:

> | **OOS-3** | Full SSO/OAuth federated identity | **Phase 3 — Future Release** (auth structured so OIDC can slot in later) | Q6 |

It propagated through every downstream DISCOVER artifact:

* `personas.md:21` (Underwriter, **Access**): *"Authenticated UI user (JWT/session); read + **act** at the human approval gate"*
* `user-journey.md:46`: *"1. **Login with JWT/session**; RBAC routes the user by role (PER-4)."*
* `stories.md` **US-PLAT-1**, **Phase: 1**, Traces PER-4/PER-5/SEC-4 — *"**Given JWT/session authentication with
  roles underwriter and auditor** / When an auditor attempts any write/edit/approve action in the UI / Then the
  action is denied by RBAC…"*

**Where it was dropped.** `unit-of-work.md:177-183` scopes U11 `auth-rbac` as *"the canonical role/permission
model + backend enforcement at both points"*, listing **PER-4/5** among its key invariants — so U11 **claims
PER-4** while its purpose covers only the authorization half. auth-rbac's FD then excludes authentication
outright (`domain-entities.md:150-151`: *"**Not** an authentication (authn) design — Phase-1 is **authz only**
over a resolved `user_id`"*), justified by **BR-AUTH-10**:

> **Condition**: `app_user.subject` is the **reserved** OIDC identity-binding seam; Phase-1 authz runs over an
> **already-resolved `user_id`**. The **SSO/OAuth authentication flow is deferred to Phase 3 / OOS-3**… This FD
> pins how a resolved `user_id` maps to permissions, **not** how the user authenticates.
> **Why**: **authn is out of Phase-1 scope**; the seam keeps the door open without pulling OOS-3 forward.

> ### ⚑ THE FINDING — BR-AUTH-10's stated reason is not supported by the requirements record
> What DISCOVER put out of Phase-1 scope was **OOS-3 — *full SSO/OAuth federated identity***. **PER-4 — basic
> login (JWT/session) — was answered IN for this build and phase-tagged Phase 1 via US-PLAT-1.** Between
> Requirements Analysis and auth-rbac's FD, *"authn deferred"* **silently widened** from *"federated SSO
> deferred"* to *"all authentication deferred."* **No artifact surfaces, questions, or approves that widening** —
> it appears in BR-AUTH-10 as an already-settled premise, and every artifact downstream (WIRE-1 A6's *"abstract
> seam, deferred"*; the composition root's `X-User-Id` stub) inherits it in good faith.

**Consequence**: **US-PLAT-1's Gherkin `Given` clause is unsatisfied.** Its `Then` clauses are built and tested;
its precondition is not. The story is half-delivered against its own acceptance criteria. **Opened as register
#25.**

### 1.5 Signup was never named anywhere — but the record answers "who creates users"

**Zero occurrences** of *signup*, *sign up*, *self-registration*, or *user registration* in requirements,
stories, personas, unit-of-work, WIRE-1, `guide-state.md`, `audit.md`, or the register. There is no deferral to
quote because it was never raised.

The record does, however, answer the underlying question **three times**:

* `requirements.md` **PER-3**: *"System administrator: manages rulebook versions, **users**, configuration.
  Minimal — **CLI / migration acceptable**, no full admin UI required."*
* `requirements.md` **PER-6**: *"RBAC UI roles = underwriter + auditor(read-only); **admin operates out-of-band
  via CLI**, not a UI role."*
* `requirements.md:62` **OOS-6**: *"Full admin UI | **Phase 3 — Future Release** (admin remains CLI/migration-based
  this engagement)"*

And that path **is built and working**: `backend/admin_cli/cli.py:43` registers `create-user`, backed by
`AppUserWriter.create_user(user_id, subject, role)` (`app_user_writer.py:48`) — gate-first, parameterized,
`IntegrityError` → *"already exists"*. **Admin-provisioned user creation via CLI is already the system's only and
intended user-creation path.** That is directly load-bearing for Q3 and is not treated as an open field.

### 1.6 The Security Guardrails extension is ENABLED — but **scoped**, and the scope excludes authentication

`guide-state.md:25-30`:

> | Security Guardrails | **Enabled (scoped)** | Requirements Analysis (Q13 answered) |
>
> Security Guardrails scope: prompt-injection defense, input validation, secrets management, read-only DB access
> for audit role, audit logging.

⚑ **`SECURITY-12: Authentication and Credential Management` is NOT in that recorded scope** — and the scope was
fixed at Requirements Analysis, i.e. under the *same* assumption §1.4 shows to be unsupported. Introducing login
therefore forces a second, independent decision: **does the extension's scope widen to cover SECURITY-12?**

Per **CLAUDE.md**, *"Non-compliance with any applicable enabled extension rule is a **blocking finding**"*. If the
scope widens, these become blocking obligations (`security-guardrails.md:212-227`), quoted verbatim:

* *"**Password policy**: Minimum 8 characters, check against breached password lists"*
* *"**Credential storage**: Passwords MUST be hashed using adaptive algorithms — never weak or non-adaptive hashing"*
* *"**Multi-factor authentication**: MFA MUST be supported for administrative accounts and SHOULD be available for all users"*
* *"**Session management**: Sessions MUST have server-side expiration, be invalidated on logout, and use secure/httpOnly/sameSite cookie attributes"*
* *"**Brute-force protection**: Login endpoints MUST implement account lockout, progressive delays, or CAPTCHA after repeated failures"*

Plus **SECURITY-08** (`:147`): *"**Token validation**: JWTs or session tokens MUST be validated server-side on
every request (signature, expiration, audience, issuer)"* — already in scope under *"application-level access
control"* on a plausible reading, and unambiguously engaged the moment a token exists.

⚑ **The MFA clause is the sharp one**: widening the scope makes **MFA for admin accounts a blocking
requirement**, which is materially larger than "add a login form". This is surfaced, not improvised past — it is
part of **Q4**.

---

## 2. ⛔ THE STRUCTURAL BLOCKER — four frozen assertions, across two units

Verified by reading each test, not inferred. A login or signup **route** cannot be added while all four stay
green.

| # | Assertion | Location | Why it fails |
|---|---|---|---|
| **A-1** | `test_route_table_equals_the_frozen_composition_root` | `backend/deploy_config/tests/test_routes.py:36` | **Exact-set equality** over `(path, method)` from `create_app().openapi()["paths"]` against the seven WIRE-1 routes. **Any eighth route fails.** Docstring marks it *"LOAD-BEARING — full-highest"*. ⚑ **App-level introspection — binds regardless of which file the router lives in.** |
| **A-2** | `test_no_new_route_file_added_under_backend_app_by_u23` | same file, `:41` | Exact-set equality over filenames in `backend/app/routes/`: `{__init__.py, session.py, decisions.py, not_wired.py}`. **A new `auth.py` fails.** |
| **A-3** | `test_the_route_table_has_exactly_one_non_get_route` | `backend/app/tests/test_no_write_route.py:107` | Asserts non-GET routes `== [("/recommendations/{recommendation_id}/commit", "POST")]`. **Any `POST /login` fails.** |
| **A-4** | `test_no_route_writes_directly_only_commit_does` | same file, `:239` | `.insert(` and `.atomic(` appear **nowhere** under `backend/app/` production source; `.commit(` only in `not_wired.py`. **A signup handler that INSERTs into `app_user` fails.** |

**A-4 is more than a test.** `dependencies.py:15-20` records the composition root's current *architectural
guarantee* as **"every write goes through the frozen `DecisionCommitService`"**. A signup route that inserts a
user would be **the first second write path in the application** — breaking a stated invariant, not merely a
green test.

**Shape**: structurally identical to register **#13 `NOTWIRED-FILENAME-STALE`**, whose register row states the
rename and the test relaxation *"are a **MATCHED PAIR** requiring their own authorization; **neither half is
valid alone**"* — but **larger**: four assertions across **two** units (U23 `deploy-config` + the composition
root) rather than one. **This is the subject of Q8.**

---

## 3. The design tension, stated precisely

> **An in-scope Phase-1 requirement (PER-4) was never built; the stub that stands in its place is a complete
> authentication bypass; and the machinery that would replace it cannot be added without relaxing four frozen
> assertions that were written — correctly — to prevent exactly this kind of unreviewed surface growth.**

This is **unlike** every prior post-Scope-B item. #19/#18/#8/#3 were *"a known deferral, disclosed, needing
work."* #20 was *"already correct, rationale unwritten."* **#25 is the first item where the build's own
requirements record and its shipped behaviour disagree** — and the disagreement was never disclosed.

Three constraints bound every option and are stated up front because they rule out the naive answers:

* ⚑ **C-A — `0001_initial_schema.sql` is FROZEN (U15).** `app_user`'s shape cannot be edited. BR-DB-4 permits
  change only as *"a NEW higher-numbered migration"*, which is `database`-owned. So credential storage, if any,
  is a **new forward-only migration**, never an edit — but it **is new persistent state inside a frozen unit's
  domain**, which is the exact reopening question Scope B had to answer for `case-lifecycle`.
* ⚑ **C-B — `Settings` has EXACTLY SIX required fields** (`secrets_config/settings.py:33-38`), fail-closed. A
  JWT signing key or session secret would be a **seventh** — which **edits a frozen unit (U16)**. There is no
  way to introduce server-held signing material without either that edit or a deliberate decision to source it
  outside `secrets-config` (which would breach SEC-3's single-source control).
* ⚑ **C-C — the `Role` enum and `PERMISSION_MATRIX` are CLOSED at the app layer** (`roles.py:22-51`), while
  `app_user.role` is deliberately an **open `VARCHAR` with no CHECK** (BR-DB-12). The database will accept any
  role string; only the application closes the set, and `to_role()` fail-closes anything non-canonical to
  **401**. Any signup that assigns a role must assign one of exactly three values, or the user is created and
  **immediately cannot authenticate**.

---

## 4. THE OPEN QUESTIONS

> **Instructions**: write your choice after each `[Answer]:` tag. Multiple letters are fine where the options
> compose. **Nothing proceeds until every tag is filled.** Once answered, the full Q&A is embedded back into this
> document and the **mandatory ambiguity-check** runs before anything else happens.

---

### Q1 — Is this a PER-4 scope-gap remediation, or a new feature outside the 24-unit decomposition?

These produce **different documents, different authorization, and different closure semantics** — so it is asked
first.

**Options:**

* **(a) — A PER-4 scope-gap remediation.** The work discharges register **#25** and completes US-PLAT-1's
  unsatisfied `Given` clause. It is corrective work on an in-scope Phase-1 requirement, sitting alongside
  #19/#18/#8/#3 as a register-item pass. `auth-rbac`'s **BR-AUTH-10 scope statement is corrected by supersession**
  (never rewritten in place), on the standing supersede-not-rewrite discipline.
* **(b) — A new feature / a 25th unit.** Treat login+signup as new work outside the 24-unit decomposition,
  following the Scope-B precedent (`case-lifecycle` U24 was added by an explicit decomposition extension with its
  own five-stage BUILD loop).
* **(c) — Both**: #25 is discharged by the *authentication* half; *signup* — never scoped at all (§1.5) — is
  genuinely new work and takes (b)'s treatment.

**Recommendation (grounded): (c), with (a) as its dominant half.** The evidence separates cleanly: **login** has
a requirement (PER-4), a persona attribute, a journey step, and a Phase-1 story with an unsatisfied precondition
— it is unambiguously *owed*, not *new*, and calling it a feature would let the build quietly re-scope a
requirement it already accepted. **Signup** has **no** requirement, **no** story, and **no** deferral anywhere
(§1.5) — calling it a discharge would be inventing a mandate. ⚑ Note the asymmetry matters for closure: under
(c), delivering login discharges #25 **even if signup is never built**, because #25's subject is PER-4, not
signup.

**[Answer]**: (c) — both. Login discharges #25 and completes US-PLAT-1's unsatisfied precondition; signup is genuinely new work, though it resolves almost entirely to "this already exists as admin-cli create-user, by design" per §1.5's evidence. Treat login as scope-gap remediation and signup as a thin layer on top of an already-built path — not a new subsystem.

---

### Q2 — Is this genuinely new domain state, and if so, whose — and does it require reopening a frozen unit?

This is the question the original brief framed as *"is this Scope B for identity?"* It is, structurally: Scope B
had to decide whether the pending-application lifecycle was un-designed domain state belonging in its own stage
(it was — hence U24), and the same test applies here.

**What each option actually creates:**

* **(a) — Credentials as new persistent state, in a NEW table, via a new forward-only `database`-owned
  migration.** E.g. `user_credential(user_id PK/FK → app_user, password_hash, algo, updated_at, failed_attempts,
  locked_until)`. `app_user`'s frozen shape is **untouched** (C-A satisfied — a new table, not an altered one).
  Credential material is isolated in one place with its own grant posture, extending **CORE-RATIONALE-20**'s
  owner-only reasoning (which already covers `app_user` — `dependencies.py:22-29`).
* **(b) — Credentials as new columns on `app_user`.** A new migration `ALTER TABLE app_user ADD COLUMN
  password_hash …`. Fewer objects, but it puts credential material in the table every role-read touches, and it
  changes the shape of a frozen unit's flagship table — a materially larger claim on U15's territory than (a).
* **(c) — NO credential state in this system at all.** Authentication happens elsewhere (an external IdP under
  OIDC, or a platform/proxy gate — see Q7(b)) and this system stores only the binding, for which
  **`app_user.subject` already exists**: *"OIDC-ready subject/issuer seam (external identity binding)"*, UNIQUE
  (`0001_initial_schema.sql:53,56`). **No migration, no new state, no password ever held here.**
* **(d) — Session state as an additional axis** (orthogonal to (a)/(b)/(c)): a `user_session` table for
  revocable server-side sessions, versus stateless tokens that need none. See Q5.

**Recommendation (grounded): (a) for credentials, and see Q5 for sessions — with (c) named as the genuinely
strong alternative if Q7(b) is chosen.** Grounds for (a) over (b): a separate table satisfies C-A with the
smallest claim on frozen territory, keeps credential material out of the hot role-read path, and lets the
credential table carry its own owner-only grant posture without re-litigating `app_user`'s. Grounds for keeping
(c) live: **the safest password store is the one that does not exist** — if Q7(b) or an OIDC answer is taken,
this system never holds a credential, and §1.6's entire SECURITY-12 obligation set largely evaporates. ⚑ **Under
every option, this is new work requiring its own authorization** — even (c) changes what `current_identity`
trusts, which is the security boundary itself.

**[Answer]**: (a) — credentials as new persistent state in a NEW table (user_credential), via a new forward-only database-owned migration. app_user's frozen shape stays untouched (C-A satisfied), credential material is isolated with its own grant posture extending CORE-RATIONALE-20's owner-only reasoning, and this keeps the smallest possible claim on U15's territory.

---

### Q3 — What does "signup" mean for a closed-role BFSI system: self-registration, or admin provisioning?

⚑ **Flagged explicitly as a real design question, not something to default past.**

**The constraint that makes this non-obvious.** `PERMISSION_MATRIX` is **closed** over exactly three roles
(`roles.py:47-51`), and `to_role()` fail-closes anything else to **401** (C-C). So "sign up" cannot mean "create
an account and pick what you are." Someone must assign one of `underwriter` / `auditor` / `admin` — and each
carries real authority: `underwriter` can **commit decisions** (`RBAC_COMMIT`), `auditor` reads the **full audit
trail**, `admin` manages **users and config**.

**Is self-service role assignment sound for a BFSI system? Stated plainly: no.** Self-selection of `underwriter`
would let anyone who can reach the signup form grant themselves the authority to commit binding underwriting
decisions — which is not a hardening detail but a **direct defeat of SEC-4's segregation of duties**, the very
invariant `auth-rbac` exists to enforce, and of the human-in-the-loop gate's meaning (a gate anyone can appoint
themselves to is not a gate). Self-selection of `auditor` would grant unrestricted read of the decision history.
There is no variant of open self-registration over this role set that is defensible.

**Options:**

* **(a) — Admin-provisioning only; no self-service signup at all.** Users are created out-of-band by an admin
  via the **already-built** `admin-cli create-user` (§1.5), with a credential set at provisioning time (or via a
  one-time set-password link). "Signup" as a public flow **does not exist**. Directly consistent with PER-3,
  PER-6 and OOS-6.
* **(b) — Self-registration with NO role** — a user may create an account, which lands with **no usable role**
  and therefore **cannot authenticate past `to_role()`'s fail-close**, until an admin assigns one via the
  existing `admin-cli set-role`. Self-service for the *credential*, admin-gated for the *authority*.
  ⚠️ Requires a fourth "pending/none" state that the closed `Role` enum has no representation for — so it either
  extends a frozen enum or leans on the DB's open `VARCHAR` in a way that only *looks* like a state.
* **(c) — Invite-based**: an admin issues a single-use invitation carrying a pre-assigned role; the invitee sets
  their own credential. Authority is admin-assigned; credential-setting is self-service.
* **(d) — Open self-registration with self-selected role.** Stated for completeness and **recommended against**
  for the reasons above.

**Recommendation (grounded): (a), with (c) as a reasonable upgrade if a browser-based provisioning experience is
wanted.** (a) is what the requirements record already decided three times over (PER-3 / PER-6 / OOS-6), it is
**already built and tested**, and it means the *signup* half of this request resolves to *"this already exists,
as a CLI, by design"* rather than to new code. (c) preserves that property — the admin still assigns the role —
while removing the need for an admin to handle a plaintext credential. ⚑ **(b) is the trap**: it looks like a
compromise but introduces a role state the frozen enum cannot express, and a user who can register but never log
in is indistinguishable at the wire from a failed login. **(d) should be recorded as considered and rejected**,
so a future reader knows it was weighed, not overlooked.

**[Answer]**: (a) — admin-provisioning only, no public self-service signup. Consistent with PER-3/PER-6/OOS-6, already built via admin-cli create-user. Self-selected roles over a closed RBAC_COMMIT-bearing role set is not defensible, and (d) is explicitly rejected on those grounds, recorded as considered-and-rejected. If a nicer provisioning experience is wanted later, (c) invite-based can be layered on without changing this answer's substance — but that's a future decision, not this one.

---

### Q4 — If passwords are introduced at all: storage, hashing, and the SECURITY-12 scope decision

⚑ **This is the new attack surface. It is not hand-waved here, and it carries a second decision (§1.6) that is
easy to miss.**

**Conditional on Q2(a)/(b).** Under Q2(c) most of this collapses — the strongest security argument available is
that this system holds no credential at all.

**4.1 — The hashing decision (if passwords exist):**

* **(a) — Argon2id** (`argon2-cffi`), memory-hard, OWASP's current first recommendation. New dependency.
* **(b) — bcrypt** (`passlib[bcrypt]` or `bcrypt`), cost ≥ 12. Older, extremely well-understood, ubiquitous.
* **(c) — scrypt / PBKDF2** via `hashlib` — **no new dependency** (stdlib), adaptive, acceptable under
  SECURITY-12's *"adaptive algorithms"* wording.

**Non-negotiable regardless of choice, and to be treated as design constraints rather than review comments:**
per-user salt; **constant-time verification**; **never** log, trace, or include credential material in an error
body (SEC-3 already forbids secret VALUES in `message`/`detail` — WIRE-1 §4:60); a **uniform failure response**
for "unknown user" and "wrong password" so the endpoint is not a user-enumeration oracle; and credential material
**never** in `AuditRecord`, Langfuse traces, or Prometheus labels.

**4.2 — ⚑ The SECURITY-12 scope decision (§1.6):**

The Security Guardrails extension is **Enabled (scoped)**, and the recorded scope **excludes** authentication —
fixed at Requirements Analysis under the same unsupported assumption §1.4 documents.

* **(i) — Widen the scope to include SECURITY-12.** Its clauses become **blocking findings** per CLAUDE.md:
  breached-password checking, **MFA supported for administrative accounts**, server-side session expiry +
  invalidation on logout + `Secure`/`HttpOnly`/`SameSite`, and **brute-force protection (lockout / progressive
  delay / CAPTCHA)** on the login endpoint.
* **(ii) — Keep the scope as recorded**, and implement a named, explicitly-justified subset (e.g. adaptive
  hashing + lockout + secure cookie attributes, **without** MFA or breached-password lookup), **disclosed as a
  deliberate narrowing** rather than silently omitted.

**Recommendation (grounded): 4.1 → (a) Argon2id; 4.2 → (ii), with the narrowing disclosed by name.** Argon2id
because if a credential store is being created in a BFSI system in 2026 there is no reason to create it with a
weaker primitive, and the dependency cost is one wheel. (ii) because **MFA is genuinely out of proportion** to
this build's stated scope (a portfolio-grade validation deploy, free-tier, synthetic data only — PROJECT-BRIEF §8),
and a breached-password API call would put a **network dependency in the authentication path** of a system that
runs its entire test suite offline. ⚑ **But (ii) must be an explicit, recorded decision** — the failure mode this
whole plan exists to correct is exactly a scope narrowing that happened without being surfaced. Choosing (ii)
without recording it would repeat #25's mistake in a new place.

**[Answer]**: 4.1 — (a) Argon2id. Current OWASP-recommended primitive, one dependency, no reason to choose weaker for a BFSI system's first credential store. 4.2 — (ii), keep the Security Guardrails extension scope as currently recorded, implement adaptive hashing + lockout + secure cookie attributes, explicitly OMIT MFA and breached-password-list checking as out of proportion to this build's stated scope (portfolio-grade validation deploy, free-tier, synthetic data only). This narrowing must be disclosed by name in the same location the extension's scope is recorded (guide-state.md's Security Guardrails scope line) — not silently decided.

---

### Q5 — Session mechanism: stateless token, or revocable server-side session?

PER-4 names *"JWT/session"* — **naming both**, so either satisfies its wording. This is therefore a genuine
engineering choice, not a compliance one.

* **(a) — JWT (stateless).** No new table. But **revocation is the known weakness**: a compromised or
  role-changed user's token stays valid until expiry, and `admin-cli set-role` would **not** take effect until
  then — a real segregation-of-duties hole in a system whose entire point is role separation. Needs a signing key
  (**C-B**: a seventh `Settings` field, editing frozen U16).
* **(b) — Opaque server-side session token in a `user_session` table.** Revocable immediately; no token-parsing
  surface; role changes take effect on the next request. Costs new persistent state (Q2(d)) and expiry
  housekeeping. ⚑ **Needs no signing key**, so **C-B is avoided entirely** — a random opaque token is validated
  by lookup, not by signature.
* **(c) — Signed cookie carrying the identity** — the middle option: no session table, but the same revocation
  weakness as (a) plus a signing key (C-B).

**Delivery, orthogonal to the above**: an `HttpOnly` + `Secure` + `SameSite` **cookie** is preferable to a
JS-readable token, and it fits this topology unusually well — `main.jsx:25` already uses `baseUrl: '/api'`, the
Vercel rewrite and the Vite dev proxy both make requests **same-origin**, so a cookie needs no CORS relaxation
and `backend/app/` needs no middleware. ⚑ Note `httpTransport.js:37` does **not** currently send `credentials`,
so cookie delivery is a one-line change **in a non-frozen composition-root file** — not a frozen-seam edit.

**Recommendation (grounded): (b), delivered as an `HttpOnly`/`Secure`/`SameSite=Lax` cookie.** Three grounds:
**(1)** it is the only option under which `admin-cli set-role` and user deactivation take effect **immediately**,
which a role-separation system should not compromise on; **(2)** it **avoids C-B entirely** — no signing key, so
frozen U16 `Settings` is not edited, which is a materially smaller blast radius than (a)/(c); **(3)** same-origin
cookie delivery needs no CORS change, preserving `deploy-config`'s load-bearing choice that the deployed topology
*"requires no CORS change in the backend and therefore never touches the closed composition root."* ⚑ Honest
cost: (b) is the only option that adds a **second** new table, so Q2 and Q5 should be answered together.

**[Answer]**: (b) — opaque server-side session token in a new user_session table, delivered as an HttpOnly + Secure + SameSite=Lax cookie. Avoids C-B entirely (no signing key, no frozen Settings edit), makes admin-cli set-role and deactivation take effect immediately (the property a segregation-of-duties system should not compromise on), and needs no CORS change given the existing same-origin /api topology.

---

### Q6 — Does WIRE-1's R1 `GET /session` contract change, or does login sit in front of it?

⚑ **A precise split matters here, and it is good news on one axis.**

**R1's response SHAPE need not change at all.** WIRE-1 §6:136 pins *"`GET /session` → `{user_id, role}`… `role`
is the exact lowercase enum value"* — that is **how the Role reaches the client**, and it is unaffected by how
the caller proved who they are. §6:137 already anticipates this exactly:

> *"The auth **handshake** mechanism (bearer token / session cookie / OIDC) is an **abstract seam, deferred** —
> **Phase-1 may stub it**… WIRE-1 pins **how the Role reaches the client** (the shape), not the handshake."*

And `dependencies.py:34` records the same expectation from the implementation side: *"Replacing this with the
real OIDC handshake **touches only this module**."*

**So**: replacing the stub with a real handshake is **the seam being used as designed**, not a contract change.
`current_identity()` resolves from a cookie/token instead of a header; R1's body is **byte-unchanged**;
`sessionClient.js`, `RoleContext`, `RoleProvider`, `useCurrentRole` and `RoleGate` need **zero** change.

* **(a) — R1 unchanged; login sits IN FRONT of it.** Browser authenticates → receives a session → R1 reads that
  session and returns `{user_id, role}` exactly as today.
* **(b) — R1's shape is amended** (e.g. `+ authenticated: bool`, `+ expires_at`). ⚠️ A **WIRE-1 §5/§6
  amendment**, and it would change a surface **five frozen UI units** consume.
* **(c) — R1 unchanged in shape, but its §3 Auth-column wording is amended** as part of a route-table amendment
  (Q7(a)).

**Recommendation (grounded): (a).** The contract already reserved this exact seam and said Phase 1 may stub it;
using the seam is not amending the pin. ⚑ **Sharp distinction to carry into Q7**: R1's **shape** needs no
amendment (a), but a new **login route** is an addition to WIRE-1 **§3's pinned route table** — which *is* an
amendment, just a different one. Answering (a) here does **not** avoid Q7. ⚑ Note also that **WIRE1-Fold-4 (the
2026-07-17 amendment) added a FIELD, never a route** — so a route addition would be the **first change to the
pinned R1–R7 table in the build's history**.

**[Answer]**: (a) — R1's response shape is unchanged. WIRE-1 §6:137 already reserved this exact seam for a real handshake to replace the stub; using it as designed is not a contract amendment. current_identity() resolves from the session cookie instead of the X-User-Id header; sessionClient.js, RoleContext, RoleProvider, useCurrentRole, and RoleGate need zero change.

---

### Q7 — A new route (WIRE-1 §3 amendment), or layered without touching WIRE-1's routes?

⚑ **A real decision point, flagged as such because WIRE-1 has been held frozen for the entire build**, and
because §2's four assertions make the cost concrete rather than notional.

* **(a) — New routes, WIRE-1 §3 amended additively.** `POST /login`, `POST /logout`, and (if Q3 selects (b)/(c))
  a signup/invite route. **Cost, stated fully**: an amendment to the **pinned route table** (the first in the
  build — WIRE1-Fold-4 added only a field) **plus all four of §2's frozen assertions** (A-1…A-4), i.e. a
  matched-pair relaxation across **two** units. **Benefit**: PER-4 is satisfied in its plain sense — a login
  endpoint the UI calls — the mechanism is self-contained, local dev works with no platform dependency, and the
  system remains honestly self-describing.
* **(b) — Platform / reverse-proxy gate; WIRE-1's route table byte-unchanged.** Authentication happens **outside**
  the FastAPI app — a Vercel middleware/edge gate or an authenticating proxy in front of Render — which verifies
  the credential and passes a **signed** identity assertion to the backend. **Zero new routes. Zero WIRE-1
  amendment. Zero frozen-test relaxation** (A-1…A-4 all stay green: no route is added, no file appears under
  `backend/app/routes/`, no non-GET route appears, and no handler writes).
  **Genuine strengths**, stated fairly and not as a consolation: it closes §1.3's actual vulnerability with the
  **smallest possible disturbance to frozen surface**; it keeps **no credential store in this repo** (composing
  naturally with Q2(c)); and it is the fastest path from "forgeable header" to "verified identity."
  **Genuine weaknesses, equally plainly**: ⚑ the backend **must still verify the assertion cryptographically**,
  because Render's service URL is publicly reachable and a proxy that can be bypassed is not a gate — this is the
  classic and fatal error in this pattern, and it means `dependencies.py` changes and **C-B (a signing/verifying
  key in frozen `Settings`) returns** ; it relocates authentication into deploy/platform configuration, splitting
  the security boundary across two owners; local development must either depend on the platform or re-introduce a
  bypass (i.e. re-create today's stub); and it satisfies PER-4's *"basic login … in the UI"* only loosely, so
  choosing it means **recording a PER-4 disposition change** rather than a clean discharge.
* **(c) — Sequenced hybrid**: (b) first as an immediate mitigation of §1.3, (a) later as the PER-4 discharge.
  ⚠️ Two passes, two authorizations, and the interim state must be **disclosed as interim**, not quietly
  recorded as done.

**Recommendation (grounded): (a) — with (b) named as legitimate and NOT dismissed.** (a) is recommended because
PER-4's plain reading is a login the application owns, because a self-contained mechanism keeps the security
boundary in one place under one owner, and because §2's cost — while real — is a **one-time, reviewable,
explicitly-authorized** relaxation of assertions that were written to force exactly this conversation, which is
them working correctly rather than obstructing. ⚑ **However**: if the priority is closing §1.3's vulnerability
with minimum disturbance to a build that has held WIRE-1 frozen for 24 units, **(b) is a defensible and honest
answer**, and it should not be dismissed on aesthetics — its decisive weakness is not that it is "less proper"
but that the **bypass problem forces a verifying key into frozen `Settings` anyway**, which erases much of its
frozen-surface advantage. That trade is the user's to weigh, and both readings are recorded here as reasonable.

**[Answer]**: (a) — new routes (POST /login, POST /logout), WIRE-1 §3 amended additively. PER-4's plain reading is a login endpoint the application owns, and keeping the security boundary under one owner in one place is worth the one-time, reviewable relaxation of the four frozen assertions named in §2. (b)'s platform-gate approach is acknowledged as legitimate but not chosen — its bypass problem reintroduces a verifying key into frozen Settings anyway, eroding its main advantage, and it would split the security boundary across two owners for a system this size.

---

### Q8 — Should relaxing the four frozen assertions be its OWN separately authorized reopening, rather than bundled into this work?

**Conditional on Q7(a) or Q7(c).** Under Q7(b) the question does not arise — nothing is relaxed.

**The precedents, both directly on point:**

* **#13 `NOTWIRED-FILENAME-STALE`**, verbatim: the rename and the test relaxation *"are a **MATCHED PAIR**
  requiring their own authorization; **neither half is valid alone**."* §2 is that shape, **four assertions
  across two units** instead of one.
* **U24's three reopenings** (`list_application_ids()`, `memo_from_canonical()`, the two-step commit claim) were
  **each authorized separately and logged to `audit.md`/`guide-state.md` BEFORE any code** — never folded into
  the pass that needed them, even when the need was obvious and the reopening was certain to be granted.

* **(a) — Its own separately authorized pass**, executed **before** the login/signup code-gen plan: a standalone
  scoping + design pass that decides **what replaces each of A-1…A-4** (a widened frozen set? an explicit
  allowlist? a narrowed invariant that still forbids unreviewed routes?), with its own ambiguity-check and its own
  gate.
* **(b) — Bundled** into the login/signup code-gen plan as a preparatory step.
* **(c) — (a)'s design and approval, (b)'s application**: the relaxation is designed and approved standalone, but
  **applied** as step 0 of the login code-gen pass — so the assertions are never weakened while nothing depends on
  the weakening.

**Recommendation (grounded): (c) — (a)'s authorization discipline with (b)'s sequencing.** Four grounds:
**(1)** the #13 row already rules that this exact shape needs its own authorization, and #13 is *smaller*;
**(2)** U24 was reopened three times and **not once** was the authorization folded into the work that needed it,
even when granting was a formality — the discipline is the point;
**(3)** A-1 is U23's **"LOAD-BEARING — full-highest"** assertion and A-4 encodes the composition root's
*"every write goes through the frozen `DecisionCommitService`"* guarantee — relaxing these inside a feature pass
means **a feature approval silently doubles as an architecture-invariant approval**, which is precisely what this
build has refused twenty-four times;
**(4)** the relaxation genuinely needs **designing**, not just permitting — "what should A-1 assert *instead* of
exact-set equality over seven routes, such that it still catches an unreviewed eighth?" is a real design question
with its own ambiguity-check, and burying it inside a login plan would be the first time this build let a
substantive design decision ride along as a preparatory step.
⚑ The **honest counter-argument for (b)**, recorded rather than suppressed: doing the relaxation strictly first
leaves a window in which the assertions are weaker with nothing yet to show for it. **That is exactly what (c)
resolves** — design and approve standalone, apply at the moment the code that justifies it lands.

**[Answer]**: (c) — design and approve the frozen-assertion relaxation as its own standalone, separately authorized pass (mirroring U24's three reopenings and the #13 matched-pair ruling), but apply it as step 0 of the login/signup code-gen pass rather than in a disconnected prior session. This keeps the authorization discipline intact (a feature approval never doubles as an architecture-invariant approval) while avoiding a window where the assertions are weakened with nothing yet landed to justify it.

---

## 5. Holds for this pass — verified, all currently upheld

| Hold | Status at plan time |
|---|---|
| No frozen-23 (or 24, incl. `case-lifecycle`) unit internal or test edited | ✅ Untouched — read-only throughout |
| `backend/app/routes/` untouched; **no route added** | ✅ Untouched — no backend file written at all |
| `backend/app/llm_client.py`, `backend/scripts/`, tier-B untouched | ✅ Untouched — #18's spend guardrails unaffected; **no API call, no spend** |
| **WIRE-1's contract text NOT amended** | ✅ Untouched — amendment is *proposed as Q6/Q7*, not performed |
| U15's frozen `0001_initial_schema.sql` / `0002_grants.sql` untouched; **no migration written** | ✅ Untouched — `app_user` read as ground truth only |
| U16's frozen `Settings` untouched (**six fields, unchanged**) | ✅ Untouched — C-B is *named*, not acted on |
| U23's frozen `test_routes.py` + the composition root's `test_no_write_route.py` **not relaxed** | ✅ Untouched — A-1…A-4 all still green and asserting exactly what they asserted |
| `not_wired.py` not renamed (#13 stays open) | ✅ Untouched |
| `audit_store` Docker-guard gap untouched — 5 errors stay exactly 5 | ✅ Untouched |
| **No code generated; no frozen file touched** | ✅ Only `guide-docs/` written: this plan, the #25 register entry, `guide-state.md`, `audit.md` |
| **#25 not resolved** — opening it is separate from designing its fix | ✅ Opened only; status **OPEN**, no fix applied |

**Test state carried forward, NOT re-run by this pass**: backend **1578 passed / 0 failed / 43 skipped / 5
pre-existing `audit_store` Docker-absence errors**, coverage **99.87%**; frontend **687 passed / 137 files / 0
failed**. **Nothing was executed or modified under `backend/` or `frontend/`.**

---

## 6. What happens after the answers

1. Answers recorded verbatim in `audit.md`; **the full Q&A embedded back into this document** (§4 becomes the
   answered record).
2. **The mandatory ambiguity-check runs** against the answer set — surface-and-stop if not clean. Likely directed
   checks, named in advance: **(i)** Q2/Q5 answer-set consistency (do the chosen credential and session stores
   compose into one migration or two?); **(ii)** whether the chosen mechanism actually avoids **C-B**, or quietly
   requires the frozen-`Settings` edit anyway (Q5(a)/(c) and Q7(b) all do — Q5(b) does not); **(iii)** whether any
   chosen option collides with `deploy-config`'s no-CORS-change property or U23's frozen tests beyond A-1/A-2;
   **(iv)** whether the Q4.2 narrowing, if chosen, is stated by name in every location that records the
   extension's scope.
3. **If Q7(a)/(c) and Q8(a)/(c)**: a **separate frozen-assertion relaxation authorization** is logged and gated
   **before** any login code-gen plan is written.
4. **Then** a code-gen plan (plan-then-generate, leaf-first TDD, RED before GREEN) under its own approval.
5. **#25 is discharged only on delivered, verified behaviour** — not on this plan, and not on an approved design.
   Per the standing evidentiary discipline (#18/#8 precedent), a mechanism that is structurally complete but
   unverified against a real running system is **NARROWED, not DISCHARGED**.

---

**STOPPED AT THE PLAN-FILE GATE.** No code. No schema. No route. No WIRE-1 amendment. No frozen test relaxed.
**#25 opened, not resolved.** The next decision is the user's.

---

## 7. MANDATORY AMBIGUITY-CHECK — run against the Q1–Q8 answer set + §1 ground truth

**Run**: 2026-07-25 · **Result**: ⚠️ **NOT CLEAN — 3 MATERIAL FINDINGS → SURFACE-AND-STOP at Q9–Q11.**
4 folds resolved. **The standalone frozen-assertion relaxation design was NOT written**, because two of the three
findings change its scope and one changes what it must assert. Writing it now would produce a plan that is wrong
on arrival.

Every finding below was established **by reading the asserting code**, not inferred.

---

### ⚠️ Directed check (i) — Q2/Q5 into one migration or two: **NOT CLEAN — MATERIAL**

Q2(a) and Q5(b) each create a table (`user_credential`, `user_session`). Whether that is one migration or two is
**not the real question** — the real question is **whose sequence they land in**, and the answer set assumed a
path that fires three assertions nobody had counted.

**⚑ `database` (U15) carries THREE exact-set assertions over its migration filenames, plus a two-entry checksum
manifest:**

| Assertion | Location | Text |
|---|---|---|
| applied set | `backend/database/tests/test_migration_apply.py:56` | `assert applied == {"0001_initial_schema.sql", "0002_grants.sql"}` |
| checksum manifest set | `backend/database/tests/test_migration_checksum.py:114` | `assert set(cs) == {"0001_initial_schema.sql", "0002_grants.sql"}` |
| discovered order | `backend/database/tests/test_migration_runner.py:75` | `assert names == ["0001_initial_schema.sql", "0002_grants.sql"]` |
| the manifest itself | `backend/database/migrations/checksums.json` | exactly two entries |

And `backend/database/migration_runner.py:69` discovers by glob — `sorted(migrations_dir.glob("[0-9][0-9][0-9][0-9]_*.sql"))`.
**So a new `0003_auth.sql` in U15's directory is auto-discovered, and all three assertions fail.**

**The U24 precedent offers an alternative that fires none of them** — `case_lifecycle` owns its **own** migrations
directory, its **own** checksum manifest, and its own `apply_case_migrations()` with a collision guard
(`backend/case_lifecycle/migrate.py:60-83`). U15's three assertions only inspect U15's directory, so an
auth-owned sequence leaves them green.

**⛔ But that alternative is not free either.** `backend/scripts/run_migrations.py:57-58` **hardcodes exactly two
sequences**:

```
applied_db   = MigrationRunner(engine).apply_all()   # U15: plain runner, its own default dir
applied_case = apply_case_migrations(engine)          # U24: collision-guard first, its own dir
```

Its own docstring pins this as deliberate — *"**Hardcoded, explicitly named** (Q3-A — no dynamic discovery, which
C-C would make hazardous)"* (register #8). **A third sequence would never run at deploy time unless that file is
edited — and `backend/scripts/` is explicitly off-limits for this pass and under the standing instruction.**

**Neither option is free, and the choice decides which unit is reopened.** → **Q9.**

---

### ✅ Directed check (ii) — does the chosen mechanism actually avoid C-B: **CLEAN (2 folds)**

**Confirmed: Q5(b) avoids C-B entirely.** An opaque, randomly-generated session token is validated by **lookup**,
not by signature, so no signing key is required and **`Settings` stays at exactly six fields** — frozen U16
untouched. Nothing else in the answer set (Argon2id parameters, cookie attributes, lockout counters) requires a
secret.

* **LOGIN-Fold-1 — a paired-edit trap that does NOT fire.** `backend/secrets_config/tests/test_governance.py:92-94`
  asserts `.env.example`'s active keys **equal** `Settings.model_fields` exactly
  (`assert active == fields, f"drift: env.example {active} != Settings {fields}"`). Any new `Settings` field would
  therefore be a **two-file paired edit across a frozen unit**. Because the answer set adds **no** field, this
  stays green — but it is recorded because it is the exact mechanism that would bite if Q5 were ever revisited
  toward (a)/(c).
* **LOGIN-Fold-2 — the `Secure`-cookie-over-local-HTTP problem, resolved by precedent.** A `Secure` cookie is not
  sent over `http://127.0.0.1`, so the dev topology needs the attribute conditional — which looks like it needs a
  new config input, i.e. C-B by the back door. **It does not.** `backend/app/llm_client.py:106-120` sets the
  precedent verbatim: *"why reading `ALLOW_REAL_LLM_CALLS` from `os.environ` here is **NOT** a SEC-3 violation.
  `dependencies.py`'s rejection of `os.environ` is scoped to **credentials and secret material specifically**.
  This is a **behavioural on/off switch** … **not a credential**"* — and it is read at `llm_client.py:120` exactly
  that way. A cookie-`Secure` toggle is the same shape. **Resolved, no stop.**

---

### ⚠️ Directed check (iii) — collision with `deploy-config`'s no-CORS property or any frozen test beyond A-1/A-2: **NOT CLEAN — MATERIAL (plus 2 folds)**

**The CORS property holds, and better than expected:**

* **LOGIN-Fold-3 — cookie delivery needs NO `httpTransport.js` change.** `fetch`'s default credentials mode is
  `same-origin`, and the topology is already same-origin (`main.jsx:25` `baseUrl: '/api'` + the Vercel rewrite +
  the Vite dev proxy). Cookies are therefore sent **automatically**, so `frontend/src/app/httpTransport.js` — a
  file `is_under_frozen` classifies as frozen (`structural.py:74`) — **is not touched at all**.
  `deploy-config`'s load-bearing *"requires no CORS change in the backend"* property is **preserved**.
* **LOGIN-Fold-4 — editing `App.jsx` to mount a login view is NOT blocked by U23.** `is_under_frozen` returns
  `True` for `frontend/src/app/App.jsx`, but `test_noedit.py` only asserts that **U23's own artifacts** sit
  outside frozen trees (`test_every_u23_artifact_is_outside_every_frozen_tree`) plus classifier non-vacuity. It
  does **not** assert `App.jsx` is unmodified — **proven by the wiring pass**, which edited `App.jsx` with
  `test_noedit`/`test_build` green at 11 passed. **No new blocker.**

**⛔ But a frozen assertion beyond A-1/A-2 WAS found, in a third surface — the frontend:**

`frontend/src/app/__tests__/app.test.jsx:261` —
`expect(Object.keys(seams).sort()).toEqual(['commit', 'history', 'memo', 'override', 'queue'])` —
**exact-set equality over the seam keys.** PER-4 requires a login **in the UI**; if the login client is registered
as a sixth seam, **this test fails.**

⚑ **This one is resolvable by design, and the precedent is exact**: `frontend/src/app/sessionClient.js` is
already a transport-calling identity client that is **deliberately not a registered seam** — its header states it
is *"Own-local, mirroring — not imported from — the seam convention: this is a one-shot read, not a unit seam."*
A login client following that same pattern keeps `app.test.jsx:261` green. **Recorded as a BINDING CONSTRAINT on
the code-gen pass rather than a stop** — but it must be pinned now, because a code-gen pass that reached for
`createSeams` would break a test the relaxation plan was never scoped to cover.

**⚑ THE CONSEQUENCE — §2's blocker figure is UNDERSTATED, and Q8 was authorized against the understated figure.**

| | Stated in §2 / register #25 / the Q8 question | Actual, under the chosen answer set |
|---|---|---|
| Assertions | **4** | **7** (A-1…A-4 **+** the three U15 migration assertions from check (i)) |
| Units | **2** (U23 + composition root) | **3** (U23 + composition root + **U15 `database`**) |
| Also engaged | — | U15's `checksums.json`; and `app.test.jsx:261` as a **design constraint** (Fold-4), not a relaxation |

The Q8 answer explicitly reasons about *"the four frozen-assertion blocker."* **That premise is now known to be
wrong.** Silently widening the relaxation pass from 4→7 assertions and 2→3 units would be precisely the
unsurfaced scope-widening that **register #25 exists to record** — repeating it inside the very pass that opened
#25 is not defensible. → **Q10.**

---

### ⚠️ Directed check (iv) — is the Q4.2 narrowing stated by name everywhere the extension's scope is recorded: **NOT CLEAN — MATERIAL**

The Q4.2 answer requires the narrowing be disclosed *"in the same location the extension's scope is recorded
(**guide-state.md's Security Guardrails scope line**)"* — naming **one** location.

**A repo-wide grep finds the scope recorded authoritatively in FIVE:**

| # | Location | What it records |
|--:|---|---|
| 1 | `guide-docs/guide-state.md:28-30` | the scope line the answer names |
| 2 | `guide-docs/discover/requirements/requirements.md:212-214` | **§10 Security Scope** — *"Enabled, enforced as blocking, **scoped** to…"* |
| 3 | `guide-docs/discover/requirements/requirements.md:261` | **§13 Extension Compliance Summary** |
| 4 | `guide-docs/discover/plans/execution-plan.md:295` | **§8 Extension Compliance** |
| 5 | `guide-docs/discover/requirements/requirement-verification-questions.md:152-153` | **Q13**, the origin of the scope |

⚑ **This is the #20 directed-check-(ii) precedent, exactly.** There, the scoping pass identified one in-code `#20`
reference and **missed a second** that asserted the opposite; the ambiguity-check caught it, and executing without
it *"would have shipped a self-contradiction."* Here the answer names one location and there are five — and
disclosing in only `guide-state.md` would leave **four** artifacts recording an authentication-excluding scope
with no note that authentication is now in scope under a **named, deliberate** narrowing.

⚑ **And the extra locations are not equivalent to the named one.** #2–#5 are **DISCOVER-phase approved
artifacts**. Touching them is a materially different act from appending to `guide-state.md`, and under this
build's supersede-not-rewrite discipline they would be **superseded, never rewritten in place**. **The answer
authorized one location; disclosing across five — or superseding approved DISCOVER artifacts — exceeds what was
authorized.** → **Q11.**

---

## 8. SURFACED — Q9, Q10, Q11 (blank; nothing proceeds until answered)

### Q9 — Which migration sequence owns `user_credential` / `user_session`?

* **(a) — A new `0003_*.sql` in `database`'s (U15) own sequence**, as Q2(a)'s wording implies. ✅ Auto-discovered
  by the existing glob; ✅ **no `backend/scripts/` edit** — it runs at deploy time for free.
  ⛔ **Fires all three U15 assertions + the checksum manifest**, adding a third unit to the relaxation pass.
* **(b) — A NEW auth-owned migration sequence** with its own directory, checksum manifest and collision guard, on
  the **U24 precedent**. ✅ **Fires zero U15 assertions** — U15 stays completely untouched.
  ⛔ **Requires editing `backend/scripts/run_migrations.py`** to register the third sequence — **explicitly
  off-limits this pass**, so it needs its own authorization, or the migration silently never runs on deploy
  (which is register **#8**'s exact failure mode, freshly remediated).
* **(c) — Land the tables in U24's existing `case_lifecycle` sequence.** ⛔ **Recommended against**: credentials
  have no relationship to case lifecycle; it would make U24's migration mean two unrelated things and dilute
  MIGSCOPE-1's self-containment rationale.

**Recommendation (grounded): (a).** The three U15 assertions are **exactly the kind of unreviewed-growth guard
this whole exercise is already relaxing under authorization** — adding them to a relaxation pass that is
happening anyway is cheaper and more honest than (b)'s alternative, which trades three visible test failures for
an **invisible** deploy-time gap in the one file this pass may not touch. ⚑ (b)'s risk is worse in kind, not just
degree: (a) fails **loudly** in CI; (b) fails **silently** in production. ⚑ If (b) is preferred anyway, the
`run_migrations.py` edit must be authorized **explicitly and separately** — it is register #8's file.

**[Answer]**: (a) — U15 owns the new migration as 0003_auth.sql, following the existing forward-only sequence with its own checksum-manifest entry. Chosen because it fails loudly in CI if anything drifts, versus (b)'s own-directory approach failing silently at deploy time via run_migrations.py's hardcoded two-sequence list — exactly register #8's remediated failure mode, and I don't want to reintroduce it one register item later. If a U24-style separate sequence is ever wanted, that's its own future decision requiring its own authorization of the run_migrations.py edit — not assumed here.

---

### Q10 — Does the standalone relaxation pass widen to cover all seven assertions across three units?

Q8(c) was answered against *"the four frozen-assertion blocker."* The true figure under this answer set is
**seven across three units** (check iii), or **four across two** if Q9 selects (b).

* **(a) — Widen it**: one relaxation pass covering A-1…A-4 **plus** the three U15 migration assertions, with the
  corrected figure written into §2 and register #25 by **supersession**, not silent edit.
* **(b) — Keep it at four**, and treat the U15 migration assertions as a **separate, later** authorization when
  the migration is actually written.
* **(c) — Conditional on Q9**: if Q9(a), widen to seven; if Q9(b), it stays at four **by construction** and this
  question dissolves.

**Recommendation (grounded): (c), which under the Q9(a) recommendation resolves to (a).** Grounds: the two
questions are **one decision viewed twice** — the assertion count is a *consequence* of the migration-ownership
choice, not an independent variable, and answering them separately risks an inconsistent pair. Widening is
preferable to (b) because the U15 assertions and A-1…A-4 fail **for the same reason** (exact-set guards meeting
authorized growth) and want **one** coherent replacement design, not two that must later be reconciled. ⚑ Either
way, **§2 and register #25 must be corrected by supersession** — the "four across two" figure is now known to be
wrong and must not be left standing as if true.

**[Answer]**: (a) — yes, the relaxation pass widens to seven assertions across three units (U23's A-1/A-2, the composition root's A-3/A-4, and U15's three migration-set assertions newly triggered by Q9). Register #25 and the plan's §2/§8 framing are corrected by supersession to state seven-across-three, not four-across-two — cite the exact assertions and units, don't silently absorb the difference.

---

### Q11 — Where is the Q4.2 SECURITY-12 narrowing disclosed?

* **(a) — `guide-state.md` only**, exactly as the Q4.2 answer says. ⛔ Leaves four artifacts asserting an
  authentication-excluding scope with no pointer.
* **(b) — `guide-state.md` + a supersession note on each of the four DISCOVER artifacts** (`requirements.md` §10
  and §13, `execution-plan.md` §8, `requirement-verification-questions.md` Q13), original text preserved verbatim.
  ✅ No artifact contradicts another. ⛔ Touches approved DISCOVER-phase artifacts — beyond what Q4.2 authorized.
* **(c) — `guide-state.md` + register #25 + this plan**, with **one** forward pointer added to `requirements.md`
  §10 (the single most authoritative DISCOVER location) and the other three left as historical record.
  A middle path: the contradiction is closed where a reader is most likely to meet it, without editing four
  approved artifacts.

**Recommendation (grounded): (c).** (a) reproduces #20's near-miss knowingly, which is not defensible now that the
five locations are enumerated. (b) is the most complete but edits four approved DISCOVER artifacts for a
**narrowing that has not yet been implemented** — disclosure should not outrun the change it describes. (c) closes
the contradiction at the authoritative source (`requirements.md` §10 is where *"enforced as blocking, scoped to"*
lives, and therefore where a compliance reader looks first) while leaving genuinely historical records intact. ⚑
Whichever is chosen, the narrowing must name **MFA** and **breached-password-list checking** explicitly as the
omitted clauses — an unnamed narrowing is the #25 failure mode.

**[Answer]**: (c) — disclose the SECURITY-12 scope narrowing at requirements.md §10 only, closing the contradiction at its source rather than editing all five locations for a narrowing that isn't implemented yet. Name explicitly what's excluded — MFA and breached-password-list checking — rather than a vague "narrowed scope" note. If/when the other four locations are next legitimately touched for unrelated reasons, the same disclosure should be added there too, but that's not authorized as part of this pass.

---

**STOPPED — SURFACE-AND-STOP at Q9–Q11.** Per Q8(c) and the standing discipline, **the standalone
frozen-assertion relaxation design has NOT been written**: Q9 and Q10 determine its scope (four assertions across
two units, or seven across three) and Q11 determines one of its disclosure obligations. Writing it before those
answers would produce a plan that is wrong on arrival, and would improvise past exactly the kind of ambiguity
this check exists to catch.

**No code. No schema. No route. No WIRE-1 amendment. No frozen test relaxed. #25 still OPEN, unresolved.**

---

## 9. AMBIGUITY-CHECK — RE-RUN against the combined Q1–Q11 answer set

**Run**: 2026-07-25 · **Result**: ⚠️ **STILL NOT CLEAN — 1 MATERIAL FINDING → SURFACE-AND-STOP at Q12–Q13.**
3 checks confirmed clean. **The relaxation design was NOT written.**

⚑ **The finding is a correction to my own §8 arithmetic, found by re-verifying it rather than trusting it.** The
Q10 answer ratified *"seven across three"* with a specific enumeration. **The count is close but the MEMBERSHIP
is wrong**: it includes an assertion that needs **no** relaxation and omits **two** that do. Since the entire
content of a relaxation plan is *"what should each assertion assert instead"*, wrong membership makes the plan
wrong. The Q10 answer explicitly required *"cite the exact assertions and units, don't silently absorb the
difference"* — so this is surfaced, not absorbed.

---

### ✅ Confirmed CLEAN — Q9(a)'s mechanics

* **No collision with U24's guard.** `assert_no_collision_with_database()` (`case_lifecycle/migrate.py:60-68`)
  intersects U24's filenames with U15's, read **live**. U24 holds `0001_case_lifecycle.sql`; adding
  `0003_auth.sql` to U15 produces an empty intersection. **Guard passes.**
* **Ordering is favourable, not merely acceptable.** `0003_auth.sql` applies **after** `0002_grants.sql`, so the
  new tables are created **after** the two audit roles exist and receive **no grant** — landing them
  **owner-only by default**, which is exactly the posture Q2 asked for and precisely
  **CORE-RATIONALE-20**'s established reasoning for `app_user`. The forward-only ordering delivers the intended
  security posture **by construction** rather than by an added statement.
* **Auto-discovery works.** `migration_runner.py:69` globs `[0-9][0-9][0-9][0-9]_*.sql`, so `0003_auth.sql` is
  picked up by the existing `MigrationRunner` — **no `backend/scripts/run_migrations.py` edit**, which is the
  whole point of Q9(a).

### ✅ Confirmed CLEAN — Q11(c) is test-neutral

**No test anywhere under `backend/` reads `requirements.md` or `execution-plan.md`** (repo-wide scan: zero hits).
Editing `requirements.md` §10 to record the narrowing therefore cannot break a suite. The only doc-reading
governance tests in the build are U16's (`.env.example`, `.gitignore`) and U23's (`deploy/README.md` marker
tokens) — none touches a DISCOVER artifact.

### ⚑ DISCLOSED evidentiary limit — one of the three U15 assertions cannot be observed here

`test_migration_apply.py:56` sits inside `test_migration_sequence_is_forward_only_and_idempotent`, which takes the
`migrated_engine` fixture — and `backend/database/tests/conftest.py:41-42` reads:

```python
if not _docker_available():
    pytest.skip("Docker unavailable — database integration tests run in CI")
```

**So it SKIPS in this environment and would fail only in CI.** The other two U15 assertions
(`test_migration_runner.py:75`, `test_migration_checksum.py:114`) are **pure file reads and DO run locally**.
Recorded on the **#8 precedent** (*"written but unexecuted here; CI-gated"*): the relaxation pass can verify two
of three locally and must state plainly that the third is **CI-only**, never claiming local green as proof.

---

### ⛔ MATERIAL — the §8 membership is wrong: it is **8 across 3**, and two items are DESIGN CONSTRAINTS, not relaxations

Re-read of `backend/app/tests/test_no_write_route.py:105-131` shows the composition root holds **THREE**
route-surface assertions, not the one §2 named:

| Assertion | Location | Breaks on a `POST /login`? |
|---|---|---|
| `test_the_route_table_has_exactly_one_non_get_route` | `:107` — `assert non_get == [("/recommendations/{recommendation_id}/commit", "POST")]` | ✅ **YES** — a second non-GET |
| `test_every_other_route_is_read_only` | `:116` — loops **every** route except the commit POST, `assert methods <= {"GET", "HEAD"}` | ✅ **YES** — and **twice**, for `/login` and `/logout` |
| `test_the_seven_wire1_routes_are_the_whole_surface` | `:122` — `assert set(route_table()) == {…seven paths…}` | ✅ **YES** — any new path |
| `test_no_route_writes_directly_only_commit_does` (**A-4**) | `:239` — `.insert(`/`.atomic(` absent under `backend/app/`; `.commit(` only in `not_wired.py` | ⛔ **NO — it PASSES**, provided the credential/session stores live **outside** `backend/app/` |

**Corrected ledger:**

| Unit | Assertions needing relaxation | Which |
|---|--:|---|
| **U23 `deploy-config`** | **2** | `test_routes.py:36` (route-table equality) · `:41` (route-file name set) |
| **Composition root** | **3** | `test_no_write_route.py:107` · **`:116`** · **`:122`** |
| **U15 `database`** | **3** | `test_migration_runner.py:75` · `test_migration_checksum.py:114` · `test_migration_apply.py:56` *(CI-only)* — plus the `checksums.json` manifest entry (an artifact, not a test) |
| **TOTAL** | **8 across 3 units** | |

**And TWO items need a binding DESIGN CONSTRAINT instead of a relaxation** — strictly better, because the
invariant survives intact:

* **`test_no_write_route.py:239` (A-4)** — keeps asserting *"every write goes through the frozen
  `DecisionCommitService`"* **if and only if** the credential and session stores live **outside** `backend/app/`
  (the `PostgresCaseStore` pattern: U24 owns its store in `backend/case_lifecycle/`, and the composition root only
  injects it). **Relaxing A-4 would weaken the composition root's stated architectural guarantee for no benefit.**
* **`frontend/src/app/__tests__/app.test.jsx:261`** — keeps asserting the exact seam-key set **if and only if**
  the login client follows `sessionClient.js`'s non-seam precedent (*"a one-shot read, not a unit seam"*).

**Net difference from the ratified enumeration**: **+`:116`, +`:122`** (both need relaxation, both omitted);
**−A-4** (needs none, was included). Count moves **7 → 8**; units unchanged at **3**. → **Q12**, **Q13**.

---

## 10. SURFACED — Q12, Q13 (blank; nothing proceeds until answered)

### Q12 — Ratify the corrected membership, and decide A-4's disposition

* **(a) — Relaxation scope = 8 assertions across 3 units** (the ledger above), **and A-4 (`:239`) is PRESERVED
  UNCHANGED**, enforced by a binding design constraint: **the `user_credential` and `user_session` stores are
  authored outside `backend/app/`** (their own package, injected at the composition root, exactly as
  `PostgresCaseStore` is). §2, §8 and register #25 are corrected by supersession to **8-across-3** with the exact
  citations.
* **(b) — Relaxation scope = 9 across 3**, relaxing A-4 as well, permitting stores under `backend/app/`.
* **(c) — Keep the ratified 7-across-3 enumeration** as answered, treating my correction as out of scope.
  ⛔ Recorded for completeness only: `:116` and `:122` **will fail** regardless of what any plan says, so the
  relaxation pass would land red.

**Recommendation (grounded): (a).** `:116` and `:122` are not optional — they fail on contact with a `POST` route
whatever is written down, so they must be in scope or the pass lands red. A-4 is the opposite case: it costs
**nothing** to keep, because the store-outside-`backend/app/` pattern is **already the build's established
shape** (U24's `PostgresCaseStore`), and keeping it means the composition root's *"every write goes through the
frozen `DecisionCommitService`"* guarantee survives this work **completely intact** — a strictly better outcome
than relaxing it. ⚑ **Relax only what growth genuinely requires; preserve by design whatever can be preserved.**

**[Answer]**: (a) — ratify the corrected 8-across-3 membership, with A-4 preserved (not relaxed) via the design constraint that any new credential/session store is authored outside backend/app/, following the existing U24 PostgresCaseStore pattern. Cite this explicitly in both the relaxation design and the corrected register/plan supersession — the relaxation scope is 8 assertions across 3 units, of which 1 (A-4) is preserved by construction rather than weakened.

---

### Q13 — `app.test.jsx:261`'s seam-key set: relax, or preserve by design constraint?

* **(a) — Preserve unchanged**; bind the login client to `sessionClient.js`'s non-seam pattern (its own module,
  calling the injected transport directly, not registered in `createSeams`). ✅ Zero frontend assertions enter the
  relaxation pass; the login client sits beside `sessionClient.js`, which is **the same surface** (identity) and
  the exact precedent.
* **(b) — Relax it** to admit a sixth seam key, adding a **fourth unit** (the frontend) to the relaxation pass.

**Recommendation (grounded): (a).** `sessionClient.js` is not a loose analogy — it is the identity client for
**this very surface**, already built, already exempt from `createSeams` by explicit design, with its reason
stated in its own header. A login client is the same kind of thing: a one-shot handshake, not a per-unit data
seam. Choosing (a) keeps the relaxation pass at **three units** instead of four and leaves the frontend suite's
exact-set guard fully intact. ⚑ Same principle as Q12: **preserve by design what does not need relaxing.**

**[Answer]**: (a) — preserve app.test.jsx:261's exact seam-key set via sessionClient.js's non-seam precedent; the login client is a one-shot read like session resolution, not a registered seam. This keeps the relaxation pass at three units, not four.

---

**STOPPED — SURFACE-AND-STOP at Q12–Q13.** **The standalone frozen-assertion relaxation design has NOT been
written**: Q12 fixes its membership (8 or 9 assertions) and Q13 fixes whether it spans three units or four.
⚑ **Q1–Q11 remain answered and stand unchanged** — nothing above revisits a settled decision; this is a
correction to *my own* §8 enumeration, surfaced rather than absorbed, exactly as the Q10 answer required.

**No code. No schema. No route. No WIRE-1 amendment. No frozen test relaxed. #25 still OPEN, unresolved.**

---

## 11. AMBIGUITY-CHECK — FINAL RE-RUN against the complete Q1–Q13 answer set

**Run**: 2026-07-25 · **Result**: ✅ **CLEAN.** The ratified **8-across-3** ledger is **CONFIRMED CORRECT** by a
**systematic sweep**, not by spot-checking the assertions I already knew about. The relaxation design is
therefore written — `guide-docs/build/plans/frozen-assertion-relaxation-plan.md`.

⚑ **Method changed deliberately.** The two prior rounds under-counted because each checked only the assertions
already in hand. This round instead enumerated **every exact-set / exact-count assertion in the repository** that
could be perturbed by the three changes this answer set implies — **+2 routes**, **+1 migration file**,
**+2 tables** — and classified each as *breaks* or *survives*, **with the reason**. Everything below was read,
not inferred.

### 11.1 CONFIRMED — the 8 that genuinely break (3 units)

| # | Unit | Assertion | Location | Why it breaks |
|--:|---|---|---|---|
| **R-1** | U23 | `test_route_table_equals_the_frozen_composition_root` | `deploy_config/tests/test_routes.py:36` | exact `(path, method)` set of 7 |
| **R-2** | U23 | `test_no_new_route_file_added_under_backend_app_by_u23` | `test_routes.py:41` (assert `:47`) | exact filename set of 4 |
| **R-3** | comp-root | `test_the_route_table_has_exactly_one_non_get_route` | `test_no_write_route.py:107` | a second and third non-GET |
| **R-4** | comp-root | `test_every_other_route_is_read_only` | `test_no_write_route.py:116` | fails **twice** — `/login`, `/logout` |
| **R-5** | comp-root | `test_the_seven_wire1_routes_are_the_whole_surface` | `test_no_write_route.py:122` | exact path set of 7 |
| **R-6** | U15 | `test_migration_files_are_ordered` | `database/tests/test_migration_runner.py:75` | exact ordered list of 2 |
| **R-7** | U15 | `test_compute_checksums_over_committed_files` | `test_migration_checksum.py:114` | exact manifest key set of 2 |
| **R-8** | U15 | `test_migration_sequence_is_forward_only_and_idempotent` | `test_migration_apply.py:56` | exact applied set of 2 — ⚑ **Docker-gated, CI-ONLY here** |

**Plus one artifact, not a test**: `backend/database/migrations/checksums.json` gains a third entry.

### 11.2 CONFIRMED — the 2 PRESERVED by design constraint (Q12a / Q13a)

| Item | Location | Preserved because |
|---|---|---|
| **A-4** | `test_no_write_route.py:239` (+ its `:258` sub-assertion) | the credential/session stores are authored **outside `backend/app/`** (U24 `PostgresCaseStore` pattern), so `.insert(`/`.atomic(` never appear under `backend/app/` and `.commit(` stays sole-to-`not_wired.py` |
| **seam keys** | `frontend/src/app/__tests__/app.test.jsx:261` | the login client follows `sessionClient.js`'s **non-seam** precedent — *"a one-shot read, not a unit seam"* |

⚑ **Q12(a)'s constraint independently verified as safe**, which was not previously checked: a new
`backend/<auth-package>/` does **not** perturb `test_frozen_untouched.py`. Its `PRODUCTION_FILES` is
`APP_ROOT.rglob("*.py")` (`:16`) — **scoped to `backend/app` only** — so `owned == {"app"}` (`:69`) is unaffected;
and the new package is not in the hardcoded `FROZEN_UNITS` set, so
`test_no_frozen_unit_imports_the_composition_root` does not scan it. **The constraint is not merely
well-motivated — it is mechanically clean.**

### 11.3 SWEPT AND CONFIRMED SURVIVING — the near-misses, with reasons

These were checked **because they looked like they might break**. None does. Recorded so a future pass need not
re-derive them:

| Candidate | Location | Survives because |
|---|---|---|
| `test_apply_from_empty_created_the_three_tables` | `test_migration_apply.py:37` | uses **`<=` (subset)**, not `==` — 5 tables still contain the 3 |
| `test_rulebook_registry_table_is_absent` | `test_migration_apply.py:89` | its own comment: *"Targeted absence (**NOT a closed-world check**)"* — matches only names containing `rulebook` |
| `test_audit_tables_have_their_expected_columns` | `test_migration_apply.py:42` | names its three tables explicitly; `app_user`'s columns are **unchanged** (Q2(a) puts credentials in a **new table**, C-A) |
| `test_frozen_untouched.py` scans | `:43-56` | scan for `CREATE TABLE` / `__tablename__` / `declarative_base` / `sa.Table(` in `backend/app/` — a route module carries none |
| U23's other 11 test files | `test_boot/build/doc/format/freetier/governance/scope/sec3` | all **offender-list (`== []`)** or **subset (`<=`)** form — none enumerates routes or migrations |
| frontend exact-sets other than `:261` | `app.test.jsx:266`, and every other `toEqual([])` | `:266` asserts `seams.history`'s keys (untouched); the rest are offender lists |
| advisory-vocabulary lint | `shell/copy/forbiddenTerms.js` | forbidden tokens are `DECLINE` / `decision` / `approved` / `declined` — **verdict** language. ⚑ Cheap binding note: login copy must avoid them (*"your sign-in was **declined**"* would violate; *"Sign in failed"* does not) |
| U24 collision guard | `case_lifecycle/migrate.py:60-68` | live filename intersection; `0003_auth.sql` ∩ `0001_case_lifecycle.sql` = ∅ |
| `.env.example` ↔ `Settings` drift guard | `secrets_config/tests/test_governance.py:92-94` | Q5(b) adds **no** `Settings` field (C-B avoided) |
| doc-reading governance tests | U16 (`.gitignore`, `.env.example`), U23 (`deploy/README.md`) | **no test anywhere reads `requirements.md` or `execution-plan.md`** — Q11(c)'s edit is test-neutral |

### 11.4 Verdict

**CLEAN. No further ambiguity surfaced.** The ratified ledger — **8 assertions across 3 units, of which A-4 is
preserved by construction rather than weakened, and one (R-8) is verifiable only in CI** — is confirmed against
disk. Proceeding to the standalone relaxation design, per Q8(c).

---

## 12. ⚑ SUPERSESSION — §2's and §8's blocker figures are CORRECTED

**This section supersedes §2's table and §8's Q10 framing. Both are preserved verbatim above as the historical
record of what was believed when each was written; neither is rewritten in place** (the standing
supersede-not-rewrite discipline).

| Stated where | Superseded figure | ⚑ Ratified figure (Q12a) |
|---|---|---|
| **§2** ("THE STRUCTURAL BLOCKER") | *"four frozen assertions, across two units"* | **8 assertions across 3 units** |
| **§8 Q10** | *"seven across three (U23's A-1/A-2, the composition root's A-3/A-4, U15's three)"* | **8 across 3** — membership corrected: **+`:116`, +`:122`, −A-4** |
| **Register #25**, *"Structural blocker"* row | *"four frozen assertions across two units"* | **8 across 3** — superseded in `BUILD-COMPLETION-REPORT.md` |

**The ratified statement, to be used verbatim from here on:**

> **The relaxation scope is 8 assertions across 3 units — U23 (2: `test_routes.py:36`, `:41`), the composition
> root (3: `test_no_write_route.py:107`, `:116`, `:122`), and U15 `database` (3:
> `test_migration_runner.py:75`, `test_migration_checksum.py:114`, `test_migration_apply.py:56` — the last
> CI-only), plus a `checksums.json` manifest entry. TWO further items are PRESERVED BY DESIGN CONSTRAINT rather
> than weakened: `test_no_write_route.py:239` (A-4), via authoring the credential/session stores OUTSIDE
> `backend/app/` on the U24 `PostgresCaseStore` pattern; and `frontend/src/app/__tests__/app.test.jsx:261`, via
> the `sessionClient.js` non-seam precedent.**

⚑ **Recorded as a disclosed process finding** (the #20 directed-check / #19-vacuous-fixture precedent): **this
plan's own §2 under-counted twice** — first at 4, then at 7-with-wrong-membership — and **both errors were caught
by the mandatory ambiguity-check, not by the plan's own ground-truth pass.** The first under-count omitted an
entire unit (U15); the second omitted two assertions in a file it had already read. The fix that worked was
**changing the method** (§11's exhaustive sweep by change-type) rather than re-checking the same list harder.
**Further evidence the ambiguity-check earns its place**, and a caution for future passes: *a ground-truth pass
that enumerates what it already knows about is not a sweep.*

**STOPPED — Q1–Q13 all answered, ambiguity-check CLEAN, supersession recorded. Continues in
`guide-docs/build/plans/frozen-assertion-relaxation-plan.md`, which stops at its own gate.**
