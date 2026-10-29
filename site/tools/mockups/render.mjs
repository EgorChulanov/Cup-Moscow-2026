// Мокапы MacBook и iPhone с экранами решения: node site/tools/mockups/render.mjs <devices.min.css>
// devices.css (MIT): npm i devices.css. Результат пишется в site/img/mock-*.webp.
import { createRequire } from 'node:module';
import { mkdtempSync, writeFileSync, copyFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';

const here = dirname(fileURLToPath(import.meta.url));
const img = resolve(here, '../../img');
const css = resolve(process.argv[2] || 'devices.min.css');
const require = createRequire(join(process.cwd(), 'noop.js'));
const { chromium } = require('playwright');
const tmp = mkdtempSync(join(tmpdir(), 'mock-'));
copyFileSync(css, join(tmp, 'devices.min.css'));

const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
async function shot(s, w, h, scale) {
  const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
  await p.goto(pathToFileURL(join(here, 'screens.html')).href + '?s=' + s, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  const out = join(tmp, s + '.png');
  await p.screenshot({ path: out });
  await p.close();
  return out;
}
const mac = await shot('mac', 1440, 900, 2);
const chat = await shot('chat', 390, 844, 3);
const card = await shot('card', 390, 844, 3);

const MAC = (src) => `<div class="device device-macbook-pro device-spacegray"><div class="device-frame"><img class="device-screen" src="${src}"></div><div class="device-stripe"></div><div class="device-header"></div><div class="device-sensors"></div><div class="device-btns"></div><div class="device-power"></div></div>`;
const PHONE = (src) => `<div class="device device-iphone-14-pro device-spacegray"><div class="device-frame"><img class="device-screen" src="${src}"></div><div class="device-stripe"></div><div class="device-header"></div><div class="device-sensors"></div><div class="device-btns"></div><div class="device-power"></div><div class="device-home"></div></div>`;
const page = (body, extra = '') => `<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="devices.min.css"><style>html,body{margin:0;background:transparent}.st{display:inline-block;padding:24px}
.device-screen{object-fit:cover;object-position:top}${extra}</style><div class="st" id="st">${body}</div>`;
const scenes = {
  mac: page(MAC(mac)),
  'phone-chat': page(PHONE(chat)),
  'phone-card': page(PHONE(card)),
  duo: page(`<div class="duo">${MAC(mac)}<div class="ph">${PHONE(chat)}</div></div>`, '.duo{position:relative;width:900px;height:560px}.duo .device-macbook-pro{position:absolute;left:0;top:40px}.duo .ph{position:absolute;right:0;top:118px;transform:scale(.5);transform-origin:top right}'),
  pair: page(`<div class="pair">${PHONE(card)}${PHONE(chat)}</div>`, '.pair{display:flex;gap:40px;align-items:flex-start}.pair>div:last-child{margin-top:70px}'),
};
for (const [name, html] of Object.entries(scenes)) {
  const f = join(tmp, name + '.html'); writeFileSync(f, html);
  const p = await b.newPage({ viewport: { width: 1200, height: 1100 }, deviceScaleFactor: 2.4 });
  await p.goto(pathToFileURL(f).href, { waitUntil: 'load' });
  await p.evaluate(() => Promise.all(Array.from(document.images).map((i) => i.decode())));
  const png = join(tmp, name + '-f.png');
  await p.locator('#st').screenshot({ path: png, omitBackground: true });
  await p.close();
  execFileSync('python3', ['-c', `from PIL import Image; im=Image.open(${JSON.stringify(png)}); im.thumbnail((2000,2000)); im.save(${JSON.stringify(join(img, 'mock-' + name + '.webp'))}, quality=88, method=6)`]);
  console.log('mock-' + name + '.webp');
}
await b.close();
