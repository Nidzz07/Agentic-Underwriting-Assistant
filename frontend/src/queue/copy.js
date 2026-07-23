// ui-queue local UI strings (realization detail) — queue-specific chrome text kept OUT of the
// components. These are NOT domain-enum display labels (those live in shell/copy and are looked up
// by value via the reused ui-shell badges). Contains no forbidden system-output vocabulary and no
// value equal to a shell label (COPY-1 / NAMESPACE-1 hold).
export const QUEUE_COPY = Object.freeze({
  emptyMessage: 'No applications in the queue',
  pendingLabel: 'Pending - not yet drafted',
  retryLabel: 'Retry',
  prevLabel: 'Previous',
  nextLabel: 'Next',
  selectLabel: 'View',
  loadingLabel: 'Loading applications',
  unknownErrorMessage: 'Something went wrong.',
  columns: Object.freeze({
    application: 'Application',
    recommendation: 'Recommendation',
    confidence: 'Confidence',
    action: 'Action',
  }),
});

export default QUEUE_COPY;
