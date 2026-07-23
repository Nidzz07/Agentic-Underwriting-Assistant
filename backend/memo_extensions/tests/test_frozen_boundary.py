"""NFR-MEXT-FROZEN-1 (LOAD-BEARING, full-highest) — extend-don't-modify; the frozen U4
boundary holds (BR-MEXT-11 / Q1-A). The two frozen facts, MIRRORED locally against U4's
**PRODUCTION** module — importing ``memo_agent_core.provider`` (U19's own legitimate edge)
and NOT U4's test file (no double-collection, no coupling to U4 test-function names).

**This is the ONLY U19 module that imports ``memo_agent_core.provider`` for assertion**
(isolated on purpose, so the deliberate cross-unit production import is obvious and
auditable). The import-discipline AST scan (``backend.* ⊆ {memo_agent_core, rules_engine,
audit_store}`` + no ``memo_agent_core.tests.*``) lives in ``test_structural_guard.py``.
"""
from __future__ import annotations

import pytest

import backend.memo_agent_core.provider as provider_module
from backend.memo_agent_core.provider import route_borderline as u4_route_borderline_stub


def test_u4_route_borderline_stays_a_not_wired_stub():
    # Mirrors frozen test_route_borderline_is_a_not_wired_stub — U4's Phase-2 seam stays a seam.
    with pytest.raises(NotImplementedError):
        u4_route_borderline_stub()


def test_u4_namespace_has_no_u19_adapter_or_mcp_names():
    # Mirrors frozen test_only_gemini_adapter_is_present_no_claude_ollama_mcp — but runs where
    # U19's adapters ARE imported, catching import-time namespace pollution U4's own test can
    # miss under collection order (NFR-MEXT-Fold-1). U19's adapters live in memo_extensions/.
    names = dir(provider_module)
    polluters = [n for n in names if ("Claude" in n or "Ollama" in n or "Mcp" in n or "MCP" in n)]
    assert polluters == [], f"U4 namespace polluted by U19 additions: {polluters}"


def test_u19_adapters_live_outside_u4_namespace():
    # Positive control: the adapters exist in U19's own package, not U4's.
    from backend.memo_extensions.provider_secondary import ClaudeAdapter
    from backend.memo_extensions.provider_showcase import OllamaAdapter

    assert ClaudeAdapter.__module__ == "backend.memo_extensions.provider_secondary"
    assert OllamaAdapter.__module__ == "backend.memo_extensions.provider_showcase"
    assert "ClaudeAdapter" not in dir(provider_module)
    assert "OllamaAdapter" not in dir(provider_module)
