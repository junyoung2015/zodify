/**
 * Post-build script: Generate per-route HTML files with correct meta tags.
 *
 * Social crawlers (Facebook, Twitter, Slack, Discord) and search engine
 * crawlers don't execute JS. In a React SPA, the <Helmet> meta tags only
 * exist after hydration. This script creates static HTML files for each
 * route with the correct <title>, <meta description>, and <link canonical>
 * baked in, so crawlers see the right metadata.
 *
 * Usage: node scripts/generate-route-html.mjs
 * Runs after `vite build` (see package.json "build" script).
 */

import { readFileSync, writeFileSync, mkdirSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const distDir = join(__dirname, "..", "dist");
const baseHtml = readFileSync(join(distDir, "index.html"), "utf-8");

const routes = [
  {
    path: "/benchmarks",
    title: "Benchmarks - zodify",
    description:
      "Performance benchmarks comparing zodify against pydantic, voluptuous, schema, and cerberus. 615K ops/sec, 48KB installed, 4ms import time.",
    canonical: "https://zodify.dev/benchmarks",
  },
  {
    path: "/docs",
    title: "Docs - zodify",
    description:
      "Documentation for zodify: installation, schemas, validation, type coercion, union types, custom validators, environment variables, and structured errors.",
    canonical: "https://zodify.dev/docs",
  },
  {
    path: "/about",
    title: "About - zodify",
    description:
      "How a 20-line automation script turned into a published Python validation library - the story behind zodify and why it exists.",
    canonical: "https://zodify.dev/about",
  },
];

for (const route of routes) {
  let html = baseHtml;

  // Replace <title>
  html = html.replace(/<title>[^<]*<\/title>/, `<title>${route.title}</title>`);

  // Replace meta name="title"
  html = html.replace(
    /<meta\s+name="title"\s+content="[^"]*"\s*\/?>/,
    `<meta name="title" content="${route.title}" />`,
  );

  // Replace meta name="description"
  html = html.replace(
    /<meta\s+name="description"\s+content="[^"]*"\s*\/?>/,
    `<meta name="description" content="${route.description}" />`,
  );

  // Replace canonical link
  html = html.replace(
    /<link\s+rel="canonical"\s+href="[^"]*"\s*\/?>/,
    `<link rel="canonical" href="${route.canonical}" />`,
  );

  // Replace OG tags
  html = html.replace(
    /<meta\s+property="og:title"\s+content="[^"]*"\s*\/?>/,
    `<meta property="og:title" content="${route.title}" />`,
  );
  html = html.replace(
    /<meta\s+property="og:description"\s+content="[^"]*"\s*\/?>/,
    `<meta property="og:description" content="${route.description}" />`,
  );
  html = html.replace(
    /<meta\s+property="og:url"\s+content="[^"]*"\s*\/?>/,
    `<meta property="og:url" content="${route.canonical}" />`,
  );

  // Replace Twitter tags
  html = html.replace(
    /<meta\s+property="twitter:title"\s+content="[^"]*"\s*\/?>/,
    `<meta property="twitter:title" content="${route.title}" />`,
  );
  html = html.replace(
    /<meta\s+property="twitter:description"\s+content="[^"]*"\s*\/?>/,
    `<meta property="twitter:description" content="${route.description}" />`,
  );
  html = html.replace(
    /<meta\s+property="twitter:url"\s+content="[^"]*"\s*\/?>/,
    `<meta property="twitter:url" content="${route.canonical}" />`,
  );

  // Write to dist/{route}/index.html
  const routeDir = join(distDir, route.path.slice(1));
  mkdirSync(routeDir, { recursive: true });
  writeFileSync(join(routeDir, "index.html"), html);
  console.log(`  ✓ ${route.path}/index.html`);
}

console.log(`\n  Generated ${routes.length} route HTML files.`);
