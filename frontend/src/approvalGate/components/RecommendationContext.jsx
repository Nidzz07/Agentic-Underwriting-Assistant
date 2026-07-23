import { ReadOnlyRegion } from '../../shell/components/ReadOnlyRegion.jsx';
import { RecommendationBadge } from '../../shell/components/RecommendationBadge.jsx';
import { ConfidenceBadge } from '../../shell/components/ConfidenceBadge.jsx';
import { APPROVAL_COPY } from '../copy.js';

// C4 — read-only display of the recommendation being approved. Composes the frozen ui-shell
// ReadOnlyRegion (aria-readonly) + RecommendationBadge/ConfidenceBadge (label look-up BY VALUE, so no
// inlined display label — COPY-1). Engine-attributed heading frames it as the deterministic engine's
// advisory output (NAMESPACE-1: the SYSTEM Recommendation, distinct from the human CommitAction).
// Presentational only; no seam, no commit capability.
export function RecommendationContext({ recommendation, confidence, testid = 'approval-recommendation-context' }) {
  return (
    <ReadOnlyRegion testid={testid}>
      <span data-testid="approval-context-heading">{APPROVAL_COPY.contextHeading}</span>
      <RecommendationBadge value={recommendation} testid="approval-recommendation" />
      <ConfidenceBadge value={confidence} testid="approval-confidence" />
    </ReadOnlyRegion>
  );
}

export default RecommendationContext;
