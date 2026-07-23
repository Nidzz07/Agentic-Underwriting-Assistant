# NFR Design Plan (Part 1) — `admin-cli` (U17)

**Phase / Stage**: BUILD → NFR Design, **Part 1 (Planning)** (plan-then-generate; numbered `[Answer]` tags — **full text + options on disk**)
**Loop position**: `admin-cli` (U17) — FD ✅ · NFR Requirements ✅ **APPROVED (Continue)** → **NFR Design Part 1 ← here.**
**Unit**: U17 `admin-cli` · **Date**: 2026-07-08 · **Depth**: **LIGHTER overall (CLI scaffolding) + FULL rigor on the two invariant-bearing mutations** (canonical-role sole gate — SEC-4; rulebook publish validate-then-append-only — FR-RULES-6/CON-DET-1) · Stories **US-ADMIN-1/2**.
**Status**: **RESOLVED — four `[Answer]` tags FILLED (all A, §7); ambiguity-check RUN 2026-07-08 → CLEAN (three realization folds ADMIN-NFRD-Fold-1/2/3, §8A — no genuine gap, no STOP); Part 2 GENERATED** (`nfr-design-patterns.md` + `logical-components.md`). This plan re-saved per the standing convention. STOPPED at the NFR-Design 2-option completion gate.

Built **ON** the frozen FD (BR-ADMIN-1..9, the module inventory, the injected-`Engine` seam, the sole-gate-vs-open-VARCHAR analysis) and the approved **NFR Requirements** (ten `NFR-ADMIN-*` targets, tiers **U/Integration**, the three **ADMIN-NFR-Folds**) — **re-opening none**. Each `NFR-ADMIN-*` target maps to a **named design pattern** + a **logical component**, at the rigor of the other units.

---

## 1. What NFR Design produces (Part 2 preview — NOT generated yet)
- `nfr-design-patterns.md` — the named patterns (each meeting its `NFR-ADMIN-*` target) + a validated **pattern-integration Mermaid** (7-rule + text alt) + a traceability table (no orphan).
- `logical-components.md` — the logical components (responsibility / ownership / reference-not-own check across all four consumed surfaces) + a **component→target coverage** table (no orphan) + a validated **component-relationship Mermaid** (7-rule + text alt) that makes the **RoleGate-before-AppUserWriter sequencing** (the sole-gate structural guarantee) **visually explicit**.

---

## 2. Pattern → target map (every `NFR-ADMIN-*` mapped; no orphan)

| Pattern | Meets target(s) | Mechanism (design, not code) |
|---|---|---|
| **P1 · ValidateThenAppendOnlyPublishPattern** | NFR-ADMIN-PUBLISH-1 + NFR-ADMIN-PUBVALID-1 | write `{version}.yaml` (`content_hash: ""`), **validate by load** via `build_rulebook`/`RulebookLoader` (the **sole** validator — schema + hash + declared-version), a **no-overwrite guard** refuses an existing version (append-only), failed validation leaves **no** file. |
| **P2 · PreConnectionRoleGatePattern** *(highest rigor)* | NFR-ADMIN-ROLEGATE-1 | a **RoleGate** component (distinct from the SQL writer) validates `role ∈ Role` **before any connection is acquired** (`connect()`/`begin()` — ADMIN-NFR-Fold-2); the writer **composes + invokes** the gate as its first step, so the gate **structurally cannot be bypassed** via the write path. Fault-injection (raw SQL, bypassing the writer) proves the open-VARCHAR DB is not a gate. |
| **P3 · ExplicitConflictDetectionPattern** | NFR-ADMIN-CREATE-1 + NFR-ADMIN-SETROLE-1 | create-user: INSERT relying on the DB PK/UNIQUE → catch the integrity violation → `UserWriteError` "already exists"; set-role: UPDATE → `rowcount == 0` → `UserWriteError` "no such user". **No upsert, no pre-SELECT** (atomic, race-free). |
| **P4 · StructuralGuardPattern** | NFR-ADMIN-REFNOTOWN-1 + NFR-ADMIN-NOSECRET-1 + NFR-ADMIN-SCOPE-1 | a stdlib-`ast` scan of `backend/admin_cli/` — no `database`/`auth_rbac` production import, no local hasher/rulebook-schema/DDL, no secret literal, no LLM/rule-eval/commit import — with a **non-vacuous self-test**. Mirrors the `corpus_generator`/`quality_gates` precedent (D11). |
| **P5 · TypedExceptionToExitCodePattern** | NFR-ADMIN-CLIERR-1 | `AdminCliError` base → `RulebookPublishError`/`UserWriteError`/`RoleValidationError`; the entrypoint maps typed errors → a **non-zero exit code + a no-secret stderr message**; success → exit 0 + a names-only status line. |
| **P6 · GovernanceAbsencePattern** *(no component)* | NFR-ADMIN-PROVIDER-DEFER-1 | a **documented absence** — no `set-provider` command and no provider-config store; the active provider stays a static composition-root value (Q3-B). |

