import { describe, it, expect } from 'vitest';
import { buildMemoRequest, buildOverrideRequest, createOverrideFetch, normalizeError } from '../overrideFetchSeam.js';

// BODY-1 — the override, reason-required, session-derived-committer request (by-construction, P4).
describe('BODY-1 — buildOverrideRequest reason-required signature', () => {
  it('body deep-equals { action: "override", reason } — no underwriter_id; reason as-entered', () => {
    const req = buildOverrideRequest('rec-9', '  I disagree  ');
    expect(req.method).toBe('POST');
    expect(req.path).toBe('/recommendations/rec-9/commit');
    expect(req.body).toEqual({ action: 'override', reason: '  I disagree  ' }); // verbatim, untrimmed
    expect(Object.keys(req.body).sort()).toEqual(['action', 'reason']);
    expect(req.body).not.toHaveProperty('underwriter_id');
  });

  it('serializes whatever reason it is handed (no non-blank enforcement in the builder)', () => {
    // The builder does NOT gate blankness — that is the orchestrator's runtime predicate (P2) and the
    // backend _gate (authoritative). A blank reason still serializes structurally.
    expect(buildOverrideRequest('rec-1', '').body).toEqual({ action: 'override', reason: '' });
  });
});

describe('overrideFetchSeam — dual operation over an injected transport', () => {
  it('fetchContext resolves the body on ok; submitOverride POSTs the reason and resolves CommittedDecision', async () => {
    const seen = [];
    const transport = async (req) => {
      seen.push(req);
      return { ok: true, body: req.method === 'GET' ? { status: 'ready' } : { recommendation_id: 'rec-1', action: 'override', reason: 'because' } };
    };
    const seam = createOverrideFetch(transport);
    await expect(seam.fetchContext('app-1')).resolves.toEqual({ status: 'ready' });
    await expect(seam.submitOverride('rec-1', 'because')).resolves.toEqual({ recommendation_id: 'rec-1', action: 'override', reason: 'because' });
    expect(seen[0]).toEqual({ method: 'GET', path: '/applications/app-1/memo' });
    expect(seen[1]).toEqual({ method: 'POST', path: '/recommendations/rec-1/commit', body: { action: 'override', reason: 'because' } });
  });

  it('both operations reject with a well-formed normalized envelope on failure', async () => {
    const seam = createOverrideFetch(async () => ({ ok: false, body: { error: { code: 'commit_conflict', message: 'no' } } }));
    await expect(seam.submitOverride('rec-1', 'r')).rejects.toEqual({ error: { code: 'commit_conflict', message: 'no', detail: {} } });
    await expect(seam.fetchContext('app-1')).rejects.toEqual({ error: { code: 'commit_conflict', message: 'no', detail: {} } });
    const throwing = createOverrideFetch(async () => { throw new Error('boom'); });
    const networkEnvelope = { error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} } };
    await expect(throwing.fetchContext('app-1')).rejects.toEqual(networkEnvelope);
    await expect(throwing.submitOverride('rec-1', 'r')).rejects.toEqual(networkEnvelope); // transport-throw path
    const falsy = createOverrideFetch(async () => undefined);
    await expect(falsy.submitOverride('rec-1', 'r')).rejects.toEqual(networkEnvelope);
    await expect(falsy.fetchContext('app-1')).rejects.toEqual(networkEnvelope);
  });
});

describe('normalizeError', () => {
  it('passes a well-formed envelope through (defaulting detail) and synthesizes network_error otherwise', () => {
    expect(normalizeError({ error: { code: 'x', message: 'y' } })).toEqual({ error: { code: 'x', message: 'y', detail: {} } });
    expect(normalizeError(null)).toEqual({ error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} } });
    expect(normalizeError('nope')).toEqual({ error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} } });
  });
});

describe('buildMemoRequest', () => {
  it('targets one memo by applicationId', () => {
    expect(buildMemoRequest('app-9')).toEqual({ method: 'GET', path: '/applications/app-9/memo' });
  });
});
