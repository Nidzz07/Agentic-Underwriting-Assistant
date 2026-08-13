// WIRE1-Fold-7 stage 6 — document upload, the optional fields, and the disclosure.
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SubmissionView, toDocumentStatuses, toFormFields } from '../SubmissionView.jsx';
import { buildSubmitRequest } from '../fetchSeam.js';
import {
  DOC_TYPES,
  OPTIONAL_FIELDS,
  REQUIRED_FIELDS,
  SUBMISSION_COPY,
} from '../copy.js';
import { documentInputTestid, documentStatusTestid, fieldInputTestid } from '../testids.js';
import { fillValid, stubSeam, VALID } from './fixtures.js';

function pdf(name = 'salary.pdf') {
  return new File([new Uint8Array([0x25, 0x50, 0x44, 0x46])], name, { type: 'application/pdf' });
}

function attach(docType, file = pdf()) {
  fireEvent.change(screen.getByTestId(documentInputTestid(docType)), {
    target: { files: [file] },
  });
}

// --- the affordance constraint (Q10) -----------------------------------------------------

describe('the disabled-until-valid affordance keys ONLY on the required seven', () => {
  it('⛔ REQUIRED_FIELDS is still exactly the original seven', () => {
    // Q10's stated constraint, as an exact set. An optional field appended here would become
    // mandatory by UI accident — a form blocking on something intake never needed.
    expect([...REQUIRED_FIELDS].sort()).toEqual([
      'as_of_date', 'city', 'date_of_birth', 'full_name',
      'gender', 'requested_cover_amount', 'verifiable_income_annual',
    ]);
  });

  it('the two sets are DISJOINT', () => {
    const overlap = OPTIONAL_FIELDS.filter((f) => REQUIRED_FIELDS.includes(f));
    expect(overlap).toEqual([]);
  });

  it('submit ENABLES with every optional field left blank', () => {
    render(<SubmissionView submissionSeam={stubSeam()} />);
    fillValid();
    expect(screen.getByTestId('submission-submit')).toBeEnabled();
  });

  it('submit STAYS enabled when an optional field is then cleared', () => {
    render(<SubmissionView submissionSeam={stubSeam()} />);
    fillValid();
    fireEvent.change(screen.getByTestId(fieldInputTestid('occupation')), { target: { value: 'X' } });
    fireEvent.change(screen.getByTestId(fieldInputTestid('occupation')), { target: { value: '' } });
    expect(screen.getByTestId('submission-submit')).toBeEnabled();
  });

  it('submit does NOT require a document', () => {
    render(<SubmissionView submissionSeam={stubSeam()} />);
    fillValid();
    expect(screen.getByTestId('submission-submit')).toBeEnabled();
  });
});

// --- the optional fields reach the wire correctly ----------------------------------------

describe('toFormFields — the projection intake actually receives', () => {
  it('omits blank optionals rather than sending empty strings', () => {
    const values = Object.fromEntries([...REQUIRED_FIELDS, ...OPTIONAL_FIELDS].map((f) => [f, '']));
    Object.assign(values, VALID);
    expect(Object.keys(toFormFields(values)).sort()).toEqual([...REQUIRED_FIELDS].sort());
  });

  it('⛔ sends health_flags as a LIST, not a string', () => {
    // `IntakeGate` does `list(extracted.get("health_flags") or [])`, so a bare string would be
    // exploded into one entry PER CHARACTER — a silently absurd profile rather than an error.
    const values = { ...VALID, health_flags: 'none reported' };
    expect(toFormFields(values).health_flags).toEqual(['none reported']);
  });

  it('passes the other optionals through as trimmed strings', () => {
    const values = { ...VALID, height_cm: ' 170 ', employment_type: 'salaried' };
    const out = toFormFields(values);
    expect(out.height_cm).toBe('170');
    expect(out.employment_type).toBe('salaried');
  });
});

// --- the seam's two encodings -------------------------------------------------------------

describe('buildSubmitRequest chooses the encoding', () => {
  it('stays JSON when no document is attached', () => {
    const request = buildSubmitRequest(VALID, {});
    expect(request.body).toEqual({ form_fields: VALID, documents: [] });
    expect(request.body instanceof FormData).toBe(false);
  });

  it('becomes FormData when a document IS attached', () => {
    const request = buildSubmitRequest(VALID, { salary_slip: pdf() });
    expect(request.body instanceof FormData).toBe(true);
    expect(request.body.get('form_fields')).toBe(JSON.stringify(VALID));
    expect(request.body.get('salary_slip')).toBeInstanceOf(File);
  });

  it('names each part by its DocType value, as WIRE-1 §1 requires', () => {
    const request = buildSubmitRequest(VALID, {
      salary_slip: pdf('a.pdf'), medical_questionnaire: pdf('b.pdf'),
    });
    expect([...request.body.keys()].sort())
      .toEqual(['form_fields', 'medical_questionnaire', 'salary_slip']);
  });

  it('ignores a cleared slot rather than sending an empty part', () => {
    const request = buildSubmitRequest(VALID, { salary_slip: null, bank_statement: pdf() });
    expect([...request.body.keys()].sort()).toEqual(['bank_statement', 'form_fields']);
  });
});

// --- per-document status is VISIBLE (Q7) --------------------------------------------------

