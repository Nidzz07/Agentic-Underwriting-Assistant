// C1 (shell/copy) — the SINGLE source of every Recommendation / Confidence / Role / CommitAction
// display label + the advisory vocabulary (BR-UI-1 / BR-UI-2, CON-BR4 language facet). Views and
// primitives IMPORT from here; they never inline a display string.
//
// Each map KEYS on the FROZEN backend wire value (verified in the built backend:
//   rules_engine.report_schema.Recommendation / .Confidence, auth_rbac.roles.Role,
//   audit_store.record_schema.CommitAction). WIRE-1 must not remap or re-case these keys.
//   Recommendation  -> UPPERCASE (hyphenated -RECOMMEND suffix)
//   Confidence      -> Title-case
//   Role            -> lowercase
//   CommitAction    -> lowercase  (a DISTINCT namespace from system Recommendation)

export const RECOMMENDATION_LABELS = Object.freeze({
  APPROVE: 'Approve',
  REFER: 'Refer',
  // -RECOMMEND preserved; NEVER a bare "DECLINE" that reads as a final verdict (BR-UI-2).
  'DECLINE-RECOMMEND': 'Decline-Recommend',
});

export const CONFIDENCE_LABELS = Object.freeze({
  High: 'High',
  Medium: 'Medium',
  Low: 'Low',
});

// Chrome/labelling only — NOT an authorization datum (BR-UI-4).
export const ROLE_LABELS = Object.freeze({
  underwriter: 'Underwriter',
  auditor: 'Auditor',
  admin: 'Admin',
});

// The HUMAN's committed-action namespace (CON-BR4) — DISTINCT from system Recommendation (FD 2.1).
//   approve  = the underwriter agrees (no reason required)
//   override = the underwriter disagrees (mandatory non-blank reason, enforced at the gate)
// The human `override` is NOT, and must never render as, the system `DECLINE-RECOMMEND`.
export const COMMIT_ACTION_LABELS = Object.freeze({
  approve: 'Approve',
  override: 'Override',
});

// System output is a *recommendation*, never a *decision* (the word "decision" is reserved for
// the human's committed action). Backs the ADVISORY_VOCABULARY required-term facet.
export const ADVISORY_VOCABULARY = Object.freeze({
  required: 'recommendation',
  systemOutputNoun: 'recommendation',
});
