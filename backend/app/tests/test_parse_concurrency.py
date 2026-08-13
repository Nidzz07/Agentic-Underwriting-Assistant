"""Bounding concurrent document parses (WIRE1-Fold-7, stage 3).

⛔ **NO ROUTE IN THIS FILE.** Q12(a) gave this its own stage because **a capacity bug is invisible
to a green suite** — every existing test passes against an implementation that would spawn forty
256 MB subprocesses at once. The bound is exercised here directly, against a stub, because R10
does not exist until stage 5 and testing it end-to-end would mean testing it never.

⚑ **WHY A BOUND EXISTS AT ALL.** Each parse is a subprocess with `RLIMIT_AS` **256 MB**. FastAPI
runs sync handlers in a threadpool of **40** by default, and the process already holds uvicorn
plus the fitted IsolationForest/SHAP model. Render's free plan is documented at 512 MB (**not
measured** — see the plan's carried-forward item 4). Unbounded, two concurrent submissions can
exceed the instance; bounded, they queue. **A wait is a better failure than a kill.**

⚑ **The tests below assume the stage-5 shape and do not need rework for it**: an `async` caller,
the blocking `subprocess.run` offloaded to a worker thread, and the bound acquired by the caller
— never inside the threadpool, where waiting would hold a worker hostage.
"""
from __future__ import annotations

import threading
import time

import anyio
import pytest

from backend.app import parse_concurrency as pc


def _recorder():
    """Records enter/exit around the blocking work so OVERLAP can be measured directly."""
    events: list[tuple[str, int, str]] = []
    lock = threading.Lock()

    def blocking(index: int) -> int:
        with lock:
            events.append(("enter", index, threading.current_thread().name))
        time.sleep(0.02)
        with lock:
            events.append(("exit", index, threading.current_thread().name))
        return index

    return events, blocking


def _max_overlap(events) -> int:
    depth = peak = 0
    for kind, _index, _thread in events:
        depth += 1 if kind == "enter" else -1
        peak = max(peak, depth)
    return peak


async def _run_many(blocking, count, limiter=None):
    results = []

    async def one(index):
        results.append(await pc.run_bounded_parse(blocking, index, limiter=limiter))

    async with anyio.create_task_group() as tg:
        for index in range(count):
            tg.start_soon(one, index)
    return results


class TestTheBoundIsNamedAndEnforced:
    """D1–D2."""

    def test_the_bound_is_a_named_constant(self):
        """D1. A literal buried in a call site cannot be found, reviewed, or tuned at deploy —
        and this value depends on a memory figure that is still **documented, not measured**."""
        assert isinstance(pc.MAX_CONCURRENT_PARSES, int)
        assert pc.MAX_CONCURRENT_PARSES >= 1
        assert pc.parse_limiter().total_tokens == pc.MAX_CONCURRENT_PARSES

    def test_callers_beyond_the_bound_WAIT_rather_than_proceed(self):
        """D2. ⚑ **Asserted by OBSERVED OVERLAP, never by timing.** A sleep-based test would be
        flaky and would not say *why* it failed; counting concurrent occupancy says exactly what
        the bound is doing."""
        events, blocking = _recorder()
        limiter = anyio.CapacityLimiter(1)
        anyio.run(_run_many, blocking, 4, limiter)

        assert _max_overlap(events) == 1, events
        assert len([e for e in events if e[0] == "enter"]) == 4, "not every caller ran"

    def test_the_bound_is_not_merely_SERIALIZING_everything(self):
        """⚑ NON-VACUITY for D2, and the half that makes it mean something. *"Never exceeds the
        bound"* is also satisfied by an implementation that runs everything one at a time — which
        would be a correctness-preserving, throughput-destroying bug. With a bound of 2, the
        observed peak must actually REACH 2."""
        events, blocking = _recorder()
        limiter = anyio.CapacityLimiter(2)
        anyio.run(_run_many, blocking, 6, limiter)

        assert _max_overlap(events) == 2, events


