import { OVERRIDE_COPY } from '../copy.js';

// C7 — the explicit confirm step (human-in-the-loop). BY-CONSTRUCTION (P1 / P8 / header-comment
// self-evidence):
//   sole commit-trigger holder — `onConfirm` is the single call site; echoes the reason read-only;
//   open/cancel is a pure client-side toggle.
// Its props are { onConfirm, onCancel, reason, testid } — `onConfirm` IS the wired submitOverride
// invocation (supplied only here by OverrideFormView, closing over the current reason), and its
// Confirm handler is THE SINGLE CALL SITE of the commit. `onCancel` returns to ready(idle) with the
// reason preserved. `reason` is rendered as a READ-ONLY echo (override-confirm-reason-echo, sourced
// from the client reason state) for final review — it is NOT an editable input. Rendering / canceling
// this dialog is a PURE client-side toggle with NO fetch, NO commit, and NO state mutation beyond the
// parent's dialog flag (BR-OVR-3) — the commit fires ONLY on Confirm. This component holds no seam
// reference of its own.
export function OverrideConfirmDialog({ onConfirm, onCancel, reason, testid = 'override-confirm-dialog' }) {
  return (
    <div data-testid={testid} role="dialog" aria-label={OVERRIDE_COPY.confirmTitle}>
      <h3 data-testid="override-confirm-title">{OVERRIDE_COPY.confirmTitle}</h3>
      <p data-testid="override-confirm-body">{OVERRIDE_COPY.confirmBody}</p>
      <p data-testid="override-confirm-reason-echo">
        {OVERRIDE_COPY.confirmReasonHeading} {reason}
      </p>
      <button type="button" data-testid="override-confirm-submit" onClick={onConfirm}>
        {OVERRIDE_COPY.confirmSubmitLabel}
      </button>
      <button type="button" data-testid="override-confirm-cancel" onClick={onCancel}>
        {OVERRIDE_COPY.confirmCancelLabel}
      </button>
    </div>
  );
}

export default OverrideConfirmDialog;
