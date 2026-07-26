import { describe, it, expect } from 'vitest';
import {
  buildLoginRequest,
  buildLogoutRequest,
  createLoginFetch,
  normalizeError,
} from '../loginFetchSeam.js';
import { createHttpTransport } from '../../app/httpTransport.js';

// The own-local seam for R8/R9 (WIRE1-Fold-5). Mirrors its siblings' shape and imports none of
// them — cross-unit consistency comes from the WIRE-1 contract, never from importing a sibling.

describe('buildLoginRequest', () => {
  it('is a POST of /login carrying exactly { user_id, password }', () => {
    const request = buildLoginRequest({ user_id: 'UW-1', password: 's3cret' });
    expect(request.method).toBe('POST');
    expect(request.path).toBe('/login');
    // ⚑ EXACTLY these two keys. WIRE-1 §5 pins the login body; anything extra would be a
    // client inventing contract surface.
    expect(Object.keys(request.body).sort()).toEqual(['password', 'user_id']);
    expect(request.body).toEqual({ user_id: 'UW-1', password: 's3cret' });
  });
});

describe('buildLogoutRequest', () => {
  it('is a POST of /logout with NO body — the session is identified by the cookie alone', () => {
    const request = buildLogoutRequest();
    expect(request.method).toBe('POST');
    expect(request.path).toBe('/logout');
    expect(request.body).toBeUndefined();
  });
});

describe('normalizeError', () => {
  it('passes a well-formed WIRE-1 §4 envelope through unchanged', () => {
    const envelope = { error: { code: 'unauthenticated', message: 'Authentication failed.', detail: {} } };
    expect(normalizeError(envelope)).toEqual(envelope);
  });

  it('synthesizes a network_error envelope for anything malformed — so the view never unpacks a raw throw', () => {
    for (const cause of [undefined, null, 'boom', new Error('x'), {}, { error: {} }]) {
      const result = normalizeError(cause);
      expect(result.error.code).toBe('network_error');
      expect(typeof result.error.message).toBe('string');
      expect(result.error.detail).toEqual({});
    }
  });
});

describe('createLoginFetch over the REAL transport', () => {
  it('a 204 on login AND on logout RESOLVES — neither is mistaken for a network failure', async () => {
    // ⚑ REGRESSION (2026-07-26). Both R8 and R9 answer 204. Before the transport learned that a
    // 204 carries no body, both rejected with a synthesized network_error -- so a SUCCESSFUL
    // login was reported to the user as "Unable to reach the server." and the session was
    // discarded client-side. Logout hid the same defect only because LogoutControl swallows a
    // rejection in its finally block.
    //
    // ⚑ This drives the REAL httpTransport, not a faked seam. The pre-existing "a 204 resolves
    // with NO body" test in login.submit.test.jsx fakes the seam itself, so it could never have
    // caught this: every fake in the suite was more forgiving than a browser.
    const transport = createHttpTransport({
      fetchImpl: async () => ({
        ok: true,
        status: 204,
        json: async () => { throw new SyntaxError('Unexpected end of JSON input'); },
      }),
    });
    const seam = createLoginFetch(transport);

    await expect(seam.submitLogin({ user_id: 'u', password: 'p' })).resolves.toBeUndefined();
    await expect(seam.submitLogout()).resolves.toBeUndefined();
  });
});
