import { SITE_VERSION, REPOSITORY } from "../siteMeta";
export function Navbar({ path }: { path: string }) {
  const docsActive = path.startsWith("/docs/") || path.startsWith("/guides/");
  return (
    <header className="site-header">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <a className="brand" href="/">
        zodify <span>{SITE_VERSION}</span>
      </a>
      <nav aria-label="Main navigation">
        <a href="/docs/" aria-current={docsActive ? (path === "/docs/" ? "page" : "location") : undefined}>Docs</a>
        <a href="/compare/" aria-current={path === "/compare/" ? "page" : undefined}>Choosing a validator</a>
        <a href={REPOSITORY}>GitHub</a>
      </nav>
    </header>
  );
}
