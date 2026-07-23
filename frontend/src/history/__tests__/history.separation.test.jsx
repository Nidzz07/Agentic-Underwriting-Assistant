import { describe, it, expect } from 'vitest';
import { screen, within } from '@testing-library/react';
import { openDetail, overrideRecord } from './fixtures.js';

// SEPARATION-1 (the LOAD-BEARING target, full-highest) — the DOM-containment teeth (NFR-HIST-Fold-B).
// ui-history is the FIRST unit to render BOTH the SYSTEM advisory Recommendation and the HUMAN
// committed CommitAction; BR-HIST-2 requires them to be structurally distinct, non-nested regions.
// The test FAILS if either namespace were rendered inside the other's region.
//
// The `override` record is deliberately used: it is the case where conflation would be most harmful
// (a human `override` must never render as, or inside, the system `DECLINE-RECOMMEND`).
describe('HistoryView — SEPARATION-1: system and human namespaces are distinct, non-nested regions (teeth)', () => {
  it('neither region contains the other; rec/conf ONLY in system; action ONLY in human; aria-readonly', async () => {
    await openDetail('dec-22', { detail: [{ resolve: overrideRecord }] });

    const system = await screen.findByTestId('history-detail-system-region');
    const human = screen.getByTestId('history-detail-human-region');

    // (a) distinct nodes, neither an ancestor/descendant of the other (jsdom Node.contains, Fold-B —
    //     sound for arbitrary depth, false across a sibling subtree).
    expect(system).not.toBe(human);
    expect(system.contains(human)).toBe(false);
    expect(human.contains(system)).toBe(false);

    // (b) the SYSTEM namespace renders inside the system region — and NOWHERE in the human region.
    expect(within(system).getByTestId('history-detail-recommendation')).toBeInTheDocument();
    expect(within(system).getByTestId('history-detail-confidence')).toBeInTheDocument();
    expect(within(human).queryByTestId('history-detail-recommendation')).toBeNull();
    expect(within(human).queryByTestId('history-detail-confidence')).toBeNull();

    // (c) the HUMAN namespace renders inside the human region — and NOWHERE in the system region.
    expect(within(human).getByTestId('history-detail-action')).toBeInTheDocument();
    expect(within(human).getByTestId('history-detail-reason')).toBeInTheDocument();
    expect(within(system).queryByTestId('history-detail-action')).toBeNull();
    expect(within(system).queryByTestId('history-detail-reason')).toBeNull();

    // (d) the system region composes the FROZEN ui-shell ReadOnlyRegion, engine-attributed.
    expect(system).toHaveAttribute('aria-readonly', 'true');
    expect(within(system).getByText('System recommendation')).toBeInTheDocument();

    // the values render EXACTLY ONCE each, and the human override never reads as the system label.
    expect(screen.getAllByTestId('history-detail-recommendation')).toHaveLength(1);
    expect(screen.getAllByTestId('history-detail-action')).toHaveLength(1);
    expect(within(system).getByTestId('history-detail-recommendation')).toHaveTextContent('Decline-Recommend');
    expect(within(human).getByTestId('history-detail-action')).toHaveTextContent('Override');
    expect(within(human).getByTestId('history-detail-action')).not.toHaveTextContent('Decline-Recommend');
  });
});
