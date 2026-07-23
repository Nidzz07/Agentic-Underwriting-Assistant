"""``quality-gates`` (U13) — the single verification authority for the four blocking gates.

Verification only (reference-not-own): bias-swap delta=0 (CON-BR1), reproducibility
×10 (CON-BR2/AC-1), rule coverage 100% (QA-3), and the code-coverage wiring gate
(AC-5). No LLM; no real PII; no enforcement/definition of any invariant (that lives
in ``rules-engine``/``outlier-model``). See ``guide-docs/build/quality-gates/``.
"""
