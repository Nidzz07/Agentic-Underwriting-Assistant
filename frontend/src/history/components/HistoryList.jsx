import { COMMIT_ACTION_LABELS } from '../../shell/copy/index.js';
import { HISTORY_COPY } from '../copy.js';
import { historyRowTestid, slugSegment } from '../testids.js';

// C3 — the R6 rows. Presentational; renders each DecisionSummary in the BACKEND-DELIVERED order
// (re-sorts nothing) with a stable `history-row-<decision_id>` testid (US-UI-6: "history rows carry
// data-testid"). Activating a row emits `onSelect(decision_id)` — the R7 key — which is handled
// INTERNALLY by HistoryView (master-detail is in-unit; contrast ui-queue's upward hand-off). No router.
//
// The row carries the HUMAN `action` (via COMMIT_ACTION_LABELS — looked up BY VALUE, never inlined)
// plus the `timestamp`. There is deliberately NO system recommendation in a row: R6 does not carry it,
// and enriching each row via R7 would be the N+1 read PERF-1 forbids (Q4-A). Per-row ids are
// interpolated (the frozen QueueRow convention) so N rows never collide on one testid.
export function HistoryList({ items, onSelect, testid = 'history-list' }) {
  return (
    <ul data-testid={testid} aria-label={HISTORY_COPY.title}>
      {items.map((summary) => {
        const slug = slugSegment(summary.decision_id);
        return (
          <li key={summary.decision_id} data-testid={historyRowTestid(summary.decision_id)}>
            <button
              type="button"
              data-testid={`history-row-select-${slug}`}
              onClick={() => onSelect(summary.decision_id)}
            >
              <span data-testid={`history-row-action-${slug}`}>{COMMIT_ACTION_LABELS[summary.action]}</span>
              <span data-testid={`history-row-timestamp-${slug}`}>{summary.timestamp}</span>
            </button>
          </li>
        );
      })}
    </ul>
  );
}

export default HistoryList;
