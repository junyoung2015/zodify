// Page content and metadata now live together in ../routes.ts.
import { Example } from "../components/Example";
import { release } from "../siteMeta";
import type { Page } from "../routes";

export function HomePage({ page }: { page: Page }) {
  return (
    <article className="content home-content" id="main-content">
      <section className="home-hero" id="start">
        <div className="home-intro">
          <h1>{page.title}</h1>
          <p className="lede">{page.description}</p>
          <a className="primary-link" href="/docs/getting-started/">Get started</a>
          <p className="release-meta">
            Python {release.python} ·{" "}
            <a href={`https://pypi.org/project/zodify/${release.version}/`}>
              released zodify {release.version}
            </a> · Alpha
          </p>
        </div>
        <div className="home-demo" aria-label="Install and validate">
          <div className="install-command">
            <pre tabIndex={0}><code id="code-install">pip install zodify</code></pre>
            <button hidden data-copy="install">Copy command</button>
          </div>
          <Example name="first-validation" />
          <p className="demo-note">A schema in, a validated dict out. Incorrect types and extra keys raise an error by default.</p>
        </div>
      </section>
      <div className="home-details">
        {page.sections.filter((s) => s.id !== "start").map((s) => (
          <section id={s.id} key={s.id}>
            <h2>{s.title}</h2>
            {s.paragraphs.map((p) => <p key={p}>{p}</p>)}
            {s.links && <ul className="related">{s.links.map(([name, href]) => (
              <li key={href}><a href={href}>{name} →</a></li>
            ))}</ul>}
          </section>
        ))}
      </div>
    </article>
  );
}
