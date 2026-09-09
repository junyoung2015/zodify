export function Command({ children, name = "install" }: { children: string; name?: string }) {
  return (
    <div className="install-command">
      <pre tabIndex={0}><code id={`code-${name}`}>{children}</code></pre>
      <button hidden data-copy={name} aria-live="polite">Copy command</button>
    </div>
  );
}
