"""NFR-DEP-FREETIER-1: free-tier only; validation/staging, not production (NFR-CONSTRAINTS-1 /
OOS-4).
"""
from __future__ import annotations

from backend.deploy_config.tests import structural as sg


def test_render_service_is_free_tier():
    svc = sg.load_yaml(sg.RENDER_YAML)["services"][0]
    assert svc["plan"] == "free"


def test_no_paid_tier_token_in_render_yaml():
    assert sg.contains_any(sg.read(sg.RENDER_YAML), sg._PAID_TIER_TOKENS) == []


def test_detector_flags_a_synthetic_paid_tier_token():
    assert sg.contains_any("plan: standard\n", sg._PAID_TIER_TOKENS) == ["plan: standard"]
