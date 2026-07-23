"""NFR-DEP-SCOPE-1: the OBS deployment half is present; the code-attachment half + MCP transport
are absent (Q1-A / DEP-FD-Fold-1). Plus the Fold-3 no-drift assertion: the Grafana dashboard's
five panels EXACTLY match observability's frozen metric topology.
"""
from __future__ import annotations

import pathlib

from backend.observability.metrics import METRIC_DEFINITIONS
from backend.deploy_config.tests import structural as sg


def test_observability_deployment_half_is_present():
    assert sg.exists(sg.GRAFANA_DASHBOARD)
    assert sg.exists(sg.PROM_SCRAPE)
    render_keys = {ev["key"] for ev in sg.load_yaml(sg.RENDER_YAML)["services"][0]["envVars"]}
    assert {"LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_HOST"} <= render_keys


def test_grafana_dashboard_panels_match_observabilitys_frozen_five_no_drift():
    # Fold-3: observability OWNS the panel topology (its metrics.py is the authority); deploy-config
    # owns the committed file that REALIZES it. The dashboard's panel exprs must be EXACTLY the five
    # frozen metric names — no sixth panel, no drift.
    dashboard = sg.load_json(sg.GRAFANA_DASHBOARD)
    panels = dashboard["panels"]
    assert len(panels) == 5
    dashboard_metrics = {p["targets"][0]["expr"] for p in panels}
    frozen_metrics = {m.name for m in METRIC_DEFINITIONS}
    assert dashboard_metrics == frozen_metrics
    assert dashboard["panels"][1]["datasource"] == "Prometheus"


_FORBIDDEN_SCOPE_IMPORTS = {"langgraph", "mcp", "langfuse"}


def test_no_live_binding_or_mcp_import_under_deploy_config():
    # U23 wires the deployment half only; the live langfuse callback attachment + the MCP transport
    # binding are composition/application's. AST import detection (not substring) so a token that
    # appears only as scan DATA is not misread as a dependency.
    for py in sg.deploy_config_py_files():
        roots = sg.import_roots(py.read_text(encoding="utf-8"))
        assert not (roots & _FORBIDDEN_SCOPE_IMPORTS), f"{py.name} imports a forbidden scope dep"


def test_detector_flags_a_synthetic_live_binding_import():
    roots = sg.import_roots("import langgraph\nfrom langfuse import Langfuse\n")
    assert {"langgraph", "langfuse"} <= roots
