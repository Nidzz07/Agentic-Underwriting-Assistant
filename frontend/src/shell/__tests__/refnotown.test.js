import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// REFNOTOWN-1 (NFR-UI-REFNOTOWN-1) — ui-shell imports NO backend production module (cross-language:
// no Python/backend path) and makes NO real network fetch. It fetches nothing real (WIRE-1 held).

const SHELL_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
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

// Detector: a backend import in a source string (scan import statements only, not comments).
const BACKEND = /backend|auth_rbac|rules_engine|audit_store|memo_agent_core|secrets_config/;
export function findBackendImport(src) {
  return src
    .split('\n')
    .filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l))
    .some((l) => BACKEND.test(l));
}
// Detector: a real network call.
export function findRealFetch(src) {
  return /\bfetch\s*\(/.test(src) || /\baxios\b/.test(src) || /XMLHttpRequest/.test(src);
}

describe('NFR-UI-REFNOTOWN-1 — reference-not-own + WIRE-1 held', () => {
  const files = walk(SHELL_ROOT, []);

  it('no_backend_import — no shell module imports a backend path', () => {
    const offenders = files.filter((f) => findBackendImport(readFileSync(f, 'utf8')));
    expect(offenders).toEqual([]);
  });

  it('no_real_fetch — no shell module issues a real fetch/axios/XHR', () => {
    const offenders = files.filter((f) => findRealFetch(readFileSync(f, 'utf8')));
    expect(offenders).toEqual([]);
  });

  it('detects_synthetic_violation — detectors are non-vacuous', () => {
    expect(findBackendImport("import x from '../../backend/api.js';")).toBe(true);
    expect(findBackendImport("import { Role } from 'auth_rbac';")).toBe(true);
    expect(findBackendImport("import { useCurrentRole } from '../session/roleContext.js';")).toBe(false);
    expect(findRealFetch("await fetch('/api/queue')")).toBe(true);
    expect(findRealFetch('const x = 1;')).toBe(false);
  });
});
