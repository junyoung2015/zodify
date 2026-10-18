import type { Page } from "../src/routes";
import examples from "../src/examples.json";
import { release, REPOSITORY, SITE_ORIGIN } from "../src/siteMeta";

// Explicit static resources, not Accept-header content negotiation.
export const markdownPath = (page: Page) =>
  page.path === "/404.html" ? "/404.md" : page.path + "index.md";

const absolute = (href: string, page: Page) =>
  href.startsWith("#") ? SITE_ORIGIN + page.path + href
    : href.startsWith("/") ? SITE_ORIGIN + href : href;

export function renderMarkdown(page: Page) {
  const blocks = [
    `# ${page.title}`,
    page.description,
    `HTML: ${SITE_ORIGIN + page.path}`,
    `Released zodify ${release.version}; Python ${release.python}; alpha. Release manifest verified ${release.verified}.`,
  ];
  for (const section of page.sections) {
    blocks.push(`## ${section.title}`, ...section.paragraphs);
    if (section.command) blocks.push("```sh\n" + section.command + "\n```");
    if (section.example) {
      const example = examples[section.example];
      blocks.push("```python\n" + example.code.trimEnd() + "\n```");
      blocks.push("Expected output:\n\n```text\n" + example.expected + "\n```");
      blocks.push(`[Download Python example](${SITE_ORIGIN}/examples/${section.example}.py)`);
    }
    if (section.table) {
      const row = (cells: string[]) => "| " + cells.map((cell) => cell.replace(/\|/g, "\\|")).join(" | ") + " |";
      blocks.push([
        row(section.table.headers),
        row(section.table.headers.map(() => "---")),
        ...section.table.rows.map(row),
      ].join("\n"));
    }
    if (section.links) blocks.push(section.links.map(([label, href]) => `- [${label}](${absolute(href, page)})`).join("\n"));
  }
  blocks.push(`Updated ${page.updated}. [Project source](${REPOSITORY}).`);
  return blocks.join("\n\n") + "\n";
}

export function renderAgentGuide(pages: Page[]) {
  return `# zodify

> Validation for Python dictionaries using ordinary Python types.

Released version: ${release.version}; Python ${release.python}; verified ${release.verified}. Zero required runtime dependencies. MIT license. This manifest is a dated release check; check PyPI for published versions.

**When to use zodify.**

Use zodify inside Python scripts to validate configuration dictionaries, parsed command-line arguments, and JSON objects at an application boundary. Choose it when reusable plain-dict checks and zero required runtime dependencies fit the task. Direct Python checks may suffice for a small one-off check. Use a broader model framework or JSON Schema validator when those contracts are required.

**How to call zodify.**

Install the documented release in the caller's Python environment with \`python -m pip install zodify==${release.version}\`. Import \`validate\` from \`zodify\` and call \`validate(schema, data)\`: schema first, dictionary data second. This is a local Python library; this documentation site provides no hosted validation HTTP API, OpenAPI service, MCP server, or official CLI executable. Shell installation commands and the argparse guide do not imply a zodify CLI.

\`validate\` returns a validated dict for dict schemas. Invalid data raises ValueError by default; \`error_mode="structured"\` raises ValidationError. Types are exact by default, unknown keys are rejected, and \`coerce=True\` opts into conversion. Defaults are trusted, inserted without validation or copying, and can be shared. The default max_depth is 32. Review error text before logging it because coercion and callback messages can include sensitive input.

The following example is the same released-version fixture used by the getting-started guide:

\`\`\`python
${examples.quickstart.code.trimEnd()}
\`\`\`

Version ${release.version} also includes canonical error details, \`zodify.json_io.validate_json\`, conservative exact JSON Schema export, and \`load_env\`. Compilation and rich reports remain unavailable. Follow the versioned reference rather than inventing APIs from proposed work.

The HTML pages work without JavaScript. Each page has an explicit static Markdown counterpart at its path plus \`index.md\`, for example /docs/index.md. These downloads do not provide Accept-header negotiation. A consolidated snapshot is available at [llms-full.txt](${SITE_ORIGIN}/llms-full.txt).

## Documentation

${pages.map((page) => `- [${page.title}](${SITE_ORIGIN + page.path}): ${page.description} [Markdown](${SITE_ORIGIN + markdownPath(page)})`).join("\n")}

## Project and release evidence

- [Published package](https://pypi.org/project/zodify/${release.version}/)
- [Release manifest](${SITE_ORIGIN}/release.json)
- [Source and full API reference](${REPOSITORY}/blob/main/reference/api.md)
- [Sitemap](${SITE_ORIGIN}/sitemap.xml)
- [Contact](${SITE_ORIGIN}/contact/)
- [Privacy](${SITE_ORIGIN}/privacy/)
`;
}
