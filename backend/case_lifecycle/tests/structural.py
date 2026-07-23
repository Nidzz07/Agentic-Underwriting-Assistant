"""C-CASE-8 — the shared AST/token scan substrate (P-CASE-14).

Parses every PRODUCTION ``.py`` under ``backend/case_lifecycle/`` (EXCLUDING ``tests/``) with
``ast``. Mirrors the frozen ``observability`` / ``memo_extensions`` / ``outlier_model`` /
``llm_judge`` substrates. Each scan in its target's test file carries a detector self-test.

⚑ **``repository.py`` IS IN THE PRODUCTION SCAN SET** even though it is omitted from coverage
(CASE-Req-Fold-3). The coverage omit governs *where a module is exercised*; the scan governs
*what it may contain*. Conflating them would make a hidden ``canon_ser(...)`` call structurally
invisible.
"""
from __future__ import annotations

import ast
import json
import pathlib
import re

UNIT_DIR = pathlib.Path(__file__).resolve().parent.parent
REPO_ROOT = UNIT_DIR.parent.parent

#: The eight production modules (non-vacuity guard). ``__init__.py`` is scanned but not required.
#: ⚑ ``memo_adapter.py`` added by U24's THIRD AUTHORIZED REOPENING (Q14-A). Contrast with the
#: list-method reopening (Q1-A), which added METHODS to existing modules and therefore correctly
#: left this set UNCHANGED — opposite calls, opposite reasons, both deliberate.
EXPECTED_PRODUCTION_MODULES = {
    "states.py",
    "schemas.py",
    "store.py",
    "repository.py",
    "pipeline.py",
    "provider.py",
    "migrate.py",
    "memo_adapter.py",
}

#: The frozen artifacts NOMETRIC-1 corroborates against — READ-ONLY, no suite re-run.
OBSERVABILITY_METRICS = REPO_ROOT / "backend" / "observability" / "metrics.py"
GRAFANA_DASHBOARD = REPO_ROOT / "deploy" / "grafana-dashboard.json"

#: ADAPTER-1 — canonicalization must go through the frozen adapter, never directly.
FORBIDDEN_CANON_CALLS = ("canon_ser", "canon_deserialize")

#: ⚑ ADAPTER-1, NARROWED (Q14-A) — the SERIALIZE direction, forbidden with NO exception anywhere.
#: U24 canonicalizes ONLY through the frozen ``CanonSerAdapter``. This never gets an allowlist.
FORBIDDEN_CANON_CALLS_UNIVERSAL = ("canon_ser",)

#: ⚑ The DESERIALIZE direction, permitted in EXACTLY ONE module and forbidden in every other.
#: WIRE-1 §5 binds R4's ``ready`` view to a PRESENT memo, and the frozen adapter rehydrates only
#: ``ApplicantProfile``/``RuleResultReport`` — so U24 owns its memo counterpart, following the
#: same per-unit thin-adapter convention every other unit already uses (``intake`` /
#: ``rules_engine`` / ``audit_store`` / ``memo_agent_core`` each have one).
#:
#: ⚑ This is a NARROWING, not a weakening. Before: no module may call it. After: exactly one
#: designated module may, for rehydration only, and its THINNESS is positively asserted.
CANON_DESERIALIZE_ALLOWLIST = {"memo_adapter.py"}

#: COMMITBOUND-1 — U24 must implement none of these.
FORBIDDEN_COMMIT_TOKENS = ("audit_record", "authorize", "RBAC_COMMIT")

#: NOMETRIC-1 — U24 declares no metric.
METRIC_TOKENS = ("MetricDefinition", "METRIC_DEFINITIONS", "Counter", "Histogram", "Gauge")


def production_py_files() -> list[pathlib.Path]:
    """Every ``.py`` under the unit EXCLUDING the ``tests`` package."""
    return [p for p in UNIT_DIR.rglob("*.py") if "tests" not in p.parts]


def authored_py_files() -> list[pathlib.Path]:
    return sorted(UNIT_DIR.rglob("*.py"))


def module_file(name: str) -> pathlib.Path:
    return UNIT_DIR / name


def parse(path: pathlib.Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def parse_source(source: str) -> ast.AST:
    return ast.parse(source)


def called_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                names.add(node.func.attr)
    return names


def assigned_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def keyword_values(tree: ast.AST, keyword: str) -> list[str]:
    """Every literal passed as ``keyword=`` — used to flag ``model_dump(mode="json")``."""
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == keyword and isinstance(kw.value, ast.Constant):
                    out.append(str(kw.value.value))
    return out


def imported_roots(tree: ast.AST) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            roots.add(node.module.split(".")[0])
    return roots


def string_constants(tree: ast.AST) -> list[str]:
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


def _docstrings(tree: ast.AST) -> set[int]:
    """``id()`` of every docstring node — module, class and function level."""
    out: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                if isinstance(body[0].value.value, str):
                    out.add(id(body[0].value))
    return out


def executable_text(tree: ast.AST) -> str:
    """Every identifier + NON-docstring string literal, joined.

    ⚑ Docstrings are EXCLUDED deliberately. A header comment that *documents a prohibition*
    ("never writes to audit_record") must not be mistaken for the prohibited thing itself —
    otherwise the scan flags its own documentation and the only way to pass would be to delete
    the disclosure. Structure-aware, not text-matching.
    """
    docs = _docstrings(tree)
    parts: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            parts.append(node.id)
        elif isinstance(node, ast.Attribute):
            parts.append(node.attr)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom) and node.module:
                parts.append(node.module)
            for alias in node.names:
                parts.append(alias.name)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) not in docs:
                parts.append(node.value)
    return " ".join(parts)


def annotation_names(tree: ast.AST) -> set[str]:
    """Every annotation type name used (dataclass fields + returns), by exact identifier."""
    names: set[str] = set()

    def _walk_ann(node: ast.AST) -> None:
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name):
                names.add(sub.id)
            elif isinstance(sub, ast.Attribute):
                names.add(sub.attr)
            elif isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                names.add(sub.value)

    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and node.annotation is not None:
            _walk_ann(node.annotation)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is not None:
                _walk_ann(node.returns)
            for arg in [*node.args.args, *node.args.kwonlyargs]:
                if arg.annotation is not None:
                    _walk_ann(arg.annotation)
    return names


def sql_without_comments(sql: str) -> str:
    """SQL with ``--`` comment lines stripped.

    ⚑ Same reasoning as :func:`executable_text`: a migration comment saying "NO GRANTS HERE"
    must not be read as a ``GRANT``.
    """
    return "\n".join(
        line for line in sql.splitlines() if not line.lstrip().startswith("--")
    )


def contains_token(haystack: str, token: str) -> bool:
    """WORD-BOUNDARY match — a naive substring test produces false positives."""
    return re.search(rf"\b{re.escape(token)}\b", haystack, flags=re.IGNORECASE) is not None


def load_dashboard() -> dict:
    """Read ``deploy/grafana-dashboard.json`` READ-ONLY. `deploy-config`'s suite is NOT re-run."""
    return json.loads(GRAFANA_DASHBOARD.read_text(encoding="utf-8"))
