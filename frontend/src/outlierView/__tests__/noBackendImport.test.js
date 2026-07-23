import { describe, it, expect } from 'vitest';
import { productionFiles, readSource, stripComments } from './refNotOwn.js';

// NFR-OUTV-SCOPE-1 (P-OUTV-10) — the cross-language reference-not-own boundary (BR-OUTV-10).
// ui-outlier-view consumes the WIRE-1 R4 `outlier` slice BY SHAPE (Python -> React via API JSON);
// it imports no backend module and re-declares no schema. It performs no authorization decision
// either — that boundary is auth-rbac's, server-side.
//
// CG-OUTV-Fold-1: scanned over comment-stripped source.
export function findBackendImport(src) {
  return stripComments(src)
    .split('\n')
    .filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l))
    .some((l) => /['"][^'"]*(backend|outlier_model|audit_store|rules_engine|auth_rbac|intake|memo_agent_core)\//.test(l));
}
export function findClientAuthzCall(src) {
  const stripped = stripComments(src);
  return /\bauthorize\s*\(/.test(stripped) || /RBAC_[A-Z]+/.test(stripped);
}

describe('SCOPE-1 (structural) — no backend import, no client-side authz', () => {
  const files = productionFiles();

  it('the scan is over a non-empty production tree (guard against a vacuous pass)', () => {
    expect(files.length).toBeGreaterThan(0);
  });

  it('no production outlierView module imports a backend module', () => {
    expect(files.filter((f) => findBackendImport(readSource(f)))).toEqual([]);
  });

  it('no production outlierView module performs an authorization decision', () => {
    expect(files.filter((f) => findClientAuthzCall(readSource(f)))).toEqual([]);
  });

  it('detector self-tests (non-vacuous)', () => {
    expect(findBackendImport("import { OutlierResult } from '../../../backend/outlier_model/schemas.py';")).toBe(true);
    expect(findBackendImport("import { AuditRecord } from '../../../backend/audit_store/record_schema.py';")).toBe(true);
    expect(findBackendImport("import { Panel } from '../shell/components/Panel.jsx';")).toBe(false);
    expect(findClientAuthzCall('if (authorize(user, RBAC_COMMIT)) {}')).toBe(true);
    expect(findClientAuthzCall('const x = 1;')).toBe(false);
  });
});
