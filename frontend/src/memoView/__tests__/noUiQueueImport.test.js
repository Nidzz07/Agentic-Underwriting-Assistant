import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// SCOPE-1 (structural) — ui-queue's fetchSeam/StructuralGuard/testid-lint are MIRRORED as a
// convention, NEVER imported. This guard proves no production memoView module imports from src/queue
// (the two sibling UI units stay decoupled; ui-queue is frozen).
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
export function findQueueImport(src) {
  return src
    .split('\n')
    .filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l))
    .some((l) => /['"][^'"]*\/queue\//.test(l));
}

describe('SCOPE-1 (structural) — ui-queue is mirrored, never imported', () => {
  const files = walk(MEMO_ROOT, []);
  it('no production memoView module imports from src/queue', () => {
    expect(files.filter((f) => findQueueImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(findQueueImport("import { createQueueFetch } from '../../queue/fetchSeam.js';")).toBe(true);
    expect(findQueueImport("import { Panel } from '../shell/components/Panel.jsx';")).toBe(false);
  });
});
