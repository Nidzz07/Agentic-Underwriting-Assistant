import { createElement } from 'react';
import { render } from '@testing-library/react';
import { RoleProvider } from '../../shell/session/roleContext.js';
import { ApprovalGateView } from '../ApprovalGateView.jsx';

// Shared test substrate for ui-approval-gate.
//
// CG-Fold-1 (dual-operation single-double) — makeCommitDouble() is a FACTORY: every call returns a
// FRESH { fetchContext, submitApprove } with its OWN calls[] arrays. Each test constructs its own
// double (never a shared module-level mutable instance), so the "exactly 0" / "exactly 1" call-count
// assertions never leak across tests. Each operation is an INDEPENDENTLY-counted spy (own calls[]).
// CG-Fold-2 (programmable/sequenceable) — a spy's outcome is settable (resolveWith / rejectWith /
// hang) and can be SEQUENCED (fail-then-succeed) so RECOVERY-1 uses its own transition sequence,
// distinct from the static ERROR-1 table — all on the SAME one factory.

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

export function makeCommitDouble() {
  return { fetchContext: makeSpy(), submitApprove: makeSpy() };
}

// ---- data fixtures -----------------------------------------------------------
export function makeMemoView(overrides = {}) {
  return {
    application_id: 'app-1',
    recommendation_id: 'rec-1',
    status: 'ready',
    profile: { application_id: 'app-1' },
    report: { recommendation: 'APPROVE', confidence: 'High' },
    memo: { recommendation: 'APPROVE', confidence: 'High' },
    ...overrides,
  };
}

export const pendingMemoView = Object.freeze({
  application_id: 'app-1', recommendation_id: null, status: 'pending', profile: null, report: null, memo: null,
});

export function makeCommittedDecision(overrides = {}) {
  return { recommendation_id: 'rec-1', underwriter_id: 'u-42', action: 'approve', reason: null, ...overrides };
}

// WIRE-1 §4 error envelopes (well-formed). `forbiddenEnvelope.detail` carries a unique marker so the
// ERROR-1 detail-never test can assert it never reaches the DOM.
export const forbiddenEnvelope = Object.freeze({ error: { code: 'forbidden', message: 'Role forbidden.', detail: { field: 'ROLE_SECRET_XYZ' } } });
export const conflictEnvelope = Object.freeze({ error: { code: 'commit_conflict', message: 'Already committed on the server.', detail: {} } });
export const invalidEnvelope = Object.freeze({ error: { code: 'invalid_request', message: 'Malformed request.', detail: {} } });
export const unprocessableEnvelope = Object.freeze({ error: { code: 'unprocessable', message: 'Unprocessable request.', detail: {} } });
export const readErrorEnvelope = Object.freeze({ error: { code: 'not_found', message: 'No such application.', detail: {} } });

// ---- render helper (createElement — keeps this file JSX-free, .js-safe) ------
export function renderGate({ role = 'underwriter', seam, applicationId = 'app-1' } = {}) {
  return render(
    createElement(
      RoleProvider,
      { value: role },
      createElement(ApprovalGateView, { commitFetchSeam: seam, applicationId })
    )
  );
}
