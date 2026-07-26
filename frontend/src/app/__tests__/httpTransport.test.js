import { describe, it, expect, vi } from 'vitest';
import { createHttpTransport, USER_ID_HEADER } from '../httpTransport.js';
import { createHistoryFetch } from '../../history/historyFetchSeam.js';

// INT-FE-1 — the real transport satisfies the duck-typed contract EVERY frozen seam expects,
// with no server and no network (fetch is injected). The point of these tests: prove the frozen
// seams work over the real transport WITHOUT modifying a single one of them.
function fakeFetch(status, body, record = []) {
  return vi.fn(async (url, init) => {
    record.push({ url, init });
    return { ok: status >= 200 && status < 300, json: async () => body };
  });
}

describe('createHttpTransport — the seam-facing contract', () => {
  it('returns { ok, body } — the shape every frozen seam consumes', async () => {
    const transport = createHttpTransport({ fetchImpl: fakeFetch(200, { items: [] }) });
    expect(await transport({ method: 'GET', path: '/decisions' }))
      .toEqual({ ok: true, body: { items: [] } });
  });

  it('reports ok:false for a non-2xx and passes the WIRE-1 envelope through UNCHANGED', async () => {
    const envelope = { error: { code: 'not_found', message: 'No such decision.', detail: {} } };
    const transport = createHttpTransport({ fetchImpl: fakeFetch(404, envelope) });
    const response = await transport({ method: 'GET', path: '/decisions/NOPE' });
    // it neither unpacks nor reshapes the envelope — that is the seam's job, not the transport's.
    expect(response).toEqual({ ok: false, body: envelope });
  });

  it('issues the request the seam built — method and path verbatim', async () => {
    const calls = [];
    const transport = createHttpTransport({ fetchImpl: fakeFetch(200, {}, calls), baseUrl: 'http://api' });
    await transport({ method: 'GET', path: '/decisions?page=2&size=20' });
    expect(calls[0].url).toBe('http://api/decisions?page=2&size=20');
    expect(calls[0].init.method).toBe('GET');
  });

  it('sends the X-User-Id stub header when a userId is configured', async () => {
    const calls = [];
    const transport = createHttpTransport({ fetchImpl: fakeFetch(200, {}, calls), userId: 'UW-1' });
    await transport({ method: 'GET', path: '/session' });
    expect(calls[0].init.headers[USER_ID_HEADER]).toBe('UW-1');
  });

  it('omits the stub header entirely when no userId is configured', async () => {
    const calls = [];
    const transport = createHttpTransport({ fetchImpl: fakeFetch(200, {}, calls) });
    await transport({ method: 'GET', path: '/session' });
    expect(calls[0].init.headers).not.toHaveProperty(USER_ID_HEADER);
  });

  it('sends no body or Content-Type for a GET (the only method Scope A issues)', async () => {
    const calls = [];
    const transport = createHttpTransport({ fetchImpl: fakeFetch(200, {}, calls) });
    await transport({ method: 'GET', path: '/decisions' });
    expect(calls[0].init).not.toHaveProperty('body');
    expect(calls[0].init.headers).not.toHaveProperty('Content-Type');
  });

  it('serializes a body when a seam supplies one (R5-shaped; unbacked in Scope A)', async () => {
    const calls = [];
    const transport = createHttpTransport({ fetchImpl: fakeFetch(501, {}, calls) });
    await transport({ method: 'POST', path: '/recommendations/REC-1/commit', body: { action: 'approve' } });
    expect(calls[0].init.method).toBe('POST');
    expect(calls[0].init.body).toBe(JSON.stringify({ action: 'approve' }));
    expect(calls[0].init.headers['Content-Type']).toBe('application/json');
  });

  it('defaults to the global fetch when none is injected — the PRODUCTION path', async () => {
    // The injected fetchImpl exists for testability; production passes none and must reach the
    // real global fetch. Left untested, the actual deployed code path would be unexercised.
    const globalFetch = fakeFetch(200, { user_id: 'UW-1', role: 'underwriter' });
    const original = globalThis.fetch;
    globalThis.fetch = globalFetch;
    try {
      const transport = createHttpTransport({ userId: 'UW-1' });
      await expect(transport({ method: 'GET', path: '/session' }))
        .resolves.toEqual({ ok: true, body: { user_id: 'UW-1', role: 'underwriter' } });
      expect(globalFetch).toHaveBeenCalledTimes(1);
    } finally {
      globalThis.fetch = original;
    }
  });

  it('a 204 No Content resolves with an undefined body — it is NEVER parsed', async () => {
    // ⚑ REGRESSION (2026-07-26). A 204 has no body BY DEFINITION, so calling .json() on it
    // rejects with a SyntaxError. This transport parsed unconditionally, so R8 POST /login --
    // which answers 204 -- came back to the seam as a THROW. The seam then synthesized a
    // network_error envelope, the login view showed "Unable to reach the server.", and
    // onAuthenticated was never reached: a login that SUCCEEDED on the server was discarded
    // by the client. Found in manual browser verification, not by this suite.
    const transport = createHttpTransport({
      fetchImpl: async () => ({
        ok: true,
        status: 204,
        json: async () => { throw new SyntaxError('Unexpected end of JSON input'); },
      }),
    });
    await expect(transport({ method: 'POST', path: '/login', body: { user_id: 'u', password: 'p' } }))
      .resolves.toEqual({ ok: true, body: undefined });
  });

  it('THROWS on a non-JSON body so the seam can synthesize its network_error envelope', async () => {
    const transport = createHttpTransport({
      fetchImpl: async () => ({ ok: true, json: async () => { throw new SyntaxError('not json'); } }),
    });
    await expect(transport({ method: 'GET', path: '/decisions' })).rejects.toBeInstanceOf(SyntaxError);
  });
});

describe('the real transport under a FROZEN seam (unmodified)', () => {
  it('ui-history fetchList resolves the R6 wrapper over the real transport', async () => {
    const body = { items: [], page: { page: 1, size: 20, total: 0 } };
    const seam = createHistoryFetch(createHttpTransport({ fetchImpl: fakeFetch(200, body) }));
    await expect(seam.fetchList(1, 20)).resolves.toEqual(body);
  });

  it("a 404 becomes the seam's own normalized envelope — the transport stays ignorant of §4", async () => {
    const envelope = { error: { code: 'not_found', message: 'No such decision.', detail: {} } };
    const seam = createHistoryFetch(createHttpTransport({ fetchImpl: fakeFetch(404, envelope) }));
    await expect(seam.fetchDetail('NOPE')).rejects.toEqual(envelope);
  });

  it('a 501 not_implemented reaches the unit as an ordinary error envelope', async () => {
    // The Scope-A boundary as a UI unit experiences it: not a crash, a normal error state.
    const envelope = { error: { code: 'not_implemented', message: 'Not wired.', detail: { route: 'R2' } } };
    const seam = createHistoryFetch(createHttpTransport({ fetchImpl: fakeFetch(501, envelope) }));
    await expect(seam.fetchList(1, 20)).rejects.toEqual(envelope);
  });

  it('a transport throw becomes the seam network_error envelope', async () => {
    const seam = createHistoryFetch(createHttpTransport({
      fetchImpl: async () => { throw new TypeError('offline'); },
    }));
    await expect(seam.fetchList(1, 20)).rejects.toEqual({
      error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} },
    });
  });
});
