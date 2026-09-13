"""``CappedOllamaClient`` + ``build_ollama_client`` — register #18's showcase half.

⛔ **NO DAEMON, NO NETWORK, NO MODEL.** Every test here drives a hand-built double through the
injected-SDK seam, which is the whole point of that seam's design. The real ``ollama`` import lives
behind ``build_ollama_client`` and is exercised only for its laziness.

⚑ **THE THREE LOAD-BEARING TESTS ARE THE THREAD ONES.** ``test_the_cap_resets_after_begin_draft``,
``test_two_threads_keep_INDEPENDENT_counters`` and ``test_a_REUSED_thread_starts_at_zero`` are the
mechanical statement of the per-draft-cap correction. Their non-vacuity was demonstrated by
reverting the counter to a plain ``self._count`` and observing all three fail; the first and third
also fail against a lazily-initialized thread-local, which is why "reset at ``begin_draft``" is
written as a separate assertion from "counts are per-thread".
"""
from __future__ import annotations

import logging
import threading

import pytest

from backend.app.ollama_client import (
    DEFAULT_OLLAMA_HOST,
    DRAFT_TIMEOUT_SECONDS,
    MAX_CALLS_PER_DRAFT,
    CappedOllamaClient,
    OllamaCallCapExceeded,
    OllamaUnreachable,
    build_ollama_client,
)


class _Response:
    """The SDK's object shape — ``GenerateResponse`` exposes ``.response``."""

    def __init__(self, text: str = "<memo><narrative_prose>x</narrative_prose></memo>") -> None:
        self.response = text


class CapturingSDK:
    """Records every outgoing request. Never touches a network."""

    def __init__(self, text: str = "<memo><narrative_prose>x</narrative_prose></memo>") -> None:
        self.calls: list[dict] = []
        self._text = text

    def generate(self, **kwargs):
        self.calls.append(kwargs)
        return _Response(self._text)


class ExplodingSDK:
    """Raises whatever it is given — stands in for a daemon that is not running."""

    def __init__(self, exc: Exception) -> None:
        self._exc = exc

    def generate(self, **kwargs):
        raise self._exc


def _client(sdk=None, **kw) -> CappedOllamaClient:
    client = CappedOllamaClient(sdk if sdk is not None else CapturingSDK(), **kw)
    client.begin_draft()
    return client


class TestTheSeamShape:
    def test_it_returns_the_generated_text(self):
        assert _client().generate(
            model="m", prompt="p", temperature=0, thinking=False
        ) == "<memo><narrative_prose>x</narrative_prose></memo>"

    def test_temperature_is_passed_through_UNTOUCHED(self):
        """⛔ TEMP0-1 lives in the frozen adapter. This wrapper must neither set nor default it —
        a wrapper that "helpfully" forced 0 would make the adapter's guarantee untestable."""
        sdk = CapturingSDK()
        _client(sdk).generate(model="m", prompt="p", temperature=0, thinking=False)
        assert sdk.calls[-1]["options"]["temperature"] == 0

        sdk2 = CapturingSDK()
        _client(sdk2).generate(model="m", prompt="p", temperature=0.7, thinking=False)
        assert sdk2.calls[-1]["options"]["temperature"] == 0.7

    def test_model_is_passed_through_UNTOUCHED(self):
        sdk = CapturingSDK()
        _client(sdk).generate(model="llama3.1:8b", prompt="p", temperature=0, thinking=False)
        assert sdk.calls[-1]["model"] == "llama3.1:8b"

    @pytest.mark.parametrize("thinking", [True, False])
    def test_the_thinking_flag_reaches_the_sdk_both_ways(self, thinking):
        """⚑ Asserted in BOTH directions. A client hardcoding ``think=False`` would pass a
        one-directional test identically, and ``route_borderline``'s EXTENDED decision would be
        silently inert — the disconnection register #30 exists to name."""
        sdk = CapturingSDK()
        _client(sdk).generate(model="m", prompt="p", temperature=0, thinking=thinking)
        assert sdk.calls[-1]["think"] is thinking

    def test_it_does_not_stream(self):
        """A streaming response is not a ``str`` and would break the adapter's XML parse."""
        sdk = CapturingSDK()
        _client(sdk).generate(model="m", prompt="p", temperature=0, thinking=False)
        assert sdk.calls[-1]["stream"] is False

    def test_a_dict_shaped_response_also_works(self):
        class DictSDK:
            def generate(self, **kwargs):
                return {"response": "from-a-mapping"}

        assert _client(DictSDK()).generate(
            model="m", prompt="p", temperature=0, thinking=False
        ) == "from-a-mapping"

    def test_an_empty_response_becomes_an_empty_string_not_None(self):
        class NoneSDK:
            def generate(self, **kwargs):
                return _Response(None)  # type: ignore[arg-type]

        assert _client(NoneSDK()).generate(
            model="m", prompt="p", temperature=0, thinking=False
        ) == ""


