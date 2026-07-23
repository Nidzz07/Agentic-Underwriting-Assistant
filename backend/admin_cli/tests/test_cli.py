"""C1 ArgparseEntrypoint — dispatch + typed-error->exit-code + no-secret (CLIERR-1/NOSECRET-1).

Tier U: ``main`` is injection-pure, driven with a fake engine + ``tmp_path`` (no Docker).
"""
from __future__ import annotations

import io
import pathlib

import pytest

from backend.admin_cli import cli

from backend.admin_cli.tests.test_app_user_writer import SpyEngine

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_VALID_SOURCE = _REPO_ROOT / "backend" / "rules_engine" / "rulebook" / "1.0.0.yaml"


def _run(argv, engine, rulebook_dir):
    out, err = io.StringIO(), io.StringIO()
    code = cli.main(argv, engine=engine, rulebook_dir=rulebook_dir, out=out, err=err)
    return code, out.getvalue(), err.getvalue()


def test_publish_success_exit_zero_names_only(tmp_path):
    src = tmp_path / "src.yaml"
    src.write_text(_VALID_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
    code, out, err = _run(["publish-rulebook", "1.0.0", str(src)], SpyEngine(), tmp_path)
    assert code == 0
    assert out.strip() == "published rulebook 1.0.0"
    assert err == ""


def test_create_user_success(tmp_path):
    code, out, err = _run(["create-user", "u1", "s1", "admin"], SpyEngine(rowcount=1), tmp_path)
    assert code == 0
    assert out.strip() == "created user u1 (admin)"


def test_set_role_success(tmp_path):
    code, out, err = _run(["set-role", "u1", "auditor"], SpyEngine(rowcount=1), tmp_path)
    assert code == 0
    assert out.strip() == "set role for u1 -> auditor"


def test_invalid_role_maps_to_exit_code_and_no_secret_stderr(tmp_path):
    code, out, err = _run(["create-user", "u1", "s1", "superuser"], SpyEngine(), tmp_path)
    assert code == 4  # RoleValidationError.exit_code
    assert err.strip() == "error: invalid role 'superuser'"


def test_set_role_absent_user_maps_to_exit_code(tmp_path):
    code, out, err = _run(["set-role", "ghost", "admin"], SpyEngine(rowcount=0), tmp_path)
    assert code == 3  # UserWriteError.exit_code
    assert err.strip() == "error: no such user ghost"


def test_republish_maps_to_exit_code(tmp_path):
    src = tmp_path / "src.yaml"
    src.write_text(_VALID_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
    _run(["publish-rulebook", "1.0.0", str(src)], SpyEngine(), tmp_path)
    code, out, err = _run(["publish-rulebook", "1.0.0", str(src)], SpyEngine(), tmp_path)
    assert code == 2  # RulebookPublishError.exit_code
    assert "already exists" in err


def test_no_secret_value_in_any_output(tmp_path):
    # Behavioural NOSECRET-1 half: no URL/credential VALUE leaks into stdout/stderr.
    code, out, err = _run(["create-user", "u1", "s1", "superuser"], SpyEngine(), tmp_path)
    for stream in (out, err):
        assert "postgresql://" not in stream
        assert "password" not in stream.lower()
