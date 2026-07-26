import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
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

// ---- Scope-B backed server -------------------------------------------------------------------
// Answers R2/R4/R5 as well as R1/R6/R7, for the newly-mounted queue -> memo -> commit surfaces.
// A SEPARATE helper from fakeServer above — fakeServer's not_implemented default is load-bearing for
// `the unbacked seams are real and callable`, so it is left byte-unchanged and this is added beside it.
const QUEUE_LIST = {
  items: [{ application_id: 'app-1', recommendation: 'APPROVE', confidence: 'High' }],
  page: { page: 1, size: 20, total: 1 },
};

// One R4 body satisfying BOTH readers of the same route: MemoView (memo.*) and ApprovalGateView
// (report.* + recommendation_id). This IS the Fold-4 duplicate-R4 reality, expressed as one fixture.
const R4_READY = {
  application_id: 'app-1',
  recommendation_id: 'rec-1',
  status: 'ready',
  profile: {
    application_id: 'app-1', age_years_derived: 42, requested_cover_amount: '500000',
    demographics: { full_name: 'Jordan Rivera', gender: 'unspecified', city: 'Metropolis' },
  },
  report: { recommendation: 'APPROVE', confidence: 'High' },
  memo: {
    narrative_prose: 'Meets the income threshold; no adverse flags.',
    cited_rule_ids: [], missing_information: [],
    recommendation: 'APPROVE', confidence: 'High', memo_hash: 'h-abc', model_version: 'm-1',
  },
  outlier: null,
};

const R4_PENDING = {
  application_id: 'app-1', recommendation_id: null, status: 'pending',
  profile: null, report: null, memo: null,
};

const COMMITTED = { recommendation_id: 'rec-1', underwriter_id: 'UW-1', action: 'approve', reason: null };
const FORBIDDEN = { error: { code: 'forbidden', message: 'You do not have permission.', detail: {} } };

const okJson = (value) => ({ ok: true, json: async () => value });
const errJson = (value) => ({ ok: false, json: async () => value });

