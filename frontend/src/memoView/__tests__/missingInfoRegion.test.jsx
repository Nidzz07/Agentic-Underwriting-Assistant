import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MissingInfoRegion } from '../components/MissingInfoRegion.jsx';
import { MISSING_INFO_SOURCE_LABELS } from '../copy.js';

// LISTORDER-1 (order preservation) + COPY-1 (memo-local source labels).
describe('MissingInfoRegion — LISTORDER-1 + source labels', () => {
  const items = [
    { source: 'incomplete_flag', detail: 'Application marked incomplete' },
    { source: 'missing_document', detail: 'Salary slip not provided' },
    { source: 'not_evaluated_rule', detail: 'Debt ratio rule not evaluated' },
  ];

  it('renders in delivered order (teeth: NOT re-sorted by source)', () => {
    render(<MissingInfoRegion items={items} />);
    const rows = screen.getAllByTestId(/^memo-missinginfo-/);
    expect(rows.map((r) => r.querySelector('span').textContent)).toEqual([
      'Application marked incomplete',
      'Salary slip not provided',
      'Debt ratio rule not evaluated',
    ]);
  });

  it('each row shows detail + the memo-local source label (Q4-A)', () => {
    render(<MissingInfoRegion items={[items[0]]} />);
    const row = screen.getByTestId('memo-missinginfo-0');
    expect(row).toHaveTextContent('Application marked incomplete');
    expect(row).toHaveTextContent(MISSING_INFO_SOURCE_LABELS.incomplete_flag);
  });

  it('an unrecognized source falls back to the raw source value (defensive branch)', () => {
    render(<MissingInfoRegion items={[{ source: 'something_else', detail: 'x' }]} />);
    expect(screen.getByTestId('memo-missinginfo-0')).toHaveTextContent('something_else');
  });

  it('empty (default prop) -> neutral copy', () => {
    render(<MissingInfoRegion />);
    expect(screen.getByTestId('memo-region-missinginfo')).toHaveTextContent('No missing information');
  });
});
