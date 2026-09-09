// Static emphasis for the Python constructs used in the maintained examples.
// Text and whitespace stay intact for copying and no-JavaScript reading.
export function PythonCode({ children }: { children: string }) {
  const tokens = children.split(/("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|#[^\n]*|\b(?:from|import|try|except|else|if|for|in|def|return|raise|class|True|False|None|print|validate)\b)/g);
  return <>{tokens.map((token, index) => {
    const kind = token.startsWith("#") ? "comment"
      : /^["']/.test(token) ? "string"
      : /^(from|import|try|except|else|if|for|in|def|return|raise|class|True|False|None)$/.test(token) ? "keyword"
      : /^(print|validate)$/.test(token) ? "function" : undefined;
    return kind ? <span className={`syntax-${kind}`} key={index}>{token}</span> : token;
  })}</>;
}
