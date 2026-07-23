import { describe, it, expect } from 'vitest';
import { readdirSync, statSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { screen } from '@testing-library/react';
import { openDetail } from './fixtures.js';

// NOSUPERSEDE-1 (BR-HIST-11) — NO premature superseded/versioning handling. `status` is write-once
// `active` and `supersedes_decision_id` is ALWAYS null in Phase 1/2, so designing a superseded branch
// would be premature abstraction for a state that cannot occur (the OOS-7 / Phase-3 seam is
// named-not-designed). Both fields are DISPLAY-ONLY.
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
function stripComments(src) {
  return src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
}

// A branch/comparison keyed on the superseded value, in either operand order, incl. membership tests.
export function findSupersededBranch(src) {
  const code = stripComments(src);
  return [
    ...(code.match(/(===|==|!==|!=)\s*['"`]superseded['"`]/gi) || []),
    ...(code.match(/['"`]superseded['"`]\s*(===|==|!==|!=)/gi) || []),
    ...(code.match(/\.(includes|indexOf|match|startsWith)\s*\(\s*['"`]superseded['"`]/gi) || []),
    ...(code.match(/case\s+['"`]superseded['"`]/gi) || []),
  ];
}
// ANY read of the nullable self-FK — the view never dereferences, links or navigates it.
export function findSupersedesDeref(src) {
  return (stripComments(src).match(/supersedes_decision_id/g) || []);
}

const files = walk(ROOT, []);

describe('NOSUPERSEDE-1 — no superseded branch, no supersedes dereference, no version affordance', () => {
  it('no production module branches on the superseded status value', () => {
    const hits = files.flatMap((f) => findSupersededBranch(readFileSync(f, 'utf8')));
    expect(hits).toEqual([]);
  });

  it('no production module reads supersedes_decision_id at all', () => {
    const hits = files.flatMap((f) => findSupersedesDeref(readFileSync(f, 'utf8')));
    expect(hits).toEqual([]);
  });

  it('detector self-tests (non-vacuous)', () => {
    expect(findSupersededBranch("if (record.status === 'superseded') return null;")).toHaveLength(1);
    expect(findSupersededBranch("const stale = 'superseded' === status;")).toHaveLength(1);
    expect(findSupersededBranch("case 'superseded': break;")).toHaveLength(1);
    expect(findSupersededBranch('<span>{status}</span>')).toEqual([]);
    // a comment naming the deferred seam must NOT trip the scan.
    expect(findSupersededBranch("// no status === 'superseded' branch exists")).toEqual([]);
    expect(findSupersedesDeref('const prev = record.supersedes_decision_id;')).toHaveLength(1);
    expect(findSupersedesDeref('const s = record.status;')).toEqual([]);
  });
});

describe('NOSUPERSEDE-1 — status renders read-only', () => {
  it('history-detail-status renders the value verbatim, with no affordance attached', async () => {
    await openDetail('dec-21');
    const status = await screen.findByTestId('history-detail-status');
    expect(status).toHaveTextContent('active');
    expect(status.tagName).toBe('SPAN');
    expect(status.querySelector('button, a, input')).toBeNull();
    // no supersede/version control anywhere in the detail.
    expect(screen.queryByTestId('history-detail-supersedes')).toBeNull();
  });
});
