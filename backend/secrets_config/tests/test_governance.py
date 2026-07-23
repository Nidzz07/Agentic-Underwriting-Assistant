"""Unit/structural tests — NFR-SEC-GOV-1 governance checkability (Step 4).

Four checkable governance pieces + the .env.example<->Settings drift guard (fold 2/3).
The repo root is located ROBUSTLY (walk up to the pyproject.toml / .git marker), not a
brittle fixed parent count.
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess

import pytest

from backend.secrets_config import settings as settings_module
from backend.secrets_config.settings import Settings
from backend.secrets_config.tests.conftest import VALID_ENV


def _repo_root() -> pathlib.Path:
    """Walk up from this test file to the dir holding pyproject.toml or .git."""
    for parent in pathlib.Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    raise RuntimeError("repo root not found (no pyproject.toml / .git marker)")


REPO_ROOT = _repo_root()
ENV_EXAMPLE = REPO_ROOT / ".env.example"
GITIGNORE = REPO_ROOT / ".gitignore"


def _active_keys(text: str) -> set[str]:
    """A line is an ACTIVE key iff it does NOT start with '#' and contains '=' — the
    token before '=' (stripped). Commented '# KEY=' (Phase-2 reserved) lines excluded."""
    keys: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            keys.add(stripped.split("=", 1)[0].strip())
    return keys


# --------------------------------------------------------------------------
# BR-SEC-3 — .env gitignored + not tracked; .env.example placeholder-only
# --------------------------------------------------------------------------
def test_gitignore_lists_dotenv():
    lines = {line.strip() for line in GITIGNORE.read_text(encoding="utf-8").splitlines()}
    assert ".env" in lines


def test_dotenv_not_git_tracked():
    if shutil.which("git") is None or not (REPO_ROOT / ".git").exists():
        pytest.skip("git unavailable")
    out = subprocess.run(
        ["git", "ls-files", ".env"], cwd=REPO_ROOT, capture_output=True, text=True
    )
    assert out.stdout.strip() == ""  # .env is not tracked


def test_env_example_is_committed_and_placeholder_only():
    assert ENV_EXAMPLE.exists()
    text = ENV_EXAMPLE.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        _, value = stripped.split("=", 1)
        assert "CHANGE_ME" in value, f"non-placeholder value in .env.example: {line!r}"


# --------------------------------------------------------------------------
# BR-SEC-4 — no default on required fields; no secret VALUE literal in the module
# --------------------------------------------------------------------------
def test_required_fields_have_no_default():
    for name, field in Settings.model_fields.items():
        assert field.is_required(), f"{name} has a default (must be required, fail-closed)"


def test_no_secret_value_literal_in_module():
    src = pathlib.Path(settings_module.__file__).read_text(encoding="utf-8")
    for value in VALID_ENV.values():          # no throwaway test dummy leaked into prod
        assert value not in src
    assert "CHANGE_ME" not in src              # no placeholder baked in either


# --------------------------------------------------------------------------
# drift guard (fold 2/3) — .env.example active keys == Settings fields (uppercased)
# --------------------------------------------------------------------------
def test_env_example_matches_settings_fields():
    active = _active_keys(ENV_EXAMPLE.read_text(encoding="utf-8"))
    fields = {name.upper() for name in Settings.model_fields}
    assert active == fields, f"drift: env.example {active} != Settings {fields}"


def test_drift_guard_excludes_commented_phase2_lines():
    # a commented Phase-2 line must NOT count as an active key
    sample = "DATABASE_URL=x\n# ANTHROPIC_API_KEY=\n#LANGFUSE_HOST=\n"
    assert _active_keys(sample) == {"DATABASE_URL"}
