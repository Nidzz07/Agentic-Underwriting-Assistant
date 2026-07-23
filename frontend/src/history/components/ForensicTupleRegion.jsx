import { HISTORY_COPY } from '../copy.js';

// C9 — the read-only forensic / replay fields of the AuditRecord: the CON-AUDIT-1 6-tuple
// (`rulebook_version`, `model_version`, `engine_version`, `memo_hash`, tuple `timestamp`) plus the
// snapshot `content_hash` and the record `status`. Presentational; frames the record as IMMUTABLE
// audit metadata — plain display, no copy/edit affordance (FAITHFUL-1).
//
// NOSUPERSEDE-1 / BR-HIST-11: `status` is DISPLAY-ONLY. There is deliberately no branch keyed on the
// value, no dereference of `supersedes_decision_id` (always null in Phase 1/2), and no version
// affordance — that is the OOS-7 / Phase-3 seam, named-not-designed. Designing for a state that
// cannot occur would be premature abstraction.
export function ForensicTupleRegion({ auditTuple, contentHash, status, testid = 'history-detail-forensic-region' }) {
  return (
    <section data-testid={testid} aria-label={HISTORY_COPY.forensicHeading}>
      <h3>{HISTORY_COPY.forensicHeading}</h3>
      <p>
        <span>{HISTORY_COPY.rulebookVersionHeading}</span>
        <span data-testid="history-detail-rulebook-version">{auditTuple.rulebook_version}</span>
      </p>
      <p>
        <span>{HISTORY_COPY.modelVersionHeading}</span>
        <span data-testid="history-detail-model-version">{auditTuple.model_version}</span>
      </p>
      <p>
        <span>{HISTORY_COPY.engineVersionHeading}</span>
        <span data-testid="history-detail-engine-version">{auditTuple.engine_version}</span>
      </p>
      <p>
        <span>{HISTORY_COPY.memoHashHeading}</span>
        <span data-testid="history-detail-memo-hash">{auditTuple.memo_hash}</span>
      </p>
      <p>
        <span>{HISTORY_COPY.contentHashHeading}</span>
        <span data-testid="history-detail-content-hash">{contentHash}</span>
      </p>
      <p>
        <span>{HISTORY_COPY.timestampHeading}</span>
        <span data-testid="history-detail-timestamp">{auditTuple.timestamp}</span>
      </p>
      <p>
        <span>{HISTORY_COPY.statusHeading}</span>
        <span data-testid="history-detail-status">{status}</span>
      </p>
    </section>
  );
}

export default ForensicTupleRegion;
