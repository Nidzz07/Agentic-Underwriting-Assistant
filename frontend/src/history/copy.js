// ui-history local UI strings (realization detail) — history-specific chrome + forensic field labels
// kept OUT of the components. These are NOT domain-enum display labels (those live in shell/copy and
// are looked up BY VALUE via the reused ui-shell badges / COMMIT_ACTION_LABELS). No value here equals a
// shell display label (COPY-1) and no value carries a FORBIDDEN_TERMS.systemOutput token (ADVISORY-1).
//
// NFR-HIST-Fold-D (binding, verified against the REAL word-boundary detector): the plural "decisions"
// passes `/\bdecision\b/i` and is used freely; the STANDALONE SINGULAR "decision" is avoided
// everywhere — hence "History" / "No decisions yet" / "Underwriter's committed action" /
// "Committed outcome". The reused advisory-vocabulary lint is the build-failing enforcement; it is
// applied UNMODIFIED (no carve-out, no second word-list).
export const HISTORY_COPY = Object.freeze({
  title: 'History',
  emptyMessage: 'No decisions yet',
  loadingLabel: 'Loading history',
  retryLabel: 'Retry',
  backLabel: 'Back to list',
  prevLabel: 'Previous',
  nextLabel: 'Next',
  paginationLabel: 'History pagination',
  unknownErrorMessage: 'Something went wrong.',

  // SYSTEM namespace (engine-attributed, advisory) — BR-HIST-2.
  systemRecommendationHeading: 'System recommendation',

  // HUMAN namespace (the underwriter's committed action) — BR-HIST-2 / HIST-Fold-4. The CON-BR4
  // concept is conveyed by the distinct region + distinct labels, never by the lexical token.
  committedActionHeading: "Underwriter's committed action",
  committedOutcomeHeading: 'Committed outcome',
  reasonHeading: 'Reason given',
  underwriterHeading: 'Underwriter ID',

  // Forensic / replay tuple labels — plain read-only labels framing an immutable audit record.
  forensicHeading: 'Forensic record',
  rulebookVersionHeading: 'Rulebook version',
  modelVersionHeading: 'Model version',
  engineVersionHeading: 'Engine version',
  memoHashHeading: 'Memo hash',
  contentHashHeading: 'Content hash',
  statusHeading: 'Record status',
  timestampHeading: 'Committed at',
  recordIdHeading: 'Record ID',
  recommendationIdHeading: 'Recommendation ID',

  // Rule-results progressive disclosure (HIST-Fold-2 / P9).
  ruleResultsHeading: 'Rule results',
  expandLabel: 'Show rule results',
  collapseLabel: 'Hide rule results',

  // Read-only applicant snapshot (the persisted verbatim input).
  profileSnapshotHeading: 'Applicant snapshot',
  profile: Object.freeze({
    application: 'Application ID',
    applicant: 'Applicant',
    age: 'Age',
    requestedCover: 'Requested cover',
    income: 'Verifiable income',
    snapshotHash: 'Snapshot hash',
  }),
});

export default HISTORY_COPY;
