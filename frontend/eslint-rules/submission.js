// Custom ESLint rule(s) for the submission unit (register #2 / WIRE1-Fold-6). Frontend-wide build
// infra — NOT a file under any frozen unit's src/ tree. The submission unit REUSES ui-shell's
// no-inline-label / advisory-vocabulary lints (the ONE FORBIDDEN_TERMS, no new word-list); this
// file adds ONLY the submission testid convention, mirroring eslint-rules/outlierView.js and
// leaving eslint-rules/index.js untouched.
//
//   submission-testid-convention -> a literal data-testid follows submission-<element>-<purpose>.
//
// ⚑ The `*` quantifier family (the memoView/approvalGate/outlierView precedent), NOT the `+`
// family (queue/history): the inventory contains TWO-SEGMENT ids — `submission-view`,
// `submission-form`, `submission-submit`, `submission-accepted` — which the `+` family rejects.
//
// ⚑ Interpolated ids (the `fieldInputTestid` / `fieldErrorTestid` / `missingItemTestid` builders)
// are template literals this rule cannot see. `slugSegment` plus its self-tests in
// __tests__/structure.test.js are the enforcement there — the ui-history arrangement exactly.
export const SUBMISSION_TESTID_PATTERN = /^submission-[a-z0-9]+(-[a-z0-9]+)*$/;

export function isValidSubmissionTestid(value) {
  return typeof value === 'string' && SUBMISSION_TESTID_PATTERN.test(value);
}

export const rules = {
  'submission-testid-convention': {
    meta: {
      type: 'problem',
      docs: { description: 'A literal data-testid in the submission unit must follow the submission-<element>-<purpose> convention.' },
      schema: [],
    },
    create(context) {
      return {
        JSXAttribute(node) {
          if (!node.name || node.name.name !== 'data-testid') return;
          const v = node.value;
          if (v && v.type === 'Literal' && typeof v.value === 'string' && !isValidSubmissionTestid(v.value)) {
            context.report({ node, message: `data-testid "${v.value}" violates the submission-<element>-<purpose> convention.` });
          }
        },
      };
    },
  },
};

export default rules;
