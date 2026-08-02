// Steps 4.4 + 4.5 — the accepted -> draft-trigger flow, and the completeness bar every other
// unit meets (role invariance, error, loading, recovery).
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SubmissionView } from '../SubmissionView.jsx';
import { SUBMISSION_COPY } from '../copy.js';
import { fieldInputTestid } from '../testids.js';
import { fillValid, stubSeam } from './fixtures.js';

async function submitSuccessfully(seam) {
  render(<SubmissionView submissionSeam={seam} />);
  fillValid();
  fireEvent.click(screen.getByTestId('submission-submit'));
  return screen.findByTestId('submission-accepted');
}

// --- step 4.4: success, then the explicit drafting trigger -------------------------------

describe('a successful submission reports the case as PENDING, not assessed', () => {
  it('renders the server-assigned application id', async () => {
    await submitSuccessfully(stubSeam());
    expect(screen.getByTestId('submission-accepted-id')).toHaveTextContent('APP-1');
  });

  it('⛔ says the application is NOT yet assessed', async () => {
    // Q3(a): submission is LLM-free and stops at `evaluated`, which R4 reports as `pending`.
    // A panel that read "submitted successfully" and stopped would let the user assume the
    // assessment had happened — the one thing the two-phase flow must not imply.
    await submitSuccessfully(stubSeam());
    expect(screen.getByTestId('submission-accepted-pending'))
      .toHaveTextContent(SUBMISSION_COPY.acceptedPendingMessage);
  });

  it('notifies the composition root of the new application id', async () => {
    // ⚑ How the submitted case reaches the queue: the root re-reads R2. Without this the user
    // would submit and see nothing appear until a manual reload.
    const onSubmitted = vi.fn();
    render(<SubmissionView submissionSeam={stubSeam()} onSubmitted={onSubmitted} />);
    fillValid();
    fireEvent.click(screen.getByTestId('submission-submit'));
    await waitFor(() => expect(onSubmitted).toHaveBeenCalledWith('APP-1'));
  });

  it('offers the drafting trigger as a SEPARATE, explicit action', async () => {
    await submitSuccessfully(stubSeam());
    expect(screen.getByTestId('submission-draft')).toBeInTheDocument();
  });

  it('the trigger targets the application just created', async () => {
    const seam = stubSeam();
    await submitSuccessfully(seam);
    fireEvent.click(screen.getByTestId('submission-draft'));
    await waitFor(() => expect(seam.triggerDraft).toHaveBeenCalledWith('APP-1'));
  });

  it('reports a completed assessment', async () => {
    await submitSuccessfully(stubSeam());
    fireEvent.click(screen.getByTestId('submission-draft'));
    expect(await screen.findByTestId('submission-draft-outcome'))
      .toHaveTextContent(SUBMISSION_COPY.draftedMessage);
  });

  it('⚑ reports a SKIPPED re-trigger as already done, not as a failure', async () => {
    // Inherits register #27's `DraftOutcome.skipped`. Rendering a skip as an error would train
    // the user to ignore the error state — the shape that kept register #18 invisible.
    const seam = stubSeam({
      triggerDraft: async () => ({ application_id: 'APP-1', status: 'ready', outcome: 'skipped' }),
    });
    await submitSuccessfully(seam);
    fireEvent.click(screen.getByTestId('submission-draft'));
    expect(await screen.findByTestId('submission-draft-outcome'))
      .toHaveTextContent(SUBMISSION_COPY.skippedMessage);
    expect(screen.queryByTestId('submission-error')).toBeNull();
  });

  it('can start a fresh application, clearing every previous value', async () => {
    await submitSuccessfully(stubSeam());
    fireEvent.click(screen.getByTestId('submission-startover'));
    expect(screen.getByTestId(fieldInputTestid('full_name'))).toHaveValue('');
    expect(screen.getByTestId('submission-submit')).toBeDisabled();
  });
});

// --- step 4.5: the completeness bar the six existing units set ----------------------------

describe('loading, error and recovery states', () => {
  it('renders a busy state while the submission is in flight', async () => {
    let release;
    const seam = stubSeam({ submit: () => new Promise((resolve) => { release = resolve; }) });
    render(<SubmissionView submissionSeam={seam} />);
    fillValid();
    fireEvent.click(screen.getByTestId('submission-submit'));

    expect(screen.getByTestId('submission-submitting')).toHaveAttribute('aria-busy', 'true');
    expect(screen.getByTestId('submission-submit')).toBeDisabled();

    release({ application_id: 'APP-1', status: 'pending' });
    await screen.findByTestId('submission-accepted');
  });

  it('renders the error code for a transport failure', async () => {
    const seam = stubSeam({
      submit: async () => {
        throw { error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} } };
      },
    });
    render(<SubmissionView submissionSeam={seam} />);
    fillValid();
    fireEvent.click(screen.getByTestId('submission-submit'));
    expect(await screen.findByTestId('submission-error-code')).toHaveTextContent('network_error');
  });

  it('a 403 from require_underwriter renders as an ordinary error, not a crash', async () => {
    // ⚑ RoleInvariant: this unit reads no Role and composes no RoleGate. The SERVER is the real
    // gate (`require_underwriter`), and its 403 must render like any other failure. Hiding the
    // form client-side would duplicate an authorization decision the server already owns.
    const seam = stubSeam({
      submit: async () => {
        throw { error: { code: 'forbidden', message: 'no permission', detail: {} } };
      },
    });
    render(<SubmissionView submissionSeam={seam} />);
    fillValid();
    fireEvent.click(screen.getByTestId('submission-submit'));
    expect(await screen.findByTestId('submission-error-code')).toHaveTextContent('forbidden');
  });

  it('a FAILED drafting trigger leaves the trigger available to retry', async () => {
    // ⚑ R11 maps a genuine drafting failure to 500 (register #14 — `failed` has no wire
    // representation). A dead end here would strand a real, submitted case with no way forward.
    const seam = stubSeam({
      triggerDraft: async () => {
        throw { error: { code: 'internal_error', message: 'Drafting did not produce a memo.', detail: {} } };
      },
    });
    await submitSuccessfully(seam);
    fireEvent.click(screen.getByTestId('submission-draft'));
    expect(await screen.findByTestId('submission-error-code')).toHaveTextContent('internal_error');
    expect(screen.getByTestId('submission-draft')).toBeInTheDocument();
    expect(screen.queryByTestId('submission-draft-outcome')).toBeNull();
  });

});
