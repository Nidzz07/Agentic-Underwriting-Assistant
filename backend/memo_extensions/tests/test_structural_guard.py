"""StructuralGuard (P-MEXT-10) — one substrate of eight AST/import scans, EACH with a
mandatory detector self-test (non-vacuous, per the CG-NFR-OUT-Fold-3 convention). Covers
the structural halves of ROUTE/FROZEN/SIGNAL/BIAS/MCPRO/CONTRACT/GROUND + SCOPE-1.

Scan 1 ⊂ Scan 7 by construction (Fold-3): the router's allow-list is TIGHTER than the
unit rule (it excludes ``audit_store``), so the two agree rather than needing reconciliation.
"""
from __future__ import annotations

import ast

from backend.memo_extensions.tests import structural as sg


# ---- shared annotation helper ---------------------------------------------
def _ann_name(node) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Subscript):
        return _ann_name(node.value)
    return None


# ===========================================================================
# Non-vacuity: the scans actually see the four production modules.
# ===========================================================================
def test_scan_set_sees_the_real_production_modules():
    names = {p.name for p in sg.production_py_files()}
    assert sg.EXPECTED_PRODUCTION_MODULES <= names


# ===========================================================================
# Scan 1 — router import ALLOW-LIST (ROUTE-1)
# ===========================================================================
_ROUTER_ALLOWED = {
    "__future__", "typing", "enum", "dataclasses",
    "backend.memo_agent_core.schemas", "backend.rules_engine.report_schema",
}


def _router_import_offenders(modules: set[str]) -> list[str]:
    return [
        m for m in modules
        if m not in _ROUTER_ALLOWED and not m.startswith("backend.memo_extensions")
    ]


def test_scan1_router_imports_are_subset_of_allow_list():
    modules = sg.imported_modules(sg.parse(sg.module_file(sg.ROUTER_MODULE)))
    assert _router_import_offenders(modules) == []


def test_scan1_detector_flags_a_synthetic_llm_import():
    modules = sg.imported_modules(sg.parse_source("import anthropic\n"))
    assert _router_import_offenders(modules) == ["anthropic"]


def test_scan1_subset_of_scan7_router_excludes_audit_store():
    edges = sg.backend_edge_roots(sg.imported_modules(sg.parse(sg.module_file(sg.ROUTER_MODULE))))
    assert "audit_store" not in edges          # tighter than the unit rule (Fold-3)
    assert edges <= {"memo_agent_core", "rules_engine", "audit_store"}


# ===========================================================================
# Scan 2 — no outlier_model import (SIGNAL-1)
# ===========================================================================
def _imports_outlier_model(modules: set[str]) -> bool:
    return any(m == "outlier_model" or "outlier_model" in m.split(".") for m in modules)


def test_scan2_no_outlier_model_import_in_production():
    for path in sg.production_py_files():
        assert not _imports_outlier_model(sg.imported_modules(sg.parse(path))), path.name


def test_scan2_detector_flags_a_synthetic_outlier_model_import():
    modules = sg.imported_modules(sg.parse_source("from backend.outlier_model import schemas\n"))
    assert _imports_outlier_model(modules)


# ===========================================================================
# Scan 3 — no flagged_features / shap_value / provenance reference (SCOPE-1)
# ===========================================================================
_PROSE_FIELDS = {"flagged_features", "shap_value", "provenance"}


def test_scan3_no_prose_bearing_outlier_field_reference():
    for path in sg.production_py_files():
        assert not (sg.attribute_names(sg.parse(path)) & _PROSE_FIELDS), path.name


def test_scan3_detector_flags_a_synthetic_outlier_field_read():
    assert sg.attribute_names(sg.parse_source("y = result.flagged_features\n")) & _PROSE_FIELDS


# ===========================================================================
# Scan 4 — no demographic read over the handler surface (BIAS-1)
# ===========================================================================
_DEMOGRAPHIC = {"full_name", "gender", "city", "demographics"}


def test_scan4_no_demographic_read_in_mcp_tools():
    attrs = sg.attribute_names(sg.parse(sg.module_file(sg.HANDLER_MODULE)))
    assert not (attrs & _DEMOGRAPHIC)


def test_scan4_detector_flags_a_synthetic_demographic_read():
    assert sg.attribute_names(sg.parse_source("c = record.demographics.city\n")) & _DEMOGRAPHIC


# ===========================================================================
# Scan 5 — read-only handler surface (MCPRO-1) — SEMANTIC, not word-matched
# ===========================================================================
_WRITE_METHOD_PREFIXES = ("commit", "write", "persist", "update", "delete", "save", "insert", "mutate")
_WRITE_IMPORT_TOKENS = ("commit_service", "DecisionCommitService", "write_transport", "session_write")


