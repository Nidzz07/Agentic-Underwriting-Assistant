import { describe, it, expect } from 'vitest';
import { readdirSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// NOTS-1 (NFR-UI-NOTS-1) — the unit is plain JS/JSX + React: zero .ts/.tsx files, no tsconfig.

const FRONTEND_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const IGNORE = new Set(['node_modules', 'coverage', '.git']);

function walk(dir, acc) {
  for (const entry of readdirSync(dir)) {
    if (IGNORE.has(entry)) continue;
    const full = path.join(dir, entry);
    if (statSync(full).isDirectory()) walk(full, acc);
    else acc.push(full);
  }
  return acc;
}

// The predicate under test — reused on synthetic inputs so the scan is non-vacuous.
function isTsArtifact(name) {
  return /\.tsx?$/.test(name) || /^tsconfig.*\.json$/.test(name);
}

describe('NFR-UI-NOTS-1 — no TypeScript in the frontend unit', () => {
  const files = walk(FRONTEND_ROOT, []);

  it('no_ts_files — zero .ts/.tsx files anywhere in the unit', () => {
    const offenders = files.filter((f) => /\.tsx?$/.test(path.basename(f)));
    expect(offenders).toEqual([]);
  });

  it('no_tsconfig — no tsconfig*.json in the unit', () => {
    const offenders = files.filter((f) => /^tsconfig.*\.json$/.test(path.basename(f)));
    expect(offenders).toEqual([]);
  });

  it('detector self-test — the predicate flags TS artifacts, passes JS (non-vacuous)', () => {
    expect(isTsArtifact('foo.ts')).toBe(true);
    expect(isTsArtifact('foo.tsx')).toBe(true);
    expect(isTsArtifact('tsconfig.json')).toBe(true);
    expect(isTsArtifact('foo.jsx')).toBe(false);
    expect(isTsArtifact('foo.js')).toBe(false);
  });
});
