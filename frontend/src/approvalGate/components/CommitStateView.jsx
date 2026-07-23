import { APPROVAL_COPY } from '../copy.js';

// C3 — the non-interactive states: loading / pending / errorRead / errorCommit.
//  - loading:     `approval-state-loading` container, a single neutral placeholder; no affordance.
//  - pending:     `approval-state-pending` — no recommendation yet, so nothing to approve (AG-Fold-5).
//  - errorRead:   ErrorEnvelopeToRenderPattern — `message` VISIBLE, `code` in a hidden testid node,
//                 `detail` NEVER rendered. Retry (onRetry) re-issues the R4 read (RECOVERY-1 a).
//  - errorCommit: same envelope discipline; the recovery control (onBack) returns to ready(idle) —
//                 NEVER an automatic resubmit (RECOVERY-1 b). Per-status friendly copy for the two
//                 documented commit codes (forbidden / commit_conflict), else the envelope message.
// Presentational only; no seam.
function commitMessage(env) {
  if (env.code === 'forbidden') return APPROVAL_COPY.notPermittedMessage;
  if (env.code === 'commit_conflict') return APPROVAL_COPY.conflictMessage;
  return env.message;
}

export function CommitStateView({ state, error = null, onRetry = null, onBack = null }) {
  if (state === 'loading') {
    return (
      <div data-testid="approval-state-loading" aria-busy="true" aria-label={APPROVAL_COPY.loadingLabel}>
        {APPROVAL_COPY.loadingLabel}
      </div>
    );
  }

  if (state === 'pending') {
    return <div data-testid="approval-state-pending">{APPROVAL_COPY.pendingMessage}</div>;
  }

  // errorRead | errorCommit — always a well-formed envelope thanks to normalizeError; the fallback is
  // purely defensive.
  const env = error && error.error
    ? error.error
    : { code: 'unknown_error', message: APPROVAL_COPY.unknownErrorMessage };
  const message = state === 'errorCommit' ? commitMessage(env) : env.message;
  return (
    <div data-testid="approval-state-error">
      <p data-testid="approval-error-message">{message}</p>
      {/* code exposed via testid for assertion/console only — never visible UI text (ERROR-1). */}
      <span data-testid="approval-error-code" hidden>{env.code}</span>
      {state === 'errorRead' && onRetry ? (
        <button type="button" data-testid="approval-error-retry" onClick={onRetry}>
          {APPROVAL_COPY.retryLabel}
        </button>
      ) : null}
      {state === 'errorCommit' && onBack ? (
        <button type="button" data-testid="approval-error-back" onClick={onBack}>
          {APPROVAL_COPY.backLabel}
        </button>
      ) : null}
    </div>
  );
}

export default CommitStateView;
