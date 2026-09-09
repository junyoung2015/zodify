import { CopyButton, DownloadLink } from "./CodeActions";
import examples from "../examples.json";
import { PythonCode } from "./PythonCode";

export function Example({ name }: { name: keyof typeof examples }) {
  const example = examples[name];
  return (
    <div className="example">
      <div className="example-toolbar">
        <span>Python</span>
        <div className="example-actions">
          <CopyButton name={name} label="Copy example" />
          <DownloadLink name={name} />
        </div>
      </div>
      <pre tabIndex={0}><code id={`code-${name}`}><PythonCode>{example.code}</PythonCode></code></pre>
      <div className="example-output">
        <span>Output</span>
        <pre tabIndex={0}><code>{example.expected}</code></pre>
      </div>
    </div>
  );
}
