import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// REFNOTOWN-1 (structural, P9) — reference-not-own guards, each non-vacuous (detector self-test):
//  - no backend import (this is a frontend unit; the real gate/persistence is server-side);
//  - ui-queue + ui-memo-view are MIRRORED as a convention, NEVER imported (both frozen);
//  - no router/navigation import;
//  - ND-Fold-3: no PRESENTATIONAL component imports createCommitFetch / commitFetchSeam — so a
//    re-fetch is impossible from a presentational component (the transport-bearing seam is held only
//    by ApprovalGateView; the pure builders perform no I/O).
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const COMPONENTS = path.join(ROOT, 'components');
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

export function findBackendImport(src) {
  return importLines(src).some((l) => /['"][^'"]*\/backend\//.test(l) || /['"]backend[./]/.test(l));
}
export function findQueueImport(src) {
  return importLines(src).some((l) => /['"][^'"]*\/queue\//.test(l));
}
export function findMemoViewImport(src) {
  return importLines(src).some((l) => /['"][^'"]*\/memoView\//.test(l));
}
export function findRouterImport(src) {
  return importLines(src).some((l) => /router|navigate|\bhistory\b/i.test(l));
}
export function findSeamImport(src) {
  return importLines(src).some((l) => /createCommitFetch|commitFetchSeam/.test(l));
}

describe('REFNOTOWN-1 — reference-not-own import guards', () => {
  const production = walk(ROOT, []);
  const presentational = walk(COMPONENTS, []);

  it('no production module imports a backend module', () => {
    expect(production.filter((f) => findBackendImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('no production module imports from src/queue (mirrored, never imported)', () => {
    expect(production.filter((f) => findQueueImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('no production module imports from src/memoView (mirrored, never imported)', () => {
    expect(production.filter((f) => findMemoViewImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('no production module imports a router/navigation module', () => {
    expect(production.filter((f) => findRouterImport(readFileSync(f, 'utf8')))).toEqual([]);
  });
  it('ND-Fold-3: no presentational component imports createCommitFetch/commitFetchSeam', () => {
    expect(presentational.filter((f) => findSeamImport(readFileSync(f, 'utf8')))).toEqual([]);
  });

  it('detector self-tests (non-vacuous)', () => {
    expect(findBackendImport("import { X } from '../../backend/foo.js';")).toBe(true);
    expect(findQueueImport("import { createQueueFetch } from '../../queue/fetchSeam.js';")).toBe(true);
    expect(findMemoViewImport("import { MemoView } from '../../memoView/MemoView.jsx';")).toBe(true);
    expect(findRouterImport("import { useNavigate } from 'react-router-dom';")).toBe(true);
    expect(findSeamImport("import { createCommitFetch } from '../commitFetchSeam.js';")).toBe(true);
    const clean = "import { Panel } from '../../shell/components/Panel.jsx';";
    expect(findBackendImport(clean) || findQueueImport(clean) || findMemoViewImport(clean) || findRouterImport(clean) || findSeamImport(clean)).toBe(false);
  });
});
