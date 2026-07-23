import { describe, it, expect, vi } from 'vitest';
import { render, screen, within, fireEvent } from '@testing-library/react';
import { SystemRecommendationRegion } from '../components/SystemRecommendationRegion.jsx';
import { CommittedActionRegion } from '../components/CommittedActionRegion.jsx';
import { ForensicTupleRegion } from '../components/ForensicTupleRegion.jsx';
import { ProfileSnapshotRegion } from '../components/ProfileSnapshotRegion.jsx';
import { HistoryList } from '../components/HistoryList.jsx';
import { HistoryPagination } from '../components/HistoryPagination.jsx';
import { RECOMMENDATION_LABELS, CONFIDENCE_LABELS, COMMIT_ACTION_LABELS } from '../../shell/copy/index.js';
import { makeAuditRecord, pageKRows } from './fixtures.js';

// COPY-1 (the RTL half) + the leaf prop-contracts of the five regions and the two list components.
describe('SystemRecommendationRegion — COPY-1 / SEPARATION-1 (the sole system render site)', () => {
  it('renders the label sourced from RECOMMENDATION_LABELS — never a bare DECLINE', () => {
    render(<SystemRecommendationRegion recommendation="DECLINE-RECOMMEND" confidence="Medium" />);
    const region = screen.getByTestId('history-detail-system-region');
    expect(within(region).getByTestId('history-detail-recommendation'))
      .toHaveTextContent(RECOMMENDATION_LABELS['DECLINE-RECOMMEND']);
    expect(region.textContent).not.toMatch(/\bDECLINE\b/);
    expect(within(region).getByTestId('history-detail-confidence'))
      .toHaveTextContent(CONFIDENCE_LABELS.Medium);
  });

  it('composes the frozen ReadOnlyRegion (aria-readonly) and is engine-attributed', () => {
    render(<SystemRecommendationRegion recommendation="APPROVE" confidence="High" />);
    const region = screen.getByTestId('history-detail-system-region');
    expect(region).toHaveAttribute('aria-readonly', 'true');
    expect(within(region).getByText('System recommendation')).toBeInTheDocument();
  });

  it('has NO human-namespace node — its props cannot carry one (by construction)', () => {
    render(<SystemRecommendationRegion recommendation="REFER" confidence="Low" />);
    expect(screen.queryByTestId('history-detail-action')).toBeNull();
    expect(screen.queryByTestId('history-detail-reason')).toBeNull();
    expect(screen.queryByTestId('history-detail-underwriter')).toBeNull();
  });
});

describe('CommittedActionRegion — COPY-1 / REASON-1 (the sole human render site)', () => {
  it('renders the CommitAction label by value and the underwriter id', () => {
    render(<CommittedActionRegion action="approve" reason={null} underwriterId="uw-7" />);
    expect(screen.getByTestId('history-detail-action')).toHaveTextContent(COMMIT_ACTION_LABELS.approve);
    expect(screen.getByTestId('history-detail-underwriter')).toHaveTextContent('uw-7');
    expect(screen.queryByTestId('history-detail-reason')).toBeNull();
  });

  it('renders the reason on override', () => {
    render(<CommittedActionRegion action="override" reason="Second income verified." underwriterId="uw-7" />);
    expect(screen.getByTestId('history-detail-reason')).toHaveTextContent('Second income verified.');
    expect(screen.getByTestId('history-detail-action')).toHaveTextContent(COMMIT_ACTION_LABELS.override);
  });

  it('has NO system-namespace node — its props cannot carry one (by construction)', () => {
    render(<CommittedActionRegion action="override" reason="r" underwriterId="uw-7" />);
    expect(screen.queryByTestId('history-detail-recommendation')).toBeNull();
    expect(screen.queryByTestId('history-detail-confidence')).toBeNull();
    // the human override is never rendered as the system DECLINE-RECOMMEND.
    expect(screen.getByTestId('history-detail-human-region').textContent)
      .not.toContain(RECOMMENDATION_LABELS['DECLINE-RECOMMEND']);
  });
});

describe('ForensicTupleRegion — the read-only forensic/replay fields', () => {
  const record = makeAuditRecord();
  it('renders every field of the tuple plus the content hash and status', () => {
    render(<ForensicTupleRegion auditTuple={record.audit_tuple} contentHash="ch-profile-1" status="active" />);
    expect(screen.getByTestId('history-detail-rulebook-version')).toHaveTextContent('1.4.0');
    expect(screen.getByTestId('history-detail-model-version')).toHaveTextContent('model-1');
    expect(screen.getByTestId('history-detail-engine-version')).toHaveTextContent('eng-sha-1');
    expect(screen.getByTestId('history-detail-memo-hash')).toHaveTextContent('memo-hash-1');
    expect(screen.getByTestId('history-detail-content-hash')).toHaveTextContent('ch-profile-1');
    expect(screen.getByTestId('history-detail-timestamp')).toHaveTextContent('2026-07-02T09:00:00Z');
    expect(screen.getByTestId('history-detail-status')).toHaveTextContent('active');
  });
  it('renders the memo HASH, never a memo body (the AuditRecord carries no narrative)', () => {
    render(<ForensicTupleRegion auditTuple={record.audit_tuple} contentHash="ch" status="active" />);
    expect(screen.queryByTestId('history-detail-narrative')).toBeNull();
  });
});

