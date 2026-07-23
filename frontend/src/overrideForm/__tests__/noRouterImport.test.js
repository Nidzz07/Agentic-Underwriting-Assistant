import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// REFNOTOWN-1 — this unit is a self-contained view; it imports no router/navigation module (the
// composition root owns routing). Non-vacuous.
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
export function findRouterImport(src) {
  return importLines(src).some((l) => /router|navigate|\bhistory\b/i.test(l));
}
describe('REFNOTOWN-1 — no router/navigation import', () => {
  it('no production module imports a router/navigation module', () => {
    expect(walk(ROOT, []).filter((f) => findRouterImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(findRouterImport("import { useNavigate } from 'react-router-dom';")).toBe(true);
    expect(findRouterImport("import { Panel } from '../../shell/components/Panel.jsx';")).toBe(false);
  });
});
