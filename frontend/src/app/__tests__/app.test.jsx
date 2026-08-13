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

// A `ready` R4 body CARRYING real outlier data — the Phase-2-OUT slice the outlier-wiring pass made
// servable. ⚑ R4_READY above keeps `outlier: null` deliberately and is NOT edited: that is the shape
// 12 of the 13 rows in the real database produce, so it stays the default and the scored case is the
// special fixture. Values mirror the live verification (`outlier_score=0.567032896281`, two flags,
// full provenance) rather than being invented.
const R4_READY_OUTLIER = {
  ...R4_READY,
  outlier: {
    outlier_score: 0.567032896281,
    is_outlier: true,
    flagged_features: [
      { feature: 'requested_cover_amount', z_score: 2.41, shap_value: 0.18, direction: 'high' },
      { feature: 'verifiable_income_annual', z_score: -1.97, shap_value: 0.11, direction: 'low' },
    ],
    provenance: { corpus_version: '1.0.0', seed: 42, outlier_model_version: 'om-1' },
  },
};

const COMMITTED = { recommendation_id: 'rec-1', underwriter_id: 'UW-1', action: 'approve', reason: null };
const FORBIDDEN = { error: { code: 'forbidden', message: 'You do not have permission.', detail: {} } };

// The R5 echo for an OVERRIDE — `reason` non-null, which no approve commit ever carries. The
// confirmation renders the reason from THIS echo, never from the client's own slice (ND-OVR-Fold-ii).
const OVERRIDE_REASON = 'Compensating factors the rulebook does not capture.';
const COMMITTED_OVERRIDE = {
  recommendation_id: 'rec-1', underwriter_id: 'UW-1', action: 'override', reason: OVERRIDE_REASON,
};
// WIRE-1 §4's already-committed conflict — what register #19's claim returns to the loser.
const CONFLICT = {
  error: { code: 'commit_conflict', message: 'This recommendation has already been committed.', detail: {} },
};

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
    // `commitResponse` may be a VALUE (every pre-existing caller) or a FUNCTION resolved per call.
    // The function form exists for the double-commit collision test, where the same URL must answer
    // 200 once and 409 thereafter — modelling register #19's claim. Strictly additive: an object
    // behaves exactly as before, so no existing caller changes.
    if (/^\/recommendations\/[^/]+\/commit$/.test(url) && method === 'POST') {
      return typeof commitResponse === 'function' ? commitResponse() : commitResponse;
    }
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

  it('login -> logout -> login AGAIN works, and the app actually mounts the second time', async () => {
    // ⚑ THE REGRESSION TEST for the defect manual verification found (2026-07-26). The suite had
    // no logout-then-relogin sequence at all, and every /login fake resolved `json()` -- which a
    // real 204 never does. So the second login reported "Unable to reach the server." while the
    // backend had logged 204: a login that SUCCEEDED server-side, discarded by the client.
    //
    // ⚑ This fake models a REAL 204: ok, status 204, and json() REJECTING on the empty body.
    // Asserting no-error-thrown would not be enough -- what broke was that the app never MOUNTED,
    // so this asserts the surfaces are actually present after the second login.
    let authenticated = false;
    const noContent = { ok: true, status: 204, json: async () => { throw new SyntaxError('Unexpected end of JSON input'); } };
    const fetchImpl = vi.fn(async (url, init) => {
      if (url === '/session') {
        return authenticated
          ? { ok: true, status: 200, json: async () => ({ user_id: 'UW-1', role: 'underwriter' }) }
          : { ok: false, status: 401, json: async () => ({ error: { code: 'unauthenticated', message: 'x', detail: {} } }) };
      }
      if (url === '/login' && init.method === 'POST') { authenticated = true; return noContent; }
      if (url === '/logout' && init.method === 'POST') { authenticated = false; return noContent; }
      return { ok: true, status: 200, json: async () => LIST };
    });
    const transport = createHttpTransport({ fetchImpl });
    render(<App seams={createSeams(transport)} transport={transport} />);

    async function signIn() {
      await screen.findByTestId('login-view');
      fireEvent.change(screen.getByTestId('login-input-user-id'), { target: { value: 'UW-1' } });
      fireEvent.change(screen.getByTestId('login-input-password'), { target: { value: 's3cret' } });
      fireEvent.click(screen.getByTestId('login-action-submit'));
    }

    // 1st login -> the app mounts
    await signIn();
    expect(await screen.findByTestId('history-list')).toBeInTheDocument();

    // logout -> back to the login view
    fireEvent.click(screen.getByTestId('login-action-logout'));
    await screen.findByTestId('login-view');

    // 2nd login -> THE SEQUENCE THAT BROKE. The app must mount again, and no error may show.
    await signIn();
    expect(await screen.findByTestId('history-list')).toBeInTheDocument();
    expect(screen.queryByTestId('login-view')).toBeNull();
    expect(screen.queryByTestId('login-state-error')).toBeNull();
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
  // directions.
  //
  // ⚑ RATIONALE AMENDED (2026-07-26), assertions BYTE-UNCHANGED. The sentence that stood here read
  // "Q5(c) deliberately excludes override and outlier — asserted absent in BOTH states". That is NO
  // LONGER TRUE of override, which is now mounted on selection. Both assertions below are still
  // correct — but for reasons that must be stated, or they would be misread as continuing to pin an
  // exclusion that no longer exists:
  //   * the first block never SELECTS a case, and override mounts only inside the selection branch
  //     (as memo and the gate do) — so its absence here is the NO-SELECTION fact, not an exclusion;
  //   * the second block is UNAUTHENTICATED, where no application surface mounts at all.
  // Override's mounted state is pinned POSITIVELY by `selection mounts the override form` above.
  //
  // ⛔ SUPERSEDED 2026-08-13 (outlier mount). The sentence here read: "OUTLIER remains genuinely
  // excluded (#17) and its absence here still asserts exactly that." ⚑ THAT IS NOW FALSE IN ITS
  // REASON THOUGH NOT IN ITS RESULT — outlier IS mounted, in the selection branch, exactly as memo,
  // the gate and override are. Its absence below is therefore the NO-SELECTION fact, identical to
  // override's, and NOT an exclusion. The assertion is BYTE-UNCHANGED and still correct; only the
  // reason changed, which is precisely why the comment could not be left alone: a file that asserts
  // a retired premise is worse than one that asserts nothing. Outlier's mounted state is pinned
  // POSITIVELY by `selection mounts the outlier view` above.
  //
  // ⚑ RENAMED (2026-07-26, authorized separately after the override pass). The previous name was:
  //     'mounts exactly the backed surfaces — queue + history always; override and outlier never'
  // ⚑ RENAMED AGAIN (2026-08-13, GATE G1 of the outlier mount plan, authorized explicitly in
  // writing rather than folded into the mount). The name immediately before this one was:
  //     'mounts exactly the backed surfaces — queue + history always; outlier never; detail surfaces only on selection'
  // ⛔ "outlier never" became FALSE the moment outlier was mounted — the SAME staleness override's
  // clause suffered one pass earlier, in this same name. The clause is DELETED rather than replaced:
  // "detail surfaces only on selection" already covers every per-application surface, and
  // enumerating one of four is what made this name go stale twice. ⚑ The shorter name is the one
  // that cannot go stale again.
  // ⛔ The trailing "override ... never" became FALSE the moment override was mounted: it mounts on
  // selection, exactly as memo and the gate do. The name was left stale for one pass because the
  // authorizing answer (Q4(a)) covered the comment only — the imprecision was recorded in this file
  // rather than silently fixed, then renamed once explicitly authorized.
  // ⚑ NAME ONLY. Every assertion below is byte-unchanged, and the test's subject is unchanged: it
  // still pins EXACTLY which surfaces the composition root mounts, in both gate states. This is the
  // #13 `NOTWIRED-FILENAME-STALE` shape — a name that outlived the thing it described — handled the
  // way this project has handled every other one: superseded in place, with the old name preserved.
  it('mounts exactly the backed surfaces — queue + history always; detail surfaces only on selection', async () => {
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
    // override AND outlier: both absent because nothing is SELECTED here — both mount in the
    // selection branch, and both are pinned positively above. ⚑ Neither line asserts an exclusion
    // any more; as of 2026-08-13 there is no unmounted unit left in this build.
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

  it('selection mounts the override form — the mandatory-reason path is reachable', async () => {
    // ⚑ Asserts `override-form-view`, NOT `override-form-panel`. OverrideFormView renders the Panel
    // in EVERY phase but the inner view testid ONLY in ready/confirming/submitting
    // (OverrideFormView.jsx:79-98) — so an assertion against the panel would pass even from
    // `pending`, i.e. for the wrong reason. R4_READY drives it to `ready`, the state the override
    // path is actually reachable from. This is the third instance of the accidental-pass trap this
    // file already refused twice (see the approval-gate / approval-gate-view note above).
    const { transport, seams } = backedServer();
    render(<App seams={seams} transport={transport} />);
    fireEvent.click(await screen.findByTestId('queue-row-select-app-1'));
    expect(await screen.findByTestId('override-form-view')).toBeInTheDocument();
  });

  it('selection mounts the outlier view — the advisory statistical panel is reachable', async () => {
    // ⛔ THE MOUNT ITSELF (#17's frontend half). Asserts `outlier-view`, NOT the panel heading —
    // `OutlierView` renders its `Panel` in EVERY state (loading / not-available / error), but the
    // inner `outlier-view` testid ONLY on the READY branch inside `ReadOnlyRegion`
    // (OutlierView.jsx:88-93). An assertion against the panel would therefore pass from
    // NOT_AVAILABLE — i.e. for the wrong reason, and against the very body 12 of 13 real rows
    // produce. This is the FOURTH instance of the accidental-pass trap this file has refused.
    const { transport, seams } = backedServer({ memoBody: R4_READY_OUTLIER });
    render(<App seams={seams} transport={transport} />);
    fireEvent.click(await screen.findByTestId('queue-row-select-app-1'));
    expect(await screen.findByTestId('outlier-view')).toBeInTheDocument();
    // ...and it is rendering the REAL numbers off the wire, not chrome that happens to mount.
    expect(screen.getByTestId('outlier-score')).toHaveTextContent('0.567032896281');
  });

  it('the outlier seam is the REAL R4 seam, not a placeholder', async () => {
    // ⚑ THE NON-VACUITY PARTNER of the mount assertion above. A seam registered as a stub — or one
    // bound to the wrong route — would still let `outlier-view` mount from a fixture; only calling
    // it proves `createSeams` wired the real transport to R4. Mirrors `the unbacked seams are real
    // and callable`, which pinned the same property when these seams answered 501.
    const { seams, calls } = backedServer({ memoBody: R4_READY_OUTLIER });
    expect(typeof seams.outlier).toBe('function');
    const body = await seams.outlier('app-1');
    expect(body.outlier.outlier_score).toBe(0.567032896281);
    expect(calls.some((c) => c.url === '/applications/app-1/memo' && c.method === 'GET')).toBe(true);
  });

  it('⛔ a selected case with NO outlier data renders NOT_AVAILABLE, never the ERROR state', async () => {
    // ⛔ THE CASE 12 OF 13 REAL ROWS PRODUCE, and the most likely way this mount goes wrong. A
    // `pending` body and a `ready` body carrying `outlier: null` BOTH mean "not analyzed" — not
    // "failed to load". `deriveOutlierState` is failure-first precisely so NOT_AVAILABLE can never
    // mask a genuine error; this asserts the other direction, which nothing else does: that an
    // absent score is not dressed up AS an error. Getting it backwards is invisible to anyone who
    // only exercises the scored case.
    const { transport, seams } = backedServer();   // R4_READY -> outlier: null
    render(<App seams={seams} transport={transport} />);
    fireEvent.click(await screen.findByTestId('queue-row-select-app-1'));
    expect(await screen.findByTestId('outlier-state-notavailable')).toBeInTheDocument();
    expect(screen.queryByTestId('outlier-state-error')).toBeNull();
    // ⚑ The retry affordance belongs to the ERROR state alone. Its presence here would mean the
    // user was being invited to retry something that did not fail.
    expect(screen.queryByTestId('outlier-error-retry')).toBeNull();
    // ...and the READY surface is genuinely absent, not merely empty.
    expect(screen.queryByTestId('outlier-view')).toBeNull();
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

  it('the override path end-to-end over the transport — Confirm POSTs exactly { action: "override", reason }, no underwriter_id', async () => {
    const calls = [];
    const { transport, seams } = backedServer({ calls, commitResponse: okJson(COMMITTED_OVERRIDE) });
    render(<App seams={seams} transport={transport} />);
    fireEvent.click(await screen.findByTestId('queue-row-select-app-1'));
    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: OVERRIDE_REASON } });
    fireEvent.click(await screen.findByTestId('override-affordance-button')); // opens the dialog, no commit
    fireEvent.click(await screen.findByTestId('override-confirm-submit'));    // the single commit call site
    expect(await screen.findByTestId('override-committed-view')).toBeInTheDocument();

    const commit = calls.find((c) => c.method === 'POST' && c.url === '/recommendations/rec-1/commit');
    expect(commit).toBeTruthy();
    const body = JSON.parse(commit.body);
    // WIRE-1 §5 / BODY-1 — EXACTLY these two keys. The reason is sent AS-ENTERED (no client trim).
    expect(body).toEqual({ action: 'override', reason: OVERRIDE_REASON });
    expect(body).not.toHaveProperty('underwriter_id'); // AUTHZ-1 — session-derived server-side
    // the committed reason is rendered from the R5 ECHO, not the client's slice (ND-OVR-Fold-ii)
    expect(screen.getByTestId('override-committed-reason')).toHaveTextContent(OVERRIDE_REASON);
  });

  it('a blank reason cannot be submitted — the affordance stays disabled and NO commit is issued', async () => {
    // ⚑ The 409 blank-reason path is UNREACHABLE from this UI by construction: the affordance is
    // disabled by the single isReasonPresent predicate, so no request can be issued. That is why
    // BR-COMMIT-GATE's server-side rejection is verified by bypassing the UI against a live
    // database, NOT here — two tiers, two claims, neither standing in for the other.
    const calls = [];
    const { transport, seams } = backedServer({ calls });
    render(<App seams={seams} transport={transport} />);
    fireEvent.click(await screen.findByTestId('queue-row-select-app-1'));
    await screen.findByTestId('override-form-view');
    expect(screen.getByTestId('override-affordance-button')).toBeDisabled();
    // whitespace-only is still blank under the trim()-based UX guard
    fireEvent.change(screen.getByTestId('override-reason-input'), { target: { value: '   ' } });
    expect(screen.getByTestId('override-affordance-button')).toBeDisabled();
    expect(calls.some((c) => c.method === 'POST')).toBe(false);
    // a real reason enables it — proving the disabled state tracks the reason, not something else
    fireEvent.change(screen.getByTestId('override-reason-input'), { target: { value: 'x' } });
    expect(screen.getByTestId('override-affordance-button')).toBeEnabled();
  });

  it('approve then override — the second commit loses the claim and renders commit_conflict', async () => {
    // ⚑ Q3(a)'s accepted consequence, pinned. Both affordances target the SAME recommendation, so the
    // first confirmed commit wins register #19's claim and the second gets 409.
    // ⚑ WHAT THIS DOES AND DOES NOT PROVE: it pins the OBSERVABLE CONTRACT of that guard — a second
    // commit returns 409 and the losing unit renders its ordinary error state. It does NOT test the
    // compare-and-swap itself, which is a Postgres row-lock property a fake cannot reach; this test
    // would pass against a backend with no CAS at all. The CAS is verified against a real database.
    // ⚑ NOT a race: the fake is a plain function and the await below sequences the two commits.
    let commits = 0;
    const commitResponse = () => {
      commits += 1;
      return commits === 1 ? okJson(COMMITTED) : errJson(CONFLICT);
    };
    const { transport, seams } = backedServer({ commitResponse });
    render(<App seams={seams} transport={transport} />);
    fireEvent.click(await screen.findByTestId('queue-row-select-app-1'));
    // the reason is typed FIRST — the override affordance is disabled until it exists
    fireEvent.change(await screen.findByTestId('override-reason-input'), { target: { value: OVERRIDE_REASON } });

    // approve wins
    fireEvent.click(await screen.findByTestId('approval-affordance-approve'));
    fireEvent.click(await screen.findByTestId('approval-confirm-submit'));
    await screen.findByTestId('approval-committed'); // ⚑ the barrier that makes the ordering deterministic

    // override loses — and renders it through its OWN error state, with no special-casing in App
    fireEvent.click(screen.getByTestId('override-affordance-button'));
    fireEvent.click(await screen.findByTestId('override-confirm-submit'));
    expect(await screen.findByTestId('override-state-error')).toBeInTheDocument();
    expect(screen.getByTestId('override-error-code')).toHaveTextContent('commit_conflict');
    expect(commits).toBe(2);
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
  it('wires every registered unit seam', () => {
    // ⚑ SUPERSEDED 2026-08-02 (register #2 / WIRE1-Fold-6). Preserved verbatim, not erased:
    //
    //     it('wires all five units seams', ...)
    //     expect(...).toEqual(['commit', 'history', 'memo', 'override', 'queue']);
    //
    // The submission unit registers a sixth key. RENAMED as well as widened, because "five" is a
    // cardinality in a NAME — register #13's exact defect shape, and leaving it would mint a new
    // instance of the problem that register keeps open. The new name carries no count.
    //
    // ⚠️ **THIS IS NOT THE LAST TIME THIS ASSERTION MOVES, AND IT DOES NOT CLAIM TO BE.** The
    // deferred outlier mount pass (its own Q4(a), already answered) supersedes THIS SAME
    // assertion. Whichever of the two lands second inherits the other's set — so if outlier
    // lands after this, the set becomes SEVEN, not six.
    //
    // ⛔ CORRECTION TO BOTH PLANS, recorded where it will be read. `register-2-submission-path-
    // plan.md` §8 item 3 and `register-2-code-gen-plan.md` §4.7 both say this pass produces a
    // "seven-key set" and that outlier would then make it eight. **Both are off by one**: the
    // superseded set above has FIVE keys, not six. The plans counted UNITS (queue, memoView,
    // approvalGate, overrideForm, history, login) where the assertion counts SEAMS — and login
    // registers none, because it takes its seam directly from the transport in App.jsx. Six now;
    // seven if outlier follows.
    const { seams } = fakeServer();
    // ⚑ SUPERSEDED 2026-08-13 (outlier mount). The set was
    //     ['commit', 'history', 'memo', 'override', 'queue', 'submission']
    // and `outlier` makes it SEVEN. ⛔ This is the supersession the outlier-wiring pass answered in
    // advance (its Q4(a)) and carried forward — with two figures that have since gone stale and are
    // corrected here: it said "five keys" and "add outlier as the sixth", both true before
    // submission landed on 2026-08-02. Six became seven, exactly as the register #2 backfill
    // predicted: "It is SIX now, and SEVEN if the outlier mount lands after this."
    expect(Object.keys(seams).sort())
      .toEqual(['commit', 'history', 'memo', 'outlier', 'override', 'queue', 'submission']);
  });

  it('the submission seam exposes both routes of the two-phase flow, plus the manifest read', () => {
    // ⚑ The set assertion above proves the KEY is registered; this proves it is the real seam and
    // not a placeholder. R10 without R11 creates cases nothing can draft — the incoherence Fold E
    // gave as the reason both routes had to land in ONE contract amendment.
    //
    // ⚑ `fetchProfile` is **R3**, pre-existing since the 2026-07-08 pin — the unit began reading
    // it when the per-document manifest turned out to live on `ApplicantProfile`, not on R10's
    // two-key `SubmissionAccepted`. ⛔ A seam gaining an operation is not the contract gaining a
    // route; no fold was required and none was made.
    const { seams } = fakeServer();
    expect(Object.keys(seams.submission).sort())
      .toEqual(['fetchProfile', 'submit', 'triggerDraft']);
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
