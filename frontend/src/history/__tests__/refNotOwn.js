// Shared helper for the REFNOTOWN structural guards (test-only). Each sibling guard lives in its own
// file (the frozen convention) but they all walk the same production tree and inspect import lines.
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

// Strip comments before scanning. Every by-construction guarantee in this unit is documented by a
// header comment that deliberately NAMES the construct it forbids ("no request-body builder", `can="read"`
// is not used, "a bounded single-page R6 fetch"), so a scan over raw text would flag the very prose
// that makes the guarantee self-evident. The guarantee is the absence of CODE, not of the words —
// the frozen ui-approval-gate singleCallSite guard set this precedent.
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
