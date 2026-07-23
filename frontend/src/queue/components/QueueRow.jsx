import { RecommendationBadge } from '../../shell/components/RecommendationBadge.jsx';
import { ConfidenceBadge } from '../../shell/components/ConfidenceBadge.jsx';
import { QUEUE_COPY } from '../copy.js';

// C5 — one ApplicationSummary row.
//  - NullRowPlaceholderPattern (P2 / PENDING-1): recommendation/confidence null (co-null) -> a
//    neutral "pending" placeholder, NO badge; the row is still shown.
//  - COPY-1: labels are looked up BY VALUE via the reused ui-shell badges (never inlined).
//  - NAMESPACE-1: renders only the SYSTEM Recommendation; never a human CommitAction.
//  - EmissionOnlyEventPattern (P6 / SELECT-1): emits onSelect(application_id) and nothing else — no router.
export function QueueRow({ summary, onSelect }) {
  const { application_id, recommendation, confidence } = summary;
  const pending = recommendation == null || confidence == null;
  return (
    <tr data-testid={`queue-row-${application_id}`}>
      <td>{application_id}</td>
      <td>
        {pending ? (
          <span data-testid={`queue-row-pending-${application_id}`}>{QUEUE_COPY.pendingLabel}</span>
        ) : (
          <RecommendationBadge value={recommendation} testid={`queue-row-recommendation-${application_id}`} />
        )}
      </td>
      <td>
        {pending ? null : (
          <ConfidenceBadge value={confidence} testid={`queue-row-confidence-${application_id}`} />
        )}
      </td>
      <td>
        <button
          type="button"
          data-testid={`queue-row-select-${application_id}`}
          onClick={() => onSelect(application_id)}
        >
          {QUEUE_COPY.selectLabel}
        </button>
      </td>
    </tr>
  );
}

export default QueueRow;
