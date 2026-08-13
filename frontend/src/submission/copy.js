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

// ⛔ THE OPTIONAL FIELDS — added by WIRE1-Fold-7 (Q10).
//
// ⚑ SUPERSEDED, and the Fold-6 text is kept because its reasoning was sound at the time:
// *"OPTIONAL intake fields are deliberately NOT offered. Under Q2(a) no document can be
// supplied, so `ApplicantProfile.incomplete` is TRUE for every Fold-6 submission regardless —
// collecting optional values would not change that."*
//
// **Documents have landed, so the premise is gone.** With three parsed documents the
// documents clause clears, and these fields clear the other six — so an application can now
// reach `incomplete = false` for the first time in this project's history.
//
// ⛔ THEY MUST NEVER JOIN `REQUIRED_FIELDS`. The submit affordance keys on that tuple alone; an
// optional field added there would become mandatory by UI accident. Pinned by a test.
export const OPTIONAL_FIELDS = Object.freeze([
  'height_cm',
  'weight_kg',
  'existing_debt_obligations_annual',
  'occupation',
  'employment_type',
  'smoking_status',
  'health_flags',
]);

//: Values the frozen `intake.schema.EmploymentType` / `SmokingStatus` enums accept, by value.
export const EMPLOYMENT_OPTIONS = Object.freeze([
  'salaried', 'self_employed', 'contract', 'unemployed', 'unknown',
]);
export const SMOKING_OPTIONS = Object.freeze(['smoker', 'non_smoker', 'unknown']);

//: The three `intake.schema.DocType` values, by value — the part names R10 accepts (WIRE-1 §1).
export const DOC_TYPES = Object.freeze([
  'salary_slip', 'bank_statement', 'medical_questionnaire',
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

  // --- documents (WIRE1-Fold-7) ---
  documentsHeading: 'Supporting documents',
  documentsHint: 'PDF only. Each document is checked when you submit.',
  documentLabels: Object.freeze({
    salary_slip: 'Salary slip',
    bank_statement: 'Bank statement',
    medical_questionnaire: 'Medical questionnaire',
  }),
  // ⛔ Q7: per-document status must be VISIBLE, never a silent downgrade. A document that fails
  // to read changes the assessment, and the applicant is entitled to know which one and why.
  documentStatusLabels: Object.freeze({
    selected: 'Ready to upload',
    uploading: 'Checking…',
    parsed: 'Read successfully',
    unparseable: 'Could not be read — the application was still accepted',
  }),
  removeDocumentLabel: 'Remove',
  tooLargeMessage: 'That file is too large. Choose a smaller PDF.',

  // --- the optional section (Q10) ---
  optionalHeading: 'Additional details (optional)',
  optionalHint: 'These are not required, but a complete application can be assessed more fully.',
  optionalFieldLabels: Object.freeze({
    height_cm: 'Height (cm)',
    weight_kg: 'Weight (kg)',
    existing_debt_obligations_annual: 'Existing annual debt obligations',
    occupation: 'Occupation',
    employment_type: 'Employment type',
    smoking_status: 'Smoking status',
    health_flags: 'Health notes',
  }),
  employmentLabels: Object.freeze({
    salaried: 'Salaried', self_employed: 'Self-employed', contract: 'Contract',
    unemployed: 'Not currently employed', unknown: 'Prefer not to say',
  }),
  smokingLabels: Object.freeze({
    smoker: 'Smoker', non_smoker: 'Non-smoker', unknown: 'Prefer not to say',
  }),

  // ⚠️ Q11(a) — THE DISCLOSED LIMITATION, STATED TO THE USER, not buried in a code comment.
  // `intake`'s completeness test treats an EMPTY health-notes list as incomplete, so an
  // applicant who reports nothing cannot be marked complete however many documents they attach.
  // This pass does not reopen frozen `intake` to change that; it says so plainly instead.
  completenessDisclosure:
    'Attaching every document does not by itself mark an application complete. '
    + 'Leaving health notes empty will also keep it marked incomplete, even when nothing is '
    + 'wrong — write "none reported" if that is the case.',

  // Q3(a): the upload latency is DISCLOSED rather than engineered away.
  uploadLatencyHint: 'Checking documents can take a few seconds.',

  unknownErrorMessage: 'Something went wrong.',
});

export default SUBMISSION_COPY;
