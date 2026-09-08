import { Layout } from "./components/Layout";
import { routes, notFound, type Page } from "./routes";
import examples from "./examples.json";
import { release, REPOSITORY } from "./siteMeta";
export default function App({
  page = routes.find(
    (p) =>
      p.path ===
      (typeof window === "undefined"
        ? "/"
        : window.location.pathname.replace(/\/?$/, "/")),
  ) || notFound,
}: {
  page?: Page;
}) {
  return (
    <Layout>
      <article className="content" id="main-content">
        <p className="eyebrow">PLAIN PYTHON · ZERO RUNTIME DEPS</p>
        <h1>{page.title}</h1>
        <p className="lede">{page.description}</p>
        <aside className="release-note">
          Docs for{" "}
          <a href={`https://pypi.org/project/zodify/${release.version}/`}>
            released zodify {release.version}
          </a>{" "}
          · Python {release.python} · Verified {release.verified}.{" "}
          <a href="/roadmap/">Unreleased features</a>
        </aside>
        {page.sections.length > 1 && (
          <nav className="toc" aria-label="On this page">
            <strong>On this page</strong>
            <ul>
              {page.sections.map((s) => (
                <li key={s.id}>
                  <a href={`#${s.id}`}>{s.title}</a>
                </li>
              ))}
            </ul>
          </nav>
        )}
        {page.sections.map((s) => (
          <section id={s.id} key={s.id}>
            <h2>{s.title}</h2>
            {s.paragraphs.map((p) => (
              <p key={p}>{p}</p>
            ))}
            {s.example && (
              <div className="example">
                <div className="example-toolbar">
                  <span>
                    Python · tested on {examples[s.example].releasedVersion}
                  </span>
                  <button hidden data-copy={s.example}>
                    Copy example
                  </button>
                  <a href={`/examples/${s.example}.py`} download>
                    Download .py
                  </a>
                </div>
                <pre tabIndex={0}>
                  <code id={`code-${s.example}`}>
                    {examples[s.example].code}
                  </code>
                </pre>
                <p className="expected">
                  Expected output: <code>{examples[s.example].expected}</code>
                </p>
              </div>
            )}
            {s.links && (
              <ul className="related">
                {s.links.map(([name, href]) => (
                  <li key={href}>
                    <a href={href}>{name} →</a>
                  </li>
                ))}
              </ul>
            )}
          </section>
        ))}
        <p className="page-meta">
          Updated {page.updated} ·{" "}
          <a href={`${REPOSITORY}/edit/main/site/src/routes.ts`}>
            Edit this page
          </a>
        </p>
      </article>
    </Layout>
  );
}
