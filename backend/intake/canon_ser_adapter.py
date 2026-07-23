"""CanonSerAdapter — ApplicantProfile <-> CANON-SER (NFR Design §6).

Serializes/deserializes the ``ApplicantProfile`` by DELEGATING to the single
shared CANON-SER spec (:mod:`backend.common.canon_ser`, defined by audit-store
§2.1). There is NO parallel serialization convention here — the adapter only
adapts the profile to/from the canonical form.

This is the replay dependency (NFR-INT-DET-2): ``audit-store`` persists the
profile snapshot via this exact spec, and ``ReplayService`` deserializes it back
to feed ``evaluate()``. Round-trip ``serialize -> deserialize -> serialize`` is
byte-identical, and types (``Decimal``/``date``/enums) are preserved.
"""
from __future__ import annotations

from backend.common.canon_ser import canon_deserialize, canon_ser, content_hash
from backend.intake.schema import ApplicantProfile


class CanonSerAdapter:
    """Adapts ``ApplicantProfile`` to the single shared CANON-SER spec."""

    @staticmethod
    def serialize(profile: ApplicantProfile) -> bytes:
        return canon_ser(profile.model_dump(mode="python"))

    @staticmethod
    def deserialize(data: bytes) -> ApplicantProfile:
        return ApplicantProfile(**canon_deserialize(data))

    @staticmethod
    def content_hash(profile: ApplicantProfile) -> str:
        return content_hash(profile.model_dump(mode="python"))
