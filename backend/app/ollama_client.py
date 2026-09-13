"""The live Ollama client — register #18's showcase half.

⛔ **THIS IS A REAL LANGUAGE MODEL.** Every memo it produces is genuine inference from
``llama3.1:8b-instruct-q4_K_M`` running on a local Ollama daemon. It is the first thing in
this build that can put non-synthetic prose in front of a human, and it is **opt-in**
(``MEMO_PROVIDER=ollama``); an unconfigured deployment still gets the offline double.

TWO PIECES, mirroring ``llm_client.py``'s deliberate separation (register #18, Q9-A):

* ``CappedOllamaClient`` — a **flag-free, purely-injected wrapper**. It receives an
  ALREADY-CONSTRUCTED SDK client object, satisfies the U19-local ``ThinkingLLMClient`` seam
  **structurally** (no import, no inheritance), bounds re-entry **per draft**, passes
  ``temperature``/``model`` through UNTOUCHED, and logs the prompt LENGTH — never the prompt
  text. It imports **nothing** from ``ollama`` and holds no credential.

* ``build_ollama_client`` — the factory and sole holder of the lazy ``import ollama``.

⚑ **WHY THERE IS NO ``ALLOW_REAL_LLM_CALLS`` EQUIVALENT** (live-llm-drafting Q1, option B's
reasoning, adopted). That flag exists in ``llm_client.py`` to gate **real billable spend**; its
own refusal message says *"set ALLOW_REAL_LLM_CALLS=true to permit real spend"*. A local daemon
costs nothing, so copying the flag would ship a **false statement** as a guard. Selection alone
(``MEMO_PROVIDER=ollama``) enables this path, and that selector fails safe to the offline double.

⚑ Logging: a module-level ``getLogger(__name__)`` with no handler and no config — inert and
silent by default, the same posture ``llm_client.py`` adopted and for the same reason.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Any, Optional

_LOG = logging.getLogger(__name__)

#: ⛔ The maximum model calls a SINGLE draft may make. **Per draft — not per process.**
#:
#: ⚑ **AN HONEST STATEMENT OF WHAT THIS DOES AND DOES NOT BOUND.** The citation-retry loop is
#: **already** bounded: ``MEMO_CITATION_RETRY_CAP = 2`` (``memo_agent_core/constants.py:18``) and
#: ``orchestrator.py:118`` re-drafts only while ``attempts < cap``, so a draft makes **at most 2**
#: calls today. This cap therefore does **NOT** contain a runaway that is currently possible — it
#: is **defence-in-depth** against a future re-entry path that is not bounded. A reader who
#: believes it load-bearing would mis-tune it, which is why the weaker claim is written here.
#:
#: **4 is headroom over a structural maximum of 2.** A breach means something re-entered that
#: should not have, which is exactly when a loud refusal is worth more than a silent retry.
MAX_CALLS_PER_DRAFT: int = 4

#: ⛔ The per-request timeout handed to the SDK. **GENEROUS ON PURPOSE.**
#:
#: ⚑ ``ollama._client`` declares ``timeout: Any = None``, deliberately overriding httpx's default —
#: so **without this the client waits forever** and a hung daemon holds a threadpool thread for the
#: life of the process. That pool is shared with R10's submissions, so enough stuck drafts starve
#: submission itself.
#:
#: ⚠️ **The failure to avoid is killing a legitimate COLD LOAD**, which can take tens of seconds on
#: first use of a model. A tight timeout would read a working design as broken — the same
#: misdiagnosis ``document-upload``'s §9 step 8 was rewritten to prevent. 120 s is comfortably
#: above a cold load and still finite.
DRAFT_TIMEOUT_SECONDS: float = 120.0

#: The daemon's default when ``OLLAMA_HOST`` is unset — used for MESSAGES ONLY, never to connect.
#: ⚑ The SDK resolves the real host itself (``_parse_host(host or os.getenv('OLLAMA_HOST'))``);
#: this constant exists so a failure message can NAME what was tried (Q3's hybrid) without this
#: module duplicating the SDK's resolution and risking the two drifting apart.
DEFAULT_OLLAMA_HOST: str = "http://127.0.0.1:11434"


class OllamaUnreachable(RuntimeError):
    """The local Ollama daemon could not be reached, or refused the request at transport level.

    ⛔ **DISTINCT FROM ``OllamaCallCapExceeded`` BY DESIGN, NOT BY ACCIDENT.** Both surface as a
    500, and an operator's response to them is **opposite**: this one means *start Ollama*; the
    other means *something re-entered the model and the app refused*. Collapsing them into one
    generic body is the failure this separation exists to prevent.
    """


class OllamaCallCapExceeded(RuntimeError):
    """A single draft exceeded ``MAX_CALLS_PER_DRAFT`` model calls and was refused.

    ⚑ **NOT an availability problem.** Ollama is fine; the app declined to keep calling it. The
    message must say so, because an operator who reads this as "Ollama is down" will restart the
    wrong thing.
    """


class CappedOllamaClient:
    """The wrapper — flag-free and purely injected. Satisfies the U19-local ``ThinkingLLMClient``
    seam ``generate(*, model, prompt, temperature, thinking) -> str`` STRUCTURALLY.

    ⛔ **THE COUNTER IS THREAD-LOCAL, AND THAT IS A CORRECTNESS PROPERTY, NOT AN OPTIMIZATION.**

    This object is built ONCE per process — ``_CompositionSeams.__init__`` runs behind
    ``@lru_cache(maxsize=1)`` — so **every concurrent draft shares this instance**. A plain
    ``self._count`` reset at the start of each draft would let draft B zero draft A's count
    mid-flight, and the cap would bound nothing exactly when load makes it matter.

    ⚑ **Thread-local is precisely per-draft here**, because R11 hands the *entire* ``pipeline.draft``
    to ``anyio.to_thread.run_sync`` as one callable: a draft, including every citation retry inside
    the graph, runs start-to-finish on **one worker thread**.

    ⛔ **DO NOT "SIMPLIFY" THIS BY SETTING ``MAX_CONCURRENT_DRAFTS`` TO 1.** Serializing drafts would
    make a naive counter safe — and would make **correctness depend on the value of a tuning
    constant**, so a later throughput bump would silently reintroduce the race with nothing failing.
    That is the drift ``parse_concurrency.py`` warns about in its own header. The bound is a
    performance knob; it must never also be a correctness guarantee.

    ⚠️ Threads are **pooled and reused**, so the counter must be **reset at ``begin_draft()``**,
    never merely lazily initialized — a reused thread would otherwise start mid-count.
    """

    def __init__(self, sdk_client: Any, *, max_calls: int = MAX_CALLS_PER_DRAFT,
                 host: str = DEFAULT_OLLAMA_HOST) -> None:
        self._sdk_client = sdk_client
        self._max_calls = max_calls
        self._host = host
        self._state = threading.local()

    # --- the per-draft boundary --------------------------------------------------------

    def begin_draft(self) -> None:
        """Open a new counting scope for THIS thread. Called once per draft, by
        ``_CompositionSeams.draft_memo`` — the only place that is exactly one-per-draft without
        reaching into ``case_lifecycle`` (which would need an authorized reopening)."""
        self._state.count = 0

    @property
    def call_count(self) -> int:
        """Calls made by the CURRENT thread's draft. Zero on a thread that never drafted."""
        return getattr(self._state, "count", 0)

    # --- the seam ----------------------------------------------------------------------

    def generate(self, *, model: str, prompt: str, temperature: float, thinking: bool) -> str:
        count = getattr(self._state, "count", 0)
        if count >= self._max_calls:
            raise OllamaCallCapExceeded(
                f"this draft made {count} model calls, reaching its per-draft cap of "
                f"{self._max_calls}; refusing further calls. Ollama is reachable — this is the "
                f"application declining to re-enter the model, not a provider outage."
            )
        self._state.count = count + 1
        started = time.perf_counter()
        try:
            # ⚑ ``options`` is a plain dict — the SDK accepts it, so no ``ollama.Options`` import
            # is needed and this wrapper stays SDK-agnostic. ``temperature`` is passed through
            # UNTOUCHED: TEMP0-1 lives in the frozen adapter, never here.
            response = self._sdk_client.generate(
                model=model,
                prompt=prompt,
                options={"temperature": temperature},
                think=thinking,
                stream=False,
            )
        except (OllamaCallCapExceeded, OllamaUnreachable):
            raise
        except Exception as exc:  # noqa: BLE001 - re-raised as a named type; see below
            # ⛔ NOT a blanket swallow. Every transport failure the SDK can raise
            # (``RequestError``, ``ResponseError``, ``httpx`` connect/timeout errors) is wrapped
            # into ONE named type carrying the host, so the route can map it without importing
            # ``ollama`` itself. Catching by SDK type here would drag the SDK into this module's
            # import surface, which is the property that keeps it offline-testable.
            raise OllamaUnreachable(
                f"could not reach the Ollama daemon at {self._host}: {type(exc).__name__}. "
                f"Is it running? (start it, or unset MEMO_PROVIDER to fall back to the offline "
                f"double)"
            ) from exc
        latency_ms = int((time.perf_counter() - started) * 1000)
        # ⚑ prompt LENGTH only — never the prompt text, which carries applicant data.
        _LOG.info(
            "ollama call model=%s host=%s prompt_len=%d latency_ms=%d draft_call=%d thinking=%s",
            model, self._host, len(prompt), latency_ms, self._state.count, thinking,
        )
        return _response_text(response)

    # --- provenance --------------------------------------------------------------------

    def show_digest(self, model_id: str) -> Optional[str]:
        """The model's content digest, for the ``model_version`` stamp — or ``None``.

        ⛔ **PROVENANCE ONLY. NEVER ON THE DRAFTING PATH**, and deliberately not counted against
        the per-draft cap: it makes no inference, spends no tokens, and is called ONCE at
        construction. Counting it would let a stamp lookup consume a draft's budget.

        ⚠️ Returns ``None`` rather than raising on any failure — the caller degrades the stamp, and
        a provenance detail must never be able to break a draft.
        """
        try:
            info = self._sdk_client.show(model_id)
        except Exception:  # noqa: BLE001 - provenance is best-effort by contract
            return None
        digest = getattr(info, "digest", None)
        if digest is None and isinstance(info, dict):
            digest = info.get("digest") or (info.get("details") or {}).get("digest")
        return str(digest) if digest else None

    def __repr__(self) -> str:
        # Deliberately does NOT delegate to the wrapped object's repr — an SDK client's repr can
        # embed request context. Mirrors ``CappedGeminiClient.__repr__``'s stated reasoning.
        return (
            f"CappedOllamaClient(host={self._host!r}, max_calls_per_draft={self._max_calls}, "
            f"this_thread_count={self.call_count})"
        )


