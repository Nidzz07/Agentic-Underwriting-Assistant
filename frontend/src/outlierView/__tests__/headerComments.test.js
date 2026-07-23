import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

// NFR-ND-OUTV-Fold-1 — the header-comment self-evidence convention, PINNED MANDATORY (not a
// candidate). A header comment is a NON-OPTIONAL Code-Gen deliverable on the four named modules, so
// each by-construction guarantee is legible READING THE MODULE IN ISOLATION.
//
// DOCUMENTATION ONLY — NOT enforcement. The enforcement is the prop signatures (P-OUTV-2/3), the
// branch ordering (P-OUTV-1) and the StructuralGuard scans (P-OUTV-10). This test asserts the
// DOCUMENTATION exists, nothing more.

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = (rel) => readFileSync(path.join(ROOT, rel), 'utf8');

// The header is the leading comment block, before the first non-comment/non-import statement.
// The prose is NORMALIZED (comment markers stripped, whitespace collapsed to single spaces) so a
// phrase that WRAPS across lines — "no request-body\n// builder" — still matches. Matching raw
// lines would make these assertions depend on incidental line-wrapping rather than on the wording.
function headerOf(src) {
  const lines = src.split('\n');
  const header = [];
  for (const line of lines) {
    if (/^\s*\/\//.test(line) || /^\s*\*/.test(line) || /^\s*\/\*/.test(line)) {
      header.push(line);
      continue;
    }
    if (/^\s*(import\b|$)/.test(line)) continue;
    break;
  }
  return header
    .join('\n')
    .replace(/^\s*(\/\/|\/\*+|\*+\/?)/gm, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

describe('Fold-1 — the four MANDATORY header comments exist and state their restriction', () => {
  it('OutlierView.jsx documents the failure-first ordering and the field discriminator', () => {
    const header = headerOf(read('OutlierView.jsx'));
    expect(header).toMatch(/MANDATORY header comment/i);
    expect(header).toMatch(/failure-first/i);
    expect(header).toMatch(/UNWRITABLE from a failure path/i);
    expect(header).toMatch(/field/i);
    expect(header).toMatch(/NOT the R4 `status`|not the R4 status/i);
  });

  it('OutlierScoreRegion.jsx documents its prop-only signature and both exclusions', () => {
    const header = headerOf(read('components/OutlierScoreRegion.jsx'));
    expect(header).toMatch(/MANDATORY header comment/i);
    expect(header).toMatch(/\{ outlierScore, isOutlier, testid \} ONLY/);
    expect(header).toMatch(/NO recommendation prop/i);
    expect(header).toMatch(/NO provenance prop/i);
    expect(header).toMatch(/seed/i);
    expect(header).toMatch(/corpus_version/i);
  });

  it('FlaggedFeaturesRegion.jsx documents its prop-only signature and both exclusions', () => {
    const header = headerOf(read('components/FlaggedFeaturesRegion.jsx'));
    expect(header).toMatch(/MANDATORY header comment/i);
    expect(header).toMatch(/\{ flaggedFeatures, testid \} ONLY/);
    expect(header).toMatch(/NO recommendation prop/i);
    expect(header).toMatch(/NO provenance prop/i);
    expect(header).toMatch(/delivered order/i);
  });

  it('fetchSeam.js documents the read-only GET-only seam and mirrors-not-imports', () => {
    const header = headerOf(read('fetchSeam.js'));
    expect(header).toMatch(/MANDATORY header comment/i);
    expect(header).toMatch(/READ-ONLY/i);
    expect(header).toMatch(/ONLY a GET/i);
    expect(header).toMatch(/no request-body builder/i);
    expect(header).toMatch(/structurally absent/i);
    expect(header).toMatch(/WITHOUT importing/i);
  });

  it('each of the four states it is documentation, NOT enforcement (Fold-1 discipline)', () => {
    for (const rel of [
      'OutlierView.jsx',
      'components/OutlierScoreRegion.jsx',
      'components/FlaggedFeaturesRegion.jsx',
      'fetchSeam.js',
    ]) {
      expect(headerOf(read(rel))).toMatch(/NOT enforcement/i);
    }
  });

  it('headerOf is non-vacuous (detector self-test)', () => {
    expect(headerOf('// a header\nimport x from "y";\nconst z = 1;')).toBe('a header');
    expect(headerOf('const z = 1;\n// not a header')).toBe('');
    // The wrap-tolerance that made this normalization necessary:
    expect(headerOf('// no request-body\n// builder here')).toBe('no request-body builder here');
  });
});
