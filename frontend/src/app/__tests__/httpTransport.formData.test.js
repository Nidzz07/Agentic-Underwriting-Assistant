// WIRE1-Fold-7 stage 6 — FormData passthrough in the SHARED transport.
//
// ⛔ THE RISK THIS FILE GUARDS. `httpTransport` is the ONE client-side wire boundary and is used
// by all six seams. Teaching it multipart must not change a single byte of what the JSON path
// sends, or a change made for document upload silently alters login, commit, override and
// history. Q7 called for exactly this test; it is here first, before the change.
import { describe, it, expect, vi } from 'vitest';
import { createHttpTransport } from '../httpTransport.js';

function capturing(status = 200, body = {}) {
  const calls = [];
  const fetchImpl = vi.fn(async (url, init) => {
    calls.push({ url, init });
    return { status, ok: status < 400, json: async () => body };
  });
  return { calls, transport: createHttpTransport({ baseUrl: '/api', fetchImpl }) };
}

describe('the JSON path is byte-unchanged', () => {
  it('still stringifies a JSON body and still sets Content-Type', async () => {
    const { calls, transport } = capturing();
    await transport({ method: 'POST', path: '/applications', body: { form_fields: { a: 1 } } });

    const { init } = calls[0];
    expect(init.body).toBe(JSON.stringify({ form_fields: { a: 1 } }));
    expect(init.headers['Content-Type']).toBe('application/json');
    expect(init.headers.Accept).toBe('application/json');
  });

  it('still sends NO body and NO Content-Type for a bodiless request', async () => {
    const { calls, transport } = capturing();
    await transport({ method: 'GET', path: '/applications?page=1&size=20' });

    expect(calls[0].init.body).toBeUndefined();
    expect(calls[0].init.headers['Content-Type']).toBeUndefined();
  });

  it('still returns { ok, body } and still short-circuits a 204', async () => {
    const { transport } = capturing(204);
    await expect(transport({ method: 'POST', path: '/logout' }))
      .resolves.toEqual({ ok: true, body: undefined });
  });
});

describe('FormData passes through untouched', () => {
  it('is NOT stringified', async () => {
    const form = new FormData();
    form.append('form_fields', '{"a":1}');
    const { calls, transport } = capturing();

    await transport({ method: 'POST', path: '/applications', body: form });

    expect(calls[0].init.body).toBe(form);           // the very same object
    expect(typeof calls[0].init.body).not.toBe('string');
  });

  it('⛔ sets NO Content-Type — the browser must supply the multipart boundary', async () => {
    // A hand-set `multipart/form-data` header omits the generated `boundary=...`, and the server
    // then cannot split the parts. This is the single easiest way to break an upload, and it
    // fails in a way that looks like a malformed body rather than a missing header.
    const { calls, transport } = capturing();
    await transport({ method: 'POST', path: '/applications', body: new FormData() });

    expect(calls[0].init.headers['Content-Type']).toBeUndefined();
    expect(calls[0].init.headers.Accept).toBe('application/json');
  });

  it('still returns the parsed body for a FormData request', async () => {
    const { transport } = capturing(200, { application_id: 'APP-1', status: 'pending' });
    await expect(transport({ method: 'POST', path: '/applications', body: new FormData() }))
      .resolves.toEqual({ ok: true, body: { application_id: 'APP-1', status: 'pending' } });
  });
});
