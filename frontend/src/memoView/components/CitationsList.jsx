import { MEMO_COPY } from '../copy.js';

// C6 — the L citations sub-list. OrderPreservingListPattern (P8 / LISTORDER-1): renders cited_rule_ids
// in the DELIVERED order (no client sort). Empty -> neutral copy (no inlined label).
export function CitationsList({ citedRuleIds = [] }) {
  if (citedRuleIds.length === 0) {
    return <p data-testid="memo-region-citations">{MEMO_COPY.noCitationsLabel}</p>;
  }
  return (
    <ul data-testid="memo-region-citations">
      {citedRuleIds.map((id) => (
        <li key={id} data-testid={`memo-citation-${id}`}>{id}</li>
      ))}
    </ul>
  );
}

export default CitationsList;
