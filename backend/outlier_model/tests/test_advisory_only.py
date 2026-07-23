"""NFR-OUT-ADVISORY-1 (structural) — advisory-only: no verdict / LLM / write / persistence.

Scans production for (a) any LLM/provider client import, (b) any DB/persistence import, (c) any
``Recommendation`` import (no verdict-producing path); and asserts the ``OutlierResult`` schema
carries a score + flags + provenance ONLY — no verdict field (BR-OUT-9 / skill #1/#3).
"""
from __future__ import annotations

from backend.outlier_model.schemas import OutlierResult
from backend.outlier_model.tests import structural

_FORBIDDEN_IMPORTS = (
    # LLM / provider clients
    "openai", "anthropic", "google.generativeai", "google.genai", "langchain", "langgraph", "ollama",
    # DB / persistence / write transports
    "sqlalchemy", "psycopg", "psycopg2", "backend.database",
    # verdict producer
    "backend.rules_engine.report_schema",
)


def _is_forbidden(module: str) -> bool:
    return any(module == f or module.startswith(f + ".") for f in _FORBIDDEN_IMPORTS)


def test_no_llm_db_or_verdict_import_in_production():
    offenders: list[str] = []
    for path in structural.production_py_files():
        for module in structural.imported_modules(structural.parse(path)):
            if _is_forbidden(module):
                offenders.append(f"{path.name}: imports {module}")
    assert offenders == [], f"advisory-only violation — forbidden imports: {offenders}"


def test_outlier_result_has_no_verdict_field():
    # Score + flags + provenance ONLY — no Recommendation / verdict / decision field.
    assert set(OutlierResult.model_fields) == {
        "outlier_score",
        "is_outlier",
        "flagged_features",
        "provenance",
    }


def test_scan_sees_the_real_production_modules():
    names = {p.name for p in structural.production_py_files()}
    assert structural.EXPECTED_PRODUCTION_MODULES <= names


def test_detector_flags_synthetic_llm_and_db_imports():
    synthetic = "import openai\nfrom backend.database import pg\nfrom backend.rules_engine.report_schema import Recommendation\n"
    detected = {m for m in structural.imported_modules(structural.parse_source(synthetic)) if _is_forbidden(m)}
    assert any(m == "openai" for m in detected)
    assert any(m.startswith("backend.database") for m in detected)
    assert any("report_schema" in m for m in detected)
