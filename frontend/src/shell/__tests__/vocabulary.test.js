import { describe, it, expect } from 'vitest';
import {
  RECOMMENDATION_LABELS,
  COMMIT_ACTION_LABELS,
  ADVISORY_VOCABULARY,
} from '../copy/index.js';
import { FORBIDDEN_TERMS } from '../copy/forbiddenTerms.js';
import { LINT_FORBIDDEN_TERMS } from '../../../eslint-rules/index.js';

// GATE-1 (NFR-UI-GATE-1) — the human-gate vocabulary/namespace SOURCE, distinct from system output.
// Structural / unit checks over the copy module ONLY. No view/gate is rendered here — the
// render-context attribution is delegated to ui-approval-gate (U7). See fold 4 (key-namespace
// disjointness) + fold 1 (one FORBIDDEN_TERMS object) + fold 2 (non-vacuous self-test).

// The invariant-bearing detector, reused on both real and synthetic maps so it is NON-VACUOUS.
function keyNamespacesDisjoint(commitLabels, recommendationLabels) {
  const commitKeys = new Set(Object.keys(commitLabels));
  return Object.keys(recommendationLabels).every((k) => !commitKeys.has(k));
}

describe('NFR-UI-GATE-1 — CommitAction namespace distinct from Recommendation', () => {
  it('commitaction_disjoint_from_recommendation (key namespaces disjoint, case-sensitive)', () => {
    // {approve, override} vs {APPROVE, REFER, DECLINE-RECOMMEND} — disjoint by casing (FD 2.1).
    expect(keyNamespacesDisjoint(COMMIT_ACTION_LABELS, RECOMMENDATION_LABELS)).toBe(true);
  });

  it('override_not_decline_recommend (the critical human-vs-system guard)', () => {
    // The human `override` must never be, or render as, the system DECLINE-RECOMMEND — key AND label.
    expect(Object.keys(RECOMMENDATION_LABELS)).not.toContain('override');
    expect(COMMIT_ACTION_LABELS.override).not.toBe(RECOMMENDATION_LABELS['DECLINE-RECOMMEND']);
    expect(COMMIT_ACTION_LABELS.override).toBe('Override');
    expect(RECOMMENDATION_LABELS['DECLINE-RECOMMEND']).toBe('Decline-Recommend');
  });

  it('same_forbidden_terms_object (fold 1 — one source object, both consumers)', () => {
    // The lint's FORBIDDEN_TERMS and the copy module's FORBIDDEN_TERMS are the SAME object.
    expect(LINT_FORBIDDEN_TERMS).toBe(FORBIDDEN_TERMS);
  });

  it('detects_synthetic_collision (fold 2 — the check is non-vacuous)', () => {
    // A synthetic CommitAction map whose key collides with a Recommendation key must be flagged.
    const colliding = { APPROVE: 'Approve', override: 'Override' };
    expect(keyNamespacesDisjoint(colliding, RECOMMENDATION_LABELS)).toBe(false);
    // And a synthetic override label equal to the system decline label is a distinct violation.
    const declineLabel = RECOMMENDATION_LABELS['DECLINE-RECOMMEND'];
    const badOverride = { approve: 'Approve', override: declineLabel };
    expect(badOverride.override).toBe(declineLabel); // the collision the guard forbids
  });
});

describe('advisory vocabulary source', () => {
  it('requires the advisory noun "recommendation"', () => {
    expect(ADVISORY_VOCABULARY.required).toBe('recommendation');
    expect(FORBIDDEN_TERMS.required).toBe('recommendation');
  });

  it('the decline label preserves the -RECOMMEND suffix (never a bare DECLINE)', () => {
    expect(RECOMMENDATION_LABELS['DECLINE-RECOMMEND']).toContain('Recommend');
    expect(Object.values(RECOMMENDATION_LABELS)).not.toContain('DECLINE');
    expect(Object.values(RECOMMENDATION_LABELS)).not.toContain('Decline');
  });
});
