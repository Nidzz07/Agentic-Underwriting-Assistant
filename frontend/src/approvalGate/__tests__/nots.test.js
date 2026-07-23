import { describe, it, expect } from 'vitest';
import { readdirSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// NOTS-1 — ui-approval-gate is plain JS/JSX: zero .ts/.tsx under src/approvalGate.
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

describe('NOTS-1 — no TypeScript in ui-approval-gate', () => {
  const files = walk(ROOT, []);
  it('zero .ts/.tsx files under src/approvalGate', () => {
    expect(files.filter((f) => /\.tsx?$/.test(path.basename(f)))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(isTsArtifact('x.ts')).toBe(true);
    expect(isTsArtifact('x.tsx')).toBe(true);
    expect(isTsArtifact('x.jsx')).toBe(false);
    expect(isTsArtifact('x.js')).toBe(false);
  });
});
