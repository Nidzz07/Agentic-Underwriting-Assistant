import { describe, it, expect } from 'vitest';
import { readdirSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// NOTS-1 (FR-UI-5) — the login unit is plain JS/JSX: zero .ts/.tsx, no TS config.
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

describe('NOTS-1 — no TypeScript in the login unit', () => {
  const files = walk(ROOT, []);

  it('zero TS artifacts, over a non-empty walk (non-vacuous)', () => {
    expect(files.length).toBeGreaterThan(0);
    expect(files.filter((f) => isTsArtifact(path.basename(f)))).toEqual([]);
    // detector self-test
    expect(isTsArtifact('x.tsx')).toBe(true);
    expect(isTsArtifact('tsconfig.json')).toBe(true);
    expect(isTsArtifact('x.jsx')).toBe(false);
  });
});
