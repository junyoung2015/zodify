export function ActionIcon({ kind }: { kind: "copy" | "download" | "check" | "error" }) {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">
      {kind === "copy" && <><rect x="8" y="8" width="12" height="12" rx="2" /><path d="M16 8V4a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v11a1 1 0 0 0 1 1h4" /></>}
      {kind === "download" && <><path d="M12 3v12m-5-5 5 5 5-5" /><path d="M4 16v4h16v-4" /></>}
      {kind === "check" && <path d="m5 12 4 4L19 6" />}
      {kind === "error" && <><circle cx="12" cy="12" r="9" /><path d="M12 7v6m0 4h.01" /></>}
    </svg>
  );
}

export function CopyButton({ name, label }: { name: string; label: string }) {
  return (
    <span className="code-action" hidden data-copy-control>
      <button type="button" className="icon-action" data-copy={name} aria-label={label} data-state="idle">
        <span className="copy-icon"><ActionIcon kind="copy" /></span>
        <span className="copied-icon"><ActionIcon kind="check" /></span>
        <span className="error-icon"><ActionIcon kind="error" /></span>
      </button>
      <span className="action-tooltip" aria-hidden="true">{label}</span>
      <span className="visually-hidden" role="status" aria-atomic="true" />
    </span>
  );
}

export function DownloadLink({ name }: { name: string }) {
  return (
    <span className="code-action">
      <a className="icon-action" href={`/examples/${name}.py`} download aria-label="Download example as Python file">
        <ActionIcon kind="download" />
      </a>
      <span className="action-tooltip" aria-hidden="true">Download .py</span>
    </span>
  );
}
