"""C-CASE-2 — the pending-store entities.

**Header comment — DOCUMENTATION ONLY, never enforcement** (each property is scan-enforced in
C-CASE-8): holds no LLM; edits no frozen unit; declares no verdict; **never re-implements the
commit gate, the authz check, or a write to ``audit_record``**; no network at tier-U.

**BR-CASE-7 / P-CASE-1 (Q8-A of the FD).** The two rich shapes are persisted as **CANON-SER
``BYTEA`` + a ``content_hash``**, mirroring the frozen ``0001_initial_schema.sql`` verbatim —
NOT as JSON. CANON-SER guarantees **P1** stable key ordering · **P2** ``Decimal`` as string, never
IEEE float · **P3** canonical scalars · **P4** no volatile fields, so *"the same logical content
serializes to the same bytes on every run"*. That makes the pending and committed sides
**byte-identical**, putting **no conversion on the replay path**.

The **four version stamps** stay **first-class scalar columns** (Q2-A) so the reproducibility
invariant is directly inspectable rather than buried in a blob.

**Bias-free**: ``ApplicantProfile`` is persisted **as a frozen shape, not widened** — no
demographic field is added, read, or indexed here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from backend.case_lifecycle.states import CaseState


@dataclass(frozen=True)
class PendingApplication:
    """One pre-commit case. ``rule_results_*`` are ``None`` until the ``evaluated`` transition."""

    application_id: str
    state: CaseState
    profile_canonical: bytes                      # CANON-SER bytes (frozen adapter)
    profile_content_hash: str                     # sha256 over those bytes
    rule_results_canonical: Optional[bytes] = None
    rule_results_content_hash: Optional[str] = None
    rulebook_version: Optional[str] = None        # stamp — first-class scalar
    engine_version: Optional[str] = None          # stamp — first-class scalar


@dataclass(frozen=True)
class PendingRecommendation:
    """⚑ Created ONLY at the ``drafted`` transition.

    Its PK, ``recommendation_id``, is **the key R5 commits by** — which is why a ``failed`` case
    can never reach the commit boundary: the object R5 is keyed by simply does not exist for it
    (COMMITBOUND-1(c)).

    Its fields are exactly what a frozen ``CommitContext`` needs that the application row does
    not already carry.
    """

    recommendation_id: str
    application_id: str
    memo_canonical: bytes
    memo_hash: str                                # stamp
    model_version: str                            # stamp
    engine_version: str                           # stamp
    rulebook_version: str                         # stamp
    outlier_canonical: Optional[bytes] = None
