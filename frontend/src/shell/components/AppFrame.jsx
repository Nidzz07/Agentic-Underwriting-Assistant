import { RoleProvider } from '../session/roleContext.js';

// C2 — page shell / layout chrome. Hosts the Role context provider (the C3 seam; populated later
// by WIRE-1). Presentational only; owns no business logic.
export function AppFrame({ children, user = null, testid = 'shell-appframe-root' }) {
  return (
    <div data-testid={testid} className="shell-appframe">
      <RoleProvider value={user ? user.role : null}>{children}</RoleProvider>
    </div>
  );
}

export default AppFrame;
