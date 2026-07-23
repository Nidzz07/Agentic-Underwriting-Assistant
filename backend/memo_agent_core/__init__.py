"""memo-agent-core (C4 / U4) — the decision-memo agent, where the LLM enters.

Downstream of the deterministic core: it drafts advisory memo prose (LLM,
temperature=0), validates citations against the handed report (hallucination
guard), derives missing_information deterministically, and computes the
memo_hash — never altering the recommendation (CON-BR2). The LLM is reached
only through an injected ProviderAbstraction, so every invariant is unit-tested
against a fake provider (no live LLM, no network).
"""
