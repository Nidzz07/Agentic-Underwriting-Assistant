# Frozen-Assertion Relaxation — DESIGN PLAN

**Stage**: POST-BUILD → a **standalone, separately-authorized** architecture-invariant change, per
**`login-signup-plan.md` Q8(c)**.
**Status**: 🟡 **DESIGN ONLY — NO TEST EDITED, NO ASSERTION RELAXED, NO CODE GENERATED.** Stopped at the
plan-file gate.
**Date**: 2026-07-25T10:42:13Z
**Scope, ratified at `login-signup-plan.md` Q12(a)/Q13(a)**: **8 assertions across 3 units**, of which **A-4 and
the frontend seam-key set are PRESERVED BY CONSTRUCTION, not weakened.**
**Precedents this pass follows**: **#13**'s matched-pair ruling (*"the rename and the test relaxation are a
MATCHED PAIR requiring their own authorization; neither half is valid alone"*) and **U24's three reopenings**,
each authorized separately and logged **before** any code.

---

## 0. What this document is and is not

* **IS**: the design for relaxing eight frozen assertions — **what each should assert instead**, such that
  **unreviewed route or write-path growth is still caught.**
* **IS NOT**: the login/signup code-gen plan. **Nothing here authorizes writing a route, a migration, a store, or
  a UI.** Per Q8(c) this design is **approved standalone and APPLIED as step 0 of the login/signup code-gen
  pass** — so no assertion is ever weakened while nothing depends on the weakening.
* **IS NOT** applied. **Every one of the eight assertions is untouched on disk right now.**

---

## 1. The governing principle

> **The strength of these guards comes from EXACT-SET EQUALITY, not from the literal being inline.**

Every assertion in scope works the same way: it compares a live-introspected set against a hardcoded literal.
Growth is caught because the comparison is **equality**, not because the literal is buried in a test body.

So the relaxation is **not** "loosen the comparison." It is:

> **Move each literal into ONE named, documented inventory, and keep the comparison at exact equality.**

Consequences, and they are the whole point:

* Adding a route/migration **still fails** every relevant assertion until the inventory is updated.
* Updating the inventory is a **one-line diff in a named, greppable place with a stated reason per entry** —
  visible in review, impossible to do by accident.
* **Growth becomes reviewable rather than either forbidden or silent.** That is exactly the property #13 says a
  matched pair must preserve.

⚑ **Two assertions get STRONGER, not weaker** (§3, R-3 and R-5). This is stated as a claim to be verified at the
gate, not as reassurance.

---

## 2. What is NOT relaxed — preserved by construction

| Item | Location | Binding design constraint that preserves it |
|---|---|---|
| **A-4** — *"every write goes through the frozen `DecisionCommitService`"* | `backend/app/tests/test_no_write_route.py:239` (+ `:258`) | ⚑ **The `user_credential` and `user_session` stores MUST be authored OUTSIDE `backend/app/`** — their own package, injected at the composition root, exactly as U24's `PostgresCaseStore` is. Then `.insert(` / `.atomic(` never appear under `backend/app/`, and `.commit(` stays sole-to-`not_wired.py`. |
| **seam-key exact set** | `frontend/src/app/__tests__/app.test.jsx:261` | ⚑ **The login client MUST follow `sessionClient.js`'s non-seam pattern** — its own module calling the injected transport directly, **not** registered in `createSeams`. |

**Verified mechanically safe** (`login-signup-plan.md` §11.2): a new `backend/<auth-package>/` does not perturb
`test_frozen_untouched.py` — its `PRODUCTION_FILES` is `APP_ROOT.rglob("*.py")` (`:16`), **scoped to
`backend/app` only**, so `owned == {"app"}` (`:69`) is unaffected; and the package is not in the hardcoded
`FROZEN_UNITS` set, so the import-direction test does not scan it.

> ⚑ **These two constraints are load-bearing, not stylistic.** If the code-gen pass violates either, the
> corresponding assertion fails and **this design is invalidated** — the relaxation scope would become 9-across-3
> or 9-across-4, requiring re-authorization. **They must be restated as hard gates in the code-gen plan.**

---

## 3. The eight relaxations — what each should assert instead

### 3.1 The shared inventory (the one new artifact this design introduces)

A single declared route inventory, authored **once**, consumed by **R-1, R-3, R-4, R-5**:

