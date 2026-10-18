import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import assert from "node:assert/strict";
import { routes } from "../src/routes";
import examples from "../src/examples.json";
import { SITE_ORIGIN, release } from "../src/siteMeta";
import { markdownPath } from "./content-resources";
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
  assert(!html.includes("<form"), `Unexpected data collection form: ${page.path}`);
  assert.deepEqual([...html.matchAll(/<script[^>]+src="([^"]+)"/g)].map((match) => match[1]), ["/enhance.js"]);
  const structured = JSON.parse(html.match(/<script type="application\/ld\+json">(.*?)<\/script>/s)![1]);
  const application = structured["@graph"].find((entity: Record<string, unknown>) => entity["@type"] === "SoftwareApplication");
  const source = structured["@graph"].find((entity: Record<string, unknown>) => entity["@type"] === "SoftwareSourceCode");
  assert.equal(application.name, "zodify");
  assert.equal(application.softwareVersion, release.version);
  assert.equal(source.version, release.version);
  assert.equal(application.installUrl, `https://pypi.org/project/zodify/${release.version}/`);
  assert(!("downloadUrl" in application));
  assert.equal(source.targetProduct["@id"], application["@id"]);
  assert(!structured["@graph"].some((entity: Record<string, unknown>) => entity["@type"] === "Organization"));
  assert(html.includes(`<meta property="og:image" content="${SITE_ORIGIN}/og-image.png">`));
  assert(html.includes(`<link rel="alternate" type="text/markdown" href="${SITE_ORIGIN + markdownPath(page)}">`));
  assert(html.includes('<link rel="describedby" href="/llms.txt" type="text/plain">'));
  const markdown = readFileSync(join(dist, markdownPath(page).slice(1)), "utf8");
  assert(markdown.startsWith(`# ${page.title}\n`));
  assert(markdown.includes(page.description));
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
    assert(markdown.includes(`## ${section.title}`));
    for (const paragraph of section.paragraphs) assert(markdown.includes(paragraph));
    if (section.command) assert(markdown.includes("```sh\n" + section.command + "\n```"));
    if (section.table) for (const row of section.table.rows) for (const cell of row) assert(markdown.includes(cell.replace(/\|/g, "\\|")));
    if (section.example) {
      assert(examples[section.example]);
      assert.equal(examples[section.example].releasedVersion, release.version);
      assert(html.includes(`<code id="code-${section.example}">`));
      assert(existsSync(join(dist, "examples", section.example + ".py")));
      assert(markdown.includes(examples[section.example].code.trimEnd()));
      assert(markdown.includes(examples[section.example].expected));
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
const missingMarkdown = readFileSync(join(dist, "404.md"), "utf8");
assert(missingMarkdown.includes("Page not found"));
assert(missingMarkdown.includes(SITE_ORIGIN + "/docs/"));
const agentGuide = readFileSync(join(dist, "llms.txt"), "utf8");
assert(agentGuide.includes(`Released version: ${release.version}`));
assert(agentGuide.includes(`python -m pip install zodify==${release.version}`));
assert(agentGuide.includes("**When to use zodify.**"));
assert(agentGuide.includes("**How to call zodify.**"));
assert(agentGuide.includes(examples.quickstart.code.trimEnd()));
assert(agentGuide.includes("validate(schema, data)"));
assert(agentGuide.includes("no hosted validation HTTP API"));
assert(agentGuide.includes("do not provide Accept-header negotiation"));
assert.equal((agentGuide.match(/^# /gm) || []).length, 1);
// llms.txt keeps detailed guidance before its H2 sections of resource lists.
for (const list of agentGuide.split(/^## .+\n/gm).slice(1))
  assert(list.trim().split("\n").every((line) => !line.trim() || /^- \[[^\]]+\]\(https:\/\//.test(line)));
const fullGuide = readFileSync(join(dist, "llms-full.txt"), "utf8");
for (const page of routes) {
  assert(agentGuide.includes(SITE_ORIGIN + markdownPath(page)));
  assert(fullGuide.includes(readFileSync(join(dist, markdownPath(page).slice(1)), "utf8")));
}
for (const path of ["contact", "privacy"]) {
  const page = routes.find((page) => page.path === `/${path}/`)!;
  assert(page.sections.flatMap((section) => section.paragraphs).join(" ").length > 500);
  assert(readFileSync(join(dist, path, "index.html"), "utf8").includes('aria-label="Footer"'));
}
assert(readFileSync(join(dist, "contact/index.html"), "utf8").includes("/security/advisories/new"));
assert(readFileSync(join(dist, "privacy/index.html"), "utf8").includes("not a promise that a hosting provider keeps no access logs"));
const social = readFileSync(join(dist, "og-image.png"));
assert.equal(social.subarray(0, 8).toString("hex"), "89504e470d0a1a0a");
assert.equal(social.readUInt32BE(16), 1200);
assert.equal(social.readUInt32BE(20), 630);
assert(existsSync(join(dist, ".nojekyll")));
assert.equal(readFileSync(join(dist, "CNAME"), "utf8").trim(), "zodify.dev");
assert.deepEqual(JSON.parse(readFileSync(join(dist, "release.json"), "utf8")), release);
const gettingStarted = routes.find((page) => page.path === "/docs/getting-started/")!;
assert.equal(gettingStarted.sections.find((section) => section.id === "install")!.command, `python -m pip install zodify==${release.version}`);
assert(routes.find((page) => page.path === "/roadmap/")!.sections.some((section) => section.title === `Released: ${release.version}`));
assert(routes.find((page) => page.path === "/changelog/")!.sections[0].title.startsWith(release.version + ","));
// Keep measured diagnostics evidence attached to the release actually measured.
assert(routes.find((page) => page.path === "/benchmarks/")!.sections.some((section) => section.title === "The cost of canonical diagnostics in 0.8.0"));
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
  `Validated ${routes.length} routes: body, code, identity graph, social image, explicit Markdown parity, agent instructions, trust pages, canonical uniqueness, links, downloads, sitemap, CNAME, and legacy anchors.`,
);
