import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { OverrideReasonInput } from '../components/OverrideReasonInput.jsx';
import { OVERRIDE_COPY } from '../copy.js';

// CAPFREE-1 (prop-contract half, P9) — the NEW capability-free component. It renders from { value,
// onChange } alone; typing reports up via onChange. It holds text, not a commit capability (the
// structural no-seam-import half is in capabilityFree.imports.test.js).
describe('C5 OverrideReasonInput — { value, onChange }-only prop contract', () => {
  it('displays the value and reports edits via onChange', () => {
    const onChange = vi.fn();
    render(<OverrideReasonInput value="draft reason" onChange={onChange} />);
    const input = screen.getByTestId('override-reason-input');
    expect(input).toHaveValue('draft reason');
    expect(input).toHaveAttribute('aria-label', OVERRIDE_COPY.reasonPromptLabel); // label association (A11Y-1)
    fireEvent.change(input, { target: { value: 'a new reason' } });
    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange).toHaveBeenCalledWith('a new reason'); // reports the raw string
  });

  it('renders the mandatory-reason prompt + required hint (advisory-clean copy)', () => {
    render(<OverrideReasonInput value="" onChange={() => {}} />);
    expect(screen.getByText(OVERRIDE_COPY.reasonPromptLabel)).toBeInTheDocument();
    expect(screen.getByTestId('override-reason-hint')).toHaveTextContent(OVERRIDE_COPY.reasonRequiredHint);
  });
});
