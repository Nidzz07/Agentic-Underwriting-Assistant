import { describe, it, expect } from 'vitest';
import { productionFiles, readSource, stripComments } from './refNotOwn.js';
import * as fetchSeamModule from '../fetchSeam.js';

// NFR-OUTV-VIEWONLY-1 (P-OUTV-8) + FETCH-1 (P-OUTV-6) — the write path is STRUCTURALLY ABSENT, not
// merely unused (BR-OUTV-4). No RoleGate, no router, no commit/POST, no request-body builder.
//
// CG-OUTV-Fold-1: the fetchSeam header comment deliberately says "no request-body builder, no
// submit*" — a raw scan would flag that prose. Stripped first; the guarantee is absent CODE.

export function findWriteVerb(src) {
  const stripped = stripComments(src);
  return /['"]POST['"]/.test(stripped)
    || /['"]PUT['"]/.test(stripped)
    || /['"]PATCH['"]/.test(stripped)
    || /['"]DELETE['"]/.test(stripped)
    || /\bsubmit[A-Z_]/.test(stripped)
    || /\bbuild\w*RequestBody\b/.test(stripped);
}
export function findRoleGateImport(src) {
  return stripComments(src)
    .split('\n')
    .filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l))
    .some((l) => /\bRoleGate\b/.test(l));
}
export function findRouterImport(src) {
  return stripComments(src)
    .split('\n')
    .filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l))
    .some((l) => /['"](react-router|react-router-dom|wouter|@reach\/router)['"]/.test(l));
}

describe('VIEWONLY-1 — no write path anywhere in the unit', () => {
  const files = productionFiles();

  it('the scan is over a non-empty production tree (guard against a vacuous pass)', () => {
    expect(files.length).toBeGreaterThan(0);
  });

  it('no production module contains a write verb, submit* or body builder', () => {
    expect(files.filter((f) => findWriteVerb(readSource(f)))).toEqual([]);
  });

  it('no production module imports RoleGate', () => {
    expect(files.filter((f) => findRoleGateImport(readSource(f)))).toEqual([]);
  });

  it('no production module imports a router', () => {
    expect(files.filter((f) => findRouterImport(readSource(f)))).toEqual([]);
  });

  // The seam's public surface is read-only BY CONSTRUCTION: there is no submit*/write export to call.
  it('fetchSeam exports no write/submit function at all', () => {
    expect(Object.keys(fetchSeamModule).sort()).toEqual([
      'buildOutlierRequest',
      'createOutlierFetch',
      'normalizeError',
    ]);
    for (const name of Object.keys(fetchSeamModule)) {
      expect(name).not.toMatch(/submit|post|write|commit|save|update/i);
    }
  });

  it('buildOutlierRequest can only ever emit GET (no method/body parameter exists)', () => {
    expect(fetchSeamModule.buildOutlierRequest.length).toBe(1);   // applicationId only
    expect(fetchSeamModule.buildOutlierRequest('x').method).toBe('GET');
  });

  it('detector self-tests (non-vacuous)', () => {
    expect(findWriteVerb("const r = { method: 'POST', path: p, body };")).toBe(true);
    expect(findWriteVerb('export function submitCommit(id) {}')).toBe(true);
    expect(findWriteVerb('export function buildCommitRequestBody(x) {}')).toBe(true);
    expect(findWriteVerb("const r = { method: 'GET', path: p };")).toBe(false);

    expect(findRoleGateImport("import { RoleGate } from '../shell/components/RoleGate.jsx';")).toBe(true);
    expect(findRoleGateImport("import { Panel } from '../shell/components/Panel.jsx';")).toBe(false);

    expect(findRouterImport("import { useNavigate } from 'react-router-dom';")).toBe(true);
    expect(findRouterImport("import { useState } from 'react';")).toBe(false);
  });
});
