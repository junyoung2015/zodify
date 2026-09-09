import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import {
  readFileSync,
  writeFileSync,
  mkdirSync,
  existsSync,
  readdirSync,
  rmSync,
} from "node:fs";
import { join, dirname } from "node:path";
import App from "../src/App";
import { routes, notFound } from "../src/routes";
import { release, SITE_ORIGIN, REPOSITORY } from "../src/siteMeta";
import examples from "../src/examples.json";
const dist = join(process.cwd(), "dist");
const base = readFileSync(join(dist, "index.html"), "utf8");
const css = [...base.matchAll(/<link[^>]+rel="stylesheet"[^>]*>/g)]
  .map((x) => x[0])
  .join("");
if (!css) throw new Error("Missing built stylesheet");
const escape = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
for (const page of [...routes, notFound]) {
  const canonical = SITE_ORIGIN + page.path;
  const title = page.title + " — zodify";
  const project = {
    "@context": "https://schema.org",
    "@type": "SoftwareSourceCode",
    "@id": SITE_ORIGIN + "/#project",
    name: "zodify",
    url: SITE_ORIGIN + "/",
    codeRepository: REPOSITORY,
    programmingLanguage: "Python",
    license: "https://opensource.org/licenses/MIT",
    version: release.version,
    description: routes[0].description,
  };
  const head = `<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>${escape(title)}</title><meta name="description" content="${escape(page.description)}">${page === notFound ? '<meta name="robots" content="noindex">' : `<link rel="canonical" href="${canonical}">`}<meta property="og:type" content="website"><meta property="og:title" content="${escape(title)}"><meta property="og:description" content="${escape(page.description)}"><meta property="og:url" content="${canonical}"><meta name="twitter:card" content="summary"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon-32x32.png" type="image/png" sizes="32x32"><link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">${css}<script type="application/ld+json">${JSON.stringify(project).replace(/</g, "\u003c")}</script>`;
  const html = `<!doctype html><html lang="en"><head>${head}</head><body>${renderToStaticMarkup(<App page={page} />)}<script src="/enhance.js" defer></script></body></html>`;
  const file = join(
    dist,
    page === notFound ? "404.html" : page.path.slice(1),
    page === notFound ? "" : "index.html",
  );
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, html);
}
mkdirSync(join(dist, "examples"), { recursive: true });
for (const [name, example] of Object.entries(examples))
  writeFileSync(join(dist, "examples", name + ".py"), example.code);
writeFileSync(
  join(dist, "release.json"),
  JSON.stringify(release, null, 2) + "\n",
);
writeFileSync(
  join(dist, "sitemap.xml"),
  '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
    routes
      .map(
        (p) =>
          `<url><loc>${SITE_ORIGIN + p.path}</loc><lastmod>${p.updated}</lastmod></url>`,
      )
      .join("") +
    "</urlset>\n",
);
writeFileSync(
  join(dist, "llms.txt"),
  `# zodify\n\n> Small, predictable validation for plain Python data.\n\nReleased version: ${release.version}; Python ${release.python}; verified ${release.verified}. Zero required runtime dependencies. MIT license.\n\nVersion 0.8.0 includes canonical details, zodify.json_io.validate_json, conservative exact JSON Schema export, and load_env. Compilation and rich reports remain unavailable. Source versions alone do not establish publication.\n\n` +
    routes
      .map((p) => `- [${p.title}](${SITE_ORIGIN + p.path}): ${p.description}`)
      .join("\n") +
    "\n",
);
// Do not ship the retired marketing images or unused app bundle.
for (const file of ["og-image.png", "og-image.svg"])
  if (existsSync(join(dist, file))) rmSync(join(dist, file));
for (const file of readdirSync(join(dist, "assets")))
  if (file.endsWith(".js")) rmSync(join(dist, "assets", file));
writeFileSync(join(dist, ".nojekyll"), "");
console.log(
  `Rendered ${routes.length} complete content pages, a real 404, and ${Object.keys(examples).length} downloadable examples.`,
);
