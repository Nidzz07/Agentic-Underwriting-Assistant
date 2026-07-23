import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import * as seamModule from '../historyFetchSeam.js';

// FAITHFUL-1 (the LOAD-BEARING structural guarantee, full-highest) — INV-FAITHFUL / BR-HIST-3.
// This is the write-path units' single-call-site guard INVERTED TO ZERO CALL SITES: `ui-history` is a
// pure READ surface over an immutable forensic record, so NOTHING under src/history may mutate,
// commit or submit it. The by-construction design (P3: the seam's four-member GET-only export) is the
// primary safeguard; this scan is the regression guard on top of it.
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

// Strip comments before scanning: the guarantee is the absence of CODE, not of the words — the seam's
// self-evidence header comment (NFR-DESIGN-Fold-1) deliberately NAMES what may not exist here (the
// ui-approval-gate precedent).
function stripComments(src) {
  return src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
}

export function findSubmitFunctions(src) {
  return (stripComments(src).match(/\bsubmit[A-Z]\w*\s*[(=:]/g) || []).map((s) => s.trim());
}
export function findWriteBuilders(src) {
  return (stripComments(src).match(/\bbuild(Commit|Override|Approve)\w*Request\b/g) || []);
}
export function findNonGetMethods(src) {
  return (stripComments(src).match(/method\s*:\s*['"`](?!GET)\w+['"`]/gi) || []);
}
export function findRequestBody(src) {
  return (stripComments(src).match(/\bbody\s*:/g) || []);
}

const files = walk(ROOT, []);

describe('FAITHFUL-1 — noWriteSeam: ZERO write-capable call sites under src/history', () => {
  it('no production module defines or invokes a submit* function', () => {
    const hits = files.flatMap((f) => findSubmitFunctions(readFileSync(f, 'utf8')).map((h) => `${path.basename(f)}: ${h}`));
    expect(hits).toEqual([]);
  });

  it('no production module defines a buildCommitRequest / buildOverrideRequest analog', () => {
    const hits = files.flatMap((f) => findWriteBuilders(readFileSync(f, 'utf8')));
    expect(hits).toEqual([]);
  });

  it('no production module builds a non-GET request, or any request carrying a body', () => {
    const methodHits = files.flatMap((f) => findNonGetMethods(readFileSync(f, 'utf8')));
    const bodyHits = files.flatMap((f) => findRequestBody(readFileSync(f, 'utf8')));
    expect(methodHits).toEqual([]);
    expect(bodyHits).toEqual([]);
  });

  it('the seam exports EXACTLY the four read members — no fifth, write-capable member', () => {
    expect(Object.keys(seamModule).sort()).toEqual([
      'buildHistoryDetailRequest',
      'buildHistoryListRequest',
      'createHistoryFetch',
      'normalizeError',
    ]);
  });

  it('both builders return ONLY { method: GET, path }', () => {
    const list = seamModule.buildHistoryListRequest(1, 20);
    const detail = seamModule.buildHistoryDetailRequest('dec-1');
    for (const req of [list, detail]) {
      expect(Object.keys(req).sort()).toEqual(['method', 'path']);
      expect(req.method).toBe('GET');
    }
  });

  it('createHistoryFetch yields exactly { fetchList, fetchDetail } — two reads, no write op', () => {
    const seam = seamModule.createHistoryFetch(async () => ({ ok: true, body: {} }));
    expect(Object.keys(seam).sort()).toEqual(['fetchDetail', 'fetchList']);
  });

  it('detector self-tests (non-vacuous)', () => {
    expect(findSubmitFunctions('await seam.submitOverride(id, reason);')).toEqual(['submitOverride(']);
    expect(findSubmitFunctions('export function submitApprove(id) {}')).toEqual(['submitApprove(']);
    expect(findSubmitFunctions('const x = 1;')).toEqual([]);
    expect(findWriteBuilders('function buildCommitRequest(id) {}')).toEqual(['buildCommitRequest']);
    expect(findWriteBuilders('function buildHistoryListRequest(p, s) {}')).toEqual([]);
    expect(findNonGetMethods("return { method: 'POST', path: '/x' };")).toHaveLength(1);
    expect(findNonGetMethods("return { method: 'GET', path: '/x' };")).toEqual([]);
    expect(findRequestBody("return { method: 'POST', path: '/x', body: { a: 1 } };")).toHaveLength(1);
    // a comment naming the forbidden construct must NOT trip the scan (the seam's header comment does).
    expect(findSubmitFunctions('// there is deliberately no submitOverride( here')).toEqual([]);
    expect(findNonGetMethods("/* no method: 'POST' builder exists */")).toEqual([]);
  });
});

describe('FAITHFUL-1 — no edit affordance / mutation seam in any region', () => {
  it('no production module imports a commit/write seam from anywhere', () => {
    const hits = files.filter((f) => {
      const importLines = readFileSync(f, 'utf8').split('\n').filter((l) => /^\s*import\b/.test(l));
      return importLines.some((l) => /commitFetchSeam|overrideFetchSeam|createCommitFetch|createOverrideFetch/.test(l));
    });
    expect(hits).toEqual([]);
  });
});