def _response_text(response: Any) -> str:
    """The generated text, from either the SDK's object shape or a plain mapping.

    ⚑ ``ollama``'s ``GenerateResponse`` exposes ``.response``; a dict-shaped double or a future
    SDK revision may expose ``["response"]``. Accepting both keeps the wrapper honest about the
    fact that it does not own the SDK's shape.
    """
    text = getattr(response, "response", None)
    if text is None and isinstance(response, dict):
        text = response.get("response")
    return text or ""


def build_ollama_client(
    *,
    model_id: str,
    max_calls: int = MAX_CALLS_PER_DRAFT,
    timeout: float = DRAFT_TIMEOUT_SECONDS,
    host: Optional[str] = None,
) -> CappedOllamaClient:
    """Construct the real, network-capable client. The ONLY holder of the ``ollama`` import.

    ⚑ **``OLLAMA_HOST`` IS NOT READ HERE, DELIBERATELY** (Q3-A). ``ollama.Client`` already resolves
    ``_parse_host(host or os.getenv('OLLAMA_HOST'))`` itself, and ``.env.example`` has reserved
    ``# OLLAMA_HOST=`` since Phase 1. Reading it ourselves would duplicate the SDK's resolution and
    let the two drift; passing ``host=None`` lets the SDK own it. What we DO keep is the resolved
    value **for messages**, so a failure can name what it tried (Q3's hybrid half).

    ⛔ No credential is read, held, or logged. A local daemon has none.
    """
    from ollama import Client  # lazy — NEVER at module import, so the offline suite needs no daemon

    _LOG.info(
        "constructing real Ollama client: model=%s cap_per_draft=%d timeout=%.0fs",
        model_id, max_calls, timeout,
    )
    client = Client(host=host, timeout=timeout)
    return CappedOllamaClient(
        client, max_calls=max_calls, host=host or DEFAULT_OLLAMA_HOST
    )
