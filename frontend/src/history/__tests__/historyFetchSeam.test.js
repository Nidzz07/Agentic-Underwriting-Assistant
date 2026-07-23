import { describe, it, expect } from 'vitest';
import * as seamModule from '../historyFetchSeam.js';
import {
  createHistoryFetch,
  buildHistoryListRequest,
  buildHistoryDetailRequest,
  normalizeError,
} from '../historyFetchSeam.js';
import { makeAuditRecord, makeListBody, errorEnvelope } from './fixtures.js';

// C2 — the READ-ONLY DUAL-READ seam (P3 / P4). FAITHFUL-1(b): the export surface is EXACTLY the four
// read members. DUALREAD-1: fetchList/fetchDetail are independent reads. ERROR-1: every failure
// rejects with a well-formed WIRE-1 §4 envelope, never a raw exception.
describe('historyFetchSeam — the four-member READ-ONLY export surface (FAITHFUL-1 b)', () => {
  it('exports exactly { createHistoryFetch, buildHistoryListRequest, buildHistoryDetailRequest, normalizeError }', () => {
    expect(Object.keys(seamModule).sort()).toEqual([
      'buildHistoryDetailRequest',
      'buildHistoryListRequest',
      'createHistoryFetch',
      'normalizeError',
    ]);
  });
  it('exposes no default export, no submit*, and no request-body builder', () => {
    expect(seamModule.default).toBeUndefined();
    expect(Object.keys(seamModule).some((k) => /^submit/.test(k))).toBe(false);
    expect(Object.keys(seamModule).some((k) => /commit|override/i.test(k))).toBe(false);
  });
});

describe('buildHistoryListRequest / buildHistoryDetailRequest — GET-only (FAITHFUL-1 a, PERF-1)', () => {
  it('the list builder emits ONLY { method: GET, path } for exactly one bounded page', () => {
    const req = buildHistoryListRequest(3, 20);
    expect(req).toEqual({ method: 'GET', path: '/decisions?page=3&size=20' });
    expect(Object.keys(req).sort()).toEqual(['method', 'path']);
    expect(req).not.toHaveProperty('body');
  });
  it('the detail builder emits ONLY { method: GET, path } for exactly one record by id', () => {
    const req = buildHistoryDetailRequest('dec-7');
    expect(req).toEqual({ method: 'GET', path: '/decisions/dec-7' });
    expect(Object.keys(req).sort()).toEqual(['method', 'path']);
    expect(req).not.toHaveProperty('body');
  });
});

describe('normalizeError — the WIRE-1 §4 envelope (own-local, not imported from a sibling)', () => {
  it('passes a well-formed envelope through', () => {
    expect(normalizeError({ error: { code: 'not_found', message: 'gone' } }))
      .toEqual({ error: { code: 'not_found', message: 'gone', detail: {} } });
  });
  it('synthesizes a network_error envelope for a raw/malformed cause', () => {
    expect(normalizeError(new Error('boom')).error.code).toBe('network_error');
    expect(normalizeError(undefined).error.code).toBe('network_error');
    expect(normalizeError({ error: { code: 1 } }).error.code).toBe('network_error');
  });
});

describe('createHistoryFetch — dual read over an injected transport', () => {
  it('fetchList resolves the R6 page wrapper and issues the GET list request', async () => {
    const seen = [];
    const seam = createHistoryFetch(async (req) => { seen.push(req); return { ok: true, body: makeListBody() }; });
    const body = await seam.fetchList(2, 20);
    expect(body.page.page).toBe(2);
    expect(seen).toEqual([{ method: 'GET', path: '/decisions?page=2&size=20' }]);
  });
  it('fetchDetail resolves the R7 AuditRecord and issues the GET detail request', async () => {
    const seen = [];
    const record = makeAuditRecord();
    const seam = createHistoryFetch(async (req) => { seen.push(req); return { ok: true, body: record }; });
    await expect(seam.fetchDetail('dec-1')).resolves.toBe(record);
    expect(seen).toEqual([{ method: 'GET', path: '/decisions/dec-1' }]);
  });
  it('createHistoryFetch returns exactly { fetchList, fetchDetail } — no write operation', () => {
    const seam = createHistoryFetch(async () => ({ ok: true, body: makeListBody() }));
    expect(Object.keys(seam).sort()).toEqual(['fetchDetail', 'fetchList']);
  });
  it('a non-ok response rejects with the parsed envelope (both reads)', async () => {
    const seam = createHistoryFetch(async () => ({ ok: false, body: errorEnvelope }));
    await expect(seam.fetchList(1, 20)).rejects.toEqual(errorEnvelope);
    await expect(seam.fetchDetail('dec-1')).rejects.toEqual(errorEnvelope);
  });
  it('a transport throw rejects with a synthesized envelope (both reads)', async () => {
    const seam = createHistoryFetch(async () => { throw new Error('offline'); });
    await expect(seam.fetchList(1, 20)).rejects.toEqual({
      error: { code: 'network_error', message: 'Unable to reach the server.', detail: {} },
    });
    await expect(seam.fetchDetail('dec-1')).rejects.toMatchObject({ error: { code: 'network_error' } });
  });
});
