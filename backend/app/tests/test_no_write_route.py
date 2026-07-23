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


# --- (i)-(iii) UNCHANGED from Scope A — these three survive the wiring verbatim -----------

class TestOnlyNonGetRouteIsTheR5Commit:
    def test_the_route_table_has_exactly_one_non_get_route(self):
        non_get = sorted(
            (path, method)
            for path, methods in route_table().items()
            for method in methods
            if method not in {"GET", "HEAD"}
        )
        assert non_get == [("/recommendations/{recommendation_id}/commit", "POST")]

    def test_every_other_route_is_read_only(self):
        for path, methods in route_table().items():
            if path == "/recommendations/{recommendation_id}/commit":
                continue
            assert methods <= {"GET", "HEAD"}, path

    def test_the_seven_wire1_routes_are_the_whole_surface(self):
        # No route beyond the contract exists — the composition root adds no endpoint of its own.
        assert set(route_table()) == {
            "/session",
            "/applications",
            "/applications/{application_id}",
            "/applications/{application_id}/memo",
            "/recommendations/{recommendation_id}/commit",
            "/decisions",
            "/decisions/{decision_id}",
        }


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

    def test_the_read_routes_invoke_no_pipeline_step(self):
        """⚑ BR-CASE-4 / TRIGGER-1 — no GET may trigger drafting.

        Structural, not behavioural: ``CasePipeline`` is not imported or constructed anywhere in
        this package, so a read CANNOT reach ``draft()`` even by mistake.
        """
        for path, source in production_source().items():
            code = strip_comments_and_docstrings(source)
            assert "CasePipeline" not in code, path
            assert ".draft(" not in code, path
            assert ".submit(" not in code, path


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
