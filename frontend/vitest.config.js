import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

// Frontend test runner (Q5/Q6). SEPARATE runner + tree from the Python pytest suite —
// coverage is gated on ui-shell's OWN JS only (src/shell); the backend suite is untouched
// and must not regress. NO TypeScript anywhere.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.js'],
    // ui-queue (U5) + ui-memo-view (U6) folded into the SAME frontend run (Q6-A). Include paths ADDED
    // only — the coverage thresholds below are UNCHANGED (ui-shell/ui-queue enforcement not weakened).
    include: [
      'src/shell/__tests__/**/*.test.{js,jsx}',
      'src/queue/__tests__/**/*.test.{js,jsx}',
      'src/memoView/__tests__/**/*.test.{js,jsx}',
      'src/approvalGate/__tests__/**/*.test.{js,jsx}',
      // ui-override-form (U8) folded into the SAME frontend run (Q1-A). Include path ADDED only — the
      // coverage thresholds below are UNCHANGED (shell/queue/memoView/approvalGate gates not weakened).
      'src/overrideForm/__tests__/**/*.test.{js,jsx}',
      // ui-history (U9) folded into the SAME frontend run (Q1-A). Include path ADDED only — the
      // coverage thresholds below are UNCHANGED (all five frozen gates stand).
      'src/history/__tests__/**/*.test.{js,jsx}',
      // src/app — the frontend composition root, authored in the out-of-band integration pass
      // (guide-docs/build/plans/composition-root-integration-plan.md). Author-only: no bundler /
      // dev-server is pulled forward (deploy-config P2 owns that). Include path ADDED only —
      // thresholds UNCHANGED; all six frozen gates stand.
      'src/app/__tests__/**/*.test.{js,jsx}',
      // ui-outlier-view (U20, Phase 2) folded into the SAME frontend run. Include path ADDED only —
      // the coverage thresholds below are UNCHANGED; all seven existing gates stand, none weakened.
      'src/outlierView/__tests__/**/*.test.{js,jsx}',
      // login (register #25's frontend half) folded into the SAME frontend run. Include path ADDED
      // only -- the coverage thresholds below are UNCHANGED; all eight existing gates stand, none
      // weakened. Every prior unit was folded in exactly this way.
      'src/login/__tests__/**/*.test.{js,jsx}',
    ],
    coverage: {
      provider: 'v8',
      include: ['src/shell/**/*.{js,jsx}', 'src/queue/**/*.{js,jsx}', 'src/memoView/**/*.{js,jsx}', 'src/approvalGate/**/*.{js,jsx}', 'src/overrideForm/**/*.{js,jsx}', 'src/history/**/*.{js,jsx}', 'src/app/**/*.{js,jsx}', 'src/outlierView/**/*.{js,jsx}', 'src/login/**/*.{js,jsx}'],
      exclude: ['src/shell/__tests__/**', 'src/queue/__tests__/**', 'src/memoView/__tests__/**', 'src/approvalGate/__tests__/**', 'src/overrideForm/__tests__/**', 'src/history/__tests__/**', 'src/app/__tests__/**', 'src/outlierView/__tests__/**', 'src/login/__tests__/**'],
      reporter: ['text', 'text-summary'],
      // QA-6: >=90% on the frontend's own JS (Q5). UNCHANGED — src/shell + src/queue stay 100%
      // and src/memoView is driven >=90% (per-file coverage reported separately, no masking).
      thresholds: { lines: 90, functions: 90, statements: 90, branches: 90 },
    },
  },
});
