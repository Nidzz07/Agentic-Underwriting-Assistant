import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueueTable } from '../components/QueueTable.jsx';

// A11Y-1 (semantic table) + COPY-1 look-up; one row per item.
describe('QueueTable', () => {
  const items = [
    { application_id: 'app-1', recommendation: 'APPROVE', confidence: 'High' },
    { application_id: 'app-2', recommendation: null, confidence: null },
  ];

  it('renders a semantic table with a row per item and 4 column headers', () => {
    render(<QueueTable items={items} onSelect={() => {}} />);
    expect(screen.getByTestId('queue-table')).toBeInTheDocument();
    expect(screen.getByRole('table')).toBeInTheDocument();
    expect(screen.getByTestId('queue-row-app-1')).toBeInTheDocument();
    expect(screen.getByTestId('queue-row-app-2')).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').length).toBe(4);
  });
});