class TestThePerDraftCap:
    """⛔ The correction that the clarification gate was opened for. Read the class docstring of
    ``CappedOllamaClient`` before changing anything here."""

    def test_it_refuses_once_the_per_draft_cap_is_reached(self):
        client = _client(max_calls=2)
        client.generate(model="m", prompt="p", temperature=0, thinking=False)
        client.generate(model="m", prompt="p", temperature=0, thinking=False)
        with pytest.raises(OllamaCallCapExceeded):
            client.generate(model="m", prompt="p", temperature=0, thinking=False)

    def test_the_cap_resets_after_begin_draft(self):
        """⛔ **LOAD-BEARING.** This is the entire difference between the corrected design and the
        ``CappedGeminiClient`` shape it started from. Against a monotonic per-instance counter the
        second draft raises and this fails."""
        client = _client(max_calls=2)
        client.generate(model="m", prompt="p", temperature=0, thinking=False)
        client.generate(model="m", prompt="p", temperature=0, thinking=False)

        client.begin_draft()  # a new draft begins

        client.generate(model="m", prompt="p", temperature=0, thinking=False)
        client.generate(model="m", prompt="p", temperature=0, thinking=False)
        assert client.call_count == 2

    def test_two_threads_keep_INDEPENDENT_counters(self):
        """⛔ **LOAD-BEARING — this is the race.** One client instance is shared by every
        concurrent draft (``@lru_cache(maxsize=1)``). With a plain ``self._count``, thread B's
        ``begin_draft`` zeroes thread A's count mid-flight and the cap bounds nothing.

        ⛔ **THE ASSERTION MUST BE ASYMMETRIC, AND THE FIRST VERSION OF THIS TEST WAS NOT.** It
        read both counts *after both threads had reset* and asserted ``{"A": 0, "B": 0}`` — which a
        single shared counter satisfies **identically**. It passed against the broken design and
        was rewritten. The discriminating question is not "what does each thread see after its own
        reset" but **"does B's reset damage A's in-flight count"**, so A must be observed AFTER B
        resets and BEFORE A resets again.
        """
        client = CappedOllamaClient(CapturingSDK(), max_calls=2)
        counted = threading.Barrier(2)
        b_has_reset = threading.Event()
        seen: dict[str, int] = {}
        errors: list[BaseException] = []

        def thread_a() -> None:
            try:
                client.begin_draft()
                client.generate(model="m", prompt="p", temperature=0, thinking=False)
                counted.wait(timeout=5)              # A has counted 1
                assert b_has_reset.wait(timeout=5)   # B has now zeroed ITS scope
                seen["A"] = client.call_count        # ⛔ must STILL be 1
            except BaseException as exc:  # noqa: BLE001 - surfaced via ``errors``
                errors.append(exc)

        def thread_b() -> None:
            try:
                client.begin_draft()
                client.generate(model="m", prompt="p", temperature=0, thinking=False)
                counted.wait(timeout=5)              # B has counted 1
                client.begin_draft()                 # B's next draft — must not touch A
                seen["B"] = client.call_count        # must be 0
                b_has_reset.set()
            except BaseException as exc:  # noqa: BLE001 - surfaced via ``errors``
                errors.append(exc)

        threads = [threading.Thread(target=thread_a), threading.Thread(target=thread_b)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert not errors, errors
        assert seen == {"A": 1, "B": 0}, seen

    def test_a_REUSED_thread_starts_at_zero(self):
        """⛔ **LOAD-BEARING.** Threadpool threads are pooled and REUSED, so the counter must be
        RESET at ``begin_draft``, not merely lazily initialized — a lazy ``if not hasattr`` leaves
        a reused thread mid-count.

        ⛔ **IT MUST BE A ONE-WORKER POOL, AND THE FIRST VERSION OF THIS TEST WAS NOT.** It spawned
        two fresh ``threading.Thread`` objects, each of which gets a **brand-new thread-local
        namespace** — so lazy initialization passed it and the test did not test its own name.
        ``ThreadPoolExecutor(max_workers=1)`` guarantees the *same* thread serves both drafts,
        which is the condition FastAPI's threadpool actually creates.
        """
        from concurrent.futures import ThreadPoolExecutor

        client = CappedOllamaClient(CapturingSDK(), max_calls=2)

        def draft() -> tuple[int, int]:
            client.begin_draft()
            client.generate(model="m", prompt="p", temperature=0, thinking=False)
            return threading.get_ident(), client.call_count

        with ThreadPoolExecutor(max_workers=1) as pool:
            first = pool.submit(draft).result(timeout=5)
            second = pool.submit(draft).result(timeout=5)

        assert first[0] == second[0], "the pool did not reuse the thread; the test proves nothing"
        assert [first[1], second[1]] == [1, 1], (first, second)

    def test_a_thread_that_never_drafted_reports_zero(self):
        """``call_count`` must not raise ``AttributeError`` on a fresh thread."""
        assert CappedOllamaClient(CapturingSDK()).call_count == 0

    def test_the_default_cap_has_headroom_over_the_retry_cap(self):
        """⚑ Pins the reasoning at ``MAX_CALLS_PER_DRAFT``: the citation-retry loop is already
        bounded at ``MEMO_CITATION_RETRY_CAP``, so this cap is defence-in-depth and must sit
        ABOVE it, never at or below — a cap at 2 would fire on a legitimate retry."""
        from backend.memo_agent_core.constants import MEMO_CITATION_RETRY_CAP

        assert MAX_CALLS_PER_DRAFT > MEMO_CITATION_RETRY_CAP


class TestUnreachableDaemon:
    def test_a_transport_failure_becomes_OllamaUnreachable(self):
        client = _client(ExplodingSDK(ConnectionError("refused")))
        with pytest.raises(OllamaUnreachable):
            client.generate(model="m", prompt="p", temperature=0, thinking=False)

    def test_the_message_NAMES_THE_HOST_it_tried(self):
        """⚑ Q3's hybrid half — the diagnostic reason the host is retained at all."""
        client = _client(ExplodingSDK(ConnectionError("refused")), host="http://example:1234")
        with pytest.raises(OllamaUnreachable, match="http://example:1234"):
            client.generate(model="m", prompt="p", temperature=0, thinking=False)

    def test_the_cap_refusal_is_NOT_swallowed_into_unreachable(self):
        """⛔ The wrapper's own refusal must escape as itself. If the broad ``except`` re-wrapped
        it, the two conditions §5.3 separates would collapse back into one at the source."""
        client = _client(max_calls=1)
        client.generate(model="m", prompt="p", temperature=0, thinking=False)
        with pytest.raises(OllamaCallCapExceeded):
            client.generate(model="m", prompt="p", temperature=0, thinking=False)

    def test_the_two_failure_MESSAGES_are_materially_different(self):
        """⛔ **STOP-GATE 3 at the source.** Asserted as DIFFERENT, not merely as present. They
        call for opposite operator responses: start Ollama vs. do not."""
        unreachable = _client(ExplodingSDK(ConnectionError("x")))
        with pytest.raises(OllamaUnreachable) as u:
            unreachable.generate(model="m", prompt="p", temperature=0, thinking=False)

        capped = _client(max_calls=1)
        capped.generate(model="m", prompt="p", temperature=0, thinking=False)
        with pytest.raises(OllamaCallCapExceeded) as c:
            capped.generate(model="m", prompt="p", temperature=0, thinking=False)

        assert str(u.value) != str(c.value)
        assert "running" in str(u.value)          # names the operator action
        assert "not a provider outage" in str(c.value)  # explicitly denies the other reading


class TestItLeaksNothing:
    def test_the_log_line_carries_LENGTH_not_the_prompt(self, caplog):
        secret = "APPLICANT SALARY 1234567 CONFIDENTIAL"
        with caplog.at_level(logging.INFO, logger="backend.app.ollama_client"):
            _client().generate(model="m", prompt=secret, temperature=0, thinking=False)
        rendered = "\n".join(r.getMessage() for r in caplog.records)
        assert secret not in rendered
        assert f"prompt_len={len(secret)}" in rendered

    def test_repr_does_not_delegate_to_the_wrapped_client(self):
        class LoudSDK:
            def __repr__(self):
                return "SDK(api_key='SHOULD-NEVER-APPEAR')"

            def generate(self, **kwargs):
                return _Response()

        assert "SHOULD-NEVER-APPEAR" not in repr(CappedOllamaClient(LoudSDK()))


class TestTheFactory:
    def test_importing_this_module_requires_no_daemon_and_no_sdk_call(self):
        """⚑ The laziness is the property that keeps the offline suite free of the SDK. If
        ``import ollama`` moved to module scope this file would still pass — but the whole suite
        would gain a hard dependency, so the assertion is on the module's own namespace."""
        import backend.app.ollama_client as mod

        assert not hasattr(mod, "Client")
        assert not hasattr(mod, "ollama")

    def test_it_builds_a_capped_client_and_passes_the_timeout(self, monkeypatch):
        captured: dict = {}

        class FakeClient:
            def __init__(self, host=None, timeout=None):
                captured["host"] = host
                captured["timeout"] = timeout

        import ollama

        monkeypatch.setattr(ollama, "Client", FakeClient)
        client = build_ollama_client(model_id="llama3.1:8b")

        assert isinstance(client, CappedOllamaClient)
        assert captured["timeout"] == DRAFT_TIMEOUT_SECONDS
        assert captured["host"] is None  # ⚑ Q3-A: the SDK resolves OLLAMA_HOST itself

    def test_the_default_host_is_used_for_MESSAGES_when_none_is_given(self, monkeypatch):
        class FakeClient:
            def __init__(self, host=None, timeout=None):
                pass

        import ollama

        monkeypatch.setattr(ollama, "Client", FakeClient)
        assert DEFAULT_OLLAMA_HOST in repr(build_ollama_client(model_id="m"))
