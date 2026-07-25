"""Hermetic environment for the authn suite (AUTHN-Fold-2).

⚑ **Why this file exists.** ``SESSION_COOKIE_SECURE`` is read from ``os.environ`` (Q4a, on
the ``ALLOW_REAL_LLM_CALLS`` precedent: a behavioural on/off switch is **not** a credential,
so SEC-3's ``os.environ`` prohibition — which is scoped to credentials and secret material —
does not apply). But an env-read switch means a developer with ``SESSION_COOKIE_SECURE=false``
exported in their shell would **silently exercise the insecure branch** in any test that does
not set it explicitly, and the suite would pass or fail depending on whose machine ran it.

This is the exact hazard ``secrets_config/tests/conftest.py`` guards against for its six keys
— *"so a real shell-set variable can never leak into or mask a case"*. Same guard, same
reason: the variable is **cleared before every test**, so each test starts from the
fail-safe default and any test that cares must opt in **explicitly**.

⚑ ``SESSION_COOKIE_SECURE`` is the **only** environment variable this package reads. Q4(a)
avoids C-B (no seventh ``Settings`` field), and nothing else here consults the environment.
"""
from __future__ import annotations

import pytest

#: Every environment variable the authn package reads. Cleared before each test.
AUTHN_ENV_KEYS = ("SESSION_COOKIE_SECURE",)


@pytest.fixture(autouse=True)
def _hermetic_authn_env(monkeypatch):
    """Clear authn's env keys before EVERY test in this package (autouse)."""
    for key in AUTHN_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
