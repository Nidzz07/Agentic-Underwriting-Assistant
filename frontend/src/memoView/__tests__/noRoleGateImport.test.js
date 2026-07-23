import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// VIEWONLY-1 (structural) — ui-memo-view composes NO RoleGate (contrast: U7/U8 will).
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
export function findRoleGateImport(src) {
  return src.split('\n').filter((l) => /^\s*import\b/.test(l)).some((l) => /RoleGate/.test(l));
}

describe('VIEWONLY-1 (structural) — no RoleGate composition', () => {
  const files = walk(MEMO_ROOT, []);
  it('no production memoView module imports RoleGate', () => {
    expect(files.filter((f) => findRoleGateImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(findRoleGateImport("import { RoleGate } from '../../shell/components/RoleGate.jsx';")).toBe(true);
    expect(findRoleGateImport("import { Panel } from '../shell/components/Panel.jsx';")).toBe(false);
  });
});
