import { GENDER_OPTIONS, REQUIRED_FIELDS, SUBMISSION_COPY } from '../copy.js';
import { fieldErrorTestid, fieldInputTestid } from '../testids.js';

// PRESENTATIONAL — no fetch, no state of its own, no Role. Values and the change handler are
// injected; `fieldErrors` is a plain `{ field: message }` map the parent derived from the
// server's `detail.field_errors`.
//
// ⚑ The per-field error is rendered BESIDE ITS OWN INPUT and wired with `aria-describedby`, not
// collected into a list at the top. That is the whole practical difference Q8(a) bought: a user
// is told which box to fix, in the place they would look.
export function SubmissionForm({ values, fieldErrors, onChange, disabled }) {
  return (
    <div data-testid="submission-form">
      {REQUIRED_FIELDS.map((field) => {
        const error = fieldErrors[field];
        const inputId = fieldInputTestid(field);
        const errorId = fieldErrorTestid(field);
        return (
          <div key={field}>
            <label htmlFor={inputId}>{SUBMISSION_COPY.fieldLabels[field]}</label>
            {field === 'gender' ? (
              <select
                id={inputId}
                data-testid={inputId}
                value={values[field]}
                disabled={disabled}
                aria-invalid={error ? 'true' : undefined}
                aria-describedby={error ? errorId : undefined}
                onChange={(event) => onChange(field, event.target.value)}
              >
                <option value="" />
                {GENDER_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {SUBMISSION_COPY.genderLabels[option]}
                  </option>
                ))}
              </select>
            ) : (
              <input
                id={inputId}
                data-testid={inputId}
                type={field.endsWith('_date') || field === 'date_of_birth' ? 'date' : 'text'}
                value={values[field]}
                disabled={disabled}
                aria-invalid={error ? 'true' : undefined}
                aria-describedby={error ? errorId : undefined}
                onChange={(event) => onChange(field, event.target.value)}
              />
            )}
            {error ? (
              <p data-testid={errorId} role="alert">{error}</p>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}

export default SubmissionForm;
