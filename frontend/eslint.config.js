// Flat ESLint config (Q3). Applies the three custom build-failing lints to ui-shell's own
// source (NOT the test tree, which deliberately contains synthetic violations as fixtures).
import customRules from './eslint-rules/index.js';
import queueRules from './eslint-rules/queue.js';
import memoRules from './eslint-rules/memoView.js';
import approvalRules from './eslint-rules/approvalGate.js';
import overrideRules from './eslint-rules/overrideForm.js';
import historyRules from './eslint-rules/history.js';
import outlierRules from './eslint-rules/outlierView.js';

const shellPlugin = { rules: customRules };
const queuePlugin = { rules: queueRules };
const memoPlugin = { rules: memoRules };
const approvalPlugin = { rules: approvalRules };
const overridePlugin = { rules: overrideRules };
const historyPlugin = { rules: historyRules };
const outlierPlugin = { rules: outlierRules };

export default [
  { ignores: ['node_modules/**', 'coverage/**'] },
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
  },
  {
    files: ['src/shell/**/*.{js,jsx}'],
    ignores: ['src/shell/__tests__/**'],
    plugins: { shell: shellPlugin },
    rules: {
      'shell/no-inline-label': 'error',
      'shell/advisory-vocabulary': 'error',
      'shell/testid-convention': 'error',
    },
  },
  {
    // ui-queue (U5) — REUSES the shell no-inline-label + advisory-vocabulary lints (the ONE
    // FORBIDDEN_TERMS, no new word-list) and adds ONLY the queue-<element>-<purpose> testid rule.
    // The shell block above is untouched; no src/shell file is modified (Q6-A).
    files: ['src/queue/**/*.{js,jsx}'],
    ignores: ['src/queue/__tests__/**'],
    plugins: { shell: shellPlugin, queue: queuePlugin },
    rules: {
      'shell/no-inline-label': 'error',
      'shell/advisory-vocabulary': 'error',
      'queue/queue-testid-convention': 'error',
    },
  },
  {
    // ui-memo-view (U6) — REUSES the shell no-inline-label + advisory-vocabulary lints (the ONE
    // FORBIDDEN_TERMS, no new word-list) and adds ONLY the memo-<element>-<purpose> testid rule.
    // The shell + queue blocks above are untouched; no src/shell or src/queue file is modified (Q6-A).
    // The runtime narrative_prose is out of scope — the lints assert static view code only (BR-MEMO-2).
    files: ['src/memoView/**/*.{js,jsx}'],
    ignores: ['src/memoView/__tests__/**'],
    plugins: { shell: shellPlugin, memo: memoPlugin },
    rules: {
      'shell/no-inline-label': 'error',
      'shell/advisory-vocabulary': 'error',
      'memo/memo-testid-convention': 'error',
    },
  },
  {
    // ui-approval-gate (U7) — REUSES the shell no-inline-label + advisory-vocabulary lints (the ONE
    // FORBIDDEN_TERMS, no new word-list) and adds ONLY the approval-<element>-<purpose> testid rule.
    // The shell + queue + memoView blocks above are untouched; no src/shell, src/queue, or
    // src/memoView file is modified (Q1-A). The advisory-vocabulary lint is applied UNMODIFIED
    // (NFR-AG-Fold-2): the copy honors the reserved-word constraint semantically (no literal
    // "decision" token), so no carve-out is needed.
    files: ['src/approvalGate/**/*.{js,jsx}'],
    ignores: ['src/approvalGate/__tests__/**'],
    plugins: { shell: shellPlugin, approval: approvalPlugin },
    rules: {
      'shell/no-inline-label': 'error',
      'shell/advisory-vocabulary': 'error',
      'approval/approval-testid-convention': 'error',
    },
  },
  {
    // ui-override-form (U8) — REUSES the shell no-inline-label + advisory-vocabulary lints (the ONE
    // FORBIDDEN_TERMS, no new word-list) and adds ONLY the override-<element>-<purpose> testid rule.
    // The shell + queue + memoView + approvalGate blocks above are untouched; no src/shell, src/queue,
    // src/memoView, or src/approvalGate file is modified (Q1-A). The advisory-vocabulary lint is
    // applied UNMODIFIED (NFR-OVR-Fold-3): all 21 OVERRIDE_COPY strings honor the reserved-word
    // constraint semantically (no literal "decision" token; override never rendered as
    // DECLINE-RECOMMEND), so no carve-out is needed.
    files: ['src/overrideForm/**/*.{js,jsx}'],
    ignores: ['src/overrideForm/__tests__/**'],
    plugins: { shell: shellPlugin, override: overridePlugin },
    rules: {
      'shell/no-inline-label': 'error',
      'shell/advisory-vocabulary': 'error',
      'override/override-testid-convention': 'error',
    },
  },
  {
    // ui-history (U9) — REUSES the shell no-inline-label + advisory-vocabulary lints (the ONE
    // FORBIDDEN_TERMS, no new word-list) and adds ONLY the history-<element>-<purpose> testid rule.
    // The shell + queue + memoView + approvalGate + overrideForm blocks above are untouched; no file
    // under any frozen src/ tree is modified (Q1-A). The advisory-vocabulary lint is applied
    // UNMODIFIED (NFR-HIST-Fold-D): HISTORY_COPY uses the plural "decisions" and the token-avoiding
    // human-region wording ("Underwriter's committed action"), so no carve-out is needed. Per
    // CG-HIST-Fold-2 this blanket lint also covers testid LITERALS — a hyphen-delimited "decision"
    // segment would be flagged, so the FD's (already lint-safe) testid inventory is used verbatim.
    files: ['src/history/**/*.{js,jsx}'],
    ignores: ['src/history/__tests__/**'],
    plugins: { shell: shellPlugin, history: historyPlugin },
    rules: {
      'shell/no-inline-label': 'error',
      'shell/advisory-vocabulary': 'error',
      'history/history-testid-convention': 'error',
    },
  },
  {
    // ui-outlier-view (U20) — REUSES the shell no-inline-label + advisory-vocabulary lints (the ONE
    // FORBIDDEN_TERMS, no new word-list) and adds ONLY the outlier-<element>-<purpose> testid rule.
    // The shell + queue + memoView + approvalGate + overrideForm + history blocks above are
    // untouched; no file under any frozen src/ tree is modified (Q1-A). The advisory-vocabulary lint
    // is applied UNMODIFIED (CG-OUTV-Fold-4): every OUTLIER_COPY / FLAG_DIRECTION_LABELS value
    // honors the reserved-word constraint semantically — no literal "decision" token, and the
    // direction labels are statistical positions ("Above the typical range"), never a bare
    // "High"/"Low" that would collide with CONFIDENCE_LABELS — so no carve-out is needed.
    // Q1-A: the testid rule uses the `*` (memoView/approvalGate) family, so the frozen FD
    // inventory's two-segment ids (outlier-view / outlier-score / outlier-isoutlier) are valid.
    // The runtime R4 outlier data is out of scope — the lints assert static view source only.
    files: ['src/outlierView/**/*.{js,jsx}'],
    ignores: ['src/outlierView/__tests__/**'],
    plugins: { shell: shellPlugin, outlier: outlierPlugin },
    rules: {
      'shell/no-inline-label': 'error',
      'shell/advisory-vocabulary': 'error',
      'outlier/outlier-testid-convention': 'error',
    },
  },
  {
    // src/app — the frontend composition root (out-of-band integration pass). It COMPOSES the six
    // frozen UI units and defines no display label of its own, so it reuses the shell
    // no-inline-label + advisory-vocabulary lints (the ONE FORBIDDEN_TERMS, no new word-list).
    // No <unit>-testid-convention rule applies: `app-root` is the composition root's own id and
    // belongs to no unit's namespace — the six unit conventions govern their own trees, which this
    // block does not touch. No file under any frozen src/ tree is modified.
    files: ['src/app/**/*.{js,jsx}'],
    ignores: ['src/app/__tests__/**'],
    plugins: { shell: shellPlugin },
    rules: {
      'shell/no-inline-label': 'error',
      'shell/advisory-vocabulary': 'error',
    },
  },
];
