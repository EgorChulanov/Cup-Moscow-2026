// Builds deck/slides.html into the submission PDF and checks the competition limits.
// Usage: node deck/build.mjs   (env: TEAM, PLAYWRIGHT_CORE, CHROMIUM_PATH, PNG_DIR)
import { createRequire } from 'node:module';
import { existsSync, mkdirSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const team = process.env.TEAM || 'Команда';
const MAX_MB = 18;
const MAIN_SLIDES = 8;

function loadPlaywright() {
  const names = [process.env.PLAYWRIGHT_CORE, 'playwright-core', 'playwright'].filter(Boolean);
  for (const base of [join(process.cwd(), 'x.js'), join(here, 'x.js')]) {
    const req = createRequire(base);
    for (const n of names) {
      try { return req(n); } catch { /* try next */ }
    }
  }
  throw new Error('playwright-core not found: npm i playwright-core, or set PLAYWRIGHT_CORE=/path/to/playwright-core');
}

const { chromium } = loadPlaywright();
const executablePath = process.env.CHROMIUM_PATH || (existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined);
mkdirSync(join(here, 'out'), { recursive: true });
const out = join(here, 'out', `CupMoscow2026-Т-Банк-${team}.pdf`);

const browser = await chromium.launch({ executablePath });
try {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto(pathToFileURL(join(here, 'slides.html')).href, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);

  const main = await page.locator('section.slide:not(.appendix)').count();
  const total = await page.locator('section.slide').count();
  if (main !== MAIN_SLIDES) throw new Error(`Main part must have ${MAIN_SLIDES} slides, found ${main}`);

  // Catch text that spills out of its slide before it reaches the jury
  const overflow = await page.evaluate(() => [...document.querySelectorAll('section.slide')].flatMap((s, i) =>
    [...s.querySelectorAll('*')].filter((el) => {
      const r = el.getBoundingClientRect(), b = s.getBoundingClientRect();
      return r.width && (r.right > b.right + 1 || r.bottom > b.bottom + 1);
    }).slice(0, 1).map((el) => `slide ${i + 1}: <${el.tagName.toLowerCase()} class="${el.className}">`)));
  if (overflow.length) console.warn('Overflow:\n  ' + overflow.join('\n  '));

  if (process.env.PNG_DIR) {
    const dir = resolve(process.env.PNG_DIR);
    mkdirSync(dir, { recursive: true });
    for (let i = 0; i < total; i++) {
      await page.locator('section.slide').nth(i).screenshot({ path: join(dir, `s${String(i + 1).padStart(2, '0')}.png`) });
    }
  }

  await page.pdf({ path: out, width: '1920px', height: '1080px', printBackground: true, preferCSSPageSize: true });
  const mb = statSync(out).size / 1024 / 1024;
  console.log(`PDF: ${out}\n  ${main} main + ${total - main} appendix slides, ${mb.toFixed(2)} MB`);
  if (mb > MAX_MB) throw new Error(`PDF is ${mb.toFixed(1)} MB, limit is ${MAX_MB} MB`);
} finally {
  await browser.close();
}
