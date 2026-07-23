import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// NOFINAL-1 (structural, P1) — the commit trigger has EXACTLY ONE invocation site of
// `submitOverride`, and it lives in OverrideFormView (the sole seam holder); OverrideAffordance holds
// no commit capability. This is the by-construction single-call-site guarantee, scanned. Header
// comments naming `submitOverride` do NOT trip it (it scans invocations `.submitOverride(`, not the word).
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
  return (src.match(/\.submitOverride\s*\(/g) || []).length;
}
export function countReasonPredicateUses(src) {
  return (src.match(/isReasonPresent\s*\(/g) || []).length;
}

describe('NOFINAL-1 — single-call-site commit', () => {
  const files = walk(ROOT, []);
  it('.submitOverride( is invoked exactly once across production source', () => {
    const total = files.reduce((n, f) => n + countSubmitInvocations(readFileSync(f, 'utf8')), 0);
    expect(total).toBe(1);
  });
  it('the single invocation lives in OverrideFormView.jsx', () => {
    const view = files.find((f) => f.endsWith('OverrideFormView.jsx'));
    expect(countSubmitInvocations(readFileSync(view, 'utf8'))).toBe(1);
  });
  it('OverrideAffordance INVOKES no submitOverride and IMPORTS no seam (no commit capability)', () => {
    const aff = files.find((f) => f.endsWith('OverrideAffordance.jsx'));
    const src = readFileSync(aff, 'utf8');
    const importLines = src.split('\n').filter((l) => /^\s*import\b/.test(l));
    expect(countSubmitInvocations(src)).toBe(0);
    expect(importLines.some((l) => /overrideFetchSeam|createOverrideFetch/.test(l))).toBe(false);
  });
  it('belt-and-suspenders (ND-OVR-Fold-i): the ONE isReasonPresent predicate is reused (derived disabled + onConfirm re-check)', () => {
    // Non-vacuous check that the belt-and-suspenders re-check is present (P2): the single predicate is
    // referenced at least twice in the view — the affordance-disabled derivation AND the onConfirm guard.
    const view = files.find((f) => f.endsWith('OverrideFormView.jsx'));
    expect(countReasonPredicateUses(readFileSync(view, 'utf8'))).toBeGreaterThanOrEqual(2);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(countSubmitInvocations('await seam.submitOverride(id, reason);')).toBe(1);
    expect(countSubmitInvocations('const x = 1;')).toBe(0);
    expect(countReasonPredicateUses('disabled={!isReasonPresent(reason)}; if (isReasonPresent(reason)) {}')).toBe(2);
  });
});
