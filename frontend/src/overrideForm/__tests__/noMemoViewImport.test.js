import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// REFNOTOWN-1 — ui-memo-view (frozen U6) is MIRRORED as a convention, NEVER imported. Non-vacuous.
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
export function findMemoViewImport(src) {
  return importLines(src).some((l) => /['"][^'"]*\/memoView\//.test(l));
}
describe('REFNOTOWN-1 — no ui-memo-view import', () => {
  it('no production module imports from src/memoView', () => {
    expect(walk(ROOT, []).filter((f) => findMemoViewImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(findMemoViewImport("import { MemoView } from '../../memoView/MemoView.jsx';")).toBe(true);
    expect(findMemoViewImport("import { Panel } from '../../shell/components/Panel.jsx';")).toBe(false);
  });
});
