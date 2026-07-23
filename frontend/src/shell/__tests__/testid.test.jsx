import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import AppFrame from '../components/AppFrame.jsx';
import Panel from '../components/Panel.jsx';
import ReadOnlyRegion from '../components/ReadOnlyRegion.jsx';
import RecommendationBadge from '../components/RecommendationBadge.jsx';
import ConfidenceBadge from '../components/ConfidenceBadge.jsx';
import { isValidTestid } from '../../../eslint-rules/index.js';

// TESTID-1 — every interactive / assertion-relevant primitive exposes a stable data-testid that
// follows the shell-<primitive>-<purpose> convention. Presence here + naming lint (eslint.rules)
// + self-test below.

describe('NFR-UI-TESTID-1 — primitives expose a stable, convention-following data-testid', () => {
  it('AppFrame (with and without a user) renders its testid', () => {
    const { rerender } = render(<AppFrame user={{ role: 'underwriter' }}>x</AppFrame>);
    const withUser = screen.getByTestId('shell-appframe-root');
    expect(withUser).toBeInTheDocument();
    expect(isValidTestid('shell-appframe-root')).toBe(true);
    rerender(<AppFrame>x</AppFrame>); // no user -> role null branch
    expect(screen.getByTestId('shell-appframe-root')).toBeInTheDocument();
  });

  it('Panel renders its testid, with and without a title', () => {
    const { rerender } = render(<Panel title="Queue" testid="shell-panel-queue">body</Panel>);
    expect(screen.getByTestId('shell-panel-queue')).toHaveTextContent('Queue');
    expect(isValidTestid('shell-panel-queue')).toBe(true);
    rerender(<Panel testid="shell-panel-plain">body</Panel>); // no title branch
    expect(screen.getByTestId('shell-panel-plain')).toBeInTheDocument();
  });

  it('ReadOnlyRegion renders its testid and frames content read-only', () => {
    render(<ReadOnlyRegion testid="shell-readonly-memo">memo</ReadOnlyRegion>);
    const el = screen.getByTestId('shell-readonly-memo');
    expect(el).toHaveAttribute('aria-readonly', 'true');
    expect(isValidTestid('shell-readonly-memo')).toBe(true);
  });

  it('badges expose convention-following default testids', () => {
    render(<RecommendationBadge value="APPROVE" />);
    render(<ConfidenceBadge value="Low" />);
    expect(isValidTestid('shell-recommendationbadge-value')).toBe(true);
    expect(isValidTestid('shell-confidencebadge-value')).toBe(true);
  });

  it('detector self-test — a misnamed testid is rejected (non-vacuous)', () => {
    expect(isValidTestid('queuePanel')).toBe(false);
    expect(isValidTestid('shell_panel_queue')).toBe(false);
  });
});
