import {
  EMPLOYMENT_OPTIONS,
  OPTIONAL_FIELDS,
  SMOKING_OPTIONS,
  SUBMISSION_COPY,
} from '../copy.js';
import { fieldInputTestid } from '../testids.js';

const SELECTS = {
  employment_type: [EMPLOYMENT_OPTIONS, SUBMISSION_COPY.employmentLabels],
  smoking_status: [SMOKING_OPTIONS, SUBMISSION_COPY.smokingLabels],
};

// PRESENTATIONAL — the seven fields `IntakeGate` reads but does not require (Q10).
//
// ⛔ **NONE OF THESE MAY EVER JOIN `REQUIRED_FIELDS`.** The submit affordance keys on that tuple
// alone; adding one here to it would make an optional field mandatory by UI accident, and the
// user would be blocked by a form asking for something intake never needed. Pinned by a test.
//
// ⚠️ **THE DISCLOSURE IS RENDERED HERE, TO THE USER** (Q11(a)). `intake` treats an EMPTY health
// notes list as incomplete, so an applicant who reports nothing cannot be marked complete no
// matter how many documents they attach. This pass does not reopen frozen `intake` to change
// that — it says so plainly, where the person affected by it will read it.
export function OptionalFields({ values, onChange, disabled }) {
  return (
    <div data-testid="submission-optional">
      <h3>{SUBMISSION_COPY.optionalHeading}</h3>
      <p>{SUBMISSION_COPY.optionalHint}</p>
      <p data-testid="submission-completeness-note">{SUBMISSION_COPY.completenessDisclosure}</p>
      {OPTIONAL_FIELDS.map((field) => {
        const inputId = fieldInputTestid(field);
        const select = SELECTS[field];
        return (
          <div key={field}>
            <label htmlFor={inputId}>{SUBMISSION_COPY.optionalFieldLabels[field]}</label>
            {select ? (
              <select
                id={inputId}
                data-testid={inputId}
                value={values[field]}
                disabled={disabled}
                onChange={(event) => onChange(field, event.target.value)}
              >
                <option value="" />
                {select[0].map((option) => (
                  <option key={option} value={option}>{select[1][option]}</option>
                ))}
              </select>
            ) : (
              <input
                id={inputId}
                data-testid={inputId}
                type="text"
                value={values[field]}
                disabled={disabled}
                onChange={(event) => onChange(field, event.target.value)}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

export default OptionalFields;
