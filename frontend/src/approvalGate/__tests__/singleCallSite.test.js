import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// NOFINAL-1 (structural, P1) — the commit trigger has EXACTLY ONE invocation site of
// `submitApprove`, and it lives in ApprovalGateView (the sole seam holder); ApproveAffordance holds no
// commit capability. This is the by-construction single-call-site guarantee, scanned.
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
export function countSubmitInvocations(src) {
  return (src.match(/\.submitApprove\s*\(/g) || []).length;
}

describe('NOFINAL-1 — single-call-site commit', () => {
  const files = walk(ROOT, []);
  it('.submitApprove( is invoked exactly once across production source', () => {
    const total = files.reduce((n, f) => n + countSubmitInvocations(readFileSync(f, 'utf8')), 0);
    expect(total).toBe(1);
  });
  it('the single invocation lives in ApprovalGateView.jsx', () => {
    const view = files.find((f) => f.endsWith('ApprovalGateView.jsx'));
    expect(countSubmitInvocations(readFileSync(view, 'utf8'))).toBe(1);
  });
  it('ApproveAffordance INVOKES no submitApprove and IMPORTS no seam (no commit capability)', () => {
    // The by-construction guarantee is the absence of a call site + seam import — NOT the absence of
    // the word, which appears in the component's self-evidence header comment (ND-Fold-1) documenting
    // exactly what it may not hold. So we scan for an invocation `.submitApprove(` and for a seam
    // import, both of which must be zero.
    const aff = files.find((f) => f.endsWith('ApproveAffordance.jsx'));
    const src = readFileSync(aff, 'utf8');
    const importLines = src.split('\n').filter((l) => /^\s*import\b/.test(l));
    expect(countSubmitInvocations(src)).toBe(0);
    expect(importLines.some((l) => /commitFetchSeam|createCommitFetch/.test(l))).toBe(false);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(countSubmitInvocations('await seam.submitApprove(id);')).toBe(1);
    expect(countSubmitInvocations('const x = 1;')).toBe(0);
  });
});
