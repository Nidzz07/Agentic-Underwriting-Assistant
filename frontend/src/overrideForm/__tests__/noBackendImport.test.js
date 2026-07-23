import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// RBAC-1 (structural half) + REFNOTOWN-1 — no production module imports a backend module, and no
// production module calls a client-side authorization function (RoleGate is cosmetic; AUTHZ-1 is the
// server's). Each detector is non-vacuous (self-test).
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
const importLines = (src) => src.split('\n').filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l));

export function findBackendImport(src) {
  return importLines(src).some((l) => /['"][^'"]*\/backend\//.test(l) || /['"]backend[./]/.test(l));
}
export function findAuthzCall(src) {
  // client-side authorization is FORBIDDEN — the UI RoleGate is cosmetic, the server is authoritative.
  return /\bauthorize\s*\(/.test(src) || /\bhasPermission\s*\(/.test(src) || /PERMISSION_MATRIX\b/.test(src);
}

describe('RBAC-1 / REFNOTOWN-1 — no backend import, no client-side authz call', () => {
  const production = walk(ROOT, []);
  it('no production module imports a backend module', () => {
    expect(production.filter((f) => findBackendImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('no production module makes a client-side authorization decision', () => {
    expect(production.filter((f) => findAuthzCall(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-tests (non-vacuous)', () => {
    expect(findBackendImport("import { X } from '../../backend/foo.js';")).toBe(true);
    expect(findBackendImport("import { Panel } from '../../shell/components/Panel.jsx';")).toBe(false);
    expect(findAuthzCall('if (authorize(user, RBAC_COMMIT)) {}')).toBe(true);
    expect(findAuthzCall('const x = 1;')).toBe(false);
  });
});
