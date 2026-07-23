import { QUEUE_COPY } from '../copy.js';

// C6 — DerivedStatePaginationPattern (P8 / PAGINATION-1). Derived state ONLY, from the R2
// `page:{page,size,total}` wrapper: prev disabled on page 1; next disabled on the last page
// (page*size >= total); the indicator shows page / derived-total. Computes no totals of its own.
export function PaginationControls({ page, size, total, onPageChange, testid = 'queue-pagination' }) {
  const totalPages = Math.max(1, Math.ceil(total / size));
  const isFirstPage = page <= 1;
  const isLastPage = page * size >= total;
  return (
    <nav data-testid={testid} aria-label="Queue pagination">
      <button
        type="button"
        data-testid="queue-pagination-prev"
        disabled={isFirstPage}
        onClick={() => onPageChange(page - 1)}
      >
        {QUEUE_COPY.prevLabel}
      </button>
      <span data-testid="queue-page-indicator">{`${page} / ${totalPages}`}</span>
      <button
        type="button"
        data-testid="queue-pagination-next"
        disabled={isLastPage}
        onClick={() => onPageChange(page + 1)}
      >
        {QUEUE_COPY.nextLabel}
      </button>
    </nav>
  );
}

export default PaginationControls;