* **Content**: the nine `(path, method)` pairs — WIRE-1's seven, plus `("/login", "post")` and
  `("/logout", "post")`.
* **Per-entry justification**: each non-GET entry carries a comment naming **why** it is permitted to be non-GET.
* ⚑ **Location is a genuine open question** — see **Q1**. It cannot be `backend/app/` production code (that
  would make a test fixture into shipped code), and the two test trees that need it (`backend/app/tests/` and
  `backend/deploy_config/tests/`) are **owned by different units**.

⚑ **This alone removes a real, pre-existing drift risk**: today `test_routes.py:36` and
`test_no_write_route.py:122` hardcode **the same seven paths twice, independently**. Nothing forces them to agree.
Sharing one inventory means they cannot silently diverge — **a strengthening delivered as a side effect.**

---

### R-1 · `deploy_config/tests/test_routes.py:36` — `test_route_table_equals_the_frozen_composition_root`

| | |
|---|---|
| **Asserts today** | `_route_set(create_app().openapi()["paths"]) == _EXPECTED` where `_EXPECTED` is 7 literal tuples |
| **Should assert instead** | The identical equality, with `_EXPECTED` **derived from the shared inventory** (9 pairs) |
| **Growth still caught** | A tenth route fails immediately — the comparison is unchanged |
| **Strength delta** | **Neutral**, plus the anti-drift benefit above |
| **Non-vacuity** | `test_detector_flags_a_synthetic_extra_route` (`:49`) **already exists** and must be kept, re-pointed at the inventory |

---

### R-2 · `deploy_config/tests/test_routes.py:41` — `test_no_new_route_file_added_under_backend_app_by_u23`

| | |
|---|---|
| **Asserts today** | `route_files == {"__init__.py", "session.py", "decisions.py", "not_wired.py"}` (assert at `:47`) |
| **Should assert instead** | Same equality, set extended to include the **one** new auth route module |
| **Growth still caught** | A sixth file fails |
| **Strength delta** | **Neutral** |
| ⚑ **Note** | The test's *name* says *"by u23"*, but it guards the whole directory. Its docstring must be updated to say the set is **the declared route-module inventory**, not *"U23 adds none"* — otherwise the name misdescribes it (**exactly register #13's disease**: a name asserting something the file no longer means). **Renaming is proposed in Q2.** |

---

### R-3 · `backend/app/tests/test_no_write_route.py:107` — `test_the_route_table_has_exactly_one_non_get_route`

⚑ **The most important one. Do not replace it mechanically.**

| | |
|---|---|
| **Asserts today** | `non_get == [("/recommendations/{recommendation_id}/commit", "POST")]` |
| **The trap** | The naive fix — `non_get == [commit, login, logout]` — preserves equality but **destroys the invariant's meaning**. The test's real content is *"there is exactly one way to change underwriting state over HTTP."* Widening the list to three silently converts a **domain-write** invariant into a **verb-count** allowlist, and every future POST joins the list unchallenged. |
| **Should assert instead — SPLIT INTO TWO** | **(a) allowlist**: `non_get == <declared non-GET inventory>` — the mechanical half, still exact equality, each entry justified.<br>**(b) ⚑ the load-bearing half, newly separable**: **exactly one non-GET route reaches domain state.** Structurally: the `/login` and `/logout` handlers **must not** reference `DecisionCommitService`, `CasePipeline`, the case store, the audit repositories, or the claim methods — asserted by the same AST/source technique `:239` already uses. |
| **Growth still caught** | **More of it than before.** A new POST must be added to the inventory **and** proven not to touch domain state. A future route that quietly reached the commit path would fail **(b)** even if someone updated the inventory. |
| **Strength delta** | ⚑ **STRONGER.** Today the domain-write invariant is only *implied* by there being one POST. After the split it is **asserted directly and independently of HTTP verb counts** — which is the property that actually matters in a BFSI system. |
| **Rename** | to reflect the split (proposed in Q2) |

---

### R-4 · `backend/app/tests/test_no_write_route.py:116` — `test_every_other_route_is_read_only`

| | |
|---|---|
| **Asserts today** | For every route except the commit POST: `methods <= {"GET", "HEAD"}` |
| **Should assert instead** | Identical, with the skip-list = **the declared non-GET inventory** (3) instead of one inline path |
| **Growth still caught** | Any route not in the inventory that is non-GET fails |
| **Strength delta** | **Neutral** — same assertion, declared skip-list |

