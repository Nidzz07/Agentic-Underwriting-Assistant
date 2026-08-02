// submission local UI strings (realization detail) — submission-specific chrome kept OUT of the
// components, mirroring HISTORY_COPY / OUTLIER_COPY.
//
// ⚑ ADVISORY-1 (binding): no value here carries a FORBIDDEN_TERMS.systemOutput token. The
// standalone singular "decision", a bare "DECLINE", "approved" and "declined" are all avoided —
// this unit describes an APPLICATION being submitted and a memo being drafted, never an outcome,
// so the constraint costs nothing here. `no-inline-label` is what forces every string through
// this module rather than into JSX.

// ⛔ THE FIELD SET IS THE FROZEN IntakeGate's, NOT THIS UNIT'S CHOICE.
// These are exactly the values `IntakeGate._evaluate` treats as required: absence of any one of
// them produces a `RejectedIntake`. Two consequences, both deliberate:
//   * Adding a field here that intake does not read produces dead UI.
//   * OMITTING one produces a form that can only ever 400 — which looks to the user like the
//     server rejecting their data, when in fact the form never asked for it.
// An exact-set test pins this list so neither can happen quietly.
//
// ⚑ OPTIONAL intake fields (height/weight/debt/employment/smoking/occupation/health flags) are
// deliberately NOT offered. Under Q2(a) no document can be supplied, so `ApplicantProfile.
// incomplete` is TRUE for every Fold-6 submission regardless — collecting optional values would
// not change that, and would add form surface for no change in outcome. A named follow-on.
export const REQUIRED_FIELDS = Object.freeze([
  'full_name',
  'city',
  'gender',
  'date_of_birth',
  'as_of_date',
  'verifiable_income_annual',
  'requested_cover_amount',
]);

//: The gender values the frozen `intake.schema.Gender` enum accepts, by value.
export const GENDER_OPTIONS = Object.freeze(['female', 'male', 'other', 'unspecified']);

export const SUBMISSION_COPY = Object.freeze({
  title: 'New application',
  submitLabel: 'Submit application',
  submittingLabel: 'Submitting the application',
  retryLabel: 'Retry',
  startOverLabel: 'Submit another application',

  // ⛔ The money hint is not decoration. Intake's BR-TYP-1 refuses a JSON float outright
  // ("float not permitted; use a decimal string"), so a user typing 1200000.50 into a number
  // input would be rejected by the server for a reason the form never explained.
  amountHint: 'Whole currency units, entered as digits',

  fieldLabels: Object.freeze({
    full_name: 'Full name',
    city: 'City',
    gender: 'Gender',
    date_of_birth: 'Date of birth',
    as_of_date: 'Assessment date',
    verifiable_income_annual: 'Verifiable annual income',
    requested_cover_amount: 'Requested cover amount',
  }),

  genderLabels: Object.freeze({
    female: 'Female',
    male: 'Male',
    other: 'Other',
    unspecified: 'Prefer not to say',
  }),

  // The 400 rejection path (Q8(a)) — the reason this unit renders structured detail at all.
  rejectionHeading: 'This application could not be accepted',
  rejectionReasonLabels: Object.freeze({
    missing_required: 'Some required information is missing.',
    malformed: 'Some information was not in a form we could read.',
    unparseable: 'A supporting document could not be read.',
  }),
  rejectionFallbackReason: 'The application did not pass validation.',
  missingItemsHeading: 'Still needed',

  // Accepted — the two-phase flow's first half (Q3(a)).
  acceptedHeading: 'Application received',
  acceptedIdLabel: 'Reference',
  // ⚑ The user is told the case is NOT yet assessed. Under Q3(a) submission is LLM-free and
  // stops at `evaluated`, so claiming anything more would misdescribe what happened.
  acceptedPendingMessage: 'The application is queued and has not yet been assessed.',

  // The drafting trigger — the second, explicit phase.
  draftLabel: 'Start assessment',
  draftingLabel: 'Assessment in progress',
  draftedMessage: 'The assessment is ready to review.',
  // ⚑ Re-triggering is idempotent, not a failure (register #27's `DraftOutcome.skipped`).
  skippedMessage: 'This application has already been assessed.',

  unknownErrorMessage: 'Something went wrong.',
});

export default SUBMISSION_COPY;
