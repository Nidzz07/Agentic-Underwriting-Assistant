"""`outlier-model` (U18, C3, Phase 2) — the deterministic statistical outlier scorer.

Advisory-only (skill #1/#3): emits an ``OutlierResult`` (a holistic score + explained
per-feature flags + a reproducibility provenance triple) as **input to the memo** —
never a ``Recommendation``, never a committed decision, no LLM, no write path, no
persistence (BR-OUT-9). Demographic-excluded by construction (BR-OUT-1), seeded and
version-anchored for reproducibility (BR-OUT-4), zero unexplained flags by schema
(BR-OUT-7). Consumes frozen shapes by shape; imports no consumer; edits no frozen unit.
"""
