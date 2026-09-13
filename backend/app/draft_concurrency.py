"""Bounding concurrent memo drafts — the capacity half of the live-LLM-drafting pass.

⛔ **THE PROBLEM THIS SOLVES.** A live draft is a network call to a local Ollama daemon that can
take **tens of seconds** on a cold model load. R11 runs on FastAPI's threadpool (40 workers by
default), and that pool is **shared with R10's submissions** — so N concurrent drafts against a
single-threaded local daemon would occupy N workers doing nothing but waiting, and enough of them
would starve submission itself.

⚑ **DELIBERATELY MODELLED ON ``parse_concurrency.py``, INCLUDING ITS HARD-WON CHOICE OF PRIMITIVE.**
Read that module's header before changing anything here: a module-level ``asyncio.Semaphore``
raises *"bound to a different event loop"* the second time it is **contended from a different
loop**, and this suite creates a fresh loop per ``TestClient``. ``anyio.CapacityLimiter`` is
async-aware, is acquired by the async caller (so waiting never holds a threadpool thread hostage),
and is the primitive ``anyio.to_thread.run_sync`` already accepts — so **the bound and the offload
cannot be separated by a later edit.**

**No LLM. No credentials. No applicant data passes through this module** — it schedules a callable.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Callable, Optional, TypeVar

import anyio
import anyio.to_thread

T = TypeVar("T")

#: ⛔ The maximum memo drafts in flight at once, process-wide.
#:
#: ⚑ **ONE, not two** — and the reason differs from ``MAX_CONCURRENT_PARSES``'s. A local Ollama
#: daemon serving one model **serializes generation anyway**; a second concurrent draft would not
#: run faster, it would interleave and make both slower while occupying a second threadpool worker
#: for the whole cold-load-plus-generate window. Bounding at one turns that into a queue.
#:
#: ⛔ **CORRECTNESS DOES NOT DEPEND ON THIS VALUE — and that is a deliberate, load-bearing
#: property.** It would have been easy to make the per-draft call cap safe by serializing drafts
#: here, so that one shared counter could never be raced. That was REJECTED: it would make a
#: **tuning knob** silently load-bearing for **correctness**, so a future engineer raising this
#: number for throughput would reintroduce a race with nothing failing. The cap is instead made
#: safe at its own layer, by a thread-local counter in ``ollama_client.py``. **Raising this number
#: must remain a pure performance decision.**
MAX_CONCURRENT_DRAFTS: int = 1


@lru_cache(maxsize=1)
def draft_limiter() -> anyio.CapacityLimiter:
    """The one process-wide bound — lazy and cached, the idiom every other provider here uses.

    ⚑ A bound is only a bound if **every caller shares the same instance**; two limiters would
    silently permit ``2 x MAX_CONCURRENT_DRAFTS``.
    """
    return anyio.CapacityLimiter(MAX_CONCURRENT_DRAFTS)


async def run_bounded_draft(
    func: Callable[..., T],
    *args: Any,
    limiter: Optional[anyio.CapacityLimiter] = None,
) -> T:
    """Run blocking ``func(*args)`` in a worker thread, bounded by the draft limiter.

    ⛔ **THE CALLABLE MUST BE THE WHOLE DRAFT, NOT JUST THE MODEL CALL.** ``ollama_client``'s
    per-draft counter is **thread-local**, which is only equivalent to *per-draft* because a draft
    runs start-to-finish on **one** worker thread. Splitting ``pipeline.draft`` across threads would
    silently break that equivalence — the counter would reset mid-draft — so this helper is handed
    the entire pipeline call.

    ⚑ The permit is released by ``run_sync`` itself on **every** exit path, including an exception;
    a leaked permit would degrade to a **permanent hang** rather than an error, which is far harder
    to diagnose than a crash.

    The result is returned **unchanged** and exceptions propagate **unchanged** — which is what lets
    R11 catch ``OllamaUnreachable`` / ``OllamaCallCapExceeded`` by type across the thread boundary.
    """
    return await anyio.to_thread.run_sync(
        func, *args, limiter=limiter if limiter is not None else draft_limiter()
    )
