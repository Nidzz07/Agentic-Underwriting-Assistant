# Frozen-Assertion Relaxation — CODE-GENERATION PLAN

**Stage**: POST-BUILD → the execution plan for `frozen-assertion-relaxation-plan.md` (design approved; Q1(c) /
Q2(a) / Q3(a) answered; ambiguity-check CLEAN).
**Status**: 🟡 **PLAN ONLY — NOTHING EXECUTED. No test edited, no assertion relaxed, no code generated.**
Stopped at the code-gen plan-file gate.
**Date**: 2026-07-25T10:42:13Z
**Scope**: **8 assertions across 3 units** + **3 renames** + **1 shared inventory (duplicated, cross-checked)**.
**A-4 and `app.test.jsx:261` are PRESERVED BY CONSTRUCTION and are NOT touched by this plan.**

---

## 0. What this document is and is not

* **IS**: the ordered, TDD-structured execution plan — explicit BEFORE/AFTER for every assertion changed or
  renamed, predicted test-count deltas stated **in advance**, and named stop-gates.
* **IS NOT**: the execution. **Nothing here has been run.**
* **IS NOT**: the login/signup code-gen plan. That is a separate, later, separately-approved pass.

---

## 1. ⚑ THE SEQUENCING FINDING — the relaxed assertions ARE the RED phase

This surfaced while ordering the work and **changes the shape of the pass**, so it leads.

`login-signup-plan.md` **Q8(c)** requires the relaxation be **applied as step 0 of the login/signup code-gen
pass**, so the assertions are never weakened while nothing depends on the weakening. Ordering the work exposes a
consequence Q8(c) did not spell out:

> **Six of the eight assertions cannot be flipped and left green on their own.** Changing `_EXPECTED` to nine
> routes while only seven exist makes the assertion **fail** — correctly. **The relaxed assertion *is* the failing
> test that drives the login routes into existence.** That is not an obstacle; it is textbook RED-before-GREEN,
> and it means the relaxation and the routes belong in **one** RED→GREEN cycle.

**Therefore the work splits into two phases, and the split is load-bearing:**

| Phase | Content | Suite state | Executed when |
|---|---|---|---|
| **A — preparatory** | 3 renames · docstring supersessions · the shared inventory (both copies) · cross-check + 2 non-vacuity tests · R-3's **split** (allowlist half still asserting today's single non-GET) | ✅ **GREEN throughout** — no expected value changes | **Step 0** of the login pass. ⚑ Also **standalone-safe** if ever wanted separately |
| **B — the flip** | The 8 expected-value changes (7 routes → 9; 2 migrations → 3) | 🔴 **RED on flip, GREEN when the login pass's routes + `0003_auth.sql` land** | **Inside** the login pass, immediately before the code that satisfies them |

⚑ **Phase A alone fully satisfies Q8(c)'s intent**: it is the entire structural change — the inventory, the
cross-check, the split, the renames — and **weakens nothing**, because every expected value still describes
today's system. **Only Phase B weakens anything, and it is inseparable from the code that re-justifies it.**

---

## 2. Explicit BEFORE / AFTER — every assertion changed or renamed

### 2.1 The shared inventory (NEW artifact, Phase A, Q1(c))

Two byte-equivalent copies, each a module-level literal with a per-entry justification comment:

* `backend/app/tests/_route_inventory.py` — **authoritative** (the composition root declares the routes)
* `backend/deploy_config/tests/_route_inventory.py` — **mirror** (deployment verification)

Content: the **nine** `(path, method)` pairs — WIRE-1's seven plus `("/login", "post")` and `("/logout", "post")`
— **plus** a separate `NON_GET_ALLOWLIST` of the three non-GET entries, each carrying a comment naming **why** it
is permitted to be non-GET.

⚑ **In Phase A both copies declare only today's SEVEN.** The two auth entries are added in **Phase B**. This is
what keeps Phase A green.

### 2.2 Cross-check (NEW, Phase A) — `backend/app/tests/test_route_inventory_sync.py`

