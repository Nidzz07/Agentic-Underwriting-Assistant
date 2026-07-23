import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { makeOverrideDouble, makeMemoView, renderForm } from './fixtures.js';

// RBAC-1 — RoleGate can="act" is COSMETIC: it shows the override affordance only to the underwriter
// cosmetic role. All three roles + null, mirroring the frozen COSMETIC_CAPABILITIES act cells. (The
// structural no-authz-call / no-backend-import half is in noBackendImport.test.js.)
describe('RBAC-1 — cosmetic RoleGate over all three roles + null', () => {
  it('underwriter sees the override affordance', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderForm({ role: 'underwriter', seam });
    expect(await screen.findByTestId('override-affordance-button')).toBeInTheDocument();
  });

  it.each(['auditor', 'admin'])('non-underwriter %s does NOT see the affordance (fallback)', async (role) => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderForm({ role, seam });
    // ready reached (context shows) but the affordance is cosmetically hidden
    await screen.findByTestId('override-recommendation-context');
    expect(screen.queryByTestId('override-affordance-button')).toBeNull();
  });

  it('null (unauthenticated) does NOT see the affordance', async () => {
    const seam = makeOverrideDouble();
    seam.fetchContext.resolveWith(makeMemoView());
    renderForm({ role: null, seam });
    await screen.findByTestId('override-recommendation-context');
    expect(screen.queryByTestId('override-affordance-button')).toBeNull();
  });
});
