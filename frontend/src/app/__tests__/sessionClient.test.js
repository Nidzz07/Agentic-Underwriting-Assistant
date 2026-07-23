import { describe, it, expect, vi } from 'vitest';
import { buildSessionRequest, createSessionClient, loadCurrentRole } from '../sessionClient.js';

// INT-FE-1 — R1 role delivery (WIRE-1 §6). The retrieval ui-shell's RoleContext deliberately
// left out ("owned by WIRE-1 — NOT designed here").
const ok = (body) => vi.fn(async () => ({ ok: true, body }));
const fail = (body) => vi.fn(async () => ({ ok: false, body }));

describe('buildSessionRequest', () => {
  it('is a GET of /session — nothing more', () => {
    expect(buildSessionRequest()).toEqual({ method: 'GET', path: '/session' });
  });
});

describe('createSessionClient', () => {
  it('resolves the R1 body { user_id, role }', async () => {
    const session = { user_id: 'UW-1', role: 'underwriter' };
    await expect(createSessionClient(ok(session))()).resolves.toEqual(session);
  });

  it('issues exactly the R1 request', async () => {
    const transport = ok({ user_id: 'UW-1', role: 'underwriter' });
    await createSessionClient(transport)();
    expect(transport).toHaveBeenCalledWith({ method: 'GET', path: '/session' });
  });

  it('rejects with the server envelope on a non-2xx', async () => {
    const envelope = { error: { code: 'unauthenticated', message: 'Authentication is required.', detail: {} } };
    await expect(createSessionClient(fail(envelope))()).rejects.toEqual(envelope);
  });

  it('rejects rather than returning a role when the transport yields nothing at all', async () => {
    // A defensive branch: a transport that resolves undefined must not be read as a session.
    await expect(createSessionClient(async () => undefined)()).rejects.toBeUndefined();
  });
});

describe('loadCurrentRole — the RoleContext value shape, fail-closed', () => {
  it.each(['underwriter', 'auditor', 'admin'])('passes the %s wire value through, never re-cased', async (role) => {
    await expect(loadCurrentRole(ok({ user_id: 'U', role }))).resolves.toBe(role);
  });

  it('fail-closes to null on 401 — the shell unauthenticated state, not an error', async () => {
    const envelope = { error: { code: 'unauthenticated', message: 'Authentication is required.', detail: {} } };
    await expect(loadCurrentRole(fail(envelope))).resolves.toBeNull();
  });

  it('fail-closes to null when the transport throws', async () => {
    await expect(loadCurrentRole(async () => { throw new TypeError('offline'); })).resolves.toBeNull();
  });

  it.each([
    ['a missing role', { user_id: 'U' }],
    ['a blank role', { user_id: 'U', role: '' }],
    ['a non-string role', { user_id: 'U', role: 42 }],
    ['a null body', null],
  ])('fail-closes to null for %s', async (_label, body) => {
    // The same fail-closed posture as the server's to_role: anything unresolvable -> null.
    await expect(loadCurrentRole(ok(body))).resolves.toBeNull();
  });

  it('does NOT validate the role against a local list — the server is the authority', async () => {
    // A role the client does not know is still passed through: re-deriving the canonical set here
    // would fork auth-rbac's frozen policy into the browser.
    await expect(loadCurrentRole(ok({ user_id: 'U', role: 'future-role' }))).resolves.toBe('future-role');
  });
});
