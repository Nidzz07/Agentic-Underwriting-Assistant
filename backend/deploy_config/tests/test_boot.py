"""NFR-DEP-BOOT-1: the backend boots on Render via the fail-closed Settings. Honest two-part
(P-DEP-5): (a) a tier-U presence check on render.yaml; (b) the actual boot is a deploy-time fact,
named-not-tested.
"""
from __future__ import annotations

from backend.deploy_config.tests import structural as sg

#: The six Phase-1 shapes the fail-closed Settings requires at construction.
_PHASE1_REQUIRED = {
    "DATABASE_URL",
    "AUDIT_WRITER_URL",
    "AUDIT_READER_URL",
    "AUDIT_WRITER_PASSWORD",
    "AUDIT_READER_PASSWORD",
    "GEMINI_API_KEY",
}


def _service(render):
    return render["services"][0]


def test_start_command_runs_the_frozen_composition_root():
    svc = _service(sg.load_yaml(sg.RENDER_YAML))
    assert "backend.app.main:app" in svc["startCommand"]
    assert svc["runtime"] == "python"


def test_env_manifest_lists_the_six_phase1_required_shapes():
    svc = _service(sg.load_yaml(sg.RENDER_YAML))
    keys = {ev["key"] for ev in svc["envVars"]}
    assert _PHASE1_REQUIRED <= keys


def test_migration_release_step_is_wired_before_traffic():
    # DEPLOY-MIGRATE-DEFERRED: the preDeployCommand slot is wired (WHEN it runs); the runnable
    # entrypoint is database's/composition's (reference-not-own).
    svc = _service(sg.load_yaml(sg.RENDER_YAML))
    assert "preDeployCommand" in svc


def test_detector_flags_a_missing_required_shape():
    keys = {"DATABASE_URL"}                      # a manifest missing five required shapes
    assert not (_PHASE1_REQUIRED <= keys)


def test_actual_boot_is_a_deploy_time_fact_not_tested_here():
    # (b) named deploy-time fact (P-DEP-5b): the real uvicorn boot + Settings construction is
    # verified at deploy, observed-never-gated — NOT a tier-U assertion.
    assert True
