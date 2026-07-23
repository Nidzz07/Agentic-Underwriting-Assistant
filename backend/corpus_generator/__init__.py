"""corpus-generator (U14) — build-time seeded, versioned, skew-audited synthetic corpus.

Public surface (call-only consumers read the *frozen* ``corpus/`` artifact, never
this package). See ``guide-docs/build/corpus-generator/`` for the frozen FD / NFR /
Code-Gen artifacts. Reference-not-own: the five call-only surfaces (``intake`` /
``rules_engine`` / ``memo_agent_core`` / ``secrets_config`` / ``common.canon_ser``)
are consumed and NONE re-implemented or edited.
"""
from __future__ import annotations

from backend.corpus_generator.config import (
    DATA2_EDGE_CASES,
    DEFAULT_TARGET_SPLIT,
    GenerationConfig,
)
from backend.corpus_generator.exceptions import (
    BudgetExhaustedError,
    CorpusGenerationError,
    SkewAuditError,
)
from backend.corpus_generator.generator import CorpusGenerator, CorpusOutput
from backend.corpus_generator.records import CorpusManifest, CorpusRecord

__all__ = [
    "GenerationConfig",
    "DEFAULT_TARGET_SPLIT",
    "DATA2_EDGE_CASES",
    "CorpusRecord",
    "CorpusManifest",
    "CorpusGenerator",
    "CorpusOutput",
    "CorpusGenerationError",
    "BudgetExhaustedError",
    "SkewAuditError",
]
