"""memo-extensions (U19, C4, Phase 2) — the provider/routing/MCP-tool extension
of ``memo-agent-core`` (U4).

Three axes, four frozen modules (``unit-of-work.md:70-71``), NO fifth:
- ``borderline_router`` — the deterministic, provider-agnostic extended-thinking
  trigger (rule-proximity OR outlier cutoff). Holds no LLM.
- ``mcp_tools`` — the two read-only MCP tool surfaces (rulebook / decisions),
  supplementary-only + demographic-free, and the append-only prompt composer.
- ``provider_secondary`` — the Claude Opus 4.8 secondary adapter (tested).
- ``provider_showcase`` — the Ollama showcase adapter (wired-only).

Extend-don't-modify: U4 is imported, never modified; U18 is reached only by
shape (never imported); rules-engine / audit-store are read-only edges.
"""
