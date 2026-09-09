import { Layout } from "./components/Layout";
import { routes, notFound, type Page } from "./routes";
import { PageHeader } from "./components/PageHeader";
import { SectionContent } from "./components/SectionContent";
import { HomePage } from "./pages/HomePage";
import { DocsPage } from "./pages/DocsPage";
import { REPOSITORY } from "./siteMeta";
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
    <Layout path={page.path}>
      {page.path === "/" ? <HomePage page={page} /> : page.path === "/docs/" ? <DocsPage page={page} /> : <article className="content document-content" id="main-content">
        <PageHeader page={page} />
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
        {page.sections.map((s) => <SectionContent key={s.id} section={s} />)}
        <p className="page-meta">
          Updated {page.updated} /{" "}
          <a href={`${REPOSITORY}/edit/main/site/src/routes.ts`}>
            Edit this page
          </a>
        </p>
      </article>}
    </Layout>
  );
}
