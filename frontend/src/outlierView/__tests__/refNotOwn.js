// Shared helper for the ui-outlier-view REFNOTOWN / StructuralGuard scans (test-only). Each guard
// lives in its own file (the frozen sibling convention) but they all walk the same production tree
// and inspect import lines. MIRRORS the frozen history/__tests__/refNotOwn.js — never imports it
// (BR-OUTV-10 / SCOPE-1: siblings are mirrored, not imported).
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const IGNORE = new Set(['__tests__']);

export function productionFiles(dir = ROOT, acc = []) {
  for (const entry of readdirSync(dir)) {
    if (IGNORE.has(entry)) continue;
    const full = path.join(dir, entry);
    if (statSync(full).isDirectory()) productionFiles(full, acc);
    else if (/\.(js|jsx)$/.test(entry)) acc.push(full);
  }
  return acc;
}

export function readSource(file) {
  return readFileSync(file, 'utf8');
}

// CG-OUTV-Fold-1 — strip comments BEFORE scanning. Every by-construction guarantee in this unit is
// documented by a MANDATORY header comment (NFR-ND-OUTV-Fold-1) that deliberately NAMES the construct
// it forbids ("no recommendation prop", "NO seed, NO corpus_version", "no request-body builder, no
// submit*"). A scan over raw text would flag the very prose that makes the guarantee self-evident.
// The guarantee is the absence of CODE, not of the words — the frozen ui-approval-gate singleCallSite
// / ui-history refNotOwn precedent.
export function stripComments(src) {
  return src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
}

// True iff any import statement resolves into the given src/<unit>/ tree.
export function makeUnitImportDetector(unit) {
  const pattern = new RegExp(`['"][^'"]*\\/${unit}\\/`);
  return function findUnitImport(src) {
    return src
      .split('\n')
      .filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l))
      .some((l) => pattern.test(l));
  };
}
