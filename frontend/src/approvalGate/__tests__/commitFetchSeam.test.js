import { describe, it, expect } from 'vitest';
import { buildMemoRequest, buildCommitRequest, createCommitFetch, normalizeError } from '../commitFetchSeam.js';

// BODY-1 — the approve-only, session-derived-committer request (by-construction, P3).
describe('BODY-1 — buildCommitRequest narrow signature', () => {
  it('body deep-equals { action: "approve" } — no underwriter_id, no reason', () => {
    const req = buildCommitRequest('rec-9');
    expect(req.method).toBe('POST');
    expect(req.path).toBe('/recommendations/rec-9/commit');
    expect(req.body).toEqual({ action: 'approve' });
    expect(Object.keys(req.body)).toEqual(['action']);
    expect(req.body).not.toHaveProperty('underwriter_id');
    expect(req.body).not.toHaveProperty('reason');
  });
});

describe('commitFetchSeam — dual operation over an injected transport', () => {
  it('fetchContext resolves the body on ok, submitApprove POSTs and resolves CommittedDecision', async () => {
    const seen = [];
    const transport = async (req) => {
      seen.push(req);
      return { ok: true, body: req.method === 'GET' ? { status: 'ready' } : { recommendation_id: 'rec-1', action: 'approve' } };
    };
    const seam = createCommitFetch(transport);
    await expect(seam.fetchContext('app-1')).resolves.toEqual({ status: 'ready' });
    await expect(seam.submitApprove('rec-1')).resolves.toEqual({ recommendation_id: 'rec-1', action: 'approve' });
    expect(seen[0]).toEqual({ method: 'GET', path: '/applications/app-1/memo' });
    expect(seen[1]).toEqual({ method: 'POST', path: '/recommendations/rec-1/commit', body: { action: 'approve' } });
  });

  it('both operations reject with a well-formed normalized envelope on failure', async () => {
    const seam = createCommitFetch(async () => ({ ok: false, body: { error: { code: 'forbidden', message: 'no' } } }));
    await expect(seam.submitApprove('rec-1')).rejects.toEqual({ error: { code: 'forbidden', message: 'no', detail: {} } });
    await expect(seam.fetchContext('app-1')).rejects.toEqual({ error: { code: 'forbidden', message: 'no', detail: {} } });
    const throwing = createCommitFetch(async () => { throw new Error('boom'); });
    const networkEnvelope = { error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} } };
    await expect(throwing.fetchContext('app-1')).rejects.toEqual(networkEnvelope);
    await expect(throwing.submitApprove('rec-1')).rejects.toEqual(networkEnvelope); // transport-throw path
    // a falsy transport response (defensive branch) also normalizes to a network_error envelope
    const falsy = createCommitFetch(async () => undefined);
    await expect(falsy.submitApprove('rec-1')).rejects.toEqual(networkEnvelope);
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
