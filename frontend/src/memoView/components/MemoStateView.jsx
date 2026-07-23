import { MEMO_COPY } from '../copy.js';

// C3 — the non-ready render states. state in {loading, pending, error}.
//  - loading: `memo-state-loading` container, a single NEUTRAL placeholder (Q1-A); NO memo region.
//  - pending: `memo-state-pending` — "memo not yet drafted" (derived from status:"pending", P6 /
//    PENDING-1); report/memo are null so there is nothing else to render.
//  - error:   ErrorEnvelopeToRenderPattern (P3 / ERROR-1) — `message` VISIBLE, `code` in a
//    testid-only (hidden) node, `detail` NEVER rendered. Uniform for every non-2xx incl. 401 (Q5-A).
//    Retry re-fetches the SAME applicationId (single resource — no page position to preserve).
export function MemoStateView({ state, error = null, onRetry = null }) {
  if (state === 'loading') {
    return (
      <div data-testid="memo-state-loading" aria-busy="true" aria-label={MEMO_COPY.loadingLabel}>
        {MEMO_COPY.loadingLabel}
      </div>
    );
  }

  if (state === 'pending') {
    return <div data-testid="memo-state-pending">{MEMO_COPY.pendingMessage}</div>;
  }

  // error — always a well-formed envelope thanks to memoFetchSeam normalization (CG-MEMO-Fold-1);
  // the fallback below is purely defensive.
  const envelope = error && error.error
    ? error.error
    : { code: 'unknown_error', message: MEMO_COPY.unknownErrorMessage };
  return (
    <div data-testid="memo-state-error">
      <p data-testid="memo-error-message">{envelope.message}</p>
      {/* code is exposed via testid for assertion/console only — never visible UI text (ERROR-1). */}
      <span data-testid="memo-error-code" hidden>{envelope.code}</span>
      {onRetry ? (
        <button type="button" data-testid="memo-error-retry" onClick={onRetry}>
          {MEMO_COPY.retryLabel}
        </button>
      ) : null}
    </div>
  );
}

export default MemoStateView;
