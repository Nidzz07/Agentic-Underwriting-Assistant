import { ReadOnlyRegion } from '../../shell/components/ReadOnlyRegion.jsx';
import { RecommendationBadge } from '../../shell/components/RecommendationBadge.jsx';
import { ConfidenceBadge } from '../../shell/components/ConfidenceBadge.jsx';
import { HISTORY_COPY } from '../copy.js';

// =============================================================================================
// C7 — SystemRecommendationRegion. StructuralIsolationCompositionPattern (P2 / SEPARATION-1 — the
// load-bearing namespace pattern). The self-evidence header comment is an EXPLICIT Code-Gen
// deliverable (the frozen ReadOnlyRegion / ReadOnlyRecommendationRegion precedent).
//
// BY CONSTRUCTION — props are `{ recommendation, confidence, testid }` ONLY.
//   * This region is the SOLE holder / SOLE render site of the SYSTEM advisory Recommendation and
//     Confidence (sourced from R7's `audit_tuple.rule_results`).
//   * It has NO `action` / `reason` / `underwriterId` prop and NO PATH by which the HUMAN namespace
//     could reach it. Rendering the human committed action here would require FIRST adding a new prop
//     to the wrong component — an obvious, reviewable change (BR-HIST-2 / WIRE-1 §1 / CON-BR4).
//   * It is a SIBLING of CommittedActionRegion, never an ancestor or descendant of it (composed as
//     siblings by C6 DecisionDetail).
//
// COPY-1: labels are looked up BY VALUE via the reused frozen ui-shell badges — never inlined; a
// `DECLINE-RECOMMEND` value renders the sourced "Decline-Recommend" label, never a bare DECLINE.
// A11Y-1: the frozen ReadOnlyRegion supplies `aria-readonly`; the heading frames the values as
// ENGINE-ATTRIBUTED advisory output, never a final verdict.
// =============================================================================================
export function SystemRecommendationRegion({ recommendation, confidence, testid = 'history-detail-system-region' }) {
  return (
    <ReadOnlyRegion testid={testid}>
      <h3>{HISTORY_COPY.systemRecommendationHeading}</h3>
      <RecommendationBadge value={recommendation} testid="history-detail-recommendation" />
      <ConfidenceBadge value={confidence} testid="history-detail-confidence" />
    </ReadOnlyRegion>
  );
}

export default SystemRecommendationRegion;
