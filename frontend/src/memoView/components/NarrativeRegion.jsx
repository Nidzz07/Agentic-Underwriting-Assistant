import { CitationsList } from './CitationsList.jsx';
import { MEMO_COPY } from '../copy.js';

// C5 — the L (LLM-authored narrative) region.
//
// STRUCTURAL ISOLATION BY CONSTRUCTION (SEPARATION-1 / CON-BR2-TYPE, NFR-DESIGN-Fold-1 — a HARD
// requirement, not optional):
//   Props are { narrative, citedRuleIds, testid } — ALL L-region content. This component has
//   NO `recommendation` / `confidence` prop and NO path to render either. The system
//   recommendation/confidence are rendered EXCLUSIVELY by ReadOnlyRecommendationRegion (the RO
//   region), a SIBLING of this node — never a descendant. A developer cannot render the
//   recommendation inside the narrative without first ADDING A NEW PROP here (an obvious, reviewable
//   change). The SEPARATION-1 DOM-containment test is a regression guard ON TOP of this guarantee.
//
//   The runtime `narrative_prose` is rendered AS-IS and is never linted or rewritten (BR-MEMO-2
//   governance — advisory conformance of the prose is memo-agent-core's backend concern, CON-BR2).
export function NarrativeRegion({ narrative, citedRuleIds = [] }) {
  return (
    <section data-testid="memo-region-narrative">
      <h3>{MEMO_COPY.narrativeHeading}</h3>
      <p data-testid="memo-narrative-prose">{narrative}</p>
      <CitationsList citedRuleIds={citedRuleIds} />
    </section>
  );
}

export default NarrativeRegion;
