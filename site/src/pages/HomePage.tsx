// Page content and metadata now live together in ../routes.ts.
import { Example } from "../components/Example";
import { ReleaseMeta } from "../components/PageHeader";
import { Command } from "../components/Command";
import { SectionContent } from "../components/SectionContent";
import type { Page } from "../routes";

export function HomePage({ page }: { page: Page }) {
  return (
    <article className="content home-content" id="main-content">
      <section className="home-hero" id="start">
        <div className="home-intro">
          <h1>{page.title}</h1>
          <p className="lede">{page.description}</p>
          <a className="primary-link" href="/docs/getting-started/">Get started</a>
          <ReleaseMeta />
        </div>
        <div className="home-demo" aria-label="Install and validate">
          <Command>pip install zodify</Command>
          <Example name="first-validation" />
          <p className="demo-note">A schema in, a validated dict out. Incorrect types and extra keys raise an error by default.</p>
        </div>
      </section>
      <div className="home-details">
        {page.sections.filter((s) => s.id !== "start").map((s) => <SectionContent key={s.id} section={s} />)}
        <a className="primary-link" href="/docs/getting-started/">Try your first validation</a>
      </div>
    </article>
  );
}
