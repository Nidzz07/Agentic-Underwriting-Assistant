"""Tests for SubprocessParseWorker (Step 9) + resource limits (Sharpening 1).

Maps: NFR-INT-SEC1-SANDBOX + NFR-INT-PERF (hard bound). Every subprocess
failure mode -> deterministic ``unparseable``:

  * wall-time timeout (parent-kill)   -- runs on ALL platforms
  * crash / non-zero exit             -- all platforms
  * undecodable stdout                -- all platforms
  * RLIMIT_CPU (CPU-spin)             -- posix_only (Linux CI)
  * RLIMIT_AS  (OOM)                  -- posix_only (Linux CI)

Isolation: a crash in one parse never affects the next. Determinism: the same
input yields the same content_hash.
"""
from __future__ import annotations

import time

import pytest

from backend.intake.parser import ParseOutcome, SubprocessParseWorker
from backend.intake.resource_limits import HAS_RESOURCE, apply_resource_limits
from backend.intake.schema import DocStatus, DocType

_FAKE = ["-m"]  # placeholder; real cmd built below


def _worker(mode: str, timeout_s: float = 5.0, cpu_seconds: int = 5,
            mem_bytes: int = 256 * 1024 * 1024) -> SubprocessParseWorker:
    import sys
    cmd = [sys.executable, "-m", "backend.intake.tests.fake_worker", mode]
    return SubprocessParseWorker(
        timeout_s=timeout_s, cpu_seconds=cpu_seconds, mem_bytes=mem_bytes, worker_cmd=cmd
    )


# --------------------------------------------------------------------------
# Happy path — canonical, deterministic
# --------------------------------------------------------------------------
def test_ok_parse_returns_parsed_entry_with_hash_and_payload():
    outcome = _worker("ok").parse(DocType.SALARY_SLIP, "unused.pdf")
    assert isinstance(outcome, ParseOutcome)
    assert outcome.entry.status is DocStatus.PARSED
    assert outcome.entry.content_hash  # non-empty sha256
    assert "net pay 50000" in outcome.payload["extracted_text"]


def test_same_input_same_content_hash():
    a = _worker("ok").parse(DocType.SALARY_SLIP, "unused.pdf")
    b = _worker("ok").parse(DocType.SALARY_SLIP, "unused.pdf")
    assert a.entry.content_hash == b.entry.content_hash  # canonical -> deterministic


# --------------------------------------------------------------------------
# Wall-time timeout (parent-kill) — ALL platforms
# --------------------------------------------------------------------------
def test_wall_time_timeout_maps_to_unparseable_on_all_platforms():
    start = time.monotonic()
    outcome = _worker("hang", timeout_s=0.5).parse(DocType.BANK_STATEMENT, "unused.pdf")
    elapsed = time.monotonic() - start
    assert outcome.entry.status is DocStatus.UNPARSEABLE
    assert elapsed < 30  # parent killed the child promptly, did not wait 60s


# --------------------------------------------------------------------------
# Crash / undecodable output — ALL platforms
# --------------------------------------------------------------------------
def test_crash_nonzero_exit_maps_to_unparseable():
    outcome = _worker("crash").parse(DocType.MEDICAL_QUESTIONNAIRE, "unused.pdf")
    assert outcome.entry.status is DocStatus.UNPARSEABLE
    assert outcome.payload == {}


def test_undecodable_stdout_maps_to_unparseable():
    outcome = _worker("garbage").parse(DocType.SALARY_SLIP, "unused.pdf")
    assert outcome.entry.status is DocStatus.UNPARSEABLE


def test_decoded_but_non_mapping_output_maps_to_unparseable():
    # Valid IPC bytes that decode to a non-dict must not be trusted as a parse.
    outcome = _worker("notdict").parse(DocType.SALARY_SLIP, "unused.pdf")
    assert outcome.entry.status is DocStatus.UNPARSEABLE


# --------------------------------------------------------------------------
# Isolation — a crash does not contaminate the next parse
# --------------------------------------------------------------------------
def test_crash_then_ok_parse_is_isolated():
    assert _worker("crash").parse(DocType.SALARY_SLIP, "x.pdf").entry.status is DocStatus.UNPARSEABLE
    ok = _worker("ok").parse(DocType.SALARY_SLIP, "x.pdf")
    assert ok.entry.status is DocStatus.PARSED  # fresh subprocess, no state carried


# --------------------------------------------------------------------------
# Kernel-enforced limits — POSIX only (Linux CI). Generous wall timeout so the
# OS limit, not the wall clock, is what terminates the child.
# --------------------------------------------------------------------------
@pytest.mark.posix_only
def test_cpu_spin_killed_by_rlimit_cpu():
    outcome = _worker("spin", timeout_s=30, cpu_seconds=1).parse(DocType.SALARY_SLIP, "x.pdf")
    assert outcome.entry.status is DocStatus.UNPARSEABLE


@pytest.mark.posix_only
def test_oom_killed_by_rlimit_as():
    outcome = _worker("alloc", timeout_s=30, mem_bytes=64 * 1024 * 1024).parse(
        DocType.SALARY_SLIP, "x.pdf"
    )
    assert outcome.entry.status is DocStatus.UNPARSEABLE


# --------------------------------------------------------------------------
# resource_limits seam
# --------------------------------------------------------------------------
def test_apply_resource_limits_is_safe_to_call():
    # On Windows (no resource module) this is a clean no-op; on POSIX the
    # dedicated posix test asserts the setrlimit calls.
    if not HAS_RESOURCE:
        assert apply_resource_limits(2, 100 * 1024 * 1024) is None


@pytest.mark.posix_only
def test_apply_resource_limits_sets_cpu_and_as(monkeypatch):
    import backend.intake.resource_limits as rl

    calls = []
    monkeypatch.setattr(rl.resource, "setrlimit", lambda which, limits: calls.append((which, limits)))
    rl.apply_resource_limits(3, 123 * 1024 * 1024)
    kinds = {c[0] for c in calls}
    assert rl.resource.RLIMIT_CPU in kinds
    assert rl.resource.RLIMIT_AS in kinds
