"""NFR-DEP-SEC3-1 (LOAD-BEARING — full-highest): no secret/key/URL VALUE in any committed U23
artifact — only variable-name SHAPES (SEC-3). The public ``RENDER_BACKEND_URL`` host is permitted
(a public endpoint is not a credential — Fold-1).
"""
from __future__ import annotations

from backend.deploy_config.tests import structural as sg


def test_no_secret_value_in_any_committed_u23_artifact():
    for rel in sg.U23_ARTIFACTS:
        offenders = sg.secret_value_offenders(sg.read(rel))
        assert offenders == [], f"{rel} carries a credential value: {offenders}"


def test_detector_flags_synthetic_credential_values():
    # Non-vacuity of the FLAG side.
    assert sg.secret_value_offenders('LANGFUSE_SECRET_KEY="sk-abcd1234efgh5678"')
    assert sg.secret_value_offenders("DATABASE_URL=postgresql://appuser:s3cr3tpw@db.host:5432/app")
    assert sg.secret_value_offenders("GEMINI_API_KEY=AIzaSyReal0Key0Value0Here")


def test_permit_side_is_not_over_broad():
    # Non-vacuity of the PERMIT side (Fold-1): bare NAME shapes + a public host are NOT credentials.
    assert sg.secret_value_offenders("- key: LANGFUSE_SECRET_KEY") == []
    assert sg.secret_value_offenders("    sync: false") == []
    assert sg.secret_value_offenders("https://REPLACE_WITH_RENDER_BACKEND_HOST/:path*") == []
    assert sg.secret_value_offenders("targets:\n  - REPLACE_WITH_RENDER_BACKEND_HOST") == []
    assert sg.secret_value_offenders("destination: https://underwriting-backend.onrender.com") == []


def test_render_yaml_env_vars_are_names_only_sync_false():
    render = sg.load_yaml(sg.RENDER_YAML)
    env_vars = render["services"][0]["envVars"]
    for ev in env_vars:
        assert set(ev.keys()) == {"key", "sync"}     # NO `value` key ever
        assert ev["sync"] is False
