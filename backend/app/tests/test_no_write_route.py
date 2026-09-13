"""INT-FAITHFUL-1 — **every ``audit_record`` write goes through the frozen ``DecisionCommitService``.**

⚑ **NARROWED AGAIN BY REGISTER #19's FIX (2026-07-21). Read this before comparing to either
earlier version.**

Scope A asserted *"zero write-CAPABLE routes"*. The Scope B wiring pass narrowed that to
*"every write goes through the frozen ``DecisionCommitService``"* when R5 was wired. **Register
#19's fix makes THAT claim false as written**: R5 now also **claims and finalizes pending case
state** through U24's own store methods — a different table, a different engine, a different
unit's transactional boundary. Those writes legitimately do **not** pass through the frozen
service, and no amount of wording makes them.

Deleting the assertion was again rejected for the reason recorded below. The guarantee is
therefore narrowed a second time, to the claim that is **both true and still falsifiable**:

> **Every ``audit_record`` write goes through the frozen ``DecisionCommitService``; every
> *pending-state* write goes through U24's own methods; and ``backend/app/`` still opens no
> transaction and writes no row itself.**

**Strictly more specific, not more permissive** — it now pins *two* channels where it previously
pinned one, and the direct-write prohibition (``.insert(`` / ``.atomic(`` appear nowhere) is
**unchanged and still enforced**, which is what keeps the composition root out of the
transaction business entirely.

⚑ **REVISED BY THE SCOPE B WIRING PASS. Read this before comparing against the Scope A version.**

Scope A asserted *"zero write-CAPABLE routes"*: no writer engine, no ``DecisionCommitService``,
no ``CommitContextProvider`` anywhere under ``backend/app/``. **R5 is now wired, so that claim is
FALSE BY DESIGN** — and deleting the assertions would have left the file asserting nothing.

Each of the five affected assertions was therefore **NARROWED, never deleted**. The substantive
guarantee moved from *the absence of writes* to *the channel every write must take*:

  (i)   the ONLY non-GET route is still R5                              (unchanged)
  (ii)  every other route is still read-only                            (unchanged)
  (iii) the seven WIRE-1 routes are still the whole surface             (unchanged)
  (iv)  R5's handler DELEGATES to the frozen service — it re-implements neither the CON-BR4
        gate nor the authz re-check, both of which run INSIDE ``commit()``
  (v)   the route module CONSTRUCTS nothing — every dependency arrives via ``Depends``
  (vi)  the writer engine is constructed EXACTLY ONCE, in EXACTLY ONE place
  (vii) the commit path uses the FROZEN service with U24's REAL provider — and the TEST-FAKE
        ``DictCommitContextProvider`` still appears NOWHERE in production (survives verbatim)
  (viii) no route writes DIRECTLY — ``.insert(``/``.atomic(`` still appear nowhere, and
        ``.commit(`` appears only on the injected service (the direct-write prohibition
        survives verbatim)

A verb count would pass while a rogue write path sat behind a POST; this cannot. Equally, a
blanket "no writes" assertion is no longer available to us — so what replaces it is the stronger,
still-falsifiable claim above.
"""
from __future__ import annotations

import ast
from pathlib import Path

from backend.app.main import create_app
from backend.app.tests._route_inventory import NON_GET_ALLOWLIST, ROUTE_INVENTORY

#: ⚑ RELAXED 2026-07-25 (frozen-assertion relaxation, R-3/R-4/R-5). The route literals below
#: were INLINE in three assertions in this file. They moved to ``_route_inventory.py``;
#: every comparison remains EXACT-SET EQUALITY, which is where the guard's strength lives.
#: ``route_table()`` upper-cases methods, so the lowercase declared methods are lifted here.
_DECLARED_PATHS = {path for path, _ in ROUTE_INVENTORY}
_DECLARED_NON_GET = sorted((path, method.upper()) for path, method in NON_GET_ALLOWLIST)
_NON_GET_PATHS = {path for path, _ in NON_GET_ALLOWLIST}

#: The ONLY route modules permitted to reach underwriting state.
#:
#: ⚑ ``submission.py`` ADDED 2026-08-02 (WIRE1-Fold-6, stage 2). Superseded text preserved:
#: *"The ONLY route module permitted to reach underwriting state (the R5 commit handler)"* —
#: ``frozenset({"not_wired.py"})``. R10 creates a case and R11 drafts one, so both reach domain
#: state; **neither creates a ``CommittedDecision``**, which remains R5's sole preserve and is
#: what the sibling assertions below still pin (``.commit(`` and the three claim methods are
#: still callable **only** from ``not_wired.py``).
_DOMAIN_WRITE_MODULES = frozenset({"not_wired.py", "submission.py"})

#: The domain seams a non-domain-write route module must not reference. ⚑ The ``.commit(``
#: and claim-method halves are covered by the two PRESERVED assertions further down; these
#: are the remaining seams, so together the invariant is independent of HTTP verb counts.
_DOMAIN_SEAMS = (
    "CasePipeline",
    "PostgresCaseStore",
    "PendingCommitContextProvider",
    "PostgresAuditRepository",
    "DecisionCommitService",
)

