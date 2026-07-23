// C4 (shell/tokens) — the SINGLE aesthetic source. Direction PINNED = refined-minimalism
// (legible, trustworthy-professional; a distinctive-but-professional type pairing, NOT
// Inter/Roboto/Arial defaults; a restrained palette, NO purple-gradient cliche). Appropriate
// to a BFSI audit-grade surface.
//
// VALUES DEFERRED (Q4-A / AESTHETIC-1): these are NEUTRAL PLACEHOLDERS as named CSS custom
// properties (categories/shapes) so primitives compile and tests run. The FINAL palette / type
// pairing / spacing scale are set later (view-unit Code-Gen or a design pass) — NOT pinned here.
// The status-accent variables are keyed by the SAME Recommendation values as shell/copy
// (one value space, two facets: label in shell/copy, accent here).

export const CSS_VARIABLES = Object.freeze({
  // color (placeholders)
  '--shell-color-surface': '#ffffff',
  '--shell-color-text': '#1a1a1a',
  '--shell-color-border': '#e2e2e2',
  // status accents keyed by Recommendation value (placeholders)
  '--shell-status-approve': '#2f7d55',
  '--shell-status-refer': '#9a7b1f',
  '--shell-status-decline-recommend': '#a23b3b',
  // typography (family names deferred — placeholder generic stacks)
  '--shell-font-display': 'serif',
  '--shell-font-body': 'system-ui',
  // spacing / radius / elevation (placeholder scale)
  '--shell-space-1': '0.5rem',
  '--shell-space-2': '1rem',
  '--shell-radius': '0.375rem',
  '--shell-elevation': '0 1px 2px rgba(0, 0, 0, 0.06)',
});

// Status-accent lookup keyed by the frozen Recommendation VALUE (placeholder var references).
export const STATUS_ACCENT = Object.freeze({
  APPROVE: 'var(--shell-status-approve)',
  REFER: 'var(--shell-status-refer)',
  'DECLINE-RECOMMEND': 'var(--shell-status-decline-recommend)',
});

export const TOKENS = Object.freeze({ cssVariables: CSS_VARIABLES, statusAccent: STATUS_ACCENT });

export default TOKENS;
