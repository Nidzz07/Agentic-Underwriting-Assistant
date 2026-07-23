"""NFR-OUT-SCOPE-1 (structural) — no import of a consumer or ``quality_gates`` (BR-OUT-10).

Scans every production module: none may import ``quality_gates``, ``memo_agent_core``,
``ui_outlier_view``, or ``observability``. ``quality_gates`` + ``memo_agent_core`` EXIST today
(P1), so the scan against them is non-vacuous now; ``ui_outlier_view`` (U20) + ``observability``
(U21) do NOT exist yet, so those are forward-looking regression guards proven by the detector
self-test (CG-NFR-OUT-Fold-3).
"""
from __future__ import annotations

import pathlib

from backend.outlier_model.tests import structural

_FORBIDDEN = ("quality_gates", "memo_agent_core", "ui_outlier_view", "observability")


def _is_forbidden(module: str) -> bool:
    for name in _FORBIDDEN:
        if module == name or module.endswith(f".{name}") or f".{name}." in f".{module}.":
            return True
    return False


def test_no_consumer_or_quality_gates_import():
    offenders: list[str] = []
    for path in structural.production_py_files():
        for module in structural.imported_modules(structural.parse(path)):
            if _is_forbidden(module):
                offenders.append(f"{path.name}: imports {module}")
    assert offenders == [], f"forbidden imports found: {offenders}"


def test_scan_sees_the_real_production_modules():
    names = {p.name for p in structural.production_py_files()}
    assert structural.EXPECTED_PRODUCTION_MODULES <= names


def test_non_vacuity_the_existing_consumers_are_real():
    # quality_gates + memo_agent_core exist on disk today → the scan against them is not a no-op.
    backend_dir = structural.UNIT_DIR.parent
    assert (backend_dir / "quality_gates" / "__init__.py").exists()
    assert (backend_dir / "memo_agent_core" / "__init__.py").exists()


def test_detector_flags_synthetic_violations():
    # self-test: the detector genuinely flags each forbidden import (incl. the forward-looking
    # U20/U21 modules that do not exist yet — proving those guards are not tautologies).
    synthetic = (
        "from backend.quality_gates import corpus_loader\n"
        "import backend.memo_agent_core\n"
        "from backend.ui_outlier_view import panel\n"
        "from backend.observability import tracer\n"
    )
    detected = {m for m in structural.imported_modules(structural.parse_source(synthetic)) if _is_forbidden(m)}
    assert any("quality_gates" in m for m in detected)
    assert any("memo_agent_core" in m for m in detected)
    assert any("ui_outlier_view" in m for m in detected)
    assert any("observability" in m for m in detected)