class TestTheShapeStage5WillWireInto:
    """D3–D4 — Constraints 1 and 2 from the ambiguity-check, pinned before the handler exists."""

    def test_the_blocking_work_runs_OFF_the_event_loop_thread(self):
        """D4. ⛔ **Constraint 1.** `SubprocessParseWorker.parse` calls `subprocess.run`, which is
        fully blocking. `async def` handlers run **on the event loop**, so calling it directly
        would freeze the whole process for up to ~15 s — every request, health checks included.
        The failure is invisible in a single-request test, so it is pinned structurally here."""
        events, blocking = _recorder()
        loop_thread = threading.current_thread().name
        anyio.run(_run_many, blocking, 2, anyio.CapacityLimiter(2))

        worker_threads = {name for _kind, _i, name in events}
        assert loop_thread not in worker_threads, f"blocking work ran on the loop thread {loop_thread}"

    def test_the_limiter_is_an_ASYNC_primitive_acquired_by_the_CALLER(self):
        """D3. ⛔ **Constraint 2, CORRECTED BY MEASUREMENT — read this before changing it back.**

        The approved constraint said `asyncio.Semaphore`. Measured against the installed runtime,
        a module-level `asyncio.Semaphore` raises

            RuntimeError: <asyncio.locks.Semaphore ...> is bound to a different event loop

        the **second time it is CONTENDED from a different loop** — and `TestClient` creates a
        fresh loop per client, of which this suite makes many. It survives the *uncontended* case,
        so the failure would not have appeared until a concurrency test existed: **stage 5.**

        `anyio.CapacityLimiter` is loop-agnostic, is the primitive `anyio.to_thread.run_sync`
        accepts natively, and honours everything Constraint 2 was protecting — async-aware,
        acquired by the caller, waiters parked on the loop rather than holding a thread.
        """
        assert isinstance(pc.parse_limiter(), anyio.CapacityLimiter)
        assert not isinstance(pc.parse_limiter(), threading.Semaphore().__class__)

    def test_the_limiter_survives_being_used_from_TWO_event_loops(self):
        """⛔ THE REGRESSION GUARD for the finding above. If someone swaps the limiter back to an
        `asyncio.Semaphore`, this fails — here, in stage 3, instead of confusingly in stage 5."""
        events, blocking = _recorder()
        anyio.run(_run_many, blocking, 3, pc.parse_limiter())
        anyio.run(_run_many, blocking, 3, pc.parse_limiter())
        assert len([e for e in events if e[0] == "enter"]) == 6

    def test_the_limiter_is_one_instance_per_process(self):
        """A bound is only a bound if every caller shares it. Two limiters would mean 2xN."""
        assert pc.parse_limiter() is pc.parse_limiter()


class TestThePermitIsAlwaysReleased:
    """D5–D6 — ⚑ a leaked permit degrades to a PERMANENT HANG, the worst failure shape here."""

    def test_the_permit_is_released_when_the_wrapped_work_RAISES(self):
        """D5. A parse that throws must not consume a permit forever. With a bound of 1, a leaked
        permit means the next submission waits for ever — and the symptom is a hung request with
        no error anywhere, which is far harder to diagnose than a crash."""
        limiter = anyio.CapacityLimiter(1)

        def exploding(_index):
            raise RuntimeError("pdfplumber fell over")

        async def scenario():
            with pytest.raises(RuntimeError):
                await pc.run_bounded_parse(exploding, 0, limiter=limiter)
            return limiter.borrowed_tokens

        assert anyio.run(scenario) == 0, "the permit leaked after an exception"

    def test_a_released_permit_is_REUSABLE(self):
        """D6. The other half: released, and genuinely usable again."""
        limiter = anyio.CapacityLimiter(1)

        def exploding(_index):
            raise RuntimeError("boom")

        async def scenario():
            with pytest.raises(RuntimeError):
                await pc.run_bounded_parse(exploding, 0, limiter=limiter)
            return await pc.run_bounded_parse(lambda i: i * 2, 21, limiter=limiter)

        assert anyio.run(scenario) == 42

    def test_the_result_is_returned_unchanged(self):
        """⚑ The helper must be transparent — it bounds and offloads, it does not transform."""
        sentinel = object()
        assert anyio.run(lambda: pc.run_bounded_parse(lambda: sentinel)) is sentinel
