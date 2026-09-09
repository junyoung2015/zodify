import type { Page } from "../routes";
import { REPOSITORY } from "../siteMeta";
import { PageHeader } from "../components/PageHeader";
import { SectionContent } from "../components/SectionContent";

export function DocsPage({ page }: { page: Page }) {
  const start = page.sections.filter((s) => ["install", "basic-validation"].includes(s.id));
  const guides = page.sections.filter((s) => s.id === "faq");
  const reference = page.sections.filter((s) => !["install", "basic-validation", "faq"].includes(s.id));
  return (
    <article className="content docs-index" id="main-content">
      <PageHeader page={page} />
      <nav className="docs-paths" aria-label="Documentation sections">
        <a href="#start-here">Start here</a>
        <a href="#faq">Task guides</a>
        <a href="#api-reference">API reference</a>
      </nav>
      <section id="start-here">
        <h2 className="visually-hidden">Start here</h2>
        <div className="docs-start">
          {start.map((s) => <SectionContent key={s.id} section={s} level={3} />)}
        </div>
      </section>
      {guides.map((s) => <SectionContent key={s.id} section={s} />)}
      <section id="api-reference">
        <h2>API reference</h2>
        <p>Look up a specific behavior below. The <a href={`${REPOSITORY}/blob/main/reference/api.md`}>full API reference</a> includes parameter tables, env-file parsing, and JSON export limits.</p>
        <div className="reference-index">
          {reference.map((s) => <SectionContent key={s.id} section={s} level={3} />)}
        </div>
      </section>
    </article>
  );
}
