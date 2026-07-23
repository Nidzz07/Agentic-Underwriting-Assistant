// Custom ESLint rules for ui-shell (Q3). Each rule reads the SINGLE shell/copy + FORBIDDEN_TERMS
// source (never a second word-list — fold 1) and is build-failing. Detector helpers are exported so
// the Vitest RuleTester self-tests (fold 2, non-vacuous) exercise the exact same logic.
//
// Rules:
//   no-inline-label     -> COPY-1  (BR-UI-1): no display-label literal outside shell/copy
//   advisory-vocabulary -> ADVISORY-1 (BR-UI-2): no forbidden system-output token
//   testid-convention   -> TESTID-1 (BR-UI-5): literal data-testid follows shell-<primitive>-<purpose>

import {
  RECOMMENDATION_LABELS,
  CONFIDENCE_LABELS,
  ROLE_LABELS,
  COMMIT_ACTION_LABELS,
} from '../src/shell/copy/index.js';
import { FORBIDDEN_TERMS } from '../src/shell/copy/forbiddenTerms.js';

// Re-export the ONE FORBIDDEN_TERMS object the lints consume, so the GATE-1 test can assert
// (===) that the lint and the copy module share a single source object (fold 1, structural).
export { FORBIDDEN_TERMS as LINT_FORBIDDEN_TERMS } from '../src/shell/copy/forbiddenTerms.js';

const COPY_DIR = 'src/shell/copy';
function inCopyModule(filename) {
  return String(filename).replace(/\\/g, '/').includes(COPY_DIR);
}

// The complete set of canonical display-label VALUES, read from the single source (no duplication).
export const LABEL_VALUES = new Set([
  ...Object.values(RECOMMENDATION_LABELS),
  ...Object.values(CONFIDENCE_LABELS),
  ...Object.values(ROLE_LABELS),
  ...Object.values(COMMIT_ACTION_LABELS),
]);

// ADVISORY-1 detector: returns the list of forbidden system-output tokens found in `text`.
// A bare "decline" is flagged unless it carries the -recommend suffix (advisory-only).
export function findForbiddenSystemOutput(text) {
  const t = String(text);
  const hits = [];
  if (/decline(?!-?recommend)/i.test(t)) hits.push('bare-decline');
  for (const term of FORBIDDEN_TERMS.systemOutput) {
    const low = term.toLowerCase();
    if (low === 'decline' || low === 'declined') continue; // covered by the suffix-aware check above
    if (new RegExp(`\\b${term}\\b`, 'i').test(t)) hits.push(low);
  }
  return hits;
}

// TESTID-1 detector: the shell-<primitive>-<purpose> naming convention.
export const TESTID_PATTERN = /^shell-[a-z]+(-[a-z0-9]+)+$/;
export function isValidTestid(value) {
  return typeof value === 'string' && TESTID_PATTERN.test(value);
}

export const rules = {
  'no-inline-label': {
    meta: {
      type: 'problem',
      docs: { description: 'No Recommendation/Confidence/Role/CommitAction display-label literal outside shell/copy (COPY-1, BR-UI-1).' },
      schema: [],
    },
    create(context) {
      const filename = context.filename ?? context.getFilename();
      if (inCopyModule(filename)) return {}; // the copy module is where labels are DEFINED
      function check(node, value) {
        if (typeof value === 'string' && LABEL_VALUES.has(value.trim())) {
          context.report({ node, message: `Inlined display label "${value.trim()}" — import it from shell/copy (COPY-1).` });
        }
      }
      return {
        Literal(node) { if (typeof node.value === 'string') check(node, node.value); },
        JSXText(node) { check(node, node.value); },
        TemplateElement(node) { check(node, node.value && node.value.cooked); },
      };
    },
  },

  'advisory-vocabulary': {
    meta: {
      type: 'problem',
      docs: { description: 'No forbidden system-output token (bare DECLINE / decision / approved / declined) — advisory-only (ADVISORY-1, BR-UI-2).' },
      schema: [],
    },
    create(context) {
      const filename = context.filename ?? context.getFilename();
      if (inCopyModule(filename)) return {}; // the copy module DEFINES the vocabulary/forbidden list
      function check(node, value) {
        const hits = findForbiddenSystemOutput(value);
        if (hits.length > 0) {
          context.report({ node, message: `Forbidden system-output vocabulary ${JSON.stringify(hits)} — use the advisory copy from shell/copy (ADVISORY-1).` });
        }
      }
      return {
        Literal(node) { if (typeof node.value === 'string') check(node, node.value); },
        JSXText(node) { check(node, node.value); },
        TemplateElement(node) { check(node, (node.value && node.value.cooked) || ''); },
      };
    },
  },

  'testid-convention': {
    meta: {
      type: 'problem',
      docs: { description: 'A literal data-testid must follow the shell-<primitive>-<purpose> convention (TESTID-1, BR-UI-5).' },
      schema: [],
    },
    create(context) {
      return {
        JSXAttribute(node) {
          if (!node.name || node.name.name !== 'data-testid') return;
          const v = node.value;
          if (v && v.type === 'Literal' && typeof v.value === 'string' && !isValidTestid(v.value)) {
            context.report({ node, message: `data-testid "${v.value}" violates the shell-<primitive>-<purpose> convention (TESTID-1).` });
          }
        },
      };
    },
  },
};

export default rules;
