"""Shared pytest configuration for the backend test suites.

Portability seam (Sharpening 1). `resource.setrlimit` is POSIX-only and absent
on the Windows dev box. Tests that assert the *kernel-enforced* half of the
subprocess sandbox (RLIMIT_CPU / RLIMIT_AS → OOM / CPU-spin) are marked
``@pytest.mark.posix_only`` and auto-skipped where ``resource`` is unavailable.

The parent-kill **wall-time** timeout test carries NO such marker — it runs on
*every* platform. The deployment target is Linux/Render, so the ``posix_only``
tests MUST run in Linux CI: that is where the setrlimit protection is actually
exercised. Skipping locally never hides a regression in CI.
"""
from __future__ import annotations

import pytest

try:
    import resource  # noqa: F401  POSIX-only

    HAS_RESOURCE = True
except ImportError:  # pragma: no cover - platform-dependent
    HAS_RESOURCE = False


def pytest_collection_modifyitems(config, items):
    if HAS_RESOURCE:
        return
    skip_posix = pytest.mark.skip(
        reason="resource.setrlimit unavailable (non-POSIX); runs in Linux CI"
    )
    for item in items:
        if "posix_only" in item.keywords:
            item.add_marker(skip_posix)
