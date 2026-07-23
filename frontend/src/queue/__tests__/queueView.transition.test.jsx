import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueueView } from '../QueueView.jsx';

// FETCH-1 — the CONSOLIDATED state-transition test (Q5-A, own file). All five transitions exercised
// on the single injected double per case: loading->ready|empty|error; error--retry-->loading; ready--page-->loading.
const ROW = { application_id: 'app-1', recommendation: 'REFER', confidence: 'Medium' };

describe('QueueView — consolidated state-transition test', () => {
  it('loading -> ready', async () => {
    const seam = async () => ({ items: [ROW], page: { page: 1, size: 20, total: 1 } });
    render(<QueueView fetchSeam={seam} onSelect={() => {}} />);
    expect(screen.getByTestId('queue-state-loading')).toBeInTheDocument();
    expect(await screen.findByTestId('queue-table')).toBeInTheDocument();
  });

  it('loading -> empty', async () => {
    const seam = async () => ({ items: [], page: { page: 1, size: 20, total: 0 } });
    render(<QueueView fetchSeam={seam} onSelect={() => {}} />);
    expect(await screen.findByTestId('queue-state-empty')).toBeInTheDocument();
  });

  it('loading -> error', async () => {
    const seam = async () => { throw { error: { code: 'internal_error', message: 'x', detail: {} } }; };
    render(<QueueView fetchSeam={seam} onSelect={() => {}} />);
    expect(await screen.findByTestId('queue-state-error')).toBeInTheDocument();
  });

  it('error --retry--> loading --> ready', async () => {
    let fail = true;
    const seam = async () => {
      if (fail) { fail = false; throw { error: { code: 'internal_error', message: 'x', detail: {} } }; }
      return { items: [ROW], page: { page: 1, size: 20, total: 1 } };
    };
    render(<QueueView fetchSeam={seam} onSelect={() => {}} />);
    fireEvent.click(await screen.findByTestId('queue-error-retry'));
    expect(await screen.findByTestId('queue-table')).toBeInTheDocument();
  });

  it('ready --page change--> loading --> ready (next page)', async () => {
    const seam = async (page) => ({
      items: [{ ...ROW, application_id: `app-${page}` }],
      page: { page, size: 20, total: 40 },
    });
    render(<QueueView fetchSeam={seam} onSelect={() => {}} />);
    await screen.findByTestId('queue-table');
    fireEvent.click(screen.getByTestId('queue-pagination-next'));
    expect(await screen.findByTestId('queue-row-app-2')).toBeInTheDocument();
  });
});
