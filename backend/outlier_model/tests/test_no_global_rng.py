"""NFR-OUT-DET-1 (structural half) — no global RNG / wall-clock in a scoring path.

AST scan forbidding, in any production module: (a) the global numpy RNG — any ``np.random.*`` /
``numpy.random.*`` attribute access (the sanctioned path imports ``RandomState`` DIRECTLY and
injects the instance, so it never touches the ``.random`` submodule); (b) the stdlib ``random``
module; (c) wall-clock reads ``time.time`` / ``datetime.now`` / ``datetime.utcnow``. The negative
self-test confirms ``from numpy.random import RandomState`` is NOT flagged (it is the local
instance the design requires).
"""
from __future__ import annotations

import ast

from backend.outlier_model.tests import structural

_NUMPY_NAMES = {"np", "numpy"}
_WALLCLOCK = {("time", "time"), ("datetime", "now"), ("datetime", "utcnow")}


def _uses_numpy_global_random(tree: ast.AST) -> list[str]:
    """``np.random.<x>`` / ``numpy.random.<x>`` attribute chains (global RNG submodule access)."""
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute):
            inner = node.value
            if (
                inner.attr == "random"
                and isinstance(inner.value, ast.Name)
                and inner.value.id in _NUMPY_NAMES
            ):
                hits.append(f"{inner.value.id}.random.{node.attr}")
    return hits


def _uses_stdlib_random(tree: ast.AST) -> bool:
    return "random" in structural.imported_modules(tree)


def _uses_wallclock(tree: ast.AST) -> list[str]:
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if (node.value.id, node.attr) in _WALLCLOCK:
                hits.append(f"{node.value.id}.{node.attr}")
    return hits


def test_no_global_rng_or_wallclock_in_production():
    offenders: list[str] = []
    for path in structural.production_py_files():
        tree = structural.parse(path)
        if _uses_numpy_global_random(tree):
            offenders.append(f"{path.name}: {_uses_numpy_global_random(tree)}")
        if _uses_stdlib_random(tree):
            offenders.append(f"{path.name}: imports stdlib random")
        if _uses_wallclock(tree):
            offenders.append(f"{path.name}: {_uses_wallclock(tree)}")
    assert offenders == [], f"global-RNG / wall-clock usage found: {offenders}"


def test_scan_sees_the_real_production_modules():
    names = {p.name for p in structural.production_py_files()}
    assert structural.EXPECTED_PRODUCTION_MODULES <= names


def test_detector_flags_synthetic_global_rng():
    assert _uses_numpy_global_random(structural.parse_source("import numpy as np\nnp.random.random(3)\n"))
    assert _uses_numpy_global_random(structural.parse_source("import numpy\nnumpy.random.seed(0)\n"))
    assert _uses_stdlib_random(structural.parse_source("import random\nrandom.random()\n"))
    assert _uses_wallclock(structural.parse_source("import time\nt = time.time()\n"))


def test_detector_allows_the_sanctioned_local_randomstate():
    # NEGATIVE self-test: the injected local instance path must NOT be flagged.
    tree = structural.parse_source("from numpy.random import RandomState\nrng = RandomState(5)\n")
    assert not _uses_numpy_global_random(tree)
    assert not _uses_stdlib_random(tree)
