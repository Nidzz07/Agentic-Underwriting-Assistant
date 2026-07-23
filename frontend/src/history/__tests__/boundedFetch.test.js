import { describe, it, expect } from 'vitest';
import { productionFiles, readSource, stripComments } from './refNotOwn.js';
import { buildHistoryListRequest, buildHistoryDetailRequest } from '../historyFetchSeam.js';

// PERF-1 (structural; observed/non-gating for latency) — BOUNDED reads. R6 fetches exactly ONE page
// by (page, size) — never an all-rows path; R7 fetches exactly ONE record by decision_id. There is
// deliberately NO per-row R7 enrichment (the N+1 the Q4-A design avoids: it is precisely why the R6
// list omits the system recommendation and the detail is the only source of it).
export function findRealNetwork(src) {
  const code = stripComments(src);
  return /\bfetch\s*\(/.test(code) || /\baxios\b/.test(code) || /XMLHttpRequest/.test(code);
}
export function findDetailFetchInAList(src) {
  // a fetchDetail call inside a .map(...) row projection would be the N+1 shape.
  return /\.map\s*\([^)]*\)[\s\S]{0,400}?fetchDetail\s*\(/.test(stripComments(src));
}

describe('PERF-1 (structural) — bounded reads, no all-rows path, no N+1 enrichment', () => {
  const files = productionFiles();

  it('the R6 request targets exactly ONE page, with both bounds always present', () => {
    expect(buildHistoryListRequest(2, 20).path).toBe('/decisions?page=2&size=20');
    expect(buildHistoryListRequest(2, 20).path).toContain('page=');
    expect(buildHistoryListRequest(2, 20).path).toContain('size=');
  });

  it('the R7 request targets exactly ONE record by id (no query string, no list path)', () => {
    expect(buildHistoryDetailRequest('dec-21').path).toBe('/decisions/dec-21');
    expect(buildHistoryDetailRequest('dec-21').path).not.toContain('?');
  });

  it('no production history module issues a real fetch/axios/XHR (the transport is injected)', () => {
    expect(files.filter((f) => findRealNetwork(readSource(f)))).toEqual([]);
  });

  it('no production history module fetches a detail per row (no N+1 enrichment)', () => {
    expect(files.filter((f) => findDetailFetchInAList(readSource(f)))).toEqual([]);
  });

  it('detector self-tests (non-vacuous)', () => {
    expect(findRealNetwork("await fetch('/decisions?page=1&size=20')")).toBe(true);
    expect(findRealNetwork('const x = 1;')).toBe(false);
    expect(findDetailFetchInAList('items.map((i) => fetchDetail(i.decision_id))')).toBe(true);
    expect(findDetailFetchInAList('items.map((i) => i.decision_id)')).toBe(false);
    // prose describing the bounded read must NOT trip the scan (the header comments say "fetch").
    expect(findRealNetwork('// a bounded single-page R6 fetch (PERF-1)')).toBe(false);
    expect(findDetailFetchInAList('/* never items.map((i) => fetchDetail(i.decision_id)) */')).toBe(false);
  });
});
