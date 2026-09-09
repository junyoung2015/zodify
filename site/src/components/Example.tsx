import examples from "../examples.json";

export function Example({ name }: { name: keyof typeof examples }) {
  const example = examples[name];
  return (
    <div className="example">
      <div className="example-toolbar">
        <span>Python · tested on {example.releasedVersion}</span>
        <button hidden data-copy={name}>Copy example</button>
        <a href={`/examples/${name}.py`} download>Download .py</a>
      </div>
      <pre tabIndex={0}><code id={`code-${name}`}>{example.code}</code></pre>
      <p className="expected">Output: <code>{example.expected}</code></p>
    </div>
  );
}