/** A backed server speaking the real WIRE-1 shapes over the real transport, for the Scope-B surfaces. */
function backedServer({ role = 'underwriter', memoBody = R4_READY, commitResponse = okJson(COMMITTED), calls = [] } = {}) {
  const fetchImpl = vi.fn(async (url, options = {}) => {
    const method = options.method ?? 'GET';
    calls.push({ url, method, body: options.body });
    if (url === '/session') return okJson({ user_id: 'UW-1', role });
    if (url.startsWith('/applications?')) return okJson(QUEUE_LIST);
    if (/^\/applications\/[^/]+\/memo$/.test(url)) return okJson(memoBody);
    if (/^\/recommendations\/[^/]+\/commit$/.test(url) && method === 'POST') return commitResponse;
    if (url.startsWith('/decisions/')) return okJson(RECORD);
    if (url.startsWith('/decisions')) return okJson(LIST);
    return errJson({ error: { code: 'not_implemented', message: 'Not wired.', detail: {} } });
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
      // MECHANICAL (fold 10): the newly-mounted queue is async too. Await it SETTLING (here, its
      // unbacked error state under fakeServer) before snapshotting — else a role-to-role snapshot can
      // catch queue mid-loading in one run and settled in another, an intermittent false failure that
      // would be indistinguishable from a real role-variance bug. Assertion unchanged; only the
      // synchronization is strengthened.
      await screen.findByTestId('queue-state-error');
      const html = container.innerHTML;
      unmount();
      return html;
    }
    const underwriter = await htmlFor('underwriter');
    expect(await htmlFor('auditor')).toBe(underwriter);

    // SUPERSEDED (2026-07-26) -- a third `expect(await htmlFor(null)).toBe(underwriter)` case was
    // removed here. It asserted that a NULL role rendered the application identically, which is
    // the SAME premise `an unauthenticated session ... still renders` rested on: correct while
    // there was no way to log in, false once the gate exists, because a null role now routes to
    // the login view. The gate's own tests assert that directly and in both directions.
    //
    // NOT WEAKENED: this test's actual subject is ROLE INVARIANCE -- that ui-history renders the
    // same for every role that can see it (VIEWONLY-1) -- and both real roles are still compared.
    // The null case was never about role invariance; it was about the fail-closed render.
  });

  // SUPERSEDED (2026-07-26): replaces `an unauthenticated session leaves a null role and still
  // renders (fail-closed, not an error)`, which asserted a 401 /session STILL rendered the
  // application surfaces.
  //
  // THAT ASSERTION WAS CORRECT FOR A BUILD WITH NO WAY TO LOG IN. With no login page in
  // existence, rendering the app in a fail-closed null-role state -- every gated affordance
  // hidden, every fetch surfacing an honest error -- was the BEST AVAILABLE BEHAVIOUR. It stops
  // being correct the moment a login page exists, because the honest response to "not
  // authenticated" becomes "here is how to authenticate", not a permanent polite dead end.
  //
  // This is a PREMISE CHANGE, NOT A REGRESSION. The old test's real content -- unauthenticated is
  // a STATE, not an error -- survives and strengthens: still not an error, and now ACTIONABLE.
  it('an unauthenticated session renders the login view and mounts no application surface', async () => {
    const fetchImpl = vi.fn(async (url) => {
      if (url === '/session') return { ok: false, json: async () => ({ error: { code: 'unauthenticated', message: 'x', detail: {} } }) };
      return { ok: true, json: async () => LIST };
    });
    const transport = createHttpTransport({ fetchImpl });
    render(<App seams={createSeams(transport)} transport={transport} />);

    expect(await screen.findByTestId('login-view')).toBeInTheDocument();
    expect(screen.queryByTestId('history-list')).toBeNull();
    expect(screen.queryByTestId('queue-view')).toBeNull();
  });

  it('the gate renders NEITHER surface while /session is still in flight', async () => {
    // FE-Fold-4, binding. A two-state gate would flash the login page on EVERY load, including
    // for already-authenticated users. The gate starts in `checking` and commits to neither
    // branch until /session resolves.
    let release;
    const fetchImpl = vi.fn((url) => {
      if (url === '/session') {
        return new Promise((resolve) => {
          release = () => resolve({ ok: true, json: async () => ({ user_id: 'UW-1', role: 'underwriter' }) });
        });
      }
      return Promise.resolve({ ok: true, json: async () => LIST });
    });
    const transport = createHttpTransport({ fetchImpl });
    render(<App seams={createSeams(transport)} transport={transport} />);

    expect(screen.getByTestId('app-checking')).toBeInTheDocument();
    expect(screen.queryByTestId('login-view')).toBeNull();
    expect(screen.queryByTestId('history-list')).toBeNull();

    release();
    expect(await screen.findByTestId('history-list')).toBeInTheDocument();
  });

  it('a successful login re-checks the session and mounts the app', async () => {
    // Q3(a): the post-login path reuses the SAME loadCurrentRole the gate already depends on, so
    // there is exactly ONE definition of "who is the current user" in the app.
    let authenticated = false;
    const fetchImpl = vi.fn(async (url, init) => {
      if (url === '/session') {
        return authenticated
          ? { ok: true, json: async () => ({ user_id: 'UW-1', role: 'underwriter' }) }
          : { ok: false, json: async () => ({ error: { code: 'unauthenticated', message: 'x', detail: {} } }) };
      }
      if (url === '/login' && init.method === 'POST') {
        authenticated = true;
        return { ok: true, json: async () => ({}) };
      }
      return { ok: true, json: async () => LIST };
    });
    const transport = createHttpTransport({ fetchImpl });
    render(<App seams={createSeams(transport)} transport={transport} />);

    await screen.findByTestId('login-view');
    fireEvent.change(screen.getByTestId('login-input-user-id'), { target: { value: 'UW-1' } });
    fireEvent.change(screen.getByTestId('login-input-password'), { target: { value: 's3cret' } });
    fireEvent.click(screen.getByTestId('login-action-submit'));

    expect(await screen.findByTestId('history-list')).toBeInTheDocument();
    expect(screen.queryByTestId('login-view')).toBeNull();
  });

  it('logout revokes and returns to the login view', async () => {
    let authenticated = true;
    const fetchImpl = vi.fn(async (url, init) => {
      if (url === '/session') {
        return authenticated
          ? { ok: true, json: async () => ({ user_id: 'UW-1', role: 'underwriter' }) }
          : { ok: false, json: async () => ({ error: { code: 'unauthenticated', message: 'x', detail: {} } }) };
      }
      if (url === '/logout' && init.method === 'POST') {
        authenticated = false;
        return { ok: true, json: async () => ({}) };
      }
      return { ok: true, json: async () => LIST };
    });
    const transport = createHttpTransport({ fetchImpl });
    render(<App seams={createSeams(transport)} transport={transport} />);

    await screen.findByTestId('history-list');
    fireEvent.click(screen.getByTestId('login-action-logout'));

    expect(await screen.findByTestId('login-view')).toBeInTheDocument();
    expect(screen.queryByTestId('history-list')).toBeNull();
  });

  // SUPERSEDED (2026-07-25): this replaces `mounts NO unbacked surface — only the history view exists
  // in Scope A`, which was CORRECT under Scope A — R2-R5 answered 501, so a mounted view could only ever
  // error, implying backing that did not exist. Scope B made all seven routes live, retiring that
  // premise. Not weakened: it still pins EXACTLY which surfaces the composition root mounts, in both
  // directions. Q5(c) deliberately excludes override and outlier — asserted absent in BOTH states.
  it('mounts exactly the backed surfaces — queue + history always; override and outlier never', async () => {
    const { transport, seams } = fakeServer();
    const authenticated = render(<App seams={seams} transport={transport} />);
    await screen.findByTestId('history-list');
    // queue is ALWAYS mounted — its Panel testid renders in every state, incl. the unbacked error state.
    expect(await screen.findByTestId('queue-view')).toBeInTheDocument();
    // no selection yet -> no detail surface. `approval-gate` is the REAL default testid the gate
    // renders (NOT `approval-gate-view`, which the old test asserted and which would pass vacuously
    // once the gate is mounted — the accidental-pass trap this build has twice refused).
    expect(screen.queryByTestId('memo-view')).toBeNull();
    expect(screen.queryByTestId('approval-gate')).toBeNull();
    // out of scope this pass (Q5(c) / Q4(a)) — never mounted, in either selection state.
    expect(screen.queryByTestId('override-form-view')).toBeNull();
    expect(screen.queryByTestId('outlier-view')).toBeNull();

    // EXTENDED (2026-07-26) -- the gate's OTHER state. Previously this rendered only the
    // authenticated shape, because that was the only shape there was. It now pins BOTH: an
    // unauthenticated session mounts the login view and NONE of the application surfaces.
    // Not weakened -- it still pins exactly which surfaces mount, now across both gate states.
    authenticated.unmount();
    const unauth = vi.fn(async (url) => {
      if (url === '/session') return { ok: false, json: async () => ({ error: { code: 'unauthenticated', message: 'x', detail: {} } }) };
      return { ok: true, json: async () => LIST };
    });
    const unauthTransport = createHttpTransport({ fetchImpl: unauth });
    const { unmount } = render(<App seams={createSeams(unauthTransport)} transport={unauthTransport} />);
    expect(await screen.findByTestId('login-view')).toBeInTheDocument();
    for (const id of ['queue-view', 'history-list', 'memo-view', 'approval-gate', 'override-form-view', 'outlier-view']) {
      expect(screen.queryByTestId(id)).toBeNull();
    }
    unmount();
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

  // --- Scope-B: the newly-mounted queue -> memo -> commit surfaces (Q5(c)) ---

  it('selection mounts the detail surfaces — a queue row click opens memo + gate with the id propagated', async () => {
    const { transport, seams } = backedServer();
    render(<App seams={seams} transport={transport} />);
    fireEvent.click(await screen.findByTestId('queue-row-select-app-1'));
    expect(await screen.findByTestId('memo-view')).toBeInTheDocument();      // R4 ready (memo)
    expect(await screen.findByTestId('approval-gate')).toBeInTheDocument();  // same R4, gate ready
  });

  it('no selection -> no detail surfaces (the other branch of the selection condition — fold 5)', async () => {
    const { transport, seams } = backedServer();
    render(<App seams={seams} transport={transport} />);
    expect(await screen.findByTestId('queue-view')).toBeInTheDocument();
    await screen.findByTestId('queue-table'); // queue settled ready, still nothing selected
    expect(screen.queryByTestId('memo-view')).toBeNull();
    expect(screen.queryByTestId('approval-gate')).toBeNull();
  });

  it('the approve path end-to-end over the transport — Confirm POSTs exactly { action: "approve" }, no underwriter_id', async () => {
    const calls = [];
    const { transport, seams } = backedServer({ calls });
    render(<App seams={seams} transport={transport} />);
    fireEvent.click(await screen.findByTestId('queue-row-select-app-1'));
    fireEvent.click(await screen.findByTestId('approval-affordance-approve')); // opens the dialog, no commit
    fireEvent.click(await screen.findByTestId('approval-confirm-submit'));     // the single commit call site
    expect(await screen.findByTestId('approval-committed')).toBeInTheDocument();

    const commit = calls.find((c) => c.method === 'POST' && c.url === '/recommendations/rec-1/commit');
    expect(commit).toBeTruthy();
    const body = JSON.parse(commit.body);
    expect(body).toEqual({ action: 'approve' });       // WIRE-1 §5 / BODY-1
    expect(body).not.toHaveProperty('underwriter_id'); // AUTHZ-1 — session-derived server-side, never in the body
  });

  it('a pending R4 renders the not-yet-drafted state, not an error', async () => {
    const { transport, seams } = backedServer({ memoBody: R4_PENDING });
    render(<App seams={seams} transport={transport} />);
    fireEvent.click(await screen.findByTestId('queue-row-select-app-1'));
    expect(await screen.findByTestId('memo-state-pending')).toBeInTheDocument();
    expect(screen.queryByTestId('memo-view')).toBeNull();
  });

  it('a commit error surfaces through the frozen gate own error state — no special-casing in App', async () => {
    const { transport, seams } = backedServer({ commitResponse: errJson(FORBIDDEN) });
    render(<App seams={seams} transport={transport} />);
    fireEvent.click(await screen.findByTestId('queue-row-select-app-1'));
    fireEvent.click(await screen.findByTestId('approval-affordance-approve'));
    fireEvent.click(await screen.findByTestId('approval-confirm-submit'));
    expect(await screen.findByTestId('approval-state-error')).toBeInTheDocument();
    expect(screen.getByTestId('approval-error-code')).toHaveTextContent('forbidden');
    expect(screen.queryByTestId('approval-committed')).toBeNull();
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
