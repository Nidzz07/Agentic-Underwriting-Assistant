import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// SELECT-1 (structural) — ui-queue emits onSelect only; it imports NO router/navigation module.
const QUEUE_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
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

describe('SELECT-1 (structural) — no router/navigation import', () => {
  const files = walk(QUEUE_ROOT, []);
  it('no production queue module imports a router/navigation module', () => {
    expect(files.filter((f) => findRouterImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(findRouterImport("import { useNavigate } from 'react-router-dom';")).toBe(true);
    expect(findRouterImport("import { QueueRow } from './QueueRow.jsx';")).toBe(false);
  });
});
