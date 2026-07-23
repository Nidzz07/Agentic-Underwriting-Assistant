"""llm-judge (U22) — the LLM-as-judge groundedness rubric over drafted memo prose.

Intentionally EMPTY of re-exports (Q5-A): ``llm_judge`` is the TERMINAL unit of the
23-unit decomposition — it wraps the built system and NOTHING in the build imports it,
so a public export surface would be speculative API. Tests import concrete modules
directly, as every sibling unit does.
"""
