"""NFR-DEP-NOEDIT-1 (LOAD-BEARING — full-highest): no U23 deliverable edits any frozen unit or
the composition root; U23 authors only root-level declarative config + the frontend build entry +
a test-only backend/deploy_config/ (BR-DEP-1).
"""
from __future__ import annotations

import json

from backend.deploy_config.tests import structural as sg


def test_every_u23_artifact_is_outside_every_frozen_tree():
    for rel in sg.U23_ARTIFACTS + [sg.FRONTEND_PKG]:
        assert not sg.is_under_frozen(rel), rel


def test_the_deploy_validators_live_only_under_backend_deploy_config():
    # backend/deploy_config/ is the ONLY backend tree U23 authors, and it is test-only.
    assert not sg.is_under_frozen("backend/deploy_config/tests/structural.py")


def test_frontend_package_json_change_is_additive_only():
    # U23 adds ONLY the `build` script (the sanctioned deliverable package.json's description
    # reserves) — the frozen test/lint scripts + deps are untouched.
    pkg = json.loads(sg.read(sg.FRONTEND_PKG))
    assert pkg["scripts"]["build"] == "vite build"
    assert pkg["scripts"]["test"] == "vitest run"          # frozen script preserved
    assert pkg["scripts"]["lint"] == "eslint ."            # frozen script preserved
    assert "react" in pkg["dependencies"]                  # frozen deps preserved


def test_main_jsx_imports_the_frozen_app_never_redefines_it():
    main = sg.read(sg.MAIN_JSX)
    assert "from './app/App.jsx'" in main                  # imports the frozen App
    assert "function App" not in main                      # does not redefine it


def test_detector_flags_a_synthetic_frozen_path_write():
    # Non-vacuity: the classifier must flag writes into frozen trees + the composition root.
    assert sg.is_under_frozen("backend/app/main.py")               # composition root
    assert sg.is_under_frozen("backend/memo_agent_core/orchestrator.py")
    assert sg.is_under_frozen("frontend/src/app/App.jsx")          # composition root (fe)
    assert sg.is_under_frozen("frontend/src/history/HistoryView.jsx")
    # ...and NOT flag U23's own allowed locations
    assert not sg.is_under_frozen("render.yaml")
    assert not sg.is_under_frozen("frontend/src/main.jsx")
    assert not sg.is_under_frozen("deploy/README.md")
