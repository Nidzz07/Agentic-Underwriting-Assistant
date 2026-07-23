"""NFR-DEP-BUILD-1: the frontend build produces a static bundle Vercel serves. Honest two-part
(P-DEP-5): (a) a tier-U presence/reference check; (b) the actual bundle build is a deploy-time
fact, named-not-tested (observed-never-gated).
"""
from __future__ import annotations

import json

from backend.deploy_config.tests import structural as sg


def test_build_entry_files_exist():
    # (a) presence
    assert sg.exists(sg.INDEX_HTML)
    assert sg.exists(sg.MAIN_JSX)
    assert sg.exists(sg.VITE_CONFIG)
    assert sg.exists(sg.VERCEL_JSON)


def test_index_html_references_the_main_entry():
    assert "/src/main.jsx" in sg.read(sg.INDEX_HTML)


def test_main_entry_mounts_the_frozen_app():
    main = sg.read(sg.MAIN_JSX)
    assert "from './app/App.jsx'" in main
    assert "createRoot" in main and "root" in main


def test_package_json_has_a_build_script():
    pkg = json.loads(sg.read(sg.FRONTEND_PKG))
    assert pkg["scripts"].get("build") == "vite build"


def test_vercel_config_builds_a_static_bundle():
    vercel = sg.load_json(sg.VERCEL_JSON)
    assert vercel["buildCommand"] == "npm run build"
    assert vercel["outputDirectory"] == "dist"


def test_actual_bundle_build_is_a_deploy_time_fact_not_tested_here():
    # (b) named deploy-time fact (P-DEP-5b): the real `vite build` producing `dist/` is verified at
    # Infrastructure Design / deploy, observed-never-gated — NOT a tier-U assertion. This test
    # documents that boundary; it asserts no build behavior.
    assert True
