import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// VIEWONLY-1 (structural) — ui-memo-view emits nothing and imports NO router/navigation module.
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
export function findRouterImport(src) {
  return src
    .split('\n')
    .filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l))
    .some((l) => /router|navigate|\bhistory\b/i.test(l));
}

describe('VIEWONLY-1 (structural) — no router/navigation import', () => {
  const files = walk(MEMO_ROOT, []);
  it('no production memoView module imports a router/navigation module', () => {
    expect(files.filter((f) => findRouterImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(findRouterImport("import { useNavigate } from 'react-router-dom';")).toBe(true);
    expect(findRouterImport("import { NarrativeRegion } from './NarrativeRegion.jsx';")).toBe(false);
  });
});
