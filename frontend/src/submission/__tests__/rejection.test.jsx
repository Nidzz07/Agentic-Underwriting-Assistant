// Step 4.3 — THE 400 REJECTION PATH. ⛔ The plan calls this "the reason Q8(a) was worth choosing",
// so these assert that the structured detail is USED, not merely received.
//
// The bar is deliberately higher than "an error is shown". A generic message would satisfy a
// naive reading of "handles 400" while discarding exactly what Q8(a) bought: `field_errors`,
// `missing_items` and `reason_category` — enough to mark the specific inputs at fault.
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SubmissionView, toFieldErrorMap } from '../SubmissionView.jsx';
import { SUBMISSION_COPY } from '../copy.js';
import { fieldErrorTestid, fieldInputTestid, missingItemTestid } from '../testids.js';
import { fillValid, stubSeam, VALID } from './fixtures.js';

function rejecting(detail) {
  return stubSeam({
    submit: async () => {
      throw {
        error: {
          code: 'invalid_request',
          message: 'The application did not pass intake validation.',
          detail,
        },
      };
    },
  });
}

const MISSING_TWO = {
  reason_category: 'missing_required',
  field_errors: [
    { field: 'date_of_birth', code: 'missing', message: 'required value absent' },
    { field: 'city', code: 'missing', message: 'required value absent' },
  ],
  missing_items: ['date_of_birth', 'city'],
};

async function submitAndReject(detail) {
  render(<SubmissionView submissionSeam={rejecting(detail)} />);
  fillValid();
  fireEvent.click(screen.getByTestId('submission-submit'));
  await screen.findByTestId('submission-rejection');
}

describe('toFieldErrorMap — the projection from WIRE-1 detail to per-field messages', () => {
  it('keys each message by its field name', () => {
    expect(toFieldErrorMap(MISSING_TWO)).toEqual({
      date_of_birth: 'required value absent',
      city: 'required value absent',
    });
  });

  it('survives a malformed or absent detail rather than taking the view down', () => {
    // It crosses the wire, so it is not trusted to be well-formed.
    expect(toFieldErrorMap(undefined)).toEqual({});
    expect(toFieldErrorMap({ field_errors: [null, {}, { field: 'x' }] }))
      .toEqual({ x: SUBMISSION_COPY.unknownErrorMessage });
  });
});

describe('the rejection renders PER-FIELD, beside the input at fault', () => {
  it('renders one message per field_errors entry, addressable by field', async () => {
    await submitAndReject(MISSING_TWO);
    expect(screen.getByTestId(fieldErrorTestid('date_of_birth')))
      .toHaveTextContent('required value absent');
    expect(screen.getByTestId(fieldErrorTestid('city')))
      .toHaveTextContent('required value absent');
  });

  it('⛔ marks ONLY the offending inputs — an untouched field carries no error', async () => {
    // The whole value of per-field errors is discrimination. If every input were marked, the
    // user would be no better off than with a banner.
    await submitAndReject(MISSING_TWO);
    expect(screen.queryByTestId(fieldErrorTestid('full_name'))).toBeNull();
    expect(screen.getByTestId(fieldInputTestid('full_name'))).not.toHaveAttribute('aria-invalid');
  });

  it('wires each message to its input with aria-describedby and aria-invalid', async () => {
    // ⚑ Rendering the text near the box is not enough for a screen-reader user; the association
    // has to be programmatic or the error is invisible to them.
    await submitAndReject(MISSING_TWO);
    const input = screen.getByTestId(fieldInputTestid('city'));
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(input).toHaveAttribute('aria-describedby', fieldErrorTestid('city'));
  });

  it('translates reason_category instead of echoing the raw slug', async () => {
    await submitAndReject(MISSING_TWO);
    expect(screen.getByTestId('submission-rejection-reason'))
      .toHaveTextContent(SUBMISSION_COPY.rejectionReasonLabels.missing_required);
    expect(screen.getByTestId('submission-rejection')).not.toHaveTextContent('missing_required');
  });

  it('renders missing_items, which field_errors alone would not cover', async () => {
    // ⚑ The two overlap but are not the same: something intake could not map to ANY input
    // appears only in `missing_items`. Rendering only the per-field half would show a rejection
    // with nothing marked.
    await submitAndReject(MISSING_TWO);
    expect(screen.getByTestId(missingItemTestid('date_of_birth'))).toBeInTheDocument();
    expect(screen.getByTestId(missingItemTestid('city'))).toBeInTheDocument();
  });

  it('falls back to a readable reason for an unrecognized category', async () => {
    await submitAndReject({ reason_category: 'something_new', field_errors: [], missing_items: [] });
    expect(screen.getByTestId('submission-rejection-reason'))
      .toHaveTextContent(SUBMISSION_COPY.rejectionFallbackReason);
  });
});

describe('a rejection is RECOVERABLE, not a dead end', () => {
  it('keeps the user on the form with every typed value intact', async () => {
    // ⛔ A rejection that cleared the form would make the structured detail useless: there would
    // be nothing left to correct. This is what makes 400 a distinct state from `error`.
    await submitAndReject(MISSING_TWO);
    expect(screen.getByTestId('submission-form')).toBeInTheDocument();
    expect(screen.getByTestId(fieldInputTestid('full_name'))).toHaveValue(VALID.full_name);
    expect(screen.getByTestId(fieldInputTestid('city'))).toHaveValue(VALID.city);
  });

  it('re-enables submit so a corrected application can be sent again', async () => {
    await submitAndReject(MISSING_TWO);
    expect(screen.getByTestId('submission-submit')).toBeEnabled();
  });

  it('⚑ does NOT render the generic error state — a rejection is a domain outcome', async () => {
    await submitAndReject(MISSING_TWO);
    expect(screen.queryByTestId('submission-error')).toBeNull();
  });

  it('a NON-400 failure takes the generic error path instead', async () => {
    // The other half of the same distinction: 403 carries nothing actionable, so there is
    // nothing to mark and a per-field render would be a lie.
    const seam = stubSeam({
      submit: async () => { throw { error: { code: 'forbidden', message: 'no', detail: {} } }; },
    });
    render(<SubmissionView submissionSeam={seam} />);
    fillValid();
    fireEvent.click(screen.getByTestId('submission-submit'));
    await waitFor(() => expect(screen.getByTestId('submission-error-code'))
      .toHaveTextContent('forbidden'));
    expect(screen.queryByTestId('submission-rejection')).toBeNull();
  });
});
