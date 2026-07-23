"""allowlist (C-OBS-3, P-OBS-4/5/3) — the shared, plane-neutral demographic-free projection.

``project_allowlisted`` is the SINGLE SOURCE of the demographic-free / allowlist guarantee
(DEMOFREE-1): a pure function that drops any field whose name is not in the caller's
``allowed`` set OR whose value is not an allowlist scalar (id / enum value / int count /
timing). It is **plane-agnostic** — it knows NOTHING of spans or metrics — so it is
structurally incapable of being a ``trace <-> metric`` coupling point (SEP-1 / Req-Fold-3):
both planes import it, and that is the ONE legitimate shared import.

Header note (documentation only, NEVER enforcement): pure, no side effect, no plane
knowledge; a demographic / free-text / ``original_span`` field is unrepresentable downstream
because it is dropped here.
"""
from __future__ import annotations

from typing import Mapping

# The only value shapes a span attribute or a metric label may carry: id / enum value /
# int count / timing. No prose, PII, free-text, or object field can survive.
ScalarValue = str | int | float | bool


def _is_scalar(value: object) -> bool:
    """True iff ``value`` is an allowlist scalar. ``bool`` is a subclass of ``int`` — both
    are intentionally allowed; every other type (objects, lists, mappings, None) is dropped."""
    return isinstance(value, (str, int, float, bool))


def project_allowlisted(
    fields: Mapping[str, object], allowed: frozenset[str]
) -> dict[str, ScalarValue]:
    """Keep only ``allowed`` field names whose value is an allowlist scalar; drop the rest.

    Knows nothing of spans or metrics — the single-sourced demographic-free guarantee.
    """
    return {k: v for k, v in fields.items() if k in allowed and _is_scalar(v)}
