import { createElement } from 'react';
import { render } from '@testing-library/react';
import { RoleProvider } from '../../shell/session/roleContext.js';
import { OverrideFormView } from '../OverrideFormView.jsx';

// Shared test substrate for ui-override-form.
//
// Fold-A (dual-operation reason-carrying single-double) — makeOverrideDouble() is a FACTORY: every
// call returns a FRESH { fetchContext, submitOverride } with its OWN calls[] arrays. Each operation is
// an INDEPENDENTLY-counted spy (own calls[]); submitOverride.calls[i] records [recommendationId, reason]
// so the reason is inspectable and asserted VERBATIM. Programmable per operation (resolveWith /
// rejectWith / hang) and SEQUENCEABLE (fail-then-succeed) so RECOVERY-1 uses its own transition
// sequence — all on the SAME one factory. One construction is reused across all teeth tests.

export function resolved(value) { return { ok: true, value }; }
export function rejected(value) { return { ok: false, value }; }

function makeSpy() {
  const calls = [];
  const queue = [];
  let fallback = { ok: true, value: undefined };
  async function spy(...args) {
    calls.push(args);
    const step = queue.length ? queue.shift() : fallback;
    if (step.hang) return new Promise(() => {}); // never resolves — stays in-flight
    if (!step.ok) throw step.value;
    return step.value;
  }
  spy.calls = calls;
  spy.resolveWith = (value) => { fallback = { ok: true, value }; return spy; };
  spy.rejectWith = (value) => { fallback = { ok: false, value }; return spy; };
  spy.hang = () => { fallback = { hang: true }; return spy; };
  spy.sequence = (steps) => { queue.push(...steps); return spy; };
  return spy;
}

export function makeOverrideDouble() {
  return { fetchContext: makeSpy(), submitOverride: makeSpy() };
}

// ---- data fixtures -----------------------------------------------------------
export function makeMemoView(overrides = {}) {
  return {
    application_id: 'app-1',
    recommendation_id: 'rec-1',
    status: 'ready',
    profile: { application_id: 'app-1' },
    report: { recommendation: 'DECLINE-RECOMMEND', confidence: 'Medium' },
    memo: { recommendation: 'DECLINE-RECOMMEND', confidence: 'Medium' },
    ...overrides,
  };
}

export const pendingMemoView = Object.freeze({
  application_id: 'app-1', recommendation_id: null, status: 'pending', profile: null, report: null, memo: null,
});

// A committed OVERRIDE decision echo: action:'override' with a non-null reason (the justification just
// recorded). The committed display sources the reason EXCLUSIVELY from decision.reason (ND-OVR-Fold-ii).
export function makeCommittedOverride(overrides = {}) {
  return { recommendation_id: 'rec-1', underwriter_id: 'u-42', action: 'override', reason: 'I disagree with this recommendation', ...overrides };
}

// ---- REASONGATE-1 whitespace fixtures (Q3-A) ---------------------------------
// Each BLANK must keep the affordance disabled AND drive the full Override->Confirm attempt to ZERO
// submitOverride calls. NONBLANK has surrounding spaces around real content — proves the payload is sent
// AS-ENTERED / untrimmed (exactly one POST carrying the reason verbatim).
export const BLANK_REASONS = Object.freeze(['', ' ', '\t', '\n', ' \t\n ']);
export const NONBLANK_REASON = ' I disagree because X ';

// ---- ERROR-1 envelope fixtures (Q4-A, table-driven) --------------------------
// WIRE-1 §4 well-formed envelopes. forbiddenEnvelope.detail carries a unique marker so the ERROR-1
// detail-never test can assert it never reaches the DOM. The 409 conflictEnvelope is REUSED for BOTH the
// already-committed and the blank-reason-race causes (one commit_conflict code, one rendered state).
export const forbiddenEnvelope = Object.freeze({ error: { code: 'forbidden', message: 'Role forbidden.', detail: { field: 'ROLE_SECRET_XYZ' } } });
export const conflictEnvelope = Object.freeze({ error: { code: 'commit_conflict', message: 'Already committed on the server.', detail: {} } });
export const invalidEnvelope = Object.freeze({ error: { code: 'invalid_request', message: 'Malformed request.', detail: {} } });
export const unprocessableEnvelope = Object.freeze({ error: { code: 'unprocessable', message: 'Unprocessable request.', detail: {} } });
export const readErrorEnvelope = Object.freeze({ error: { code: 'not_found', message: 'No such application.', detail: {} } });

// ---- render helper (createElement — keeps this file JSX-free, .js-safe) ------
export function renderForm({ role = 'underwriter', seam, applicationId = 'app-1' } = {}) {
  return render(
    createElement(
      RoleProvider,
      { value: role },
      createElement(OverrideFormView, { overrideFetchSeam: seam, applicationId })
    )
  );
}
