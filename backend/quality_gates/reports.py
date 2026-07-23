"""C8 ``EvidenceReportBase`` + the four evidence-record shapes (P9 / NFR-QG-EVIDENCE-1).

Each gate emits a **human-readable, reproducible** auditor evidence record
(US-PLAT-3/4/5). The shared base carries only cross-cutting *shape* concerns — a
``passed`` field and a readable serialization — and **no** gate/coverage/engine
logic (ND-QG-Fold-1), so it cannot blur the C6/C7 dual-producer separation.

**Determinism (EVIDENCE-1)** — a report is a pure function of ``(corpus, rulebook,
engine)``: the provenance stamp (``generated_at``) is **NOT a model field**, so two
runs on identical inputs produce **field-equal** models (no content-hash needed).
The provenance stamp is added only at ``to_json()`` / ``emit()`` time as a
serialization envelope — never part of model equality.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class EvidenceReportBase(_Frozen):
    """Shared base — determinism + readable serialization, no gate logic."""

    passed: bool

    def to_readable_dict(self) -> dict[str, Any]:
        """The human-readable projection (no provenance — deterministic content)."""
        return self.model_dump(mode="json")

    def to_json(self, *, generated_at: Optional[str] = None, indent: int = 2) -> str:
        """Readable JSON. ``generated_at`` is an optional provenance **envelope**
        (never a model field / never part of equality)."""
        payload = self.to_readable_dict()
        if generated_at is not None:
            payload = {"generated_at": generated_at, **payload}
        return json.dumps(payload, indent=indent, sort_keys=True, default=str)

    def emit(self, output_dir: str | Path, *, generated_at: Optional[str] = None) -> Path:
        """Write the readable JSON evidence artifact to ``output_dir`` (default
        repo-level ``reports/quality_gates/`` per Q1-A) — one file per gate."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"{type(self).__name__}.json"
        path.write_text(self.to_json(generated_at=generated_at), encoding="utf-8")
        return path


class SwapRecord(_Frozen):
    """One bias-swap comparison row (auditor-readable)."""

    application_id: str
    swapped_fields: list[str]
    baseline_recommendation: str
    swapped_recommendation: str


class BiasSwapReport(EvidenceReportBase):
    """CON-BR1 evidence — delta=0 over the corpus (any delta blocking)."""

    profiles_tested: int
    swaps: list[SwapRecord] = Field(default_factory=list)
    delta_count: int


class ReproducibilityReport(EvidenceReportBase):
    """CON-BR2/AC-1 evidence — ×10 identical projection per profile (100%)."""

    profiles_tested: int
    runs: int
    mismatches: list[dict[str, Any]] = Field(default_factory=list)
    reproducibility_pct: float


class RuleCoverageReport(EvidenceReportBase):
    """QA-3 evidence — every rule reaches a definite PASS/FAIL (100%)."""

    rulebook_version: str
    total_rules: int
    covered_rule_ids: list[str] = Field(default_factory=list)
    uncovered_rule_ids: list[str] = Field(default_factory=list)
    coverage_pct: float


class CoverageGateReport(EvidenceReportBase):
    """AC-5 evidence — ONE shape written by TWO distinct producers (ND-QG-Fold-1):
    C6 CoverageWiringGate sets ``passed`` + the wiring fields; C7
    CoverageEvidenceGate sets ``measured_pct`` (informational, never ``passed``)."""

    wiring_present: bool = False
    fail_under_configured: Optional[int] = None
    measured_pct: Optional[float] = None
