// outlierView/copy.js — the outlier-local chrome + enum labels (BR-OUTV-5; the ui-memo-view
// copy.js precedent). LINT-SUBJECT: the frozen `advisory-vocabulary` + `no-inline-label` rules
// are registered on src/outlierView/** — reusing the ONE shell/copy FORBIDDEN_TERMS source.
// There is NO local word-list here (P-OUTV-9 / ADVISORY-1).
//
// Every value below honors the reserved-word constraint SEMANTICALLY — no literal "decision"
// token, no bare "decline", no "approved"/"declined" — so the advisory-vocabulary lint applies
// UNMODIFIED with no carve-out (the frozen ui-approval-gate NFR-AG-Fold-2 / ui-history
// NFR-HIST-Fold-D precedent). copy.test.js runs EVERY value through the REAL detector
// (findForbiddenSystemOutput, imported from eslint-rules/index.js) rather than assuming.

// FLAG_DIRECTION_LABELS (Q7-A) — the FlagDirection wire enum (`high`/`low`), keyed BY VALUE (never
// remapped/re-cased — WIRE-1 §1). Each label states a STATISTICAL POSITION relative to the corpus
// distribution — deliberately NOT a severity or verdict word: a `high` flag means the value sits
// above the typical range, NOT that the applicant is "high risk" (OUTV-FD-Fold-3 / COPY-1).
//
// Collision note (CG-OUTV-Fold-4): these values must never equal a shell/copy display label — a
// bare "High"/"Low" would collide EXACTLY with CONFIDENCE_LABELS and both trip `no-inline-label`
// and false-fail the NOVERDICT-1 rendered-absence teeth. The phrases below cannot collide.
export const FLAG_DIRECTION_LABELS = Object.freeze({
  high: 'Above the typical range',
  low: 'Below the typical range',
});

export const OUTLIER_COPY = Object.freeze({
  // Panel chrome — frames the whole panel as an advisory statistical signal (BR-OUTV-2).
  panelHeading: 'Statistical outlier analysis',
  advisoryNote: 'Advisory statistical signal for underwriter review.',

  // Score region (P-OUTV-2: presentational only — a statistical anomaly score, not a verdict).
  scoreHeading: 'Anomaly score',
  outlierScoreLabel: 'Anomaly score',
  isOutlierLabel: 'Flagged as an outlier',
  isOutlierYes: 'Yes',
  isOutlierNo: 'No',

  // Flagged-features region.
  flagsHeading: 'Flagged features',
  // Empty `flagged_features` on a PRESENT outlier — analyzed, nothing anomalous (EMPTY-1).
  // Deliberately distinct wording from notAvailableMessage below.
  noFlagsLabel: 'No anomalous features were flagged for this applicant.',
  zScoreLabel: 'z-score',
  shapValueLabel: 'SHAP contribution',

  // The field-derived NOT_AVAILABLE state (Q4-B / STATE-1) — covers BOTH null-causes (a `pending`
  // body and a Phase-1 `ready` body carrying `outlier: null`). "not analyzed" — NOT "analyzed,
  // nothing found" (that is noFlagsLabel above).
  notAvailableMessage: 'Outlier analysis is not available for this application.',

  loadingLabel: 'Loading outlier analysis…',
  retryLabel: 'Retry',
  unknownErrorMessage: 'Unable to load the outlier analysis.',
});

export default OUTLIER_COPY;
