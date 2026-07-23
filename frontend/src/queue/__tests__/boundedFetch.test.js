import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { buildQueueRequest, DEFAULT_PAGE_SIZE } from '../fetchSeam.js';

// PERF-1 (structural) — bounded-by-pagination: every request carries page+size (never an all-rows
// path); no production queue module makes a real network call (the seam transport is injected).
const QUEUE_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
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

describe('PERF-1 (structural) — bounded fetch, no real network', () => {
  it('every request is a single bounded page (page + size present)', () => {
    expect(buildQueueRequest(1).path).toMatch(/page=1/);
    expect(buildQueueRequest(1).path).toMatch(/size=/);
    expect(buildQueueRequest(5, DEFAULT_PAGE_SIZE).path).toContain(`size=${DEFAULT_PAGE_SIZE}`);
  });
  it('no production queue module issues a real fetch/axios/XHR (seam transport is injected)', () => {
    const files = walk(QUEUE_ROOT, []);
    expect(files.filter((f) => findRealFetch(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(findRealFetch("await fetch('/applications')")).toBe(true);
    expect(findRealFetch('const x = 1;')).toBe(false);
  });
});
