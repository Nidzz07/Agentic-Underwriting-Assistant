"""MissingInfoDeriver — deterministic missing_information (MISSINGINFO-1).

Derived from three signals in the handed **clean** inputs — **not LLM-authored**:
  (i)   ``DocumentManifest`` entries with status ``missing`` / ``unparseable``
  (ii)  ``RuleResult``s with status == ``not_evaluated``
  (iii) ``profile.incomplete == True``

Emitted in a **fixed TOTAL cross-source order** so the list is byte-stable
regardless of which sources fire or their internal iteration order — this
matters because the list feeds the hashed memo content (HASH-1) and
``canon_ser`` PRESERVES list order (the DET-2 class). The total order is:

  primary key   = the source-enum declared order (``MissingInfoSource``)
  secondary key = the within-source detail (doc_type / rule_id / fixed constant)
"""
from __future__ import annotations

from backend.intake.schema import DocStatus
from backend.rules_engine.report_schema import RuleStatus
from backend.memo_agent_core.schemas import (
    MemoAgentInput,
    MissingInfoSource,
    MissingInformationItem,
)

#: Fixed detail for the single-valued profile-incomplete signal.
_INCOMPLETE_DETAIL = "profile_incomplete"

#: Primary sort key: the declared order of the source enum (missing_document <
#: unparseable_document < not_evaluated_rule < incomplete_flag).
_SOURCE_ORDER = {source: index for index, source in enumerate(MissingInfoSource)}


class MissingInfoDeriver:
    """Pure derivation of ``missing_information`` (no provider, reproducible)."""

    def derive(self, agent_input: MemoAgentInput) -> list[MissingInformationItem]:
        items: list[MissingInformationItem] = []

        # (i) documents missing / unparseable
        for entry in agent_input.applicant_profile.documents.entries:
            if entry.status is DocStatus.MISSING:
                items.append(
                    MissingInformationItem(
                        source=MissingInfoSource.MISSING_DOCUMENT, detail=entry.doc_type.value
                    )
                )
            elif entry.status is DocStatus.UNPARSEABLE:
                items.append(
                    MissingInformationItem(
                        source=MissingInfoSource.UNPARSEABLE_DOCUMENT, detail=entry.doc_type.value
                    )
                )

        # (ii) rules not evaluated (operand absent)
        for result in agent_input.rule_report.rule_results:
            if result.status is RuleStatus.NOT_EVALUATED:
                items.append(
                    MissingInformationItem(
                        source=MissingInfoSource.NOT_EVALUATED_RULE, detail=result.rule_id
                    )
                )

        # (iii) profile incomplete flag
        if agent_input.applicant_profile.incomplete:
            items.append(
                MissingInformationItem(
                    source=MissingInfoSource.INCOMPLETE_FLAG, detail=_INCOMPLETE_DETAIL
                )
            )

        # FIXED TOTAL order: source-major (declared enum order), then detail.
        items.sort(key=lambda item: (_SOURCE_ORDER[item.source], item.detail))
        return items
