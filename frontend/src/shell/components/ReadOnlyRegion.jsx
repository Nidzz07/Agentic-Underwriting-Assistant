// C2 — wraps read-only memo regions (recommendation / confidence) so views frame them as
// read-only (the memo-agent-core three-region shape). Presentational only.
export function ReadOnlyRegion({ children, testid }) {
  return (
    <div data-testid={testid} className="shell-readonly" aria-readonly="true">
      {children}
    </div>
  );
}

export default ReadOnlyRegion;
