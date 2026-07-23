import { describe, it, expect } from 'vitest';
import { buildOutlierRequest, normalizeError, createOutlierFetch } from '../fetchSeam.js';
import { makeReadyPopulatedBody, makeCapturingTransport, makeFailingTransport } from './fixtures.js';

// FETCH-1 (P-OUTV-6) + ERROR-1 build/normalize half (P-OUTV-7) — the own-local, READ-ONLY R4 seam.
describe('FETCH-1 — buildOutlierRequest emits ONLY a GET', () => {
  it('builds the R4 request for one application', () => {
    expect(buildOutlierRequest('app-7')).toEqual({ method: 'GET', path: '/applications/app-7/memo' });
  });

  it('emits no body key and no method other than GET (write structurally absent)', () => {
    const request = buildOutlierRequest('app-7');
    expect(Object.keys(request).sort()).toEqual(['method', 'path']);
    expect(request.method).toBe('GET');
  });
});

describe('ERROR-1 — normalizeError always yields a well-formed WIRE-1 envelope', () => {
  it('passes a well-formed envelope through, defaulting detail', () => {
    expect(normalizeError({ error: { code: 'not_found', message: 'Nope.' } }))
      .toEqual({ error: { code: 'not_found', message: 'Nope.', detail: {} } });
  });

  it('preserves a supplied detail', () => {
    expect(normalizeError({ error: { code: 'not_found', message: 'Nope.', detail: { hint: 'x' } } }))
      .toEqual({ error: { code: 'not_found', message: 'Nope.', detail: { hint: 'x' } } });
  });

  it('synthesizes network_error for a raw/malformed cause', () => {
    for (const cause of [new Error('boom'), null, undefined, {}, { error: {} }, 'string']) {
      expect(normalizeError(cause).error.code).toBe('network_error');
    }
  });
});

describe('FETCH-1 — createOutlierFetch', () => {
  it('resolves the R4 body on ok:true and captures the request', async () => {
    const body = makeReadyPopulatedBody('app-3');
    const transport = makeCapturingTransport(body);
    const fetchOutlier = createOutlierFetch(transport);

    await expect(fetchOutlier('app-3')).resolves.toBe(body);
    expect(transport.calls).toEqual([{ method: 'GET', path: '/applications/app-3/memo' }]);
  });

  it('rejects with a well-formed envelope on a non-2xx body', async () => {
    const fetchOutlier = createOutlierFetch(makeFailingTransport('envelope'));
    await expect(fetchOutlier('app-3')).rejects.toEqual({
      error: { code: 'not_found', message: 'No such application.', detail: { hint: 'internal detail' } },
    });
  });

  it('rejects with a normalized envelope on a raw transport throw — never a raw exception', async () => {
    const fetchOutlier = createOutlierFetch(makeFailingTransport('throw'));
    await expect(fetchOutlier('app-3')).rejects.toEqual({
      error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} },
    });
  });

  it('rejects with a normalized envelope when the transport resolves a malformed failure', async () => {
    const fetchOutlier = createOutlierFetch(async () => ({ ok: false, body: null }));
    await expect(fetchOutlier('app-3')).rejects.toEqual({
      error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} },
    });
  });

  it('rejects with a normalized envelope when the transport resolves nothing at all', async () => {
    const fetchOutlier = createOutlierFetch(async () => undefined);
    await expect(fetchOutlier('app-3')).rejects.toEqual({
      error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} },
    });
  });
});
