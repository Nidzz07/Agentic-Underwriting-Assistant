import { HISTORY_COPY } from '../copy.js';

// C5 — the non-content render states of the master-detail machine (P5 / STATEMACHINE-1), mirroring the
// frozen QueueStateView. state in {listLoading, listEmpty, listError, detailLoading, detailError}.
//  - listLoading / detailLoading: the shared `history-state-loading` placeholder (the FD inventory
//    pins ONE loading id for both reads).
//  - listEmpty: the single page-level "no decisions yet" message (P7 / EMPTY-1).
//  - listError / detailError: PerOperationRetryTargetingPattern (P8 / ERROR-1) — `message` VISIBLE,
//    `code` in a testid-only hidden node, `detail` NEVER rendered. The container id distinguishes the
//    failing READ (list vs detail), not the failure CAUSE: every non-2xx is uniform, and R7's 404
//    `not_found` flows through this SAME generic detail path with no dedicated branch (HIST-Fold-3).
//    Retry is wired to `onRetry`, which the orchestrator targets per-operation.
export function HistoryStateView({ state, error = null, onRetry = null }) {
  if (state === 'listLoading' || state === 'detailLoading') {
    return (
      <div data-testid="history-state-loading" aria-busy="true" aria-label={HISTORY_COPY.loadingLabel} />
    );
  }

  if (state === 'listEmpty') {
    return <div data-testid="history-state-empty">{HISTORY_COPY.emptyMessage}</div>;
  }

  // error — always a well-formed envelope thanks to the seam's normalization; the fallback is
  // purely defensive.
  const envelope = error && error.error
    ? error.error
    : { code: 'unknown_error', message: HISTORY_COPY.unknownErrorMessage };
  const containerTestid = state === 'listError' ? 'history-state-error-list' : 'history-state-error-detail';

  return (
    <div data-testid={containerTestid}>
      <p data-testid="history-error-message">{envelope.message}</p>
      {/* code is exposed via testid for assertion/console only — never visible UI text (ERROR-1). */}
      <span data-testid="history-error-code" hidden>{envelope.code}</span>
      {onRetry ? (
        <button type="button" data-testid="history-error-retry" onClick={onRetry}>
          {HISTORY_COPY.retryLabel}
        </button>
      ) : null}
    </div>
  );
}

export default HistoryStateView;
