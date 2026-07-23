// C10 (overrideForm/copy.js) — override-local UI strings (realization detail) kept OUT of the
// components. These are NOT domain-enum display labels (those are looked up by value via the reused
// ui-shell badges + COMMIT_ACTION_LABELS.override). LINT-SUBJECT: reused ESLint no-inline-label +
// advisory-vocabulary lints run over this file.
//
// NFR-OVR-Fold-3 (Q8-A) — advisory-clean by construction: the system output is called a
// "recommendation", never a "decision"; the human's committed action is framed via
// "override" / "reason" / "record" / "committed" WITHOUT the literal forbidden token "decision"
// (nor "approved" / "declined" / bare "DECLINE"), and the human `override` is NEVER rendered as the
// system `DECLINE-RECOMMEND` (BR-OVR-7). The reserved-word constraint is honored SEMANTICALLY, so the
// shared advisory-vocabulary lint applies UNMODIFIED (no carve-out, no second word-list). All 21
// strings are consumed verbatim from the frozen FD (domain-entities.md §3) — no Code-Gen re-draft.
export const OVERRIDE_COPY = Object.freeze({
  loadingLabel: 'Loading recommendation',
  pendingMessage: 'No recommendation has been drafted yet for this application.',
  contextHeading: 'Recommendation from the rules engine',
  reasonPromptLabel: 'Reason for overriding this recommendation',
  reasonPlaceholder: 'Explain why you are overriding this recommendation',
  reasonRequiredHint: 'A reason is required to override.',
  overrideLabel: 'Override recommendation',
  confirmTitle: 'Confirm override',
  confirmBody: 'You are about to override this recommendation. Your override and reason will be recorded.',
  confirmReasonHeading: 'Your reason',
  confirmSubmitLabel: 'Confirm override',
  confirmCancelLabel: 'Cancel',
  submittingLabel: 'Submitting override',
  committedTitle: 'Override recorded',
  committedByLabel: 'Committed by',
  committedReasonHeading: 'Reason recorded',
  conflictMessage: 'This recommendation has already been committed.',
  notPermittedMessage: 'You are not permitted to override recommendations.',
  retryLabel: 'Retry',
  backLabel: 'Back to review',
  unknownErrorMessage: 'Something went wrong.',
});

export default OVERRIDE_COPY;
