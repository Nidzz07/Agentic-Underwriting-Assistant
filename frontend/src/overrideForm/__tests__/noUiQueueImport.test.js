import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// REFNOTOWN-1 — ui-queue (frozen U5) is MIRRORED as a convention, NEVER imported. Non-vacuous.
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
export function findQueueImport(src) {
  return importLines(src).some((l) => /['"][^'"]*\/queue\//.test(l));
}
describe('REFNOTOWN-1 — no ui-queue import', () => {
  it('no production module imports from src/queue', () => {
    expect(walk(ROOT, []).filter((f) => findQueueImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(findQueueImport("import { createQueueFetch } from '../../queue/fetchSeam.js';")).toBe(true);
    expect(findQueueImport("import { Panel } from '../../shell/components/Panel.jsx';")).toBe(false);
  });
});
