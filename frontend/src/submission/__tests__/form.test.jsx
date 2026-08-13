// Step 4.2 — form rendering, field validation, and the disabled-until-valid affordance.
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { SubmissionView } from '../SubmissionView.jsx';
import { REQUIRED_FIELDS, SUBMISSION_COPY } from '../copy.js';
import { fieldInputTestid } from '../testids.js';
import { fillValid, stubSeam, VALID } from './fixtures.js';

describe('the form renders every field intake requires', () => {
  it('renders the view and one input per required field', () => {
    render(<SubmissionView submissionSeam={stubSeam()} />);
    expect(screen.getByTestId('submission-view')).toBeInTheDocument();
    for (const field of REQUIRED_FIELDS) {
      expect(screen.getByTestId(fieldInputTestid(field))).toBeInTheDocument();
    }
  });

  it('the field set is EXACTLY what the frozen IntakeGate requires — no more, no fewer', () => {
    // ⚑ An exact-set assertion, not a spot check. A field added here that intake does not read
    // is dead UI; a required field MISSING here produces a form that can only ever 400 — the
    // worst outcome, because it looks like the server rejecting the user's data.
    expect([...REQUIRED_FIELDS].sort()).toEqual([
      'as_of_date', 'city', 'date_of_birth', 'full_name',
      'gender', 'requested_cover_amount', 'verifiable_income_annual',
    ]);
  });

  it('every label comes from the copy module, never inlined', () => {
    render(<SubmissionView submissionSeam={stubSeam()} />);
    for (const field of REQUIRED_FIELDS) {
      expect(screen.getByText(SUBMISSION_COPY.fieldLabels[field])).toBeInTheDocument();
    }
  });
});

describe('the submit affordance is disabled until the form is valid', () => {
  it('is disabled on first render, when every field is empty', () => {
    render(<SubmissionView submissionSeam={stubSeam()} />);
    expect(screen.getByTestId('submission-submit')).toBeDisabled();
  });

  it('stays disabled while ANY required field is still empty', () => {
    render(<SubmissionView submissionSeam={stubSeam()} />);
    fillValid();
    fireEvent.change(screen.getByTestId(fieldInputTestid('city')), { target: { value: '' } });
    expect(screen.getByTestId('submission-submit')).toBeDisabled();
  });

  it('treats a whitespace-only value as empty', () => {
    // ⚑ The same discipline BR-COMMIT-GATE applies to an override reason. A form that accepted
    // "   " would hand intake a value it will reject, turning a client-side check the user can
    // see into a server round-trip they cannot.
    render(<SubmissionView submissionSeam={stubSeam()} />);
    fillValid();
    fireEvent.change(screen.getByTestId(fieldInputTestid('full_name')), { target: { value: '   ' } });
    expect(screen.getByTestId('submission-submit')).toBeDisabled();
  });

  it('becomes enabled once every required field carries a value', () => {
    render(<SubmissionView submissionSeam={stubSeam()} />);
    fillValid();
    expect(screen.getByTestId('submission-submit')).toBeEnabled();
  });

  it('submits the typed values to the seam, verbatim', () => {
    // ⚑ SUPERSEDED 2026-08-03 (WIRE1-Fold-7). The Fold-6 assertion is preserved verbatim:
    //
    //     expect(seam.submit).toHaveBeenCalledWith(VALID);
    //
    // The seam gained a SECOND argument — the `{ docType: File }` map — so a one-argument
    // assertion no longer describes the call. ⛔ What it still pins is unchanged and is the
    // point: the REQUIRED values reach the seam verbatim, none renamed, none dropped, and with
    // no documents attached the second argument is empty (which is what keeps the JSON encoding
    // in play for a document-free submission).
    const seam = stubSeam();
    render(<SubmissionView submissionSeam={seam} />);
    fillValid();
    fireEvent.click(screen.getByTestId('submission-submit'));

    const [formFields, documents] = seam.submit.mock.calls[0];
    expect(formFields).toEqual(VALID);
    expect(Object.values(documents).filter(Boolean)).toEqual([]);
  });

  it('⛔ NEVER sends an application_id — the server assigns it', () => {
    // ⚑ WIRE-1 §5 (Fold-6): `application_id` is assigned by IntakeGate on gate pass, the same
    // shape as R5's server-derived `underwriter_id`. A client that could choose its own id could
    // collide with, or overwrite, another applicant's case.
    const seam = stubSeam();
    render(<SubmissionView submissionSeam={seam} />);
    fillValid();
    fireEvent.click(screen.getByTestId('submission-submit'));
    expect(seam.submit.mock.calls[0][0]).not.toHaveProperty('application_id');
  });

  it('does not call the seam while the form is invalid', () => {
    const seam = stubSeam();
    render(<SubmissionView submissionSeam={seam} />);
    fireEvent.click(screen.getByTestId('submission-submit'));
    expect(seam.submit).not.toHaveBeenCalled();
  });
});
