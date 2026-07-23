import { QueueRow } from './QueueRow.jsx';
import { QUEUE_COPY } from '../copy.js';

// C4 — the ready-state SEMANTIC table (A11Y-1 semantic markup). Composes one QueueRow per item;
// forwards onSelect. Pure — no fetch, no state.
export function QueueTable({ items, onSelect, testid = 'queue-table' }) {
  const { columns } = QUEUE_COPY;
  return (
    <table data-testid={testid}>
      <thead>
        <tr>
          <th scope="col">{columns.application}</th>
          <th scope="col">{columns.recommendation}</th>
          <th scope="col">{columns.confidence}</th>
          <th scope="col">{columns.action}</th>
        </tr>
      </thead>
      <tbody>
        {items.map((summary) => (
          <QueueRow key={summary.application_id} summary={summary} onSelect={onSelect} />
        ))}
      </tbody>
    </table>
  );
}

export default QueueTable;