#: The pipeline seams. Referencing any of them is permitted ONLY in ``_PIPELINE_MODULES``.
_PIPELINE_SEAMS = ("CasePipeline", ".draft(", ".submit(")

#: ⚑ The EXACT set of production modules permitted to reference the pipeline (WIRE1-Fold-6).
#: ``dependencies.py`` COMPOSES it — the composition root's job, the same latitude the
#: ``_DOMAIN_SEAMS`` scan already grants it — and ``submission.py`` is R10/R11's module, the
#: only place ``submit()`` and ``draft()`` are invoked.
#:
#: ⚑ Deliberately NOT merged into ``_DOMAIN_WRITE_MODULES``: that set is scoped to
#: ``backend/app/routes/`` and exempts a ROUTE module from the domain-seam scan; this one is
#: scoped to the WHOLE package and names the pipeline's reachable surface. Two differently
#: scoped claims in one constant would weaken both.
_PIPELINE_MODULES = frozenset({"dependencies.py", "submission.py"})

#: The filesystem-WRITE constructs. ⛔ **WRITES ONLY — reads are deliberately absent.**
#: ``outlier_composition.py`` legitimately READS the committed corpus and ``RulebookLoader`` reads
#: the rulebook; the invariant here is about what this package PUTS on disk, not what it takes off.
#:
#: ⚑ ``open(`` is included even though it also opens for READING. Matching on mode would be
#: brittle (``"wb"``, ``"w"``, ``mode=`` keyword, a variable), and no production file in this
#: package uses ``open(`` at all — so the strictness costs nothing today and forces any future
#: read to say so explicitly with ``Path.read_text()`` / ``Path.read_bytes()``.
_FILESYSTEM_WRITE_CALLS = (
    "open(", ".write_bytes(", ".write_text(", ".mkdir(", "os.makedirs(",
    "tempfile", "shutil", "NamedTemporaryFile", "TemporaryDirectory",
)

#: ⛔ The EXACT set of production modules permitted to write to the filesystem.
#:
#: ⚑ **EMPTY, DELIBERATELY — AND THAT IS THE POINT** (WIRE1-Fold-7 / Q14(a)). No module in
#: ``backend/app/`` has ever written a file, and until this guard existed **nothing in this
#: package had an opinion about that**: every other assertion here polices transactions, engines,
#: domain seams and pipeline reachability. A grep of this file for ``open(`` / ``write_bytes`` /
#: ``mkdir`` / ``tempfile`` / ``shutil`` returned **zero** before Fold-7.
#:
#: The guard is created **BEFORE** the first module that writes, so that module's first encounter
#: with it is a **FAILURE** — the same RED-first discipline every other assertion in this file was
#: created under, applied to a guard being **created** rather than **widened**.
#:
#: ⚑ Adding a name here is a DELIBERATE ACT, and a weightier one than the sibling sets: the
#: subject is **raw applicant PII on disk**, not a transaction boundary.
#: ⚑ ``upload_storage.py`` ADDED 2026-08-03 (WIRE1-Fold-7, stage 2). Superseded text preserved:
#: the set was ``frozenset()`` — **empty** — from its creation at stage 1 until this line, and the
#: guard **failed on ``upload_storage.py`` before this edit was made**, observed on screen. That
#: failure is the whole reason the guard was created first (Q14(a)).
#:
#: ⛔ It is the **ONLY** member and must stay so. Every uploaded byte lands in a directory this
#: module creates, under a root it defines — which is precisely what makes the orphan sweep safe,
#: because it never touches a path the framework manages.
_FILESYSTEM_WRITE_MODULES: frozenset[str] = frozenset({"upload_storage.py"})

#: The ``memo_extensions`` import surface, scoped to ``backend/app/`` — the live-LLM-drafting gate.
#:
#: ⛔ **READ THE NAME'S SUFFIX. IT IS LOAD-BEARING.** This set governs which modules **inside
#: ``backend/app/``** may import ``backend.memo_extensions``. It says **nothing** about the rest of
#: the tree, and it *cannot*: ``PRODUCTION_FILES`` below is rooted at ``APP_ROOT``, so every module
#: outside this package is **structurally invisible** to the assertion.
#:
#: ⚑ **THE THING THAT MAKES THE SUFFIX NECESSARY, stated so it can never be misread as an
#: overclaim**: ``memo_extensions`` is **already imported in production, from outside this
#: package** — ``case_lifecycle/pipeline.py:38`` imports ``borderline_router`` and calls it on
#: **every draft** (``:184``). A bare ``_MEMO_EXTENSIONS_IMPORT_MODULES`` would therefore assert
#: something FALSE by implication: that these are *the* modules importing ``memo_extensions``.
#: They are the modules importing it **from here**.
#:
#: ⚑ This is the ``TRIGGER-1`` lesson applied at creation rather than after the fact. That guard
#: *"was ALSO BROADER THAN ITS OWN NAME — it said 'the read routes' but scanned every production
#: file"*, and had to be narrowed later. This one carries its scope in its name from birth.
#:
#: ⚠️ ``memo_extensions`` is **NOT** in ``test_frozen_untouched.py``'s ``FROZEN_UNITS`` and **no
#: pre-existing guard forbade this import**. This set is **discipline, not compliance**: it exists
#: so the NEXT such import meets an assertion instead of nothing.
#:
#: ⚑ ``dependencies.py`` ADDED at stage 3. Superseded text preserved verbatim, because it was true
#: for the whole of stage 1 and its truth is the evidence:
#:
#:     ⛔ **EMPTY AT CREATION, DELIBERATELY** (live-llm-drafting stage 1). The importing module does
#:     not exist yet; stage 3's ``dependencies.py`` import will **FAIL** this assertion, and that
#:     failure is the whole reason the guard is created first — the ``_FILESYSTEM_WRITE_MODULES``
#:     discipline (Fold-7 / Q14(a)), here applied **across a stage boundary**.
#:
#: ⛔ **THE FAILURE WAS OBSERVED BEFORE THIS LINE WAS EDITED.** The guard refused ``dependencies.py``
#: by name, on screen, and only then was the name added. Widening this set to silence a red
#: assertion **without having seen it red** is the one move the guard exists to make visible.
#:
#: ⛔ It is the **ONLY** member and must stay so. ``dependencies.py`` is the composition root — the
#: single place a provider is chosen. A second name here means something other than composition is
#: reaching for a provider adapter, which is a reviewable act with its own gate.
_MEMO_EXTENSIONS_IMPORT_MODULES_FROM_APP: frozenset[str] = frozenset({"dependencies.py"})

