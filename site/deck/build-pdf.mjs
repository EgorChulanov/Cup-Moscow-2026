// Сборка PDF презентации: node site/deck/build-pdf.mjs
// TEAM=<Название> задаёт имя файла CupMoscow2026-Т-Банк-<Название>.pdf (по умолчанию «Команда»).
// PNG_DIR=<папка> дополнительно сохраняет каждый слайд в PNG.
import { createRequire } from 'node:module';
import { existsSync, mkdirSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const require = createRequire(join(process.cwd(), 'noop.js'));
let pw;
for (const name of [process.env.PLAYWRIGHT_CORE, 'playwright', 'playwright-core'].filter(Boolean)) {
  try { pw = require(name); break; } catch { /* следующий вариант */ }
}
if (!pw) throw new Error('Не найден playwright. Установите: npm i playwright-core');

const team = (process.env.TEAM || 'Команда').trim();
const out = resolve(process.env.OUT || join(here, `CupMoscow2026-Т-Банк-${team}.pdf`));
const executablePath = process.env.CHROMIUM_PATH || (existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined);
const browser = await pw.chromium.launch({ executablePath, args: ['--allow-file-access-from-files'] });
try {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto(pathToFileURL(join(here, 'index.html')).href + '?print', { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => Promise.all(Array.from(document.images).map((i) => i.decode().catch(() => {}))));
  const count = await page.locator('section.slide').count();
  if (process.env.PNG_DIR) {
    const dir = resolve(process.env.PNG_DIR); mkdirSync(dir, { recursive: true });
    for (let i = 0; i < count; i++) await page.locator('section.slide').nth(i).screenshot({ path: join(dir, `slide-${String(i + 1).padStart(2, '0')}.png`) });
  }
  await page.emulateMedia({ media: 'print' });
  await page.pdf({ path: out, width: '1920px', height: '1080px', printBackground: true, preferCSSPageSize: true });
  console.log(`${out}: ${count} слайдов, ${Math.round(statSync(out).size / 1024)} КБ`);
} finally {
  await browser.close();
}
