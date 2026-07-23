import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RoleProvider } from '../../shell/session/roleContext.js';
import { MemoView } from '../MemoView.jsx';
import { unsortedReadyMemoView } from './fixtures.js';

// VIEWONLY-1 — the memo view reads no Role and composes no RoleGate: render is IDENTICAL across roles.
const seam = async () => unsortedReadyMemoView;

async function htmlForRole(role) {
  const { container, unmount } = render(
    <RoleProvider value={role}><MemoView memoFetchSeam={seam} applicationId="app-1" /></RoleProvider>,
  );
  await screen.findByTestId('memo-view');
  const html = container.innerHTML;
  unmount();
  return html;
}

describe('MemoView — VIEWONLY-1: render identical across roles', () => {
  it('underwriter / auditor / admin produce identical output', async () => {
    const u = await htmlForRole('underwriter');
    const a = await htmlForRole('auditor');
    const d = await htmlForRole('admin');
    expect(a).toBe(u);
    expect(d).toBe(u);
  });
});