APP_ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_FILES = sorted(p for p in APP_ROOT.rglob("*.py") if "tests" not in p.parts)
ROUTES_MODULE = APP_ROOT / "routes" / "not_wired.py"


def route_table() -> dict[str, set[str]]:
    """``{path: {METHOD, ...}}`` — read from the app's own OpenAPI schema.

    The schema is the stable, public description of what the app exposes (the internal
    ``app.routes`` structure is version-dependent and wraps included routers). Docs/openapi
    endpoints are framework chrome, not contract routes, and carry no domain capability.
    """
    paths = create_app().openapi()["paths"]
    return {path: {method.upper() for method in operations} for path, operations in paths.items()}


def production_source() -> dict[Path, str]:
    return {p: p.read_text(encoding="utf-8") for p in PRODUCTION_FILES}


def strip_comments_and_docstrings(source: str) -> str:
    """Return code with comments/docstrings removed.

    Every by-construction guarantee in this package is documented in prose that NAMES the
    construct it discusses (main.py's header names ``DecisionCommitService``; not_wired.py
    explains the commit delegation). The guarantee is about CODE, not words — the frozen
    ui-approval-gate ``singleCallSite`` precedent, generalized.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                node.body.pop(0)
    return ast.unparse(tree)


def _handler(name: str) -> ast.FunctionDef:
    tree = ast.parse(ROUTES_MODULE.read_text(encoding="utf-8"))
    return next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == name
    )


def module_serves_a_get_route(source: str) -> bool:
    """True if the module declares at least one ``@….get(...)`` route decorator.

    ⚑ Deliberately BROAD — it matches any ``.get(`` call decorator, not only ``@router.get``.
    Broad means STRICTER here: a module wrongly classed as GET-serving is *forbidden* the
    pipeline, so the error direction is fail-closed.
    """
    tree = ast.parse(source)
    return any(
        isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == "get"
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        for d in n.decorator_list
    )


def references_a_pipeline_seam(source: str) -> bool:
    """True if the module references a pipeline seam in CODE — prose is stripped first."""
    code = strip_comments_and_docstrings(source)
    return any(seam in code for seam in _PIPELINE_SEAMS)


def references_a_filesystem_write(source: str) -> bool:
    """True if the module WRITES to the filesystem in CODE — prose is stripped first.

    ⚑ Reads are not writes: ``Path.read_text()`` / ``read_bytes()`` / ``is_file()`` / ``exists()``
    are all permitted and must stay permitted, because the corpus and the rulebook are read from
    disk by design.
    """
    code = strip_comments_and_docstrings(source)
    return any(call in code for call in _FILESYSTEM_WRITE_CALLS)


def imports_memo_extensions(source: str) -> bool:
    """True if the module IMPORTS ``backend.memo_extensions`` in CODE — prose is stripped first.

    ⚑ Prose is stripped for the same reason every other detector here strips it: this file's own
    comments **name** ``backend.memo_extensions`` repeatedly (the block above does so four times),
    and a raw text scan would flag the guard's own documentation as an offender.
    """
    code = strip_comments_and_docstrings(source)
    return "backend.memo_extensions" in code


# --- (i)-(iii) UNCHANGED from Scope A — these three survive the wiring verbatim -----------

class TestOnlyNonGetRouteIsTheR5Commit:
    def test_the_declared_non_get_routes_are_exactly_the_allowlist(self):
        """The non-GET routes are exactly those declared, each with a recorded reason.

        ⚑ RENAMED 2026-07-25 from ``test_the_route_table_has_exactly_one_non_get_route``
        (frozen-assertion relaxation, R-3 · Q2(a)). **Supersede-not-rewrite: the old name is
        recorded here, not erased.**

        ⚑ **The old name's REAL content is NOT lost — it was PROMOTED.** *"Exactly one"* was
        never really a claim about HTTP verbs; it was the claim that **there is exactly one
        way to change underwriting state over HTTP**. Widening this list to admit ``/login``
        and ``/logout`` would have silently converted a **domain-write** invariant into a
        **verb-count allowlist**, with every future POST joining unchallenged. So the
        substantive half now lives in
        ``test_no_non_get_route_but_the_commit_reaches_domain_state`` below, where it is
        asserted **directly and structurally** instead of being implied by counting.

        This half remains **exact-set equality** against the declared allowlist, so a new
        non-GET route still fails until it is deliberately declared **with its reason**.
        """
        non_get = sorted(
            (path, method)
            for path, methods in route_table().items()
            for method in methods
            if method not in {"GET", "HEAD"}
        )
        assert non_get == _DECLARED_NON_GET

    def test_no_non_get_route_but_the_commit_reaches_domain_state(self):
        """⚑ THE LOAD-BEARING HALF of R-3's split (Q3(a) — structural, not conventional).

        Being non-GET is **necessary but never sufficient**: a declared non-GET route must
        also be proven not to touch underwriting state. Only ``not_wired.py`` (the R5 commit
        handler) may reference the domain seams.

        **Scanned on STRIPPED source** — a handler that legitimately *documents* what it does
        not touch (*"unlike R5, this reaches no domain state"*) must not be failed for its
        prose. This file's other structural assertions already use the same helper.

        **File-level, not handler-level** — following the existing ``.commit(``-caller
        assertion's whole-module form, so a helper-function indirection inside a route module
        cannot evade it.

        ⚑ **Scoped to ROUTE MODULES, deliberately.** ``dependencies.py`` legitimately
        constructs every one of these seams — that is precisely the composition root's job
        (*"the ONLY place frozen units are constructed"*), and injection is what keeps the
        route modules free of them. Scanning the whole package would forbid the very wiring
        this architecture requires. The invariant is about **which ROUTES reach domain
        state**, so ``backend/app/routes/`` is the correct scan root.

        ⚑ **Precise scope, stated so it is not over-read**: the ``.commit(`` and claim-method
        halves are already enforced by ``test_no_route_writes_directly_only_commit_does`` and
        ``test_pending_state_writes_go_through_u24s_own_claim_methods``, which this pass
        deliberately leaves **untouched**. What this adds is the prohibition on the remaining
        seams below — together they make the domain-write invariant independent of verb counts.
        """
        route_modules = sorted((APP_ROOT / "routes").glob("*.py"))
        assert route_modules, "expected route modules to scan"   # never vacuously empty
        for path in route_modules:
            if path.name in _DOMAIN_WRITE_MODULES:
                continue
            code = strip_comments_and_docstrings(path.read_text(encoding="utf-8"))
            for seam in _DOMAIN_SEAMS:
                assert seam not in code, f"{path.name} references the domain seam {seam!r}"

    def test_detector_flags_a_synthetic_domain_seam_reference(self):
        # ⚑ NON-VACUITY: the scan above must actually discriminate. A synthetic module that
        # references a domain seam in CODE must be caught, while one that mentions it only in
        # a docstring must NOT be — that asymmetry is the whole point of stripping first.
        offending = "def handler():\n    return CasePipeline()\n"
        assert any(s in strip_comments_and_docstrings(offending) for s in _DOMAIN_SEAMS)

        documented_only = '"""Unlike R5, this never touches CasePipeline."""\ndef handler():\n    return None\n'
        assert not any(s in strip_comments_and_docstrings(documented_only) for s in _DOMAIN_SEAMS)

    def test_every_other_route_is_read_only(self):
        # ⚑ RELAXED (R-4): the skip-list is now the DECLARED non-GET allowlist rather than one
        # inline path. The assertion itself is unchanged — every route outside the allowlist
        # must be read-only. Name unchanged: it still describes exactly what it asserts.
        for path, methods in route_table().items():
            if path in _NON_GET_PATHS:
                continue
            assert methods <= {"GET", "HEAD"}, path

    def test_the_declared_route_inventory_is_the_whole_surface(self):
        """No route beyond the declared inventory exists.

        ⚑ RENAMED 2026-07-25 from ``test_the_seven_wire1_routes_are_the_whole_surface``
        (frozen-assertion relaxation, R-5 · Q2(a)). **Supersede-not-rewrite: the old name is
        recorded here, not erased.**

        **Why renamed**: *"seven"* is a count that the relaxation makes false. A name carrying
        a stale cardinality is **register #13**'s defect — a name asserting something the file
        no longer means — and leaving it would have minted a new instance of exactly the
        problem that register keeps open.

        **What did NOT change**: still **exact-set equality**, so the composition root still
        adds no endpoint of its own without a deliberate inventory update.

        ⚑ This assertion and U23's ``test_routes.py`` previously hardcoded **the same seven
        paths independently**, with nothing forcing them to agree. Both now read one declared
        inventory, cross-checked by ``test_route_inventory_sync.py`` — a **pre-existing** drift
        risk closed as a side effect.
        """
        assert set(route_table()) == _DECLARED_PATHS


# --- (iv)-(v) REVISED: the marker assertions become DELEGATION assertions ------------------

class TestR5DelegatesToTheFrozenServiceAndReimplementsNothing:
    """⚑ REPLACES ``test_its_first_statement_raises_the_marker``.

    Scope A asserted R5's handler did exactly one thing: raise. Now it commits — so what must be
    asserted is that it commits **through the frozen service** and re-implements none of the
    enforcement that lives inside it.
    """

    def test_the_r5_handler_calls_commit_on_an_injected_service(self):
        handler = _handler("commit_recommendation")
        calls = {
            node.func.attr
            for node in ast.walk(handler)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        assert "commit" in calls, "R5 must delegate to DecisionCommitService.commit"

        # the service is INJECTED, never constructed in the handler
        code = strip_comments_and_docstrings(ROUTES_MODULE.read_text(encoding="utf-8"))
        assert "DecisionCommitService(" not in code, "the service must be injected, not built here"

    def test_the_r5_handler_reimplements_neither_the_gate_nor_the_authz_recheck(self):
        """⚑ The CON-BR4 gate and the authz re-check run INSIDE the frozen ``commit()``.

        The route may reject a malformed ACTION (a closed-enum wire-shape check, WIRE-1 §4's
        422), but it must not re-derive the gate's own predicates — the blank-reason-override
        rule or any authorization decision of its own.
        """
        handler = _handler("commit_recommendation")
        source = ast.unparse(handler)
        # the gate's own reason predicate must not be duplicated here
        assert "reason.strip()" not in source
        assert ".strip() ==" not in source
        # authorization is never decided in the handler — it only DEPENDS on the guard
        assert "authorize(" not in source
        assert "PERMISSION_MATRIX" not in source

    def test_the_route_module_constructs_no_service_and_no_engine(self):
        """⚑ REPLACES ``test_the_marker_module_constructs_no_service_and_reads_no_body``.

        The module now legitimately reads a body and takes ``Depends`` — that prohibition is
        obsolete. What must hold instead is that it CONSTRUCTS nothing: every collaborator
        arrives injected, so the composition root's wiring stays in ``dependencies.py``.
        """
        code = strip_comments_and_docstrings(ROUTES_MODULE.read_text(encoding="utf-8"))
        for forbidden in ("create_engine", "DecisionCommitService(", "PostgresCaseStore(",
                          "PendingCommitContextProvider(", "get_settings("):
            assert forbidden not in code, forbidden

    def test_no_get_route_can_reach_the_pipeline(self):
        """⚑ BR-CASE-4 / TRIGGER-1 — no GET may trigger drafting.

        ⚑ **RENAMED + NARROWED A THIRD TIME BY WIRE1-Fold-6 (2026-08-02).** The old name was
        ``test_the_read_routes_invoke_no_pipeline_step``; the claim it made is preserved
        verbatim:

        > *"Structural, not behavioural: ``CasePipeline`` is not imported or constructed
        > anywhere in this package, so a read CANNOT reach ``draft()`` even by mistake."*

        **That became FALSE BY DESIGN when R10/R11 landed** — a submission route must call
        ``submit()`` and a drafting trigger must call ``draft()``. Deleting the assertion was
        refused for the THIRD time on this file's own recorded reasoning: it would leave the
        strongest structural guarantee in this package asserting nothing.

        ⚑ **The old guard was ALSO BROADER THAN ITS OWN NAME.** It said *"the read routes"* but
        scanned **every** production file, GET handler or not. The replacement asserts the claim
        the name always made, and asserts it **directly**:

        > **No module that serves a GET route may reference the pipeline; and the modules that
        > DO reference it are EXACTLY ``_PIPELINE_MODULES``.**

        **Strictly more specific, not more permissive**, in three ways.
        **(i) Exact-set equality, not a skip-list** — a sixth module reaching for the pipeline
        still fails, *and* a named module quietly dropping it fails too, which the old blanket
        scan could not express.
        **(ii) File-level, not handler-level** — following the sibling ``_DOMAIN_SEAMS``
        assertion's deliberate choice, *"so a helper-function indirection inside a route module
        cannot evade it"*. A GET handler cannot reach ``draft()`` via a module-level helper.
        **(iii) It forces R10/R11 into a module with NO GET route in it**, converting what would
        otherwise be reviewer discipline into a mechanical check.

        ⚑ **Non-vacuity is DEMONSTRATED, not assumed** — see the detector test below.
        """
        offenders = {
            path.name
            for path, source in production_source().items()
            if references_a_pipeline_seam(source)
        }
        assert offenders == _PIPELINE_MODULES, offenders

        for path, source in production_source().items():
            if module_serves_a_get_route(source):
                assert not references_a_pipeline_seam(source), (
                    f"{path.name} serves a GET route AND references the pipeline"
                )

    def test_detector_flags_a_get_module_reaching_for_the_pipeline(self):
        """⚑ NON-VACUITY for the narrowing above — step 1.7, MANDATORY not optional.

        A narrowing that is merely MORE PERMISSIVE rather than STRICTLY MORE SPECIFIC would
        silently retire the only mechanical enforcement of the §0.2 invariant. These three cases
        are what tell the two apart.
        """
        get_module_reaching_for_it = (
            "@router.get('/applications/{application_id}/memo')\n"
            "def memo_view(application_id: str):\n"
            "    return CasePipeline().draft(application_id)\n"
        )
        assert module_serves_a_get_route(get_module_reaching_for_it)
        assert references_a_pipeline_seam(get_module_reaching_for_it)     # ⚑ STILL CAUGHT

        get_module_that_only_documents_it = (
            '"""Unlike R11, this GET never reaches CasePipeline.draft()."""\n'
            "@router.get('/applications')\n"
            "def queue():\n"
            "    return []\n"
        )
        assert module_serves_a_get_route(get_module_that_only_documents_it)
        assert not references_a_pipeline_seam(get_module_that_only_documents_it)

        post_only_module = (
            "@router.post('/applications')\n"
            "def submit_application(body: dict):\n"
            "    return CasePipeline().submit(body)\n"
        )
        assert not module_serves_a_get_route(post_only_module)            # ⚑ the R10/R11 shape
        assert references_a_pipeline_seam(post_only_module)


# --- (vi)-(viii) REVISED: absence assertions become CHANNEL assertions ---------------------

class TestEveryWriteGoesThroughTheFrozenCommitService:
    def test_the_writer_engine_is_constructed_exactly_once_and_only_in_dependencies(self):
        """⚑ REPLACES ``test_no_writer_engine_is_ever_constructed``.

        The writer now exists (R5 needs it). The guarantee narrows to: ONE writer, ONE place.
        """
        holders = {
            path.name: code
            for path, source in production_source().items()
            if "AUDIT_WRITER_URL" in (code := strip_comments_and_docstrings(source))
        }
        assert set(holders) == {"dependencies.py"}, holders
        assert holders["dependencies.py"].count("AUDIT_WRITER_URL") == 1, "exactly one construction site"

        # the writer PASSWORD is still never read anywhere (it belongs to the URL, not the app)
        for path, source in production_source().items():
            assert "AUDIT_WRITER_PASSWORD" not in strip_comments_and_docstrings(source), path

    def test_the_commit_path_is_the_frozen_service_with_u24s_real_provider(self):
        """⚑ REPLACES ``test_no_commit_service_or_context_provider_exists``.

        Both now exist by design. What must hold is WHICH ones: the FROZEN service (imported,
        never re-declared) and U24's REAL provider.

        ⚑ The fake-provider prohibition SURVIVES VERBATIM — ``DictCommitContextProvider`` is
        audit-store's self-labelled "Test/fake provider" and must never reach production.
        """
        joined = "\n".join(
            strip_comments_and_docstrings(source) for source in production_source().values()
        )
        # the frozen service is IMPORTED, never re-declared here
        assert "from backend.audit_store.commit_service import" in joined
        assert "class DecisionCommitService" not in joined
        # U24's real provider backs it
        assert "PendingCommitContextProvider" in joined
        # ⚑ SURVIVES VERBATIM from Scope A — the test fake never reaches production
        assert "DictCommitContextProvider" not in joined

    def test_no_route_writes_directly_only_commit_does(self):
        """⚑ REPLACES ``test_no_repository_write_method_is_called``.

        ⚑ The direct-write prohibition SURVIVES VERBATIM through BOTH narrowings: ``.insert(``
        and ``.atomic(`` still appear NOWHERE under ``backend/app/`` — the composition root
        never opens a transaction or writes a row itself, **including for the register-#19
        claim**, whose three methods each own their transaction INSIDE U24. Only ``.commit(``
        is permitted, and only in the R5 handler.
        """
        for path, source in production_source().items():
            code = strip_comments_and_docstrings(source)
            for forbidden in (".insert(", ".atomic("):
                assert forbidden not in code, f"{path}: {forbidden}"

        commit_callers = {
            path.name
            for path, source in production_source().items()
            if ".commit(" in strip_comments_and_docstrings(source)
        }
        assert commit_callers == {"not_wired.py"}, commit_callers

    def test_pending_state_writes_go_through_u24s_own_claim_methods(self):
        """⚑ THE SECOND CHANNEL, added by register #19's narrowing.

        The pending-state writes are real and must be pinned as tightly as the audit write was:
        they may happen **only** through U24's three named claim methods, and **only** in the R5
        handler. If a future edit wrote pending state anywhere else under ``backend/app/`` — or
        reached for ``put_application`` directly — this fails.
        """
        claim_methods = (".claim_for_commit(", ".finalize_commit(", ".release_claim(")

        callers = {
            path.name
            for path, source in production_source().items()
            if any(m in strip_comments_and_docstrings(source) for m in claim_methods)
        }
        assert callers == {"not_wired.py"}, callers

        # ⚑ the RAW pending-state writers stay forbidden — the claim methods are the ONLY door
        for path, source in production_source().items():
            code = strip_comments_and_docstrings(source)
            for forbidden in (".put_application(", ".put_recommendation("):
                assert forbidden not in code, f"{path}: {forbidden}"

    def test_the_r5_handler_takes_the_claim_before_it_calls_commit(self):
        """⚑ ORDER IS THE WHOLE GUARANTEE (register #19).

        If ``commit()`` ran before the claim, the compare-and-swap would no longer prevent a
        duplicate ``AuditRecord`` — it would merely record one after the damage. A structural
        assertion, so the ordering cannot regress unnoticed.
        """
        handler = _handler("commit_recommendation")
        order = [
            node.func.attr
            for node in ast.walk(handler)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr in {"claim_for_commit", "commit", "finalize_commit"}
        ]
        assert "claim_for_commit" in order and "commit" in order and "finalize_commit" in order
        source = ast.unparse(handler)
        assert source.index("claim_for_commit") < source.index("service.commit")
        assert source.index("service.commit") < source.index("finalize_commit")



class TestNothingWritesToTheFilesystem:
    """⛔ WIRE1-Fold-7 / Q14(a) — a guard CREATED, not widened, and created BEFORE its subject.

    ``backend/app/`` has never written a file. Document upload will make it write **raw applicant
    PDFs**, and until this class existed **nothing in this package had an opinion about that**:
    every other assertion in this file polices transactions, engines, domain seams and pipeline
    reachability. A grep for ``open(`` / ``write_bytes`` / ``mkdir`` / ``tempfile`` / ``shutil``
    over this file returned **zero** before Fold-7.

    ⚑ **Created FIRST, deliberately.** The module that writes does not exist yet, so the declared
    set below is **empty** and the first module to write will **fail** this — which is the same
    RED-first discipline every other assertion here was created under, applied to a guard being
    created rather than narrowed.
    """

    def test_no_production_module_writes_to_the_filesystem_but_the_declared_ones(self):
        """**Exact-set equality, not a skip-list** — the shape ``_PIPELINE_MODULES`` established.

        A new module writing files fails until it is deliberately named, **and** a named module
        that stops writing fails too, so the declaration cannot rot into a stale exemption
        nobody notices.
        """
        writers = {
            path.name
            for path, source in production_source().items()
            if references_a_filesystem_write(source)
        }
        assert writers == _FILESYSTEM_WRITE_MODULES, writers

    def test_exactly_one_module_has_earned_a_place_in_the_declared_set(self):
        """⚑ SUPERSEDED 2026-08-03 (stage 2). The stage-1 assertion is preserved verbatim:

            it('the declared set is empty until a module earns a place in it')
            assert _FILESYSTEM_WRITE_MODULES == frozenset()

        It was TRUE for the whole of stage 1 and is FALSE now, **which is the point**:
        ``upload_storage.py`` earned its place by failing the guard first, observed on screen
        before this set was widened.

        ⛔ What the assertion still pins is the thing that matters — **exactly one** module writes
        to disk. A second name appearing here must be a reviewed act with its own gate, never a
        quiet edit made to turn a red assertion green.
        """
        assert _FILESYSTEM_WRITE_MODULES == frozenset({"upload_storage.py"})

    def test_detector_flags_every_filesystem_write_construct(self):
        """⚑ NON-VACUITY, tier 1 — and fed EACH construct SEPARATELY, not one representative.

        ⛔ **This is stage 1's named risk made mechanical.** A guard that catches ``open(`` and
        misses ``Path.write_bytes`` would look identical to a working one on the day it is
        written and would let an applicant's PDF onto disk unnoticed six months later.
        """
        for construct in (
            "def h():\n    open('/tmp/x', 'wb').write(b'')\n",
            "from pathlib import Path\ndef h():\n    Path('/tmp/x').write_bytes(b'')\n",
            "from pathlib import Path\ndef h():\n    Path('/tmp/x').write_text('x')\n",
            "from pathlib import Path\ndef h():\n    Path('/tmp/d').mkdir()\n",
            "import os\ndef h():\n    os.makedirs('/tmp/d')\n",
            "import tempfile\ndef h():\n    return tempfile.mkdtemp()\n",
            "import shutil\ndef h():\n    shutil.copy('a', 'b')\n",
            "from tempfile import NamedTemporaryFile\ndef h():\n    return NamedTemporaryFile()\n",
            "from tempfile import TemporaryDirectory\ndef h():\n    return TemporaryDirectory()\n",
        ):
            assert references_a_filesystem_write(construct), construct

    def test_the_detector_permits_reads_and_prose(self):
        """⛔ THE OTHER HALF, and the one that stops the guard being merely restrictive.

        ``outlier_composition.py`` READS the committed corpus and ``RulebookLoader`` reads the
        rulebook — both by design. A guard that failed those would be wrong, not strict, and the
        pressure would be to weaken it rather than fix it.
        """
        from pathlib import Path as _P  # noqa: F401  (referenced in the synthetic sources below)

        for permitted in (
            "from pathlib import Path\ndef h():\n    return Path('corpus.json').read_text()\n",
            "from pathlib import Path\ndef h():\n    return Path('corpus.json').read_bytes()\n",
            "from pathlib import Path\ndef h():\n    return Path('corpus.json').is_file()\n",
            "from pathlib import Path\ndef h():\n    return Path('corpus.json').exists()\n",
            "from pathlib import Path\nROOT = Path(__file__).resolve().parents[2]\n",
        ):
            assert not references_a_filesystem_write(permitted), permitted


class TestOnlyDeclaredAppModulesImportMemoExtensions:
    """⛔ The live-LLM-drafting gate (G1) — a guard CREATED, not widened, and created BEFORE the
    module it constrains, like ``_FILESYSTEM_WRITE_MODULES`` before it.

    ⚑ **WHAT THIS CLASS DOES AND DOES NOT CLAIM.** It claims that within ``backend/app/``, exactly
    the declared modules import ``backend.memo_extensions``. It does **NOT** claim they are the only
    production modules importing it anywhere — ``case_lifecycle/pipeline.py:38`` already does, and
    is outside ``APP_ROOT`` and therefore outside this scan by construction. The set's name carries
    that scope so a future reader cannot mistake the narrower claim for the broader one.

    ⚠️ **This guard was not required by anything.** ``memo_extensions`` is absent from
    ``FROZEN_UNITS`` and no pre-existing assertion mentioned it. It exists because a structural
    first deserves a mechanical trace — the same reasoning that created the filesystem guard when a
    grep for ``open(`` over this file returned zero.
    """

    def test_no_app_module_imports_memo_extensions_but_the_declared_ones(self):
        """**Exact-set equality, not a skip-list** — the shape ``_PIPELINE_MODULES`` established.

        A new importer fails until it is deliberately named, **and** a named module that stops
        importing fails too, so the declaration cannot rot into a stale exemption.
        """
        importers = {
            path.name
            for path, source in production_source().items()
            if imports_memo_extensions(source)
        }
        assert importers == _MEMO_EXTENSIONS_IMPORT_MODULES_FROM_APP, importers

    def test_exactly_one_app_module_has_earned_a_place_in_the_declared_set(self):
        """⚑ SUPERSEDED at stage 3. The stage-1 assertion is preserved verbatim:

            it('the declared set is empty until a module earns a place in it')
            assert _MEMO_EXTENSIONS_IMPORT_MODULES_FROM_APP == frozenset()

        It was TRUE for the whole of stage 1 and is FALSE now, **which is the point**:
        ``dependencies.py`` earned its place by failing the guard first, observed on screen before
        the set was widened — and the sibling assertion above failed **first**, this one second,
        in that order and never the reverse.

        ⛔ What the assertion still pins is the thing that matters — **exactly one** module in
        ``backend/app/`` reaches for ``memo_extensions``, and it is the composition root.
        """
        assert _MEMO_EXTENSIONS_IMPORT_MODULES_FROM_APP == frozenset({"dependencies.py"})

    def test_detector_flags_every_import_form(self):
        """⚑ NON-VACUITY, tier 1 — every syntactic route to the package, fed separately.

        ⛔ Without this, an empty allowlist over zero importers asserts **nothing at all**: the
        equality would hold for a detector that always returned ``False``.
        """
        for construct in (
            "from backend.memo_extensions.provider_showcase import OllamaAdapter\n",
            "from backend.memo_extensions import borderline_router\n",
            "import backend.memo_extensions\n",
            "import backend.memo_extensions.provider_secondary as p\n",
            "from backend.memo_extensions.provider_secondary import ThinkingLLMClient\n",
        ):
            assert imports_memo_extensions(construct), construct

    def test_the_detector_ignores_prose_and_unrelated_imports(self):
        """⛔ THE OTHER HALF. This very file NAMES ``backend.memo_extensions`` in its own comments,
        and ``memo_agent_core`` is a different package that must stay freely importable."""
        for permitted in (
            '"""A docstring naming backend.memo_extensions in prose."""\nX = 1\n',
            "# a comment naming backend.memo_extensions\nX = 1\n",
            "from backend.memo_agent_core.provider import GeminiAdapter\n",
            "from backend.case_lifecycle.pipeline import CasePipeline\n",
        ):
            assert not imports_memo_extensions(permitted), permitted

        # ...and prose naming a write must not be flagged — this file's stripping precedent.
        documented_only = (
            '"""This module never calls write_bytes and creates no tempfile."""\n'
            "def h():\n    return None\n"
        )
        assert not references_a_filesystem_write(documented_only)


# --- detector self-tests (unchanged substrate) --------------------------------------------

class TestDetectorSelfTests:
    def test_the_comment_stripper_removes_prose_but_keeps_code(self):
        source = (
            '"""A docstring naming DecisionCommitService and AUDIT_WRITER_URL."""\n'
            "# a comment naming CommitContextProvider\n"
            "x = 1\n"
        )
        code = strip_comments_and_docstrings(source)
        assert "DecisionCommitService" not in code
        assert "AUDIT_WRITER_URL" not in code
        assert "CommitContextProvider" not in code
        assert "x = 1" in code

    def test_the_scan_would_catch_a_direct_repository_write(self):
        code = strip_comments_and_docstrings("repo.insert(record)\n")
        assert ".insert(" in code

    def test_the_scan_would_catch_a_second_writer_engine(self):
        code = strip_comments_and_docstrings("e = create_engine(get_settings().AUDIT_WRITER_URL)\n")
        assert "AUDIT_WRITER_URL" in code

    def test_the_scan_would_catch_the_test_fake_provider(self):
        code = strip_comments_and_docstrings("p = DictCommitContextProvider({})\n")
        assert "DictCommitContextProvider" in code
