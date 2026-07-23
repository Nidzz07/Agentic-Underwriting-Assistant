// memoView local UI strings (realization detail) — memo-specific chrome kept OUT of the components.
// These are NOT domain-enum display labels (those live in shell/copy and are looked up by value via
// the reused ui-shell badges). LINT-SUBJECT (MEMO-Fold-1): contains no forbidden system-output
// vocabulary (advisory-vocabulary) and no value equal to a shell display label (no-inline-label).
// MISSING_INFO_SOURCE_LABELS keys on the frozen MissingInfoSource wire values (Q4-A).
export const MISSING_INFO_SOURCE_LABELS = Object.freeze({
  missing_document: 'Missing document',
  unparseable_document: 'Unreadable document',
  not_evaluated_rule: 'Rule not evaluated',
  incomplete_flag: 'Incomplete application flag',
});

export const MEMO_COPY = Object.freeze({
  loadingLabel: 'Loading memo',
  pendingMessage: 'The memo has not yet been drafted for this application.',
  retryLabel: 'Retry',
  unknownErrorMessage: 'Something went wrong.',
  narrativeHeading: 'Narrative',
  citationsHeading: 'Cited rules',
  missingInfoHeading: 'Missing information',
  // Frames the RO region as attributable to the deterministic engine (advisory, engine-authored).
  recommendationHeading: 'Recommendation from the rules engine',
  noCitationsLabel: 'No rules cited',
  noMissingInfoLabel: 'No missing information',
  headers: Object.freeze({
    applicant: 'Applicant',
    age: 'Age',
    requestedCover: 'Requested cover',
  }),
});

export default MEMO_COPY;
