"""ProviderAbstraction + GeminiAdapter (P1) + Phase-2 seams (PROV-1 / TEMP0-1).

``ProviderAbstraction`` is the injected Protocol the memo sub-flow reaches the
LLM through — ``complete(prompt, schema) -> MemoDraftOutput``. The signature
carries **no temperature parameter**: ``temperature=0`` is fixed **centrally**
inside each concrete adapter, never caller-controlled (TEMP0-1 part ii).

``GeminiAdapter`` (P1) takes an **injected client** (constructor seam) so its
real ``temperature=0`` wiring and XML→Pydantic parsing are unit-tested **offline**
— a capturing test double records the outgoing request; no network, no key, no
CI live call (TEMP0-1 part i). The real google-genai client is wrapped to this
minimal ``LLMClient`` seam at composition time (a deploy-config/secrets concern,
per the logged Infra SKIP).

Phase-2 (``memo-extensions``) is **named, not wired**: ``route_borderline`` is a
not-wired stub; there are **no** Claude/Ollama adapters and **no** MCP here.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable
from xml.etree import ElementTree

from backend.memo_agent_core.schemas import MemoDraftOutput, ThinkingMode

#: temperature is fixed centrally — never a per-call / caller-controlled param.
_PRODUCTION_TEMPERATURE = 0


@runtime_checkable
class ProviderAbstraction(Protocol):
    """The injected LLM seam. ``complete`` has NO temperature parameter."""

    def complete(self, prompt: str, schema: type[MemoDraftOutput]) -> MemoDraftOutput: ...


@runtime_checkable
class LLMClient(Protocol):
    """The minimal Gemini-SDK-shaped seam ``GeminiAdapter`` drives. The real
    google-genai client is wrapped to this at composition (deploy-config/secrets);
    a capturing test double implements it offline (no network, no key)."""

    def generate(self, *, model: str, prompt: str, temperature: float) -> str: ...


class GeminiAdapter:
    """P1 provider adapter. Central ``temperature=0`` + XML→Pydantic structured
    output. The LLM client is **injected** (offline-testable)."""

    def __init__(self, client: LLMClient, *, model: str = "gemini-2.5-flash") -> None:
        self._client = client
        self._model = model

    @property
    def model_version(self) -> str:
        return self._model

    def complete(self, prompt: str, schema: type[MemoDraftOutput]) -> MemoDraftOutput:
        raw_xml = self._client.generate(
            model=self._model,
            prompt=prompt,
            temperature=_PRODUCTION_TEMPERATURE,  # central; not caller-controlled
        )
        return self._parse_xml(raw_xml, schema)

    @staticmethod
    def _parse_xml(raw_xml: str, schema: type[MemoDraftOutput]) -> MemoDraftOutput:
        root = ElementTree.fromstring(raw_xml)
        prose_el = root.find("narrative_prose")
        prose = (prose_el.text or "") if prose_el is not None else ""
        cited = [el.text or "" for el in root.findall("./cited_rule_ids/rule_id")]
        return schema(narrative_prose=prose, cited_rule_ids=cited)


def route_borderline(*args, **kwargs) -> ThinkingMode:
    """Phase-2 seam (``memo-extensions``) — extended-thinking routing (FR-MEMO-6/7).
    **Not wired in Phase 1.**"""
    raise NotImplementedError(
        "route_borderline is a Phase-2 seam (memo-extensions); not wired in Phase 1"
    )
