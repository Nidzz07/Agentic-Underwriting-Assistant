import { describe, it, expect } from 'vitest';
import { buildMemoRequest, normalizeError, createMemoFetch } from '../memoFetchSeam.js';
import { emptyListsReadyMemoView } from './fixtures.js';

// FETCH-1 (seam) + PERF-1 (bounded) + CG-MEMO-Fold-1 (own-local normalization, WIRE-1 §4 shape).
describe('memoFetchSeam — request building + normalization', () => {
  it('buildMemoRequest targets a single memo by applicationId (PERF-1 bounded)', () => {
    expect(buildMemoRequest('app-1')).toEqual({ method: 'GET', path: '/applications/app-1/memo' });
  });

  it('resolves the MemoView body on ok', async () => {
    const seam = createMemoFetch(async () => ({ ok: true, body: emptyListsReadyMemoView }));
    expect(await seam('app-1')).toBe(emptyListsReadyMemoView);
  });

  it('rejects with the parsed envelope on a non-2xx body', async () => {
    const seam = createMemoFetch(async () => ({
      ok: false,
      body: { error: { code: 'not_found', message: 'nope', detail: { a: 1 } } },
    }));
    await expect(seam('x')).rejects.toEqual({ error: { code: 'not_found', message: 'nope', detail: { a: 1 } } });
  });

  it('normalizes a transport failure to a network_error envelope (CG-MEMO-Fold-1)', async () => {
    const seam = createMemoFetch(async () => { throw new Error('down'); });
    await expect(seam('x')).rejects.toEqual({
      error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} },
    });
  });

  it('normalizeError passes a well-formed envelope through and synthesizes for malformed', () => {
    expect(normalizeError({ error: { code: 'c', message: 'm' } })).toEqual({ error: { code: 'c', message: 'm', detail: {} } });
    expect(normalizeError(null).error.code).toBe('network_error');
    expect(normalizeError({ nope: true }).error.code).toBe('network_error');
  });
});
