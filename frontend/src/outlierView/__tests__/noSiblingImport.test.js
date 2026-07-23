import { describe, it, expect } from 'vitest';
import { productionFiles, readSource, makeUnitImportDetector, stripComments } from './refNotOwn.js';

// NFR-OUTV-SCOPE-1 (P-OUTV-10) — reference-not-own, the SIBLING half (BR-OUTV-10 / Q1-A).
// ui-outlier-view MIRRORS the sibling read-seam + StructuralGuard conventions; it imports NO sibling
// view module. The frozen sibling trees stay untouched and decoupled.
//
// outlier-model (U18) is reached ONLY (orchestrated) via R4 — never imported (the reciprocal of
// U18's own StructuralGuard, which forbids importing ui_outlier_view).

const SIBLING_UNITS = ['memoView', 'queue', 'approvalGate', 'overrideForm', 'history', 'app'];

describe('SCOPE-1 — no sibling UI unit is imported', () => {
  const files = productionFiles();

  it('the scan is over a non-empty production tree (guard against a vacuous pass)', () => {
    expect(files.length).toBeGreaterThan(0);
  });

  it.each(SIBLING_UNITS)('no production module imports src/%s/', (unit) => {
    const detect = makeUnitImportDetector(unit);
    expect(files.filter((f) => detect(stripComments(readSource(f))))).toEqual([]);
  });

  it('the ONLY cross-unit import is the frozen ui-shell (composed, never edited)', () => {
    const foreign = [];
    for (const file of files) {
      const lines = stripComments(readSource(file))
        .split('\n')
        .filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l));
      for (const line of lines) {
        const match = line.match(/from\s+['"]([^'"]+)['"]/);
        if (!match) continue;
        const spec = match[1];
        if (!spec.startsWith('.')) continue;                 // react etc.
        if (/\/shell\//.test(spec)) continue;                // the frozen ui-shell — allowed
        if (/^\.\/|^\.\.\/(components|copy|testids|fetchSeam)/.test(spec)) continue;  // own tree
        foreign.push(`${file}: ${spec}`);
      }
    }
    expect(foreign).toEqual([]);
  });

  it('detector self-tests (non-vacuous)', () => {
    const detectMemo = makeUnitImportDetector('memoView');
    expect(detectMemo("import { MemoView } from '../memoView/MemoView.jsx';")).toBe(true);
    expect(detectMemo("import { Panel } from '../shell/components/Panel.jsx';")).toBe(false);

    const detectQueue = makeUnitImportDetector('queue');
    expect(detectQueue("import { QueueTable } from '../queue/components/QueueTable.jsx';")).toBe(true);
    expect(detectQueue("import { OUTLIER_COPY } from './copy.js';")).toBe(false);
  });
});
