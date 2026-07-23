import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { stripComments } from './refNotOwn.js';

// VIEWONLY-1 (structural, P11) — ui-history composes NO RoleGate (contrast the frozen write-path
// units U7/U8, which wrap their act-affordance in RoleGate can="act"). A pure read surface has no
// act-affordance to gate, and `can="read"` is deliberately NOT used: it would cosmetically exclude
// `admin` (RoleGate's COSMETIC_CAPABILITIES has admin read:false), diverging from R6/R7's
// authenticated-any-role contract.
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
export function findRoleGateImport(src) {
  return src.split('\n').filter((l) => /^\s*import\b/.test(l)).some((l) => /RoleGate/.test(l));
}
export function findRoleGateUsage(src) {
  const code = stripComments(src);
  return /<RoleGate\b/.test(code) || /\bcan\s*=\s*["']read["']/.test(code);
}
export function findRoleRead(src) {
  return /\buseCurrentRole\s*\(/.test(stripComments(src));
}

describe('VIEWONLY-1 (structural) — no RoleGate composition, no Role read', () => {
  const files = walk(ROOT, []);
  it('no production history module imports RoleGate', () => {
    expect(files.filter((f) => findRoleGateImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('no production history module renders RoleGate or uses can="read"', () => {
    expect(files.filter((f) => findRoleGateUsage(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('no production history module reads the current Role', () => {
    expect(files.filter((f) => findRoleRead(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-tests (non-vacuous)', () => {
    expect(findRoleGateImport("import { RoleGate } from '../../shell/components/RoleGate.jsx';")).toBe(true);
    expect(findRoleGateImport("import { Panel } from '../shell/components/Panel.jsx';")).toBe(false);
    expect(findRoleGateUsage('<RoleGate can="read">{x}</RoleGate>')).toBe(true);
    expect(findRoleGateUsage('<section>{x}</section>')).toBe(false);
    expect(findRoleRead('const role = useCurrentRole();')).toBe(true);
    expect(findRoleRead('const x = 1;')).toBe(false);
    // prose explaining WHY can="read" is unused must NOT trip the scan (HistoryView's header says so).
    expect(findRoleGateUsage('// `can="read"` is deliberately NOT used — it would exclude admin')).toBe(false);
    expect(findRoleRead('/* reads no Role: never calls useCurrentRole() */')).toBe(false);
  });
});
