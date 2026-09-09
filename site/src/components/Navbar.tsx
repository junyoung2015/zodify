import { routes } from "../routes";
import { SITE_VERSION, REPOSITORY } from "../siteMeta";
export function Navbar() {
  return (
    <header className="site-header">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <a className="brand" href="/">
        <img src="/brand/lockup-dark.svg" alt="zodify" width="147" height="41" />
        <span>{SITE_VERSION}</span>
      </a>
      <nav aria-label="Main navigation">
        {routes
          .filter((p) => p.nav)
          .map((p) => (
            <a key={p.path} href={p.path}>
              {p.nav}
            </a>
          ))}
        <a href={REPOSITORY}>GitHub</a>
      </nav>
    </header>
  );
}
