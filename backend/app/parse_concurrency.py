"""Bounding concurrent document parses — the capacity half of WIRE1-Fold-7.

⛔ **THE PROBLEM THIS SOLVES.** Each document is parsed in a subprocess with `RLIMIT_AS`
**256 MB** (`intake/parser.py`). FastAPI runs handlers in a threadpool of **40** by default, and
nothing anywhere bounds how many parses may be in flight — `parser.py` spawns unconditionally.
Meanwhile the process already holds uvicorn **plus** the fitted IsolationForest/SHAP model, which
is resident for the process lifetime (register #2, stage 3).

⚠️ Render's free plan is **documented** at 512 MB. **That figure has not been measured** and the
deployment pass owes a measurement (`document-upload-code-gen-plan.md` §11 item 1). If it is
right, **two concurrent parses can exceed the instance.** Bounded, they queue instead.
**A wait is a better failure than a kill.**

⚑ **ONE CALL BOUNDS AND OFFLOADS**, which is why this module is four lines of logic. Two separate
mechanisms — a semaphore here, a threadpool call there — can drift apart; a later edit could
offload without acquiring, and nothing would notice until production memory spiked.
`anyio.to_thread.run_sync` takes the limiter natively, so the bound and the offload **cannot be
separated**.

⛔ **WHY `anyio.CapacityLimiter` AND NOT `asyncio.Semaphore` — corrected by measurement, and read
this before changing it back.** The design's Constraint 2 specified `asyncio.Semaphore`. Against
the installed runtime, a module-level `asyncio.Semaphore` raises

    RuntimeError: <asyncio.locks.Semaphore object ...> is bound to a different event loop

the **second time it is CONTENDED from a different event loop**. `TestClient` creates a fresh loop
per client and this suite makes many, so the suite would have broken — but only once a
*concurrency* test existed, i.e. at stage 5, far from the cause. ⚑ The uncontended path works
fine, which is exactly why it would not have been caught earlier.

`CapacityLimiter` honours everything Constraint 2 was protecting: it is **async-aware** (waiters
park on the event loop, they do not block it), it is acquired **by the async caller** rather than
inside the worker (so waiting never holds a threadpool thread hostage), and it is the primitive
`anyio.to_thread.run_sync` already accepts. Pinned by
`test_the_limiter_survives_being_used_from_TWO_event_loops`.

**No LLM. No credentials. No applicant data passes through this module** — it schedules a callable.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Callable, Optional, TypeVar

import anyio
import anyio.to_thread

T = TypeVar("T")

#: ⛔ The maximum number of document parses in flight at once, process-wide.
#:
#: ⚑ **TWO, not one**, deliberately: one would serialize every concurrent submission behind a
#: ~15 s worst case (three documents at the 5 s parse timeout), and the point of the bound is to
#: cap memory, not to eliminate concurrency. Two keeps peak parse memory at ~512 MB of *address
#: space* — which is a reservation, not resident usage — while letting two submissions progress.
#:
#: ⚠️ **This number is a judgement against an UNMEASURED memory figure.** It is a named constant
#: precisely so it can be revisited at deploy time when the real instance size is known.
MAX_CONCURRENT_PARSES: int = 2


@lru_cache(maxsize=1)
def parse_limiter() -> anyio.CapacityLimiter:
    """The one process-wide bound — lazy and cached, the idiom the four other providers use.

    ⚑ A bound is only a bound if **every caller shares the same instance**; two limiters would
    silently permit ``2 x MAX_CONCURRENT_PARSES``.
    """
    return anyio.CapacityLimiter(MAX_CONCURRENT_PARSES)


async def run_bounded_parse(
    func: Callable[..., T],
    *args: Any,
    limiter: Optional[anyio.CapacityLimiter] = None,
) -> T:
    """Run blocking ``func(*args)`` in a worker thread, bounded by the parse limiter.

    ⛔ **The caller must be ``async``, and the callable must be the BLOCKING one.** This is the
    shape stage 5's handler wires into: `subprocess.run` never touches the event loop, and the
    permit is held by the awaiting coroutine rather than by a threadpool worker.

    ⚑ The permit is released by ``run_sync`` itself on **every** exit path, including an
    exception — a leaked permit would degrade to a **permanent hang** rather than an error, which
    is the worst available failure shape and far harder to diagnose than a crash.

    The result is returned **unchanged** and exceptions propagate **unchanged**: this helper
    schedules, it does not transform.
    """
    return await anyio.to_thread.run_sync(
        func, *args, limiter=limiter if limiter is not None else parse_limiter()
    )
