import { describe, it, expect } from 'vitest';
import { productionFiles, readSource, stripComments } from './refNotOwn.js';

// PERF-1 (structural) — the login unit makes NO real network call of its own. Like every sibling
// seam it builds requests and normalizes failures; the transport is injected at the composition
// root. It also stores nothing: no localStorage/sessionStorage/document.cookie anywhere.
export function findRealNetwork(src) {
  const code = stripComments(src);
  return /\bfetch\s*\(/.test(code) || /\baxios\b/.test(code) || /XMLHttpRequest/.test(code);
}
export function findClientSideCredentialStorage(src) {
  // ⚑ The session is an HttpOnly cookie the browser manages. Any localStorage/cookie handling
  // here would mean the unit was keeping credential material JavaScript can read.
  const code = stripComments(src);
  return /localStorage|sessionStorage|document\.cookie/.test(code);
}

describe('PERF-1 / credential hygiene (structural)', () => {
  const files = productionFiles();

  it('no real network call, and no client-side credential storage', () => {
    expect(files.length).toBeGreaterThan(0);
    expect(files.filter((f) => findRealNetwork(readSource(f)))).toEqual([]);
    expect(files.filter((f) => findClientSideCredentialStorage(readSource(f)))).toEqual([]);
    // detector self-tests
    expect(findRealNetwork('await fetch("/login")')).toBe(true);
    expect(findClientSideCredentialStorage('localStorage.setItem("t", token)')).toBe(true);
    expect(findRealNetwork('transport(request)')).toBe(false);
  });
});
