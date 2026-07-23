import { ReadOnlyRegion } from '../../shell/components/ReadOnlyRegion.jsx';
import { RecommendationBadge } from '../../shell/components/RecommendationBadge.jsx';
import { ConfidenceBadge } from '../../shell/components/ConfidenceBadge.jsx';
import { MEMO_COPY } from '../copy.js';

// C8 — the RO (read-only recommendation) region. StructuralIsolationCompositionPattern (P2) +
// ReadOnlyRegion composition:
//  - Composes the FROZEN ui-shell ReadOnlyRegion (aria-readonly, FIRST USE) around the system
//    RecommendationBadge + ConfidenceBadge, framed via memo-local chrome as attributable to the
//    DETERMINISTIC ENGINE (never the LLM) — a direct visual expression of CON-BR2-TYPE.
//  - This is the SOLE render site for recommendation/confidence (SEPARATION-1 / N3). It is a SIBLING
//    of NarrativeRegion, never a descendant.
//  - COPY-1: labels are looked up BY VALUE via the reused ui-shell badges (never inlined).
//  - NAMESPACE-1: renders only the SYSTEM Recommendation, never a human CommitAction.
export function ReadOnlyRecommendationRegion({ recommendation, confidence }) {
  return (
    <ReadOnlyRegion testid="memo-region-readonly">
      <h3>{MEMO_COPY.recommendationHeading}</h3>
      <RecommendationBadge value={recommendation} testid="memo-recommendation" />
      <ConfidenceBadge value={confidence} testid="memo-confidence" />
    </ReadOnlyRegion>
  );
}

export default ReadOnlyRecommendationRegion;
