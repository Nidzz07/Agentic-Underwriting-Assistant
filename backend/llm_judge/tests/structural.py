"""Shared AST/path/token scan substrate for the U22 StructuralGuard (C-JUDGE-5 / P-JUDGE-13).

Parses every PRODUCTION ``.py`` file under ``backend/llm_judge/`` (EXCLUDING ``tests/``) with
``ast`` — robust against comments/strings a text scan would misfire on. Mirrors the frozen
``observability`` / ``memo_extensions`` / ``outlier_model`` ``structural.py`` precedent. Each
scan in ``test_structural_guard.py`` carries its own detector self-test + non-vacuity guard.

⚑ **Scope asymmetry is DELIBERATE** (CG-JUDGE-Fold-2 / Fold-3):
  * ADVISORY-1's VERDICT-token scan runs over PRODUCTION ONLY — the frozen U4
    ``DecisionMemo.recommendation`` field is REQUIRED, so fixtures MUST carry a verdict; that
    is the memo under judgment (judge INPUT), never judge OUTPUT.
  * NODEMO-1's DEMOGRAPHIC-token scan ALSO covers ``tests/fixtures.py`` — because the FD
    explicitly requires the hand-authored REFERENCE MEMO be demographic-free.
"""
from __future__ import annotations

import ast
import json
import pathlib
import re

# backend/llm_judge/  (parent of this tests/ dir)
UNIT_DIR = pathlib.Path(__file__).resolve().parent.parent
# repo root: backend/llm_judge -> backend -> <root>
REPO_ROOT = UNIT_DIR.parent.parent

# The production modules that MUST be in every scan set (non-vacuity guard).
EXPECTED_PRODUCTION_MODULES = {"rubric.py", "schemas.py", "pipeline.py", "engine.py"}

FIXTURES_MODULE = UNIT_DIR / "tests" / "fixtures.py"

# NOEDIT-1: the only tree U22 may author into.
ALLOWED_U22_PREFIXES = ("backend/llm_judge",)

# NOEDIT-1: trees U22 must never write into (frozen units + the CLOSED composition root).
FROZEN_PREFIXES = (
    "backend/app",
    "backend/intake",
    "backend/common",
    "backend/rules_engine",
    "backend/audit_store",
    "backend/memo_agent_core",
    "backend/database",
    "backend/auth_rbac",
    "backend/secrets_config",
    "backend/corpus_generator",
    "backend/quality_gates",
    "backend/admin_cli",
    "backend/outlier_model",
    "backend/memo_extensions",
    "backend/observability",
    "backend/deploy_config",
    "frontend/src",
)

# CLIDEFER-1: the external engine U22 production must never import.
FORBIDDEN_PRODUCTION_IMPORTS = {"promptfoo"}

# ADVISORY-1: bare verdict tokens (production only — see the scope note above).
VERDICT_TOKENS = ("APPROVE", "REFER", "DECLINE")

# NODEMO-1: demographic attribute names that must never appear.
DEMOGRAPHIC_TOKENS = (
    "full_name",
    "gender",
    "city",
    "demographics",
    "ethnicity",
    "religion",
    "marital_status",
)

# NOMETRIC-1: U22 declares no metric.
METRIC_TOKENS = ("MetricDefinition", "METRIC_DEFINITIONS", "Counter", "Histogram", "Gauge")

# The frozen artifacts NOMETRIC-1 corroborates against — READ-ONLY, no suite re-run.
OBSERVABILITY_METRICS = REPO_ROOT / "backend" / "observability" / "metrics.py"
GRAFANA_DASHBOARD = REPO_ROOT / "deploy" / "grafana-dashboard.json"


def production_py_files() -> list[pathlib.Path]:
    """Every ``.py`` under ``backend/llm_judge/`` EXCLUDING the ``tests`` package."""
    return [p for p in UNIT_DIR.rglob("*.py") if "tests" not in p.parts]


def authored_py_files() -> list[pathlib.Path]:
    """Every ``.py`` U22 authored — production AND tests (NOEDIT-1's path scan subject)."""
    return sorted(UNIT_DIR.rglob("*.py"))


def repo_relative(path: pathlib.Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def parse(path: pathlib.Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def parse_source(source: str) -> ast.AST:
    return ast.parse(source)


def imported_roots(tree: ast.AST) -> set[str]:
    """Top-level module roots imported by a parsed tree (incl. ``TYPE_CHECKING``)."""
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                roots.add(node.module.split(".")[0])
    return roots


def annotation_names(tree: ast.AST) -> set[str]:
    """Every annotation type name used (dataclass fields + returns) — ADVISORY-1's
    structural half: a ``Recommendation``-typed field would surface here."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and node.annotation is not None:
            names |= _ann_names(node.annotation)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns:
            names |= _ann_names(node.returns)
    return names


def _ann_names(node: ast.AST) -> set[str]:
    out: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name):
            out.add(sub.id)
        elif isinstance(sub, ast.Attribute):
            out.add(sub.attr)
        elif isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            out.add(sub.value)
    return out


def called_names(tree: ast.AST) -> set[str]:
    """Every callee name — NOMETRIC-1's provenance scan surfaces ``MetricDefinition(...)``."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                names.add(node.func.attr)
    return names


def assigned_names(tree: ast.AST) -> set[str]:
    """Every module-level assignment target name (a metric CONSTANT would surface here)."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def string_constants(tree: ast.AST) -> list[str]:
    """Every string literal (docstrings included) — the token scans' subject."""
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


def contains_token(haystack: str, token: str) -> bool:
    """WORD-BOUNDARY match, deliberately not a naive substring test.

    A substring test produces false positives that would make the demographic scan
    dishonest: ``"ethnicity"`` contains ``"city"``, so a bare ``in`` would flag the wrong
    token and mask which attribute actually appeared.
    """
    return re.search(rf"\b{re.escape(token)}\b", haystack, flags=re.IGNORECASE) is not None


def load_dashboard() -> dict:
    """Read ``deploy/grafana-dashboard.json`` READ-ONLY (import-to-read != edit).
    ``deploy-config``'s suite is NOT re-run."""
    return json.loads(GRAFANA_DASHBOARD.read_text(encoding="utf-8"))
