// C9 (approvalGate/copy.js) — approval-local UI strings (realization detail) kept OUT of the
// components. These are NOT domain-enum display labels (those are looked up by value via the reused
// ui-shell badges + COMMIT_ACTION_LABELS). LINT-SUBJECT: reused ESLint no-inline-label +
// advisory-vocabulary lints run over this file.
//
// NFR-AG-Fold-2 (Q4-A) — advisory-clean by construction: the system output is called a
// "recommendation", never a "decision"; the human's committed action is framed via
// "approve" / "approval" / "record" / "committed" WITHOUT the literal forbidden token "decision"
// (nor "approved" / "declined" / bare "DECLINE"). The reserved-word constraint is honored
// SEMANTICALLY, so the shared advisory-vocabulary lint applies UNMODIFIED (no carve-out, no second
// word-list).
export const APPROVAL_COPY = Object.freeze({
  loadingLabel: 'Loading recommendation',
  pendingMessage: 'No recommendation has been drafted yet for this application.',
  contextHeading: 'Recommendation from the rules engine',
  approveLabel: 'Approve recommendation',
  confirmTitle: 'Confirm approval',
  confirmBody: 'You are about to approve this recommendation. Your approval will be recorded.',
  confirmSubmitLabel: 'Confirm approval',
  confirmCancelLabel: 'Cancel',
  submittingLabel: 'Submitting approval',
  committedTitle: 'Approval recorded',
  committedByLabel: 'Committed by',
  conflictMessage: 'This recommendation has already been committed.',
  notPermittedMessage: 'You are not permitted to approve recommendations.',
  retryLabel: 'Retry',
  backLabel: 'Back to review',
  unknownErrorMessage: 'Something went wrong.',
});

export default APPROVAL_COPY;
