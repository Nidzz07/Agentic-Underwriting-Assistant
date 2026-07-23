import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { makeCommitDouble, makeMemoView, renderGate } from './fixtures.js';

// RBAC-1 — RoleGate can="act" is COSMETIC: it shows the approve affordance only to the underwriter
// cosmetic role. All three roles + null, mirroring the frozen COSMETIC_CAPABILITIES act cells
// (Fold-3). (The structural no-authz-call / no-backend-import half is in refNotOwn.imports.test.js.)
describe('RBAC-1 — cosmetic RoleGate over all three roles + null', () => {
  it('underwriter sees the approve affordance', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderGate({ role: 'underwriter', seam });
    expect(await screen.findByTestId('approval-affordance-approve')).toBeInTheDocument();
  });

  it.each(['auditor', 'admin'])('non-underwriter %s does NOT see the affordance (fallback)', async (role) => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderGate({ role, seam });
    // ready reached (context shows) but the affordance is cosmetically hidden
    await screen.findByTestId('approval-recommendation-context');
    expect(screen.queryByTestId('approval-affordance-approve')).toBeNull();
  });

  it('null (unauthenticated) does NOT see the affordance', async () => {
    const seam = makeCommitDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderGate({ role: null, seam });
    await screen.findByTestId('approval-recommendation-context');
    expect(screen.queryByTestId('approval-affordance-approve')).toBeNull();
  });
});
