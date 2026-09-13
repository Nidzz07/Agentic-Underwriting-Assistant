"""ClaudeAdapter (C-MEXT-5, secondary/tested) + the U19-local thinking-aware client
seam (R2). BR-MEXT-4/5 · NFR-MEXT-THINK-1/TEMP0-1/AGNOSTIC-1/CONTRACT-1.

**R2 realization (disclosed Code-Gen decision — see code-summary.md):** the frozen
``memo_agent_core.LLMClient`` seam is ``generate(*, model, prompt, temperature) -> str``
— **three kwargs, no thinking channel** — and is U4's Gemini path, left completely
UNTOUCHED. U19's new adapters need a thinking channel that seam cannot carry, so U19
defines its OWN thinking-aware client seam here (``ThinkingLLMClient``, with a real
``thinking`` request parameter as on the actual Claude/Gemini APIs). This scopes the
deviation to the two new adapters only and gives NFR-MEXT-THINK-1(b) real, non-vacuous,
provider-API-faithful teeth.

**Header-comment deliverables (documentation only — NEVER enforcement):**
- ``temperature=0`` is fixed **CENTRALLY** inside the adapter (``_PRODUCTION_TEMPERATURE``)
  and is **never** a caller-controlled parameter — ``complete(prompt, schema)`` has no
  ``temperature`` parameter (TEMP0-1 part ii). Extended thinking never implies a non-zero
  temperature.
- The thinking mode arrives at **CONSTRUCTION** because the frozen ``ProviderAbstraction.
  complete(prompt, schema)`` signature admits no such parameter (Fold-1). The adapter maps
  it to the ``thinking`` request flag causally at call time.
"""
from __future__ import annotations

from typing import Final, Protocol, runtime_checkable
from xml.etree import ElementTree

from backend.memo_agent_core.provider import require_memo_shape, strip_to_memo_element
from backend.memo_agent_core.schemas import MemoDraftOutput, ThinkingMode

#: temperature is fixed centrally — never a per-call / caller-controlled parameter.
_PRODUCTION_TEMPERATURE: Final[int] = 0


@runtime_checkable
class ThinkingLLMClient(Protocol):
    """The U19-local thinking-aware client seam the Claude/Ollama adapters drive (R2).

    Distinct from the frozen ``memo_agent_core.LLMClient`` (which is U4's Gemini seam and
    is NOT modified): this seam carries a ``thinking`` request parameter — the faithful
    shape for provider extended thinking. The real per-provider client is wrapped to this
    at composition (deploy-config/secrets); a capturing double implements it offline
    (no network, no key).
    """

    def generate(self, *, model: str, prompt: str, temperature: float, thinking: bool) -> str: ...


def _parse_xml(raw_xml: str, schema: type[MemoDraftOutput]) -> MemoDraftOutput:
    """XML → ``MemoDraftOutput`` (mirrors the frozen ``GeminiAdapter`` parsing). The
    model fills ONLY ``narrative_prose`` + ``cited_rule_ids`` — CON-BR2-TYPE means it
    cannot represent a recommendation change.

    ⛔ **Register #33 change (g) — X3 tolerance is SHARED, not re-implemented.**
    :func:`~backend.memo_agent_core.provider.strip_to_memo_element` is **imported** from U4 rather
    than copied, because ⚠️ **two hand-rolled tolerance implementations would drift**, and this
    parser mirroring U4's is the whole point of the docstring above. ⚑ The import is a legitimate
    frozen edge: Scan 7 allows the ``memo_agent_core`` root, and Scan 1's tighter allow-list is
    scoped to ``borderline_router.py`` only (§6.2).

    ⚑ **DEFERRED: candidate X2 — true structured output.** ``format=<json schema>`` on Claude /
    Ollama would make malformed output impossible rather than tolerated. ⛔ **Not a config
    change**: it is JSON-schema based, so it would replace this parser and U4's, the offline
    double's hardcoded XML, and every XML-asserting test — a wire-format migration needing a
    ``PROJECT-BRIEF`` §3/§9 amendment. **Tracked on the register; not authorized here.**
    """
    root = ElementTree.fromstring(strip_to_memo_element(raw_xml))
    require_memo_shape(root)  # register #33 change (h) - shared, not re-implemented
    prose_el = root.find("narrative_prose")
    prose = (prose_el.text or "") if prose_el is not None else ""
    cited = [el.text or "" for el in root.findall("./cited_rule_ids/rule_id")]
    return schema(narrative_prose=prose, cited_rule_ids=cited)


class ClaudeAdapter:
    """Claude Opus 4.8 secondary adapter (tested). Implements the frozen
    ``ProviderAbstraction`` structurally. Central ``temperature=0`` + construction-time
    thinking mode + XML→Pydantic structured output."""

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
