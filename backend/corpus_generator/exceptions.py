"""Named typed-exception taxonomy (NFR-Design §10, Q1-A).

One unit base exception with two catchable subclasses; tests assert the specific
subclass. Both are build-blocking and loud by construction — never a silent
degrade, never a hang.

    CorpusGenerationError            (base — the unit's build-time failure)
    ├── BudgetExhaustedError         (P3 — pre-flight infeasibility OR runtime budget exhaustion)
    └── SkewAuditError               (P4 — band failure OR edge-checklist failure)
"""
from __future__ import annotations


class CorpusGenerationError(Exception):
    """Base class for every build-time corpus-generation failure."""


class BudgetExhaustedError(CorpusGenerationError):
    """Bounded rejection-sampling could not meet the quotas within ``attempt_budget``.

    Raised by BOTH P3 guards: the seed-independent pre-flight feasibility guard
    (band lower-edge count ``> attempt_budget`` — pigeonhole) and the runtime
    exhaustion guard.
    """


class SkewAuditError(CorpusGenerationError):
    """The blocking skew-audit gate failed — ``band_ok`` OR ``edges_ok`` is false."""
