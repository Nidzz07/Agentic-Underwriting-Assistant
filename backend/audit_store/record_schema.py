"""Record schema — the frozen ``AuditRecord`` superset (FD ``domain-entities.md``).

Pydantic v2 realization of the persisted **superset** entity that embeds the three
frozen shapes (`AuditTuple` 6-tuple + `CommittedDecision` + `ApplicantProfileSnapshot`)
+ the OOS-7 seam. Value objects: ``frozen=True`` + ``extra="forbid"``. **No frozen
shape is re-opened** — this composes them.

Reference-not-own: `AuditTuple.rule_results` is intake/rules-engine's **imported
`RuleResultReport`** (the full report field-for-field, §3.1); `ApplicantProfileSnapshot.
profile` is intake's **imported `ApplicantProfile`** (persisted verbatim, §4). Neither
is re-declared. The persisted CANON-SER columns (`rule_results` json, `profile_canonical`
json, `content_hash`) are produced by the `CanonSerAdapter` at the repository boundary.

Advisory-only: ``CommitAction`` (approve/override) is the one place "decision" is
correct — the **human's** committed action.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict

from backend.intake.schema import ApplicantProfile
from backend.rules_engine.report_schema import RuleResultReport


class DecisionStatus(str, Enum):
    """OOS-7 seam status. Phase-1/2 is write-once ``active`` (§5)."""
    ACTIVE = "active"
    SUPERSEDED = "superseded"


class CommitAction(str, Enum):
    """The human's committed action (CON-BR4). ``approve`` = agree; ``override`` = disagree."""
    APPROVE = "approve"
    OVERRIDE = "override"


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class AuditTuple(_Frozen):
    """The CON-AUDIT-1 6-tuple (FD §3.1) — every field required (TUPLE-1)."""
    rulebook_version: str                 # semver — the replay LOAD key
    rule_results: RuleResultReport        # the full imported report (CANON-SER at persist)
    timestamp: datetime                   # commit wall-clock — audit metadata, excluded from replay equality
    model_version: str                    # memo LLM/provider version (from memo-agent-core)
    memo_hash: str                        # hash of the committed memo (integrity via comparison)
    engine_version: str                   # rules-engine git SHA — forensic, not a replay equality trigger


class CommittedDecision(_Frozen):
    """The human commit linkage (FD §3.2) — WHO / WHAT / WHY."""
    recommendation_id: str
    underwriter_id: str                   # WHO — always mandatory (CON-BR4)
    action: CommitAction                  # WHAT — closed enum
    reason: Optional[str] = None          # WHY — mandatory (non-blank) on override; enforced at the gate


class ApplicantProfileSnapshot(_Frozen):
    """The persisted original input (FD §4). ``profile`` is intake's exact
    ``ApplicantProfile``; its CANON-SER is the persisted ``profile_canonical`` column."""
    application_id: str
    profile: ApplicantProfile             # persisted verbatim (intake's contract governs)
    content_hash: str                     # CANON-SER hash of the profile — tamper-evidence


class AuditRecord(_Frozen):
    """The persisted superset — one row per committed decision, keyed by ``decision_id``."""
    decision_id: str                                  # system-generated PK (OOS-7 seam)
    application_id: str                               # the case (intake system-assigned)
    recommendation_id: str                            # the committed pending recommendation
    audit_tuple: AuditTuple
    applicant_profile_snapshot: ApplicantProfileSnapshot
    committed_decision: CommittedDecision
    status: DecisionStatus = DecisionStatus.ACTIVE    # write-once active (Phase 1/2)
    supersedes_decision_id: Optional[str] = None      # nullable self-FK — always null in Phase 1/2


class CommitContext(_Frozen):
    """The pending-recommendation context the orchestrator/pipeline supplies to
    ``DecisionCommitService`` via the injected ``CommitContextProvider`` (plan §1.5) —
    the assembly inputs the frozen 4-param ``commit`` signature does not carry."""
    rule_results: RuleResultReport
    memo_hash: str
    model_version: str
    engine_version: str
    rulebook_version: str
    applicant_profile: ApplicantProfile
