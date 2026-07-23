import { describe, it, expect } from 'vitest';
import { findForbiddenSystemOutput, LABEL_VALUES } from '../../../eslint-rules/index.js';
import { FORBIDDEN_TERMS } from '../../shell/copy/forbiddenTerms.js';
import { OUTLIER_COPY, FLAG_DIRECTION_LABELS } from '../copy.js';

// COPY-1 + ADVISORY-1 (P-OUTV-9) — Q7-A: every copy value is verified against the REAL detector
// imported from eslint-rules/index.js (findForbiddenSystemOutput — /decline(?!-?recommend)/i
// SUBSTRING + \bdecision\b / \bapproved\b word-boundary), never a re-implementation and never an
// eyeball. The frozen precedent: every prior unit verified its copy this way.

const ALL_VALUES = [...Object.values(OUTLIER_COPY), ...Object.values(FLAG_DIRECTION_LABELS)];

describe('ADVISORY-1 — no forbidden system-output vocabulary in the outlier-local copy', () => {
  it('every copy value passes the REAL imported detector', () => {
    const offenders = ALL_VALUES.filter((v) => findForbiddenSystemOutput(v).length > 0);
    expect(offenders).toEqual([]);
  });

  it('the detector is non-vacuous against this exact copy set (self-test)', () => {
    expect(findForbiddenSystemOutput('the final decision was made')).toContain('decision');
    expect(findForbiddenSystemOutput('the application was approved')).toContain('approved');
    expect(findForbiddenSystemOutput('DECLINE')).toContain('bare-decline');
    expect(findForbiddenSystemOutput('DECLINE-RECOMMEND')).toEqual([]);
  });

  it('reuses the ONE FORBIDDEN_TERMS source — no local word-list is defined here', () => {
    expect(FORBIDDEN_TERMS.systemOutput).toEqual(['DECLINE', 'decision', 'approved', 'declined']);
    for (const term of FORBIDDEN_TERMS.systemOutput) {
      const bare = ALL_VALUES.filter((v) => new RegExp(`\\b${term}\\b`, 'i').test(v));
      expect(bare).toEqual([]);
    }
  });
});

describe('COPY-1 — no collision with a shell/copy display label', () => {
  it('no outlier copy value equals a canonical shell display label', () => {
    const collisions = ALL_VALUES.filter((v) => LABEL_VALUES.has(String(v).trim()));
    expect(collisions).toEqual([]);
  });

  // CG-OUTV-Fold-4 — the concrete trap Q7-A avoids: a bare "High"/"Low" direction label would
  // collide EXACTLY with CONFIDENCE_LABELS, tripping no-inline-label AND false-failing the
  // NOVERDICT-1 rendered-absence teeth. Prove the collision is real and that our labels dodge it.
  it('a bare High/Low WOULD have collided (the avoided trap is real)', () => {
    expect(LABEL_VALUES.has('High')).toBe(true);
    expect(LABEL_VALUES.has('Low')).toBe(true);
    expect(LABEL_VALUES.has(FLAG_DIRECTION_LABELS.high)).toBe(false);
    expect(LABEL_VALUES.has(FLAG_DIRECTION_LABELS.low)).toBe(false);
  });
});

describe('COPY-1 — FLAG_DIRECTION_LABELS frames direction as a STATISTICAL POSITION (Fold-3)', () => {
  it('is keyed BY VALUE on the FlagDirection wire enum — no remap, no re-case', () => {
    expect(Object.keys(FLAG_DIRECTION_LABELS).sort()).toEqual(['high', 'low']);
  });

  it('states a position relative to the typical range, not a severity/verdict', () => {
    expect(FLAG_DIRECTION_LABELS.high).toBe('Above the typical range');
    expect(FLAG_DIRECTION_LABELS.low).toBe('Below the typical range');
  });

  it('contains no severity/risk vocabulary', () => {
    for (const label of Object.values(FLAG_DIRECTION_LABELS)) {
      expect(label).not.toMatch(/\b(risk|risky|severe|severity|critical|bad|danger|dangerous)\b/i);
    }
  });
});

describe('EMPTY-1 — "analyzed, no anomalies" and "not analyzed" are DIFFERENT copy', () => {
  it('noFlagsLabel is distinct from notAvailableMessage', () => {
    expect(OUTLIER_COPY.noFlagsLabel).not.toBe(OUTLIER_COPY.notAvailableMessage);
  });
});

// CG-OUTV-Fold-2 — Q6-A omitted the outlier_model_version footnote, so the FD's CONDITIONAL
// copy key (`modelVersionFootnoteLabel`, "optional (Q5-A)") is deliberately NOT realized.
// Provenance is entirely absent from the render (P-OUTV-3 total prop-exclusion).
describe('PROV-1 / Fold-2 — no provenance-bearing copy key exists at all', () => {
  it('copy carries no footnote key and no provenance vocabulary', () => {
    expect(OUTLIER_COPY.modelVersionFootnoteLabel).toBeUndefined();
    const keys = Object.keys(OUTLIER_COPY);
    expect(keys.filter((k) => /provenance|seed|corpus|modelversion/i.test(k))).toEqual([]);
  });
});
