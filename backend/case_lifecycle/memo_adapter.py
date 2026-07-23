"""C-CASE-9 — U24's OWN thin CANON-SER adapter for the memo. **Rehydration only.**

⚑ **Added by U24's THIRD AUTHORIZED REOPENING (Scope B wiring pass, Q14-A)**, logged in
``audit.md``/``guide-state.md`` **before** this module was written.

**Header comment — DOCUMENTATION ONLY, never enforcement** (each property is scan-enforced in
C-CASE-8): holds no LLM; edits no frozen unit; declares no verdict; **never re-implements the
commit gate, the authz check, or a write to ``audit_record``**; no network at tier-U.

**Why this module exists.** WIRE-1 §5 binds R4's ``status: "ready"`` to mean the ``memo`` field is
**PRESENT**, so R4 must turn ``PendingRecommendation.memo_canonical`` back into a
``DecisionMemo``. The frozen ``audit_store.CanonSerAdapter`` exposes exactly four methods —
``canonical_bytes`` · ``content_hash`` · ``profile_from_canonical`` · ``report_from_canonical`` —
**hardcoded to ``ApplicantProfile`` and ``RuleResultReport``**. A full ``backend/``-wide check
found **no memo rehydration anywhere in the build**. Nothing existed to reuse.

**Why HERE and not elsewhere** (the three rejected alternatives, recorded so the choice stays
legible):
  * **NOT** by adding a method to ``audit_store``'s ``CanonSerAdapter`` — that is a **frozen-unit
    edit**, forbidden outright.
  * **NOT** as an ad hoc ``canon_deserialize`` call inside ``backend/app/`` — that would put
    **U24-shaped domain knowledge** (how a ``DecisionMemo`` is rehydrated) in the composition
    root, breaking its *"contains no domain logic"* invariant, and **no scan would catch it** —
    which is precisely why it is the wrong home even though it would work.
  * **NOT** by emitting ``memo: null`` on a ``ready`` view — a direct **WIRE-1 §5 violation**.

⚑ **This follows the MEASURED convention, it does not invent one.** Every unit in this build
reaches the shared ``backend.common.canon_ser`` through **its own thin adapter** —
``intake/canon_ser_adapter.py``, ``rules_engine/canon_adapter.py``,
``audit_store/canon_adapter.py``, ``memo_agent_core/memo_hash_adapter.py``. **No production
module anywhere calls the shared module ad hoc.** This is U24's counterpart, and it is
deliberately as thin as its siblings: **deserialize, validate, return. Nothing else.**

⚑ **ADAPTER-1 is NARROWED, NOT WEAKENED, to admit this module.** ``canon_ser`` (the SERIALIZE
direction) stays forbidden in **every** U24 production module without exception — U24 still
canonicalizes **only** through the frozen adapter. ``canon_deserialize`` is permitted **here and
nowhere else**, enforced by a one-module allowlist plus a **positive thinness assertion** and a
detector self-test (``tests/test_adapter.py``). *Before*: no module may call it. *After*: exactly
one designated module may, for rehydration only. **Strictly more specific, not more permissive.**
"""
from __future__ import annotations

from backend.common.canon_ser import canon_deserialize
from backend.memo_agent_core.schemas import DecisionMemo


class MemoCanonAdapter:
    """The rehydration half for the memo. ⚑ **No serialize direction — deliberately.**

    U24 canonicalizes the memo **on the way in** through the FROZEN
    ``CanonSerAdapter.canonical_bytes`` (``pipeline.py``). This adapter supplies **only** the way
    back out. Adding a ``canonical_bytes``-alike here would fork the serialize discipline the
    frozen adapter owns — exactly what ADAPTER-1 exists to prevent.
    """

    @staticmethod
    def memo_from_canonical(data: bytes) -> DecisionMemo:
        """CANON-SER bytes -> the frozen ``DecisionMemo``.

        Mirrors ``CanonSerAdapter.profile_from_canonical``/``report_from_canonical`` **verbatim**
        in shape (``model_validate(canon_deserialize(data))``), so the two directions round-trip
        byte-identically and **no conversion sits on the replay path**.
        """
        return DecisionMemo.model_validate(canon_deserialize(data))
