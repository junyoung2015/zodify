// Optional local browser gate: supply PLAYWRIGHT_MODULE when using a bundled runtime.
import assert from "node:assert/strict";
import { mkdirSync } from "node:fs";
const { chromium } = await import(
  process.env.PLAYWRIGHT_MODULE || "playwright"
);
const origin = process.env.SITE_URL || "http://127.0.0.1:4175";
const browser = await chromium.launch({ channel: "chrome", headless: true });
const context = await browser.newContext({ javaScriptEnabled: false });
const page = await context.newPage();
mkdirSync("output/playwright", { recursive: true });
for (const path of [
  "/",
  "/docs/",
  "/docs/types-and-coercion/",
  "/guides/json-object-validation/",
  "/benchmarks/",
  "/about/",
  "/contact/",
  "/privacy/",
  "/articles/python-314-class-annotations/",
]) {
  const response = await page.goto(origin + path);
  assert.equal(response.status(), 200);
  assert(await page.locator("h1").isVisible());
  assert(await page.locator("main").innerText());
  const nav = page.getByRole("navigation", { name: "Main navigation" });
  assert(await nav.isVisible());
  assert(
    await nav.getByRole("link", { name: "Docs", exact: true }).isVisible(),
  );
  await nav.getByRole("link", { name: "Docs", exact: true }).click();
  assert.equal(new URL(page.url()).pathname, "/docs/");
}
await page.goto(origin + "/docs/#structured-errors");
assert(await page.locator("#structured-errors").isVisible());
await page.goto(origin + "/");
await page.screenshot({
  path: "output/playwright/site-home-desktop.png",
  fullPage: true,
});
await page.setViewportSize({ width: 390, height: 844 });
await page.goto(origin + "/guides/json-object-validation/");
assert.equal(
  await page.evaluate(
    () => document.documentElement.scrollWidth <= window.innerWidth,
  ),
  true,
);
assert.equal(
  await page
    .locator(".example > pre")
    .evaluate((el) => el.scrollWidth > el.clientWidth),
  true,
);
await page.screenshot({
  path: "output/playwright/site-json-mobile.png",
  fullPage: true,
});
await page.goto(origin + "/articles/python-314-class-annotations/#execution");
assert(await page.locator("#execution").isVisible());
assert.equal(await page.locator(".example").count(), 3);
assert.equal(
  await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
  true,
);
for (const id of ["annotation-namespace", "annotation-release-comparison", "annotation-execution"]) {
  assert(await page.locator(`#code-${id}`).isVisible());
  assert(await page.locator(`a[href="/examples/${id}.py"]`).isVisible());
}
await page.screenshot({
  path: "output/playwright/site-annotations-mobile.png",
  fullPage: true,
});
const missing = await page.goto(origin + "/this-route-should-not-exist/");
assert.equal(missing.status(), 404);
assert.equal(await page.locator("h1").innerText(), "Page not found");
await context.close();
const enhanced = await browser.newContext({
  permissions: ["clipboard-read", "clipboard-write"],
});
const interactive = await enhanced.newPage();
await interactive.goto(origin + "/docs/getting-started/");
await interactive
  .getByRole("button", { name: "Copy example", exact: true })
  .click();
await interactive
  .locator('button[data-copy][data-state="copied"]')
  .waitFor({ state: "visible" });
assert.equal(
  await interactive
    .getByRole("button", { name: "Copy example", exact: true })
    .getAttribute("data-state"),
  "copied",
);
assert.equal(
  await interactive.locator(".example [role='status']").innerText(),
  "Example copied to clipboard.",
);
assert.equal(
  await interactive.evaluate(() => navigator.clipboard.readText()),
  await interactive.locator(".example > pre code").textContent(),
);
await browser.close();
console.log(
  "Browser gate passed: no-JS primary pages and links, legacy fragment, mobile overflow, real 404, and copy feedback.",
);
