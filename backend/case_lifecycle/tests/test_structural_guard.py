"""The StructuralGuard substrate's own self-tests (C-CASE-8 / P-CASE-14).

Mirrors the frozen `observability` / `memo_extensions` / `outlier_model` / `llm_judge`
substrates: the SCANS themselves are exercised here, so no scan in this unit can pass over an
empty file set or a degenerate input.
"""
from __future__ import annotations

from backend.case_lifecycle.tests import structural as sg


def test_the_production_scan_set_is_non_vacuous_and_excludes_tests():
    production = sg.production_py_files()
    names = {p.name for p in production}
    assert names >= sg.EXPECTED_PRODUCTION_MODULES
    assert all("tests" not in p.parts for p in production)
    assert "fixtures.py" not in names
    assert "structural.py" not in names


def test_all_seven_expected_production_modules_exist_on_disk():
    names = {p.name for p in sg.production_py_files()}
    for expected in sg.EXPECTED_PRODUCTION_MODULES:
        assert expected in names, expected


def test_the_expected_set_matches_the_modules_actually_on_disk():
    """⚑ CG-CASE-Fold-2 — nothing missing, nothing extra.

    ⚑ REVISED by U24's THIRD AUTHORIZED REOPENING (Q14-A), which added ``memo_adapter.py`` as an
    eighth production module. The assertion is now by **EXACT SET** rather than by count: a bare
    count said only *"how many"*, which is both weaker (a swapped module passes) and more brittle
    (every authorized addition breaks it for no diagnostic gain). This form states which modules
    are expected and catches an unexpected addition, a removal AND a substitution.
    """
    on_disk = {p.name for p in sg.production_py_files() if p.name != "__init__.py"}
    assert on_disk == sg.EXPECTED_PRODUCTION_MODULES


def test_the_authored_scan_set_includes_both_production_and_tests():
    authored = {p.name for p in sg.authored_py_files()}
    assert authored >= sg.EXPECTED_PRODUCTION_MODULES
    assert "fixtures.py" in authored


def test_called_and_assigned_names_are_detected():
    tree = sg.parse_source("Y = Counter()\nZ: int = 1\n")
    assert "Counter" in sg.called_names(tree)
    assert {"Y", "Z"} <= sg.assigned_names(tree)


def test_keyword_values_extracts_a_literal_keyword_argument():
    assert sg.keyword_values(sg.parse_source('f(mode="json")\n'), "mode") == ["json"]
    assert sg.keyword_values(sg.parse_source("f(x=1)\n"), "mode") == []


def test_imported_roots_detects_both_import_forms():
    tree = sg.parse_source("import json\nfrom pathlib import Path\n")
    assert sg.imported_roots(tree) == {"json", "pathlib"}


def test_string_constants_include_docstrings_and_literals():
    literals = sg.string_constants(sg.parse_source('"""doc"""\nX = "lit"\n'))
    assert "doc" in literals and "lit" in literals


def test_contains_token_matches_whole_words_only():
    """Regression guard for the substring collision class (e.g. 'city' inside 'ethnicity')."""
    assert not sg.contains_token("ethnicity", "city")
    assert sg.contains_token("the city here", "city")


def test_every_production_module_parses():
    for path in sg.production_py_files():
        assert sg.parse(path) is not None


def test_the_frozen_artifacts_are_readable_read_only():
    assert sg.OBSERVABILITY_METRICS.exists()
    assert sg.GRAFANA_DASHBOARD.exists()
    assert "panels" in sg.load_dashboard()
