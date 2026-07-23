"""NFR-DEP (P-DEP-8) ConfigFormatValidation — supporting: the config artifacts are well-formed
and name their expected keys (a precondition of the token/presence scans). `render.yaml` via
`pyyaml`; `vercel.json` + `grafana-dashboard.json` via stdlib `json`.
"""
from __future__ import annotations

from backend.deploy_config.tests import structural as sg


def test_render_yaml_is_well_formed_and_names_expected_keys():
    render = sg.load_yaml(sg.RENDER_YAML)
    assert isinstance(render["services"], list) and render["services"]
    svc = render["services"][0]
    for key in ("type", "runtime", "plan", "buildCommand", "startCommand", "envVars"):
        assert key in svc
    assert svc["type"] == "web"


def test_vercel_json_is_well_formed_with_a_rewrite():
    vercel = sg.load_json(sg.VERCEL_JSON)
    assert "buildCommand" in vercel and "outputDirectory" in vercel
    rewrites = vercel["rewrites"]
    assert rewrites and rewrites[0]["source"] == "/api/:path*"
    # the rewrite proxies to the backend host SHAPE (Fold-1) — same-origin, no CORS
    assert "REPLACE_WITH_RENDER_BACKEND_HOST" in rewrites[0]["destination"]


def test_grafana_dashboard_is_well_formed_json():
    dashboard = sg.load_json(sg.GRAFANA_DASHBOARD)
    assert "panels" in dashboard and isinstance(dashboard["panels"], list)


def test_prometheus_scrape_is_well_formed_yaml():
    scrape = sg.load_yaml(sg.PROM_SCRAPE)
    job = scrape["scrape_configs"][0]
    assert job["metrics_path"] == "/metrics"
