import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// REFNOTOWN-1 / CAPFREE-1 (structural) — NO presentational component imports createOverrideFetch /
// overrideFetchSeam, so a re-fetch or commit is impossible from a presentational component: the
// transport-bearing seam is held ONLY by OverrideFormView (C1); the pure builders perform no I/O. The
// components/ directory is exactly the presentational set (C3–C8); C1 (the orchestrator) lives at the
// unit root, outside components/, and is the sole legitimate seam holder. Non-vacuous.
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const COMPONENTS = path.join(ROOT, 'components');
function walk(dir, acc) {
  for (const entry of readdirSync(dir)) {
    const full = path.join(dir, entry);
    if (statSync(full).isDirectory()) walk(full, acc);
    else if (/\.(js|jsx)$/.test(entry)) acc.push(full);
  }
  return acc;
}
const importLines = (src) => src.split('\n').filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l));
export function findSeamImport(src) {
  return importLines(src).some((l) => /createOverrideFetch|overrideFetchSeam/.test(l));
}
describe('REFNOTOWN-1 / CAPFREE-1 — no presentational component imports the seam', () => {
  const presentational = walk(COMPONENTS, []);
  it('no component under components/ imports createOverrideFetch/overrideFetchSeam', () => {
    expect(presentational.filter((f) => findSeamImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(findSeamImport("import { createOverrideFetch } from '../overrideFetchSeam.js';")).toBe(true);
    expect(findSeamImport("import { OVERRIDE_COPY } from '../copy.js';")).toBe(false);
  });
});
