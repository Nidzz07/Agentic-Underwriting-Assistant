import { describe, it, expect } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { OVERRIDE_COPY } from '../copy.js';
import {
  makeOverrideDouble, makeMemoView, makeCommittedOverride, NONBLANK_REASON,
  forbiddenEnvelope, conflictEnvelope, invalidEnvelope, unprocessableEnvelope, renderForm,
} from './fixtures.js';

// ERROR-1 — per-status surfacing via the ONE envelope: message visible / code hidden testid / detail
// never. Table-driven across the four documented commit statuses; plus the 200 success path. The 409
// conflictEnvelope is REUSED for both already-committed and blank-reason-race causes (one code, one
// rendered state — no special-casing beyond copy).
const cases = [
  { label: '403 forbidden', envelope: forbiddenEnvelope, code: 'forbidden', message: OVERRIDE_COPY.notPermittedMessage },
  { label: '409 conflict', envelope: conflictEnvelope, code: 'commit_conflict', message: OVERRIDE_COPY.conflictMessage },
  { label: '400 invalid', envelope: invalidEnvelope, code: 'invalid_request', message: invalidEnvelope.error.message },
  { label: '422 unprocessable', envelope: unprocessableEnvelope, code: 'unprocessable', message: unprocessableEnvelope.error.message },
];

async function overrideThenConfirm(seam) {
  renderForm({ seam });
  fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: NONBLANK_REASON } });
  fireEvent.click(screen.getByTestId('override-affordance-button'));
  fireEvent.click(await screen.findByTestId('override-confirm-submit'));
}

describe('ERROR-1 — per-status commit surfacing', () => {
  it.each(cases)('$label renders its distinct error state via the shared envelope', async ({ envelope, code, message }) => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitOverride.rejectWith(envelope);
    await overrideThenConfirm(seam);

    await screen.findByTestId('override-state-error');
    expect(screen.getByTestId('override-error-message')).toHaveTextContent(message);
    expect(screen.getByTestId('override-error-code')).toHaveTextContent(code);
    expect(screen.getByTestId('override-error-code')).not.toBeVisible(); // code never visible UI text
  });

  it('never renders error.detail (no leakage)', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitOverride.rejectWith(forbiddenEnvelope); // detail carries ROLE_SECRET_XYZ
    await overrideThenConfirm(seam);
    await screen.findByTestId('override-state-error');
    expect(document.body.innerHTML).not.toContain('ROLE_SECRET_XYZ');
  });

  it('200 renders the committed-override confirmation', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    seam.submitOverride.resolveWith(makeCommittedOverride());
    await overrideThenConfirm(seam);
    expect(await screen.findByTestId('override-committed-view')).toBeInTheDocument();
  });
});
