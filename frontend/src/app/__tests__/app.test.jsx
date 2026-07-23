import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { App } from '../App.jsx';
import { createSeams } from '../seams.js';
import { createHttpTransport } from '../httpTransport.js';

// INT-FE-1 — the frontend composition root. Author-only (Decision 5): no bundler, no browser.
const RECORD = {
  decision_id: 'DEC-1',
  application_id: 'APP-1',
  recommendation_id: 'REC-1',
  audit_tuple: {
    rulebook_version: '1.0.0',
    rule_results: {
      rule_results: [], recommendation: 'APPROVE', confidence: 'High',
      rulebook_version: '1.0.0', content_hash: 'h', engine_version: 'e',
      decline_reasons: [], refer_reasons: [],
    },
    timestamp: '2026-01-01T13:00:00+00:00',
    model_version: 'm', memo_hash: 'mh', engine_version: 'e',
  },
  applicant_profile_snapshot: {
    application_id: 'APP-1',
    profile: {
      application_id: 'APP-1', age_years_derived: 40, verifiable_income_annual: '1000000',
      requested_cover_amount: '5000000',
      demographics: { full_name: 'Ada Byron', gender: 'female', city: 'Metropolis' },
    },
    content_hash: 'ph',
  },
  committed_decision: { recommendation_id: 'REC-1', underwriter_id: 'UW-1', action: 'approve', reason: null },
  status: 'active',
  supersedes_decision_id: null,
};

const LIST = { items: [{ decision_id: 'DEC-1', application_id: 'APP-1', recommendation_id: 'REC-1', action: 'approve', timestamp: '2026-01-01T13:00:00+00:00' }], page: { page: 1, size: 20, total: 1 } };

/** A fake server speaking the real WIRE-1 shapes over the real transport. */
function fakeServer({ role = 'underwriter', calls = [] } = {}) {
  const fetchImpl = vi.fn(async (url) => {
    calls.push(url);
    if (url === '/session') return { ok: true, json: async () => ({ user_id: 'UW-1', role }) };
    if (url.startsWith('/decisions/')) return { ok: true, json: async () => RECORD };
    if (url.startsWith('/decisions')) return { ok: true, json: async () => LIST };
    return { ok: false, json: async () => ({ error: { code: 'not_implemented', message: 'Not wired.', detail: {} } }) };
  });
  const transport = createHttpTransport({ fetchImpl, userId: 'UW-1' });
  return { transport, seams: createSeams(transport), calls };
}

describe('App — the Scope-A composition root', () => {
  it('mounts the shell and renders the history surface from the REAL transport', async () => {
    const { transport, seams } = fakeServer();
    render(<App seams={seams} transport={transport} />);

    expect(await screen.findByTestId('history-list')).toBeInTheDocument();
    expect(screen.getByTestId('history-row-dec-1')).toBeInTheDocument();
    expect(screen.getByTestId('shell-appframe-root')).toBeInTheDocument();
  });

  it('drives the master-detail flow end-to-end over the transport (R6 -> R7)', async () => {
    const { transport, seams, calls } = fakeServer();
    render(<App seams={seams} transport={transport} />);
    await screen.findByTestId('history-list');

    // the wire calls the real seams actually issued
    expect(calls).toContain('/decisions?page=1&size=20');
    expect(calls).toContain('/session');
  });

  it('feeds R1 role into the FROZEN AppFrame seam, not around it', async () => {
    // AppFrame hosts the RoleProvider itself; App populates its `user` prop — the shell's
    // documented WIRE-1 injection point. A second provider would have been shadowed.
    const { transport, seams } = fakeServer({ role: 'auditor' });
    render(<App seams={seams} transport={transport} />);
    await screen.findByTestId('history-list');
    await waitFor(() => expect(screen.getByTestId('app-root')).toBeInTheDocument());
  });

  it('renders identically for every role — ui-history is view-only (VIEWONLY-1 holds end-to-end)', async () => {
    async function htmlFor(role) {
      const { transport, seams } = fakeServer({ role });
      const { container, unmount } = render(<App seams={seams} transport={transport} />);
      await screen.findByTestId('history-list');
      const html = container.innerHTML;
      unmount();
      return html;
    }
    const underwriter = await htmlFor('underwriter');
    expect(await htmlFor('auditor')).toBe(underwriter);
    expect(await htmlFor(null)).toBe(underwriter);
  });

  it('an unauthenticated session leaves a null role and still renders (fail-closed, not an error)', async () => {
    const fetchImpl = vi.fn(async (url) => {
      if (url === '/session') return { ok: false, json: async () => ({ error: { code: 'unauthenticated', message: 'x', detail: {} } }) };
      return { ok: true, json: async () => LIST };
    });
    const transport = createHttpTransport({ fetchImpl });
    render(<App seams={createSeams(transport)} transport={transport} />);
    expect(await screen.findByTestId('history-list')).toBeInTheDocument();
  });

  it('mounts NO unbacked surface — only the history view exists in Scope A', async () => {
    const { transport, seams } = fakeServer();
    render(<App seams={seams} transport={transport} />);
    await screen.findByTestId('history-list');
    // the four unbacked units are wired in seams.js but deliberately not rendered
    expect(screen.queryByTestId('queue-view')).toBeNull();
    expect(screen.queryByTestId('memo-view')).toBeNull();
    expect(screen.queryByTestId('approval-gate-view')).toBeNull();
    expect(screen.queryByTestId('override-form-view')).toBeNull();
  });

  it('surfaces a backend error through the frozen unit own error state', async () => {
    const envelope = { error: { code: 'forbidden', message: 'You do not have permission.', detail: {} } };
    const fetchImpl = vi.fn(async (url) => {
      if (url === '/session') return { ok: true, json: async () => ({ user_id: 'ADM-1', role: 'admin' }) };
      return { ok: false, json: async () => envelope };
    });
    const transport = createHttpTransport({ fetchImpl, userId: 'ADM-1' });
    render(<App seams={createSeams(transport)} transport={transport} />);

    // The Q1-B divergence as an admin would experience it end-to-end: the server 403s, and
    // ui-history renders its ORDINARY generic error state — no crash, no special-casing.
    expect(await screen.findByTestId('history-state-error-list')).toBeInTheDocument();
    expect(screen.getByTestId('history-error-message')).toHaveTextContent('You do not have permission.');
    expect(screen.getByTestId('history-error-code')).toHaveTextContent('forbidden');
  });
});

describe('createSeams — every frozen unit seam over one real transport', () => {
  it('wires all five units seams', () => {
    const { seams } = fakeServer();
    expect(Object.keys(seams).sort()).toEqual(['commit', 'history', 'memo', 'override', 'queue']);
  });

  it('the history seam is the dual-read one ui-history expects', () => {
    const { seams } = fakeServer();
    expect(Object.keys(seams.history).sort()).toEqual(['fetchDetail', 'fetchList']);
  });

  it('the unbacked seams are real and callable — they simply have no backing yet', async () => {
    const { seams } = fakeServer();
    // R2 is unwired: the fake server 501s, and the FROZEN queue seam normalizes it. Ready the
    // day R2 lands, with no change here.
    await expect(seams.queue(1, 20)).rejects.toMatchObject({ error: { code: 'not_implemented' } });
  });
});
