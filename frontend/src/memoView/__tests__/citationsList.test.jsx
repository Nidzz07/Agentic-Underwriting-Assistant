import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CitationsList } from '../components/CitationsList.jsx';

// LISTORDER-1 — cited_rule_ids rendered in the DELIVERED order (no client sort).
describe('CitationsList — LISTORDER-1: delivered order, no client sort', () => {
  it('renders cited_rule_ids in the input order (teeth: not re-sorted)', () => {
    render(<CitationsList citedRuleIds={['R-3', 'R-1', 'R-2']} />);
    const items = screen.getAllByTestId(/^memo-citation-/);
    expect(items.map((n) => n.textContent)).toEqual(['R-3', 'R-1', 'R-2']);
  });

  it('empty (default prop) -> neutral copy', () => {
    render(<CitationsList />);
    expect(screen.getByTestId('memo-region-citations')).toHaveTextContent('No rules cited');
  });
});
