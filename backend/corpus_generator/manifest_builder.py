"""C7 ``CorpusManifestBuilder`` / ``FreezeAdapter`` — freeze + manifest (FREEZE-1 + HASH-1).

``content_hash`` delegates to the **single shared CANON-SER**
(``common.canon_ser.content_hash`` — no local hasher, no local serialization,
BR-CORP-11) over the canonicalized ``CorpusRecord`` list. Each record is projected
to the composite ``{profile: profile.model_dump(mode="python"), label,
edge_case_tags, documents_text}`` — reusing intake's blessed profile→canon
projection convention (``model_dump(mode="python")`` — ND-Fold-2), keeping the
projection single-sourced with ``intake``.

Two field-sets differ **by design** (Q4 / §6.5), both excluding manifest provenance:
  * ``content_hash`` **INCLUDES** ``documents_text`` — freeze/tamper-evidence over
    all committed content;
  * DET-1's byte-identity comparison **EXCLUDES** ``documents_text`` — frozen LLM
    prose is not part of *seeded-generation* determinism.
Both EXCLUDE the manifest provenance (``generation_timestamp`` …) per CANON-SER P4.

On-disk serialization (Q1-A) is human-readable (``indent=2``, UTF-8, Decimal-as-string,
sorted keys) and **decoupled** from ``content_hash`` (which is over ``canon_ser``
bytes, not the pretty-printed file bytes) — file readability never affects the hash.
"""
from __future__ import annotations

import json
from typing import Any, Sequence

from backend.common.canon_ser import content_hash as canon_content_hash
from backend.corpus_generator.config import GenerationConfig
from backend.corpus_generator.records import CorpusManifest, CorpusRecord
from backend.corpus_generator.skew_audit import class_proportions, edge_checklist


def record_projection(record: CorpusRecord) -> dict[str, Any]:
    """The canonicalizable composite for one record (content field-set — INCLUDES prose)."""
    return {
        "profile": record.profile.model_dump(mode="python"),   # intake projection convention (ND-Fold-2)
        "label": record.label,                                 # Enum -> canonical value in canon_ser
        "edge_case_tags": record.edge_case_tags,
        "documents_text": record.documents_text,               # JSON-native str, same canon pass
    }


def determinism_projection(records: Sequence[CorpusRecord]) -> list[dict[str, Any]]:
    """The DET-1 comparison field-set — EXCLUDES ``documents_text`` (non-seeded prose)."""
    return [
        {
            "profile": r.profile.model_dump(mode="python"),
            "label": r.label,
            "edge_case_tags": r.edge_case_tags,
        }
        for r in records
    ]


def compute_content_hash(records: Sequence[CorpusRecord]) -> str:
    """Freeze hash via the SINGLE shared CANON-SER over the composite record list."""
    return canon_content_hash([record_projection(r) for r in records])


def build_manifest(
    records: Sequence[CorpusRecord],
    config: GenerationConfig,
    *,
    generation_timestamp: str,
    model_version: str,
    corpus_version: str = "1.0.0",
    provider: str = "gemini",
) -> CorpusManifest:
    """Build the frozen manifest (single ``rulebook_version``; provenance-excluded hash)."""
    counts: dict[str, int] = {cls: 0 for cls in config.target_split}
    for record in records:
        counts[record.label.value] = counts.get(record.label.value, 0) + 1

    proportions = {cls: format(prop, "f") for cls, prop in class_proportions(counts).items()}
    present_edges = {tag for record in records for tag in record.edge_case_tags}

    return CorpusManifest(
        seed=config.seed,
        corpus_version=corpus_version,
        rulebook_version=config.rulebook_version,
        engine_version=config.engine_version,
        provider=provider,
        model_version=model_version,
        class_counts=counts,
        class_proportions=proportions,
        tolerance_pp=config.tolerance_pp,
        edge_case_checklist=edge_checklist(present_edges, config),
        profile_count=len(records),
        content_hash=compute_content_hash(records),
        generation_timestamp=generation_timestamp,
    )


# --------------------------------------------------------------------------
# Human-readable on-disk serialization (Q1-A) — decoupled from content_hash
# --------------------------------------------------------------------------
def corpus_to_json(records: Sequence[CorpusRecord]) -> str:
    """``corpus/profiles.json`` — a single JSON array of ``CorpusRecord`` objects."""
    payload = [r.model_dump(mode="json") for r in records]
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)


def manifest_to_json(manifest: CorpusManifest) -> str:
    """``corpus/manifest.json`` — the one ``CorpusManifest`` object."""
    return json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True, ensure_ascii=False)
