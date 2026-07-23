import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// REFNOTOWN / DUALREAD-1 (structural) — the master-detail navigation is INTERNAL HistoryView state,
// not a route. ui-history imports no router and emits nothing upward (contrast ui-queue's onSelect
// hand-off to a DIFFERENT unit; here the audit tuple belongs to history itself, so the detail is
// kept in-unit — BR-HIST-4).
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
export function findRouterImport(src) {
  return src
    .split('\n')
    .filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l))
    .some((l) => /react-router|wouter|next\/(router|link|navigation)|@reach\/router|history\/browser/.test(l));
}

describe('DUALREAD-1 (structural) — no router import', () => {
  const files = walk(ROOT, []);
  it('no production history module imports a router', () => {
    expect(files.filter((f) => findRouterImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(findRouterImport("import { useNavigate } from 'react-router-dom';")).toBe(true);
    expect(findRouterImport("import { useRouter } from 'next/router';")).toBe(true);
    expect(findRouterImport("import { Panel } from '../shell/components/Panel.jsx';")).toBe(false);
  });
});
