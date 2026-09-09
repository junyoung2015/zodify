import { Layout } from "./components/Layout";
import { routes, notFound, type Page } from "./routes";
import { Example } from "./components/Example";
import { HomePage } from "./pages/HomePage";
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
      {page.path === "/" ? <HomePage page={page} /> : <article className="content" id="main-content">
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
            {s.example && <Example name={s.example} />}
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
      </article>}
    </Layout>
  );
}
