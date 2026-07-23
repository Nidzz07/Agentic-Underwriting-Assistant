import { MEMO_COPY, MISSING_INFO_SOURCE_LABELS } from '../copy.js';

// C7 — the D (deterministic missing-information) region. OrderPreservingListPattern (P8 / LISTORDER-1):
// renders missing_information in the DELIVERED (backend deterministic MISSINGINFO-1) order — NO client
// re-sort. Each row: `detail` primary + the source label from the memo-local MISSING_INFO_SOURCE_LABELS
// (Q4-A / COPY-1, never inlined). Empty -> neutral copy.
export function MissingInfoRegion({ items = [] }) {
  if (items.length === 0) {
    return <p data-testid="memo-region-missinginfo">{MEMO_COPY.noMissingInfoLabel}</p>;
  }
  return (
    <ul data-testid="memo-region-missinginfo">
      {items.map((item, index) => (
        <li key={index} data-testid={`memo-missinginfo-${index}`}>
          <span>{item.detail}</span>
          <span>{MISSING_INFO_SOURCE_LABELS[item.source] ?? item.source}</span>
        </li>
      ))}
    </ul>
  );
}

export default MissingInfoRegion;
