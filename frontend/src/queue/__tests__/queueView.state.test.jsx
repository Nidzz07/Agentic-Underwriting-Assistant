import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueueView } from '../QueueView.jsx';

// FETCH-1 — the four per-state renders, each on the single injected capturing double (Fold-1).
const ROW = { application_id: 'app-1', recommendation: 'APPROVE', confidence: 'High' };

describe('QueueView — FETCH-1 four render states', () => {
  it('loading: shows the loading state while the fetch is in flight', () => {
    const pending = () => new Promise(() => {}); // never resolves
    render(<QueueView fetchSeam={pending} onSelect={() => {}} />);
    expect(screen.getByTestId('queue-state-loading')).toBeInTheDocument();
  });

  it('ready: non-empty items -> table', async () => {
    const seam = async () => ({ items: [ROW], page: { page: 1, size: 20, total: 1 } });
    render(<QueueView fetchSeam={seam} onSelect={() => {}} />);
    expect(await screen.findByTestId('queue-table')).toBeInTheDocument();
  });

  it('empty: items [] -> empty state', async () => {
    const seam = async () => ({ items: [], page: { page: 1, size: 20, total: 0 } });
    render(<QueueView fetchSeam={seam} onSelect={() => {}} />);
    expect(await screen.findByTestId('queue-state-empty')).toBeInTheDocument();
  });

  it('error: rejection envelope -> error state with message', async () => {
    const seam = async () => { throw { error: { code: 'internal_error', message: 'kaboom', detail: {} } }; };
    render(<QueueView fetchSeam={seam} onSelect={() => {}} />);
    expect(await screen.findByTestId('queue-state-error')).toBeInTheDocument();
    expect(screen.getByTestId('queue-error-message')).toHaveTextContent('kaboom');
  });
});