describe('ProfileSnapshotRegion — the read-only persisted input', () => {
  const snapshot = makeAuditRecord().applicant_profile_snapshot;
  it('renders the identifying subset read-only, with the snapshot hash', () => {
    render(<ProfileSnapshotRegion profile={snapshot.profile} applicationId="app-21" contentHash="ch-profile-1" />);
    expect(screen.getByTestId('history-detail-profile-application')).toHaveTextContent('app-21');
    expect(screen.getByTestId('history-detail-profile-applicant')).toHaveTextContent('Jordan Rivera');
    expect(screen.getByTestId('history-detail-profile-age')).toHaveTextContent('42');
    expect(screen.getByTestId('history-detail-profile-income')).toHaveTextContent('900000');
    expect(screen.getByTestId('history-detail-profile-cover')).toHaveTextContent('500000');
    expect(screen.getByTestId('history-detail-profile-hash')).toHaveTextContent('ch-profile-1');
  });
  it('offers no edit affordance (FAITHFUL-1)', () => {
    const { container } = render(
      <ProfileSnapshotRegion profile={snapshot.profile} applicationId="app-21" contentHash="ch" />,
    );
    expect(container.querySelectorAll('input, textarea, button, select')).toHaveLength(0);
  });
});

describe('HistoryList — R6 rows (DUALREAD-1 select)', () => {
  it('renders the human action + timestamp per row, in the delivered order, and emits onSelect', () => {
    const onSelect = vi.fn();
    render(<HistoryList items={pageKRows} onSelect={onSelect} />);
    expect(screen.getAllByRole('listitem').map((li) => li.dataset.testid))
      .toEqual(pageKRows.map((r) => `history-row-${r.decision_id}`));
    expect(screen.getByTestId('history-row-action-dec-22')).toHaveTextContent(COMMIT_ACTION_LABELS.override);
    expect(screen.getByTestId('history-row-timestamp-dec-21')).toHaveTextContent('2026-07-02T09:00:00Z');

    fireEvent.click(screen.getByTestId('history-row-select-dec-23'));
    expect(onSelect).toHaveBeenCalledTimes(1);
    expect(onSelect).toHaveBeenCalledWith('dec-23');
  });

  it('carries NO system recommendation in a row (R6 omits it — no N+1 enrichment)', () => {
    render(<HistoryList items={pageKRows} onSelect={() => {}} />);
    expect(screen.queryByTestId('history-detail-recommendation')).toBeNull();
    expect(screen.getByTestId('history-list').textContent)
      .not.toContain(RECOMMENDATION_LABELS['DECLINE-RECOMMEND']);
  });

  it('renders an empty list body without rows (the empty STATE is the orchestrator\'s)', () => {
    render(<HistoryList items={[]} onSelect={() => {}} />);
    expect(screen.queryAllByRole('listitem')).toHaveLength(0);
  });
});

describe('HistoryPagination — derived state over the R6 page wrapper (PERF-1)', () => {
  it('derives the page count and emits onPageChange for the next/prev page', () => {
    const onPageChange = vi.fn();
    render(<HistoryPagination page={2} size={20} total={45} onPageChange={onPageChange} />);
    expect(screen.getByTestId('history-page-indicator')).toHaveTextContent('2 / 3');

    fireEvent.click(screen.getByTestId('history-pagination-next'));
    expect(onPageChange).toHaveBeenCalledWith(3);
    fireEvent.click(screen.getByTestId('history-pagination-prev'));
    expect(onPageChange).toHaveBeenCalledWith(1);
  });

  it('disables prev on the first page and next on the last page', () => {
    const { unmount } = render(<HistoryPagination page={1} size={20} total={45} onPageChange={() => {}} />);
    expect(screen.getByTestId('history-pagination-prev')).toBeDisabled();
    expect(screen.getByTestId('history-pagination-next')).toBeEnabled();
    unmount();

    render(<HistoryPagination page={3} size={20} total={45} onPageChange={() => {}} />);
    expect(screen.getByTestId('history-pagination-next')).toBeDisabled();
  });

  it('a zero-total page still derives one page (never a divide-by-zero / zero-page indicator)', () => {
    render(<HistoryPagination page={1} size={20} total={0} onPageChange={() => {}} />);
    expect(screen.getByTestId('history-page-indicator')).toHaveTextContent('1 / 1');
  });
});
