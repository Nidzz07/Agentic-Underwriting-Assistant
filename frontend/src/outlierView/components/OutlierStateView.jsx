import { OUTLIER_COPY } from '../copy.js';

// C-OUTV-3 (OutlierStateView) — the non-ready render states. state in {loading, not_available, error}.
//
//  - loading:       `outlier-state-loading` — a neutral placeholder.
//  - not_available: `outlier-state-notavailable` (P-OUTV-4 / EMPTY-1 + STATE-1) — the FIELD-DERIVED
//    neutral state, reached ONLY on a resolved (2xx) response carrying `outlier: null`. Covers BOTH
//    null-causes (a `pending` body AND a Phase-1 `ready` body with a null outlier). This is
//    "NOT ANALYZED" — a structurally DIFFERENT branch, container and message from
//    FlaggedFeaturesRegion's "analyzed, no anomalous features" (which lives in the READY tree).
//  - error: ErrorEnvelopeToRenderPattern (P-OUTV-7 / ERROR-1) — `message` VISIBLE, `code` in a
//    hidden testid-only node, `detail` NEVER rendered raw. Retry re-fetches the SAME applicationId.
export function OutlierStateView({ state, error = null, onRetry = null, testid = null }) {
  if (state === 'loading') {
    return (
      <div
        data-testid={testid ?? 'outlier-state-loading'}
        aria-busy="true"
        aria-label={OUTLIER_COPY.loadingLabel}
      >
        {OUTLIER_COPY.loadingLabel}
      </div>
    );
  }

  if (state === 'not_available') {
    return (
      <div data-testid={testid ?? 'outlier-state-notavailable'}>
        {OUTLIER_COPY.notAvailableMessage}
      </div>
    );
  }

  // error — always a well-formed envelope thanks to fetchSeam normalization; the fallback is
  // purely defensive.
  const envelope = error && error.error
    ? error.error
    : { code: 'unknown_error', message: OUTLIER_COPY.unknownErrorMessage };
  return (
    <div data-testid={testid ?? 'outlier-state-error'}>
      <p data-testid="outlier-error-message">{envelope.message}</p>
      {/* code is exposed via testid for assertion/console only — never visible UI text (ERROR-1). */}
      <span data-testid="outlier-error-code" hidden>{envelope.code}</span>
      {onRetry ? (
        <button type="button" data-testid="outlier-error-retry" onClick={onRetry}>
          {OUTLIER_COPY.retryLabel}
        </button>
      ) : null}
    </div>
  );
}

export default OutlierStateView;
