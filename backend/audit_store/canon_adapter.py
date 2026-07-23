"""CanonSerAdapter — canonicalize both payloads via the shared CANON-SER (Step 2).

NFR-AUDIT-CANON-1 / NFR Design §7. Normalizes a Pydantic model (the imported
`RuleResultReport` or `ApplicantProfile`) via ``.model_dump()`` and calls the
**UNCHANGED** shared ``backend.common.canon_ser`` — one convention for both
``rule_results`` and ``profile_canonical`` (the `RulebookCanonAdapter` / intake
`CanonSerAdapter` precedent). ``content_hash = sha256(canonical bytes)`` is the
pre-replay tamper check. **audit-store is the §2.1 spec authority; `backend/common/`
is the shared location — no fork, no §2.1 change, no re-declaration.**
"""
from __future__ import annotations

from pydantic import BaseModel

from backend.common.canon_ser import canon_deserialize, canon_ser
from backend.common.canon_ser import content_hash as _content_hash
from backend.intake.schema import ApplicantProfile
from backend.rules_engine.report_schema import RuleResultReport


class CanonSerAdapter:
    """Delegate to the single shared canon_ser for both audit payloads (no fork)."""

    @staticmethod
    def canonical_bytes(model: BaseModel) -> bytes:
        return canon_ser(model.model_dump(mode="python"))

    @staticmethod
    def content_hash(model: BaseModel) -> str:
        return _content_hash(model.model_dump(mode="python"))

    @staticmethod
    def profile_from_canonical(data: bytes) -> ApplicantProfile:
        """Deserialize back to the EXACT intake ``ApplicantProfile`` (replay input)."""
        return ApplicantProfile.model_validate(canon_deserialize(data))

    @staticmethod
    def report_from_canonical(data: bytes) -> RuleResultReport:
        """Deserialize the recorded ``rule_results`` back to rules-engine's report."""
        return RuleResultReport.model_validate(canon_deserialize(data))
