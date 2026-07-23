import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { PaginationControls } from '../components/PaginationControls.jsx';

// PAGINATION-1 — boundary disabling both ends; indicator from the R2 page wrapper.
describe('PaginationControls — PAGINATION-1', () => {
  it('page 1: prev disabled, next enabled; indicator shows 1 / 2', () => {
    render(<PaginationControls page={1} size={20} total={40} onPageChange={() => {}} />);
    expect(screen.getByTestId('queue-pagination-prev')).toBeDisabled();
    expect(screen.getByTestId('queue-pagination-next')).not.toBeDisabled();
    expect(screen.getByTestId('queue-page-indicator')).toHaveTextContent('1 / 2');
  });

  it('last page: next disabled, prev enabled', () => {
    render(<PaginationControls page={2} size={20} total={40} onPageChange={() => {}} />);
    expect(screen.getByTestId('queue-pagination-next')).toBeDisabled();
    expect(screen.getByTestId('queue-pagination-prev')).not.toBeDisabled();
  });

  it('middle page: both enabled; onPageChange fires next/prev page', () => {
    const onPageChange = vi.fn();
    render(<PaginationControls page={2} size={20} total={100} onPageChange={onPageChange} />);
    fireEvent.click(screen.getByTestId('queue-pagination-next'));
    fireEvent.click(screen.getByTestId('queue-pagination-prev'));
    expect(onPageChange).toHaveBeenNthCalledWith(1, 3);
    expect(onPageChange).toHaveBeenNthCalledWith(2, 1);
  });
});
