import { SystemRecommendationRegion } from './SystemRecommendationRegion.jsx';
import { CommittedActionRegion } from './CommittedActionRegion.jsx';
import { ForensicTupleRegion } from './ForensicTupleRegion.jsx';
import { RuleResultsRegion } from './RuleResultsRegion.jsx';
import { ProfileSnapshotRegion } from './ProfileSnapshotRegion.jsx';
import { HISTORY_COPY } from '../copy.js';

// =============================================================================================
// C6 — DecisionDetail: the STRICTLY READ-ONLY composer of the R7 AuditRecord. Header comment per the
// frozen NFR-Design.
//
//   * READ-ONLY: there is NO edit affordance and NO mutation seam anywhere in this subtree — no
//     input, no submit, no commit/override control (INV-FAITHFUL / BR-HIST-3). This view only READS
//     records the human already committed via U7/U8. It never implies the record could be altered.
//   * The five regions are composed as SIBLINGS at the same tree level (P2 / SEPARATION-1) — in
//     particular SystemRecommendationRegion and CommittedActionRegion are distinct sibling nodes,
//     NEITHER an ancestor of the other.
//   * Each region receives ONLY its own slice of the AuditRecord: the SYSTEM region gets only
//     `rule_results.recommendation`/`.confidence`; the HUMAN region gets only the `committed_decision`
//     fields. The namespaces cannot cross here because neither region has a prop that would carry the
//     other's data.
//
// BR-HIST-5 (faithfulness) / CG-HIST-Fold-3: the record linkage is rendered at the detail root under
// token-avoiding, convention-compliant ids — the FD's region prop shapes carry no `decisionId`/
// `recommendationId`, and a hyphen-delimited "decision" segment would fail the reused
// advisory-vocabulary lint (CG-HIST-Fold-2). `application_id` is rendered by the snapshot region.
//
// BR-HIST-11: `status` is passed through display-only; `supersedes_decision_id` is never read.
// =============================================================================================
export function DecisionDetail({ record, testid = 'history-detail' }) {
  const tuple = record.audit_tuple;
  const report = tuple.rule_results;
  const snapshot = record.applicant_profile_snapshot;
  const committed = record.committed_decision;

  return (
    <div data-testid={testid}>
      <p>
        <span>{HISTORY_COPY.recordIdHeading}</span>
        <span data-testid="history-detail-record-id">{record.decision_id}</span>
      </p>
      <p>
        <span>{HISTORY_COPY.recommendationIdHeading}</span>
        <span data-testid="history-detail-recommendation-id">{record.recommendation_id}</span>
      </p>

      <SystemRecommendationRegion recommendation={report.recommendation} confidence={report.confidence} />
      <CommittedActionRegion
        action={committed.action}
        reason={committed.reason}
        underwriterId={committed.underwriter_id}
      />
      <ForensicTupleRegion auditTuple={tuple} contentHash={snapshot.content_hash} status={record.status} />
      <RuleResultsRegion ruleResults={report} />
      <ProfileSnapshotRegion
        profile={snapshot.profile}
        applicationId={snapshot.application_id}
        contentHash={snapshot.content_hash}
      />
    </div>
  );
}

export default DecisionDetail;