---

### R-5 · `backend/app/tests/test_no_write_route.py:122` — `test_the_seven_wire1_routes_are_the_whole_surface`

| | |
|---|---|
| **Asserts today** | `set(route_table()) == {…7 literal paths…}` |
| **Should assert instead** | Same equality over the **shared inventory**'s paths (9) |
| **Growth still caught** | Any tenth path fails |
| **Strength delta** | ⚑ **STRONGER** — shares one inventory with R-1 (see §3.1), closing the pre-existing two-independent-literals drift risk |
| **Rename** | `…_the_seven_wire1_routes_…` → a name naming the inventory, since "seven" becomes false (Q2) |

---

### R-6 · `database/tests/test_migration_runner.py:75` — `test_migration_files_are_ordered`

| | |
|---|---|
| **Asserts today** | `names == ["0001_initial_schema.sql", "0002_grants.sql"]` **and** `names == sorted(names)` |
| **Should assert instead** | `names == [… , "0003_auth.sql"]` — third element appended. ⚑ **The `sorted()` half is the actual forward-only guard and is NOT touched.** |
| **Growth still caught** | A `0004_*.sql` fails; out-of-order naming still fails `sorted()` |
| **Strength delta** | **Neutral** |

---

### R-7 · `database/tests/test_migration_checksum.py:114` — `test_compute_checksums_over_committed_files`

| | |
|---|---|
| **Asserts today** | `set(cs) == {"0001_initial_schema.sql", "0002_grants.sql"}` + all values 64-hex |
| **Should assert instead** | Same equality, third filename added; the 64-hex check untouched |
| **Paired artifact** | `backend/database/migrations/checksums.json` gains a **third entry** — the real sha256 of the new file. ⚑ **The two existing entries MUST remain byte-identical**; U15's frozen migrations are not re-hashed |
| **Growth still caught** | A fourth migration, or a drifted hash, fails |
| **Strength delta** | **Neutral** |

---

### R-8 · `database/tests/test_migration_apply.py:56` — inside `test_migration_sequence_is_forward_only_and_idempotent`

| | |
|---|---|
| **Asserts today** | `applied == {"0001_initial_schema.sql", "0002_grants.sql"}` |
| **Should assert instead** | Same equality, third filename added |
| ⚑ **EVIDENTIARY LIMIT** | It takes the `migrated_engine` fixture, and `database/tests/conftest.py:41-42` does `pytest.skip("Docker unavailable — database integration tests run in CI")`. **It SKIPS in this environment and can only be confirmed in CI.** |
| **How this is handled** | On the **#8 precedent**: the code-gen pass verifies **R-1…R-7 locally** and records **R-8 as CI-only, written-but-unexecuted-here**. ⛔ **Local green is NOT proof for R-8 and must never be reported as such.** |

---

## 4. What this design deliberately does NOT do

* **Does not touch WIRE-1's contract text.** The §3 route-table amendment is `login-signup-plan.md` Q7(a)'s, and
  is **its own act** at the code-gen gate — not smuggled in here.
* **Does not weaken A-4** or the frontend seam-key set (§2).
* **Does not relax `sorted()`**, the 64-hex checksum check, the `.insert(`/`.atomic(` prohibition, or the
  import-direction guard.
* **Does not touch the `audit_store` Docker-guard gap** — 5 errors stay exactly 5.
* **Does not rename `not_wired.py`** — register **#13 stays open**, untouched.
* **Applies nothing.** Per Q8(c), application is **step 0 of the login/signup code-gen pass**.

---

## 5. THE OPEN QUESTIONS

> **Instructions**: write your choice after each `[Answer]:` tag. **Nothing proceeds until every tag is filled.**

---

### Q1 — Where does the shared route inventory live?

R-1 sits in **U23's** test tree; R-3/R-4/R-5 sit in the **composition root's**. They must share one inventory or
the drift risk returns.

