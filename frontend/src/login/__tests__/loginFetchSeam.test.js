import { describe, it, expect } from 'vitest';
import {
  buildLoginRequest,
  buildLogoutRequest,
  createLoginFetch,
  normalizeError,
} from '../loginFetchSeam.js';

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
