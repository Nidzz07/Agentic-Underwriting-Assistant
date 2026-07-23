import { HISTORY_COPY } from '../copy.js';

// C4 — derived-state pagination over the R6 `page:{page,size,total}` wrapper, mirroring — never
// importing — ui-queue's local PaginationControls (ui-shell stays frozen; this is a history-local
// component, not a promoted shared primitive). Derived state ONLY: prev disabled on page 1; next
// disabled on the last page; the indicator shows page / derived-total. Computes no totals of its own.
// A page change emits `onPageChange(next)` -> exactly ONE bounded single-page R6 fetch (PERF-1).
export function HistoryPagination({ page, size, total, onPageChange, testid = 'history-pagination' }) {
  const totalPages = Math.max(1, Math.ceil(total / size));
  const isFirstPage = page <= 1;
  const isLastPage = page * size >= total;
  return (
    <nav data-testid={testid} aria-label={HISTORY_COPY.paginationLabel}>
      <button
        type="button"
        data-testid="history-pagination-prev"
        disabled={isFirstPage}
        onClick={() => onPageChange(page - 1)}
      >
        {HISTORY_COPY.prevLabel}
      </button>
      <span data-testid="history-page-indicator">{`${page} / ${totalPages}`}</span>
      <button
        type="button"
        data-testid="history-pagination-next"
        disabled={isLastPage}
        onClick={() => onPageChange(page + 1)}
      >
        {HISTORY_COPY.nextLabel}
      </button>
    </nav>
  );
}

export default HistoryPagination;
