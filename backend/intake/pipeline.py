"""IntakePipeline — the frozen ``parse -> sanitize -> gate`` wiring (FD §1).

Composes the unit's components into the C1 pipeline:

  1. parse each uploaded document in an isolated subprocess (SubprocessParseWorker),
     building the DocumentManifest (parsed / missing / unparseable);
  2. sanitize the free-text / narrative fields (SanitizerEngine), routing the
     SanitizationReport to the audit channel ONLY (SEC-1-FORENSIC surface 1);
  3. validate the assembled draft at the SEC-2 gate (IntakeGate), producing
     exactly one of ``ApplicantProfile`` (valid, possibly ``incomplete``) or
     ``RejectedIntake``.

Telemetry is emitted for each stage through the forensic-free TelemetryEmitter
(counts / enums only). Intake never emits a recommendation (CON-BR2). The
FastAPI HTTP entrypoint that calls this pipeline is the orchestrator's concern
(Build & Test), not this unit.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Protocol

from backend.intake.parser import ParseOutcome
from backend.intake.schema import (
    ApplicantProfile,
    DocStatus,
    DocType,
    DocumentEntry,
    RejectedIntake,
    SanitizedText,
)
from backend.intake.sanitizer.report_channel import SanitizationReportChannel
from backend.intake.sanitizer.sanitizer import SanitizerEngine
from backend.intake.telemetry import TelemetryEmitter, TelemetryEvent, TelemetryEventType
from backend.intake.validation_gate import IntakeGate


class _ParseWorker(Protocol):
    def parse(self, doc_type: DocType, source_path: str) -> ParseOutcome:  # pragma: no cover
        ...


@dataclass(frozen=True)
class DocumentInput:
    doc_type: DocType
    source_path: Optional[str] = None  # None => the document was not supplied


@dataclass
class PipelineResult:
    outcome: ApplicantProfile | RejectedIntake
    sanitized_texts: list[SanitizedText] = field(default_factory=list)


class IntakePipeline:
    def __init__(
        self,
        parse_worker: _ParseWorker,
        sanitizer: Optional[SanitizerEngine] = None,
        gate: Optional[IntakeGate] = None,
        telemetry: Optional[TelemetryEmitter] = None,
        report_channel: Optional[SanitizationReportChannel] = None,
    ) -> None:
        self._parse = parse_worker
        self._sanitizer = sanitizer or SanitizerEngine()
        self._gate = gate or IntakeGate()
        self._telemetry = telemetry or TelemetryEmitter()
        self._report_channel = report_channel or SanitizationReportChannel()

    def process(
        self, form_fields: dict[str, Any], documents: list[DocumentInput]
    ) -> PipelineResult:
        # 1 — parse
        entries: list[DocumentEntry] = []
        payloads: dict[str, dict] = {}
        unparseable = 0
        for doc in documents:
            if doc.source_path is None:
                entries.append(DocumentEntry(doc_type=doc.doc_type, status=DocStatus.MISSING))
                continue
            outcome = self._parse.parse(doc.doc_type, doc.source_path)
            entries.append(outcome.entry)
            if outcome.entry.status is DocStatus.PARSED:
                payloads[doc.doc_type.value] = outcome.payload
            else:
                unparseable += 1
        self._telemetry.emit(TelemetryEvent(
            event=TelemetryEventType.PARSE, unparseable_doc_count=unparseable))

        # 2 — sanitize free-text (form narrative + parsed document text)
        free_texts: dict[str, str] = dict(form_fields.get("free_text_fields", {}))
        for ref, payload in payloads.items():
            text = payload.get("extracted_text")
            if text:
                free_texts.setdefault(ref, text)
        sanitized: list[SanitizedText] = []
        neutralizations = 0
        for ref, text in free_texts.items():
            st = self._sanitizer.sanitize(text, source_ref=ref)
            sanitized.append(st)
            if st.was_modified:
                neutralizations += len(st.report)
                self._report_channel.publish(ref, st.report)  # audit channel only
        self._telemetry.emit(TelemetryEvent(
            event=TelemetryEventType.SANITIZE, neutralization_count=neutralizations))

        # 3 — gate
        draft = {k: v for k, v in form_fields.items() if k != "free_text_fields"}
        draft["documents"] = entries
        result = self._gate.validate_gate(draft)
        if isinstance(result, RejectedIntake):
            self._telemetry.emit(TelemetryEvent(
                event=TelemetryEventType.VALIDATE_GATE, reject_reason=result.reason_category))
        else:
            self._telemetry.emit(TelemetryEvent(
                event=TelemetryEventType.VALIDATE_GATE, incomplete=result.incomplete))

        return PipelineResult(outcome=result, sanitized_texts=sanitized)
