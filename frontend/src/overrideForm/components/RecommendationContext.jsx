import { ReadOnlyRegion } from '../../shell/components/ReadOnlyRegion.jsx';
import { RecommendationBadge } from '../../shell/components/RecommendationBadge.jsx';
import { ConfidenceBadge } from '../../shell/components/ConfidenceBadge.jsx';
import { OVERRIDE_COPY } from '../copy.js';

// C4 — read-only display of the recommendation being OVERRIDDEN. Composes the frozen ui-shell
// ReadOnlyRegion (aria-readonly) + RecommendationBadge/ConfidenceBadge (label look-up BY VALUE, so no
// inlined display label — COPY-1). Engine-attributed heading frames it as the deterministic engine's
// advisory output (NAMESPACE-1: the SYSTEM Recommendation, distinct from the human CommitAction
// `override`). Presentational only; no seam, no commit capability.
export function RecommendationContext({ recommendation, confidence, testid = 'override-recommendation-context' }) {
  return (
    <ReadOnlyRegion testid={testid}>
      <span data-testid="override-context-heading">{OVERRIDE_COPY.contextHeading}</span>
      <RecommendationBadge value={recommendation} testid="override-recommendation-value" />
      <ConfidenceBadge value={confidence} testid="override-confidence-value" />
    </ReadOnlyRegion>
  );
}

export default RecommendationContext;
