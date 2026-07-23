"""ReplayService — replay-as-detection (Step 6).

FD ``business-rules.md §5`` + ``business-logic-model.md §4``; NFR Design §5.
``ReplayService`` owns **load + call + compare only** — it has **no evaluation
logic of its own**. It loads the ``AuditRecord``, calls **rules-engine's pure
``evaluate()``** (imported ``RulesEngine``, **not reimplemented**) against the
**original ``rulebook_version``** (the load key) over the **exact persisted
``ApplicantProfile``**, and applies **rules-engine's own ``evaluation_output()``**
to **both** the recorded and the fresh report — a **single imported projection**,
never re-derived here (REPLAY-1).

Excluded from the equality set (so no *false* mismatch): ``timestamp`` /
``underwriter_id`` / ``reason`` / ``memo_hash`` and the provenance embedded in
``rule_results`` — ``rulebook_version`` (load key), ``content_hash``,
``engine_version`` (**forensic** — surfaced to explain a mismatch, never compared).
**No LLM, no memo re-draft, no re-commit** (REPLAY-2). Storage ≠ influence: the
snapshot holds demographics but ``evaluate()`` structurally excludes them (BR1-1).
"""
from __future__ import annotations

from typing import Any, NamedTuple, Optional

from backend.rules_engine.report import evaluation_output
from backend.audit_store.repository import AuditRepository


class ReplayNotFound(KeyError):
    """No ``AuditRecord`` exists for the requested ``decision_id``."""


class ReplayVerdict(NamedTuple):
    decision_id: str
    match: bool
    fresh_projection: dict[str, Any]
    recorded_projection: dict[str, Any]
    delta: Optional[dict[str, Any]]     # None on match; the forensic diff on mismatch
    engine_drift: bool                  # forensic — recorded vs fresh engine_version
    rulebook_drift: bool                # forensic — recorded vs fresh content_hash


class ReplayService:
    """Pure re-evaluation + comparison. ``engine`` is rules-engine's ``RulesEngine``
    (injected, reference-not-own — audit-store never evaluates rules itself)."""

    def __init__(self, repository: AuditRepository, engine) -> None:
        self._repository = repository
        self._engine = engine

    def replay(self, decision_id: str) -> ReplayVerdict:
        record = self._repository.get(decision_id)
        if record is None:
            raise ReplayNotFound(decision_id)

        profile = record.applicant_profile_snapshot.profile   # the exact intake profile
        version = record.audit_tuple.rulebook_version         # the load key
        recorded = record.audit_tuple.rule_results

        fresh = self._engine.evaluate(profile, version)       # rules-engine pure evaluate()

        # THE equality set — the single-sourced evaluation-output projection on both.
        recorded_proj = evaluation_output(recorded)
        fresh_proj = evaluation_output(fresh)
        match = recorded_proj == fresh_proj

        # Forensic distinguishers (recorded vs fresh) — never equality triggers.
        engine_drift = fresh.engine_version != recorded.engine_version
        rulebook_drift = fresh.content_hash != recorded.content_hash

        delta = None if match else {"recorded": recorded_proj, "fresh": fresh_proj}
        return ReplayVerdict(
            decision_id=decision_id, match=match,
            fresh_projection=fresh_proj, recorded_projection=recorded_proj,
            delta=delta, engine_drift=engine_drift, rulebook_drift=rulebook_drift,
        )
