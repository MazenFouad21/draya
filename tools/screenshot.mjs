// Screenshot a page at desktop, tablet and phone widths with Playwright.
// Usage: node tools/screenshot.mjs <file.html | url> [outDir]
import { chromium } from 'playwright';
import { resolve } from 'node:path';
import { mkdirSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const target = process.argv[2] ?? 'dirayah-template.html';
const out = process.argv[3] ?? 'shots';
const url = /^https?:/.test(target) ? target : pathToFileURL(resolve(target)).href;
const widths = [1440, 768, 390];

mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const errors = [];
for (const width of widths) {
  const page = await browser.newPage({ viewport: { width, height: 900 }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => errors.push(`[${width}] ${e.message}`));
  page.on('console', (m) => m.type() === 'error' && errors.push(`[${width}] console: ${m.text()}`));
  await page.goto(url, { waitUntil: 'networkidle' }).catch(() => page.goto(url));
  await page.waitForTimeout(500);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
  if (overflow > 0) errors.push(`[${width}] horizontal overflow: ${overflow}px`);
  const file = `${out}/${width}.png`;
  await page.screenshot({ path: file, fullPage: true });
  console.log('saved', file);
  await page.close();
}
await browser.close();
if (errors.length) console.log('\nIssues:\n' + errors.join('\n'));
