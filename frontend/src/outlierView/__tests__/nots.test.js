import { describe, it, expect } from 'vitest';
import { readdirSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// NFR-OUTV-NOTS-1 (FR-UI-5 / D-INH-1) — ui-outlier-view is plain JS/JSX: zero .ts/.tsx under
// src/outlierView, no TS config.
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

function walk(dir, acc) {
  for (const entry of readdirSync(dir)) {
    const full = path.join(dir, entry);
    if (statSync(full).isDirectory()) walk(full, acc);
    else acc.push(full);
  }
  return acc;
}
function isTsArtifact(name) { return /\.tsx?$/.test(name) || /^tsconfig.*\.json$/.test(name); }

describe('NOTS-1 — no TypeScript in ui-outlier-view', () => {
  const files = walk(ROOT, []);

  it('the walk found files (guard against a vacuous pass)', () => {
    expect(files.length).toBeGreaterThan(0);
  });

  it('zero .ts/.tsx files under src/outlierView', () => {
    expect(files.filter((f) => /\.tsx?$/.test(path.basename(f)))).toEqual([]);
  });

  it('no tsconfig under src/outlierView', () => {
    expect(files.filter((f) => /^tsconfig.*\.json$/.test(path.basename(f)))).toEqual([]);
  });

  it('detector self-test (non-vacuous)', () => {
    expect(isTsArtifact('x.ts')).toBe(true);
    expect(isTsArtifact('x.tsx')).toBe(true);
    expect(isTsArtifact('tsconfig.json')).toBe(true);
    expect(isTsArtifact('x.jsx')).toBe(false);
    expect(isTsArtifact('x.js')).toBe(false);
  });
});
