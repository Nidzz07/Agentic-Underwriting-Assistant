import { RecommendationBadge } from '../../shell/components/RecommendationBadge.jsx';
import { COMMIT_ACTION_LABELS } from '../../shell/copy/index.js';
import { OVERRIDE_COPY } from '../copy.js';

// C8 — the committed-override confirmation (success state). BY-CONSTRUCTION (P6 / NOREFETCH-1 /
// header-comment self-evidence):
//   props { decision, context } only — no seam; renders the committed echo, cannot re-fetch.
// It holds NO seam reference, so a re-fetch is STRUCTURALLY IMPOSSIBLE (the transport-bearing seam is
// held only by OverrideFormView; this component never imports createOverrideFetch). It renders from
// the echo, never re-fetches.
//
// `decision` = CommittedDecision { recommendation_id, underwriter_id, action:'override', reason }.
// `context`  = the R4 MemoView (used only for the read-only recommendation value).
// SOURCE-OF-TRUTH (ND-OVR-Fold-ii): the committed `reason` is sourced EXCLUSIVELY from `decision.reason`
// (the R5 echo) — NOT the orchestrator's client `reason` slice (never passed here). The human action
// label comes from COMMIT_ACTION_LABELS (the human CommitAction namespace), never a
// RECOMMENDATION_LABELS value — the human `override` must never render as the system DECLINE-RECOMMEND
// (NAMESPACE-1 / BR-OVR-7).
export function CommittedConfirmation({ decision, context, testid = 'override-committed-view' }) {
  return (
    <div data-testid={testid}>
      <h3 data-testid="override-committed-title">{OVERRIDE_COPY.committedTitle}</h3>
      <RecommendationBadge value={context.report.recommendation} testid="override-committed-recommendation" />
      <p data-testid="override-committed-action">{COMMIT_ACTION_LABELS[decision.action]}</p>
      <p data-testid="override-committed-by">
        {OVERRIDE_COPY.committedByLabel} {decision.underwriter_id}
      </p>
      <p data-testid="override-committed-reason">
        {OVERRIDE_COPY.committedReasonHeading} {decision.reason}
      </p>
    </div>
  );
}

export default CommittedConfirmation;
