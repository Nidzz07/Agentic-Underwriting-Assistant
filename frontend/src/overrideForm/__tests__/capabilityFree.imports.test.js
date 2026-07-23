import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// CAPFREE-1 (structural half, P9) — the capability-free components hold NO commit capability: neither
// OverrideReasonInput (the NEW capability-free component) nor OverrideAffordance imports the seam module
// or INVOKES submitOverride. Holding the reason *text* is not a commit capability (the refined
// invariant); a commit requires the trigger/seam, which lives only in OverrideConfirmDialog (onConfirm)
// and OverrideFormView. Header comments naming submitOverride do NOT trip it (it scans invocation +
// import, not the word). Non-vacuous.
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const COMPONENTS = path.join(ROOT, 'components');
const importLines = (src) => src.split('\n').filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l));
export function findSeamImport(src) {
  return importLines(src).some((l) => /createOverrideFetch|overrideFetchSeam/.test(l));
}
export function countSubmitInvocations(src) {
  return (src.match(/\.submitOverride\s*\(/g) || []).length;
}

describe('CAPFREE-1 — OverrideReasonInput / OverrideAffordance hold no commit capability', () => {
  for (const name of ['OverrideReasonInput.jsx', 'OverrideAffordance.jsx']) {
    it(`${name} imports no seam and invokes no submitOverride`, () => {
      const src = readFileSync(path.join(COMPONENTS, name), 'utf8');
      expect(findSeamImport(src)).toBe(false);
      expect(countSubmitInvocations(src)).toBe(0);
    });
  }
  it('detector self-tests (non-vacuous)', () => {
    expect(findSeamImport("import { createOverrideFetch } from '../overrideFetchSeam.js';")).toBe(true);
    expect(findSeamImport("import { RoleGate } from '../../shell/components/RoleGate.jsx';")).toBe(false);
    expect(countSubmitInvocations('await seam.submitOverride(id, reason);')).toBe(1);
    expect(countSubmitInvocations('onClick={onOverride}')).toBe(0);
  });
});
