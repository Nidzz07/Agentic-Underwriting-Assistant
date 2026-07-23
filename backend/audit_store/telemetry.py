"""TelemetryEmitter — allowlist, demographic-free telemetry (Step 8).

NFR Design §8. Allowlist Pydantic schemas whose only ``str`` leaves are **metadata
ids** (``decision_id`` / ``rulebook_version``); everything else is an ``int`` /
``bool`` / ``Enum``. There is **no applicant-profile / demographic / free-text
field** (no ``reason``, ``memo_hash``, ``underwriter_id``, profile) — CON-BR1
extends to telemetry **by construction** (NFR-AUDIT-OBS-1). ``extra="forbid"``
rejects any sneaked-in field. **Distinct from the SEC-5 audit trail** (which
deliberately persists the full record).

Performance is **observed-only** (NFR-AUDIT-PERF-1): commit/replay ``*_micros`` are
emitted for the soft-budget dashboard and **never gated**. Emit-only — the
``observability`` unit wires the stack (reference-not-own).
"""
from __future__ import annotations

from enum import Enum
from typing import Callable, Optional, Union

from pydantic import BaseModel, ConfigDict

from backend.audit_store.record_schema import AuditRecord, CommitAction
from backend.audit_store.replay_service import ReplayVerdict


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ReplayOutcome(str, Enum):
    MATCH = "match"
    MISMATCH = "mismatch"


class CommitTelemetry(_Frozen):
    decision_id: str            # metadata id
    rulebook_version: str       # metadata
    action: CommitAction        # enum
    commit_micros: int          # observed-only timing


class ReplayTelemetry(_Frozen):
    decision_id: str            # metadata id
    rulebook_version: str       # metadata
    outcome: ReplayOutcome      # enum
    engine_drift: bool          # forensic flag
    rulebook_drift: bool        # forensic flag
    replay_micros: int          # observed-only timing


class TelemetryEmitter:
    """Emit-only seam. The ``observability`` unit supplies the ``sink``."""

    def __init__(self, sink: Optional[Callable[[Union[CommitTelemetry, ReplayTelemetry]], None]] = None) -> None:
        self._sink = sink
        self.last: Optional[Union[CommitTelemetry, ReplayTelemetry]] = None

    def emit_commit(self, record: AuditRecord, commit_micros: int) -> CommitTelemetry:
        telemetry = CommitTelemetry(
            decision_id=record.decision_id,
            rulebook_version=record.audit_tuple.rulebook_version,
            action=record.committed_decision.action,
            commit_micros=commit_micros,
        )
        return self._push(telemetry)

    def emit_replay(
        self, verdict: ReplayVerdict, rulebook_version: str, replay_micros: int
    ) -> ReplayTelemetry:
        telemetry = ReplayTelemetry(
            decision_id=verdict.decision_id,
            rulebook_version=rulebook_version,
            outcome=ReplayOutcome.MATCH if verdict.match else ReplayOutcome.MISMATCH,
            engine_drift=verdict.engine_drift,
            rulebook_drift=verdict.rulebook_drift,
            replay_micros=replay_micros,
        )
        return self._push(telemetry)

    def _push(self, telemetry):
        if self._sink is not None:
            self._sink(telemetry)
        self.last = telemetry
        return telemetry
