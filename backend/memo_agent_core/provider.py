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

_MEMO_OPEN = "<memo"
_MEMO_CLOSE = "</memo>"


class MemoDocumentShapeError(ValueError):
    """⛔ **Register #33 change (h)** — a well-formed XML document of the WRONG SHAPE.

    ⚑ **Why this type exists.** The parsers read ``narrative_prose`` and
    ``./cited_rule_ids/rule_id`` **by exact path**, so a model that returns tidy XML under
    different element names (``<memo_text>``, ``<summary>``, a translated name) ⛔ **parsed to
    silence**: empty prose, no citations, and **no exception**. Downstream that surfaced only as
    *"drafting produced no memo"*, with the cause discarded.

    ⚠️ **X1 is what makes this reachable, which is why (h) lands with it.** Asking the model for
    XML converts a **loud** failure (not XML at all → ``ParseError``) into a **quiet** one
    (well-formed XML, wrong names). ⛔ Without (h), X1 would trade a diagnosable crash for an
    undiagnosable blank.

    ⚠️ **DELIBERATELY NARROW (Q13-A).** It fires only when **NEITHER** expected element is
    present. A model that emits prose and an **empty** ``<cited_rule_ids/>`` has *genuinely cited
    nothing* — a legitimate outcome that ``CitationValidator`` must block **on the merits**.
    ⛔ Widening this to "no citations found" would destroy exactly the distinction it exists to
    draw. It is a ``ValueError``, **not** a ``ParseError``: "XML of the wrong shape" and "not XML"
    are different failures and stay different types.
    """


def require_memo_shape(root: ElementTree.Element) -> None:
    """Raise :class:`MemoDocumentShapeError` if ``root`` carries neither expected element.

    ⚑ Shared by both parsers for the same anti-drift reason as
    :func:`strip_to_memo_element` — see change (g).
    """
    if root.find("narrative_prose") is not None or root.find("cited_rule_ids") is not None:
        return
    raise MemoDocumentShapeError(
        "the model returned a well-formed XML document that contains neither a "
        "<narrative_prose> element nor a <cited_rule_ids> element; root is "
        f"<{root.tag}> with children {[child.tag for child in root]}. "
        "This is a FORMAT failure, not an empty memo - a model that genuinely cited nothing "
        "still emits <narrative_prose>. See REQUIRED OUTPUT FORMAT in the prompt (register #33)."
    )


def strip_to_memo_element(raw_xml: str) -> str:
    """Return the ``<memo>…</memo>`` span of ``raw_xml``, or ``raw_xml`` unchanged.

    ⛔ **Register #33 change (g) — X3 parse tolerance, SUBTRACTIVE ONLY.** Real models wrap a
    correct document in things the XML parser cannot accept: a ```` ```xml ```` fence, a
    *"Certainly! Here is the memo:"* preamble, a closing offer to rephrase. ⚑ This removes what
    **surrounds** the document and hands the remainder to the **same**
    :func:`~xml.etree.ElementTree.fromstring` as before.

    ⚠️ **It never extracts or reconstructs VALUES** (Q4-A, explicitly rejected): the return is
    always a literal substring of the input, so nothing this function does can invent prose or a
    citation. ⛔ **If no document is present it returns the input UNCHANGED** — so genuine prose
    still raises ``ParseError``, and the error still quotes what the model actually said.
    ⚑ **Tolerance must not become "never fails"**: a model that ignored the format instruction
    has produced no memo, and that has to stay loud.

    ⚑ **Shared by both parsers** — :meth:`GeminiAdapter._parse_xml` here and
    ``memo_extensions.provider_secondary._parse_xml``, which imports it. ⚠️ It lives in **this**
    module rather than a new one because a new module would be a **FIFTH** file in a frozen unit,
    outside the signed authorization (§6.2).

    ⚑ **DEFERRED: candidate X2 — true structured output.** A stronger mechanism exists and was
    **consciously not taken**: ``response_schema`` on ``google-genai`` / ``format=`` on ``ollama``
    would make malformed output impossible rather than tolerated. ⛔ **It is not a config change.**
    Both are **JSON-schema** based, so taking X2 replaces ``_parse_xml`` in **both** adapters, plus
    the offline double's hardcoded XML and every test asserting on XML — a wire-format migration
    that also collides with ``PROJECT-BRIEF`` §3/§9 (*"Structured XML output → Pydantic
    validation"*) and would need a brief amendment. **Tracked on the register; not authorized here.**
    """
    start = raw_xml.find(_MEMO_OPEN)
    end = raw_xml.rfind(_MEMO_CLOSE)
    if start == -1 or end == -1 or end < start:
        return raw_xml
    return raw_xml[start : end + len(_MEMO_CLOSE)]


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
        # ⛔ Register #33 change (f) — X3. Subtractive tolerance, then the SAME parse as before.
        # See strip_to_memo_element for why this is not `response_schema` (candidate X2, deferred).
        root = ElementTree.fromstring(strip_to_memo_element(raw_xml))
        require_memo_shape(root)  # change (h) — the silent-empty path
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
