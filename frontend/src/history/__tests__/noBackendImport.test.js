import { describe, it, expect } from 'vitest';
import { productionFiles, readSource } from './refNotOwn.js';

// REFNOTOWN / SCOPE-1 (structural) — the cross-language reference-not-own boundary. ui-history
// consumes the WIRE-1 R6/R7 + audit_store `AuditRecord` shapes BY SHAPE (Python -> React via API
// JSON); it imports no backend module and re-declares no schema. It also performs no client-side
// authorization: the auditor read-only distinction is auth-rbac's, server-side (SEC-4).
export function findBackendImport(src) {
  return src
    .split('\n')
    .filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l))
    .some((l) => /['"][^'"]*(backend|audit_store|rules_engine|auth_rbac|intake|memo_agent_core)\//.test(l));
}
export function findClientAuthzCall(src) {
  return /\bauthorize\s*\(/.test(src) || /RBAC_[A-Z]+/.test(src);
}

describe('SCOPE-1 (structural) — no backend import, no client-side authz', () => {
  const files = productionFiles();
  it('no production history module imports a backend module', () => {
    expect(files.filter((f) => findBackendImport(readSource(f)))).toEqual([]);
  });
  it('no production history module performs an authorization decision', () => {
    expect(files.filter((f) => findClientAuthzCall(readSource(f)))).toEqual([]);
  });
  it('detector self-tests (non-vacuous)', () => {
    expect(findBackendImport("import { AuditRecord } from '../../../backend/audit_store/record_schema.py';")).toBe(true);
    expect(findBackendImport("import { Panel } from '../shell/components/Panel.jsx';")).toBe(false);
    expect(findClientAuthzCall('if (authorize(user, RBAC_COMMIT)) {}')).toBe(true);
    expect(findClientAuthzCall('const x = 1;')).toBe(false);
  });
});
