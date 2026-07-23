import { QUEUE_COPY } from '../copy.js';

// C3 — the non-ready render states. state in {loading, empty, error}.
//  - loading: `queue-state-loading` container + a fixed count of skeleton rows (Q1-A; the COUNT is a
//    cosmetic constant, NOT asserted — only container presence + "no real rows").
//  - empty:   a distinct "no applications" message.
//  - error:   ErrorEnvelopeToRenderPattern (P3 / ERROR-1) — `message` VISIBLE, `code` in a
//    testid-only (hidden) node, `detail` NEVER rendered. Uniform for every non-2xx incl. 401 (Q4-A).
const SKELETON_ROWS = 3; // Q1-A — cosmetic constant

export function QueueStateView({ state, error = null, onRetry = null }) {
  if (state === 'loading') {
    return (
      <div data-testid="queue-state-loading" aria-busy="true" aria-label={QUEUE_COPY.loadingLabel}>
        {Array.from({ length: SKELETON_ROWS }).map((_, i) => (
          <div key={i} data-testid="queue-skeleton-row" className="queue-skeleton-row" />
        ))}
      </div>
    );
  }

  if (state === 'empty') {
    return <div data-testid="queue-state-empty">{QUEUE_COPY.emptyMessage}</div>;
  }

  // error — always a well-formed envelope thanks to fetchSeam normalization (CG-Fold-1); the
  // fallback below is purely defensive.
  const envelope = error && error.error
    ? error.error
    : { code: 'unknown_error', message: QUEUE_COPY.unknownErrorMessage };
  return (
    <div data-testid="queue-state-error">
      <p data-testid="queue-error-message">{envelope.message}</p>
      {/* code is exposed via testid for assertion/console only — never visible UI text (ERROR-1). */}
      <span data-testid="queue-error-code" hidden>{envelope.code}</span>
      {onRetry ? (
        <button type="button" data-testid="queue-error-retry" onClick={onRetry}>
          {QUEUE_COPY.retryLabel}
        </button>
      ) : null}
    </div>
  );
}

export default QueueStateView;
