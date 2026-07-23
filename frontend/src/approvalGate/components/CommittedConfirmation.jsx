import { RecommendationBadge } from '../../shell/components/RecommendationBadge.jsx';
import { COMMIT_ACTION_LABELS } from '../../shell/copy/index.js';
import { APPROVAL_COPY } from '../copy.js';

// C7 — the committed-decision confirmation (success state). BY-CONSTRUCTION (Q3-A / ND-Fold-3):
//   props are { decision, context } ONLY — the R5 CommittedDecision echo + the R4 context already in
//   hand. This component holds NO seam reference, so a re-fetch is STRUCTURALLY IMPOSSIBLE (the
//   transport-bearing seam is held only by ApprovalGateView; this component never imports
//   createCommitFetch). It renders from the echo, never re-fetches (NOREFETCH-1).
//
// `decision`  = CommittedDecision { recommendation_id, underwriter_id, action, reason|null }.
// `context`   = the R4 MemoView (used only for the read-only recommendation value).
// The human action label comes from COMMIT_ACTION_LABELS (the human CommitAction namespace), never a
// RECOMMENDATION_LABELS value (NAMESPACE-1).
export function CommittedConfirmation({ decision, context, testid = 'approval-committed' }) {
  return (
    <div data-testid={testid}>
      <h3 data-testid="approval-committed-title">{APPROVAL_COPY.committedTitle}</h3>
      <RecommendationBadge value={context.report.recommendation} testid="approval-committed-recommendation" />
      <p data-testid="approval-committed-action">{COMMIT_ACTION_LABELS[decision.action]}</p>
      <p data-testid="approval-committed-by">
        {APPROVAL_COPY.committedByLabel} {decision.underwriter_id}
      </p>
    </div>
  );
}

export default CommittedConfirmation;
