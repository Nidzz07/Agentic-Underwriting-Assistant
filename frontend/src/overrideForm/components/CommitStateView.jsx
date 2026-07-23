import { OVERRIDE_COPY } from '../copy.js';

// C3 — the non-interactive states: loading / pending / errorRead / errorCommit.
//  - loading:     `override-state-loading` container, a single neutral placeholder; no affordance.
//  - pending:     `override-state-pending` — no recommendation yet, so nothing to override (OVR-Fold-5).
//  - errorRead:   PerStatusEnvelopeToRenderPattern — `message` VISIBLE, `code` in a hidden testid node,
//                 `detail` NEVER rendered. Retry (onRetry) re-issues the R4 read (RECOVERY-1 a).
//  - errorCommit: same envelope discipline; the recovery control (onBack) returns to ready(idle) —
//                 NEVER an automatic resubmit (RECOVERY-1 b). The 409 `commit_conflict` code is the
//                 SINGLE rendered conflict state for BOTH already-committed AND the blank-reason
//                 race/bypass tail (no special-casing beyond copy — ERROR-1 / FD-OVR-Fold-1); 403
//                 maps to not-permitted; else the envelope message.
// Presentational only; no seam.
function commitMessage(env) {
  if (env.code === 'forbidden') return OVERRIDE_COPY.notPermittedMessage;
  if (env.code === 'commit_conflict') return OVERRIDE_COPY.conflictMessage;
  return env.message;
}

export function CommitStateView({ state, error = null, onRetry = null, onBack = null }) {
  if (state === 'loading') {
    return (
      <div data-testid="override-state-loading" aria-busy="true" aria-label={OVERRIDE_COPY.loadingLabel}>
        {OVERRIDE_COPY.loadingLabel}
      </div>
    );
  }

  if (state === 'pending') {
    return <div data-testid="override-state-pending">{OVERRIDE_COPY.pendingMessage}</div>;
  }

  // errorRead | errorCommit — always a well-formed envelope thanks to normalizeError; the fallback is
  // purely defensive.
  const env = error && error.error
    ? error.error
    : { code: 'unknown_error', message: OVERRIDE_COPY.unknownErrorMessage };
  const message = state === 'errorCommit' ? commitMessage(env) : env.message;
  return (
    <div data-testid="override-state-error">
      <p data-testid="override-error-message">{message}</p>
      {/* code exposed via testid for assertion/console only — never visible UI text (ERROR-1). */}
      <span data-testid="override-error-code" hidden>{env.code}</span>
      {state === 'errorRead' && onRetry ? (
        <button type="button" data-testid="override-error-retry" onClick={onRetry}>
          {OVERRIDE_COPY.retryLabel}
        </button>
      ) : null}
      {state === 'errorCommit' && onBack ? (
        <button type="button" data-testid="override-error-back" onClick={onBack}>
          {OVERRIDE_COPY.backLabel}
        </button>
      ) : null}
    </div>
  );
}

export default CommitStateView;
