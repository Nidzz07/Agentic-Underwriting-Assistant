"""Frozen output records — ``CorpusRecord`` + ``CorpusManifest`` (FD ``domain-entities.md §4/§5``).

Pydantic v2 value objects: ``frozen=True`` + ``extra="forbid"``. ``CorpusRecord``
carries a valid frozen ``intake.ApplicantProfile`` + the engine-assigned ``label``
(CON-BR2) + the generation-target ``intended_class`` (provenance only, never
authoritative) + the DATA-2 ``edge_case_tags`` it satisfies + the (frozen) LLM
document ``documents_text``.

``CorpusManifest`` pins the frozen corpus: seed + versions + counts + the edge-case
checklist + the ``content_hash`` (computed via the shared CANON-SER over the
canonicalized record list — see ``manifest_builder`` / BR-CORP-11). Provenance
fields (``generation_timestamp`` …) are recorded but EXCLUDED from that hash (P4).
"""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from backend.intake.schema import ApplicantProfile
from backend.rules_engine.report_schema import Recommendation


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class CorpusRecord(_Frozen):
    """One frozen corpus row."""

    profile: ApplicantProfile
    documents_text: dict[str, str] = Field(default_factory=dict)
    label: Recommendation                      # engine-assigned (CON-BR2); the authority
    intended_class: Recommendation             # generation target only — never authoritative
    edge_case_tags: list[str] = Field(default_factory=list)


class CorpusManifest(_Frozen):
    """The freeze record pinning the frozen corpus (FD §4)."""

    seed: int
    corpus_version: str
    rulebook_version: str                      # the single version the corpus was labeled against (Fold 4)
    engine_version: str
    provider: str                              # "gemini" (FR-PROV-4)
    model_version: str
    class_counts: dict[str, int]
    class_proportions: dict[str, str]          # Decimal-as-string (canonical)
    tolerance_pp: Decimal
    edge_case_checklist: dict[str, bool]       # each required DATA-2 edge -> present (all True)
    profile_count: int
    content_hash: str                          # shared CANON-SER over the record list (provenance-excluded)
    generation_timestamp: str                  # recorded provenance — NEVER an input to generation (DET-1)
