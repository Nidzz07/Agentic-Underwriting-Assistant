import { describe, it, expect } from 'vitest';
import { productionFiles, readSource, stripComments } from './refNotOwn.js';

// NFR-OUTV-NOVERDICT-1 (P-OUTV-2) — LOAD-BEARING, the STRUCTURAL half (the PRIMARY robust
// guarantee): a component you never import cannot render. If no production module imports
// RecommendationBadge/ConfidenceBadge, no verdict can reach the DOM through them.
//
// CG-OUTV-Fold-1: scanned over COMMENT-STRIPPED source. The four mandatory header comments
// deliberately NAME the forbidden props ("no recommendation prop", "NO seed, NO corpus_version"),
// so a raw-text scan would flag the very prose that makes the guarantee self-evident. The guarantee
// is the absence of CODE, not of the words.
export function findVerdictBadgeImport(src) {
  return stripComments(src)
    .split('\n')
    .filter((l) => /^\s*import\b/.test(l) && /\bfrom\b/.test(l))
    .some((l) => /\b(RecommendationBadge|ConfidenceBadge)\b/.test(l));
}

// PROV-1 / NOVERDICT-1 structural companion: no verdict or provenance IDENTIFIER appears anywhere in
// the production CODE (props, destructuring, member access) — only in the header prose, which is
// stripped first.
export function findVerdictIdentifier(src) {
  return /\b(recommendation|confidence)\b/i.test(stripComments(src));
}
export function findProvenanceIdentifier(src) {
  return /\b(provenance|corpus_version|corpusVersion)\b/i.test(stripComments(src))
    || /\bseed\b/i.test(stripComments(src));
}

describe('NOVERDICT-1 (structural) — no verdict badge is imported anywhere in the unit', () => {
  const files = productionFiles();

  it('the scan is over a non-empty production tree (guard against a vacuous pass)', () => {
    expect(files.length).toBeGreaterThan(0);
  });

  it('no production outlierView module imports RecommendationBadge or ConfidenceBadge', () => {
    expect(files.filter((f) => findVerdictBadgeImport(readSource(f)))).toEqual([]);
  });

  it('no production outlierView module names a recommendation/confidence identifier in CODE', () => {
    expect(files.filter((f) => findVerdictIdentifier(readSource(f)))).toEqual([]);
  });

  it('no production outlierView module names a provenance/seed/corpus_version identifier in CODE', () => {
    expect(files.filter((f) => findProvenanceIdentifier(readSource(f)))).toEqual([]);
  });

  it('detector self-tests (non-vacuous)', () => {
    expect(findVerdictBadgeImport("import { RecommendationBadge } from '../shell/components/RecommendationBadge.jsx';")).toBe(true);
    expect(findVerdictBadgeImport("import { ConfidenceBadge } from '../shell/components/ConfidenceBadge.jsx';")).toBe(true);
    expect(findVerdictBadgeImport("import { Panel } from '../shell/components/Panel.jsx';")).toBe(false);

    expect(findVerdictIdentifier('const x = view.memo.recommendation;')).toBe(true);
    expect(findVerdictIdentifier('function R({ confidence }) {}')).toBe(true);
    expect(findVerdictIdentifier('const x = outlier.outlier_score;')).toBe(false);

    expect(findProvenanceIdentifier('const p = outlier.provenance;')).toBe(true);
    expect(findProvenanceIdentifier('const s = provenance.seed;')).toBe(true);
    expect(findProvenanceIdentifier('const c = outlier.provenance.corpus_version;')).toBe(true);
    expect(findProvenanceIdentifier('const x = outlier.flagged_features;')).toBe(false);
  });

  // CG-OUTV-Fold-1 proof: the header comments DO name the forbidden tokens, and the strip is what
  // keeps the scan honest. Without stripComments these scans would false-fail on our own prose.
  it('Fold-1 — the header comments name the forbidden tokens; stripping is load-bearing', () => {
    const viewSrc = readSource(files.find((f) => f.endsWith('OutlierView.jsx')));
    const scoreSrc = readSource(files.find((f) => f.endsWith('OutlierScoreRegion.jsx')));

    // Raw source: the prose names them (the guarantee is self-evident when reading the module).
    expect(/recommendation/i.test(viewSrc) || /recommendation/i.test(scoreSrc)).toBe(true);
    expect(/seed/i.test(scoreSrc)).toBe(true);

    // Stripped source: the CODE names neither. Absence of code, not absence of words.
    expect(findVerdictIdentifier(scoreSrc)).toBe(false);
    expect(findProvenanceIdentifier(scoreSrc)).toBe(false);
  });
});
