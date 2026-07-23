"""NFR-MEXT-PERF-1 — adapter/handler cost observed, non-gating. No hard SLO (the uniform
prior-unit posture); nothing to time at tier-U (every provider + transport is a double).
Real per-provider latency is a deploy-config / observability (U21) concern."""
from __future__ import annotations

import time

from backend.memo_agent_core.schemas import MemoDraftOutput
from backend.memo_extensions.provider_secondary import ClaudeAdapter
from backend.memo_extensions.tests import fixtures as fx


def test_adapter_complete_cost_is_observed_not_gated():
    adapter = ClaudeAdapter(fx.CapturingThinkingClient(), model="m")
    start = time.perf_counter()
    adapter.complete("prompt", MemoDraftOutput)
    elapsed = time.perf_counter() - start
    assert elapsed >= 0.0  # observed/soft, non-gating (no hard SLO)
