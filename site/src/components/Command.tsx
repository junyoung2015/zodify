import { CopyButton } from "./CodeActions";

export function Command({ children, name = "install" }: { children: string; name?: string }) {
  return (
    <div className="install-command">
      <pre tabIndex={0}><code id={`code-${name}`}>{children}</code></pre>
      <CopyButton name={name} label="Copy command" />
    </div>
  );
}
