"""PII-1 — zero real PII: governance note + light structural (Q4-A).

Governance: all data is synthetic (Faker structured fields + build-authored Gemini
prose over synthetic inputs); the unit finalizes no decision. Light structural: the
generation path (excluding the tier-B ``build.py``) reads NO external-identifier
source and makes NO network read — the only network is the injected Gemini seam at
tier B, mocked in CI.
"""
from __future__ import annotations

import ast
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parents[1]
_EXCLUDED_FILES = {"build.py"}                 # tier-B real-client entrypoint (the only network)
_NETWORK_MODULES = {"requests", "httpx", "urllib", "urllib.request", "socket", "http", "http.client"}


def _generation_files() -> list[Path]:
    return [p for p in PKG_DIR.glob("*.py") if p.name not in _EXCLUDED_FILES]


def _imported_roots(source: str) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            roots.update(a.name for a in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module)
    return roots


def test_generation_path_makes_no_network_read():
    for path in _generation_files():
        imports = _imported_roots(path.read_text(encoding="utf-8"))
        offending = imports & _NETWORK_MODULES
        assert not offending, f"{path.name} imports network module(s): {offending}"


def test_generation_path_reads_no_external_identifier_source():
    # no os.environ / os.getenv reads in the generation path (secrets are tier-B only)
    for path in _generation_files():
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                assert not (node.value.id == "os" and node.attr in {"environ", "getenv"}), path.name


def test_data_is_synthetic_by_construction():
    # governance: the factory uses Faker (synthetic) + the injected prose seam only.
    factory_src = (PKG_DIR / "profile_factory.py").read_text(encoding="utf-8")
    assert "from faker import Faker" in factory_src
