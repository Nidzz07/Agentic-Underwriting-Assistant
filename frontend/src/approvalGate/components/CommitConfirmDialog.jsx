import { APPROVAL_COPY } from '../copy.js';

// C6 — the explicit confirm step (Q2-A / human-in-the-loop). BY-CONSTRUCTION (ND-Fold-2):
//   this component is the SOLE holder of the commit trigger. Its props are
//   { onConfirm, onCancel } — `onConfirm` IS the wired submitApprove invocation (supplied only here by
//   ApprovalGateView), and its Confirm handler is THE SINGLE CALL SITE of the commit. `onCancel`
//   returns to ready(idle). Rendering / canceling this dialog is a PURE client-side toggle with NO
//   fetch, NO commit, and NO state mutation beyond the parent's dialog flag (BR-AG-3 / AG-Fold-1) —
//   the commit fires ONLY on Confirm. This component holds no seam reference of its own.
export function CommitConfirmDialog({ onConfirm, onCancel, testid = 'approval-confirm-dialog' }) {
  return (
    <div data-testid={testid} role="dialog" aria-label={APPROVAL_COPY.confirmTitle}>
      <h3 data-testid="approval-confirm-title">{APPROVAL_COPY.confirmTitle}</h3>
      <p data-testid="approval-confirm-body">{APPROVAL_COPY.confirmBody}</p>
      <button type="button" data-testid="approval-confirm-submit" onClick={onConfirm}>
        {APPROVAL_COPY.confirmSubmitLabel}
      </button>
      <button type="button" data-testid="approval-confirm-cancel" onClick={onCancel}>
        {APPROVAL_COPY.confirmCancelLabel}
      </button>
    </div>
  );
}

export default CommitConfirmDialog;
