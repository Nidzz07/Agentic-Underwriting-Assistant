import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// REFNOTOWN-1 (NEW — the first sibling that must also not import the frozen U7) — ui-approval-gate
// (frozen U7) is MIRRORED as a convention, NEVER imported. ui-override-form re-realizes the sibling
// fetchSeam/StructuralGuard/by-construction patterns LOCALLY (the override/reason path), not by import.
// Non-vacuous.
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
const importLines = (src) => src.split('\n').filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l));
export function findApprovalGateImport(src) {
  return importLines(src).some((l) => /['"][^'"]*\/approvalGate\//.test(l));
}
describe('REFNOTOWN-1 — no ui-approval-gate import (NEW)', () => {
  it('no production module imports from src/approvalGate', () => {
    expect(walk(ROOT, []).filter((f) => findApprovalGateImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('detector self-test (non-vacuous)', () => {
    expect(findApprovalGateImport("import { createCommitFetch } from '../../approvalGate/commitFetchSeam.js';")).toBe(true);
    expect(findApprovalGateImport("import { ApprovalGateView } from '../../approvalGate/ApprovalGateView.jsx';")).toBe(true);
    expect(findApprovalGateImport("import { Panel } from '../../shell/components/Panel.jsx';")).toBe(false);
  });
});
