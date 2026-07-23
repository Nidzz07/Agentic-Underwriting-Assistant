import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueueStateView } from '../components/QueueStateView.jsx';

// FETCH-1 (loading/empty renders) + ERROR-1 (message visible / code testid-only / detail never rendered).
describe('QueueStateView — loading / empty / error', () => {
  it('loading: container present + skeleton rows; no real table', () => {
    render(<QueueStateView state="loading" />);
    expect(screen.getByTestId('queue-state-loading')).toBeInTheDocument();
    expect(screen.getAllByTestId('queue-skeleton-row').length).toBeGreaterThan(0);
    expect(screen.queryByTestId('queue-table')).toBeNull();
  });

  it('empty: distinct no-applications message', () => {
    render(<QueueStateView state="empty" />);
    expect(screen.getByTestId('queue-state-empty')).toHaveTextContent('No applications in the queue');
  });

  it('error: message VISIBLE, code present-but-hidden, detail NEVER rendered (ERROR-1)', () => {
    const error = { error: { code: 'forbidden', message: 'You cannot view this.', detail: { secretHint: 'do-not-render' } } };
    render(<QueueStateView state="error" error={error} onRetry={() => {}} />);
    const msg = screen.getByTestId('queue-error-message');
    expect(msg).toBeVisible();
    expect(msg).toHaveTextContent('You cannot view this.');
    const code = screen.getByTestId('queue-error-code');
    expect(code).toHaveTextContent('forbidden');
    expect(code).not.toBeVisible();
    expect(document.body.innerHTML).not.toContain('do-not-render'); // detail leaks nowhere
  });

  it('error: Retry calls onRetry; absent without onRetry; defensive fallback message', () => {
    const onRetry = vi.fn();
    const { rerender } = render(<QueueStateView state="error" error={{ error: { code: 'x', message: 'm' } }} onRetry={onRetry} />);
    fireEvent.click(screen.getByTestId('queue-error-retry'));
    expect(onRetry).toHaveBeenCalledTimes(1);
    rerender(<QueueStateView state="error" error={null} />);
    expect(screen.queryByTestId('queue-error-retry')).toBeNull();
    expect(screen.getByTestId('queue-error-message')).toHaveTextContent('Something went wrong.');
  });
});
