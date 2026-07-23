"""NFR-MEXT-TEMP0-1 — ``temperature=0`` centrally, for all providers, in both modes
(BR-MEXT-5 / FR-PROV-3 / skill #4). The capturing double records temperature==0 on every
call from every adapter in both thinking modes; ``complete`` exposes no temperature
parameter (extended thinking never implies a non-zero temperature).
"""
from __future__ import annotations

import inspect

import pytest

from backend.memo_agent_core.schemas import MemoDraftOutput, ThinkingMode
from backend.memo_extensions.provider_secondary import ClaudeAdapter
from backend.memo_extensions.provider_showcase import OllamaAdapter
from backend.memo_extensions.tests import fixtures as fx

ADAPTERS = [ClaudeAdapter, OllamaAdapter]
MODES = [ThinkingMode.STANDARD, ThinkingMode.EXTENDED]


@pytest.mark.parametrize("cls", ADAPTERS)
@pytest.mark.parametrize("mode", MODES)
def test_temperature_is_zero_every_call_every_adapter_both_modes(cls, mode):
    client = fx.CapturingThinkingClient()
    cls(client, model="m", thinking_mode=mode).complete("prompt", MemoDraftOutput)
    assert client.calls[-1]["temperature"] == 0


@pytest.mark.parametrize("cls", ADAPTERS)
def test_complete_has_no_temperature_parameter(cls):
    assert "temperature" not in inspect.signature(cls.complete).parameters
