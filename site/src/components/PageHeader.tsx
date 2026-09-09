import { release } from "../siteMeta";
import type { Page } from "../routes";

export function ReleaseMeta() {
  return (
    <p className="release-meta">
      Python {release.python} /{" "}
      <a href={`https://pypi.org/project/zodify/${release.version}/`}>
        released zodify {release.version}
      </a> / Alpha
    </p>
  );
}

export function PageHeader({ page }: { page: Page }) {
  const isGuide = page.path.startsWith("/guides/");
  const isReference = page.path.startsWith("/docs/") && page.path !== "/docs/";
  return (
    <header className="page-header">
      {(isGuide || isReference) && (
        <nav className="breadcrumb" aria-label="Breadcrumb">
          <a href="/docs/">Docs</a>
          <span aria-hidden="true">/</span>
          <span>{isGuide ? "Task guides" : "Reference and tutorials"}</span>
        </nav>
      )}
      <h1>{page.title}</h1>
      <p className="lede">{page.description}</p>
      <ReleaseMeta />
    </header>
  );
}