describe('toDocumentStatuses — the server manifest drives what the user sees', () => {
  it('reports parsed and unparseable per document, not in aggregate', () => {
    const statuses = toDocumentStatuses(
      [
        { doc_type: 'salary_slip', status: 'parsed' },
        { doc_type: 'bank_statement', status: 'unparseable' },
      ],
      { salary_slip: pdf(), bank_statement: pdf() },
    );
    expect(statuses).toEqual({ salary_slip: 'parsed', bank_statement: 'unparseable' });
  });

  it('survives a malformed manifest rather than taking the view down', () => {
    expect(toDocumentStatuses([null, {}, { doc_type: 'nope', status: 'parsed' }], {})).toEqual({});
    expect(toDocumentStatuses(undefined, {})).toEqual({});
  });
});

describe('the user SEES what happened to each document', () => {
  it('renders one file input per DocType', () => {
    render(<SubmissionView submissionSeam={stubSeam()} />);
    for (const docType of DOC_TYPES) {
      expect(screen.getByTestId(documentInputTestid(docType))).toBeInTheDocument();
    }
  });

  it('shows "selected" as soon as a file is chosen', () => {
    render(<SubmissionView submissionSeam={stubSeam()} />);
    attach('salary_slip');
    expect(screen.getByTestId(documentStatusTestid('salary_slip')))
      .toHaveTextContent(SUBMISSION_COPY.documentStatusLabels.selected);
  });

  it('⛔ shows PARSED and UNPARSEABLE per document, never one aggregate', async () => {
    // Q7's requirement. `DOCS-COMPLETE-1` counts only documents that PARSED, so a failure
    // changes the assessment — an applicant told nothing cannot fix the one file at fault.
    const seam = stubSeam({
      submit: async () => ({
        application_id: 'APP-1',
        status: 'pending',
        documents: [
          { doc_type: 'salary_slip', status: 'parsed' },
          { doc_type: 'bank_statement', status: 'unparseable' },
        ],
      }),
    });
    render(<SubmissionView submissionSeam={seam} />);
    fillValid();
    attach('salary_slip');
    attach('bank_statement');
    fireEvent.click(screen.getByTestId('submission-submit'));

    await screen.findByTestId('submission-accepted');
    expect(screen.getByTestId(documentStatusTestid('salary_slip')))
      .toHaveTextContent(SUBMISSION_COPY.documentStatusLabels.parsed);
    expect(screen.getByTestId(documentStatusTestid('bank_statement')))
      .toHaveTextContent(SUBMISSION_COPY.documentStatusLabels.unparseable);
  });

  it('the attached files reach the seam', async () => {
    const seam = stubSeam();
    render(<SubmissionView submissionSeam={seam} />);
    fillValid();
    attach('salary_slip');
    fireEvent.click(screen.getByTestId('submission-submit'));

    await waitFor(() => expect(seam.submit).toHaveBeenCalled());
    const [, documents] = seam.submit.mock.calls[0];
    expect(documents.salary_slip).toBeInstanceOf(File);
  });

  it('a removed document is not sent', async () => {
    const seam = stubSeam();
    render(<SubmissionView submissionSeam={seam} />);
    fillValid();
    attach('salary_slip');
    fireEvent.click(screen.getByTestId(`${documentInputTestid('salary_slip')}-remove`));
    fireEvent.click(screen.getByTestId('submission-submit'));

    await waitFor(() => expect(seam.submit).toHaveBeenCalled());
    expect(seam.submit.mock.calls[0][1].salary_slip).toBeNull();
  });

  it('a 413 is recoverable and keeps the user on the form', async () => {
    const seam = stubSeam({
      submit: async () => {
        throw { error: { code: 'payload_too_large', message: 'too big', detail: {} } };
      },
    });
    render(<SubmissionView submissionSeam={seam} />);
    fillValid();
    attach('salary_slip');
    fireEvent.click(screen.getByTestId('submission-submit'));

    expect(await screen.findByTestId('submission-error-code'))
      .toHaveTextContent('payload_too_large');
    expect(screen.getByTestId('submission-form')).toBeInTheDocument();
    expect(screen.getByTestId('submission-submit')).toBeEnabled();
  });
});

// --- the disclosures (Q11, Q3(a)) ----------------------------------------------------------

describe('the disclosures are rendered TO THE USER', () => {
  it('⚠️ Q11: the health-notes completeness limitation is stated in the form', () => {
    render(<SubmissionView submissionSeam={stubSeam()} />);
    const note = screen.getByTestId('submission-completeness-note');
    expect(note).toBeInTheDocument();
    expect(note.textContent).toMatch(/does not by itself mark an application complete/i);
    expect(note.textContent).toMatch(/health notes/i);
  });

  it('the disclosure is copy, not an inline string', () => {
    render(<SubmissionView submissionSeam={stubSeam()} />);
    expect(screen.getByTestId('submission-completeness-note'))
      .toHaveTextContent(SUBMISSION_COPY.completenessDisclosure);
  });

  it('Q3(a): the upload latency is disclosed rather than engineered away', () => {
    render(<SubmissionView submissionSeam={stubSeam()} />);
    expect(screen.getByTestId('submission-latency-hint'))
      .toHaveTextContent(SUBMISSION_COPY.uploadLatencyHint);
  });

  it('every optional field is labelled from the copy module', () => {
    render(<SubmissionView submissionSeam={stubSeam()} />);
    for (const field of OPTIONAL_FIELDS) {
      expect(screen.getByText(SUBMISSION_COPY.optionalFieldLabels[field])).toBeInTheDocument();
    }
  });
});
