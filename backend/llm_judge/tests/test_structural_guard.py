"""The StructuralGuard substrate's own self-tests (C-JUDGE-5 / P-JUDGE-13).

Mirrors the frozen ``observability`` / ``memo_extensions`` / ``outlier_model``
``test_structural_guard.py`` precedent: the SCANS themselves are exercised here, so no scan
in this unit can pass over an empty file set or a degenerate input.

The six scans and their per-target detector self-tests live with their targets
(``test_noedit.py``, ``test_nometric.py``, ``test_clidefer.py``, ``test_advisory.py``,
``test_nodemo.py``, ``test_disclose.py``). This file guards the SUBSTRATE they share.
"""
from __future__ import annotations

from backend.llm_judge.tests import structural as sg


def test_the_production_scan_set_is_non_vacuous_and_excludes_tests():
    production = sg.production_py_files()
    names = {p.name for p in production}
    assert names >= sg.EXPECTED_PRODUCTION_MODULES
    assert all("tests" not in p.parts for p in production)
    assert "fixtures.py" not in names
    assert "structural.py" not in names


def test_the_expected_production_modules_all_exist_on_disk():
    names = {p.name for p in sg.production_py_files()}
    for expected in sg.EXPECTED_PRODUCTION_MODULES:
        assert expected in names, expected


def test_the_authored_scan_set_includes_both_production_and_tests():
    authored = {p.name for p in sg.authored_py_files()}
    assert authored >= sg.EXPECTED_PRODUCTION_MODULES
    assert "fixtures.py" in authored
    assert "test_structural_guard.py" in authored


def test_repo_relative_paths_resolve_under_the_unit_tree():
    for path in sg.authored_py_files():
        assert sg.repo_relative(path).startswith("backend/llm_judge/")


def test_imported_roots_detects_both_import_forms():
    tree = sg.parse_source("import json\nfrom pathlib import Path\n")
    assert sg.imported_roots(tree) == {"json", "pathlib"}


def test_annotation_names_detects_field_and_return_annotations():
    source = (
        "from dataclasses import dataclass\n"
        "@dataclass\n"
        "class A:\n"
        "    x: Recommendation\n"
        "def f() -> Verdict:\n"
        "    ...\n"
    )
    names = sg.annotation_names(sg.parse_source(source))
    assert "Recommendation" in names
    assert "Verdict" in names


def test_called_and_assigned_names_are_detected():
    tree = sg.parse_source("Y = Counter()\nZ: int = 1\n")
    assert "Counter" in sg.called_names(tree)
    assert {"Y", "Z"} <= sg.assigned_names(tree)


def test_string_constants_include_docstrings_and_literals():
    literals = sg.string_constants(sg.parse_source('"""doc"""\nX = "lit"\n'))
    assert "doc" in literals
    assert "lit" in literals


def test_contains_token_is_case_insensitive():
    # A neutral token is used here on purpose: NODEMO-1 scans this file, and spelling a
    # demographic attribute out would trip its own (correct) whole-word check.
    assert sg.contains_token("A Widget here", "widget")
    assert not sg.contains_token("nothing here", "widget")


def test_contains_token_matches_whole_words_only():
    """Regression guard for a real substring collision: 'ethnicity' contains 'city'.
    A naive `in` test would flag the wrong attribute and mask which one appeared."""
    assert not sg.contains_token("ethnicity", "city")
    assert sg.contains_token("the city here", "city")
    assert sg.contains_token("ethnicity", "ethnicity")


def test_every_production_module_parses():
    for path in sg.production_py_files():
        assert sg.parse(path) is not None


def test_the_frozen_artifacts_are_readable_read_only():
    assert sg.OBSERVABILITY_METRICS.exists()
    assert sg.GRAFANA_DASHBOARD.exists()
    assert "panels" in sg.load_dashboard()