**No orphan** — all ten `NFR-ADMIN-*` targets met (PUBLISH-1+PUBVALID-1→P1; ROLEGATE-1→P2; CREATE-1+SETROLE-1→P3; REFNOTOWN-1+NOSECRET-1+SCOPE-1→P4; CLIERR-1→P5; PROVIDER-DEFER-1→P6).

---

## 3. Logical components (responsibility · ownership · reference-not-own)

| Component | Responsibility | Owns / references |
|---|---|---|
| **C1 · ArgparseEntrypoint** | argparse root; routes `<subcommand>`; injects the `Engine`/rulebook-dir from the composition root; maps typed exceptions → exit code + no-secret message (via C5) | **owns**; no consumed-surface import |
| **C2 · RulebookPublisher** | write-then-validate-by-load-then-append-only publish (P1) | **owns**; **references** `build_rulebook`/`RulebookLoader` (call-only) |
| **C3 · RoleGate** | pre-connection canonical-role validation (P2) — the **sole gate**; **pure** (no DB), unit-covered | **owns**; **references** `auth_rbac.roles.Role` (call-only) |
| **C4 · AppUserWriter** | the two `app_user` operations (create/set-role) via the injected `Engine`; **composes C3 and invokes it first** (before `connect()`/`begin()`); explicit conflict/absence detection (P3). **Pure statement-build + result-interpretation counted; the SQL-exec shim omitted from unit coverage** (like `pg_repository.py`) | **owns**; **references** `database` `app_user` columns (schema owned by database; no CHECK added) |
| **C5 · ExceptionTaxonomy** | `AdminCliError` base + the three typed subclasses (P5) | **owns** |
| **C6 · StructuralGuard / test substrate** | the AST-scan guards (P4) + non-vacuous self-test; in `tests/` (not counted toward production coverage) | **owns**; scans `backend/admin_cli/` |

> **C3 RoleGate is a distinct component that C4 AppUserWriter composes and invokes as its first step** — this is what makes NFR-ADMIN-ROLEGATE-1's "sole gate, structurally un-bypassable" guarantee a **design property**, not just prose (subject to **Q1**).

---

## 4. Reference-not-own check (all four consumed surfaces — call-only, none edited)

| Surface | How consumed | By | Edited? |
|---|---|---|---|
| `rules_engine.loader.build_rulebook` / `RulebookLoader` | the sole publish validator, call-only | C2 | **No** |
| `auth_rbac.roles.Role` | the canonical set for the pre-write gate, call-only | C3 | **No** |
| `database` `app_user` (`user_id`/`subject`/`role` open VARCHAR) | parameterized INSERT/UPDATE via injected `Engine`; no schema/CHECK added | C4 | **No** |
| `secrets-config` `DATABASE_URL` (**indirect**) | the composition root builds the injected `Engine`; admin-cli reads no secret VALUE | C1 (injected) | **No** |

> **Verification/wrapper only** — `build_rulebook` is the sole rulebook validator; `Role` is the sole canonical set; database owns the `app_user` schema (no CHECK); no `database`/`auth_rbac` production import; no local hasher/rulebook-schema/DDL (P4 self-tested).

---

## 5. Component → target coverage (no orphan)

| Target | Component(s) | Pattern(s) |
|---|---|---|
| NFR-ADMIN-PUBLISH-1 | C2 | P1 |
| NFR-ADMIN-PUBVALID-1 | C2 | P1 |
| NFR-ADMIN-ROLEGATE-1 | C3 (+C4 composes it) | P2 |
| NFR-ADMIN-CREATE-1 | C4 | P3 |
| NFR-ADMIN-SETROLE-1 | C4 | P3 |
| NFR-ADMIN-REFNOTOWN-1 | C6 | P4 |
| NFR-ADMIN-NOSECRET-1 | C6 (+C1/C5 message discipline) | P4 |
| NFR-ADMIN-SCOPE-1 | C6 | P4 |
| NFR-ADMIN-CLIERR-1 | C5 (+C1) | P5 |
| NFR-ADMIN-PROVIDER-DEFER-1 | — (documented absence) | P6 |

