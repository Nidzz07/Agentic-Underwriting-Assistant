// login local UI strings (COPY-1) — kept OUT of the components, like every sibling unit.
//
// ⚑ ADVISORY-1: none of these may contain the shell's forbidden system-output vocabulary
// (DECLINE / decision / approved / declined). That vocabulary is reserved for underwriting
// outcomes; a sign-in failure is not one, and phrasing it as "declined" would blur the two.
//
// ⚑ THE FAILURE MESSAGE IS NOT DEFINED HERE. The server's message is rendered verbatim
// (ERROR-1), precisely so the client cannot invent a distinction the server withholds — a
// wrong password and a locked-out account return the SAME 401 with the SAME text, because
// telling them apart is a user-enumeration oracle. `unknownErrorMessage` below is the
// defensive fallback for a malformed envelope only.
export const LOGIN_COPY = Object.freeze({
  title: 'Sign in',
  userIdLabel: 'User ID',
  passwordLabel: 'Password',
  submitLabel: 'Sign in',
  submittingLabel: 'Signing in',
  logoutLabel: 'Sign out',
  unknownErrorMessage: 'Something went wrong.',
});
