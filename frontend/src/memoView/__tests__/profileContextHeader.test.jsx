import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ProfileContextHeader } from '../components/ProfileContextHeader.jsx';

const profile = {
  application_id: 'app-1',
  age_years_derived: 42,
  requested_cover_amount: '500000',
  demographics: { full_name: 'Jordan Rivera', gender: 'unspecified', city: 'Metropolis' },
};

// A11Y-1 / minimal identifying header (Q2-A).
describe('ProfileContextHeader — minimal identifying header', () => {
  it('renders application_id, applicant name, derived age, requested cover', () => {
    render(<ProfileContextHeader profile={profile} />);
    const header = screen.getByTestId('memo-header-context');
    expect(header).toHaveTextContent('app-1');
    expect(header).toHaveTextContent('Jordan Rivera');
    expect(header).toHaveTextContent('42');
    expect(header).toHaveTextContent('500000');
  });

  it('null profile -> renders nothing', () => {
    const { container } = render(<ProfileContextHeader profile={null} />);
    expect(container.firstChild).toBeNull();
  });
});