def _write_methods(tree) -> list[str]:
    return [m for m in sg.defined_method_names(tree) if m.startswith(_WRITE_METHOD_PREFIXES)]


def test_scan5_no_write_member_on_handler_surface():
    tree = sg.parse(sg.module_file(sg.HANDLER_MODULE))
    assert _write_methods(tree) == []
    # semantic list must PERMIT the pure composer members (non-vacuity of the permit)
    methods = sg.defined_method_names(tree)
    assert {"compose_prompt", "supplementary_block", "describe_rules", "recent_precedent"} <= methods


def test_scan5_no_write_transport_import_in_handler():
    modules = sg.imported_modules(sg.parse(sg.module_file(sg.HANDLER_MODULE)))
    assert not any(tok in m for m in modules for tok in _WRITE_IMPORT_TOKENS)


def test_scan5_detector_flags_a_synthetic_write_member_and_import():
    src = (
        "from backend.audit_store.commit_service import DecisionCommitService\n"
        "class X:\n"
        "    def commit_decision(self):\n"
        "        pass\n"
    )
    tree = sg.parse_source(src)
    assert _write_methods(tree) == ["commit_decision"]
    modules = sg.imported_modules(tree)
    assert any(tok in m for m in modules for tok in _WRITE_IMPORT_TOKENS)


# ===========================================================================
# Scan 6 — no LLM-output model / no Recommendation-producing path (CONTRACT-1, Q5-A)
# ===========================================================================
def _complete_return_names(tree) -> list[str]:
    return [
        _ann_name(node.returns)
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "complete"
    ]


def _recommendation_typed_paths(tree) -> list[str]:
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and _ann_name(node.annotation) in {"Recommendation", "Confidence"}:
            hits.append("field")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _ann_name(node.returns) in {
            "Recommendation", "Confidence"
        }:
            hits.append(node.name)
    return hits


def test_scan6_llm_output_type_stays_the_frozen_memo_draft_output():
    returns: list[str] = []
    for path in sg.production_py_files():
        returns.extend(_complete_return_names(sg.parse(path)))
    assert returns  # non-vacuity: the adapters' complete() methods exist
    assert set(returns) == {"MemoDraftOutput"}  # no U19-declared LLM-output model


def test_scan6_no_recommendation_producing_path_in_production():
    for path in sg.production_py_files():
        assert _recommendation_typed_paths(sg.parse(path)) == [], path.name


def test_scan6_permits_the_handler_read_projections_q5a():
    # PrecedentSummary/RuleDescription (BaseModel read projections) are present and NOT flagged.
    models = sg.basemodel_classes_with_fields(sg.parse(sg.module_file(sg.HANDLER_MODULE)))
    assert {"PrecedentSummary", "RuleDescription"} <= set(models)


def test_scan6_detector_flags_a_synthetic_llm_output_model_and_recommendation_field():
    assert _complete_return_names(sg.parse_source("def complete(self, p, s) -> _FakeOut: ...\n")) == ["_FakeOut"]
    assert _recommendation_typed_paths(sg.parse_source("class M:\n    recommendation: Recommendation\n"))


# ===========================================================================
# Scan 7 — backend.* ⊆ {memo_agent_core, rules_engine, audit_store} + no memo_agent_core.tests.*
# ===========================================================================
_ALLOWED_BACKEND_ROOTS = {"memo_agent_core", "rules_engine", "audit_store"}


def _forbidden_edges(modules: set[str]) -> list[str]:
    bad = list(sg.backend_edge_roots(modules) - _ALLOWED_BACKEND_ROOTS)
    bad += [m for m in modules if "memo_agent_core.tests" in m]
    return bad


def test_scan7_backend_imports_are_exactly_the_three_frozen_edges():
    for path in sg.production_py_files():
        assert _forbidden_edges(sg.imported_modules(sg.parse(path))) == [], path.name


def test_scan7_detector_flags_a_foreign_edge_and_a_u4_test_import():
    src = (
        "from backend.quality_gates import x\n"
        "import backend.memo_agent_core.tests.test_provider\n"
    )
    bad = _forbidden_edges(sg.imported_modules(sg.parse_source(src)))
    assert any("quality_gates" == b for b in bad)
    assert any("memo_agent_core.tests" in b for b in bad)


# ===========================================================================
# Scan 8 — no append to cited_rule_ids (GROUND-1)
# ===========================================================================
def test_scan8_no_append_into_cited_rule_ids_in_production():
    for path in sg.production_py_files():
        assert not sg.mutating_calls_on_attribute(sg.parse(path), "cited_rule_ids"), path.name


def test_scan8_detector_flags_a_synthetic_cited_rule_ids_append():
    assert sg.mutating_calls_on_attribute(sg.parse_source('draft.cited_rule_ids.append("X")\n'), "cited_rule_ids")
