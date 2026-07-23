// C2 — a bordered content region; layout primitive. `title` is a caller-supplied prop
// (never an inlined display label). Exposes a stable data-testid.
export function Panel({ title = null, children, testid }) {
  return (
    <section data-testid={testid} className="shell-panel">
      {title ? <h2 className="shell-panel-title">{title}</h2> : null}
      <div className="shell-panel-body">{children}</div>
    </section>
  );
}

export default Panel;