All ten targets covered; no orphan. C3 (RoleGate) + C5 (ExceptionTaxonomy) are shared enablers.

---

## 6. Mermaid (generated + 7-rule-validated at Part 2 — consistent with the other units)
Two diagrams, each with a text alternative, produced in Part 2 (mirroring `corpus-generator`/`quality-gates`, which presented their Mermaids in the Part-2 artifacts):
- **pattern-integration** (in `nfr-design-patterns.md`) — entrypoint → publish/user-write flows → patterns.
- **component-relationship** (in `logical-components.md`) — C1..C6 wiring, with **C3 RoleGate strictly BEFORE C4 AppUserWriter's connection acquisition** made **visually explicit** (an edge `RoleGate → AppUserWriter connect/begin`, gate-first), so the sole-gate structural guarantee is shown, not just asserted.
Both validated against the 7 rules (alphanumeric node IDs, every label double-quoted, no forbidden characters, balanced blocks) before write, with a text alternative always included.

---

## 7. Clarifying questions (fill each `[Answer]` tag; last option = Other)

These decide **NFR-Design pattern/component realization** — they do **not** re-open the FD, the BR-ADMIN rules, the ten `NFR-ADMIN-*` targets, the five FD answers, or the six folds (three ADMIN-Fold + three ADMIN-NFR-Fold).

### Question 1 — RoleGate placement (the sole-gate structural guarantee) — P2 / C3 / C4
Where does the RoleGate live so it **structurally cannot be bypassed** by the write path?
A) **RoleGate is a distinct component that `AppUserWriter` composes and invokes as the FIRST line of each write method — before any `connect()`/`begin()`.** Any call through `AppUserWriter`'s public API therefore passes the gate (can't be bypassed); the entrypoint calls only `AppUserWriter`. The gate stays **pure** (unit-covered with the spy engine); the SQL-exec is the omitted shim. **Recommended** (this makes "sole gate" a design property, not prose).
B) **RoleGate is a separate entrypoint step** called before `AppUserWriter` (gate outside the writer) — cleaner separation, but a **direct** `AppUserWriter` call could bypass it (weaker guarantee).
C) Other.

[Answer]: A

### Question 2 — Explicit conflict/absence detection mechanism — P3 / C4
How are "already exists" (create) and "no such user" (set-role) detected — without upsert semantics?
A) **DB-constraint-driven, atomic, no pre-SELECT**: create-user INSERTs and **catches the integrity violation** (PK `user_id` / UNIQUE `subject`) → `UserWriteError` "already exists"; set-role UPDATEs and checks **`result.rowcount == 0`** → `UserWriteError` "no such user". One statement each, race-free. **Recommended.**
B) **Pre-SELECT existence check** then INSERT/UPDATE — a TOCTOU race + an extra round-trip; rejected.
C) Other.

[Answer]: A

### Question 3 — No-overwrite guard mechanism (append-only publish) — P1 / C2
How does the publisher refuse to overwrite an existing version?
A) **Check `{version}.yaml` existence BEFORE writing** and refuse (raise `RulebookPublishError`) if it exists — explicit, sufficient for an out-of-band single-operator CLI, and it never touches the existing file (the append-only-teeth test asserts byte-identity before/after). **Recommended.**
B) **Write to a temp file then rename with a no-clobber check** — more machinery than an out-of-band CLI needs.
C) Other.

[Answer]: A

### Question 4 — StructuralGuard location — P4 / C6
Where do the AST-scan guards live?
A) **One `StructuralGuard` in `tests/`** (an `ast`-scan module + `test_reference_not_own.py`-style tests covering REFNOTOWN-1/NOSECRET-1/SCOPE-1 + the PROVIDER-DEFER-1 absence + a **non-vacuous self-test**), mirroring the `corpus_generator`/`quality_gates` precedent; **not counted** toward production coverage (in `tests/`). **Recommended.**
B) **A production guard module** shipped in `backend/admin_cli/` — adds runtime code for a test-time concern; rejected.
C) Other.

[Answer]: A

---

