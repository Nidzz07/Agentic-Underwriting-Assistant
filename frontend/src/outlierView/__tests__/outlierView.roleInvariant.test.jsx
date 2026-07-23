import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RoleProvider } from '../../shell/session/roleContext.js';
import { OutlierView } from '../OutlierView.jsx';
import { createOutlierFetch } from '../fetchSeam.js';
import { makeReadyPopulatedBody, makeCapturingTransport } from './fixtures.js';

// NFR-OUTV-VIEWONLY-1 (P-OUTV-8) — RoleInvariantRenderingPattern. The view gates on nothing: the
// rendered output is IDENTICAL for every Role and for no Role at all. shell/session is available
// for chrome but is not gated on (Q2-A / BR-OUTV-4; unit-of-work.md:247 "no write/commit control ->
// no RBAC facet"). The real authorization boundary stays auth-rbac, server-side.

async function renderAs(role) {
  const fetchSeam = createOutlierFetch(makeCapturingTransport(makeReadyPopulatedBody()));
  const { container, unmount } = render(
    <RoleProvider value={role}>
      <OutlierView fetchSeam={fetchSeam} applicationId="app-1" />
    </RoleProvider>,
  );
  await screen.findByTestId('outlier-view');
  const html = container.innerHTML;
  unmount();
  return html;
}

describe('VIEWONLY-1 — rendering is invariant across every Role', () => {
  it('underwriter, auditor, admin and null all render byte-identical output', async () => {
    const underwriter = await renderAs('underwriter');
    const auditor = await renderAs('auditor');
    const admin = await renderAs('admin');
    const anonymous = await renderAs(null);

    expect(auditor).toBe(underwriter);
    expect(admin).toBe(underwriter);
    expect(anonymous).toBe(underwriter);
  });

  it('the invariant output is non-empty (not a vacuous pass)', async () => {
    const html = await renderAs('underwriter');
    expect(html).toContain('outlier-region-score');
    expect(html).toContain('outlier-region-flags');
  });

  it('renders no commit/submit affordance — the only button is Retry, and only on error', async () => {
    const fetchSeam = createOutlierFetch(makeCapturingTransport(makeReadyPopulatedBody()));
    const { container } = render(<OutlierView fetchSeam={fetchSeam} applicationId="app-1" />);
    await screen.findByTestId('outlier-view');

    expect(container.querySelectorAll('button')).toHaveLength(0);
    expect(container.querySelectorAll('form')).toHaveLength(0);
    expect(container.querySelectorAll('input')).toHaveLength(0);
  });
});
