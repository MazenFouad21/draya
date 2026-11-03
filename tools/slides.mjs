// Screenshot every slide of a built preview. Usage: node tools/slides.mjs [preview.html] [outDir] [width] [height]
import { chromium } from 'playwright';
import { resolve } from 'node:path';
import { mkdirSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
const [file = 'shots/preview.html', out = 'shots/slides', w = '1440', h = '900'] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: +w, height: +h } });
const errs = [];
page.on('pageerror', (e) => errs.push(e.message));
await page.route(/\.mp3$/, (r) => r.abort());
await page.goto(pathToFileURL(resolve(file)).href, { waitUntil: 'networkidle' });
await page.addStyleTag({ content: '*{animation-duration:0s!important;animation-delay:0s!important;transition-duration:0s!important}' });
const n = await page.evaluate(() => document.querySelectorAll('.slide').length);
for (let i = 0; i < n; i++) {
  await page.evaluate((i) => window.go ? go(i) : null, i);
  await page.waitForTimeout(150);
  await page.screenshot({ path: `${out}/${String(i + 1).padStart(2, '0')}.png` });
}
console.log(`${n} slides -> ${out}`, errs.length ? '\nerrors: ' + errs.join('\n') : '');
await browser.close();
