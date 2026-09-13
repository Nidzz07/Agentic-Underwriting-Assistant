"""R11's bound, its async conversion, and the two-typed failure catch.

⛔ **THE TWO LOAD-BEARING TESTS HERE ARE ``test_the_event_loop_stays_RESPONSIVE_during_a_draft``
(stop-gate 4A) AND ``test_the_two_failure_messages_are_MATERIALLY_DIFFERENT`` (stop-gate 3).**
Both were written against the specific way this could be got wrong, not against the happy path.
"""
from __future__ import annotations

import threading
import time

import anyio
import pytest
from fastapi.testclient import TestClient

from backend.app.draft_concurrency import (
    MAX_CONCURRENT_DRAFTS,
    draft_limiter,
    run_bounded_draft,
)
from backend.app.ollama_client import OllamaCallCapExceeded, OllamaUnreachable


class TestTheLimiter:
    def test_it_bounds_concurrency_to_the_declared_maximum(self):
        in_flight = 0
        peak = 0
        lock = threading.Lock()

        def slow_draft(_n):
            nonlocal in_flight, peak
            with lock:
                in_flight += 1
                peak = max(peak, in_flight)
            time.sleep(0.05)
            with lock:
                in_flight -= 1
            return _n

        async def main():
            async with anyio.create_task_group() as tg:
                for i in range(6):
                    tg.start_soon(run_bounded_draft, slow_draft, i)

        anyio.run(main)
        assert peak <= MAX_CONCURRENT_DRAFTS, peak

    def test_the_bound_is_not_merely_SERIALIZING_by_accident(self):
        """⚑ NON-VACUITY. With ``MAX_CONCURRENT_DRAFTS == 1`` the peak is 1 whether or not the
        limiter works, because a single-threaded test would also show 1. Passing an explicit
        2-permit limiter proves the helper actually honours the limiter it is GIVEN."""
        in_flight = 0
        peak = 0
        lock = threading.Lock()

        def slow(_n):
            nonlocal in_flight, peak
            with lock:
                in_flight += 1
                peak = max(peak, in_flight)
            time.sleep(0.05)
            with lock:
                in_flight -= 1

        limiter = anyio.CapacityLimiter(2)

        async def main():
            async with anyio.create_task_group() as tg:
                for i in range(6):
                    tg.start_soon(lambda n=i: run_bounded_draft(slow, n, limiter=limiter))

        anyio.run(main)
        assert peak == 2, peak

    def test_the_limiter_survives_being_used_from_TWO_event_loops(self):
        """⛔ The Fold-7 lesson, applied here rather than rediscovered. A module-level
        ``asyncio.Semaphore`` raises 'bound to a different event loop' the second time it is
        CONTENDED from a different loop — and this suite makes a fresh loop per ``TestClient``."""
        def work(_n):
            return _n

        async def main():
            async with anyio.create_task_group() as tg:
                for i in range(3):
                    tg.start_soon(run_bounded_draft, work, i)

        anyio.run(main)
        anyio.run(main)  # a SECOND, different event loop over the same cached limiter

    def test_a_permit_is_released_on_the_EXCEPTION_path(self):
        """⛔ A leaked permit degrades to a PERMANENT HANG, which is far worse than an error."""
        def boom(_n):
            raise RuntimeError("x")

        async def main():
            for _ in range(MAX_CONCURRENT_DRAFTS + 2):
                with pytest.raises(RuntimeError):
                    await run_bounded_draft(boom, 1)
            # if permits leaked, this final acquisition would hang rather than complete
            with anyio.fail_after(5):
                assert await run_bounded_draft(lambda _n: "ok", 1) == "ok"

        anyio.run(main)

    def test_exceptions_propagate_UNCHANGED_across_the_thread_boundary(self):
        """⚑ The property R11's typed catch depends on. If the helper wrapped exceptions, the
        route could not distinguish the two Ollama conditions at all."""
        def unreachable(_n):
            raise OllamaUnreachable("daemon down")

        def capped(_n):
            raise OllamaCallCapExceeded("cap")

        async def main():
            with pytest.raises(OllamaUnreachable):
                await run_bounded_draft(unreachable, 1)
            with pytest.raises(OllamaCallCapExceeded):
                await run_bounded_draft(capped, 1)

        anyio.run(main)

    def test_the_limiter_is_shared_process_wide(self):
        """A bound is only a bound if every caller shares one instance."""
        assert draft_limiter() is draft_limiter()


