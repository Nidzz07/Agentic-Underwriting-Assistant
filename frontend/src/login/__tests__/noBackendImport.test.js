import { describe, it, expect } from 'vitest';
import { productionFiles, readSource, stripComments } from './refNotOwn.js';

// SCOPE-1 — the login unit imports no backend module, re-declares no schema, and performs no
// client-side authorization. It consumes WIRE-1 R8/R9 BY SHAPE only.
export function findBackendImport(src) {
  return stripComments(src)
    .split('\n')
    .filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l))
    .some((l) => /['"][^'"]*(backend|authn|auth_rbac|audit_store|rules_engine|intake)\//.test(l));
}
export function findClientAuthzCall(src) {
  const code = stripComments(src);
  return /\bauthorize\s*\(/.test(code) || /RBAC_[A-Z]+/.test(code);
}

describe('SCOPE-1 (structural) — no backend import, no client-side authz', () => {
  const files = productionFiles();

  it('no production file imports a backend module or decides authorization', () => {
    expect(files.length).toBeGreaterThan(0);
    expect(files.filter((f) => findBackendImport(readSource(f)))).toEqual([]);
    expect(files.filter((f) => findClientAuthzCall(readSource(f)))).toEqual([]);
    // detector self-tests (non-vacuous)
    expect(findBackendImport("import x from '../../backend/authn/service.js';")).toBe(true);
    expect(findClientAuthzCall('if (authorize(user, RBAC_COMMIT)) {}')).toBe(true);
    expect(findBackendImport("import { Panel } from '../shell/components/Panel.jsx';")).toBe(false);
  });
});
