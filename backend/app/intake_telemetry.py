"""The intake telemetry SINK — Q8(c)'s evidence channel, supplied by the composition root.

⛔ **WHY THIS MODULE EXISTS, stated plainly.** ``IntakePipeline`` has always *emitted*
``neutralization_count`` on the ``SANITIZE`` event, and the composition root has always let it
fall back to ``TelemetryEmitter()``'s default sink — ``lambda event: None``. Every count the
sanitizer produced was therefore computed and **discarded**. That was survivable while no
applicant could supply free text: with structured-only intake there was nothing to inject.

⚑ **WIRE1-Fold-7 is what changes that.** Uploaded PDFs make PROJECT-BRIEF §10 failure mode #4 —
*prompt injection in an uploaded document* — reachable for the first time in this build, and
``neutralization_count`` is the only signal that would make an attempt **visible**. The pass that
creates the risk must not be the pass that leaves the evidence channel unwired.

⛔ **WHAT THIS IS NOT.** It is **not** the durable verbatim-span sink. Q8's answer chose **(c)**:
emit the *counts* now, **defer** the forensic span store, and keep the deferral tracked rather
than assumed away. The verbatim ``original_span`` stays where SR-FORENSIC put it — on
``SanitizationReportChannel``, the audit-only channel — and **cannot** reach here even by
accident: :class:`TelemetryEvent` is an allowlist schema of enums, ints and bools with **no
free-text field**, so span text is *structurally unrepresentable* in telemetry. This module
cannot leak what it has no field to carry.

⚑ **EMIT-ONLY, stack-agnostic** (NFR-INT-OBS). ``logging`` is the seam, not the destination: the
``observability`` unit binds Langfuse/Prometheus behind it without this module changing. That is
the whole reason ``TelemetryEmitter`` takes a ``sink`` rather than owning one.

⚠️ **ONE OPERATIONAL NOTE, carried not hidden.** ``TelemetryEmitter`` also appends every event to
its own ``.emitted`` list. That is unbounded, so the emitter must stay **per-request** — which it
is, ``get_intake_pipeline`` being an uncached ``Depends`` provider. ⛔ Caching that provider would
turn this into a slow memory leak. The hazard is **pre-existing** (the discarded default appended
identically) and is recorded here because this module is where a reader will look for it.
"""
from __future__ import annotations

import logging

from backend.intake.telemetry import TelemetryEmitter, TelemetryEvent

#: The named logger the intake telemetry stream lands on. ⚑ Greppable and asserted by name, so an
#: operator wiring a handler — and the test that proves the channel is live — agree on one string.
TELEMETRY_LOGGER = "underwriting.intake.telemetry"

_logger = logging.getLogger(TELEMETRY_LOGGER)


def _emit_to_log(event: TelemetryEvent) -> None:
    """Render ONE allowlisted event. ⛔ The whole event is dumped **because it is safe to dump**.

    Every field of :class:`TelemetryEvent` is an enum, an int or a bool. There is no ``str``
    leaf, so no applicant value, document text or neutralized span can appear in this line —
    the guarantee is the schema's, not this function's discretion, and that is the stronger
    arrangement. ``mode="json"`` renders the enums as their values rather than ``repr``.
    """
    payload = event.model_dump(mode="json")
    _logger.info("intake.%s %s", event.event.value, payload, extra={"intake_telemetry": payload})


def build_intake_telemetry() -> TelemetryEmitter:
    """The REAL emitter — a sink that goes somewhere, in place of one that discards.

    ⚑ A fresh instance per call, deliberately: see the module docstring's note on ``.emitted``.
    """
    return TelemetryEmitter(sink=_emit_to_log)