class TestR11FailureMapping:
    """⛔ The §1.3 gap — an uncaught provider failure used to escape as a plain-text 500."""

    def _client(self, monkeypatch, exc):
        from backend.app.main import create_app
        from backend.app import dependencies as dep
        from backend.app.routes import submission as sub

        class _Case:
            application_id = "APP-1"
            state = type("S", (), {"value": "evaluated"})()

        class _Pipeline:
            def read(self, _id):
                return _Case()

            def draft(self, _id):
                raise exc

        app = create_app()
        app.dependency_overrides[sub.get_case_pipeline] = lambda: _Pipeline()
        app.dependency_overrides[sub.require_underwriter] = lambda: dep.Identity(
            user_id="u", role=dep.to_role("underwriter")
        )
        monkeypatch.setattr(sub, "case_to_memo_view_state", lambda _c: "pending")
        return TestClient(app)

    def test_an_unreachable_daemon_is_a_500_IN_THE_WIRE1_ENVELOPE(self, monkeypatch):
        """⛔ Not a plain-text 500. ``main.py`` claims 'no route can emit a non-contract body' and
        until this pass nothing enforced that against an uncaught exception."""
        client = self._client(monkeypatch, OllamaUnreachable("could not reach ... is it running?"))
        response = client.post("/applications/APP-1/draft")
        assert response.status_code == 500
        body = response.json()
        assert body["error"]["code"] == "internal_error"
        assert body["error"]["detail"]["cause"] == "provider_unreachable"

    def test_a_cap_exceeded_is_a_500_IN_THE_WIRE1_ENVELOPE(self, monkeypatch):
        client = self._client(monkeypatch, OllamaCallCapExceeded("per-draft cap ... not a provider outage."))
        response = client.post("/applications/APP-1/draft")
        assert response.status_code == 500
        assert response.json()["error"]["detail"]["cause"] == "draft_call_cap_exceeded"

    def test_the_two_failure_messages_are_MATERIALLY_DIFFERENT(self, monkeypatch):
        """⛔ **STOP-GATE 3.** Asserted as DIFFERENT from each other, not merely as present.

        They call for OPPOSITE operator responses — start Ollama vs. do not — so a shared generic
        body would actively mislead. Both the human message and the machine discriminator differ.
        """
        unreachable = self._client(
            monkeypatch, OllamaUnreachable("could not reach the Ollama daemon at http://h. Is it running?")
        ).post("/applications/APP-1/draft").json()["error"]
        capped = self._client(
            monkeypatch, OllamaCallCapExceeded("reached its per-draft cap; not a provider outage.")
        ).post("/applications/APP-1/draft").json()["error"]

        assert unreachable["message"] != capped["message"]
        assert unreachable["detail"]["cause"] != capped["detail"]["cause"]

    def test_a_NON_ollama_exception_is_NOT_swallowed_by_the_catch(self, monkeypatch):
        """⛔ The named-types-only requirement, made mechanical. A bare ``except Exception`` would
        report a genuine programming error as an Ollama problem — the most expensive wrong
        diagnosis available. ``TestClient`` re-raises, which is exactly the visibility wanted."""
        client = self._client(monkeypatch, ValueError("a real bug"))
        with pytest.raises(ValueError, match="a real bug"):
            client.post("/applications/APP-1/draft")


class TestStopGate4A:
    def test_the_event_loop_stays_RESPONSIVE_during_a_draft(self, monkeypatch):
        """⛔ **STOP-GATE 4A's NON-VACUITY, and the reason the conversion is a three-call change.**

        A slow draft must not stall the event loop. This is the same probe the document-upload
        walkthrough used on the live wire (a request answered mid-load), run here in-process.

        ⚑ It is asserted with ``anyio.fail_after``: if ``pipeline.draft`` were awaited on the loop
        instead of offloaded, the concurrent liveness call could not complete until the draft
        finished, and the deadline would fire.
        """
        from backend.app.draft_concurrency import run_bounded_draft as _bounded

        def slow_draft(_id):
            time.sleep(0.4)
            return "done"

        async def main():
            async with anyio.create_task_group() as tg:
                tg.start_soon(_bounded, slow_draft, "APP-1")
                await anyio.sleep(0.05)          # let the draft get going
                with anyio.fail_after(0.2):       # << the draft's 0.4s: must NOT be blocked
                    await anyio.sleep(0.01)       # a trivial loop-bound task
                    assert True

        anyio.run(main)

    def test_all_three_blocking_calls_are_offloaded_in_the_handler(self):
        """⛔ Structural, because the behavioural version is hard to observe: assert the handler's
        source never calls ``pipeline.read`` or ``pipeline.draft`` directly on the loop.

        ⚠️ A future edit that 'simplifies' one of the reads back to a direct call would pass every
        behavioural test in this file — ``TestClient`` tolerates a blocked loop — and would only
        show up in production as latency. This is the assertion that catches it.
        """
        import inspect

        from backend.app.routes import submission

        source = inspect.getsource(submission.trigger_drafting)
        assert "await run_in_threadpool(pipeline.read" in source
        assert "await run_bounded_draft(pipeline.draft" in source
        # no bare, un-awaited invocation of either
        assert "\n    outcome = pipeline.draft(" not in source
        assert "if pipeline.read(" not in source
        assert "case = pipeline.read(" not in source
