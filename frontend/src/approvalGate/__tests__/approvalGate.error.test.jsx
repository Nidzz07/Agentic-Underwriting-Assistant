import { describe, it, expect } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { APPROVAL_COPY } from '../copy.js';
import {
  makeCommitDouble, makeMemoView, makeCommittedDecision,
  forbiddenEnvelope, conflictEnvelope, invalidEnvelope, unprocessableEnvelope, renderGate,
} from './fixtures.js';

// ERROR-1 — per-status surfacing via the ONE envelope: message visible / code hidden testid /
// detail never. Table-driven across the four documented commit statuses; plus the 200 success path.
const cases = [
  { label: '403 forbidden', envelope: forbiddenEnvelope, code: 'forbidden', message: APPROVAL_COPY.notPermittedMessage },
  { label: '409 conflict', envelope: conflictEnvelope, code: 'commit_conflict', message: APPROVAL_COPY.conflictMessage },
  { label: '400 invalid', envelope: invalidEnvelope, code: 'invalid_request', message: invalidEnvelope.error.message },
  { label: '422 unprocessable', envelope: unprocessableEnvelope, code: 'unprocessable', message: unprocessableEnvelope.error.message },
];

async function approveThenConfirm(seam) {
  renderGate({ seam });
  fireEvent.click(await screen.findByTestId('approval-affordance-approve'));
  fireEvent.click(await screen.findByTestId('approval-confirm-submit'));
}

describe('ERROR-1 — per-status commit surfacing', () => {
  it.each(cases)('$label renders its distinct error state via the shared envelope', async ({ envelope, code, message }) => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitApprove.rejectWith(envelope);
    await approveThenConfirm(seam);

    await screen.findByTestId('approval-state-error');
    expect(screen.getByTestId('approval-error-message')).toHaveTextContent(message);
    expect(screen.getByTestId('approval-error-code')).toHaveTextContent(code);
    expect(screen.getByTestId('approval-error-code')).not.toBeVisible(); // code never visible UI text
  });

  it('never renders error.detail (no leakage)', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitApprove.rejectWith(forbiddenEnvelope); // detail carries ROLE_SECRET_XYZ
    await approveThenConfirm(seam);
    await screen.findByTestId('approval-state-error');
    expect(document.body.innerHTML).not.toContain('ROLE_SECRET_XYZ');
  });

  it('200 renders the committed-decision confirmation', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitApprove.resolveWith(makeCommittedDecision());
    await approveThenConfirm(seam);
    expect(await screen.findByTestId('approval-committed')).toBeInTheDocument();
  });
});
