import { describe, it, expect } from 'vitest';
import { DEFAULT_PAGE_SIZE, buildQueueRequest, normalizeError, createQueueFetch } from '../fetchSeam.js';

// FETCH-1 (seam) + CG-Fold-1 (every rejection carries a well-formed envelope) + PERF-1 (bounded).
describe('fetchSeam — seam contract + CG-Fold-1 normalization', () => {
  it('buildQueueRequest builds a single bounded page request (page + size)', () => {
    const req = buildQueueRequest(3, 20);
    expect(req.method).toBe('GET');
    expect(req.path).toContain('page=3');
    expect(req.path).toContain('size=20');
  });

  it('buildQueueRequest defaults size to DEFAULT_PAGE_SIZE (20, Q2-A)', () => {
    expect(DEFAULT_PAGE_SIZE).toBe(20);
    expect(buildQueueRequest(1).path).toContain('size=20');
  });

  it('normalizeError passes a well-formed envelope through', () => {
    const env = normalizeError({ error: { code: 'not_found', message: 'nope', detail: { x: 1 } } });
    expect(env).toEqual({ error: { code: 'not_found', message: 'nope', detail: { x: 1 } } });
  });

  it('normalizeError synthesizes a network_error envelope for a raw/transport/malformed failure', () => {
    expect(normalizeError(new Error('boom')).error.code).toBe('network_error');
    expect(normalizeError(undefined).error.code).toBe('network_error');
    expect(normalizeError({ error: { code: 'x' } }).error.code).toBe('network_error'); // missing message -> synth
    expect(normalizeError({ error: { code: 'x', message: 'y' } }).error.detail).toEqual({}); // detail defaulted
  });

  it('createQueueFetch resolves the list wrapper on success', async () => {
    const body = { items: [{ application_id: 'app-1' }], page: { page: 1, size: 20, total: 1 } };
    const seam = createQueueFetch(async () => ({ ok: true, body }));
    await expect(seam(1, 20)).resolves.toEqual(body);
  });

  it('createQueueFetch rejects a well-formed envelope on non-2xx', async () => {
    const seam = createQueueFetch(async () => ({ ok: false, body: { error: { code: 'forbidden', message: 'no', detail: {} } } }));
    await expect(seam(1, 20)).rejects.toEqual({ error: { code: 'forbidden', message: 'no', detail: {} } });
  });

  it('createQueueFetch rejects a network_error envelope when the transport throws', async () => {
    const seam = createQueueFetch(async () => { throw new Error('down'); });
    await expect(seam(2, 20)).rejects.toEqual({ error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} } });
  });
});
