import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { RoleProvider } from '../../shell/session/roleContext.js';
import { HistoryView } from '../HistoryView.jsx';
import { makeHistoryDouble, makeListBody, approveRecord } from './fixtures.js';

// VIEWONLY-1 (P11) — role-invariant rendering. R6/R7 are authenticated ANY-ROLE and this is a pure
// READ surface with no act-affordance to gate, so no RoleGate is composed. `can="read"` is
// deliberately NOT used: it would cosmetically exclude `admin` (RoleGate's COSMETIC_CAPABILITIES has
// admin read:false), diverging from the frozen contract. The auditor read-only distinction is
// enforced SERVER-side (auth-rbac SEC-4), never by this view.
async function htmlForRole(role, testid) {
  const seam = makeHistoryDouble({
    list: [{ resolve: makeListBody() }],
    detail: [{ resolve: approveRecord }],
  });
  render(<RoleProvider value={role}><HistoryView fetchSeam={seam} /></RoleProvider>);
  await screen.findByTestId(testid);
  const html = document.body.innerHTML;
  cleanup();
  return html;
}

describe('HistoryView — VIEWONLY-1: render identical across ALL roles incl. null', () => {
  it('underwriter / auditor / admin / null produce identical LIST output', async () => {
    const underwriter = await htmlForRole('underwriter', 'history-list');
    expect(await htmlForRole('auditor', 'history-list')).toBe(underwriter);
    expect(await htmlForRole('admin', 'history-list')).toBe(underwriter);   // admin NOT excluded
    expect(await htmlForRole(null, 'history-list')).toBe(underwriter);
  });

  it('underwriter / auditor / admin / null produce identical DETAIL output', async () => {
    async function detailHtmlForRole(role) {
      const seam = makeHistoryDouble({
        list: [{ resolve: makeListBody() }],
        detail: [{ resolve: approveRecord }],
      });
      render(<RoleProvider value={role}><HistoryView fetchSeam={seam} /></RoleProvider>);
      await screen.findByTestId('history-list');
      fireEvent.click(screen.getByTestId('history-row-select-dec-21'));
      await screen.findByTestId('history-detail');
      const html = document.body.innerHTML;
      cleanup();
      return html;
    }
    const underwriter = await detailHtmlForRole('underwriter');
    expect(await detailHtmlForRole('auditor')).toBe(underwriter);
    expect(await detailHtmlForRole('admin')).toBe(underwriter);
    expect(await detailHtmlForRole(null)).toBe(underwriter);
  });

  it('no act-affordance exists for any role — the detail is read-only', async () => {
    await htmlForRole('underwriter', 'history-list');
    const seam = makeHistoryDouble({
      list: [{ resolve: makeListBody() }],
      detail: [{ resolve: approveRecord }],
    });
    render(<RoleProvider value="underwriter"><HistoryView fetchSeam={seam} /></RoleProvider>);
    await screen.findByTestId('history-list');
    fireEvent.click(screen.getByTestId('history-row-select-dec-21'));
    await screen.findByTestId('history-detail');

    // no input, no textarea, no form anywhere — the only controls are read-navigation.
    expect(document.querySelectorAll('input, textarea, form, select')).toHaveLength(0);
    const buttons = [...document.querySelectorAll('button')].map((b) => b.dataset.testid);
    expect(buttons).toEqual(['history-detail-ruleresults-toggle', 'history-detail-back']);
  });
});