* **(a) — In `backend/deploy_config/tests/structural.py`** (U23's existing shared test-helper module), imported
  by the composition root's tests. ⛔ Makes a **frozen-23 unit's** helper a dependency of the composition root's
  tests — an import direction the build has otherwise kept one-way.
* **(b) — In a new module under `backend/app/tests/`**, imported by U23's tests. ⛔ Inverts it: U23's tests would
  import from the composition root's **test** tree, which `test_routes.py:55`
  (`test_routes_introspection_needs_no_frozen_test_tree`) **explicitly asserts against** —
  *"the scan imports only the PRODUCTION composition root, never `backend/app/tests`."* **This option breaks a
  ninth assertion and is therefore not viable as stated.**
* **(c) — Duplicated in both trees, with a cross-checking test** asserting the two copies are identical.
  ✅ No new import edge; the drift risk is closed by an **assertion** rather than by sharing.
* **(d) — Derived from WIRE-1's contract document** by parsing the pinned route table at test time.
  ✅ Single source of truth is the contract itself. ⛔ Introduces doc-parsing into the test path, and WIRE-1's
  markdown was never designed as a machine-readable interface.

**Recommendation (grounded): (c).** (b) is **eliminated by evidence** — it breaks `test_routes.py:55`, which
would make this a nine-assertion pass. (a) creates a frozen-unit→composition-root test dependency that the build
has deliberately avoided. (d) is architecturally attractive but turns a prose contract into a parsed interface,
which is a larger commitment than this pass should make unilaterally. **(c) achieves the anti-drift property with
zero new import edges and one small, honest test** — and that test is itself a useful guard, since it fails loudly
the moment someone updates one copy and not the other.

**[Answer]**: (c) — duplicate-with-cross-check, as the only surviving option given (b) is eliminated by test_routes.py:55's production-only import constraint. Ensure the cross-check itself is specified precisely: what compares the two copies, at what granularity, and what happens on drift (fails loudly, presumably) — don't leave that as an implied detail.

---

### Q2 — Are the misdescribing test names renamed, or left with corrected docstrings only?

After relaxation, three names assert things that are no longer true: `…has_exactly_one_non_get_route` (three),
`…the_seven_wire1_routes…` (nine), and `…added_under_backend_app_by_u23` (guards the directory, not U23).

* **(a) — Rename all three**, with the old names recorded in the plan and in each docstring.
  ✅ Removes the #13 disease at source. ⛔ Renames tests in **two units**, and any external reference by test id
  (CI selectors, docs) breaks.
* **(b) — Keep the names, correct the docstrings** to state precisely what is now asserted.
  ✅ Zero rename churn. ⛔ **Knowingly recreates register #13** — *"a maintainer tracing … lands in a file called
  `not_wired.py` that is entirely wired"* — in three new places.
* **(c) — Rename only R-3** (whose name becomes actively misleading about a **security** invariant), correct
  docstrings for R-2 and R-5.

**Recommendation (grounded): (a).** #13 is an **open register item** whose entire content is the cost of a name
that stopped being true, and its row states the rename and the test change are a matched pair *"requiring their
own authorization"* — this pass **is** such an authorization, so knowingly minting three more instances of the
same defect (option (b)) is the one outcome the register argues hardest against. The churn is bounded: a
repo-wide grep for each test id can confirm no external reference before renaming. ⚑ If churn is a concern, **(c)
is a defensible middle** — R-3's name is the one that misleads about a security property, which is the name most
worth fixing.

**[Answer]**: (a) — rename the three now-misdescribing test names to match what they actually assert post-relaxation, rather than leaving stale names that would repeat register #13's exact defect three more times. Use the same supersede-not-rewrite discipline for the rename's own documentation (record what the name was, why it changed) rather than a silent rename.

---

### Q3 — Is R-3's split enforced structurally, or by convention?

R-3(b) — *"exactly one non-GET route reaches domain state"* — is the strengthening this design claims.

* **(a) — Structurally**, by an AST/source assertion that the login/logout handlers reference none of
  `DecisionCommitService`, `CasePipeline`, the case store, the audit repositories, or the claim methods — the
  same technique `:239` and `:283` already use.
  ✅ The claim is **machine-checked**, so it cannot regress unnoticed. ⛔ One more structural test to maintain.
* **(b) — By convention**, documented in the docstring and reviewed at the gate.
  ⛔ Then the "STRONGER" claim in §3 is **not true**, and this design should stop claiming it.

**Recommendation (grounded): (a).** The entire justification for relaxing R-3 rather than mechanically widening
it is that the **domain-write invariant survives independently** of the verb count. If that survival is only
conventional, the relaxation is a **net weakening** wearing better language — and this build's standing rule is
that a claim must be *"proven at tier-U"* or stated as unproven. The technique already exists in the same file,
so the cost is small and the precedent is local. ⚑ **If (b) is chosen, §1's "two assertions get STRONGER" claim
must be struck from this plan** — I will not leave an unearned strength claim standing.

**[Answer]**: (a) — structural. The exactly-one-non-GET-domain-write invariant must be enforced by genuine code structure (e.g. an explicit, checkable marker on the route/handler, or a scan that traces to DecisionCommitService.commit() specifically), not by a convention that happens to hold today. If verifying this turns out to actually require (b) instead, don't quietly settle for it — strike the "STRONGER" claim from the plan as you said you would, and flag that reversal explicitly rather than let it pass unremarked.

---

## 6. Holds for this pass — verified, all currently upheld

| Hold | Status |
|---|---|
| **No assertion relaxed; no test edited** | ✅ All eight untouched on disk — this is a design, not an application |
| No frozen-23-or-24 unit internal edited | ✅ Untouched |
| `backend/app/routes/` untouched; no route added | ✅ Untouched |
| `backend/app/llm_client.py`, `backend/scripts/`, tier-B untouched | ✅ Untouched |
| WIRE-1's contract text **not amended** | ✅ Untouched — the §3 amendment is the code-gen pass's own act |
| U15's migrations + `checksums.json` untouched; **no migration written** | ✅ Untouched |
| U16's six-field `Settings` untouched | ✅ Untouched |
| `not_wired.py` not renamed (**#13 stays open**) | ✅ Untouched |
| `audit_store` Docker-guard gap untouched (5 stays 5) | ✅ Untouched |
| **No code generated** | ✅ Only `guide-docs/` written |
| **#25 stays OPEN** | ✅ Unresolved |

**Suites carried forward, NOT re-run**: backend **1578 / 0 / 43 / 5 / 99.87%**; frontend **687 / 137 / 0**.

---

## 7. What happens after the answers

1. Answers recorded verbatim in `audit.md`; embedded back into §5.
2. **This plan's own mandatory ambiguity-check** runs against the Q1–Q3 answer set — surface-and-stop if not
   clean. Named in advance: **(i)** does the chosen inventory location create an import edge any existing
   structural test forbids (`test_routes.py:55` is the known one); **(ii)** does any rename break an external
   reference (repo-wide grep per test id); **(iii)** does R-3(a)'s structural assertion collide with the
   docstring-stripping scanners already in that file.
3. **Then** the login/signup code-gen plan is written separately, applying this design as **step 0**, with the §2
   design constraints restated as hard gates.
4. **This design is not "done" when approved** — it is done when applied and green, with **R-8 disclosed as
   CI-only**.

---

**STOPPED AT THE PLAN-FILE GATE.** No test edited. No assertion relaxed. No route. No migration. No code.
**#25 still OPEN.**

---

## 8. AMBIGUITY-CHECK — run against the Q1–Q3 answer set

**Run**: 2026-07-25 · **Result**: ✅ **CLEAN — 3 directed checks, 3 folds, one PRECISION CORRECTION (not a
reversal).** The code-gen plan is written: `guide-docs/build/plans/frozen-assertion-relaxation-code-gen-plan.md`.

### ✅ Directed check (i) — does Q1(c)'s cross-check create a forbidden import edge? **CLEAN**

Two constraints were checked, both by reading the asserting code:

* **`test_routes.py:55`** (`test_routes_introspection_needs_no_frozen_test_tree`) parses **`__file__`** — it
  constrains **only `test_routes.py`'s own imports**, not U23's whole tree. A *different* file in
  `deploy_config/tests/` is outside its reach.
* **`test_scope.py:42`** iterates every `deploy_config` py file but forbids only
  `_FORBIDDEN_SCOPE_IMPORTS = {"langgraph", "mcp", "langfuse"}`. `backend.app.*` is not forbidden there.

**RELAX-Fold-1 — the cross-check reads both copies as TEXT, so the question does not arise.** Following
`structural.py`'s own established pattern (`sg.read(...)` + AST/`ast.literal_eval`, never `import`), the
cross-check opens both files by path and parses their inventory literal. **Reading a file is not importing it**,
so **zero new import edges are created** and neither constraint above is engaged even in principle. This is
strictly safer than the import-based form and needs no exception.

**⚑ Q1's answer explicitly required the cross-check be specified precisely, not left implied. Specified:**

| Aspect | Specification |
|---|---|
| **What compares** | One test, `test_the_two_route_inventories_are_identical`, living in **`backend/app/tests/`** — the composition root declares the routes, so it owns the authoritative copy; U23's is the deployment-verification mirror |
| **How** | Reads **both files as text** and extracts each inventory literal via `ast` — **never `import`**, never raw-text diff (so comments, ordering and formatting cannot cause a false failure) |
| **Granularity** | Compares the **set of `(path, method)` pairs**, **plus** an explicit **duplicate check on each copy** (`len(list) == len(set)`) — so a duplicated entry in one copy cannot silently mask a missing one under set comparison |
| **On drift** | **Fails loudly.** The assertion message names **both absolute file paths** and the **symmetric difference in both directions** (`only_in_app`, `only_in_deploy_config`), so the failure states exactly what diverged rather than "sets not equal" |
| **Non-vacuity** | Paired `test_detector_flags_a_synthetic_inventory_drift`, feeding the comparator two deliberately-divergent literals and asserting it reports the difference — so the cross-check cannot rot into a tautology |

### ✅ Directed check (ii) — do the Q2(a) renames break any external reference? **CLEAN**

Repo-wide grep for all three test ids across `*.py`, `*.md`, `*.yaml`, `*.yml`, `*.toml`, `*.cfg`:

* **Code**: only their own definitions. **No test, conftest, or helper references them by name.**
* **CI**: ⚑ **there is no `.github/workflows/` directory at all** — no pipeline selects tests by id.
* **Config**: `pyproject.toml` selects by `testpaths`/`--cov`, **never by test name**.
* **Docs**: `guide-docs/audit.md` and three plan files mention them — **historical records**, which under
  supersede-not-rewrite are **left unedited**.

**RELAX-Fold-2**: the renames break **zero** external references. Per Q2's instruction, each rename is documented
**supersede-not-rewrite style** — the new docstring records **the former name and why it changed**, so the
history is readable at the test rather than only in a plan.

### ✅ Directed check (iii) — does R-3(b)'s structural assertion collide with the docstring-stripping scanners? **CLEAN, with one binding constraint and one precision correction**

**RELAX-Fold-3 — the assertion MUST scan `strip_comments_and_docstrings(source)`, never raw source.**
`test_no_write_route.py` already applies that helper before every content assertion. A login handler would very
naturally *document* what it does not touch (*"unlike R5, this reaches no domain state"*) — and a **raw** scan
would read that prose as a violation. **Scanning stripped source is mandatory, and the plan says so.**

**⚑ PRECISION CORRECTION to §3's R-3 entry — a sharpening, NOT the reversal Q3 asked to be flagged.**
Q3(a) asked for structural enforcement and warned that if only convention were achievable, the *"STRONGER"* claim
must be struck. **Structural enforcement IS achievable — so the claim STANDS and nothing is struck.** But
re-reading the preserved assertions shows R-3(b)'s **genuinely new** content is **narrower** than §3 implied, and
that is stated rather than left flattering:

* `test_no_write_route.py:258` (**inside A-4, preserved unchanged**) already asserts `.commit(` callers
  `== {"not_wired.py"}` across **all** production files under `backend/app/`. So *"the auth module never calls the
  commit service"* is **already enforced** — by an assertion this pass does not touch.
* `:275` (**also preserved**) already asserts the claim-method callers `== {"not_wired.py"}`.
* **R-3(b)'s new content is therefore the remaining domain seams**: `CasePipeline`, the case store, and the audit
  repositories.

**The net position, stated precisely**: after the split, *"exactly one non-GET route reaches domain state"* is
**asserted directly and file-level** — by R-3(b) **together with** the preserved `:258`/`:275` — instead of being
**implied by a verb count**. That remains **stronger than what it replaces**, because a future route that reached
domain state would now fail an assertion **even if someone updated the non-GET allowlist**. The claim is kept;
its basis is now stated exactly.

**File-level, not handler-level** (a further consequence, worth pinning): the assertion follows `:258`'s existing
**whole-module** form rather than inspecting only the handler function body — so a helper-function indirection
inside the auth module **cannot evade it**.

### Verdict

**CLEAN.** No further ambiguity. Proceeding to the code-gen plan, which stops at its own gate.
