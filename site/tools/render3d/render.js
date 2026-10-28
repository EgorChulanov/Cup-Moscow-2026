// Рендер 3D-объектов в PNG с прозрачным фоном: node render.js out_dir obj1 obj2 ...
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

const root = __dirname;
const types = { '.html': 'text/html', '.js': 'text/javascript' };
const server = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (e, d) => { if (e) { res.writeHead(404); return res.end(); } res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' }); res.end(d); });
}).listen(0, async () => {
  const port = server.address().port;
  const [out, ...objs] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  for (const o of objs) {
    const page = await browser.newPage({ viewport: { width: 1200, height: 1200 } });
    page.on('console', m => console.log(o, m.text()));
    page.on('pageerror', e => console.log(o, 'ERR', e.message));
    await page.goto(`http://localhost:${port}/scene.html?obj=${o}`);
    await page.waitForFunction('window.__done === true', null, { timeout: 120000 });
    await page.locator('canvas').screenshot({ path: path.join(out, `${o}.png`), omitBackground: true });
    console.log('ok', o);
    await page.close();
  }
  await browser.close();
  server.close();
});
