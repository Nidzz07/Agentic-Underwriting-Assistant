import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueueRow } from '../components/QueueRow.jsx';
import { RECOMMENDATION_LABELS, CONFIDENCE_LABELS } from '../../shell/copy/index.js';

function renderRow(summary, onSelect = () => {}) {
  return render(<table><tbody><QueueRow summary={summary} onSelect={onSelect} /></tbody></table>);
}

// PENDING-1 / COPY-1 (look-up) / SELECT-1 (emission-only).
describe('QueueRow', () => {
  it('renders shell badges BY VALUE look-up (COPY-1); no inlined label', () => {
    renderRow({ application_id: 'app-1', recommendation: 'DECLINE-RECOMMEND', confidence: 'Low' });
    expect(screen.getByTestId('queue-row-recommendation-app-1')).toHaveTextContent(RECOMMENDATION_LABELS['DECLINE-RECOMMEND']);
    expect(screen.getByTestId('queue-row-confidence-app-1')).toHaveTextContent(CONFIDENCE_LABELS.Low);
  });

  it('null recommendation/confidence -> pending placeholder, no badge, row present (PENDING-1)', () => {
    renderRow({ application_id: 'app-2', recommendation: null, confidence: null });
    expect(screen.getByTestId('queue-row-app-2')).toBeInTheDocument();
    expect(screen.getByTestId('queue-row-pending-app-2')).toBeInTheDocument();
    expect(screen.queryByTestId('queue-row-recommendation-app-2')).toBeNull();
    expect(screen.queryByTestId('queue-row-confidence-app-2')).toBeNull();
  });

  it('select affordance emits onSelect(application_id) once (SELECT-1)', () => {
    const onSelect = vi.fn();
    renderRow({ application_id: 'app-3', recommendation: 'APPROVE', confidence: 'High' }, onSelect);
    fireEvent.click(screen.getByTestId('queue-row-select-app-3'));
    expect(onSelect).toHaveBeenCalledTimes(1);
    expect(onSelect).toHaveBeenCalledWith('app-3');
  });
});
