import { describe, it, expect } from 'vitest';
import { screen, fireEvent } from '@testing-library/react';
import { makeCommitDouble, makeMemoView, renderGate } from './fixtures.js';

// SCOPE-APPROVE-1 — approve-only: no override control, no reason input anywhere in the tree.
describe('SCOPE-APPROVE-1 — approve-only scope', () => {
  it('the confirm flow renders no override control and no reason input', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderGate({ seam });
    fireEvent.click(await screen.findByTestId('approval-affordance-approve'));
    await screen.findByTestId('approval-confirm-dialog');

    expect(screen.queryByTestId('approval-override')).toBeNull();
    expect(document.querySelector('textarea')).toBeNull();
    expect(document.querySelector('input')).toBeNull();
  });
});
