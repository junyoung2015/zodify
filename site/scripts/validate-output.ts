import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import assert from "node:assert/strict";
import { routes } from "../src/routes";
import examples from "../src/examples.json";
import { SITE_ORIGIN, release } from "../src/siteMeta";
const dist = join(process.cwd(), "dist");
const canonicals = new Set();
for (const page of routes) {
  const html = readFileSync(
    join(dist, page.path.slice(1), "index.html"),
    "utf8",
  );
  assert(html.includes("<h1>"), `Missing h1: ${page.path}`);
  assert.equal((html.match(/<h1>/g) || []).length, 1);
  assert(
    html.includes(page.title.replace(/&/g, "&amp;")),
    `Missing heading: ${page.path}`,
  );
  assert(
    html.includes("<main>") && html.includes("<section"),
    `Missing primary content: ${page.path}`,
  );
  const canonical = [...html.matchAll(/<link rel="canonical" href="([^"]+)"/g)];
  assert.equal(canonical.length, 1);
  assert.equal(canonical[0][1], SITE_ORIGIN + page.path);
  assert(!canonicals.has(canonical[0][1]));
  canonicals.add(canonical[0][1]);
  assert.equal((html.match(/<title>/g) || []).length, 1);
  assert(
    !/opacity:\s*0|id="root"><\/div>|fastest pure-python|533K|381 collected/i.test(
      html,
    ),
  );
  assert(html.includes(`released zodify ${release.version}`));
  const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]);
  assert.equal(ids.length, new Set(ids).size);
  for (const section of page.sections) {
    assert(ids.includes(section.id));
    if (section.example) {
      assert(examples[section.example]);
      assert(html.includes(`<code id="code-${section.example}">`));
      assert(existsSync(join(dist, "examples", section.example + ".py")));
    }
  }
  for (const match of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const href = match[1];
    if (!href.startsWith("/") && !href.startsWith("#")) continue;
    const [path, fragment] = href.split("#");
    const target = path
      ? join(dist, path.slice(1), path.endsWith("/") ? "index.html" : "")
      : join(dist, page.path.slice(1), "index.html");
    assert(existsSync(target), `Broken link on ${page.path}: ${href}`);
    if (fragment)
      assert(
        readFileSync(target, "utf8").includes(`id="${fragment}"`),
        `Broken fragment ${href}`,
      );
  }
}
const missing = readFileSync(join(dist, "404.html"), "utf8");
assert(missing.includes("Page not found"));
assert(missing.includes('name="robots" content="noindex"'));
assert(!missing.includes('rel="canonical"'));
assert.equal(readFileSync(join(dist, "CNAME"), "utf8").trim(), "zodify.dev");
const sitemap = readFileSync(join(dist, "sitemap.xml"), "utf8");
assert.equal((sitemap.match(/<loc>/g) || []).length, routes.length);
for (const canonical of canonicals)
  assert(sitemap.includes(`<loc>${canonical}</loc>`));
for (const id of [
  "install",
  "basic-validation",
  "type-support",
  "optional-keys",
  "union-types",
  "nested-schemas",
  "class-schemas",
  "custom-validators",
  "environment-apis",
  "error-handling",
  "structured-errors",
  "faq",
])
  assert(
    readFileSync(join(dist, "docs/index.html"), "utf8").includes(`id="${id}"`),
  );
console.log(
  `Validated ${routes.length} routes: body, code, metadata, canonical uniqueness, links, downloads, sitemap, CNAME, and legacy anchors.`,
);
