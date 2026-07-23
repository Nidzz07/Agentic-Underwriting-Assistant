import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RoleProvider } from '../../shell/session/roleContext.js';
import { QueueView } from '../QueueView.jsx';

// VIEWONLY-1 — the queue reads no Role and composes no RoleGate: render is IDENTICAL across roles.
const seam = async () => ({
  items: [{ application_id: 'app-1', recommendation: 'APPROVE', confidence: 'High' }],
  page: { page: 1, size: 20, total: 1 },
});

async function htmlForRole(role) {
  const { container, unmount } = render(
    <RoleProvider value={role}><QueueView fetchSeam={seam} onSelect={() => {}} /></RoleProvider>,
  );
  await screen.findByTestId('queue-table');
  const html = container.innerHTML;
  unmount();
  return html;
}

describe('QueueView — VIEWONLY-1: render identical across roles', () => {
  it('underwriter / auditor / admin produce identical output', async () => {
    const u = await htmlForRole('underwriter');
    const a = await htmlForRole('auditor');
    const d = await htmlForRole('admin');
    expect(a).toBe(u);
    expect(d).toBe(u);
  });
});
