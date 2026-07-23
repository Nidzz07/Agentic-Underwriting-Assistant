import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { buildMemoRequest, buildOverrideRequest } from '../overrideFetchSeam.js';

// PERF-1 (structural) — bounded: R4 fetches one memo by applicationId, R5 posts one commit by
// recommendationId (never a list/all-rows path); no production module makes a real network call (the
// seam transport is injected).
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
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

describe('PERF-1 (structural) — bounded single-resource requests, no real network', () => {
  it('the R4 + R5 requests each target a single resource (no list/all-rows, no query string)', () => {
    expect(buildMemoRequest('app-9').path).toBe('/applications/app-9/memo');
    expect(buildMemoRequest('app-9').path).not.toContain('?');
    expect(buildOverrideRequest('rec-9', 'because').path).toBe('/recommendations/rec-9/commit');
    expect(buildOverrideRequest('rec-9', 'because').path).not.toContain('?');
  });
  it('no production overrideForm module issues a real fetch/axios/XHR (seam transport is injected)', () => {
    const files = walk(ROOT, []);
    expect(files.filter((f) => findRealFetch(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(findRealFetch("await fetch('/x')")).toBe(true);
    expect(findRealFetch('const x = 1;')).toBe(false);
  });
});
