// Shared helper for the login unit's structural scans (test-only). MIRRORS the frozen
// history/ and outlierView/ refNotOwn.js — never imports either (siblings are mirrored,
// not imported).
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

// Strip comments BEFORE scanning — this unit's header comments deliberately NAME the constructs
// they forbid ("never distinguish lockout", "does not decide who the user is"), and a raw-text
// scan would flag the very prose that makes the guarantee self-evident. The guarantee is the
// absence of CODE, not of the words (the frozen singleCallSite / refNotOwn precedent).
export function stripComments(src) {
  return src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
}
