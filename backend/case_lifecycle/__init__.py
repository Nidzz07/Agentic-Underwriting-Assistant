"""case-lifecycle (U24, Scope B) — the pending (pre-commit) half of the underwriting case.

Intentionally EMPTY of re-exports: the composition root imports concrete modules directly
(the sibling convention), and the only cross-package import a future wiring pass needs is the
single pure function ``states.case_to_memo_view_state``.
"""
