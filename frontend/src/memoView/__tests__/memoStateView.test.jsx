import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoStateView } from '../components/MemoStateView.jsx';

// FETCH-1 (loading/pending renders) + ERROR-1 (message visible / code testid-only / detail never).
describe('MemoStateView — loading / pending / error', () => {
  it('loading: container present; no memo region', () => {
    render(<MemoStateView state="loading" />);
    expect(screen.getByTestId('memo-state-loading')).toBeInTheDocument();
    expect(screen.queryByTestId('memo-region-narrative')).toBeNull();
  });

  it('pending: distinct not-yet-drafted message', () => {
    render(<MemoStateView state="pending" />);
    expect(screen.getByTestId('memo-state-pending')).toBeInTheDocument();
  });

  it('error: message VISIBLE, code present-but-hidden, detail NEVER rendered (ERROR-1)', () => {
    const error = { error: { code: 'forbidden', message: 'You cannot view this.', detail: { secretHint: 'do-not-render' } } };
    render(<MemoStateView state="error" error={error} onRetry={() => {}} />);
    const msg = screen.getByTestId('memo-error-message');
    expect(msg).toBeVisible();
    expect(msg).toHaveTextContent('You cannot view this.');
    const code = screen.getByTestId('memo-error-code');
    expect(code).toHaveTextContent('forbidden');
    expect(code).not.toBeVisible();
    expect(document.body.innerHTML).not.toContain('do-not-render'); // detail leaks nowhere
  });

  it('error: Retry calls onRetry; absent without onRetry; defensive fallback message', () => {
    const onRetry = vi.fn();
    const { rerender } = render(<MemoStateView state="error" error={{ error: { code: 'x', message: 'm' } }} onRetry={onRetry} />);
    fireEvent.click(screen.getByTestId('memo-error-retry'));
    expect(onRetry).toHaveBeenCalledTimes(1);
    rerender(<MemoStateView state="error" error={null} />);
    expect(screen.queryByTestId('memo-error-retry')).toBeNull();
    expect(screen.getByTestId('memo-error-message')).toHaveTextContent('Something went wrong.');
  });
});