| Aspect | Specification (from the design's §8 check (i)) |
|---|---|
| Compares | Both `_route_inventory.py` copies |
| How | Reads both **as text**, extracts each literal via `ast` — **never `import`**, never raw-text diff |
| Granularity | Set of `(path, method)` pairs **+ a duplicate check on each copy** (`len(list) == len(set)`) so a duplicate cannot mask a missing entry |
| On drift | **Fails loudly** — message names **both absolute paths** and the symmetric difference **in both directions** (`only_in_app`, `only_in_deploy_config`) |
| Non-vacuity | `test_detector_flags_a_synthetic_inventory_drift` — feeds two deliberately-divergent literals, asserts the difference is reported |

### 2.3 R-1 · `backend/deploy_config/tests/test_routes.py:36`

```
BEFORE  _EXPECTED = { …7 literal (path, method) tuples… }
        def test_route_table_equals_the_frozen_composition_root():
            assert _route_set(create_app().openapi()["paths"]) == _EXPECTED

AFTER   from backend.deploy_config.tests._route_inventory import ROUTE_INVENTORY
        def test_route_table_equals_the_declared_route_inventory():
            assert _route_set(create_app().openapi()["paths"]) == set(ROUTE_INVENTORY)
```
**Comparison unchanged (exact-set equality).** Only the literal's home moves.
**Kept**: `test_detector_flags_a_synthetic_extra_route` (`:49`), re-pointed at the inventory.

### 2.4 R-2 · `backend/deploy_config/tests/test_routes.py:41` — **RENAMED (Q2a)**

```
BEFORE  def test_no_new_route_file_added_under_backend_app_by_u23():
            assert route_files == {"__init__.py", "session.py", "decisions.py", "not_wired.py"}

AFTER   def test_route_modules_are_exactly_the_declared_inventory():
            """... ⚑ RENAMED from test_no_new_route_file_added_under_backend_app_by_u23.
            The old name made a PROVENANCE claim ("U23 adds none") while the assertion is a
            directory-wide exact-set guard that fires on ANY author's addition — intent and
            implementation diverged. Renamed rather than left stale: register #13 is an open item
            whose entire content is the cost of exactly that divergence. Old name recorded here,
            not erased."""
            assert route_files == set(ROUTE_MODULE_INVENTORY)
```
**Phase B** extends `ROUTE_MODULE_INVENTORY` by the one auth module.

### 2.5 R-3 · `backend/app/tests/test_no_write_route.py:107` — **RENAMED + SPLIT (Q2a, Q3a)**

```
BEFORE  def test_the_route_table_has_exactly_one_non_get_route(self):
            non_get = sorted(…)
            assert non_get == [("/recommendations/{recommendation_id}/commit", "POST")]

AFTER (a) def test_the_declared_non_get_routes_are_exactly_the_allowlist(self):
            """⚑ RENAMED from test_the_route_table_has_exactly_one_non_get_route. 'exactly one'
            became false when /login and /logout landed. ⚑ The old name's REAL content — that only
            one route changes underwriting state — is NOT lost: it moved to the test below, where it
            is asserted DIRECTLY instead of implied by a verb count. Old name recorded, not erased."""
            assert non_get == sorted(NON_GET_ALLOWLIST)

AFTER (b) def test_no_non_get_route_but_the_commit_reaches_domain_state(self):
            """⚑ NEW — the load-bearing half of the split (Q3-a, structural not conventional)."""
            for path, source in production_source().items():
                if path.name in DOMAIN_WRITE_MODULES:      # {"not_wired.py"}
                    continue
                code = strip_comments_and_docstrings(source)     # ⚑ MANDATORY — see below
                for seam in ("CasePipeline", "PostgresCaseStore", "PendingCommitContextProvider",
                             "PostgresAuditRepository", "DecisionCommitService"):
                    assert seam not in code, f"{path}: {seam}"
```
⚑ **`strip_comments_and_docstrings` is mandatory, not stylistic**: an auth handler will naturally *document* what
it does not touch (*"unlike R5, this reaches no domain state"*), and a raw scan would read that prose as a
violation. The file's existing assertions already use this helper.
⚑ **File-level, not handler-level** — following `:258`'s existing whole-module form, so a helper-function
indirection inside the auth module cannot evade it.
**New non-vacuity**: `test_detector_flags_a_synthetic_domain_seam_reference`.

> ⚑ **Precise strength claim, restated here so it is not over-read.** `:258` and `:275` (**inside A-4, preserved
> unchanged**) already assert that `.commit(` callers and claim-method callers are `== {"not_wired.py"}`. So
> R-3(b)'s **new** content is the remaining seams (`CasePipeline`, case store, audit repositories). The net
> position: *"exactly one non-GET route reaches domain state"* becomes **asserted directly** rather than
> **implied by a verb count** — **stronger**, because a future route reaching domain state now fails an assertion
> **even if someone updated the allowlist**.

### 2.6 R-4 · `backend/app/tests/test_no_write_route.py:116`

```
BEFORE  if path == "/recommendations/{recommendation_id}/commit": continue
AFTER   if (path, method) in NON_GET_ALLOWLIST: continue      # skip-list now declared
```
Assertion (`methods <= {"GET","HEAD"}`) **unchanged**. No rename — the name stays true.

### 2.7 R-5 · `backend/app/tests/test_no_write_route.py:122` — **RENAMED (Q2a)**

```
BEFORE  def test_the_seven_wire1_routes_are_the_whole_surface(self):
            assert set(route_table()) == { …7 literal paths… }

AFTER   def test_the_declared_route_inventory_is_the_whole_surface(self):
            """⚑ RENAMED from test_the_seven_wire1_routes_are_the_whole_surface — 'seven' became
            false. ⚑ Also closes a PRE-EXISTING drift risk: this test and U23's test_routes.py
            hardcoded the same seven paths INDEPENDENTLY, with nothing forcing agreement. Both now
            read one inventory, cross-checked. Old name recorded, not erased."""
            assert set(route_table()) == {p for p, _ in ROUTE_INVENTORY}
```

### 2.8 R-6 / R-7 / R-8 · U15 `database` (Phase B only)

```
R-6  test_migration_runner.py:75
BEFORE  assert names == ["0001_initial_schema.sql", "0002_grants.sql"]
AFTER   assert names == ["0001_initial_schema.sql", "0002_grants.sql", "0003_auth.sql"]
        assert names == sorted(names)          # ⚑ UNTOUCHED — the real forward-only guard

R-7  test_migration_checksum.py:114
BEFORE  assert set(cs) == {"0001_initial_schema.sql", "0002_grants.sql"}
AFTER   assert set(cs) == {"0001_initial_schema.sql", "0002_grants.sql", "0003_auth.sql"}
        assert all(len(v) == 64 for v in cs.values())    # ⚑ UNTOUCHED

R-8  test_migration_apply.py:56          ⚑ Docker-gated → CI-ONLY here
BEFORE  assert applied == {"0001_initial_schema.sql", "0002_grants.sql"}
AFTER   assert applied == {"0001_initial_schema.sql", "0002_grants.sql", "0003_auth.sql"}
```
**Paired artifact**: `backend/database/migrations/checksums.json` gains a **third** entry.
⛔ **The two existing entries MUST remain byte-identical** — U15's frozen migrations are never re-hashed.
No renames in U15 — all three names stay accurate.

---

## 3. Predicted test-count deltas — stated IN ADVANCE

**Baseline (carried, not re-run)**: backend **1578 passed / 0 failed / 43 skipped / 5 errors / 99.87%** ·
frontend **687 / 137 / 0**.

### Phase A — predicted **1582 passed / 0 failed / 43 skipped / 5 errors / 99.87%**

| Change | Δ passed |
|---|--:|
| `test_no_non_get_route_but_the_commit_reaches_domain_state` (R-3b) | **+1** |
| `test_detector_flags_a_synthetic_domain_seam_reference` | **+1** |
| `test_the_two_route_inventories_are_identical` | **+1** |
| `test_detector_flags_a_synthetic_inventory_drift` | **+1** |
| 3 renames | **0** (renames never change counts) |
| R-1/R-2/R-4/R-5 literal relocation | **0** |
| **TOTAL** | **+4 → 1578 → 1582** |

**Skipped stays 43. Errors stay exactly 5** (same `audit_store` Docker-absence names).
**Coverage stays exactly 99.87%** — ⚑ verified from config, not assumed: `[tool.coverage.run] omit` includes
`"*/tests/*"`, so both inventory copies and all four new tests are **coverage-invisible**. Frontend **untouched,
not re-run**.

### Phase B — predicted **6 RED locally**, on flip, before the login code lands

| Assertion | On flip, routes/migration absent |
|---|---|
| R-1 (9 vs 7) · R-2 (5 vs 4) · R-3a (3 vs 1) · R-5 (9 vs 7) · R-6 (3 vs 2) · R-7 (3 vs 2) | 🔴 **RED — 6** |
| R-4 | ✅ green — the loop finds no violating route |
| R-8 | ⏭️ **SKIP** — Docker-gated |
| R-3b | ✅ green — no auth module yet (⚑ its non-vacuity companion is what keeps this honest) |

**All six go GREEN when the login pass lands the two routes + `0003_auth.sql` + the checksum entry.**
⛔ **R-8 can only be confirmed in CI. Local green is NOT proof for it and must never be reported as such (#8
precedent).**

---

## 4. TDD execution order

**Phase A** — each step ends green; stop if not.
1. **Step 0** — baseline: `pytest backend` must read **exactly 1578 / 0 / 43 / 5 / 99.87%**. Mismatch ⇒ **STOP**.
2. **Step 1** — author both `_route_inventory.py` copies (**seven entries**, matching today).
3. **Step 2** — **RED first**: write `test_the_two_route_inventories_are_identical` **+ its non-vacuity
   companion** against a *deliberately divergent* pair, watch it fail, then correct the copies → **GREEN**.
4. **Step 3** — R-1, R-5, R-4: re-point at the inventory. **Expected values unchanged** ⇒ green throughout.
5. **Step 4** — R-2: re-point at `ROUTE_MODULE_INVENTORY` (four entries) ⇒ green.
6. **Step 5** — **RED first**: R-3(b) + its non-vacuity companion, proven to fail against a synthetic
   domain-seam reference before passing against the real tree.
7. **Step 6** — R-3(a): rename + re-point at `NON_GET_ALLOWLIST` (one entry today) ⇒ green.
8. **Step 7** — the three renames' docstring supersessions (old name + why), then **full suite → expect
   1582 / 0 / 43 / 5 / 99.87%**. Any other number ⇒ **STOP**.

**Phase B** — executed **inside the login/signup code-gen pass**, not here.
9. **Step 8** — flip all 8 expected values (+2 route entries, +1 migration entry, +1 checksum entry).
   **Expect exactly the 6 REDs predicted in §3.** A different set ⇒ **STOP** (the prediction was wrong, which is
   itself the finding).
10. **Step 9** — the login pass's routes, module and migration land → all 6 GREEN; R-8 recorded **CI-only**.

---

## 5. Stop-gates

1. Step 0 baseline ≠ **1578 / 0 / 43 / 5 / 99.87%**.
2. Any test **other than the named ones** changes state, at any step.
3. A RED step fails for **any reason other than the predicted one**.
4. Phase A final count ≠ **1582**.
5. Phase B's RED set ≠ **exactly the 6 predicted**.
6. `errors` ever ≠ **5**, or `skipped` ever ≠ **43** (Phase A).
7. Either preserved item is touched — **A-4** (`:239`/`:258`/`:275`) or **`app.test.jsx:261`**. Touching either
   **invalidates the approved design** and requires re-authorization.

---

## 6. Holds

| Hold | Status |
|---|---|
| **Nothing executed; no test edited; no assertion relaxed** | ✅ This is a plan |
| **A-4 and `app.test.jsx:261` not touched** | ✅ Preserved by construction |
| No frozen-23-or-24 unit **internal** edited | ✅ Only **test** files are in scope, and only at execution |
| `backend/app/routes/` untouched; no route added | ✅ |
| `llm_client.py`, `backend/scripts/`, tier-B untouched | ✅ |
| WIRE-1 unamended | ✅ The §3 amendment is the login pass's own act |
| U15's `*.sql` and `checksums.json` untouched; no migration written | ✅ Phase B only, and the two existing hashes are never re-computed |
| U16's six-field `Settings` untouched | ✅ |
| `not_wired.py` not renamed (**#13 open**) | ✅ |
| `audit_store` Docker-guard gap untouched (5 stays 5) | ✅ |
| **No code generated · #25 stays OPEN · NO COMMIT** | ✅ |

---

## 7. What happens after approval

1. **Phase A** executes at **step 0 of the login/signup code-gen pass**, per Q8(c).
2. **Phase B** executes **within** that pass, immediately before the code that satisfies it.
3. The login/signup code-gen plan **must restate as hard gates** the two design constraints that keep A-4 and
   `app.test.jsx:261` preserved: **stores authored outside `backend/app/`**, and **the login client is not a
   registered seam**.
4. **This design is not "done" when approved** — only when applied and green, with **R-8 disclosed CI-only**.

---

**STOPPED AT THE CODE-GEN PLAN-FILE GATE.** Nothing executed. No test edited. No assertion relaxed. No route.
No migration. No code. **#25 still OPEN.**
