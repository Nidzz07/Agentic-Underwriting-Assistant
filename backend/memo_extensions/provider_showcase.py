"""OllamaAdapter (C-MEXT-5, showcase/wired-only) — FR-PROV-2/5 · BR-MEXT-3/10 ·
NFR-MEXT-THINK-1/TEMP0-1/PROVGATE-1.

The local Ollama showcase adapter. Same frozen ``ProviderAbstraction`` shape, same
central ``temperature=0``, same U19-local ``ThinkingLLMClient`` seam (R2) as the Claude
secondary. *"Wired-only" != untested code* — it is unit-tested offline like every other
adapter; it is exempt from the memo-QUALITY gates only (groundedness/promptfoo), NEVER
from the DECISION-LEVEL gates (reproducibility, bias-swap, ``temperature=0``,
CON-BR2-TYPE) which apply to ALL providers (BR-MEXT-10 / FR-PROV-GATE-1).

It may not support extended thinking (FR-PROV-5) — but constructed with ``EXTENDED`` it
still **completes** (degrades at the adapter, never at the trigger); the router's outcome
is unchanged by that (BR-MEXT-3).

**Header-comment deliverables (documentation only — NEVER enforcement):** ``temperature=0``
fixed centrally, never caller-controlled; the thinking mode arrives at construction because
the frozen ``complete()`` admits no such parameter.
"""
from __future__ import annotations

from backend.memo_agent_core.schemas import MemoDraftOutput, ThinkingMode
from backend.memo_extensions.provider_secondary import (
    _PRODUCTION_TEMPERATURE,
    ThinkingLLMClient,
    _parse_xml,
)


class OllamaAdapter:
    """Ollama showcase adapter (wired-only). Identical constructor + ``complete`` shape
    to the Claude secondary; drives the same U19-local thinking-aware seam."""

    def __init__(
        self,
        client: ThinkingLLMClient,
        *,
        model: str,
        thinking_mode: ThinkingMode = ThinkingMode.STANDARD,
    ) -> None:
        self._client = client
        self._model = model
        self._thinking_mode = thinking_mode

    @property
    def model_version(self) -> str:
        return self._model

    def complete(self, prompt: str, schema: type[MemoDraftOutput]) -> MemoDraftOutput:
        raw_xml = self._client.generate(
            model=self._model,
            prompt=prompt,
            temperature=_PRODUCTION_TEMPERATURE,  # central; not caller-controlled
            thinking=(self._thinking_mode is ThinkingMode.EXTENDED),
        )
        return _parse_xml(raw_xml, schema)
