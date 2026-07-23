// C1 (shell/copy) — the ONE FORBIDDEN_TERMS source (fold 1).
//
// BOTH the ADVISORY-1 lexical lint AND the GATE-1 namespace-distinctness check import THIS
// single object — never a second, divergent word-list. One list, two checks
// (lexical vs contextual). Backs BR-UI-2 / BR-UI-3 (CON-BR4 / underwriting hard-constraint #1).

export const FORBIDDEN_TERMS = Object.freeze({
  // Tokens that read as a FINAL verdict — forbidden as SYSTEM output (advisory-only):
  //  - a bare "DECLINE" (must be DECLINE-RECOMMEND; the -RECOMMEND suffix is mandatory, FR-RULES-5)
  //  - "decision" (reserved for the HUMAN underwriter's committed action, never system output)
  //  - "approved" / "declined" (final-verdict phrasing)
  systemOutput: Object.freeze(['DECLINE', 'decision', 'approved', 'declined']),
  // The required advisory noun for system output.
  required: 'recommendation',
});

export default FORBIDDEN_TERMS;
