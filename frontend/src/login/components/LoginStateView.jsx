import { LOGIN_COPY } from '../copy.js';

// C3 — the error render state. ErrorEnvelopeToRenderPattern (ERROR-1), identical in shape to
// every sibling unit: `message` VISIBLE, `code` in a testid-only hidden node, `detail` NEVER
// rendered.
//
// ⚑ The message is the SERVER'S, rendered verbatim and unexamined. This component does not
// branch on the code, does not count attempts, and does not hint at lockout — the backend
// deliberately makes a wrong password and a locked account indistinguishable, and a client
// that reconstructed the difference would re-open the enumeration oracle the backend closed.
export function LoginStateView({ error }) {
  const envelope = error && error.error
    ? error.error
    : { code: 'unknown_error', message: LOGIN_COPY.unknownErrorMessage };

  return (
    <div data-testid="login-state-error" role="alert">
      <p data-testid="login-error-message">{envelope.message}</p>
      <span data-testid="login-error-code" hidden>{envelope.code}</span>
    </div>
  );
}

export default LoginStateView;
