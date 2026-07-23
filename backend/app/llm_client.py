"""Register #18 — the FIRST production ``LLMClient`` path in this build.

TWO pieces (Q9-A), deliberately separated so the spend gate never touches the
offline test surface:

* ``CappedGeminiClient`` — a **flag-free, purely-injected wrapper**. It receives an
  ALREADY-CONSTRUCTED SDK client object, satisfies the frozen
  ``memo_agent_core.LLMClient`` seam **structurally** (no import, no inheritance),
  counts EVERY ``generate`` call (so the citation-retry loop is covered), refuses
  once its cap is exceeded, passes ``temperature``/``model`` through UNTOUCHED, and
  logs the prompt LENGTH — never the prompt text, never a key. It imports **nothing**
  from ``google.genai`` and holds **no key at all**.

* ``build_gemini_client`` — a **guarded factory**, the ONLY spend-capable path. It is
  the sole holder of the ``ALLOW_REAL_LLM_CALLS`` gate and the lazy ``google-genai``
  import, and reads the key exclusively off the injected ``settings`` (``get_settings``).

This module lives in the composition root (``backend/app/``), which is where both
frozen docstrings in ``memo_agent_core/provider.py`` say the real client belongs —
*"wrapped to this at composition"*. It reopens no frozen unit. See
``guide-docs/build/plans/fix-register-18-code-gen-plan.md``.

⚑ Logging: a module-level ``getLogger(__name__)`` with no handler and no config —
inert and silent by default (the conventional library default; ``print`` is rejected
for a library module). Named in the plan so it is visible and overridable at the gate.
"""
from __future__ import annotations

import logging
import os
import time

_LOG = logging.getLogger(__name__)


class LLMCallCapExceeded(RuntimeError):
    """Raised by ``CappedGeminiClient`` once its per-process call cap is exceeded.

    Bounds real spend INCLUDING the memo agent's citation-retry loop, because the cap
    counts inside ``generate`` — exactly where the orchestrator re-enters the client.
    """


class RealLLMCallsNotEnabled(RuntimeError):
    """Raised by ``build_gemini_client`` when the real-spend path is refused — either
    the ``ALLOW_REAL_LLM_CALLS`` gate is not exactly ``"true"`` or the key is empty.

    Its message never contains key material (Q3c)."""


class CappedGeminiClient:
    """The wrapper — flag-free and purely injected. Satisfies the frozen
    ``LLMClient`` seam ``generate(*, model, prompt, temperature) -> str`` STRUCTURALLY.

    Takes an already-constructed SDK client object; it therefore **holds no key** and
    imports nothing from ``google.genai`` — SDK-agnostic by construction, it merely
    calls the object it was handed.
    """

    def __init__(self, sdk_client, *, max_calls: int = 20) -> None:
        self._sdk_client = sdk_client
        self._max_calls = max_calls
        self._count = 0

    def generate(self, *, model: str, prompt: str, temperature: float) -> str:
        if self._count >= self._max_calls:
            raise LLMCallCapExceeded(
                f"real LLM call cap of {self._max_calls} reached; refusing further calls"
            )
        self._count += 1
        started = time.perf_counter()
        # config is a plain dict — google-genai accepts it, so NO ``types`` import is
        # needed and the wrapper stays SDK-agnostic. ``temperature`` is passed through
        # UNTOUCHED: the wrapper sets nothing and defaults nothing (TEMP0-1 lives in
        # the frozen ``GeminiAdapter``, not here).
        response = self._sdk_client.models.generate_content(
            model=model,
            contents=prompt,
            config={"temperature": temperature},
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        # ⚑ prompt LENGTH only — never the prompt text, never a key.
        _LOG.info(
            "gemini call model=%s prompt_len=%d latency_ms=%d call_count=%d",
            model,
            len(prompt),
            latency_ms,
            self._count,
        )
        return response.text or ""

    @property
    def call_count(self) -> int:
        return self._count

    def __repr__(self) -> str:
        # Deliberately does NOT delegate to the wrapped object's repr — a real SDK
        # client's repr could embed request context; this holds no key to leak anyway.
        return f"CappedGeminiClient(call_count={self._count}, max_calls={self._max_calls})"


def build_gemini_client(settings, *, model_id: str, max_calls: int = 20) -> CappedGeminiClient:
    """The guarded factory — the ONLY spend-capable path.

    Two independent things must hold before a real client is built:
      1. ``os.environ['ALLOW_REAL_LLM_CALLS']`` is EXACTLY ``"true"`` — else refuse.
      2. ``settings.GEMINI_API_KEY`` is non-empty — else fail closed (Q3b-i).

    ⚑ Confirm 2 — why reading ``ALLOW_REAL_LLM_CALLS`` from ``os.environ`` here is NOT a
    SEC-3 violation. ``dependencies.py``'s rejection of ``os.environ`` is scoped to
    **credentials and secret material specifically**. This is a **behavioural on/off
    switch controlling whether real spend is permitted, not a credential**, and it is
    **never** conflated with or read alongside ``GEMINI_API_KEY``'s retrieval path,
    which stays **exclusively** through ``get_settings()`` (the injected ``settings``).

    ⚑ Q3c honest limit: this guarantees **our** code never discloses the key. It
    **cannot** guarantee the SDK's own exceptions never embed request context — that is
    not ours to promise, and this docstring claims no stronger guarantee than that.
    """
    if os.environ.get("ALLOW_REAL_LLM_CALLS") != "true":
        raise RealLLMCallsNotEnabled(
            "real Gemini calls are disabled; set ALLOW_REAL_LLM_CALLS=true to permit real spend"
        )
    key = settings.GEMINI_API_KEY
    if key is None or not key.strip():
        raise RealLLMCallsNotEnabled(
            "refusing to construct a real Gemini client: the configured API key is empty"
        )
    return _capped_client_over_real_genai(key, model_id, max_calls)  # pragma: no cover - real-spend path


def _capped_client_over_real_genai(  # pragma: no cover - real SDK / network-bound; no offline test drives it
    api_key: str, model_id: str, max_calls: int
) -> CappedGeminiClient:
    """Lazily import ``google-genai`` and construct the real, spend-capable client.

    Entirely on the real-spend path — no offline test drives it (the point of the
    injected-seam design, Q9-A). It therefore carries ``# pragma: no cover`` following
    the ``not_wired.py:127`` precedent, rather than a ``pyproject.toml`` omit entry; the
    flag check, key validation and refusal paths in ``build_gemini_client`` stay covered.
    """
    from google import genai  # lazy — NEVER at module import, so the offline suite needs no SDK

    _LOG.info("constructing real Gemini client: model=%s cap=%d", model_id, max_calls)
    return CappedGeminiClient(genai.Client(api_key=api_key), max_calls=max_calls)
