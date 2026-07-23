"""Shared substrate for the U23 deploy_validators scans (C-DEP-1 / P-DEP-1..11).

pytest is the RUNNER; the teeth are **config-validation / file-presence / structural-scan** checks
over the **actual committed deploy artifacts** — not application behavior (DEP-D8 / Q1-A). Every
scan-bearing target carries a detector self-test (Req-Fold-3). No live cloud deploy, no network,
no secret value.
"""
from __future__ import annotations

import ast
import json
import pathlib
import re

import yaml

# backend/deploy_config/tests/structural.py -> parents[3] == repo root
REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]

# --- the U23-owned committed deploy artifacts (DEP-D8 RESOLVED — final locations) ---
RENDER_YAML = "render.yaml"
VERCEL_JSON = "frontend/vercel.json"
INDEX_HTML = "frontend/index.html"
MAIN_JSX = "frontend/src/main.jsx"
VITE_CONFIG = "frontend/vite.config.js"
FRONTEND_PKG = "frontend/package.json"
DEPLOY_DIR = "deploy"
GRAFANA_DASHBOARD = "deploy/grafana-dashboard.json"
PROM_SCRAPE = "deploy/prometheus-scrape.yml"
DEPLOY_DOC = "deploy/README.md"

#: The committed deploy artifacts scanned for secrets / tokens / format (SEC3-1, DOC-1, format).
U23_ARTIFACTS = [
    RENDER_YAML,
    VERCEL_JSON,
    INDEX_HTML,
    MAIN_JSX,
    VITE_CONFIG,
    GRAFANA_DASHBOARD,
    PROM_SCRAPE,
    DEPLOY_DOC,
]


def path(rel: str) -> pathlib.Path:
    return REPO_ROOT / rel


def read(rel: str) -> str:
    return path(rel).read_text(encoding="utf-8")


def exists(rel: str) -> bool:
    return path(rel).exists()


def load_yaml(rel: str) -> object:
    return yaml.safe_load(read(rel))


def load_json(rel: str) -> object:
    return json.loads(read(rel))


# --- NOEDIT-1 (P-DEP-1): the frozen-vs-allowed path classifier ---------------
def is_under_frozen(rel: str) -> bool:
    """True iff a repo-relative path lies under a FROZEN tree — any ``backend/<unit>/…`` except
    ``deploy_config`` (incl. the ``backend/app`` composition root), or any ``frontend/src/<unit>/…``
    (incl. ``frontend/src/app``). U23's own paths (root ``render.yaml``, ``frontend/{vercel.json,
    index.html,src/main.jsx,vite.config.js}``, ``deploy/…``, ``backend/deploy_config/…``) are NOT frozen."""
    parts = rel.replace("\\", "/").split("/")
    if parts[0] == "backend" and len(parts) >= 3 and parts[1] != "deploy_config":
        return True
    if parts[:2] == ["frontend", "src"] and len(parts) >= 4:
        return True
    return False


# --- SEC3-1 (P-DEP-2): credential-value patterns (Fold-1: public host NOT a credential) ---
_CREDENTIAL_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{8,}"),                         # api key literal
    re.compile(r"pk-[A-Za-z0-9]{8,}"),                         # api key literal
    re.compile(r"postgresql://[^\s:/]+:[^\s@/]+@"),            # credential-bearing conn string
    re.compile(r"(?:SECRET|PASSWORD|API_KEY)\s*[:=]\s*[\"']?[^\s\"'{}$<]{6,}"),  # NAME = value
]


def secret_value_offenders(text: str) -> list[str]:
    """Every credential-value match in ``text``. A bare NAME shape (no value) and a public host
    (``REPLACE_WITH_RENDER_BACKEND_HOST`` / a plain ``https://host``) are NOT credentials (Fold-1)."""
    hits: list[str] = []
    for pattern in _CREDENTIAL_PATTERNS:
        hits.extend(m.group(0) for m in pattern.finditer(text))
    return hits


# --- config-token helpers (FREETIER-1, DOC-1) --------------------------------
_PAID_TIER_TOKENS = ("plan: starter", "plan: standard", "plan: pro", "plan: team")


def contains_any(text: str, tokens) -> list[str]:
    return [t for t in tokens if t in text]


# --- AST import detection (SCOPE-1 / ROUTES-1 — robust vs token-as-DATA self-matching) ---
def imported_modules(source: str) -> set[str]:
    """Top-level absolute module names imported by ``source`` (via ``ast``, so a name appearing
    only as a string/comment literal is NOT counted)."""
    tree = ast.parse(source)
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules.add(node.module)
    return modules


def import_roots(source: str) -> set[str]:
    return {m.split(".")[0] for m in imported_modules(source)}


def deploy_config_py_files() -> list[pathlib.Path]:
    return list((REPO_ROOT / "backend" / "deploy_config").rglob("*.py"))
