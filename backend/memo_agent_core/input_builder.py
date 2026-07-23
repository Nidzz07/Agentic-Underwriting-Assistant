"""MemoAgentInputBuilder — assemble MemoAgentInput from clean artifacts (GROUND-1 / SEC1-1).

Takes ONLY the clean, read-only artifacts — the intake ``ApplicantProfile`` and
the rules-engine ``RuleResultReport`` — and produces the ``MemoAgentInput`` the
agent is handed. The ``recommendation``/``confidence`` are the injected read-only
values (defaulting to the report's, which the deterministic core produced).

There is **no parameter and no field** for ``original_span`` / ``SanitizationReport``:
the forensic span structurally cannot enter the memo path (SEC1-1).
"""
from __future__ import annotations

from typing import Optional

from backend.intake.schema import ApplicantProfile
from backend.rules_engine.report_schema import Confidence, Recommendation, RuleResultReport
from backend.memo_agent_core.schemas import MemoAgentInput


class MemoAgentInputBuilder:
    def build(
        self,
        *,
        applicant_profile: ApplicantProfile,
        rule_report: RuleResultReport,
        recommendation: Optional[Recommendation] = None,
        confidence: Optional[Confidence] = None,
    ) -> MemoAgentInput:
        return MemoAgentInput(
            applicant_profile=applicant_profile,
            rule_report=rule_report,
            recommendation=recommendation if recommendation is not None else rule_report.recommendation,
            confidence=confidence if confidence is not None else rule_report.confidence,
        )