## 8. Carried folds (referenced, not re-derived — the substrate NFR-Design builds on)
**ADMIN-Folds (FD):** ADMIN-Fold-1 (open-VARCHAR/no-CHECK → the pre-write `Role` gate is the SOLE enforcement) → **P2** · ADMIN-Fold-2 (validate-then-append-only publish) → **P1** · ADMIN-Fold-3 (provider-config deferred, no store) → **P6**.
**ADMIN-NFR-Folds (NFR-Req):** ADMIN-NFR-Fold-1 (fault-injection isolation — disposable testcontainers only) → **P2** integration proof · ADMIN-NFR-Fold-2 (spy asserts on `connect()`/`begin()`, not `.execute`, in SQLAlchemy 2.0) → **P2/C3/C4 sequencing** · ADMIN-NFR-Fold-3 (test-only `app_user` harness, SCOPE-1, reference-not-own) → **P3 integration substrate**.

## 8A. Ambiguity-check (RUN 2026-07-08 against the four filled answers + frozen FD + approved NFR-Req) — CLEAN
Ran on the three named checks; grounded on the four consumed surfaces re-read on disk (`loader.py`, `roles.py`, `0001_initial_schema.sql:51-57`, `settings.py`) + the `pg_repository.py` injected-Engine precedent + the SQLAlchemy 2.0 Engine API. **No genuine gap → no STOP.** Three realization folds embedded in `nfr-design-patterns.md` §5:
- **ADMIN-NFRD-Fold-1 (check i — RoleGate ordering is test-enforced).** The **spy-engine assertion that `connect()` and `begin()` are BOTH never called on a non-canonical role** is a structural reorder-guard: any future edit that acquired a connection before gating fails the regression test — enforcement is beyond code review. **Residual (accepted lighter-tier limit)**: exercised over the two Phase-1 write methods; a future third write method would need its own spy assertion (no per-method AST enforcement added — gold-plating for CLI-scaffolding scope).
- **ADMIN-NFRD-Fold-2 (check ii — generic "already exists" is accurate).** A generic "already exists" is truthful for both the PK `user_id` and the UNIQUE `subject` collision; CREATE-1(b) requires only an explicit error. Distinguishing which constraint fired is an **optional Code-Gen message-wording** choice (driver-specific/brittle), not an NFR-Design gap.
- **ADMIN-NFRD-Fold-3 (check iii — publish TOCTOU eliminated by atomic exclusive-create).** Q3-A ("check existence and refuse; never touch the existing file") is realized via **atomic exclusive-create** (`open(path, "x")` / `O_CREAT|O_EXCL`) — one race-free syscall, so the check-then-write TOCTOU window does not exist; existing file byte-identical (PUBLISH-1(b)). **Explicitly accepted scope**: single-operator out-of-band CLI, but the design does not *rely* on that for safety — a concurrent duplicate publish fails cleanly with `RulebookPublishError` rather than clobbering. (Rejected Q3-B temp-then-rename = strictly more machinery for the same guarantee.)

## 9. Settled items held (not re-opened)
The frozen FD + approved NFR-Req (BR-ADMIN-1..9, the ten `NFR-ADMIN-*` targets, the injected-`Engine` seam, the sole-gate analysis, the six folds) is the substrate — NFR-Design builds patterns/components **on** it. **Reference-not-own** — the four surfaces call-only, none edited; `build_rulebook` sole rulebook validator; `Role` sole canonical set; no schema/CHECK added. **Canonical-role sole gate** (SEC-4; RoleGate before `connect()`/`begin()`). **SEC-3** no secret VALUES. **Provider-config management deferred to P2.** **No new production dependency; no LLM; no rule-eval; no decision/commit; no admin UI; WIRE-1 untouched; tier-B NOT authorized; no other unit started.**

## 10. Next step (STOPPED at the NFR-Design 2-option gate) — DONE
Four `[Answer]` tags filled (all A, §7); ambiguity-check RUN → **CLEAN** (§8A, three ADMIN-NFRD-Folds); **Part 2 GENERATED** — `guide-docs/build/admin-cli/nfr-design/nfr-design-patterns.md` (P1–P6, pattern-integration Mermaid + text alt, traceability no-orphan, Security-Guardrails table) + `logical-components.md` (C1–C6, reference-not-own across all four surfaces verified on disk, component→target coverage no-orphan, component-relationship Mermaid + text alt with **RoleGate-before-connection as a visible edge** — the connection node's only inbound edge is from C3). This plan re-saved per the standing convention. **STOPPED at the standardized NFR-Design 2-option completion gate (1. Request Changes / 2. Continue to Next Stage — Infrastructure Design) — did NOT advance. WIRE-1 untouched; tier-B run NOT authorized; no other unit started.**
