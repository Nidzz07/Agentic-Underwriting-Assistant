import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { buildMemoRequest } from '../memoFetchSeam.js';

// PERF-1 (structural) — single bounded resource: the seam builds a request for exactly ONE memo by
// applicationId (never a list/all-rows path); no production memoView module makes a real network call
// (the seam transport is injected).
const MEMO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const IGNORE = new Set(['__tests__']);

function walk(dir, acc) {
  for (const entry of readdirSync(dir)) {
    if (IGNORE.has(entry)) continue;
    const full = path.join(dir, entry);
    if (statSync(full).isDirectory()) walk(full, acc);
    else if (/\.(js|jsx)$/.test(entry)) acc.push(full);
  }
  return acc;
}
function findRealFetch(src) {
  return /\bfetch\s*\(/.test(src) || /\baxios\b/.test(src) || /XMLHttpRequest/.test(src);
}

describe('PERF-1 (structural) — bounded single-resource fetch, no real network', () => {
  it('the request targets a single memo by applicationId (no list/all-rows path, no query string)', () => {
    expect(buildMemoRequest('app-9').path).toBe('/applications/app-9/memo');
    expect(buildMemoRequest('app-9').path).not.toContain('?');
  });
  it('no production memoView module issues a real fetch/axios/XHR (seam transport is injected)', () => {
    const files = walk(MEMO_ROOT, []);
    expect(files.filter((f) => findRealFetch(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(findRealFetch("await fetch('/applications/x/memo')")).toBe(true);
    expect(findRealFetch('const x = 1;')).toBe(false);
  });
});
